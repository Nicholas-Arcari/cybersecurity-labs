# 02 - Network Scanning Attivo

> - **Fase:** Reconnaissance - Active Network Scanning
> - **Visibilita:** Bassa / Alta - da ARP sweep locale a SYN flood su reti remote
> - **Prerequisiti:** Autorizzazione scritta sul perimetro di test, IP/range target confermati, accesso alla rete (locale o VPN)
> - **Output:** Mappa degli host attivi (SCAN-001), porte aperte (SCAN-002), configurazioni critiche dei servizi (SCAN-003)

---

## Introduzione

Il Network Scanning Attivo e la transizione dalla ricognizione invisibile all'interazione diretta con i sistemi del target. A differenza dell'OSINT passivo, qui si inviano pacchetti: questo significa che le attivita sono rilevabili dagli IDS/IPS del target e devono essere eseguite esclusivamente all'interno dello scope autorizzato.

L'obiettivo e costruire una mappa precisa della superficie di attacco di rete:
- Quali indirizzi IP sono assegnati a dispositivi attivi?
- Quali porte TCP/UDP sono aperte su questi host?
- Quali versioni dei servizi sono in esecuzione?
- Quali configurazioni di sicurezza sono presenti (o assenti)?

La sequenza operativa standard prevede tre livelli progressivi di dettaglio: discovery rapido (chi c'e?), port scanning (cosa gira?), script enumeration (come e configurato?). Ogni livello aumenta il dettaglio ma anche la visibilita.

Il Network Scanning e il prerequisito diretto per il modulo `02-vulnerability-assessment/`, che prende in input la mappa dei servizi esposti per identificare vulnerabilita sfruttabili.

---

## Struttura della cartella

```
02-network-scanning-active/
+-- README.md                        <- questo file (indice + registro finding)
|
+-- live-host-discovery/
|   +-- README.md                    <- SCAN-001: ARP/ICMP sweep (arp-scan, netdiscover, nmap -sn)
|   +-- img/                         <- screenshot del lab
|
+-- port-scanning (Nmap)/
    +-- masscan/
    |   +-- README.md                <- SCAN-002: high-speed port discovery (Masscan)
    |   +-- img/                     <- screenshot del lab
    |
    +-- nmap-scripts/
        +-- README.md                <- SCAN-003: NSE enumeration (SMB signing, NetBIOS)
        +-- img/                     <- screenshot del lab
```

---

## `live-host-discovery/` - Identificazione Host Attivi

**ID Finding:** `SCAN-001` | **Severity:** `Informativo`

Il Live Host Discovery e il primo passo operativo del network scanning: prima di scansionare porte, occorre identificare quali indirizzi IP nel range target corrispondono a dispositivi attivi. Inviare SYN su 65535 porte a migliaia di host inesistenti spreca tempo prezioso.

Tre approcci complementari:
- `arp-scan -l` (Layer 2, LAN): il piu affidabile in reti locali, bypassa i firewall OS
- `netdiscover -r <CIDR>` (ARP attivo): utile in ambienti con broadcast abilitato
- `nmap -sn <CIDR>` (ICMP Ping Sweep): standard per reti remote, ma soggetto a blocchi firewall

**Risultato del lab:** identificato il target Windows 10 a `10.0.2.3` nella subnet `10.0.2.0/24`.

---

## `port-scanning (Nmap)/masscan/` - High-Speed Port Discovery

**ID Finding:** `SCAN-002` | **Severity:** `Informativo`

Masscan e uno scanner di porte TCP asincrono con stack TCP/IP personalizzato. Permette di scansionare milioni di porte al secondo su reti fisiche, rendendolo lo strumento ideale per il Broad Scope Discovery (range `/16`, `/8`).

**Limitazione critica documentata in lab:** in ambienti virtualizzati con NAT (VirtualBox), il raw socket personalizzato di Masscan non riceve correttamente i pacchetti di risposta, generando falsi negativi. La cross-validation con Nmap e obbligatoria quando Masscan restituisce risultati negativi su target sospetti.

> **Tool moderno consigliato:** `RustScan` - combina velocita di discovery (Masscan-like) con compatibilita migliorata per ambienti NAT virtualizzati, passando automaticamente i risultati a Nmap per l'enumeration dettagliata.

---

## `port-scanning (Nmap)/nmap-scripts/` - NSE Enumeration

**ID Finding:** `SCAN-003` | **Severity:** `Alto`

L'Nmap Scripting Engine (NSE) permette di estrarre informazioni di configurazione che il semplice port scanning non rivela. Gli script di default (`-sC`) eseguono una batteria di test sicuri su ciascun servizio identificato.

**Due finding critici identificati in lab su 10.0.2.3:**
- `SCAN-003a`: SMB Signing `enabled but not required` - vettore diretto per attacchi SMB Relay (MITM)
- `SCAN-003b`: NetBIOS name disclosure (`WINDOWS-TEST`) - information disclosure del nome host

La misconfiguration SMB Signing rilevata qui (SCAN-003) viene sfruttata attivamente nel modulo `07-post-exploitation/04-pivoting-tunneling/`.

---

## Flusso operativo consigliato

```
[INPUT] Range IP target autorizzato (es. 10.0.2.0/24)
          |
          v
[1] Live Host Discovery (veloce, bassa visibilita)
     +-- sudo arp-scan -l              # LAN: usa ARP, bypassa firewall OS
     +-- nmap -sn 10.0.2.0/24         # remoto: ICMP ping sweep
     -> Lista IP attivi
          |
          v
[2] Port Discovery (veloce, alta visibilita)
     +-- masscan -p1-65535 <IP> --rate=1000 -e eth0   # solo reti fisiche
     +-- nmap -p- --min-rate=3000 <IP>                 # alternativa NAT-safe
     -> Lista porte aperte
          |
          v
[3] Service & Script Enumeration (dettagliata)
     +-- nmap -p <PORTE> -sC -sV -O <IP>
     -> Banner, versioni, configurazioni di sicurezza
          |
          v
[OUTPUT] Attack Surface Map -> 02-vulnerability-assessment/
```

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `arp-scan` | Port scanner | CLI (Layer 2) | Live host discovery in LAN, bypassa firewall OS |
| `netdiscover` | Port scanner | CLI (ARP attivo) | Discovery passivo/attivo in reti con broadcast |
| `nmap` | Port scanner / Service enumerator | CLI | Standard per port scan, versioning e NSE |
| `Masscan` | Port scanner | CLI (raw socket) | High-speed port discovery su reti fisiche |
| `RustScan` | Port scanner | CLI | Discovery veloce compatibile con NAT, feed Nmap |
| `nmap -sC` (NSE) | Service enumerator | CLI | Automazione test di configurazione via script |

> **Tool moderno consigliato:** `RustScan` (`rustscan -a <IP> -- -sC -sV`) - esegue il port discovery in pochi secondi e passa automaticamente le porte trovate a Nmap per l'enumeration dettagliata, risolvendo il problema NAT di Masscan in ambienti virtualizzati.

---

## Registro Finding

| ID | Descrizione | Severity | File |
| :--- | :--- | :---: | :--- |
| `SCAN-001` | Host attivi identificati in 10.0.2.0/24, target Windows 10 a 10.0.2.3 | `Informativo` | `live-host-discovery/README.md` |
| `SCAN-002` | Port discovery con Masscan - falso negativo documentato in ambiente NAT | `Informativo` | `port-scanning (Nmap)/masscan/README.md` |
| `SCAN-003` | SMB Signing non obbligatorio + NetBIOS name disclosure su 10.0.2.3 | `Alto` | `port-scanning (Nmap)/nmap-scripts/README.md` |

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Remote System Discovery | `T1018` | ARP sweep e ICMP ping sweep per identificare host attivi nella subnet 10.0.2.0/24 (SCAN-001) |
| Reconnaissance | Network Service Discovery | `T1046` | Port scanning con Masscan e Nmap per identificare servizi esposti sul target (SCAN-001, SCAN-002, SCAN-003) |
| Reconnaissance | Gather Victim Host Info: Software | `T1592.002` | NSE scripts per identificare versioni software e configurazioni di sicurezza SMB (SCAN-003) |

---

> **Nota:** Tutte le attivita di network scanning documentate in questa sezione sono state eseguite su un laboratorio VirtualBox isolato con target Windows 10 autorizzato (subnet 10.0.2.0/24). Nessuna scansione e stata condotta su reti o sistemi privi di autorizzazione esplicita.
