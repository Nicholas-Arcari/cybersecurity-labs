> **English** | [Italiano](README.md)

# 02 - Network forensics

> - **Phase:** Digital Forensics & Incident Response - Network Analysis
> - **Category:** Analysis - incident reconstruction from network traffic
> - **Prerequisites:** Capture of traffic (PCAP) from IDS/tap/SIEM; analysis tools (Wireshark, Zeek, tshark); incident context
> - **Output:** Finding FOR-002; reconstruction of the network sessions; confirmation of C2/exfiltration; IOCs extracted from the traffic

---

## Introduction

Network forensics is the analysis of the incident from the perspective of network traffic. It has a property that makes it valuable: the traffic is the direct and non-alterable recording of what actually happened on the wire. Where the logs of a host can be tampered with by whoever compromises it (anti-forensics, `07-post-exploitation`), a network capture collected by an independent system records the truth of the communication, immune to retroactive application tampering.

Network analysis operates on two complementary levels:

- **Flow / metadata:** who communicates with whom, when, how much, with what frequency. This level (Zeek logs, NetFlow, conversation statistics) reveals the patterns - the C2 beaconing, the exfiltration volumes - and is visible even when the content is encrypted.
- **Content / packets:** what exactly was transmitted. This level (Wireshark, Follow Stream) reconstructs the application sessions, recovers files and credentials, but is limited by encryption.

The section is centered on **Wireshark (FOR-002)**, the reference tool for detailed packet analysis. Its positioning in the path is precise, as per the strategic note of module 08: detection (SIEM/IDS) flags where to look, Wireshark shows what is there. It does not open at random, it opens after an alert has provided the starting point of the investigation.

The link with the rest of the defense is direct: network forensics is the last mile of the chain detection, correlation, detailed analysis. The SIEM (`../../08-defense-hardenings/01-siem-log-analysis/`) detects and correlates, network forensics confirms and details, producing the documented certainty on which the response is based.

---

## Folder structure

```
02-network-forensics/
+-- README.md          # this file: FOR-002 registry, network forensics concept
|
+-- wireshark/         # FOR-002: PCAP analysis, stream reassembly, IOC extraction
```

---

## Recommended operational flow

```
[INPUT] Alert from the SIEM/IDS (module 08) + traffic capture (PCAP)
         |
         v
[1] Pointing (from the alert)
     +-- the alert provides IP/time/pattern -> starting point of the investigation
              |
              v
[2] Metadata analysis (big picture)
     +-- conversations/flow -> beaconing, volumes, destinations (even in TLS)
              |
              v
[3] Content analysis (detail) - wireshark/
     +-- display filter + Follow Stream -> reconstructed sessions (FOR-002)
              |
              v
[4] IOC and artifact extraction
     +-- exfiltrated files, C2 IPs, cleartext credentials
              |
              v
[OUTPUT] Incident confirmed and quantified -> IOC -> detection (feedback to the SIEM)
```

---

## Reference tools

| tool | type | role | main use case |
| :--- | :--- | :--- | :--- |
| `Wireshark` | packet analyzer | gui | detailed analysis, follow stream (FOR-002) |
| `tshark` | packet analyzer | cli | scriptable analysis and automatic extraction |
| `Zeek` (bro) | network analysis | framework | structured logs for large-scale analysis |
| `NetworkMiner` | network forensics | gui | automatic extraction of files/credentials/hosts |
| `Suricata` | ids | engine | detection that triggers the analysis |

> **Recommended modern tool:** `Zeek` for the big picture (structured logs of connections, DNS, HTTP, files) and `Wireshark`/`tshark` for the detail of the single stream. The combination covers both levels - metadata and content - of network analysis.

---

## Finding registry - network forensics section

| id | description | severity | subfolder |
| :--- | :--- | :---: | :--- |
| `FOR-002` | wireshark: session reconstruction, c2/exfiltration confirmation, ioc extraction from pcap | `High` | `wireshark/` |

---

## MITRE ATT&CK mapping - aggregated

> Attack techniques **reconstructed/confirmed** by network analysis.

| tactic (reconstructed) | technique | mitre id | related finding |
| :--- | :--- | :--- | :--- |
| command and control | application layer protocol: web protocols | `T1071.001` | FOR-002 |
| command and control | application layer protocol: dns | `T1071.004` | FOR-002 |
| exfiltration | exfiltration over c2 channel | `T1041` | FOR-002 |
| credential access | network sniffing | `T1040` | FOR-002 |

---

> **Note:** Analyzing third-party network traffic without authorization is a crime and violates communications regulations. All documented activities were conducted on lab captures owned by the author. In real contexts, traffic capture must be conducted with an adequate legal basis and in compliance with privacy. Techniques are documented for educational and defensive/investigative purposes in an authorized context.
