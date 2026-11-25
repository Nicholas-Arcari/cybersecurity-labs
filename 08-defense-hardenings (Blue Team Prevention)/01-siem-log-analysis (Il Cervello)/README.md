> [English](README.en.md) | **Italiano**

# 01 - SIEM & Log Analysis (Il Cervello)

> - **Fase:** Defense & Hardening - Detection & Correlation
> - **Categoria:** Detection - il centro nervoso della difesa
> - **Prerequisiti:** Host SIEM con risorse adeguate (RAM per ELK/Indexer); sorgenti di log configurate; agenti/forwarder sugli endpoint
> - **Output:** Finding DEF-001..002; piattaforma di detection centralizzata; capacita di correlazione e threat hunting

---

## Introduzione

Il SIEM (Security Information and Event Management) e "il cervello" della difesa: il punto in cui convergono tutti i log dell'ambiente e in cui gli eventi isolati diventano detection. La premessa teorica e semplice ma fondamentale: un singolo log non racconta un attacco. Un login fallito e rumore, un port scan e rumore di fondo di Internet, un processo nuovo e attivita normale. E la loro correlazione - nel tempo, tra sorgenti diverse - a rivelare la kill chain.

Un SIEM svolge quattro funzioni: **raccolta** (aggrega i log da endpoint, firewall, server), **normalizzazione** (uniforma formati eterogenei), **correlazione** (mette in relazione eventi di sorgenti diverse) e **alerting** (notifica quando un pattern corrisponde a una firma d'attacco). Senza SIEM, i log restano isolati sui singoli host - parziali, non correlabili e manomettibili dall'attaccante che compromette l'host.

La sezione confronta i due approcci di riferimento:

1. **ELK Stack (DEF-001):** l'alternativa open source (Elasticsearch, Logstash, Kibana). Gratuito e potentissimo, richiede di costruire manualmente pipeline e dashboard. La scelta formativa che insegna ogni pezzo della catena.

2. **Splunk (DEF-002):** il SIEM commerciale di riferimento. Molto pronto all'uso, con il linguaggio SPL espressivo per la correlazione, a fronte di un costo di licenza sul volume ingerito.

Il posizionamento nel percorso difensivo: il SIEM riceve gli alert dagli strumenti degli altri strati - Wazuh/XDR (`../02-endpoint-security-xdr/`), i honeypot (`../03-deception/`) - e li correla. E il cervello che da senso ai dati che i sensori producono.

---

## Struttura della cartella

```
01-siem-log-analysis (Il Cervello)/
+-- README.md          # questo file: registro DEF-001..002, concetto di SIEM
|
+-- elk-stack/         # DEF-001: SIEM open source (Elasticsearch, Logstash, Kibana)
+-- splunk/            # DEF-002: SIEM commerciale, correlazione SPL
```

---

## Flusso operativo consigliato

```
[INPUT] Log da endpoint, firewall, server, Wazuh, Suricata
         |
         v
[1] Scelta della piattaforma
     +-- open source / apprendimento / budget zero -> elk-stack/ (DEF-001)
     +-- enterprise / pronto all'uso / correlazione -> splunk/ (DEF-002)
              |
              v
[2] Ingestione
     +-- Beats / Universal Forwarder -> log centralizzati in tempo reale
              |
              v
[3] Detection e correlazione
     +-- regole/query -> brute force, port scan, kill chain correlate
              |
              v
[4] Alerting e risposta
     +-- alert -> notifica SOC / active response (Wazuh DEF-004)
              |
              v
[OUTPUT] Attacco rilevato -> contenimento + threat hunting retrospettivo
```

---

## Tool di riferimento

| Tool | Tipo | Ruolo | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `ELK Stack` | SIEM open source | Piattaforma | Detection e log analysis gratuita e flessibile |
| `Splunk` | SIEM commerciale | Piattaforma | Correlazione SPL e detection enterprise |
| `Filebeat`/`Winlogbeat` | Log shipper | Agent | Inoltro log da endpoint (ELK) |
| `Universal Forwarder` | Log shipper | Agent | Inoltro log da endpoint (Splunk) |
| `Sysmon` | Endpoint sensor | Agent (Win) | Telemetria di processo per detection avanzata |

> **Tool moderno consigliato:** per l'apprendimento e i budget contenuti, `ELK Stack` con il modulo Elastic Security (regole MITRE native). Per l'enterprise, `Splunk ES`. In entrambi i casi, `Sysmon` sugli endpoint Windows arricchisce enormemente la telemetria correlabile.

---

## Registro Finding - Sezione SIEM & Log Analysis

| ID | Descrizione | Severity | Sottocartella |
| :--- | :--- | :---: | :--- |
| `DEF-001` | ELK Stack: centralizzazione dei log e detection (brute force SSH) | `Alto` | `elk-stack/` |
| `DEF-002` | Splunk: correlazione multi-sorgente via SPL (kill chain scan -> accesso) | `Alto` | `splunk/` |

---

## Mappatura MITRE ATT&CK - Aggregata

> Tecniche d'attacco **rilevate** dai controlli della sezione.

| Tattica (rilevata) | Tecnica | ID MITRE | Finding Correlato |
| :--- | :--- | :--- | :--- |
| Credential Access | Brute Force | `T1110` | DEF-001, DEF-002 |
| Reconnaissance | Active Scanning | `T1595` | DEF-002 |
| Initial Access | Valid Accounts | `T1078` | DEF-001, DEF-002 |
| Lateral Movement | Remote Services | `T1021` | DEF-002 |
| Defense Evasion | Indicator Removal: Clear Logs | `T1070` | DEF-001 (l'inoltro in tempo reale vanifica la cancellazione) |

---

> **Nota:** Tutte le attivita documentate in questa sezione sono state condotte su un ambiente di laboratorio di proprieta dell'autore, con attacchi simulati sui sistemi di test. Il monitoraggio dei log in contesti reali deve rispettare la normativa su privacy e trattamento dei dati. Le tecniche sono documentate a scopo educativo e di difesa in contesto autorizzato.
