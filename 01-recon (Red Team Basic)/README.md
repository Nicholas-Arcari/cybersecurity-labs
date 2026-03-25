# 01 - Reconnaissance (Red Team Basic)

> - **Fase:** Reconnaissance - Pre-engagement Information Gathering
> - **Visibilita:** Zero / Bassa - da OSINT passivo a network scanning attivo
> - **Prerequisiti:** Definizione dello scope, autorizzazione scritta del target
> - **Output:** Mappa della superficie di attacco (IP, domini, email, tecnologie, finding OSINT-001..004, SCAN-001..003, DNS-001..003, INTEL-001..004)

---

## Introduzione

La fase di Reconnaissance e il punto di partenza di qualsiasi attivita di penetration test. Prima di poter sfruttare una vulnerabilita, un attaccante deve sapere cosa esiste, dove si trova e come e configurato. Questa fase risponde a domande fondamentali: quali server sono attivi? Quali domini e sottodomini espone l'organizzazione? Quali tecnologie usa? Chi sono i dipendenti?

La Reconnaissance si divide in due macro-aree che operano in sequenza:

1. **Passiva (OSINT):** l'analista raccoglie informazioni da fonti pubbliche senza mai contattare direttamente i sistemi del target. Nessun pacchetto viene inviato. Nessun log viene generato lato target. Invisibilita totale.

2. **Attiva (Network Scanning):** l'analista invia pacchetti al target per identificare host attivi, porte aperte e servizi in esecuzione. Questa attivita e rilevabile e deve essere eseguita solo dopo aver ottenuto autorizzazione scritta.

Nella Cyber Kill Chain (Lockheed Martin), questa fase corrisponde al primo stadio: **Reconnaissance**. Nella matrice MITRE ATT&CK, le tecniche di questa fase appartengono principalmente alla tattica `Reconnaissance` (TA0043).

---

## Struttura della cartella

```
01-recon (Red Team Basic)/
+-- README.md                            <- questo file (indice + registro finding)
|
+-- 01-osint-passive (Open Source Intelligence)/
|   +-- README.md                        <- indice OSINT + finding OSINT-001..004
|   +-- breach-data/                     <- OSINT-001: credenziali in breach pubblici
|   +-- email-harvesting/                <- OSINT-002: email esposte sul dominio
|   +-- google-dorks/                    <- OSINT-003: file e pannelli indicizzati
|   +-- user-enumeration/                <- OSINT-004: identity correlation (Sherlock)
|
+-- 02-network-scanning-active/
|   +-- README.md                        <- indice network scanning + finding SCAN-001..003
|   +-- live-host-discovery/             <- SCAN-001: host attivi nella subnet
|   +-- port-scanning (Nmap)/
|       +-- masscan/                     <- SCAN-002: port discovery ad alta velocita
|       +-- nmap-scripts/               <- SCAN-003: NSE scripts (SMB signing, NetBIOS)
|
+-- 03-dns-enumeration/
|   +-- README.md                        <- indice DNS + finding DNS-001..003
|   +-- dns-recon/                       <- DNS-001: zone transfer, NS records
|   +-- hosts-file/                      <- DNS-002: virtual host via /etc/hosts
|   +-- subdomain-finding/               <- DNS-003: sottodomini passivi (Sublist3r, Assetfinder)
|
+-- 04-infrastructure-intel/
    +-- README.md                        <- indice infra intel + finding INTEL-001..004
    +-- shodan-censys/                   <- INTEL-001..003: asset esposti, RDP, VoIP, FTP
    +-- tech-stack/                      <- INTEL-004: fingerprinting tecnologico (WhatWeb)
```

---

## Flusso operativo consigliato

```
[INIZIO] Scope definito e autorizzazione ottenuta
          |
          v
[1] OSINT Passivo (invisibile)
     +-- breach-data/    -> credenziali compromesse (h8mail, HIBP)
     +-- email-harvest/  -> email esposte (theHarvester)
     +-- google-dorks/   -> file e login indicizzati (Google GHDB)
     +-- user-enum/      -> presenza su social (Sherlock)
          |
          v
[2] DNS Enumeration (semi-passiva)
     +-- dns-recon/      -> zone transfer, NS, MX (dig, dnsenum)
     +-- subdomain/      -> sottodomini da CT logs (Sublist3r, Assetfinder)
     +-- hosts-file/     -> virtual host non pubblicati (/etc/hosts)
          |
          v
[3] Infrastructure Intel (passiva, da database)
     +-- shodan-censys/  -> asset esposti, versioni, banner (Shodan, Censys)
     +-- tech-stack/     -> fingerprint tecnologico (WhatWeb, Wappalyzer)
          |
          v
[4] Network Scanning Attivo (richiede autorizzazione)
     +-- live-host/      -> ARP/ICMP sweep (arp-scan, nmap -sn)
     +-- masscan/        -> port discovery veloce (Masscan)
     +-- nmap-scripts/   -> enumeration dettagliata NSE (nmap -sC)
          |
          v
[OUTPUT] Attack Surface Map -> input per modulo 02-vulnerability-assessment/
```

---

## Registro Finding

Tutti i finding identificati durante la fase di Reconnaissance sono elencati di seguito. La colonna "File" punta al README della sottocartella che contiene i dettagli tecnici completi.

| ID | Descrizione | Severity | File |
| :--- | :--- | :---: | :--- |
| `OSINT-001` | Credenziali del target identificate in data breach pubblici | `Alto` | `01-osint-passive/breach-data/` |
| `OSINT-002` | Esposizione email su dominio personale - superficie di attacco minima | `Informativo` | `01-osint-passive/email-harvesting/` |
| `OSINT-003` | Documenti e pannelli di login indicizzati da Google su nasa.gov | `Variabile (Basso / Alto)` | `01-osint-passive/google-dorks/` |
| `OSINT-004` | Identity correlation tramite username riutilizzato su piu piattaforme | `Basso` | `01-osint-passive/user-enumeration/` |
| `SCAN-001` | Host attivi identificati nella subnet 10.0.2.0/24 (target Windows 10) | `Informativo` | `02-network-scanning-active/live-host-discovery/` |
| `SCAN-002` | Port discovery con Masscan - falso negativo in ambiente NAT virtualizzato | `Informativo` | `02-network-scanning-active/port-scanning (Nmap)/masscan/` |
| `SCAN-003` | SMB Signing non obbligatorio su 10.0.2.3 - vettore SMB Relay abilitato | `Alto` | `02-network-scanning-active/port-scanning (Nmap)/nmap-scripts/` |
| `DNS-001` | Zone Transfer riuscito su zonetransfer.me - esposizione completa della zona DNS | `Critico` | `03-dns-enumeration/dns-recon/` |
| `DNS-002` | Virtual Host non pubblicato accessibile via manipolazione /etc/hosts | `Medio` | `03-dns-enumeration/hosts-file/` |
| `DNS-003` | 500+ sottodomini di tesla.com enumerati passivamente (inclusi vpn, sso, dev-app) | `Medio` | `03-dns-enumeration/subdomain-finding/` |
| `INTEL-001` | 60+ dispositivi con RDP esposto a Parma - Information Disclosure (nomi host, OS) | `Alto` | `04-infrastructure-intel/shodan-censys/` |
| `INTEL-002` | Workstation con RDP + Apache + porte non standard esposta su IP pubblico | `Alto` | `04-infrastructure-intel/shodan-censys/` |
| `INTEL-003` | Server aziendale con VoIP (3CX) + FTP (FileZilla) + RDP esposti su ADSL consumer | `Critico` | `04-infrastructure-intel/shodan-censys/` |
| `INTEL-004` | tesla.com protetta da Akamai WAF - fingerprinting bloccato, HSTS attivo | `Informativo` | `04-infrastructure-intel/tech-stack/` |

---

## Mappatura MITRE ATT&CK

Tabella aggregata di tutte le tecniche MITRE ATT&CK rilevate durante la fase di Reconnaissance.

| Tattica | Tecnica | ID MITRE | Finding Correlato |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Identity Info: Credentials | `T1589.001` | OSINT-001 |
| Reconnaissance | Gather Victim Identity Info: Email Addresses | `T1589.002` | OSINT-002 |
| Reconnaissance | Search Open Websites/Domains: Search Engines | `T1593.002` | OSINT-003 |
| Reconnaissance | Gather Victim Identity Info: Employee Names | `T1589.003` | OSINT-004 |
| Reconnaissance | Search Open Websites/Domains: Social Media | `T1593.001` | OSINT-004 |
| Reconnaissance | Remote System Discovery | `T1018` | SCAN-001 |
| Reconnaissance | Network Service Discovery | `T1046` | SCAN-001, SCAN-002, SCAN-003 |
| Reconnaissance | Gather Victim Host Info: Software | `T1592.002` | SCAN-003, INTEL-004 |
| Reconnaissance | Gather Victim Network Info: DNS | `T1590.002` | DNS-001, DNS-003 |
| Reconnaissance | Search Open Technical Databases: DNS/Passive DNS | `T1596.001` | DNS-001, DNS-003 |
| Reconnaissance | Search Open Technical Databases: Scan Databases | `T1596.005` | INTEL-001, INTEL-002, INTEL-003 |
| Reconnaissance | Gather Victim Network Info: Network Topology | `T1590.004` | INTEL-001, INTEL-002, INTEL-003 |

---

> **Nota:** Tutte le attivita documentate in questo modulo sono state eseguite su target autorizzati (laboratorio VirtualBox, dominio personale nicholas-arcari.github.io, target pubblicamente disponibili per scopi didattici come zonetransfer.me e programmi bug bounty pubblici come tesla.com). Nessuna attivita e stata condotta su sistemi privi di autorizzazione esplicita.
