> **English** | [Italiano](README.md)

# 05 - Pretexting Methodology

> - **Phase:** Social Engineering - Pretexting & Target Profiling (human dimension of the attack)
> - **Visibility:** Zero (passive OSINT research) / Low (phone/email interaction with pretext)
> - **Prerequisites:** Completion of module 01-recon (passive OSINT); access to public sources (LinkedIn, social media, target company website); understanding of psychological influence principles
> - **Output:** Finding SE-013 (complete target dossier via OSINT - severity Informational); ready-to-use pretexting scenario templates; reproducible target profiling methodology

---

## Introduction

Pretexting is the human and psychological dimension of social engineering - the one that distinguishes a senior penetration tester from a tool operator. While the previous sections document the technical "how" (which tool, which payload, which infrastructure), this section documents the "why" and the "who": how to choose the right target, how to build a credible narrative, and how to exploit psychological influence principles to maximize the probability of success.

In a professional engagement, pretexting quality directly determines the click rate and success rate of the campaign. A technically perfect email with a weak pretext ("You won a prize!") has a click rate of 2-5%. The same email with a contextual pretext ("Your manager Marco shared a document on SharePoint") reaches 30-50%.

This section documents two complementary skills:

1. **Target Profiling (SE-013):** collection and aggregation of OSINT information to build a target dossier. Corporate role, contacts, technology stack, social media habits - every piece of data becomes an element of the pretext.

2. **Pretext Scenarios:** pretexting scenario templates based on Cialdini's principles, calibrated by corporate role and context. From the classic "email from IT department" to the sophisticated "CEO fraud" and "vendor impersonation".

---

## Folder Structure

```
05-pretexting-methodology/
+-- target-profiling/     # OSINT aggregation for target dossier - SE-013
+-- pretext-scenarios/    # Templates calibrated by role and context
```

---

## `target-profiling/` - OSINT-Based Dossier Construction

**Finding ID:** `SE-013` | **Severity:** `Informational` (complete target dossier via public sources)

### Operational Context

Target profiling is the information-gathering phase focused on the person (not the system). The goal is to build a dossier that answers five questions: who is the target (role, responsibilities), who do they interact with (manager, colleagues, vendors), what technology stack do they use, what are their digital habits (social media, posts, comments), and what are the most effective psychological triggers (urgency, authority, fear).

### Main Commands

```Bash
# OSINT email: theHarvester for corporate email collection
theHarvester -d target-lab.com -b google,linkedin,bing -l 200
```

```
[*] Emails found:
m.rossi@target-lab.com                                      <-- primary target (CFO)
l.bianchi@target-lab.com                                    <-- secondary target (HR)
a.verdi@target-lab.com                                      <-- tertiary target (IT)
info@target-lab.com                                         <-- generic
```

```Bash
# LinkedIn OSINT: role enumeration and org chart
# (manual search or with linkedin2username)
linkedin2username -c target-lab -s "Italy"
```

```Bash
# Social media footprint
# Manual search on:
# - LinkedIn: role, skills, connections, recent posts
# - Twitter/X: opinions, interests, mentioned technologies
# - GitHub: projects, languages, emails in commits
# - Facebook/Instagram: personal information, geolocation
```

---

## `pretext-scenarios/` - Pretexting Scenario Templates

### Operational Context

Pretexting templates are pre-built scenarios calibrated by corporate role and psychological principle. Each template includes: the narrative pretext, the exploited Cialdini principle, the recommended delivery vector, and the variables to customize with target profiling data.

---

## The Six Cialdini Principles in Social Engineering

| Principle | Definition | SE Application |
| :--- | :--- | :--- |
| **Authority** | We tend to obey authority figures | Email from CEO, IT, vendor |
| **Urgency/Scarcity** | We act impulsively under time pressure | "Within 24 hours", "Account will be suspended" |
| **Reciprocity** | We feel obligated to return a favor | "I sent you the report, can you confirm?" |
| **Social Proof** | We follow the behavior of others | "90% of colleagues have already completed" |
| **Commitment/Consistency** | We maintain consistency with previous actions | Follow-up to a previously accepted request |
| **Liking** | We are influenced by people we like | Friendly tone, common interests |

---

## Recommended Operational Flow

```
[1] Target identification (from 01-recon OSINT)
     +-- Corporate emails
     +-- Org chart: who is the manager, who are the colleagues
     +-- Role and responsibilities
              |
              v
[2] Deep profiling
     +-- LinkedIn: skills, recent posts, connections
     +-- Social media: interests, habits, geolocation
     +-- GitHub/personal sites: tech stack, emails in commits
              |
              v
[3] Dossier construction
     +-- Target card: name, role, email, manager, interests
     +-- Psychological triggers: which Cialdini principle is most effective
     +-- Recommended vector: email, phone, in person
              |
              v
[4] Pretext selection
     +-- IT/Tech role -> "Security update" (Authority)
     +-- Finance role -> "Pending invoice" (Urgency)
     +-- HR role -> "Application to review" (Reciprocity)
     +-- C-Level -> "CEO fraud" (Authority + Urgency)
              |
              v
[5] Customization and Delivery
     +-- Insert contextual details from dossier
     +-- Choose framework (GoPhish, SET, Evilginx)
     +-- Launch campaign
```

---

## Reference Tools

| Tool | Type | Technique/Access | Primary Use Case |
| :--- | :--- | :--- | :--- |
| `theHarvester` | OSINT email | CLI | Email and subdomain collection from public sources |
| `linkedin2username` | Social OSINT | CLI - Python | Username generation from LinkedIn profiles |
| `Maltego` | OSINT aggregator | GUI | Relationship visualization between entities (people, emails, domains) |
| `SpiderFoot` | OSINT automation | Web UI | Automated OSINT collection from 200+ sources |
| `Recon-ng` | OSINT framework | CLI | Modular reconnaissance framework with social media modules |

> **Recommended modern tool:** `SpiderFoot HX` (hosted) or `SpiderFoot` (self-hosted) for complete OSINT automation. `Maltego CE` for graphical relationship visualization. For LinkedIn, `linkedin2username` combined with manual search for qualitative context.

---

## Finding Registry

| ID | Description | Severity | CVSS | Subfolder |
| :--- | :--- | :---: | :---: | :--- |
| `SE-013` | OSINT target profiling: complete target dossier (role, contacts, tech stack, social habits) built entirely from public sources | `Informational` | 2.1 | `target-profiling/` |

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Related Finding |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Identity Information: Email Addresses | `T1589.002` | SE-013 |
| Reconnaissance | Gather Victim Identity Information: Employee Names | `T1589.003` | SE-013 |
| Reconnaissance | Gather Victim Org Information: Identify Roles | `T1591.004` | SE-013 |
| Reconnaissance | Gather Victim Org Information: Identify Business Tempo | `T1591.003` | SE-013 |
| Reconnaissance | Search Open Websites/Domains: Social Media | `T1593.001` | SE-013 |
| Reconnaissance | Search Victim-Owned Websites | `T1594` | SE-013 |

---

> **Note:** The target profiling activities documented here were conducted on fictitious profiles created ad hoc. No real personal information was collected or used without authorization.
