> **English** | [Italiano](README.md)

# Terraform Scanning - Static Analysis of Infrastructure as Code

> - **Phase:** Cloud Security - IaC Static Analysis (Defense)
> - **Category:** Defensive - static analysis of the configuration before deployment
> - **Prerequisites:** IaC code (Terraform, CloudFormation); scanners (Checkov, tfsec, Trivy); CI/CD integration
> - **Output:** Finding CLOUD-010; misconfigurations identified before deployment; blocking of insecure infrastructures at the build

- **Operating Environment:** IaC repository, CI/CD, Checkov/tfsec
- **Main tools:** Checkov, tfsec, Trivy, Terrascan

---

## Executive Summary

Today infrastructure is written as code (Infrastructure as Code): a Terraform file describes servers, networks, storage and permissions, and the deploy creates them automatically. This brings enormous advantages (reproducibility, versioning, review) but also a mirror risk: an error in the code becomes an error in the infrastructure, replicated everywhere that code is applied. A wrong firewall rule written once is deployed to every environment.

Static analysis of the IaC identifies these misconfigurations **before** deployment, reading the code and comparing it with known security rules. Finding CLOUD-010 documents the use of Checkov and tfsec: scanners that analyze the Terraform and flag the classic errors - "you left port 22 (SSH) open to the entire Internet", "this S3 bucket is public", "this database is not encrypted". It is shift-left applied to the infrastructure: finding the error in the code, where it costs a one-line change, instead of in production, where it costs an incident.

The value is preventive and integrates into CI/CD: a scan at every Terraform change blocks the deployment of insecure infrastructures, making security an automatic gate of the pipeline instead of a fallible manual review.

---

## Folder Structure

```
terraform-scanning/
+-- README.md      # this file: IaC static analysis (Checkov, tfsec) (CLOUD-010)
+-- img/           # Checkov report and CI/CD integration
```

---

## Static Analysis with Checkov and tfsec

**Finding ID:** `CLOUD-010` | **Severity:** `Medium` (preventive detection of misconfigurations in the IaC before deployment; the real severity depends on the misconfig found)

### Operational Context

Checkov and tfsec read the Terraform code (without applying it) and evaluate it against hundreds of security policies. They identify misconfigured resources - too-open accesses, missing encryption, disabled logging - and indicate the line and the correction. It is static analysis: it finds the error in the code, not in the deployed infrastructure.

### PoC - Scanning the Terraform (Checkov)

```Bash
# Checkov analyzes the Terraform code against the security policies
checkov -d terraform/
```

```
Check: CKV_AWS_24: "Ensure no security groups allow ingress from 0.0.0.0:0 to port 22"
  FAILED for resource: aws_security_group.web
  File: /terraform/main.tf:12-20
    | ingress { from_port = 22, cidr_blocks = ["0.0.0.0/0"] }   <-- SSH open to the Internet (CLOUD-010)

Check: CKV_AWS_18: "Ensure S3 bucket has access logging enabled"
  FAILED for resource: aws_s3_bucket.data
```

### PoC - The problematic code

```HCL
# main.tf - ANTIPATTERN: SSH open to the world
resource "aws_security_group" "web" {
  ingress {
    from_port   = 22
    to_port     = 22
    cidr_blocks = ["0.0.0.0/0"]     # <-- anyone on the Internet can reach SSH
  }
}
```

### PoC - tfsec (alternative) and CI/CD integration

```Bash
# tfsec: alternative scanner, security-focused output
tfsec terraform/

# In pipeline: blocks the merge/deploy if there are high-severity FAILs
checkov -d terraform/ --hard-fail-on HIGH
```

```
[!] non-zero exit code: HIGH misconfig present -> deploy blocked   <-- insecure infra prevented (CLOUD-010)
```

### Defensive Operations

- **Shift-left in CI/CD:** integrate Checkov/tfsec as a gate of the pipeline; no Terraform with high-severity misconfig gets applied
- **Baseline and soft/hard fail:** define which checks block (hard-fail) and which warn (soft-fail); calibrate to the context to avoid noise
- **Guided correction:** every finding indicates the policy and the correction; Checkov can generate the patches for some resources
- **Broad coverage:** these scanners cover AWS, Azure, GCP, Kubernetes manifests and Dockerfiles; a single control for the heterogeneous IaC. Complementary to the secret discovery (`../secrets-management/`)

---

## Lab Experience

The value of Checkov was making visible errors that in the code seemed harmless. An `ingress` block with `cidr_blocks = ["0.0.0.0/0"]` is syntactically correct and works perfectly - it deploys a security group that exposes SSH to the entire world. Nothing in the code signals the danger; only the scanner, comparing it with the CKV_AWS_24 policy, highlights it. This made concrete that syntactic correctness is not security: the right code can describe the wrong infrastructure.

The lesson on the replication of the error was the most important. In traditional infrastructure, a wrong firewall rule is an error on one server; in IaC, it is an error in the code that replicates to every environment where the Terraform is applied - dev, staging, production. IaC amplifies both good practices and errors. This makes static analysis not an option but a necessity: the error must be caught in the code, before it multiplies in the infrastructure.

The integration into CI/CD completed the picture of shift-left, consistent with the image scanning (`../../02-containers-security/image-scanning/`). The same principle - automatic control at the build, blocking of the defects before the deploy - applied to the infrastructure instead of the containers. I noticed the symmetry of the entire "modern" approach: security shifts left, into the pipeline, becoming an automatic gate instead of a human review. It is the model that makes security scalable as much as the automation it protects.

---

## Theoretical Analysis: Shift-Left and Infrastructure as Verifiable Code

Infrastructure as Code has a valuable security property: it makes the infrastructure verifiable before it exists. Traditional infrastructure is inspected after deployment (active scanning, configuration audit); IaC is inspected as code, before deployment, statically. This anticipates the control to the most economical moment - before the infrastructure is created, when correcting means modifying a line - realizing shift-left: moving security as far upstream as possible in the life cycle.

The foundation is an economics of correction identical to that of image scanning. A misconfiguration found in the code costs a change; the same in production costs an exposure, potentially an incident. Since IaC replicates the code to every environment, the cost of an uncaught error multiplies by the number of deploys. Anticipating the control not only reduces the unit cost of the correction, but prevents the multiplication of the error - a double saving that makes the static analysis of IaC particularly advantageous.

This places security inside the development process, not next to it. The static analysis of IaC, like the scanning of images and secrets, belongs to the pipeline: it is an automatic gate crossed by every change, not an external periodic review. It is the security model of modern infrastructure - "policy as code" that verifies "infrastructure as code" - where the defense is automated and integrated as much as what it protects. Security scales only if it is code too.

---

## Reference Tools

| Tool | Type | Role | Main use case |
| :--- | :--- | :--- | :--- |
| `Checkov` | IaC scanner | Defensive | Static analysis of Terraform/CloudFormation/K8s (standard) |
| `tfsec` | Terraform scanner | Defensive | Static analysis focused on Terraform |
| `Trivy` | Multi-scanner | Defensive | IaC + images + secrets scanning (unified) |
| `Terrascan` | IaC scanner | Defensive | Static analysis with OPA policies |
| `OPA/Conftest` | Policy engine | Defensive | Custom "as code" policies on the IaC |

> **Recommended modern tool:** `Checkov` (Bridgecrew) as the standard for breadth (Terraform, CloudFormation, Kubernetes, Dockerfile), integrable in every CI/CD. `tfsec` as an alternative focused on Terraform. `Trivy` unifies IaC, images (`../../02-containers-security/image-scanning/`) and secrets in a single scanner.

---

## MITRE ATT&CK Mapping

> Attack techniques **prevented** by identifying the misconfig in the IaC before deployment.

| Tactic (prevented) | Technique | MITRE ID | Role of the control |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Detection of exposed services (e.g. SSH to 0.0.0.0/0) (CLOUD-010) |
| Initial Access | External Remote Services | `T1133` | Prevention of too-open remote accesses in the IaC |
| Collection | Data from Cloud Storage | `T1530` | Detection of public/unencrypted buckets in the code |
| Defense Evasion | Impair Defenses | `T1562` | Detection of disabled logging/monitoring in the IaC |

| Defensive countermeasure (D3FEND) | D3FEND ID | Application |
| :--- | :--- | :--- |
| Configuration Inventory | `D3-CI` | Static analysis of the infrastructure configuration |
| Platform Hardening | `D3-PH` | Correction of the misconfig before deployment |

---

> **Note:** All documented activities were conducted on IaC code and environments owned by the author. Static analysis of IaC is a non-intrusive defensive control. Techniques are documented for educational and defensive purposes in an authorized context.
