> **English** | [Italiano](LAB_SETUP.md)

# LAB_SETUP.md - lab topology and configuration

> Technical reference document for reproducing the lab environment used in this repository.
> All testing sessions were performed in a virtualized environment isolated from the production network.

---

## Table of contents

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

## Hardware requirements

| resource | minimum | recommended |
| :--- | :--- | :--- |
| total host ram | 8 gb | 16 gb |
| cpu | quad-core, vt-x enabled | 8 cores, vt-x/amd-v |
| host disk | 100 gb free | 200 gb ssd |
| network adapter | 1x (nat sufficient) | 1x (bridge requires lan access) |

---

## Virtualization software

| software | version used | notes |
| :--- | :--- | :--- |
| virtualbox | 7.0.x | main hypervisor, free |
| virtualbox extension pack | same version | required for usb 3.0 and advanced network adapters |
| host os | any (linux/windows/macos) | lab executed on linux host |

---

## Virtual machines

### Kali Linux (attacker)

| parameter | value |
| :--- | :--- |
| os | kali linux 2024.x (rolling) |
| ram | 4096 mb |
| cpu | 2 vcpu |
| disk | 80 gb (thin provisioned) |
| network adapters | 2x (adapter 1: nat or bridge depending on module) |
| pre-operative snapshots | recommended before every exploitation session |

### Windows 10 (primary target)

| parameter | value |
| :--- | :--- |
| os | windows 10 pro x64 (unpatched, vulnerable by design) |
| ram | 2048 mb |
| cpu | 2 vcpu |
| disk | 60 gb |
| security configuration | firewall disabled, uac reduced, smbv1 enabled |
| configured users | `Administrator` (weak password), `user1`, `svc_backup` |
| exposed services | smb (445), rdp (3389), http (8080), snmp (161 udp) |

### Ubuntu Linux (secondary target - Linux PrivEsc)

| parameter | value |
| :--- | :--- |
| os | ubuntu server 20.04 lts |
| ram | 1024 mb |
| cpu | 1 vcpu |
| disk | 20 gb |
| security configuration | intentionally misconfigured for privesc |
| configured users | `ubuntu` (low-privilege), `www-data` (web service) |
| exposed services | ssh (22), http (80), misconfigured suid services |

---

## Network topologies

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

## NAT configuration (modules 01-02)

Used for: passive/active reconnaissance, vulnerability assessment, phases that
do not require direct visibility on the real LAN.

### IP addresses (NAT)

| vm | hostname | ip | role |
| :--- | :--- | :--- | :--- |
| kali linux | kali | `10.0.2.15` | attacker |
| windows 10 | win10-target | `10.0.2.3` | primary target |
| virtualbox gateway | - | `10.0.2.1` | default gateway |
| virtualbox dhcp | - | `10.0.2.2` | dhcp server |

### VirtualBox configuration (NAT)

```
VM Settings > Network > Adapter 1:
  - Attached to: NAT
  - (Advanced) Port Forwarding: not required for internal traffic
```

### Optional port forwarding (host to VM access in NAT)

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

## Network bridge configuration (modules 03-04)

Used for: active exploitation, privilege escalation, post-exploitation,
phases simulating an attacker already on the same network as the target.

> **Security note:** In Bridge mode, VMs are visible on the physical LAN.
> ALWAYS run in a controlled network environment (isolated home network or dedicated VLAN).
> Never on a corporate or public network.

### IP addresses (bridge)

| vm | hostname | ip | role |
| :--- | :--- | :--- | :--- |
| kali linux | kali | `192.168.0.110` | attacker |
| windows 10 | win10-target | `192.168.0.109` | primary target |
| lan gateway | router | `192.168.0.1` | default gateway |
| subnet | - | `192.168.0.0/24` | lab segment |

### VirtualBox configuration (bridge)

```
VM Settings > Network > Adapter 1:
  - Attached to: Bridged Adapter
  - Name: [select the host's physical NIC]
  - Promiscuous Mode: Deny (or Allow VMs for advanced scenarios)
```

> IPs 192.168.0.109 and 192.168.0.110 may vary. Assign static IPs
> or verify with `ip a` (Kali) and `ipconfig` (Windows) at the beginning of each session.

### Static IP assignment on Kali (bridge)

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

## Modules by topology

| module | topology | kali ip | target ip |
| :--- | :--- | :--- | :--- |
| `01-recon` | nat | 10.0.2.15 | 10.0.2.3 |
| `02-vulnerability-assessment` | nat | 10.0.2.15 | 10.0.2.3 |
| `03-web-attacks` | nat | 10.0.2.15 | 10.0.2.3 |
| `04-system-exploitation` | bridge | 192.168.0.110 | 192.168.0.109 |
| `05-social-engineering` | bridge | 192.168.0.110 | 192.168.0.109 |
| `06-wireless-security` | bridge | 192.168.0.110 | n/a (physical ap) |
| `07-post-exploitation` | bridge | 192.168.0.110 | 192.168.0.109 |
| `08-defense-hardenings` | nat | 10.0.2.15 | n/a (self) |
| `09-digital-forensics` | nat | n/a | local disk images |
| `10-cloud-security` | internet | n/a | cloud endpoints |

---

## Snapshots and VM management

### Recommended snapshot strategy

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

### VirtualBox CLI commands (vboxmanage)

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

## Reproducing the lab

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

### Setup sequence

1. Import Kali Linux OVA into VirtualBox (`File > Import Appliance`)
2. Install Windows 10 from ISO in a new VM with parameters from the table above
3. Configure Windows 10 as target (disable firewall, enable SMBv1, create users)
4. Choose the network topology based on the module to be executed
5. Take a base snapshot of both VMs before starting
6. Verify connectivity with `ping` before every session

### Connectivity verification (NAT)

```Bash
# From Kali
ping 10.0.2.3 -c 3
nmap -sn 10.0.2.3
```

### Connectivity verification (bridge)

```Bash
# From Kali
ping 192.168.0.109 -c 3
nmap -sn 192.168.0.109
```

### Windows target configuration (PowerShell script - run as administrator)

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

## Containerized web targets (Docker compose)

For module 03 (Web Attacks) and parts of module 02 labs, a `docker-compose.yml` is available in the repository root providing containerized web targets. This is **complementary** to the VirtualBox topology - it does not replace it.

### What Docker compose covers

| service | port | module | target for |
| :--- | :--- | :--- | :--- |
| dvwa | `localhost:8080` | 03-web-attacks | sqli, xss, command injection, csrf |
| dvga | `localhost:5013` | 03-web-attacks | graphql introspection, idor, batching |
| juice shop | `localhost:3000` | 03-web-attacks | full owasp top 10 (100+ challenges) |

### What still requires VirtualBox

System Exploitation (module 04), Post-Exploitation (module 07), Wireless (module 06) labs and all Windows-based scenarios require the VMs documented in previous sections.

### Quick start

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

## Demo recording with asciinema

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

### Recommended labs to record

| lab | file | target duration |
| :--- | :--- | :--- |
| nmap 3-phase scan | `01-recon/.../nmap/` | 2-3 min |
| manual sqli on dvwa | `03-web-attacks/.../sql-injection/` | 3-5 min |
| winpeas enumeration | `04-system-exploitation/.../winpeas/` | 2-3 min |
| hashcat mask attack | `04-system-exploitation/.../hashcat/` | 1-2 min |
| mimikatz credential dump | `07-post-exploitation/.../mimikatz/` | 2-3 min |

---

> **Disclaimer:** This lab is intentionally configured in a vulnerable manner
> for educational purposes. Do not replicate this configuration on production systems.
> Always run in an isolated environment. The documented IPs and configurations
> refer exclusively to the virtualized testing environment.
