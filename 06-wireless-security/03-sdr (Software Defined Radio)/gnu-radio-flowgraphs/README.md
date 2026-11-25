> [English](README.en.md) | **Italiano**

# GNU radio flowgraphs - elaborazione del segnale personalizzata

> - **Fase:** Wireless Security - Custom DSP & Signal Processing (Software Defined Radio)
> - **Visibilita:** Zero in ricezione; Media in trasmissione (dipende dal flowgraph)
> - **Prerequisiti:** GNU Radio Companion installato; SDR (RTL-SDR per RX, HackRF per RX/TX); comprensione dei concetti DSP di base (campionamento, filtri, demodulazione)
> - **Output:** Flowgraph riutilizzabili per demodulazione/modulazione custom di protocolli non supportati dai tool pronti all'uso

- **Ambiente Operativo:** Kali Linux (Attaccante), GNU Radio Companion, RTL-SDR/HackRF
- **Scopo:** Elaborazione di segnali quando URH e rtl_433 non bastano
- **Tool principali:** GNU Radio Companion (GRC), gr-osmosdr

---

## Executive summary

GNU Radio e il framework di elaborazione del segnale (DSP) di riferimento per la Software Defined Radio. Mentre GQRX visualizza, rtl_433 decodifica protocolli noti e URH gestisce i casi comuni di reverse engineering (vedere `../signal-analysis/`), GNU Radio interviene quando serve costruire una catena di elaborazione personalizzata: modulazioni non standard, protocolli complessi, decodifica in tempo reale, o l'integrazione di piu stadi (filtri, demodulatori, decodificatori) in un flusso su misura.

Questa sottocartella non documenta un finding specifico: e una cassetta degli attrezzi metodologica. GNU Radio Companion (GRC) permette di costruire visivamente i flowgraph collegando blocchi funzionali (sorgente SDR, filtri, demodulatori, sink) come uno schema a blocchi, generando il codice Python sottostante. E lo strumento a cui ricorrere quando l'analisi di un segnale (WIFI-008) supera le capacita dei tool pronti all'uso.

---

## Struttura della cartella

```
gnu-radio-flowgraphs/
+-- README.md      # questo file: metodologia flowgraph GNU Radio per DSP custom
+-- img/           # screenshot di flowgraph GRC
```

---

## Anatomia di un flowgraph di ricezione

### Contesto operativo

Un flowgraph di ricezione tipico per l'analisi di un segnale sub-GHz collega quattro stadi: acquisizione dal SDR, filtraggio del canale, demodulazione e output. Ogni blocco ha parametri configurabili (frequenza, sample rate, larghezza di banda del filtro) che si regolano in base al segnale target.

```
Flowgraph RX (schema concettuale):

[osmocom Source]      # acquisizione dall'SDR (RTL-SDR/HackRF)
  freq: 433.92M
  sample_rate: 2M
       |
       v
[Low Pass Filter]     # isola il canale, rimuove il rumore fuori banda
  cutoff: 100k
       |
       v
[Quadrature Demod]    # demodulazione FSK (o AM Demod per OOK/ASK)
       |
       v
[Binary Slicer]       # converte in sequenza di bit
       |
       v
[File Sink / Scope]   # output: bit stream o visualizzazione
```

### Esecuzione

```Bash
# Avvio di GNU Radio Companion (editor grafico dei flowgraph)
gnuradio-companion

# Il flowgraph .grc genera automaticamente uno script Python eseguibile:
python3 rx_433_fsk.py
```

Il flowgraph, una volta costruito e validato, e riutilizzabile e parametrizzabile: lo stesso schema serve per qualsiasi segnale FSK cambiando solo frequenza e sample rate. E questo il vantaggio rispetto ai tool monolitici: la catena di elaborazione e completamente sotto controllo e adattabile.

---

## Quando usare GNU radio invece di URH o rtl_433

### Analisi comparativa

La scelta dello strumento dipende dalla natura del segnale e dall'obiettivo:

- **rtl_433:** protocollo commerciale noto (200+ device supportati). Zero configurazione, decodifica immediata. Prima scelta sempre.
- **Universal Radio Hacker (URH):** protocollo sconosciuto ma con modulazione standard (OOK/FSK/PSK) e struttura relativamente semplice. Reverse engineering interattivo. Seconda scelta.
- **GNU Radio:** modulazione non standard, elaborazione multi-stadio, decodifica real-time, o necessita di integrare l'elaborazione in un sistema piu grande. Massima flessibilita, massima complessita. Ultima risorsa quando gli altri non bastano.

La progressione naturale in un assessment RF e quindi: tentare rtl_433, poi URH, e ricorrere a GNU Radio solo per i segnali che resistono a entrambi. GNU Radio richiede la comprensione dei fondamenti DSP (teorema del campionamento, aliasing, decimazione, tipi di demodulazione) che gli strumenti di piu alto livello nascondono.

---

## Esperienza di laboratorio

Nel percorso di laboratorio, GNU Radio e stato lo strumento meno utilizzato ma il piu formativo. Per i dispositivi di test (sensore meteo, telecomandi), rtl_433 e URH sono stati sufficienti e GNU Radio sarebbe stato un sovradimensionamento. La sua utilita e emersa nel comprendere cosa quei tool fanno "sotto il cofano": costruire manualmente un flowgraph di demodulazione ASK ha chiarito concetti (decimazione, filtraggio del canale, slicing dei bit) che URH esegue automaticamente ma nasconde.

La curva di apprendimento e ripida e legata ai fondamenti dell'elaborazione del segnale, non all'interfaccia. La lezione operativa e stata di priorita: in un assessment reale con tempo limitato, GNU Radio non e il primo strumento da aprire, ma la conoscenza dei suoi concetti e cio che permette di interpretare correttamente i risultati degli strumenti automatici e di affrontare i segnali che questi non gestiscono.

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `GNU Radio Companion` | dsp framework | gui - flowgraph | costruzione visuale di catene di elaborazione del segnale |
| `gr-osmosdr` | sdr source block | libreria | interfaccia gnu radio verso rtl-sdr, hackrf, altri sdr |
| `Universal Radio Hacker` | signal analyzer | gui | alternativa piu semplice per la maggior parte dei casi (vedere `../signal-analysis/`) |
| `Python + NumPy/SciPy` | dsp scripting | codice | elaborazione del segnale programmatica per casi custom |
| `inspectrum` | signal visualizer | gui | analisi visuale preliminare prima di costruire il flowgraph |

> **Tool moderno consigliato:** per la maggior parte degli assessment, `Universal Radio Hacker` copre i casi d'uso con una frazione della complessita di GNU Radio. Riservare GNU Radio ai segnali con modulazioni non standard o alla necessita di elaborazione in tempo reale. GNU Radio resta lo standard accademico e professionale per il DSP quando la flessibilita e prioritaria.

---

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| reconnaissance | gather victim host information | `T1592` | costruzione di catene dsp custom per demodulare e analizzare segnali rf non standard |
| credential access | network sniffing | `T1040` | elaborazione del segnale per estrarre dati da trasmissioni rf con protocolli custom |

---

> **Nota:** Questa sottocartella documenta metodologia e strumenti di elaborazione del segnale, senza finding specifici. Ogni attivita di cattura e trasmissione va condotta su dispositivi di proprieta in ambiente controllato e nel rispetto della normativa sulle bande radio. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
