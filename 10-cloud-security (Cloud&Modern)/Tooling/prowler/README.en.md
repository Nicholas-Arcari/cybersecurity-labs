> **English** | [Italiano](README.md)

# Prowler - Cloud Hardening and Compliance

> - **Phase:** Cloud Security - Audit & Compliance (Defense)
> - **Category:** Defensive - the de facto standard for cloud hardening
> - **Prerequisites:** Credentials with read-only/audit permissions on the account; Prowler
> - **Output:** Prioritized report of misconfigurations and non-conformities (CIS, NIST, GDPR, ...)

- **Main tool:** Prowler (multi-cloud: AWS, Azure, GCP)

---

## What It Is and What It Is For

`Prowler` is the de facto standard for cloud hardening and compliance: it runs hundreds of security checks on the account and produces a report of what is wrong, mapped to recognized frameworks (CIS Benchmark, NIST, GDPR, PCI-DSS, and MITRE ATT&CK). It is the defensive tool that answers the question "how secure is my cloud account?" with a concrete and prioritized list of corrections.

Unlike the offensive scanners (Pacu), which look for a specific attack path, Prowler adopts a broad and systematic view: it verifies every service against the best practices, from public buckets to permissive IAM policies, from disabled logging to missing encryption. It is the audit, hardening cycle applied to the cloud, with Prowler as an objective measure - the cloud equivalent of Lynis/kube-bench.

---

## Usage

```Bash
# Complete audit of an AWS account against the CIS Benchmark
prowler aws --compliance cis_2.0_aws
```

```
FAIL  iam_root_mfa_enabled           Root account without MFA        <-- critical
FAIL  s3_bucket_public_access        Bucket 'data' public            <-- (related CLOUD-002)
FAIL  iam_policy_no_admin_priv       Policy with admin privileges
PASS  cloudtrail_enabled             CloudTrail active

== 142 PASS, 23 FAIL, 8 WARN -> HTML/JSON report generated
```

```Bash
# Prowler also supports Azure and GCP
prowler azure
prowler gcp
```

---

## When to Use It in the Flow

- **Periodic audit of the account:** run it regularly to measure and maintain the security posture
- **Before an incident:** closing the priority FAILs (root without MFA, public buckets, IAM admin) makes the account resilient to credential leaks
- **Compliance:** the mapping to CIS/NIST/GDPR produces the conformity evidence required in regulated contexts
- **Complementary to Pacu:** Prowler systematically finds what Pacu would exploit specifically

---

## Related Tools

| Tool | Role | Relationship |
| :--- | :--- | :--- |
| `Prowler` | Audit/compliance | This tool (defensive) |
| `ScoutSuite` | Multi-cloud audit | Complementary big-picture (`../scoutsuite/`) |
| `Pacu` | Exploitation | The offensive counterpart (`../pacu/`) |
| `Trivy` | Container/IaC scan | Covers containers and IaC, not the cloud account |

> **Recommended modern tool:** `Prowler` for the in-depth audit and the compliance (mapping to frameworks), `ScoutSuite` for the quick big picture. The two are complementary: Prowler for the depth and the conformity evidence, ScoutSuite for the multi-cloud overview.

---

## MITRE ATT&CK Mapping

| Tactic (prevented) | Technique | MITRE ID | Role of the control |
| :--- | :--- | :--- | :--- |
| Privilege Escalation | Valid Accounts: Cloud Accounts | `T1078.004` | Detects the IAM policies that allow privesc |
| Collection | Data from Cloud Storage | `T1530` | Detects the public/unencrypted buckets |
| Defense Evasion | Impair Defenses | `T1562` | Detects disabled logging/monitoring |

| Defensive countermeasure (D3FEND) | D3FEND ID | Application |
| :--- | :--- | :--- |
| Configuration Inventory | `D3-CI` | Inventory and verification of the cloud configuration |
| Platform Hardening | `D3-PH` | Hardening guided by the conformity checks |

---

> **Note:** Prowler is a non-intrusive defensive tool, to be run on accounts owned or with authorization. Documented for educational and defensive purposes in an authorized context.
