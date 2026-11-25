> [English](README.en.md) | **Italiano**

# Wireshark - analisi dei pacchetti e ricostruzione delle sessioni

> - **Fase:** Digital Forensics & Incident Response - Network Forensics (packet analysis)
> - **Categoria:** Analysis - analisi di dettaglio del traffico catturato
> - **Prerequisiti:** Cattura di traffico (PCAP) da analizzare; Wireshark/tshark; comprensione dei protocolli di rete; contesto dell'incidente (cosa cercare)
> - **Output:** Finding FOR-002; ricostruzione delle sessioni dell'attaccante; estrazione di IOC dal traffico; conferma di esfiltrazione, C2 o credenziali in chiaro

- **Ambiente Operativo:** Workstation forense, file PCAP da SIEM/IDS o cattura mirata
- **Ruolo:** L'ultimo miglio dell'analisi: guardare dentro i singoli pacchetti
- **Tool principali:** Wireshark, tshark, NetworkMiner, Zeek

---

## Executive summary

Wireshark e lo strumento di analisi di dettaglio del traffico di rete: dove il SIEM (`../../../08-defense-hardenings/01-siem-log-analysis/`) rileva e correla e Suricata segnala, Wireshark si apre dopo, per guardare dentro i singoli pacchetti e capire esattamente cosa contenevano. E l'ultimo miglio dell'analisi di rete: la conferma definitiva di cosa e realmente passato sul filo.

La nota strategica del percorso lo colloca con precisione: Splunk ti dice "ho visto una connessione strana + un login fallito + un alert di Wazuh nello stesso minuto"; Wireshark lo apri dopo che Splunk ti ha avvisato, per esaminare quei pacchetti specifici e capire cosa trasportavano. La detection indica dove guardare, Wireshark mostra cosa c'e.

Il finding FOR-002 documenta l'analisi forense di una cattura di traffico: l'uso dei display filter per isolare le conversazioni rilevanti, la dissezione dei protocolli, la ricostruzione delle sessioni (stream reassembly) e l'estrazione di IOC. In una cattura contenente traffico d'attacco, questo permette di confermare l'esfiltrazione (cosa e uscito), identificare il C2 (con chi comunicava l'host compromesso) e recuperare credenziali o comandi trasmessi in chiaro.

---

## Struttura della cartella

```
wireshark/
+-- README.md      # questo file: analisi PCAP, stream reassembly, estrazione IOC (FOR-002)
+-- img/           # display filter e Follow TCP Stream
```

---

## Analisi forense di una cattura di traffico

**ID Finding:** `FOR-002` | **Severity:** `Alto` (ricostruzione delle sessioni d'attacco dal traffico, conferma di esfiltrazione/C2 ed estrazione di IOC)

### Contesto operativo

Una cattura di traffico grezza contiene migliaia di pacchetti, in gran parte rumore. L'analisi forense e l'arte di isolare il segnale: i **display filter** di Wireshark permettono di restringere la vista alle sole conversazioni rilevanti, e il **Follow Stream** ricompone i pacchetti frammentati di una sessione TCP nella loro sequenza logica, rendendo leggibile lo scambio applicativo.

### PoC - display filter: isolare il traffico sospetto

```
# Filtro: traffico verso un IP sospetto identificato dal SIEM
ip.addr == 45.83.x.x

# Filtro: possibile esfiltrazione (upload HTTP POST di grandi dimensioni)
http.request.method == "POST" and http.content_length > 100000

# Filtro: possibile tunnel DNS (query anomale, sottodomini lunghi)
dns.qry.name.len > 50
```

### PoC - follow TCP stream: ricostruire la sessione

```
# Wireshark: tasto destro sul pacchetto -> Follow -> TCP Stream
# Ricompone l'intera conversazione applicativa

# Esempio: credenziali trasmesse in chiaro (HTTP Basic / FTP / Telnet)
POST /login HTTP/1.1
Host: internal-app
Authorization: Basic YWRtaW46UGFzc3cwcmQh    <-- credenziali in chiaro (base64) (FOR-002)
# decodifica base64 -> admin:Passw0rd!
```

### PoC - identificazione del c2 (beaconing)

```
# Statistics -> Conversations: individua il beaconing (connessioni regolari)
# Un host interno che contatta un IP esterno a intervalli fissi = C2 beacon

ip.src == 10.0.5.15 and ip.dst == 45.83.x.x and tcp.flags.syn == 1
```

```
# Pattern di beaconing rilevato:
10.0.5.15 -> 45.83.x.x:443  ogni 60s (+/- jitter)   <-- C2 beacon (FOR-002)
# connessione regolare a intervalli fissi = canale di comando e controllo
```

### PoC - estrazione di file e IOC (tshark)

```Bash
# Estrazione automatica degli oggetti trasferiti (file exfiltrati/malware)
tshark -r capture.pcap --export-objects http,extracted/

# Estrazione degli IOC: tutti gli IP di destinazione esterni contattati
tshark -r capture.pcap -T fields -e ip.dst | sort -u
```

```
extracted/exfil.zip      <-- file esfiltrato recuperato dal traffico (FOR-002)
45.83.x.x                <-- IOC: IP C2/esfiltrazione
```

### Metodologia di analisi

- **Parti dall'indizio:** la detection (SIEM/IDS) fornisce il punto di partenza (un IP, un orario, un alert); il display filter restringe la cattura a quel contesto invece di navigare a caso
- **Ricostruisci, non leggere pacchetto per pacchetto:** il Follow Stream ricompone la sessione; l'analisi avviene sulla conversazione, non sui singoli frame
- **Cifratura come limite:** il traffico TLS non e leggibile senza le chiavi; l'analisi si sposta sui metadati (chi parla con chi, quando, quanto - il beaconing e visibile anche in TLS)
- **Preserva la cattura:** il PCAP e una prova; va trattato con la stessa integrita (hashing) di un'immagine disco

---

## Esperienza di laboratorio

Il salto di comprensione e stato passare dalla cattura grezza alla sessione ricostruita. Una cattura di migliaia di pacchetti e illeggibile pacchetto per pacchetto; il primo `Follow TCP Stream` che ha ricomposto una conversazione HTTP completa - richiesta, header, credenziali, risposta - ha reso Wireshark improvvisamente utile. Ho capito che l'analista forense non legge pacchetti, ricostruisce conversazioni: il pacchetto e l'unita di trasporto, la sessione e l'unita di significato.

La nota strategica del percorso si e verificata nella pratica. Non ho aperto Wireshark a caso: l'ho aperto perche il SIEM (modulo 08) mi aveva segnalato una connessione verso un IP specifico. Quel puntamento ha trasformato un mare di pacchetti in un'indagine mirata - filtro sull'IP, follow dello stream, e in pochi minuti avevo la conferma. Detection e analisi di dettaglio non competono: la prima dice dove guardare, la seconda cosa c'e. Usarle in sequenza e enormemente piu efficiente che l'una senza l'altra.

Il limite piu istruttivo e stato la cifratura. Gran parte del traffico moderno e TLS, e aprire uno stream cifrato mostra solo byte illeggibili. La lezione: contro il traffico cifrato, l'analisi si sposta dai contenuti ai metadati. Non potevo leggere cosa l'host esfiltrava, ma il pattern di beaconing - connessioni regolari ogni 60 secondi verso lo stesso IP esterno - era visibile e sufficiente a identificare il C2. La cifratura protegge il contenuto, non il comportamento.

---

## Analisi teorica: il traffico come registrazione fedele degli eventi

Il traffico di rete ha una proprieta forense unica: e la registrazione diretta e non alterabile di cio che e realmente accaduto sul filo. Mentre i log sono una rappresentazione di secondo livello (un'applicazione decide cosa registrare e puo essere manomessa), una cattura di pacchetti e la realta stessa della comunicazione, catturata al livello piu basso. Se un dato e uscito dalla rete, e nel PCAP; nessuna anti-forensics applicativa puo cancellarlo da una cattura gia effettuata.

Questo colloca la network forensics in una posizione privilegiata rispetto alla host forensics. Un attaccante che compromette un host puo alterarne i log e cancellarne i file (anti-forensics, modulo 07), ma non puo modificare retroattivamente una cattura di rete raccolta da un sistema indipendente. Il traffico e testimone imparziale: registra sia cio che l'attaccante voleva fare (i comandi, le richieste) sia cio che non voleva rivelare (il beaconing C2, i volumi di esfiltrazione).

Il limite teorico e la cifratura, che introduce una tensione fondamentale. Il TLS protegge la confidenzialita del contenuto anche dall'analista legittimo, spostando l'analisi sui metadati: chi comunica con chi, quando, con quale frequenza e volume. Questo riflette un principio generale della sicurezza - i metadati sono spesso rivelatori quanto i contenuti. Un canale C2 puo cifrare i comandi, ma il pattern della comunicazione (regolarita, destinazione, dimensioni) tradisce la sua natura. L'analista forense moderno legge il comportamento del traffico quando non puo leggerne il contenuto, e spesso il comportamento e sufficiente a ricostruire l'attacco.

---

## Scenario reale: la conferma dell'Incidente

> Questa sezione descrive come l'analisi di rete opererebbe in un incidente reale, confermando e dettagliando cio che la detection ha segnalato.

### Il contesto (l'innesco)

Il SIEM (modulo 08) ha correlato una connessione anomala di un host interno verso un IP esterno sconosciuto, in coincidenza con un alert Wazuh. L'host viene isolato e il suo traffico (catturato dall'IDS/tap) viene passato all'analisi forense per capire cosa e realmente accaduto.

### L'analisi di rete (cosa conferma)

```
[FOR-002] PCAP dell'host sospetto -> display filter sull'IP segnalato dal SIEM
        |
        v
Follow Stream: ricostruzione delle sessioni -> comandi/dati scambiati
        |
        +-- beaconing regolare ogni 60s -> confermato canale C2 (non falso positivo)
        +-- HTTP POST voluminoso -> confermata esfiltrazione
        |
        v
tshark export-objects: recupero del file esfiltrato -> scope reale dei dati usciti
        |
        v
Estrazione IOC: IP C2, hash del file, pattern di beaconing
        |
        v
IOC -> regole SIEM/blocklist -> caccia alla stessa minaccia sugli altri host
```

**Valore investigativo:** l'analisi di rete trasforma un sospetto ("connessione anomala") in una certezza documentata ("esfiltrazione di questo file verso questo C2, con questo pattern"). Conferma o smentisce l'allarme, quantifica il danno (cosa e uscito), e produce IOC riutilizzabili per rilevare la stessa minaccia altrove.

**Indicatori estratti (IOC):** IP e domini C2, pattern di beaconing (intervallo, jitter, porta), hash dei file trasferiti, credenziali eventualmente esposte in chiaro. Questi chiudono il ciclo alimentando la detection.

**Lezione difensiva:** la network forensics e il testimone imparziale dell'incidente. Dove i log dell'host possono essere manomessi, il traffico catturato da un sistema indipendente registra la verita di cio che e passato. E la conferma finale che trasforma un alert in un fatto accertato - e la base solida su cui costruire la risposta.

---

## Tool di riferimento

| tool | tipo | ruolo | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Wireshark` | packet analyzer | gui | analisi interattiva, display filter, follow stream |
| `tshark` | packet analyzer | cli | analisi scriptabile, estrazione oggetti/campi |
| `NetworkMiner` | network forensics | gui | estrazione automatica di file, credenziali, host |
| `Zeek` (bro) | network analysis | framework | log strutturati del traffico per analisi su larga scala |
| `tcpdump` | packet capture | cli | cattura del traffico (a monte dell'analisi) |
| `Suricata` | ids | engine | detection che innesca l'analisi (`../../../08-.../`) |

> **Tool moderno consigliato:** `Wireshark` per l'analisi interattiva di dettaglio, `tshark` per l'automazione e l'estrazione. Per le catture grandi, `Zeek` produce log strutturati (connessioni, DNS, HTTP, file) che rendono l'analisi scalabile - complementare a Wireshark: Zeek per il quadro d'insieme, Wireshark per il dettaglio del singolo stream. `NetworkMiner` per l'estrazione automatica rapida di artefatti.

---

## Mappatura MITRE ATT&CK

> La tabella mappa le tecniche d'attacco che l'analisi di rete **ricostruisce/conferma** dal traffico.

| tattica (ricostruita) | tecnica | id mitre | ruolo dell'analisi |
| :--- | :--- | :--- | :--- |
| command and control | application layer protocol: web protocols | `T1071.001` | identificazione del beaconing c2 su http/s (FOR-002) |
| command and control | application layer protocol: dns | `T1071.004` | rilevamento di tunnel dns (query anomale) (FOR-002) |
| exfiltration | exfiltration over c2 channel | `T1041` | conferma e quantificazione dell'esfiltrazione (FOR-002) |
| credential access | network sniffing / cleartext | `T1040` | recupero di credenziali trasmesse in chiaro (FOR-002) |
| command and control | non-standard port | `T1571` | identificazione di c2 su porte non standard |

| contromisura difensiva (d3fend) | id d3fend | applicazione |
| :--- | :--- | :--- |
| network traffic analysis | `D3-NTA` | analisi del traffico per ricostruire le sessioni |
| protocol metadata anomaly detection | `D3-PMAD` | rilevamento di beaconing/tunnel dai metadati |
| client-server payload profiling | `D3-CSPP` | profilazione del payload per identificare c2/esfil |

---

> **Nota:** Tutte le attivita documentate sono state condotte su catture di traffico di laboratorio di proprieta dell'autore. L'intercettazione e l'analisi del traffico di rete di terzi senza autorizzazione costituisce reato e viola la normativa sulle comunicazioni. In contesti reali, la cattura del traffico puo esporre dati personali e comunicazioni private: va condotta nel rispetto della normativa su privacy e con base giuridica adeguata. Le tecniche sono documentate a scopo educativo e di difesa/investigazione in contesto autorizzato.
