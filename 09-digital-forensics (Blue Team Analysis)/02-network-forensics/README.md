> [English](README.en.md) | **Italiano**

# 02 - Network Forensics

> - **Fase:** Digital Forensics & Incident Response - Network Analysis
> - **Categoria:** Analysis - ricostruzione dell'incidente dal traffico di rete
> - **Prerequisiti:** Cattura di traffico (PCAP) da IDS/tap/SIEM; strumenti di analisi (Wireshark, Zeek, tshark); contesto dell'incidente
> - **Output:** Finding FOR-002; ricostruzione delle sessioni di rete; conferma di C2/esfiltrazione; IOC estratti dal traffico

---

## Introduzione

La network forensics e l'analisi dell'incidente dal punto di vista del traffico di rete. Ha una proprieta che la rende preziosa: il traffico e la registrazione diretta e non alterabile di cio che e realmente accaduto sul filo. Dove i log di un host possono essere manomessi da chi lo compromette (anti-forensics, `07-post-exploitation`), una cattura di rete raccolta da un sistema indipendente registra la verita della comunicazione, immune alla manomissione applicativa retroattiva.

L'analisi di rete opera su due livelli complementari:

- **Flow / metadati:** chi comunica con chi, quando, quanto, con quale frequenza. Questo livello (log Zeek, NetFlow, statistiche delle conversazioni) rivela i pattern - il beaconing C2, i volumi di esfiltrazione - ed e visibile anche quando il contenuto e cifrato.
- **Contenuto / pacchetti:** cosa esattamente e stato trasmesso. Questo livello (Wireshark, Follow Stream) ricostruisce le sessioni applicative, recupera file e credenziali, ma e limitato dalla cifratura.

La sezione e centrata su **Wireshark (FOR-002)**, lo strumento di riferimento per l'analisi di dettaglio dei pacchetti. Il suo posizionamento nel percorso e preciso, come da nota strategica del modulo 08: la detection (SIEM/IDS) segnala dove guardare, Wireshark mostra cosa c'e. Non si apre a caso, si apre dopo che un alert ha fornito il punto di partenza dell'indagine.

Il collegamento con il resto della difesa e diretto: la network forensics e l'ultimo miglio della catena rilevamento, correlazione, analisi. Il SIEM (`../../08-defense-hardenings/01-siem-log-analysis/`) rileva e correla, la network forensics conferma e dettaglia, producendo la certezza documentata su cui si basa la risposta.

---

## Struttura della cartella

```
02-network-forensics/
+-- README.md          # questo file: registro FOR-002, concetto di network forensics
|
+-- wireshark/         # FOR-002: analisi PCAP, stream reassembly, estrazione IOC
```

---

## Flusso operativo consigliato

```
[INPUT] Alert dal SIEM/IDS (modulo 08) + cattura di traffico (PCAP)
         |
         v
[1] Puntamento (dall'alert)
     +-- l'alert fornisce IP/orario/pattern -> punto di partenza dell'indagine
              |
              v
[2] Analisi dei metadati (quadro d'insieme)
     +-- conversazioni/flow -> beaconing, volumi, destinazioni (anche in TLS)
              |
              v
[3] Analisi del contenuto (dettaglio) - wireshark/
     +-- display filter + Follow Stream -> sessioni ricostruite (FOR-002)
              |
              v
[4] Estrazione IOC e artefatti
     +-- file esfiltrati, IP C2, credenziali in chiaro
              |
              v
[OUTPUT] Incidente confermato e quantificato -> IOC -> detection (feedback al SIEM)
```

---

## Tool di riferimento

| Tool | Tipo | Ruolo | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Wireshark` | Packet analyzer | GUI | Analisi di dettaglio, Follow Stream (FOR-002) |
| `tshark` | Packet analyzer | CLI | Analisi scriptabile ed estrazione automatica |
| `Zeek` (Bro) | Network analysis | Framework | Log strutturati per l'analisi su larga scala |
| `NetworkMiner` | Network forensics | GUI | Estrazione automatica di file/credenziali/host |
| `Suricata` | IDS | Engine | Detection che innesca l'analisi |

> **Tool moderno consigliato:** `Zeek` per il quadro d'insieme (log strutturati di connessioni, DNS, HTTP, file) e `Wireshark`/`tshark` per il dettaglio del singolo stream. La combinazione copre entrambi i livelli - metadati e contenuto - dell'analisi di rete.

---

## Registro Finding - Sezione Network Forensics

| ID | Descrizione | Severity | Sottocartella |
| :--- | :--- | :---: | :--- |
| `FOR-002` | Wireshark: ricostruzione sessioni, conferma C2/esfiltrazione, estrazione IOC dal PCAP | `Alto` | `wireshark/` |

---

## Mappatura MITRE ATT&CK - Aggregata

> Tecniche d'attacco **ricostruite/confermate** dall'analisi di rete.

| Tattica (ricostruita) | Tecnica | ID MITRE | Finding Correlato |
| :--- | :--- | :--- | :--- |
| Command and Control | Application Layer Protocol: Web Protocols | `T1071.001` | FOR-002 |
| Command and Control | Application Layer Protocol: DNS | `T1071.004` | FOR-002 |
| Exfiltration | Exfiltration Over C2 Channel | `T1041` | FOR-002 |
| Credential Access | Network Sniffing | `T1040` | FOR-002 |

---

> **Nota:** L'analisi del traffico di rete di terzi senza autorizzazione costituisce reato e viola la normativa sulle comunicazioni. Tutte le attivita documentate sono state condotte su catture di laboratorio di proprieta dell'autore. In contesti reali, la cattura del traffico va condotta con base giuridica adeguata e nel rispetto della privacy. Le tecniche sono documentate a scopo educativo e di difesa/investigazione in contesto autorizzato.
