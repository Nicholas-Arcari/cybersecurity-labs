> **English** | [Italiano](README.md)

# SQL Injection (SQLi)

> - **Phase:** Web Attack - SQL Injection Testing
> - **Visibility:** Medium - HTTP requests with payload in URL parameter or POST body
> - **Prerequisites:** Endpoint with dynamic parameters identified, known database stack (MySQL, MSSQL, PostgreSQL), proxy configured
> - **Output:** Finding WEB-004 (manual injection), WEB-011 (sqlmap), complete database dump, auth bypass proof of concept

---

## Introduction

SQL Injection is one of the most long-lived and devastating vulnerabilities in the web security landscape. Classified by OWASP as A03:2021 (Injection), it allows an attacker to insert arbitrary SQL commands into application input, manipulating queries to the backend database.

The root cause is almost always the same: **direct concatenation of user input in the SQL string** instead of using Prepared Statements (parameterized queries). This practice allows the attacker to modify the logical structure of the query, not just its values.

The main types of SQLi and their mechanisms:

| Type | Mechanism | When to Use |
| :--- | :--- | :--- |
| Error-based | The database returns error messages with structural info | Known technology stack, verbose messages |
| UNION-based | Adds arbitrary query results to the normal response | The original query returns visible output |
| Boolean-based Blind | The app responds differently to true/false conditions | No direct output, only binary behavior |
| Time-based Blind | `SLEEP(N)` is used to infer information from delay | No output, no behavioral difference |
| Out-of-Band | The app exfiltrates data to an external server (DNS, HTTP) | Perimeter defenses block other techniques |

---

## Folder Structure

```
sql-injection (SQLi)/
+-- manual-payloads/   # Auth bypass, UNION-based, manual data dump - WEB-004
+-- sql-map-data/      # Automated sqlmap - WEB-011
```

---

## `manual-payloads/` - Manual SQL Injection

**Finding ID:** `WEB-004` | **Severity:** `Critical` | **CVSS v3.1:** 9.8

### Operational Context

The manual approach to SQLi is fundamental for two reasons. First, it allows understanding exactly how the vulnerable query works, revealing the database structure and present defenses. Second, it is often necessary when sqlmap is blocked by the WAF or when the server response format is non-standard.

The document `manual-payloads/README.md` covers three progressive scenarios:
- **Scenario A (Auth Bypass):** payload `admin' #` to bypass login without knowing the password. The `#` character comments out the password check in the MySQL query.
- **Scenario B (UNION-based):** column count enumeration, visible column identification, database fingerprinting (version, current user).
- **Scenario C (Complete Data Dump):** access to `information_schema.tables` to list tables, then dump of usernames, passwords and credit card data from the `users` table.

### Remediation

- **Immediate action:** disable verbose database error messages in production (prevents fingerprinting).
- **Structural action:** rewrite all queries using Prepared Statements (PDO in PHP, `PreparedStatement` in Java, ORM with parameterized queries).
- **Principle of Least Privilege:** the database user used by the app should not have access to `information_schema` or unnecessary write permissions.
- **Verification:** use sqlmap (`--level=5 --risk=3`) on the patched code to confirm there are no more injection vectors.

---

## `sql-map-data/` - Automated SQLi with sqlmap

**Finding ID:** `WEB-011` | **Severity:** `Critical` | **CVSS v3.1:** 9.8

### Operational Context

sqlmap is the standard tool for automated verification and exploitation of SQL Injection. Unlike the manual approach, sqlmap automatically detects the injection type (boolean, error, union, time-based), the backend database and its version, and automates the entire data exfiltration process.

The document `sql-map-data/README.md` documents the complete exploitation of the `artists.php` endpoint:
- **Phase 1 (Fingerprinting):** identification of DBMS (MySQL 5.1+), current user (`acuart@localhost`) and active database (`acuart`).
- **Phase 2 (Database Enum):** dump of the 8 tables in database `acuart`.
- **Phase 3 (Data Exfiltration):** complete dump of the `users` table with local CSV saving.

Finding WEB-011 presents a critical PCI-DSS violation: credit card numbers (PAN) are stored in plaintext in the database, constituting a direct violation of PCI-DSS Requirement 3.4.

### Remediation

- **Immediate:** Prepared Statements on all endpoints (see `manual-payloads/`).
- **Passwords:** migrate to bcrypt/Argon2id with salting. Never store passwords in plaintext.
- **Card PANs:** tokenization through PCI-DSS certified Payment Gateway. Never store the complete card number unless strictly necessary.
- **WAF:** ModSecurity or Cloudflare WAF with SQLi ruleset to block known sqlmap patterns.

---

## Recommended Operational Flow

```
[1] Identify endpoints with dynamic parameters
     +-- URL GET: ?id=1, ?artist=1, ?cat=3
     +-- POST Forms: login, search, filters
              |
              v
[2] Manual confirmation test (manual-payloads/)
     +-- payload: ' -> SQL error? (confirms injection)
     +-- payload: ' OR 1=1 -- -> auth bypass?
     +-- payload: ORDER BY N -> column count
              |
              v
[3] UNION-based enumeration (if output visible)
     +-- UNION SELECT 1,2,3 -> which columns are visible?
     +-- UNION SELECT 1,version(),user() -> fingerprinting
     +-- UNION SELECT ... FROM information_schema.tables -> table listing
              |
              v
[4] Automate with sqlmap (sql-map-data/)
     +-- sqlmap -u "URL?param=1" --banner --current-db --current-user
     +-- sqlmap -u "URL?param=1" -D <DB> --tables
     +-- sqlmap -u "URL?param=1" -D <DB> -T users --dump
```

---

## Reference Tools

| Tool | Type | Technique/Access | Primary Use Case |
| :--- | :--- | :--- | :--- |
| `sqlmap` | SQL Injection framework | CLI - Active | Automated exploitation, database dump |
| `Burp Suite Repeater` | Web proxy | GUI - Manual | Manual iterative SQL payload testing |
| `Burp Suite Intruder` | Web proxy | GUI - Semi-auto | Parameter fuzzing with payload lists |
| `ghauri` | Modern SQLi tool | CLI - Active | sqlmap alternative, improved WAF evasion |
| `havij` | SQLi framework | GUI - Active | Legacy tool (unmaintained), avoid in prod |

> **Recommended modern tool:** `ghauri` - modern alternative to sqlmap with better WAF evasion capabilities and support for advanced injection techniques. Installation: `pip3 install ghauri`.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | SQL Injection exploitation on the `artist` parameter and login form of `testphp.vulnweb.com` (WEB-004, WEB-011) |
| Discovery | Account Discovery: Local Account | `T1087.001` | Database user enumeration through UNION injection on `information_schema.tables` (WEB-004) |
| Collection | Data from Information Repositories | `T1213` | Complete dump of `users` table with plaintext credentials and credit card PANs (WEB-004, WEB-011) |
| Exfiltration | Exfiltration Over Web Service | `T1567` | Database dump saved to local CSV file through sqlmap (WEB-011) |
| Credential Access | Brute Force: Password Guessing | `T1110.001` | Use of extracted credentials (`test:test`) to access the application (WEB-004) |

---

> **Note:** The SQL Injection activities documented were conducted on `testphp.vulnweb.com`, Acunetix's intentionally vulnerable public training environment. Database dumps containing credentials and credit card numbers were treated as sensitive data and not published in this repository. In a real engagement, such data would be classified as "Strictly Confidential" and delivered to the client in encrypted form exclusively.
