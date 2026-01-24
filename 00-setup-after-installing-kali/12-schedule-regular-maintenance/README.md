# Pianifica manutenzione regolare

Comando: 

```Bash
crontab -e
```

Aggiungi script di pulizia o update sotto la riga `# 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/`:

```Bash
0 2 * * * apt update && apt upgrade -y
```

- Perché farlo?

I file di log crescono all'infinito, la cache si riempie

- Cosa accade dopo?

Il sistema esegue "le pulizie di casa" automaticamente a orari prestabiliti

- Cosa rischi se non lo fai?

Il disco si riempie gradualmente fino a bloccare il sistema, spesso nel momento peggiore