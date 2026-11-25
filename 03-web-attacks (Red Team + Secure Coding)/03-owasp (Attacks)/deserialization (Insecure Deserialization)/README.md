> [English](README.en.md) | **Italiano**

# Insecure Deserialization (gadget chain, ysoserial)

> - **Fase:** Web Exploitation - OWASP A08:2021 Software and Data Integrity Failures (deserializzazione di dati non fidati)
> - **Visibilita:** Media - invio di oggetti serializzati anomali; l'esecuzione del gadget chain genera processi figli dal processo applicativo
> - **Prerequisiti:** un'applicazione che deserializza dati forniti dall'utente (cookie, parametri, messaggi) con una libreria che, in presenza di gadget disponibili nel classpath, permette l'esecuzione di codice
> - **Natura del documento:** metodologia. Payload illustrativi (concetto di gadget chain, nessun payload RCE copia-incolla armato), nessun Finding ID fabbricato (prossimo `WEB-016`, da assegnare in lab).

- Obiettivo: ottenere esecuzione di codice remoto (RCE) sfruttando la deserializzazione di dati non fidati, quando l'applicazione ricostruisce oggetti da input controllato dall'attaccante.

---

## Executive Summary

La serializzazione converte un oggetto in memoria in un flusso di byte (per salvarlo o trasmetterlo); la
deserializzazione fa l'inverso. Il problema sorge quando un'applicazione deserializza dati forniti
dall'utente: durante la ricostruzione dell'oggetto, alcuni linguaggi eseguono automaticamente metodi
"magici" (es. `readObject` in Java, `__wakeup`/`__destruct` in PHP, `__reduce__` in Python pickle). Se nel
classpath dell'applicazione esistono classi le cui combinazioni di metodi (una "gadget chain") portano
all'esecuzione di comandi, un attaccante puo costruire un oggetto serializzato malevolo che, una volta
deserializzato, esegue codice sul server.

In Java questo e sistematizzato da ysoserial, uno strumento che genera payload per decine di gadget chain
note (Commons-Collections, Spring, ecc.). L'impatto tipico e RCE diretta, quindi severity `Critico`. Il
vettore e insidioso perche la deserializzazione avviene spesso in punti non ovvi: cookie di sessione
serializzati, parametri `ViewState`, messaggi su code, token.

## Contesto operativo (perche, prima del come)

Si cerca la deserializzazione dove l'app accetta dati strutturati "opachi": cookie o parametri che
contengono blob Base64 che iniziano con marcatori noti (es. `rO0` per Java serializzato, `TypeError`/`gASV`
per pickle Python). La decisione operativa chiave e identificare il formato (Java, PHP, .NET, Python) e
quali gadget chain sono disponibili nel classpath/ambiente dell'app: non basta che l'app deserializzi, serve
una catena di gadget sfruttabile. ysoserial automatizza la generazione per Java provando le chain note.

## Esecuzione / Comandi

### Fase 1 - Identificazione del formato serializzato

```bash
# Un blob Base64 che decodifica a byte che iniziano con 0xAC 0xED (o 'rO0' in Base64) = oggetto Java serializzato
echo "rO0ABXNy..." | base64 -d | xxd | head -1
```

Output illustrativo:

```
00000000: aced 0005 7372 ...        <-- magic bytes Java serialization: candidato a insecure deserialization
```

### Fase 2 - Generazione del payload (concetto, ysoserial)

ysoserial genera un oggetto serializzato basato su una gadget chain nota. A livello concettuale:

```bash
# Genera un payload per la gadget chain CommonsCollections che esegue un comando (forma didattica)
java -jar ysoserial.jar CommonsCollections5 '<comando>' > payload.bin
```

Il comando incapsulato, in un test di laboratorio, e tipicamente un semplice marcatore verificabile (es. un
`ping` verso la macchina attaccante o la scrittura di un file), NON un payload distruttivo. La verifica OOB
(il server contatta l'attaccante) conferma l'RCE senza bisogno di una shell completa.

### Fase 3 - Invio e conferma

Il payload viene inviato nel punto di deserializzazione (cookie, parametro, corpo) e si osserva l'effetto
del comando (callback di rete, file creato). Output illustrativo lato attaccante:

```
# listener che riceve il ping/callback dal server bersaglio
ICMP echo request from 10.10.10.40   <-- il server ha deserializzato ed eseguito: RCE confermata
```

## Analisi dei risultati

La conferma del callback dimostra l'esecuzione di codice sul server: e RCE, severity `Critico`. Da qui, in
un engagement, si passerebbe da un comando "marcatore" a una reverse shell per l'accesso interattivo, ma la
dimostrazione del finding non richiede di spingersi oltre la prova OOB. Se l'app deserializza ma non esiste
una gadget chain sfruttabile nel classpath, l'impatto si riduce (possibile DoS o nessun effetto): il finding
reale va classificato in base all'esito effettivo in lab.

### Analisi Teorica

La deserializzazione insicura e un caso estremo di confusione tra dati e codice: l'applicazione tratta un
flusso di byte come la ricetta per ricostruire oggetti arbitrari, e la ricostruzione ha effetti collaterali
(i metodi magici). Una gadget chain e un percorso, attraverso classi gia presenti e legittime, che concatena
questi effetti collaterali fino all'esecuzione di comandi: l'attaccante non inietta codice, orchestra codice
esistente (simile nello spirito al ROP del binary exploitation). La contromisura teorica e non deserializzare
mai dati non fidati con meccanismi che permettono tipi arbitrari; dove inevitabile, usare allow-list dei tipi
e formati che trasportano solo dati (JSON) senza istruzioni.

## Remediation (Blue Team)

**Rilevamento (WAF/SIEM/EDR).**
- Input con marcatori di serializzazione (`rO0`/`0xACED` per Java, `gASV`/`\x80\x04` per pickle, `TypeError`
  in .NET BinaryFormatter) in cookie/parametri.
- Processi figli (`sh`, `cmd`, `powershell`) generati dal processo applicativo Java/web subito dopo la
  ricezione di un input serializzato.
- Callback di rete in uscita dal server verso destinazioni inattese.

**Hardening (secure coding).**
- Non deserializzare dati non fidati. Dove serve persistenza/trasporto, usare formati solo-dati (JSON) con
  schema, non la serializzazione nativa di oggetti.
- Se la deserializzazione nativa e inevitabile: allow-list rigida dei tipi consentiti (es.
  `ObjectInputFilter` in Java), firma/HMAC dei dati serializzati per garantirne l'integrita.
- Rimuovere dal classpath le librerie con gadget chain note se non necessarie; tenere aggiornate le
  dipendenze.
- Firmare e cifrare i cookie/ViewState (impedisce la manomissione del blob serializzato).

---

## Scenario Reale: Proiezione Post-Exploitation

> Vale per l'esito "RCE confermata" (severity Critico).

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** punto di deserializzazione individuato (es. cookie Java serializzato) e gadget chain
disponibile.

**Passo successivo immediato:** payload con comando marcatore per confermare l'RCE (OOB), poi reverse shell
per l'accesso interattivo.

**Kill Chain proiettata:**

```
Input serializzato controllato dall'attaccante
        |
        v
Gadget chain (ysoserial) -> esecuzione comando sul server (RCE)
        |
        v
Reverse shell -> accesso al contesto del processo applicativo
        |
        v
Enumerazione locale + privesc (modulo 04) -> movimento laterale
```

**Impatto potenziale:** RCE sul server applicativo, da cui l'intera catena di post-exploitation. Spesso il
processo gira con privilegi non banali (service account), accorciando la strada verso la compromissione del
sistema.

**Vettori di monetizzazione tipici:** ransomware/esfiltrazione a valle dell'RCE; uso del server come pivot
verso la rete interna.

### Prospettiva Difensore (Blue Team)

**Rilevamento:** marcatori di serializzazione in input; processi figli anomali dal processo applicativo;
callback in uscita.

**Indicatori di Compromissione (IOC):**
- Cookie/parametri con blob `rO0...`/`0xACED` manomessi.
- `java` (o il processo web) che genera `sh -c`/`cmd.exe` subito dopo una richiesta.
- Connessioni in uscita dal server applicativo verso IP esterni inattesi.

**Contenimento:** blocco del pattern via WAF; isolamento del server; analisi dei processi figli e delle
connessioni.

**Eradicazione e hardening:** eliminare la deserializzazione di dati non fidati; ObjectInputFilter/allow-list;
firma dei dati serializzati; aggiornamento dipendenze; rimozione gadget chain dal classpath.

**Lezione difensiva:** il problema non e "validare meglio" il blob serializzato, ma non deserializzare dati
non fidati come oggetti. La difesa efficace e architetturale (formati solo-dati, allow-list di tipi), non un
filtro a valle.

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `ysoserial` | Exploit generator | CLI - Attivo | Genera payload Java per gadget chain note (CommonsCollections, Spring, ...) |
| `ysoserial.net` | Exploit generator | CLI - Attivo | Equivalente per .NET (BinaryFormatter, Json.NET, ...) |
| `Burp Suite` | Proxy/scanner | Web - Attivo | Individua e modifica input serializzati; estensione "Java Deserialization Scanner" |
| `phpggc` | Exploit generator | CLI - Attivo | Gadget chain per PHP (unserialize) |

## Note di metodologia

In lab reale (es. un'app Java vulnerabile o un target dedicato) i dati da documentare come finding: il punto
di deserializzazione, il formato, la gadget chain funzionante e la conferma OOB dell'esecuzione. Valgono le
regole di integrita: output reali, mai fabbricati. In laboratorio il comando incapsulato resta un marcatore
non distruttivo per dimostrare l'RCE.

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Sfruttamento della deserializzazione insicura su un endpoint esposto. |
| Execution | Command and Scripting Interpreter | `T1059` | Esecuzione di comandi sul server tramite la gadget chain deserializzata. |

---

## Correlazioni con altri finding

| Provenienza | Questa tecnica | Effetto |
| :--- | :--- | :--- |
| [02-web-recon](../../02-web-recon (Enumeration)/README.md) | Deserializzazione | individua input serializzati (cookie/parametri con marcatori noti) |
| Deserializzazione (RCE) | [04-system-exploitation](../../../04-system-exploitation/README.md) | l'RCE apre a enumerazione locale e privilege escalation |
| Deserializzazione | [secure-coding-lab](../../06-secure-coding-lab (Defense)/README.md) | la remediation (no deserializzazione di dati non fidati) si collega al secure coding |

---

> **Nota:** Contenuto didattico e di metodologia. Le tecniche vanno eseguite esclusivamente su applicazioni di proprieta o con autorizzazione esplicita. I payload sono illustrativi e non provengono da sistemi reali o di terze parti.
