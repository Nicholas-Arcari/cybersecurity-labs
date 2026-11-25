> **English** | [Italiano](REPORT_STANDARDS.md)

# Report Writing Standards - Cybersecurity Labs

> Reference document for the professional writing of technical READMEs in this repository.
> Compliance with these rules is mandatory to maintain consistency, quality and professional
> readability across all modules. Update this file whenever a new convention is defined.

---

## Table of Contents

1. [Work progress status](#1-work-progress-status)
2. [Language and style](#2-language-and-style)
3. [Mandatory README structure](#3-mandatory-readme-structure)
4. [Finding ID system](#4-finding-id-system)
5. [Severity scale](#5-severity-scale)
6. [MITRE ATT&CK format](#6-mitre-attck-format)
7. [Tool documentation](#7-tool-documentation)
8. [Text outputs and code blocks](#8-text-outputs-and-code-blocks)
9. [Diagrams and operational flows](#9-diagrams-and-operational-flows)
10. [Remediation section (Blue Team)](#10-remediation-section-blue-team)
11. [Cross-referencing between sections](#11-cross-referencing-between-sections)
12. [Forbidden characters and formatting](#12-forbidden-characters-and-formatting)
13. [Anti-patterns to avoid](#13-anti-patterns-to-avoid)
14. [Pre-publication checklist](#14-pre-publication-checklist)
15. [The Three Dimensions of the Report](#15-the-three-dimensions-of-the-report)
16. [Projection Towards Real-World Scenarios](#16-projection-towards-real-world-scenarios)

---

## 1. Work Progress Status

### READMEs completed and compliant with standards

| Module | File | Status | Notes |
| :--- | :--- | :---: | :--- |
| 00-setup | all (21 files) | Complete | Hardening guide: no finding IDs, no MITRE (setup/config) |
| Root | `README.md` | Complete | Updated structure, finding table and aggregated MITRE |
| 01-recon | `README.md` | Complete | Finding registry + MITRE ATT&CK master table |
| 01-recon | `01-osint-passive/README.md` | Complete | Finding ID, severity, text outputs, MITRE |
| 01-recon | `02-network-scanning-active/README.md` | Complete | Finding ID, severity, text outputs, MITRE |
| 01-recon | `03-dns-enumeration/README.md` | Complete | Finding ID, severity, text outputs, MITRE |
| 01-recon | `04-infrastructure-intel/README.md` | Complete | Finding ID, severity, text outputs, MITRE |
| 02-vulnerability-assessment | `README.md` | Complete | Finding registry + aggregated MITRE ATT&CK |
| 02-vulnerability-assessment | `01-general-scanners/README.md` | Complete | Overview of 3 scanners |
| 02-vulnerability-assessment | `01-general-scanners/nessus/README.md` | Complete | VULN-001, VULN-002, credentialed scan |
| 02-vulnerability-assessment | `01-general-scanners/nmap-nse-vuln/README.md` | Complete | NSE scripts, categories, workflow |
| 02-vulnerability-assessment | `01-general-scanners/open-vas-gvm/README.md` | Complete | GVM setup, PostgreSQL troubleshooting |
| 02-vulnerability-assessment | `02-protocol-specific-audit/README.md` | Complete | Protocol audit overview |
| 02-vulnerability-assessment | `02-protocol-specific-audit/smb-net-bios/README.md` | Complete | VULN-003, VULN-004, C$ access |
| 02-vulnerability-assessment | `02-protocol-specific-audit/smtp/README.md` | Complete | VULN-005, filtered port |
| 02-vulnerability-assessment | `02-protocol-specific-audit/snmp/README.md` | Complete | VULN-006, SNMP absent |
| 02-vulnerability-assessment | `02-protocol-specific-audit/ssl-tls/README.md` | Complete | testssl.sh/sslscan methodology, lab to be completed |
| 02-vulnerability-assessment | `03-cve-analysis/README.md` | Complete | CVE analysis overview |
| 02-vulnerability-assessment | `03-cve-analysis/cvss-calculator/README.md` | Complete | CVSS v3.1, Python, contextual scoring |
| 02-vulnerability-assessment | `03-cve-analysis/searchsploit-manual-lookup/README.md` | Complete | Searchsploit, msfvenom, code analysis |
| 02-vulnerability-assessment | `03-cve-analysis/vulnerability-databases/README.md` | Complete | CVE/NVD/Exploit-DB cross-referencing |
| 02-vulnerability-assessment | `04-reporting-templates/README.md` | Complete | Reporting templates overview |
| 02-vulnerability-assessment | `04-reporting-templates/executive-summary-template/README.md` | Complete | Template + filled example |
| 02-vulnerability-assessment | `04-reporting-templates/technical-findings-template/README.md` | Complete | Template + 3 filled examples |
| 03-web-attacks | all | Complete | WEB-001..015, 34 READMEs written |
| 04-system-exploitation | `01-frameworks/README.md` | Complete | Finding registry EXPLOIT-001..004, aggregated MITRE |
| 04-system-exploitation | `01-frameworks/empire/README.md` | Complete | EXPLOIT-001, EXPLOIT-002, Real-World Scenario |
| 04-system-exploitation | `01-frameworks/metasploit/README.md` | Complete | EXPLOIT-003, EXPLOIT-004, SOCKS pivoting |
| 04-system-exploitation | `02-exploit-database/README.md` | Complete | Finding registry EXPLOIT-005..007, aggregated MITRE |
| 04-system-exploitation | `02-exploit-database/compiled-exploits/README.md` | Complete | EXPLOIT-005, EXPLOIT-006, MinGW cross-compilation |
| 04-system-exploitation | `02-exploit-database/searchsploit/README.md` | Complete | EXPLOIT-007, offline exploit research |
| 04-system-exploitation | `03-privilege-escalation/README.md` | Complete | Finding registry EXPLOIT-008..019, aggregated MITRE |
| 04-system-exploitation | `03-privilege-escalation/linux-priv-esc/README.md` | Complete | Finding registry EXPLOIT-008..012, Linux MITRE |
| 04-system-exploitation | `03-privilege-escalation/linux-priv-esc/gtfo-bins-notes/README.md` | Complete | EXPLOIT-008, EXPLOIT-009, LotL sudo/SUID |
| 04-system-exploitation | `03-privilege-escalation/linux-priv-esc/linpeas/README.md` | Complete | EXPLOIT-010, EXPLOIT-011, EXPLOIT-012 |
| 04-system-exploitation | `03-privilege-escalation/windows-priv-esc/README.md` | Complete | Finding registry EXPLOIT-013..019, Windows MITRE |
| 04-system-exploitation | `03-privilege-escalation/windows-priv-esc/juicypotato-printnightmare/README.md` | Complete | EXPLOIT-013, EXPLOIT-014, PrintSpoofer SYSTEM |
| 04-system-exploitation | `03-privilege-escalation/windows-priv-esc/sherlock/README.md` | Complete | EXPLOIT-015, kernel patch audit |
| 04-system-exploitation | `03-privilege-escalation/windows-priv-esc/winpeas/README.md` | Complete | EXPLOIT-016..019, Unattend.xml + XAMPP ACL |
| 04-system-exploitation | `04-binary-exploitation/README.md` | Complete | Finding registry EXPLOIT-020..021, aggregated MITRE |
| 04-system-exploitation | `04-binary-exploitation/buffer-overflow-prep/README.md` | Complete | EXPLOIT-020, classic stack overflow, Immunity + Mona.py |
| 04-system-exploitation | `04-binary-exploitation/pwntools-scripts/README.md` | Complete | EXPLOIT-021, ROP chain, ASLR/DEP bypass, Ret2Libc |
| 04-system-exploitation | `05-password-cracking/README.md` | Complete | Finding registry EXPLOIT-022..025, aggregated MITRE |
| 04-system-exploitation | `05-password-cracking/hashcat/README.md` | Complete | EXPLOIT-022, EXPLOIT-023, Mask + Rule-based Attack NTLM |
| 04-system-exploitation | `05-password-cracking/john-the-ripper/README.md` | Complete | EXPLOIT-024, EXPLOIT-025, ZIP cracking + Linux unshadowing |
| 04-system-exploitation | `05-password-cracking/wordlists/README.md` | Complete | Wordlist guide: RockYou, SecLists, CeWL, CUPP |
| 05-social-engineering | all | To do | - |
| 06-wireless-security | all | To do | - |
| 07-post-exploitation | all | To do | - |
| 08-defense-hardenings | all | To do | - |
| 09-digital-forensics | all | To do | - |
| 10-cloud-security | all | To do | - |

### Finding ID Global Sequence

| Prefix | Module | Next available ID |
| :--- | :--- | :--- |
| `OSINT-` | 01-recon/01-osint-passive | `OSINT-005` |
| `SCAN-` | 01-recon/02-network-scanning | `SCAN-004` |
| `DNS-` | 01-recon/03-dns-enumeration | `DNS-004` |
| `INTEL-` | 01-recon/04-infrastructure-intel | `INTEL-005` |
| `VULN-` | 02-vulnerability-assessment | `VULN-007` |
| `WEB-` | 03-web-attacks | `WEB-016` |
| `EXPLOIT-` | 04-system-exploitation | `EXPLOIT-026` |
| `SE-` | 05-social-engineering | `SE-001` |
| `WIFI-` | 06-wireless-security | `WIFI-001` |
| `POST-` | 07-post-exploitation | `POST-001` |
| `DEF-` | 08-defense-hardenings | `DEF-001` |
| `FOR-` | 09-digital-forensics | `FOR-001` |
| `CLOUD-` | 10-cloud-security | `CLOUD-001` |

---

## 2. Language and Style

### Language

- **Primary language: Italian.** All narrative text, explanations, section titles and
  operational notes are written in Italian.
- **Accepted English exceptions:** tool proper names (`Nmap`, `Sherlock`, `Masscan`), standard
  technical terms (`payload`, `exploit`, `banner`, `finding`, `scope`, `engagement`, `shellcode`),
  MITRE IDs (`T1046`), technology names (`SMB`, `RDP`, `TLS`), tool outputs (always in original language).
- **Do not translate** established industry technical terms: use `finding` not `result`,
  `misconfiguration` not `wrong configuration`, `payload` not `payload equivalent`.

### Narrative Style

- Write in **impersonal third person** or first person plural: "the scan reveals", "the analysis
  highlighted", not "I did", "I found".
- **Always explain the WHY before the HOW.** Operational context and impact first,
  then commands. A recruiter or client reads why that technique is relevant first, then
  how to execute it.
- **Active voice** and short sentences. Avoid unnecessary subordinate clauses.
- Do not use informal tones ("easy", "simple", "just run"). The document should appear
  written by a senior professional for a client or a peer-level colleague.

---

## 3. Mandatory README Structure

Every subfolder README (specific technique) must follow this template in the indicated order.
Mandatory sections are marked with [M], optional sections with [O] (optional if not applicable).

```
# [Number] - [Descriptive Title]                              [M]

> - **Phase:** [phase name] - [sub-phase name]                [M]
> - **Visibility:** [Zero / Low / High] - [explanation]        [M]
> - **Prerequisites:** [what is needed beforehand]             [M]
> - **Output:** [what this phase produces]                     [M]

---

## Introduction                                                [M]
[Paragraph explaining the WHY of this phase/technique,
 its positioning in the kill chain and operational value]

---

## Folder Structure                                            [M if has subfolders]
[Code block with directory tree and comments]

---

## `subfolder-name/` - Technique Title                        [M for each subfolder]

**Finding ID:** `XXX-NNN` | **Severity:** `[level]`           [M if technique produces a finding]

### What You'll Find                                           [M]
### Operational Context                                        [M]
### Execution / Commands                                       [M]
[bash block with commands]
[structured example output block]                              [O if not applicable]
### Results Analysis / Documented Finding                      [M]
### Remediation                                                [M - always, even brief]

---

## Recommended Operational Flow                                [M]
[ASCII diagram with sequence and decisions]

---

## Reference Tools                                             [M]
[table Tool | Type | Command/Access | Use Case]

---

## MITRE ATT&CK Mapping                                       [M]
[table Tactic | Technique | MITRE ID | Action Description]

---

> **Note:** [disclaimer about authorized targets / lab]        [M]
```

### Parent Section READMEs (e.g., `01-recon/README.md`)

Parent READMEs have a different structure: they are navigation and summary documents, not technical guides.
They must contain:

1. Header metadata (same as children)
2. Phase introduction (positioning in the kill chain)
3. Folder structure with description of each subfolder
4. Operational flow for the entire phase
5. **Finding Registry** (table ID | Description | Severity | Subfolder)
6. **Aggregated MITRE ATT&CK Mapping** (all techniques in the section)
7. Disclaimer note

---

## 4. Finding ID System

### Format

```
[PREFIX]-[NNN]
```

- `[PREFIX]`: uppercase abbreviation of the module (see table in section 1)
- `[NNN]`: sequential three-digit number, starting from `001`
- Examples: `OSINT-001`, `SCAN-003`, `DNS-001`, `EXPLOIT-005`

### Assignment Rules

- IDs are **sequential and never reused**, even if a finding is removed.
- IDs are **globally unique** within the repository: no two findings with the
  same ID exist in different modules.
- The sequence restarts at `001` for each prefix/module but not for each file: `OSINT-001`
  is assigned in `breach-data/` and `OSINT-004` is assigned in `user-enumeration/`, all
  belonging to the same OSINT sequence.
- Always update the "Finding ID Global Sequence" table in this file when adding
  new findings.

### Positioning in Text

The finding ID badge is positioned **immediately after the section title** that introduces
the finding, before the descriptive text, on a dedicated line:

```markdown
## `section-name/` - Technique Title

**Finding ID:** `OSINT-001` | **Severity:** `High`

### What You'll Find
```

For nested findings within a larger section (e.g., two findings in the same
subfolder), the badge is positioned after the sub-paragraph title:

```markdown
#### Finding 1 - Information Disclosure (NetBIOS)

**Finding ID:** `SCAN-002` | **Severity:** `Low`
```

---

## 5. Severity Scale

Use exclusively the following five levels, written in Italian, in backticks in text:

| Level | Backtick | Assignment Criteria |
| :--- | :--- | :--- |
| Critical | `Critico` | Immediate and total compromise of the system or infrastructure. Example: successful Zone Transfer, unauthenticated RCE, plaintext admin credentials. |
| High | `Alto` | Unauthorized access to sensitive data or probable privilege escalation with low effort. Example: SMB Signing not mandatory (SMB Relay vector), credentials in active breaches. |
| Medium | `Medio` | Exploitable vulnerability with moderate effort or specific conditions. Example: hidden Virtual Host accessible, self-signed certificates, information facilitating subsequent attacks. |
| Low | `Basso` | Information useful for further attacks but not directly exploitable. Example: NetBIOS name disclosure, username on social networks. |
| Informational | `Informativo` | Data relevant for attack surface mapping, no direct risk. Example: active hosts identified, WAF/CDN detected, technology stack confirmed. |

### Variable Severity

If severity depends on found content (e.g., Google Dorks that may find nothing or find
credentials), use the format:

```markdown
**Severity:** `Variable (Medium / High)`
```

Explain in the body text what determines the effective severity.

---

## 6. MITRE ATT&CK Format

### Standard Table

The MITRE ATT&CK table is **mandatory** in every technical README. It is always positioned
**at the end of the document**, before the final disclaimer note, separated by `---`.

```markdown
---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| [Tactic] | [Extended Technique Name] | `T1234.001` | [What was concretely done, with reference to finding ID if applicable.] |
```

### Compilation Rules

- **Tactic:** use the official MITRE tactic name in English
  (e.g., `Reconnaissance`, `Discovery`, `Credential Access`, `Privilege Escalation`).
- **Technique:** use the official extended English name, including the sub-name after the colon
  if applicable (e.g., `Gather Victim Identity Info: Credentials`).
- **MITRE ID:** always in backtick, format uppercase `T` + number + optional sub-technique
  (e.g., `T1589.001`). Always verify the ID on the official platform attack.mitre.org.
- **Action Description:** in the document language, describe what was concretely done in the lab,
  not what MITRE theory says. Include the correlated Finding ID in parentheses if it exists.

### Aggregated Table in Parent README

Each module's parent README must contain an aggregated MITRE table with an additional
"Correlated Finding" column:

```markdown
| Tactic | Technique | MITRE ID | Correlated Finding |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Identity Info: Credentials | `T1589.001` | OSINT-001 |
```

### Where to Find Correct MITRE IDs

- Official site: `https://attack.mitre.org/techniques/`
- Search by technique: `https://attack.mitre.org/techniques/T1589/`
- Do not invent IDs. If the exact technique is not found, use the parent technique without sub-technique.

---

## 7. Tool Documentation

### Reference Tool Table

Every README must close (before the MITRE section) with a tool table that includes
**also modern equivalent or alternative tools**, not just those used in the documented exercise:

```markdown
| Tool | Type | Technique/Access | Main Use Case |
| :--- | :--- | :--- | :--- |
| `tool-name` | [category] | [passive/active/CLI/Web] | [when and why to use it] |
```

### Accepted Tool Categories

- `Email/Subdomain harvesting`
- `Username enumeration`
- `Breach data`
- `DNS query`
- `Port scanner`
- `Service enumerator`
- `Vulnerability scanner`
- `Tech fingerprint`
- `Exploitation framework`
- `Post-exploitation`
- `Password cracking`
- `Network sniffer`
- `Traffic analyzer`
- `SIEM/Log analysis`

### Note on Modern Tools

When a more modern and maintained tool exists compared to the one used in the exercise, add it
to the table and add a blockquote with explanation:

```markdown
> **Recommended modern tool:** `name` - explanation of advantage over previous tool
> and example command.
```

Modern tools to prefer (updated to 2025-2026):

| Classic tool | Modern alternative | Reason |
| :--- | :--- | :--- |
| `Sublist3r` | `amass` (OWASP) | More powerful, actively maintained, more sources |
| `httprobe` | `httpx` (ProjectDiscovery) | Faster, provides status code + title + tech |
| `Masscan` (on VM) | `RustScan` | Compatible with virtualized NAT, more stable |
| `theHarvester` base | `theHarvester` + Hunter.io API | Without API key results are very limited |
| Manual scanner | `nuclei` (ProjectDiscovery) | Template-based, thousands of pre-written CVEs |
| `enum4linux` | `enum4linux-ng` | Modern rewrite, more stable on recent environments |
| `CrackMapExec` | `NetExec` (nxc) | Active fork after original repo was abandoned |

---

## 8. Text Outputs and Code Blocks

### When to Include Text Outputs

Include a structured output block (even synthetic/example) whenever:
- The command is shown for the first time in that context
- The output contains relevant findings to highlight
- The output demonstrates a misconfiguration or critical data

Full and lengthy outputs are not necessary: use **synthetic but realistic** outputs
that show the relevant lines. Annotate the most important lines with `<--`.

### Code Block Format

```markdown
Command block:
    ```Bash
    sudo nmap -p 445 -sC 10.0.2.3
    ```

Structured output block (example):
    ```
    PORT    STATE SERVICE
    445/tcp open  microsoft-ds
    | smb2-security-mode:
    |_    Message signing enabled but not required    <-- SCAN-003
    | nbstat: NetBIOS name: WINDOWS-TEST              <-- SCAN-002
    ```
```

### Code Block Rules

- Commands are **always** in ` ```Bash ` blocks with language specification.
- Outputs are in ` ``` ` blocks without language specification.
- Configuration files are in ` ```plaintext ` blocks or with the specific language
  (` ```xml `, ` ```json `, etc.).
- Inline output annotations use `<--` with a space before and brief description.
- Do not paste huge outputs: trim with `[... truncated output ...]` if necessary.
- Commands with placeholders use `<PLACEHOLDER>` in uppercase with angle brackets.

### Screenshot vs Text Output

- **Always prefer text output** when available: it is verifiable, copyable, searchable.
- Screenshots are accepted only when the output is graphical (GUI, browser, dashboard).
- If only a screenshot is available but not the text, indicate:
  `[Output available in ./img/Screenshot_YYYY-MM-DD.jpg]`
- **Never replace a text output with a screenshot** of a terminal.

---

## 9. Diagrams and Operational Flows

### When to Include an Operational Flow

Mandatory in parent READMEs for each module. Optional (but recommended) in complex
technical READMEs with multiple sequential steps or conditional decisions.

### Mandatory ASCII Format

Use exclusively pure ASCII in diagrams, compatible with any Markdown viewer.

**Allowed characters for diagrams:**

```
Horizontal lines:    ---
Vertical lines:      |
Arrows:              -> (right), <- (left), v (down), ^ (up)
Branch:              +-- (branch from vertical line)
Connectors:          +   (intersection)
Simple boxes:        [text]  (text)
Inline comments:     # comment
```

**FORBIDDEN characters in diagrams** (cause issues on some viewers):

```
- Unicode arrows:  -->, -->, <=>, =>
- Unicode boxes:   +--+, |  |
- Special symbols: ►, ◄, ●, ○
```

Correct flow example:

```markdown
    ```
    [1] Live Host Discovery
         +-- arp-scan -l  ->  list of active LAN IPs
                  |
                  v
    [2] Port Discovery
         +-- masscan -p1-65535 <IP> --rate=1000
                  |
                  v
    [3] Deep Enumeration
         +-- nmap -sC -p<ports> <IP>
                  |
                  v
         [Output] -> attack surface map
    ```
```

---

## 10. Remediation Section (Blue Team)

### Requirement

The Remediation section is **mandatory for every finding with Critical, High or Medium severity**.
For Low and Informational findings it is optional but recommended.

### Positioning

Immediately after the finding description and its analysis, before the next section.

### Minimum Structure

```markdown
### Remediation

- **Immediate action:** [what to do immediately to mitigate]
- **Structural action:** [how to resolve the root cause]
- **Verification:** [how to confirm the remediation worked]
```

### Tone

Remediation is written from the **Blue Team / Defender** perspective, not the attacker's.
Use a technical but action-oriented tone. Always specify the component to configure
(e.g., "GPO: `Microsoft network server: Digitally sign communications`") not just the generic
category ("enable SMB signing").

---

## 11. Cross-referencing Between Sections

### How to Reference Other Modules

When a technique or finding in one section directly connects to another section
in the repository, indicate it explicitly:

```markdown
The subdomain list produced becomes direct input for
`03-web-attacks/02-web-recon/`.

The SMB Signing misconfiguration (SCAN-003) is exploited in phase
`07-post-exploitation/04-pivoting-tunneling/`.
```

### How to Reference Findings

In current text, reference previous or correlated findings with their ID in backticks:

```markdown
This finding confirms what was already detected in `DNS-001`: the target's
DNS attack surface is completely exposed.
```

### How to Reference Tools in Other Modules

```markdown
For vulnerability scanning on found subdomains, see
`02-vulnerability-assessment/01-general-scanners/nmap-nse-vuln/`.
```

---

## 12. Forbidden Characters and Formatting

### Em Dash Character (FORBIDDEN)

The character `—` (U+2014, em dash) is **absolutely forbidden** throughout the repository.

- WRONG: `This tool - used in Red Team — is very powerful`
- CORRECT: `This tool - used in Red Team - is very powerful`

To check for em dash presence in a file:

```Bash
grep -P "\xe2\x80\x94" file.md
```

To replace all em dashes in a file:

```Bash
python3 -c "
content = open('file.md').read()
open('file.md', 'w').write(content.replace('\u2014', '-'))
"
```

### Unicode Arrows in Text (FORBIDDEN outside code blocks)

- FORBIDDEN in narrative text: `->`, `=>`, `-->`, and any unicode arrow
- ALLOWED only inside code blocks ` ``` ` for ASCII diagrams

### Headings with Blockquote in Metadata

The header metadata uses **simple hyphen + space** as separator, not arrows or em dashes:

```markdown
# Correct:
> - **Phase:** Reconnaissance - Passive Information Gathering
> - **Visibility:** Zero - no packets sent

# WRONG:
> **Phase:** Reconnaissance -> Passive Information Gathering
> **Visibility:** Zero — no packets sent
```

### Accents and Special Characters in Text

Accented vowels are allowed in Italian narrative text.
In code blocks and commands, use exclusively pure ASCII (no accents).

---

## 13. Anti-patterns to Avoid

### Content Anti-patterns

| Anti-pattern | Problem | Correction |
| :--- | :--- | :--- |
| "Just run `nmap`" | Informal tone, doesn't explain why | Always explain context and motivation before the command |
| List of commands without explanation | Doesn't demonstrate understanding | Every command must have a line of operational context |
| "As seen in the screenshot" | Not verifiable, not searchable | Always accompany with text output when possible |
| Severity not assigned | Unclassified finding | Every finding must have ID and severity |
| Finding without remediation | Incomplete document | Always add at least one line of remediation |
| Tool without version | Not reproducible | Specify version when critical for reproducibility (e.g., "Nmap 7.94") |
| Unauthorized target used without note | Legal/reputational risk | Always declare the authorization perimeter |
| Missing MITRE section | Not professional | Mandatory in every technical README |
| Em dash in text | Inconsistency, standard violation | Replace with simple hyphen `-` |
| English text where not necessary | Linguistic inconsistency | Use Italian for all narrative (in Italian version) |

### Structural Anti-patterns

- **Do not create a README that is just a list of commands:** every document must have
  introduction, operational context, analysis and conclusions.
- **Do not duplicate content between parent and child README:** the parent provides summary and navigation,
  the child provides technical detail.
- **Do not omit the operational flow:** the reader must understand the order in which to execute activities.
- **Do not use generic titles:** instead of `## Analysis`, use `## Critical Analysis: false negatives
  in virtualized environment`.

---

## 14. Pre-publication Checklist

Before considering a README completed, verify all points:

### Structure

- [ ] Header metadata present with Phase, Visibility, Prerequisites, Output
- [ ] Introduction with positioning in the kill chain
- [ ] Folder structure documented (if applicable)
- [ ] Each subfolder has its own section

### Findings

- [ ] Each finding has a unique ID in `PREFIX-NNN` format
- [ ] Each finding has a severity assigned from the standard scale
- [ ] ID sequence updated in `REPORT_STANDARDS.md` (section 1 table)
- [ ] Critical and High findings have complete remediation section

### Technical Content

- [ ] Each technique has operational context (why before how)
- [ ] Main commands have an example output block
- [ ] `<--` annotations highlight the most important output lines
- [ ] Operational flow is present and uses only allowed ASCII

### Tools

- [ ] Reference tool table present
- [ ] Modern equivalent tools included when they exist
- [ ] `> **Recommended modern tool:**` note present if applicable

### MITRE ATT&CK

- [ ] MITRE section present at end of document
- [ ] Each technique has verified ID on attack.mitre.org
- [ ] Action description is in the document language and refers to concrete lab activity
- [ ] Finding IDs are cited in the description column

### Formatting

- [ ] No em dash `—` in the document (verify with grep)
- [ ] Document language used for all narrative text
- [ ] Code blocks with language specification (`bash`, `plaintext`, etc.)
- [ ] Final disclaimer note present with reference to authorized targets

### Parent README (if updating a module README)

- [ ] Finding Registry updated with all new findings
- [ ] Aggregated MITRE table updated
- [ ] Subfolder description updated in parent README

### Three Dimensions of the Report (Section 15)

- [ ] TECHNICAL dimension: real outputs, CVSS score, finding ID, verified MITRE IDs
- [ ] DESCRIPTIVE dimension: first person (plural) narration of steps performed, problems
  encountered, decisions made during the exercise
- [ ] THEORETICAL dimension: explanation of the principle behind the technique, methodology choice
  motivation, result interpretation in the kill chain context
- [ ] "Real-World Scenario" section present for findings with High or Critical severity (Section 16)

---

## 15. The Three Dimensions of the Report

Every quality technical README must balance three distinct dimensions. A document missing
even one appears incomplete to a senior recruiter or a client.

---

### Dimension 1 - TECHNICAL

**What it is:** precise and reproducible documentation of what was executed.

**How it manifests:**

- Exact commands with all flags, in `bash` blocks
- Real outputs (or realistic synthetic ones) with `<--` annotations
- Finding IDs in standard format, severity from CVSS v3.1 scale
- MITRE ATT&CK IDs verified on attack.mitre.org
- Tool versions when relevant for reproducibility

**Template:**

```markdown
### Test Execution

The tool was configured with the following parameters to maximize coverage
while maintaining a low rate that wouldn't trigger the target's IDS.

```Bash
sudo nmap -sV -sC -p 80,443,8080 --script http-methods 10.0.2.3
```

```
PORT     STATE SERVICE VERSION
80/tcp   open  http    Apache 2.4.41          <-- VULN-002: EOL version
| http-methods:
|   Supported Methods: GET HEAD POST OPTIONS TRACE
|_  Potentially risky methods: TRACE             <-- XST possible
```

**Finding ID:** `WEB-005` | **Severity:** `Medium` | **CVSS v3.1:** 6.1

```

---

### Dimension 2 - DESCRIPTIVE

**What it is:** the narrative of the experience lived during the lab. It transforms a list
of commands into a professional story that demonstrates problem-solving ability and method.

**How it manifests:**

- First person plural narration ("it was observed", "the test returned", "we encountered")
  of steps performed in sequence
- Documentation of problems encountered and how they were resolved (troubleshooting)
- Description of decision moments: why one tool was chosen over another, why the
  approach was changed mid-exercise
- Specific results obtained in this lab, not generic technique results
- Notes on differences from expected behavior (virtualized environment, hardened target,
  unexpected response)

**Template:**

```markdown
### Lab Experience

The first anonymous enumeration attempt was rejected by the target with the message
`[E] Server doesn't allow session using username '', password ''`. This behavior,
correct from a defensive standpoint, required an approach change: the test was
repeated providing standard user credentials to simulate a more realistic
"Compromised Credentials" scenario.

During the authenticated enumeration phase, unexpected data was observed: the account
`nessus_audit` (RID 1001), presumably created for previous Nessus scans, was still
active in the system. In a real engagement this would represent an autonomous attack
vector to investigate separately.

The most significant problem encountered was network latency between the attacker
machine and target in VirtualBox NAT: enum4linux took approximately 4 minutes to
complete the full RID cycle. In a real physical environment the time would be
significantly reduced.
```

---

### Dimension 3 - THEORETICAL

**What it is:** the explanation of the technical principle behind the technique and contextual
interpretation of results. It demonstrates deep understanding, not just mechanical execution.

**How it manifests:**

- Explanation of the protocol or mechanism exploited (at a technical level, not introductory)
- Motivation for the approach choice compared to available alternatives
- Result interpretation: what that finding means in the assessment context,
  not just as an isolated fact
- Kill chain connection: where we are now, what this result opens going forward
- Contextualization relative to target architecture (Windows vs Linux, internal network vs DMZ)

**Template:**

```markdown
### Theoretical Analysis

The SMB (Server Message Block) protocol is designed for resource sharing in Windows
networks. Its authentication relies on the NTLM Challenge-Response mechanism: the
client receives a challenge from the server, combines it with the password's NTLM hash
and sends the response. If SMB Signing is not mandatory, an attacker in a
Man-in-the-Middle position can intercept this response and use it to authenticate
elsewhere (SMB Relay Attack, T1557.001) without knowing the plaintext password.

The choice of enum4linux over more modern tools like enum4linux-ng was dictated by
availability in the lab and greater familiarity with the tool. In a professional
engagement, enum4linux-ng would be preferred for its better error handling and
compatibility with SMBv3 environments.

Finding VULN-004 (C$ access with default credentials) is not a vulnerability in the
SMB protocol itself, but rather the result of poor privileged identity management:
an account with a weak password and local administrator privileges nullifies any
network restriction. This is the most common pattern in corporate breaches documented
in the Verizon DBIR 2024: the vector is almost always the compromised credential,
not the zero-day.
```

---

### How to Balance the Three Dimensions

The three dimensions do not always carry the same weight. Adapt based on document type:

| README Type | Technical | Descriptive | Theoretical |
| :--- | :---: | :---: | :---: |
| Specific technique (e.g., nmap, enum4linux) | High | High | Medium |
| Exploitation (e.g., SQLi, SSTI, Drupalgeddon2) | High | High | High |
| Introductory module (e.g., parent README) | Low | Low | High |
| Secure Coding / Remediation | Medium | Low | High |
| Automated scanner (e.g., Nessus, Nikto) | Medium | High | Low |

---

## 16. Projection Towards Real-World Scenarios

Every README related to findings with `High` or `Critical` severity must include a section
that projects the lab towards a real-world scenario. This section answers the question:
"If this weren't a lab, what would happen next?"

The section must be presented from two parallel perspectives: **attacker** and **defender**.

---

### Positioning in the Document

The "Real-World Scenario" section is inserted **after Conclusions and before the MITRE table**,
separated by `---`. It is a standalone block, not a subsection of the remediation.

---

### Mandatory Template

```markdown
---

## Real-World Scenario: Post-Exploitation Projection

> This section describes how this finding would fit into a real engagement, from both
> the attacker's (Red Team) and defender's (Blue Team) perspective.

### Attacker Perspective (Red Team)

**Starting point:** [state achieved at the end of the lab]

**Immediate next step:** [first concrete action an attacker would take]

**Projected Kill Chain:**
```

[current finding]
        |
        v
[next technique] -> [intermediate objective]
        |
        v
[next technique] -> [final objective: access, persistence, exfiltration, ransomware]

```

**Potential impact:** [concrete consequence for the target organization: data loss,
system encryption, ransom demand, reputational damage]

**Typical monetization vectors:**
- Ransomware: file encryption + cryptocurrency ransom demand
- Data exfiltration: selling data on the dark web (PII, IP, credentials)
- Business Email Compromise: mailbox access for financial fraud
- Access Broker: reselling initial access to other threat actors

### Defender Perspective (Blue Team)

**Detection:** [how the SOC could detect this activity through logs, SIEM, IDS]

**Indicators of Compromise (IOC):**
- [specific log event, e.g., Windows Event ID]
- [anomalous traffic pattern]
- [artifact on disk or in memory]

**Containment:** [immediate actions to stop attack progression]

**Eradication and hardening:** [structural changes to prevent recurrence]

**Defensive lesson:** [security principle demonstrated by this finding]
```

---

### Compiled Example (from SMB/VULN-004)

```markdown
## Real-World Scenario: Post-Exploitation Projection

> This section describes how VULN-004 would fit into a real engagement.

### Attacker Perspective (Red Team)

**Starting point:** access to C$ share on WINDOWS-TEST through nick/1234 credentials
with local administrator privileges.

**Immediate next step:** credential dump from memory with Mimikatz to obtain
NTLM hashes of all users who recently logged into the machine.

**Projected Kill Chain:**

```

VULN-004: C$ access (nick - local admin)
        |
        v
Mimikatz sekurlsa::logonpasswords -> Domain Administrator NTLM hash
        |
        v
Pass-the-Hash / PTK on Domain Controller -> Domain Admin
        |
        v
DCSync (Replication) -> dump all domain hashes
        |
        v
Persistence: Golden Ticket (10-year validity) + backdoor account creation
        |
        v
Ransomware deployment on all hosts via GPO / PsExec

```

**Potential impact:** total compromise of the Active Directory domain. In a real
corporate context, this scenario typically leads to: encryption of all file servers and
critical systems, exfiltration of sensitive data (employee PII, financial data, IP),
ransom demand between $100,000 and $5,000,000 USD (based on CISA 2024 documented cases).

**Typical monetization vectors:**
- Ransomware-as-a-Service (RaaS): groups like LockBit 3.0 or BlackCat/ALPHV
- Double extortion: ransom to decrypt + ransom not to publish data
- Access Broker: reselling initial access on underground forums ($500 - $50,000)

### Defender Perspective (Blue Team)

**Detection:** C$ access generates Event ID 4624 (Logon Type 3 - Network) and Event ID
5140 (A network share object was accessed) in Windows Security logs. A SIEM with a rule
on "C$ access from unauthorized IP" or "administrative share access at unusual hours"
would have triggered an alert within seconds.

**Indicators of Compromise (IOC):**
- Event ID 4624 with LogonType=3 + AccountName=nick + ShareName=C$
- Inbound SMB connections on port 445 from IPs not in the whitelist
- Creation of executable files in system paths via SMB share

**Containment:** immediate machine isolation from the network (switch port quarantine),
forced reset of nick credentials and all local administrative accounts, revocation of
any active sessions (Get-SMBSession | Close-SMBSession in PowerShell).

**Eradication and hardening:**
- Implement Tiering Model: standard account != admin account (never the same credentials)
- Disable hidden administrative shares (C$, ADMIN$) if not needed via GPO
- Enable Windows Defender Credential Guard to protect NTLM hashes in memory
- Implement LAPS (Local Administrator Password Solution) for unique per-machine passwords

**Defensive lesson:** a weak password on an account with elevated privileges nullifies
any perimeter defense. The Least Privilege principle (each account has only the minimum
necessary permissions) would have limited the impact even in case of credential compromise.
```
