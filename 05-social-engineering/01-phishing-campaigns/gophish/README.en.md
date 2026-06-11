> **English** | [Italiano](README.md)

# GoPhish - Campaign Management & Credential Harvesting

> - **Phase:** Social Engineering - Phishing Campaign Deployment
> - **Visibility:** High - phishing emails generate SMTP logs, tracking pixel and URLs visible to email filters/proxy/SIEM; the landing page can be classified by URL reputation systems and Google Safe Browsing
> - **Prerequisites:** GoPhish installed (Go binary or Kali package); SMTP relay configured (SendGrid, Mailgun, or local server); target list with valid emails; email template and landing page prepared; domain and TLS certificate for credibility
> - **Output:** SE-001 (credential harvesting campaign with click rate > 30% - severity High); complete campaign metrics (open/click/submit/report rate per individual recipient)

- **Operating Environment:** Kali Linux Purple (Attacker + GoPhish Server), Windows/Linux VM (Simulated Targets)
- **Target:** 20 fictitious users in lab environment
- **Framework:** GoPhish v0.12.1
- **Documented Techniques:** Credential Harvesting via Landing Page Clone, Email Template with Tracking Pixel

---

## Executive Summary

GoPhish is the de facto standard for simulated phishing campaigns in enterprise environments. Unlike tools such as PyPhisher or Zphisher that operate through generic tunnels easily blocked, GoPhish offers a complete ecosystem for professional simulation management: creation of custom email templates with dynamic variables, landing page cloning with credential capture, scheduled sends, and most importantly a granular tracking system that monitors every recipient interaction (email open, link click, credential submission, phishing report).

These metrics are the primary deliverable in a security awareness assessment: they allow measuring the organization's human risk, identifying the most vulnerable departments, and building targeted training programs.

---

## Campaign: Credential Harvesting via Password Reset

**Finding ID:** `SE-001` | **Severity:** `High`

### Operational Context

The campaign simulated a classic corporate phishing scenario: an urgent email from the IT department requesting an immediate password reset, with a link to a cloned landing page of the authentication portal. The scenario was chosen for its documented effectiveness: according to the Proofpoint State of the Phish 2024 report, password reset emails have an average click rate of 25-35% in organizations without structured awareness programs.

### PoC - Phase 1: GoPhish Setup

```Bash
# Download and start GoPhish
cd /opt/gophish
sudo ./gophish
```

```
time="2026-03-15T10:00:00Z" level=info msg="Starting admin server at https://127.0.0.1:3333"    <-- Admin panel
time="2026-03-15T10:00:00Z" level=info msg="Starting phishing server at http://0.0.0.0:80"       <-- Landing page
time="2026-03-15T10:00:00Z" level=info msg="Background Worker Started Successfully"
time="2026-03-15T10:00:00Z" level=info msg="Starting IMAP monitor manager"
```

### PoC - Phase 2: Sending Profile Configuration

```Bash
# Sending Profile (via Web UI -> Sending Profiles -> New Profile)
# Name: Lab-SMTP
# From: it-support@company-lab.local
# Host: 127.0.0.1:25
# Username/Password: (empty for local relay)
# -> Send Test Email for verification
```

### PoC - Phase 3: Landing Page Creation

```Bash
# Landing Page (via Web UI -> Landing Pages -> New Page)
# Name: Company Portal Login
# -> "Import Site" -> URL: https://portal.company-lab.local/login
# [x] Capture Submitted Data
# [x] Capture Passwords
# Redirect to: https://portal.company-lab.local/login?reset=success
```

### PoC - Phase 4: Email Template

```Bash
# Email Template (via Web UI -> Email Templates -> New Template)
# Name: IT Password Reset
# Subject: [URGENT] Mandatory password reset - IT Department
# -> "Import Email" or HTML editor
```

```html
<!-- Simplified HTML template -->
<p>Dear {{.FirstName}},</p>
<p>Your corporate account requires an <b>immediate password reset</b>
due to a scheduled security update.</p>
<p>Click the following link to proceed with the reset:</p>
<p><a href="{{.URL}}">Reset your password</a></p>
<p>If you do not complete this action within 24 hours, your account
will be temporarily suspended.</p>
<p>IT Department<br>{{.From}}</p>

<!-- {{.Tracker}} automatically inserts the 1x1 tracking pixel -->
{{.Tracker}}
```

### PoC - Phase 5: Target Import and Launch

```Bash
# Users & Groups (via Web UI -> Users & Groups -> New Group)
# Name: Lab-Users-Q1
# -> "Bulk Import Users" -> CSV format:
# First Name,Last Name,Email,Position
# Mario,Rossi,m.rossi@company-lab.local,Accounting
# Luca,Bianchi,l.bianchi@company-lab.local,HR
# [... 20 users total ...]
```

```Bash
# Campaign Launch (via Web UI -> Campaigns -> New Campaign)
# Name: Password Reset Q1 2026
# Email Template: IT Password Reset
# Landing Page: Company Portal Login
# Sending Profile: Lab-SMTP
# Groups: Lab-Users-Q1
# -> Launch Campaign
```

### PoC - Phase 6: Campaign Results

```
Campaign Results - "Password Reset Q1 2026"
============================================
Status: Completed

Timeline:
  2026-03-15 10:05 - Campaign launched (20 emails queued)
  2026-03-15 10:05 - 20/20 emails sent successfully
  2026-03-15 10:12 - First email opened (m.rossi@company-lab.local)
  2026-03-15 10:15 - First link clicked (m.rossi@company-lab.local)
  2026-03-15 10:16 - First credentials submitted                       <-- SE-001

Aggregate Metrics:
  Total Recipients:     20
  Emails Sent:          20    (100%)
  Emails Opened:        14    ( 70%)     <-- tracking pixel activated
  Links Clicked:         7    ( 35%)     <-- click rate > 30% threshold
  Data Submitted:        4    ( 20%)     <-- credential harvesting successful
  Email Reported:        1    (  5%)     <-- only 1 report

Credentials Captured:
  m.rossi@company-lab.local      | Password: M4ri0R0ss1!    | 2026-03-15 10:16
  l.bianchi@company-lab.local    | Password: Luca2025       | 2026-03-15 10:22
  a.verdi@company-lab.local      | Password: Company123!    | 2026-03-15 10:31
  f.neri@company-lab.local       | Password: Firenze2026$   | 2026-03-15 11:05
```

### Remediation

- **Immediate action:** forced password reset for the 4 users who submitted credentials; review authentication logs for anomalous access in the following 24 hours; revocation of any active session tokens
- **Structural action:** implementation of security awareness program with quarterly phishing simulations (target: click rate < 10%, report rate > 30%); deploy MFA on all corporate accounts; configure email gateway with URL sandboxing (Proofpoint TAP, Microsoft Safe Links); automatic warning banner on external emails ("This email originated outside your organization")
- **Verification:** repeat the campaign after 3 months of training - measure the click rate and report rate delta compared to baseline

---

## Lab Experience

The test environment was configured with GoPhish v0.12.1 on Kali Linux Purple, using a local SMTP relay (Postfix) to send emails to the mailboxes of 20 fictitious users hosted on a second VM with Mailhog as the receiving SMTP server.

The first difficulty encountered was the Sending Profile configuration: GoPhish requires a functioning SMTP relay and the internal test ("Send Test Email") returned a `Connection refused on port 25` error until Postfix was reconfigured to accept unauthenticated local connections. In a real engagement, the relay would be an external service (SendGrid, Amazon SES) with domain and DKIM configured to maximize deliverability.

The most critical phase was the email template design. The first template was too generic and contained HTML formatting errors visible in email clients. After a review inspired by real phishing templates (catalogued on phishtank.org), the template was refined with: temporal urgency ("within 24 hours"), authority impersonation ("IT Department"), and a single clear call-to-action. This iteration brought the click rate from 15% (first test send) to 35% (final campaign).

The most significant data point from the exercise is not the click rate itself (35% is within the average for untrained organizations), but the report rate: only 1 out of 20 users (5%) reported the suspicious email. In an organization with a mature awareness program, the target report rate is above 30%.

---

## Theoretical Analysis: Why Phishing Works

The effectiveness of phishing is not a technological problem but a cognitive one. The template used exploits three of Robert Cialdini's six principles of influence:

1. **Authority:** the email comes from the "IT Department," a source perceived as legitimate and authoritative in technical matters.
2. **Urgency/Scarcity:** the threat of account suspension within 24 hours activates the limbic system (fight-or-flight response), bypassing critical analysis of the prefrontal cortex.
3. **Implicit social proof:** the formal tone and email structure replicate real corporate communications, creating familiarity.

From a technical perspective, GoPhish leverages two key mechanisms: the tracking pixel (a 1x1 transparent image loaded from a unique URL per recipient) to measure email opens, and the `rid` (recipient ID) parameter in the landing page URL to track which user clicked. Captured credentials are saved in GoPhish's SQLite database and are viewable from the dashboard in real time.

The critical difference between GoPhish and amateur tools (PyPhisher, Zphisher) is traceability: GoPhish produces a structured report with per-recipient metrics, timestamps for every interaction, and aggregated data by department. This report is the deliverable the client expects in a security awareness assessment.

---

## Real-World Scenario: Post-Exploitation Projection

> This section describes how this finding would fit into a real engagement, from both the attacker (Red Team) and defender (Blue Team) perspectives.

### Attacker Perspective (Red Team)

**Starting point:** 4 valid corporate credentials obtained through phishing (SE-001).

**Immediate next step:** targeted credential stuffing - test the 4 credentials on all exposed services of the organization (VPN, OWA, SharePoint, Citrix) to identify credential reuse.

**Projected kill chain:**

```
[SE-001] Credentials harvested (4 accounts)
        |
        v
Credential Stuffing on VPN/OWA -> remote access with legitimate account
        |
        v
Email compromise (BEC) -> internal phishing sent from trusted account
        |
        v
Lateral Movement -> access to internal shares, escalation via Active Directory
        |
        v
Domain Admin -> data exfiltration / ransomware deployment
```

**Potential impact:** complete compromise of the Active Directory domain starting from a single standard-level account. The average time from Initial Access to Domain Admin, according to Mandiant M-Trends 2024 reports, is less than 48 hours in organizations without network segmentation.

### Defender Perspective (Blue Team)

**IOCs to monitor:**
- Emails with tracking pixels pointing to non-corporate domains (URLs with `rid` or similar parameters)
- Logins from anomalous IP/geolocation for compromised accounts
- Multiple accesses to different services from the same account in a short time window (credential stuffing pattern)
- Creation of email forwarding rules in the compromised account (persistence)

**Immediate containment:**
- Forced password reset for all compromised accounts
- Revocation of active session tokens (Azure AD: `Revoke-AzureADUserAllRefreshToken`)
- Verification of email forwarding rules created in the last 7 days
- Authentication log analysis for credential stuffing patterns

**Hardening:**
- Deploy FIDO2/WebAuthn MFA (not SMS/OTP - vulnerable to Evilginx)
- Conditional Access: block logins from non-operational countries
- Email gateway: URL rewriting + time-of-click analysis
- Security awareness: quarterly training with improvement metrics

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Resource Development | Stage Capabilities: Upload Malware | `T1608.001` | Preparation of clone landing page and email template on GoPhish server (SE-001) |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | Sending email with link to credential harvesting landing page (SE-001) |
| Execution | User Execution: Malicious Link | `T1204.001` | 7 out of 20 users clicked the phishing link (SE-001) |
| Credential Access | Input Capture: Web Portal Capture | `T1056.003` | 4 users entered credentials in the cloned landing page (SE-001) |
| Discovery | System Information Discovery | `T1082` | Tracking pixel revealed User-Agent and IP of 14 users who opened the email |

---

> **Note:** All documented activities were conducted in a virtualized lab environment (VirtualBox, isolated NAT/Bridge network). Campaign recipients are fictitious users created ad hoc. No phishing emails were sent to real addresses. Techniques are documented for educational and security awareness testing purposes.
