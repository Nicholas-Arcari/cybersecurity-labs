> **English** | [Italiano](README.md)

# Container image scanning - CVEs in Docker images

> - **Phase:** Cloud Security - Container Security (Supply Chain / Vulnerability Management)
> - **Category:** Defensive - static analysis of the images before deployment
> - **Prerequisites:** Docker images to analyze; Trivy/Grype/Dive; integration in the CI/CD pipeline (ideally)
> - **Output:** Finding CLOUD-005; inventory of the known vulnerabilities in the images; base for patching and blocking vulnerable deployments

- **Operating Environment:** Workstation/CI, Docker, Trivy
- **Main tools:** Trivy, Grype, Clair, Dive

---

## Executive summary

A Docker image is not an atomic artifact: it is a stack of layers that includes a base operating system, libraries, application dependencies and the code. Each of these strata can contain known vulnerabilities (CVE), and an image "pulled" from a registry - even an official one - inherits all the vulnerabilities of its components. Image scanning is the static analysis that identifies them before the image is deployed to production.

Finding CLOUD-005 documents the scanning of the images with Trivy, the de facto standard: a scanner that compares the packages present in each layer with the databases of known vulnerabilities and produces an inventory of the CVEs, ordered by severity. It is a **supply chain security** control: it guarantees that what one puts into production does not carry known and fixable vulnerabilities.

The value is preventive and integrates into the CI/CD pipeline: an automatic scan at each build blocks the deployment of images with critical vulnerabilities, shifting security "left" (shift-left) - from the runtime, where the problem is costly, to the build, where it is cheap to fix.

---

## Folder structure

```
image-scanning/
+-- README.md      # this file: CVE scanning of the images (CLOUD-005)
+-- img/           # Trivy report and layer analysis with Dive
```

---

## Image scanning with trivy

**Finding ID:** `CLOUD-005` | **Severity:** `Medium` (detection of known vulnerabilities in the images before deployment; the real severity depends on the CVEs found)

### Operational context

Trivy scans an image layer by layer, identifies the installed packages (OS and application) and compares them with the CVE databases. The result is a list of vulnerabilities with severity, affected version and version that fixes them - an action list for patching.

### PoC - scanning an image

```Bash
# Complete scan of an image (OS CVEs + application dependencies)
trivy image imagename:tag
```

```
imagename:tag (debian 11.3)
Total: 47 (UNKNOWN: 0, LOW: 12, MEDIUM: 23, HIGH: 10, CRITICAL: 2)

LIBRARY        VULNERABILITY   SEVERITY   INSTALLED   FIXED       TITLE
openssl        CVE-2022-....   CRITICAL   1.1.1k      1.1.1n      OpenSSL infinite loop   <-- (CLOUD-005)
libc6          CVE-2021-....   HIGH       2.31        2.31-13     glibc buffer overflow
```

### PoC - layer analysis (dive)

```Bash
# Dive: analyzes the layers to understand where the vulnerabilities/waste are introduced
dive imagename:tag
```

```
# Dive shows layer by layer what adds weight and what introduces vulnerable packages
# -> often the obsolete base image is the cause: updating it fixes many CVEs
```

### PoC - CI/CD integration (shift-left)

```Bash
# In pipeline: fails the build if there are CRITICAL CVEs (blocks the vulnerable deploy)
trivy image --exit-code 1 --severity CRITICAL imagename:tag
```

```
[!] exit code 1: CRITICAL CVEs present -> build blocked   <-- vulnerable deploy prevented (CLOUD-005)
```

### Remediation and operations

- **Minimal and updated base images:** starting from small (distroless, alpine) and updated images drastically reduces the surface; many CVEs disappear by updating the base layer
- **Patching guided by the fixed version:** Trivy indicates the version that fixes; update the dependencies to that version
- **Shift-left in CI/CD:** automatic scan at each build, blocking on the critical CVEs; security must be shifted to the build, not left to the runtime
- **Registry scanning:** periodically scan also the images already in the registry (new CVEs emerge after the build); Trivy/Grype support continuous scanning

---

## Lab experience

The most immediate lesson was how much vulnerability an "innocent" image carries. An image based on an outdated version of Debian, downloaded without thinking, carried dozens of CVEs inherited from the base system - none introduced by my code, all from the foundations. This made concrete the concept of supply chain: the security of a container is not just the code I put in, but everything I inherit from the underlying layers.

Dive added the dimension of the cause. Seeing layer by layer where the vulnerable packages came from clarified that the most effective countermeasure is not patching individual packages but starting from a better base image: switching to a minimal and updated image, most of the CVEs disappeared in one go. The choice of the base layer is the most impactful security decision in the construction of an image.

The integration into CI/CD closed the loop of preventive value. A `trivy image --exit-code 1` in the pipeline turns the scan from an occasional activity into an automatic control: no image with critical CVEs reaches production, without depending on manual diligence. It is the essence of shift-left: making security an automatic step of the build, not a subsequent control.

---

## Theoretical analysis: supply chain and inherited security

A container embodies the principle that security is inherited along the supply chain. The final image is the sum of components the author did not write: the base system, the system libraries, the language dependencies, the third-party packages. Each is a potential vector, and the security of the whole is no better than that of its most vulnerable component. The application code, often the only one the author focuses on, is frequently the smallest part of the surface.

This shifts the focus of security from writing secure code to managing secure dependencies. Most of an image's vulnerabilities are not in the code but in its inherited foundations, and managing them is a problem of inventory and updating, not programming. Image scanning is the tool that makes this inherited surface visible, otherwise invisible: without scanning, the vulnerabilities of the underlying layers are present but unknown.

The shift-left principle reflects an economics of correction: a CVE found at the build costs a version update; the same CVE exploited in production costs an incident. Shifting the control as far upstream as possible (build instead of runtime) minimizes the cost of the correction and maximizes the probability that it happens. Supply chain security is not added at the end, it is integrated at the beginning - and that is why image scanning belongs to the pipeline, not to the SOC.

---

## Reference tools

| tool | type | role | main use case |
| :--- | :--- | :--- | :--- |
| `Trivy` | vulnerability scanner | defensive | cve scanning of images, filesystem, iac (standard) |
| `Grype` | vulnerability scanner | defensive | alternative to trivy, sbom integration (syft) |
| `Clair` | vulnerability scanner | defensive | static scanning integrated in the registries |
| `Dive` | layer analysis | analysis | inspection of the layers, optimization and package origin |
| `Docker Scout` | vulnerability scanner | defensive | scanner integrated in docker |

> **Recommended modern tool:** `Trivy` (Aqua Security) is the de facto standard: lightweight, fast, it scans images, filesystems, repositories and IaC, and integrates into every CI/CD pipeline. `Dive` as a complement to understand the origin of the problems in the layers. See also `../../Tooling/`.

---

## MITRE ATT&CK mapping

| tactic (prevented) | technique | mitre id | role of the control |
| :--- | :--- | :--- | :--- |
| initial access | supply chain compromise | `T1195` | detection of vulnerable components in the images (CLOUD-005) |
| execution | exploitation for client execution | `T1203` | prevention of the exploitation of known cves in containers |
| initial access | exploit public-facing application | `T1190` | reduction of the exploitable surface in exposed containers |

| defensive countermeasure (d3fend) | d3fend id | application |
| :--- | :--- | :--- |
| application vulnerability assessment | `D3-AVA` | scanning of the images for known vulnerabilities |
| software update | `D3-SU` | patching guided by the fixed versions indicated by trivy |

---

> **Note:** All documented activities were conducted on images and environments owned by the author. Image scanning is a defensive and non-intrusive control. Techniques are documented for educational and defensive purposes in an authorized context.
