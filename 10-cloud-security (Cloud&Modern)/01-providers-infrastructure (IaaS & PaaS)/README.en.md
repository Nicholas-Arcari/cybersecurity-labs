> **English** | [Italiano](README.md)

# 01 - Providers Infrastructure (IaaS & PaaS)

> - **Phase:** Cloud Security - IaaS/PaaS providers (AWS, Azure, GCP)
> - **Category:** Offensive + Defensive - identity as the perimeter
> - **Prerequisites:** Test account/tenant/project on the providers; official CLIs; for the offensive, credentials or compromised resources
> - **Output:** Findings CLOUD-001..004; understanding of the attack surface of the three major providers and the countermeasures

---

## Introduction

This section covers the three dominant cloud providers - AWS, Azure, GCP - united by a principle the module makes central: **in the cloud, identity is the new perimeter**. There is no longer a border firewall; every service is an API endpoint and the only access control is identity (IAM on AWS, Entra ID on Azure, Service Accounts on GCP). Whoever holds a valid credential is "inside", and what they can do depends on the permissions - almost always misconfigured.

The reference framework is the **Shared Responsibility Model**: the provider protects the security *of* the cloud (hardware, physical network, hypervisor), the customer the security *in* the cloud (data, configurations, accesses). The vast majority of compromises do not derive from provider bugs but from customer-side misconfigurations - over-privileged identities, exposed storage, excessive permissions.

The three providers share the same attack pattern declined differently:

1. **AWS (CLOUD-001, CLOUD-002):** IAM enumeration and privilege escalation; exposed S3 buckets. The most widespread and most attacked provider.

2. **Azure (CLOUD-003):** enumeration of Entra ID (the cloud AD, with AzureHound) and managed identity abuse via IMDS.

3. **GCP (CLOUD-004):** theft of the service account tokens via the metadata service, often through an SSRF.

The common thread is cross-cutting: the non-human identities tied to the resources (IAM role, managed identity, service account) are convenient but dangerous if over-privileged, and their token is always one step away from the metadata service. Whoever learns the pattern on one provider finds it on the others.

---

## Folder Structure

```
01-providers-infrastructure (IaaS & PaaS)/
+-- README.md                          # this file: CLOUD-001..004 registry
|
+-- AWS (Amazon Web Services)/         # CLOUD-001 (IAM), CLOUD-002 (S3)
+-- Azure/                             # CLOUD-003 (Entra ID + managed identity)
+-- GCP (Google Cloud Platform)/       # CLOUD-004 (metadata SSRF + service account)
```

---

## Recommended Operational Flow

```
[INPUT] Compromised credential / compromised resource / SSRF web app
         |
         v
[1] Obtain an identity
     +-- AWS: IAM credential (leak)      -> AWS/IAM-enumeration/
     +-- Azure: managed identity (IMDS)  -> Azure/
     +-- GCP: service account (metadata) -> GCP/
              |
              v
[2] Enumerate the permissions and search for escalation
     +-- least privilege violated -> path toward admin/owner
              |
              v
[3] Action on objectives
     +-- data access (storage, DB), persistence, exfiltration
              |
              v
[OUTPUT] Environment compromise -> defense: least privilege + audit (Tooling/)
```

---

## Reference Tools

| Tool | Provider | Type | Main use case |
| :--- | :--- | :--- | :--- |
| `Pacu` | AWS | Offensive | AWS exploitation framework |
| `AzureHound` / `MicroBurst` | Azure | Offensive | Attack path and Entra ID enumeration |
| `gcloud` + metadata | GCP | Offensive | Service account token theft |
| `ScoutSuite` | Multi | Defensive | Multi-cloud audit of the configuration |
| `Prowler` | AWS/Azure/GCP | Defensive | Security and compliance checks |

> **Recommended modern tool:** `ScoutSuite` for the unified multi-cloud audit; by provider, `Pacu` (AWS), `AzureHound` (Azure), `Prowler` (cross-cutting). Detail in `../Tooling/`.

---

## Finding Registry - Providers Infrastructure

| ID | Description | Severity | Subfolder |
| :--- | :--- | :---: | :--- |
| `CLOUD-001` | AWS IAM enumeration + privilege escalation to admin | `Critical` | `AWS/IAM-enumeration/` |
| `CLOUD-002` | Exposed/misconfigured AWS S3 bucket: data exfiltration | `High` | `AWS/S3-buckets-attacks/` |
| `CLOUD-003` | Azure: managed identity abuse (IMDS) + Entra ID enumeration | `High` | `Azure/` |
| `CLOUD-004` | GCP: service account token theft via metadata/SSRF | `High` | `GCP/` |

---

## MITRE ATT&CK Mapping - Aggregated

> Reference: MITRE ATT&CK for Cloud (IaaS).

| Tactic | Technique | MITRE ID | Related Finding |
| :--- | :--- | :--- | :--- |
| Discovery | Cloud Infrastructure Discovery | `T1580` | CLOUD-001, CLOUD-003, CLOUD-004 |
| Privilege Escalation | Valid Accounts: Cloud Accounts | `T1078.004` | CLOUD-001, CLOUD-003, CLOUD-004 |
| Credential Access | Steal Application Access Token | `T1528` | CLOUD-003, CLOUD-004 |
| Credential Access | Unsecured Credentials: Cloud Instance Metadata API | `T1552.005` | CLOUD-004 |
| Collection | Data from Cloud Storage | `T1530` | CLOUD-002 |
| Persistence | Account Manipulation: Additional Cloud Credentials | `T1098.001` | CLOUD-001 |

---

> **Note:** All documented activities were conducted on lab accounts/tenants/projects owned by the author. Security testing on third-party cloud environments requires explicit authorization and compliance with the provider's terms. Techniques are documented for educational and authorized security assessment purposes.
