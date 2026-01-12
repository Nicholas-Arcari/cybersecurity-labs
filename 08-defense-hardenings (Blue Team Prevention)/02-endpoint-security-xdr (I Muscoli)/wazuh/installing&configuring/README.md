# Wazuh SIEM & Suricata IDS - Home Lab Setup

Questa repository documenta il processo di installazione, configurazione e troubleshooting di un ambiente di sicurezza monitorato (SIEM) utilizzando **Wazuh** su Kali Linux e **Suricata** come IDS, con agenti distribuiti su macchine Windows.

Il setup è pensato per essere flessibile, funzionante anche in ambienti mobili (es. connessione via Hotspot Wi-Fi).

---

### Architettura

Wazuh opera secondo un modello client-server gerarchico e modulare.

La comprensione di questa architettura è fondamentale per un dispiegamento efficace.

---

### Prerequisiti

L'installazione su Kali Linux, spesso eseguita in ambienti virtualizzati o su hardware non server-grade, richiede un'attenta pianificazione delle risorse.

L'errore più comune che porta al fallimento dei servizi (in particolare dell'Indexer) è l'insufficienza di memoria RAM, che causa l'intervento del processo OOM (Out Of Memory) Killer del kernel Linux.

----------------------------------------------------------------------------------------
| Componente |    Requisito Minimo      |        Requisito Raccomandato  |        Note Tecniche  |
----------------------------------------------------------------------------------------
| CPU   |   2 vCPU  |   4-8 vCPU  | L'Indexer richiede parallelismo per la gestione degli shard. Meno di 4 core possono causare timeout all'avvio |
| RAM| 4 GB |8-16 GB |L'Indexer alloca di default il 50% della RAM (fino a 32GB) alla JVM Heap. Con meno di 4GB totali, il sistema diventa instabile |
| Storage | 20 GB | 100 GB+ (SSD) | La velocità di I/O è critica per l'indicizzazione. Dischi rotativi possono causare colli di bottiglia |
| OS | Kali Linux (Rolling) | Debian 11/12 Stable | Kali è basata su Debian Testing. Questo implica aggiornamenti frequenti delle librerie (libc, openssl) che possono richiedere il pinning dei pacchetti Wazuh |

---

### Componenti Centrali (Lato Server - Kali Linux)

Il "Server Wazuh" non è un monolite, ma un'orchestrazione di tre servizi distinti che devono comunicare in modo sincrono:

- Wazuh Indexer: È un motore di ricerca e analisi full-text distribuito, basato su OpenSearch. La sua funzione è l'indicizzazione ad alta velocità e lo stoccaggio persistente degli allarmi di sicurezza generati dal Manager. Essendo basato su Java (JVM), è il componente più esoso in termini di risorse.   
- Wazuh Manager: Il cuore operativo della piattaforma. Riceve i log dagli agenti, li decodifica, li normalizza e li confronta con un set di regole per rilevare anomalie o minacce. Gestisce inoltre la crittografia delle comunicazioni e l'inventario degli endpoint.   
- Wazuh Dashboard: L'interfaccia utente web (basata su OpenSearch Dashboards) che permette agli analisti di visualizzare i dati, eseguire query di threat hunting e gestire la configurazione del cluster.

---

### Installazione del Nodo Centrale su Kali Linux

La procedura seguente assume che l'utente abbia privilegi di root sulla macchina Kali. A differenza di Ubuntu o CentOS, Kali Linux non sempre avvia automaticamente i servizi dopo l'installazione a causa delle policy di sicurezza predefinite.

---

### Preparazione del Sistema e Repository
Il primo passo consiste nell'installare i pacchetti necessari per gestire repository HTTPS sicuri e importare la chiave GPG di Wazuh. L'uso di gnupg è mandatorio per verificare l'integrità dei pacchetti e prevenire attacchi di tipo supply-chain.

```Bash
apt-get update
apt-get install gnupg apt-transport-https curl lsb-release
```

Importazione della chiave GPG e aggiunta del repository:

```Bash
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import && chmod 644 /usr/share/keyrings/wazuh.gpg
echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | tee -a /etc/apt/sources.list.d/wazuh.list
apt-get update
```

Analisi: L'uso di signed-by nel file `.list` è una best practice di sicurezza moderna su Debian che vincola quel repository specifico a quella chiave, evitando che una chiave compromessa possa validare pacchetti da altri repository.

---

### Installazione e Configurazione di Wazuh Indexer

L'Indexer deve essere installato per primo.

```Bash
apt-get install wazuh-indexer
```

Configurazione Critica del Cluster: Modificare `/etc/wazuh-indexer/opensearch.yml`. In un ambiente "All-in-One" (singolo nodo), la configurazione di rete è vitale.

```YAML
network.host: "127.0.0.1"  # Vincola al localhost per sicurezza se non serve accesso esterno diretto all'Indexer
node.name: "node-1"
cluster.initial_master_nodes: ["node-1"]
plugins.security.ssl.http.enabled: true
```

Gestione della Memoria JVM: Su macchine Kali con risorse limitate (es. 4-8GB RAM), è imperativo limitare l'Heap della Java Virtual Machine per evitare crash. Modificare `/etc/wazuh-indexer/jvm.options`:

`-Xms2g` `-Xmx2g` Questo imposta l'heap minimo e massimo a 2GB, lasciando RAM residua per il sistema operativo e il Wazuh Manager.

Avvio del Servizio:

```Bash
systemctl daemon-reload
systemctl enable wazuh-indexer
systemctl start wazuh-indexer
```

Nota: Questo passaggio può richiedere diversi minuti. Se fallisce, consultare la sezione TROUBLESHOOTING per la gestione dei timeout di systemd.

---

### Installazione di Wazuh Manager

```Bash
apt-get install wazuh-manager
systemctl enable wazuh-manager
systemctl start wazuh-manager
```

Dopo l'avvio, verificare che il manager sia correttamente in ascolto sulle porte critiche:

- `1514/TCP`: Comunicazione sicura con gli agenti (enrollment e dati).
- `55000/TCP`: API RESTful per la gestione e l'interfacciamento con la Dashboard.   

---

### Installazione di Wazuh Dashboard

```Bash
apt-get install wazuh-dashboard
```

La configurazione del file `/etc/wazuh-dashboard/opensearch_dashboards.yml` è il punto dove si verifica la maggior parte degli errori di connessione. È essenziale che l'URL dell'host OpenSearch corrisponda esattamente a quanto configurato nell'Indexer (protocollo HTTPS e porta).

```YAML
server.host: "0.0.0.0" # Ascolta su tutte le interfacce per permettere l'accesso dal browser
opensearch.hosts: ["https://127.0.0.1:9200"] # Connessione interna all'Indexer
opensearch.ssl.verificationMode: certificate
```

---

### Deployment degli Agenti: Windows e Raspberry Pi

L'efficacia del SIEM dipende dalla corretta configurazione degli agenti. La regola fondamentale per la stabilità è che la versione dell'Agente deve essere minore o uguale a quella del Manager.   

### Installazione su Windows (Workstation/Server)

L'utente ha riscontrato difficoltà nell'installazione via PowerShell. Analizziamo il comando corretto e le sue implicazioni.

Comando PowerShell Ottimizzato:

```PowerShell
Invoke-WebRequest -Uri https://packages.wazuh.com/4.x/windows/wazuh-agent-4.11.2-1.msi -OutFile $env:tmp\wazuh-agent.msi; msiexec.exe /i $env:tmp\wazuh-agent.msi /q WAZUH_MANAGER='<ip_dispositivo_windows>' WAZUH_AGENT_NAME='WindowsPC' WAZUH_REGISTRATION_SERVER='<ip_dispositivo_windows>'
```

Analisi dei Parametri:

- `WAZUH_MANAGER`: L'indirizzo IP della macchina Kali.
- `WAZUH_REGISTRATION_SERVER`: Spesso coincide con il Manager, ma specificarlo esplicitamente risolve problemi in cui l'agente non sa dove inviare la richiesta di chiave iniziale.
- `WAZUH_AGENT_NAME`: Un identificativo univoco. Se omesso, viene usato l'hostname del PC.

Post-Installazione e Avvio: Dopo l'installazione, il servizio non parte automaticamente in alcune configurazioni.

```PowerShell
NET START WazuhSvc
```

Se il comando restituisce "Servizio richiesto già avviato" ma l'agente non appare nel Manager, il problema risiede quasi certamente nella connettività di rete (Firewall di Windows o iptables su Kali che bloccano la porta 1514).

###  Installazione su Raspberry Pi (Linux ARM)
I Raspberry Pi utilizzano architetture ARM (armhf per sistemi a 32-bit, aarch64 per sistemi a 64-bit). Il gestore pacchetti apt gestisce automaticamente l'architettura, ma attenzione alle versioni.

Verifica Architettura:

```Bash
uname -m
# Output atteso: 'aarch64' (Pi 3/4/5 con OS 64bit) o 'armv7l' (Pi datati o OS 32bit)
```

Installazione e Blocco Versione: Per evitare che un aggiornamento automatico (`apt upgrade`) porti l'agente a una versione superiore a quella del Manager (causando disconnessione), è vitale bloccare il pacchetto.   

```Bash
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import && chmod 644 /usr/share/keyrings/wazuh.gpg
echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | tee -a /etc/apt/sources.list.d/wazuh.list
apt-get update

# Installazione esplicita (sostituire IP_KALI con l'IP reale)
WAZUH_MANAGER="IP_KALI" apt-get install wazuh-agent

# Blocco della versione (Hold)
echo "wazuh-agent hold" | dpkg --set-selections
```

---

### Il Concetto di "Agente 000" (Monitoraggio del Manager)

Una domanda ricorrente riguarda l'installazione di un agente sulla macchina stessa del Manager.

Tecnicamente, non si deve installare il pacchetto wazuh-agent sul server Wazuh Manager.

Il servizio wazuh-manager include nativamente un modulo "agente locale" che ha ID 000.

Questo agente monitora il sistema operativo sottostante (Kali Linux) esattamente come un agente esterno, ma con privilegi diretti sui file di log locali. 

Tentare di installare wazuh-agent sulla stessa macchina causerebbe conflitti sulla porta TCP 1514 e sui file di configurazione in `/var/ossec/etc/`, corrompendo l'installazione.

La configurazione dell'Agente 000 avviene modificando direttamente `/var/ossec/etc/ossec.conf`

---

### TROUBLESHOOTING.md: Analisi Approfondita e Risoluzione degli Errori

Questa sezione affronta le problematiche specifiche emerse durante la configurazione, fornendo una spiegazione teorica della causa e la procedura tecnica di risoluzione.

### Errore Critico Dashboard: "Wazuh dashboard server is not ready yet"

Sintomo: Tentando di accedere all'interfaccia web, l'utente visualizza il messaggio di caricamento infinito o l'errore "server not ready". Nei log (`journalctl -u wazuh-dashboard` o `/usr/share/wazuh-dashboard/data/wazuh/logs/wazuhapp.log`), compaiono errori di tipo `ConnectionError`, `ECONNREFUSED 127.0.0.1:9200` o `Internal Server Error 500`.   

Analisi delle Cause: La Dashboard agisce come un frontend per l'Indexer. Questo errore indica che la catena di comunicazione è interrotta. Le cause principali sono:

- Servizio Indexer non attivo: La Dashboard tenta di connettersi alla porta 9200, ma nessuno risponde.
- Mismatch di Protocollo (HTTP vs HTTPS): L'Indexer usa HTTPS di default, ma la Dashboard potrebbe essere configurata per usare HTTP.
- Certificati SSL non validi o corrotti: L'Indexer rifiuta la connessione perché la Dashboard non presenta un certificato valido o la Dashboard non si fida della CA dell'Indexer.

Protocollo di Risoluzione:

Fase 1: Verifica dello stato dell'Indexer Eseguire sulla macchina Kali:

```Bash
systemctl status wazuh-indexer
```

Se lo stato è failed (spesso con "`start operation timed out`"), procedere alla Sezione "Errore di Avvio Servizio: 'Start operation timed out' (Systemd)" Se è active, verificare se risponde effettivamente alle richieste API:

```Bash
curl -k -u admin:PASSWORD https://127.0.0.1:9200
```

Se si riceve un JSON con lo stato del cluster (es. "status" : "green" o "yellow"), l'Indexer funziona. Il problema è nella configurazione della Dashboard.

Fase 2: Rettifica della Configurazione Dashboard Modificare `/etc/wazuh-dashboard/opensearch_dashboards.yml`. Verificare la sezione `opensearch.hosts`. Errato: opensearch.hosts: [`http://127.0.0.1:9200`] Corretto: opensearch.hosts: [`https://127.0.0.1:9200`]

Assicurarsi che i percorsi dei certificati CA siano corretti e che i file esistano e siano leggibili dall'utente wazuh-dashboard:

```YAML
opensearch.ssl.certificateAuthorities: ["/etc/wazuh-dashboard/certs/root-ca.pem"]
opensearch.ssl.verificationMode: certificate
```

Dopo ogni modifica, riavviare il servizio: `systemctl restart wazuh-dashboard`.

### Errore di Autenticazione: "Resource 'admin' is reserved"

Sintomo: L'utente tenta di cambiare la password dell'utente admin tramite l'interfaccia grafica della Dashboard (o API) e riceve l'errore JSON: `{"status":"FORBIDDEN","message":"Resource 'admin' is reserved."}`.

Analisi Teorica: In OpenSearch (e quindi Wazuh Indexer), l'utente admin è un "super-user" interno gestito dal plugin di sicurezza. Per motivi di integrità del sistema, questo utente è marcato come reserved e non può essere modificato tramite le API standard RESTful che la GUI utilizza. La modifica deve avvenire a livello di configurazione backend, rigenerando gli hash delle password e ricaricando la configurazione di sicurezza.

Soluzione (Wazuh Passwords Tool): Wazuh fornisce uno script bash dedicato per questa operazione, che automatizza la complessità della rigenerazione degli hash e l'aggiornamento dei file di configurazione collegati (come `filebeat.yml` che usa queste credenziali per inviare log).

Accedere alla directory degli strumenti di sicurezza:

```Bash
cd /usr/share/wazuh-indexer/plugins/opensearch-security/tools/
```

Eseguire lo script `wazuh-passwords-tool.sh`. Per cambiare la password dell'utente admin:

```Bash
bash wazuh-passwords-tool.sh -u admin -p NuovaPasswordSicura!
```

Nota Cruciale per Ambienti Distribuiti: Sebbene lo script tenti di aggiornare le configurazioni, in alcuni casi è necessario aggiornare manualmente la password anche nel file `/etc/filebeat/filebeat.yml` (sezione `output.elasticsearch`) e `/etc/wazuh-dashboard/opensearch_dashboards.yml` (sezione `opensearch.password`), altrimenti questi componenti perderanno l'accesso all'Indexer.   

### Errore di Avvio Servizio: "Start operation timed out" (Systemd)

Sintomo: Il servizio wazuh-indexer fallisce l'avvio. systemctl status riporta: `wazuh-indexer.service: start operation timed out. Terminating..`  

Analisi delle Cause: L'inizializzazione della Java Virtual Machine (JVM) e il bootstrap del cluster OpenSearch sono operazioni intense. Su hardware limitato (come una VM Kali con dischi virtuali o un Raspberry Pi usato come nodo), il tempo necessario per raggiungere lo stato "Ready" può superare il timeout predefinito di systemd (solitamente 90 secondi). Quando il timeout scade, systemd invia un segnale SIGTERM, uccidendo il processo proprio mentre stava per avviarsi correttamente.

Soluzione Definitiva (Override Systemd): Non è sufficiente riprovare. È necessario estendere o disabilitare il timeout nel file unit del servizio.

Creare un override della configurazione systemd per l'Indexer:

```Bash
systemctl edit --full wazuh-indexer.service
```

Individuare la direttiva `` e aggiungere o modificare il parametro TimeoutStartSec. Impostarlo a 0 disabilita il timeout (attesa infinita), oppure impostare un valore elevato (es. 600 secondi).

```Bash
TimeoutStartSec=0
```

Salvare, ricaricare la configurazione del demone e riavviare:

```Bash
systemctl daemon-reload
systemctl restart wazuh-indexer
```

Questo approccio è spesso risolutivo in ambienti di laboratorio o VM con risorse condivise.   

### Conflitto di Versioni: Downgrade Agente su Linux

Sintomo: Gli agenti su Raspberry Pi o altri sistemi Linux si disconnettono dopo un aggiornamento di sistema. I log mostrano errori di negoziazione.

Analisi: Wazuh garantisce la compatibilità solo se Versione Manager è maggiore uguale Versione Agente. Se un apt upgrade aggiorna l'agente alla 4.10 mentre il manager è alla 4.9, la comunicazione si interrompe. Il downgrade non è supportato direttamente dai comandi di aggiornamento; richiede la rimozione e reinstallazione del pacchetto specifico.

Procedura di Downgrade:

Disinstallare la versione corrente:

```Bash
apt-get remove wazuh-agent
```

Installare la versione target specifica (es. 4.7.5-1):

```Bash
apt-get install wazuh-agent=4.7.5-1
```

Verificare che la configurazione (`ossec.conf`) e la chiave (`client.keys`) siano state preservate (Wazuh di solito non elimina i file di configurazione alla rimozione del pacchetto, ma farne un backup preventivo è saggio).   

### Problemi di Connettività Agente Windows (Firewall e Porte)

Sintomo: L'installazione via PowerShell su Windows termina con successo, il servizio WazuhSvc è in esecuzione, ma l'agente non appare nella Dashboard.

Analisi: Se il servizio è attivo, il problema è quasi sempre a livello di rete. Wazuh usa due porte critiche:

- `1514 TCP`: Canale principale per dati e keepalive.
- `1515 TCP`: Canale di enrollment (registrazione iniziale).

Procedura di Diagnosi su Windows (PowerShell): Utilizzare il cmdlet Test-NetConnection (o oggetti.NET TCP) per verificare se Windows riesce a raggiungere il Manager sulla porta 1514.

```PowerShell
Test-NetConnection -ComputerName <ip_dispositivo_windows> -Port 1514
```

Se il risultato è TcpTestSucceeded : False, il firewall di Kali Linux sta bloccando la connessione in entrata o il Firewall di Windows sta bloccando l'uscita.

Risoluzione su Kali Linux: Verificare iptables o ufw.

```Bash
ufw allow 1514/tcp
ufw allow 1515/tcp
iptables -A INPUT -p tcp --dport 1514 -j ACCEPT
iptables -A INPUT -p tcp --dport 1515 -j ACCEPT
```

Nota: Kali Linux ha spesso policy di default restrittive. Assicurarsi che le regole siano persistenti al riavvio.

---

### Analisi dei Log e Strumenti di Diagnostica

Per un troubleshooting efficace, è essenziale sapere dove guardare. La tabella seguente mappa i componenti ai rispettivi file di log e comandi di controllo

Componente	        File di Log Principale	                                    Comando Diagnostico (Status)	            Pattern di Errore Comuni
Wazuh Manager	    /var/ossec/logs/ossec.log	                                systemctl status wazuh-manager	            wazuh-remoted: ERROR: Bind to port 1514 failed (Porta occupata)
Wazuh Indexer	    /var/log/wazuh-indexer/wazuh-cluster.log	                journalctl -u wazuh-indexer	                Master not discovered, OutOfMemoryError
Wazuh Dashboard	    /usr/share/wazuh-dashboard/data/wazuh/logs/wazuhapp.log	    journalctl -u wazuh-dashboard	            ECONNREFUSED, Request failed with status code 500
Agente (Linux/RPi)	/var/ossec/logs/ossec.log	                                /var/ossec/bin/agent_control -l	            ERROR: (1137): Unable to connect to server
Agente (Windows)	C:\Program Files (x86)\ossec-agent\ossec.log	            Get-Service WazuhSvc	                    Error sending message to server


### Uso di agent_control

Sul Manager, il comando `/var/ossec/bin/agent_control` è lo strumento definitivo per verificare lo stato reale degli agenti, bypassando eventuali ritardi della Dashboard.

- `agent_control -l`: Lista tutti gli agenti registrati e il loro stato (Active/Disconnected).
- `agent_control -i <ID>`: Fornisce dettagli estesi su un agente specifico.

---

### Conclusioni e Raccomandazioni Operative

L'implementazione di Wazuh su un'architettura ibrida con Kali Linux come nodo centrale offre una potente piattaforma di monitoraggio della sicurezza, ma richiede una gestione rigorosa delle configurazioni di sistema. Le criticità maggiori risiedono nella gestione delle risorse (RAM per l'Indexer), nella sincronizzazione delle versioni tra Manager e Agenti, e nella corretta configurazione della catena di fiducia SSL/TLS.

Raccomandazioni Finali:

Pinning dei Pacchetti: Su sistemi "rolling" come Kali e su agenti distribuiti come Raspberry Pi, bloccare sempre le versioni dei pacchetti (apt-mark hold) una volta raggiunta una configurazione stabile.

Monitoraggio delle Risorse: Utilizzare l'Agente 000 per monitorare lo stato di salute del server Kali stesso, configurando allarmi per l'uso della memoria e del disco.

Backup dei Keystore: Prima di ogni aggiornamento, eseguire il backup dei file .keystore e dei certificati in `/etc/wazuh-indexer/certs` e `/etc/wazuh-dashboard/certs`.

Gestione Automatica Timeout: Implementare sistematicamente l'override TimeoutStartSec=0 per l'Indexer in ambienti virtualizzati o con risorse limitate per prevenire false failure all'avvio.