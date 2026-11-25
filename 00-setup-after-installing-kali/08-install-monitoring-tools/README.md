> [English](README.en.md) | **Italiano**

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

| tool | tipo | caso d'uso principale |
| :--- | :--- | :--- |
| `glances` | dashboard terminale | monitoraggio real-time cpu/ram/disco/rete in singola vista |
| `htop` | process monitor | gestione interattiva dei processi con filtri e segnali |
| `iostat` | disk i/o monitor | analisi delle performance disco durante scansioni intensive |
| `iftop` | network monitor | traffico di rete per host in tempo reale |
| `Zabbix agent` | agent monitoraggio | integrazione con server zabbix per monitoraggio centralizzato |
| `Prometheus + Grafana` | stack monitoraggio | dashboard avanzate con alerting per ambienti piu complessi |

---

> **Nota:** Per ambienti di laboratorio su VM con risorse limitate, `glances` e il punto di partenza ottimale: leggero, informativo, zero configurazione. Nagios e Zabbix hanno senso in ambienti con piu macchine da monitorare centralmente.
