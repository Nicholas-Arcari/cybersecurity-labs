> **English** | [Italiano](LAB_SETUP.md)

# LAB_SETUP.md - Lab Topology and Configuration

> Technical reference document for reproducing the lab environment used in this repository.
> All testing sessions were performed in a virtualized environment isolated from the production network.

---

## Table of Contents

- [Hardware requirements](#hardware-requirements)
- [Virtualization software](#virtualization-software)
- [Virtual machines](#virtual-machines)
- [Network topologies](#network-topologies)
- [NAT configuration (Modules 01-02)](#nat-configuration-modules-01-02)
- [Network Bridge configuration (Modules 03-04)](#network-bridge-configuration-modules-03-04)
- [Modules by topology](#modules-by-topology)
- [Snapshots and VM management](#snapshots-and-vm-management)
- [Reproducing the lab](#reproducing-the-lab)
- [Containerized Web Targets (Docker Compose)](#containerized-web-targets-docker-compose)
- [Demo Recording with Asciinema](#demo-recording-with-asciinema)

---

## Hardware Requirements

| Resource | Minimum | Recommended |
| :--- | :--- | :--- |
| Total host RAM | 8 GB | 16 GB |
| CPU | Quad-core, VT-x enabled | 8 cores, VT-x/AMD-V |
| Host disk | 100 GB free | 200 GB SSD |
| Network adapter | 1x (NAT sufficient) | 1x (Bridge requires LAN access) |

---

## Virtualization Software

| Software | Version used | Notes |
| :--- | :--- | :--- |
| VirtualBox | 7.0.x | Main hypervisor, free |
| VirtualBox Extension Pack | same version | Required for USB 3.0 and advanced network adapters |
| Host OS | Any (Linux/Windows/macOS) | Lab executed on Linux host |

---

## Virtual Machines

### Kali Linux (Attacker)

| Parameter | Value |
| :--- | :--- |
| OS | Kali Linux 2024.x (rolling) |
| RAM | 4096 MB |
| CPU | 2 vCPU |
| Disk | 80 GB (thin provisioned) |
| Network adapters | 2x (Adapter 1: NAT or Bridge depending on module) |
| Pre-operative snapshots | Recommended before every exploitation session |

### Windows 10 (Primary Target)

| Parameter | Value |
| :--- | :--- |
| OS | Windows 10 Pro x64 (unpatched, vulnerable by design) |
| RAM | 2048 MB |
| CPU | 2 vCPU |
| Disk | 60 GB |
| Security configuration | Firewall disabled, UAC reduced, SMBv1 enabled |
| Configured users | `Administrator` (weak password), `user1`, `svc_backup` |
| Exposed services | SMB (445), RDP (3389), HTTP (8080), SNMP (161 UDP) |

### Ubuntu Linux (Secondary Target - Linux PrivEsc)

| Parameter | Value |
| :--- | :--- |
| OS | Ubuntu Server 20.04 LTS |
| RAM | 1024 MB |
| CPU | 1 vCPU |
| Disk | 20 GB |
| Security configuration | Intentionally misconfigured for PrivEsc |
| Configured users | `ubuntu` (low-privilege), `www-data` (web service) |
| Exposed services | SSH (22), HTTP (80), misconfigured SUID services |

---

## Network Topologies

The lab used two distinct network modes depending on the testing phase.
The choice depends on the objective: NAT for maximum isolation, Bridge for simulating
realistic scenarios on a LAN segment.

```
+-----------------------------------------------------------+
|                    NAT TOPOLOGY                           |
|                  (Modules 01-02)                          |
|                                                           |
|  [Host OS] <---NAT---> [VirtualBox NAT Gateway]           |
|                               |                           |
|                    +----------+----------+                |
|                    |                     |                |
|             [Kali Linux]        [Windows 10]              |
|            10.0.2.15             10.0.2.3                 |
|           (attacker)            (target)                  |
|                                                           |
|  NAT Gateway: 10.0.2.1   DHCP: 10.0.2.2                   |
+-----------------------------------------------------------+

+-----------------------------------------------------------+
|               NETWORK BRIDGE TOPOLOGY                     |
|                  (Modules 03-04)                          |
|                                                           |
|  [LAN Router] <---> [Host OS NIC] <---> [VirtualBox]      |
|       |                                     |             |
|  [Other LAN hosts]              +------------+----------+  |
|                                |                       |  |
|                         [Kali Linux]        [Windows]  |  |
|                        192.168.0.110      192.168.0.109|  |
|                         (attacker)           (target)  |  |
|                                                        |  |
|  Gateway: 192.168.0.1   Subnet: 192.168.0.0/24         |  |
+-----------------------------------------------------------+
```

---

## NAT Configuration (Modules 01-02)

Used for: passive/active reconnaissance, vulnerability assessment, phases that
do not require direct visibility on the real LAN.

### IP Addresses (NAT)

| VM | Hostname | IP | Role |
| :--- | :--- | :--- | :--- |
| Kali Linux | kali | `10.0.2.15` | Attacker |
| Windows 10 | WIN10-TARGET | `10.0.2.3` | Primary target |
| VirtualBox Gateway | - | `10.0.2.1` | Default gateway |
| VirtualBox DHCP | - | `10.0.2.2` | DHCP server |

### VirtualBox Configuration (NAT)

```
VM Settings > Network > Adapter 1:
  - Attached to: NAT
  - (Advanced) Port Forwarding: not required for internal traffic
```

### Optional Port Forwarding (host to VM access in NAT)

```
Host: 127.0.0.1:2222  -->  Guest: 10.0.2.15:22   (SSH Kali)
Host: 127.0.0.1:8080  -->  Guest: 10.0.2.3:8080  (HTTP Windows)
Host: 127.0.0.1:3389  -->  Guest: 10.0.2.3:3389  (RDP Windows)
```

VirtualBox configuration:

```
VM Settings > Network > Adapter 1 > Advanced > Port Forwarding > [+]
```

---

## Network Bridge Configuration (Modules 03-04)

Used for: active exploitation, privilege escalation, post-exploitation,
phases simulating an attacker already on the same network as the target.

> **Security note:** In Bridge mode, VMs are visible on the physical LAN.
> ALWAYS run in a controlled network environment (isolated home network or dedicated VLAN).
> Never on a corporate or public network.

### IP Addresses (Bridge)

| VM | Hostname | IP | Role |
| :--- | :--- | :--- | :--- |
| Kali Linux | kali | `192.168.0.110` | Attacker |
| Windows 10 | WIN10-TARGET | `192.168.0.109` | Primary target |
| LAN Gateway | router | `192.168.0.1` | Default gateway |
| Subnet | - | `192.168.0.0/24` | Lab segment |

### VirtualBox Configuration (Bridge)

```
VM Settings > Network > Adapter 1:
  - Attached to: Bridged Adapter
  - Name: [select the host's physical NIC]
  - Promiscuous Mode: Deny (or Allow VMs for advanced scenarios)
```

> IPs 192.168.0.109 and 192.168.0.110 may vary. Assign static IPs
> or verify with `ip a` (Kali) and `ipconfig` (Windows) at the beginning of each session.

### Static IP Assignment on Kali (Bridge)

```Bash
sudo ip addr add 192.168.0.110/24 dev eth0
sudo ip route add default via 192.168.0.1
```

Persistent configuration in `/etc/network/interfaces`:

```
auto eth0
iface eth0 inet static
  address 192.168.0.110
  netmask 255.255.255.0
  gateway 192.168.0.1
```

---

## Modules by Topology

| Module | Topology | Kali IP | Target IP |
| :--- | :--- | :--- | :--- |
| `01-recon` | NAT | 10.0.2.15 | 10.0.2.3 |
| `02-vulnerability-assessment` | NAT | 10.0.2.15 | 10.0.2.3 |
| `03-web-attacks` | NAT | 10.0.2.15 | 10.0.2.3 |
| `04-system-exploitation` | Bridge | 192.168.0.110 | 192.168.0.109 |
| `05-social-engineering` | Bridge | 192.168.0.110 | 192.168.0.109 |
| `06-wireless-security` | Bridge | 192.168.0.110 | N/A (physical AP) |
| `07-post-exploitation` | Bridge | 192.168.0.110 | 192.168.0.109 |
| `08-defense-hardenings` | NAT | 10.0.2.15 | N/A (self) |
| `09-digital-forensics` | NAT | N/A | local disk images |
| `10-cloud-security` | Internet | N/A | cloud endpoints |

---

## Snapshots and VM Management

### Recommended Snapshot Strategy

```
[BASE SNAPSHOT]                          <- clean state post-installation
      |
      +-- [PRE-RECON SNAPSHOT]           <- after network configuration
      |         |
      |         +-- [PRE-EXPLOIT SNAPSHOT] <- after vuln assessment
      |                   |
      |                   +-- [POST-SHELL SNAPSHOT] <- after initial access
      |                             |
      |                             +-- [PRE-PRIVESC SNAPSHOT]
```

### VirtualBox CLI Commands (vboxmanage)

```Bash
# Create snapshot
vboxmanage snapshot "Kali Linux" take "pre-exploitation" --description "Before MS17-010"

# List snapshots
vboxmanage snapshot "Kali Linux" list

# Restore snapshot
vboxmanage snapshot "Kali Linux" restore "pre-exploitation"

# Delete snapshot
vboxmanage snapshot "Kali Linux" delete "pre-exploitation"
```

---

## Reproducing the Lab

### Prerequisites

```Bash
# Verify hardware virtualization is enabled
grep -E '(vmx|svm)' /proc/cpuinfo | head -1

# Install VirtualBox (Debian/Ubuntu/Kali)
sudo apt install virtualbox virtualbox-ext-pack

# Download images
# Kali Linux:   https://www.kali.org/get-kali/#kali-virtual-machines (preconfigured OVA)
# Windows 10:   https://www.microsoft.com/evalcenter/download-windows-10-enterprise (90-day eval ISO)
```

### Setup Sequence

1. Import Kali Linux OVA into VirtualBox (`File > Import Appliance`)
2. Install Windows 10 from ISO in a new VM with parameters from the table above
3. Configure Windows 10 as target (disable firewall, enable SMBv1, create users)
4. Choose the network topology based on the module to be executed
5. Take a base snapshot of both VMs before starting
6. Verify connectivity with `ping` before every session

### Connectivity Verification (NAT)

```Bash
# From Kali
ping 10.0.2.3 -c 3
nmap -sn 10.0.2.3
```

### Connectivity Verification (Bridge)

```Bash
# From Kali
ping 192.168.0.109 -c 3
nmap -sn 192.168.0.109
```

### Windows Target Configuration (PowerShell script - run as Administrator)

```Bash
# Disable firewall
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

# Enable SMBv1 (for MS17-010 testing)
Set-SmbServerConfiguration -EnableSMB1Protocol $true -Force

# Enable RDP
Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name fDenyTSConnections -Value 0
Enable-NetFirewallRule -DisplayGroup "Remote Desktop"

# Create low-privilege user for testing
net user user1 Password123! /add
net user svc_backup ServicePass1! /add
net localgroup "Remote Desktop Users" user1 /add
```

---

## Containerized Web Targets (Docker Compose)

For module 03 (Web Attacks) and parts of module 02 labs, a `docker-compose.yml` is available in the repository root providing containerized web targets. This is **complementary** to the VirtualBox topology - it does not replace it.

### What Docker Compose Covers

| Service | Port | Module | Target for |
| :--- | :--- | :--- | :--- |
| DVWA | `localhost:8080` | 03-web-attacks | SQLi, XSS, Command Injection, CSRF |
| DVGA | `localhost:5013` | 03-web-attacks | GraphQL Introspection, IDOR, Batching |
| Juice Shop | `localhost:3000` | 03-web-attacks | Full OWASP Top 10 (100+ challenges) |

### What Still Requires VirtualBox

System Exploitation (module 04), Post-Exploitation (module 07), Wireless (module 06) labs and all Windows-based scenarios require the VMs documented in previous sections.

### Quick Start

```Bash
# Start all web targets
cd cybersecurity-labs/
docker compose up -d

# Start only DVWA
docker compose up dvwa dvwa-db -d

# Check status
docker compose ps

# Stop everything
docker compose down

# Stop and remove volumes (full reset)
docker compose down -v
```

---

## Demo Recording with Asciinema

To record demonstrative terminal sessions of labs, use [asciinema](https://asciinema.org/). Recordings complement screenshots (static PoC) and show the complete operational workflow.

### Installation

```Bash
sudo apt install asciinema
```

### Recording

```Bash
# Record a session (saves locally as .cast)
asciinema rec demo_nmap_scan.cast

# Record with title and limited idle time (recommended)
asciinema rec -t "Nmap 3-Phase Scan Pipeline" --idle-time-limit 3 nmap_pipeline.cast

# End recording
exit   # or Ctrl+D
```

### Embedding in READMEs (MkDocs)

To include a recording in a README visible on MkDocs/GitHub Pages, use the JavaScript player:

```html
<div id="demo-player"></div>
<script src="https://asciinema.org/a/XXXXX.js" id="asciicast-XXXXX" async></script>
```

Or in Markdown format (GitHub-compatible):

```markdown
[![asciicast](https://asciinema.org/a/XXXXX.svg)](https://asciinema.org/a/XXXXX)
```

### Recommended Labs to Record

| Lab | File | Target Duration |
| :--- | :--- | :--- |
| Nmap 3-phase scan | `01-recon/.../nmap/` | 2-3 min |
| Manual SQLi on DVWA | `03-web-attacks/.../sql-injection/` | 3-5 min |
| WinPEAS enumeration | `04-system-exploitation/.../winpeas/` | 2-3 min |
| Hashcat mask attack | `04-system-exploitation/.../hashcat/` | 1-2 min |
| Mimikatz credential dump | `07-post-exploitation/.../mimikatz/` | 2-3 min |

---

> **Disclaimer:** This lab is intentionally configured in a vulnerable manner
> for educational purposes. Do not replicate this configuration on production systems.
> Always run in an isolated environment. The documented IPs and configurations
> refer exclusively to the virtualized testing environment.
