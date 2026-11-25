> **English** | [Italiano](README.md)

# XXE - XML external entity injection

> - **Phase:** Web Exploitation - OWASP A05:2021 Security Misconfiguration / Injection (insecure XML parsing)
> - **Visibility:** Medium - anomalous XML requests to the endpoint; out-of-band variants generate outbound traffic from the server to the attacker
> - **Prerequisites:** an endpoint that accepts and processes XML input (SOAP/REST API, XML/DOCX/SVG file upload, SAML) with a parser that resolves external entities
> - **Nature of the document:** methodology. Illustrative payloads (OWASP educational form), no fabricated Finding ID (next `WEB-016`, to assign in a lab).

- Objective: exploit a misconfigured XML parser to read local files on the server, perform SSRF toward internal services, or cause denial of service, by defining external entities in the XML document.

---

## Executive summary

XXE exploits a legitimate but dangerous feature of the XML standard: external entities, which allow a
document to include content from an external source (a file, a URL). If the application passes the user's XML
input to a parser that resolves these entities without disabling them, an attacker can define an entity that
points to a server file (`file:///etc/passwd`) or to an internal service (`http://169.254.169.254/` for
cloud metadata), and have the content returned in the application's response (in-band XXE) or exfiltrate it
to their own server (out-of-band XXE, when the response is not visible).

The main impacts are: arbitrary file reading (configurations, keys, `/etc/passwd`), SSRF toward internal
infrastructure and cloud metadata, and denial of service (e.g., "billion laughs"). It is an often
underestimated vector because it is hidden in non-obvious features: Office/SVG document uploads, SAML
endpoints, old SOAP APIs.

## Operational context (why, before how)

XXE is sought wherever the application accepts XML, even indirectly. The DOCX, XLSX and SVG formats are ZIPs
containing XML: an "image" SVG or "document" upload can be an XXE vector. The operational decision is to
understand whether the response reflects the parsed content (in-band, simpler) or not (the out-of-band
variant with a controlled external server is needed). You first test with a harmless entity to confirm the
parser resolves them, then target sensitive files or services.

## Execution / commands

### Phase 1 - confirm the parser resolves entities

Send an XML with an internal entity and check whether it is expanded in the response:

```xml
<?xml version="1.0"?>
<!DOCTYPE test [ <!ENTITY probe "XXE-OK"> ]>
<data>&probe;</data>
```

If the response contains `XXE-OK`, the parser expands entities: the target is a candidate for XXE.

### Phase 2 - reading local files (in-band)

External entity pointing to a server file (the canonical OWASP educational form):

```xml
<?xml version="1.0"?>
<!DOCTYPE data [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<data>&xxe;</data>
```

Illustrative output (representative, in the app's response):

```
root:x:0:0:root:/root:/bin/bash
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin   <-- reading /etc/passwd via XXE
```

### Phase 3 - SSRF toward cloud metadata or internal services

```xml
<!DOCTYPE data [ <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/"> ]>
```

### Out-of-band variant (when the response does not show the content)

When the app does not reflect the entity, you use an external DTD hosted on a controlled server that
exfiltrates the file via an outbound request (the content is captured in your server's logs). This is the
natural link with [SSRF](../../05-api-security/README.en.md) and with cloud-metadata attacks.

## Analysis of results

Reading `/etc/passwd` confirms XXE with arbitrary file reading: from here you target high-value files
(`/etc/shadow` if the process is privileged, app configuration files with DB credentials, private keys,
tokens). If the SSRF variant reaches the cloud metadata (169.254.169.254), the impact rises to the theft of
temporary IAM credentials. The real severity, in a lab, ranges from `High` (reading sensitive files) to
`Critical` (SSRF to cloud metadata with credentials, or RCE in specific scenarios). A parser that does not
expand entities (Phase 1 test negative) closes the vector.

### Theoretical analysis

XXE arises from the combination of two properties of the XML standard (DTD): the ability to define entities
and the ability to resolve them from external sources (`SYSTEM`). The problem is that many parsers, for
backward compatibility, resolve external entities by default. It is a case of confusion between data and
instructions: the user's input (which should be data only) contains directives (the entity definition) that
the parser executes. The countermeasure is structural and definitive: disable DTD/external-entity resolution
in the parser (secure-by-default), because the vast majority of applications do not need it. It links to the
general injection theme [Su & Wassermann 2006]: trusting input as if it were code.

## Remediation (blue team)

**Detection (WAF/SIEM).**
- Requests containing `<!DOCTYPE`, `<!ENTITY`, or `SYSTEM`/`PUBLIC` references in the XML body.
- Outbound traffic from the web server toward unexpected destinations (a sign of out-of-band XXE or SSRF).
- The web process accessing sensitive files (`/etc/passwd`, config) or 169.254.169.254.

**Hardening (secure coding).**
- Disable external-entity and DTD resolution in the XML parser (the primary countermeasure). In Java:
  `setFeature("http://apache.org/xml/features/disallow-doctype-decl", true)`; equivalents in .NET, PHP,
  Python (`defusedxml`).
- Prefer less dangerous data formats (JSON) where possible.
- Validate and limit upload formats; treat DOCX/SVG as potential XML vectors.
- Segment the network to prevent the web server from reaching cloud metadata (IMDSv2 with hop limit).

---

## Real-World scenario: Post-Exploitation projection

> Applies to the "reading sensitive files / SSRF to metadata" outcome (severity High/Critical).

### Attacker perspective (red team)

**Starting point:** an endpoint that processes XML with a vulnerable parser (confirmed in Phase 1).

**Immediate next step:** read the application's configuration files to extract credentials (DB, API), or SSRF
toward the cloud metadata.

**Projected Kill Chain:**

```
Vulnerable XML endpoint
        |
        v
XXE -> read app config (DB credentials, keys)
   or
XXE + SSRF -> 169.254.169.254 -> temporary IAM credentials
        |
        v
Access to the DB / cloud with the obtained credentials
        |
        v
Data exfiltration / cloud escalation (see module 10)
```

**Potential impact:** theft of application or cloud credentials starting from an XML-parsing feature. In the
SSRF-metadata case, the impact extends to the cloud account.

**Typical monetization vectors:** exfiltration and resale of the data; abuse of cloud credentials for
cryptomining or further compromise.

### Defender perspective (blue team)

**Detection:** XML payloads with DOCTYPE/ENTITY; anomalous outbound traffic from the web server; access to
sensitive files or metadata.

**Indicators of Compromise (IOC):**
- Request bodies with `<!ENTITY ... SYSTEM ...>`.
- Connections from the web server toward 169.254.169.254 or an unexpected external host.
- Reading of `/etc/passwd` or configuration files by the web process.

**Containment:** block the endpoint or the pattern via WAF; rotate potentially read credentials; verify
access to the metadata.

**Eradication and hardening:** disable DTD/external entities in the parser; IMDSv2; segmentation; code review
of the points that parse XML.

**Defensive lesson:** XXE is a parser-configuration defect, not strictly an application defect. The definitive
defense is a secure-by-default parser: no downstream control replaces disabling external entities.

---

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `Burp Suite` | proxy/scanner | web - active | intercepts and modifies xml requests; extensions for xxe and oob collaborator |
| `curl` | http client | cli - active | manual sending of xml payloads to the endpoint |
| `XXEinjector` | exploit tool | cli - active | automation of xxe, including out-of-band variants |
| `defusedxml` | python library | secure coding | secure xml parser for remediation (blue team) |

## Methodology notes

In a real lab (e.g., an app with an XML endpoint or an OWASP WebGoat target) the data to document as a
finding: confirmation of entity expansion, the file read and any successful SSRF. The integrity rules apply:
real outputs, never fabricated. The payloads shown are in the OWASP educational form.

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | exploitation of the vulnerable xml parser on an exposed endpoint. |
| discovery | file and directory discovery | `T1083` | reading of local server files via the external entity. |
| credential access | unsecured credentials: credentials in files | `T1552.001` | extraction of credentials from configuration files read via xxe. |

---

## Correlations with other findings

| source | this technique | effect |
| :--- | :--- | :--- |
| [02-web-recon](../../02-web-recon (Enumeration)/README.en.md) | xxe | enumeration identifies xml/soap endpoints and upload features |
| xxe (ssrf to metadata) | [10-cloud-security](../../../10-cloud-security (Cloud&Modern)/README.en.md) | the obtained iam credentials open the way to cloud escalation |
| xxe | [secure-coding-lab](../../06-secure-coding-lab (Defense)/README.en.md) | the remediation (secure parser) links to the secure-coding lab |

---

> **Note:** Educational and methodology content. The techniques must be executed only on owned applications or with explicit authorization. The payloads are illustrative and do not come from real or third-party systems.
