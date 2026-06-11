> [English](README.en.md) | **Italiano**

# Tracking Pixel - Email Open Tracking & IP Geolocation

> - **Fase:** Social Engineering - Campaign Analytics (Email Open Detection)
> - **Visibilita:** Bassa - il tracking pixel e una singola richiesta HTTP GET per un'immagine 1x1; indistinguibile dal caricamento di risorse email legittime; rilevabile solo da client email che bloccano il caricamento immagini esterne di default
> - **Prerequisiti:** Python 3.x, Flask; server raggiungibile dal client email della vittima; per geolocalizzazione: database GeoLite2 (MaxMind, gratuito con registrazione)
> - **Output:** SE-015 (geolocalizzazione IP al momento dell'apertura email - severity Informativo)

- **Ambiente Operativo:** Kali Linux Purple (Server Flask), Windows 10 VM (Client Outlook)
- **Framework:** Flask 3.x, Python 3.11
- **Tecniche Documentate:** Tracking Pixel Injection, IP Logging, GeoIP Resolution

---

## Executive Summary

Il tracking pixel e una tecnica classica di email marketing legittimo (utilizzata da tutti i servizi di newsletter) applicata al social engineering per misurare l'apertura delle email di phishing. Il server Flask serve un'immagine GIF trasparente di 1x1 pixel (43 byte) con un URL unico per destinatario. Quando il client email carica l'immagine, il server logga IP, User-Agent, timestamp e - con il database GeoLite2 - la geolocalizzazione approssimativa.

GoPhish include questa funzionalita nativamente (variabile `{{.Tracker}}`), ma il server custom permette tracking indipendente dal framework di phishing e integrazione con campagne non-GoPhish (SET, email manuali, LinkedIn messages).

---

## Tracking Pixel: Email Open Detection

**ID Finding:** `SE-015` | **Severity:** `Informativo`

### PoC - Fase 1: Server Flask

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

### PoC - Fase 2: Embedding nel Template Email

```html
<!-- Inserire nel template HTML della email di phishing -->
<img src="http://192.168.0.110:8080/img/user001.gif"
     width="1" height="1" style="display:none" alt="" />
```

### PoC - Fase 3: Risultato

```Bash
python3 tracker.py
```

```
 * Running on http://0.0.0.0:8080

[*] Email opened by user001: IP 192.168.0.120              <-- SE-015
[*] Email opened by user003: IP 192.168.0.122
[*] Email opened by user001: IP 192.168.0.120              <-- seconda apertura (re-read)
```

```
# logs/opens.json
{"timestamp": "2026-03-15T10:12:00", "tracking_id": "user001", "ip": "192.168.0.120", "user_agent": "Mozilla/5.0 Outlook/16.0"}
{"timestamp": "2026-03-15T10:15:30", "tracking_id": "user003", "ip": "192.168.0.122", "user_agent": "Mozilla/5.0 Outlook/16.0"}
```

### Remediation

- **Azione immediata:** N/A (finding informativo, nessun impatto diretto)
- **Azione strutturale:** configurazione client email per blocco caricamento immagini esterne di default (Outlook: `File > Options > Trust Center > Automatic Download > Don't download pictures`); email gateway con proxy di immagini che anonimizza l'IP dell'utente (Google Workspace Image Proxy, Apple Mail Privacy Protection)
- **Verifica:** apertura email di test con tracking pixel - il server non deve ricevere la richiesta se le immagini esterne sono bloccate

---

## Esperienza di Laboratorio

Il test e stato condotto con Outlook su Windows 10 VM configurato con impostazioni di default (caricamento immagini abilitato). Il tracking ha funzionato immediatamente: l'apertura dell'email ha generato la richiesta HTTP GET verso il server Flask.

Un aspetto importante emerso dal test: Outlook in modalita "preview pane" carica le immagini anche senza che l'utente apra esplicitamente l'email. Questo significa che il tracking pixel registra un "open" anche quando l'utente scorre semplicemente la casella di posta. Per campagne professionali, e importante distinguere tra "preview" (User-Agent contiene "Outlook") e "browser click" (User-Agent contiene "Chrome/Firefox") per metriche accurate.

---

## Analisi Teorica: Limiti del Tracking Pixel

Il tracking pixel ha tre limitazioni principali:

1. **Client con immagini bloccate:** Outlook per macOS, Thunderbird, e Apple Mail (con Privacy Protection abilitato) bloccano il caricamento di immagini esterne di default, rendendo il tracking pixel inefficace.

2. **Proxy di immagini:** Google Workspace e Apple Mail Privacy Protection proxano le richieste di immagini attraverso i propri server, mascherando l'IP reale dell'utente. Il server vede l'IP del proxy Google/Apple, non dell'utente.

3. **Falsi positivi:** scanner email automatici (sandbox, antivirus) possono caricare le immagini durante l'analisi pre-delivery, generando "open" falsi prima ancora che l'email raggiunga la casella del destinatario.

Nonostante queste limitazioni, il tracking pixel resta lo standard de facto per misurare l'email open rate perche non esiste un'alternativa piu affidabile che non richieda interazione attiva dell'utente (come il click su un link).

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Resource Development | Stage Capabilities: Upload Malware | `T1608.001` | Deploy del server tracking pixel su infrastruttura attaccante |
| Discovery | System Information Discovery | `T1082` | Raccolta IP, User-Agent e geolocalizzazione della vittima (SE-015) |
| Reconnaissance | Active Scanning: Scanning IP Blocks | `T1595.001` | Identificazione IP attivi dei destinatari tramite tracking |

---

> **Nota:** Il server tracking e stato testato esclusivamente in ambiente lab. Nessun tracking pixel e stato inviato a indirizzi email reali.
