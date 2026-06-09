> **English** | [Italiano](README.md)

# Active Scanning: High-Speed Port Discovery (Masscan)

> - **Phase:** Reconnaissance - Active Network Scanning
> - **Visibility:** High - SYN flood towards the target, anomalous traffic pattern easily detectable by IDS/IPS
> - **Prerequisites:** Masscan installed, root access, physical network interface (limitations in virtualized NAT environments)
> - **Output:** SCAN-002 - Open TCP ports on target; in this lab: documented false negative in VirtualBox NAT environment

---

Objective: Execution of high-speed massive scans to quickly identify open ports on large network segments, simulating a "Large Scale Reconnaissance" scenario.
Target: Lab Subnet (`10.0.2.0/24`)

Tools: `Masscan`

---

## 1. Theoretical Introduction

Masscan is an asynchronous TCP port scanner. Unlike traditional scanners, it uses a custom TCP/IP stack that allows it to send packets (SYN packets) at a speed limited only by the hardware bandwidth, without waiting for responses synchronously.

Use Case: This tool is ideal for the initial phase of Broad Scope Discovery (e.g., scanning entire `/16` or `/8` classes), where speed takes priority over detail (Service Versioning).

---

## 2 Technical Execution

**Finding ID:** `SCAN-002` | **Severity:** `Informational`

#### Phase 1: Target Validation (Ground Truth)

An Nmap scan was launched to confirm the presence of open ports on the target host and establish a "ground truth".

```Bash
sudo nmap -p 445 10.0.2.0/24 --open
```

![](./img/Screenshot_2026-02-04_11_34_09.jpg)

Analysis: Host 10.0.2.3 is active and port 445 is confirmed OPEN.

#### Phase 2: High-Speed Test (Masscan)

Subsequently, Masscan was tested on the same specific target to verify asynchronous detection capability.

```Bash
sudo apt install masscan
sudo masscan -p445 10.0.2.3 --rate=100 -e eth0
```

- `--rate=100`: Limits sending to 100 pps (packets per second).
- `-p445`: Targeted scan on the known open port.

![](./img/Screenshot_2026-02-04_11_37_50.jpg)

Analysis: Masscan completed the scan without detecting the open port (False Negative).

---

## 3 Critical Analysis: Limitations in Virtual Environments

The test highlighted a substantial behavioral difference due to the lab's network architecture (VirtualBox NAT Network).

| Feature | Nmap | Masscan |
|---------|------|---------|
| Technology | Synchronous / Stateful | Asynchronous / Stateless|
| | Uses standard Linux Kernel `syscalls` | Uses Raw Sockets and bypasses the Kernel (custom stack) |
| NAT Handling | Excellent. The operating system manages connection tracking and NAT traversal | Critical. Response packets (SYN-ACK) are often not correctly routed from the virtual interface to the Masscan process |
| Result | Port detected (open) | False negative (closed/filtered) |

Lesson Learned: In real-world scenarios, Masscan is unbeatable for speed on direct physical networks. However, in virtualized environments or behind complex NAT, its custom stack may lose return packets. It is essential to always perform Cross-Validation with Nmap when Masscan results are negative on suspected targets.

---

## 4 OpSec Considerations

Regardless of the technical result in the lab, using Masscan in a real Red Team Engagement requires caution:

- Noisiness: The aggressive nature of generated packets (even at low rates) creates an anomalous traffic pattern easily detectable by IDS/IPS.
- Saturation: An incorrect rate (e.g., `--rate=100000`) on consumer hardware can cause an unintentional Denial of Service (DoS) on intermediate routers.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Discovery | Network Service Discovery | `T1046` | High-speed asynchronous port discovery with Masscan on subnet 10.0.2.0/24, documenting behavior in virtualized NAT environment (SCAN-002) |

---

> **Note:** Port scanning activities with Masscan were performed exclusively within an isolated VirtualBox lab. The rate used (100 pps) was chosen to minimize impact on the test network. In real-world environments, Masscan requires explicit authorization and rate calibration based on available bandwidth.
