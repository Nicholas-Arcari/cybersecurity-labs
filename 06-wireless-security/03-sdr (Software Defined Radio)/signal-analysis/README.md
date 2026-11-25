> [English](README.en.md) | **Italiano**

# Signal analysis - cattura e demodulazione con SDR

> - **Fase:** Wireless Security - RF Reconnaissance & Signal Analysis (Software Defined Radio)
> - **Visibilita:** Zero - la ricezione SDR e completamente passiva; nessuna trasmissione, nessuna emissione rilevabile (ricezione pura dello spettro radio)
> - **Prerequisiti:** Ricevitore SDR (RTL-SDR 30 euro per sola ricezione, HackRF One per RX/TX); antenna adeguata alla banda target; GQRX/URH installati; conoscenza della banda del segnale target
> - **Output:** WIFI-008; identificazione e caratterizzazione di segnali RF (frequenza, modulazione, encoding); demodulazione di telemetrie in chiaro; base per gli attacchi replay (`../replay-attacks/`)

- **Ambiente Operativo:** Kali Linux (Attaccante), RTL-SDR v3 + HackRF One, dispositivi RF di laboratorio
- **Target:** Telecomando 433 MHz di test, sensore meteo wireless, telecomando garage di test
- **Tool principali:** GQRX, Universal Radio Hacker (URH), rtl_433

---

## Executive summary

La Software Defined Radio (SDR) sposta l'elaborazione del segnale radio dall'hardware dedicato al software: un ricevitore economico (RTL-SDR da 30 euro) cattura l'intero spettro RF e il software si occupa di demodulazione e decodifica. Questo apre alla sicurezza un dominio enorme e storicamente ignorato - telecomandi, sensori, sistemi di allarme, apricancelli, chiavi auto, dispositivi industriali - che opera nelle bande ISM (315, 433, 868, 915 MHz) spesso senza alcuna cifratura.

Questa sezione copre la fase di analisi: identificare un segnale nello spettro (GQRX), catturarlo e demodularlo per comprenderne la struttura (URH), e - dove il protocollo e noto - decodificarlo direttamente (rtl_433). E il prerequisito indispensabile agli attacchi attivi: prima di poter ripetere o falsificare un segnale (`../replay-attacks/`) bisogna capirne modulazione, encoding e struttura del payload.

Il finding WIFI-008 documenta la cattura in chiaro della telemetria di un sensore wireless: molti dispositivi trasmettono dati (temperatura, stato, identificativi) senza cifratura ne autenticazione, esponendo informazioni e permettendo la falsificazione. E la dimostrazione che l'assenza di cifratura al layer RF e la norma, non l'eccezione, nel mondo dei dispositivi embedded economici.

---

## Struttura della cartella

```
signal-analysis/
+-- README.md      # questo file: cattura, demodulazione e analisi segnali RF (WIFI-008)
+-- img/           # waterfall GQRX e analisi URH
```

---

## Identificazione del segnale con GQRX

**ID Finding:** `WIFI-008` | **Severity:** `Informativo` (telemetria RF in chiaro intercettata; abilita gli attacchi replay documentati separatamente)

### Contesto operativo

Il primo passo e localizzare il segnale nello spettro. GQRX fornisce una visualizzazione waterfall (frequenza sull'asse X, tempo sull'asse Y, intensita a colori) che rende visibile ogni trasmissione. Azionando il dispositivo target (premendo il telecomando) si osserva il "burst" comparire a una frequenza precisa, che diventa il punto di partenza per la cattura mirata.

### Esecuzione

```Bash
# Avvio GQRX con RTL-SDR, sintonizzato sulla banda ISM 433 MHz
gqrx
# Device: RTL-SDR, Center freq: 433.920 MHz, Sample rate: 2.4 Msps
# Azionare il telecomando -> osservare il burst nel waterfall
```

```
Waterfall @ 433.920 MHz:
  433.900   433.920   433.940
     |         |         |
     .    ####BURST####   .        <-- trasmissione OOK a ~433.92 MHz (telecomando)
     .         |         .
```

```Bash
# Decodifica automatica se il protocollo e noto (rtl_433 conosce 200+ device)
rtl_433 -f 433920000
```

```
time      : 2026-05-14 16:22:10
model     : Nexus-TH   House Code: 210   Channel: 1
Temperature: 21.5 C     Humidity: 48 %          <-- telemetria in chiaro (WIFI-008)
Integrity : CRC
```

rtl_433 riconosce e decodifica direttamente il sensore meteo: temperatura, umidita e house code sono trasmessi in chiaro, senza cifratura ne autenticazione.

---

## Analisi del protocollo con universal radio hacker (URH)

### Contesto operativo

Quando il protocollo non e noto a rtl_433, si passa a URH: cattura il segnale grezzo (IQ samples), lo demodula (ASK/OOK, FSK, PSK), e permette di analizzare la sequenza di bit per reverse-engineering del protocollo. URH e lo strumento che trasforma un burst radio in una sequenza di bit interpretabile.

### Esecuzione

```
URH Workflow:
[1] Record Signal -> cattura IQ del burst (RTL-SDR @ 433.92 MHz)
[2] Interpretation -> demodulazione:
       Modulation: ASK/OOK
       Bit length: 350 samples
       -> sequenza binaria: 1010 0011 1100 0101 ...
[3] Analysis -> individuazione della struttura:
       [Preambolo] [Device ID] [Comando] [CRC]
       AAAA         C5A3        01(open)   E7
[4] Generation -> sintesi di un nuovo segnale modificando il payload
```

La struttura rivelata (preambolo, device ID, comando, CRC) mostra un protocollo statico senza rolling code: lo stesso comando produce sempre la stessa sequenza, il che lo rende vulnerabile al replay (approfondito in `../replay-attacks/`).

### Remediation

- **Azione immediata:** trattare come pubbliche tutte le informazioni trasmesse via RF in chiaro; non affidarsi alla segretezza del protocollo (security by obscurity)
- **Azione strutturale:** per i dispositivi che trasmettono dati sensibili o comandi, adottare cifratura del payload e autenticazione; per i comandi (telecomandi, chiavi), implementare rolling code (KeeLoq, AES) che impedisce il replay; per la telemetria, se la riservatezza e richiesta, cifrare a livello applicativo
- **Verifica:** ricatturare il segnale dopo l'hardening e confermare che il payload sia cifrato e che comandi identici producano sequenze diverse (rolling code)

---

## Esperienza di laboratorio

La curva di apprendimento e stata prevalentemente sui concetti di elaborazione del segnale, non sugli strumenti. La prima difficolta e stata la scelta della sample rate e del gain in GQRX: un gain troppo alto saturava il ricevitore, uno troppo basso rendeva il segnale indistinguibile dal rumore. La regolazione empirica osservando il waterfall e stata piu efficace di qualsiasi valore teorico.

Il momento chiave e stato l'uso di rtl_433: la sua capacita di decodificare automaticamente 200+ protocolli commerciali ha reso banale l'intercettazione del sensore meteo. Questo ha ridimensionato la mia percezione della difficolta: molti dispositivi RF usano protocolli standard e ben documentati, e la loro decodifica non richiede reverse engineering ma solo lo strumento giusto. URH e servito solo per il telecomando garage, il cui protocollo custom ha richiesto la demodulazione manuale e l'analisi della struttura dei bit.

L'osservazione piu significativa e stata l'assenza sistematica di cifratura: ogni dispositivo di test trasmetteva in chiaro. Questo non e un caso isolato del laboratorio ma la norma per l'RF embedded economico, dove i vincoli di costo, consumo e semplicita hanno storicamente prevalso sulla sicurezza.

---

## Analisi teorica: perche l'RF embedded e storicamente insicuro

I dispositivi RF sub-GHz (315/433/868 MHz) sono nati in un'epoca e in un segmento di mercato in cui la sicurezza non era una preoccupazione: microcontrollori a basso costo e consumo, memoria minima, nessuna capacita crittografica. Il modello di minaccia implicito era la scarsa probabilita che qualcuno avesse l'attrezzatura per intercettare - un'assunzione demolita dall'avvento delle SDR economiche.

Tecnicamente, la maggior parte di questi dispositivi usa modulazioni semplici (OOK/ASK - On-Off Keying, o FSK) con encoding di linea elementari (Manchester, PWM) e payload statici. Non c'e nonce, non c'e timestamp, non c'e challenge-response: il ricevitore accetta qualsiasi segnale che corrisponda al pattern atteso. Questo li rende trasparenti all'analisi e vulnerabili al replay.

La distinzione critica e tra sistemi a codice fisso e sistemi a rolling code. Un codice fisso trasmette sempre la stessa sequenza per lo stesso comando (vulnerabile). Un rolling code (KeeLoq, usato nelle chiavi auto moderne) usa un contatore sincronizzato e cifrato: ogni trasmissione e diversa e valida una sola volta, neutralizzando il replay. La presenza o assenza di rolling code, rivelata dall'analisi URH (comandi identici producono sequenze identiche o diverse?), determina se il dispositivo e vulnerabile - il ponte diretto verso `../replay-attacks/`.

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `GQRX` | sdr receiver | gui | visualizzazione waterfall, identificazione frequenza dei segnali |
| `Universal Radio Hacker` | signal analyzer | gui | demodulazione, reverse engineering protocolli, generazione segnali |
| `rtl_433` | protocol decoder | cli | decodifica automatica di 200+ dispositivi ism commerciali |
| `SDR++` / `CubicSDR` | sdr receiver | gui | alternative moderne a gqrx per la visualizzazione dello spettro |
| `GNU Radio` | dsp framework | gui - flowgraph | elaborazione del segnale personalizzata (vedere `../gnu-radio-flowgraphs/`) |
| `inspectrum` | signal visualizer | gui | analisi visuale e misurazione di segnali catturati |

> **Tool moderno consigliato:** `Universal Radio Hacker` (URH) e il riferimento per l'analisi e il reverse engineering dei protocolli RF: integra cattura, demodulazione, analisi e generazione in un unico flusso. Il [Flipper Zero](https://github.com/Nicholas-Arcari/FlipperZero-guide) porta l'analisi e la cattura sub-GHz in un dispositivo tascabile, ideale per il recon RF sul campo.

---

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| reconnaissance | gather victim host information | `T1592` | identificazione e caratterizzazione di dispositivi rf tramite analisi dello spettro (WIFI-008) |
| credential access | network sniffing | `T1040` | cattura passiva e demodulazione di segnali rf e telemetria in chiaro (WIFI-008) |
| collection | data from information repositories | `T1213` | estrazione di dati di telemetria (temperatura, id, stato) trasmessi in chiaro |

---

> **Nota:** Tutte le attivita documentate sono state condotte in ricezione passiva su dispositivi RF di laboratorio di proprieta dell'autore. La ricezione e stata limitata a segnali di test in bande ISM. L'intercettazione di comunicazioni radio di terzi puo violare la normativa sulle comunicazioni elettroniche. Le trasmissioni (`../replay-attacks/`) richiedono attenzione ulteriore alle bande consentite. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
