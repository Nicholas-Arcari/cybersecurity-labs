> [English](README.en.md) | **Italiano**

# 05 - Social Engineering

> - **Fase:** Social Engineering - Attacco al Layer 8 (fattore umano)
> - **Visibilita:** Variabile - da Zero (pretexting research, crafting email/landing page) ad Alta (invio email phishing, consegna payload, callback C2 post-click)
> - **Prerequisiti:** Completamento modulo 01-recon (OSINT sul target: email aziendali, organigramma, tecnologie usate); infrastruttura email operativa (dominio, SMTP relay); payload generati dal modulo 04-system-exploitation se necessari
> - **Output:** Finding SE-001..015; credenziali raccolte tramite campagne phishing simulate; sessioni MFA hijacked; payload consegnati ed eseguiti; metodologia completa di social engineering riproducibile

---

## Introduzione

Il modulo `05-social-engineering` documenta le tecniche di attacco al fattore umano - il Layer 8 dello stack ISO/OSI. Mentre i moduli precedenti operano su protocolli, servizi e sistemi operativi, qui l'obiettivo e la persona: convincerla a cliccare un link, inserire credenziali, aprire un allegato, eseguire un file. In un penetration test professionale, il social engineering e spesso il vettore di Initial Access piu efficace: secondo il Verizon DBIR 2024, il phishing e il pretexting rappresentano oltre il 70% dei vettori iniziali nelle violazioni confermate.

La sezione e organizzata in sei aree di competenza che riflettono la kill chain completa di un attacco social engineering:

1. **Phishing Campaigns (SE-001..002):** piattaforme per campagne phishing professionali. GoPhish e lo standard aziendale per simulazioni con metriche dettagliate (open rate, click rate, credential submission). Evilginx rappresenta l'evoluzione moderna: reverse proxy phishing che intercetta sessioni MFA in tempo reale, rendendo insufficiente anche l'autenticazione a due fattori.

2. **Social-Engineer Toolkit (SE-003..006):** il framework offensivo piu completo per social engineering. SET integra quattro vettori di attacco documentati separatamente: Website Attack (credential harvesting via clone), Spear-Phishing (email con payload), Infectious Media (supporti rimovibili), PowerShell Attack (stager encoded per Windows).

3. **Payload Delivery (SE-007..010):** le tecniche di consegna del codice malevolo al target. Dalla tecnica classica (macro VBA in documenti Office) alle tecniche moderne post-2022 (HTML Smuggling per bypass email gateway, ISO + LNK per eludere Mark-of-the-Web), fino all'attacco fisico (USB Rubber Ducky).

4. **Email Infrastructure (SE-011..012):** l'infrastruttura tecnica che rende credibile una campagna phishing. Audit SPF/DKIM/DMARC per identificare domini vulnerabili a spoofing, configurazione SMTP relay, generazione di domini typosquatting confondibili.

5. **Pretexting Methodology (SE-013):** la dimensione umana e psicologica dell'attacco. Target profiling OSINT per costruire dossier sul bersaglio, progettazione di scenari di pretexting basati sui principi di Cialdini, template per i pretesti piu efficaci (helpdesk IT, CEO fraud, vendor impersonation).

6. **Custom Python Tools (SE-014..015):** sviluppo di strumenti personalizzati in Python per automatizzare fasi specifiche della kill chain SE: credential harvester Flask custom, generatore di permutazioni email, server tracking pixel per geolocalizzazione.

Nella Cyber Kill Chain e nella matrice MITRE ATT&CK, questo modulo copre le tattiche Reconnaissance (TA0043), Resource Development (TA0042), Initial Access (TA0001), Execution (TA0002) e Collection (TA0009). Il social engineering e il ponte tra la fase di intelligence (moduli 01-02) e l'accesso iniziale che abilita tutte le fasi successive (moduli 04, 07).

---

## Struttura della cartella

```
05-social-engineering/
+-- README.md                                <- questo file: registro finding + MITRE aggregata
|
+-- 01-phishing-campaigns/
|   +-- README.md                            <- panoramica framework phishing, registro SE-001..002
|   +-- gophish/                             <- SE-001 (campaign credential harvest, click rate > 30%)
|   +-- evilginx/                            <- SE-002 (MFA bypass reverse proxy - Critico)
|   +-- pyphisher/                           <- quick testing tool (77 template, tunnel automatico)
|
+-- 02-social-engineer-toolkit/
|   +-- README.md                            <- panoramica SET, registro SE-003..006
|   +-- website-attack-vectors/              <- SE-003 (credential harvester via cloned login)
|   +-- spear-phishing-vectors/              <- SE-004 (email con payload .hta mascherato)
|   +-- infectious-media-generator/          <- SE-005 (autorun.inf su supporto rimovibile)
|   +-- powershell-attack-vectors/           <- SE-006 (PS-encoded reverse shell)
|
+-- 03-payload-delivery/
|   +-- README.md                            <- panoramica vettori delivery, registro SE-007..010
|   +-- malicious-macros/                    <- SE-007 (VBA macro reverse shell PowerShell)
|   +-- html-smuggling/                      <- SE-008 (bypass email gateway con blob JS)
|   +-- iso-lnk-delivery/                    <- SE-009 (delivery chain post-macro kill - Critico)
|   +-- usb-rubber-ducky/                    <- SE-010 (HID attack, esfiltrazione in < 30s)
|
+-- 04-email-infrastructure/
|   +-- README.md                            <- panoramica infrastruttura email, registro SE-011..012
|   +-- spf-dkim-dmarc/                      <- SE-011 (audit misconfiguration DMARC)
|   +-- smtp-relay/                          <- configurazione SMTP relay per campagne
|   +-- domain-typosquatting/                <- SE-012 (generazione domini confondibili)
|
+-- 05-pretexting-methodology/
|   +-- README.md                            <- panoramica metodologia SE umana, registro SE-013
|   +-- target-profiling/                    <- SE-013 (OSINT-based dossier construction)
|   +-- pretext-scenarios/                   <- template scenari: helpdesk, CEO fraud, vendor
|
+-- 06-custom-python-tools/
    +-- README.md                            <- panoramica tool custom, registro SE-014..015
    +-- credential-harvester/                <- SE-014 (Flask credential harvester custom)
    +-- email-generator/                     <- generatore permutazioni email aziendali
    +-- tracking-pixel/                      <- SE-015 (IP geolocation su click tracking)
```

---

## Flusso operativo consigliato

```
[INPUT da 01-recon + 02-vulnerability-assessment]
Email aziendali, organigramma, tecnologie target, domini
         |
         v
[1] Target Profiling & Pretexting (05-pretexting-methodology)
     +-- OSINT aggregation -> dossier target (ruolo, abitudini, stack tech)
     +-- Scelta pretesto -> helpdesk IT / CEO fraud / vendor / delivery
     +-- Costruzione narrativa credibile
              |
              v
[2] Infrastructure Setup (04-email-infrastructure)
     +-- Audit SPF/DKIM/DMARC dominio target -> spoofing possibile?
     +-- Domain typosquatting -> acquisto dominio confondibile
     +-- SMTP relay config -> SendGrid/Mailgun/GoPhish SMTP
              |
              v
[3] Weaponization (03-payload-delivery + 06-custom-python-tools)
     +-- Scelta vettore:
     |   +-- Credential harvest only ---------> GoPhish landing page / Flask custom
     |   +-- Code execution necessaria -------> Macro VBA / HTML Smuggling / ISO+LNK
     |   +-- Accesso fisico disponibile ------> USB Rubber Ducky
     +-- Creazione payload con msfvenom/Empire (da 04-system-exploitation)
     +-- Template email e landing page
              |
              v
[4] Delivery & Execution (01-phishing-campaigns + 02-social-engineer-toolkit)
     +-- Phishing standard ---------> GoPhish campaign (metriche, tracking)
     +-- MFA bypass necessario -----> Evilginx reverse proxy
     +-- Test rapido ---------------> PyPhisher + tunnel
     +-- Multi-vector attack -------> SET (website + spear-phishing + media)
              |
              v
[5] Collection & Analisi
     +-- Credenziali raccolte -> verifica validita (spray mirato, non brute-force)
     +-- Sessioni MFA hijacked -> accesso diretto senza password
     +-- Payload eseguiti -> callback C2 (04-system-exploitation)
     +-- Metriche campagna -> report per il cliente
              |
              v
[OUTPUT] Credenziali valide + sessioni attive + shell C2
     -> input per 07-post-exploitation (lateral movement, persistence, exfiltration)
```

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `GoPhish` | Phishing platform | Web UI + CLI | Standard aziendale per campagne phishing simulate con metriche complete |
| `Evilginx` | Reverse proxy phisher | CLI | MFA bypass in tempo reale tramite reverse proxy (session hijacking) |
| `PyPhisher` | Automated phishing | CLI - Python | Quick testing con 77 template e 4 tunnel provider (ngrok, cloudflared) |
| `SET` | Social engineering framework | CLI - Menu interattivo | Framework multi-vettore: website clone, spear-phishing, media, PowerShell |
| `msfvenom` | Payload generator | CLI | Generazione payload per macro VBA, HTA, PowerShell stager |
| `dnstwist` | Domain analysis | CLI - Python | Generazione e verifica domini typosquatting confondibili |
| `spoofcheck` | Email audit | CLI - Python | Verifica configurazione SPF/DMARC di un dominio target |
| `Rubber Ducky` | HID attack device | Hardware + DuckyScript | Attacco fisico: iniezione keystroke automatizzata via USB |
| `Flask` | Web framework | Python | Sviluppo credential harvester custom e tracking server |

> **Tool moderno consigliato:** `Evilginx 3.x` per phishing avanzato con MFA bypass - sostituisce i phishing kit tradizionali in scenari dove il target ha MFA abilitato. `dnstwist` per typosquatting detection. `GoPhish` + `Mailhog` per testing locale senza infrastruttura SMTP esterna.

---

## Registro Finding - Modulo 05

| ID | Descrizione | Severity | Sottocartella |
| :--- | :--- | :---: | :--- |
| `SE-001` | GoPhish campaign: credential harvesting con click rate > 30% su target simulato (20 utenti) | `Alto` | `01-phishing-campaigns/gophish/` |
| `SE-002` | Evilginx: MFA bypass via reverse proxy - session token intercettato in tempo reale, accesso senza password | `Critico` | `01-phishing-campaigns/evilginx/` |
| `SE-003` | SET Website Attack: credential harvester via pagina login clonata, credenziali catturate in chiaro | `Alto` | `02-social-engineer-toolkit/website-attack-vectors/` |
| `SE-004` | SET Spear-Phishing: email con allegato .hta mascherato, esecuzione stager PowerShell | `Alto` | `02-social-engineer-toolkit/spear-phishing-vectors/` |
| `SE-005` | SET Infectious Media: payload autorun.inf su supporto USB, esecuzione al mount | `Medio` | `02-social-engineer-toolkit/infectious-media-generator/` |
| `SE-006` | SET PowerShell Attack: reverse shell encoded Base64, bypass execution policy | `Alto` | `02-social-engineer-toolkit/powershell-attack-vectors/` |
| `SE-007` | Macro VBA Office: documento Word con macro che esegue stager PowerShell encoded | `Alto` | `03-payload-delivery/malicious-macros/` |
| `SE-008` | HTML Smuggling: bypass email gateway tramite blob JavaScript download, payload .exe ricostruito lato client | `Alto` | `03-payload-delivery/html-smuggling/` |
| `SE-009` | ISO + LNK delivery: esecuzione payload senza Mark-of-the-Web, bypass SmartScreen | `Critico` | `03-payload-delivery/iso-lnk-delivery/` |
| `SE-010` | USB Rubber Ducky: esfiltrazione credenziali WiFi salvate in < 30 secondi tramite HID attack | `Alto` | `03-payload-delivery/usb-rubber-ducky/` |
| `SE-011` | SPF/DKIM/DMARC audit: dominio target con DMARC policy `none` - spoofing email possibile | `Medio` | `04-email-infrastructure/spf-dkim-dmarc/` |
| `SE-012` | Domain typosquatting: 15+ domini confondibili generati, 3 non registrati e acquistabili | `Informativo` | `04-email-infrastructure/domain-typosquatting/` |
| `SE-013` | Target profiling OSINT: dossier completo su target (ruolo, contatti, stack tech, abitudini social) | `Informativo` | `05-pretexting-methodology/target-profiling/` |
| `SE-014` | Credential harvester Flask: pagina login clone con logging IP/User-Agent/credenziali in tempo reale | `Alto` | `06-custom-python-tools/credential-harvester/` |
| `SE-015` | Tracking pixel: geolocalizzazione IP del destinatario al momento dell'apertura email | `Informativo` | `06-custom-python-tools/tracking-pixel/` |

---

## Mappatura MITRE ATT&CK - Aggregata

| Tattica | Tecnica | ID MITRE | Finding Correlato |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Identity Information: Email Addresses | `T1589.002` | SE-013 |
| Reconnaissance | Gather Victim Org Information: Identify Roles | `T1591.004` | SE-013 |
| Reconnaissance | Search Open Websites/Domains | `T1593` | SE-013 |
| Resource Development | Acquire Infrastructure: Domains | `T1583.001` | SE-012 |
| Resource Development | Develop Capabilities: Malware | `T1587.001` | SE-007, SE-008, SE-009 |
| Resource Development | Obtain Capabilities: Tool | `T1588.002` | SE-003, SE-004, SE-005, SE-006 |
| Resource Development | Stage Capabilities: Upload Malware | `T1608.001` | SE-001, SE-002, SE-014 |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | SE-001, SE-002, SE-003, SE-014 |
| Initial Access | Phishing: Spearphishing Attachment | `T1566.001` | SE-004, SE-007, SE-008, SE-009 |
| Initial Access | Phishing: Spearphishing via Service | `T1566.003` | SE-005, SE-010 |
| Initial Access | Replication Through Removable Media | `T1091` | SE-005, SE-010 |
| Execution | User Execution: Malicious Link | `T1204.001` | SE-001, SE-002, SE-003, SE-014 |
| Execution | User Execution: Malicious File | `T1204.002` | SE-004, SE-007, SE-008, SE-009 |
| Execution | Command and Scripting Interpreter: PowerShell | `T1059.001` | SE-006, SE-007 |
| Execution | Command and Scripting Interpreter: Visual Basic | `T1059.005` | SE-007 |
| Defense Evasion | Subvert Trust Controls: Mark-of-the-Web Bypass | `T1553.005` | SE-009 |
| Defense Evasion | Obfuscated Files or Information: HTML Smuggling | `T1027.006` | SE-008 |
| Credential Access | Input Capture: Web Portal Capture | `T1056.003` | SE-001, SE-003, SE-014 |
| Credential Access | Steal Web Session Cookie | `T1539` | SE-002 |
| Collection | Input Capture: Credential API Hooking | `T1056.004` | SE-010 |
| Discovery | System Information Discovery | `T1082` | SE-010, SE-015 |

---

> **Nota:** Tutte le attivita documentate in questo modulo sono state condotte in un ambiente di laboratorio virtualizzato (VirtualBox, rete NAT/Bridge isolata). Le campagne di phishing sono state eseguite esclusivamente contro utenti fittizi creati ad hoc su macchine virtuali di proprieta dell'autore. Nessuna email di phishing e stata inviata a indirizzi reali. Nessuna tecnica e stata applicata a persone o sistemi reali senza autorizzazione esplicita. Le tecniche di social engineering sono documentate a scopo educativo e di awareness.
