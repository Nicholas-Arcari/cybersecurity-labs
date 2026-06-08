> **English** | [Italiano](README.md)

# 14 - Configure an IDS (Suricata)

> - **Phase:** System Setup - Network Intrusion Detection
> - **Priority:** High for exposed environments; Medium for isolated VMs
> - **Prerequisites:** Sudo access; network interface identified (`ip a`)
> - **Estimated time:** 20-30 minutes (installation + base rule configuration)

---

## Commands

```Bash
# Installation
sudo apt install -y suricata

# Update Emerging Threats rules (attack signature database)
sudo suricata-update

# Configure listening interface (replace eth0 with your interface)
sudo vim /etc/suricata/suricata.yaml
# Find the "af-packet:" line and set the correct interface

# Start and enable at boot
sudo systemctl enable --now suricata

# Verify status
sudo systemctl status suricata
sudo tail -f /var/log/suricata/fast.log   # Real-time alert log
```

---

## Why do it?

Kali Linux Purple is a distribution designed also for Blue Team and Threat Hunting. An IDS (Intrusion Detection System) is the network's "surveillance camera": it analyzes every packet in transit and generates an alarm when it detects known attack signatures (port scan, exploits, C2 beaconing, data exfiltration).

## What happens next?

Suricata will analyze network traffic in real time. When someone runs Nmap against the machine, when malware attempts a C2 connection, or when an exploit traverses the network, Suricata generates an alert in `/var/log/suricata/fast.log` and in structured JSON format in `eve.json`.

## What's the risk if you don't?

You will never know if someone is scanning or attacking the system until it is too late. In a lab environment, having no visibility into inbound traffic means being unable to correlate alerts with ongoing exploitation activities.

---

## Reference Tools

| Tool | Type | Use Case |
| :--- | :--- | :--- |
| `Suricata` | IDS/IPS | Network packet inspection with Emerging Threats rules |
| `Snort` | Alternative IDS | Classic IDS, same rule architecture as Suricata |
| `Zeek` (Bro) | Network monitor | Behavioral traffic analysis, structured logging |
| `suricata-update` | Rule manager | Automatic rule update from ET Open and other sources |
| `evebox` | Log viewer | Web GUI for viewing Suricata `eve.json` alerts |

---

> **Note:** To integrate Suricata with a SIEM, configure the `eve.json` output and send it to Elasticsearch (ELK stack) or Splunk. In lab environments, `tail -f /var/log/suricata/fast.log` is sufficient for real-time monitoring during testing sessions.
