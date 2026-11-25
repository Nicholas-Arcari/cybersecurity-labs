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

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `aircrack-ng suite` | wireless attack suite | cli | monitor mode, cattura handshake, deauth, cracking (essenziale) |
| `Kismet` | wids / passive sniffer | cli + web | discovery passiva, reti nascoste, correlazione temporale |
| `hashcat` | gpu cracker | cli | cracking wpa2 accelerato gpu (modalita 22000) |
| `hcxdumptool` | clientless capture | cli | cattura pmkid senza client (attacco moderno) |
| `Wifite2` | attack automator | cli | automazione dell'intero audit wireless |
| `Airgeddon` | multi-attack framework | cli - menu | evil twin, wps, dos in un unico strumento guidato |
| `hostapd-mana` | rogue ap daemon | cli | evil twin con karma per credential harvesting |

> **Tool moderno consigliato:** la combinazione `hcxdumptool` + `hashcat -m 22000` per il cracking clientless e lo standard moderno; `Wifite2` per l'automazione; `eaphammer` per le reti WPA2-Enterprise (802.1X).

---

## Registro finding - sezione WiFi

| id | descrizione | severity | sottocartella |
| :--- | :--- | :---: | :--- |
| `WIFI-001` | monitor mode + de-anonimizzazione ssid nascosto e client via probe request | `Basso` | `recon-monitor/` |
| `WIFI-002` | wpa2 4-way handshake catturato e psk recuperata via attacco a dizionario | `Alto` | `cracking/` |
| `WIFI-003` | pmkid clientless catturato e psk recuperata senza client connessi | `Alto` | `cracking/` |
| `WIFI-004` | evil twin con captive portal: credential harvesting + posizione mitm | `Critico` | `rogue-ap/` |
| `WIFI-005` | wps pixie-dust: pin wps recuperato in secondi, psk compromessa a prescindere dalla robustezza | `Alto` | `automated-attacks/` |

---

## Mappatura MITRE ATT&CK - aggregata

| tattica | tecnica | id mitre | finding correlato |
| :--- | :--- | :--- | :--- |
| reconnaissance | active scanning | `T1595` | WIFI-001 |
| reconnaissance | gather victim network information | `T1590` | WIFI-001 |
| credential access | network sniffing | `T1040` | WIFI-001, WIFI-002, WIFI-003, WIFI-005 |
| credential access | brute force: password cracking | `T1110.002` | WIFI-002, WIFI-003 |
| credential access | brute force | `T1110` | WIFI-005 |
| credential access | adversary-in-the-middle: evil twin | `T1557.004` | WIFI-004 |
| collection | adversary-in-the-middle | `T1557` | WIFI-001, WIFI-002, WIFI-004, WIFI-005 |
| credential access | input capture: web portal capture | `T1056.003` | WIFI-004 |
| initial access | hardware additions | `T1200` | WIFI-004 |
| initial access | valid accounts | `T1078` | WIFI-002, WIFI-003, WIFI-004, WIFI-005 |

---

> **Nota:** Tutte le attivita documentate in questa sezione sono state condotte su reti WiFi di laboratorio di proprieta dell'autore, in ambiente radio isolato. Nessun attacco e stato diretto contro reti di terzi. L'intercettazione e l'accesso non autorizzato a reti wireless costituiscono reato ai sensi della normativa vigente. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
