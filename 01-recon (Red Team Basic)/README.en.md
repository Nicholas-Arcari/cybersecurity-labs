> **English** | [Italiano](README.md)

# 01 - Reconnaissance (Red Team Basic)

> - **Phase:** Reconnaissance - Pre-engagement Information Gathering
> - **Visibility:** Zero / Low - from passive OSINT to active network scanning
> - **Prerequisites:** Scope definition, written target authorization
> - **Output:** Attack surface map (IPs, domains, emails, technologies, findings OSINT-001..004, SCAN-001..003, DNS-001..003, INTEL-001..004)

---

## Introduction

The Reconnaissance phase is the starting point of any penetration testing activity. Before exploiting a vulnerability, an attacker must know what exists, where it is located and how it is configured. This phase answers fundamental questions: which servers are active? Which domains and subdomains does the organization expose? Which technologies does it use? Who are the employees?

Reconnaissance is divided into two macro-areas that operate in sequence:

1. **Passive (OSINT):** the analyst collects information from public sources without ever directly contacting the target systems. No packets are sent. No logs are generated on the target side. Total invisibility.

2. **Active (Network Scanning):** the analyst sends packets to the target to identify active hosts, open ports and running services. This activity is detectable and must only be performed after obtaining written authorization.

In the Cyber Kill Chain (Lockheed Martin), this phase corresponds to the first stage: **Reconnaissance**. In the MITRE ATT&CK matrix, the techniques in this phase primarily belong to the `Reconnaissance` tactic (TA0043).

---

## Folder Structure

```
01-recon (Red Team Basic)/
+-- README.md                            <- this file (index + finding registry)
|
+-- 01-osint-passive (Open Source Intelligence)/
|   +-- README.md                        <- OSINT index + findings OSINT-001..004
|   +-- breach-data/                     <- OSINT-001: credentials in public breaches
|   +-- email-harvesting/                <- OSINT-002: emails exposed on domain
|   +-- google-dorks/                    <- OSINT-003: indexed files and panels
|   +-- user-enumeration/                <- OSINT-004: identity correlation (Sherlock)
|
+-- 02-network-scanning-active/
|   +-- README.md                        <- network scanning index + findings SCAN-001..003
|   +-- live-host-discovery/             <- SCAN-001: active hosts in subnet
|   +-- port-scanning (Nmap)/
|       +-- masscan/                     <- SCAN-002: high-speed port discovery
|       +-- nmap-scripts/               <- SCAN-003: NSE scripts (SMB signing, NetBIOS)
|
+-- 03-dns-enumeration/
|   +-- README.md                        <- DNS index + findings DNS-001..003
|   +-- dns-recon/                       <- DNS-001: zone transfer, NS records
|   +-- hosts-file/                      <- DNS-002: virtual host via /etc/hosts
|   +-- subdomain-finding/               <- DNS-003: passive subdomains (Sublist3r, Assetfinder)
|
+-- 04-infrastructure-intel/
    +-- README.md                        <- infra intel index + findings INTEL-001..004
    +-- shodan-censys/                   <- INTEL-001..003: exposed assets, RDP, VoIP, FTP
    +-- tech-stack/                      <- INTEL-004: technology fingerprinting (WhatWeb)
```

---

## Recommended Operational Flow

```
[START] Scope defined and authorization obtained
          |
          v
[1] Passive OSINT (invisible)
     +-- breach-data/    -> compromised credentials (h8mail, HIBP)
     +-- email-harvest/  -> exposed emails (theHarvester)
     +-- google-dorks/   -> indexed files and login pages (Google GHDB)
     +-- user-enum/      -> social media presence (Sherlock)
          |
          v
[2] DNS Enumeration (semi-passive)
     +-- dns-recon/      -> zone transfer, NS, MX (dig, dnsenum)
     +-- subdomain/      -> subdomains from CT logs (Sublist3r, Assetfinder)
     +-- hosts-file/     -> unpublished virtual hosts (/etc/hosts)
          |
          v
[3] Infrastructure Intel (passive, from databases)
     +-- shodan-censys/  -> exposed assets, versions, banners (Shodan, Censys)
     +-- tech-stack/     -> technology fingerprint (WhatWeb, Wappalyzer)
          |
          v
[4] Active Network Scanning (requires authorization)
     +-- live-host/      -> ARP/ICMP sweep (arp-scan, nmap -sn)
     +-- masscan/        -> fast port discovery (Masscan)
     +-- nmap-scripts/   -> detailed NSE enumeration (nmap -sC)
          |
          v
[OUTPUT] Attack Surface Map -> input for module 02-vulnerability-assessment/
```

---

## Finding Registry

All findings identified during the Reconnaissance phase are listed below. The "File" column points to the subfolder README containing the complete technical details.

| ID | Description | Severity | File |
| :--- | :--- | :---: | :--- |
| `OSINT-001` | Target credentials identified in public data breaches | `High` | `01-osint-passive/breach-data/` |
| `OSINT-002` | Email exposure on personal domain - minimal attack surface | `Informational` | `01-osint-passive/email-harvesting/` |
| `OSINT-003` | Documents and login panels indexed by Google on nasa.gov | `Variable (Low / High)` | `01-osint-passive/google-dorks/` |
| `OSINT-004` | Identity correlation through username reused across multiple platforms | `Low` | `01-osint-passive/user-enumeration/` |
| `SCAN-001` | Active hosts identified in subnet 10.0.2.0/24 (Windows 10 target) | `Informational` | `02-network-scanning-active/live-host-discovery/` |
| `SCAN-002` | Port discovery with Masscan - false negative in virtualized NAT environment | `Informational` | `02-network-scanning-active/port-scanning (Nmap)/masscan/` |
| `SCAN-003` | SMB Signing not mandatory on 10.0.2.3 - SMB Relay vector enabled | `High` | `02-network-scanning-active/port-scanning (Nmap)/nmap-scripts/` |
| `DNS-001` | Successful Zone Transfer on zonetransfer.me - complete DNS zone exposure | `Critical` | `03-dns-enumeration/dns-recon/` |
| `DNS-002` | Unpublished Virtual Host accessible via /etc/hosts manipulation | `Medium` | `03-dns-enumeration/hosts-file/` |
| `DNS-003` | 500+ tesla.com subdomains passively enumerated (including vpn, sso, dev-app) | `Medium` | `03-dns-enumeration/subdomain-finding/` |
| `INTEL-001` | 60+ devices with exposed RDP in Parma - Information Disclosure (hostnames, OS) | `High` | `04-infrastructure-intel/shodan-censys/` |
| `INTEL-002` | Workstation with RDP + Apache + non-standard ports exposed on public IP | `High` | `04-infrastructure-intel/shodan-censys/` |
| `INTEL-003` | Corporate server with VoIP (3CX) + FTP (FileZilla) + RDP exposed on consumer ADSL | `Critical` | `04-infrastructure-intel/shodan-censys/` |
| `INTEL-004` | tesla.com protected by Akamai WAF - fingerprinting blocked, HSTS active | `Informational` | `04-infrastructure-intel/tech-stack/` |

---

## MITRE ATT&CK Mapping

Aggregated table of all MITRE ATT&CK techniques detected during the Reconnaissance phase.

| Tactic | Technique | MITRE ID | Correlated Finding |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Identity Info: Credentials | `T1589.001` | OSINT-001 |
| Reconnaissance | Gather Victim Identity Info: Email Addresses | `T1589.002` | OSINT-002 |
| Reconnaissance | Search Open Websites/Domains: Search Engines | `T1593.002` | OSINT-003 |
| Reconnaissance | Gather Victim Identity Info: Employee Names | `T1589.003` | OSINT-004 |
| Reconnaissance | Search Open Websites/Domains: Social Media | `T1593.001` | OSINT-004 |
| Reconnaissance | Remote System Discovery | `T1018` | SCAN-001 |
| Reconnaissance | Network Service Discovery | `T1046` | SCAN-001, SCAN-002, SCAN-003 |
| Reconnaissance | Gather Victim Host Info: Software | `T1592.002` | SCAN-003, INTEL-004 |
| Reconnaissance | Gather Victim Network Info: DNS | `T1590.002` | DNS-001, DNS-003 |
| Reconnaissance | Search Open Technical Databases: DNS/Passive DNS | `T1596.001` | DNS-001, DNS-003 |
| Reconnaissance | Search Open Technical Databases: Scan Databases | `T1596.005` | INTEL-001, INTEL-002, INTEL-003 |
| Reconnaissance | Gather Victim Network Info: Network Topology | `T1590.004` | INTEL-001, INTEL-002, INTEL-003 |

---

> **Note:** All activities documented in this module were performed on authorized targets (VirtualBox lab, personal domain nicholas-arcari.github.io, publicly available targets for educational purposes such as zonetransfer.me and public bug bounty programs such as tesla.com). No activity was conducted on systems without explicit authorization.
