# Blind XSS / Out-of-Band (OOB) Interaction

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

Il campo Referer (http://testphp.vulnweb.com/) conferma che l'attacco ha avuto successo e che la richiesta è originata dal sito vittima.

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