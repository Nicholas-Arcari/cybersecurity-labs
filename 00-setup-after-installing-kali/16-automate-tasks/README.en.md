> **English** | [Italiano](README.md)

# 16 - Automate Log Backup

> - **Phase:** System Setup - Log Management & Forensic Readiness
> - **Priority:** High - logs are unrepeatable forensic evidence
> - **Prerequisites:** Backup destination directory created; sudo access to reach `/var/log`
> - **Estimated time:** 10 minutes

---

## Commands

Creating the log backup script:

```Bash
touch ~/scripts/backup_logs.sh
chmod +x ~/scripts/backup_logs.sh
```

Script contents:

```Bash
#!/bin/bash
BACKUP_DIR="/backup/logs"
DATE=$(date +%F)
mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/logs-$DATE.tar.gz" /var/log
echo "[$(date)] Logs backed up to $BACKUP_DIR/logs-$DATE.tar.gz"
```

Adding to crontab for automatic nightly execution:

```Bash
crontab -e
# Add the line:
0 1 * * * /home/[user]/scripts/backup_logs.sh >> /var/log/backup.log 2>&1
```

Manual execution for testing:

```Bash
~/scripts/backup_logs.sh
ls -lh /backup/logs/
```

---

## Why do it?

Logs are forensic evidence. In case of intrusion, a competent attacker's first action is to delete or alter logs to cover their tracks (`rm /var/log/auth.log`, `history -c`). Having periodic log copies in a separate directory - ideally on an encrypted volume or remote system - preserves evidence for post-incident analysis.

## What happens next?

You will have historical copies of logs (auth.log, syslog, suricata, dpkg) saved with timestamps. In case of an incident, you can compare current logs with copies to identify changes made by the attacker and reconstruct the intrusion timeline.

## What's the risk if you don't?

In case of intrusion, you will have no way to reconstruct what happened. Incident Response becomes impossible: you cannot identify the access vector, commands executed, data exfiltrated or the duration of the compromise.

---

> **Note:** For maximum security, send log backups to a remote server (e.g., via `rsync` or `scp`) immediately after creation, so that an attacker with local access cannot delete them. Alternatively, configure a log shipper like `rsyslog` or `Filebeat` to send logs in real time to a SIEM or centralized syslog server.
