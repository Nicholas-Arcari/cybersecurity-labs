> **English** | [Italiano](README.md)

# ELK Stack - The Open Source SIEM (Elasticsearch, Logstash, Kibana)

> - **Phase:** Defense & Hardening - Detection & Log Analysis (SIEM)
> - **Category:** Detection - log centralization and correlation
> - **Prerequisites:** Host with at least 8 GB RAM (the Indexer JVM is demanding); Docker/Docker Compose or Elastic packages; log sources to forward (endpoints, firewall, servers)
> - **Output:** Finding DEF-001; centralized logging platform; detection and threat hunting capability over all the logs of the environment

- **Operating Environment:** Kali/Debian (SIEM server), Linux/Windows endpoints with Beats/agent
- **Role:** "The Brain" - aggregates and correlates everything the other tools generate
- **Main tools:** Elasticsearch, Logstash, Kibana, Filebeat/Winlogbeat

---

## Executive Summary

The ELK Stack (Elasticsearch, Logstash, Kibana) is the open source alternative to commercial SIEMs like Splunk (`../splunk/`). It is the backbone of defensive detection: where the individual tools see a fragment (Wazuh a suspicious file, Suricata an anomalous packet), the SIEM aggregates everything in a single point and allows correlating events that, in isolation, would seem harmless.

The three components divide the work: **Elasticsearch** is the distributed search and storage engine that indexes the logs; **Logstash** is the ingestion pipeline that receives, normalizes and enriches the logs before indexing them; **Kibana** is the interface for visualization, search and alerting. The logs arrive from the endpoints via the **Beats** (Filebeat for log files, Winlogbeat for Windows Event Logs).

Finding DEF-001 documents the detection capability enabled by centralization: without a SIEM, logs remain isolated on the individual hosts, where an attacker can delete them (see `07-post-exploitation/05-exfiltration-cleanup/log-cleaning/`). With the ELK Stack forwarding the logs in real time, defensive visibility becomes structural and resistant to tampering.

---

## Folder Structure

```
elk-stack/
+-- README.md      # this file: ELK deploy + centralized detection (DEF-001)
+-- img/           # Kibana dashboard and detection rules
```

---

## Centralized Detection with ELK

**Finding ID:** `DEF-001` | **Severity:** `High` (log centralization is the founding defensive capability: without visibility there is no detection)

### Operational Context

The value of the SIEM is not to archive the logs but to make them queryable and correlatable in real time. The clearest didactic use case is the detection of an SSH brute force: a single failed login is noise, but dozens of failed logins from the same IP in a few seconds are an attack. Only an engine that aggregates the authentication logs of all the hosts can detect this pattern.

### PoC - Phase 1: Stack deployment (Docker Compose)

```Bash
# Minimal ELK stack in Docker (single-node for the lab)
docker compose -f elk-docker-compose.yml up -d

# Verify that Elasticsearch responds
curl -s http://localhost:9200/_cluster/health | jq .status
```

```
"green"                                    <-- ELK cluster operational
```

### PoC - Phase 2: Endpoint log ingestion (Filebeat)

```YAML
# /etc/filebeat/filebeat.yml (on the endpoint to monitor)
filebeat.inputs:
  - type: filestream
    paths:
      - /var/log/auth.log        # SSH/sudo authentication logs
output.logstash:
  hosts: ["SIEM_IP:5044"]        # forwarding to the Logstash pipeline
```

```Bash
# Start and verify the forwarding
sudo systemctl enable --now filebeat
sudo filebeat test output
```

```
logstash: SIEM_IP:5044...
  connection...
    parse host... OK
    talk to server... OK          <-- logs forwarded to the SIEM in real time
```

### PoC - Phase 3: Detection rule (SSH brute force)

```
# KQL query in Kibana: failed SSH logins aggregated by source IP
event.dataset : "system.auth" and system.auth.ssh.event : "Failed"

# Alerting rule (Kibana): threshold -> more than 10 "Failed" from the same
# source.ip in a 60-second window -> generate an alert
```

```
[ALERT] SSH Brute Force Detected
  source.ip: 10.0.2.15
  count: 47 failed logins in 38s        <-- brute force detected (DEF-001)
  host.name: web-prod-01
```

### Tuning and Defensive Operations

- **False positive reduction:** exclude known management IPs and automated jobs; calibrate the thresholds on the real behavior of the environment (a legitimate bastion host generates more logins than a workstation)
- **Resilience:** the key value of the SIEM is that the logs leave the host in real time, so an attacker who compromises the endpoint cannot delete the already-forwarded logs (structural countermeasure to log tampering, `07-post-exploitation`)
- **Retention and integrity:** define a retention policy (ILM - Index Lifecycle Management) and protect access to the Indexer; the log storage must be out of reach of the monitored accounts
- **Escalation:** every alert rule must have an associated response procedure (who is notified, which containment steps)

---

## Lab Experience

The first obstacle was predictable and consistent with what was already seen on Wazuh (`../../02-endpoint-security-xdr/wazuh/installing&configuring/`): the RAM hunger of Elasticsearch. With the default JVM heap the stack saturated the lab VM's memory; limiting the heap to 2 GB (`ES_JAVA_OPTS=-Xms2g -Xmx2g`) stabilized everything. It is the same lesson as the Wazuh Indexer, which on closer inspection is OpenSearch, a fork of Elasticsearch: the technological kinship is direct.

The operational revelation was seeing correlation in action. I generated the SSH brute force from a second host and watched the failed logins materialize in Kibana within a few seconds, aggregated by source IP. The single event says nothing; the aggregate view turns noise into signal. This made concrete why the SIEM is "the brain": it does not add new sensors, but gives meaning to the data the sensors already produce.

The ELK vs Splunk choice (`../splunk/`) became clear in the field: ELK is free and very powerful, but requires manually building pipelines, parsing and dashboards. Splunk offers a lot ready to use but at the cost of a license. For a home lab and to learn the fundamentals, ELK is the better learning choice precisely because it forces you to understand every piece of the chain.

---

## Theoretical Analysis: Why Centralization Is the Precondition of Detection

Effective detection requires three properties that only a centralized log guarantees: **completeness** (all logs in one place), **correlation** (events from different sources put in temporal relation) and **integrity** (the logs out of reach of the attacker). A local log on a compromised host has none of the three: it is partial, isolated and tamperable.

Correlation is the qualitative leap. The kill chain of an attack leaves traces on different systems: a suspicious login on the firewall, an anomalous process on an endpoint, an unusual outbound connection. Each, in isolation, is below the alarm threshold; together, in the same time window, they draw the attack. The SIEM is the only point from which this correlation is possible, because it is the only one that sees everything simultaneously.

This links directly to the anti-forensics principle seen in `07-post-exploitation`: the mature attacker deletes the local logs to hinder the analysis. The SIEM neutralizes this move by moving the logs to a system the attacker does not control, at the very moment of their generation. Detection and log integrity are therefore two sides of the same coin: one cannot detect what one does not see, and one cannot trust what the adversary can rewrite.

---

## Real-World Scenario: Detection in Action

> This section describes how this defensive control would operate in a real incident, showing the attacker's perspective and the defender's response.

### Attacker Perspective (what they attempt)

The attacker launches an SSH brute force against an exposed server, trusting that the failed attempts get lost in the local logs and that no one looks at them. In an environment without a SIEM, this bet wins: the logs remain on the host, invisible until someone inspects them manually.

### Defender Perspective (how the control responds)

```
[DEF-001] Filebeat forwards auth.log in real time -> Logstash -> Elasticsearch
        |
        v
Kibana rule: >10 failed SSH logins / same IP / 60s -> ALERT
        |
        v
SOC notified in <1 minute from the start of the attack
        |
        v
Containment: block the source IP (firewall / Wazuh active response)
        |
        v
Threat hunting: retrospective query over the whole environment for the same IP
```

**Defensive value:** centralization turns a silent attack into an event detected in near real time. The retrospective query is the second value: once the hostile IP is identified, the SIEM allows searching for it across all the historical logs of all the hosts, revealing the entire extent of the attacker's activity - impossible with isolated logs.

**Monitored indicators (IOC):** spikes of failed authentications per IP, successful logins after a series of failures (successful brute force), accesses from anomalous geolocations or times, correlation between Suricata/Wazuh alerts and the network logs.

**Defensive lesson:** a SIEM does not prevent the attack, it makes it visible. But visibility is the precondition of every other defense: one cannot contain, investigate or learn from what one did not see happen.

---

## Reference Tools

| Tool | Type | Role | Main use case |
| :--- | :--- | :--- | :--- |
| `Elasticsearch` | Search/storage engine | Backend | Indexing and full-text search of the logs |
| `Logstash` | Ingestion pipeline | Backend | Parsing, normalization and enrichment of the logs |
| `Kibana` | Visualization/alerting | Frontend | Dashboards, KQL queries, detection rules |
| `Filebeat` / `Winlogbeat` | Log shipper | Agent | Forwarding of the logs from Linux/Windows endpoints |
| `Elastic SIEM` (Security) | Detection app | Module | Ready-made detection rules + native MITRE mapping |
| `ElastAlert2` | Alerting engine | Add-on | Advanced alerting on self-hosted ELK clusters |

> **Recommended modern tool:** the `Elastic Security` module (formerly SIEM app) integrates ready-to-use detection rules with native MITRE ATT&CK mapping and enormously reduces the manual configuration work. For modern ingestion, `Elastic Agent` unifies the various Beats into a single centrally-managed agent. Comparison with the commercial alternative in `../splunk/`.

---

## MITRE ATT&CK Mapping

> In a defensive module, the table maps the attack techniques that the control **detects**. Complementary defensive reference: MITRE D3FEND (countermeasures).

| Tactic (detected) | Technique | MITRE ID | Role of the control |
| :--- | :--- | :--- | :--- |
| Credential Access | Brute Force: Password Guessing | `T1110.001` | Detection via aggregation of failed logins per IP (DEF-001) |
| Credential Access | Brute Force: Password Spraying | `T1110.003` | Detection of an IP attempting many accounts with few passwords |
| Initial Access | Valid Accounts | `T1078` | Detection of a successful login after a series of failures (successful brute force) |
| Defense Evasion | Indicator Removal: Clear Linux Logs | `T1070.002` | Real-time forwarding makes the deletion of local logs ineffective |

| Defensive countermeasure (D3FEND) | D3FEND ID | Application |
| :--- | :--- | :--- |
| Platform Monitoring | `D3-PM` | Centralized collection and monitoring of system logs |
| User Behavior Analysis | `D3-UBA` | Analysis of authentication patterns to detect anomalies |

---

> **Note:** All documented activities were conducted on a lab environment owned by the author. The detection was validated against simulated traffic and attacks on the test systems. Log monitoring must comply with privacy and data-processing regulations (in real contexts, authentication and network logs may contain personal data). Techniques are documented for educational and defensive purposes in an authorized context.
