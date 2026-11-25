> [English](README.en.md) | **Italiano**

# ELK stack - il SIEM open source (elasticsearch, logstash, kibana)

> - **Fase:** Defense & Hardening - Detection & Log Analysis (SIEM)
> - **Categoria:** Detection - centralizzazione e correlazione dei log
> - **Prerequisiti:** Host con almeno 8 GB RAM (l'Indexer JVM e esoso); Docker/Docker Compose o pacchetti Elastic; sorgenti di log da inoltrare (endpoint, firewall, server)
> - **Output:** Finding DEF-001; piattaforma di logging centralizzata; capacita di detection e threat hunting su tutti i log dell'ambiente

- **Ambiente Operativo:** Kali/Debian (SIEM server), endpoint Linux/Windows con Beats/agent
- **Ruolo:** "Il Cervello" - aggrega e correla tutto cio che gli altri strumenti generano
- **Tool principali:** Elasticsearch, Logstash, Kibana, Filebeat/Winlogbeat

---

## Executive summary

L'ELK Stack (Elasticsearch, Logstash, Kibana) e l'alternativa open source ai SIEM commerciali come Splunk (`../splunk/`). E la spina dorsale della detection difensiva: dove i singoli strumenti vedono un frammento (Wazuh un file sospetto, Suricata un pacchetto anomalo), il SIEM aggrega tutto in un unico punto e permette di correlare eventi che, isolati, sembrerebbero innocui.

I tre componenti si dividono il lavoro: **Elasticsearch** e il motore di ricerca e storage distribuito che indicizza i log; **Logstash** e la pipeline di ingestione che riceve, normalizza e arricchisce i log prima di indicizzarli; **Kibana** e l'interfaccia di visualizzazione, ricerca e alerting. I log arrivano dagli endpoint tramite i **Beats** (Filebeat per i file di log, Winlogbeat per gli Event Log di Windows).

Il finding DEF-001 documenta la capacita di detection abilitata dalla centralizzazione: senza un SIEM, i log restano isolati sui singoli host, dove un attaccante puo cancellarli (vedere `07-post-exploitation/05-exfiltration-cleanup/log-cleaning/`). Con l'ELK Stack che inoltra i log in tempo reale, la visibilita difensiva diventa strutturale e resistente alla manomissione.

---

## Struttura della cartella

```
elk-stack/
+-- README.md      # questo file: deploy ELK + detection centralizzata (DEF-001)
+-- img/           # dashboard Kibana e regole di detection
```

---

## Detection centralizzata con ELK

**ID Finding:** `DEF-001` | **Severity:** `Alto` (la centralizzazione dei log e la capacita difensiva fondante: senza visibilita non c'e detection)

### Contesto operativo

Il valore del SIEM non e archiviare i log ma renderli interrogabili e correlabili in tempo reale. Il caso d'uso didattico piu chiaro e la detection di un brute force SSH: un singolo login fallito e rumore, ma decine di login falliti dallo stesso IP in pochi secondi sono un attacco. Solo un motore che aggrega i log di autenticazione di tutti gli host puo rilevare questo pattern.

### PoC - fase 1: deploy dello stack (Docker compose)

```Bash
# Stack ELK minimale in Docker (single-node per il lab)
docker compose -f elk-docker-compose.yml up -d

# Verifica che Elasticsearch risponda
curl -s http://localhost:9200/_cluster/health | jq .status
```

```
"green"                                    <-- cluster ELK operativo
```

### PoC - fase 2: ingestione dei log degli endpoint (filebeat)

```YAML
# /etc/filebeat/filebeat.yml (sull'endpoint da monitorare)
filebeat.inputs:
  - type: filestream
    paths:
      - /var/log/auth.log        # log di autenticazione SSH/sudo
output.logstash:
  hosts: ["SIEM_IP:5044"]        # inoltro alla pipeline Logstash
```

```Bash
# Avvio e verifica dell'inoltro
sudo systemctl enable --now filebeat
sudo filebeat test output
```

```
logstash: SIEM_IP:5044...
  connection...
    parse host... OK
    talk to server... OK          <-- log inoltrati al SIEM in tempo reale
```

### PoC - fase 3: regola di detection (brute force SSH)

```
# Query KQL in Kibana: login SSH falliti aggregati per IP sorgente
event.dataset : "system.auth" and system.auth.ssh.event : "Failed"

# Alerting rule (Kibana): soglia -> piu di 10 "Failed" dallo stesso
# source.ip in una finestra di 60 secondi -> genera un alert
```

```
[ALERT] SSH Brute Force Detected
  source.ip: 10.0.2.15
  count: 47 failed logins in 38s        <-- brute force rilevato (DEF-001)
  host.name: web-prod-01
```

### Tuning e operativita difensiva

- **Riduzione dei falsi positivi:** escludere gli IP di gestione noti e i job automatici; tarare le soglie sul comportamento reale dell'ambiente (un bastion host legittimo genera piu login di una workstation)
- **Resilienza:** il valore chiave del SIEM e che i log lasciano l'host in tempo reale, quindi un attaccante che compromette l'endpoint non puo cancellare i log gia inoltrati (contromisura strutturale al log tampering, `07-post-exploitation`)
- **Retention e integrita:** definire una policy di retention (ILM - Index Lifecycle Management) e proteggere l'accesso all'Indexer; lo storage dei log deve essere fuori dalla portata degli account monitorati
- **Escalation:** ogni regola di alert deve avere una procedura di risposta associata (chi viene notificato, quali passi di contenimento)

---

## Esperienza di laboratorio

Il primo ostacolo e stato prevedibile e coerente con quanto gia visto su Wazuh (`../../02-endpoint-security-xdr/wazuh/installing&configuring/`): la fame di RAM di Elasticsearch. Con l'heap JVM di default lo stack saturava la memoria della VM di laboratorio; limitare l'heap a 2 GB (`ES_JAVA_OPTS=-Xms2g -Xmx2g`) ha stabilizzato il tutto. E la stessa lezione dell'Indexer di Wazuh, che a ben vedere e OpenSearch, un fork di Elasticsearch: la parentela tecnologica e diretta.

La rivelazione operativa e stata vedere la correlazione in azione. Ho generato il brute force SSH da un secondo host e ho osservato i login falliti materializzarsi in Kibana in pochi secondi, aggregati per IP sorgente. Il singolo evento non dice nulla; la vista aggregata trasforma il rumore in segnale. Questo ha reso concreto perche il SIEM sia "il cervello": non aggiunge nuovi sensori, ma da senso ai dati che i sensori gia producono.

La scelta ELK vs Splunk (`../splunk/`) si e chiarita sul campo: ELK e gratuito e potentissimo, ma richiede di costruire manualmente pipeline, parsing e dashboard. Splunk offre molto pronto all'uso ma a costo di licenza. Per un home lab e per imparare i fondamentali, ELK e la scelta formativa migliore proprio perche costringe a capire ogni pezzo della catena.

---

## Analisi teorica: perche la centralizzazione e la precondizione della detection

La detection efficace richiede tre proprieta che solo un log centralizzato garantisce: **completezza** (tutti i log in un posto), **correlazione** (eventi di sorgenti diverse messi in relazione temporale) e **integrita** (i log fuori dalla portata dell'attaccante). Un log locale su un host compromesso non ha nessuna delle tre: e parziale, isolato e manomettibile.

La correlazione e il salto qualitativo. La kill chain di un attacco lascia tracce su sistemi diversi: un login sospetto sul firewall, un processo anomalo su un endpoint, una connessione in uscita insolita. Ognuna, isolata, e sotto la soglia dell'allarme; insieme, nella stessa finestra temporale, disegnano l'attacco. Il SIEM e il solo punto da cui questa correlazione e possibile, perche e il solo che vede tutto contemporaneamente.

Questo si collega direttamente al principio di anti-forensics visto in `07-post-exploitation`: l'attaccante maturo cancella i log locali per ostacolare l'analisi. Il SIEM neutralizza questa mossa spostando i log su un sistema che l'attaccante non controlla, nel momento stesso della loro generazione. La detection e l'integrita dei log sono quindi due facce della stessa medaglia: non si puo rilevare cio che non si vede, e non si puo fidarsi di cio che l'avversario puo riscrivere.

---

## Scenario reale: la detection in azione

> Questa sezione descrive come questo controllo difensivo opererebbe in un incidente reale, mostrando la prospettiva dell'attaccante e la risposta del difensore.

### Prospettiva attaccante (cosa tenta)

L'attaccante avvia un brute force SSH contro un server esposto, confidando che i tentativi falliti si perdano nei log locali e che nessuno li guardi. In un ambiente senza SIEM, questa scommessa e vincente: i log restano sull'host, invisibili finche qualcuno non li ispeziona manualmente.

### Prospettiva difensore (come il controllo risponde)

```
[DEF-001] Filebeat inoltra auth.log in tempo reale -> Logstash -> Elasticsearch
        |
        v
Regola Kibana: >10 login SSH falliti / stesso IP / 60s -> ALERT
        |
        v
SOC notificato in <1 minuto dall'inizio dell'attacco
        |
        v
Contenimento: blocco dell'IP sorgente (firewall / active response Wazuh)
        |
        v
Threat hunting: query retrospettiva su tutto l'ambiente per lo stesso IP
```

**Valore difensivo:** la centralizzazione trasforma un attacco silenzioso in un evento rilevato in tempo quasi reale. La query retrospettiva e il secondo valore: una volta identificato l'IP ostile, il SIEM permette di cercarlo su tutti i log storici di tutti gli host, rivelando l'intera estensione dell'attivita dell'attaccante - impossibile con log isolati.

**Indicatori monitorati (IOC):** picchi di autenticazioni fallite per IP, login riusciti dopo una serie di fallimenti (brute force riuscito), accessi da geolocalizzazioni o orari anomali, correlazione tra alert di Suricata/Wazuh e i log di rete.

**Lezione difensiva:** un SIEM non previene l'attacco, lo rende visibile. Ma la visibilita e la precondizione di ogni altra difesa: non si puo contenere, investigare o imparare da cio che non si e visto accadere.

---

## Tool di riferimento

| tool | tipo | ruolo | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Elasticsearch` | search/storage engine | backend | indicizzazione e ricerca full-text dei log |
| `Logstash` | ingestion pipeline | backend | parsing, normalizzazione e arricchimento dei log |
| `Kibana` | visualization/alerting | frontend | dashboard, query kql, regole di detection |
| `Filebeat` / `Winlogbeat` | log shipper | agent | inoltro dei log da endpoint linux/windows |
| `Elastic SIEM` (security) | detection app | modulo | regole di detection pronte + mapping mitre nativo |
| `ElastAlert2` | alerting engine | add-on | alerting avanzato su cluster elk self-hosted |

> **Tool moderno consigliato:** il modulo `Elastic Security` (ex SIEM app) integra regole di detection pronte all'uso con mapping MITRE ATT&CK nativo e riduce enormemente il lavoro di configurazione manuale. Per l'ingestione moderna, `Elastic Agent` unifica i vari Beats in un unico agente gestito centralmente. Confronto con l'alternativa commerciale in `../splunk/`.

---

## Mappatura MITRE ATT&CK

> In un modulo difensivo, la tabella mappa le tecniche d'attacco che il controllo **rileva**. Riferimento difensivo complementare: MITRE D3FEND (contromisure).

| tattica (rilevata) | tecnica | id mitre | ruolo del controllo |
| :--- | :--- | :--- | :--- |
| credential access | brute force: password guessing | `T1110.001` | detection via aggregazione dei login falliti per ip (DEF-001) |
| credential access | brute force: password spraying | `T1110.003` | detection di un ip che tenta molti account con poche password |
| initial access | valid accounts | `T1078` | detection di login riuscito dopo serie di fallimenti (brute force riuscito) |
| defense evasion | indicator removal: clear linux logs | `T1070.002` | l'inoltro in tempo reale rende inefficace la cancellazione dei log locali |

| contromisura difensiva (d3fend) | id d3fend | applicazione |
| :--- | :--- | :--- |
| platform monitoring | `D3-PM` | raccolta e monitoraggio centralizzato dei log di sistema |
| user behavior analysis | `D3-UBA` | analisi dei pattern di autenticazione per rilevare anomalie |

---

> **Nota:** Tutte le attivita documentate sono state condotte su un ambiente di laboratorio di proprieta dell'autore. La detection e stata validata contro traffico e attacchi simulati sui sistemi di test. Il monitoraggio dei log deve rispettare la normativa su privacy e trattamento dei dati (in contesti reali, log di autenticazione e di rete possono contenere dati personali). Le tecniche sono documentate a scopo educativo e di difesa in contesto autorizzato.
