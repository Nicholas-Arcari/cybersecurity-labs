Automatizza il Backup dei Log

Comando: Script Bash che fa `tar -czf` di `/var/log`.

```Bash
touch backup_logs.sh
sudo nano backup_logs.sh
```

Aggiungere al file le seguenti linee:

```Bash
#!/bin/bash
tar -czf /backup/logs-$(date +%F).tar.gz /var/log
echo "Logs backed up succesfully"
```

Dopo aver salvato il file bisogna renderlo eseguibile con il seguente comando:

```Bash
chmod +x backup_logs.sh
```

- Perché farlo?

I log sono prove forensi. Se un attaccante entra, la prima cosa che fa è cancellarli

- Cosa accade dopo?

Hai copie storiche dei log salvate altrove, utili per indagini post-incidente

- Cosa rischi se non lo fai?

In caso di intrusione, non avrai modo di ricostruire cosa è successo ("Incident Response" impossibile)