> **English** | [Italiano](README.md)

# 01 - SIEM & log analysis (the brain)

> - **Phase:** Defense & Hardening - Detection & Correlation
> - **Category:** Detection - the nerve center of the defense
> - **Prerequisites:** SIEM host with adequate resources (RAM for ELK/Indexer); configured log sources; agents/forwarders on the endpoints
> - **Output:** Findings DEF-001..002; centralized detection platform; correlation and threat hunting capability

---

## Introduction

The SIEM (Security Information and Event Management) is "the brain" of the defense: the point where all the logs of the environment converge and where isolated events become detection. The theoretical premise is simple but fundamental: a single log does not tell an attack. A failed login is noise, a port scan is Internet background noise, a new process is normal activity. It is their correlation - in time, across different sources - that reveals the kill chain.

A SIEM performs four functions: **collection** (it aggregates the logs from endpoints, firewalls, servers), **normalization** (it uniforms heterogeneous formats), **correlation** (it relates events from different sources) and **alerting** (it notifies when a pattern matches an attack signature). Without a SIEM, the logs remain isolated on the individual hosts - partial, non-correlatable and tamperable by the attacker who compromises the host.

The section compares the two reference approaches:

1. **ELK Stack (DEF-001):** the open source alternative (Elasticsearch, Logstash, Kibana). Free and very powerful, it requires manually building pipelines and dashboards. The learning choice that teaches every piece of the chain.

2. **Splunk (DEF-002):** the reference commercial SIEM. Very ready to use, with the expressive SPL language for correlation, at the cost of a license based on the ingested volume.

The positioning in the defensive path: the SIEM receives the alerts from the tools of the other layers - Wazuh/XDR (`../02-endpoint-security-xdr/`), the honeypots (`../03-deception/`) - and correlates them. It is the brain that gives meaning to the data the sensors produce.

---

## Folder structure

```
01-siem-log-analysis (Il Cervello)/
+-- README.md          # this file: DEF-001..002 registry, SIEM concept
|
+-- elk-stack/         # DEF-001: open source SIEM (Elasticsearch, Logstash, Kibana)
+-- splunk/            # DEF-002: commercial SIEM, SPL correlation
```

---

## Recommended operational flow

```
[INPUT] Logs from endpoints, firewalls, servers, Wazuh, Suricata
         |
         v
[1] Platform choice
     +-- open source / learning / zero budget -> elk-stack/ (DEF-001)
     +-- enterprise / ready to use / correlation -> splunk/ (DEF-002)
              |
              v
[2] Ingestion
     +-- Beats / Universal Forwarder -> logs centralized in real time
              |
              v
[3] Detection and correlation
     +-- rules/queries -> brute force, port scan, correlated kill chain
              |
              v
[4] Alerting and response
     +-- alert -> SOC notification / active response (Wazuh DEF-004)
              |
              v
[OUTPUT] Attack detected -> containment + retrospective threat hunting
```

---

## Reference tools

| tool | type | role | main use case |
| :--- | :--- | :--- | :--- |
| `ELK Stack` | open source siem | platform | free and flexible detection and log analysis |
| `Splunk` | commercial siem | platform | spl correlation and enterprise detection |
| `Filebeat`/`Winlogbeat` | log shipper | agent | log forwarding from endpoints (elk) |
| `Universal Forwarder` | log shipper | agent | log forwarding from endpoints (splunk) |
| `Sysmon` | endpoint sensor | agent (win) | process telemetry for advanced detection |

> **Recommended modern tool:** for learning and constrained budgets, `ELK Stack` with the Elastic Security module (native MITRE rules). For the enterprise, `Splunk ES`. In both cases, `Sysmon` on the Windows endpoints enormously enriches the correlatable telemetry.

---

## Finding registry - SIEM & log analysis section

| id | description | severity | subfolder |
| :--- | :--- | :---: | :--- |
| `DEF-001` | elk stack: log centralization and detection (ssh brute force) | `High` | `elk-stack/` |
| `DEF-002` | splunk: multi-source correlation via spl (scan -> access kill chain) | `High` | `splunk/` |

---

## MITRE ATT&CK mapping - aggregated

> Attack techniques **detected** by the controls of the section.

| tactic (detected) | technique | mitre id | related finding |
| :--- | :--- | :--- | :--- |
| credential access | brute force | `T1110` | DEF-001, DEF-002 |
| reconnaissance | active scanning | `T1595` | DEF-002 |
| initial access | valid accounts | `T1078` | DEF-001, DEF-002 |
| lateral movement | remote services | `T1021` | DEF-002 |
| defense evasion | indicator removal: clear logs | `T1070` | DEF-001 (real-time forwarding defeats deletion) |

---

> **Note:** All activities documented in this section were conducted on a lab environment owned by the author, with simulated attacks on the test systems. Log monitoring in real contexts must comply with privacy and data-processing regulations. Techniques are documented for educational and defensive purposes in an authorized context.
