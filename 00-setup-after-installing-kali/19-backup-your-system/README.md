# 19 - Esegui backup del sistema

> - **Fase:** System Setup - Disaster Recovery & Business Continuity
> - **Priorita:** Alta - la perdita del sistema di laboratorio configura significa perdita di settimane di lavoro
> - **Prerequisiti:** Spazio disco sufficiente per il backup; `rsync` installato (default in Kali)
> - **Tempo stimato:** Setup 10 minuti; primo backup 20-60 minuti (dipende dalla dimensione del sistema)

---

## Comandi

### Opzione 1: rsync (backup incrementale)

Creazione dello script di backup sistema:

```Bash
touch ~/scripts/backup_system.sh
chmod +x ~/scripts/backup_system.sh
```

Contenuto dello script:

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

### Opzione 2: Timeshift (snapshot grafico)

```Bash
sudo apt install timeshift
sudo timeshift --create --comments "post-setup backup"
sudo timeshift --list    # Lista snapshot disponibili
```

### Opzione 3: Snapshot VM (raccomandato per ambienti virtualizzati)

Per VirtualBox: `Machine > Tools > Snapshots > Take` prima di ogni sessione rischiosa.

---

## Perche farlo?

Gli aggiornamenti possono rompere il sistema, un comando errato puo cancellare file di configurazione importanti, un exploit andato male durante i test puo destabilizzare l'ambiente. Senza backup, l'unica opzione e reinstallare e riconfigurare tutto da zero.

## Cosa accade dopo?

Puoi ripristinare lo stato del sistema a un punto precedente in caso di disastro. Con Timeshift, il ripristino richiede pochi minuti. Con gli snapshot VM, si torna allo stato precedente in secondi.

## Cosa rischi se non lo fai?

Dover formattare e reinstallare tutto da zero, perdendo giorni di configurazione, tool personalizzati, note e dati di laboratorio. In un contesto professionale, la perdita del sistema di lavoro durante un engagement e inaccettabile.

---

## Strategia di backup consigliata (3-2-1)

| Copia | Dove | Strumento |
| :--- | :--- | :--- |
| Copia 1 | Disco interno (partizione separata) | Timeshift / rsync |
| Copia 2 | Disco esterno USB | rsync manuale |
| Copia 3 | Cloud cifrato o NAS remoto | rsync + LUKS o Restic |

---

> **Nota:** In ambienti virtualizzati (VirtualBox, VMware), gli snapshot della VM sono il metodo piu rapido ed efficiente per il backup pre-operativo. Eseguire uno snapshot prima di ogni sessione di testing aggressivo (exploitation, privilege escalation) per poter ripristinare l'ambiente in secondi in caso di crash.
