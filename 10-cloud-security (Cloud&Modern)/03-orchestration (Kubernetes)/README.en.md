> **English** | [Italiano](README.md)

# 03 - Orchestration (Kubernetes)

> - **Phase:** Cloud Security - Kubernetes (Orchestration)
> - **Category:** Offensive + Defensive - the operating system of the cloud
> - **Prerequisites:** Test K8s cluster; kubectl; for the offensive, an exposed cluster or initial access; for the defensive, audit access
> - **Output:** Findings CLOUD-007..008; understanding of the cluster's attack surface and the countermeasures

---

## Introduction

Kubernetes is the operating system of the modern cloud: it orchestrates thousands of containers on clusters of nodes, managing deployments, networking, storage and secrets. This centrality makes it a very high-value target - compromising the cluster means controlling all the workloads running on it - and a vast and complex attack surface, where security is the sum of many correct configurations and one exposed component is enough to compromise the whole.

The section addresses Kubernetes from the two complementary perspectives:

1. **K8s Attacks (CLOUD-007):** the offensive. Exploitation of exposed and misconfigured clusters - API server with anonymous access, unauthenticated etcd (which contains the Secrets in cleartext), open kubelet, over-privileged service accounts. kube-hunter for the reconnaissance.

2. **K8s Auditing (CLOUD-008):** the defense. CIS Benchmark conformity audit with kube-bench and prevention of dangerous pods with the Pod Security Standards. Closes the exposures the offensive exploits.

The cross-cutting theme is the management of complexity. Kubernetes has too many components and configurations for security to be verified by hand; systematic auditing against a baseline (kube-bench/CIS) and admission control that constrains the future deploys (Pod Security Standards) are needed. The offensive/defensive symmetry is strong: kube-hunter finds what kube-bench helps to correct.

---

## Folder Structure

```
03-orchestration (Kubernetes)/
+-- README.md          # this file: CLOUD-007..008 registry
|
+-- K8s-attacks/       # CLOUD-007: exposed/misconfigured clusters (kube-hunter, etcd)
+-- K8s-auditing/      # CLOUD-008: CIS audit (kube-bench) + Pod Security Standards
```

---

## Recommended Operational Flow

```
[OFFENSIVE] K8s-attacks/
     +-- kube-hunter -> exposed API/etcd/kubelet -> Secret theft / cluster control (CLOUD-007)
              |
              v
[DEFENSIVE] K8s-auditing/
     +-- kube-bench (CIS) -> closes the control plane exposures (CLOUD-008)
     +-- Pod Security Standards -> prevents the dangerous pods (escape)
              |
              v
[OUTPUT] Hardened cluster: protected control plane, escape and escalation prevented
```

---

## Reference Tools

| Tool | Type | Role | Main use case |
| :--- | :--- | :--- | :--- |
| `kubectl` | K8s CLI | Official | Interaction with the cluster |
| `kube-hunter` | Scanner | Offensive | Discovery of exposed components |
| `Peirates` | Exploitation | Offensive | Post-exploitation on K8s |
| `kube-bench` | CIS auditor | Defensive | CIS conformity audit |
| `Pod Security` / `Kyverno` | Admission | Defensive | Blocking of dangerous pods |
| `Falco` | Runtime security | Defensive | Runtime detection |

> **Recommended modern tool:** `kube-hunter`/`Peirates` (offensive) and `kube-bench` + Pod Security Standards + `Falco` (defensive). See `../Tooling/` for the cross-cutting cloud scanners.

---

## Finding Registry - Orchestration (Kubernetes)

| ID | Description | Severity | Subfolder |
| :--- | :--- | :---: | :--- |
| `CLOUD-007` | Exposed/misconfigured K8s cluster: Secret theft and control of the control plane | `Critical` | `K8s-attacks/` |
| `CLOUD-008` | K8s auditing: CIS benchmark (kube-bench) + Pod Security Standards (hardening) | `High` | `K8s-auditing/` |

---

## MITRE ATT&CK Mapping - Aggregated

> Reference: MITRE ATT&CK for Containers.

| Tactic | Technique | MITRE ID | Related Finding |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | CLOUD-007, CLOUD-008 |
| Credential Access | Unsecured Credentials: Container API | `T1552.007` | CLOUD-007, CLOUD-008 |
| Privilege Escalation | Escape to Host | `T1611` | CLOUD-008 (prevention) |
| Execution | Deploy Container | `T1610` | CLOUD-007, CLOUD-008 |
| Discovery | Container and Resource Discovery | `T1613` | CLOUD-007 |

---

> **Note:** All documented activities were conducted on a Kubernetes lab cluster owned by the author. Unauthorized access to third-party clusters is a crime. Techniques are documented for educational and authorized security assessment purposes.
