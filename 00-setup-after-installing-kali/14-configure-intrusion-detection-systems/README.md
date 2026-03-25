# 14 - Configura un IDS (Suricata)

> - **Fase:** System Setup - Network Intrusion Detection
> - **Priorita:** Alta per ambienti esposti; Media per VM isolate
> - **Prerequisiti:** Accesso sudo; interfaccia di rete identificata (`ip a`)
> - **Tempo stimato:** 20-30 minuti (installazione + configurazione regole base)

---

## Comandi

```Bash
# Installazione
sudo apt install -y suricata

# Aggiornamento regole Emerging Threats (database firme attacchi)
sudo suricata-update

# Configurazione interfaccia di ascolto (sostituire eth0 con la propria interfaccia)
sudo vim /etc/suricata/suricata.yaml
# Cercare la riga "af-packet:" e impostare l'interfaccia corretta

# Avvio e abilitazione al boot
sudo systemctl enable --now suricata

# Verifica stato
sudo systemctl status suricata
sudo tail -f /var/log/suricata/fast.log   # Log alert in tempo reale
```

---

## Perche farlo?

Kali Linux Purple e una distribuzione progettata anche per il Blue Team e il Threat Hunting. Un IDS (Intrusion Detection System) e la "telecamera di sorveglianza" della rete: analizza ogni pacchetto in transito e genera un allarme quando rileva firme di attacco note (port scan, exploit, C2 beaconing, esfiltrazione dati).

## Cosa accade dopo?

Suricata analizzera il traffico di rete in tempo reale. Quando qualcuno eseguira Nmap contro la macchina, quando un malware tentera una connessione C2, o quando un exploit passera per la rete, Suricata genera un alert in `/var/log/suricata/fast.log` e in formato JSON strutturato in `eve.json`.

## Cosa rischi se non lo fai?

Non saprai mai se qualcuno sta scansionando o attaccando il sistema finche non sara troppo tardi. In un ambiente di laboratorio, non avere visibilita sul traffico in entrata significa non poter correlare gli alert con le attivita di exploitation in corso.

---

## Tool di riferimento

| Tool | Tipo | Caso d'uso |
| :--- | :--- | :--- |
| `Suricata` | IDS/IPS | Network packet inspection con regole Emerging Threats |
| `Snort` | IDS alternativo | IDS classico, stessa architettura regole di Suricata |
| `Zeek` (Bro) | Network monitor | Analisi comportamentale del traffico, logging strutturato |
| `suricata-update` | Rule manager | Aggiornamento automatico regole ET Open e altre sorgenti |
| `evebox` | Log viewer | GUI web per visualizzare gli alert `eve.json` di Suricata |

---

> **Nota:** Per integrare Suricata con un SIEM, configurare l'output `eve.json` e inviarlo a Elasticsearch (stack ELK) o Splunk. In ambienti di laboratorio, `tail -f /var/log/suricata/fast.log` e sufficiente per il monitoraggio in tempo reale durante le sessioni di testing.
