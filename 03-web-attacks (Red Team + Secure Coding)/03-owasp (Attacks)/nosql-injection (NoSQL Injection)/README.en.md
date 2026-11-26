> **English** | [Italiano](README.md)

# NoSQL injection

> - **Phase:** Web exploitation - OWASP A03:2021 Injection (NoSQL query built with unsanitized input)
> - **Visibility:** Medium - requests with NoSQL operators in the parameters; blind extraction generates many requests with boolean differences or delays
> - **Prerequisites:** an application that builds a query toward a NoSQL database (typically MongoDB) inserting user input without sanitization/type-check
> - **Nature of the document:** methodology + practical payloads for a lab environment. Example values; no fabricated Finding ID (next `WEB-016`, to assign in lab).

- Objective: manipulate a NoSQL query by injecting operators (`$ne`, `$gt`, `$regex`, `$where`) to bypass authentication, extract data or, with `$where`, execute server-side code.

---

## Executive summary

NoSQL injection targets non-relational databases (MongoDB first of all). Unlike SQLi, you do not break a query
string but abuse the fact that many frameworks accept **data structures** (objects/arrays) as input, not just
strings: a parameter expected as a string can become an object with a MongoDB operator (`{"$ne": null}`),
altering the query logic. The main impacts are authentication bypass, blind data extraction and, when the app
uses the `$where` operator (which evaluates server-side JavaScript), code execution.

The typical severity is `High` (auth bypass + data extraction); it rises to `Critical` when `$where` leads to
RCE.

## Operational context (why, before how)

You look where the app receives parameters that end up in a MongoDB query: login, filters, searches. The key
point is **type juggling**: if the app reads `req.body.user` without forcing it to a string, the attacker can
send an object. In JSON you inject the operator directly; in URL-encoded forms you use the bracket notation
(`param[$ne]=value`) that many parsers convert to an object. The operational decision is to distinguish direct
bypass, blind extraction (boolean with `$regex`) and `$where` (RCE).

## Execution / commands

### Authentication bypass

```
# JSON body: the password becomes an object with $ne (not null) -> always true
{"username": "admin", "password": {"$ne": null}}

# URL-encoded form variant (bracket notation, converted to an object by many parsers)
username=admin&password[$ne]=

# Select the first user without knowing the username
username[$ne]=&password[$ne]=
```

### Blind (boolean) extraction with $regex

```
# Confirm character by character the password/field of 'admin'
{"username": "admin", "password": {"$regex": "^a"}}   -> "login ok" response if it starts with 'a'
{"username": "admin", "password": {"$regex": "^ad"}}  -> ... up to the full string
```

### Useful operators and $where (RCE)

```
{"age": {"$gt": ""}}                 # comparisons to filter/extract
{"$where": "sleep(5000)"}            # time-based: confirms server-side JS execution (blind)
{"$where": "this.password.length>8"} # JavaScript evaluation over the documents
```

Illustrative output (representative):

```
# with password[$ne]= the login succeeds without a valid password
HTTP/1.1 302 Found   Location: /dashboard   <-- authentication bypassed
```

## Analysis of results

The bypass confirms that the input is not constrained to a string (type juggling). The `$regex` extraction
recovers sensitive fields character by character; a `$where` that introduces a measurable delay demonstrates
server-side JavaScript execution (RCE, severity `Critical`). If the app enforces types (cast to string) and
disables `$where`, the vector is closed.

### Theoretical analysis

It is the data/instructions problem [Su & Wassermann 2006] in the "data structure" variant: the app expects a
scalar value but the protocol (JSON/bracket) allows passing an operator, which the driver interprets as logic.
The countermeasure is **type enforcement**: validate that the input is of the expected type (string, not
object), use parameterized queries/ODM with a schema, and disable server-side JavaScript execution (`$where`,
`mapReduce`).

## Remediation (blue team)

**Detection (WAF/SIEM).**
- Parameters containing NoSQL operators (`$ne`, `$gt`, `$regex`, `$where`) or bracket notation (`param[$...]`).
- Request bodies where a field expected to be scalar arrives as an object/array.
- Queries with `$where`/`mapReduce` originating from user input.

**Hardening (secure coding).**
- Force the input type (cast to string) before building the query; validate with a schema (Mongoose).
- Never pass raw user objects to the driver; sanitize keys that start with `$`.
- Disable server-side JavaScript execution (`$where`, `mapReduce`) if not needed.

---

## Real-world scenario: post-exploitation projection

> Applies to the "auth bypass / extraction / RCE via $where" outcome (severity High/Critical).

### Attacker perspective (red team)

**Starting point:** an endpoint with a MongoDB backend and untyped input.

**Immediate next step:** authentication bypass as admin, then blind data extraction or RCE with `$where`.

**Projected kill chain:**

```
NoSQL injection (type juggling)
        |
        v
Auth bypass as admin / blind extraction of credentials
        |
        v
$where -> server-side JavaScript execution (RCE) where supported
        |
        v
Access to the data / compromise of the application server
```

**Potential impact:** from unauthorized access to exfiltration of the entire collection; with `$where`, code
execution.

**Typical monetization vectors:** data theft and resale; access to restricted areas; pivot on the server.

### Defender perspective (blue team)

**Detection:** `$` operators in parameters; scalar fields received as objects; use of `$where`.

**Indicators of Compromise (IoC):** requests with `[$ne]`/`[$regex]`; spikes of nearly identical requests
(blind extraction); `$where` queries with functions like `sleep`.

**Containment:** block the pattern via WAF; rotate the exposed credentials; investigate the accesses.

**Eradication and hardening:** type enforcement, schema validation, disabling of `$where`.

**Defensive lesson:** NoSQL injection shows that "no concatenated strings" is not enough: if the input can be a
data structure, the type must be constrained. The defense is type enforcement, not character filtering.

---

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `Burp Suite` | proxy/scanner | web - active | modifies parameters into objects/operators; tests type juggling |
| `NoSQLMap` | exploit tool | cli - active | automation of nosql injection (mongodb): bypass, extraction, `$where` |
| `nosqli` | scanner | cli - active | automated detection of nosql injection |

## Methodology notes

In a real lab (a Node/Express + MongoDB app or a didactic target) the data to document: the successful bypass,
the fields extracted via `$regex` and any RCE with `$where`. Real credentials must be redacted in the report.

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | exploitation of the unsanitized nosql query on an exposed application. |
| collection | data from information repositories | `T1213` | extraction of data from the nosql database via injection operators. |
| execution | command and scripting interpreter | `T1059` | execution of server-side javascript via the `$where` operator. |

---

## Links to other findings

| source | this technique | effect |
| :--- | :--- | :--- |
| [sql injection](<../sql-injection (SQLi)/README.en.md>) | nosql injection | same class (injection), nosql engine; bypass via type juggling |
| [02-web-recon](<../../02-web-recon (Enumeration)/README.en.md>) | nosql injection | enumeration identifies stacks with a nosql (mongodb) backend |
| nosql injection | [secure-coding-lab](<../../06-secure-coding-lab (Defense)/README.en.md>) | the remediation (type enforcement, schema) links to secure coding |

---

> **Note:** Educational content. The payloads are functional and must be executed only on owned applications or with explicit authorization, in a lab environment. Outputs are illustrative.
