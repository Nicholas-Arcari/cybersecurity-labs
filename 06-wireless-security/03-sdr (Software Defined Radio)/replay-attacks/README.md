> [English](README.en.md) | **Italiano**

# Replay Attacks - Cattura e Ritrasmissione di Segnali RF

> - **Fase:** Wireless Security - RF Replay & Signal Injection (Software Defined Radio)
> - **Visibilita:** Media - la cattura e passiva; la ritrasmissione emette un segnale RF sulla banda target, potenzialmente rilevabile da un ricevitore e - se su banda regolamentata - da autorita di controllo
> - **Prerequisiti:** SDR con capacita di trasmissione (HackRF One, non l'RTL-SDR che e solo RX; oppure [Flipper Zero](https://github.com/Nicholas-Arcari/FlipperZero-guide) per sub-GHz); analisi del segnale completata (`../signal-analysis/`, WIFI-008); assenza di rolling code confermata
> - **Output:** WIFI-009; azionamento non autorizzato di dispositivi controllati via RF (cancelli, telecomandi) tramite ritrasmissione del segnale catturato

- **Ambiente Operativo:** Kali Linux (Attaccante), HackRF One (RX/TX), Flipper Zero, dispositivi RF di laboratorio
- **Target:** Telecomando apricancello di test (433 MHz, codice fisso), telecomando garage di test
- **Tool principali:** hackrf_transfer, Universal Radio Hacker (URH), Flipper Zero

---

## Executive Summary

Il replay attack e l'attacco RF piu diretto e concettualmente semplice: si cattura il segnale trasmesso da un telecomando legittimo e lo si ritrasmette in un secondo momento per replicare l'azione originale. Non c'e reverse engineering necessario, non c'e crittografia da rompere: si registra e si riproduce, esattamente come un registratore audio.

Questa banalita e anche la sua pericolosita. Ogni dispositivo RF a codice fisso - una fetta enorme di apricancelli, telecomandi per garage, alcuni sistemi di allarme e citofoni economici - e vulnerabile. Il finding WIFI-009 documenta l'azionamento di un cancello di test tramite replay del segnale catturato: un attaccante non ha bisogno del telecomando fisico, gli basta essere stato nel raggio radio quando il proprietario lo ha usato una volta.

L'unica difesa efficace e il rolling code, che invalida ogni segnale dopo un singolo utilizzo. La sezione dimostra sia l'attacco (contro codice fisso) sia il motivo per cui il rolling code lo neutralizza, chiarendo la distinzione fondamentale che ogni valutatore di sicurezza fisica deve saper fare.

---

## Struttura della cartella

```
replay-attacks/
+-- README.md      # questo file: cattura e ritrasmissione RF, codice fisso vs rolling (WIFI-009)
+-- img/           # cattura URH e setup HackRF/Flipper Zero
```

---

## Replay Attack su Codice Fisso

**ID Finding:** `WIFI-009` | **Severity:** `Alto` (azionamento non autorizzato di dispositivo controllato via RF - accesso fisico a cancelli/garage)

### Contesto operativo

L'analisi precedente (`../signal-analysis/`, WIFI-008) ha confermato che il telecomando apricancello di test usa un codice fisso: azionamenti ripetuti producono sequenze identiche. Questo e il presupposto del replay. Con un HackRF (capace di trasmettere, a differenza dell'RTL-SDR) o un Flipper Zero, il segnale catturato viene ritrasmesso per replicare il comando "apri".

### PoC - Fase 1: Cattura del segnale grezzo

```Bash
# Cattura IQ del burst mentre si aziona il telecomando (HackRF, 433.92 MHz)
hackrf_transfer -r gate_capture.iq -f 433920000 -s 2000000 -g 40 -l 40
# Premere il telecomando durante la cattura, poi Ctrl+C
```

```
Stop with Ctrl-C
 4.2 MiB / 1.000 sec = 4.2 MiB/second
Exiting... (captured 8388608 samples)      <-- segnale registrato in gate_capture.iq
```

### PoC - Fase 2: Ritrasmissione (replay)

```Bash
# Ritrasmissione del segnale catturato sulla stessa frequenza
hackrf_transfer -t gate_capture.iq -f 433920000 -s 2000000 -x 40
```

```
 4.2 MiB / 1.000 sec = 4.2 MiB/second
Exiting...                                 <-- cancello azionato (WIFI-009)
```

Il cancello di test si e aperto: il segnale ritrasmesso e indistinguibile dall'originale perche e l'originale, campione per campione.

### PoC - Alternativa con Flipper Zero

```
Flipper Zero -> Sub-GHz -> Read (RAW)
   [cattura mentre si aziona il telecomando]
   -> Salva "gate_signal"
Flipper Zero -> Sub-GHz -> Saved -> gate_signal -> Send
   -> cancello azionato
```

Il Flipper Zero rende l'attacco portatile e immediato: cattura e replay in pochi tap, senza laptop ne configurazione, direttamente sul campo.

### Remediation

- **Azione immediata:** sostituire i telecomandi a codice fisso con dispositivi a rolling code; questa e l'unica contromisura realmente efficace contro il replay
- **Azione strutturale:** adottare sistemi con rolling code crittografico (KeeLoq, AES-128) per ogni controllo di accesso RF; dove possibile, affiancare un secondo fattore (tag RFID, PIN); per installazioni critiche, valutare sistemi con challenge-response bidirezionale invece della semplice trasmissione unidirezionale
- **Verifica:** catturare due azionamenti consecutivi e confrontarli - se sono identici, il sistema e a codice fisso e vulnerabile; un rolling code produce sequenze diverse a ogni pressione

---

## Perche il Rolling Code Neutralizza il Replay

### Contesto operativo

Ripetendo la cattura su un telecomando auto moderno (rolling code), il replay fallisce: il segnale ritrasmesso viene rifiutato dal ricevitore. Questo dimostra praticamente la differenza tra i due modelli.

```
Codice fisso (vulnerabile):
   Pressione 1 -> C5A3-01-E7
   Pressione 2 -> C5A3-01-E7        <-- identico, replay funziona

Rolling code (sicuro):
   Pressione 1 -> C5A3-[counter:1042]-cifrato-9F2A
   Pressione 2 -> C5A3-[counter:1043]-cifrato-3B71   <-- diverso, replay rifiutato
```

Il ricevitore mantiene un contatore sincronizzato e accetta solo valori successivi mai visti: un segnale gia usato (replay) ha un contatore obsoleto e viene scartato.

---

## Esperienza di Laboratorio

Il passaggio dall'RTL-SDR all'HackRF e stato la lezione hardware fondamentale: l'RTL-SDR, usato per tutta l'analisi precedente, riceve soltanto. Per il replay serve un dispositivo capace di trasmettere, e questo ha richiesto l'HackRF One (o, in alternativa portatile, il Flipper Zero). E un promemoria che nel dominio RF le capacita dell'hardware definiscono rigidamente cio che e possibile.

Il replay via `hackrf_transfer` del segnale IQ grezzo ha funzionato al primo tentativo sul telecomando a codice fisso, confermando quanto sia banale l'attacco: non ho dovuto capire il protocollo, solo registrare e riprodurre i campioni. Il contrasto con il tentativo sul telecomando rolling code e stato didatticamente perfetto: stesso identico procedimento, risultato nullo. Vedere il replay fallire ha reso tangibile il valore del rolling code molto piu di qualsiasi spiegazione teorica.

Un'attenzione pratica e legale importante emersa nell'esercizio: la trasmissione RF non e passiva come la ricezione. Trasmettere su bande regolamentate, anche a bassa potenza, puo interferire con servizi legittimi ed e soggetto a normativa. Tutte le trasmissioni di test sono state confinate a dispositivi di proprieta in ambiente controllato e a bassissima potenza.

---

## Analisi Teorica: Il Replay come Fallimento dell'Autenticazione Temporale

Il replay attack, in senso astratto, e il fallimento dell'autenticazione a garantire la "freschezza" (freshness) di un messaggio. Un sistema a codice fisso verifica solo che il messaggio sia valido (corrisponde al pattern atteso), ma non che sia recente o mai usato prima. Manca la dimensione temporale dell'autenticazione: qualsiasi copia di un messaggio valido e accettata, indipendentemente da quando e stata generata.

Questo e lo stesso principio che rende vulnerabili i sistemi digitali senza nonce o timestamp - dal replay di token di sessione al replay di pacchetti di autenticazione di rete. Il rolling code risolve il problema esattamente come i nonce nei protocolli di rete: introduce un valore che cambia a ogni messaggio (un contatore) e che il ricevitore verifica per unicita, rifiutando i valori gia visti.

L'implementazione KeeLoq combina il contatore con la cifratura: il contatore e cifrato con una chiave condivisa device-ricevitore, quindi un attaccante non puo semplicemente incrementarlo e ritrasmettere - non conosce la chiave per produrre il ciphertext corretto del contatore successivo. Esistono attacchi noti a KeeLoq (RollJam di Samy Kamkar, che intercetta e blocca il segnale per riutilizzarlo, e attacchi crittografici alla chiave), ma richiedono tecniche molto piu sofisticate del semplice replay, confermando che il rolling code alza drasticamente la barriera d'attacco.

---

## Scenario Reale: Proiezione Post-Exploitation

> Questa sezione descrive come questo finding si inserirebbe in un engagement reale, sia dal punto di vista dell'attaccante (Red Team) che del difensore (Blue Team).

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** capacita di azionare un dispositivo di accesso fisico controllato via RF a codice fisso (WIFI-009) - cancello, garage, sbarra.

**Passo successivo immediato:** ottenimento dell'accesso fisico all'area protetta senza forzatura, in modo silenzioso e ripetibile.

**Kill Chain proiettata:**

```
[WIFI-009] Replay del segnale -> apertura cancello/garage
        |
        v
Accesso fisico all'area perimetrale (parcheggio, cortile)
        |
        v
Accesso a punti di rete fisici / porte secondarie / social engineering (tailgating)
        |
        v
Drop di un implant o accesso a postazioni -> foothold interno
```

**Impatto potenziale:** il controllo di accessi fisici via RF non protetti annulla la sicurezza perimetrale fisica. Un attaccante che ha osservato il proprietario azionare il telecomando una sola volta (anche a distanza, con un'antenna direzionale) puo replicare l'accesso a piacimento. Il vettore collega la sicurezza RF alla sicurezza fisica e all'accesso alla rete interna, analogamente al badge cloning (`../../04-rfid-nfc (Physical Access)/`).

### Prospettiva Difensore (Blue Team)

**Rilevamento:** i sistemi RF economici non loggano ne rilevano i replay. Sistemi piu evoluti possono rilevare anomalie (azionamenti a orari inusuali, pattern di segnale duplicati con un ricevitore di monitoraggio).

**Indicatori di Compromissione (IOC):**
- Azionamenti del cancello/garage non correlati alla presenza del personale autorizzato
- Segnali RF duplicati identici rilevati da un monitor di spettro
- Presenza di dispositivi SDR/Flipper Zero rilevati in prossimita (ispezione fisica)

**Contenimento:** sostituzione immediata dei telecomandi a codice fisso; riprogrammazione dei ricevitori per accettare solo i nuovi dispositivi rolling code.

**Eradicazione e hardening:**
- Sistemi di accesso RF esclusivamente a rolling code crittografico
- Autenticazione a due fattori per gli accessi critici (RF + RFID/PIN)
- Monitoraggio dello spettro nelle installazioni ad alto valore
- Videosorveglianza sui punti di accesso per correlare azionamenti e presenze

**Lezione difensiva:** un sistema di controllo accessi deve garantire che ogni comando sia unico e non riproducibile. La comodita di un telecomando che "funziona sempre allo stesso modo" e esattamente la proprieta che lo rende vulnerabile: nella sicurezza, la ripetibilita di un'autenticazione e un difetto, non una caratteristica.

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `HackRF One` | SDR TX/RX | Hardware + CLI | Cattura e ritrasmissione RF full-duplex (1 MHz - 6 GHz) |
| `hackrf_transfer` | SDR utility | CLI | Cattura (`-r`) e replay (`-t`) di segnali IQ grezzi |
| `Universal Radio Hacker` | Signal analyzer | GUI | Cattura, analisi e generazione/ritrasmissione di segnali |
| `Flipper Zero` | Portable multi-tool | Hardware | Cattura e replay sub-GHz portatile (codice fisso) |
| `RTL-SDR` | SDR RX only | Hardware | Solo ricezione (analisi); non trasmette, non fa replay |
| `rpitx` / `PortaPack` | TX platform | Hardware | Piattaforme alternative di trasmissione RF |

> **Tool moderno consigliato:** l'`HackRF One` per il lavoro di laboratorio flessibile (RX+TX su banda amplissima) e il `Flipper Zero` per il replay sub-GHz sul campo. Attenzione: il Flipper Zero blocca di default la trasmissione su alcune bande regolamentate per conformita normativa.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Credential Access | Network Sniffing | `T1040` | Cattura del segnale RF del telecomando durante l'azionamento (WIFI-009) |
| Collection | Adversary-in-the-Middle | `T1557` | Intercettazione del segnale ai fini della successiva ritrasmissione |
| Initial Access | Hardware Additions | `T1200` | Utilizzo di hardware SDR/Flipper per replay e accesso fisico (WIFI-009) |
| Impact (ICS) | Manipulation of Control | `T0831` | Ritrasmissione del segnale per azionare un dispositivo fisico (cancello) senza autorizzazione |

---

> **Nota:** Tutte le attivita documentate sono state condotte su dispositivi RF di laboratorio di proprieta dell'autore, con trasmissioni a bassissima potenza in ambiente controllato. La trasmissione RF su bande regolamentate e soggetta a normativa e la ritrasmissione di segnali per azionare dispositivi di terzi costituisce reato. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
