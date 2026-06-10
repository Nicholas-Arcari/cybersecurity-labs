> **English** | [Italiano](README.md)

# 03 - Web Attacks (Red Team + Secure Coding)

> - **Phase:** Web Application Penetration Testing
> - **Visibility:** Variable - from Zero (passive code analysis) to High (automated scanners like Nikto)
> - **Prerequisites:** Completion of module 01-recon (HTTP/HTTPS attack surface identified), module 02-vulnerability-assessment (target technologies known)
> - **Output:** Documented findings WEB-001..015, working payloads, exploitation evidence, remediation for each vulnerability

---

## Introduction

Module `03-web-attacks` represents the operational core of a modern penetration test. The majority of corporate attack surface is now exposed via web (HTTP/HTTPS): CMS applications, REST and GraphQL APIs, administration panels, authentication forms.

This section has a **dual nature**, which distinguishes it from a simple exploit archive:

- **Red Team:** offensive techniques to identify and exploit vulnerabilities in web applications, following the OWASP Testing Guide and the kill chain methodology (from recon to RCE).
- **Secure Coding:** for each documented vulnerability, the vulnerable source code and the correction pattern (Prepared Statements, Output Encoding, Input Validation) are presented. This defensive perspective demonstrates root cause understanding - essential for writing professional technical reports.

The operational flow is as follows: target technology identification (`02-web-recon`) -> traffic interception (`01-proxy-tools`) -> resource enumeration (`dir-busting`, `subdomain-enum`) -> OWASP exploitation (`03-owasp`) -> CMS-specific attacks (`04-cms-specific`) -> API testing (`05-api-security`) -> remediation verification (`06-secure-coding-lab`).

---

## Folder Structure

```
03-web-attacks (Red Team + Secure Coding)/
+-- 01-proxy-tools (Intercept)/      # Burp Suite, OWASP ZAP, HTTPS certificates
|   +-- burp-suite/                  # Traffic interception, User-Agent spoofing
|   +-- certificates/                # Burp CA installation for HTTPS MitM
|   +-- owasp-zap/                   # DAST scanner, finding WEB-001 (CSRF)
+-- 02-web-recon (Enumeration)/      # Web application-specific reconnaissance
|   +-- dir-busting/                 # Gobuster/Feroxbuster, finding WEB-003
|   +-- subdomain-enum/              # Subfinder, OWASP Amass, VHost fuzzing
|   +-- tech-profiler/               # WhatWeb, Wappalyzer, finding WEB-002
|   +-- vulnerability-scanners/      # Nikto, Nuclei (template-based)
+-- 03-owasp (Attacks)/              # OWASP Top 10:2021 Exploitation
|   +-- auth-attacks/                # Brute Force (WEB-009), Session Hijacking (WEB-010)
|   +-- sql-injection (SQLi)/        # Manual SQLi (WEB-004), sqlmap (WEB-011)
|   +-- ssti/                        # SSTI Jinja2 RCE (WEB-008)
|   +-- xss (Cross-Site Scripting)/  # Reflected (WEB-005), Stored (WEB-006), Blind (WEB-007)
+-- 04-cms-specific/                 # CMS fingerprinting and targeted exploitation
|   +-- drupal/                      # CVE-2018-7600 Drupalgeddon2 (WEB-015)
|   +-- wordpress/                   # WPScan: enumeration and brute force
|   +-- joomla/                      # JoomScan: fingerprinting and CVE-2023-23752
+-- 05-api-security/                 # OWASP API Top 10:2023
|   +-- jwt-tokens/                  # JWT weak secret + token forging (WEB-012)
|   +-- graphql/                     # GraphQL Introspection + Command Injection (WEB-013)
|   +-- postman/                     # IDOR/BOLA + other users' financial data (WEB-014)
+-- 06-secure-coding-lab (Defense)/  # SAST analysis, vulnerable vs. patched code
    +-- vulnerable-snippets/         # Code with OS Command Injection and SQLi (CWE-78, CWE-89)
    +-- fixed-snippets/              # Corrected code with Prepared Statements
        +-- input-sanitization-examples/  # XSS Output encoding (htmlspecialchars)
```

---

## Recommended Operational Flow

```
[1] Proxy Setup
     +-- Burp Suite / OWASP ZAP  ->  intercept HTTP/HTTPS traffic
              |
              v
[2] Web Recon (different from Network Recon)
     +-- tech-profiler     ->  identify technology stack and versions
     +-- dir-busting       ->  find hidden resources and admin panels
     +-- subdomain-enum    ->  expand attack surface
     +-- vuln-scanners     ->  automated Nikto/Nuclei scan
              |
              v
[3] CMS Detection?
     +-- YES ->  04-cms-specific (WPScan / JoomScan / Drupalgeddon2)
     +-- NO  ->  continue with OWASP attacks
              |
              v
[4] OWASP Exploitation (03-owasp)
     +-- auth-attacks     ->  brute force, session hijacking
     +-- sql-injection    ->  manual (UNION, Blind) then sqlmap
     +-- xss              ->  reflected, stored, blind OOB
     +-- ssti             ->  Jinja2 -> RCE
              |
              v
[5] API Security (05-api-security)
     +-- jwt-tokens       ->  crack key, admin token forging
     +-- graphql          ->  introspection, command injection
     +-- postman          ->  IDOR/BOLA enumeration
              |
              v
[6] Remediation Verification (06-secure-coding-lab)
     +-- vulnerable vs. patched code comparison
     +-- re-test with same payloads
```

---

## Finding Registry - Module 03-web-attacks

| ID | Description | Severity | CVSS v3.1 | Subfolder |
| :--- | :--- | :---: | :---: | :--- |
| `WEB-001` | Missing CSRF token - forms unprotected against Cross-Site Request Forgery | `Medium` | 5.4 | `01-proxy-tools/owasp-zap/` |
| `WEB-002` | PHP 5.6.40 EOL + X-Powered-By header exposed | `High` | 7.5 | `02-web-recon/tech-profiler/` |
| `WEB-003` | CVS directory and .idea folder publicly exposed | `High` | 7.5 | `02-web-recon/dir-busting/` |
| `WEB-004` | Manual SQL Injection: auth bypass and UNION-based data exfiltration | `Critical` | 9.8 | `03-owasp/sql-injection/manual-payloads/` |
| `WEB-005` | XSS Reflected - URL input reflected without encoding | `Medium` | 6.1 | `03-owasp/xss/reflected/` |
| `WEB-006` | XSS Stored - persistent payload in database (user profile) | `High` | 8.2 | `03-owasp/xss/stored/` |
| `WEB-007` | XSS Blind/OOB - callback to webhook.site from admin area | `High` | 8.2 | `03-owasp/xss/xss-hunter-payloads/` |
| `WEB-008` | SSTI Jinja2 - Remote Code Execution via template injection | `Critical` | 9.8 | `03-owasp/ssti/` |
| `WEB-009` | Web authentication Brute Force - missing rate limiting and lockout | `High` | 7.5 | `03-owasp/auth-attacks/bruteforce-web/` |
| `WEB-010` | Session Hijacking - cookie missing HttpOnly and Secure flags | `High` | 8.0 | `03-owasp/auth-attacks/session-hijacking/` |
| `WEB-011` | Automated SQLi sqlmap - complete DB dump with credit card PANs | `Critical` | 9.8 | `03-owasp/sql-injection/sql-map-data/` |
| `WEB-012` | JWT weak secret (secret123) - token forging with admin role | `Critical` | 9.8 | `05-api-security/jwt-tokens/` |
| `WEB-013` | GraphQL Introspection enabled + Command Injection RCE | `Critical` | 9.8 | `05-api-security/graphql/` |
| `WEB-014` | IDOR/BOLA - unauthorized access to other users' financial data | `Critical` | 9.1 | `05-api-security/postman/` |
| `WEB-015` | Drupal CVE-2018-7600 Drupalgeddon2 - RCE and Web Shell on Windows | `Critical` | 9.8 | `04-cms-specific/drupal/` |

---

## MITRE ATT&CK Mapping - Aggregated

| Tactic | Technique | MITRE ID | Related Finding |
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

> **Note:** All activities documented in this module were conducted on intentionally vulnerable lab environments (`testphp.vulnweb.com`, DVGA, local virtual machines) or on authorized targets within educational activities. Replicating these techniques on systems without explicit written authorization constitutes a criminal offense under applicable cybercrime legislation.
