# 08 - Installa strumenti di monitoraggio

> - **Fase:** System Setup - System Health Monitoring
> - **Priorita:** Media - essenziale per sessioni di lavoro intensive (scansioni lunghe, analisi forense)
> - **Prerequisiti:** Sistema aggiornato; accesso sudo
> - **Tempo stimato:** 10-30 minuti (dipende dal tool scelto)

---

## Comandi

Per un monitoraggio leggero (raccomandato per ambienti VM):

```Bash
sudo apt install -y glances   # Dashboard terminale all-in-one (CPU, RAM, rete, disco, processi)
glances                        # Avvio interattivo
```

Per un agente Zabbix (monitoraggio centralizzato):

```Bash
sudo apt install zabbix-agent
sudo systemctl enable --now zabbix-agent
```

Per Nagios (monitoraggio servizi completo):

```Bash
sudo apt install nagios3
```

---

## Perche farlo?

In un ambiente difensivo (Blue Team), devi sapere se i tuoi sensori e servizi sono attivi e responsivi. Durante scansioni intensive (OpenVAS, Nmap massivo) o analisi forense (Volatility su dump di memoria), le risorse del sistema possono saturarsi senza preavviso.

## Cosa accade dopo?

Avrai visibilita in tempo reale sull'utilizzo di CPU, RAM, disco e rete. E possibile impostare soglie di allerta per ricevere notifiche quando le risorse si avvicinano alla saturazione.

## Cosa rischi se non lo fai?

Il sistema potrebbe bloccarsi per disco pieno o out-of-memory durante un'analisi critica senza darti alcun preavviso, causando la perdita del lavoro in corso e potenzialmente corrompendo i dati di analisi.

---

## Tool di riferimento

| Tool | Tipo | Caso d'uso principale |
| :--- | :--- | :--- |
| `glances` | Dashboard terminale | Monitoraggio real-time CPU/RAM/disco/rete in singola vista |
| `htop` | Process monitor | Gestione interattiva dei processi con filtri e segnali |
| `iostat` | Disk I/O monitor | Analisi delle performance disco durante scansioni intensive |
| `iftop` | Network monitor | Traffico di rete per host in tempo reale |
| `Zabbix agent` | Agent monitoraggio | Integrazione con server Zabbix per monitoraggio centralizzato |
| `Prometheus + Grafana` | Stack monitoraggio | Dashboard avanzate con alerting per ambienti piu complessi |

---

> **Nota:** Per ambienti di laboratorio su VM con risorse limitate, `glances` e il punto di partenza ottimale: leggero, informativo, zero configurazione. Nagios e Zabbix hanno senso in ambienti con piu macchine da monitorare centralmente.
