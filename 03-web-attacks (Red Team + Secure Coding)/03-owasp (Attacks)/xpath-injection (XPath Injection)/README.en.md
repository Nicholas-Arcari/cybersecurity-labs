> **English** | [Italiano](README.md)

# XPath Injection

> - **Phase:** Web Exploitation - OWASP A03:2021 Injection (XPath query built with unsanitized input)
> - **Visibility:** Medium - anomalous queries toward the XML/XPath parser; blind extraction generates many requests with behavioral differences
> - **Prerequisites:** an application that queries an XML document with XPath, building the query from user input (login or lookup with an XML backend)
> - **Nature of the document:** methodology. Illustrative payloads (OWASP didactic form), no fabricated Finding ID (next `WEB-016`, to assign in lab).

- Objective: manipulate an XPath query to bypass authentication and extract the entire content of the underlying XML document, exploiting the absence of access control typical of XPath.

---

## Executive Summary

XPath Injection is the cousin of SQL Injection for applications that use **XML documents** as the data source
and **XPath** as the query language. When an app builds an XPath expression by concatenating user input
(classically in a login form that looks up the user in an XML file), an attacker can inject the XPath syntax and
alter the query's logic.

Compared to SQLi and LDAP Injection, XPath has a characteristic that makes it particularly insidious: **XPath has
no access control model**. In a database there are per-table/column permissions; in an XML document queried via
XPath, once the injection is obtained you can read the **entire document**, not just the intended node. The main
impacts are authentication bypass and full extraction of the XML data (often credentials and user profiles). The
typical severity is `High`.

## Operational context (why, before how)

XPath Injection is encountered where the application uses XML as a "small database": authentication, user lists,
configurations. The initial test is analogous to SQLi: you inject an XPath metacharacter (a quote, a bracket) and
observe whether the query breaks or changes behavior. The next decision is between direct bypass (if the query
authenticates), cleartext extraction (if it reflects) or blind extraction (true/false behavioral differences), as
in [blind SQLi](<../sql-injection (SQLi)/README.en.md>).

## Execution / Commands

### Phase 1 - Confirm the vulnerability

A typical authentication XPath query has this form:

```
//user[username/text()='NAME' and password/text()='PASS']
```

You inject a quote into the username and check whether the query breaks (XPath error) or changes behavior: a sign
that the input reaches the expression without escape.

### Phase 2 - Authentication bypass (conceptual)

As in SQLi, you introduce an always-true condition (a tautology) that makes the password irrelevant. In minimal
didactic form:

```
Username: ' or '1'='1          <-- tautology: the condition becomes always true
# the unsanitized query returns the first user node -> authentication bypassed
```

### Phase 3 - Blind extraction of the entire document

In the absence of access control, you navigate the XML document one node/character at a time using XPath
functions (`substring()`, `string-length()`, `name()`) and the behavioral differences between true and false
conditions.

Illustrative output (representative, outcome of a test condition):

```
string-length(//user[1]/password) > 8  -> TRUE   <-- the first user's password is longer than 8 characters
```

Tools like `XCat` automate the blind extraction of the entire XML.

## Analysis of results

Authentication bypass grants access as an arbitrary user; blind extraction can exfiltrate the entire XML
document, including usernames and passwords if stored there. The real severity is `High` (bypass + full data
read); it rises toward `Critical` if the XML contains credentials reusable toward more important systems. If the
application uses precompiled XPath with variable binding (or escapes correctly), the vector is closed.

### Theoretical Analysis

XPath Injection is another instance of the data/instructions problem [Su & Wassermann 2006]. The theoretical
peculiarity is the absence of an authorization model in the language: XPath is designed to navigate a document
freely, so there is no concept of "a node the user cannot access". This amplifies the injection's impact compared
to SQLi, where database privileges can limit the damage. The countermeasure is structural: do not build the
expression by concatenation but use parameterized XPath (bound variables, a precompiled `XPathExpression` with
`XPathVariableResolver` in Java, `lxml` with variables in Python), plus input validation.

## Remediation (Blue Team)

**Detection (WAF/SIEM).**
- Input containing XPath metacharacters (quotes, `[`, `]`, `or`, `and`, functions like `substring`) in the
  parameters.
- XPath parser errors in the application logs.
- Anomalous volume of requests with small variations (sign of blind extraction).

**Hardening (secure coding).**
- Use parameterized XPath with variable binding, never string concatenation (the primary countermeasure).
- Validate and restrict the input (whitelist of allowed characters).
- Escape the XPath metacharacters when parameterization is not available.
- Evaluate whether XML is the appropriate backend: authentication data belongs better in a store with access
  control.

---

## Real-World Scenario: Post-Exploitation Projection

> Applies to the "auth bypass / full XML extraction" outcome (severity High/Critical).

### Attacker Perspective (Red Team)

**Starting point:** an application with XML/XPath-based authentication or lookup and unsanitized input.

**Immediate next step:** authentication bypass, then blind extraction of the entire XML document.

**Projected Kill Chain:**

```
XPath Injection on a login/lookup with an XML backend
        |
        v
Authentication bypass (tautology) + extraction of the entire document
        |
        v
Credentials and user profiles exfiltrated from the XML
        |
        v
Reuse of credentials toward other systems / access to sensitive data
```

**Potential impact:** unauthorized access and full exfiltration of the XML data store; escalation via credential
reuse when the XML stores passwords.

**Typical monetization vectors:** data theft and resale; access to restricted areas; credential reuse.

### Defender Perspective (Blue Team)

**Detection:** XPath metacharacters in the parameters; parser errors; blind extraction patterns.

**Indicators of Compromise (IOC):**
- Parameters with quotes, XPath logical operators or `substring`/`string-length` functions not expected.
- Sequences of nearly identical requests with differential responses.

**Containment:** block the pattern via WAF; rotate any credentials exposed in the XML.

**Eradication and hardening:** parameterized XPath; input validation; reassessment of the store for
authentication data.

**Defensive lesson:** XPath Injection reminds us that every query language concatenated with user input is
vulnerable to injection, and that the absence of access control in XPath makes extraction total: the defense is
separating data and code (parameterization) regardless of the engine.

---

## Reference tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `Burp Suite` | Proxy/scanner | Web - Active | Intercepts and modifies the parameters; fuzzing of XPath metacharacters |
| `XCat` | Exploit tool | CLI - Active | Automation of the blind extraction of an XML document via XPath injection |
| `lxml` (Python) | XML library | Secure coding | Parameterized XPath with variables for the remediation (Blue Team) |

## Methodology notes

In a real lab (e.g., an app with login on an XML file or a didactic target) the data to document as a finding:
the confirmation of the vulnerability, the bypass outcome and the portion of the document extracted. Any real
credentials extracted must be treated as sensitive data and redacted. The payloads shown are in the minimal
didactic form.

## MITRE ATT&CK mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Exploitation of the unsanitized XPath expression on an exposed application. |
| Collection | Data from Information Repositories | `T1213` | Extraction of the entire XML document (profiles, credentials) via XPath injection. |

---

## Links to other findings

| Source | This technique | Effect |
| :--- | :--- | :--- |
| [02-web-recon](<../../02-web-recon (Enumeration)/README.en.md>) | XPath Injection | enumeration identifies the features with an XML backend |
| [SQL Injection](<../sql-injection (SQLi)/README.en.md>) | XPath Injection | same class (injection), different query engine; XPath without access control |
| XPath Injection | [secure-coding-lab](<../../06-secure-coding-lab (Defense)/README.en.md>) | the remediation (parameterized XPath) links to the secure coding lab |

---

> **Note:** All described techniques are for educational and methodology-documentation purposes. Execution only on owned applications or with explicit authorization. The payloads are illustrative and do not come from real or third-party systems.
