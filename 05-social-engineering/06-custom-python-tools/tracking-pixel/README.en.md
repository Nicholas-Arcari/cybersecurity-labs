> **English** | [Italiano](README.md)

# Tracking Pixel - Email Open Tracking & IP Geolocation

> - **Phase:** Social Engineering - Campaign Analytics (Email Open Detection)
> - **Visibility:** Low - the tracking pixel is a single HTTP GET request for a 1x1 image; indistinguishable from loading legitimate email resources; detectable only by email clients that block external image loading by default
> - **Prerequisites:** Python 3.x, Flask; server reachable from the victim's email client; for geolocation: GeoLite2 database (MaxMind, free with registration)
> - **Output:** SE-015 (IP geolocation at the time of email opening - severity Informational)

- **Operating Environment:** Kali Linux Purple (Flask Server), Windows 10 VM (Outlook Client)
- **Framework:** Flask 3.x, Python 3.11
- **Documented Techniques:** Tracking Pixel Injection, IP Logging, GeoIP Resolution

---

## Executive Summary

The tracking pixel is a classic legitimate email marketing technique (used by all newsletter services) applied to social engineering to measure phishing email open rates. The Flask server serves a 1x1 transparent GIF image (43 bytes) with a unique URL per recipient. When the email client loads the image, the server logs IP, User-Agent, timestamp and - with the GeoLite2 database - approximate geolocation.

GoPhish includes this functionality natively (variable `{{.Tracker}}`), but the custom server allows tracking independent of the phishing framework and integration with non-GoPhish campaigns (SET, manual emails, LinkedIn messages).

---

## Tracking Pixel: Email Open Detection

**Finding ID:** `SE-015` | **Severity:** `Informational`

### PoC - Phase 1: Flask Server

```python
# tracker.py
from flask import Flask, request, send_file
import json, datetime, io

app = Flask(__name__)

PIXEL = (b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00'
         b'\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x00\x00'
         b'\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00'
         b'\x00\x02\x02\x44\x01\x00\x3b')

@app.route('/img/<tid>.gif')
def track(tid):
    data = {
        'timestamp': datetime.datetime.now().isoformat(),
        'tracking_id': tid,
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'unknown'),
    }
    with open('logs/opens.json', 'a') as f:
        f.write(json.dumps(data) + '\n')
    print(f"[*] Email opened by {tid}: IP {data['ip']}")
    return send_file(io.BytesIO(PIXEL), mimetype='image/gif',
                     max_age=0)  # no cache

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### PoC - Phase 2: Embedding in Email Template

```html
<!-- Insert in the phishing email HTML template -->
<img src="http://192.168.0.110:8080/img/user001.gif"
     width="1" height="1" style="display:none" alt="" />
```

### PoC - Phase 3: Result

```Bash
python3 tracker.py
```

```
 * Running on http://0.0.0.0:8080

[*] Email opened by user001: IP 192.168.0.120              <-- SE-015
[*] Email opened by user003: IP 192.168.0.122
[*] Email opened by user001: IP 192.168.0.120              <-- second open (re-read)
```

```
# logs/opens.json
{"timestamp": "2026-03-15T10:12:00", "tracking_id": "user001", "ip": "192.168.0.120", "user_agent": "Mozilla/5.0 Outlook/16.0"}
{"timestamp": "2026-03-15T10:15:30", "tracking_id": "user003", "ip": "192.168.0.122", "user_agent": "Mozilla/5.0 Outlook/16.0"}
```

### Remediation

- **Immediate action:** N/A (informational finding, no direct impact)
- **Structural action:** configure email client to block external image loading by default (Outlook: `File > Options > Trust Center > Automatic Download > Don't download pictures`); email gateway with image proxy that anonymizes the user's IP (Google Workspace Image Proxy, Apple Mail Privacy Protection)
- **Verification:** open test email with tracking pixel - the server must not receive the request if external images are blocked

---

## Lab Experience

The test was conducted with Outlook on a Windows 10 VM configured with default settings (image loading enabled). Tracking worked immediately: opening the email generated the HTTP GET request to the Flask server.

An important aspect that emerged from testing: Outlook in "preview pane" mode loads images even without the user explicitly opening the email. This means the tracking pixel registers an "open" even when the user simply scrolls through the inbox. For professional campaigns, it is important to distinguish between "preview" (User-Agent contains "Outlook") and "browser click" (User-Agent contains "Chrome/Firefox") for accurate metrics.

---

## Theoretical Analysis: Tracking Pixel Limitations

The tracking pixel has three main limitations:

1. **Clients with blocked images:** Outlook for macOS, Thunderbird, and Apple Mail (with Privacy Protection enabled) block external image loading by default, rendering the tracking pixel ineffective.

2. **Image proxies:** Google Workspace and Apple Mail Privacy Protection proxy image requests through their own servers, masking the user's real IP. The server sees the Google/Apple proxy IP, not the user's.

3. **False positives:** automated email scanners (sandbox, antivirus) may load images during pre-delivery analysis, generating false "opens" before the email even reaches the recipient's inbox.

Despite these limitations, the tracking pixel remains the de facto standard for measuring email open rate because no more reliable alternative exists that does not require active user interaction (such as clicking a link).

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Resource Development | Stage Capabilities: Upload Malware | `T1608.001` | Tracking pixel server deployment on attacker infrastructure |
| Discovery | System Information Discovery | `T1082` | Victim IP, User-Agent and geolocation collection (SE-015) |
| Reconnaissance | Active Scanning: Scanning IP Blocks | `T1595.001` | Active recipient IP identification via tracking |

---

> **Note:** The tracking server was tested exclusively in a lab environment. No tracking pixel was sent to real email addresses.
