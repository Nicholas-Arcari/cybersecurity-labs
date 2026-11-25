> **English** | [Italiano](README.md)

# 09 - Digital forensics (blue team analysis)

> - **Phase:** Defense - Digital Forensics & Incident Response (DFIR)
> - **Category:** Analysis - incident reconstruction from the evidence
> - **Prerequisites:** Understanding of the offensive techniques (modules 01-07) and of detection (module 08); forensic tools (SIFT/Autopsy/Wireshark); methodological rigor (integrity, chain of custody)
> - **Output:** Findings FOR-001..002; documented reconstruction of the attack; extracted IOCs; base for response, attribution and defensive lessons

---

## Introduction

The `09-digital-forensics` module is the post-incident analysis: after an attack has occurred (modules 01-07) and the defense has detected it (module 08), forensics reconstructs what exactly happened, examining the traces left on the systems and in the traffic. It is the module that closes the incident response cycle: detection says "something happened", forensics says "here is exactly what, how, when and with what impact".

It is also the module where the offensive techniques of the path are seen from the other side. Every action of the attacker leaves traces - files, timestamps, logs, packets - and forensics interprets them to recompose the story of the attack. What module 07 taught to do (enumerate, persist, exfiltrate, delete the traces), module 09 teaches to reconstruct afterwards. It is the investigative countermeasure to anti-forensics: what the attacker deletes, forensics often recovers.

The principle that governs the entire discipline is **evidence integrity**. Digital evidence is fragile and alterable; an analysis conducted without rigor contaminates it, making it useless or inadmissible. Hence the non-negotiable protocol: always work on copies (never on the original), verify integrity with cryptographic hashes, document every step in a chain of custody, respect the order of volatility. Methodological rigor is not pedantry: it is the very condition of validity of the result.

The module covers the two major areas of forensics:

1. **Disk Forensics (`01-disk-forensics/`, FOR-001):** the analysis of storage media (and of RAM). Image acquisition, integrity verification, construction of the incident timeline, recovery of the artifacts - including the files the attacker deleted.

2. **Network Forensics (`02-network-forensics/`, FOR-002):** the analysis of network traffic. Wireshark reconstructs the attacker's sessions from the packets, confirming exfiltration and C2 and extracting IOCs. The traffic is the impartial witness: not retroactively tamperable like the logs of a compromised host.

The positioning in the path is at the end of the defensive chain: prevent (08/hardening), detect (08/SIEM-XDR), respond and **analyze** (09/forensics). Forensics provides the understanding without which the response is blind and future prevention impossible.

---

## Folder structure

```
09-digital-forensics (Blue Team Analysis)/
+-- README.md                          <- this file: FOR-001..002 registry + aggregated MITRE
|
+-- 01-disk-forensics/                 <- FOR-001 (acquisition, timeline, artifact recovery)
|
+-- 02-network-forensics/
    +-- README.md                      <- FOR-002 registry, network forensics concept
    +-- wireshark/                     <- FOR-002 (PCAP analysis, stream reassembly, IOC)
```

---

## Recommended operational flow

```
[INPUT] Detected incident (alert from module 08) + systems/traffic to analyze
         |
         v
[1] Preservation (order of volatility)
     +-- memory and network state BEFORE the disk (if the system is on)
     +-- acquisition with write blocker + integrity hash
              |
              v
[2] Disk & Memory Forensics (01-disk-forensics/)
     +-- incident timeline + recovery of deleted artifacts (FOR-001)
     +-- memory analysis -> processes/C2 in RAM
              |
              v
[3] Network Forensics (02-network-forensics/)
     +-- PCAP analysis -> confirm exfiltration/C2, extract IOCs (FOR-002)
              |
              v
[4] Correlation and reporting
     +-- disk timeline + traffic -> complete narrative of the attack
     +-- IOC -> feedback to the detection (module 08)
              |
              v
[OUTPUT] Incident reconstructed and documented -> response, attribution, targeted hardening
```

---

## Reference tools

| tool | area | role | main use case |
| :--- | :--- | :--- | :--- |
| `Autopsy` / `Sleuth Kit` | disk | platform | filesystem analysis, timeline, recovery (FOR-001) |
| `Volatility 3` | memory | analyzer | analysis of ram dumps (processes, network, injection) |
| `plaso` / `log2timeline` | disk | timeline | correlated super-timeline of the incident |
| `Wireshark` / `tshark` | network | analyzer | pcap analysis, session reconstruction (FOR-002) |
| `Zeek` | network | framework | structured traffic logs at large scale |
| `dc3dd` / write blocker | acquisition | preservation | forensic copy with guaranteed integrity |

> **Recommended modern tool:** the `SIFT Workstation` (SANS) integrates the entire forensic arsenal ready to use (Autopsy, Volatility, plaso, Wireshark). For a disk, memory, network flow, the combination `Autopsy` + `Volatility 3` + `Wireshark` covers the complete analysis of an incident, from the disk timeline to the confirmation on the traffic.

---

## Finding registry - module 09

| id | description | severity | subfolder |
| :--- | :--- | :---: | :--- |
| `FOR-001` | disk forensics: acquisition, incident timeline, recovery of deleted artifacts | `High` | `01-disk-forensics/` |
| `FOR-002` | network forensics (wireshark): session reconstruction, c2/exfil confirmation, ioc | `High` | `02-network-forensics/wireshark/` |

---

## MITRE ATT&CK mapping - aggregated

> The forensic module maps the attack techniques that the analysis **reconstructs and confirms** after the fact from the evidence. Complementary framework: MITRE D3FEND.

| tactic (reconstructed) | technique | mitre id | related finding |
| :--- | :--- | :--- | :--- |
| defense evasion | indicator removal: file deletion | `T1070.004` | FOR-001 (carving recovers the deleted files) |
| defense evasion | indicator removal: clear linux logs | `T1070.002` | FOR-001 (the timeline highlights the tampering) |
| persistence | account manipulation: ssh authorized keys | `T1098.004` | FOR-001 |
| command and control | application layer protocol: web protocols | `T1071.001` | FOR-001, FOR-002 |
| command and control | application layer protocol: dns | `T1071.004` | FOR-002 |
| exfiltration | exfiltration over c2 channel | `T1041` | FOR-002 |
| exfiltration | data staged | `T1074` | FOR-001 |
| credential access | network sniffing | `T1040` | FOR-002 |

| defensive countermeasure (d3fend) | d3fend id | area |
| :--- | :--- | :--- |
| file analysis | `D3-FA` | disk forensics (filesystem artifacts) |
| memory boundary tracking | `D3-MBT` | memory forensics (ram analysis) |
| network traffic analysis | `D3-NTA` | network forensics (pcap analysis) |

---

> **Note:** All activities documented in this module were conducted on lab images, systems and traffic captures owned by the author. Forensics on third-party systems or traffic requires legal authorization (warrant, owner's consent) and rigorous compliance with the chain of custody, which determines its admissibility. Forensic analysis frequently exposes personal data and private communications: it must be conducted in compliance with privacy regulations and with an adequate legal basis. Techniques are documented for educational and defensive/investigative purposes in an authorized context.
