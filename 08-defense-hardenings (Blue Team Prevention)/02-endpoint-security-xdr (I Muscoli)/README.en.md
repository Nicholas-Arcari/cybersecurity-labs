> **English** | [Italiano](README.md)

# 02 - Endpoint Security & XDR (The Muscles)

> - **Phase:** Defense & Hardening - Detection & Automated Response (Endpoint)
> - **Category:** Detection + Prevention - sensors and response on the endpoint
> - **Prerequisites:** XDR Manager/platform and agents on the endpoints; adequate resources on the server; agent-manager connectivity
> - **Output:** Findings DEF-003..004; endpoint visibility and response; detection of persistence, tampering and threats; automatic containment

---

## Introduction

If the SIEM (`../01-siem-log-analysis/`) is "the brain" that sees and correlates, endpoint security is "the muscles": it is where the defense not only observes but acts, directly on the system where the threat manifests. The evolution goes from the classic antivirus (static signatures) to EDR (Endpoint Detection and Response, behavioral analysis) to XDR (Extended Detection and Response, which extends visibility and response beyond the endpoint, correlating network, cloud and identity).

The key difference from the SIEM is the closeness to action. The SIEM receives the logs and analyzes them after the fact; the agent on the endpoint lives inside the system, sees the processes being born, the files changing, the connections opening, and can intervene in real time - terminate a process, block an IP, isolate the host. It is the difference between an analyst who reads a report and a guard present on the spot.

The section is centered on **Wazuh**, the reference open source XDR platform:

1. **Installation and configuration:** the deployment of the Manager and the agents on Linux, Windows and Raspberry Pi, with the real troubleshooting (Indexer RAM management, versions, SSL).

2. **Suricata integration:** the union of Wazuh (what happens inside the system) with Suricata (what passes on the network), turning the platform into SIEM + IDS.

3. **Threat Detection & Active Response (DEF-003, DEF-004):** the File Integrity Monitoring that detects persistence and tampering, and the active response that automatically contains the attacker.

The positioning in the path: the endpoint agents are the sensors that generate the alerts, the SIEM is the brain that correlates them. Together, sensors and brain form the cycle detection, correlation, response.

---

## Folder Structure

```
02-endpoint-security-xdr (I Muscoli)/
+-- README.md          # this file: DEF-003..004 registry, EDR/XDR concept
|
+-- wazuh/             # the open source XDR platform
    +-- README.md                          # what Wazuh is
    +-- installing&configuring/            # Manager + agents deployment (setup)
    +-- suricata-integration/              # Wazuh + Suricata = SIEM + IDS (setup)
    +-- threat-detection&active-response/  # DEF-003 (FIM), DEF-004 (active response)
```

---

## Recommended Operational Flow

```
[INPUT] Endpoint to protect (Linux/Windows/RPi)
         |
         v
[1] Deployment (wazuh/installing&configuring/)
     +-- Manager + agents -> endpoint visibility
              |
              v
[2] Network extension (wazuh/suricata-integration/)
     +-- Suricata IDS -> Wazuh reads eve.json -> SIEM + IDS
              |
              v
[3] Detection (wazuh/threat-detection&active-response/)
     +-- FIM -> detects persistence/tampering (DEF-003)
              |
              v
[4] Automated response
     +-- active response -> attacker IP block in seconds (DEF-004)
              |
              v
[OUTPUT] Alert -> SIEM (01) for correlation + automatic containment
```

---

## Reference Tools

| Tool | Type | Role | Main use case |
| :--- | :--- | :--- | :--- |
| `Wazuh` | Open source XDR | Platform | Endpoint detection, FIM, active response |
| `Wazuh Agent` | Endpoint sensor | Agent | Telemetry and response on Linux/Windows/RPi |
| `Suricata` | IDS | Integration | Correlated network detection in Wazuh |
| `Sysmon` | Endpoint sensor | Agent (Win) | Detailed process telemetry |
| `OSSEC` | HIDS | Alternative | The project Wazuh derives from (legacy) |

> **Recommended modern tool:** `Wazuh` is the open source standard for EDR/XDR, with FIM, vulnerability detection, active response and MITRE integration. Pairing with `Sysmon` on the Windows endpoints brings the telemetry to commercial EDR level. Commercial alternatives: CrowdStrike Falcon, Microsoft Defender for Endpoint, SentinelOne.

---

## Finding Registry - Endpoint Security & XDR Section

| ID | Description | Severity | Subfolder |
| :--- | :--- | :---: | :--- |
| `DEF-003` | Wazuh FIM: detection of persistence, tampering of critical files and rootkits | `High` | `wazuh/threat-detection&active-response/` |
| `DEF-004` | Wazuh Active Response: automatic containment (IP block) on alert | `High` | `wazuh/threat-detection&active-response/` |

> The `installing&configuring/` and `suricata-integration/` files are setup/configuration guides (no finding ID, consistent with the convention for installation files).

---

## MITRE ATT&CK Mapping - Aggregated

> Attack techniques **detected and contained** by the controls of the section.

| Tactic (countered) | Technique | MITRE ID | Related Finding |
| :--- | :--- | :--- | :--- |
| Persistence | Account Manipulation: SSH Authorized Keys | `T1098.004` | DEF-003 |
| Persistence | Boot or Logon Autostart: Registry Run Keys | `T1547.001` | DEF-003 |
| Defense Evasion | Rootkit | `T1014` | DEF-003 |
| Credential Access | Brute Force | `T1110` | DEF-004 |

---

> **Note:** All activities documented in this section were conducted on a lab environment owned by the author. The attack simulations to validate the sensors were performed on test systems. Active response must be configured carefully to avoid self-blocks. Techniques are documented for educational and defensive purposes in an authorized context.
