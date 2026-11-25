> **English** | [Italiano](README.md)

# 02 - Containers Security (Docker)

> - **Phase:** Cloud Security - Container Security
> - **Category:** Defensive + Offensive - supply chain and isolation
> - **Prerequisites:** Docker; images to analyze; for the offensive, access to a misconfigured container
> - **Output:** Findings CLOUD-005..006; security of the images (build) and of the runtime (isolation)

---

## Introduction

The "Modern" in the module name refers first of all to this: containers changed the way of distributing and running software. A container packages an application with all its dependencies into a portable, lightweight and reproducible artifact. But this convenience introduces two new security surfaces: what is inside the image (the supply chain) and how isolated the running container is (the runtime).

The fundamental difference from virtual machines defines all container security: a container is not isolated by a hypervisor but shares the host's kernel, protected only by kernel mechanisms (namespaces, cgroups, capabilities). The isolation is not a physical barrier but a configuration - effective if correct, fragile if not.

The section covers the two surfaces:

1. **Image Scanning (CLOUD-005):** the security of the build. An image inherits the vulnerabilities of all its layers (base OS, libraries, dependencies); Trivy scans them before deployment. It is a supply chain control, to be integrated into CI/CD (shift-left).

2. **Runtime Security (CLOUD-006):** the security of the execution. The misconfigurations (mounted Docker socket, `--privileged`, excessive capabilities) allow the container escape - the evasion toward the host, which nullifies the isolation.

The two findings cover the life cycle: scanning prevents the known vulnerabilities before deployment, runtime security prevents (and detects) the evasion during execution. Together they answer the two questions of container security: "what is inside?" and "how contained is it?".

---

## Folder Structure

```
02-containers-security (Docker)/
+-- README.md              # this file: CLOUD-005..006 registry
|
+-- image-scanning/        # CLOUD-005: CVE scanning of the images (Trivy) - build
+-- runtime-security/      # CLOUD-006: container escape techniques - runtime
```

---

## Recommended Operational Flow

```
[BUILD] Image built
         |
         v
[1] Image Scanning (image-scanning/)
     +-- Trivy -> CVEs in the layers -> block deploy if critical (CLOUD-005)
              |
              v
[DEPLOY] Container running
         |
         v
[2] Runtime Security (runtime-security/)
     +-- least-privilege config (no socket, no privileged, non-root)
     +-- Falco -> escape detection at runtime (CLOUD-006)
              |
              v
[OUTPUT] Container secure from build to runtime; escape prevented and detected
```

---

## Reference Tools

| Tool | Phase | Type | Main use case |
| :--- | :--- | :--- | :--- |
| `Trivy` | Build | Defensive | CVE scanning of images (standard) |
| `Dive` | Build | Analysis | Inspection of the layers |
| `Falco` | Runtime | Defensive | Runtime detection of the escapes |
| `deepce` | Runtime | Offensive | Enumeration of the escape paths |
| `seccomp`/`AppArmor` | Runtime | Defensive | Restriction of the syscalls/capabilities |

> **Recommended modern tool:** `Trivy` for the build (supply chain), `Falco` for the runtime (escape detection). The combination covers both surfaces. See `../Tooling/` for the broader cloud scanners.

---

## Finding Registry - Containers Security

| ID | Description | Severity | Subfolder |
| :--- | :--- | :---: | :--- |
| `CLOUD-005` | Image scanning: known vulnerabilities (CVE) in the images before deployment | `Medium` | `image-scanning/` |
| `CLOUD-006` | Container escape via Docker socket: evasion and root on the host | `Critical` | `runtime-security/` |

---

## MITRE ATT&CK Mapping - Aggregated

| Tactic | Technique | MITRE ID | Related Finding |
| :--- | :--- | :--- | :--- |
| Initial Access | Supply Chain Compromise | `T1195` | CLOUD-005 |
| Privilege Escalation | Escape to Host | `T1611` | CLOUD-006 |
| Execution | Deploy Container | `T1610` | CLOUD-006 |
| Discovery | Container and Resource Discovery | `T1613` | CLOUD-006 |

---

> **Note:** All documented activities were conducted on hosts and containers owned by the author. Container escape on third-party infrastructures without authorization is a crime. Image scanning is a non-intrusive defensive control. Techniques are documented for educational and authorized security assessment purposes.
