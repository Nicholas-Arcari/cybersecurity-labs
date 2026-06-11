> **English** | [Italiano](README.md)

# 01 - Phishing Campaigns

> - **Phase:** Social Engineering - Phishing Campaign Deployment & Credential Harvesting
> - **Visibility:** High - phishing emails generate SMTP logs, tracking URLs are visible to email filters/proxy, landing pages can be classified by URL reputation systems; Evilginx generates anomalous TLS traffic (double handshake)
> - **Prerequisites:** Completion of target profiling phase (corporate emails, org chart); email infrastructure configured (domain, SMTP relay, SPF/DKIM); for Evilginx: valid domain with TLS certificate and controlled DNS records
> - **Output:** Finding SE-001..002; credentials harvested via GoPhish landing page; MFA session tokens intercepted via Evilginx; campaign metrics (open/click/submit rate)

---

## Introduction

The phishing campaign is the moment when all preparation (pretexting, infrastructure, payload) is executed against the target. The frameworks documented in this section cover three levels of complexity:

**GoPhish (SE-001):** open-source platform that represents the enterprise standard for phishing simulations. GoPhish manages the entire cycle: email template creation, landing page with credential harvesting, scheduled sending, granular tracking (email opens, link clicks, credential submission). The metrics produced are the primary deliverable in a security awareness assessment.

**Evilginx (SE-002):** reverse proxy phishing framework that operates as a Man-in-the-Middle between the target and the legitimate service (Microsoft 365, Google Workspace, Okta). Unlike traditional phishing that only captures username and password, Evilginx intercepts post-authentication session cookies, completely bypassing MFA. It is the most advanced phishing technique documented in this repository and represents the primary threat for organizations that consider MFA a sufficient protection.

**PyPhisher:** automated wrapper with 77 pre-built templates and 4 tunneling providers. Useful for quick tests and PoC, but unsuitable for professional campaigns (generic tunnels easily blocked, no metrics, no advanced customization).

In the kill chain, this section covers the Delivery and Exploitation phases: the email reaches the victim (Delivery), the victim interacts with the content (Exploitation), and credentials/sessions are collected (Collection).

---

## Folder Structure

```
01-phishing-campaigns/
+-- gophish/       # Enterprise standard: campaign management + analytics - SE-001
+-- evilginx/      # MFA bypass reverse proxy - SE-002
+-- pyphisher/     # Quick testing: 77 templates, automatic tunnel (no finding)
```

---

## `gophish/` - Campaign Management & Credential Harvesting

**Finding ID:** `SE-001` | **Severity:** `High` (click rate > 30% on simulated campaign with credential submission)

### Operational Context

GoPhish was used to design and launch a simulated phishing campaign against a group of 20 fictitious users in a lab environment. The campaign replicated a typical corporate scenario: an urgent password reset email from the IT department, with a link to a cloned landing page of the internal authentication portal. The result - click rate above 30% and significant credential submission rate - demonstrates the effectiveness of the phishing vector even without technical sophistication.

### Key Commands

```Bash
# Start GoPhish
cd /opt/gophish && sudo ./gophish
# Admin panel: https://127.0.0.1:3333
# Phishing server: http://0.0.0.0:80
```

```Bash
# Workflow via Web UI:
# 1. Sending Profile -> SMTP relay (SendGrid/local)
# 2. Landing Page -> "Import Site" -> clone of target portal
# 3. Email Template -> HTML with {{.URL}} and {{.Tracker}}
# 4. Users & Groups -> import CSV (first name, last name, email, role)
# 5. Campaign -> component association -> Launch
```

---

## `evilginx/` - MFA Bypass via Reverse Proxy

**Finding ID:** `SE-002` | **Severity:** `Critical` (MFA session token intercepted - full access without password)

### Operational Context

Evilginx operates as a transparent reverse proxy between the victim and the legitimate authentication service. The victim completes the entire login flow (password + MFA) interacting with the real service, but Evilginx intercepts the session cookies issued post-authentication. The attacker then imports these cookies into their own browser to access the account without knowing the password and without repeating MFA.

### Key Commands

```Bash
# Setup Evilginx
sudo ./evilginx -p ./phishlets -developer
config domain lab.local
config ipv4 192.168.0.110

# Microsoft 365 Phishlet
phishlets hostname o365 login.lab.local
phishlets enable o365

# Create phishing URL
lures create o365
lures get-url 0
# Output: https://login.lab.local/NeKzw3E

# Captured sessions
sessions
# -> Azure AD session cookie captured post-MFA
```

---

## `pyphisher/` - Quick Testing & Proof of Concept

### Operational Context

PyPhisher is a Python tool that automates the creation of phishing pages with 77 pre-built templates and 4 tunneling providers (Ngrok, Cloudflared, LocalXpose, LocalHostRun). Useful for quick PoC and educational demonstrations, but with significant limitations for professional use: generic tunnels easily blocked, no metrics, non-customizable templates. Complete documentation is in the dedicated README in the subfolder.

---

## Recommended Operational Flow

```
[1] Target analysis
     +-- MFA enabled? -----> YES -> Evilginx (MFA bypass)
     |                 +--> NO  -> GoPhish (standard credential harvesting)
     +-- PoC/demo only? ----> PyPhisher (quick test with tunnel)
              |
              v
[2] Infrastructure setup
     +-- GoPhish:   SMTP relay + landing page + email template
     +-- Evilginx:  domain + DNS + TLS certificate + phishlet
     +-- PyPhisher: local installation + tunnel selection
              |
              v
[3] Crafting & Launch
     +-- Customized email template (pretext from 05-pretexting)
     +-- Cloned landing page of target portal
     +-- Real-time metrics monitoring
              |
              v
[4] Collection & Reporting
     +-- Harvested credentials -> validity verification
     +-- Session token -> browser replay
     +-- Client report with metrics and recommendations
```

---

## Reference Tools

| Tool | Type | Technique/Access | Primary Use Case |
| :--- | :--- | :--- | :--- |
| `GoPhish` | Phishing platform | Web UI | Enterprise standard: campaign management, templates, analytics |
| `Evilginx 3.x` | Reverse proxy phisher | CLI | MFA bypass via session hijacking, phishlets for cloud services |
| `PyPhisher` | Automated phishing | CLI - Python | Quick PoC with 77 templates and automatic tunnel |
| `King Phisher` | Phishing platform | GUI + CLI | Alternative to GoPhish with advanced reporting |
| `Modlishka` | Reverse proxy | CLI - Go | Alternative to Evilginx, more lightweight |
| `Mailhog` | SMTP testing | Web UI | Fake SMTP server for local testing |

> **Recommended modern tool:** `Evilginx 3.x` is the reference tool for advanced phishing in 2024-2026. For enterprise campaigns, `GoPhish` + `Mailhog` allows complete testing without risk of sending to real addresses.

---

## Finding Registry

| ID | Description | Severity | CVSS | Subfolder |
| :--- | :--- | :---: | :---: | :--- |
| `SE-001` | GoPhish campaign: credential harvesting with click rate > 30% and submission rate 20% on 20 simulated users | `High` | 8.1 | `gophish/` |
| `SE-002` | Evilginx: MFA bypass via reverse proxy - Microsoft 365 session token intercepted after complete MFA authentication | `Critical` | 9.3 | `evilginx/` |

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Related Finding |
| :--- | :--- | :--- | :--- |
| Resource Development | Stage Capabilities: Upload Malware | `T1608.001` | SE-001, SE-002 |
| Resource Development | Acquire Infrastructure: Domains | `T1583.001` | SE-002 |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | SE-001, SE-002 |
| Execution | User Execution: Malicious Link | `T1204.001` | SE-001, SE-002 |
| Credential Access | Input Capture: Web Portal Capture | `T1056.003` | SE-001 |
| Credential Access | Steal Web Session Cookie | `T1539` | SE-002 |
| Credential Access | Adversary-in-the-Middle | `T1557` | SE-002 |

---

> **Note:** All documented activities were conducted in a virtualized lab environment (VirtualBox, isolated NAT/Bridge network). Phishing campaigns were directed exclusively against fictitious users on virtual machines owned by the author. No emails were sent to real addresses.
