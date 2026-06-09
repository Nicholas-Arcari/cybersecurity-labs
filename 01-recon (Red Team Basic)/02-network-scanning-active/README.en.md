> **English** | [Italiano](README.md)

# 02 - Active Network Scanning

> - **Phase:** Reconnaissance - Active Network Scanning
> - **Visibility:** Low / High - from local ARP sweep to SYN flood on remote networks
> - **Prerequisites:** Written authorization on the test perimeter, confirmed target IPs/ranges, network access (local or VPN)
> - **Output:** Active host map (SCAN-001), open ports (SCAN-002), critical service configurations (SCAN-003)

---

## Introduction

Active Network Scanning is the transition from invisible reconnaissance to direct interaction with target systems. Unlike passive OSINT, packets are sent here: this means activities are detectable by the target's IDS/IPS and must be performed exclusively within the authorized scope.

The objective is to build a precise map of the network attack surface:
- Which IP addresses are assigned to active devices?
- Which TCP/UDP ports are open on these hosts?
- Which service versions are running?
- Which security configurations are present (or absent)?

The standard operational sequence involves three progressive detail levels: rapid discovery (who's there?), port scanning (what's running?), script enumeration (how is it configured?). Each level increases detail but also visibility.

Network Scanning is the direct prerequisite for the `02-vulnerability-assessment/` module, which takes the exposed service map as input to identify exploitable vulnerabilities.

---

## Folder Structure

```
02-network-scanning-active/
+-- README.md                        <- this file (index + finding registry)
|
+-- live-host-discovery/
|   +-- README.md                    <- SCAN-001: ARP/ICMP sweep (arp-scan, netdiscover, nmap -sn)
|   +-- img/                         <- lab screenshots
|
+-- port-scanning (Nmap)/
    +-- masscan/
    |   +-- README.md                <- SCAN-002: high-speed port discovery (Masscan)
    |   +-- img/                     <- lab screenshots
    |
    +-- nmap-scripts/
        +-- README.md                <- SCAN-003: NSE enumeration (SMB signing, NetBIOS)
        +-- img/                     <- lab screenshots
```

---

## `live-host-discovery/` - Active Host Identification

**Finding ID:** `SCAN-001` | **Severity:** `Informational`

Live Host Discovery is the first operational step in network scanning: before scanning ports, you need to identify which IP addresses in the target range correspond to active devices. Sending SYN packets on 65535 ports to thousands of non-existent hosts wastes valuable time.

Three complementary approaches:
- `arp-scan -l` (Layer 2, LAN): the most reliable in local networks, bypasses OS firewalls
- `netdiscover -r <CIDR>` (active ARP): useful in environments with broadcast enabled
- `nmap -sn <CIDR>` (ICMP Ping Sweep): standard for remote networks, but subject to firewall blocks

**Lab result:** identified the Windows 10 target at `10.0.2.3` in subnet `10.0.2.0/24`.

---

## `port-scanning (Nmap)/masscan/` - High-Speed Port Discovery

**Finding ID:** `SCAN-002` | **Severity:** `Informational`

Masscan is an asynchronous TCP port scanner with a custom TCP/IP stack. It can scan millions of ports per second on physical networks, making it the ideal tool for Broad Scope Discovery (`/16`, `/8` ranges).

**Critical limitation documented in lab:** in virtualized environments with NAT (VirtualBox), Masscan's custom raw socket does not correctly receive response packets, generating false negatives. Cross-validation with Nmap is mandatory when Masscan returns negative results on suspected targets.

> **Recommended modern tool:** `RustScan` - combines Masscan-like discovery speed with improved compatibility for virtualized NAT environments, automatically passing results to Nmap for detailed enumeration.

---

## `port-scanning (Nmap)/nmap-scripts/` - NSE Enumeration

**Finding ID:** `SCAN-003` | **Severity:** `High`

The Nmap Scripting Engine (NSE) extracts configuration information that simple port scanning does not reveal. Default scripts (`-sC`) run a battery of safe tests on each identified service.

**Two critical findings identified in lab on 10.0.2.3:**
- `SCAN-003a`: SMB Signing `enabled but not required` - direct vector for SMB Relay attacks (MITM)
- `SCAN-003b`: NetBIOS name disclosure (`WINDOWS-TEST`) - hostname information disclosure

The SMB Signing misconfiguration detected here (SCAN-003) is actively exploited in module `07-post-exploitation/04-pivoting-tunneling/`.

---

## Recommended Operational Flow

```
[INPUT] Authorized target IP range (e.g., 10.0.2.0/24)
          |
          v
[1] Live Host Discovery (fast, low visibility)
     +-- sudo arp-scan -l              # LAN: uses ARP, bypasses OS firewall
     +-- nmap -sn 10.0.2.0/24         # remote: ICMP ping sweep
     -> Active IP list
          |
          v
[2] Port Discovery (fast, high visibility)
     +-- masscan -p1-65535 <IP> --rate=1000 -e eth0   # physical networks only
     +-- nmap -p- --min-rate=3000 <IP>                 # NAT-safe alternative
     -> Open port list
          |
          v
[3] Service & Script Enumeration (detailed)
     +-- nmap -p <PORTS> -sC -sV -O <IP>
     -> Banners, versions, security configurations
          |
          v
[OUTPUT] Attack Surface Map -> 02-vulnerability-assessment/
```

---

## Reference Tools

| Tool | Type | Technique/Access | Main Use Case |
| :--- | :--- | :--- | :--- |
| `arp-scan` | Port scanner | CLI (Layer 2) | LAN live host discovery, bypasses OS firewall |
| `netdiscover` | Port scanner | CLI (active ARP) | Passive/active discovery in broadcast networks |
| `nmap` | Port scanner / Service enumerator | CLI | Standard for port scan, versioning and NSE |
| `Masscan` | Port scanner | CLI (raw socket) | High-speed port discovery on physical networks |
| `RustScan` | Port scanner | CLI | Fast discovery compatible with NAT, feeds Nmap |
| `nmap -sC` (NSE) | Service enumerator | CLI | Configuration testing automation via scripts |

> **Recommended modern tool:** `RustScan` (`rustscan -a <IP> -- -sC -sV`) - performs port discovery in seconds and automatically passes found ports to Nmap for detailed enumeration, solving Masscan's NAT problem in virtualized environments.

---

## Finding Registry

| ID | Description | Severity | File |
| :--- | :--- | :---: | :--- |
| `SCAN-001` | Active hosts identified in 10.0.2.0/24, Windows 10 target at 10.0.2.3 | `Informational` | `live-host-discovery/README.md` |
| `SCAN-002` | Port discovery with Masscan - documented false negative in NAT environment | `Informational` | `port-scanning (Nmap)/masscan/README.md` |
| `SCAN-003` | SMB Signing not mandatory + NetBIOS name disclosure on 10.0.2.3 | `High` | `port-scanning (Nmap)/nmap-scripts/README.md` |

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Remote System Discovery | `T1018` | ARP sweep and ICMP ping sweep to identify active hosts in subnet 10.0.2.0/24 (SCAN-001) |
| Reconnaissance | Network Service Discovery | `T1046` | Port scanning with Masscan and Nmap to identify exposed services on the target (SCAN-001, SCAN-002, SCAN-003) |
| Reconnaissance | Gather Victim Host Info: Software | `T1592.002` | NSE scripts to identify software versions and SMB security configurations (SCAN-003) |

---

> **Note:** All network scanning activities documented in this section were performed on an isolated VirtualBox lab with an authorized Windows 10 target (subnet 10.0.2.0/24). No scans were conducted on networks or systems without explicit authorization.
