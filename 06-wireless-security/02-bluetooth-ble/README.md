> [English](README.en.md) | **Italiano**

# 02 - Bluetooth & BLE

> - **Fase:** Wireless Security - Attacco a Bluetooth Classic e Bluetooth Low Energy
> - **Visibilita:** Bassa - discovery ed enumerazione passivi/poco appariscenti; la scrittura GATT e una connessione client apparentemente legittima
> - **Prerequisiti:** Adattatore Bluetooth 4.2+ (integrato o dongle CSR/Broadcom); stack BlueZ; per lo sniffing avanzato: nRF52840 o Ubertooth One
> - **Output:** Finding WIFI-006..007; inventario device BLE e mappa GATT; manipolazione dello stato di dispositivi IoT non protetti

---

## Introduzione

La sezione `02-bluetooth-ble` copre un layer spesso trascurato negli assessment ma sempre piu critico: con la proliferazione dell'IoT, il Bluetooth Low Energy (BLE) e il protocollo di controllo di serrature smart, wearable, dispositivi medici e sistemi di building automation. A differenza dell'802.11, dove il target e la rete, qui il target e il singolo dispositivo e i servizi che espone.

La sezione si articola in due fasi complementari:

1. **Recon (WIFI-006):** discovery dei device BLE tramite gli advertising packet ed enumerazione della struttura GATT (servizi, caratteristiche, permessi). L'enumerazione rivela immediatamente il modello di sicurezza del produttore: quali caratteristiche sono protette e quali sono esposte senza autenticazione.

2. **Spoofing (WIFI-007):** sfruttamento delle caratteristiche non protette identificate nel recon. GATT write non autorizzata per manipolare lo stato del device (nel test, sblocco di una serratura smart) e device impersonation per sostituirsi a un dispositivo fidato.

Il filo conduttore della sezione e un principio di sicurezza IoT: molti dispositivi delegano interamente la sicurezza all'applicazione mobile, lasciando il layer di trasporto BLE completamente aperto. Poiche chiunque nel raggio radio puo connettersi al layer BLE, questa delega e un errore strutturale che l'enumerazione GATT rende immediatamente visibile e lo spoofing sfrutta.

---

## Struttura della cartella

```
02-bluetooth-ble/
+-- README.md      # questo file: registro WIFI-006..007 + MITRE aggregata
|
+-- recon/         # WIFI-006: discovery BLE + enumerazione GATT (bettercap, gatttool)
+-- spoofing/      # WIFI-007: GATT write non autorizzata + impersonation (bettercap, spooftooph)
```

---

## Flusso operativo consigliato

```
[INPUT] Adattatore BLE, dispositivi IoT nel raggio radio
         |
         v
[1] Discovery (recon/)
     +-- bettercap ble.recon -> lista device (MAC, nome, vendor, RSSI)
              |
              v
[2] Enumerazione GATT (recon/)
     +-- bettercap ble.enum <MAC> -> servizi, caratteristiche, permessi (WIFI-006)
     -> identificazione caratteristiche WRITE senza autenticazione
              |
              v
[3] Manipolazione (spoofing/)
     +-- ble.write <MAC> <char> <value> -> comando non autorizzato (WIFI-007)
     +-- oppure spooftooph -> device impersonation
              |
              v
[OUTPUT] Controllo del device -> accesso fisico / injection dati
     -> collegamento con 04-rfid-nfc (sicurezza fisica) e 07-post-exploitation
```

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `bettercap` | mitm framework | cli | il riferimento ble: `ble.recon`, `ble.enum`, `ble.write` |
| `gatttool` | gatt client | cli | lettura/scrittura diretta di caratteristiche (legacy ma preciso) |
| `bluetoothctl` | bluez cli | cli | discovery, pairing e gestione device |
| `spooftooph` | bt address spoofer | cli | clonazione indirizzo bluetooth per impersonation |
| `btlejack` | ble hijacker | cli | hijacking di connessioni ble attive (hardware micro:bit) |
| `nRF Connect` | ble explorer | gui / mobile | esplorazione gatt interattiva |

> **Tool moderno consigliato:** `bettercap` e il riferimento indiscusso per il recon e la manipolazione BLE (sostituisce gatttool/hcitool deprecati). Per lo sniffing del pairing serve hardware dedicato (`nRF52840`, `Ubertooth One`); il [Flipper Zero](https://github.com/Nicholas-Arcari/FlipperZero-guide) copre scenari di recon/replay portatili.

---

## Registro finding - sezione bluetooth & BLE

| id | descrizione | severity | sottocartella |
| :--- | :--- | :---: | :--- |
| `WIFI-006` | enumerazione gatt: caratteristica di controllo scrivibile senza autenticazione su device iot | `Informativo` | `recon/` |
| `WIFI-007` | gatt write non autorizzata: manipolazione dello stato di una serratura smart di test | `Medio` | `spoofing/` |

---

## Mappatura MITRE ATT&CK - aggregata

| tattica | tecnica | id mitre | finding correlato |
| :--- | :--- | :--- | :--- |
| reconnaissance | active scanning | `T1595` | WIFI-006 |
| reconnaissance | gather victim host information | `T1592` | WIFI-006 |
| credential access | network sniffing | `T1040` | WIFI-006 |
| collection | adversary-in-the-middle | `T1557` | WIFI-007 |
| defense evasion | impersonation | `T1656` | WIFI-007 |
| impact (ics) | manipulation of control | `T0831` | WIFI-007 |
| initial access | hardware additions | `T1200` | WIFI-007 |

---

> **Nota:** Tutte le attivita documentate in questa sezione sono state condotte su dispositivi Bluetooth/BLE di laboratorio di proprieta dell'autore. Nessun attacco e stato diretto contro device di terzi. La manipolazione non autorizzata di dispositivi Bluetooth costituisce reato. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
