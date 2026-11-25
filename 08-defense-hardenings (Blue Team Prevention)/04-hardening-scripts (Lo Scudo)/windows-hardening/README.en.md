> **English** | [Italiano](README.md)

# Windows hardening - GPO, credential guard and CIS baseline

> - **Phase:** Defense & Hardening - System Hardening (Prevention)
> - **Category:** Prevention - Windows and Active Directory hardening
> - **Prerequisites:** Domain administrator (for GPOs) or local privileges; Microsoft Security Compliance Toolkit / CIS-CAT for the baselines; test environment before production
> - **Output:** Finding DEF-008; endpoints and domain hardened via GPO; countermeasures to credential dumping and lateral movement; CIS baseline applied

- **Operating Environment:** Windows (workstation/server), Active Directory, Group Policy
- **Role:** "The Shield" - it prevents the Windows offensive techniques at the policy level
- **Main tools:** Group Policy (GPO), Microsoft Security Baseline, LAPS, Credential Guard, CIS-CAT

---

## Executive summary

Windows hardening is the direct preventive countermeasure to the offensive techniques of modules 04 and 07: credential dumping (Mimikatz/LSASS), pass-the-hash, privilege escalation, persistence. Unlike Linux where one acts host by host, in a Windows environment the power of hardening lies in the **Group Policy (GPO)**: a centrally defined policy applies to thousands of endpoints simultaneously, making hardening scalable and consistent.

The approach is guided by baselines: the **Microsoft Security Baselines** (in the Security Compliance Toolkit) and the **CIS Benchmarks** provide sets of pre-configured and recognized GPOs, which close Windows' insecure defaults. Finding DEF-008 documents the application of these baselines and of the specific countermeasures to the techniques seen in the offensive path.

Three countermeasures deserve emphasis because they neutralize attacks documented in `07-post-exploitation`: **Credential Guard** isolates LSASS in a virtualized environment, making credential dumping with Mimikatz ineffective (POST-003); **LAPS** randomizes the local administrator password for each machine, breaking lateral pass-the-hash; disabling **SMBv1** and legacy protocols closes lateral movement vectors and NTLM relays.

---

## Folder structure

```
windows-hardening/
+-- README.md      # this file: GPO, Credential Guard, LAPS, CIS baseline (DEF-008)
+-- GPO-templates/ # export of the hardening GPOs (backup/import)
+-- img/           # baseline application and verification
```

---

## Windows hardening via GPO and baseline

**Finding ID:** `DEF-008` | **Severity:** `High` (preventive countermeasure to credential dumping, pass-the-hash and lateral movement in a Windows/AD environment)

### Operational context

The strength of Windows hardening is centralization via GPO: the policy is defined once and Active Directory propagates it to all the domain endpoints. The Microsoft Security Baselines provide these GPOs already configured; the defender's task is to import them, adapt them to the context and verify their application, not reinvent them.

### PoC - phase 1: import of the security baseline

```PowerShell
# Microsoft Security Compliance Toolkit: import of the baseline into GPO
# (the baselines are sets of GPO backups ready to import)
Import-GPO -BackupGpoName "MSFT Windows 11 - Computer" -TargetName "CIS-Baseline-Workstation" -Path C:\Baselines
```

### PoC - phase 2: credential guard (countermeasure to Mimikatz/LSASS - POST-003)

```PowerShell
# Enabling Credential Guard via GPO / registry
# Isolates LSASS in a virtualized container (VBS) -> Mimikatz cannot dump
reg add "HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard" /v EnableVirtualizationBasedSecurity /t REG_DWORD /d 1 /f
reg add "HKLM\SYSTEM\CurrentControlSet\Control\LSA" /v LsaCfgFlags /t REG_DWORD /d 1 /f
```

```PowerShell
# Verify that Credential Guard is active
(Get-CimInstance -ClassName Win32_DeviceGuard -Namespace root\Microsoft\Windows\DeviceGuard).SecurityServicesRunning
```

```
1                        <-- Credential Guard active: LSASS isolated (DEF-008)
                         # the dump with Mimikatz (POST-003) now returns encrypted/inaccessible hashes
```

### PoC - phase 3: lateral movement countermeasures

```PowerShell
# Disable SMBv1 (legacy vector, WannaCry/EternalBlue, relay)
Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart

# LAPS: local admin password randomized and unique per host (breaks lateral pass-the-hash)
# (deployment via GPO + extended AD schema)
Get-LapsADPassword -Identity "WIN-CLIENT-01"     # unique and rotated password per host

# Block execution from user paths (countermeasure to dropped payloads)
# via AppLocker / WDAC policy
```

### Defensive operations and cautions

- **Test before production:** a misapplied GPO can lock out access to thousands of machines; test in a pilot OU before the rollout
- **Priority order:** start from the high-impact countermeasures (Credential Guard, LAPS, disabling SMBv1, RDP NLA) before the detail rules
- **Compatibility:** Credential Guard requires hardware with virtualization (VBS) and can be incompatible with some legacy drivers; verify first
- **Hardening + detection:** pair the hardening with monitoring (Wazuh/Sysmon) to detect attempts to bypass or disable it

---

## Lab experience

The most powerful demonstration was Credential Guard against Mimikatz. In module 07 I had used Mimikatz to dump NTLM hashes and Kerberos tickets from LSASS (POST-003, Critical finding); here, with Credential Guard enabled, I re-executed the same attack and saw the dump return encrypted and unusable data. The same technique that as an attacker had given me the keys to the domain, as a defender I had neutralized it with a single policy. Seeing the attack fail where it previously succeeded made the value of hardening concrete better than any theory.

The lesson on scalability was understanding the power of GPOs. On Linux I had hardened host by host; on Windows, defining the policy once and seeing it propagate to all the endpoints of the test domain showed why Active Directory hardening is structurally different. Centralization is both the strength (one change, thousands of machines) and the risk (one mistake, thousands of machines): the same GPO that protects everything can break everything if wrong.

The caution learned was about the operational risk of aggressive policies. An attempt to apply a complete CIS baseline without testing it blocked legitimate functionality in a test VM. The lesson repeats the Linux one but amplified by scale: in AD, untested hardening does not damage a host but potentially the entire domain. The gradual rollout via a pilot OU is not bureaucracy, it is operational survival.

---

## Theoretical analysis: hardening as neutralization of the techniques, not of the individual attacks

Mature Windows hardening does not chase the individual exploits but neutralizes the techniques at the root. Mimikatz is one of many tools that dump LSASS; chasing the tool (blocking Mimikatz.exe) is useless, because dozens of variants and reimplementations exist (pypykatz, comsvcs.dll). Credential Guard instead neutralizes the technique: it isolates LSASS so that no tool, present or future, can read its memory. Defending the technique instead of the tool is the principle of effective hardening.

This links to the concept of "raising the cost" - raising the cost of the attack. LAPS does not make it impossible to compromise a machine, but it breaks lateral pass-the-hash: the hash of the local admin of one host does not work on any other, because each host has a unique password. The attacker who compromises one machine no longer obtains the keys to all the others; they must compromise each one individually, multiplying the cost and the probability of being detected. Hardening does not promise invulnerability, it promises to make the attack so costly that it is not worth it.

The foundation is defense in depth applied to identity. In Active Directory, identity is the real perimeter: whoever controls the credentials controls the domain. The hardening countermeasures (Credential Guard on in-memory credentials, LAPS on local passwords, the baseline on insecure defaults) protect different layers of the same critical resource - identity. None is sufficient alone, but together they transform a domain from "compromise of one machine = compromise of the domain" (the model the offensive exploits) to "each machine is a separate obstacle". It is the reversal of the economics that makes a Windows environment defensible.

---

## Real-World scenario: prevention in action

> This section describes how this defensive control would operate in a real incident.

### Attacker perspective (what they attempt)

The attacker compromises a workstation and applies the playbook of `07-post-exploitation`: dumps LSASS with Mimikatz to obtain hashes and tickets, then uses the local admin hash to move laterally (pass-the-hash) toward other hosts, aiming at the Domain Controller.

### Defender perspective (how the control responds)

```
[DEF-008] Domain hardened: Credential Guard + LAPS + baseline via GPO
        |
        v
Attacker launches Mimikatz on LSASS -> Credential Guard isolates LSASS
        |                                 -> encrypted/inaccessible dump (POST-003 neutralized)
        v
Attacker attempts pass-the-hash with the local admin -> LAPS: unique hash per host
        |                                 -> the hash does not work on any other host
        v
Lateral movement blocked: each host requires a separate compromise
        |
        v
Cost and noise of the attack multiplied -> higher probability of detection
```

**Defensive value:** the two countermeasures break the kill chain at the critical point - the passage from a compromised host to the domain. Credential Guard denies the in-memory credentials, LAPS denies their lateral reusability. The attacker who with a single dump would have obtained the keys to the kingdom finds themselves with useless credentials and each host as a separate obstacle.

**Synergy with detection:** the failed attempts (LSASS access, rejected pass-the-hash) generate telemetry (Sysmon/Wazuh) that the detection catches. Hardening not only prevents, but turns the attack attempt into a noisy and detectable signal.

**Defensive lesson:** in Active Directory identity is the perimeter. The countermeasures that protect the credentials (Credential Guard, LAPS) are worth more than any firewall, because they attack the economic model on which domain compromise rests: the reusability of credentials.

---

## Reference tools

| tool | type | role | main use case |
| :--- | :--- | :--- | :--- |
| `Group Policy` (gpo) | policy management | ad | centralized application of hardening to the domain |
| `Microsoft Security Baseline` | baseline (sct) | toolkit | pre-configured and recognized hardening gpos |
| `Credential Guard` | credential protection | feature | isolation of lsass (countermeasure to mimikatz/post-003) |
| `LAPS` | password management | feature | unique and rotated local admin password per host |
| `CIS-CAT` | compliance scanner | cli | verification of conformity to the windows cis benchmarks |
| `AppLocker` / `WDAC` | application control | feature | blocking execution from unauthorized paths |

> **Recommended modern tool:** the `Microsoft Security Baselines` (Security Compliance Toolkit) are the standard starting point, integrated with `CIS-CAT` for conformity verification. `Credential Guard` and `LAPS` (now native Windows LAPS) are the two highest-impact countermeasures against credential dumping and lateral movement techniques. For application control, `WDAC` (Windows Defender Application Control) is more robust than AppLocker.

---

## MITRE ATT&CK mapping

> The table maps the attack techniques that hardening **prevents or neutralizes**.

| tactic (prevented) | technique | mitre id | role of the control |
| :--- | :--- | :--- | :--- |
| credential access | os credential dumping: lsass memory | `T1003.001` | credential guard isolates lsass (neutralizes POST-003) (DEF-008) |
| lateral movement | use alternate authentication material: pass the hash | `T1550.002` | laps: unique local admin hash per host (DEF-008) |
| lateral movement | remote services: smb/windows admin shares | `T1021.002` | disabling smbv1, restriction of admin shares |
| execution | user execution / payload from user paths | `T1204` | applocker/wdac block unauthorized execution |
| persistence | boot or logon autostart: registry run keys | `T1547.001` | baseline restricts autostart keys and privileges |

| defensive countermeasure (d3fend) | d3fend id | application |
| :--- | :--- | :--- |
| platform hardening | `D3-PH` | cis/microsoft baseline applied via gpo |
| credential hardening | `D3-CH` | credential guard + laps protect the credentials |
| executable allowlisting | `D3-EAL` | applocker/wdac allow only authorized executables |

---

> **Note:** All documented activities were conducted on a lab Active Directory environment owned by the author. The hardening GPOs must be tested in a pilot OU before the production rollout, because an erroneous policy can impact the entire domain. Techniques are documented for educational and defensive purposes in an authorized context.
