> [English](README.en.md) | **Italiano**

# Proxy Tools: Burp Suite Interception & Extensions

> - **Fase:** Web Attack - Proxy Setup & Traffic Manipulation
> - **Visibilita:** Locale - il traffico rimane tra browser e proxy, nessun pacchetto aggiuntivo verso il target
> - **Prerequisiti:** Browser configurato per usare proxy `127.0.0.1:8080`, certificato CA Burp installato nel trust store
> - **Output:** Intercettazione e manipolazione del traffico HTTP/HTTPS, User-Agent spoofing, log delle richieste per analisi successiva

---

Obiettivo: Configurazione di un proxy HTTP locale per intercettare, analizzare e manipolare il traffico tra il client (Browser) e il server target, estendendo le funzionalità base tramite BApps.

Target: `tesla.com` (Analisi Client-Side)

Strumenti: `Burp Suite Community Edition`

---

## 1 Introduzione Teorica

Un Web Proxy (come Burp Suite) è lo strumento fondamentale per il Web Application Penetration Testing. Si posiziona come "Man-in-the-Middle" (MitM) tra il browser dell'attaccante e il server web. A differenza degli sniffer passivi (Wireshark), il Proxy permette di:

- Intercettare: Bloccare una richiesta HTTP prima che lasci il computer.
- Modificare: Cambiare parametri, cookie o header "al volo".
- Inoltrare: Inviare la richiesta manipolata al server e analizzare come risponde.

---

## 2 Esecuzione Tecnica: Traffic Manipulation

È stato configurato il proxy listener su `127.0.0.1:8080` ed è stato intercettato il traffico verso il target.

Scenario: User-Agent Spoofing L'obiettivo è modificare l'identità del client dichiarata nell'header HTTP per simulare un dispositivo diverso o un bot autorizzato.

Procedura:

- Attivazione di `Intercept On` nel tab Proxy.
- Navigazione verso `tesla.com`.
- La richiesta GET è stata bloccata.
- L'header `User-Agent` è stato modificato manualmente da Mozilla/5.0... a `Portfolio-Red-Team-Phone`.
- La richiesta è stata inoltrata al server (`Forward`).

![](./img/Screenshot_2026-02-10_18_39_10.jpg)

Perché questa tecnica è critica nel Red Teaming?

La manipolazione dello User-Agent permette di eseguire attacchi di Evasione e Accesso:

- WAF Evasion: Modificare lo User-Agent in GoogleBot permette spesso di bypassare i firewall che bloccano gli scanner di vulnerabilità automatici.
- Mobile Attack Surface: Fingersi un dispositivo mobile (iPhone, Android) può costringere il server a restituire una versione semplificata del sito, che spesso contiene meno controlli di sicurezza o API diverse vulnerabili.
- Legacy Access: Simulare browser obsoleti (es. IE6) può sbloccare pannelli di amministrazione legacy non visibili ai browser moderni.

---

## 3 Advanced Configuration: BApp Store

Per preparare l'ambiente a test più complessi, è stato esplorato il BApp Store, il repository ufficiale delle estensioni di Burp. Le estensioni permettono di automatizzare task ripetitivi o supportare protocolli specifici.

Estensioni chiave identificate:

- Logger++: Per un logging avanzato delle richieste (utile quando la History di base non basta).
- Turbo Intruder: Per attacchi di brute-force ad alta velocità (Race Conditions).
- Autorize: Per testare automaticamente le vulnerabilità di controllo accessi (IDOR) navigando come utenti diversi.

![](./img/Screenshot_2026-02-10_19_22_04.jpg)

---

## 4 Conclusioni

La capacità di intercettare e modificare il traffico "in transito" è il prerequisito per qualsiasi attività di Web Hacking avanzato. Attraverso questo lab, è stata dimostrata la competenza nella gestione del flusso HTTP, superando la semplice navigazione passiva e interagendo direttamente con il protocollo sottostante per manipolare la risposta del server.

---

## 5 Extra, nota su Persistenza e Reporting (.burp files)

Durante questo laboratorio è stata utilizzata la Community Edition, che opera esclusivamente in modalità "Temporary Project" (in memoria).
In un contesto aziendale (Enterprise/Red Team) che utilizza Burp Suite Professional, il flusso di lavoro standard prevede il salvataggio continuo dei progetti in formato `.burp`.

Importanza dei file .burp:

- Evidence Retention: Garantiscono la conservazione forense di tutto il traffico generato, utile per rispondere a contestazioni future o per redigere il report finale.
- Pause & Resume: Permettono di interrompere un test e riprenderlo giorni dopo mantenendo lo stato dello Scanner, del Repeater e della Sitemap.
- Collaboration: I file possono essere condivisi tra membri del team per analizzare vulnerabilità complesse in gruppo.

---

## Analisi a Basso Livello: Architettura del Proxy e Flusso di Intercettazione

### Come Funziona Burp Suite a Livello di Rete

Burp Suite opera come un forward proxy HTTP/HTTPS che si inserisce nel flusso TCP tra il browser e il server:

```
Browser (Firefox)              Burp Suite (127.0.0.1:8080)          Server (tesla.com)
    |                                |                                    |
    |--- TCP connect :8080 -------->|                                    |
    |--- CONNECT tesla.com:443 ---->|  <-- metodo HTTP CONNECT per HTTPS |
    |<-- 200 Connection established-|                                    |
    |                               |                                    |
    |--- TLS ClientHello ---------->|  (Burp genera cert falso per       |
    |<-- TLS ServerHello -----------|   tesla.com firmato dalla CA Burp) |
    |   [Cert: CN=tesla.com,       |                                    |
    |    Issuer: PortSwigger CA]    |                                    |
    |                               |--- TLS ClientHello -------------->|
    |                               |<-- TLS ServerHello (cert reale) --|
    |                               |   [Cert: CN=tesla.com,            |
    |                               |    Issuer: DigiCert]              |
    |                               |                                    |
    |=== Sessione TLS #1 ===========|=== Sessione TLS #2 ===============|
    |   (browser <-> Burp)          |   (Burp <-> server)               |
    |                               |                                    |
    |--- GET / HTTP/1.1 ----------->|  [Burp decifra, mostra in UI,     |
    |   User-Agent: Mozilla/5.0     |   permette modifica]              |
    |                               |--- GET / HTTP/1.1 --------------->|
    |                               |   User-Agent: Portfolio-Red-Team  |
    |                               |<-- 200 OK (risposta) -------------|
    |<-- 200 OK (re-cifrata) ------|                                    |
```

### Moduli Burp Suite e Workflow

| Modulo | Funzione | Caso d'uso operativo |
| :--- | :--- | :--- |
| **Proxy** | Intercetta e modifica richieste | Manipolazione parametri, header, cookie |
| **Repeater** | Re-invia richieste singole modificate | Testing manuale di parametri vulnerabili |
| **Intruder** | Brute force parametrizzato | Credential stuffing, parameter fuzzing |
| **Scanner** (Pro) | Vulnerability scanning automatico | DAST su applicazioni web |
| **Decoder** | Encoding/decoding (Base64, URL, HTML) | Analisi payload offuscati |
| **Comparer** | Diff tra risposte HTTP | Identificare differenze in risposte autenticate vs non |

### BApp Extensions per Assessment Professionali

```
Extension            Tipo              Uso
Autorize             Auth testing      Testa IDOR: invia ogni richiesta come utente low-priv
Turbo Intruder       Performance       Race conditions: invia N richieste simultaneamente
Logger++             Logging           Filtra e cerca nel traffico HTTP con regex
Active Scan++        Scanner           Aggiunge check per vulnerabilita aggiuntive
Param Miner          Discovery         Trova parametri HTTP nascosti (cache poisoning)
Hackvertor           Encoding          Encoding dinamico nei payload (bypass WAF)
```

---

## Blue Team: Detection dei Proxy di Intercettazione

### Indicatori di Manipolazione del Traffico

- **JA3 fingerprint:** il TLS handshake di Burp Suite (Java) ha un JA3 hash diverso da qualsiasi browser reale - i WAF moderni confrontano il JA3 con il User-Agent dichiarato e bloccano se non corrispondono
- **Certificate chain:** se un'organizzazione ispeziona il traffico TLS dei dipendenti (corporate proxy), la CA dell'organizzazione e nell'Issuer - anomalie nella chain indicano proxy non autorizzati
- **Timing anomalies:** l'intercettazione manuale (Intercept On) introduce latenza variabile nelle richieste, rilevabile da analisi statistica dei tempi di risposta

### Hardening Anti-Proxy

- **Certificate Pinning** nelle applicazioni mobili: ignora il trust store del dispositivo, accetta solo il certificato specifico dell'app
- **JA3 validation** lato server: rifiutare connessioni dove il JA3 hash non corrisponde a browser noti
- **Token binding:** legare i token di sessione al canale TLS specifico, invalidandoli se il canale cambia (come nel caso di un proxy MitM)

---

## Esperienza di Laboratorio

La manipolazione del User-Agent e stata la prima dimostrazione concreta di come il traffico HTTP sia "fidato ma non verificato": il server non ha modo di distinguere un User-Agent reale da uno spoofato, perche l'header e controllato interamente dal client. Questo e il principio fondamentale del web application testing: tutto cio che arriva dal client puo essere manipolato.

La differenza tra Community e Professional Edition e stata tangibile: senza la possibilita di salvare progetti `.burp`, ogni sessione parte da zero. In un assessment che dura giorni o settimane, la perdita della sitemap, della history e dello stato dello Scanner rende la Community Edition inadeguata per uso professionale. Tuttavia, per l'apprendimento e il testing puntuale, i moduli Proxy, Repeater e Decoder della Community Edition sono sufficienti.

L'esplorazione del BApp Store ha rivelato l'ecosistema di estensioni che trasforma Burp da semplice proxy a piattaforma di testing completa. Autorize in particolare e fondamentale per testare le vulnerabilita di Broken Access Control (OWASP A01:2021): naviga l'applicazione come admin, e Autorize ri-invia automaticamente ogni richiesta come utente low-privilege, evidenziando le risorse accessibili senza autorizzazione.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Collection | Man-in-the-Middle | `T1557` | Posizionamento di Burp Suite come proxy MitM tra browser e server `tesla.com` per intercettare il traffico HTTP/HTTPS |
| Defense Evasion | Masquerading: Masquerade File Type | `T1036.008` | Modifica dell'header `User-Agent` da browser standard a `Portfolio-Red-Team-Phone` per simulare un dispositivo diverso e potenzialmente bypassare controlli di sicurezza |

---

> **Nota:** Le attivita documentate in questo lab si sono svolte su `tesla.com` nell'ambito di
> un'analisi client-side del traffico HTTP dal browser locale verso il target. Il traffico non
> ha generato richieste invasive o automatizzate verso il server. In un engagement reale, qualsiasi
> attivita di intercettazione su sistemi non autorizzati costituisce una violazione della privacy
> e un reato informatico.