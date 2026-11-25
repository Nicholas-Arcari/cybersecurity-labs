> **English** | [Italiano](README.md)

# 04 - IaC Security (Infrastructure as Code)

> - **Phase:** Cloud Security - Infrastructure as Code
> - **Category:** Defensive - "shift-left" infrastructure security
> - **Prerequisites:** IaC code (Terraform); scanners (Checkov, tfsec, gitleaks); CI/CD integration
> - **Output:** Findings CLOUD-009..010; secrets and misconfigurations identified before deployment

---

## Introduction

Today infrastructures are written as code: a Terraform file describes servers, networks, storage and permissions, and the deploy creates them automatically. Infrastructure as Code (IaC) brings reproducibility, versioning and review, but introduces a mirror risk - an error in the code becomes an error in the infrastructure, replicated to every environment where the code is applied. IaC amplifies both good practices and errors.

IaC security is "shift-left": moving the controls as far upstream as possible, into the code, before the infrastructure exists. It is the most economical moment to correct (a line instead of an incident) and the only one that prevents the multiplication of the error across the deploys. The section covers the two fundamental controls:

1. **Secrets Management (CLOUD-009):** secrets must not live in the code. Discovery of the hardcoded secrets (gitleaks/trufflehog, also in the git history) and management with Vault (short-lived dynamic secrets). Cross-cutting countermeasure to the attacker's most precious loot.

2. **Terraform Scanning (CLOUD-010):** static analysis of the IaC (Checkov, tfsec) that identifies the misconfigurations before deployment - "SSH port open to the Internet", "public bucket", "unencrypted database".

Both integrate into CI/CD as automatic gates: no secret enters git, no insecure infrastructure gets deployed. It is the security model of modern infrastructure - policy as code that verifies infrastructure as code - where the defense is automated as much as what it protects.

---

## Folder Structure

```
04-iac-security (Infrastructure as Code)/
+-- README.md              # this file: CLOUD-009..010 registry
|
+-- secrets-management/    # CLOUD-009: hardcoded secrets + Vault
+-- terraform-scanning/    # CLOUD-010: IaC static analysis (Checkov, tfsec)
```

---

## Recommended Operational Flow

```
[CODE] IaC written (Terraform) + secrets to manage
         |
         v
[1] Secrets (secrets-management/)
     +-- gitleaks/trufflehog -> no secret in git; Vault -> dynamic secrets (CLOUD-009)
              |
              v
[2] Static analysis (terraform-scanning/)
     +-- Checkov/tfsec -> misconfig identified and blocked before deployment (CLOUD-010)
              |
              v
[CI/CD] automatic gates -> deploy only if secure
              |
              v
[OUTPUT] Infrastructure without hardcoded secrets and without known misconfig
```

---

## Reference Tools

| Tool | Type | Role | Main use case |
| :--- | :--- | :--- | :--- |
| `gitleaks` / `trufflehog` | Secret scanner | Defensive | Secret discovery in code and git history |
| `HashiCorp Vault` | Secrets manager | Defensive | Centralized store, dynamic secrets |
| `Checkov` | IaC scanner | Defensive | Multi-platform static analysis (standard) |
| `tfsec` | Terraform scanner | Defensive | Static analysis focused on Terraform |
| `Trivy` | Multi-scanner | Defensive | IaC + images + secrets unified |

> **Recommended modern tool:** `gitleaks` + `Vault` for the secrets, `Checkov`/`tfsec` for the misconfig, all in CI/CD. `Trivy` as a unified scanner (IaC, images, secrets). The common principle: shift-left, automatic controls in the pipeline.

---

## Finding Registry - IaC Security

| ID | Description | Severity | Subfolder |
| :--- | :--- | :---: | :--- |
| `CLOUD-009` | Hardcoded secrets in code/IaC/git + management with Vault (dynamic secrets) | `High` | `secrets-management/` |
| `CLOUD-010` | Terraform scanning: IaC misconfigurations identified before deployment | `Medium` | `terraform-scanning/` |

---

## MITRE ATT&CK Mapping - Aggregated

| Tactic | Technique | MITRE ID | Related Finding |
| :--- | :--- | :--- | :--- |
| Credential Access | Unsecured Credentials: Credentials In Files | `T1552.001` | CLOUD-009 |
| Credential Access | Unsecured Credentials: Credentials in Repositories | `T1552.008` | CLOUD-009 |
| Initial Access | Exploit Public-Facing Application | `T1190` | CLOUD-010 |
| Initial Access | External Remote Services | `T1133` | CLOUD-010 |
| Privilege Escalation | Valid Accounts: Cloud Accounts | `T1078.004` | CLOUD-009 |

---

> **Note:** All documented activities were conducted on code and environments owned by the author. Scanning IaC and secrets is a defensive control; scanning third-party repositories without authorization and using leaked credentials are crimes. Techniques are documented for educational and defensive purposes in an authorized context.
