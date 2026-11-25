> **English** | [Italiano](README.md)

# 04 - IaC security (infrastructure as code)

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

## Folder structure

```
04-iac-security (Infrastructure as Code)/
+-- README.md              # this file: CLOUD-009..010 registry
|
+-- secrets-management/    # CLOUD-009: hardcoded secrets + Vault
+-- terraform-scanning/    # CLOUD-010: IaC static analysis (Checkov, tfsec)
```

---

## Recommended operational flow

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

## Reference tools

| tool | type | role | main use case |
| :--- | :--- | :--- | :--- |
| `gitleaks` / `trufflehog` | secret scanner | defensive | secret discovery in code and git history |
| `HashiCorp Vault` | secrets manager | defensive | centralized store, dynamic secrets |
| `Checkov` | iac scanner | defensive | multi-platform static analysis (standard) |
| `tfsec` | terraform scanner | defensive | static analysis focused on terraform |
| `Trivy` | multi-scanner | defensive | iac + images + secrets unified |

> **Recommended modern tool:** `gitleaks` + `Vault` for the secrets, `Checkov`/`tfsec` for the misconfig, all in CI/CD. `Trivy` as a unified scanner (IaC, images, secrets). The common principle: shift-left, automatic controls in the pipeline.

---

## Finding registry - IaC security

| id | description | severity | subfolder |
| :--- | :--- | :---: | :--- |
| `CLOUD-009` | hardcoded secrets in code/iac/git + management with vault (dynamic secrets) | `High` | `secrets-management/` |
| `CLOUD-010` | terraform scanning: iac misconfigurations identified before deployment | `Medium` | `terraform-scanning/` |

---

## MITRE ATT&CK mapping - aggregated

| tactic | technique | mitre id | related finding |
| :--- | :--- | :--- | :--- |
| credential access | unsecured credentials: credentials in files | `T1552.001` | CLOUD-009 |
| credential access | unsecured credentials: credentials in repositories | `T1552.008` | CLOUD-009 |
| initial access | exploit public-facing application | `T1190` | CLOUD-010 |
| initial access | external remote services | `T1133` | CLOUD-010 |
| privilege escalation | valid accounts: cloud accounts | `T1078.004` | CLOUD-009 |

---

> **Note:** All documented activities were conducted on code and environments owned by the author. Scanning IaC and secrets is a defensive control; scanning third-party repositories without authorization and using leaked credentials are crimes. Techniques are documented for educational and defensive purposes in an authorized context.
