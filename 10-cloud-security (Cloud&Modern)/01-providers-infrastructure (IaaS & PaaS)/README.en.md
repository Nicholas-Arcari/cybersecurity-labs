> **English** | [Italiano](README.md)

# 01 - Providers infrastructure (IaaS & PaaS)

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

## Folder structure

```
01-providers-infrastructure (IaaS & PaaS)/
+-- README.md                          # this file: CLOUD-001..004 registry
|
+-- AWS (Amazon Web Services)/         # CLOUD-001 (IAM), CLOUD-002 (S3)
+-- Azure/                             # CLOUD-003 (Entra ID + managed identity)
+-- GCP (Google Cloud Platform)/       # CLOUD-004 (metadata SSRF + service account)
```

---

## Recommended operational flow

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

## Reference tools

| tool | provider | type | main use case |
| :--- | :--- | :--- | :--- |
| `Pacu` | aws | offensive | aws exploitation framework |
| `AzureHound` / `MicroBurst` | azure | offensive | attack path and entra id enumeration |
| `gcloud` + metadata | gcp | offensive | service account token theft |
| `ScoutSuite` | multi | defensive | multi-cloud audit of the configuration |
| `Prowler` | aws/azure/gcp | defensive | security and compliance checks |

> **Recommended modern tool:** `ScoutSuite` for the unified multi-cloud audit; by provider, `Pacu` (AWS), `AzureHound` (Azure), `Prowler` (cross-cutting). Detail in `../Tooling/`.

---

## Finding registry - providers infrastructure

| id | description | severity | subfolder |
| :--- | :--- | :---: | :--- |
| `CLOUD-001` | aws iam enumeration + privilege escalation to admin | `Critical` | `AWS/IAM-enumeration/` |
| `CLOUD-002` | exposed/misconfigured aws s3 bucket: data exfiltration | `High` | `AWS/S3-buckets-attacks/` |
| `CLOUD-003` | azure: managed identity abuse (imds) + entra id enumeration | `High` | `Azure/` |
| `CLOUD-004` | gcp: service account token theft via metadata/ssrf | `High` | `GCP/` |

---

## MITRE ATT&CK mapping - aggregated

> Reference: MITRE ATT&CK for Cloud (IaaS).

| tactic | technique | mitre id | related finding |
| :--- | :--- | :--- | :--- |
| discovery | cloud infrastructure discovery | `T1580` | CLOUD-001, CLOUD-003, CLOUD-004 |
| privilege escalation | valid accounts: cloud accounts | `T1078.004` | CLOUD-001, CLOUD-003, CLOUD-004 |
| credential access | steal application access token | `T1528` | CLOUD-003, CLOUD-004 |
| credential access | unsecured credentials: cloud instance metadata api | `T1552.005` | CLOUD-004 |
| collection | data from cloud storage | `T1530` | CLOUD-002 |
| persistence | account manipulation: additional cloud credentials | `T1098.001` | CLOUD-001 |

---

> **Note:** All documented activities were conducted on lab accounts/tenants/projects owned by the author. Security testing on third-party cloud environments requires explicit authorization and compliance with the provider's terms. Techniques are documented for educational and authorized security assessment purposes.
