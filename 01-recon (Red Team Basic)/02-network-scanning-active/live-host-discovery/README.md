> [English](README.en.md) | **Italiano**

# Network Scanning Active: Live Host Discovery

> - **Fase:** Reconnaissance - Active Network Scanning
> - **Visibilita:** Bassa - pacchetti ARP/ICMP verso la subnet locale, rilevabili da IDS ma comuni nel traffico legittimo
> - **Prerequisiti:** Accesso alla rete target (LAN o VPN), arp-scan e nmap installati, privilegi root per ARP
> - **Output:** SCAN-001 - Mappa degli host attivi nella subnet con IP, MAC address e vendor

---

Obiettivo: Mappatura dei nodi attivi (Live Hosts) all'interno della rete target per identificare la superficie di attacco interna.
Target: Rete Laboratorio (`10.0.2.0/24`)

Strumenti: `arp-scan`, `netdiscover`, `nmap`

---

## 1 Introduzione Teorica

Il Live Host Discovery è la fase preliminare del Network Scanning. Consiste nell'identificare quali indirizzi IP all'interno di un range di rete sono assegnati a dispositivi attivi.

Questa attività è fondamentale per:
- Ottimizzare i tempi: Evitare di scansionare porte su indirizzi IP inesistenti.
- Network Mapping: Creare una topologia della rete (Server, Client, Gateway).

### Differenza tra ARP e ICMP

- Scansione ARP (Layer 2): Utilizzata per reti locali (LAN). È estremamente affidabile poiché il protocollo ARP è essenziale per la comunicazione e raramente bloccato dai firewall locali.
- Scansione ICMP/Ping (Layer 3): Utilizzata per reti remote. Spesso soggetta a blocchi da parte di firewall (es. Windows Defender blocca le richieste Echo ICMP di default).

---

## 2 Esecuzione Tecnica

**ID Finding:** `SCAN-001` | **Severity:** `Informativo`

#### A. Scansione ARP (arp-scan)
È stato utilizzato `arp-scan` per una rilevazione rapida degli host nella sottorete locale. Questo metodo bypassa i firewall di livello OS.

Comando:

```Bash
sudo apt install arp-scan
sudo arp-scan -l
```

![](./img/Screenshot_2026-02-04_09_52_01.jpg)

Analisi: Sono stati rilevati 3 dispositivi, inclusa la macchina target Windows 10 (identificabile dal MAC Address o dall'IP noto).

#### B. Mappatura Attiva (Netdiscover)

È stato utilizzato netdiscover in modalità attiva per interrogare l'intero range di rete.

Comando:

```Bash
sudo apt install netdiscover
sudo netdiscover -r 10.0.2.0/24
```

![](./img/Screenshot_2026-02-04_09_51_05.jpg)

Analisi: Il tool ha fornito una lista chiara di IP e relativi vendor MAC (es. Oracle VirtualBox).

#### C. Ping Sweep (Nmap)

È stata eseguita una scansione ICMP (Ping Sweep) per verificare la visibilità degli host tramite protocolli routabili.

Comando:

```Bash
nmap -sn 10.0.2.0/24
```

![](./img/Screenshot_2026-02-04_09_51_24.jpg)

---

## 3 Conclusioni

L'attività di Live Host Discovery ha permesso di identificare con successo il target Windows 10 all'indirizzo IP 10.0.2.3. La comparazione tra ARP e ICMP ha confermato che, trovandosi nella stessa sottorete fisica, la scansione ARP risulta la più veloce e affidabile per l'enumerazione iniziale.

---

## Analisi a Basso Livello: ARP Frame e ICMP Discovery

### Struttura del Frame ARP (Layer 2)

Il protocollo ARP (RFC 826) opera a Layer 2 (Data Link) ed e il fondamento del live host discovery su reti locali. Un ARP Request e un frame Ethernet broadcast strutturato come segue:

```
Ethernet Header:
  Dst MAC: ff:ff:ff:ff:ff:ff    <-- broadcast a tutti i nodi del segmento
  Src MAC: aa:bb:cc:dd:ee:ff    <-- MAC dell'attaccante
  EtherType: 0x0806             <-- identifica il payload come ARP

ARP Payload:
  Hardware Type: 0x0001         <-- Ethernet
  Protocol Type: 0x0800         <-- IPv4
  Opcode: 0x0001                <-- ARP Request (chi ha questo IP?)
  Sender MAC: aa:bb:cc:dd:ee:ff
  Sender IP: 10.0.2.1
  Target MAC: 00:00:00:00:00:00 <-- sconosciuto (campo da compilare)
  Target IP: 10.0.2.3           <-- IP di cui si cerca il MAC
```

L'host con IP 10.0.2.3 risponde con un ARP Reply (Opcode 0x0002) unicast, inserendo il proprio MAC nel campo Sender MAC. Questo meccanismo e infallibile su reti locali: nessun firewall Layer 3+ puo filtrare ARP perche opera prima dell'IP stack. L'unica difesa e 802.1X (port-based access control) o Dynamic ARP Inspection (DAI) sullo switch.

### Nmap Ping Sweep: Tecniche Multiple

Il comando `nmap -sn` non invia solo ICMP Echo Request. Quando eseguito con privilegi root su rete locale, Nmap utilizza una combinazione di probe:

| Tecnica | Pacchetto | Livello | Efficacia |
| :--- | :--- | :--- | :--- |
| ARP Request | Broadcast Ethernet | Layer 2 | Massima (non filtrabile da firewall IP) |
| ICMP Echo (Type 8) | ICMP Echo Request | Layer 3 | Media (bloccato da Windows Firewall di default) |
| TCP SYN | SYN sulla porta 443 | Layer 4 | Alta (molti host rispondono con RST anche se filtrati) |
| ICMP Timestamp (Type 13) | ICMP Timestamp Request | Layer 3 | Bassa (raramente usata, spesso filtrata) |

Su rete locale, Nmap invia solo ARP Request (scelta ottimale). Su reti remote, invia in parallelo tutti e 4 i probe e considera l'host "up" se riceve risposta da almeno uno. Questa combinazione riduce drasticamente i falsi negativi rispetto al semplice `ping`.

### OUI Lookup (Vendor Identification)

Il MAC address contiene nei primi 3 byte (24 bit) l'OUI (Organizationally Unique Identifier) assegnato da IEEE al produttore hardware. `arp-scan` e Nmap consultano il database OUI per tradurre `08:00:27:xx:xx:xx` in "PCS Systemtechnik GmbH" (OUI di Oracle VirtualBox). In un assessment reale, il vendor MAC rivela il tipo di dispositivo senza necessita di interazione applicativa: Cisco, Juniper, Dell, HP identificano infrastruttura di rete; Apple, Samsung identificano endpoint mobili; VMware, Hyper-V identificano ambienti virtualizzati.

---

## Blue Team: Rilevamento e Contromisure

**Detection:**
- ARP scanning genera un volume anomalo di ARP Request da un singolo MAC address verso tutti gli IP della subnet in sequenza rapida. Switch managed con Dynamic ARP Inspection (DAI) possono rilevare e bloccare questo pattern.
- ICMP sweep genera un burst di ICMP Echo Request verso IP sequenziali - pattern rilevabile da IDS (Snort/Suricata) con regola su ICMP threshold (es. >20 ICMP request/secondo dallo stesso IP sorgente)

**Hardening:**
- Implementare 802.1X per autenticazione a livello di porta switch - impedisce a dispositivi non autorizzati di inviare traffico sulla rete
- Abilitare Dynamic ARP Inspection (DAI) sugli switch managed per validare le risposte ARP contro il DHCP snooping database
- Segmentare la rete con VLAN per limitare il broadcast domain (un ARP scan dalla VLAN utenti non raggiunge la VLAN server)
- Configurare rate limiting ICMP sul firewall perimetrale e sugli host (`iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/s -j ACCEPT`)

---

## Esperienza di Laboratorio

Il confronto tra i tre tool ha evidenziato differenze operative significative. `arp-scan -l` e il piu veloce e silenzioso per reti locali: completa la scansione della /24 in meno di 2 secondi e restituisce risultati puliti con MAC address e vendor. `netdiscover -r` offre un output piu leggibile (tabella interattiva aggiornata in tempo reale) ma e piu lento a causa del retry automatico per host che non rispondono al primo tentativo.

Il dato piu interessante e stato il comportamento di `nmap -sn`: nonostante il target Windows avesse il firewall attivo (ICMP Echo bloccato), Nmap lo ha rilevato come "up" grazie alla probe ARP (eseguita automaticamente su rete locale con privilegi root). Se lo stesso comando fosse stato lanciato senza root (`nmap -sn 10.0.2.0/24` da utente normale), Nmap avrebbe usato solo TCP connect sulla porta 80/443 e il risultato avrebbe potuto differire. Questa differenza di comportamento tra esecuzione privilegiata e non privilegiata e un dettaglio critico che l'analista deve conoscere per interpretare correttamente i risultati.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Discovery | Remote System Discovery | `T1018` | ARP sweep con arp-scan e ICMP ping sweep con nmap -sn per identificare host attivi nella subnet 10.0.2.0/24, rilevando il target Windows 10 a 10.0.2.3 (SCAN-001) |
| Discovery | Network Service Discovery | `T1046` | Netdiscover in modalita attiva per mappare IP attivi e vendor MAC address nella rete locale (SCAN-001) |

---

> **Nota:** Le attivita di Live Host Discovery sono state eseguite esclusivamente all'interno di un laboratorio VirtualBox isolato (subnet 10.0.2.0/24) con target Windows 10 autorizzato. Nessuna scansione e stata condotta su reti esterne o sistemi privi di autorizzazione.