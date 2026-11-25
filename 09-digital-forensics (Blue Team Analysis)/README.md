> [English](README.en.md) | **Italiano**

# 09 - Digital Forensics (Blue Team Analysis)

> - **Fase:** Difesa - Digital Forensics & Incident Response (DFIR)
> - **Categoria:** Analysis - ricostruzione dell'incidente dalle prove
> - **Prerequisiti:** Comprensione delle tecniche offensive (moduli 01-07) e della detection (modulo 08); strumenti forensi (SIFT/Autopsy/Wireshark); rigore metodologico (integrita, catena di custodia)
> - **Output:** Finding FOR-001..002; ricostruzione documentata dell'attacco; IOC estratti; base per risposta, attribuzione e lezioni difensive

---

## Introduzione

Il modulo `09-digital-forensics` e l'analisi post-incidente: dopo che un attacco e avvenuto (moduli 01-07) e la difesa lo ha rilevato (modulo 08), la forensics ricostruisce cosa e successo esattamente, esaminando le tracce lasciate sui sistemi e nel traffico. E il modulo che chiude il ciclo dell'incident response: la detection dice "e successo qualcosa", la forensics dice "ecco esattamente cosa, come, quando e con quale impatto".

E anche il modulo dove le tecniche offensive del percorso vengono viste dall'altra parte. Ogni azione dell'attaccante lascia tracce - file, timestamp, log, pacchetti - e la forensics le interpreta per ricomporre la storia dell'attacco. Cio che il modulo 07 ha insegnato a fare (enumerare, persistere, esfiltrare, cancellare le tracce), il modulo 09 insegna a ricostruire dopo. E la contromisura investigativa all'anti-forensics: cio che l'attaccante cancella, la forensics spesso recupera.

Il principio che governa l'intera disciplina e l'**integrita della prova**. La prova digitale e fragile e alterabile; un'analisi condotta senza rigore la contamina, rendendola inutile o inammissibile. Da qui il protocollo non negoziabile: lavorare sempre su copie (mai sull'originale), verificare l'integrita con hash crittografici, documentare ogni passaggio in una catena di custodia, rispettare l'ordine di volatilita. Il rigore metodologico non e pedanteria: e la condizione stessa di validita del risultato.

Il modulo copre le due grandi aree della forensics:

1. **Disk Forensics (`01-disk-forensics/`, FOR-001):** l'analisi dei supporti di memorizzazione (e della RAM). Acquisizione dell'immagine, verifica di integrita, costruzione della timeline dell'incidente, recupero degli artefatti - inclusi i file che l'attaccante ha cancellato.

2. **Network Forensics (`02-network-forensics/`, FOR-002):** l'analisi del traffico di rete. Wireshark ricostruisce le sessioni dell'attaccante dai pacchetti, confermando esfiltrazione e C2 ed estraendo IOC. Il traffico e il testimone imparziale: non manomettibile a posteriori come i log di un host compromesso.

Il posizionamento nel percorso e alla fine della catena difensiva: prevenire (08/hardening), rilevare (08/SIEM-XDR), rispondere e **analizzare** (09/forensics). La forensics fornisce la comprensione senza cui la risposta e cieca e la prevenzione futura impossibile.

---

## Struttura della cartella

```
09-digital-forensics (Blue Team Analysis)/
+-- README.md                          <- questo file: registro FOR-001..002 + MITRE aggregata
|
+-- 01-disk-forensics/                 <- FOR-001 (acquisizione, timeline, recupero artefatti)
|
+-- 02-network-forensics/
    +-- README.md                      <- registro FOR-002, concetto di network forensics
    +-- wireshark/                     <- FOR-002 (analisi PCAP, stream reassembly, IOC)
```

---

## Flusso operativo consigliato

```
[INPUT] Incidente rilevato (alert dal modulo 08) + sistemi/traffico da analizzare
         |
         v
[1] Preservazione (ordine di volatilita)
     +-- memoria e stato di rete PRIMA del disco (se il sistema e acceso)
     +-- acquisizione con write blocker + hash di integrita
              |
              v
[2] Disk & Memory Forensics (01-disk-forensics/)
     +-- timeline dell'incidente + recupero artefatti cancellati (FOR-001)
     +-- memory analysis -> processi/C2 in RAM
              |
              v
[3] Network Forensics (02-network-forensics/)
     +-- analisi PCAP -> conferma esfiltrazione/C2, estrazione IOC (FOR-002)
              |
              v
[4] Correlazione e reporting
     +-- timeline disco + traffico -> narrazione completa dell'attacco
     +-- IOC -> feedback alla detection (modulo 08)
              |
              v
[OUTPUT] Incidente ricostruito e documentato -> risposta, attribuzione, hardening mirato
```

---

## Tool di riferimento

| Tool | Area | Ruolo | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Autopsy` / `Sleuth Kit` | Disk | Piattaforma | Analisi filesystem, timeline, recupero (FOR-001) |
| `Volatility 3` | Memory | Analyzer | Analisi dei dump di RAM (processi, rete, injection) |
| `plaso` / `log2timeline` | Disk | Timeline | Super-timeline correlata dell'incidente |
| `Wireshark` / `tshark` | Network | Analyzer | Analisi PCAP, ricostruzione sessioni (FOR-002) |
| `Zeek` | Network | Framework | Log strutturati del traffico su larga scala |
| `dc3dd` / write blocker | Acquisizione | Preservazione | Copia forense con integrita garantita |

> **Tool moderno consigliato:** la `SIFT Workstation` (SANS) integra l'intero arsenale forense pronto all'uso (Autopsy, Volatility, plaso, Wireshark). Per un flusso disco, memoria, rete, la combinazione `Autopsy` + `Volatility 3` + `Wireshark` copre l'analisi completa di un incidente, dalla timeline su disco alla conferma sul traffico.

---

## Registro Finding - Modulo 09

| ID | Descrizione | Severity | Sottocartella |
| :--- | :--- | :---: | :--- |
| `FOR-001` | Disk forensics: acquisizione, timeline dell'incidente, recupero artefatti cancellati | `Alto` | `01-disk-forensics/` |
| `FOR-002` | Network forensics (Wireshark): ricostruzione sessioni, conferma C2/esfil, IOC | `Alto` | `02-network-forensics/wireshark/` |

---

## Mappatura MITRE ATT&CK - Aggregata

> Il modulo forense mappa le tecniche d'attacco che l'analisi **ricostruisce e conferma** a posteriori dalle prove. Framework complementare: MITRE D3FEND.

| Tattica (ricostruita) | Tecnica | ID MITRE | Finding Correlato |
| :--- | :--- | :--- | :--- |
| Defense Evasion | Indicator Removal: File Deletion | `T1070.004` | FOR-001 (carving recupera i file cancellati) |
| Defense Evasion | Indicator Removal: Clear Linux Logs | `T1070.002` | FOR-001 (la timeline evidenzia il tampering) |
| Persistence | Account Manipulation: SSH Authorized Keys | `T1098.004` | FOR-001 |
| Command and Control | Application Layer Protocol: Web Protocols | `T1071.001` | FOR-001, FOR-002 |
| Command and Control | Application Layer Protocol: DNS | `T1071.004` | FOR-002 |
| Exfiltration | Exfiltration Over C2 Channel | `T1041` | FOR-002 |
| Exfiltration | Data Staged | `T1074` | FOR-001 |
| Credential Access | Network Sniffing | `T1040` | FOR-002 |

| Contromisura difensiva (D3FEND) | ID D3FEND | Area |
| :--- | :--- | :--- |
| File Analysis | `D3-FA` | Disk forensics (artefatti su filesystem) |
| Memory Boundary Tracking | `D3-MBT` | Memory forensics (analisi RAM) |
| Network Traffic Analysis | `D3-NTA` | Network forensics (analisi PCAP) |

---

> **Nota:** Tutte le attivita documentate in questo modulo sono state condotte su immagini, sistemi e catture di traffico di laboratorio di proprieta dell'autore. La forensics su sistemi o traffico di terzi richiede autorizzazione legale (mandato, consenso del titolare) e il rispetto rigoroso della catena di custodia, che ne determina l'ammissibilita. L'analisi forense espone frequentemente dati personali e comunicazioni private: va condotta nel rispetto della normativa su privacy e con base giuridica adeguata. Le tecniche sono documentate a scopo educativo e di difesa/investigazione in contesto autorizzato.
