# 07 - Abilita aggiornamenti automatici

> - **Fase:** System Setup - Patch Management Automatico
> - **Priorita:** Media - complementare al passo 01 per la manutenzione a lungo termine
> - **Prerequisiti:** Sistema aggiornato (passo 01); accesso sudo
> - **Tempo stimato:** 3 minuti

---

## Comandi

```Bash
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

Per verificare la configurazione:

```Bash
cat /etc/apt/apt.conf.d/50unattended-upgrades
sudo unattended-upgrades --dry-run --debug   # Test senza installare
```

---

## Perche farlo?

La sicurezza e un processo continuo, ma gli esseri umani dimenticano di aggiornare. Le patch di sicurezza critiche vengono rilasciate in risposta a vulnerabilita attivamente sfruttate: ogni giorno di ritardo nell'applicazione e una finestra di esposizione.

## Cosa accade dopo?

Il sistema installera autonomamente le patch di sicurezza critiche in background, senza richiedere intervento manuale. Gli aggiornamenti vengono applicati secondo una schedule configurabile (di default, notturna).

## Cosa rischi se non lo fai?

Potresti rimanere esposto a una vulnerabilita critica (una CVE diventata pubblica e gia weaponizzata) per settimane o mesi, semplicemente perche hai dimenticato di lanciare `apt upgrade`. Molti breach aziendali documentati sono stati causati da sistemi non patchati contro vulnerabilita con patch disponibile da settimane.

---

> **Nota:** Su Kali Linux, `unattended-upgrades` aggiorna per default solo i repository di sicurezza. Gli aggiornamenti delle versioni dei tool (es. nuova versione di Metasploit) richiedono ancora un `apt upgrade` manuale. Verificare periodicamente i log in `/var/log/unattended-upgrades/`.
