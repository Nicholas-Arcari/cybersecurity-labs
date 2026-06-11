> **English** | [Italiano](README.md)

# Target Profiling - OSINT-Based Dossier Construction

> - **Phase:** Social Engineering - Reconnaissance on the human factor
> - **Visibility:** Zero - all information is gathered from public sources (LinkedIn, social media, search engines, DNS) without direct interaction with the target
> - **Prerequisites:** theHarvester, linkedin2username, SpiderFoot or Maltego; access to public OSINT sources; results from module 01-recon (emails, domains)
> - **Output:** SE-013 (complete OSINT dossier on target - severity Informational); target card with role, contacts, tech stack, psychological triggers

- **Operating Environment:** Kali Linux Purple (reconnaissance)
- **Target:** Simulated corporate profile
- **Framework:** theHarvester, linkedin2username, manual research
- **Documented Techniques:** Email Harvesting, Social Media Profiling, Organigramma Reconstruction

---

## Executive Summary

Target profiling transforms raw OSINT data (emails, names, roles) into an operational dossier that guides social engineering campaign customization. The difference between generic phishing (5% click rate) and targeted phishing (40%+ click rate) lies entirely in profiling quality: knowing the target's manager name, the project they are working on, or the tool they mentioned in a LinkedIn post allows building pretexts that are nearly impossible to recognize as fraudulent.

---

## Target Profiling: OSINT Dossier Construction

**Finding ID:** `SE-013` | **Severity:** `Informational`

### PoC - Phase 1: Email Harvesting

```Bash
theHarvester -d target-lab.com -b google,linkedin,bing,crtsh -l 500
```

```
[*] Emails found: 12
m.rossi@target-lab.com
l.bianchi@target-lab.com
a.verdi@target-lab.com
g.ferrari@target-lab.com
[... 8 more ...]

[*] Hosts found: 4
mail.target-lab.com: 93.184.216.34
vpn.target-lab.com: 93.184.216.35                          <-- exposed VPN
sharepoint.target-lab.com: 93.184.216.36                    <-- external SharePoint
```

### PoC - Phase 2: LinkedIn Profiling

```Bash
# Username list generation from LinkedIn
linkedin2username -c target-lab -s "Italy" -d target-lab.com
```

```
Mario Rossi - Chief Financial Officer                       <-- C-Level: high-value target
Luca Bianchi - HR Manager                                   <-- HR: access to personal data
Anna Verdi - IT System Administrator                        <-- IT: privileged access
Giovanni Ferrari - Sales Director                           <-- Sales: less security-aware
```

### PoC - Phase 3: Deep Profiling (Manual Research)

```
=== TARGET DOSSIER: Mario Rossi (CFO) ===

IDENTITY:
  Name:        Mario Rossi
  Role:        Chief Financial Officer
  Email:       m.rossi@target-lab.com
  Manager:     CEO (name from LinkedIn: Paolo Conti)
  Team:        Finance (4 people)

TECHNOLOGY STACK:
  Email:       Microsoft 365 (from MX records: outlook.com)
  VPN:         Present (vpn.target-lab.com)
  Collaboration: SharePoint (sharepoint.target-lab.com)

SOCIAL FOOTPRINT:
  LinkedIn:    Active, 500+ connections, posts about fintech
  Twitter:     @mrossi_fin - tweets about economics, Serie A
  GitHub:      No profile found
  Facebook:    Private profile, profile picture visible

RECOMMENDED PSYCHOLOGICAL TRIGGERS:
  Primary:     Authority (email from CEO Paolo Conti)
  Secondary:   Urgency (tax deadline, audit)
  Tertiary:    Reciprocity (document shared by colleague)

RECOMMENDED PRETEXT:
  "Paolo Conti shared a confidential document on SharePoint:
   Budget_Revisione_Q2_2026.xlsx - Urgent approval requested"
  Vector: Email with link to GoPhish landing page (SharePoint clone)
```

### Remediation

- **Immediate action:** raise staff awareness about the amount of personal information publicly exposed; review privacy settings on social media profiles
- **Structural action:** corporate policy on social media presence (what to share and what not to); specific training for C-Level and roles with access to sensitive data; removal of unnecessary information from the company website (full names, direct emails, detailed org chart)
- **Verification:** repeat the profiling after implementing the measures - the exposed information surface must be reduced

---

## Lab Experience

The profiling was conducted on fictitious profiles created specifically on LinkedIn and test social media accounts. The most significant finding was the time required: a complete operational dossier for a single target takes approximately 30-45 minutes of manual research. In an engagement with 20 targets, profiling can require 2-3 days of work - an investment that pays off entirely in campaign click rate.

The main challenge was correlating information across different platforms. The name "Mario Rossi" on LinkedIn is not immediately linkable to the Twitter profile "@mrossi_fin" without a connection point (shared email, similar profile picture, overlapping interests). Tools like Maltego automate this correlation through relationship graphs, but human judgment remains essential for validating the connections.

---

## Theoretical Analysis: OSINT as a Force Multiplier

The value of target profiling in social engineering is quantifiable: according to the Verizon DBIR 2024 study, targeted spear-phishing campaigns (profiling-based) have a 10x higher success rate than generic phishing. The reason is cognitive: the human brain uses familiarity as a proxy for trust. An email that mentions the manager's name, the current project, or the tool in use activates recognition circuits that bypass critical analysis.

OSINT profiling operates on the public information surface of the organization and its employees. Every piece of published data - from a LinkedIn post to the "About Us" page on the company website - is a potential component of a pretext. The defense is not to eliminate online presence (impractical), but to educate staff to recognize how public information can be weaponized and to adopt a "minimum viable exposure" approach.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Identity Information: Email Addresses | `T1589.002` | Email collection via theHarvester (SE-013) |
| Reconnaissance | Gather Victim Identity Information: Employee Names | `T1589.003` | Name and role enumeration via LinkedIn (SE-013) |
| Reconnaissance | Gather Victim Org Information: Identify Roles | `T1591.004` | Org chart and chain of command reconstruction |
| Reconnaissance | Search Open Websites/Domains: Social Media | `T1593.001` | Social media profiling for psychological triggers |
| Reconnaissance | Search Victim-Owned Websites | `T1594` | Company website analysis for technology stack |

---

> **Note:** The profiling was conducted on fictitious profiles. No real personal information was collected without authorization.
