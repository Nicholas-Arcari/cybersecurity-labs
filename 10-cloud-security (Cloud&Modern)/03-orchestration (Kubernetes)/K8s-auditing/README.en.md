> **English** | [Italiano](README.md)

# Kubernetes Auditing - CIS Benchmark and Pod Security

> - **Phase:** Cloud Security - Kubernetes Hardening (Defense)
> - **Category:** Defensive - conformity audit and cluster hardening
> - **Prerequisites:** Access to the cluster (nodes/control plane) for the audit; kube-bench; knowledge of the Pod Security Standards
> - **Output:** Finding CLOUD-008; CIS conformity report; cluster hardening; closing of the exposures exploited in `../K8s-attacks/`

- **Operating Environment:** Author's lab Kubernetes cluster, kube-bench
- **Main tools:** kube-bench, Pod Security Standards/Admission, kubectl

---

## Executive Summary

Kubernetes auditing is the direct defensive countermeasure to the attacks documented in `../K8s-attacks/` (CLOUD-007). Since the security of a cluster is the sum of many correct configurations, and complexity makes error probable, a systematic way to verify the security posture is needed - not by hand, but against a recognized baseline. The **CIS Kubernetes Benchmark** is this baseline, and **kube-bench** is the tool that measures the cluster's conformity to it.

Finding CLOUD-008 documents the audit and hardening cycle: kube-bench runs hundreds of checks on the control plane, nodes, etcd and policies, comparing them with the CIS Benchmark and producing a PASS/FAIL/WARN report with the correction recommendations. It is the Kubernetes equivalent of Lynis for Linux (`../../../08-defense-hardenings/04-hardening-scripts/linux-hardening/`): it makes the cluster's hardening objective, measurable and repeatable.

The second pillar are the **Pod Security Standards** (and the Pod Security Admission that enforces them): policies that prevent the deployment of dangerous pods (privileged, with host mount, with excessive capabilities) - exactly the pods an attacker would use for the escape (CLOUD-006) or the escalation. The audit finds the weaknesses, the Pod Security Standards prevent them at the admission level.

---

## Folder Structure

```
K8s-auditing/
+-- README.md      # this file: CIS audit (kube-bench) + Pod Security (CLOUD-008)
+-- img/           # kube-bench report and policies
```

---

## CIS Audit with kube-bench

**Finding ID:** `CLOUD-008` | **Severity:** `High` (cluster hardening; closes the control plane exposures and prevents the dangerous pods exploited in CLOUD-006/007)

### Operational Context

kube-bench runs the checks of the CIS Kubernetes Benchmark against the cluster components: it verifies the permissions of the configuration files, the API server flags, the security of etcd, the RBAC policies. The report indicates what is conformant and what is not, with the correction recommendation for every FAIL.

### PoC - Running the CIS audit

```Bash
# kube-bench runs the CIS checks on the cluster (control plane + nodes)
kube-bench run --targets master,node,etcd,policies
```

```
[INFO] 1 Master Node Security Configuration
[PASS] 1.2.1 Ensure --anonymous-auth is set to false
[FAIL] 1.2.16 Ensure --encryption-provider-config is set     <-- unencrypted Secrets (CLOUD-008)
[FAIL] 2.1 Ensure etcd is configured with client cert auth   <-- etcd without auth (CLOUD-008)
[WARN] 5.2.1 Minimize privileged containers (PodSecurity)

== Summary == 42 checks PASS, 8 FAIL, 11 WARN
```

Every FAIL corresponds to an exploitable exposure: 1.2.16 (unencrypted Secrets) and 2.1 (etcd without auth) are exactly the vectors of CLOUD-007. The audit makes them visible before the attacker.

### PoC - Pod Security Standards (prevention of dangerous pods)

```YAML
# Pod Security Admission: blocks privileged/host-mount pods at the namespace level
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted   # <-- "restricted" policy
```

```Bash
# Attempt to deploy a privileged pod -> rejected by the admission
kubectl apply -f privileged-pod.yaml
```

```
Error: pods "evil" is forbidden: violates PodSecurity "restricted:latest":
  privileged (container must not set securityContext.privileged=true)   <-- escape prevented (CLOUD-008)
```

### Defensive Operations

- **Cycle audit, hardening, re-audit:** run kube-bench, correct the priority FAILs (etcd, Secret encryption, anonymous auth), re-run to confirm
- **Priority corrections:** Secret encryption at rest, mutual TLS on etcd, disabling of anonymous access, least-privilege RBAC
- **Pod Security Standards:** apply the `restricted` policy to the application namespaces to block privileged pods, host mounts and excessive capabilities (prevents CLOUD-006)
- **Automation:** integrate kube-bench into CI/CD and the periodic audit; pair with policy engines like OPA/Gatekeeper or Kyverno for custom policies beyond the Pod Security Standards

---

## Lab Experience

The value of kube-bench was translating the vastness of Kubernetes into an actionable checklist. After seeing in `../K8s-attacks/` how broad the cluster surface is, the idea of verifying it by hand was daunting; kube-bench reduced it to a PASS/FAIL report with the corrections. Seeing the FAILs correspond exactly to the vectors I had exploited from the offensive side (etcd without auth, unencrypted Secrets) made the symmetry concrete: the same cluster I had attacked, I was now hardening by closing the FAILs one by one.

The Pod Security Standards were the most powerful discovery on the preventive plane. In the containers module I had used privileged pods for the escape; here, with the `restricted` policy applied to the namespace, the deployment of a privileged pod was simply rejected at admission. The difference between detecting a dangerous pod afterwards (detection) and preventing its deployment beforehand (admission control) is the difference between reactive and preventive defense. Blocking the entire class of dangerous pods upstream is more robust than chasing the individual ones.

The reflection was on the necessity of automation. A real cluster changes continuously - new deploys, new configurations - and the security posture drifts with every change. A one-off audit is not enough; kube-bench in CI/CD and admission policies that impose the constraints at every deploy are needed. Kubernetes security is not a state one reaches but a constraint one maintains, and maintaining it requires automation.

---

## Theoretical Analysis: Baseline and Admission Control as Scalable Defense

Baseline auditing (CIS) solves the complexity problem with the same principle as traditional hardening (Lynis, CIS Benchmark of module 08): turning "is it secure?" - a subjective and unmanageable question on a complex system - into "is it conformant to this recognized baseline?" - an objective and verifiable question. The baseline encapsulates the shared security knowledge into a checklist, making hardening repeatable and independent of the expert. One does not need to know by heart every secure Kubernetes configuration; one needs to verify conformity to the CIS.

Admission control (Pod Security Standards) introduces a second principle: preventing at the door instead of detecting afterwards. A dangerous pod can be detected after deployment (detection, reactive) or rejected before (admission, preventive). Admission control is structurally superior because it acts on the creation flow: no pod that violates the policy enters the cluster, regardless of who deploys it. It shifts security from monitoring what happens to constraining what can happen, and this is the scalable model for a system where deploys are continuous and automated.

Together, audit and admission cover the two times of the defense: the audit verifies the existing state (what is misconfigured now), the admission constrains the future changes (what cannot be deployed). In a dynamic system like Kubernetes, both are needed - correcting the present and constraining the future - because security is not a photograph but a film, and it must be defended in every frame.

---

## Real-World Scenario: Hardening in Action

> Defensive perspective: how the audit and the admission control would have countered the attack of CLOUD-007.

```
[CLOUD-008] kube-bench + Pod Security Standards applied
        |
        v
Attacker scans the cluster (kube-hunter) -> anonymous access DISABLED
        |                                   -> etcd with mutual TLS, not exposed
        v
FAILs corrected by the audit: the vectors of CLOUD-007 are closed upstream
        |
        v
Attacker compromises a pod -> attempts to deploy a privileged pod for the escape
        |
        v
Pod Security "restricted" REJECTS the privileged pod -> escape (CLOUD-006) prevented
        |
        v
Attack contained: no path to the control plane, no escape possible
```

**Defensive value:** the audit closes the control plane exposures (the vectors of CLOUD-007) and the Pod Security Standards prevent the dangerous pods (the vector of CLOUD-006). The defense is in depth: even if the attacker compromises a workload, they find neither an exposed control plane nor the possibility of deploying pods for the escape.

**Defensive lesson:** the defense of Kubernetes is built before the attack, in the conformity to the baseline and in the admission policies. The audit finds what is already wrong; the admission control prevents wrongdoing in the future. It is the same philosophy as the hardening of module 08, applied to the complexity of the cluster: making insecurity hard, not just detectable.

---

## Reference Tools

| Tool | Type | Role | Main use case |
| :--- | :--- | :--- | :--- |
| `kube-bench` | CIS auditor | Defensive | Verification of conformity to the CIS Kubernetes Benchmark |
| `Pod Security Admission` | Admission control | Defensive | Blocking of dangerous pods at the namespace level |
| `OPA/Gatekeeper` | Policy engine | Defensive | Custom admission policies (beyond the Pod Security Standards) |
| `Kyverno` | Policy engine | Defensive | K8s-native policies, alternative to OPA |
| `kubescape` | Security scanner | Defensive | Framework-based audit (NSA/MITRE) |

> **Recommended modern tool:** `kube-bench` for the CIS audit, the native `Pod Security Standards` as the first line of admission control, and `Kyverno`/`OPA-Gatekeeper` for the custom policies. `kubescape` for a framework-based audit (NSA/MITRE). The combination audit + admission covers the present state and the future changes.

---

## MITRE ATT&CK Mapping

> Attack techniques **prevented** by the cluster hardening.

| Tactic (prevented) | Technique | MITRE ID | Role of the control |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Closing of the control plane exposures (CLOUD-008) |
| Privilege Escalation | Escape to Host | `T1611` | Pod Security blocks the privileged pods (prevents CLOUD-006) |
| Credential Access | Unsecured Credentials: Container API | `T1552.007` | Secret encryption + etcd auth (prevents CLOUD-007) |
| Execution | Deploy Container | `T1610` | Admission control on the deployable pods |

| Defensive countermeasure (D3FEND) | D3FEND ID | Application |
| :--- | :--- | :--- |
| Platform Hardening | `D3-PH` | Conformity to the CIS Kubernetes Benchmark |
| Mandatory Access Control | `D3-MAC` | Pod Security Standards / admission policies |

---

> **Note:** All documented activities were conducted on a Kubernetes lab cluster owned by the author. Auditing is a non-intrusive defensive control. Techniques are documented for educational and defensive purposes in an authorized context.
