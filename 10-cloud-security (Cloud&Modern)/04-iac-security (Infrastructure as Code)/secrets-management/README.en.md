> **English** | [Italiano](README.md)

# Secrets Management - Hardcoded Secrets and HashiCorp Vault

> - **Phase:** Cloud Security - Secrets Management (IaC & Supply Chain)
> - **Category:** Offensive (discovery) + Defensive (management with Vault)
> - **Prerequisites:** Code/IaC/repository to analyze; secret scanners (gitleaks/trufflehog); for the solution, HashiCorp Vault
> - **Output:** Finding CLOUD-009; hardcoded secrets identified; secrets management architecture that eliminates them at the root

- **Operating Environment:** Code/IaC repository, CI/CD, HashiCorp Vault (lab)
- **Main tools:** gitleaks, trufflehog, HashiCorp Vault

---

## Executive Summary

Hardcoded secrets are one of the most widespread and persistent vulnerabilities in modern infrastructure: API keys, database passwords, cloud tokens written directly in the code, in the configuration files or in the Infrastructure as Code (Terraform). The problem is aggravated by versioning: a secret committed in git remains in the repository's history even if removed in a subsequent commit, and anyone with access to the repo (or a fork/clone of it) can recover it. It is the same vector seen in `01-recon` (code secret leakage) and in `07-post-exploitation` (credentials in files), here addressed from the management point of view.

Finding CLOUD-009 documents two faces of the problem. The discovery: scanners like gitleaks and trufflehog find the secrets in the code and in the git history - the same as an attacker would do. The solution: HashiCorp Vault, which eliminates hardcoded secrets at the root by providing a centralized store and, most importantly, **dynamic secrets** that are short-lived, generated on demand and automatically revoked. With Vault, the code does not contain secrets but only the reference to request them at runtime.

The principle is that secrets must never live in the code. Code describes logic; secrets are sensitive data that must be managed by a dedicated system, with access control, rotation and audit - responsibilities that a text file in a repository cannot fulfill.

---

## Folder Structure

```
secrets-management/
+-- README.md      # this file: hardcoded secrets + Vault (CLOUD-009)
+-- img/           # gitleaks scan and Vault flow
```

---

## Secret Discovery and Management with Vault

**Finding ID:** `CLOUD-009` | **Severity:** `High` (hardcoded secrets exposed in the code/git history; credentials directly usable by anyone with access to the repository)

### Operational Context

The first step, both for the attacker and the defender, is to discover the secrets. gitleaks and trufflehog scan the code and - crucially - the entire git history, where "removed" secrets survive. The defensive solution is not just to remove them but to change architecture: move the secrets to Vault and reference them at runtime.

### PoC - Secret discovery (gitleaks)

```Bash
# Scan of the repository and its entire git history
gitleaks detect --source . --report-format json
```

```
Finding:     AWS Access Key
File:        terraform/main.tf
Secret:      AKIA...EXAMPLE
Commit:      a3f9c1  (3 months ago, "removed" in the next commit)   <-- still in the history (CLOUD-009)
Rule:        aws-access-token
```

### PoC - The problem: hardcoded secret in IaC

```HCL
# terraform/main.tf - ANTIPATTERN: cleartext secret in the code
resource "aws_db_instance" "prod" {
  username = "admin"
  password = "SuperSecret123!"          # <-- hardcoded, ends up in git and in the state
}
```

### PoC - The solution: dynamic secrets with Vault

```Bash
# Vault generates dynamic, short-lived database credentials, on demand
vault read database/creds/prod-role
```

```
Key                Value
lease_duration     1h                    <-- credential valid 1 hour, then revoked
username           v-token-prod-x7f2...   <-- user generated on the fly, not hardcoded
password           A1b2-dynamic-...       <-- never written in the code (CLOUD-009 solved)
```

```HCL
# The code now references Vault, does not contain the secret
data "vault_database_secret" "db" {
  path = "database/creds/prod-role"      # <-- reference, not secret
}
```

### Remediation

- **Scanning in CI/CD:** gitleaks/trufflehog as a pre-commit hook and in the pipeline block the secrets before they enter git; scanning is the first control
- **History remediation:** a committed secret must be considered compromised and rotated immediately; removing it from the current commit is not enough (it remains in the history and must already be considered leaked)
- **Vault (or equivalent):** centralize the secrets in Vault/AWS Secrets Manager/Azure Key Vault; prefer the short-lived dynamic secrets, which limit the validity window of a possible leak
- **Never in the Terraform state:** the state file contains the values in cleartext; protect it (encrypted backend, restricted access) and never commit it

---

## Lab Experience

The most instructive discovery was the persistence of the secrets in the git history. I had "removed" a key from a file and committed the removal, believing the problem solved; gitleaks found it anyway, in the previous commit. This made concrete a principle I had encountered in the recon module: git does not forget. A committed secret is compromised forever, regardless of the subsequent commits, and the only correct response is to rotate it - not to remove it and hope.

Vault changed my mental model of secrets. I was used to thinking of secrets as static values to hide well; Vault's dynamic secrets make them ephemeral by construction - a database credential generated on the fly, valid one hour, then automatically revoked. Even if it leaks, the exploitation window is minimal. This shifts the defense from "hide the secret well" (fragile) to "the secret is worth so little for so long that hiding it matters less" (robust). It is the same philosophy as the short-lived credentials (STS roles) seen on AWS.

The reflection was on the inevitability of human error. No one hardcodes a secret out of malice; one does it out of haste, to make something work. The effective defense is not to ask developers never to make a mistake (it will fail), but to make the mistake harmless (short-lived dynamic secrets) and interceptable (scanning in CI/CD). As with S3 buckets, robust security contains the error instead of pretending it will not happen.

---

## Theoretical Analysis: The Secret as Data, not as Code

The conceptual error at the root of hardcoded secrets is treating sensitive data as if it were code. Code describes logic and is made to be versioned, shared, inspected; a secret is confidential data that requires the opposite - access control, rotation, audit, confidentiality. Putting them in the same file means applying to the secret the properties of code (versioned, shared, permanent in git), which are exactly the wrong ones for a secret. The separation between code and secrets is not a convention but a necessity deriving from their opposite nature.

Dynamic secrets add a temporal dimension to the defense. A static secret is vulnerable as long as it exists: the longer it lives, the more opportunities it has to leak. A short-lived dynamic secret inverts the equation: it exists only for the necessary time and then ceases to be valid. This reduces the temporal surface of the exposure - it does not eliminate the possibility of a leak, but drastically limits its exploitation. It is the application to secrets of the principle of minimization: least privilege in time, as well as in space.

The link with the rest of the path is direct and recurring. Hardcoded secrets are what the attacker looks for everywhere: in the repositories (recon), in the system files (post-exploitation), in the buckets (cloud), in the containers. Centralized and dynamic secrets management is the cross-cutting countermeasure that deprives the attacker of this loot. Every module of the path showed the attacker collecting credentials; this shows the defender making them unreachable and ephemeral, breaking the vector at the source.

---

## Real-World Scenario: Post-Exploitation Projection

> Attacker and defender perspectives.

### Attacker Perspective (Red Team)

**Projected kill chain:**

```
[CLOUD-009] gitleaks/trufflehog on the public or cloned repo -> AWS key in the git history
        |
        v
The key is still valid (static secret never rotated)
        |
        v
AWS access -> IAM enumeration (CLOUD-001) -> escalation
        |
        v
Compromise of the cloud account
```

**Potential impact:** a single hardcoded secret in a repository (especially if public or exposed) is often the entry point to a complete cloud compromise. The pattern "AWS key on GitHub, account compromised in minutes" is documented extensively: automated bots scan the public repositories in real time looking for exactly these secrets. The link with CLOUD-001 (IAM) is direct: the leaked key is the starting point of the escalation.

### Defender Perspective (Blue Team)

**Detection:** continuous scanning of the repositories (gitleaks/trufflehog in CI/CD and on the existing repos); monitoring of the credential use (CloudTrail) for secrets that appear used from anomalous contexts.

**IOC:** use of a credential from an IP/geolocation never seen; secrets identified by the scanning; long-lived credentials never rotated.

**Containment and hardening:**
- Immediate rotation of every secret found (consider it compromised)
- Vault/Secrets Manager with short-lived dynamic secrets
- Mandatory scanning in CI/CD and pre-commit hooks
- Protected Terraform state, never committed

**Defensive lesson:** secrets management is a cross-cutting defense that deprives the attacker of the most precious loot - the credentials. Two controls combine: intercepting the secrets before they enter git (scanning) and making them ephemeral when they exist (dynamic Vault). Together they turn a secret from a permanent vulnerability into a contained and temporary exposure.

---

## Reference Tools

| Tool | Type | Role | Main use case |
| :--- | :--- | :--- | :--- |
| `gitleaks` | Secret scanner | Defensive/Offensive | Scanning of code and git history for secrets |
| `trufflehog` | Secret scanner | Defensive/Offensive | Discovery of secrets with validity verification |
| `HashiCorp Vault` | Secrets manager | Defensive | Centralized store and dynamic secrets |
| `AWS Secrets Manager` | Secrets manager | Defensive | Native AWS secrets management with rotation |
| `Azure Key Vault` | Secrets manager | Defensive | Native Azure secrets management |
| `git-secrets` | Pre-commit hook | Defensive | Blocking of secrets before the commit |

> **Recommended modern tool:** `gitleaks`/`trufflehog` for the scanning (in CI/CD and pre-commit), `HashiCorp Vault` for the centralized management with dynamic secrets. The native secrets managers (AWS/Azure/GCP) are excellent alternatives integrated with the provider. The common principle: secrets out of the code, short-lived, with audit.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Credential Access | Unsecured Credentials: Credentials In Files | `T1552.001` | Hardcoded secrets in code/IaC (CLOUD-009) |
| Credential Access | Unsecured Credentials: Credentials in Repositories | `T1552.008` | Secrets in the git history of the repositories (CLOUD-009) |
| Reconnaissance | Search Open Technical Databases / Repos | `T1596` | Scanning of the repositories for exposed secrets |
| Privilege Escalation | Valid Accounts: Cloud Accounts | `T1078.004` | Use of the leaked secret to access the cloud |

| Defensive countermeasure (D3FEND) | D3FEND ID | Application |
| :--- | :--- | :--- |
| Credential Rotation | `D3-CR` | Rotation of the compromised secrets / short-lived dynamic |
| File Analysis | `D3-FA` | Scanning of the code and the git history for secrets |

---

> **Note:** All documented activities were conducted on repositories and environments owned by the author. Scanning third-party repositories for secrets without authorization, and using leaked credentials, are crimes. Techniques are documented for educational and defensive/authorized security assessment purposes.
