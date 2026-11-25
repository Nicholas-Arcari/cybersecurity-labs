> **English** | [Italiano](README.md)

# AWS (Amazon web services) - security and attack

> - **Phase:** Cloud Security - AWS (IaaS & PaaS)
> - **Category:** Offensive + Defensive - identity and storage at the center
> - **Prerequisites:** Test AWS account; AWS CLI; for the offensive, compromised credentials (leak/SSRF/secret); for the defensive, audit access
> - **Output:** Findings CLOUD-001..002; understanding of the AWS attack surface and the countermeasures

---

## Introduction

AWS is the dominant cloud provider and, consequently, the most attacked platform. Its security revolves around a principle this chapter makes central: **in the cloud, identity is the new perimeter**. There is no border firewall to get past; whoever holds a valid credential is "inside", and what they can do depends on the IAM permissions. The vast majority of AWS compromises do not derive from Amazon bugs but from customer-side misconfigurations - consistent with the **Shared Responsibility Model**, which assigns to AWS the security *of* the cloud (hardware, network, hypervisor) and to the customer the security *in* the cloud (data, accesses, configurations).

The chapter covers the two most relevant AWS attack surfaces:

1. **IAM Enumeration & Privilege Escalation (CLOUD-001):** the attack on identity. From a limited credential, the enumeration of the permissions and the search for a privilege escalation chain toward administrative privileges. It is the entry point and the primary defensive focus (least privilege, boundaries, audit).

2. **S3 Bucket Attacks (CLOUD-002):** the attack on storage. Misconfigured buckets (public or with permissive ACLs) that expose sensitive data - one of the most common causes of cloud data breaches.

The two findings are linked: an exposed bucket often contains credentials that feed the IAM enumeration, and a compromised IAM gives access to all the buckets. The real AWS breach pattern is almost always a combination of identity and storage misconfigurations.

---

## Folder structure

```
AWS (Amazon Web Services)/
+-- README.md              # this file: CLOUD-001..002 registry, AWS principles
|
+-- IAM-enumeration/       # CLOUD-001: permission enumeration + privilege escalation
+-- S3-buckets-attacks/    # CLOUD-002: exposed buckets and misconfigurations
```

---

## Recommended operational flow

```
[INPUT] Compromised AWS credential or bucket name (OSINT)
         |
         v
[1] Identity (IAM-enumeration/)
     +-- who am I? what can I do? -> search for privesc path -> admin (CLOUD-001)
              |
              v
[2] Data (S3-buckets-attacks/)
     +-- exposed buckets -> exfiltration; credentials in buckets -> IAM pivot (CLOUD-002)
              |
              v
[3] Consolidation
     +-- persistence (new keys/roles), access to the datastores, exfiltration
              |
              v
[OUTPUT] Account compromise -> defense: least privilege + Block Public Access + audit
```

---

## Reference tools

| tool | type | role | main use case |
| :--- | :--- | :--- | :--- |
| `aws-cli` | cloud cli | official | interaction with the aws apis |
| `Pacu` | exploitation framework | offensive | enum, privesc, persistence on aws |
| `enumerate-iam` / `cloud_enum` | recon | offensive | permission and bucket enumeration |
| `Prowler` / `ScoutSuite` | audit | defensive | detection of misconfig and privesc paths |
| `PMapper` | iam graph | defensive | graph analysis of the iam escalations |

> **Recommended modern tool:** `Pacu` (offensive) and `Prowler`/`ScoutSuite` (defensive) cover the attack/defense symmetry on AWS. See `../../../Tooling/` for the detail of each.

---

## Finding registry - AWS

| id | description | severity | subfolder |
| :--- | :--- | :---: | :--- |
| `CLOUD-001` | iam enumeration + privilege escalation from a limited credential to admin | `Critical` | `IAM-enumeration/` |
| `CLOUD-002` | exposed/misconfigured s3 bucket: data exfiltration or tampering | `High` | `S3-buckets-attacks/` |

---

## MITRE ATT&CK mapping - aggregated

> Reference: MITRE ATT&CK for Cloud (IaaS).

| tactic | technique | mitre id | related finding |
| :--- | :--- | :--- | :--- |
| discovery | cloud infrastructure discovery | `T1580` | CLOUD-001 |
| privilege escalation | valid accounts: cloud accounts | `T1078.004` | CLOUD-001 |
| persistence | account manipulation: additional cloud credentials | `T1098.001` | CLOUD-001 |
| collection | data from cloud storage | `T1530` | CLOUD-002 |
| discovery | cloud storage object discovery | `T1619` | CLOUD-002 |

---

> **Note:** All documented activities were conducted on an AWS lab account owned by the author. Security testing on third-party cloud accounts requires explicit authorization and compliance with the provider's terms. Techniques are documented for educational and authorized security assessment purposes.
