> **English** | [Italiano](README.md)

# Cross-Site Scripting (XSS)

> - **Phase:** Web Attack - Cross-Site Scripting (XSS)
> - **Visibility:** Variable - Low (Reflected and Stored: standard requests) / Zero (Blind: dormant payload)
> - **Prerequisites:** Input point that reflects or persists user input without encoding, proxy configured for interception
> - **Output:** Arbitrary JavaScript execution in victim's browser, cookie theft, defacement, findings WEB-005..007

---

Cross-Site Scripting (XSS) is a vulnerability that allows an attacker to inject malicious scripts within web pages viewed by other users.

This repository contains practical examples of the two main XSS types:

## 1 [Reflected XSS](./reflected/)

The script is injected in the request (e.g., URL parameter) and immediately reflected by the server. It requires the victim to click on a malicious link.

- Impact: Phishing, Session Hijacking (Requires user interaction).

## 2 [Stored XSS](./stored/)

The script is permanently saved on the target server (e.g., in a database). The victim executes the script simply by viewing the infected page.

- Impact: Critical (No user interaction required, affects multiple users/administrators).

## 3 [XSS Hunter Payloads](./xss-hunter-payloads/) (Blind XSS)

Resources for "Blind XSS" attacks. In this scenario, the attacker injects the payload blindly (e.g., in a "Contact Us" form or in server Logs) and does not see the immediate result.

The payload is designed to "call home" (send a notification to the attacker) only when an Administrator views that data in the protected management panel.

- Impact: Critical (Often compromises Administrator/Backend accounts).

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Exploitation of unsanitized inputs to inject JavaScript code into the application (WEB-005, WEB-006, WEB-007) |
| Credential Access | Steal Web Session Cookie | `T1539` | Session cookie theft through `document.cookie` injected via XSS (WEB-005, WEB-006) |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | Distribution of malicious URLs with Reflected XSS payloads to target specific users (WEB-005) |
| Persistence | Server Software Component: Web Shell | `T1505.003` | Persistent Stored XSS in database that executes code on every page view (WEB-006) |
| Collection | Browser Session Hijacking | `T1185` | Victim redirect towards attacker server through Stored XSS to silently capture the cookie (WEB-007) |
| Reconnaissance | Gather Victim Identity Information | `T1589` | Blind/OOB XSS through img tag to obtain the administrator's IP and User-Agent when viewing the profile (WEB-007) |

---

> **Note:** The three XSS variants documented in the subfolders (`reflected/`, `stored/`, `xss-hunter-payloads/`) were practiced on `testphp.vulnweb.com` (Acunetix environment). Findings WEB-005, WEB-006, WEB-007 document real vulnerabilities on the same target, progressively more critical in terms of impact and detection difficulty.
