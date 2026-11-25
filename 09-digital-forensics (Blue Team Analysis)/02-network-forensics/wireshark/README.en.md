> **English** | [Italiano](README.md)

# Wireshark - packet analysis and session reconstruction

> - **Phase:** Digital Forensics & Incident Response - Network Forensics (packet analysis)
> - **Category:** Analysis - detailed analysis of the captured traffic
> - **Prerequisites:** Capture of traffic (PCAP) to analyze; Wireshark/tshark; understanding of network protocols; context of the incident (what to look for)
> - **Output:** Finding FOR-002; reconstruction of the attacker's sessions; extraction of IOCs from the traffic; confirmation of exfiltration, C2 or cleartext credentials

- **Operating Environment:** Forensic workstation, PCAP file from SIEM/IDS or targeted capture
- **Role:** The last mile of the analysis: looking inside the individual packets
- **Main tools:** Wireshark, tshark, NetworkMiner, Zeek

---

## Executive summary

Wireshark is the detailed network traffic analysis tool: where the SIEM (`../../../08-defense-hardenings/01-siem-log-analysis/`) detects and correlates and Suricata flags, Wireshark opens afterwards, to look inside the individual packets and understand exactly what they contained. It is the last mile of network analysis: the definitive confirmation of what actually passed on the wire.

The strategic note of the path places it precisely: Splunk tells you "I saw a strange connection + a failed login + a Wazuh alert in the same minute"; you open Wireshark after Splunk has alerted you, to examine those specific packets and understand what they carried. Detection indicates where to look, Wireshark shows what is there.

Finding FOR-002 documents the forensic analysis of a traffic capture: the use of display filters to isolate the relevant conversations, protocol dissection, session reconstruction (stream reassembly) and IOC extraction. In a capture containing attack traffic, this allows confirming exfiltration (what went out), identifying the C2 (with whom the compromised host communicated) and recovering credentials or commands transmitted in cleartext.

---

## Folder structure

```
wireshark/
+-- README.md      # this file: PCAP analysis, stream reassembly, IOC extraction (FOR-002)
+-- img/           # display filters and Follow TCP Stream
```

---

## Forensic analysis of a traffic capture

**Finding ID:** `FOR-002` | **Severity:** `High` (reconstruction of the attack sessions from the traffic, confirmation of exfiltration/C2 and extraction of IOCs)

### Operational context

A raw traffic capture contains thousands of packets, largely noise. Forensic analysis is the art of isolating the signal: Wireshark's **display filters** allow narrowing the view to only the relevant conversations, and the **Follow Stream** recomposes the fragmented packets of a TCP session into their logical sequence, making the application exchange readable.

### PoC - display filter: isolate the suspicious traffic

```
# Filter: traffic toward a suspicious IP identified by the SIEM
ip.addr == 45.83.x.x

# Filter: possible exfiltration (large HTTP POST upload)
http.request.method == "POST" and http.content_length > 100000

# Filter: possible DNS tunnel (anomalous queries, long subdomains)
dns.qry.name.len > 50
```

### PoC - follow TCP stream: reconstruct the session

```
# Wireshark: right-click on the packet -> Follow -> TCP Stream
# Recomposes the entire application conversation

# Example: credentials transmitted in cleartext (HTTP Basic / FTP / Telnet)
POST /login HTTP/1.1
Host: internal-app
Authorization: Basic YWRtaW46UGFzc3cwcmQh    <-- cleartext credentials (base64) (FOR-002)
# base64 decode -> admin:Passw0rd!
```

### PoC - c2 identification (beaconing)

```
# Statistics -> Conversations: identifies the beaconing (regular connections)
# An internal host that contacts an external IP at fixed intervals = C2 beacon

ip.src == 10.0.5.15 and ip.dst == 45.83.x.x and tcp.flags.syn == 1
```

```
# Beaconing pattern detected:
10.0.5.15 -> 45.83.x.x:443  every 60s (+/- jitter)   <-- C2 beacon (FOR-002)
# regular connection at fixed intervals = command and control channel
```

### PoC - file and IOC extraction (tshark)

```Bash
# Automatic extraction of the transferred objects (exfiltrated files/malware)
tshark -r capture.pcap --export-objects http,extracted/

# IOC extraction: all the external destination IPs contacted
tshark -r capture.pcap -T fields -e ip.dst | sort -u
```

```
extracted/exfil.zip      <-- exfiltrated file recovered from the traffic (FOR-002)
45.83.x.x                <-- IOC: C2/exfiltration IP
```

### Analysis methodology

- **Start from the lead:** detection (SIEM/IDS) provides the starting point (an IP, a time, an alert); the display filter narrows the capture to that context instead of navigating at random
- **Reconstruct, do not read packet by packet:** the Follow Stream recomposes the session; the analysis happens on the conversation, not on the individual frames
- **Encryption as a limit:** TLS traffic is not readable without the keys; the analysis moves to the metadata (who talks to whom, when, how much - beaconing is visible even in TLS)
- **Preserve the capture:** the PCAP is evidence; it must be treated with the same integrity (hashing) as a disk image

---

## Lab experience

The leap in understanding was moving from the raw capture to the reconstructed session. A capture of thousands of packets is unreadable packet by packet; the first `Follow TCP Stream` that recomposed a complete HTTP conversation - request, headers, credentials, response - made Wireshark suddenly useful. I understood that the forensic analyst does not read packets, they reconstruct conversations: the packet is the unit of transport, the session is the unit of meaning.

The strategic note of the path was verified in practice. I did not open Wireshark at random: I opened it because the SIEM (module 08) had flagged a connection toward a specific IP. That pointing turned a sea of packets into a targeted investigation - filter on the IP, follow the stream, and within a few minutes I had the confirmation. Detection and detailed analysis do not compete: the first says where to look, the second what is there. Using them in sequence is enormously more efficient than one without the other.

The most instructive limit was encryption. Much of modern traffic is TLS, and opening an encrypted stream shows only unreadable bytes. The lesson: against encrypted traffic, the analysis moves from content to metadata. I could not read what the host was exfiltrating, but the beaconing pattern - regular connections every 60 seconds toward the same external IP - was visible and sufficient to identify the C2. Encryption protects the content, not the behavior.

---

## Theoretical analysis: traffic as a faithful recording of the events

Network traffic has a unique forensic property: it is the direct and non-alterable recording of what actually happened on the wire. While logs are a second-level representation (an application decides what to record and can be tampered with), a packet capture is the very reality of the communication, captured at the lowest level. If a datum left the network, it is in the PCAP; no application anti-forensics can erase it from an already-made capture.

This places network forensics in a privileged position compared to host forensics. An attacker who compromises a host can alter its logs and delete its files (anti-forensics, module 07), but cannot retroactively modify a network capture collected by an independent system. The traffic is an impartial witness: it records both what the attacker wanted to do (the commands, the requests) and what they did not want to reveal (the C2 beaconing, the exfiltration volumes).

The theoretical limit is encryption, which introduces a fundamental tension. TLS protects the confidentiality of the content even from the legitimate analyst, moving the analysis to the metadata: who communicates with whom, when, with what frequency and volume. This reflects a general principle of security - metadata is often as revealing as content. A C2 channel can encrypt the commands, but the pattern of the communication (regularity, destination, sizes) betrays its nature. The modern forensic analyst reads the behavior of the traffic when they cannot read its content, and often the behavior is sufficient to reconstruct the attack.

---

## Real-World scenario: the confirmation of the incident

> This section describes how network analysis would operate in a real incident, confirming and detailing what detection flagged.

### The context (the trigger)

The SIEM (module 08) correlated an anomalous connection of an internal host toward an unknown external IP, coinciding with a Wazuh alert. The host is isolated and its traffic (captured by the IDS/tap) is passed to forensic analysis to understand what actually happened.

### The network analysis (what it confirms)

```
[FOR-002] PCAP of the suspicious host -> display filter on the IP flagged by the SIEM
        |
        v
Follow Stream: reconstruction of the sessions -> commands/data exchanged
        |
        +-- regular beaconing every 60s -> confirmed C2 channel (not a false positive)
        +-- voluminous HTTP POST -> confirmed exfiltration
        |
        v
tshark export-objects: recovery of the exfiltrated file -> real scope of the data that went out
        |
        v
IOC extraction: C2 IP, file hash, beaconing pattern
        |
        v
IOC -> SIEM rules/blocklist -> hunt for the same threat on the other hosts
```

**Investigative value:** network analysis turns a suspicion ("anomalous connection") into a documented certainty ("exfiltration of this file toward this C2, with this pattern"). It confirms or refutes the alarm, quantifies the damage (what went out), and produces reusable IOCs to detect the same threat elsewhere.

**Extracted indicators (IOC):** C2 IPs and domains, beaconing pattern (interval, jitter, port), hashes of the transferred files, credentials possibly exposed in cleartext. These close the loop by feeding the detection.

**Defensive lesson:** network forensics is the impartial witness of the incident. Where the host's logs can be tampered with, the traffic captured by an independent system records the truth of what passed. It is the final confirmation that turns an alert into an established fact - and the solid foundation on which to build the response.

---

## Reference tools

| tool | type | role | main use case |
| :--- | :--- | :--- | :--- |
| `Wireshark` | packet analyzer | gui | interactive analysis, display filters, follow stream |
| `tshark` | packet analyzer | cli | scriptable analysis, object/field extraction |
| `NetworkMiner` | network forensics | gui | automatic extraction of files, credentials, hosts |
| `Zeek` (bro) | network analysis | framework | structured traffic logs for large-scale analysis |
| `tcpdump` | packet capture | cli | traffic capture (upstream of the analysis) |
| `Suricata` | ids | engine | detection that triggers the analysis (`../../../08-.../`) |

> **Recommended modern tool:** `Wireshark` for interactive detailed analysis, `tshark` for automation and extraction. For large captures, `Zeek` produces structured logs (connections, DNS, HTTP, files) that make the analysis scalable - complementary to Wireshark: Zeek for the big picture, Wireshark for the detail of the single stream. `NetworkMiner` for quick automatic extraction of artifacts.

---

## MITRE ATT&CK mapping

> The table maps the attack techniques that network analysis **reconstructs/confirms** from the traffic.

| tactic (reconstructed) | technique | mitre id | role of the analysis |
| :--- | :--- | :--- | :--- |
| command and control | application layer protocol: web protocols | `T1071.001` | identification of the c2 beaconing over http/s (FOR-002) |
| command and control | application layer protocol: dns | `T1071.004` | detection of dns tunnels (anomalous queries) (FOR-002) |
| exfiltration | exfiltration over c2 channel | `T1041` | confirmation and quantification of the exfiltration (FOR-002) |
| credential access | network sniffing / cleartext | `T1040` | recovery of credentials transmitted in cleartext (FOR-002) |
| command and control | non-standard port | `T1571` | identification of c2 on non-standard ports |

| defensive countermeasure (d3fend) | d3fend id | application |
| :--- | :--- | :--- |
| network traffic analysis | `D3-NTA` | analysis of the traffic to reconstruct the sessions |
| protocol metadata anomaly detection | `D3-PMAD` | detection of beaconing/tunnels from the metadata |
| client-server payload profiling | `D3-CSPP` | payload profiling to identify c2/exfil |

---

> **Note:** All documented activities were conducted on lab traffic captures owned by the author. Intercepting and analyzing third-party network traffic without authorization is a crime and violates communications regulations. In real contexts, traffic capture may expose personal data and private communications: it must be conducted in compliance with privacy regulations and with an adequate legal basis. Techniques are documented for educational and defensive/investigative purposes in an authorized context.
