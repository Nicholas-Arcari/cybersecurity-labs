> **English** | [Italiano](REPORT_STANDARDS.md)

# Report writing standards - cybersecurity labs

> Reference document for the professional writing of technical READMEs in this repository.
> Compliance with these rules is mandatory to maintain consistency, quality and professional
> readability across all modules. Update this file whenever a new convention is defined.

---

## Table of contents

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

## 1. Work progress status

### READMEs completed and compliant with standards

| module | file | status | notes |
| :--- | :--- | :---: | :--- |
| 00-setup | all (21 files) | complete | hardening guide: no finding ids, no mitre (setup/config) |
| root | `README.md` | complete | updated structure, finding table and aggregated mitre |
| 01-recon | `README.md` | complete | finding registry + mitre att&ck master table |
| 01-recon | `01-osint-passive/README.md` | complete | finding id, severity, text outputs, mitre |
| 01-recon | `02-network-scanning-active/README.md` | complete | finding id, severity, text outputs, mitre |
| 01-recon | `03-dns-enumeration/README.md` | complete | finding id, severity, text outputs, mitre |
| 01-recon | `04-infrastructure-intel/README.md` | complete | finding id, severity, text outputs, mitre |
| 02-vulnerability-assessment | `README.md` | complete | finding registry + aggregated mitre att&ck |
| 02-vulnerability-assessment | `01-general-scanners/README.md` | complete | overview of 3 scanners |
| 02-vulnerability-assessment | `01-general-scanners/nessus/README.md` | complete | VULN-001, VULN-002, credentialed scan |
| 02-vulnerability-assessment | `01-general-scanners/nmap-nse-vuln/README.md` | complete | nse scripts, categories, workflow |
| 02-vulnerability-assessment | `01-general-scanners/open-vas-gvm/README.md` | complete | gvm setup, postgresql troubleshooting |
| 02-vulnerability-assessment | `02-protocol-specific-audit/README.md` | complete | protocol audit overview |
| 02-vulnerability-assessment | `02-protocol-specific-audit/smb-net-bios/README.md` | complete | VULN-003, VULN-004, c$ access |
| 02-vulnerability-assessment | `02-protocol-specific-audit/smtp/README.md` | complete | VULN-005, filtered port |
| 02-vulnerability-assessment | `02-protocol-specific-audit/snmp/README.md` | complete | VULN-006, snmp absent |
| 02-vulnerability-assessment | `02-protocol-specific-audit/ssl-tls/README.md` | complete | testssl.sh/sslscan methodology, lab to be completed |
| 02-vulnerability-assessment | `03-cve-analysis/README.md` | complete | cve analysis overview |
| 02-vulnerability-assessment | `03-cve-analysis/cvss-calculator/README.md` | complete | cvss v3.1, python, contextual scoring |
| 02-vulnerability-assessment | `03-cve-analysis/searchsploit-manual-lookup/README.md` | complete | searchsploit, msfvenom, code analysis |
| 02-vulnerability-assessment | `03-cve-analysis/vulnerability-databases/README.md` | complete | cve/nvd/exploit-db cross-referencing |
| 02-vulnerability-assessment | `04-reporting-templates/README.md` | complete | reporting templates overview |
| 02-vulnerability-assessment | `04-reporting-templates/executive-summary-template/README.md` | complete | template + filled example |
| 02-vulnerability-assessment | `04-reporting-templates/technical-findings-template/README.md` | complete | template + 3 filled examples |
| 03-web-attacks | all | complete | WEB-001..015, 34 readmes written |
| 04-system-exploitation | `01-frameworks/README.md` | complete | finding registry EXPLOIT-001..004, aggregated mitre |
| 04-system-exploitation | `01-frameworks/empire/README.md` | complete | EXPLOIT-001, EXPLOIT-002, real-world scenario |
| 04-system-exploitation | `01-frameworks/metasploit/README.md` | complete | EXPLOIT-003, EXPLOIT-004, socks pivoting |
| 04-system-exploitation | `02-exploit-database/README.md` | complete | finding registry EXPLOIT-005..007, aggregated mitre |
| 04-system-exploitation | `02-exploit-database/compiled-exploits/README.md` | complete | EXPLOIT-005, EXPLOIT-006, mingw cross-compilation |
| 04-system-exploitation | `02-exploit-database/searchsploit/README.md` | complete | EXPLOIT-007, offline exploit research |
| 04-system-exploitation | `03-privilege-escalation/README.md` | complete | finding registry EXPLOIT-008..019, aggregated mitre |
| 04-system-exploitation | `03-privilege-escalation/linux-priv-esc/README.md` | complete | finding registry EXPLOIT-008..012, linux mitre |
| 04-system-exploitation | `03-privilege-escalation/linux-priv-esc/gtfo-bins-notes/README.md` | complete | EXPLOIT-008, EXPLOIT-009, lotl sudo/suid |
| 04-system-exploitation | `03-privilege-escalation/linux-priv-esc/linpeas/README.md` | complete | EXPLOIT-010, EXPLOIT-011, EXPLOIT-012 |
| 04-system-exploitation | `03-privilege-escalation/windows-priv-esc/README.md` | complete | finding registry EXPLOIT-013..019, windows mitre |
| 04-system-exploitation | `03-privilege-escalation/windows-priv-esc/juicypotato-printnightmare/README.md` | complete | EXPLOIT-013, EXPLOIT-014, printspoofer system |
| 04-system-exploitation | `03-privilege-escalation/windows-priv-esc/sherlock/README.md` | complete | EXPLOIT-015, kernel patch audit |
| 04-system-exploitation | `03-privilege-escalation/windows-priv-esc/winpeas/README.md` | complete | EXPLOIT-016..019, unattend.xml + xampp acl |
| 04-system-exploitation | `04-binary-exploitation/README.md` | complete | finding registry EXPLOIT-020..021, aggregated mitre |
| 04-system-exploitation | `04-binary-exploitation/buffer-overflow-prep/README.md` | complete | EXPLOIT-020, classic stack overflow, immunity + mona.py |
| 04-system-exploitation | `04-binary-exploitation/pwntools-scripts/README.md` | complete | EXPLOIT-021, rop chain, aslr/dep bypass, ret2libc |
| 04-system-exploitation | `05-password-cracking/README.md` | complete | finding registry EXPLOIT-022..025, aggregated mitre |
| 04-system-exploitation | `05-password-cracking/hashcat/README.md` | complete | EXPLOIT-022, EXPLOIT-023, mask + rule-based attack ntlm |
| 04-system-exploitation | `05-password-cracking/john-the-ripper/README.md` | complete | EXPLOIT-024, EXPLOIT-025, zip cracking + linux unshadowing |
| 04-system-exploitation | `05-password-cracking/wordlists/README.md` | complete | wordlist guide: rockyou, seclists, cewl, cupp |
| 05-social-engineering | all | to do | - |
| 06-wireless-security | all | to do | - |
| 07-post-exploitation | all | to do | - |
| 08-defense-hardenings | all | to do | - |
| 09-digital-forensics | all | to do | - |
| 10-cloud-security | all | to do | - |

### Finding ID global sequence

| prefix | module | next available id |
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

## 2. Language and style

### Language

- **Primary language: Italian.** All narrative text, explanations, section titles and
  operational notes are written in Italian.
- **Accepted English exceptions:** tool proper names (`Nmap`, `Sherlock`, `Masscan`), standard
  technical terms (`payload`, `exploit`, `banner`, `finding`, `scope`, `engagement`, `shellcode`),
  MITRE IDs (`T1046`), technology names (`SMB`, `RDP`, `TLS`), tool outputs (always in original language).
- **Do not translate** established industry technical terms: use `finding` not `result`,
  `misconfiguration` not `wrong configuration`, `payload` not `payload equivalent`.

### Narrative style

- Write in **impersonal third person** or first person plural: "the scan reveals", "the analysis
  highlighted", not "I did", "I found".
- **Always explain the WHY before the HOW.** Operational context and impact first,
  then commands. A recruiter or client reads why that technique is relevant first, then
  how to execute it.
- **Active voice** and short sentences. Avoid unnecessary subordinate clauses.
- Do not use informal tones ("easy", "simple", "just run"). The document should appear
  written by a senior professional for a client or a peer-level colleague.

---

## 3. Mandatory README structure

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

### Parent section READMEs (e.g., `01-recon/README.md`)

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

## 4. Finding ID system

### Format

```
[PREFIX]-[NNN]
```

- `[PREFIX]`: uppercase abbreviation of the module (see table in section 1)
- `[NNN]`: sequential three-digit number, starting from `001`
- Examples: `OSINT-001`, `SCAN-003`, `DNS-001`, `EXPLOIT-005`

### Assignment rules

- IDs are **sequential and never reused**, even if a finding is removed.
- IDs are **globally unique** within the repository: no two findings with the
  same ID exist in different modules.
- The sequence restarts at `001` for each prefix/module but not for each file: `OSINT-001`
  is assigned in `breach-data/` and `OSINT-004` is assigned in `user-enumeration/`, all
  belonging to the same OSINT sequence.
- Always update the "Finding ID Global Sequence" table in this file when adding
  new findings.

### Positioning in text

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

## 5. Severity scale

Use exclusively the following five levels, written in Italian, in backticks in text:

| level | backtick | assignment criteria |
| :--- | :--- | :--- |
| Critical | `Critico` | immediate and total compromise of the system or infrastructure. example: successful zone transfer, unauthenticated rce, plaintext admin credentials. |
| High | `Alto` | unauthorized access to sensitive data or probable privilege escalation with low effort. example: smb signing not mandatory (smb relay vector), credentials in active breaches. |
| Medium | `Medio` | exploitable vulnerability with moderate effort or specific conditions. example: hidden virtual host accessible, self-signed certificates, information facilitating subsequent attacks. |
| Low | `Basso` | information useful for further attacks but not directly exploitable. example: netbios name disclosure, username on social networks. |
| Informational | `Informativo` | data relevant for attack surface mapping, no direct risk. example: active hosts identified, waf/cdn detected, technology stack confirmed. |

### Variable severity

If severity depends on found content (e.g., Google Dorks that may find nothing or find
credentials), use the format:

```markdown
**Severity:** `Variable (Medium / High)`
```

Explain in the body text what determines the effective severity.

---

## 6. MITRE ATT&CK format

### Standard table

The MITRE ATT&CK table is **mandatory** in every technical README. It is always positioned
**at the end of the document**, before the final disclaimer note, separated by `---`.

```markdown
---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| [Tactic] | [Extended Technique Name] | `T1234.001` | [What was concretely done, with reference to finding ID if applicable.] |
```

### Compilation rules

- **Tactic:** use the official MITRE tactic name in English
  (e.g., `Reconnaissance`, `Discovery`, `Credential Access`, `Privilege Escalation`).
- **Technique:** use the official extended English name, including the sub-name after the colon
  if applicable (e.g., `Gather Victim Identity Info: Credentials`).
- **MITRE ID:** always in backtick, format uppercase `T` + number + optional sub-technique
  (e.g., `T1589.001`). Always verify the ID on the official platform attack.mitre.org.
- **Action Description:** in the document language, describe what was concretely done in the lab,
  not what MITRE theory says. Include the correlated Finding ID in parentheses if it exists.

### Aggregated table in parent README

Each module's parent README must contain an aggregated MITRE table with an additional
"Correlated Finding" column:

```markdown
| Tactic | Technique | MITRE ID | Correlated Finding |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Identity Info: Credentials | `T1589.001` | OSINT-001 |
```

### Where to find correct MITRE IDs

- Official site: `https://attack.mitre.org/techniques/`
- Search by technique: `https://attack.mitre.org/techniques/T1589/`
- Do not invent IDs. If the exact technique is not found, use the parent technique without sub-technique.

---

## 7. Tool documentation

### Reference tool table

Every README must close (before the MITRE section) with a tool table that includes
**also modern equivalent or alternative tools**, not just those used in the documented exercise:

```markdown
| Tool | Type | Technique/Access | Main Use Case |
| :--- | :--- | :--- | :--- |
| `tool-name` | [category] | [passive/active/CLI/Web] | [when and why to use it] |
```

### Accepted tool categories

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

### Note on modern tools

When a more modern and maintained tool exists compared to the one used in the exercise, add it
to the table and add a blockquote with explanation:

```markdown
> **Recommended modern tool:** `name` - explanation of advantage over previous tool
> and example command.
```

Modern tools to prefer (updated to 2025-2026):

| classic tool | modern alternative | reason |
| :--- | :--- | :--- |
| `Sublist3r` | `amass` (owasp) | more powerful, actively maintained, more sources |
| `httprobe` | `httpx` (projectdiscovery) | faster, provides status code + title + tech |
| `Masscan` (on vm) | `RustScan` | compatible with virtualized nat, more stable |
| `theHarvester` base | `theHarvester` + hunter.io api | without api key results are very limited |
| manual scanner | `nuclei` (projectdiscovery) | template-based, thousands of pre-written cves |
| `enum4linux` | `enum4linux-ng` | modern rewrite, more stable on recent environments |
| `CrackMapExec` | `NetExec` (nxc) | active fork after original repo was abandoned |

---

## 8. Text outputs and code blocks

### When to include text outputs

Include a structured output block (even synthetic/example) whenever:
- The command is shown for the first time in that context
- The output contains relevant findings to highlight
- The output demonstrates a misconfiguration or critical data

Full and lengthy outputs are not necessary: use **synthetic but realistic** outputs
that show the relevant lines. Annotate the most important lines with `<--`.

### Code block format

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

### Code block rules

- Commands are **always** in ` ```Bash ` blocks with language specification.
- Outputs are in ` ``` ` blocks without language specification.
- Configuration files are in ` ```plaintext ` blocks or with the specific language
  (` ```xml `, ` ```json `, etc.).
- Inline output annotations use `<--` with a space before and brief description.
- Do not paste huge outputs: trim with `[... truncated output ...]` if necessary.
- Commands with placeholders use `<PLACEHOLDER>` in uppercase with angle brackets.

### Screenshot vs text output

- **Always prefer text output** when available: it is verifiable, copyable, searchable.
- Screenshots are accepted only when the output is graphical (GUI, browser, dashboard).
- If only a screenshot is available but not the text, indicate:
  `[Output available in ./img/Screenshot_YYYY-MM-DD.jpg]`
- **Never replace a text output with a screenshot** of a terminal.

---

## 9. Diagrams and operational flows

### When to include an operational flow

Mandatory in parent READMEs for each module. Optional (but recommended) in complex
technical READMEs with multiple sequential steps or conditional decisions.

### Mandatory ASCII format

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

## 10. Remediation section (blue team)

### Requirement

The Remediation section is **mandatory for every finding with Critical, High or Medium severity**.
For Low and Informational findings it is optional but recommended.

### Positioning

Immediately after the finding description and its analysis, before the next section.

### Minimum structure

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

## 11. Cross-referencing between sections

### How to reference other modules

When a technique or finding in one section directly connects to another section
in the repository, indicate it explicitly:

```markdown
The subdomain list produced becomes direct input for
`03-web-attacks/02-web-recon/`.

The SMB Signing misconfiguration (SCAN-003) is exploited in phase
`07-post-exploitation/04-pivoting-tunneling/`.
```

### How to reference findings

In current text, reference previous or correlated findings with their ID in backticks:

```markdown
This finding confirms what was already detected in `DNS-001`: the target's
DNS attack surface is completely exposed.
```

### How to reference tools in other modules

```markdown
For vulnerability scanning on found subdomains, see
`02-vulnerability-assessment/01-general-scanners/nmap-nse-vuln/`.
```

---

## 12. Forbidden characters and formatting

### Em dash character (FORBIDDEN)

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

### Unicode arrows in text (FORBIDDEN outside code blocks)

- FORBIDDEN in narrative text: `->`, `=>`, `-->`, and any unicode arrow
- ALLOWED only inside code blocks ` ``` ` for ASCII diagrams

### Headings with blockquote in metadata

The header metadata uses **simple hyphen + space** as separator, not arrows or em dashes:

```markdown
# Correct:
> - **Phase:** Reconnaissance - Passive Information Gathering
> - **Visibility:** Zero - no packets sent

# WRONG:
> **Phase:** Reconnaissance -> Passive Information Gathering
> **Visibility:** Zero — no packets sent
```

### Accents and special characters in text

Accented vowels are allowed in Italian narrative text.
In code blocks and commands, use exclusively pure ASCII (no accents).

---

## 13. Anti-patterns to avoid

### Content anti-patterns

| anti-pattern | problem | correction |
| :--- | :--- | :--- |
| "just run `nmap`" | informal tone, doesn't explain why | always explain context and motivation before the command |
| list of commands without explanation | doesn't demonstrate understanding | every command must have a line of operational context |
| "as seen in the screenshot" | not verifiable, not searchable | always accompany with text output when possible |
| severity not assigned | unclassified finding | every finding must have id and severity |
| finding without remediation | incomplete document | always add at least one line of remediation |
| tool without version | not reproducible | specify version when critical for reproducibility (e.g., "nmap 7.94") |
| unauthorized target used without note | legal/reputational risk | always declare the authorization perimeter |
| missing mitre section | not professional | mandatory in every technical readme |
| em dash in text | inconsistency, standard violation | replace with simple hyphen `-` |
| english text where not necessary | linguistic inconsistency | use italian for all narrative (in italian version) |

### Structural anti-patterns

- **Do not create a README that is just a list of commands:** every document must have
  introduction, operational context, analysis and conclusions.
- **Do not duplicate content between parent and child README:** the parent provides summary and navigation,
  the child provides technical detail.
- **Do not omit the operational flow:** the reader must understand the order in which to execute activities.
- **Do not use generic titles:** instead of `## Analysis`, use `## Critical Analysis: false negatives
  in virtualized environment`.

---

## 14. Pre-publication checklist

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

### Technical content

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

### Three dimensions of the report (section 15)

- [ ] TECHNICAL dimension: real outputs, CVSS score, finding ID, verified MITRE IDs
- [ ] DESCRIPTIVE dimension: first person (plural) narration of steps performed, problems
  encountered, decisions made during the exercise
- [ ] THEORETICAL dimension: explanation of the principle behind the technique, methodology choice
  motivation, result interpretation in the kill chain context
- [ ] "Real-World Scenario" section present for findings with High or Critical severity (Section 16)

---

## 15. The three dimensions of the report

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

### How to balance the three dimensions

The three dimensions do not always carry the same weight. Adapt based on document type:

| readme type | technical | descriptive | theoretical |
| :--- | :---: | :---: | :---: |
| specific technique (e.g., nmap, enum4linux) | High | High | Medium |
| exploitation (e.g., sqli, ssti, drupalgeddon2) | High | High | High |
| introductory module (e.g., parent readme) | Low | Low | High |
| secure coding / remediation | Medium | Low | High |
| automated scanner (e.g., nessus, nikto) | Medium | High | Low |

---

## 16. Projection towards Real-World scenarios

Every README related to findings with `High` or `Critical` severity must include a section
that projects the lab towards a real-world scenario. This section answers the question:
"If this weren't a lab, what would happen next?"

The section must be presented from two parallel perspectives: **attacker** and **defender**.

---

### Positioning in the document

The "Real-World Scenario" section is inserted **after Conclusions and before the MITRE table**,
separated by `---`. It is a standalone block, not a subsection of the remediation.

---

### Mandatory template

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

### Compiled example (from SMB/VULN-004)

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
