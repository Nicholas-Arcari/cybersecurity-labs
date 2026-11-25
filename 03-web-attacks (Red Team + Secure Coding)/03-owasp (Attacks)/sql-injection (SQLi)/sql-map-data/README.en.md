> **English** | [Italiano](README.md)

# Automated vulnerability assessment: SQL injection & data exfiltration

> - **Phase:** Web Attack - SQL Injection (Automated)
> - **Visibility:** High - sqlmap generates heavy HTTP traffic in short time, easily detectable by WAF and IDS
> - **Prerequisites:** Vulnerable endpoint identified (also through manual test WEB-004), `sqlmap` installed (preinstalled on Kali)
> - **Output:** DBMS fingerprint, table dump, complete data exfiltration (credentials, credit card PANs), finding WEB-011

---

**Finding ID:** `WEB-011` | **Severity:** `Critical` | **CVSS v3.1:** 9.8

---

## 1 Executive summary

During the automated Security Assessment activity, a critical SQL Injection vulnerability was detected on the `artists.php` endpoint.

Using the SQLMap tool allowed automating the entire attack process, confirming the possibility of injecting arbitrary commands into the backend database (MySQL).

The impact is assessed as Catastrophic for the following reasons:

- Total Exfiltration: It was possible to download the entire user database.
- PCI-DSS Violation: Credit Card numbers (PAN) stored in plaintext were found.
- Insecure Credential Management: User passwords are saved in plaintext, without any Hashing function.

---

## 2 Technical execution

#### Phase 1: vulnerability scanning & fingerprinting

In this initial phase, the tool queried the server to identify the database type and current user. 4 attack vectors were detected (Boolean-based, Error-based, Time-based, UNION query).

Command:

```Bash
sqlmap -u "http://testphp.vulnweb.com/artists.php?artist=1" --banner --current-user --current-db --is-dba
```

![](./img/Screenshot_2026-02-15_17_16_46.jpg)

Result (Recon):

- DBMS: MySQL >= 5.1
- Current Database: `acuart`
- Current User: `acuart@localhost` (Not DBA)

#### Phase 2: database enumeration

Once the target database (`acuart`) was identified, table enumeration was performed to map the data structure and locate sensitive information.

Command:

```Bash
sqlmap -u "http://testphp.vulnweb.com/artists.php?artist=1" -D acuart --tables
```

![](./img/Screenshot_2026-02-15_17_17_36.jpg)

Result:

8 tables were identified. The `users` table was selected as the primary target for exfiltration.

#### Phase 3: data exfiltration (the breach)

Having confirmed the presence of the `users` table, a complete dump of columns containing credentials and personal data was performed.

Command:

```Bash
sqlmap -u "http://testphp.vulnweb.com/artists.php?artist=1" -D acuart -T users --dump --batch
```

![](./img/Screenshot_2026-02-15_17_19_26.jpg)

Output Analysis (Evidence):

The screenshot below shows the successful data extraction. SQLMap generated a CSV report containing sensitive records, including passwords and credit cards.

Local File Path:

The complete dump was saved locally at: `~/.local/share/sqlmap/output/testphp.vulnweb.com/dump/acuart/users.csv`

---

## 3 Risk analysis & compliance

The extracted data analysis highlights severe violations of security best practices and international regulations.

| extracted data | example value | violation / risk |
| --------------- | ---------------- | ---------------------- |
| password | test | CRITICAL. passwords are saved in plaintext (cleartext). total lack of hashing (e.g., bcrypt, argon2) and salting. an attacker can immediately impersonate any user. |
| credit card (cc) | 1234-5678... | CRITICAL (pci-dss). storing the pan (primary account number) in plaintext is a direct violation of pci-dss requirement 3.4. |
| pii data | email, phone, address | HIGH (gdpr). personal data exposure that can lead to identity theft and significant administrative penalties. |

---

## 4 Remediation plan

To secure the infrastructure, the following immediate corrective actions are recommended:

- Secure Code (Preventive):
    
  - Implement Prepared Statements (Parameterized Queries) throughout all PHP code to neutralize SQL injection at its root.

- Data Protection (Corrective):

  - Passwords: Immediately migrate all user passwords to strong hashing algorithms (e.g., `bcrypt` or `Argon2id`). Never store passwords in plaintext.

  - Credit Cards: Never store complete credit card data unless strictly necessary. If required, use tokenization through Payment Gateway or strong encryption (AES-256) with secure key management.

- Infrastructure:

  - Implement a Web Application Firewall (WAF) (e.g., ModSecurity or Cloudflare services) to block known SQLMap attack patterns and malicious requests.

---

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | automated exploitation with sqlmap of the `artist` parameter vulnerable to sql injection on `testphp.vulnweb.com` (WEB-011) |
| collection | data from information repositories | `T1213` | complete dump of the `acuart` database through sqlmap, including the `users` table with plaintext passwords and credit card pan numbers (WEB-011) |
| exfiltration | exfiltration over web service | `T1567` | database dump saved in local csv format at `~/.local/share/sqlmap/output/` (WEB-011) |

---

> **Note:** The sqlmap scan was conducted on `testphp.vulnweb.com`, Acunetix's public training environment. The CSV dump with credentials and credit card PANs was treated as sensitive data and not published in this repository. Finding WEB-011 includes a PCI-DSS Requirement 3.4 violation (plaintext PAN storage) that in a real engagement would require immediate client notification and incident response procedure.
