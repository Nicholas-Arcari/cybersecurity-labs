> **English** | [Italiano](README.md)

# 04 - Hardening Scripts (The Shield)

> - **Phase:** Defense & Hardening - System Hardening (Prevention)
> - **Category:** Prevention - attack surface reduction
> - **Prerequisites:** Privileged access to the systems; audit tools (Lynis, CIS-CAT); reference baseline (CIS Benchmarks); test environment
> - **Output:** Findings DEF-007..008; hardened Linux and Windows systems; reduced and measurable attack surface

---

## Introduction

Hardening is "the shield": the preventive defense that acts before the attack, reducing what the attacker can exploit. While SIEM (`../01-siem-log-analysis/`) and XDR (`../02-endpoint-security-xdr/`) detect ongoing attacks and deception (`../03-deception/`) betrays them, hardening prevents them at the root - it closes the doors before the attacker knocks.

It is the most efficient layer of the defense because it acts on the cause, not the symptom: a prevented attack does not have to be detected or contained. Every unnecessary service disabled, every permission restricted, every insecure default corrected eliminates a vector at zero functional cost. The guiding principle is the minimization of the attack surface: everything that is not needed is a risk without benefit.

The approach is not improvised but guided by recognized baselines (CIS Benchmarks, Microsoft Security Baseline) and measured by audit tools (Lynis, CIS-CAT) that make hardening objective and repeatable - a cycle audit, hardening, re-audit with a measurable score, not a collection of commands applied at random.

The section is the mirror countermeasure to the offensive path:

1. **Linux Hardening (DEF-007):** audit with Lynis and CIS baseline. Closes the privilege escalation classes of module 04 (abusable SUID, misconfigured sudo, writable cron, cleartext credentials).

2. **Windows Hardening (DEF-008):** GPO, Credential Guard, LAPS and CIS baseline. Neutralizes the credential dumping (Mimikatz/LSASS) and lateral movement (pass-the-hash) techniques of module 07.

Every offensive finding of the path has here its preventive countermeasure: hardening is the module where the studied attack becomes applied defense.

---

## Folder Structure

```
04-hardening-scripts (Lo Scudo)/
+-- README.md              # this file: DEF-007..008 registry, hardening philosophy
|
+-- linux-hardening/       # DEF-007: Lynis audit + Linux CIS baseline
+-- windows-hardening/     # DEF-008: GPO, Credential Guard, LAPS, CIS baseline
```

---

## Recommended Operational Flow

```
[INPUT] System to harden (Linux/Windows)
         |
         v
[1] Initial audit (baseline)
     +-- Lynis (Linux) / CIS-CAT (Windows) -> hardening index + warnings
              |
              v
[2] Applying the hardening
     +-- Linux: SSH, SUID, sudo, sysctl (DEF-007)
     +-- Windows: GPO, Credential Guard, LAPS, SMBv1 (DEF-008)
     +-- ALWAYS: snapshot before, test after (do not break the services)
              |
              v
[3] Re-audit (measure of the improvement)
     +-- the hardening index confirms the objective reduction of the surface
              |
              v
[4] Hardening + detection
     +-- FIM (Wazuh DEF-003) on the hardened files -> detects attempts to undo the hardening
              |
              v
[OUTPUT] Reduced attack surface -> entire attack classes prevented
```

---

## Reference Tools

| Tool | Platform | Role | Main use case |
| :--- | :--- | :--- | :--- |
| `Lynis` | Linux | Auditor | Hardening audit with index and recommendations |
| `CIS Benchmarks` | Multi | Baseline | Recognized security configurations |
| `Microsoft Security Baseline` | Windows | Baseline | Pre-configured hardening GPOs |
| `Credential Guard` / `LAPS` | Windows | Countermeasure | Credential protection (anti Mimikatz/PtH) |
| `OpenSCAP` / `CIS-CAT` | Multi | Compliance | Verification of conformity to security profiles |
| `Ansible` (hardening role) | Multi | Automation | Idempotent hardening on machine fleets |

> **Recommended modern tool:** `Lynis` (Linux) and `CIS-CAT` (Windows) for audit and measurement; the `CIS`/`Microsoft` baselines as reference; `Ansible` (DevSec Hardening Framework) for idempotent application at scale. On Windows, `Credential Guard` and `LAPS` are the highest-impact countermeasures.

---

## Finding Registry - Hardening Scripts Section

| ID | Description | Severity | Subfolder |
| :--- | :--- | :---: | :--- |
| `DEF-007` | Linux hardening: Lynis audit + CIS baseline, surface reduction (anti privesc) | `High` | `linux-hardening/` |
| `DEF-008` | Windows hardening: GPO, Credential Guard, LAPS (anti credential dumping / PtH) | `High` | `windows-hardening/` |

---

## MITRE ATT&CK Mapping - Aggregated

> Attack techniques **prevented** by the hardening of the section.

| Tactic (prevented) | Technique | MITRE ID | Related Finding |
| :--- | :--- | :--- | :--- |
| Privilege Escalation | Abuse Elevation Control: Sudo | `T1548.003` | DEF-007 |
| Privilege Escalation | Setuid and Setgid | `T1548.001` | DEF-007 |
| Credential Access | OS Credential Dumping: LSASS Memory | `T1003.001` | DEF-008 |
| Lateral Movement | Use Alternate Authentication Material: Pass the Hash | `T1550.002` | DEF-008 |
| Persistence | Boot or Logon Autostart: Registry Run Keys | `T1547.001` | DEF-008 |
| Credential Access | Unsecured Credentials: Credentials In Files | `T1552.001` | DEF-007 |

---

> **Note:** All activities documented in this section were conducted on lab systems owned by the author. Hardening must be applied with attention to the system's role (snapshots and tests mandatory): an erroneous policy can interrupt legitimate services or, in Active Directory, impact the entire domain. Techniques are documented for educational and defensive purposes in an authorized context.
