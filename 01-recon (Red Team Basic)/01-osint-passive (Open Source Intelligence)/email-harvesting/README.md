> [English](README.en.md) | **Italiano**

# OSINT passive: email harvesting (personal audit)

> - **Fase:** Reconnaissance - Passive Information Gathering
> - **Visibilita:** Zero - nessun contatto diretto con il target, interrogazione di motori di ricerca pubblici
> - **Prerequisiti:** Dominio target, tool theHarvester installato, accesso a Internet
> - **Output:** OSINT-002 - Mappa delle email esposte e analisi della superficie di attacco del dominio target

---

Obiettivo: Verifica dell'esposizione di indirizzi email sul dominio personale e analisi della superficie di attacco del portfolio digitale.

Target: `nicholas-arcari.github.io`
Strumenti: `theHarvester`, `Google Dorks`

---

## 1 Introduzione teorica

L'Email Harvesting è una tecnica di ricognizione (Reconnaissance) solitamente utilizzata per mappare la struttura organigrammatica di un'organizzazione target.

Tuttavia, in un contesto di Personal Security Audit, questa tecnica viene adattata per verificare se un sito web personale espone involontariamente dati di contatto (PII) che potrebbero essere indicizzati dai motori di ricerca e successivamente bersagliati da bot di spam o campagne di Spear Phishing.

---

## 2 Esecuzione tecnica

**ID Finding:** `OSINT-002` | **Severity:** `Informativo`

#### A. scansione automatizzata (TheHarvester)

È stato interrogato il dominio del portfolio utilizzando `theHarvester` per aggregare risultati da fonti pubbliche (OSINT) e verificare l'indicizzazione di email associate al sottodominio.

Comando:

```Bash
theHarvester -d nicholas-arcari.github.io -b all
```

Nota Tecnica: Poiché GitHub Pages è un servizio di hosting statico e non fornisce un server di posta elettronica diretto, è atteso un risultato nullo per le email strettamente legate al dominio (es. `info@nicholas-arcari.github.io`), a meno di configurazioni personalizzate errate.

#### B. analisi dei risultati (TheHarvester)

Fonti utilizzate: Baidu, Bing, DuckDuckGo, Yahoo, CRTsh.

|categoria | risultato |analisi tecnica|
|---------|-------------|-----------------|
|email esposte | 0 email found | positiva. non vi è esposizione diretta di contatti email indicizzati sui motori di ricerca per questo dominio specifico|
|infrastruttura | 4 ip (es. 185.199...) | gli indirizzi ip appartengono all'infrastruttura di github pages (hosting provider). non rappresentano un server privato gestito dall'utente|
|sottodomini | 19 hosts (es. shop., ftp.) | falsi positivi. si tratta di un artefatto dovuto ai record dns wildcard generati dall'infrastruttura cloud di github. una verifica manuale conferma che questi servizi non sono attivi|

#### C. ricerca mirata (Google dorking)

Poiché il dominio è ospitato su GitHub, esiste il rischio che le email di contatto personali (es. Gmail) siano state lasciate "in chiaro" nel codice sorgente o nei file di documentazione (README).

Query Eseguita:

```Bash
site:nicholas-arcari.github.io "gmail.com"
```

Obiettivo: Identificare se l'indirizzo email personale è visibile in chiaro nelle pagine del portfolio.

L'analisi ha evidenziato/non ha evidenziato la presenza dell'indirizzo personale.

---

## 3 Conclusione e remediation

Dall'analisi emerge che il dominio personale presenta una superficie di attacco minima per quanto riguarda l'harvesting automatico.

Raccomandazioni:

- Obfuscation (Offuscamento): Se è necessario pubblicare un contatto email, evitare il formato testo standard (`testo@dominio`). Utilizzare immagini o formati non machine-readable (es. `nome [at] gmail [dot] com`) per prevenire lo scraping da parte dei bot.
- Moduli di Contatto: Preferire l'integrazione di moduli backend-less (es. Formspree) che permettono il contatto senza esporre l'indirizzo di destinazione nel codice frontend.

---

## Analisi a basso livello: infrastruttura email e record DNS associati

L'email harvesting non si limita alla raccolta di indirizzi: i record DNS associati al dominio rivelano l'intera infrastruttura di posta elettronica e le relative protezioni anti-spoofing.

### Record MX (mail exchanger)

Il record MX definisce quale server accetta la posta per un dominio. La sua analisi rivela il provider email utilizzato:

```Bash
dig MX nicholas-arcari.github.io +short
# Risultato atteso per GitHub Pages: nessun record MX
# Risultato tipico aziendale:
# 10 mx1.azienda.it          <-- server primario (priorita 10)
# 20 mx2.azienda.it          <-- server secondario (failover)
# Per Google Workspace: ASPMX.L.GOOGLE.COM
# Per Microsoft 365: azienda-it.mail.protection.outlook.com
```

L'assenza di record MX per `nicholas-arcari.github.io` conferma che GitHub Pages non fornisce servizi email - un esito atteso che riduce la superficie di attacco a zero per questo vettore.

### SPF, DKIM e DMARC: la triade di autenticazione email

Questi tre meccanismi, implementati come record TXT nel DNS, costituiscono la difesa contro l'email spoofing:

| record | funzione | verifica con dig |
| :--- | :--- | :--- |
| **spf** (rfc 7208) | dichiara quali ip sono autorizzati a inviare email per il dominio | `dig TXT dominio.it +short` -> `"v=spf1 include:_spf.google.com ~all"` |
| **dkim** (rfc 6376) | firma crittografica (rsa/ed25519) nel header dell'email verificabile tramite chiave pubblica nel dns | `dig TXT selector._domainkey.dominio.it` |
| **dmarc** (rfc 7489) | policy che istruisce il server ricevente su come trattare email che falliscono spf/dkim | `dig TXT _dmarc.dominio.it` -> `"v=DMARC1; p=reject; rua=mailto:..."` |

**Valore per il Red Team:** un dominio con SPF in modalita `~all` (SoftFail) o senza DMARC consente l'invio di email spoofate che superano i filtri di molti provider. L'harvesting delle email combinato con l'analisi dei record DNS permette di valutare la fattibilita di campagne di spear phishing con email che appaiono provenire dal dominio target.

### theHarvester: pipeline di raccolta

theHarvester opera interrogando in parallelo le API di motori di ricerca e servizi OSINT. Il parametro `-b all` attiva tutte le fonti disponibili, ma il throughput reale dipende dalle API key configurate:

```
theHarvester -b all
        |
        +-- Bing API -> scraping risultati per "email @dominio"
        +-- Google (rate limited, CAPTCHA dopo ~100 query)
        +-- CRTsh -> Certificate Transparency logs per sottodomini
        +-- DNSDumpster -> record DNS passivi
        +-- Shodan (richiede API key) -> banner con email nei servizi esposti
        +-- Hunter.io (richiede API key) -> database aziendale email
```

Senza API key, molte fonti restituiscono risultati parziali o nulli. Il tool `Hunter.io` (gratuito fino a 25 ricerche/mese) e spesso la fonte piu produttiva per email aziendali perche indicizza firme email, pagine "Chi Siamo" e documenti PDF.

---

## Blue team: protezione contro email harvesting

**Monitoring dell'esposizione:**
- Eseguire periodicamente `theHarvester -d dominio.it -b all` sul proprio dominio per verificare cosa e visibile
- Configurare Google Alerts per `"@dominio.it" -site:dominio.it` per rilevare email indicizzate su siti esterni
- Utilizzare Hunter.io Domain Search per verificare quante email aziendali sono nel loro database

**Hardening:**
- Implementare DMARC con policy `p=reject` e reporting (`rua=`) per bloccare spoofing e monitorare tentativi
- Configurare SPF con `-all` (HardFail) invece di `~all` (SoftFail) quando possibile
- Rimuovere email in chiaro dal codice sorgente di siti web (utilizzare form di contatto o JavaScript encoding)
- Applicare EXIF/metadata stripping ai documenti PDF/DOCX pubblicati (rimuovono autore, email, software)

---

## Esperienza di laboratorio

L'esecuzione su un dominio GitHub Pages ha prodotto un risultato apparentemente banale (zero email trovate), ma l'esercizio ha avuto valore formativo per due aspetti. Il primo: theHarvester ha restituito 4 indirizzi IP e 19 host per il dominio - tutti appartenenti all'infrastruttura GitHub (range 185.199.x.x). Senza l'analisi manuale, questi risultati avrebbero potuto essere erroneamente classificati come server del target. I 19 sottodomini (shop, ftp, www) erano falsi positivi generati dalla wildcard DNS di GitHub Pages - pattern che si ripresenta con qualsiasi servizio cloud che implementa catch-all DNS.

Il secondo aspetto: la ricerca Google Dork `site:nicholas-arcari.github.io "gmail.com"` ha dimostrato un vettore spesso sottovalutato per i siti statici - il codice sorgente. Su GitHub Pages, l'intero repository e pubblico: un'email inserita in un `README.md` o in un file di configurazione diventa permanentemente indicizzata, anche se successivamente rimossa (la cache di Google e la Wayback Machine la preservano). Questa persistenza delle informazioni e un concetto chiave per l'OSINT: una volta che un dato e stato indicizzato, la rimozione dalla fonte non garantisce la rimozione dall'indice.

---

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| reconnaissance | gather victim identity info: email addresses | `T1589.002` | harvesting email associate al dominio nicholas-arcari.github.io con theharvester e google dorks per mappare la superficie di attacco del portfolio (OSINT-002) |

---

> **Nota:** Le attivita documentate in questa sezione sono state condotte su un dominio di proprieta personale a scopo di audit. I risultati confermano una superficie di attacco minima per email harvesting.
