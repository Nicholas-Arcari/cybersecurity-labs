> **English** | [Italiano](README.md)

# 08 - Defense & Hardening (Blue Team Prevention)

> - **Phase:** Defense - Prevention, Detection & Response (Blue Team)
> - **Category:** The perspective shift: from attack to defense
> - **Prerequisites:** Understanding of the offensive techniques of modules 01-07 (one defends what one knows how to attack); host for SIEM/XDR with adequate resources; test environment
> - **Output:** Findings DEF-001..008; multi-layer defensive architecture; detection, deception and hardening validated against the attacks of the previous modules

---

## Introduction

The `08-defense-hardenings` module is the perspective shift of the path: after seven modules dedicated to attack (Red Team), here one moves to defense (Blue Team). It is the module in which every offensive technique studied finds its countermeasure, and in which the guiding principle becomes explicit: one defends well only what one knows how to attack. The offensive knowledge of the previous modules is not an end but the tool to build defenses that hold against real adversaries.

The defensive philosophy of the module is **defense in depth**: no single control is sufficient, but their layering makes the attack progressively more costly, noisier and less probable. The module is organized according to an anatomical metaphor that clarifies its complementary roles:

1. **The Brain - SIEM & Log Analysis (`01-siem-log-analysis/`, DEF-001..002):** the nerve center that sees everything and correlates. ELK Stack and Splunk aggregate the environment's logs and turn isolated events into detection. Without visibility there is no defense.

2. **The Muscles - Endpoint Security & XDR (`02-endpoint-security-xdr/`, DEF-003..004):** the sensors that act on the endpoint. Wazuh not only detects (File Integrity Monitoring) but reacts (active response), containing the attacker in seconds.

3. **The Traps - Deception (`03-deception/`, DEF-005..006):** the high-confidence decoys. Canary tokens and honeypots warn when the attacker is already inside and study their techniques, with structurally null false positives.

4. **The Shield - Hardening Scripts (`04-hardening-scripts/`, DEF-007..008):** prevention at the root. The hardening of Linux and Windows reduces the attack surface, closing entire classes of privilege escalation and lateral movement before the attacker tries them.

These four layers cover the complete defensive cycle: **prevent** (hardening), **detect** (SIEM + XDR + deception), **respond** (active response). An attack that gets past the prevention is detected; one that evades a sensor meets another; one that touches a decoy betrays itself. The strength is not in the single layer but in their sum.

### Note on the framing of the defensive Findings

In a defensive module, the **Finding** (`DEF-NNN`) does not represent a vulnerability of the environment but a **validated detection/prevention/deception control**. The **Severity** indicates the criticality of the threat the control addresses (a `High` control counters high-impact attack techniques). The **MITRE ATT&CK** tables map the techniques that each control detects, prevents or observes; where useful, the **MITRE D3FEND** framework (defensive countermeasures) is added alongside. This keeps the structure uniform with the rest of the repository, inverting its perspective.

---

## Folder Structure

```
08-defense-hardenings (Blue Team Prevention)/
+-- README.md                              <- this file: DEF-001..008 registry + aggregated MITRE
|
+-- 01-siem-log-analysis (Il Cervello)/
|   +-- README.md                          <- DEF-001..002 registry, SIEM concept
|   +-- elk-stack/                         <- DEF-001 (ELK: centralization + detection)
|   +-- splunk/                            <- DEF-002 (Splunk: SPL correlation)
|
+-- 02-endpoint-security-xdr (I Muscoli)/
|   +-- README.md                          <- DEF-003..004 registry, EDR/XDR concept
|   +-- wazuh/                             <- open source XDR platform
|       +-- installing&configuring/        <- Manager + agents deployment (setup)
|       +-- suricata-integration/          <- Wazuh + Suricata = SIEM + IDS (setup)
|       +-- threat-detection&active-response/  <- DEF-003 (FIM), DEF-004 (active response)
|
+-- 03-deception (Le Trappole)/
|   +-- README.md                          <- DEF-005..006 registry, deception philosophy
|   +-- honeypots/
|       +-- canary-tokens/                 <- DEF-005 (digital tripwires)
|       +-- t-pot/                         <- DEF-006 (honeypot + threat intel)
|
+-- 04-hardening-scripts (Lo Scudo)/
    +-- README.md                          <- DEF-007..008 registry, hardening philosophy
    +-- linux-hardening/                   <- DEF-007 (Lynis + CIS)
    +-- windows-hardening/                 <- DEF-008 (GPO, Credential Guard, LAPS)
```

---

## Recommended Operational Flow

```
[INPUT] Environment to defend + offensive knowledge (modules 01-07)
         |
         v
[1] Prevent - The Shield (04-hardening)
     +-- reduce the surface: Linux/Windows hardening (DEF-007..008)
              |
              v
[2] See - The Brain (01-siem)
     +-- centralize the logs, correlate: ELK/Splunk (DEF-001..002)
              |
              v
[3] Detect and React - The Muscles (02-xdr)
     +-- endpoint sensors + active response: Wazuh (DEF-003..004)
              |
              v
[4] Deceive - The Traps (03-deception)
     +-- high-confidence decoys: canary tokens, honeypots (DEF-005..006)
              |
              v
[CYCLE] The alerts (02, 03) flow into the SIEM (01) for correlation;
        the hardening (04) reduces what must be detected
              |
              v
[OUTPUT] Defense in depth: attack prevented, or detected, or betrayed by a decoy
```

---

## Reference Tools

| Tool | Layer | Role | Main use case |
| :--- | :--- | :--- | :--- |
| `ELK Stack` / `Splunk` | The Brain | SIEM | Centralization, correlation, detection |
| `Wazuh` | The Muscles | XDR | Endpoint detection, FIM, active response |
| `Suricata` | The Muscles | IDS | Integrated network detection in Wazuh |
| `Canarytokens` / `T-Pot` | The Traps | Deception | Early warning and threat intelligence |
| `Lynis` / `CIS-CAT` | The Shield | Auditor | Measurement and application of hardening |
| `Credential Guard` / `LAPS` | The Shield | Countermeasure | Windows credential protection |

> **Recommended modern tool:** a complete open source defensive architecture is built with `Wazuh` (XDR + lightweight SIEM) or `ELK/Elastic Security` as the brain, `Suricata` for the network, `canarytokens`/`OpenCanary` for deception, and `Lynis`/`CIS Benchmarks` with `Ansible` for idempotent hardening. This stack covers the entire prevent-detect-respond cycle without license costs.

---

## Finding Registry - Module 08

| ID | Description | Severity | Subfolder |
| :--- | :--- | :---: | :--- |
| `DEF-001` | ELK Stack: log centralization and detection (SSH brute force) | `High` | `01-siem/elk-stack/` |
| `DEF-002` | Splunk: multi-source correlation via SPL (scan -> access kill chain) | `High` | `01-siem/splunk/` |
| `DEF-003` | Wazuh FIM: detection of persistence, tampering and rootkits | `High` | `02-xdr/wazuh/threat-detection.../` |
| `DEF-004` | Wazuh Active Response: automatic containment (IP block) on alert | `High` | `02-xdr/wazuh/threat-detection.../` |
| `DEF-005` | Canary Tokens: digital tripwires for early breach detection | `Medium` | `03-deception/honeypots/canary-tokens/` |
| `DEF-006` | T-Pot: multi-service honeypot platform, collection of TTPs/IOCs | `Medium` | `03-deception/honeypots/t-pot/` |
| `DEF-007` | Linux hardening: Lynis audit + CIS baseline (anti privilege escalation) | `High` | `04-hardening/linux-hardening/` |
| `DEF-008` | Windows hardening: GPO, Credential Guard, LAPS (anti credential dumping / PtH) | `High` | `04-hardening/windows-hardening/` |

---

## MITRE ATT&CK Mapping - Aggregated

> The defensive module maps the attack techniques that its controls **detect, prevent or observe**. Complementary framework: MITRE D3FEND (defensive countermeasures).

| Tactic (countered) | Technique | MITRE ID | Related Finding |
| :--- | :--- | :--- | :--- |
| Credential Access | Brute Force | `T1110` | DEF-001, DEF-002, DEF-004, DEF-006 |
| Reconnaissance | Active Scanning | `T1595` | DEF-002 |
| Initial Access | Valid Accounts | `T1078` | DEF-001, DEF-002, DEF-006 |
| Lateral Movement | Remote Services | `T1021` | DEF-002 |
| Lateral Movement | Use Alternate Authentication Material: Pass the Hash | `T1550.002` | DEF-008 |
| Persistence | Account Manipulation: SSH Authorized Keys | `T1098.004` | DEF-003, DEF-007 |
| Persistence | Boot or Logon Autostart: Registry Run Keys | `T1547.001` | DEF-003, DEF-008 |
| Credential Access | OS Credential Dumping: LSASS Memory | `T1003.001` | DEF-008 |
| Privilege Escalation | Abuse Elevation Control: Sudo | `T1548.003` | DEF-007 |
| Privilege Escalation | Setuid and Setgid | `T1548.001` | DEF-007 |
| Defense Evasion | Rootkit | `T1014` | DEF-003 |
| Defense Evasion | Indicator Removal: Clear Logs | `T1070` | DEF-001 |
| Collection | Data from Network Shared Drive | `T1039` | DEF-005 |
| Credential Access | Unsecured Credentials: Credentials In Files | `T1552.001` | DEF-005, DEF-007 |
| Command and Control | Ingress Tool Transfer | `T1105` | DEF-006 |

| Defensive countermeasure (D3FEND) | D3FEND ID | Layer |
| :--- | :--- | :--- |
| Platform Monitoring | `D3-PM` | The Brain (SIEM) |
| File Integrity Monitoring | `D3-FIM` | The Muscles (Wazuh) |
| Network Traffic Filtering | `D3-NTF` | The Muscles (active response) |
| Decoy File / Credential / Environment | `D3-DF`/`D3-DUC`/`D3-DE` | The Traps (deception) |
| Platform / Credential Hardening | `D3-PH`/`D3-CH` | The Shield (hardening) |

---

> **Note:** All activities documented in this module were conducted on a lab environment owned by the author, in a controlled context. The defensive tools (SIEM, XDR, honeypot, hardening) are by nature legitimate; the only cautions concern the isolation of the honeypots (which capture real malware), the tuning of the active response (to avoid self-blocks) and the testing of the hardening (to avoid interrupting legitimate services). Log monitoring in real contexts must comply with privacy and data-processing regulations. Techniques are documented for educational and defensive purposes in an authorized context.
