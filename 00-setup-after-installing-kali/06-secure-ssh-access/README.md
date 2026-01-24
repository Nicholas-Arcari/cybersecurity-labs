# Metti in sicurezza l'accesso SSH

Comando: 

Modifica `/etc/ssh/sshd_config`:

```Bash
Port 2222               # Cambia la porta standard
PermitRootLogin no      # Vieta login diretto come root
```

Poi riavvia: `sudo systemctl restart ssh`

- Perché farlo?

La porta 22 è la più attaccata al mondo da bot automatici. L'account root è il bersaglio principale dei brute-force

- Cosa accade dopo?

Per connetterti dovrai specificare la porta (es. `ssh -p 2222 user@ip`). I bot automatici che scansionano la porta 22 non troveranno nulla

- Cosa rischi se non lo fai?

Il tuo file di log si riempirà di migliaia di tentativi di accesso falliti (rumore) e aumenti la probabilità che un attacco brute-force abbia successo