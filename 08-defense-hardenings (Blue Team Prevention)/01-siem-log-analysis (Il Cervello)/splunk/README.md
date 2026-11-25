> [English](README.en.md) | **Italiano**

# Splunk - Correlazione e Threat Hunting con SPL

> - **Fase:** Defense & Hardening - Detection & Correlation (SIEM commerciale)
> - **Categoria:** Detection - correlazione multi-sorgente e threat hunting
> - **Prerequisiti:** Splunk Enterprise (licenza trial 60 giorni) o Splunk Free (500 MB/giorno); Universal Forwarder sugli endpoint; sorgenti di log configurate
> - **Output:** Finding DEF-002; capacita di correlazione multi-sorgente; query SPL riutilizzabili per la detection di attacchi comuni

- **Ambiente Operativo:** Splunk server (VM dedicata), endpoint con Universal Forwarder
- **Ruolo:** Il correlatore - unisce eventi di firewall, server e endpoint in una singola narrazione
- **Tool principali:** Splunk Enterprise, Universal Forwarder, SPL (Search Processing Language)

---

## Executive Summary

Splunk e il SIEM commerciale di riferimento del settore. Rispetto all'ELK Stack (`../elk-stack/`) offre molto pronto all'uso - parsing automatico, app pre-costruite, un linguaggio di ricerca (SPL) estremamente espressivo - a fronte di un costo di licenza basato sul volume di dati ingeriti al giorno.

Il valore distintivo di Splunk, come da nota strategica di questo laboratorio, e la **correlazione**. La differenza tra i tre strumenti difensivi del percorso e netta:

- **Wazuh (`../../02-endpoint-security-xdr/wazuh/`)** dice: "C'e un file sospetto su questo PC" (visione endpoint).
- **Splunk** dice: "Ho visto una connessione strana dal firewall + un login fallito sul server + un alert di Wazuh, tutti nello stesso minuto" (correlazione).
- **Wireshark (`../../../09-digital-forensics (Blue Team Analysis)/`)** si apre dopo, per guardare dentro i singoli pacchetti e capire cosa contenevano (analisi di dettaglio).

Il finding DEF-002 documenta la capacita di correlazione: costruire query SPL che uniscono sorgenti diverse per rilevare pattern d'attacco (brute force, port scanning, movimento laterale) che nessuna singola sorgente rivelerebbe da sola.

---

## Struttura della cartella

```
splunk/
+-- README.md            # questo file: correlazione e threat hunting SPL (DEF-002)
+-- SPL-Queries/         # libreria di query SPL per detection (brute force, port scan, ...)
+-- Data-Ingestion/      # configurazione degli Universal Forwarder
+-- Dashboards/          # export XML/JSON delle dashboard difensive
+-- img/                 # screenshot delle detection
```

---

## Detection tramite Correlazione SPL

**ID Finding:** `DEF-002` | **Severity:** `Alto` (la correlazione multi-sorgente rileva attacchi invisibili alle singole sorgenti isolate)

### Contesto operativo

Il Search Processing Language (SPL) e il linguaggio proprietario di Splunk: una pipeline di comandi (in stile Unix, concatenati con `|`) che filtra, aggrega e correla gli eventi. Costruire una libreria di query SPL per gli attacchi comuni e il lavoro difensivo centrale: ogni query codifica la "firma comportamentale" di un attacco.

### PoC - Ingestione dei log (Universal Forwarder)

```Bash
# Sull'endpoint: l'Universal Forwarder inoltra i log a Splunk
# /opt/splunkforwarder/etc/system/local/outputs.conf
[tcpout:default]
server = SPLUNK_IP:9997

# Definizione di cosa inoltrare (inputs.conf)
[monitor:///var/log/auth.log]
sourcetype = linux_secure
```

```Bash
# Verifica dell'inoltro dal server Splunk
/opt/splunk/bin/splunk list forward-server
```

```
Active forwards:
    10.0.2.30:9997                        <-- endpoint che inoltra i log
```

### PoC - Query SPL: detection brute force

```
index=* sourcetype=linux_secure "Failed password"
| stats count by src_ip, user
| where count > 10
| sort - count
```

```
src_ip        user     count
10.0.2.15     root     47        <-- brute force su root (DEF-002)
10.0.2.15     admin    31
```

### PoC - Query SPL: detection port scanning

```
index=* sourcetype=firewall action=blocked
| stats dc(dest_port) as porte_distinte by src_ip
| where porte_distinte > 50
```

```
src_ip        porte_distinte
10.0.2.15     1024              <-- un solo IP verso 1024 porte = port scan
```

### PoC - Query SPL: correlazione multi-sorgente (il vero valore)

```
# Correla: scan di rete (firewall) SEGUITO da login riuscito (server)
# dallo stesso IP entro 5 minuti -> attacco riuscito, non solo tentativo
index=* (sourcetype=firewall action=blocked) OR (sourcetype=linux_secure "Accepted password")
| transaction src_ip maxspan=5m
| search action=blocked AND "Accepted password"
```

```
src_ip        eventi
10.0.2.15     scan(1024 porte) -> login riuscito user=svc_web   <-- kill chain correlata (DEF-002)
```

Questa e la correlazione che nessuna sorgente singola puo fornire: il firewall vede lo scan, il server vede il login, ma solo Splunk vede che sono lo stesso attaccante e che il secondo evento e la conseguenza del primo.

### Tuning e Operativita Difensiva

- **Salvare le query come Saved Searches:** ogni query di detection va salvata come alert schedulato con soglia e azione (notifica, ticket, active response)
- **Riduzione falsi positivi:** whitelist degli scanner di vulnerabilita autorizzati e dei bastion host; tarare le soglie sull'ambiente
- **Accelerazione:** per dataset grandi, usare i Data Model e le tstats per query performanti; le dashboard devono interrogare summary index, non raw data
- **Licenza:** Splunk fattura sul volume ingerito/giorno; filtrare a monte (nell'inputs.conf) cio che non serve alla detection riduce costi e rumore

---

## Esperienza di Laboratorio

La curva di apprendimento di Splunk e stata inversa rispetto a ELK: dove ELK richiede di costruire tutto ma insegna ogni pezzo, Splunk parte subito produttivo ma nasconde la complessita. In pochi minuti, con l'Universal Forwarder configurato, i log erano ricercabili; scrivere la prima query brute force in SPL e stato immediato e intuitivo (`stats count by src_ip | where count > 10`). Questa immediatezza spiega perche Splunk domina il mercato enterprise nonostante il costo.

Il momento formativo e stato capire il comando `transaction`. Le query di conteggio (brute force, port scan) le padroneggiavo gia concettualmente da ELK; la correlazione temporale tra sorgenti diverse - raggruppare eventi eterogenei per `src_ip` entro una finestra e verificare una sequenza - e stata la vera novita. Vedere lo scan e il login riuscito uniti in un'unica "transaction" ha reso tangibile la differenza tra un SIEM che aggrega e un SIEM che correla.

La nota strategica del laboratorio si e chiarita usando gli strumenti fianco a fianco: Splunk mi diceva CHE qualcosa era successo e COME gli eventi si collegavano, ma per capire ESATTAMENTE cosa conteneva il traffico dovevo aprire il pcap in Wireshark (modulo 09). I tre strumenti non competono, si completano lungo la catena rilevamento, correlazione, analisi di dettaglio.

---

## Analisi Teorica: La Correlazione come Ricostruzione della Kill Chain

Un attacco non e un evento singolo ma una sequenza: ricognizione, accesso iniziale, escalation, movimento laterale, azione sull'obiettivo. Ogni fase genera eventi su sistemi diversi e, presa isolatamente, ogni evento e sotto la soglia dell'allarme - un port scan e "rumore di Internet", un login riuscito e "attivita normale". La correlazione ricostruisce la sequenza, e la sequenza e l'attacco.

Splunk formalizza questo con `transaction` e con i Data Model: raggruppa eventi eterogenei attorno a un'entita comune (un IP, un utente, una sessione) e li ordina nel tempo. E l'operazione inversa a quella dell'attaccante, che distribuisce la propria attivita su sistemi e tempi diversi proprio per restare sotto le soglie. Il difensore che correla annulla questa dispersione, ricomponendo i frammenti in una narrazione.

Questo definisce il posto di Splunk nell'architettura difensiva: non e un sensore (non genera dati propri) ma un cervello analitico che ragiona sui dati dei sensori. Il suo limite e speculare al suo valore: correla solo cio che riceve. Sorgenti mancanti sono punti ciechi nella correlazione, motivo per cui la completezza dell'ingestione (Data-Ingestion) e importante quanto la sofisticazione delle query.

---

## Scenario Reale: La Detection in Azione

> Questa sezione descrive come questo controllo difensivo opererebbe in un incidente reale.

### Prospettiva Attaccante (cosa tenta)

L'attaccante distribuisce deliberatamente la propria attivita per restare sotto le soglie: uno scan lento, qualche tentativo di login sparso, un accesso "legittimo" a distanza di minuti. Confida che ogni sistema, guardando solo i propri log, non veda nulla di allarmante.

### Prospettiva Difensore (come il controllo risponde)

```
[DEF-002] Universal Forwarder -> Splunk indicizza log di firewall + server + Wazuh
        |
        v
Saved Search schedulata: transaction per src_ip (scan -> login riuscito, 5m)
        |
        v
ALERT: kill chain correlata -> l'IP e passato da recon ad accesso
        |
        v
Contenimento: blocco IP + disabilitazione dell'account compromesso (svc_web)
        |
        v
Threat hunting: pivot su svc_web -> ogni sistema toccato dall'account
```

**Valore difensivo:** la correlazione trasforma tre eventi "innocui" in una kill chain evidente. Una volta identificato l'account compromesso, il pivot in SPL rivela tutta l'estensione dell'accesso - quali sistemi, quali orari, quali dati toccati - fornendo lo scope reale dell'incidente.

**Indicatori monitorati (IOC):** sequenze scan, accesso dallo stesso IP, un account che appare su host inusuali, login riusciti preceduti da fallimenti, accessi correlati ad alert Wazuh/Suricata nello stesso intervallo.

**Lezione difensiva:** l'attaccante vince disperdendo, il difensore vince correlando. La detection matura non cerca il singolo evento malevolo (spesso indistinguibile dal normale) ma la sequenza che solo un attacco produce.

---

## Tool di riferimento

| Tool | Tipo | Ruolo | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Splunk Enterprise` | SIEM commerciale | Piattaforma | Indicizzazione, SPL, alerting, dashboard |
| `Universal Forwarder` | Log shipper | Agent | Inoltro leggero dei log dagli endpoint |
| `SPL` | Search language | Linguaggio | Query di detection e correlazione |
| `Splunk ES` (Enterprise Security) | SIEM premium | App | Correlation searches pronte + framework MITRE |
| `Splunk Free` | SIEM (limitato) | Piattaforma | Lab e volumi piccoli (500 MB/giorno, no auth) |
| `Sysmon` | Endpoint sensor | Agent (Win) | Telemetria di processo dettagliata da correlare in SPL |

> **Tool moderno consigliato:** per un ambiente di produzione, `Splunk Enterprise Security` (ES) fornisce correlation searches pronte all'uso mappate su MITRE ATT&CK. In un home lab, `Splunk Free` e sufficiente per imparare SPL. L'abbinamento con `Sysmon` sugli endpoint Windows fornisce la telemetria di processo che rende la correlazione molto piu ricca. Alternativa open source completa in `../elk-stack/`.

---

## Mappatura MITRE ATT&CK

> La tabella mappa le tecniche d'attacco che il controllo **rileva** tramite correlazione SPL.

| Tattica (rilevata) | Tecnica | ID MITRE | Ruolo del controllo |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Active Scanning: Scanning IP Blocks | `T1595.001` | Query SPL: un IP verso molte porte distinte (port scan) (DEF-002) |
| Credential Access | Brute Force | `T1110` | Query SPL: aggregazione login falliti per IP/utente (DEF-002) |
| Initial Access | Valid Accounts | `T1078` | Correlazione scan - login riuscito (accesso ottenuto) |
| Lateral Movement | Remote Services | `T1021` | Correlazione: stesso account su host multipli in sequenza |

| Contromisura difensiva (D3FEND) | ID D3FEND | Applicazione |
| :--- | :--- | :--- |
| Network Traffic Analysis | `D3-NTA` | Correlazione dei log di rete per rilevare scanning e accessi |
| User Behavior Analysis | `D3-UBA` | Rilevamento di sequenze di attivita anomale per utente/IP |

---

> **Nota:** Tutte le attivita documentate sono state condotte su un ambiente di laboratorio di proprieta dell'autore, con attacchi simulati sui sistemi di test. Il monitoraggio dei log in contesti reali deve rispettare la normativa su privacy e trattamento dei dati. Le tecniche sono documentate a scopo educativo e di difesa in contesto autorizzato.
