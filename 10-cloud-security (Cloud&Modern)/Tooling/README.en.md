> **English** | [Italiano](README.md)

# Tooling - Cloud Security Tools

> - **Phase:** Cloud Security - Cross-cutting toolkit
> - **Category:** Tool reference (offensive and defensive)
> - **Prerequisites:** Credentials/access to the cloud environments to test or audit
> - **Output:** Reference guide to the cloud tools used cross-cuttingly in the module

---

## Introduction

This folder collects the "must-have" tools for cloud security, used cross-cuttingly in the module's sections. Unlike the thematic folders (which document findings and techniques), this is a reference guide to the tools: what they do, when to use them, how to integrate them into the workflow. It does not contain findings of its own - the tools are applied in the findings of the respective sections.

The tools divide by perspective, reflecting the dual nature of the module:

- **Offensive:** `Pacu` (AWS exploitation framework), `cloud-enum` (asset and bucket discovery). They simulate the attacker to find the weaknesses.
- **Defensive:** `Prowler` (hardening and compliance), `ScoutSuite` (multi-cloud audit). They verify the security posture to correct it before the attacker.

The symmetry is the central theme of cloud security: the same paths an offensive tool (Pacu) exploits, a defensive tool (Prowler/ScoutSuite) identifies and helps to close. Mastering both perspectives is what distinguishes a complete cloud security analyst.

---

## Folder Structure

```
Tooling/
+-- README.md          # this file: reference guide to the cloud tools
|
+-- cloud-enum/        # Recon: asset and bucket discovery (multi-cloud)
+-- pacu/              # Offensive: AWS exploitation framework
+-- prowler/           # Defensive: hardening and compliance (AWS/Azure/GCP)
+-- scoutsuite/        # Defensive: multi-cloud audit of the configuration
```

---

## When to Use Which Tool

```
[RECON]      cloud-enum   -> discovery of assets, buckets, exposed services (multi-cloud)
                |
                v
[OFFENSIVE]  Pacu         -> AWS exploitation: permission enum, privesc, persistence
                |
                v
[DEFENSIVE]  Prowler      -> hundreds of security/compliance checks, prioritized report
             ScoutSuite   -> multi-cloud audit, big picture of the posture
                |
                v
[CORRECTION] the defensive findings guide the hardening (least privilege, block public access, ...)
```

---

## Reference Tools

| Tool | Perspective | Provider | Main role |
| :--- | :--- | :--- | :--- |
| `cloud_enum` | Recon | Multi | Asset and bucket discovery via name permutation |
| `Pacu` | Offensive | AWS | "Metasploit for AWS": enum, privesc, exploitation |
| `Prowler` | Defensive | AWS/Azure/GCP | Security and compliance checks (CIS, ...) |
| `ScoutSuite` | Defensive | Multi | Multi-cloud audit of the configuration |
| `Trivy` | Defensive | (container/IaC) | Universal scanner (see `../02-.../image-scanning/`) |

> **Recommended modern tool:** for a complete cloud assessment, `cloud_enum` for the recon, `Pacu` for the AWS exploitation, `Prowler` and `ScoutSuite` for the defensive audit. `Trivy` (documented in `../02-containers-security/image-scanning/`) as a universal scanner for containers and IaC.

---

> **Note:** This folder is a reference guide to the tools, without findings of its own. Every tool must be used exclusively on cloud environments owned by the author or with explicit authorization; using them on third-party environments without permission is a crime and violates the providers' terms. Techniques are documented for educational and authorized security assessment purposes.
