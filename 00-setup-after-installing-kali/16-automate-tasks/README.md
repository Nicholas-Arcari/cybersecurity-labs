# 16 - Automatizza il Backup dei Log

> - **Fase:** System Setup - Log Management & Forensic Readiness
> - **Priorita:** Alta - i log sono prove forensi irripetibili
> - **Prerequisiti:** Directory di destinazione backup creata; accesso sudo per accedere a `/var/log`
> - **Tempo stimato:** 10 minuti

---

## Comandi

Creazione dello script di backup log:

```Bash
touch ~/scripts/backup_logs.sh
chmod +x ~/scripts/backup_logs.sh
```

Contenuto dello script:

```Bash
#!/bin/bash
BACKUP_DIR="/backup/logs"
DATE=$(date +%F)
mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/logs-$DATE.tar.gz" /var/log
echo "[$(date)] Logs backed up to $BACKUP_DIR/logs-$DATE.tar.gz"
```

Aggiunta al crontab per esecuzione automatica notturna:

```Bash
crontab -e
# Aggiungere la riga:
0 1 * * * /home/[utente]/scripts/backup_logs.sh >> /var/log/backup.log 2>&1
```

Esecuzione manuale per test:

```Bash
~/scripts/backup_logs.sh
ls -lh /backup/logs/
```

---

## Perche farlo?

I log sono prove forensi. In caso di intrusione, la prima azione di un attaccante competente e cancellare o alterare i log per coprire le proprie tracce (`rm /var/log/auth.log`, `history -c`). Avere copie periodiche dei log su una directory separata - idealmente su un volume cifrato o un sistema remoto - preserva le evidenze per l'analisi post-incidente.

## Cosa accade dopo?

Avrai copie storiche dei log (auth.log, syslog, suricata, dpkg) salvate con timestamp. In caso di incidente, potrai confrontare i log attuali con le copie per identificare le modifiche operate dall'attaccante e ricostruire la timeline dell'intrusione.

## Cosa rischi se non lo fai?

In caso di intrusione, non avrai modo di ricostruire cosa e successo. L'Incident Response diventa impossibile: non puoi identificare il vettore di accesso, i comandi eseguiti, i dati esfiltrati o la durata della compromissione.

---

> **Nota:** Per massima sicurezza, inviare i backup dei log a un server remoto (es. via `rsync` o `scp`) immediatamente dopo la creazione, in modo che un attaccante con accesso locale non possa cancellarli. In alternativa, configurare un log shipper come `rsyslog` o `Filebeat` per inviare i log in tempo reale a un SIEM o un server syslog centralizzato.
