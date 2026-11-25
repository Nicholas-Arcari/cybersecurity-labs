> [English](README.en.md) | **Italiano**

# Bluetooth & BLE recon - discovery ed enumerazione GATT

> - **Fase:** Wireless Security - Reconnaissance (Bluetooth Classic & Bluetooth Low Energy)
> - **Visibilita:** Bassa - lo scanning BLE e passivo (ascolto degli advertising packet); l'enumerazione dei servizi GATT richiede una connessione al device (Attiva ma poco appariscente, tipica del comportamento di un client legittimo)
> - **Prerequisiti:** Adattatore Bluetooth compatibile (integrato o dongle CSR/Broadcom); BlueZ stack installato; per lo sniffing avanzato: dongle nRF52840 o Ubertooth One
> - **Output:** WIFI-006; inventario dei device Bluetooth/BLE nel raggio d'azione (MAC, nome, RSSI, servizi); mappa dei servizi e caratteristiche GATT esposti; identificazione di caratteristiche scrivibili senza autenticazione

- **Ambiente Operativo:** Kali Linux (Attaccante), dongle Bluetooth 5.0, dispositivi IoT/BLE di laboratorio (smart lock, fitness tracker di test)
- **Target:** Dispositivi BLE di test (serratura smart, sensore ambientale)
- **Tool principali:** bluetoothctl, bettercap, gatttool, bluehydra

---

## Executive summary

Il Bluetooth e spesso il layer piu trascurato di un assessment, ma e diventato critico con la proliferazione dell'IoT: serrature smart, dispositivi medici, wearable, sistemi di building automation comunicano quasi tutti via Bluetooth Low Energy (BLE). A differenza dell'802.11, dove l'obiettivo e la rete, qui l'obiettivo e il singolo device e i servizi che espone.

La ricognizione BLE si articola in due livelli. Il primo, la discovery, cattura passivamente gli advertising packet che ogni device BLE trasmette per annunciarsi, ricavandone MAC, nome e servizi pubblicizzati. Il secondo, l'enumerazione GATT (Generic Attribute Profile), stabilisce una connessione al device e ne mappa la struttura interna: servizi, caratteristiche, e - dato piu critico - i permessi di ogni caratteristica (lettura, scrittura, notifica) e se richiedono autenticazione.

Il finding WIFI-006 documenta la scoperta di caratteristiche GATT scrivibili senza autenticazione su un dispositivo di test: la premessa tecnica dell'attacco di spoofing/manipolazione documentato nella sezione `../spoofing/`. Molti dispositivi BLE economici delegano interamente la sicurezza all'applicazione mobile, lasciando il layer GATT completamente aperto.

---

## Struttura della cartella

```
recon/
+-- README.md      # questo file: discovery BLE + enumerazione GATT (WIFI-006)
+-- img/           # screenshot bettercap ble.recon e mappa GATT
```

---

## Discovery dei dispositivi

**ID Finding:** `WIFI-006` | **Severity:** `Informativo` (mappatura superficie d'attacco BLE; diventa `Medio` se emergono caratteristiche scrivibili senza autenticazione)

### Contesto operativo

Ogni dispositivo BLE in modalita "connectable" trasmette advertising packet a intervalli regolari sui tre canali di advertising (37, 38, 39). Questi pacchetti sono in chiaro e contengono l'indirizzo del device, il nome e i servizi pubblicizzati. La discovery e completamente passiva.

### Esecuzione

```Bash
# Discovery Bluetooth Classic + BLE con bluetoothctl
sudo bluetoothctl
[bluetooth]# scan on
```

```
[NEW] Device 4C:65:A8:DB:11:22 SmartLock-A8DB          <-- serratura smart (target)
[NEW] Device 60:AB:D2:5F:33:44 Mi Band 6
[NEW] Device C8:2B:96:1A:55:66 EnvSensor-1A55
```

```Bash
# Discovery BLE avanzata con bettercap (RSSI, vendor, servizi)
sudo bettercap
> ble.recon on
> ble.show
```

```
 RSSI │ MAC               │ Vendor         │ Flags       │ Connectable │ Name
 -42  │ 4c:65:a8:db:11:22 │ Espressif      │ BR/EDR, LE  │      yes     │ SmartLock-A8DB
 -67  │ 60:ab:d2:5f:33:44 │ Xiaomi         │ LE only     │      yes     │ Mi Band 6
```

### Esecuzione - enumerazione dei servizi GATT

```Bash
# Enumerazione completa dei servizi e caratteristiche del target
> ble.enum 4c:65:a8:db:11:22
```

```
 Handles    │ Service > Characteristics                    │ Properties
 0001-0009  │ Generic Access (1800)
   0003     │   Device Name (2a00)                          │ READ
 000a-0012  │ Device Information (180a)
   000c     │   Manufacturer Name (2a29)                    │ READ
 0013-001f  │ Custom Service (ffe0)
   0015     │   Lock Control (ffe1)                         │ READ, WRITE    <-- scrivibile, no auth (WIFI-006)
   0018     │   Lock Status (ffe2)                          │ READ, NOTIFY
```

La riga critica: la caratteristica `Lock Control (ffe1)` espone la proprieta `WRITE` senza alcun flag di autenticazione o cifratura. Un attaccante puo scrivere direttamente su questo handle, potenzialmente comandando la serratura (approfondito in `../spoofing/`).

### Verifica della scrittura (proof of concept read)

```Bash
# Lettura del valore corrente della caratteristica con gatttool
gatttool -b 4C:65:A8:DB:11:22 --char-read -a 0x0015
```

```
Characteristic value/descriptor: 00        <-- stato "unlocked=0", scrivibile senza pairing
```

### Remediation

- **Azione immediata:** verificare che le caratteristiche GATT che comandano funzioni sensibili (lock/unlock, configurazione) richiedano autenticazione (flag `Authenticated Signed Writes` o pairing con protezione MITM)
- **Azione strutturale:** implementare BLE Secure Connections (LE Secure Connections, introdotto in Bluetooth 4.2) con pairing basato su ECDH; applicare autorizzazione a livello applicativo su ogni scrittura sensibile (challenge-response), non affidarsi alla sola sicurezza del layer di trasporto; ridurre la potenza di trasmissione per limitare il raggio d'attacco
- **Verifica:** ripetere `ble.enum` e confermare che le caratteristiche sensibili mostrino requisiti di autenticazione; test di scrittura non autorizzata deve fallire

---

## Esperienza di laboratorio

L'ostacolo iniziale e stato hardware: l'adattatore Bluetooth integrato del laptop supportava la discovery ma non lo sniffing passivo del traffico tra due device gia accoppiati. Per la discovery e l'enumerazione GATT (connessione diretta al device) l'adattatore integrato e stato sufficiente; per lo sniffing del pairing tra app e device sarebbe stato necessario un nRF52840 o un Ubertooth One con firmware dedicato.

Il risultato piu interessante e emerso dall'enumerazione GATT del dispositivo di test: la struttura dei servizi rivela immediatamente la filosofia di sicurezza del produttore. Il device esponeva una caratteristica `Lock Control` scrivibile senza pairing, delegando ogni controllo di accesso all'app mobile. Questo pattern - sicurezza nell'app, layer BLE aperto - e estremamente comune nei dispositivi IoT economici e trasforma l'enumerazione GATT da semplice recon a scoperta di una vulnerabilita sfruttabile.

---

## Analisi teorica: il modello GATT e i suoi punti deboli

Il BLE organizza i dati secondo il Generic Attribute Profile (GATT): il device (server GATT) espone Servizi, ciascuno contenente Caratteristiche, ciascuna con un valore e un set di proprieta (Read, Write, Notify, Indicate) e permessi di sicurezza. Il client (tipicamente l'app mobile) legge, scrive o si sottoscrive alle notifiche.

Il modello di sicurezza BLE opera su tre livelli: il pairing (scambio di chiavi), il bonding (memorizzazione delle chiavi per connessioni future) e la cifratura del link. Il punto debole strutturale e che questi controlli sono opzionali e configurabili per singola caratteristica: un produttore puo esporre una caratteristica critica con permesso di scrittura ma senza richiedere ne pairing ne cifratura. In quel caso, chiunque nel raggio radio puo scrivervi.

Le versioni BLE pre-4.2 usavano inoltre il metodo di pairing "Legacy" con la modalita "Just Works", vulnerabile a intercettazione e MITM durante lo scambio delle chiavi. LE Secure Connections (4.2+) introduce ECDH (curva P-256) che protegge lo scambio, ma la sua adozione dipende dall'implementazione. In pratica, la sicurezza reale di un dispositivo BLE dipende meno dalla versione dello standard e piu dalle scelte del produttore su quali caratteristiche proteggere - un fatto che l'enumerazione GATT rende immediatamente visibile.

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `bluetoothctl` | bluez cli | cli | discovery, pairing e gestione device via stack bluez |
| `bettercap` | mitm framework | cli | modulo `ble.recon`/`ble.enum`: discovery ed enumerazione gatt (il riferimento ble) |
| `gatttool` | gatt client | cli | lettura/scrittura diretta di caratteristiche gatt (deprecato ma utile) |
| `bluehydra` | bt discovery | cli | discovery continua bluetooth classic + ble con database |
| `hcitool` / `hciconfig` | bluez legacy | cli | gestione a basso livello dell'interfaccia hci (legacy) |
| `nRF Connect` | ble explorer | gui / mobile | esplorazione gatt interattiva (desktop e mobile, nordic) |

> **Tool moderno consigliato:** `bettercap` e il riferimento moderno per il BLE recon (i moduli `ble.recon`, `ble.enum`, `ble.write` sostituiscono gatttool e hcitool, deprecati). Per lo sniffing del traffico e del pairing, un dongle `nRF52840` con firmware Sniffer o `Ubertooth One`. Il [Flipper Zero](https://github.com/Nicholas-Arcari/FlipperZero-guide) integra scanner BLE e alcune funzioni GATT in un form factor portatile per il recon fisico rapido.

---

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| reconnaissance | active scanning | `T1595` | discovery dei device ble tramite scanning degli advertising packet (WIFI-006) |
| reconnaissance | gather victim host information | `T1592` | enumerazione dei servizi gatt, caratteristiche e informazioni del device (WIFI-006) |
| credential access | network sniffing | `T1040` | cattura passiva degli advertising packet e (con hardware dedicato) del traffico ble |

---

> **Nota:** Tutte le attivita documentate sono state condotte su dispositivi Bluetooth/BLE di laboratorio di proprieta dell'autore. La discovery e l'enumerazione GATT sono state eseguite esclusivamente contro device di test. L'accesso non autorizzato a dispositivi Bluetooth di terzi costituisce reato. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
