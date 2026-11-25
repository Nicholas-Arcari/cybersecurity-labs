> **English** | [Italiano](README.md)

# 19 - Backup your system

> - **Phase:** System Setup - Disaster Recovery & Business Continuity
> - **Priority:** High - losing a configured lab system means losing weeks of work
> - **Prerequisites:** Sufficient disk space for backup; `rsync` installed (default in Kali)
> - **Estimated time:** Setup 10 minutes; first backup 20-60 minutes (depends on system size)

---

## Commands

### Option 1: rsync (incremental backup)

Creating the system backup script:

```Bash
touch ~/scripts/backup_system.sh
chmod +x ~/scripts/backup_system.sh
```

Script contents:

```Bash
#!/bin/bash
BACKUP_DEST="/backup/system"
DATE=$(date +%F)
mkdir -p "$BACKUP_DEST"

rsync -av \
  --exclude='/proc' \
  --exclude='/sys' \
  --exclude='/dev' \
  --exclude='/run' \
  --exclude='/tmp' \
  --exclude='/mnt' \
  --exclude='/backup' \
  / "$BACKUP_DEST/system-$DATE/"

echo "[$(date)] System backup completed to $BACKUP_DEST/system-$DATE/"
```

### Option 2: timeshift (graphical snapshot)

```Bash
sudo apt install timeshift
sudo timeshift --create --comments "post-setup backup"
sudo timeshift --list    # List available snapshots
```

### Option 3: VM snapshot (recommended for virtualized environments)

For VirtualBox: `Machine > Tools > Snapshots > Take` before every risky session.

---

## Why do it?

Updates can break the system, an erroneous command can delete important configuration files, a failed exploit during testing can destabilize the environment. Without backup, the only option is to reinstall and reconfigure everything from scratch.

## What happens next?

You can restore the system state to a previous point in case of disaster. With Timeshift, restoration takes only minutes. With VM snapshots, you return to the previous state in seconds.

## What's the risk if you don't?

Having to format and reinstall everything from scratch, losing days of configuration, custom tools, notes and lab data. In a professional context, losing the work system during an engagement is unacceptable.

---

## Recommended backup strategy (3-2-1)

| copy | where | tool |
| :--- | :--- | :--- |
| copy 1 | internal disk (separate partition) | timeshift / rsync |
| copy 2 | external usb disk | manual rsync |
| copy 3 | encrypted cloud or remote nas | rsync + luks or restic |

---

> **Note:** In virtualized environments (VirtualBox, VMware), VM snapshots are the fastest and most efficient method for pre-operative backup. Take a snapshot before every aggressive testing session (exploitation, privilege escalation) to be able to restore the environment in seconds in case of crash.
