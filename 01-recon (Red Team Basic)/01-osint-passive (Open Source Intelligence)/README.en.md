> **English** | [Italiano](README.md)

# 01 - Passive OSINT (open source intelligence)

> - **Phase:** Reconnaissance - Passive Information Gathering
> - **Visibility:** Zero - no packets sent to the target, no logs generated on target systems
> - **Prerequisites:** Target identification (domain, email, known usernames), Internet access
> - **Output:** Breach credentials (OSINT-001), exposed emails (OSINT-002), indexed files/login pages (OSINT-003), correlated social profiles (OSINT-004)

---

## Introduction

Passive OSINT is the safest reconnaissance phase for the analyst and the most insidious for the defender: information is collected exclusively from public and open sources, without ever contacting target systems. Every piece of data is already available on the Internet - the Red Team's task is to aggregate it, correlate it and transform it into operational intelligence.

The guiding principle is the OSINT graph: start from a known data point (e.g., a domain, an email, a name) and expand towards other connected data (subdomains, employees, credentials, social accounts). Each found node becomes a new starting point for further research.

Passive OSINT directly feeds subsequent phases:
- Found emails become targets for Phishing campaigns (`05-social-engineering/`)
- Found subdomains become scope for the Web Attack module (`03-web-attacks/`)
- Breach credentials are tested in the Credential Reuse phase (`07-post-exploitation/`)
- Employee names found with Sherlock are used to build Social Engineering campaigns

---

## Folder structure

```
01-osint-passive (Open Source Intelligence)/
+-- README.md                 <- this file (OSINT index + finding registry)
|
+-- breach-data/
|   +-- README.md             <- OSINT-001: breach credentials (h8mail, HIBP)
|   +-- img/                  <- lab screenshots
|
+-- email-harvesting/
|   +-- README.md             <- OSINT-002: exposed emails (theHarvester, Google Dorks)
|
+-- google-dorks/
|   +-- README.md             <- OSINT-003: indexed files and login pages (GHDB, advanced operators)
|
+-- user-enumeration/
    +-- README.md             <- OSINT-004: identity correlation (Sherlock)
    +-- img/                  <- lab screenshots
```

---

## `breach-data/` - Compromised credentials analysis

**Finding ID:** `OSINT-001` | **Severity:** `High`

Public data breach analysis allows identifying compromised credentials associated with the target. If an employee reused the same password between an old breached service (e.g., LinkedIn 2012) and the corporate VPN, an attacker can gain immediate access without any exploitation technique.

Main tools: `h8mail` (CLI), `HaveIBeenPwned` (Web).

**Lesson learned from this lab:** CLI tools depend on external API availability. A "not compromised" result from the command line should always be manually validated on the HIBP portal.

---

## `email-harvesting/` - Exposed email mapping

**Finding ID:** `OSINT-002` | **Severity:** `Informational`

Email Harvesting identifies email addresses associated with a target domain, both through automated tools (`theHarvester`) and targeted Google Dorking. Found emails constitute the target list for Spear Phishing campaigns.

In this lab: audit of the personal domain `nicholas-arcari.github.io`. Result: minimal attack surface, 0 direct indexed emails.

---

## `google-dorks/` - Sensitive data exposure via search engines

**Finding ID:** `OSINT-003` | **Severity:** `Variable (Low / High)`

Google Dorks leverage advanced operators (`site:`, `filetype:`, `inurl:`, `intitle:`) to find sensitive files, login panels and directory listings indexed by mistake. Severity depends on what is found: from a list of PDFs (Low) to plaintext credentials or accessible admin panels (High).

Target: `nasa.gov` (public disclosure program, educational purposes only).

---

## `user-enumeration/` - Identity correlation and user tracking

**Finding ID:** `OSINT-004` | **Severity:** `Low`

Passive User Enumeration exploits users' tendency to reuse the same handle across different platforms. With `Sherlock`, 300+ sites are queried to verify the presence of a username, building a complete target profile useful for Social Engineering.

Critical attention: false positives are frequent. Each hit must be manually verified before being used in a report.

---

## Recommended operational flow

```
[INPUT] A starting data point (e.g., domain, email, full name)
          |
          v
[1] Breach Data Check
     +-- h8mail -t <EMAIL>
     +-- HIBP web (manual validation)
     -> If credentials found: escalation to finding OSINT-001 (High)
          |
          v
[2] Email Harvesting
     +-- theHarvester -d <DOMAIN> -b all
     +-- Google Dork: site:<DOMAIN> "@gmail.com"
     -> Email list -> input for phishing and further OSINT
          |
          v
[3] Google Dorking
     +-- site:<DOMAIN> filetype:pdf
     +-- site:<DOMAIN> inurl:login
     +-- site:<DOMAIN> intitle:"index of /"
     -> Exposed documents, admin panels, directory listings
          |
          v
[4] User Enumeration
     +-- sherlock <USERNAME>
     -> Target social profile (manual verification mandatory)
          |
          v
[OUTPUT] Intelligence report -> input for 03-web-attacks/ and 05-social-engineering/
```

---

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `h8mail` | breach data | cli (python) | automated breach credential search |
| `HaveIBeenPwned` | breach data | web | manual validation on authoritative source |
| `theHarvester` | email/subdomain harvesting | cli | email and subdomain aggregation from search engines |
| `Sherlock` | username enumeration | cli (python) | identity correlation across 300+ platforms |
| google ghdb | sensitive data exposure | web | google hacking database - pre-built queries |
| `Maltego` | osint aggregator | gui | osint graph visualization (free community edition) |
| `SpiderFoot` | osint aggregator | cli/web | multi-source osint automation (open source) |

> **Recommended modern tool:** `SpiderFoot HX` - compared to manual workflow, it automates correlation between emails, domains, breaches and social media in a single navigable graph. For enterprise environments, it replaces hours of manual research.

---

## Finding registry

| id | description | severity | file |
| :--- | :--- | :---: | :--- |
| `OSINT-001` | target credentials identified in public data breaches | `High` | `breach-data/README.md` |
| `OSINT-002` | email exposure on personal domain - minimal surface | `Informational` | `email-harvesting/README.md` |
| `OSINT-003` | documents and login panels indexed on nasa.gov | `Variable (Low / High)` | `google-dorks/README.md` |
| `OSINT-004` | identity correlation through reused username | `Low` | `user-enumeration/README.md` |

---

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| reconnaissance | gather victim identity info: credentials | `T1589.001` | compromised credential search on hibp and h8mail (OSINT-001) |
| reconnaissance | gather victim identity info: email addresses | `T1589.002` | email harvesting with theharvester and google dorks on target domain (OSINT-002) |
| reconnaissance | search open websites/domains: search engines | `T1593.002` | google dorking to locate exposed pdf files, login panels and directory listings (OSINT-003) |
| reconnaissance | gather victim identity info: employee names | `T1589.003` | identity correlation through username with sherlock across 300+ platforms (OSINT-004) |
| reconnaissance | search open websites/domains: social media | `T1593.001` | target social presence enumeration for profiling and social engineering (OSINT-004) |

---

> **Note:** All activities documented in this section were performed on authorized targets: personal domain `nicholas-arcari.github.io`, public educational target `nasa.gov` (Google queries only, no direct access), public bug bounty program. No credentials identified in breaches were used to attempt unauthorized access.
