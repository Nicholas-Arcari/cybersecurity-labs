> **English** | [Italiano](README.md)

# Tech Stack Fingerprinting: WhatWeb & BuiltWith

> - **Phase:** Reconnaissance - Infrastructure Intelligence
> - **Visibility:** Low - standard HTTP requests for fingerprinting, detectable by WAF but common in legitimate traffic
> - **Prerequisites:** WhatWeb installed, target domain, Wappalyzer as browser extension for passive analysis
> - **Output:** INTEL-004 - Target technology profile; in this lab: Akamai WAF detected on tesla.com, backend fingerprinting blocked

---

Objective: Identify the underlying technologies (CMS, Web Server, Framework, JS Libraries) used by the target to find obsolete versions or known vulnerabilities (CVE).

Target: `tesla.com`

Tools: `WhatWeb` (CLI), `Wappalyzer` (Browser Extension), `BuiltWith` (Web)

---

## 1 Theoretical Introduction

Tech Stack Fingerprinting is the process of collecting "digital fingerprints" from the web server. By analyzing HTTP responses, cookies, and HTML source code, it is possible to determine:

- Operating System: (e.g., Ubuntu, CentOS, Windows Server)
- Web Server: (e.g., Nginx, Apache, IIS)
- Framework/CMS: (e.g., Drupal, WordPress, React)
- Client-side Libraries: (e.g., jQuery, Bootstrap)

For an attacker, this phase is crucial to select the correct exploits (e.g., not launching PHP attacks against a Java server).

---

## 2 Technical Execution: WhatWeb

**Finding ID:** `INTEL-004` | **Severity:** `Informational`

`WhatWeb` is a next-generation scanner that identifies web technologies. It was launched against the target domain to obtain a quick profile.

Command:
```Bash
whatweb -v tesla.com
```

(Note: The -v option enables verbose mode for more details)

![](./img/Screenshot_2026-02-08_15_33_17.jpg)

![](./img/Screenshot_2026-02-08_15_40_42.jpg)

Output Analysis:

The output demonstrates the effectiveness of Tesla's perimeter defenses. The scanner failed to reach the underlying web application, being blocked at the entrance:

- Access Denied / 403 Forbidden:

    Observation: The scanner received an HTTP `403 Forbidden` status and the page title `Access Denied`, instead of the classic `200 OK`.

    Technical Analysis: The defense system identified `WhatWeb`'s signature (User-Agent or behavior) as automated/malicious traffic, immediately terminating the connection.

- The "Culprit" (Akamai):

    Observation: The following plugins were detected: `Akamai-Global-Host` and the server string `AkamaiGHost`.

    Technical Analysis: This confirms that `tesla.com` uses Akamai as CDN and WAF (Web Application Firewall). The resolved IP is not the real server's, but an Akamai edge node's, acting as a shield (Reverse Proxy) against direct attacks.

- SSL Security (HSTS):

    Observation: The header `Strict-Transport-Security` is present.

    Technical Analysis: The domain forces browsers to use exclusively encrypted HTTPS connections, preventing "SSL Stripping" or "Downgrade" attacks.

---

## 3 Conclusions

This fingerprinting phase confirmed that tesla.com uses a "Defense in Depth" strategy. Automated direct attack is effectively mitigated by Akamai. For an attacker, this implies that using "noisy" active scanners (like Nikto or standard WhatWeb) is ineffective against the main domain. It would be necessary to use evasion techniques (IP rotation, User-Agent spoofing) or shift to purely passive reconnaissance (Wappalyzer) to map backend technologies (e.g., Drupal) without alerting the WAF.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Host Info: Software | `T1592.002` | Technology fingerprinting of tesla.com with WhatWeb to identify CMS, web server, framework and client-side libraries (INTEL-004) |
| Reconnaissance | Active Scanning: Vulnerability Scanning | `T1595.002` | HTTP fingerprinting request that revealed the presence of Akamai WAF as perimeter defense system, confirming active HSTS (INTEL-004) |

---

> **Note:** The fingerprinting documented in this section was performed on tesla.com within the public bug bounty program. WhatWeb sends a single standard HTTP GET request, equivalent to a normal browser visit. No exploitation or WAF evasion techniques were attempted.
