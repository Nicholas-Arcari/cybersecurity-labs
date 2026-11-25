> [English](README.en.md) | **Italiano**

# 01 - Reconnaissance (red team basic)

> - **Fase:** Reconnaissance - Pre-engagement Information Gathering
> - **Visibilita:** Zero / Bassa - da OSINT passivo a network scanning attivo
> - **Prerequisiti:** Definizione dello scope, autorizzazione scritta del target
> - **Output:** Mappa della superficie di attacco (IP, domini, email, tecnologie, finding OSINT-001..006, SCAN-001..003, DNS-001..003, INTEL-001..006)

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
|   +-- README.md                        <- indice OSINT + finding OSINT-001..006
|   +-- breach-data/                     <- OSINT-001: credenziali in breach pubblici
|   +-- email-harvesting/                <- OSINT-002: email esposte sul dominio
|   +-- google-dorks/                    <- OSINT-003: file e pannelli indicizzati
|   +-- user-enumeration/                <- OSINT-004: identity correlation (Sherlock)
|   +-- osint-frameworks/                <- OSINT-005: automazione OSINT (SpiderFoot, recon-ng, Maltego)
|   +-- code-secret-leakage/             <- OSINT-006: segreti nei repository pubblici (gitleaks, TruffleHog)
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
    +-- README.md                        <- indice infra intel + finding INTEL-001..006
    +-- shodan-censys/                   <- INTEL-001..003: asset esposti, RDP, VoIP, FTP
    +-- tech-stack/                      <- INTEL-004: fingerprinting tecnologico (WhatWeb)
    +-- asn-whois-ct/                    <- INTEL-005: perimetro (ASN, WHOIS, Certificate Transparency)
    +-- cloud-asset-discovery/           <- INTEL-006: storage cloud esposto (bucket S3/Blob/GCP)
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

## Registro finding

Tutti i finding identificati durante la fase di Reconnaissance sono elencati di seguito. La colonna "File" punta al README della sottocartella che contiene i dettagli tecnici completi.

| id | descrizione | severity | file |
| :--- | :--- | :---: | :--- |
| `OSINT-001` | credenziali del target identificate in data breach pubblici | `Alto` | `01-osint-passive/breach-data/` |
| `OSINT-002` | esposizione email su dominio personale - superficie di attacco minima | `Informativo` | `01-osint-passive/email-harvesting/` |
| `OSINT-003` | documenti e pannelli di login indicizzati da google su nasa.gov | `Variabile (Basso / Alto)` | `01-osint-passive/google-dorks/` |
| `OSINT-004` | identity correlation tramite username riutilizzato su piu piattaforme | `Basso` | `01-osint-passive/user-enumeration/` |
| `OSINT-005` | correlazione osint automatica del target via framework multi-fonte (spiderfoot, recon-ng, maltego) | `Variabile (Informativo / Alto)` | `01-osint-passive/osint-frameworks/` |
| `OSINT-006` | segreti (credenziali, api key, chiavi) esposti in repository pubblici (git history) | `Variabile (Alto / Critico)` | `01-osint-passive/code-secret-leakage/` |
| `SCAN-001` | host attivi identificati nella subnet 10.0.2.0/24 (target windows 10) | `Informativo` | `02-network-scanning-active/live-host-discovery/` |
| `SCAN-002` | port discovery con masscan - falso negativo in ambiente nat virtualizzato | `Informativo` | `02-network-scanning-active/port-scanning (Nmap)/masscan/` |
| `SCAN-003` | smb signing non obbligatorio su 10.0.2.3 - vettore smb relay abilitato | `Alto` | `02-network-scanning-active/port-scanning (Nmap)/nmap-scripts/` |
| `DNS-001` | zone transfer riuscito su zonetransfer.me - esposizione completa della zona dns | `Critico` | `03-dns-enumeration/dns-recon/` |
| `DNS-002` | virtual host non pubblicato accessibile via manipolazione /etc/hosts | `Medio` | `03-dns-enumeration/hosts-file/` |
| `DNS-003` | 500+ sottodomini di tesla.com enumerati passivamente (inclusi vpn, sso, dev-app) | `Medio` | `03-dns-enumeration/subdomain-finding/` |
| `INTEL-001` | 60+ dispositivi con rdp esposto a parma - information disclosure (nomi host, os) | `Alto` | `04-infrastructure-intel/shodan-censys/` |
| `INTEL-002` | workstation con rdp + apache + porte non standard esposta su ip pubblico | `Alto` | `04-infrastructure-intel/shodan-censys/` |
| `INTEL-003` | server aziendale con voip (3cx) + ftp (filezilla) + rdp esposti su adsl consumer | `Critico` | `04-infrastructure-intel/shodan-censys/` |
| `INTEL-004` | tesla.com protetta da akamai waf - fingerprinting bloccato, hsts attivo | `Informativo` | `04-infrastructure-intel/tech-stack/` |
| `INTEL-005` | perimetro completo mappato via asn/whois e sottodomini da certificate transparency | `Variabile (Informativo / Medio)` | `04-infrastructure-intel/asn-whois-ct/` |
| `INTEL-006` | storage cloud esposto (bucket s3/blob) con lettura anonima di dati sensibili | `Variabile (Medio / Critico)` | `04-infrastructure-intel/cloud-asset-discovery/` |

---

## Mappatura MITRE ATT&CK

Tabella aggregata di tutte le tecniche MITRE ATT&CK rilevate durante la fase di Reconnaissance.

| tattica | tecnica | id mitre | finding correlato |
| :--- | :--- | :--- | :--- |
| reconnaissance | gather victim identity info: credentials | `T1589.001` | OSINT-001 |
| reconnaissance | gather victim identity info: email addresses | `T1589.002` | OSINT-002 |
| reconnaissance | search open websites/domains: search engines | `T1593.002` | OSINT-003 |
| reconnaissance | gather victim identity info: employee names | `T1589.003` | OSINT-004 |
| reconnaissance | search open websites/domains: social media | `T1593.001` | OSINT-004 |
| reconnaissance | remote system discovery | `T1018` | SCAN-001 |
| reconnaissance | network service discovery | `T1046` | SCAN-001, SCAN-002, SCAN-003 |
| reconnaissance | gather victim host info: software | `T1592.002` | SCAN-003, INTEL-004 |
| reconnaissance | gather victim network info: dns | `T1590.002` | DNS-001, DNS-003 |
| reconnaissance | search open technical databases: dns/passive dns | `T1596.001` | DNS-001, DNS-003 |
| reconnaissance | search open technical databases: scan databases | `T1596.005` | INTEL-001, INTEL-002, INTEL-003 |
| reconnaissance | gather victim network info: network topology | `T1590.004` | INTEL-001, INTEL-002, INTEL-003, INTEL-005 |
| reconnaissance | search open technical databases (aggregazione multi-fonte) | `T1596` | OSINT-005, OSINT-006, INTEL-006 |
| reconnaissance | search open technical databases: whois | `T1596.002` | OSINT-005, INTEL-005 |
| reconnaissance | search open technical databases: digital certificates | `T1596.003` | INTEL-005 |
| reconnaissance | gather victim network info: ip addresses | `T1590.005` | INTEL-005 |
| credential access | unsecured credentials: credentials in files | `T1552.001` | OSINT-006 |
| collection | data from cloud storage | `T1530` | INTEL-006 |

---

> **Nota:** Tutte le attivita documentate in questo modulo sono state eseguite su target autorizzati (laboratorio VirtualBox, dominio personale nicholas-arcari.github.io, target pubblicamente disponibili per scopi didattici come zonetransfer.me e programmi bug bounty pubblici come tesla.com). Nessuna attivita e stata condotta su sistemi privi di autorizzazione esplicita.
