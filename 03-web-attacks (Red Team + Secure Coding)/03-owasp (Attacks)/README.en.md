> **English** | [Italiano](README.md)

# 03 - OWASP Attacks

> - **Phase:** Web Attack - OWASP Top 10:2021 Exploitation
> - **Visibility:** Variable - from Medium (HTTP requests with payloads) to High (automated scanners and brute force attacks)
> - **Prerequisites:** Technology stack identified (`02-web-recon`), proxy configured (`01-proxy-tools`), input endpoints identified
> - **Output:** Findings WEB-004..011, proof of concept for each OWASP vulnerability, remediation with secure code

---

## Introduction

The OWASP Top 10 is the list of the most critical vulnerabilities in web applications, periodically updated by the Open Web Application Security Project Foundation. The 2021 version introduces new categories compared to previous ones: Insecure Design (A04), Security Logging and Monitoring Failures (A09) and Server-Side Request Forgery (A10).

This section documents the practical exploitation of the most relevant OWASP categories identified in the target `testphp.vulnweb.com` and in local lab environments:

| OWASP Top 10:2021 Category | Related Finding | Subfolder |
| :--- | :--- | :--- |
| A01:2021 - Broken Access Control | WEB-010 (Session Hijacking) | `auth-attacks/` |
| A02:2021 - Cryptographic Failures | WEB-010 (cookie without Secure flag) | `auth-attacks/` |
| A03:2021 - Injection | WEB-004, WEB-008, WEB-011 | `sql-injection/`, `ssti/` |
| A07:2021 - Identification & Auth Failures | WEB-009 (Brute Force), WEB-010 | `auth-attacks/` |
| A03:2021 - Injection (XSS) | WEB-005, WEB-006, WEB-007 | `xss/` |

The philosophy of this section is the **dual perspective**: every offensive technique is accompanied by root cause analysis and the secure fix pattern, because understanding the why of a vulnerability is equally important for an analyst as knowing how to exploit it.

---

## Folder Structure

```
03-owasp (Attacks)/
+-- auth-attacks/             # Authentication and session management
|   +-- bruteforce-web/       # Hydra on HTTP/POST form - WEB-009
|   +-- session-hijacking/    # Cookie stealing, XSS, ARP spoofing - WEB-010
+-- sql-injection (SQLi)/     # SQL Injection on MySQL
|   +-- manual-payloads/      # Auth bypass, UNION-based, data dump - WEB-004
|   +-- sql-map-data/         # Automated sqlmap + PCI-DSS violation - WEB-011
+-- ssti/                     # Server-Side Template Injection Jinja2 - WEB-008
+-- xss (Cross-Site Scripting)/  # Cross-Site Scripting
    +-- reflected/            # Reflected XSS on URL parameter - WEB-005
    +-- stored/               # Stored XSS on profile field - WEB-006
    +-- xss-hunter-payloads/  # Blind XSS with OOB callback - WEB-007
```

---

## `auth-attacks/` - Authentication & Session Attacks

### Operational Context

Authentication and session management vulnerabilities are among the most impactful because they allow impersonation of legitimate users, including administrators. The difference between Brute Force and Session Hijacking is the attack point: the first attacks credentials (before login), the second attacks the already established session (after login).

See `auth-attacks/README.md` for the complete guide.

**Findings:** `WEB-009` (Brute Force) and `WEB-010` (Session Hijacking).

---

## `sql-injection (SQLi)/` - SQL Injection

### Operational Context

SQL Injection is one of the most long-lived and devastating vulnerabilities in the web landscape. It consists of injecting arbitrary SQL commands through unsanitized user input, allowing the attacker to manipulate database queries.

The main types:
- **Error-based:** the database returns error messages with structural information.
- **UNION-based:** allows adding arbitrary query results to the response.
- **Blind Boolean-based:** the application responds differently to true/false conditions.
- **Time-based Blind:** response delay is used to infer information (e.g., `SLEEP(5)`).

The root cause is almost always the same: direct concatenation of user input in the SQL string, instead of using Prepared Statements.

See `sql-injection/README.md` for the complete guide.

**Findings:** `WEB-004` (manual) and `WEB-011` (automated sqlmap).

---

## `ssti/` - Server Side Template Injection

### Operational Context

SSTI is a critical vulnerability that occurs when user input is inserted directly into the template before the rendering engine processes it. The engine then interprets the input as template code (e.g., `{{ 7*7 }}` in Jinja2) instead of simple text.

SSTI often allows reaching Remote Code Execution because modern template engines (Jinja2, Twig, Freemarker) have access to underlying language classes that allow invoking system commands.

**Finding:** `WEB-008` (SSTI Jinja2 RCE).

---

## `xss (Cross-Site Scripting)/` - XSS

### Operational Context

Cross-Site Scripting allows an attacker to inject arbitrary JavaScript code that is executed in the victim's browser within the context of the legitimate domain. This bypasses the Same-Origin Policy and allows access to cookies, the DOM and saved credentials.

The three variants have different impact and visibility:

| Variant | Persistence | Target | Visibility |
| :--- | :--- | :--- | :--- |
| Reflected (WEB-005) | No (per request) | Whoever clicks the malicious link | Low (URL with payload) |
| Stored (WEB-006) | Yes (in database) | All page visitors | Zero (payload is in DB) |
| Blind/OOB (WEB-007) | Yes | Management panel admin | Zero (payload is server-side) |

Stored XSS (WEB-006) is the most critical in terms of impact because it affects all users without requiring specific interaction, and often leads to administrator session cookie theft.

---

## Recommended Operational Flow

```
[1] Identify input points
     +-- login, search, comment forms
     +-- URL parameters (GET)
     +-- HTTP headers (User-Agent, Referer)
              |
              v
[2] Test for SQL Injection (sql-injection/)
     +-- manual payload: ' OR 1=1 --
     +-- if vulnerable: UNION-based dump -> sqlmap --dump
              |
              v
[3] Test for XSS (xss/)
     +-- payload: <script>alert(1)</script>
     +-- if reflected -> Reflected XSS (WEB-005)
     +-- if persistent -> Stored XSS (WEB-006)
     +-- if in admin area -> Blind XSS (WEB-007)
              |
              v
[4] Test for SSTI (ssti/)
     +-- payload: {{ 7*7 }} -> if returns 49 -> SSTI confirmed
     +-- escalation to RCE: {{ self.__init__.__globals__ ... }}
              |
              v
[5] Test authentication (auth-attacks/)
     +-- brute force: hydra -l <USER> -P passlist.txt
     +-- session hijacking: XSS + document.cookie
```

---

## Finding Registry - OWASP Attacks

| ID | Description | Severity | CVSS | Subfolder |
| :--- | :--- | :---: | :---: | :--- |
| `WEB-004` | Manual SQL Injection: auth bypass and UNION-based data exfiltration | `Critical` | 9.8 | `sql-injection/manual-payloads/` |
| `WEB-005` | XSS Reflected - URL input reflected without encoding | `Medium` | 6.1 | `xss/reflected/` |
| `WEB-006` | XSS Stored - persistent payload in database | `High` | 8.2 | `xss/stored/` |
| `WEB-007` | XSS Blind/OOB - callback to webhook.site from admin area | `High` | 8.2 | `xss/xss-hunter-payloads/` |
| `WEB-008` | SSTI Jinja2 - Remote Code Execution via template injection | `Critical` | 9.8 | `ssti/` |
| `WEB-009` | Web authentication Brute Force - missing rate limiting | `High` | 7.5 | `auth-attacks/bruteforce-web/` |
| `WEB-010` | Session Hijacking - cookie missing HttpOnly and Secure flags | `High` | 8.0 | `auth-attacks/session-hijacking/` |
| `WEB-011` | Automated SQLi - complete DB dump with credit card PANs | `Critical` | 9.8 | `sql-injection/sql-map-data/` |

---

## MITRE ATT&CK Mapping - Aggregated

| Tactic | Technique | MITRE ID | Related Finding |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | WEB-004, WEB-005, WEB-006, WEB-008, WEB-011 |
| Credential Access | Brute Force: Password Guessing | `T1110.001` | WEB-009 |
| Credential Access | Brute Force: Password Spraying | `T1110.004` | WEB-009 |
| Credential Access | Steal Web Session Cookie | `T1539` | WEB-005, WEB-006, WEB-007, WEB-010 |
| Collection | Man-in-the-Middle: AiTM HTTPS Interception | `T1557.002` | WEB-010 |
| Collection | Browser Session Hijacking | `T1185` | WEB-007, WEB-010 |
| Execution | Command and Scripting Interpreter: Python | `T1059.006` | WEB-008 |
| Execution | Command and Scripting Interpreter: Unix Shell | `T1059.004` | WEB-008 |
| Persistence | Server Software Component: Web Shell | `T1505.003` | WEB-006 |
| Defense Evasion | Use Alternate Authentication Material: Web Session Cookie | `T1550.004` | WEB-010 |
| Discovery | Account Discovery: Local Account | `T1087.001` | WEB-004 |
| Discovery | File and Directory Discovery | `T1083` | WEB-008 |
| Collection | Data from Information Repositories | `T1213` | WEB-004, WEB-011 |
| Exfiltration | Exfiltration Over Web Service | `T1567` | WEB-011 |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | WEB-005 |
| Reconnaissance | Gather Victim Identity Information | `T1589` | WEB-007 |
| Credential Access | Modify Authentication Process | `T1556` | WEB-009 |

---

> **Note:** All exploitation activities documented in this section were conducted on intentionally vulnerable lab environments: `testphp.vulnweb.com` (Acunetix Art, public test environment) and local Flask/Python applications. Any similar activity on real systems requires prior written authorization from the owner.
