> **English** | [Italiano](README.md)

# 04 - Infrastructure intelligence

> - **Phase:** Reconnaissance - Infrastructure Intelligence Gathering
> - **Visibility:** Zero / Low - search on public databases, standard HTTP fingerprinting
> - **Prerequisites:** Target domain or IP range identified, Shodan/Censys account (free tier sufficient)
> - **Output:** Exposed assets with RDP/VoIP/FTP on public IPs (INTEL-001, INTEL-002, INTEL-003), target technology profile (INTEL-004)

---

## Introduction

Infrastructure Intelligence is the reconnaissance phase that leverages public databases built by automated scanners that continuously sweep the entire IPv4 address space of the Internet. Tools like Shodan and Censys archive the banners and certificates of every publicly reachable service, allowing analysts to "see" any organization's infrastructure without sending a single packet towards it.

The operational advantage is twofold:
- **For the Red Team:** a complete and historical external attack surface map is obtained, including software versions, open ports, TLS certificates and configurations in extremely reduced time
- **For the defender:** these databases are accessible to anyone, including ransomware groups. If a corporate asset appears on Shodan with exposed RDP, it is already in the crosshairs of automated malicious actors

This phase completes the organization profile built in previous phases:
- `01-osint-passive/` identified emails, employees and credentials
- `03-dns-enumeration/` mapped subdomains and DNS records
- **This section** connects the data to services exposed on the Internet and identifies the tech stack

Tech stack fingerprinting is directly connected to the `02-vulnerability-assessment/` module: knowing that a server runs Apache 2.4.49 allows immediately searching for the corresponding CVE.

---

## Folder structure

```
04-infrastructure-intel/
+-- README.md                <- this file (index + finding registry)
|
+-- shodan-censys/
|   +-- README.md            <- INTEL-001..003: exposed RDP/VoIP/FTP assets (Shodan, Censys, Whois)
|   +-- img/                 <- lab screenshots
|
+-- tech-stack/
    +-- README.md            <- INTEL-004: technology fingerprinting (WhatWeb, Wappalyzer)
    +-- img/                 <- lab screenshots
```

---

## `shodan-censys/` - Asset intelligence from public databases

**Finding ID:** `INTEL-001` | **Severity:** `High`
**Finding ID:** `INTEL-002` | **Severity:** `High`
**Finding ID:** `INTEL-003` | **Severity:** `Critical`

The Shodan and Censys analysis of the city of Parma (educational case study) revealed three categories of critically exposed assets:

- **INTEL-001:** 60+ devices with publicly exposed RDP (port 3389), with Information Disclosure of hostnames and operating system
- **INTEL-002:** Personal/corporate workstation with RDP + non-standard Apache + management services exposed on business public IP - the classic "forgotten PC under the desk"
- **INTEL-003:** Single corporate server simultaneously managing VoIP (3CX), File Server (FileZilla FTP), Remote Desktop and Plex Media Server on a consumer ADSL line - critical attack surface with single point of failure

Cross-validation between Shodan (service and banner identification) and Censys (TLS certificate analysis) confirmed target identities and discovered additional services not visible in the initial analysis.

---

## `tech-stack/` - Tech stack fingerprinting

**Finding ID:** `INTEL-004` | **Severity:** `Informational`

Tech Stack Fingerprinting identifies the underlying technologies of a web application by analyzing HTTP responses, cookies, headers and source code. Knowing the CMS, web server and client-side libraries allows selecting the correct exploits during the exploitation phase.

**Lab result on `tesla.com`:** WhatWeb blocked by Akamai WAF (403 Forbidden). However, the response itself revealed the use of Akamai as CDN/WAF and the presence of HSTS. Tesla's perimeter defenses prevent automated backend fingerprinting.

**Operational lesson:** against targets with enterprise WAF (Akamai, Cloudflare, F5), passive fingerprinting via Wappalyzer or BuiltWith is more effective than active scanners.

---

## Recommended operational flow

```
[INPUT] Target domain or IP range
          |
          v
[1] Shodan Query (Zero-Touch)
     +-- ip:<TARGET_IP>                     # specific IP analysis
     +-- hostname:<DOMAIN>                  # services by domain
     +-- port:3389 org:"<COMPANY>"          # exposed RDP by org
     +-- port:22 vuln:CVE-XXXX-YYYY         # specific vulnerable hosts
     -> Asset map: IPs, ports, banners, versions, OS
          |
          v
[2] Censys Cross-Reference (Zero-Touch)
     +-- ip:<TARGET_IP>                     # validation and new findings
     -> TLS certificate analysis, new services, identity confirmation
          |
          v
[3] Whois (Zero-Touch)
     +-- whois <IP>                         # ISP, abuse contacts, AS number
     -> Connection type identification (datacenter vs consumer), real geolocation
          |
          v
[4] Tech Stack Fingerprinting (Low Visibility)
     +-- whatweb -v <DOMAIN>                # single HTTP request
     +-- Wappalyzer browser extension       # passive analysis during browsing
     +-- BuiltWith web                      # historical tech stack database
     -> CMS, frameworks, libraries, versions
          |
          v
[OUTPUT] Complete asset map -> 02-vulnerability-assessment/ (CVE lookup for found versions)
```

---

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `Shodan` | scan database | web / cli (`shodan`) | exposed asset search by ip, port, banner, cve |
| `Censys` | scan database | web | tls certificate analysis, shodan validation |
| `Whois` | osint | cli | isp, abuse contacts, real geolocation |
| `WhatWeb` | tech fingerprint | cli | web technology fingerprinting via http request |
| `Wappalyzer` | tech fingerprint | browser extension | passive fingerprinting during browsing |
| `BuiltWith` | tech fingerprint | web | historical tech stack database by domain |
| `FOFA` | scan database | web | asian alternative to shodan, useful for specific targets |
| `Netlas.io` | scan database | web | modern alternative to shodan with advanced queries |

> **Recommended modern tool:** `Shodan CLI` (`pip install shodan`, `shodan init <API_KEY>`) - allows automating Shodan queries in scripts and integrating results into automated OSINT workflows. Example command: `shodan search "port:3389 city:Parma" --fields ip_str,port,org`.

---

## Finding registry

| id | description | severity | file |
| :--- | :--- | :---: | :--- |
| `INTEL-001` | 60+ devices with exposed rdp in parma - hostnames and os detected | `High` | `shodan-censys/README.md` |
| `INTEL-002` | workstation with rdp + apache on non-standard port + management services on public ip | `High` | `shodan-censys/README.md` |
| `INTEL-003` | corporate server with voip (3cx) + ftp (filezilla) + rdp on consumer adsl | `Critical` | `shodan-censys/README.md` |
| `INTEL-004` | tesla.com protected by akamai waf - fingerprinting blocked, hsts active | `Informational` | `tech-stack/README.md` |

---

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| reconnaissance | search open technical databases: scan databases | `T1596.005` | search for exposed assets on shodan and censys by ip and port, identifying public rdp, voip, ftp (INTEL-001, INTEL-002, INTEL-003) |
| reconnaissance | gather victim network info: network topology | `T1590.004` | target infrastructure mapping through shodan banner analysis and censys tls certificates (INTEL-001, INTEL-002, INTEL-003) |
| reconnaissance | gather victim host info: software | `T1592.002` | tech stack fingerprinting through whatweb and wappalyzer to identify cms, web server and framework (INTEL-004) |

---

> **Note:** Shodan and Censys searches were conducted for exclusively educational purposes to document Infrastructure Intelligence methodologies. Identified targets (real companies with exposed assets) were reported following the Responsible Disclosure principle. No access or exploitation attempts were conducted on third-party systems.
