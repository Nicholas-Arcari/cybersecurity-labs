> **English** | [Italiano](README.md)

# Denial of service (DoS) and DDoS

> - **Nature:** conceptual page (background knowledge). Mechanism + defense angle. No DoS attack tool.
> - **Objective:** explain what a denial-of-service attack is, its categories, the amplification/reflection mechanism and, above all, how it is detected and mitigated.
> - **Scope:** DoS is out of scope for a penetration test (it is disruptive); here it is treated as defensive and contextual knowledge, not as a technique to run.

## Introduction

A **DoS** (Denial of Service) attack aims to make a service unavailable to its legitimate users, by exhausting
one of its resources (bandwidth, CPU, memory, connection state, application capacity). When the attack comes from
many coordinated sources (typically a **botnet**), it is called **DDoS** (Distributed DoS): the distribution
makes the origin hard to block and multiplies the volume.

Unlike most of the techniques documented in the repository, DoS does not aim to obtain access or data: it targets
**impact on availability** (the "A" of the CIA triad). This is why in a penetration-test engagement it is
normally **excluded** from scope: you document the defensive posture, you do not run the attack.

## Categories

| category | exhausted resource | example mechanism | metric |
| :--- | :--- | :--- | :--- |
| **volumetric** | network bandwidth | udp/icmp flood, amplification/reflection | gbps / tbps |
| **protocol (state exhaustion)** | connection state/tables (firewall, lb, server) | syn flood, ack flood, fragmentation | pps (packets/s) |
| **application (layer 7)** | application capacity (cpu, threads, db) | http flood, expensive requests, slowloris (slow connections kept open) | rps (requests/s) |

Application attacks are the most insidious: low volumes (hard to distinguish from legitimate traffic) but high
cost for the server (e.g., a heavy search repeated).

## Amplification and reflection (concept)

The technique that generates the highest volumes abuses misconfigured public UDP services as **amplifiers**:

```
Attacker (spoofed victim IP) --small request--> Public UDP server (DNS/NTP/memcached)
Public server --large response--> Victim (because the source IP was spoofed)
```

- **Source IP spoofing**: the attacker puts the victim's IP as the sender; the response goes to the victim.
- **Amplification factor**: the response/request ratio. DNS ~ x50, NTP (monlist) ~ x500, **memcached** up to
  ~ x50,000. The 2018 GitHub attack (1.35 Tbps) abused exactly exposed memcached.

The root of the problem is twofold: UDP services exposed that answer anyone, and networks that **do not filter
spoofing** outbound (lack of BCP38/ingress filtering adoption).

## Relation to botnets

Modern volumetric DDoS is powered by **botnets**: thousands of compromised devices (often IoT with weak
credentials, see [malware taxonomy](<../malware-taxonomy/README.en.md>)) that send traffic at the C2's command.
**Mirai** (2016) is the example: mass compromise of IoT cameras/routers, used for attacks beyond the Tbps (Dyn,
OVH, Krebs).

## Detection and mitigation (blue team)

**Detection.**
- Anomalous spikes of inbound traffic (Gbps/pps) or L7 requests (rps) versus the baseline.
- Many sources generating similar requests; anomalous geographic distribution; repetitive user-agent/patterns.
- NetFlow/sFlow to quickly identify the type (volumetric vs protocol vs L7).

**Mitigation.**
- **Upstream (provider)**: scrubbing centers, anti-DDoS services (absorb the volume before it reaches the
  origin); blackholing/RTBH as a last resort.
- **Architecture**: **anycast** (distributes load across multiple PoPs), CDN (absorbs and caches),
  over-provisioning.
- **Protocol**: SYN cookies, connection-state limits, per-IP rate limiting.
- **Application (L7)**: WAF, rate limiting, CAPTCHA/challenge, caching of expensive responses.
- **Against amplification**: do not expose unnecessary UDP services; disable `monlist` (NTP); adopt **BCP38**
  (ingress filtering) to prevent spoofing outbound from your own network.

## MITRE ATT&CK mapping

| tactic | technique | mitre id |
| :--- | :--- | :--- |
| impact | network denial of service | `T1498` |
| impact | network denial of service: direct network flood | `T1498.001` |
| impact | network denial of service: reflection amplification | `T1498.002` |
| impact | endpoint denial of service | `T1499` |
| impact | endpoint denial of service: application exhaustion / service exhaustion flood | `T1499.003` / `T1499.002` |

## References

- MITRE ATT&CK, Impact tactic (`T1498`, `T1499`).
- BCP38 / RFC 2827 (Network Ingress Filtering) against source IP spoofing.
- Historical cases: Mirai (2016, IoT botnet); GitHub (2018, memcached amplification, 1.35 Tbps).

---

## Links to the operational modules

| concept | related module | link |
| :--- | :--- | :--- |
| botnet as the ddos source | [malware taxonomy](<../malware-taxonomy/README.en.md>) | the bots (often iot) are the engine of the volume |
| detection and mitigation | [08-defense-hardenings](<../../08-defense-hardenings (Blue Team Prevention)/README.en.md>) | traffic monitoring, rate limiting, network hardening |
| anti-spoofing filters (bcp38) | networking / edge-router configuration | cut the amplification surface at the root (not specific to one module) |

---

> **Note:** Educational and conceptual content, defense-oriented. It contains no tools or procedures to run a DoS/DDoS attack.
