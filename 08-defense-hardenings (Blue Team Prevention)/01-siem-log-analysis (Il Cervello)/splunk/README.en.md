> **English** | [Italiano](README.md)

# Splunk - correlation and threat hunting with SPL

> - **Phase:** Defense & Hardening - Detection & Correlation (commercial SIEM)
> - **Category:** Detection - multi-source correlation and threat hunting
> - **Prerequisites:** Splunk Enterprise (60-day trial license) or Splunk Free (500 MB/day); Universal Forwarder on the endpoints; configured log sources
> - **Output:** Finding DEF-002; multi-source correlation capability; reusable SPL queries for the detection of common attacks

- **Operating Environment:** Splunk server (dedicated VM), endpoints with Universal Forwarder
- **Role:** The correlator - joins events from firewall, servers and endpoints into a single narrative
- **Main tools:** Splunk Enterprise, Universal Forwarder, SPL (Search Processing Language)

---

## Executive summary

Splunk is the industry-reference commercial SIEM. Compared to the ELK Stack (`../elk-stack/`) it offers a lot ready to use - automatic parsing, pre-built apps, an extremely expressive search language (SPL) - at the cost of a license based on the volume of data ingested per day.

The distinctive value of Splunk, as per the strategic note of this lab, is **correlation**. The difference between the three defensive tools of the path is stark:

- **Wazuh (`../../02-endpoint-security-xdr/wazuh/`)** tells you: "There's a suspicious file on this PC" (endpoint view).
- **Splunk** tells you: "I saw a strange connection from the firewall + a failed login on the server + a Wazuh alert, all in the same minute" (correlation).
- **Wireshark (`../../../09-digital-forensics (Blue Team Analysis)/`)** you open afterwards, to look inside the individual packets and understand what they contained (detail analysis).

Finding DEF-002 documents the correlation capability: building SPL queries that join different sources to detect attack patterns (brute force, port scanning, lateral movement) that no single source would reveal alone.

---

## Folder structure

```
splunk/
+-- README.md            # this file: SPL correlation and threat hunting (DEF-002)
+-- SPL-Queries/         # library of SPL queries for detection (brute force, port scan, ...)
+-- Data-Ingestion/      # Universal Forwarder configuration
+-- Dashboards/          # XML/JSON export of the defensive dashboards
+-- img/                 # detection screenshots
```

---

## Detection via SPL correlation

**Finding ID:** `DEF-002` | **Severity:** `High` (multi-source correlation detects attacks invisible to the individual isolated sources)

### Operational context

The Search Processing Language (SPL) is Splunk's proprietary language: a pipeline of commands (Unix-style, chained with `|`) that filters, aggregates and correlates the events. Building a library of SPL queries for common attacks is the central defensive work: each query encodes the "behavioral signature" of an attack.

### PoC - log ingestion (universal forwarder)

```Bash
# On the endpoint: the Universal Forwarder forwards the logs to Splunk
# /opt/splunkforwarder/etc/system/local/outputs.conf
[tcpout:default]
server = SPLUNK_IP:9997

# Definition of what to forward (inputs.conf)
[monitor:///var/log/auth.log]
sourcetype = linux_secure
```

```Bash
# Verify the forwarding from the Splunk server
/opt/splunk/bin/splunk list forward-server
```

```
Active forwards:
    10.0.2.30:9997                        <-- endpoint forwarding the logs
```

### PoC - SPL query: brute force detection

```
index=* sourcetype=linux_secure "Failed password"
| stats count by src_ip, user
| where count > 10
| sort - count
```

```
src_ip        user     count
10.0.2.15     root     47        <-- brute force on root (DEF-002)
10.0.2.15     admin    31
```

### PoC - SPL query: port scanning detection

```
index=* sourcetype=firewall action=blocked
| stats dc(dest_port) as distinct_ports by src_ip
| where distinct_ports > 50
```

```
src_ip        distinct_ports
10.0.2.15     1024              <-- a single IP toward 1024 ports = port scan
```

### PoC - SPL query: multi-source correlation (the real value)

```
# Correlates: network scan (firewall) FOLLOWED BY successful login (server)
# from the same IP within 5 minutes -> successful attack, not just an attempt
index=* (sourcetype=firewall action=blocked) OR (sourcetype=linux_secure "Accepted password")
| transaction src_ip maxspan=5m
| search action=blocked AND "Accepted password"
```

```
src_ip        events
10.0.2.15     scan(1024 ports) -> successful login user=svc_web   <-- correlated kill chain (DEF-002)
```

This is the correlation that no single source can provide: the firewall sees the scan, the server sees the login, but only Splunk sees that they are the same attacker and that the second event is the consequence of the first.

### Tuning and defensive operations

- **Save the queries as Saved Searches:** every detection query should be saved as a scheduled alert with a threshold and an action (notification, ticket, active response)
- **False positive reduction:** whitelist the authorized vulnerability scanners and bastion hosts; calibrate the thresholds to the environment
- **Acceleration:** for large datasets, use Data Models and tstats for performant queries; dashboards should query summary indexes, not raw data
- **License:** Splunk bills on the ingested volume/day; filtering upstream (in inputs.conf) what is not needed for detection reduces costs and noise

---

## Lab experience

The learning curve of Splunk was the inverse of ELK: where ELK requires building everything but teaches every piece, Splunk starts productive immediately but hides the complexity. Within a few minutes, with the Universal Forwarder configured, the logs were searchable; writing the first brute force query in SPL was immediate and intuitive (`stats count by src_ip | where count > 10`). This immediacy explains why Splunk dominates the enterprise market despite the cost.

The formative moment was understanding the `transaction` command. The counting queries (brute force, port scan) I already mastered conceptually from ELK; the temporal correlation between different sources - grouping heterogeneous events by `src_ip` within a window and verifying a sequence - was the real novelty. Seeing the scan and the successful login joined into a single "transaction" made tangible the difference between a SIEM that aggregates and a SIEM that correlates.

The strategic note of the lab became clear using the tools side by side: Splunk told me THAT something happened and HOW the events connected, but to understand EXACTLY what the traffic contained I had to open the pcap in Wireshark (module 09). The three tools do not compete, they complement each other along the chain detection, correlation, detail analysis.

---

## Theoretical analysis: correlation as kill chain reconstruction

An attack is not a single event but a sequence: reconnaissance, initial access, escalation, lateral movement, action on objective. Each phase generates events on different systems and, taken in isolation, each event is below the alarm threshold - a port scan is "Internet noise", a successful login is "normal activity". Correlation reconstructs the sequence, and the sequence is the attack.

Splunk formalizes this with `transaction` and with the Data Models: it groups heterogeneous events around a common entity (an IP, a user, a session) and orders them in time. It is the inverse operation to the attacker's, who distributes their activity across different systems and times precisely to stay below the thresholds. The defender who correlates cancels this dispersion, recomposing the fragments into a narrative.

This defines Splunk's place in the defensive architecture: it is not a sensor (it does not generate its own data) but an analytical brain that reasons over the sensors' data. Its limit mirrors its value: it correlates only what it receives. Missing sources are blind spots in the correlation, which is why the completeness of the ingestion (Data-Ingestion) is as important as the sophistication of the queries.

---

## Real-World scenario: detection in action

> This section describes how this defensive control would operate in a real incident.

### Attacker perspective (what they attempt)

The attacker deliberately distributes their activity to stay below the thresholds: a slow scan, a few scattered login attempts, a "legitimate" access minutes apart. They trust that each system, looking only at its own logs, sees nothing alarming.

### Defender perspective (how the control responds)

```
[DEF-002] Universal Forwarder -> Splunk indexes firewall + server + Wazuh logs
        |
        v
Scheduled Saved Search: transaction by src_ip (scan -> successful login, 5m)
        |
        v
ALERT: correlated kill chain -> the IP moved from recon to access
        |
        v
Containment: block IP + disable the compromised account (svc_web)
        |
        v
Threat hunting: pivot on svc_web -> every system touched by the account
```

**Defensive value:** correlation turns three "harmless" events into an evident kill chain. Once the compromised account is identified, the SPL pivot reveals the entire extent of the access - which systems, which times, which data touched - providing the real scope of the incident.

**Monitored indicators (IOC):** scan, access sequences from the same IP, an account appearing on unusual hosts, successful logins preceded by failures, accesses correlated to Wazuh/Suricata alerts in the same interval.

**Defensive lesson:** the attacker wins by dispersing, the defender wins by correlating. Mature detection does not look for the single malicious event (often indistinguishable from normal) but for the sequence that only an attack produces.

---

## Reference tools

| tool | type | role | main use case |
| :--- | :--- | :--- | :--- |
| `Splunk Enterprise` | commercial siem | platform | indexing, spl, alerting, dashboards |
| `Universal Forwarder` | log shipper | agent | lightweight forwarding of the logs from the endpoints |
| `SPL` | search language | language | detection and correlation queries |
| `Splunk ES` (enterprise security) | premium siem | app | ready-made correlation searches + mitre framework |
| `Splunk Free` | siem (limited) | platform | lab and small volumes (500 mb/day, no auth) |
| `Sysmon` | endpoint sensor | agent (win) | detailed process telemetry to correlate in spl |

> **Recommended modern tool:** for a production environment, `Splunk Enterprise Security` (ES) provides ready-to-use correlation searches mapped to MITRE ATT&CK. In a home lab, `Splunk Free` is sufficient to learn SPL. Pairing with `Sysmon` on the Windows endpoints provides the process telemetry that makes the correlation much richer. Complete open source alternative in `../elk-stack/`.

---

## MITRE ATT&CK mapping

> The table maps the attack techniques that the control **detects** via SPL correlation.

| tactic (detected) | technique | mitre id | role of the control |
| :--- | :--- | :--- | :--- |
| reconnaissance | active scanning: scanning ip blocks | `T1595.001` | spl query: an ip toward many distinct ports (port scan) (DEF-002) |
| credential access | brute force | `T1110` | spl query: aggregation of failed logins per ip/user (DEF-002) |
| initial access | valid accounts | `T1078` | correlation scan - successful login (access obtained) |
| lateral movement | remote services | `T1021` | correlation: same account on multiple hosts in sequence |

| defensive countermeasure (d3fend) | d3fend id | application |
| :--- | :--- | :--- |
| network traffic analysis | `D3-NTA` | correlation of the network logs to detect scanning and accesses |
| user behavior analysis | `D3-UBA` | detection of anomalous activity sequences per user/ip |

---

> **Note:** All documented activities were conducted on a lab environment owned by the author, with simulated attacks on the test systems. Log monitoring in real contexts must comply with privacy and data-processing regulations. Techniques are documented for educational and defensive purposes in an authorized context.
