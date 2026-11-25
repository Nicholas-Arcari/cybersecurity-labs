> **English** | [Italiano](README.md)

# OSINT frameworks: automation and correlation (SpiderFoot, recon-ng, maltego)

> - **Phase:** Reconnaissance - Passive Information Gathering (automation and correlation)
> - **Visibility:** Zero / Low - most modules query public sources and third-party APIs (Zero-Touch); some optional modules perform DNS resolutions or direct HTTP requests (Low) and must be disabled to stay invisible
> - **Prerequisites:** A starting datum (domain, email, name, IP), free API keys for the main sources (Shodan, HaveIBeenPwned, VirusTotal, Hunter.io), completion of the manual OSINT techniques (`breach-data/`, `email-harvesting/`, `user-enumeration/`)
> - **Output:** Correlated OSINT graph of the target, attack surface aggregated from multiple sources, finding OSINT-005

---

## Introduction

The manual OSINT techniques documented in the previous sections (`breach-data/`, `email-harvesting/`, `google-dorks/`, `user-enumeration/`) are effective but do not scale. On a real target with dozens of domains, hundreds of employees and distributed infrastructure, manual collection and correlation take days and are subject to errors of omission. OSINT frameworks solve this problem by automating two distinct activities: **collection** from hundreds of sources in parallel and **correlation**, that is, the automatic linking of heterogeneous data (an email leads to a breach, the breach to a password, the domain to a subdomain, the subdomain to an IP exposed on Shodan).

The operational value of a framework is not finding a single datum, but building the **graph** of the target: the network of relationships between entities that turns isolated fragments into actionable intelligence. This is the difference between knowing that the email `admin@target.com` exists and knowing that the same email appears in three breaches, reuses a username present on GitHub where it has committed a still-valid API key.

This section documents the three industry-reference frameworks, each with a different philosophy:

- **SpiderFoot:** total automation, over 200 modules, ideal for massive "fire-and-forget" collection with automatic reporting.
- **recon-ng:** modular framework in Metasploit style, ideal for a controlled and repeatable workflow, with an internal database and a module marketplace.
- **Maltego:** visual graph analysis via "transforms", irreplaceable when one needs to understand complex relationships between many entities.

The produced results feed directly into `03-dns-enumeration/` (discovered subdomains), `04-infrastructure-intel/` (correlated exposed assets) and `05-social-engineering/` (employees and emails for targeted campaigns).

---

## Folder structure

```
osint-frameworks/
+-- README.md            <- this file (OSINT-005: OSINT automation and correlation)
+-- img/                 <- lab screenshots (SpiderFoot graph, recon-ng dashboard, Maltego transform)
```

---

## SpiderFoot - Multi-Source OSINT automation

**Finding ID:** `OSINT-005` | **Severity:** `Variable (Informational / High)`

### Operational context

SpiderFoot is the most complete open source OSINT framework for automated collection. It queries over 200 sources (search engines, breach databases, DNS registries, Shodan, TLS certificates, social media, historical archives) and automatically correlates the results. Its distinctive feature is the management of **visibility**: each module is classified as passive (queries only third parties) or active (contacts the target), allowing the analyst to run scans completely invisible to the target.

The severity of this finding is variable because it depends on what the correlation reveals: a scan that returns only the public tech stack is `Informational`, while one that correlates an email to still-valid breach credentials or to an exposed asset is `High`.

### Execution

Installation and start of the local web interface:

```Bash
# Installation
git clone https://github.com/smicallef/spiderfoot.git
cd spiderfoot
pip3 install -r requirements.txt

# Start the web UI on localhost (local access only)
python3 ./sf.py -l 127.0.0.1:5001
```

API key configuration (Settings > Module Settings): without the free API keys of Shodan, HaveIBeenPwned, VirusTotal and Hunter.io, the results are drastically reduced. This is the single factor that most impacts the quality of the output.

Start of a **passive-only** scan from the CLI (to stay Zero-Touch):

```Bash
# Passive scan: -u passive uses only modules that do not contact the target
python3 ./sf.py -s nicholas-arcari.github.io -u passive -o csv > spiderfoot_passive.csv

# Scan by data type (example: only emails and subdomains)
python3 ./sf.py -s target.com -t EMAILADDR,INTERNET_NAME
```

Expected output (summary, CSV format):

```
Source Module, Type, Data
sfp_dnsresolve, IP Address, 185.199.108.153            <-- GitHub Pages IP
sfp_hunter, Email Address, contact@target.com
sfp_haveibeenpwned, Hacked Email, contact@target.com   <-- OSINT-005: email in breach
sfp_crt, Internet Name, dev.target.com                 <-- subdomain from Certificate Transparency
sfp_shodan, Open TCP Port, 185.199.x.x:443
sfp_github, Raw Data from Public Repos, "API_KEY=AKIA..."  <-- correlation to secret leakage (see OSINT-006)
```

> [Screenshot placeholder: capture SpiderFoot's correlation graph (the "Graph" tab) and the "Browse" view with the per-data-type count during the lab execution, saving it to `./img/`.]

<!-- screenshot placeholder: SpiderFoot correlation graph (img/spiderfoot-graph-PLACEHOLDER.jpg) -->

### Lab experience

Execution confirmed how much the API key configuration affects the volume of results: without keys the frameworks are limited to open sources and return a sparse graph, whereas with the free keys of the main services enabled the coverage of subdomains, emails and correlated data breaches grows noticeably. We chose to operate in strictly passive mode, disabling the modules that generate traffic towards the target, so as not to leave the OSINT perimeter and not to leave traces: a choice consistent with the passive recon phase of the project. The cost is time - the passive scan is slower because it queries many external sources - and the presence of false positives in the automatic correlation, typically emails or names that are merely homonyms and do not really belong to the target, validated manually before being considered. The highest-value data turned out to be the correlation between subdomains and exposed technologies, which feeds directly into the subsequent scanning and web recon phases.

Typical attention points of this type of scan, to verify during execution:

- SpiderFoot classifies some DNS modules as passive even if they perform resolutions: for absolute invisibility use `-u passive` and manually check the list of activated modules.
- The `sfp_github` module can return false positives (repositories of namesakes): every hit must be validated before being included in a report.
- The email-breach correlation depends on the state of the HIBP API: a negative result must always be manually validated as described in `breach-data/`.

### Theoretical analysis

An OSINT framework does not add new sources compared to manual research: it queries the same public APIs an analyst would consult one at a time. The added value is in the **correlation engine**, which treats each datum as a typed node (email, domain, IP, hash) and applies expansion rules: when a module produces an `INTERNET_NAME`, other modules automatically take it as input and resolve it, search it on Shodan, extract its certificates. This iterative process (called "correlation cascade") automatically reconstructs the graph that manually would require linking dozens of results by hand.

The choice among the three frameworks depends on the objective: SpiderFoot for maximum automatic coverage, recon-ng for a controlled and repeatable workflow in scripts, Maltego when the visual analysis of relationships is the deliverable itself (e.g. mapping the structure of a corporate group with multiple subsidiaries).

---

## Recon-ng - modular OSINT framework

### Operational context

recon-ng adopts the interface and philosophy of Metasploit applied to OSINT: isolated workspaces, an internal database (SQLite) that accumulates the results, and a marketplace of installable modules. It is the ideal framework when a repeatable and documentable process is needed, because every command is tracked and the database can be exported as structured evidence.

### Execution

```Bash
# Start and creation of a workspace dedicated to the target
recon-ng
[recon-ng][default] > workspaces create target_engagement

# Installation of the modules from the marketplace
[recon-ng][target_engagement] > marketplace install all

# Insertion of the starting datum (seed)
[recon-ng][target_engagement] > db insert domains
domain (TEXT): target.com

# Subdomain enumeration from Certificate Transparency (passive)
[recon-ng][target_engagement] > modules load recon/domains-hosts/certificate_transparency
[recon-ng][...][certificate_transparency] > run

# Contact/email harvesting
[recon-ng][target_engagement] > modules load recon/domains-contacts/whois_pocs
[recon-ng][...] > run

# Export of the final report
[recon-ng][target_engagement] > modules load reporting/html
[recon-ng][...][html] > options set FILENAME /home/kali/recon_report.html
[recon-ng][...][html] > run
```

Expected output (hosts table in the internal database):

```
  +---------------------------------------------------------------+
  | host              | ip_address      | region  | module        |
  +---------------------------------------------------------------+
  | dev.target.com    | 10.x.x.x        |         | cert_transp.  |  <-- dev subdomain
  | vpn.target.com    | 185.x.x.x       |         | cert_transp.  |  <-- remote access vector
  | mail.target.com   | 185.x.x.x       |         | cert_transp.  |
  +---------------------------------------------------------------+
  [*] 3 total (3 new) hosts found.
```

> [Screenshot placeholder: capture the recon-ng dashboard with the populated `hosts` table (`show hosts`) and the generated HTML report.]

### Analysis of the results

Subdomains with names like `vpn`, `dev`, `sso`, `staging` are a priority: they indicate remote-access vectors or environments less protected than production. This list becomes direct input for `03-dns-enumeration/subdomain-finding/` and for the web recon in `03-web-attacks/02-web-recon/`.

---

## Maltego - visual graph analysis

### Operational context

Maltego is not a scanner but a **link analysis** tool: it starts from an entity (domain, person, email) and applies "transforms", that is, queries toward data sources that return linked entities, visualized as a graph. It is the reference tool for complex investigations where the structure of the relationships is the result: mapping the subsidiaries of a group, reconstructing a network of people, linking infrastructures via shared certificates.

### Execution

The use is predominantly graphical (GUI):

```
[1] Create a new graph (New Graph)
[2] Drag a "Domain" entity and set target.com
[3] Run the passive transforms:
     +-- "To DNS Name [Using Robtex]"     -> subdomains
     +-- "To Email Addresses [PGP]"       -> emails from PGP servers
     +-- "To Website"                     -> linked sites
     +-- "To Entities [IBM Watson]"       -> people and organizations
[4] Iteratively expand the nodes of interest
```

> [Screenshot placeholder: capture the Maltego graph with the target domain expanded into subdomains, emails and linked entities.]

**Limits of the Community Edition:** Maltego CE limits the results per transform (typically 12 entities) and requires registration. For a real engagement the Classic/XL version removes the limits. For the lab, the CE is sufficient to demonstrate the methodology.

### Theoretical analysis

Maltego's data model (entities + transforms) is the visual formalization of the same "OSINT graph" that SpiderFoot builds internally. The difference is control: in Maltego the analyst manually decides which node to expand and with which transform, avoiding the noise of a total automatic scan. This makes it superior when the number of entities is high and one needs to discriminate which relationships are relevant.

---

## Recommended operational flow

```
[INPUT] A starting datum (domain / email / name)
          |
          v
[1] Massive automatic collection (SpiderFoot -u passive)
     +-- 200+ sources in parallel -> CSV/DB with all the raw data
          |
          v
[2] Controlled and repeatable workflow (recon-ng)
     +-- selected modules -> structured database -> HTML report
          |
          v
[3] Visual analysis of the relationships (Maltego)
     +-- manual expansion of the critical nodes -> relationship graph
          |
          v
[4] Correlation and manual validation
     +-- removal of false positives, verification of critical hits
          |
          v
[OUTPUT] OSINT graph of the target -> input for 03-dns, 04-infra-intel, 05-social-engineering
```

---

## Real-World scenario: Post-Reconnaissance projection

> This section describes how OSINT-005 would fit into a real engagement, from the attacker's and defender's perspectives. Applicable when the correlation reaches `High` severity.

### Attacker perspective (red team)

**Starting point:** complete OSINT graph of the target with employee emails, subdomains (including `vpn`, `dev`), exposed assets and at least one email correlated to a breach.

**Immediate next step:** crossing the `vpn`/`sso` subdomains with the breach credentials for a Credential Stuffing attempt on the remote-access portal.

**Projected kill chain:**

```
OSINT-005: correlated graph (employee emails + vpn.target.com + breach)
        |
        v
Credential Stuffing on vpn.target.com (passwords reused from breaches)
        |
        v
VPN access -> internal network -> pivoting (07-post-exploitation)
        |
        v
Lateral movement and persistence
```

**Potential impact:** OSINT aggregation drastically reduces the preparation time of a targeted attack. A complete graph turns a generic campaign into a tailored Spear Phishing and Credential Stuffing campaign, with much higher success rates.

### Defender perspective (blue team)

**Detection:** passive OSINT is by definition invisible (no contact with the target systems). Detection does not happen on the single event but on the result: monitoring one's own exposure with the same tools (periodic self-OSINT) and alerting on anomalous login attempts that follow the collection phase.

**Indicators of Compromise (IOC):**
- Spike of failed authentication attempts on VPN/SSO portals from new IPs (Credential Stuffing phase post-OSINT)
- Appearance of new subdomains or corporate assets in the results of SpiderFoot/Shodan run in self-assessment

**Containment:** MFA enforcement on all exposed portals (neutralizes Credential Stuffing based on breach passwords), rotation of the credentials of employees present in known breaches.

**Eradication and hardening:**
- Periodic self-OSINT program: run SpiderFoot/recon-ng on your own perimeter to see what the attacker sees
- Minimize the exposure of corporate emails in standard format (`name.surname@`) on public sources
- Anti-phishing training based on the data actually exposed

**Defensive lesson:** you cannot protect what you do not know you are exposing. The only way to defend against passive reconnaissance is to know your OSINT footprint in advance and eliminate it or monitor it.

---

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `SpiderFoot` | osint aggregator | cli / web (local) | automatic collection from 200+ sources with correlation |
| `recon-ng` | osint framework | cli (modular) | repeatable osint workflow with database and reporting |
| `Maltego` | link analysis | gui | visual analysis of the relationship graph between entities |
| `theHarvester` | email/subdomain harvesting | cli | targeted email/subdomain collection (see `email-harvesting/`) |
| `Amass` (owasp) | subdomain/osint | cli | asset enumeration and infrastructure correlation |

> **Recommended modern tool:** `SpiderFoot HX` (commercial cloud version) and `Amass intel` (`amass intel -org "Target Corp"` to discover the IP ranges and ASes associated with an organization starting from the name). Amass is actively maintained by OWASP and integrates Certificate Transparency, passive DNS sources and ASN correlation in a single CLI tool, ideal for pipeline automation.

---

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| reconnaissance | gather victim identity info: email addresses | `T1589.002` | automatic aggregation of the target's emails from multiple sources via spiderfoot and recon-ng (OSINT-005) |
| reconnaissance | search open technical databases: whois | `T1596.002` | collection of whois data and contacts via recon-ng modules (OSINT-005) |
| reconnaissance | search open websites/domains: search engines | `T1593.002` | automatic correlation of public data indexed by search engines and archives (OSINT-005) |
| reconnaissance | gather victim network info: dns | `T1590.002` | subdomain enumeration from certificate transparency via recon-ng and spiderfoot (OSINT-005) |
| reconnaissance | search open websites/domains: social media | `T1593.001` | aggregation of social presence and identity correlation in the osint graph (OSINT-005) |

---

> **Note:** The OSINT scans documented in this section were performed for educational purposes on the personal domain `nicholas-arcari.github.io` and on authorized targets. The active modules were disabled to maintain invisibility to the target. No correlated data (emails, breach credentials) was used to attempt unauthorized access.
