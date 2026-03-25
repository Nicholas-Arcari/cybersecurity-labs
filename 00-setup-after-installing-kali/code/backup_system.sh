#!/bin/bash
# backup_system.sh - Backup incrementale del sistema con rsync
# Uso: chmod +x backup_system.sh && sudo ./backup_system.sh [DEST_PATH]
# Esempio: sudo ./backup_system.sh /media/usb/kali-backup

set -euo pipefail

BACKUP_DEST="${1:-/backup/system}"
DATE=$(date +%F_%H-%M)
BACKUP_PATH="$BACKUP_DEST/system-$DATE"
LOG_FILE="/var/log/backup_system.log"

log() { echo "[$(date '+%F %T')] $1" | tee -a "$LOG_FILE"; }

[[ $EUID -ne 0 ]] && { echo "[-] Eseguire come root"; exit 1; }

log "Avvio backup verso $BACKUP_PATH"
mkdir -p "$BACKUP_PATH"

rsync -av --delete \
    --exclude='/proc' \
    --exclude='/sys' \
    --exclude='/dev' \
    --exclude='/run' \
    --exclude='/tmp' \
    --exclude='/mnt' \
    --exclude='/media' \
    --exclude='/backup' \
    --exclude='/var/log/*.gz' \
    / "$BACKUP_PATH/" 2>&1 | tee -a "$LOG_FILE"

USED=$(du -sh "$BACKUP_PATH" | cut -f1)
log "Backup completato. Dimensione: $USED. Path: $BACKUP_PATH"

# Rimuove backup piu vecchi di 30 giorni
find "$BACKUP_DEST" -maxdepth 1 -name "system-*" -mtime +30 -exec rm -rf {} \; 2>/dev/null
log "Pulizia backup obsoleti (>30 giorni) completata"
