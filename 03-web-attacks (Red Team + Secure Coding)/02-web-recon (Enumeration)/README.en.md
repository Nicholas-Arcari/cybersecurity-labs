> **English** | [Italiano](README.md)

# 02 - Web recon (enumeration)

> - **Phase:** Web Attack - Web Application Enumeration
> - **Visibility:** Variable - Low (tech profiling with standard HTTP requests) / Medium (dir-busting and scanners generate heavy traffic) / Low (passive subdomain enum)
> - **Prerequisites:** Web target identified from module `01-recon`, proxy configured (`01-proxy-tools`)
> - **Output:** Map of hidden resources, technology stack and software versions, subdomains, findings WEB-002 and WEB-003

---

## Introduction

Web reconnaissance is a distinct and complementary phase to the network recon of module `01-recon`. While that phase identifies IPs, open ports and network services, here the focus is exclusively on the HTTP/HTTPS application layer.

The operational distinction is fundamental:

| network recon (`01-recon`) | web recon (`02-web-recon`) |
| :--- | :--- |
| open ports and services (`nmap`) | hidden pages and directories (`gobuster`) |
| hostname and dns | hidden virtual hosts (`gobuster vhost`) |
| service banners (`nc`, `telnet`) | technology stack and versions (`whatweb`) |
| ip and asn | web subdomains (`subfinder`, `amass`) |
| network vulnerabilities (`nmap NSE`) | application vulnerabilities (`nikto`, `nuclei`) |

Web recon is the prerequisite for any OWASP attack: without knowing that the target uses PHP 5.6 (WEB-002) or exposes `/CVS` (WEB-003), subsequent phases would be conducted blindly.

The modern reference tool for this phase is `nuclei` (ProjectDiscovery), which combines technology fingerprinting and vulnerability scanning in a single tool based on YAML templates updated daily by the community.

---

## Folder structure

```
02-web-recon (Enumeration)/
+-- dir-busting/            # Gobuster, Feroxbuster - finding WEB-003
+-- subdomain-enum/         # Subfinder, OWASP Amass, VHost fuzzing
+-- tech-profiler/          # WhatWeb, Wappalyzer - finding WEB-002
+-- vulnerability-scanners/ # Nikto (legacy), Nuclei (modern)
```

---

## `tech-profiler/` - Technology fingerprinting

**Finding ID:** `WEB-002` | **Severity:** `High` | **CVSS v3.1:** 7.5

### Operational context

Before launching any attack, an analyst must know "what the target is made of". Tech profiling analyzes HTTP headers, source code, cookies and resource paths to identify the exact software and versions in use.

The direct result is **CVE mapping**: knowing that the server uses PHP 5.6.40 (End of Life), one searches for known exploits on Exploit-DB specific to that version, instead of wasting time with generic attacks. See section `02-vulnerability-assessment/03-cve-analysis/` for the CVE research workflow.

Main tools:
- `whatweb`: CLI scanner, header analysis and CMS fingerprinting.
- `Wappalyzer`: browser extension, passive fingerprinting while browsing.

Finding WEB-002 is documented in detail in `tech-profiler/README.md`.

---

## `dir-busting/` - Directory & file enumeration

**Finding ID:** `WEB-003` | **Severity:** `High` | **CVSS v3.1:** 7.5

### Operational context

Web applications often expose resources that do not appear in navigable links: administration panels (`/admin`), backup files (`.bak`, `.old`), version control directories (`.git`, `CVS`), IDE configuration files (`.idea`).

Dir-busting is an active brute force technique: the tool sends thousands of HTTP requests, one for each wordlist entry, and analyzes response status codes to determine which resources exist.

The status code is the primary signal:
- `200 OK`: existing and accessible resource.
- `301/302 Redirect`: existing directory (often indicates `/admin` or similar).
- `403 Forbidden`: existing resource but access denied (interesting for subsequent escalation).
- `404 Not Found`: resource not present.

Finding WEB-003 (CVS directory and `.idea` exposed) is documented in detail in `dir-busting/README.md`.

---

## `subdomain-enum/` - Subdomain enumeration

### Operational context

The target organization rarely exposes a single domain. The ecosystem includes subdomains for staging environments, VPN, SSO portals, APIs, CDNs. These secondary subdomains are often less monitored and updated than the main domain, making them privileged targets.

Techniques are divided into:
- **Passive:** querying Certificate Transparency Logs, VirusTotal, Censys, SecurityTrails. Zero interaction with the target.
- **Active:** DNS brute force with wordlists, zone transfers, VHost fuzzing. Generates traffic towards the target.

The produced subdomain list becomes direct input for the next phase: each subdomain is a potential entry point to test with dir-busting and tech profiling.

---

## `vulnerability-scanners/` - Automated web scanning

### Operational context

Web vulnerability scanners automate the search for misconfigurations and default files by comparing server responses against databases of known signatures. They complement tech profiling with an exploit-oriented perspective.

The operational distinction between the two main scanners:

| scanner | approach | speed | waf detection | ideal use |
| :--- | :--- | :--- | :--- | :--- |
| `Nikto` | signature-based (legacy) | slow | easy | initial baseline, lab |
| `Nuclei` | yaml templates (modern) | fast | difficult | ci/cd pipelines, real engagements |

Nikto is known for being very "noisy" (generates many anomalous requests) and is easily blocked by WAFs in production environments. Nuclei, based on specific YAML templates, is more precise and less detectable.

Findings WEB-002 (PHP EOL) and WEB-003 (.idea exposure) were also confirmed by Nuclei through the `php-eol` and `idea-folder-exposure` templates.

---

## Recommended operational flow

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

## Finding registry - web recon

| id | description | severity | subfolder |
| :--- | :--- | :---: | :--- |
| `WEB-002` | php 5.6.40 eol + `X-Powered-By` header exposed | `High` | `tech-profiler/` |
| `WEB-003` | cvs directory and `.idea` folder publicly exposed | `High` | `dir-busting/` |

---

## Reference tools

| tool | type | technique/access | primary use case |
| :--- | :--- | :--- | :--- |
| `whatweb` | tech fingerprint | cli - active | cms, web server, languages and version identification |
| `Wappalyzer` | tech fingerprint | browser extension - passive | visual fingerprint while browsing |
| `gobuster` | dir/vhost brute force | cli - active | directory busting and vhost fuzzing |
| `feroxbuster` | dir brute force | cli - active | recursive dir busting, faster than gobuster |
| `subfinder` | subdomain enum | cli - passive | passive enumeration from ct logs and osint |
| `amass` | subdomain/asn enum | cli - active | deep mapping with asn and reverse whois |
| `nikto` | vulnerability scanner | cli - active | general baseline, server misconfiguration |
| `nuclei` | vulnerability scanner | cli - active | yaml templates, cve-specific, ci/cd pipelines |
| `httpx` | http prober | cli - active | quick verification of which subdomains are active |

> **Recommended modern tool:** `nuclei` (ProjectDiscovery) - replaces Nikto for most modern use cases. Each template is mapped to specific CVEs or CWEs, reducing false positives. Template update: `nuclei -update-templates`.

---

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| reconnaissance | active scanning: vulnerability scanning | `T1595.002` | scanning with nikto and nuclei to identify php eol, exposed headers and sensitive files (WEB-002, WEB-003) |
| reconnaissance | active scanning: wordlist scanning | `T1595.003` | directory busting with gobuster/feroxbuster on `common.txt` wordlist to enumerate hidden resources (WEB-003) |
| reconnaissance | gather victim host info: software | `T1592.002` | tech profiling with whatweb to identify php 5.6.40, nginx 1.19 and technology stack (WEB-002) |
| reconnaissance | gather victim network info: domain properties | `T1590.001` | subdomain enumeration with subfinder and owasp amass to expand the attack surface |
| discovery | file and directory discovery | `T1083` | identification of cvs directory, `.idea` and `/admin` through dir-busting (WEB-003) |
| discovery | network service scanning | `T1046` | automated nikto/nuclei scanning to identify services and versions on the target |
| collection | data from information repositories | `T1213` | potential access to source code through exposed cvs directory that could allow downloading application source files (WEB-003) |

---

> **Note:** The web recon activities documented were conducted on `testphp.vulnweb.com` (authorized public test environment by Acunetix) and on `tesla.com` limited to passive subdomain enumeration from public OSINT sources (Certificate Transparency Logs). Active reconnaissance on unauthorized targets is illegal under applicable cybercrime legislation.
