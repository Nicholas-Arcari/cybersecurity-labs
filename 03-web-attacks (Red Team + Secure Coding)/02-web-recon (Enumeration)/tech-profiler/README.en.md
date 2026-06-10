> **English** | [Italiano](README.md)

# Web Recon: Tech Profiling & Fingerprinting

> - **Phase:** Web Attack - Technology Fingerprinting
> - **Visibility:** Low - standard HTTP requests similar to normal browser navigation
> - **Prerequisites:** Web target identified, `whatweb` preinstalled on Kali, `Wappalyzer` extension in browser
> - **Output:** Complete technology stack (web server, language, CMS, versions), finding WEB-002 (PHP 5.6.40 EOL + X-Powered-By header)

---

**Finding ID:** `WEB-002` | **Severity:** `High` | **CVSS v3.1:** 7.5

---

Objective: Identify the target's "Technology Stack" (Operating System, Web Server, Framework, Languages) to target the search for known vulnerabilities (CVE).

Target: `http://testphp.vulnweb.com`

Tools: `WhatWeb` (CLI), `Wappalyzer` (Browser Extension)

---

## 1 Theoretical Introduction

Fingerprinting is the art of understanding "what a website is made of" by analyzing server responses.

Web technologies leave unique digital fingerprints:

- HTTP Headers: `Server: Apache/2.4.41` or `X-Powered-By: PHP/7.4`.
- Source Code: Folder structure (e.g., `/wp-content/` indicates WordPress).
- Cookies: Specific names like `JSESSIONID` (Java) or `PHPSESSID` (PHP).

This phase is crucial for an attacker: knowing the exact version of software allows searching for specific Public Exploits on databases like Exploit-DB.

Why does a Red Teamer want to know these things?

- CVE Mapping (The main reason):

    - If WhatWeb tells me the site uses PHP 5.6.40, I go to Google and search: "PHP 5.6.40 vulnerabilities". I will discover it is old and full of holes.
    - If it tells me WordPress 4.8, I search for exploits for that specific version. I don't waste time launching Joomla attacks if the site is WordPress.

- Default Credentials:

    - If I discover the server is Tomcat, I will try logging in with tomcat:s3cret.
    - If it is Jenkins, I will try admin:password.
    - Knowing the technology gives you the key to guessing the default password.

- WAF Detection:

    - These tools often tell you if there is a WAF (Web Application Firewall) like Cloudflare or Imperva. If you know that, you know you need to use evasion techniques (or give up to avoid getting banned).
        
---

## 2 Tools Used

### WhatWeb (Active Scanner)

Command-line tool preinstalled on Kali Linux. Performs a quick scan identifying CMS, blogging platforms, JavaScript libraries and web servers. Supports different aggressiveness levels.

### Wappalyzer (Passive)

Usually used as a browser extension, it identifies technologies by passively analyzing the loaded page. Useful for an immediate visual verification without sending suspicious scanning packets.

---

## 3 Technical Execution: WhatWeb Scan

A detailed scan (`-v`) was performed against the target to extract software versions.

```Bash
whatweb -v http://testphp.vulnweb.com
```

![](./img/Screenshot_2026-02-12_19_12_54.jpg)

![](./img/Screenshot_2026-02-12_19_13_00.jpg)

Findings Analysis: The output reveals critical information for the next attack phase:

- Web Server: Nginx 1.19.0. Knowing it is Nginx and not Apache changes the configuration techniques and files to look for (e.g., .htaccess does not work on Nginx).
- Language: PHP 5.6.40. Critical Finding. This PHP version is obsolete (End of Life) and suffers from numerous known vulnerabilities that could allow Remote Code Execution (RCE).
- Framework: No complex CMS (like WordPress) detected, suggesting a custom application ("Home of Acunetix Art").

---

## 4 Conclusions

Tech Profiling confirmed that the target runs on legacy infrastructure (PHP 5.6). This information narrows the field of action: instead of launching generic attacks, a Red Team would now search for specific exploits for PHP 5.6 or configuration vulnerabilities typical of Nginx 1.19.

---

## 5 Special Scenarios: Localhost & Static Sites

Tech Profiling takes on different meanings depending on the target environment.

#### A. Localhost / Docker (Hardening)

When running WhatWeb against local development environments (`localhost:5173`), the objective is not attack but Hardening.

Modern frameworks (e.g., Express.js, Flask, Spring Boot) expose by default headers like `X-Powered-By` or `Server` that reveal precise runtime versions.

Best Practice: Identifying these leaks locally allows the developer to disable them (e.g., `app.disable('x-powered-by')` in Express) before production deployment.

#### B. Static Hosting (GitHub Pages)

When analyzing static sites like `https://nicholas-arcari.github.io`, the web server is managed by the provider (GitHub) and therefore out of attack scope.
Attention shifts to Client-Side Libraries.

WhatWeb and Wappalyzer are fundamental for detecting obsolete JavaScript library versions (e.g., jQuery < 3.0, old Bootstrap) that often contain known DOM-based XSS vulnerabilities, exploitable directly in the victim's browser without touching the server.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Host Info: Software | `T1592.002` | Tech profiling with WhatWeb and Wappalyzer to identify PHP 5.6.40, Nginx 1.19.0 and the complete technology stack of `testphp.vulnweb.com` (WEB-002) |
| Reconnaissance | Active Scanning: Vulnerability Scanning | `T1595.002` | HTTP header analysis (e.g., `X-Powered-By: PHP/5.6.40`) to map software versions and identify applicable CVEs (WEB-002) |

---

> **Note:** Tech profiling was conducted on `testphp.vulnweb.com` (Acunetix) and on `nicholas-arcari.github.io` (personal static site). Finding WEB-002 (PHP 5.6.40 EOL) is documented as an example of typical misconfiguration. In a real engagement, this information would be classified as "Confidential" and used exclusively for planning subsequent test phases.
