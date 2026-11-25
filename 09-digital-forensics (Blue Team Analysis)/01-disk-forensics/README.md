> [English](README.en.md) | **Italiano**

# Disk forensics - acquisizione, timeline e recupero degli artefatti

> - **Fase:** Digital Forensics & Incident Response - Disk & Memory Analysis
> - **Categoria:** Analysis - ricostruzione post-incidente dalle prove su disco
> - **Prerequisiti:** Accesso al supporto o all'immagine da analizzare; write blocker (fisico o software) per preservare la prova; workstation forense (Kali/SIFT/Autopsy); spazio di storage per le immagini
> - **Output:** Finding FOR-001; immagine forense verificata; timeline dell'incidente; artefatti recuperati (file cancellati, tool dell'attaccante, tracce di esecuzione); catena di custodia documentata

- **Ambiente Operativo:** Workstation forense (Kali Linux / SIFT), write blocker, supporto/immagine da analizzare
- **Ruolo:** Ricostruire cosa e successo dopo che l'attacco e avvenuto
- **Tool principali:** dc3dd/Guymager, Sleuth Kit, Autopsy, Volatility, plaso/log2timeline

---

## Executive summary

La disk forensics e l'analisi post-incidente: quando un sistema e stato compromesso, l'analista forense ricostruisce cosa e successo esaminando le tracce lasciate sul disco (e in memoria). E il modulo dove le tecniche offensive dei moduli 01-07 vengono viste dall'altra parte - non come si esegue un attacco, ma come lo si ricostruisce dopo, dalle prove che ha inevitabilmente lasciato.

Il principio che governa tutta la disciplina e l'**integrita della prova**: la prova digitale e fragile e alterabile, e un'analisi condotta male la contamina, rendendola inutilizzabile. Per questo la forensics segue un protocollo rigoroso: si lavora sempre su una **copia** (mai sull'originale), acquisita tramite **write blocker**, verificata con **hash crittografici** (se l'hash dell'immagine corrisponde a quello dell'originale, la copia e fedele), e ogni passaggio e documentato in una **catena di custodia** che ne garantisce l'ammissibilita.

Il finding FOR-001 documenta il ciclo forense completo su un sistema di test compromesso: acquisizione dell'immagine, verifica di integrita, costruzione della timeline (la sequenza temporale di tutto cio che e accaduto sul filesystem) e recupero degli artefatti dell'attaccante - inclusi file cancellati nel tentativo di coprire le tracce. E la contromisura investigativa all'anti-forensics vista in `07-post-exploitation`: cio che l'attaccante cancella, la forensics spesso recupera.

---

## Struttura della cartella

```
01-disk-forensics/
+-- README.md      # questo file: acquisizione, timeline, recupero artefatti (FOR-001)
+-- img/           # timeline e analisi Autopsy/Sleuth Kit
```

---

## Il ciclo forense: dall'Acquisizione al recupero

**ID Finding:** `FOR-001` | **Severity:** `Alto` (ricostruzione completa dell'intrusione dalle prove su disco, incluso il recupero di artefatti cancellati dall'attaccante)

### Contesto operativo

L'ordine delle operazioni forensi non e arbitrario ma segue l'**ordine di volatilita**: si acquisiscono prima le prove piu effimere (memoria RAM, connessioni di rete, processi) e poi quelle persistenti (disco). La RAM contiene tracce che spariscono allo spegnimento - chiavi di cifratura, processi malevoli, connessioni C2 - e va catturata per prima se il sistema e ancora acceso.

### PoC - fase 1: acquisizione dell'immagine (con integrita)

```Bash
# Acquisizione forense del disco con dc3dd (calcola l'hash durante la copia)
# Il write blocker impedisce ogni scrittura sul supporto originale
sudo dc3dd if=/dev/sdb of=evidence.dd hash=sha256 log=acquisition.log
```

```
dc3dd: 500 GB copied
  [ok] sha256: 9f2a8b...c41d              <-- hash dell'originale
evidence.dd: 500 GB written
```

### PoC - fase 2: verifica di integrita (la copia e fedele?)

```Bash
# L'hash dell'immagine deve corrispondere a quello dell'originale
sha256sum evidence.dd
```

```
9f2a8b...c41d  evidence.dd                <-- hash identico: copia forense valida (FOR-001)
# corrispondenza confermata -> l'immagine e ammissibile come prova
```

### PoC - fase 3: acquisizione ed analisi della memoria (Volatility)

```Bash
# Analisi di un dump di memoria: processi attivi al momento dell'incidente
vol.py -f memory.dmp windows.pslist
vol.py -f memory.dmp windows.netscan       # connessioni di rete (C2)
```

```
PID    PPID   Name             Note
6612   4408   svch0st.exe      <-- processo malevolo (nome camuffato) (FOR-001)
                               netscan: 6612 -> 45.83.x.x:443  (C2 attivo)
```

### PoC - fase 4: timeline dell'incidente

```Bash
# Costruzione della super-timeline con plaso (log2timeline)
log2timeline.py --storage-file timeline.plaso evidence.dd
psort.py -o l2tcsv -w timeline.csv timeline.plaso
```

```
# Estratto della timeline (ordine cronologico degli eventi)
2026-06-14 03:08  FILE  /tmp/linpeas.sh          created    <-- tool di enum (04)
2026-06-14 03:11  FILE  /root/.ssh/authorized_keys modified <-- persistenza (07)
2026-06-14 03:14  LOG   /var/log/auth.log        truncated  <-- anti-forensics (07)
2026-06-14 03:15  FILE  /tmp/exfil.tar.gz        created    <-- staging esfiltrazione
```

### PoC - fase 5: recupero di file cancellati (carving)

```Bash
# Recupero di file cancellati dall'attaccante (foremost/photorec)
foremost -i evidence.dd -o recovered/
```

```
Processing: evidence.dd
  sh: 1 file (deleted /tmp/exfil.tar.gz recuperato)   <-- artefatto recuperato (FOR-001)
# cio che l'attaccante ha cancellato per coprire le tracce e stato recuperato
```

### Metodologia e catena di custodia

- **Mai sull'originale:** ogni analisi si conduce sull'immagine, mai sul supporto originale; il write blocker garantisce che l'acquisizione non alteri la prova
- **Integrita verificabile:** l'hash acquisito al momento della copia va riverificato prima e dopo l'analisi; una discrepanza invalida la prova
- **Catena di custodia:** ogni passaggio (chi, cosa, quando, dove) va documentato; una prova la cui custodia non e tracciabile e inammissibile in un procedimento
- **Ordine di volatilita:** RAM e stato di rete prima del disco, se il sistema e acceso; spegnere un sistema distrugge le prove volatili

---

## Esperienza di laboratorio

La lezione piu importante e stata la disciplina dell'integrita, non la tecnica. Acquisire un'immagine con `dd` e banale; farlo in modo forensicamente valido - write blocker, hash calcolato durante la copia, verifica successiva - e cio che distingue un'analisi ammissibile da una contaminata. La prima volta ho montato distrattamente l'immagine in lettura-scrittura e ho alterato i timestamp: lezione appresa a mie spese sul perche ogni passaggio del protocollo esista. La prova digitale non perdona la sciatteria.

La ricostruzione della timeline e stata l'esperienza piu potente. Vedere la super-timeline di plaso allineare cronologicamente ogni evento - la creazione di `linpeas.sh` (l'enumerazione del modulo 04), la modifica di `authorized_keys` (la persistenza del modulo 07), il troncamento di `auth.log` (l'anti-forensics) - ha trasformato una collezione di file in una narrazione dell'attacco. La timeline non mostra file, mostra la storia di cosa l'attaccante ha fatto, minuto per minuto.

Il momento piu istruttivo e stato il recupero dell'archivio di esfiltrazione cancellato. Nel modulo 07 avevo documentato come un attaccante cancella le tracce; qui, con `foremost`, ho recuperato dallo spazio non allocato proprio il `.tar.gz` che l'attaccante-io aveva eliminato. Questo ha reso concreto il limite dell'anti-forensics: la cancellazione di un file rimuove il riferimento, non i dati, che restano recuperabili finche non sovrascritti. Cio che l'attaccante crede eliminato, la forensics spesso ricostruisce.

---

## Analisi teorica: la prova digitale come ricostruzione del passato

La forensics e archeologia del recente: ricostruire un evento passato (l'attacco) dalle tracce materiali che ha lasciato. Ogni azione su un sistema informatico lascia residui - file creati, timestamp modificati, voci di log, blocchi non allocati contenenti dati cancellati - e l'analista li interpreta per ricomporre la sequenza degli eventi. Il fondamento e che l'attivita non e mai senza traccia: anche l'attaccante piu attento altera lo stato del sistema, e ogni alterazione e potenzialmente una prova.

Il concetto chiave e l'ordine di volatilita, che deriva dalla fisica dell'informazione: alcune tracce sono effimere (la RAM si cancella allo spegnimento), altre persistenti (il disco sopravvive). L'analista deve catturare le prime prima che svaniscano, invertendo la priorita istintiva (spegnere il sistema compromesso e l'errore che distrugge le prove volatili). Questa gerarchia temporale della fragilita governa l'intero protocollo di acquisizione.

Il principio dell'integrita, infine, colloca la forensics all'incrocio tra tecnica e diritto. Una prova digitale ha valore solo se se ne puo dimostrare l'autenticita e la non-alterazione: l'hash crittografico e lo strumento matematico che lo garantisce (se l'hash non e cambiato, il dato non e cambiato), e la catena di custodia e lo strumento procedurale che ne traccia la storia. Questo rende la forensics una disciplina dove il rigore metodologico non e pedanteria ma la condizione stessa di validita del risultato. Si collega direttamente all'anti-forensics di `07-post-exploitation`: l'attaccante tenta di distruggere o alterare le tracce, l'analista di preservarle e recuperarle - due facce della stessa lotta sull'integrita della prova.

---

## Scenario reale: la ricostruzione dell'Incidente

> Questa sezione descrive come l'analisi forense opererebbe in un incidente reale, ricostruendo l'attacco per la risposta e l'eventuale attribuzione.

### Il contesto (cosa e successo)

Un endpoint ha generato un alert (SIEM/Wazuh, modulo 08) e viene isolato per l'analisi forense. L'attaccante, prima di essere rilevato, ha eseguito enumerazione, stabilito persistenza, tentato di cancellare le proprie tracce ed esfiltrato dati.

### La ricostruzione forense (cosa rivela l'analisi)

```
[FOR-001] Acquisizione immagine + memoria -> integrita verificata (hash)
        |
        v
Timeline (plaso): sequenza completa dell'intrusione ricostruita
        |
        +-- 03:08 tool di enumerazione droppato (accesso iniziale confermato)
        +-- 03:11 persistenza stabilita (authorized_keys)
        +-- 03:14 tentativo di anti-forensics (auth.log troncato)
        +-- 03:15 staging esfiltrazione (exfil.tar.gz)
        |
        v
Memory analysis (Volatility): processo C2 attivo -> IP dell'infrastruttura attaccante
        |
        v
Carving (foremost): archivio esfiltrazione cancellato recuperato -> scope dei dati
        |
        v
Report: timeline + IOC + scope della compromissione -> risposta e lezioni difensive
```

**Valore investigativo:** l'analisi forense risponde alle domande che la sola detection non puo: cosa esattamente ha fatto l'attaccante, quali dati ha toccato, da dove operava, quando e entrato. La timeline fornisce il "cosa e quando", la memory analysis il "chi" (l'IP C2 come IOC), il carving lo "scope" (i dati recuperati rivelano cosa era in procinto di essere esfiltrato).

**Indicatori estratti (IOC):** hash dei tool dell'attaccante, IP/domini C2 dalle connessioni in memoria, timestamp dell'intrusione, artefatti di persistenza. Questi IOC alimentano la detection (regole SIEM, blocklist) per rilevare la stessa minaccia altrove.

**Lezione difensiva:** la forensics chiude il ciclo dell'incident response. La detection (modulo 08) dice "e successo qualcosa"; la forensics dice "ecco esattamente cosa, come e con quale impatto". Senza questa ricostruzione, la risposta e cieca: non si puo contenere cio di cui non si conosce l'estensione, ne prevenire il ripetersi di un attacco che non si e compreso.

---

## Tool di riferimento

| tool | tipo | ruolo | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `dc3dd` / `Guymager` | imager | acquisizione | copia forense con hashing integrato |
| `Sleuth Kit` (tsk) | forensic toolkit | cli | analisi filesystem, recupero, timeline (fls/mactime) |
| `Autopsy` | forensic platform | gui | front-end di tsk: analisi visuale, keyword search, artefatti |
| `Volatility 3` | memory forensics | cli | analisi dei dump di ram (processi, rete, injection) |
| `plaso` / `log2timeline` | timeline | cli | super-timeline correlata da tutte le sorgenti |
| `foremost` / `photorec` | file carving | cli | recupero di file cancellati dallo spazio non allocato |
| `write blocker` | hardware/software | preservazione | impedisce la scrittura sul supporto originale |

> **Tool moderno consigliato:** per un flusso completo, `Autopsy` (front-end di Sleuth Kit) copre analisi filesystem, timeline e keyword search in un'unica interfaccia. `Volatility 3` e lo standard per la memoria. `plaso` per le super-timeline. La distribuzione `SIFT Workstation` (SANS) integra l'intero arsenale forense pronto all'uso.

---

## Mappatura MITRE ATT&CK

> La tabella mappa le tecniche d'attacco che l'analisi forense **ricostruisce/rileva** a posteriori.

| tattica (ricostruita) | tecnica | id mitre | ruolo dell'analisi |
| :--- | :--- | :--- | :--- |
| defense evasion | indicator removal: file deletion | `T1070.004` | carving recupera i file cancellati dall'attaccante (FOR-001) |
| defense evasion | indicator removal: clear linux logs | `T1070.002` | la timeline evidenzia il troncamento dei log |
| persistence | account manipulation: ssh authorized keys | `T1098.004` | la timeline rivela la modifica di authorized_keys |
| command and control | application layer protocol | `T1071` | memory analysis rivela le connessioni c2 attive |
| exfiltration | data staged | `T1074` | il carving recupera l'archivio di staging dell'esfiltrazione |

| contromisura difensiva (d3fend) | id d3fend | applicazione |
| :--- | :--- | :--- |
| system call analysis | `D3-SCA` | analisi degli artefatti di esecuzione sul disco |
| memory boundary tracking | `D3-MBT` | analisi forense della memoria per processi/injection |
| file analysis | `D3-FA` | recupero e analisi degli artefatti su filesystem |

---

> **Nota:** Tutte le attivita documentate sono state condotte su immagini e sistemi di laboratorio di proprieta dell'autore. La disk forensics su supporti di terzi richiede autorizzazione legale (mandato, consenso del titolare) e il rispetto rigoroso della catena di custodia, che ne determina l'ammissibilita. L'analisi forense puo esporre dati personali: va condotta nel rispetto della normativa su privacy e trattamento dei dati. Le tecniche sono documentate a scopo educativo e di difesa/investigazione in contesto autorizzato.
