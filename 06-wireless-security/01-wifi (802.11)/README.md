> [English](README.en.md) | **Italiano**

# 01 - WiFi (802.11)

> - **Fase:** Wireless Security - Attacco alle reti 802.11
> - **Visibilita:** Variabile - da Bassa (monitor mode passivo, cracking offline) ad Alta (deautenticazione, rogue AP, WPS bruteforce)
> - **Prerequisiti:** Scheda WiFi con chipset compatibile monitor mode + packet injection (Atheros AR9271, Realtek RTL8812AU); aircrack-ng suite; wordlist dedicate; GPU per il cracking WPA2
> - **Output:** Finding WIFI-001..005; mappa dello spettro radio; PSK recuperate; credenziali via Evil Twin; accesso alle reti target come client legittimo

---

## Introduzione

La sezione `01-wifi (802.11)` e la piu corposa del modulo wireless perche l'802.11 e la tecnologia radio piu diffusa e la superficie d'attacco piu ricca. Qui l'obiettivo e ottenere accesso alla rete WiFi target - come credenziale (PSK/portale) o come posizione Man-in-the-Middle - bypassando il perimetro fisico dell'organizzazione.

La sezione copre l'intera kill chain wireless in quattro fasi:

1. **Recon & Monitor (WIFI-001):** attivazione della monitor mode e mappatura passiva dello spettro. Discovery di AP, client e SSID nascosti tramite airodump-ng e Kismet. E il prerequisito tecnico di ogni attacco successivo.

2. **Cracking (WIFI-002..003):** recupero della PSK WPA2 tramite cattura del 4-way handshake (metodo classico) e attacco PMKID clientless (metodo moderno). Il cracking offline con aircrack-ng e hashcat riduce la sicurezza della rete alla robustezza della password.

3. **Rogue AP & Evil Twin (WIFI-004):** attacco agli utenti anziche alla crittografia. Creazione di un AP fasullo con captive portal per il credential harvesting e la posizione MITM. Efficace anche contro reti con PSK robusta.

4. **Automated Attacks (WIFI-005):** orchestrazione dell'intera catena con Wifite2 e Airgeddon, incluso l'attacco WPS Pixie-Dust che bypassa la PSK sfruttando una debolezza implementativa del WPS.

Concetto chiave sulle wordlist: le PSK WiFi hanno spesso pattern specifici (8 cifre numeriche - default di molti router, date, numeri di telefono). Le wordlist dedicate al WiFi e le regole hashcat mirate a questi pattern sono documentate in `04-system-exploitation/05-password-cracking/wordlists/`.

---

## Struttura della cartella

```
01-wifi (802.11)/
+-- README.md              # questo file: registro WIFI-001..005 + MITRE aggregata
|
+-- recon-monitor/         # WIFI-001: monitor mode, discovery, de-anon SSID (airodump, Kismet)
+-- cracking/              # WIFI-002 handshake WPA2, WIFI-003 PMKID (aircrack-ng, hashcat)
+-- rogue-ap/              # WIFI-004: Evil Twin + captive portal (hostapd-mana, Airgeddon)
+-- automated-attacks/     # WIFI-005: Wifite2 + WPS Pixie-Dust (Wifite2, Airgeddon, reaver)
```

---

## Flusso operativo consigliato

```
[INPUT] Scheda WiFi monitor+injection, area target nel raggio radio
         |
         v
[1] Recon & Monitor (recon-monitor/)
     +-- airmon-ng start wlan0 -> monitor mode
     +-- airodump-ng -> mappa AP/client, canale, cifratura (WIFI-001)
              |
              v
[2] Scelta della strategia in base al target
     +-- WPS abilitato? --------> automated-attacks/ (Pixie-Dust, vittoria rapida) WIFI-005
     +-- PSK debole probabile? -> cracking/ (handshake/PMKID + dizionario) WIFI-002/003
     +-- PSK robusta / target utenti? -> rogue-ap/ (Evil Twin, credential harvest) WIFI-004
              |
              v
[3] Esecuzione dell'attacco
     +-- cattura handshake/PMKID -> cracking offline (hashcat -m 22000)
     +-- oppure Evil Twin -> captive portal -> credenziali
     +-- oppure Wifite2 -> audit automatizzato multi-target
              |
              v
[4] Accesso alla rete
     +-- PSK recuperata / credenziali catturate
     -> connessione come client legittimo
              |
              v
[OUTPUT] Accesso rete interna -> 07-post-exploitation (lateral movement, scan interno)
```

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `aircrack-ng suite` | Wireless attack suite | CLI | Monitor mode, cattura handshake, deauth, cracking (essenziale) |
| `Kismet` | WIDS / passive sniffer | CLI + Web | Discovery passiva, reti nascoste, correlazione temporale |
| `hashcat` | GPU cracker | CLI | Cracking WPA2 accelerato GPU (modalita 22000) |
| `hcxdumptool` | Clientless capture | CLI | Cattura PMKID senza client (attacco moderno) |
| `Wifite2` | Attack automator | CLI | Automazione dell'intero audit wireless |
| `Airgeddon` | Multi-attack framework | CLI - Menu | Evil Twin, WPS, DoS in un unico strumento guidato |
| `hostapd-mana` | Rogue AP daemon | CLI | Evil Twin con KARMA per credential harvesting |

> **Tool moderno consigliato:** la combinazione `hcxdumptool` + `hashcat -m 22000` per il cracking clientless e lo standard moderno; `Wifite2` per l'automazione; `eaphammer` per le reti WPA2-Enterprise (802.1X).

---

## Registro Finding - Sezione WiFi

| ID | Descrizione | Severity | Sottocartella |
| :--- | :--- | :---: | :--- |
| `WIFI-001` | Monitor mode + de-anonimizzazione SSID nascosto e client via Probe Request | `Basso` | `recon-monitor/` |
| `WIFI-002` | WPA2 4-way handshake catturato e PSK recuperata via attacco a dizionario | `Alto` | `cracking/` |
| `WIFI-003` | PMKID clientless catturato e PSK recuperata senza client connessi | `Alto` | `cracking/` |
| `WIFI-004` | Evil Twin con captive portal: credential harvesting + posizione MITM | `Critico` | `rogue-ap/` |
| `WIFI-005` | WPS Pixie-Dust: PIN WPS recuperato in secondi, PSK compromessa a prescindere dalla robustezza | `Alto` | `automated-attacks/` |

---

## Mappatura MITRE ATT&CK - Aggregata

| Tattica | Tecnica | ID MITRE | Finding Correlato |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Active Scanning | `T1595` | WIFI-001 |
| Reconnaissance | Gather Victim Network Information | `T1590` | WIFI-001 |
| Credential Access | Network Sniffing | `T1040` | WIFI-001, WIFI-002, WIFI-003, WIFI-005 |
| Credential Access | Brute Force: Password Cracking | `T1110.002` | WIFI-002, WIFI-003 |
| Credential Access | Brute Force | `T1110` | WIFI-005 |
| Credential Access | Adversary-in-the-Middle: Evil Twin | `T1557.004` | WIFI-004 |
| Collection | Adversary-in-the-Middle | `T1557` | WIFI-001, WIFI-002, WIFI-004, WIFI-005 |
| Credential Access | Input Capture: Web Portal Capture | `T1056.003` | WIFI-004 |
| Initial Access | Hardware Additions | `T1200` | WIFI-004 |
| Initial Access | Valid Accounts | `T1078` | WIFI-002, WIFI-003, WIFI-004, WIFI-005 |

---

> **Nota:** Tutte le attivita documentate in questa sezione sono state condotte su reti WiFi di laboratorio di proprieta dell'autore, in ambiente radio isolato. Nessun attacco e stato diretto contro reti di terzi. L'intercettazione e l'accesso non autorizzato a reti wireless costituiscono reato ai sensi della normativa vigente. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
