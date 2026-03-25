# 02 - Web Recon (Enumeration)

> - **Fase:** Web Attack - Web Application Enumeration
> - **Visibilita:** Variabile - Bassa (tech profiling con richieste HTTP standard) / Media (dir-busting e scanner generano molto traffico) / Bassa (subdomain enum passiva)
> - **Prerequisiti:** Target web identificato dal modulo `01-recon`, proxy configurato (`01-proxy-tools`)
> - **Output:** Mappa delle risorse nascoste, stack tecnologico e versioni software, sottodomini, finding WEB-002 e WEB-003

---

## Introduzione

La web reconnaissance e una fase distinta e complementare rispetto alla network recon del modulo `01-recon`. Mentre in quella fase si identificano IP, porte aperte e servizi di rete, qui ci si concentra esclusivamente sullo strato applicativo HTTP/HTTPS.

La distinzione operativa e fondamentale:

| Network Recon (`01-recon`) | Web Recon (`02-web-recon`) |
| :--- | :--- |
| Porte aperte e servizi (`nmap`) | Pagine e directory nascoste (`gobuster`) |
| Hostname e DNS | Virtual host nascosti (`gobuster vhost`) |
| Banner di servizio (`nc`, `telnet`) | Stack tecnologico e versioni (`whatweb`) |
| IP e ASN | Sottodomini web (`subfinder`, `amass`) |
| Vulnerabilita di rete (`nmap NSE`) | Vulnerabilita applicative (`nikto`, `nuclei`) |

La web recon e il prerequisito per qualsiasi attacco OWASP: senza sapere che il target usa PHP 5.6 (WEB-002) o che espone `/CVS` (WEB-003), le fasi successive sarebbero condotte alla cieca.

Il tool moderno di riferimento per questa fase e `nuclei` (ProjectDiscovery), che combina fingerprinting tecnologico e vulnerability scanning in un unico tool basato su template YAML aggiornati quotidianamente dalla community.

---

## Struttura della cartella

```
02-web-recon (Enumeration)/
+-- dir-busting/            # Gobuster, Feroxbuster - finding WEB-003
+-- subdomain-enum/         # Subfinder, OWASP Amass, VHost fuzzing
+-- tech-profiler/          # WhatWeb, Wappalyzer - finding WEB-002
+-- vulnerability-scanners/ # Nikto (legacy), Nuclei (moderno)
```

---

## `tech-profiler/` - Technology Fingerprinting

**ID Finding:** `WEB-002` | **Severity:** `Alto` | **CVSS v3.1:** 7.5

### Contesto operativo

Prima di lanciare qualsiasi attacco, un analista deve sapere "di cosa e fatto" il target. Il tech profiling analizza gli header HTTP, il codice sorgente, i cookie e i path delle risorse per identificare il software e le versioni esatte in uso.

Il risultato diretto e il **CVE mapping**: conoscendo che il server usa PHP 5.6.40 (End of Life), si cercano exploit noti su Exploit-DB specifici per quella versione, invece di perdere tempo con attacchi generici. Vedere la sezione `02-vulnerability-assessment/03-cve-analysis/` per il workflow di ricerca CVE.

Strumenti principali:
- `whatweb`: scanner CLI, analisi degli header e fingerprint del CMS.
- `Wappalyzer`: estensione browser, fingerprint passivo mentre si naviga.

Il finding WEB-002 e documentato in dettaglio in `tech-profiler/README.md`.

---

## `dir-busting/` - Directory & File Enumeration

**ID Finding:** `WEB-003` | **Severity:** `Alto` | **CVSS v3.1:** 7.5

### Contesto operativo

Le applicazioni web spesso espongono risorse che non compaiono nei link navigabili: pannelli di amministrazione (`/admin`), file di backup (`.bak`, `.old`), directory di versionamento (`.git`, `CVS`), file di configurazione IDE (`.idea`).

Il dir-busting e una tecnica di brute force attiva: lo strumento invia migliaia di richieste HTTP, una per ogni voce della wordlist, e analizza i codici di stato della risposta per determinare quali risorse esistono.

Il codice di stato e il segnale primario:
- `200 OK`: risorsa esistente e accessibile.
- `301/302 Redirect`: directory esistente (spesso indica `/admin` o simili).
- `403 Forbidden`: risorsa esistente ma accesso negato (interessante per escalation successiva).
- `404 Not Found`: risorsa non presente.

Il finding WEB-003 (directory CVS e `.idea` esposti) e documentato in dettaglio in `dir-busting/README.md`.

---

## `subdomain-enum/` - Subdomain Enumeration

### Contesto operativo

L'organizzazione target raramente espone un solo dominio. L'ecosistema include sottodomini per ambienti di staging, VPN, portali SSO, API, CDN. Questi sottodomini secondari sono spesso meno monitorati e aggiornati rispetto al dominio principale, rendendoli target privilegiati.

Le tecniche si dividono in:
- **Passiva:** interrogazione di Certificate Transparency Logs, VirusTotal, Censys, SecurityTrails. Zero interazione con il target.
- **Attiva:** brute force DNS con wordlist, zone transfer, VHost fuzzing. Genera traffico verso il target.

La lista di sottodomini prodotta diventa input diretto per la fase successiva: ogni sottodominio e un potenziale entry point da testare con dir-busting e tech profiling.

---

## `vulnerability-scanners/` - Automated Web Scanning

### Contesto operativo

I vulnerability scanner web automatizzano la ricerca di configurazioni errate e file di default confrontando le risposte del server con database di firme note. Completano il tech profiling con una prospettiva orientata agli exploit.

La distinzione operativa tra i due scanner principali:

| Scanner | Approccio | Velocita | Rilevamento WAF | Uso ideale |
| :--- | :--- | :--- | :--- | :--- |
| `Nikto` | Signature-based (legacy) | Lento | Facile | Prima baseline, lab |
| `Nuclei` | Template YAML (moderno) | Veloce | Difficile | Pipeline CI/CD, engagement reali |

Nikto e noto per essere molto "rumoroso" (genera molte richieste anomale) e viene facilmente bloccato dai WAF in ambienti di produzione. Nuclei, basato su template YAML specifici, e piu preciso e meno rilevabile.

I finding WEB-002 (PHP EOL) e WEB-003 (.idea exposure) sono stati confermati anche da Nuclei tramite i template `php-eol` e `idea-folder-exposure`.

---

## Flusso operativo consigliato

```
[1] Tech Profiling (tech-profiler/)
     +-- whatweb -v <TARGET>          ->  stack tecnologico e versioni
     +-- Wappalyzer (browser)         ->  conferma passiva
         |
         v
[2] CVE Mapping (02-vulnerability-assessment/03-cve-analysis/)
     +-- se PHP 5.6 -> cercare CVE per PHP 5.6.x
     +-- se WordPress X.Y -> cercare CVE per quella versione
         |
         v
[3] Dir Busting (dir-busting/)
     +-- gobuster dir -u <TARGET> -w common.txt
     +-- feroxbuster -u <TARGET> (ricorsivo)
         |
         v
[4] Subdomain Enum (subdomain-enum/)
     +-- subfinder -d <DOMINIO>        ->  passivo
     +-- amass enum -d <DOMINIO>       ->  attivo + ASN mapping
     +-- gobuster vhost (per lab locali)
         |
         v
[5] Automated Scan (vulnerability-scanners/)
     +-- nikto -h <TARGET>             ->  baseline generale
     +-- nuclei -u <TARGET>            ->  template-based (piu preciso)
```

---

## Registro Finding - Web Recon

| ID | Descrizione | Severity | Sottocartella |
| :--- | :--- | :---: | :--- |
| `WEB-002` | PHP 5.6.40 EOL + header `X-Powered-By` esposto | `Alto` | `tech-profiler/` |
| `WEB-003` | Directory CVS e cartella `.idea` esposti pubblicamente | `Alto` | `dir-busting/` |

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `whatweb` | Tech fingerprint | CLI - Attiva | Identificazione CMS, web server, linguaggi e versioni |
| `Wappalyzer` | Tech fingerprint | Browser Extension - Passiva | Fingerprint visivo durante navigazione |
| `gobuster` | Dir/VHost brute force | CLI - Attiva | Directory busting e VHost fuzzing |
| `feroxbuster` | Dir brute force | CLI - Attiva | Dir busting ricorsivo, piu veloce di gobuster |
| `subfinder` | Subdomain enum | CLI - Passiva | Enumerazione passiva da CT logs e OSINT |
| `amass` | Subdomain/ASN enum | CLI - Attiva | Mappatura profonda con ASN e reverse WHOIS |
| `nikto` | Vulnerability scanner | CLI - Attiva | Baseline generale, misconfiguration server |
| `nuclei` | Vulnerability scanner | CLI - Attiva | Template YAML, CVE-specifico, pipeline CI/CD |
| `httpx` | HTTP prober | CLI - Attiva | Verifica rapida di quali sottodomini sono attivi |

> **Tool moderno consigliato:** `nuclei` (ProjectDiscovery) - sostituisce Nikto per la maggior parte dei casi d'uso moderni. Ogni template e mappato su CVE o CWE specifici, riducendo i falsi positivi. Aggiornamento dei template: `nuclei -update-templates`.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Active Scanning: Vulnerability Scanning | `T1595.002` | Scansione con Nikto e Nuclei per identificare PHP EOL, header esposti e file sensibili (WEB-002, WEB-003) |
| Reconnaissance | Active Scanning: Wordlist Scanning | `T1595.003` | Directory busting con Gobuster/Feroxbuster su wordlist `common.txt` per enumerare risorse nascoste (WEB-003) |
| Reconnaissance | Gather Victim Host Info: Software | `T1592.002` | Tech profiling con WhatWeb per identificare versione PHP 5.6.40, Nginx 1.19 e stack tecnologico (WEB-002) |
| Reconnaissance | Gather Victim Network Info: Domain Properties | `T1590.001` | Enumerazione sottodomini con Subfinder e OWASP Amass per espandere la superficie di attacco |
| Discovery | File and Directory Discovery | `T1083` | Identificazione di directory CVS, `.idea` e `/admin` tramite dir-busting (WEB-003) |
| Discovery | Network Service Scanning | `T1046` | Scansione automatizzata Nikto/Nuclei per identificare servizi e versioni sul target |
| Collection | Data from Information Repositories | `T1213` | Accesso a directory di versionamento CVS esposta che potrebbe rivelare il codice sorgente (WEB-003) |

---

> **Nota:** Le attivita di web recon documentate sono state condotte su `testphp.vulnweb.com`
> (ambiente di test pubblico e autorizzato di Acunetix) e su `tesla.com` limitatamente alla
> subdomain enumeration passiva da fonti OSINT pubbliche (Certificate Transparency Logs).
> La ricognizione attiva su target non autorizzati e illegale ai sensi dell'art. 615-ter c.p.
