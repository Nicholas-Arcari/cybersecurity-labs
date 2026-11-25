> [English](README.en.md) | **Italiano**

# Recon & monitor mode - mappatura dello spettro 802.11

> - **Fase:** Wireless Security - Reconnaissance & Passive Discovery (802.11)
> - **Visibilita:** Bassa - la scheda in monitor mode ascolta senza trasmettere (nessun pacchetto verso le reti target); la de-anonimizzazione degli SSID nascosti richiede l'invio di frame di deautenticazione (Attiva - genera traffico rilevabile da un WIDS)
> - **Prerequisiti:** Scheda WiFi con chipset compatibile monitor mode e packet injection (Atheros AR9271, Ralink RT3070, Realtek RTL8812AU); driver e aircrack-ng suite installati; antenna esterna consigliata per copertura estesa
> - **Output:** WIFI-001; mappa completa delle reti 802.11 nel raggio d'azione (BSSID, ESSID, canale, cifratura, potenza segnale); lista dei client associati per ogni AP; SSID nascosti de-anonimizzati; base dati per le fasi di cracking e rogue AP

- **Ambiente Operativo:** Kali Linux (Attaccante), scheda Alfa AWUS036ACH (monitor mode + injection), rete WiFi di laboratorio isolata
- **Target:** Access point WPA2-PSK di test (SSID `LAB-CORP`) + un AP con SSID nascosto (`LAB-HIDDEN`)
- **Tool principali:** airmon-ng, airodump-ng, Kismet

---

## Executive summary

La ricognizione wireless e il primo atto di ogni attacco al layer fisico 802.11: prima di poter attaccare una rete bisogna vederla. A differenza della recon di rete tradizionale (modulo 01-recon) che opera su IP e porte, qui il mezzo trasmissivo e l'etere e l'unita di osservazione e il frame di gestione 802.11, che le stazioni trasmettono in chiaro anche su reti cifrate WPA2.

La monitor mode trasforma la scheda WiFi in un ricevitore passivo che cattura tutti i frame nell'aria, non solo quelli destinati all'attaccante. Da questi frame si ricostruisce l'intera topologia radio: quali AP esistono, con quale cifratura, su quale canale, quali client sono associati e - dato piu prezioso - quali client stanno cercando reti a cui si sono connessi in passato (Probe Request), rivelando i loro pattern di mobilita.

Il finding WIFI-001 documenta la de-anonimizzazione di un SSID nascosto: la pratica diffusa di "nascondere" il nome della rete come misura di sicurezza e inefficace, perche il nome viene comunque trasmesso in chiaro nei frame di association ogni volta che un client legittimo si connette.

---

## Struttura della cartella

```
recon-monitor/
+-- README.md      # questo file: setup monitor mode, discovery, de-anon SSID nascosti
+-- img/           # screenshot airodump-ng e dashboard Kismet
```

---

## Attivazione della monitor mode

**ID Finding:** `WIFI-001` | **Severity:** `Basso` (information disclosure: SSID nascosto de-anonimizzato + client de-anonimizzati via Probe Request)

### Contesto operativo

La scheda WiFi in modalita normale (managed) processa solo i frame destinati al proprio MAC address. La monitor mode disabilita questo filtro e permette la cattura di tutti i frame radio sul canale corrente. E il prerequisito tecnico di ogni attivita wireless successiva: senza monitor mode non e possibile ne catturare handshake ne effettuare injection.

### Esecuzione

```Bash
# Identificazione dell'interfaccia wireless e dei processi interferenti
sudo airmon-ng
sudo airmon-ng check kill        # termina NetworkManager e wpa_supplicant

# Attivazione monitor mode (crea wlan0mon)
sudo airmon-ng start wlan0

# Verifica dello stato
iwconfig wlan0mon
```

```
PHY     Interface       Driver          Chipset
phy0    wlan0           88XXau          Realtek RTL8812AU

        (mac80211 monitor mode vif enabled for [phy0]wlan0 on [phy0]wlan0mon)   <-- monitor attivo
        (mac80211 station mode vif disabled for [phy0]wlan0)
```

---

## Discovery delle reti con airodump-ng

### Contesto operativo

airodump-ng effettua il channel hopping automatico su tutti i canali 2.4 GHz (e 5 GHz se il chipset lo supporta), catturando i Beacon frame trasmessi dagli AP e i frame dei client. Produce in tempo reale la mappa completa dello spettro.

### Esecuzione

```Bash
# Scansione completa dello spettro (channel hopping automatico)
sudo airodump-ng wlan0mon

# Cattura mirata su un AP specifico (BSSID + canale fisso) con salvataggio su file
sudo airodump-ng --bssid AA:BB:CC:DD:EE:FF -c 6 -w capture_lab wlan0mon
```

```
 CH  6 ][ Elapsed: 2 mins ][ 2026-05-12 14:30

 BSSID              PWR  Beacons    #Data, #/s  CH   MB   ENC  CIPHER  AUTH ESSID

 AA:BB:CC:DD:EE:FF  -42      312      1240   12   6  270   WPA2 CCMP   PSK  LAB-CORP        <-- target WPA2
 11:22:33:44:55:66  -58      201        45    0  11  130   WPA2 CCMP   PSK  <length: 10>    <-- SSID nascosto
 99:88:77:66:55:44  -71      145         3    0   1   54   OPN              GuestFree       <-- rete aperta

 BSSID              STATION            PWR   Rate    Lost    Frames  Notes  Probes

 AA:BB:CC:DD:EE:FF  A0:B1:C2:D3:E4:F5  -48    1e-6e     0       340         LAB-CORP
 11:22:33:44:55:66  60:70:80:90:A0:B0  -62    1e-1e    12        88         LAB-HIDDEN,HomeNet   <-- Probe Request
```

Le righe piu significative: l'AP `11:22:33:44:55:66` espone `<length: 10>` come ESSID (SSID nascosto, 10 caratteri), ma un suo client nella colonna Probes rivela `LAB-HIDDEN` - il nome reale della rete e stato intercettato dalla Probe Request del client.

---

## De-anonimizzazione dell'SSID nascosto

### Contesto operativo

Se nessun client sta trasmettendo Probe Request, si puo forzare la rivelazione dell'SSID inviando un frame di deautenticazione a un client associato: il client si disconnette e si riassocia immediatamente, e durante la riassociazione trasmette l'SSID in chiaro nel frame di Association Request.

### Esecuzione

```Bash
# Deautenticazione mirata di un client (forza riassociazione)
sudo aireplay-ng --deauth 5 -a 11:22:33:44:55:66 -c 60:70:80:90:A0:B0 wlan0mon
```

```
14:35:02  Waiting for beacon frame (BSSID: 11:22:33:44:55:66) on channel 11
14:35:02  Sending 64 directed DeAuth (code 7). STMAC: [60:70:80:90:A0:B0]  [ 8|12 ACKs]
14:35:04  Sending 64 directed DeAuth (code 7). STMAC: [60:70:80:90:A0:B0]  [ 6|10 ACKs]
```

```
 BSSID              CH   ENC  ESSID
 11:22:33:44:55:66  11   WPA2  LAB-HIDDEN         <-- SSID rivelato dopo la riassociazione
```

### Remediation

- **Azione immediata:** non affidarsi all'occultamento dell'SSID come misura di sicurezza; il nome viene comunque trasmesso in chiaro. Rimuovere l'SSID hiding elimina un falso senso di sicurezza senza ridurre la protezione reale (che dipende esclusivamente dalla robustezza della PSK e dal protocollo di cifratura)
- **Azione strutturale:** adottare WPA3-SAE dove supportato (protegge dagli attacchi offline sulla PSK); configurare Protected Management Frames (PMF, 802.11w) obbligatori per impedire i frame di deautenticazione forgiati; su reti aziendali migrare a WPA2/WPA3-Enterprise (802.1X) che elimina la PSK condivisa
- **Verifica:** un WIDS (Wireless IDS) come Kismet o il modulo wireless di un controller aziendale deve generare alert sui pattern di deauth flood

---

## Kismet - monitoraggio continuo e WIDS

### Contesto operativo

Airodump-ng e ideale per la sessione di attacco puntuale; Kismet e la scelta per il monitoraggio continuo e l'analisi passiva estesa. Kismet correla i dati nel tempo, mantiene un database SQLite di tutti i device visti, geolocalizza gli AP se collegato a un GPS, e opera come Wireless IDS rilevando deauth flood e rogue AP.

### Esecuzione

```Bash
# Avvio Kismet sull'interfaccia in monitor mode
sudo kismet -c wlan0mon
# Interfaccia web: http://localhost:2501
```

Kismet cattura anche i device che airodump-ng ignora: dispositivi Bluetooth (con datasource dedicato), reti nascoste correlate nel tempo, e client "silenziosi" che trasmettono solo Probe Request sporadiche. La dashboard web permette il filtraggio per tipo, la visualizzazione della potenza del segnale nel tempo e l'esportazione in formato Wigle per il wardriving mapping.

---

## Flusso operativo consigliato

```
[1] Setup interfaccia
     +-- airmon-ng check kill        # rimuove processi interferenti
     +-- airmon-ng start wlan0       # crea wlan0mon
              |
              v
[2] Discovery ad ampio spettro
     +-- airodump-ng wlan0mon        # channel hopping, mappa tutte le reti
     -> identificazione BSSID, canale, cifratura, client
              |
              v
[3] Cattura mirata
     +-- airodump-ng --bssid <BSSID> -c <CH> -w capture wlan0mon
     -> raccolta dati sul singolo target
              |
              v
[4] De-anonimizzazione (se SSID nascosto)
     +-- aireplay-ng --deauth 5 -a <BSSID> -c <CLIENT> wlan0mon
     -> SSID rivelato in Association Request (WIFI-001)
              |
              v
[5] Monitoraggio esteso / WIDS
     +-- kismet -c wlan0mon          # correlazione temporale, rogue detection
              |
              v
[OUTPUT] Mappa radio completa -> input per cracking/ e rogue-ap/
```

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `airmon-ng` | monitor mode manager | cli | attivazione monitor mode e gestione processi interferenti |
| `airodump-ng` | wireless sniffer | cli | discovery reti/client, cattura handshake, channel hopping |
| `aireplay-ng` | frame injector | cli | deautenticazione, forzatura riassociazione per de-anon ssid |
| `Kismet` | wids / passive sniffer | cli + web ui | monitoraggio continuo, correlazione temporale, rogue detection |
| `iw` | wireless config | cli | configurazione interfaccia, verifica capacita chipset |
| `hcxdumptool` | modern capture | cli | cattura pmkid e handshake (alternativa moderna ad airodump) |

> **Tool moderno consigliato:** `hcxdumptool` (ZerBea) sostituisce airodump-ng per la cattura clientless: acquisisce direttamente il PMKID dagli AP vulnerabili senza attendere un handshake completo, riducendo drasticamente i tempi di raccolta. Si integra con `hcxtools` per la conversione al formato hashcat. Vedere `../cracking/` per l'attacco PMKID (WIFI-003).

---

## Analisi teorica: perche i frame di gestione sono in chiaro

Lo standard 802.11 cifra esclusivamente il payload dei frame di dati (Data frames) tramite WPA2/WPA3. I frame di gestione (Management frames: Beacon, Probe Request/Response, Association, Deauthentication) e i frame di controllo viaggiano in chiaro per necessita progettuale: un client deve poter scoprire e negoziare l'associazione a una rete prima di stabilire le chiavi di sessione. Questo e il tallone d'Achille intrinseco del protocollo.

Ne consegue che tre categorie di informazioni sono sempre estraibili passivamente, indipendentemente dalla robustezza della cifratura:

1. **Metadati di rete:** BSSID, ESSID (anche se "nascosto", viene rivelato nell'Association), canale, capabilities, tipo di cifratura.
2. **Topologia dei client:** quali stazioni sono associate a quale AP, ricostruibile dal campo indirizzo dei Data frame.
3. **Storia di mobilita:** le Probe Request contengono i nomi delle reti a cui il device si e connesso in passato (Preferred Network List), permettendo il tracking del dispositivo e - nel finding WIFI-001 - la de-anonimizzazione.

L'introduzione dei Protected Management Frames (802.11w) mitiga solo la falsificazione dei frame di deauth/disassoc, ma non cifra Beacon e Probe. La difesa reale non e nascondere questi metadati (impossibile), ma rendere inutile la loro conoscenza tramite una PSK robusta o l'autenticazione 802.1X.

---

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| reconnaissance | active scanning | `T1595` | channel hopping e scansione dello spettro 802.11 per mappare ap e client (WIFI-001) |
| reconnaissance | gather victim network information | `T1590` | raccolta di bssid, essid, cifratura e topologia client dai frame di gestione 802.11 |
| credential access | network sniffing | `T1040` | cattura passiva dei frame radio in monitor mode per estrazione metadati e probe request |
| collection | adversary-in-the-middle | `T1557` | deautenticazione di un client per forzare la riassociazione e rivelare l'ssid nascosto (WIFI-001) |

---

> **Nota:** Tutte le attivita documentate sono state condotte su una rete WiFi di laboratorio di proprieta dell'autore, in ambiente radio isolato. La cattura di traffico e i frame di deautenticazione sono stati diretti esclusivamente contro AP e client di test. L'intercettazione di reti WiFi di terzi senza autorizzazione esplicita costituisce reato ai sensi della normativa vigente sulle comunicazioni elettroniche.
