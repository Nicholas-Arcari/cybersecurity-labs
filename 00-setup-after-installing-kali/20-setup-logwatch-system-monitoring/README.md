# 20 - Imposta Logwatch (System Monitoring Report)

> - **Fase:** System Setup - Log Aggregation & Security Reporting
> - **Priorita:** Media - trasforma il log fatigue in intelligence azionabile
> - **Prerequisiti:** Accesso sudo; MTA configurato (postfix/sendmail) se si vuole invio email; logwatch installabile da apt
> - **Tempo stimato:** 15-20 minuti

---

## Comandi

Installazione:

```Bash
sudo apt install logwatch
```

Configurazione (file di override consigliato, non modificare il default):

```Bash
sudo mkdir -p /etc/logwatch/conf
sudo vim /etc/logwatch/conf/logwatch.conf
```

Configurazione minima consigliata per report locale:

```Bash
Output = stdout
Format = text
Detail = Med
Range = yesterday
Service = All
```

Generazione manuale del report:

```Bash
sudo logwatch --detail high --output stdout --format text --range today
```

Per invio automatico via email (richiede postfix):

```Bash
sudo logwatch --detail high --mailto tuo@email.com --output mail
```

Aggiunta al crontab per report giornaliero automatico:

```Bash
sudo crontab -e
# Aggiungere:
0 7 * * * /usr/sbin/logwatch --output stdout --format text --detail med >> /var/log/logwatch-report.log
```

---

## Perche farlo?

Nessuno ha tempo di leggere 10.000 righe di log grezzi ogni giorno. Logwatch aggrega e riassume automaticamente gli eventi di sicurezza piu rilevanti dai vari log di sistema (`auth.log`, `syslog`, `dpkg.log`, ecc.) in un report leggibile in 5 minuti.

## Cosa accade dopo?

Ogni giorno (o alla frequenza configurata) ricevi un sommario che include: tentativi di login falliti, connessioni SSH, modifiche ai pacchetti, errori critici del sistema, statistiche di utilizzo disco. Le anomalie rispetto al comportamento normale emergono immediatamente.

## Cosa rischi se non lo fai?

"Log fatigue": ignori i log perche sono troppi e incomprensibili nel formato grezzo, perdendoti l'unico avviso critico nascosto nel rumore (es. "5 tentativi di login SSH da IP esterno alle 3:00 di notte").

---

## Tool di riferimento

| Tool | Tipo | Caso d'uso |
| :--- | :--- | :--- |
| `Logwatch` | Log aggregator | Report giornaliero riassuntivo da `/var/log` |
| `GoAccess` | Web log analyzer | Analisi in tempo reale log Apache/Nginx con dashboard |
| `fail2ban` | Ban automatico | Blocca IP dopo N tentativi falliti (complementare a Logwatch) |
| `logcheck` | Alert log | Alternativa leggera a Logwatch, invia solo le righe anomale |
| `Splunk Free` | SIEM | Ingestione, indexing e dashboard avanzate per volumi di log elevati |

---

> **Nota:** Il file di configurazione mostrato nel README originale e il file `default.conf` di sistema - non modificarlo direttamente. Usare il file di override in `/etc/logwatch/conf/logwatch.conf` per le personalizzazioni, come indicato nella documentazione ufficiale. In questo modo gli aggiornamenti del pacchetto non sovrascrivono la configurazione personalizzata.
