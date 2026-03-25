# 03 - Web Attacks (Red Team + Secure Coding)

> - **Fase:** Web Application Penetration Testing
> - **Visibilita:** Variabile - da Zero (analisi passiva del codice) ad Alta (scanner automatici come Nikto)
> - **Prerequisiti:** Completamento modulo 01-recon (superficie d'attacco HTTP/HTTPS identificata), modulo 02-vulnerability-assessment (tecnologie target note)
> - **Output:** Finding documentati WEB-001..015, payload funzionanti, prove di sfruttamento, remediation per ogni vulnerabilita

---

## Introduzione

Il modulo `03-web-attacks` rappresenta il cuore operativo di un penetration test moderno. La maggior parte della superficie di attacco aziendale e oggi esposta via web (HTTP/HTTPS): applicazioni CMS, API REST e GraphQL, pannelli di amministrazione, form di autenticazione.

Questa sezione ha una **doppia anima**, che la distingue da un semplice archivio di exploit:

- **Red Team:** tecniche offensive per identificare e sfruttare vulnerabilita nelle applicazioni web, seguendo l'OWASP Testing Guide e la metodologia della kill chain (da recon a RCE).
- **Secure Coding:** per ogni vulnerabilita documentata, viene presentato il codice sorgente vulnerabile e il pattern di correzione (Prepared Statements, Output Encoding, Input Validation). Questa prospettiva difensiva dimostra comprensione della causa radice - fondamentale per la redazione di report tecnici professionali.

Il flusso operativo e il seguente: identificazione tecnologia target (`02-web-recon`) → intercettazione traffico (`01-proxy-tools`) → enumerazione risorse (`dir-busting`, `subdomain-enum`) → exploitation OWASP (`03-owasp`) → attacchi CMS specifici (`04-cms-specific`) → test API (`05-api-security`) → verifica remediation (`06-secure-coding-lab`).

---

## Struttura della cartella

```
03-web-attacks (Red Team + Secure Coding)/
+-- 01-proxy-tools (Intercept)/      # Burp Suite, OWASP ZAP, certificati HTTPS
|   +-- burp-suite/                  # Traffic interception, User-Agent spoofing
|   +-- certificates/                # Installazione CA Burp per HTTPS MitM
|   +-- owasp-zap/                   # DAST scanner, finding WEB-001 (CSRF)
+-- 02-web-recon (Enumeration)/      # Ricognizione specifica delle applicazioni web
|   +-- dir-busting/                 # Gobuster/Feroxbuster, finding WEB-003
|   +-- subdomain-enum/              # Subfinder, OWASP Amass, VHost fuzzing
|   +-- tech-profiler/               # WhatWeb, Wappalyzer, finding WEB-002
|   +-- vulnerability-scanners/      # Nikto, Nuclei (template-based)
+-- 03-owasp (Attacks)/              # Exploitation OWASP Top 10:2021
|   +-- auth-attacks/                # Brute Force (WEB-009), Session Hijacking (WEB-010)
|   +-- sql-injection (SQLi)/        # SQLi manuale (WEB-004), sqlmap (WEB-011)
|   +-- ssti/                        # SSTI Jinja2 RCE (WEB-008)
|   +-- xss (Cross-Site Scripting)/  # Reflected (WEB-005), Stored (WEB-006), Blind (WEB-007)
+-- 04-cms-specific/                 # CMS fingerprinting e exploitation mirata
|   +-- drupal/                      # CVE-2018-7600 Drupalgeddon2 (WEB-015)
|   +-- wordpress/                   # WPScan: enumerazione e brute force
|   +-- joomla/                      # JoomScan: fingerprinting e CVE-2023-23752
+-- 05-api-security/                 # OWASP API Top 10:2023
|   +-- jwt-tokens/                  # JWT weak secret + token forging (WEB-012)
|   +-- graphql/                     # GraphQL Introspection + Command Injection (WEB-013)
|   +-- postman/                     # IDOR/BOLA + dati finanziari altrui (WEB-014)
+-- 06-secure-coding-lab (Defense)/  # Analisi SAST, codice vulnerabile vs. patchato
    +-- vulnerable-snippets/         # Codice con OS Command Injection e SQLi (CWE-78, CWE-89)
    +-- fixed-snippets/              # Codice corretto con Prepared Statements
        +-- input-sanitization-examples/  # Output encoding XSS (htmlspecialchars)
```

---

## Flusso operativo consigliato

```
[1] Proxy Setup
     +-- Burp Suite / OWASP ZAP  ->  intercettare il traffico HTTP/HTTPS
              |
              v
[2] Web Recon (differente dalla Network Recon)
     +-- tech-profiler     ->  identificare stack tecnologico e versioni
     +-- dir-busting       ->  trovare risorse nascoste e pannelli admin
     +-- subdomain-enum    ->  espandere superficie di attacco
     +-- vuln-scanners     ->  scan automatico Nikto/Nuclei
              |
              v
[3] CMS Detection?
     +-- SI  ->  04-cms-specific (WPScan / JoomScan / Drupalgeddon2)
     +-- NO  ->  continua con OWASP attacks
              |
              v
[4] OWASP Exploitation (03-owasp)
     +-- auth-attacks     ->  brute force, session hijacking
     +-- sql-injection    ->  manuale (UNION, Blind) poi sqlmap
     +-- xss              ->  reflected, stored, blind OOB
     +-- ssti             ->  Jinja2 -> RCE
              |
              v
[5] API Security (05-api-security)
     +-- jwt-tokens       ->  crack chiave, forging token admin
     +-- graphql          ->  introspection, command injection
     +-- postman          ->  IDOR/BOLA enumeration
              |
              v
[6] Verifica Remediation (06-secure-coding-lab)
     +-- confronto codice vulnerabile vs. patchato
     +-- re-test con stessi payload
```

---

## Registro Finding - Modulo 03-web-attacks

| ID | Descrizione | Severity | CVSS v3.1 | Sottocartella |
| :--- | :--- | :---: | :---: | :--- |
| `WEB-001` | Assenza token CSRF - form non protetti da Cross-Site Request Forgery | `Medio` | 5.4 | `01-proxy-tools/owasp-zap/` |
| `WEB-002` | PHP 5.6.40 EOL + header X-Powered-By esposto | `Alto` | 7.5 | `02-web-recon/tech-profiler/` |
| `WEB-003` | Directory CVS e cartella .idea esposti pubblicamente | `Alto` | 7.5 | `02-web-recon/dir-busting/` |
| `WEB-004` | SQL Injection manuale: auth bypass e UNION-based data exfiltration | `Critico` | 9.8 | `03-owasp/sql-injection/manual-payloads/` |
| `WEB-005` | XSS Reflected - input URL riflesso senza encoding | `Medio` | 6.1 | `03-owasp/xss/reflected/` |
| `WEB-006` | XSS Stored - payload persistente nel database (profilo utente) | `Alto` | 8.2 | `03-owasp/xss/stored/` |
| `WEB-007` | XSS Blind/OOB - callback su webhook.site da area admin | `Alto` | 8.2 | `03-owasp/xss/xss-hunter-payloads/` |
| `WEB-008` | SSTI Jinja2 - Remote Code Execution tramite template injection | `Critico` | 9.8 | `03-owasp/ssti/` |
| `WEB-009` | Brute Force autenticazione web - assenza rate limiting e lockout | `Alto` | 7.5 | `03-owasp/auth-attacks/bruteforce-web/` |
| `WEB-010` | Session Hijacking - cookie privo di flag HttpOnly e Secure | `Alto` | 8.0 | `03-owasp/auth-attacks/session-hijacking/` |
| `WEB-011` | SQLi automatizzata sqlmap - dump completo DB con PAN carte di credito | `Critico` | 9.8 | `03-owasp/sql-injection/sql-map-data/` |
| `WEB-012` | JWT weak secret (secret123) - token forging con ruolo admin | `Critico` | 9.8 | `05-api-security/jwt-tokens/` |
| `WEB-013` | GraphQL Introspection abilitata + Command Injection RCE | `Critico` | 9.8 | `05-api-security/graphql/` |
| `WEB-014` | IDOR/BOLA - accesso dati finanziari di altri utenti senza autorizzazione | `Critico` | 9.1 | `05-api-security/postman/` |
| `WEB-015` | Drupal CVE-2018-7600 Drupalgeddon2 - RCE e Web Shell su Windows | `Critico` | 9.8 | `04-cms-specific/drupal/` |

---

## Mappatura MITRE ATT&CK - Aggregata

| Tattica | Tecnica | ID MITRE | Finding Correlato |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Active Scanning: Vulnerability Scanning | `T1595.002` | WEB-001, WEB-002, WEB-003 |
| Reconnaissance | Active Scanning: Wordlist Scanning | `T1595.003` | WEB-003, WEB-013 |
| Reconnaissance | Gather Victim Host Info: Software | `T1592.002` | WEB-002 |
| Reconnaissance | Gather Victim Network Info: Domain Properties | `T1590.001` | (subdomain-enum) |
| Collection | Man-in-the-Middle | `T1557` | WEB-001 (OWASP ZAP proxy) |
| Collection | Browser Session Hijacking | `T1185` | WEB-007, WEB-010 |
| Credential Access | Brute Force: Password Guessing | `T1110.001` | WEB-009 |
| Credential Access | Brute Force: Password Spraying | `T1110.004` | WEB-009 |
| Credential Access | Brute Force: Password Cracking | `T1110.002` | WEB-012 |
| Credential Access | Steal Web Session Cookie | `T1539` | WEB-005, WEB-006, WEB-007, WEB-010 |
| Initial Access | Exploit Public-Facing Application | `T1190` | WEB-004, WEB-005, WEB-006, WEB-008, WEB-011, WEB-015 |
| Execution | Command and Scripting Interpreter: Unix Shell | `T1059.004` | WEB-013 |
| Execution | Command and Scripting Interpreter: Python | `T1059.006` | WEB-008 |
| Persistence | Server Software Component: Web Shell | `T1505.003` | WEB-006, WEB-015 |
| Defense Evasion | Subvert Trust Controls: Install Root Certificate | `T1553.004` | (certificates) |
| Defense Evasion | Use Alternate Authentication Material: Web Session Cookie | `T1550.004` | WEB-010 |
| Defense Evasion | Use Alternate Authentication Material | `T1550` | WEB-012 |
| Discovery | File and Directory Discovery | `T1083` | WEB-003, WEB-008 |
| Discovery | Account Discovery | `T1087` | WEB-004, WEB-014 |
| Discovery | Network Service Scanning | `T1046` | (vulnerability-scanners) |
| Collection | Data from Information Repositories | `T1213` | WEB-003, WEB-004, WEB-011, WEB-013, WEB-014 |
| Exfiltration | Exfiltration Over Web Service | `T1567` | WEB-011 |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | WEB-005 |
| Lateral Movement | Valid Accounts | `T1078` | WEB-014 |
| Lateral Movement | Valid Accounts: Cloud Accounts | `T1078.003` | WEB-012 |
| Reconnaissance | Gather Victim Identity Information | `T1589` | WEB-007 |
| Collection | Man-in-the-Middle: AiTM HTTPS Interception | `T1557.002` | WEB-010 |

---

> **Nota:** Tutte le attivita documentate in questo modulo sono state condotte su ambienti di laboratorio
> intenzionalmente vulnerabili (`testphp.vulnweb.com`, DVGA, macchine virtuali locali) o su target
> autorizzati nell'ambito di attivita didattiche. Replicare queste tecniche su sistemi senza esplicita
> autorizzazione scritta costituisce un reato penale ai sensi del D.Lgs. 231/2001 e della normativa
> vigente in materia di crimini informatici (art. 615-ter c.p.).
