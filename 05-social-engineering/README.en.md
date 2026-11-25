> **English** | [Italiano](README.md)

# 05 - Social engineering

> - **Phase:** Social Engineering - Layer 8 Attack (human factor)
> - **Visibility:** Variable - from Zero (pretexting research, crafting email/landing page) to High (sending phishing emails, payload delivery, post-click C2 callback)
> - **Prerequisites:** Completion of module 01-recon (OSINT on target: corporate emails, org chart, technologies in use); operational email infrastructure (domain, SMTP relay); payloads generated from module 04-system-exploitation if needed
> - **Output:** Finding SE-001..015; credentials harvested through simulated phishing campaigns; hijacked MFA sessions; delivered and executed payloads; complete reproducible social engineering methodology

---

## Introduction

Module `05-social-engineering` documents techniques for attacking the human factor - Layer 8 of the ISO/OSI stack. While previous modules operate on protocols, services, and operating systems, the target here is the person: convincing them to click a link, enter credentials, open an attachment, execute a file. In a professional penetration test, social engineering is often the most effective Initial Access vector: according to the Verizon DBIR 2024, phishing and pretexting account for over 70% of initial vectors in confirmed breaches.

The section is organized into six competency areas that reflect the complete kill chain of a social engineering attack:

1. **Phishing Campaigns (SE-001..002):** platforms for professional phishing campaigns. GoPhish is the enterprise standard for simulations with detailed metrics (open rate, click rate, credential submission). Evilginx represents the modern evolution: reverse proxy phishing that intercepts MFA sessions in real time, making even two-factor authentication insufficient.

2. **Social-Engineer Toolkit (SE-003..006):** the most comprehensive offensive framework for social engineering. SET integrates four separately documented attack vectors: Website Attack (credential harvesting via clone), Spear-Phishing (email with payload), Infectious Media (removable media), PowerShell Attack (encoded stager for Windows).

3. **Payload Delivery (SE-007..010):** malicious code delivery techniques to the target. From the classic technique (VBA macros in Office documents) to modern post-2022 techniques (HTML Smuggling for email gateway bypass, ISO + LNK to evade Mark-of-the-Web), to physical attack (USB Rubber Ducky).

4. **Email Infrastructure (SE-011..012):** the technical infrastructure that makes a phishing campaign credible. SPF/DKIM/DMARC audit to identify domains vulnerable to spoofing, SMTP relay configuration, generation of confusable typosquatting domains.

5. **Pretexting Methodology (SE-013):** the human and psychological dimension of the attack. OSINT target profiling to build dossiers on the target, designing pretexting scenarios based on Cialdini's principles, templates for the most effective pretexts (IT helpdesk, CEO fraud, vendor impersonation).

6. **Custom Python Tools (SE-014..015):** development of custom Python tools to automate specific phases of the SE kill chain: custom Flask credential harvester, email permutation generator, tracking pixel server for geolocation.

In the Cyber Kill Chain and MITRE ATT&CK matrix, this module covers the Reconnaissance (TA0043), Resource Development (TA0042), Initial Access (TA0001), Execution (TA0002), and Collection (TA0009) tactics. Social engineering is the bridge between the intelligence phase (modules 01-02) and the initial access that enables all subsequent phases (modules 04, 07).

---

## Folder structure

```
05-social-engineering/
+-- README.md                                <- this file: finding registry + aggregated MITRE
|
+-- 01-phishing-campaigns/
|   +-- README.md                            <- phishing framework overview, registry SE-001..002
|   +-- gophish/                             <- SE-001 (campaign credential harvest, click rate > 30%)
|   +-- evilginx/                            <- SE-002 (MFA bypass reverse proxy - Critical)
|   +-- pyphisher/                           <- quick testing tool (77 templates, automatic tunnel)
|
+-- 02-social-engineer-toolkit/
|   +-- README.md                            <- SET overview, registry SE-003..006
|   +-- website-attack-vectors/              <- SE-003 (credential harvester via cloned login)
|   +-- spear-phishing-vectors/              <- SE-004 (email with disguised .hta payload)
|   +-- infectious-media-generator/          <- SE-005 (autorun.inf on removable media)
|   +-- powershell-attack-vectors/           <- SE-006 (PS-encoded reverse shell)
|
+-- 03-payload-delivery/
|   +-- README.md                            <- delivery vectors overview, registry SE-007..010
|   +-- malicious-macros/                    <- SE-007 (VBA macro PowerShell reverse shell)
|   +-- html-smuggling/                      <- SE-008 (email gateway bypass with JS blob)
|   +-- iso-lnk-delivery/                    <- SE-009 (post-macro kill delivery chain - Critical)
|   +-- usb-rubber-ducky/                    <- SE-010 (HID attack, exfiltration in < 30s)
|
+-- 04-email-infrastructure/
|   +-- README.md                            <- email infrastructure overview, registry SE-011..012
|   +-- spf-dkim-dmarc/                      <- SE-011 (DMARC misconfiguration audit)
|   +-- smtp-relay/                          <- SMTP relay configuration for campaigns
|   +-- domain-typosquatting/                <- SE-012 (confusable domain generation)
|
+-- 05-pretexting-methodology/
|   +-- README.md                            <- human SE methodology overview, registry SE-013
|   +-- target-profiling/                    <- SE-013 (OSINT-based dossier construction)
|   +-- pretext-scenarios/                   <- scenario templates: helpdesk, CEO fraud, vendor
|
+-- 06-custom-python-tools/
    +-- README.md                            <- custom tool overview, registry SE-014..015
    +-- credential-harvester/                <- SE-014 (custom Flask credential harvester)
    +-- email-generator/                     <- corporate email permutation generator
    +-- tracking-pixel/                      <- SE-015 (IP geolocation on click tracking)
```

---

## Recommended operational flow

```
[INPUT from 01-recon + 02-vulnerability-assessment]
Corporate emails, org chart, target technologies, domains
         |
         v
[1] Target Profiling & Pretexting (05-pretexting-methodology)
     +-- OSINT aggregation -> target dossier (role, habits, tech stack)
     +-- Pretext selection -> IT helpdesk / CEO fraud / vendor / delivery
     +-- Building credible narrative
              |
              v
[2] Infrastructure Setup (04-email-infrastructure)
     +-- SPF/DKIM/DMARC audit of target domain -> spoofing possible?
     +-- Domain typosquatting -> purchase confusable domain
     +-- SMTP relay config -> SendGrid/Mailgun/GoPhish SMTP
              |
              v
[3] Weaponization (03-payload-delivery + 06-custom-python-tools)
     +-- Vector selection:
     |   +-- Credential harvest only ---------> GoPhish landing page / custom Flask
     |   +-- Code execution required ---------> VBA Macro / HTML Smuggling / ISO+LNK
     |   +-- Physical access available -------> USB Rubber Ducky
     +-- Payload creation with msfvenom/Empire (from 04-system-exploitation)
     +-- Email and landing page templates
              |
              v
[4] Delivery & Execution (01-phishing-campaigns + 02-social-engineer-toolkit)
     +-- Standard phishing ---------> GoPhish campaign (metrics, tracking)
     +-- MFA bypass required -------> Evilginx reverse proxy
     +-- Quick test ----------------> PyPhisher + tunnel
     +-- Multi-vector attack -------> SET (website + spear-phishing + media)
              |
              v
[5] Collection & Analysis
     +-- Harvested credentials -> validity verification (targeted spray, not brute-force)
     +-- Hijacked MFA sessions -> direct access without password
     +-- Executed payloads -> C2 callback (04-system-exploitation)
     +-- Campaign metrics -> client report
              |
              v
[OUTPUT] Valid credentials + active sessions + C2 shells
     -> input for 07-post-exploitation (lateral movement, persistence, exfiltration)
```

---

## Reference tools

| tool | type | technique/access | primary use case |
| :--- | :--- | :--- | :--- |
| `GoPhish` | phishing platform | web ui + cli | enterprise standard for simulated phishing campaigns with complete metrics |
| `Evilginx` | reverse proxy phisher | cli | real-time mfa bypass via reverse proxy (session hijacking) |
| `PyPhisher` | automated phishing | cli - python | quick testing with 77 templates and 4 tunnel providers (ngrok, cloudflared) |
| `SET` | social engineering framework | cli - interactive menu | multi-vector framework: website clone, spear-phishing, media, powershell |
| `msfvenom` | payload generator | cli | payload generation for vba macros, hta, powershell stager |
| `dnstwist` | domain analysis | cli - python | generation and verification of confusable typosquatting domains |
| `spoofcheck` | email audit | cli - python | verification of spf/dmarc configuration for a target domain |
| `Rubber Ducky` | hid attack device | hardware + duckyscript | physical attack: automated keystroke injection via usb |
| `Flask` | web framework | python | custom credential harvester and tracking server development |

> **Recommended modern tool:** `Evilginx 3.x` for advanced phishing with MFA bypass - replaces traditional phishing kits in scenarios where the target has MFA enabled. `dnstwist` for typosquatting detection. `GoPhish` + `Mailhog` for local testing without external SMTP infrastructure.

---

## Finding registry - module 05

| id | description | severity | subfolder |
| :--- | :--- | :---: | :--- |
| `SE-001` | gophish campaign: credential harvesting with click rate > 30% on simulated target (20 users) | `High` | `01-phishing-campaigns/gophish/` |
| `SE-002` | evilginx: mfa bypass via reverse proxy - session token intercepted in real time, access without password | `Critical` | `01-phishing-campaigns/evilginx/` |
| `SE-003` | set website attack: credential harvester via cloned login page, credentials captured in cleartext | `High` | `02-social-engineer-toolkit/website-attack-vectors/` |
| `SE-004` | set spear-phishing: email with disguised .hta attachment, powershell stager execution | `High` | `02-social-engineer-toolkit/spear-phishing-vectors/` |
| `SE-005` | set infectious media: autorun.inf payload on usb drive, execution on mount | `Medium` | `02-social-engineer-toolkit/infectious-media-generator/` |
| `SE-006` | set powershell attack: base64 encoded reverse shell, execution policy bypass | `High` | `02-social-engineer-toolkit/powershell-attack-vectors/` |
| `SE-007` | vba office macro: word document with macro executing encoded powershell stager | `High` | `03-payload-delivery/malicious-macros/` |
| `SE-008` | html smuggling: email gateway bypass via javascript blob download, .exe payload reconstructed client-side | `High` | `03-payload-delivery/html-smuggling/` |
| `SE-009` | iso + lnk delivery: payload execution without mark-of-the-web, smartscreen bypass | `Critical` | `03-payload-delivery/iso-lnk-delivery/` |
| `SE-010` | usb rubber ducky: saved wifi credential exfiltration in < 30 seconds via hid attack | `High` | `03-payload-delivery/usb-rubber-ducky/` |
| `SE-011` | spf/dkim/dmarc audit: target domain with dmarc policy `none` - email spoofing possible | `Medium` | `04-email-infrastructure/spf-dkim-dmarc/` |
| `SE-012` | domain typosquatting: 15+ confusable domains generated, 3 unregistered and purchasable | `Informational` | `04-email-infrastructure/domain-typosquatting/` |
| `SE-013` | osint target profiling: complete dossier on target (role, contacts, tech stack, social media habits) | `Informational` | `05-pretexting-methodology/target-profiling/` |
| `SE-014` | flask credential harvester: cloned login page with real-time ip/user-agent/credential logging | `High` | `06-custom-python-tools/credential-harvester/` |
| `SE-015` | tracking pixel: recipient ip geolocation at the moment of email opening | `Informational` | `06-custom-python-tools/tracking-pixel/` |

---

## MITRE ATT&CK mapping - aggregated

| tactic | technique | mitre id | related finding |
| :--- | :--- | :--- | :--- |
| reconnaissance | gather victim identity information: email addresses | `T1589.002` | SE-013 |
| reconnaissance | gather victim org information: identify roles | `T1591.004` | SE-013 |
| reconnaissance | search open websites/domains | `T1593` | SE-013 |
| resource development | acquire infrastructure: domains | `T1583.001` | SE-012 |
| resource development | develop capabilities: malware | `T1587.001` | SE-007, SE-008, SE-009 |
| resource development | obtain capabilities: tool | `T1588.002` | SE-003, SE-004, SE-005, SE-006 |
| resource development | stage capabilities: upload malware | `T1608.001` | SE-001, SE-002, SE-014 |
| initial access | phishing: spearphishing link | `T1566.002` | SE-001, SE-002, SE-003, SE-014 |
| initial access | phishing: spearphishing attachment | `T1566.001` | SE-004, SE-007, SE-008, SE-009 |
| initial access | phishing: spearphishing via service | `T1566.003` | SE-005, SE-010 |
| initial access | replication through removable media | `T1091` | SE-005, SE-010 |
| execution | user execution: malicious link | `T1204.001` | SE-001, SE-002, SE-003, SE-014 |
| execution | user execution: malicious file | `T1204.002` | SE-004, SE-007, SE-008, SE-009 |
| execution | command and scripting interpreter: powershell | `T1059.001` | SE-006, SE-007 |
| execution | command and scripting interpreter: visual basic | `T1059.005` | SE-007 |
| defense evasion | subvert trust controls: mark-of-the-web bypass | `T1553.005` | SE-009 |
| defense evasion | obfuscated files or information: html smuggling | `T1027.006` | SE-008 |
| credential access | input capture: web portal capture | `T1056.003` | SE-001, SE-003, SE-014 |
| credential access | steal web session cookie | `T1539` | SE-002 |
| collection | input capture: credential api hooking | `T1056.004` | SE-010 |
| discovery | system information discovery | `T1082` | SE-010, SE-015 |

---

> **Note:** All activities documented in this module were conducted in a virtualized lab environment (VirtualBox, isolated NAT/Bridge network). Phishing campaigns were directed exclusively against fictitious users created ad hoc on virtual machines owned by the author. No phishing emails were sent to real addresses. No technique was applied to real people or systems without explicit authorization. Social engineering techniques are documented for educational and awareness purposes.
