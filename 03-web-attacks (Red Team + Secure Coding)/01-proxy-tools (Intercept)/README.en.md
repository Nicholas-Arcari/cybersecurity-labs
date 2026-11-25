> **English** | [Italiano](README.md)

# 01 - Proxy tools (intercept)

> - **Phase:** Web Attack - Proxy Setup & Traffic Interception
> - **Visibility:** Local - traffic stays between browser and proxy, no additional packets towards the target
> - **Prerequisites:** Browser configured to use the proxy (`127.0.0.1:8080`), proxy CA certificate installed in the browser trust store
> - **Output:** HTTP/HTTPS traffic interception and manipulation, request logging, finding WEB-001

---

## Introduction

Before testing any web application, it is necessary to position yourself between the browser and the server. Interception proxy tools perform a **local Man-in-the-Middle**: the browser sends requests to the proxy, which blocks them, makes them inspectable and modifiable, then sends them to the actual server.

Without this stage, every test is limited to what is visible in the user interface. With an active proxy, you gain access to the entire HTTP layer: hidden headers, session tokens, parameters sent via POST, server responses before the browser processes them.

The operational logic is:

1. The browser communicates with the proxy (Burp Suite or OWASP ZAP).
2. The proxy intercepts the request, blocks it and presents it to the analyst.
3. The analyst modifies it (User-Agent, cookies, parameters) and sends it to the server.
4. The server responds to the proxy, which in turn responds to the browser.

For HTTPS traffic, the proxy must generate fake SSL certificates on the fly. The browser accepts these certificates only if the proxy's CA is installed in its trust store - hence the need for the certificate configuration described in `certificates/`.

---

## Folder structure

```
01-proxy-tools (Intercept)/
+-- burp-suite/       # Proxy configuration, User-Agent spoofing, BApp Store
+-- certificates/     # Burp CA installation for HTTPS interception
+-- owasp-zap/        # Automated DAST scanner - finding WEB-001
```

---

## `burp-suite/` - Traffic interception & manipulation

### Operational context

Burp Suite is the de facto standard for web application penetration testing. It is used in manual mode to analyze individual requests, manipulate parameters, test business logic and conduct targeted attacks. The Community Edition limits Scanner speed; the Professional Edition is used in real engagements.

Key use cases:
- **User-Agent Spoofing:** impersonating a crawler (GoogleBot) to bypass WAFs that block known automated scanners.
- **Parameter Tampering:** modifying POST form values, session IDs, CSRF tokens.
- **Repeater:** resending modified requests to the server iteratively (useful for manual SQLi and IDOR testing).
- **Intruder:** automated attacks on individual parameters (brute force, fuzzing).

### Essential commands

```Bash
# Launch Burp Suite Community Edition from terminal
burpsuite
```

Browser configuration (Firefox):
- `Settings -> Network -> Connection Settings -> Manual Proxy`
- HTTP Proxy: `127.0.0.1` - Port: `8080`

---

## `certificates/` - HTTPS interception setup

### Operational context

Modern HTTPS traffic is encrypted end-to-end. To intercept it, the proxy generates an SSL certificate for each visited domain, signed by its own internal CA. The browser accepts this certificate only if the CA has been imported as a "trusted authority".

Without this step, the browser displays a `SEC_ERROR_UNKNOWN_ISSUER` error and refuses to load HTTPS pages, making it impossible to test any modern application.

### Procedure

1. Start Burp Suite and navigate to `http://burp` from the browser configured with the proxy.
2. Download the `cacert.der` certificate.
3. In Firefox: `Settings -> Privacy -> Certificates -> View Certificates -> Import`.
4. Select `cacert.der` and enable "Trust this CA to identify websites".
5. Verify: visit `https://google.com` - the certificate issuer should be "PortSwigger CA".

---

## `owasp-zap/` - Automated DAST scanner

**Finding ID:** `WEB-001` | **Severity:** `Medium` | **CVSS v3.1:** 5.4

### Operational context

OWASP ZAP (Zed Attack Proxy) is the reference open-source DAST scanner. Unlike Burp Suite (manual analysis), ZAP is optimized for automated scanning: it runs a crawler to map all pages and forms, then launches test payloads (SQLi, XSS, CSRF) on every parameter found.

The primary real-world use case is CI/CD pipeline integration (Jenkins, GitHub Actions) to automatically block deployment if vulnerabilities are detected. For an analyst, ZAP provides a quick initial baseline before manual analysis with Burp.

### Commands

```Bash
# Launch OWASP ZAP from terminal
zaproxy
```

Example output (Alerts section):

```
Alert: Absence of Anti-CSRF Tokens                     <-- WEB-001
Risk: Medium
Confidence: Medium
URL: http://testphp.vulnweb.com/guestbook.php
Evidence: <form method="POST" action="/guestbook.php">
Description: No Anti-CSRF tokens were found in a HTML submission form.

Alert: User Controllable HTML Element Attribute
Risk: Medium
URL: http://testphp.vulnweb.com/listproducts.php
Parameter: cat
```

### Finding WEB-001 analysis

The `guestbook.php` form does not implement CSRF tokens. An attacker can build a malicious web page that sends POST requests to the form as if they came from the authenticated user, executing actions on their behalf (posting content, modifying profile).

### Remediation

- **Immediate action:** generate and validate a random CSRF token (e.g., using `csurf` in Node.js, `django.middleware.csrf.CsrfViewMiddleware` in Django) for every stateful form.
- **Structural action:** implement the Synchronizer Token Pattern or Double Submit Cookie on all POST forms.
- **Verification:** rerun OWASP ZAP after the patch and confirm the `Absence of Anti-CSRF Tokens` alert is no longer present.

---

## Recommended operational flow

```
[1] Configure browser -> proxy 127.0.0.1:8080
         |
         v
[2] Install Burp CA certificate (certificates/)
         |
         v
[3] Browse the target with Intercept ON (burp-suite/)
         +-- manual analysis: Repeater, Intruder
         |
         v
[4] Launch automated scan (owasp-zap/)
         +-- Automated Scan -> Spider -> Active Scan
         |
         v
[5] Alert Triaging
         +-- Manual verification of each alert (eliminate false positives)
         +-- Document confirmed findings
```

---

## Reference tools

| tool | type | technique/access | primary use case |
| :--- | :--- | :--- | :--- |
| `Burp Suite Community` | proxy / interceptor | gui + browser proxy | manual analysis, request modification, repeater |
| `Burp Suite Professional` | proxy / scanner | gui + browser proxy | real engagements, advanced automated scanning |
| `OWASP ZAP` | dast scanner | gui + cli | automated scanning, ci/cd integration |
| `mitmproxy` | cli proxy | terminal | lightweight command-line interception |
| `Caido` | modern proxy | web ui | modern burp alternative, browser-based interface |

> **Recommended modern tool:** `Caido` - alternative to Burp Suite with native web interface, YAML-based workflows and excellent session management. Install from `https://caido.io` with the dedicated package manager.

---

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| collection | man-in-the-middle | `T1557` | positioning burp suite proxy between browser and server to intercept http/https traffic |
| defense evasion | subvert trust controls: install root certificate | `T1553.004` | installing burp ca certificate in the browser trust store to enable https interception without errors |
| collection | man-in-the-middle: aitm https interception | `T1557.002` | generating fake ssl certificates for each visited domain, allowing encrypted traffic reading |
| reconnaissance | active scanning: vulnerability scanning | `T1595.002` | dast scanning with owasp zap generating traffic towards the target to identify vulnerabilities (WEB-001) |
| initial access | exploit public-facing application | `T1190` | identification of forms lacking csrf tokens (WEB-001) as an attack vector for cross-site request forgery |

---

> **Note:** Proxy configuration and HTTPS interception were performed in a local lab environment. In production environments, installing unauthorized CA certificates constitutes a violation of corporate security policies and potentially a criminal offense. All activities were conducted on authorized targets (`testphp.vulnweb.com` - public test environment).
