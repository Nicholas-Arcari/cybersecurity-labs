> **English** | [Italiano](README.md)

# 02 - Web Recon (Enumeration)

> - **Phase:** Web Attack - Web Application Enumeration
> - **Visibility:** Variable - Low (tech profiling with standard HTTP requests) / Medium (dir-busting and scanners generate heavy traffic) / Low (passive subdomain enum)
> - **Prerequisites:** Web target identified from module `01-recon`, proxy configured (`01-proxy-tools`)
> - **Output:** Map of hidden resources, technology stack and software versions, subdomains, findings WEB-002 and WEB-003

---

## Introduction

Web reconnaissance is a distinct and complementary phase to the network recon of module `01-recon`. While that phase identifies IPs, open ports and network services, here the focus is exclusively on the HTTP/HTTPS application layer.

The operational distinction is fundamental:

| Network Recon (`01-recon`) | Web Recon (`02-web-recon`) |
| :--- | :--- |
| Open ports and services (`nmap`) | Hidden pages and directories (`gobuster`) |
| Hostname and DNS | Hidden virtual hosts (`gobuster vhost`) |
| Service banners (`nc`, `telnet`) | Technology stack and versions (`whatweb`) |
| IP and ASN | Web subdomains (`subfinder`, `amass`) |
| Network vulnerabilities (`nmap NSE`) | Application vulnerabilities (`nikto`, `nuclei`) |

Web recon is the prerequisite for any OWASP attack: without knowing that the target uses PHP 5.6 (WEB-002) or exposes `/CVS` (WEB-003), subsequent phases would be conducted blindly.

The modern reference tool for this phase is `nuclei` (ProjectDiscovery), which combines technology fingerprinting and vulnerability scanning in a single tool based on YAML templates updated daily by the community.

---

## Folder Structure

```
02-web-recon (Enumeration)/
+-- dir-busting/            # Gobuster, Feroxbuster - finding WEB-003
+-- subdomain-enum/         # Subfinder, OWASP Amass, VHost fuzzing
+-- tech-profiler/          # WhatWeb, Wappalyzer - finding WEB-002
+-- vulnerability-scanners/ # Nikto (legacy), Nuclei (modern)
```

---

## `tech-profiler/` - Technology Fingerprinting

**Finding ID:** `WEB-002` | **Severity:** `High` | **CVSS v3.1:** 7.5

### Operational Context

Before launching any attack, an analyst must know "what the target is made of". Tech profiling analyzes HTTP headers, source code, cookies and resource paths to identify the exact software and versions in use.

The direct result is **CVE mapping**: knowing that the server uses PHP 5.6.40 (End of Life), one searches for known exploits on Exploit-DB specific to that version, instead of wasting time with generic attacks. See section `02-vulnerability-assessment/03-cve-analysis/` for the CVE research workflow.

Main tools:
- `whatweb`: CLI scanner, header analysis and CMS fingerprinting.
- `Wappalyzer`: browser extension, passive fingerprinting while browsing.

Finding WEB-002 is documented in detail in `tech-profiler/README.md`.

---

## `dir-busting/` - Directory & File Enumeration

**Finding ID:** `WEB-003` | **Severity:** `High` | **CVSS v3.1:** 7.5

### Operational Context

Web applications often expose resources that do not appear in navigable links: administration panels (`/admin`), backup files (`.bak`, `.old`), version control directories (`.git`, `CVS`), IDE configuration files (`.idea`).

Dir-busting is an active brute force technique: the tool sends thousands of HTTP requests, one for each wordlist entry, and analyzes response status codes to determine which resources exist.

The status code is the primary signal:
- `200 OK`: existing and accessible resource.
- `301/302 Redirect`: existing directory (often indicates `/admin` or similar).
- `403 Forbidden`: existing resource but access denied (interesting for subsequent escalation).
- `404 Not Found`: resource not present.

Finding WEB-003 (CVS directory and `.idea` exposed) is documented in detail in `dir-busting/README.md`.

---

## `subdomain-enum/` - Subdomain Enumeration

### Operational Context

The target organization rarely exposes a single domain. The ecosystem includes subdomains for staging environments, VPN, SSO portals, APIs, CDNs. These secondary subdomains are often less monitored and updated than the main domain, making them privileged targets.

Techniques are divided into:
- **Passive:** querying Certificate Transparency Logs, VirusTotal, Censys, SecurityTrails. Zero interaction with the target.
- **Active:** DNS brute force with wordlists, zone transfers, VHost fuzzing. Generates traffic towards the target.

The produced subdomain list becomes direct input for the next phase: each subdomain is a potential entry point to test with dir-busting and tech profiling.

---

## `vulnerability-scanners/` - Automated Web Scanning

### Operational Context

Web vulnerability scanners automate the search for misconfigurations and default files by comparing server responses against databases of known signatures. They complement tech profiling with an exploit-oriented perspective.

The operational distinction between the two main scanners:

| Scanner | Approach | Speed | WAF Detection | Ideal Use |
| :--- | :--- | :--- | :--- | :--- |
| `Nikto` | Signature-based (legacy) | Slow | Easy | Initial baseline, lab |
| `Nuclei` | YAML templates (modern) | Fast | Difficult | CI/CD pipelines, real engagements |

Nikto is known for being very "noisy" (generates many anomalous requests) and is easily blocked by WAFs in production environments. Nuclei, based on specific YAML templates, is more precise and less detectable.

Findings WEB-002 (PHP EOL) and WEB-003 (.idea exposure) were also confirmed by Nuclei through the `php-eol` and `idea-folder-exposure` templates.

---

## Recommended Operational Flow

```
[1] Tech Profiling (tech-profiler/)
     +-- whatweb -v <TARGET>          ->  technology stack and versions
     +-- Wappalyzer (browser)         ->  passive confirmation
         |
         v
[2] CVE Mapping (02-vulnerability-assessment/03-cve-analysis/)
     +-- if PHP 5.6 -> search CVEs for PHP 5.6.x
     +-- if WordPress X.Y -> search CVEs for that specific version
         |
         v
[3] Dir Busting (dir-busting/)
     +-- gobuster dir -u <TARGET> -w common.txt
     +-- feroxbuster -u <TARGET> (recursive)
         |
         v
[4] Subdomain Enum (subdomain-enum/)
     +-- subfinder -d <DOMAIN>         ->  passive
     +-- amass enum -d <DOMAIN>        ->  active + ASN mapping
     +-- gobuster vhost (for local labs)
         |
         v
[5] Automated Scan (vulnerability-scanners/)
     +-- nikto -h <TARGET>             ->  general baseline
     +-- nuclei -u <TARGET>            ->  template-based (more precise)
```

---

## Finding Registry - Web Recon

| ID | Description | Severity | Subfolder |
| :--- | :--- | :---: | :--- |
| `WEB-002` | PHP 5.6.40 EOL + `X-Powered-By` header exposed | `High` | `tech-profiler/` |
| `WEB-003` | CVS directory and `.idea` folder publicly exposed | `High` | `dir-busting/` |

---

## Reference Tools

| Tool | Type | Technique/Access | Primary Use Case |
| :--- | :--- | :--- | :--- |
| `whatweb` | Tech fingerprint | CLI - Active | CMS, web server, languages and version identification |
| `Wappalyzer` | Tech fingerprint | Browser Extension - Passive | Visual fingerprint while browsing |
| `gobuster` | Dir/VHost brute force | CLI - Active | Directory busting and VHost fuzzing |
| `feroxbuster` | Dir brute force | CLI - Active | Recursive dir busting, faster than gobuster |
| `subfinder` | Subdomain enum | CLI - Passive | Passive enumeration from CT logs and OSINT |
| `amass` | Subdomain/ASN enum | CLI - Active | Deep mapping with ASN and reverse WHOIS |
| `nikto` | Vulnerability scanner | CLI - Active | General baseline, server misconfiguration |
| `nuclei` | Vulnerability scanner | CLI - Active | YAML templates, CVE-specific, CI/CD pipelines |
| `httpx` | HTTP prober | CLI - Active | Quick verification of which subdomains are active |

> **Recommended modern tool:** `nuclei` (ProjectDiscovery) - replaces Nikto for most modern use cases. Each template is mapped to specific CVEs or CWEs, reducing false positives. Template update: `nuclei -update-templates`.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Active Scanning: Vulnerability Scanning | `T1595.002` | Scanning with Nikto and Nuclei to identify PHP EOL, exposed headers and sensitive files (WEB-002, WEB-003) |
| Reconnaissance | Active Scanning: Wordlist Scanning | `T1595.003` | Directory busting with Gobuster/Feroxbuster on `common.txt` wordlist to enumerate hidden resources (WEB-003) |
| Reconnaissance | Gather Victim Host Info: Software | `T1592.002` | Tech profiling with WhatWeb to identify PHP 5.6.40, Nginx 1.19 and technology stack (WEB-002) |
| Reconnaissance | Gather Victim Network Info: Domain Properties | `T1590.001` | Subdomain enumeration with Subfinder and OWASP Amass to expand the attack surface |
| Discovery | File and Directory Discovery | `T1083` | Identification of CVS directory, `.idea` and `/admin` through dir-busting (WEB-003) |
| Discovery | Network Service Scanning | `T1046` | Automated Nikto/Nuclei scanning to identify services and versions on the target |
| Collection | Data from Information Repositories | `T1213` | Potential access to source code through exposed CVS directory that could allow downloading application source files (WEB-003) |

---

> **Note:** The web recon activities documented were conducted on `testphp.vulnweb.com` (authorized public test environment by Acunetix) and on `tesla.com` limited to passive subdomain enumeration from public OSINT sources (Certificate Transparency Logs). Active reconnaissance on unauthorized targets is illegal under applicable cybercrime legislation.
