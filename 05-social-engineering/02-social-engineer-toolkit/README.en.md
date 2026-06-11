> **English** | [Italiano](README.md)

# 02 - Social-Engineer Toolkit (SET)

> - **Phase:** Social Engineering - Multi-Vector Attack Framework
> - **Visibility:** Variable - from Medium (website cloning generates anomalous HTTP traffic) to High (email with payload triggers email gateway, PowerShell execution triggers EDR)
> - **Prerequisites:** SET installed on Kali Linux (`sudo apt install set`); for spear-phishing: SMTP relay configured; for website attacks: port 80/443 available on the listener; payloads generated with msfvenom if needed
> - **Output:** Finding SE-003..006; credentials harvested via website clone; payloads delivered via email and removable media; reverse shells obtained via encoded PowerShell

---

## Introduction

The Social-Engineer Toolkit (SET), created by David Kennedy (TrustedSec), is the most comprehensive offensive framework for social engineering attacks. SET integrates the main attack vectors that a penetration tester uses to compromise the human factor into a single menu-driven interface. Unlike GoPhish - focused on email campaigns with metrics - SET is oriented toward active exploitation: site cloning for credential harvesting, malicious payload generation and delivery, attacks via removable media.

The lab documents four of SET's six main vectors, selected for their operational relevance in a modern engagement:

1. **Website Attack Vectors (SE-003):** real-time cloning of a login page and credential harvesting. The most commonly used vector: the user enters credentials in a perfect replica of the corporate portal.

2. **Spear-Phishing Attack Vectors (SE-004):** generation of email with attached payload (disguised .hta). SET handles payload creation, email composition, and SMTP delivery.

3. **Infectious Media Generator (SE-005):** creation of autorun payloads for removable media (USB). A classic technique but still effective in environments with autorun enabled or untrained employees.

4. **PowerShell Attack Vectors (SE-006):** generation of Base64 encoded PowerShell one-liner for reverse shell. Bypasses restrictive execution policies and operates entirely in memory.

In the kill chain, SET simultaneously covers the Weaponization, Delivery, and Exploitation phases: it prepares the payload, delivers it to the target, and collects the result (credentials or shell).

---

## Folder Structure

```
02-social-engineer-toolkit/
+-- website-attack-vectors/       # Credential harvester via site clone - SE-003
+-- spear-phishing-vectors/       # Email with .hta payload - SE-004
+-- infectious-media-generator/   # Autorun USB payload - SE-005
+-- powershell-attack-vectors/    # PS-encoded reverse shell - SE-006
```

---

## `website-attack-vectors/` - Credential Harvester via Site Clone

**Finding ID:** `SE-003` | **Severity:** `High` (credentials captured in cleartext via cloned login page)

### Operational Context

SET clones a target service's login page in real time and serves it on a local web server controlled by the attacker. When the victim enters credentials in the cloned page, SET captures them and displays them in the attacker's console, then redirects the victim to the real site to avoid suspicion. Compared to GoPhish, this technique is faster to configure but does not offer campaign metrics.

### Key Commands

```Bash
sudo setoolkit
# 1) Social-Engineering Attacks
# 2) Website Attack Vectors
# 3) Credential Harvester Attack Method
# 2) Site Cloner
# IP: 192.168.0.110
# URL to clone: https://portal.company-lab.local/login
```

---

## `spear-phishing-vectors/` - Email with Payload Attachment

**Finding ID:** `SE-004` | **Severity:** `High` (payload .hta executed via spear-phishing email)

### Operational Context

SET generates a customized email with an attached payload and sends it via SMTP relay. The lab used an .hta (HTML Application) file as the vector: when the victim opens the attachment, Windows executes the HTA code that launches a PowerShell stager for the reverse shell. The .hta format was chosen because it bypassed traditional filters (it is not an .exe) and is natively executable on Windows.

### Key Commands

```Bash
sudo setoolkit
# 1) Social-Engineering Attacks
# 1) Spear-Phishing Attack Vectors
# 1) Perform a Mass Email Attack
# -> Select payload (e.g., Windows Reverse Shell)
# -> Configure LHOST, LPORT
# -> Compose email with attachment
# -> Send via SMTP
```

---

## `infectious-media-generator/` - Autorun USB Payload

**Finding ID:** `SE-005` | **Severity:** `Medium` (payload executed via autorun on removable media)

### Operational Context

SET generates a payload with an autorun.inf file configured for automatic execution when the USB drive is mounted. Although autorun is disabled by default on Windows 10+, the technique remains relevant in legacy environments (Windows 7, industrial systems) and can be combined with social engineering (USB labeled "Salary_Report_2026.pdf" left in a common area).

### Key Commands

```Bash
sudo setoolkit
# 1) Social-Engineering Attacks
# 3) Infectious Media Generator
# -> Select payload
# -> Configure LHOST, LPORT
# -> Output: files for USB (autorun.inf + payload)
```

---

## `powershell-attack-vectors/` - Encoded Reverse Shell

**Finding ID:** `SE-006` | **Severity:** `High` (encoded PowerShell reverse shell bypasses execution policy)

### Operational Context

SET generates a Base64 encoded PowerShell one-liner that, when executed on the target Windows machine, establishes a reverse shell to the attacker. The Base64 encoding bypasses restrictive execution policies (`-ExecutionPolicy Bypass`) and execution occurs entirely in memory without writing files to disk, reducing the detection surface for signature-based AV solutions.

### Key Commands

```Bash
sudo setoolkit
# 1) Social-Engineering Attacks
# 4) PowerShell Attack Vectors
# 1) PowerShell Alphanumeric Shellcode Injector
# -> LHOST: 192.168.0.110
# -> LPORT: 4444
# Output: encoded PowerShell one-liner to deliver to the victim
```

---

## Recommended Operational Flow

```
[1] Target reconnaissance
     +-- What is the login service? -> URL for website clone
     +-- Valid emails available? -> spear-phishing possible
     +-- Physical access? -> infectious media
              |
              v
[2] SET vector selection
     +-- Credentials only ----------> Website Attack Vectors (SE-003)
     +-- Code execution via email --> Spear-Phishing Vectors (SE-004)
     +-- Physical code execution ---> Infectious Media (SE-005)
     +-- Quick Windows shell -------> PowerShell Attack (SE-006)
              |
              v
[3] Listener setup (if code execution)
     +-- Metasploit: use exploit/multi/handler
     +-- SET: built-in listener
              |
              v
[4] Delivery & Collection
     +-- Credentials -> SET console in real-time
     +-- Shell -> Meterpreter / reverse_tcp callback
```

---

## Reference Tools

| Tool | Type | Technique/Access | Primary Use Case |
| :--- | :--- | :--- | :--- |
| `SET (setoolkit)` | SE framework | CLI - Interactive menu | Multi-vector framework: clone, spear-phishing, media, PowerShell |
| `msfvenom` | Payload generator | CLI | Custom payload generation for SET attachments |
| `Metasploit` | Exploitation framework | CLI | Handler for reverse shells generated by SET |
| `BeEF` | Browser exploitation | Web UI | Alternative for client-side attacks via JavaScript hook |
| `HiddenEye` | Phishing tool | CLI - Python | Modern alternative to SET for website cloning |

> **Recommended modern tool:** SET remains relevant for its multi-vector integration, but for credential harvesting alone `GoPhish` offers superior metrics. For modern payload delivery, consider techniques in `03-payload-delivery/` (HTML Smuggling, ISO+LNK) that bypass current filters.

---

## Finding Registry

| ID | Description | Severity | CVSS | Subfolder |
| :--- | :--- | :---: | :---: | :--- |
| `SE-003` | SET Website Attack: credential harvester via cloned login page, credentials captured in cleartext | `High` | 7.5 | `website-attack-vectors/` |
| `SE-004` | SET Spear-Phishing: email with .hta attachment, PowerShell stager executed on victim | `High` | 8.1 | `spear-phishing-vectors/` |
| `SE-005` | SET Infectious Media: autorun.inf payload on USB, execution on mount (legacy environments) | `Medium` | 5.3 | `infectious-media-generator/` |
| `SE-006` | SET PowerShell Attack: Base64 encoded reverse shell, execution policy bypass, in-memory execution | `High` | 8.1 | `powershell-attack-vectors/` |

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Related Finding |
| :--- | :--- | :--- | :--- |
| Resource Development | Obtain Capabilities: Tool | `T1588.002` | SE-003, SE-004, SE-005, SE-006 |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | SE-003 |
| Initial Access | Phishing: Spearphishing Attachment | `T1566.001` | SE-004 |
| Initial Access | Replication Through Removable Media | `T1091` | SE-005 |
| Execution | User Execution: Malicious Link | `T1204.001` | SE-003 |
| Execution | User Execution: Malicious File | `T1204.002` | SE-004, SE-005 |
| Execution | Command and Scripting Interpreter: PowerShell | `T1059.001` | SE-006 |
| Defense Evasion | Obfuscated Files or Information | `T1027` | SE-006 |
| Credential Access | Input Capture: Web Portal Capture | `T1056.003` | SE-003 |

---

> **Note:** All documented activities were conducted in a virtualized lab environment (VirtualBox, isolated NAT/Bridge network). Payloads were executed exclusively on virtual machines owned by the author. No payload was sent to real systems or people.
