> **English** | [Italiano](README.md)

# 12 - Schedule Regular Maintenance (Cron)

> - **Phase:** System Setup - Maintenance Automation
> - **Priority:** Medium - prevents disk issues and keeps the system updated over time
> - **Prerequisites:** User access with crontab; `cron` active (default in Kali)
> - **Estimated time:** 5 minutes

---

## Commands

Open crontab editor for the current user:

```Bash
crontab -e
```

Recommended maintenance tasks to add:

```Bash
# Automatic update every Monday at 02:00
0 2 * * 1 sudo apt update && sudo apt upgrade -y >> /var/log/auto-update.log 2>&1

# Clean apt cache every Sunday at 03:00
0 3 * * 0 sudo apt autoremove -y && sudo apt autoclean >> /var/log/auto-clean.log 2>&1

# Log rotation: compress old logs daily at 04:00
0 4 * * * find /var/log -name "*.log" -mtime +7 -exec gzip {} \;
```

Verify jobs were saved:

```Bash
crontab -l
```

---

## Why do it?

Log files grow indefinitely, the `apt` cache accumulates, obsolete packages take up space. Without periodic maintenance, an intensively used system (scans, analysis, labs) reaches disk saturation in weeks.

## What happens next?

The system performs "cleanup" operations automatically at preset times, at night or on weekends, without requiring manual intervention. The disk stays under control and the system always updated.

## What's the risk if you don't?

The disk gradually fills up until it blocks the system, often at the worst moment: during a long scan, a forensic analysis or an exploitation session that cannot be interrupted.

---

## Crontab Syntax (quick reference)

```
* * * * * command
| | | | |
| | | | +----- Day of week (0=Sun, 1=Mon, ..., 6=Sat)
| | | +------- Month (1-12)
| | +--------- Day of month (1-31)
| +----------- Hour (0-23)
+------------- Minute (0-59)
```

---

> **Note:** For tasks requiring `sudo`, add commands to root's crontab (`sudo crontab -e`) or configure the `/etc/sudoers` file to allow passwordless execution for specific commands. Always verify cron job logs in `/var/log/syslog` or in the log file specified in the `>>` redirect.
