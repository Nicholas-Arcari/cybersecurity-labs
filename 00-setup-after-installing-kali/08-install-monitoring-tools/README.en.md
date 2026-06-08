> **English** | [Italiano](README.md)

# 08 - Install Monitoring Tools

> - **Phase:** System Setup - System Health Monitoring
> - **Priority:** Medium - essential for intensive work sessions (long scans, forensic analysis)
> - **Prerequisites:** System updated; sudo access
> - **Estimated time:** 10-30 minutes (depends on chosen tool)

---

## Commands

For lightweight monitoring (recommended for VM environments):

```Bash
sudo apt install -y glances   # All-in-one terminal dashboard (CPU, RAM, network, disk, processes)
glances                        # Interactive launch
```

For a Zabbix agent (centralized monitoring):

```Bash
sudo apt install zabbix-agent
sudo systemctl enable --now zabbix-agent
```

For Nagios (full service monitoring):

```Bash
sudo apt install nagios3
```

---

## Why do it?

In a defensive environment (Blue Team), you need to know if your sensors and services are active and responsive. During intensive scans (OpenVAS, massive Nmap) or forensic analysis (Volatility on memory dumps), system resources can saturate without warning.

## What happens next?

You will have real-time visibility into CPU, RAM, disk and network usage. Alert thresholds can be set to receive notifications when resources approach saturation.

## What's the risk if you don't?

The system could freeze from full disk or out-of-memory during a critical analysis without giving you any warning, causing loss of work in progress and potentially corrupting analysis data.

---

## Reference Tools

| Tool | Type | Main Use Case |
| :--- | :--- | :--- |
| `glances` | Terminal dashboard | Real-time CPU/RAM/disk/network monitoring in a single view |
| `htop` | Process monitor | Interactive process management with filters and signals |
| `iostat` | Disk I/O monitor | Disk performance analysis during intensive scans |
| `iftop` | Network monitor | Real-time per-host network traffic |
| `Zabbix agent` | Monitoring agent | Integration with Zabbix server for centralized monitoring |
| `Prometheus + Grafana` | Monitoring stack | Advanced dashboards with alerting for more complex environments |

---

> **Note:** For VM lab environments with limited resources, `glances` is the optimal starting point: lightweight, informative, zero configuration. Nagios and Zabbix make sense in environments with multiple machines to monitor centrally.
