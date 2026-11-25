> **English** | [Italiano](README.md)

# 10 - Cloud Security (Cloud & Modern)

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

## Folder Structure

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

## Recommended Operational Flow

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

## Reference Tools

| Tool | Area | Perspective | Main use case |
| :--- | :--- | :--- | :--- |
| `Pacu` | AWS | Offensive | Exploitation framework (enum, privesc) |
| `AzureHound` / `MicroBurst` | Azure | Offensive | Attack path and Entra ID enumeration |
| `cloud_enum` | Multi | Recon | Asset and bucket discovery |
| `Trivy` | Container/IaC | Defensive | CVE and misconfig scanning |
| `Falco` | Container/K8s | Defensive | Runtime detection (escape, anomalies) |
| `kube-bench` / `kube-hunter` | Kubernetes | Def./Off. | CIS audit / exposure discovery |
| `Checkov` / `gitleaks` | IaC | Defensive | Static analysis and secret discovery |
| `Prowler` / `ScoutSuite` | Multi | Defensive | Account audit and compliance |

> **Recommended modern tool:** a complete cloud stack combines `Pacu`/`kube-hunter` (offensive), `Prowler`/`ScoutSuite`/`kube-bench` (defensive audit), `Trivy`/`Checkov`/`gitleaks` (shift-left in CI/CD) and `Falco` (runtime detection). Detail in `Tooling/` and in the respective sections.

---

## Finding Registry - Module 10

| ID | Description | Severity | Subfolder |
| :--- | :--- | :---: | :--- |
| `CLOUD-001` | AWS IAM enumeration + privilege escalation to admin | `Critical` | `01-.../AWS/IAM-enumeration/` |
| `CLOUD-002` | Exposed/misconfigured AWS S3 bucket: data exfiltration | `High` | `01-.../AWS/S3-buckets-attacks/` |
| `CLOUD-003` | Azure: managed identity abuse (IMDS) + Entra ID enumeration | `High` | `01-.../Azure/` |
| `CLOUD-004` | GCP: service account token theft via metadata/SSRF | `High` | `01-.../GCP/` |
| `CLOUD-005` | Container image scanning: CVEs in the images before deployment | `Medium` | `02-.../image-scanning/` |
| `CLOUD-006` | Container escape via Docker socket: root on the host | `Critical` | `02-.../runtime-security/` |
| `CLOUD-007` | Exposed K8s cluster: Secret theft and control of the control plane | `Critical` | `03-.../K8s-attacks/` |
| `CLOUD-008` | K8s auditing: CIS (kube-bench) + Pod Security Standards | `High` | `03-.../K8s-auditing/` |
| `CLOUD-009` | Hardcoded secrets in code/IaC/git + management with Vault | `High` | `04-.../secrets-management/` |
| `CLOUD-010` | Terraform scanning: IaC misconfigurations before deployment | `Medium` | `04-.../terraform-scanning/` |

---

## MITRE ATT&CK Mapping - Aggregated

> Reference: MITRE ATT&CK for Cloud (IaaS) and for Containers. Complementary defensive framework: MITRE D3FEND.

| Tactic | Technique | MITRE ID | Related Finding |
| :--- | :--- | :--- | :--- |
| Discovery | Cloud Infrastructure Discovery | `T1580` | CLOUD-001, CLOUD-003, CLOUD-004 |
| Privilege Escalation | Valid Accounts: Cloud Accounts | `T1078.004` | CLOUD-001, CLOUD-003, CLOUD-004, CLOUD-009 |
| Credential Access | Steal Application Access Token | `T1528` | CLOUD-003, CLOUD-004 |
| Credential Access | Unsecured Credentials: Cloud Instance Metadata API | `T1552.005` | CLOUD-004 |
| Credential Access | Unsecured Credentials: Credentials In Files | `T1552.001` | CLOUD-009 |
| Credential Access | Unsecured Credentials: Credentials in Repositories | `T1552.008` | CLOUD-009 |
| Credential Access | Unsecured Credentials: Container API | `T1552.007` | CLOUD-007, CLOUD-008 |
| Collection | Data from Cloud Storage | `T1530` | CLOUD-002 |
| Persistence | Account Manipulation: Additional Cloud Credentials | `T1098.001` | CLOUD-001 |
| Initial Access | Supply Chain Compromise | `T1195` | CLOUD-005 |
| Initial Access | Exploit Public-Facing Application | `T1190` | CLOUD-007, CLOUD-008, CLOUD-010 |
| Privilege Escalation | Escape to Host | `T1611` | CLOUD-006, CLOUD-008 |
| Execution | Deploy Container | `T1610` | CLOUD-006, CLOUD-007 |
| Discovery | Container and Resource Discovery | `T1613` | CLOUD-006, CLOUD-007 |

| Defensive countermeasure (D3FEND) | D3FEND ID | Area |
| :--- | :--- | :--- |
| Configuration Inventory | `D3-CI` | Cloud audit (Prowler/ScoutSuite), IaC (Checkov) |
| Platform Hardening | `D3-PH` | Least privilege, kube-bench, IaC hardening |
| Application Vulnerability Assessment | `D3-AVA` | Image scanning (Trivy) |
| Mandatory Access Control | `D3-MAC` | Pod Security, seccomp/AppArmor |
| Credential Rotation | `D3-CR` | Secrets management (Vault, dynamic secrets) |

---

> **Note:** All activities documented in this module were conducted on accounts, tenants, projects, clusters and lab environments owned by the author. Security testing on third-party cloud infrastructures requires explicit authorization and, for some activities, prior notification to the provider (each provider has its own penetration testing policy). Unauthorized access to third-party cloud environments, containers and clusters is a crime and violates the terms of service. Numerous sections document, with equal emphasis, the defensive countermeasures (least privilege, hardening, audit, shift-left), consistent with the objective of understanding the attack to strengthen the defense. Techniques are documented for educational and authorized security assessment purposes with an explicitly defined scope.
