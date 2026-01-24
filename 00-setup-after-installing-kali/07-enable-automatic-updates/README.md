# Abilita aggiornamenti automatici

Comando:

```Bash
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

- Perché farlo?

La sicurezza è un processo continuo, ma gli umani dimenticano di aggiornare

- Cosa accade dopo?

Il sistema installerà autonomamente le patch di sicurezza critiche in background

- Cosa rischi se non lo fai?

Potresti rimanere esposto a una vulnerabilità critica ("Zero-day" diventata nota) per settimane, semplicemente perché hai dimenticato di lanciare `apt upgrade`