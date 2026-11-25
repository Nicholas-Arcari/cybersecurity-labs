> **English** | [Italiano](README.md)

# Linux hardening - attack surface reduction

> - **Phase:** Defense & Hardening - System Hardening (Prevention)
> - **Category:** Prevention - attack surface reduction and security baseline
> - **Prerequisites:** Root access to the system to harden; Lynis for the audit; snapshot/backup before the changes; knowledge of the system's role (to avoid breaking legitimate services)
> - **Output:** Finding DEF-007; system hardened according to CIS baseline; reduced attack surface; measurable and repeatable audit score

- **Operating Environment:** Linux server/workstation (Debian/Ubuntu), Lynis as auditor
- **Role:** "The Shield" - it prevents, it does not detect: it closes the doors before the attacker knocks
- **Main tools:** Lynis, Bastille, CIS Benchmarks, auditd

---

## Executive summary

Hardening is preventive defense: while SIEM (`../../01-siem-log-analysis/`) and Wazuh detect ongoing attacks, hardening prevents them by reducing what the attacker can exploit. Every unnecessary service disabled, every permission restricted, every insecure default corrected is a door closed before the attacker even finds it. It is the most economical and effective layer of defense, because it acts on the cause (attack surface) instead of the symptom (ongoing attack).

The approach is not improvised but guided by standard baselines. The **CIS Benchmarks** define recognized security configurations for each operating system; **Lynis** is the audit tool that measures how much a system conforms to them, producing a numerical "hardening index" and a prioritized list of recommendations. Finding DEF-007 documents the cycle audit, hardening, re-audit, with Lynis as an objective measure of the improvement.

The value for this path is the mirror image of the offensive: the Linux privilege escalation techniques of `04-system-exploitation` (abusable SUID, misconfigured sudo, writable cron, cleartext credentials) are exactly what hardening closes. Every EXPLOIT finding of the offensive module has here its preventive countermeasure.

---

## Folder structure

```
linux-hardening/
+-- README.md      # this file: Lynis audit + CIS baseline (DEF-007)
+-- img/           # Lynis report and hardening index
```

---

## Audit and hardening with lynis

**Finding ID:** `DEF-007` | **Severity:** `High` (structural reduction of the attack surface; prevents entire classes of privilege escalation and lateral movement)

### Operational context

The correct hardening cycle starts from measurement, not from action: first the system is audited to know where it stands (Lynis produces a hardening index and a list of warnings), then the priority recommendations are addressed, finally it is re-audited to verify the improvement. This makes hardening objective and repeatable, not a collection of commands applied at random.

### PoC - phase 1: initial audit (baseline)

```Bash
# Installation and complete audit of the system
sudo apt install lynis
sudo lynis audit system
```

```
[+] Hardening
    Hardening index : 58 [########------------]        <-- pre-hardening baseline (DEF-007)

  Warnings:
  - [SSH-7408] SSH PermitRootLogin is enabled          <-- root SSH active
  - [AUTH-9282] Password aging limits not configured
  - [KRNL-5820] core dumps not disabled
  Suggestions: 47 hardening opportunities
```

### PoC - phase 2: applying the hardening (targeted examples)

```Bash
# SSH hardening: deny root login, force keys
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# Removal of unnecessary SUID bits (countermeasure to GTFOBins privesc)
sudo chmod u-s /usr/bin/<unnecessary_binary>

# Kernel hardening (sysctl): disable core dumps, protect the network
echo "kernel.core_pattern=|/bin/false" | sudo tee -a /etc/sysctl.d/99-hardening.conf
sudo sysctl --system
```

### PoC - phase 3: re-audit (measure of the improvement)

```Bash
sudo lynis audit system
```

```
[+] Hardening
    Hardening index : 84 [################----]        <-- post-hardening (DEF-007)
    # from 58 to 84: attack surface reduced measurably
```

### Defensive operations and cautions

- **Always measure before and after:** the hardening index makes the progress objective; without a baseline one does not know if it has improved
- **Do not break the services:** every change must be evaluated against the system's role (disabling a "useless" service that is actually needed causes an outage); snapshot before, test after
- **Idempotent automation:** for machine fleets, hardenings must be applied via idempotent Ansible/scripts aligned to a CIS Benchmark, not by hand host by host
- **Hardening + detection:** hardening reduces the surface but does not eliminate the risk; it must be paired with monitoring (Wazuh FIM on the hardened config files, to detect attempts to undo the hardening)

---

## Lab experience

The value of Lynis was making hardening measurable instead of anecdotal. Before, I knew the individual countermeasures (disable root SSH, remove useless SUID) but I had no way to know "how" secure a system was. The hardening index - from 58 to 84 in my test cycle - turned a feeling ("now it's more secure") into a datum. This changes hardening from a subjective activity to a verifiable process, and it is exactly what a professional report requires.

The defensive satisfaction was closing, one by one, the doors I had opened in the offensive module. In module 04 I had exploited abusable SUID and misconfigured sudo for escalation; here I was removing and restricting them, seeing Lynis confirm the closing of those specific paths. The direct link between an offensive finding (EXPLOIT-008, GTFOBins) and its preventive countermeasure made the attack/defense symmetry tangible.

The caution learned was the flip side of the enthusiasm. In the attempt to maximize the hardening index, I disabled a service I thought was useless and broke a test functionality. The lesson: maximum hardening is not the goal, hardening appropriate to the system's role is. A server has different needs from a workstation; applying a baseline blindly without understanding the operational context causes more harm than good. Snapshot before, test after, always.

---

## Theoretical analysis: hardening as attack surface reduction

The attack surface of a system is the set of all the points through which an attacker can attempt to interact with it: listening services, accounts, privileged binaries, file permissions, exposed configurations. Hardening is the systematic application of a principle: minimize this surface. Every unnecessary element is a risk without benefit; removing it eliminates a potential vector at zero functional cost.

This is founded on the principle of least privilege and of "secure by default" inverted. Systems arrive configured for maximum compatibility and ease of use, not for security: services active "just in case", broad permissions, permissive defaults. Hardening inverts this setup, starting from the opposite assumption - everything disabled until there is an explicit reason to enable it. It is the shift from "open unless forbidden" to "closed unless necessary".

The link with the rest of the defense is hierarchical. Hardening is the first layer (prevention): it reduces what can be attacked. Monitoring is the second (detection): it detects what gets past the prevention. Response is the third (reaction): it contains what is detected. Hardening is the most efficient because it acts upstream: a prevented attack does not have to be detected or contained. But it is not sufficient alone - no surface is ever zero - which is why it integrates with the detection and response of the other layers. Defense in depth is the sum of these layers, and hardening is its foundation.

---

## Real-World scenario: prevention in action

> This section describes how this defensive control would operate in a real incident.

### Attacker perspective (what they attempt)

The attacker, having gained initial access as an unprivileged user, looks for a privilege escalation path: enumerates the SUID binaries, checks the sudo rules, looks for writable cron jobs and cleartext credentials - exactly the playbook of `04-system-exploitation`.

### Defender perspective (how the control responds)

```
[DEF-007] System hardened according to CIS baseline (Lynis index 84)
        |
        v
Attacker enumerates SUID -> the abusable binaries have been removed (chmod u-s)
        |
        v
Attacker checks sudo -> minimal configuration, no abusable NOPASSWD
        |
        v
Attacker looks for writable cron -> restricted permissions, no path
        |
        v
Escalation failed: the surface the attack requires no longer exists
```

**Defensive value:** hardening does not generate an alert, it generates a non-event: the escalation simply finds no footholds. The most common privilege escalation classes (SUID, sudo, cron, permissions) are closed upstream, before the attacker can try them. This is the silent value of prevention: the best attack is the one that never had a surface to grab onto.

**Synergy with detection:** pairing FIM (Wazuh, DEF-003) with the hardened configuration files means also detecting attempts to undo the hardening (an attacker trying to re-add the SUID or re-enable root SSH generates a FIM alert). Prevention and detection reinforce each other.

**Defensive lesson:** prevention is invisible when it works - there are no alerts, only attacks that fail in silence. This makes it underestimated but it is the most efficient layer: every vector closed by hardening is an incident that will never happen.

---

## Reference tools

| tool | type | role | main use case |
| :--- | :--- | :--- | :--- |
| `Lynis` | security auditor | cli | hardening audit with numerical index and recommendations |
| `CIS Benchmarks` | baseline standard | document | recognized security configurations for os/services |
| `Bastille` | hardening script | cli | interactive guided hardening (legacy but didactic) |
| `auditd` | audit framework | daemon | logging of system events for detection and compliance |
| `OpenSCAP` | compliance scanner | cli | verification of conformity to security profiles (scap) |
| `Ansible` (hardening role) | automation | iac | idempotent application of hardening on machine fleets |

> **Recommended modern tool:** `Lynis` for the audit and the measurement (the hardening index makes the progress objective). For application at scale, the Ansible roles aligned to the `CIS Benchmarks` (e.g. the DevSec Hardening Framework collections) make hardening idempotent and repeatable. `OpenSCAP` for formal compliance verification. Bastille remains didactically useful but is dated.

---

## MITRE ATT&CK mapping

> The table maps the attack techniques that hardening **prevents** by reducing the surface.

| tactic (prevented) | technique | mitre id | role of the control |
| :--- | :--- | :--- | :--- |
| privilege escalation | abuse elevation control: sudo and sudo caching | `T1548.003` | minimal sudo configuration, no abusable nopasswd (DEF-007) |
| privilege escalation | setuid and setgid | `T1548.001` | removal of the unnecessary suid bits (DEF-007) |
| privilege escalation | scheduled task/job: cron | `T1053.003` | restricted permissions on cron and directories (DEF-007) |
| persistence | account manipulation: ssh authorized keys | `T1098.004` | disabling root login, forcing keys, restricted permissions |
| credential access | unsecured credentials: credentials in files | `T1552.001` | remediation of cleartext credentials in config files |

| defensive countermeasure (d3fend) | d3fend id | application |
| :--- | :--- | :--- |
| platform hardening | `D3-PH` | attack surface reduction via cis baseline |
| local account monitoring | `D3-LAM` | audit and restriction of accounts and privileges |
| executable denylisting | `D3-EDL` | removal/restriction of abusable privileged binaries |

---

> **Note:** All documented activities were conducted on lab systems owned by the author. Hardening must be applied with attention to the system's role to avoid interrupting legitimate services (snapshots and tests mandatory). Techniques are documented for educational and defensive purposes in an authorized context.
