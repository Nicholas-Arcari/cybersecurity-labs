> **English** | [Italiano](README.md)

# 10 - Cloud security (cloud & modern)

> - **Phase:** Cloud & Modern Infrastructure Security
> - **Category:** Offensive + Defensive - identity and configuration as the perimeter
> - **Prerequisites:** Test cloud accounts/tenants/projects; provider CLIs; lab Docker/Kubernetes; understanding of modules 01-09 (the techniques transpose to the cloud)
> - **Output:** Findings CLOUD-001..010; understanding of the cloud attack surface (IaaS/PaaS, containers, orchestration, IaC) and the related defenses

---

## Introduction

The `10-cloud-security` module covers the security of modern infrastructure: the cloud providers (AWS, Azure, GCP), containers (Docker), orchestration (Kubernetes) and Infrastructure as Code (Terraform). The "Modern" in the name marks the transition from the on-premise world of the previous modules to the one where infrastructure is software, ephemeral and defined by APIs. It is the module where the techniques of the entire path transpose and transform into the cloud context.

One principle dominates the entire module: **in the cloud, the perimeter is no longer of network but of identity and configuration**. On-premise one defends with firewalls and segmentation; in the cloud, every service is a public API endpoint and the only access control is identity (IAM, managed identity, service account). The vast majority of cloud compromises do not derive from provider bugs but from customer-side misconfigurations - over-privileged identities, exposed storage, misconfigured containers, hardcoded secrets. The framework is the **Shared Responsibility Model**: the provider protects the security *of* the cloud, the customer the security *in* the cloud.

The module constantly interweaves the two perspectives, offensive and defensive, showing their symmetry: the same paths an attacker exploits (Pacu, kube-hunter), a defender identifies and closes (Prowler, kube-bench). Mastering both is what defines a complete cloud security analyst.

The four areas of the module:

1. **Providers Infrastructure (`01-providers-infrastructure/`, CLOUD-001..004):** AWS (IAM privesc, S3), Azure (Entra ID, managed identity), GCP (metadata SSRF, service account). Identity as the perimeter, declined on the three major providers.

2. **Containers Security (`02-containers-security/`, CLOUD-005..006):** the supply chain of the images (Trivy) and the isolation of the runtime (container escape). What is inside and how contained it is.

3. **Orchestration (`03-orchestration/`, CLOUD-007..008):** Kubernetes, the operating system of the cloud - attacks on the cluster (etcd, exposed APIs) and hardening (CIS, Pod Security).

4. **IaC Security (`04-iac-security/`, CLOUD-009..010):** infrastructure as code - secrets management (Vault) and static analysis (Checkov). Shift-left security, inside the pipeline.

The **Tooling** section (`Tooling/`) collects the cross-cutting tools (Pacu, cloud_enum, Prowler, ScoutSuite) as a reference guide.

The module closes the path by linking to all the previous ones: the SSRF (03) becomes cloud credential theft, the privilege escalation (04) transposes to IAM, persistence and exfiltration (07) have their cloud equivalent, hardening and audit (08) apply to clusters and accounts, and secrets management recalls recon (01) and post-exploitation (07). The cloud is not a separate world: it is where all the competencies of the path converge and update to the present.

---

## Folder structure

```
10-cloud-security (Cloud&Modern)/
+-- README.md                                      <- this file: CLOUD-001..010 registry + MITRE
|
+-- 01-providers-infrastructure (IaaS & PaaS)/
|   +-- README.md                                  <- CLOUD-001..004 registry
|   +-- AWS (Amazon Web Services)/
|   |   +-- IAM-enumeration/                        <- CLOUD-001 (IAM privesc)
|   |   +-- S3-buckets-attacks/                     <- CLOUD-002 (exposed S3)
|   +-- Azure/                                      <- CLOUD-003 (Entra ID + managed identity)
|   +-- GCP (Google Cloud Platform)/                <- CLOUD-004 (metadata SSRF)
|
+-- 02-containers-security (Docker)/
|   +-- README.md                                  <- CLOUD-005..006 registry
|   +-- image-scanning/                             <- CLOUD-005 (Trivy, supply chain)
|   +-- runtime-security/                           <- CLOUD-006 (container escape)
|
+-- 03-orchestration (Kubernetes)/
|   +-- README.md                                  <- CLOUD-007..008 registry
|   +-- K8s-attacks/                                <- CLOUD-007 (exposed clusters)
|   +-- K8s-auditing/                               <- CLOUD-008 (kube-bench, Pod Security)
|
+-- 04-iac-security (Infrastructure as Code)/
|   +-- README.md                                  <- CLOUD-009..010 registry
|   +-- secrets-management/                         <- CLOUD-009 (secrets + Vault)
|   +-- terraform-scanning/                         <- CLOUD-010 (Checkov, tfsec)
|
+-- Tooling/                                        <- tool guide (Pacu, cloud_enum, Prowler, ScoutSuite)
```

---

## Recommended operational flow

```
[INPUT] Cloud environment to test/defend (accounts, clusters, IaC)
         |
         v
[1] Recon (Tooling/cloud-enum) -> assets and public surface
         |
         v
[2] Providers (01) -> identity: IAM/Entra/SA -> privesc (CLOUD-001..004)
         |
         v
[3] Containers (02) -> supply chain (CLOUD-005) + escape (CLOUD-006)
         |
         v
[4] Orchestration (03) -> K8s cluster: attack (CLOUD-007) and hardening (CLOUD-008)
         |
         v
[5] IaC (04) -> secrets (CLOUD-009) + misconfig (CLOUD-010), shift-left in CI/CD
         |
         v
[DEFENSE] cross-cutting audit (Prowler/ScoutSuite) -> least privilege + hardening
         |
         v
[OUTPUT] Cloud environment understood from both sides: attackable and defensible
```

---

## Reference tools

| tool | area | perspective | main use case |
| :--- | :--- | :--- | :--- |
| `Pacu` | aws | offensive | exploitation framework (enum, privesc) |
| `AzureHound` / `MicroBurst` | azure | offensive | attack path and entra id enumeration |
| `cloud_enum` | multi | recon | asset and bucket discovery |
| `Trivy` | container/iac | defensive | cve and misconfig scanning |
| `Falco` | container/k8s | defensive | runtime detection (escape, anomalies) |
| `kube-bench` / `kube-hunter` | kubernetes | def./off. | cis audit / exposure discovery |
| `Checkov` / `gitleaks` | iac | defensive | static analysis and secret discovery |
| `Prowler` / `ScoutSuite` | multi | defensive | account audit and compliance |

> **Recommended modern tool:** a complete cloud stack combines `Pacu`/`kube-hunter` (offensive), `Prowler`/`ScoutSuite`/`kube-bench` (defensive audit), `Trivy`/`Checkov`/`gitleaks` (shift-left in CI/CD) and `Falco` (runtime detection). Detail in `Tooling/` and in the respective sections.

---

## Finding registry - module 10

| id | description | severity | subfolder |
| :--- | :--- | :---: | :--- |
| `CLOUD-001` | aws iam enumeration + privilege escalation to admin | `Critical` | `01-.../AWS/IAM-enumeration/` |
| `CLOUD-002` | exposed/misconfigured aws s3 bucket: data exfiltration | `High` | `01-.../AWS/S3-buckets-attacks/` |
| `CLOUD-003` | azure: managed identity abuse (imds) + entra id enumeration | `High` | `01-.../Azure/` |
| `CLOUD-004` | gcp: service account token theft via metadata/ssrf | `High` | `01-.../GCP/` |
| `CLOUD-005` | container image scanning: cves in the images before deployment | `Medium` | `02-.../image-scanning/` |
| `CLOUD-006` | container escape via docker socket: root on the host | `Critical` | `02-.../runtime-security/` |
| `CLOUD-007` | exposed k8s cluster: secret theft and control of the control plane | `Critical` | `03-.../K8s-attacks/` |
| `CLOUD-008` | k8s auditing: cis (kube-bench) + pod security standards | `High` | `03-.../K8s-auditing/` |
| `CLOUD-009` | hardcoded secrets in code/iac/git + management with vault | `High` | `04-.../secrets-management/` |
| `CLOUD-010` | terraform scanning: iac misconfigurations before deployment | `Medium` | `04-.../terraform-scanning/` |

---

## MITRE ATT&CK mapping - aggregated

> Reference: MITRE ATT&CK for Cloud (IaaS) and for Containers. Complementary defensive framework: MITRE D3FEND.

| tactic | technique | mitre id | related finding |
| :--- | :--- | :--- | :--- |
| discovery | cloud infrastructure discovery | `T1580` | CLOUD-001, CLOUD-003, CLOUD-004 |
| privilege escalation | valid accounts: cloud accounts | `T1078.004` | CLOUD-001, CLOUD-003, CLOUD-004, CLOUD-009 |
| credential access | steal application access token | `T1528` | CLOUD-003, CLOUD-004 |
| credential access | unsecured credentials: cloud instance metadata api | `T1552.005` | CLOUD-004 |
| credential access | unsecured credentials: credentials in files | `T1552.001` | CLOUD-009 |
| credential access | unsecured credentials: credentials in repositories | `T1552.008` | CLOUD-009 |
| credential access | unsecured credentials: container api | `T1552.007` | CLOUD-007, CLOUD-008 |
| collection | data from cloud storage | `T1530` | CLOUD-002 |
| persistence | account manipulation: additional cloud credentials | `T1098.001` | CLOUD-001 |
| initial access | supply chain compromise | `T1195` | CLOUD-005 |
| initial access | exploit public-facing application | `T1190` | CLOUD-007, CLOUD-008, CLOUD-010 |
| privilege escalation | escape to host | `T1611` | CLOUD-006, CLOUD-008 |
| execution | deploy container | `T1610` | CLOUD-006, CLOUD-007 |
| discovery | container and resource discovery | `T1613` | CLOUD-006, CLOUD-007 |

| defensive countermeasure (d3fend) | d3fend id | area |
| :--- | :--- | :--- |
| configuration inventory | `D3-CI` | cloud audit (prowler/scoutsuite), iac (checkov) |
| platform hardening | `D3-PH` | least privilege, kube-bench, iac hardening |
| application vulnerability assessment | `D3-AVA` | image scanning (trivy) |
| mandatory access control | `D3-MAC` | pod security, seccomp/apparmor |
| credential rotation | `D3-CR` | secrets management (vault, dynamic secrets) |

---

> **Note:** All activities documented in this module were conducted on accounts, tenants, projects, clusters and lab environments owned by the author. Security testing on third-party cloud infrastructures requires explicit authorization and, for some activities, prior notification to the provider (each provider has its own penetration testing policy). Unauthorized access to third-party cloud environments, containers and clusters is a crime and violates the terms of service. Numerous sections document, with equal emphasis, the defensive countermeasures (least privilege, hardening, audit, shift-left), consistent with the objective of understanding the attack to strengthen the defense. Techniques are documented for educational and authorized security assessment purposes with an explicitly defined scope.
