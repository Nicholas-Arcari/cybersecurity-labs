# 12 - Pianifica manutenzione regolare (Cron)

> - **Fase:** System Setup - Automazione Manutenzione
> - **Priorita:** Media - previene problemi di disco e mantiene il sistema aggiornato nel tempo
> - **Prerequisiti:** Accesso utente con crontab; `cron` attivo (default in Kali)
> - **Tempo stimato:** 5 minuti

---

## Comandi

Apertura editor crontab per l'utente corrente:

```Bash
crontab -e
```

Task di manutenzione consigliati da aggiungere:

```Bash
# Aggiornamento automatico ogni lunedi alle 02:00
0 2 * * 1 sudo apt update && sudo apt upgrade -y >> /var/log/auto-update.log 2>&1

# Pulizia cache apt ogni domenica alle 03:00
0 3 * * 0 sudo apt autoremove -y && sudo apt autoclean >> /var/log/auto-clean.log 2>&1

# Rotazione log: compressione log vecchi ogni giorno alle 04:00
0 4 * * * find /var/log -name "*.log" -mtime +7 -exec gzip {} \;
```

Verifica che i job siano stati salvati:

```Bash
crontab -l
```

---

## Perche farlo?

I file di log crescono all'infinito, la cache `apt` si accumula, i pacchetti obsoleti occupano spazio. Senza manutenzione periodica, un sistema usato intensivamente (scansioni, analisi, lab) raggiunge la saturazione del disco in settimane.

## Cosa accade dopo?

Il sistema esegue le operazioni di "pulizia" automaticamente agli orari prestabiliti, di notte o nei weekend, senza richiedere intervento manuale. Il disco rimane sotto controllo e il sistema sempre aggiornato.

## Cosa rischi se non lo fai?

Il disco si riempie gradualmente fino a bloccare il sistema, spesso nel momento peggiore: durante una scansione lunga, un'analisi forense o una sessione di exploitation che non puo essere interrotta.

---

## Sintassi crontab (riferimento rapido)

```
* * * * * comando
| | | | |
| | | | +----- Giorno della settimana (0=Dom, 1=Lun, ..., 6=Sab)
| | | +------- Mese (1-12)
| | +--------- Giorno del mese (1-31)
| +----------- Ora (0-23)
+------------- Minuto (0-59)
```

---

> **Nota:** Per task che richiedono `sudo`, aggiungere i comandi al crontab di root (`sudo crontab -e`) oppure configurare il file `/etc/sudoers` per permettere l'esecuzione senza password per comandi specifici. Verificare sempre i log dei cron job in `/var/log/syslog` o nel file di log specificato nel redirect `>>`.
