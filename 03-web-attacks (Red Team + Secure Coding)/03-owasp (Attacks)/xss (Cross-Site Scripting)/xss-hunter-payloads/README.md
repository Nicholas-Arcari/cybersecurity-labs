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