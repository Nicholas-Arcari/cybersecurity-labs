# Esegui backup del sistema

Comando: Script con `rsync` o tool come `Timeshift`.

```Bash
touch backup_system.sh
sudo nano backup_system.sh
```

Aggiungere al file le seguenti linee:

```Bash
#!/bin/bash
rsync -av --exclude='/proc' --exclude='/sys' /backup/
echo "Backup completed succesfully"
```

Dopo aver salvato il file bisogna renderlo eseguibile con il seguente comando:

```Bash
chmod +x backup_system.sh
```

- Perché farlo?

Gli aggiornamenti possono rompere il sistema, o potresti cancellare file per errore

- Cosa accade dopo?

Puoi ripristinare lo stato del sistema a un punto precedente in caso di disastro

- Cosa rischi se non lo fai?

Dover formattare e reinstallare tutto da zero, perdendo giorni di configurazione e dati