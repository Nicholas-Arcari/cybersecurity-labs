> [English](README.en.md) | **Italiano**

# 02 - Web recon (enumeration)

> - **Fase:** Web Attack - Web Application Enumeration
> - **Visibilita:** Variabile - Bassa (tech profiling con richieste HTTP standard) / Media (dir-busting e scanner generano molto traffico) / Bassa (subdomain enum passiva)
> - **Prerequisiti:** Target web identificato dal modulo `01-recon`, proxy configurato (`01-proxy-tools`)
> - **Output:** Mappa delle risorse nascoste, stack tecnologico e versioni software, sottodomini, finding WEB-002 e WEB-003

---

## Introduzione

La web reconnaissance e una fase distinta e complementare rispetto alla network recon del modulo `01-recon`. Mentre in quella fase si identificano IP, porte aperte e servizi di rete, qui ci si concentra esclusivamente sullo strato applicativo HTTP/HTTPS.

La distinzione operativa e fondamentale:

| network recon (`01-recon`) | web recon (`02-web-recon`) |
| :--- | :--- |
| porte aperte e servizi (`nmap`) | pagine e directory nascoste (`gobuster`) |
| hostname e dns | virtual host nascosti (`gobuster vhost`) |
| banner di servizio (`nc`, `telnet`) | stack tecnologico e versioni (`whatweb`) |
| ip e asn | sottodomini web (`subfinder`, `amass`) |
| vulnerabilita di rete (`nmap NSE`) | vulnerabilita applicative (`nikto`, `nuclei`) |

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

## `tech-profiler/` - Technology fingerprinting

**ID Finding:** `WEB-002` | **Severity:** `Alto` | **CVSS v3.1:** 7.5

### Contesto operativo

Prima di lanciare qualsiasi attacco, un analista deve sapere "di cosa e fatto" il target. Il tech profiling analizza gli header HTTP, il codice sorgente, i cookie e i path delle risorse per identificare il software e le versioni esatte in uso.

Il risultato diretto e il **CVE mapping**: conoscendo che il server usa PHP 5.6.40 (End of Life), si cercano exploit noti su Exploit-DB specifici per quella versione, invece di perdere tempo con attacchi generici. Vedere la sezione `02-vulnerability-assessment/03-cve-analysis/` per il workflow di ricerca CVE.

Strumenti principali:
- `whatweb`: scanner CLI, analisi degli header e fingerprint del CMS.
- `Wappalyzer`: estensione browser, fingerprint passivo mentre si naviga.

Il finding WEB-002 e documentato in dettaglio in `tech-profiler/README.md`.

---

## `dir-busting/` - Directory & file enumeration

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

## `subdomain-enum/` - Subdomain enumeration

### Contesto operativo

L'organizzazione target raramente espone un solo dominio. L'ecosistema include sottodomini per ambienti di staging, VPN, portali SSO, API, CDN. Questi sottodomini secondari sono spesso meno monitorati e aggiornati rispetto al dominio principale, rendendoli target privilegiati.

Le tecniche si dividono in:
- **Passiva:** interrogazione di Certificate Transparency Logs, VirusTotal, Censys, SecurityTrails. Zero interazione con il target.
- **Attiva:** brute force DNS con wordlist, zone transfer, VHost fuzzing. Genera traffico verso il target.

La lista di sottodomini prodotta diventa input diretto per la fase successiva: ogni sottodominio e un potenziale entry point da testare con dir-busting e tech profiling.

---

## `vulnerability-scanners/` - Automated web scanning

### Contesto operativo

I vulnerability scanner web automatizzano la ricerca di configurazioni errate e file di default confrontando le risposte del server con database di firme note. Completano il tech profiling con una prospettiva orientata agli exploit.

La distinzione operativa tra i due scanner principali:

| scanner | approccio | velocita | rilevamento waf | uso ideale |
| :--- | :--- | :--- | :--- | :--- |
| `Nikto` | signature-based (legacy) | lento | facile | prima baseline, lab |
| `Nuclei` | template yaml (moderno) | veloce | difficile | pipeline ci/cd, engagement reali |

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

## Registro finding - web recon

| id | descrizione | severity | sottocartella |
| :--- | :--- | :---: | :--- |
| `WEB-002` | php 5.6.40 eol + header `X-Powered-By` esposto | `Alto` | `tech-profiler/` |
| `WEB-003` | directory cvs e cartella `.idea` esposti pubblicamente | `Alto` | `dir-busting/` |

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `whatweb` | tech fingerprint | cli - attiva | identificazione cms, web server, linguaggi e versioni |
| `Wappalyzer` | tech fingerprint | browser extension - passiva | fingerprint visivo durante navigazione |
| `gobuster` | dir/vhost brute force | cli - attiva | directory busting e vhost fuzzing |
| `feroxbuster` | dir brute force | cli - attiva | dir busting ricorsivo, piu veloce di gobuster |
| `subfinder` | subdomain enum | cli - passiva | enumerazione passiva da ct logs e osint |
| `amass` | subdomain/asn enum | cli - attiva | mappatura profonda con asn e reverse whois |
| `nikto` | vulnerability scanner | cli - attiva | baseline generale, misconfiguration server |
| `nuclei` | vulnerability scanner | cli - attiva | template yaml, cve-specifico, pipeline ci/cd |
| `httpx` | http prober | cli - attiva | verifica rapida di quali sottodomini sono attivi |

> **Tool moderno consigliato:** `nuclei` (ProjectDiscovery) - sostituisce Nikto per la maggior parte dei casi d'uso moderni. Ogni template e mappato su CVE o CWE specifici, riducendo i falsi positivi. Aggiornamento dei template: `nuclei -update-templates`.

---

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| reconnaissance | active scanning: vulnerability scanning | `T1595.002` | scansione con nikto e nuclei per identificare php eol, header esposti e file sensibili (WEB-002, WEB-003) |
| reconnaissance | active scanning: wordlist scanning | `T1595.003` | directory busting con gobuster/feroxbuster su wordlist `common.txt` per enumerare risorse nascoste (WEB-003) |
| reconnaissance | gather victim host info: software | `T1592.002` | tech profiling con whatweb per identificare versione php 5.6.40, nginx 1.19 e stack tecnologico (WEB-002) |
| reconnaissance | gather victim network info: domain properties | `T1590.001` | enumerazione sottodomini con subfinder e owasp amass per espandere la superficie di attacco |
| discovery | file and directory discovery | `T1083` | identificazione di directory cvs, `.idea` e `/admin` tramite dir-busting (WEB-003) |
| discovery | network service scanning | `T1046` | scansione automatizzata nikto/nuclei per identificare servizi e versioni sul target |
| collection | data from information repositories | `T1213` | accesso a directory di versionamento cvs esposta che potrebbe rivelare il codice sorgente (WEB-003) |

---

> **Nota:** Le attivita di web recon documentate sono state condotte su `testphp.vulnweb.com`
> (ambiente di test pubblico e autorizzato di Acunetix) e su `tesla.com` limitatamente alla
> subdomain enumeration passiva da fonti OSINT pubbliche (Certificate Transparency Logs).
> La ricognizione attiva su target non autorizzati e illegale ai sensi dell'art. 615-ter c.p.
