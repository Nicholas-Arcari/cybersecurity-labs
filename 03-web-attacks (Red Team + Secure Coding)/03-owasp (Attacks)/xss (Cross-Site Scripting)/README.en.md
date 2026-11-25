> **English** | [Italiano](README.md)

# Cross-Site scripting (XSS)

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

## 3 [XSS hunter payloads](./xss-hunter-payloads/) (blind XSS)

Resources for "Blind XSS" attacks. In this scenario, the attacker injects the payload blindly (e.g., in a "Contact Us" form or in server Logs) and does not see the immediate result.

The payload is designed to "call home" (send a notification to the attacker) only when an Administrator views that data in the protected management panel.

- Impact: Critical (Often compromises Administrator/Backend accounts).

---

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | exploitation of unsanitized inputs to inject javascript code into the application (WEB-005, WEB-006, WEB-007) |
| credential access | steal web session cookie | `T1539` | session cookie theft through `document.cookie` injected via xss (WEB-005, WEB-006) |
| initial access | phishing: spearphishing link | `T1566.002` | distribution of malicious urls with reflected xss payloads to target specific users (WEB-005) |
| persistence | server software component: web shell | `T1505.003` | persistent stored xss in database that executes code on every page view (WEB-006) |
| collection | browser session hijacking | `T1185` | victim redirect towards attacker server through stored xss to silently capture the cookie (WEB-007) |
| reconnaissance | gather victim identity information | `T1589` | blind/oob xss through img tag to obtain the administrator's ip and user-agent when viewing the profile (WEB-007) |

---

> **Note:** The three XSS variants documented in the subfolders (`reflected/`, `stored/`, `xss-hunter-payloads/`) were practiced on `testphp.vulnweb.com` (Acunetix environment). Findings WEB-005, WEB-006, WEB-007 document real vulnerabilities on the same target, progressively more critical in terms of impact and detection difficulty.
