> **English** | [Italiano](README.md)

# 20 - Setup Logwatch (System Monitoring Report)

> - **Phase:** System Setup - Log Aggregation & Security Reporting
> - **Priority:** Medium - transforms log fatigue into actionable intelligence
> - **Prerequisites:** Sudo access; MTA configured (postfix/sendmail) if email delivery is desired; logwatch installable from apt
> - **Estimated time:** 15-20 minutes

---

## Commands

Installation:

```Bash
sudo apt install logwatch
```

Configuration (recommended override file, do not modify the default):

```Bash
sudo mkdir -p /etc/logwatch/conf
sudo vim /etc/logwatch/conf/logwatch.conf
```

Recommended minimal configuration for local report:

```Bash
Output = stdout
Format = text
Detail = Med
Range = yesterday
Service = All
```

Manual report generation:

```Bash
sudo logwatch --detail high --output stdout --format text --range today
```

For automatic email delivery (requires postfix):

```Bash
sudo logwatch --detail high --mailto your@email.com --output mail
```

Adding to crontab for automatic daily report:

```Bash
sudo crontab -e
# Add:
0 7 * * * /usr/sbin/logwatch --output stdout --format text --detail med >> /var/log/logwatch-report.log
```

---

## Why do it?

Nobody has time to read 10,000 lines of raw logs every day. Logwatch automatically aggregates and summarizes the most relevant security events from various system logs (`auth.log`, `syslog`, `dpkg.log`, etc.) into a report readable in 5 minutes.

## What happens next?

Every day (or at the configured frequency) you receive a summary that includes: failed login attempts, SSH connections, package modifications, critical system errors, disk usage statistics. Anomalies from normal behavior emerge immediately.

## What's the risk if you don't?

"Log fatigue": you ignore logs because they are too many and incomprehensible in raw format, missing the single critical warning hidden in the noise (e.g., "5 SSH login attempts from external IP at 3:00 AM").

---

## Reference Tools

| Tool | Type | Use Case |
| :--- | :--- | :--- |
| `Logwatch` | Log aggregator | Daily summary report from `/var/log` |
| `GoAccess` | Web log analyzer | Real-time Apache/Nginx log analysis with dashboard |
| `fail2ban` | Automatic ban | Block IPs after N failed attempts (complementary to Logwatch) |
| `logcheck` | Log alert | Lightweight Logwatch alternative, sends only anomalous lines |
| `Splunk Free` | SIEM | Ingestion, indexing and advanced dashboards for high log volumes |

---

> **Note:** The configuration file shown in the original README is the system `default.conf` file - do not modify it directly. Use the override file in `/etc/logwatch/conf/logwatch.conf` for customizations, as indicated in the official documentation. This way package updates will not overwrite your custom configuration.
