> **English** | [Italiano](README.md)

# 03 - OWASP attacks

> - **Phase:** Web Attack - OWASP Top 10:2021 Exploitation
> - **Visibility:** Variable - from Medium (HTTP requests with payloads) to High (automated scanners and brute force attacks)
> - **Prerequisites:** Technology stack identified (`02-web-recon`), proxy configured (`01-proxy-tools`), input endpoints identified
> - **Output:** Findings WEB-004..011, proof of concept for each OWASP vulnerability, remediation with secure code

---

## Introduction

The OWASP Top 10 is the list of the most critical vulnerabilities in web applications, periodically updated by the Open Web Application Security Project Foundation. The 2021 version introduces new categories compared to previous ones: Insecure Design (A04), Security Logging and Monitoring Failures (A09) and Server-Side Request Forgery (A10).

This section documents the practical exploitation of the most relevant OWASP categories identified in the target `testphp.vulnweb.com` and in local lab environments:

| owasp top 10:2021 category | related finding | subfolder |
| :--- | :--- | :--- |
| A01:2021 - broken access control | WEB-010 (session hijacking) | `auth-attacks/` |
| A02:2021 - cryptographic failures | WEB-010 (cookie without secure flag) | `auth-attacks/` |
| A03:2021 - injection | WEB-004, WEB-008, WEB-011 | `sql-injection/`, `ssti/` |
| A07:2021 - identification & auth failures | WEB-009 (brute force), WEB-010 | `auth-attacks/` |
| A03:2021 - injection (xss) | WEB-005, WEB-006, WEB-007 | `xss/` |
| A03:2021 - injection (extended family) | methodology (no lab) | `ldap-injection/`, `xpath-injection/`, `crlf-injection/`, `command-injection/` |
| A05:2021 - security misconfiguration (xxe) | methodology (no lab) | `xxe (XML External Entity)/` |
| A08:2021 - software & data integrity (deserialization) | methodology (no lab) | `deserialization (Insecure Deserialization)/` |

The philosophy of this section is the **dual perspective**: every offensive technique is accompanied by root cause analysis and the secure fix pattern, because understanding the why of a vulnerability is equally important for an analyst as knowing how to exploit it.

> **Methodology pages.** Besides the lab findings (WEB-004..011), the section includes methodology pages that
> complete the injection family and the related OWASP categories (XXE, deserialization, LDAP/XPath/CRLF/Command
> Injection). They have illustrative outputs and **no fabricated Finding ID**: the next available ID is
> `WEB-016`, to assign when the techniques are executed in a lab.

---

## Folder structure

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
|   +-- reflected/            # Reflected XSS on URL parameter - WEB-005
|   +-- stored/               # Stored XSS on profile field - WEB-006
|   +-- xss-hunter-payloads/  # Blind XSS with OOB callback - WEB-007
|
|   # --- Methodology pages (no lab, no fabricated Finding ID) ---
+-- xxe (XML External Entity)/           # XXE: file read / SSRF (A05) - methodology
+-- deserialization (Insecure Deserialization)/  # Insecure deserialization (A08) - methodology
+-- ldap-injection (LDAP Injection)/     # LDAP Injection: AD auth bypass, directory enum - methodology
+-- xpath-injection (XPath Injection)/   # XPath Injection: auth bypass, XML extraction - methodology
+-- crlf-injection (CRLF Injection)/     # CRLF / HTTP response splitting, log injection - methodology
+-- command-injection (OS Command Injection)/  # OS Command Injection: RCE - methodology
```

---

## `auth-attacks/` - Authentication & session attacks

### Operational context

Authentication and session management vulnerabilities are among the most impactful because they allow impersonation of legitimate users, including administrators. The difference between Brute Force and Session Hijacking is the attack point: the first attacks credentials (before login), the second attacks the already established session (after login).

See `auth-attacks/README.md` for the complete guide.

**Findings:** `WEB-009` (Brute Force) and `WEB-010` (Session Hijacking).

---

## `sql-injection (SQLi)/` - SQL injection

### Operational context

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

## `ssti/` - Server side template injection

### Operational context

SSTI is a critical vulnerability that occurs when user input is inserted directly into the template before the rendering engine processes it. The engine then interprets the input as template code (e.g., `{{ 7*7 }}` in Jinja2) instead of simple text.

SSTI often allows reaching Remote Code Execution because modern template engines (Jinja2, Twig, Freemarker) have access to underlying language classes that allow invoking system commands.

**Finding:** `WEB-008` (SSTI Jinja2 RCE).

---

## `xss (Cross-Site Scripting)/` - XSS

### Operational context

Cross-Site Scripting allows an attacker to inject arbitrary JavaScript code that is executed in the victim's browser within the context of the legitimate domain. This bypasses the Same-Origin Policy and allows access to cookies, the DOM and saved credentials.

The three variants have different impact and visibility:

| variant | persistence | target | visibility |
| :--- | :--- | :--- | :--- |
| reflected (WEB-005) | no (per request) | whoever clicks the malicious link | Low (url with payload) |
| stored (WEB-006) | yes (in database) | all page visitors | zero (payload is in db) |
| blind/oob (WEB-007) | yes | management panel admin | zero (payload is server-side) |

Stored XSS (WEB-006) is the most critical in terms of impact because it affects all users without requiring specific interaction, and often leads to administrator session cookie theft.

---

## Recommended operational flow

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

## Finding registry - OWASP attacks

| id | description | severity | cvss | subfolder |
| :--- | :--- | :---: | :---: | :--- |
| `WEB-004` | manual sql injection: auth bypass and union-based data exfiltration | `Critical` | 9.8 | `sql-injection/manual-payloads/` |
| `WEB-005` | xss reflected - url input reflected without encoding | `Medium` | 6.1 | `xss/reflected/` |
| `WEB-006` | xss stored - persistent payload in database | `High` | 8.2 | `xss/stored/` |
| `WEB-007` | xss blind/oob - callback to webhook.site from admin area | `High` | 8.2 | `xss/xss-hunter-payloads/` |
| `WEB-008` | ssti jinja2 - remote code execution via template injection | `Critical` | 9.8 | `ssti/` |
| `WEB-009` | web authentication brute force - missing rate limiting | `High` | 7.5 | `auth-attacks/bruteforce-web/` |
| `WEB-010` | session hijacking - cookie missing httponly and secure flags | `High` | 8.0 | `auth-attacks/session-hijacking/` |
| `WEB-011` | automated sqli - complete db dump with credit card pans | `Critical` | 9.8 | `sql-injection/sql-map-data/` |

---

## MITRE ATT&CK mapping - aggregated

| tactic | technique | mitre id | related finding |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | WEB-004, WEB-005, WEB-006, WEB-008, WEB-011 |
| credential access | brute force: password guessing | `T1110.001` | WEB-009 |
| credential access | brute force: password spraying | `T1110.004` | WEB-009 |
| credential access | steal web session cookie | `T1539` | WEB-005, WEB-006, WEB-007, WEB-010 |
| collection | man-in-the-middle: aitm https interception | `T1557.002` | WEB-010 |
| collection | browser session hijacking | `T1185` | WEB-007, WEB-010 |
| execution | command and scripting interpreter: python | `T1059.006` | WEB-008 |
| execution | command and scripting interpreter: unix shell | `T1059.004` | WEB-008 |
| persistence | server software component: web shell | `T1505.003` | WEB-006 |
| defense evasion | use alternate authentication material: web session cookie | `T1550.004` | WEB-010 |
| discovery | account discovery: local account | `T1087.001` | WEB-004 |
| discovery | file and directory discovery | `T1083` | WEB-008 |
| collection | data from information repositories | `T1213` | WEB-004, WEB-011 |
| exfiltration | exfiltration over web service | `T1567` | WEB-011 |
| initial access | phishing: spearphishing link | `T1566.002` | WEB-005 |
| reconnaissance | gather victim identity information | `T1589` | WEB-007 |
| credential access | modify authentication process | `T1556` | WEB-009 |
| discovery | account discovery: domain account | `T1087.002` | ldap injection (methodology) |
| credential access | unsecured credentials: credentials in files | `T1552.001` | xxe (methodology) |
| execution | command and scripting interpreter: unix shell | `T1059.004` | command injection / deserialization (methodology) |
| execution | command and scripting interpreter: windows command shell | `T1059.003` | command injection (methodology) |
| impact | data manipulation: stored data manipulation | `T1565.001` | crlf injection (methodology) |

> The rows marked "(methodology)" refer to the pages without a Finding ID (XXE, deserialization, LDAP / XPath /
> CRLF / Command Injection); `T1190` and `T1213`, already present, also cover these pages.

---

> **Note:** All exploitation activities documented in this section were conducted on intentionally vulnerable lab environments: `testphp.vulnweb.com` (Acunetix Art, public test environment) and local Flask/Python applications. Any similar activity on real systems requires prior written authorization from the owner.
