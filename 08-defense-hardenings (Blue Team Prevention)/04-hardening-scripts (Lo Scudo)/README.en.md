> **English** | [Italiano](README.md)

# 04 - Hardening scripts (the shield)

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

## Folder structure

```
04-hardening-scripts (Lo Scudo)/
+-- README.md              # this file: DEF-007..008 registry, hardening philosophy
|
+-- linux-hardening/       # DEF-007: Lynis audit + Linux CIS baseline
+-- windows-hardening/     # DEF-008: GPO, Credential Guard, LAPS, CIS baseline
```

---

## Recommended operational flow

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

## Reference tools

| tool | platform | role | main use case |
| :--- | :--- | :--- | :--- |
| `Lynis` | linux | auditor | hardening audit with index and recommendations |
| `CIS Benchmarks` | multi | baseline | recognized security configurations |
| `Microsoft Security Baseline` | windows | baseline | pre-configured hardening gpos |
| `Credential Guard` / `LAPS` | windows | countermeasure | credential protection (anti mimikatz/pth) |
| `OpenSCAP` / `CIS-CAT` | multi | compliance | verification of conformity to security profiles |
| `Ansible` (hardening role) | multi | automation | idempotent hardening on machine fleets |

> **Recommended modern tool:** `Lynis` (Linux) and `CIS-CAT` (Windows) for audit and measurement; the `CIS`/`Microsoft` baselines as reference; `Ansible` (DevSec Hardening Framework) for idempotent application at scale. On Windows, `Credential Guard` and `LAPS` are the highest-impact countermeasures.

---

## Finding registry - hardening scripts section

| id | description | severity | subfolder |
| :--- | :--- | :---: | :--- |
| `DEF-007` | linux hardening: lynis audit + cis baseline, surface reduction (anti privesc) | `High` | `linux-hardening/` |
| `DEF-008` | windows hardening: gpo, credential guard, laps (anti credential dumping / pth) | `High` | `windows-hardening/` |

---

## MITRE ATT&CK mapping - aggregated

> Attack techniques **prevented** by the hardening of the section.

| tactic (prevented) | technique | mitre id | related finding |
| :--- | :--- | :--- | :--- |
| privilege escalation | abuse elevation control: sudo | `T1548.003` | DEF-007 |
| privilege escalation | setuid and setgid | `T1548.001` | DEF-007 |
| credential access | os credential dumping: lsass memory | `T1003.001` | DEF-008 |
| lateral movement | use alternate authentication material: pass the hash | `T1550.002` | DEF-008 |
| persistence | boot or logon autostart: registry run keys | `T1547.001` | DEF-008 |
| credential access | unsecured credentials: credentials in files | `T1552.001` | DEF-007 |

---

> **Note:** All activities documented in this section were conducted on lab systems owned by the author. Hardening must be applied with attention to the system's role (snapshots and tests mandatory): an erroneous policy can interrupt legitimate services or, in Active Directory, impact the entire domain. Techniques are documented for educational and defensive purposes in an authorized context.
