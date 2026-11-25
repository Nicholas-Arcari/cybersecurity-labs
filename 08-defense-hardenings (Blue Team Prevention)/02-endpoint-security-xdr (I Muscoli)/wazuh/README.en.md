> **English** | [Italiano](README.md)

# Wazuh - open source XDR platform

> - **Phase:** Defense & Hardening - Endpoint Detection & Response (XDR)
> - **Category:** Detection + Prevention - the central defensive platform of the module
> - **Prerequisites:** Server with adequate resources (RAM for the Indexer); endpoints to monitor; agent-manager connectivity (ports 1514/1515)
> - **Output:** Operational detection and response platform; base for findings DEF-003, DEF-004

---

## What Wazuh is

Wazuh is an open source security platform that unifies in a single solution functions that traditionally required separate tools: XDR (Extended Detection and Response) and SIEM. Born as a fork of OSSEC (a historic HIDS), Wazuh extended it with a modern analysis engine based on OpenSearch (a fork of Elasticsearch), a web dashboard and a rich set of defensive features.

Its capabilities cover the entire spectrum of endpoint defense:

- **File Integrity Monitoring (FIM):** watches critical files and directories, detecting unauthorized modifications (persistence, tampering).
- **Threat Detection:** analyzes logs and events against a set of rules to detect anomalies and known threats.
- **Rootcheck:** searches for rootkits, malware and anomalous configurations.
- **Vulnerability Detection:** correlates the installed software with the CVE databases to flag known vulnerabilities.
- **Active Response:** automatically executes containment actions (IP block, process kill) when a rule triggers.
- **Compliance:** maps events to compliance frameworks (PCI DSS, GDPR, HIPAA, NIST) and to MITRE ATT&CK.

The architecture is client-server: the **agents** installed on the endpoints (Linux, Windows, macOS, Raspberry Pi) collect telemetry and send it to the **Manager**, which decodes it, analyzes it against the rules and generates the alerts; the **Indexer** (OpenSearch) archives them and makes them searchable; the **Dashboard** visualizes them. This separation between collection (agent) and analysis (Manager) is what makes Wazuh both an endpoint sensor and a lightweight SIEM.

---

## Folder structure

```
wazuh/
+-- README.md                          # this file: what Wazuh is (concept and architecture)
|
+-- installing&configuring/            # Manager + agents deployment + real troubleshooting
+-- suricata-integration/              # Wazuh + Suricata = SIEM + IDS
+-- threat-detection&active-response/  # DEF-003 (FIM/detection), DEF-004 (active response)
```

---

## Recommended path

```
[1] installing&configuring/
     +-- deployment of the Manager on Kali + agents on Windows/RPi
     +-- troubleshooting: Indexer RAM, versions, SSL/TLS
              |
              v
[2] suricata-integration/
     +-- Suricata as a network IDS -> Wazuh reads eve.json
     +-- from endpoint monitoring to complete SIEM + IDS
              |
              v
[3] threat-detection&active-response/
     +-- FIM: detects persistence and tampering (DEF-003)
     +-- active response: automatic containment (DEF-004)
```

---

## Reference tools

| component | role | function |
| :--- | :--- | :--- |
| `Wazuh Manager` | analysis | decodes logs, applies rules, generates alerts, manages active response |
| `Wazuh Indexer` | storage | indexing and search (opensearch); ram-hungry |
| `Wazuh Dashboard` | visualization | web interface, threat hunting, management |
| `Wazuh Agent` | collection | telemetry and response on the endpoints |
| `Suricata` | network ids | integrated network detection (`suricata-integration/`) |

> **Note on the architecture:** the Indexer is the most resource-hungry component (JVM/OpenSearch). As documented in `installing&configuring/`, RAM management (limiting the JVM heap) is the main challenge of a deployment on limited hardware. It is the same constraint as the ELK Stack (`../../01-siem-log-analysis/elk-stack/`), given the common OpenSearch/Elasticsearch base.

---

> **Note:** Wazuh is a purely defensive tool. All activities documented in the subfolders were conducted on a lab environment owned by the author. Techniques are documented for educational and defensive purposes in an authorized context.
