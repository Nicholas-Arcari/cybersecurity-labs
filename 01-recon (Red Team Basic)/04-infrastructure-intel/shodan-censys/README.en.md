> **English** | [Italiano](README.md)

# Infrastructure Intelligence: Passive Recon with Shodan & Censys

> - **Phase:** Reconnaissance - Infrastructure Intelligence
> - **Visibility:** Zero - search on public databases pre-built by third-party scanners, no contact with the targets
> - **Prerequisites:** Shodan account (free tier), Censys account (free tier), Internet access
> - **Output:** INTEL-001 (60+ exposed RDP), INTEL-002 (workstation with multiple services on public IP), INTEL-003 (corporate server VoIP+FTP+RDP on consumer ADSL)

---

Objective: Mapping the technology infrastructure exposed on the Internet using device (IoT) and certificate search engines, without directly interacting with the targets (Zero-Touch Recon).

Target Case Study: Exposed infrastructure in Parma (IT) Tools: `Shodan` (Web), `Censys` (Web), `Whois`

---

## 1 Theoretical Introduction

Unlike active scanners (like Nmap) that send packets to targets, tools like Shodan and Censys perform constant scans of the entire IPv4 address space, archiving service responses (Banners). This allows security analysts to query a historical database to discover exposed assets, vulnerable software versions and misconfigurations in a completely passive manner, invisible to the target's IDS/IPS.

---

## 2 Technical Execution: Shodan (IoT & Services)

**Finding ID:** `INTEL-001` | **Severity:** `High`

Scenario: Search for exposed RDP services

The search focused on identifying servers with publicly exposed Remote Desktop Protocol (RDP) in a specific geographic area. Port 3389 is one of the main vectors for initial access by Ransomware groups.

Shodan Query:

```Plaintext
port:3389 city:"Parma"
```

![](./img/Screenshot_2026-02-08_11_24_00.jpg)

General Result:

Macro Analysis: The search returned over 60 exposed devices. Banner analysis revealed severe Information Disclosure issues:

- Hostnames: Specific machine names identified such as `SERVER2022` (corporate infrastructure) and `PC-MARCO` (personal device).
- OS Fingerprinting: It is possible to clearly distinguish between client machines (Windows 11) and servers (Windows Server 2016/2022).

Target Deep Dive Analysis

Detailed analysis of Shodan data on two specific hosts revealed extremely risky configurations:

**Finding ID:** `INTEL-002` | **Severity:** `High`

#### Target A (Exposed Workstation)

- IP: `2.118.xx.xx` (Business ISP)
- OS Fingerprinting: Shodan identifies the operating system as Windows 11.

    Significance: This is not a proper server (Windows Server), but a workstation. Probably a PC used by an employee or technician, left on and directly connected to the Internet (Business IP Telecom Italia).

- Anomalous Web Server (Port 3080): There is an active Apache server on non-standard port 3080.

    Significance: This often indicates administration panels or test software.
    
- Port 2000 (Bandwidth Test?): Open port 2000 with that binary banner often belongs to router management services (MikroTik) or bandwidth testing.

    Conclusions: This machine is a "sieve". It has RDP (3389), Web (3080) and management services exposed. It is the classic "forgotten PC" under the desk that allows an attacker to enter the corporate network.

![](./img/Screenshot_2026-02-08_11_27_39.jpg)

**Finding ID:** `INTEL-003` | **Severity:** `Critical`

#### Target B (Critical Business Server)

This is a critical target. Looking at the domains and ports, we can understand exactly what this company does.

- IP: `87.26.xx.xx`
- Identity Disclosure: Associated domains are `carosello.net` and `carosello.my3cx.it`.

    Significance: We have the business name ("Carosello").

- Exposed VoIP System (Ports 5060, 5090 + 3CX domain):

    Significance: The `my3cx.it` domain and SIP ports indicate that this server manages the Corporate Phones (3CX PBX).

    Risk: If a hacker gets in here, they can eavesdrop on phone calls, redirect calls or make premium-rate calls at the company's expense.

- Exposed File Server (Port 21): FileZilla Server is active.

    Significance: They use this PC to exchange files. A Brute Force attack here could lead to theft of corporate documents.

- Remote Desktop (Port 3389):

    As always, the management port is open.

Verdict: This single PC manages Phones, Files and Remote Access. If this PC falls (e.g., Ransomware), the company stops completely (no phone, no data).

![](./img/Screenshot_2026-02-08_11_28_14.jpg)

---

## 3 OSINT Integration: ISP Identification (Whois)

To complete the profiling of the critical target (`87.26.xx.xx`), a Whois query was performed to identify the Internet Service Provider (ISP) and abuse contacts.

Command:

```Bash
whois 87.26.xx.xx
```

![](./img/Screenshot_2026-02-08_11_33_05.jpg)

Analysis:

- `netname: TELECOM-ADSL-IPTV`:

    This tells you what type of connection it is. It is not a data center (like Amazon AWS or Google Cloud), but a regular ADSL/Fiber Business line. This confirms that the server is physically inside the company's office or store, not in the cloud.

- `descr: Telecom Italia S.p.A.`:

    The owner of the physical infrastructure (the cables) is Telecom Italia. The IP is leased from them.

- `abuse-mailbox: abuse@retail.telecomitalia.it`:

    This is the most important line for an Ethical Hacker. If you need to report an attack, a virus or a severe vulnerability (Responsible Disclosure), this is the official email to write to.

- `address: Via Oriolo Romano 240, 00189 Roma`:

    Warning: This is NOT the target's address (Carosello in Parma). This is the registered office address of Telecom Italia in Rome. Whois rarely gives you the customer's home address for privacy reasons.

Note on Geolocation: Although Shodan locates the IP in Parma, cross-referenced OSINT analysis on the domains (`carosello.net`) and the VAT number revealed that the company primarily operates in Liguria. This discrepancy is attributable to ISP routing and confirms the importance of manual verification of automated data.


## 4 Technical Execution: Censys (Validation & New Findings)

Scenario: Cross-reference validation of the critical target identified on Shodan. The objective is to analyze TLS certificates and discover services that might have been missed in the initial analysis.

Censys Query:

```text
ip: 87.26.xx.xx
```

Results Analysis (New Discoveries): The Censys analysis enriched the intelligence picture with critical details about the machine's usage:

- Promiscuous Use (Business + Personal): A Plex Media Server service was identified on port 32400. The presence of personal entertainment software on a server managing corporate data (FTP) and telephony (VoIP) indicates a severe security policy violation and a high risk of accidental compromise.
- Identity Confirmation (RDP Certificate): SSL certificate analysis on port 3389 unequivocally confirms the hostname PC-Marco (CN=PC-Marco), corroborating the NetBIOS data found by Shodan.
- Security Posture: All detected certificates (FTP, RDP) are "Self-Signed" (not validated by a CA), exposing connections to potential Man-in-the-Middle attacks.

![](./img/Screenshot_2026-02-08_12_38_17.jpg)

![](./img/Screenshot_2026-02-08_12_39_08.jpg)

---

## 5 Ethical Handling

In a real-world scenario, after identifying such a high criticality (VoIP and Data Exposure), the correct Responsible Disclosure procedure involves:

- Attribution: Owner identification through `DNS lookup` and `Whois`.
- Reporting: Sending a formal communication to the ISP's `abuse@` address or the company's technical contact, providing exposure details without ever attempting access (Exploitation).
- Recommended Remediation:

    - Immediately close ports 3389 (RDP), 21 (FTP) and 5060 (SIP) on the perimeter firewall.
    - Implement access exclusively through VPN.

---

## 6 Conclusions

Infrastructure Intelligence allowed mapping a critical attack surface without sending a single packet towards the target. We identified a real company that exposes the core of its operations (Phones and Files) on a consumer line, making it vulnerable to Ransomware or industrial espionage attacks with minimal effort from an attacker.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Search Open Technical Databases: Scan Databases | `T1596.005` | Shodan search with query `port:3389 city:"Parma"` to identify devices with exposed RDP, detecting 60+ targets with Information Disclosure of hostnames and OS (INTEL-001) |
| Reconnaissance | Gather Victim Network Info: Network Topology | `T1590.004` | Shodan banner and Censys TLS certificate analysis to reconstruct the critical targets' infrastructure topology (INTEL-002, INTEL-003) |
| Reconnaissance | Gather Victim Network Info: IP Addresses | `T1590.005` | IP correlation through Whois to identify ISP, connection type (consumer vs datacenter) and real geolocation of targets (INTEL-002, INTEL-003) |

---

> **Note:** Shodan and Censys searches documented in this section were conducted for educational purposes to illustrate Infrastructure Intelligence methodologies. Companies identified as critical targets were reported following Responsible Disclosure principles. No access attempts to identified systems were conducted.
