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

## Folder structure

```
03-orchestration (Kubernetes)/
+-- README.md          # this file: CLOUD-007..008 registry
|
+-- K8s-attacks/       # CLOUD-007: exposed/misconfigured clusters (kube-hunter, etcd)
+-- K8s-auditing/      # CLOUD-008: CIS audit (kube-bench) + Pod Security Standards
```

---

## Recommended operational flow

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

## Reference tools

| tool | type | role | main use case |
| :--- | :--- | :--- | :--- |
| `kubectl` | k8s cli | official | interaction with the cluster |
| `kube-hunter` | scanner | offensive | discovery of exposed components |
| `Peirates` | exploitation | offensive | post-exploitation on k8s |
| `kube-bench` | cis auditor | defensive | cis conformity audit |
| `Pod Security` / `Kyverno` | admission | defensive | blocking of dangerous pods |
| `Falco` | runtime security | defensive | runtime detection |

> **Recommended modern tool:** `kube-hunter`/`Peirates` (offensive) and `kube-bench` + Pod Security Standards + `Falco` (defensive). See `../Tooling/` for the cross-cutting cloud scanners.

---

## Finding registry - orchestration (Kubernetes)

| id | description | severity | subfolder |
| :--- | :--- | :---: | :--- |
| `CLOUD-007` | exposed/misconfigured k8s cluster: secret theft and control of the control plane | `Critical` | `K8s-attacks/` |
| `CLOUD-008` | k8s auditing: cis benchmark (kube-bench) + pod security standards (hardening) | `High` | `K8s-auditing/` |

---

## MITRE ATT&CK mapping - aggregated

> Reference: MITRE ATT&CK for Containers.

| tactic | technique | mitre id | related finding |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | CLOUD-007, CLOUD-008 |
| credential access | unsecured credentials: container api | `T1552.007` | CLOUD-007, CLOUD-008 |
| privilege escalation | escape to host | `T1611` | CLOUD-008 (prevention) |
| execution | deploy container | `T1610` | CLOUD-007, CLOUD-008 |
| discovery | container and resource discovery | `T1613` | CLOUD-007 |

---

> **Note:** All documented activities were conducted on a Kubernetes lab cluster owned by the author. Unauthorized access to third-party clusters is a crime. Techniques are documented for educational and authorized security assessment purposes.
