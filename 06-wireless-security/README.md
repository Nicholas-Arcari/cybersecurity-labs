> [English](README.en.md) | **Italiano**

# 06 - Wireless Security

> - **Fase:** Wireless Security - Attacco alle tecnologie radio (WiFi, Bluetooth, SDR, RFID/NFC)
> - **Visibilita:** Variabile - da Zero (ricezione SDR passiva, cracking offline) ad Alta (deautenticazione, rogue AP, trasmissione RF)
> - **Prerequisiti:** Hardware radio dedicato (scheda WiFi monitor+injection, adattatore BLE, SDR RTL-SDR/HackRF, lettore RFID/Proxmark3); Kali Linux con la suite wireless; opzionale ma consigliato: [Flipper Zero](https://github.com/Nicholas-Arcari/FlipperZero-guide) come multi-tool portatile
> - **Output:** Finding WIFI-001..012; accesso a reti WiFi; controllo di dispositivi BLE; azionamento di dispositivi RF; cloni di badge di accesso fisico

---

## Introduzione

Il modulo `06-wireless-security` e dedicato a tutto cio che viaggia "nell'aria". A differenza dei moduli precedenti che operano su cavi, IP e server, qui il mezzo trasmissivo e l'etere e la superficie d'attacco si organizza per protocollo e frequenza radio. La caratteristica comune di tutti questi vettori e che bypassano il perimetro fisico e di rete tradizionale: un attaccante non ha bisogno di attraversare il firewall se puo entrare dalla rete WiFi, sbloccare una porta via BLE, aprire un cancello via RF o clonare un badge.

La struttura del modulo divide gli strumenti in base alla tecnologia radio che attaccano, coprendo l'intero spettro di interesse per un assessment wireless completo:

1. **WiFi 802.11 (WIFI-001..005):** la superficie piu ricca. Monitor mode e recon, cracking WPA2 (handshake e PMKID), Evil Twin con captive portal, automazione con Wifite2 e attacco WPS. L'obiettivo e l'accesso alla rete interna, oltre il perimetro.

2. **Bluetooth & BLE (WIFI-006..007):** il layer dell'IoT. Discovery ed enumerazione GATT, sfruttamento di caratteristiche non protette per manipolare dispositivi (serrature smart, wearable). Spesso trascurato ma critico con la proliferazione dei dispositivi connessi.

3. **SDR - Software Defined Radio (WIFI-008..009):** lo spettro RF sub-GHz. Analisi e demodulazione di segnali, replay attack su telecomandi a codice fisso (cancelli, garage). Con hardware da poche decine di euro si accede a un dominio storicamente privo di cifratura.

4. **RFID/NFC (WIFI-010..012):** il confine con la sicurezza fisica. Recupero chiavi e clonazione di badge di accesso (MIFARE Classic, EM4100), fino all'emulazione con Proxmark3. Comprometterli significa impersonare fisicamente il titolare.

Un filo conduttore trasversale, richiamato dagli appunti di laboratorio, e il Flipper Zero: un multi-tool tascabile che tocca WiFi (con dev board), sub-GHz, BLE e RFID/NFC, ideale per il recon e gli attacchi rapidi sul campo, complementare all'hardware specializzato usato in laboratorio.

Nella matrice MITRE ATT&CK, il modulo copre principalmente Reconnaissance (TA0043), Credential Access (TA0006), Initial Access (TA0001) e Collection (TA0009), con l'aggiunta di tecniche di sicurezza fisica (Hardware Additions) e, per i dispositivi IoT/OT, alcune tecniche ICS. Il modulo e il ponte tra la sicurezza logica dei moduli precedenti e la sicurezza fisica: i suoi finding aprono l'accesso che alimenta il modulo `07-post-exploitation`.

---

## Struttura della cartella

```
06-wireless-security/
+-- README.md                          <- questo file: registro finding + MITRE aggregata
|
+-- 01-wifi (802.11)/
|   +-- README.md                      <- registro WIFI-001..005, MITRE WiFi
|   +-- recon-monitor/                 <- WIFI-001 (monitor mode, de-anon SSID)
|   +-- cracking/                      <- WIFI-002 handshake WPA2, WIFI-003 PMKID
|   +-- rogue-ap/                      <- WIFI-004 (Evil Twin + captive portal - Critico)
|   +-- automated-attacks/             <- WIFI-005 (Wifite2 + WPS Pixie-Dust)
|
+-- 02-bluetooth-ble/
|   +-- README.md                      <- registro WIFI-006..007, MITRE BLE
|   +-- recon/                         <- WIFI-006 (discovery + enumerazione GATT)
|   +-- spoofing/                      <- WIFI-007 (GATT write non autorizzata)
|
+-- 03-sdr (Software Defined Radio)/
|   +-- README.md                      <- registro WIFI-008..009, MITRE SDR
|   +-- signal-analysis/               <- WIFI-008 (cattura, demodulazione, rtl_433/URH)
|   +-- replay-attacks/                <- WIFI-009 (replay RF su codice fisso)
|   +-- gnu-radio-flowgraphs/          <- DSP custom (nessun finding)
|
+-- 04-rfid-nfc (Physical Access)/
    +-- README.md                      <- registro WIFI-010..012, MITRE RFID/NFC
    +-- nfc-tools/                     <- WIFI-010 (key recovery MIFARE, dump)
    +-- mifare-cloning/                <- WIFI-011 (clonazione su tag magic)
    +-- proxmark3-client/              <- WIFI-012 (LF/HF, emulazione)
```

---

## Flusso operativo consigliato

```
[INPUT] Hardware radio (WiFi monitor, BLE, SDR, RFID), target nel raggio
         |
         v
[1] WiFi 802.11 (01-wifi/)
     +-- monitor mode -> cracking WPA2 / Evil Twin / WPS
     -> accesso alla rete interna (WIFI-001..005)
         |
         v
[2] Bluetooth & BLE (02-bluetooth-ble/)
     +-- enumerazione GATT -> manipolazione dispositivi IoT
     -> controllo serrature/wearable non protetti (WIFI-006..007)
         |
         v
[3] SDR (03-sdr/)
     +-- analisi segnale -> replay su codice fisso
     -> azionamento cancelli/telecomandi (WIFI-008..009)
         |
         v
[4] RFID/NFC (04-rfid-nfc/)
     +-- key recovery -> clonazione/emulazione badge
     -> accesso fisico impersonando il titolare (WIFI-010..012)
         |
         v
[OUTPUT] Accesso (rete / fisico / dispositivi)
     -> 07-post-exploitation (lateral movement, persistence)
     -> 05-social-engineering (prossimita per skimming, credential reuse)
```

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `aircrack-ng suite` | WiFi attack suite | CLI | Monitor mode, handshake, deauth, cracking WPA2 |
| `hashcat` + `hcxdumptool` | WiFi cracking | CLI | Cracking clientless PMKID/handshake (modalita 22000) |
| `Wifite2` / `Airgeddon` | WiFi automation | CLI | Audit wireless automatizzato + WPS |
| `bettercap` | BLE/MITM framework | CLI | Recon ed enumerazione GATT, manipolazione BLE |
| `HackRF One` / `RTL-SDR` | SDR | Hardware | Cattura e replay di segnali RF sub-GHz |
| `Universal Radio Hacker` | Signal analyzer | GUI | Demodulazione e reverse engineering RF |
| `Proxmark3 RDV4` | RFID multi-tool | Hardware | Clonazione RFID LF/HF, sniffing, emulazione |
| `Flipper Zero` | Portable multi-tool | Hardware | Sub-GHz, BLE, RFID/NFC in un dispositivo tascabile |

> **Tool moderno consigliato:** la combinazione `hcxdumptool` + `hashcat -m 22000` per il WiFi, `bettercap` per il BLE, `Universal Radio Hacker` + `HackRF` per l'RF, `Proxmark3 RDV4` (Iceman) per l'RFID. Il `Flipper Zero` come multi-tool trasversale per il recon e gli attacchi rapidi sul campo.

---

## Registro Finding - Modulo 06

| ID | Descrizione | Severity | Sottocartella |
| :--- | :--- | :---: | :--- |
| `WIFI-001` | Monitor mode + de-anonimizzazione SSID nascosto e client via Probe Request | `Basso` | `01-wifi/recon-monitor/` |
| `WIFI-002` | WPA2 4-way handshake catturato e PSK recuperata via attacco a dizionario | `Alto` | `01-wifi/cracking/` |
| `WIFI-003` | PMKID clientless catturato e PSK recuperata senza client connessi | `Alto` | `01-wifi/cracking/` |
| `WIFI-004` | Evil Twin con captive portal: credential harvesting + posizione MITM | `Critico` | `01-wifi/rogue-ap/` |
| `WIFI-005` | WPS Pixie-Dust: PIN WPS recuperato in secondi, PSK compromessa a prescindere dalla robustezza | `Alto` | `01-wifi/automated-attacks/` |
| `WIFI-006` | Enumerazione GATT: caratteristica di controllo scrivibile senza autenticazione su device IoT | `Informativo` | `02-bluetooth-ble/recon/` |
| `WIFI-007` | GATT write non autorizzata: manipolazione dello stato di una serratura smart di test | `Medio` | `02-bluetooth-ble/spoofing/` |
| `WIFI-008` | Telemetria RF in chiaro intercettata; segnale caratterizzato e payload rivelato | `Informativo` | `03-sdr/signal-analysis/` |
| `WIFI-009` | Replay attack su telecomando a codice fisso: azionamento non autorizzato di un cancello di test | `Alto` | `03-sdr/replay-attacks/` |
| `WIFI-010` | Recupero chiavi e dump di un badge MIFARE Classic con chiavi di default (nested mfoc) | `Medio` | `04-rfid-nfc/nfc-tools/` |
| `WIFI-011` | Clonazione completa del badge MIFARE su tag magic, incluso l'UID - clone funzionante | `Alto` | `04-rfid-nfc/mifare-cloning/` |
| `WIFI-012` | Lettura e clonazione di badge Low Frequency EM4100 (nessuna autenticazione) via Proxmark3 | `Alto` | `04-rfid-nfc/proxmark3-client/` |

---

## Mappatura MITRE ATT&CK - Aggregata

| Tattica | Tecnica | ID MITRE | Finding Correlato |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Active Scanning | `T1595` | WIFI-001, WIFI-006 |
| Reconnaissance | Gather Victim Network Information | `T1590` | WIFI-001 |
| Reconnaissance | Gather Victim Host Information | `T1592` | WIFI-006, WIFI-008, WIFI-010, WIFI-012 |
| Credential Access | Network Sniffing | `T1040` | WIFI-001, WIFI-002, WIFI-003, WIFI-006, WIFI-008, WIFI-009, WIFI-012 |
| Credential Access | Brute Force: Password Cracking | `T1110.002` | WIFI-002, WIFI-003 |
| Credential Access | Brute Force | `T1110` | WIFI-005, WIFI-010 |
| Credential Access | Adversary-in-the-Middle: Evil Twin | `T1557.004` | WIFI-004 |
| Credential Access | Steal Application Access Token | `T1528` | WIFI-010 |
| Collection | Adversary-in-the-Middle | `T1557` | WIFI-004, WIFI-007, WIFI-009 |
| Collection | Data from Information Repositories | `T1213` | WIFI-008 |
| Credential Access | Input Capture: Web Portal Capture | `T1056.003` | WIFI-004 |
| Resource Development | Develop Capabilities | `T1587` | WIFI-011 |
| Defense Evasion | Impersonation | `T1656` | WIFI-007, WIFI-011, WIFI-012 |
| Impact (ICS) | Manipulation of Control | `T0831` | WIFI-007, WIFI-009 |
| Initial Access | Hardware Additions | `T1200` | WIFI-004, WIFI-009, WIFI-010, WIFI-011, WIFI-012 |
| Initial Access | Valid Accounts | `T1078` | WIFI-002, WIFI-003, WIFI-004, WIFI-005 |
| Initial Access | Valid Accounts: Local Accounts | `T1078.003` | WIFI-011, WIFI-012 |

---

> **Nota:** Tutte le attivita documentate in questo modulo sono state condotte su reti, dispositivi e token radio di laboratorio di proprieta dell'autore, in ambiente controllato e isolato. Nessun attacco e stato diretto contro reti, dispositivi o badge di terzi. L'intercettazione di comunicazioni radio, l'accesso non autorizzato a reti wireless, la manipolazione di dispositivi e la clonazione di badge di accesso costituiscono reati ai sensi della normativa vigente. Le trasmissioni RF sono soggette a regolamentazione delle bande. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato con perimetro esplicitamente definito.
