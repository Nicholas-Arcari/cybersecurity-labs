> [English](README.en.md) | **Italiano**

# 03 - SDR (Software Defined Radio)

> - **Fase:** Wireless Security - Attacco allo spettro RF tramite Software Defined Radio
> - **Visibilita:** Zero in ricezione (passiva pura); Media in trasmissione (replay, injection)
> - **Prerequisiti:** Ricevitore SDR (RTL-SDR ~30 euro per RX; HackRF One per RX/TX); antenna adeguata alla banda; GQRX, URH, GNU Radio; per il campo: [Flipper Zero](https://github.com/Nicholas-Arcari/FlipperZero-guide)
> - **Output:** Finding WIFI-008..009; segnali RF caratterizzati e demodulati; telemetria in chiaro intercettata; azionamento di dispositivi via replay

---

## Introduzione

La sezione `03-sdr` e la piu avanzata del modulo wireless e apre un dominio storicamente ignorato dalla sicurezza: lo spettro RF sub-GHz. Con un ricevitore economico (RTL-SDR da 30 euro) o un trasmettitore come l'HackRF One, diventa accessibile un intero mondo di dispositivi - apricancelli, telecomandi auto, sensori, allarmi, stazioni meteo, dispositivi industriali - che operano nelle bande ISM (315, 433, 868, 915 MHz) quasi sempre senza cifratura.

Come indicato negli appunti di laboratorio, questa e la sezione dove si conservano e analizzano i segnali radio catturati (apricancelli, telecomandi auto, stazioni meteo), con un collegamento naturale al Flipper Zero come strumento di cattura e replay portatile.

La sezione si articola in tre fasi:

1. **Signal Analysis (WIFI-008):** identificazione del segnale nello spettro (GQRX), cattura e demodulazione, decodifica automatica dei protocolli noti (rtl_433) o reverse engineering di quelli custom (URH). E il prerequisito di ogni attacco attivo.

2. **Replay Attacks (WIFI-009):** cattura e ritrasmissione del segnale per replicare un'azione (aprire un cancello). Efficace contro i sistemi a codice fisso, neutralizzato dal rolling code. Richiede un SDR capace di trasmettere (HackRF, Flipper Zero).

3. **GNU Radio Flowgraphs (nessun finding):** cassetta degli attrezzi per l'elaborazione del segnale personalizzata, quando i tool pronti all'uso non bastano.

Il principio conduttore e che l'assenza di cifratura al layer RF e la norma nel mondo embedded economico, dovuta a vincoli storici di costo e consumo. La distinzione critica che questa sezione insegna e tra codice fisso (vulnerabile al replay) e rolling code (protetto).

---

## Struttura della cartella

```
03-sdr (Software Defined Radio)/
+-- README.md                # questo file: registro WIFI-008..009 + MITRE aggregata
|
+-- signal-analysis/         # WIFI-008: cattura, demodulazione, decodifica (GQRX, URH, rtl_433)
+-- replay-attacks/          # WIFI-009: cattura e ritrasmissione RF (HackRF, Flipper Zero)
+-- gnu-radio-flowgraphs/    # DSP custom, nessun finding (GNU Radio Companion)
```

---

## Flusso operativo consigliato

```
[INPUT] SDR (RTL-SDR/HackRF), dispositivo RF target nel raggio
         |
         v
[1] Identificazione del segnale (signal-analysis/)
     +-- GQRX -> waterfall, individuazione della frequenza
     +-- rtl_433 -> decodifica se protocollo noto (WIFI-008)
              |
              v
[2] Analisi del protocollo (signal-analysis/)
     +-- URH -> demodulazione, struttura del payload
     +-- GNU Radio -> se modulazione non standard (gnu-radio-flowgraphs/)
     -> codice fisso o rolling code?
              |
              +-- rolling code -> replay inefficace, stop
              |
              +-- codice fisso -> prosegui
              v
[3] Replay (replay-attacks/) [richiede HackRF/Flipper]
     +-- hackrf_transfer -r (cattura) -> -t (replay)
     -> azionamento del dispositivo (WIFI-009)
              |
              v
[OUTPUT] Controllo del dispositivo RF -> accesso fisico
     -> collegamento con 04-rfid-nfc e sicurezza fisica
```

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `RTL-SDR` | SDR RX only | Hardware | Ricezione economica per analisi (non trasmette) |
| `HackRF One` | SDR TX/RX | Hardware | Cattura e ritrasmissione full-duplex (1 MHz - 6 GHz) |
| `GQRX` | SDR receiver | GUI | Visualizzazione waterfall, identificazione frequenze |
| `Universal Radio Hacker` | Signal analyzer | GUI | Demodulazione e reverse engineering protocolli |
| `rtl_433` | Protocol decoder | CLI | Decodifica automatica di 200+ dispositivi ISM |
| `GNU Radio` | DSP framework | GUI - Flowgraph | Elaborazione del segnale personalizzata |
| `Flipper Zero` | Portable multi-tool | Hardware | Cattura e replay sub-GHz portatile sul campo |

> **Tool moderno consigliato:** `Universal Radio Hacker` per l'analisi (cattura+demod+generazione in un flusso), `HackRF One` per la flessibilita RX/TX in laboratorio, `Flipper Zero` per il recon e replay sub-GHz sul campo. Attenzione alla normativa sulle trasmissioni.

---

## Registro Finding - Sezione SDR

| ID | Descrizione | Severity | Sottocartella |
| :--- | :--- | :---: | :--- |
| `WIFI-008` | Telemetria RF in chiaro intercettata; segnale caratterizzato e struttura del payload rivelata | `Informativo` | `signal-analysis/` |
| `WIFI-009` | Replay attack su telecomando a codice fisso: azionamento non autorizzato di un cancello di test | `Alto` | `replay-attacks/` |

---

## Mappatura MITRE ATT&CK - Aggregata

| Tattica | Tecnica | ID MITRE | Finding Correlato |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Host Information | `T1592` | WIFI-008 |
| Credential Access | Network Sniffing | `T1040` | WIFI-008, WIFI-009 |
| Collection | Data from Information Repositories | `T1213` | WIFI-008 |
| Collection | Adversary-in-the-Middle | `T1557` | WIFI-009 |
| Initial Access | Hardware Additions | `T1200` | WIFI-009 |
| Impact (ICS) | Manipulation of Control | `T0831` | WIFI-009 |

---

> **Nota:** Tutte le attivita documentate in questa sezione sono state condotte su dispositivi RF di laboratorio di proprieta dell'autore. La ricezione e stata limitata a segnali di test; le trasmissioni (replay) sono state confinate a bassissima potenza in ambiente controllato. La trasmissione su bande regolamentate e soggetta a normativa e l'intercettazione o la manipolazione di dispositivi di terzi costituisce reato. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
