# 01 - OSINT Passivo (Open Source Intelligence)

> - **Fase:** Reconnaissance - Passive Information Gathering
> - **Visibilita:** Zero - nessun pacchetto inviato al target, nessun log generato sui sistemi del bersaglio
> - **Prerequisiti:** Identificazione del target (dominio, email, username noti), accesso a Internet
> - **Output:** Credenziali in breach (OSINT-001), email esposte (OSINT-002), file/login indicizzati (OSINT-003), profili social correlati (OSINT-004)

---

## Introduzione

L'OSINT Passivo e la fase di ricognizione piu sicura per l'analista e piu insidiosa per il difensore: le informazioni vengono raccolte esclusivamente da fonti pubbliche e aperte, senza mai contattare i sistemi del target. Ogni dato e gia disponibile su Internet - il compito del Red Team e aggregarlo, correlarlo e trasformarlo in intelligence operativa.

Il principio guida e il grafo OSINT: si parte da un dato noto (es. un dominio, un'email, un nome) e si espande verso altri dati collegati (sottodomini, dipendenti, credenziali, account social). Ogni nodo trovato diventa un nuovo punto di partenza per ulteriori ricerche.

L'OSINT passivo alimenta direttamente le fasi successive:
- Le email trovate diventano target per campagne di Phishing (`05-social-engineering/`)
- I sottodomini trovati diventano scope per il Web Attack module (`03-web-attacks/`)
- Le credenziali in breach vengono testate nella fase di Credential Reuse (`07-post-exploitation/`)
- I nomi dei dipendenti trovati con Sherlock vengono usati per costruire lanci di Social Engineering

---

## Struttura della cartella

```
01-osint-passive (Open Source Intelligence)/
+-- README.md                 <- questo file (indice OSINT + registro finding)
|
+-- breach-data/
|   +-- README.md             <- OSINT-001: credenziali in breach (h8mail, HIBP)
|   +-- img/                  <- screenshot del lab
|
+-- email-harvesting/
|   +-- README.md             <- OSINT-002: email esposte (theHarvester, Google Dorks)
|
+-- google-dorks/
|   +-- README.md             <- OSINT-003: file e login indicizzati (GHDB, operatori avanzati)
|
+-- user-enumeration/
    +-- README.md             <- OSINT-004: identity correlation (Sherlock)
    +-- img/                  <- screenshot del lab
```

---

## `breach-data/` - Analisi Credenziali Compromesse

**ID Finding:** `OSINT-001` | **Severity:** `Alto`

L'analisi dei data breach pubblici permette di identificare credenziali compromesse associate al target. Se un dipendente ha riutilizzato la stessa password tra un vecchio servizio violato (es. LinkedIn 2012) e la VPN aziendale, un attaccante puo ottenere accesso immediato senza alcuna tecnica di exploitation.

Tool principali: `h8mail` (CLI), `HaveIBeenPwned` (Web).

**Lezione appresa da questo lab:** i tool CLI dipendono dalla disponibilita delle API esterne. Un risultato "non compromesso" da riga di comando va sempre validato manualmente sul portale HIBP.

---

## `email-harvesting/` - Mappatura Email Esposte

**ID Finding:** `OSINT-002` | **Severity:** `Informativo`

L'Email Harvesting identifica gli indirizzi email associati a un dominio target, sia attraverso tool automatizzati (`theHarvester`) sia tramite Google Dorking mirato. Le email trovate costituiscono la lista di target per campagne di Spear Phishing.

In questo lab: audit del dominio personale `nicholas-arcari.github.io`. Risultato: superficie di attacco minima, 0 email dirette indicizzate.

---

## `google-dorks/` - Sensitive Data Exposure tramite Motori di Ricerca

**ID Finding:** `OSINT-003` | **Severity:** `Variabile (Basso / Alto)`

Le Google Dorks sfruttano operatori avanzati (`site:`, `filetype:`, `inurl:`, `intitle:`) per trovare file sensibili, pannelli di login e directory listing indicizzati per errore. La severity dipende da cosa si trova: da una lista di PDF (Basso) a credenziali in chiaro o pannelli di amministrazione accessibili (Alto).

Target: `nasa.gov` (programma pubblico di divulgazione, solo scopo didattico).

---

## `user-enumeration/` - Identity Correlation e User Tracking

**ID Finding:** `OSINT-004` | **Severity:** `Basso`

La User Enumeration passiva sfrutta la tendenza degli utenti a riutilizzare lo stesso handle su piattaforme diverse. Con `Sherlock` si interrogano 300+ siti per verificare la presenza di un username, costruendo un profilo completo del target utile per Social Engineering.

Attenzione critica: i falsi positivi sono frequenti. Ogni hit va verificato manualmente prima di essere usato in un report.

---

## Flusso operativo consigliato

```
[INPUT] Un dato di partenza (es. dominio, email, nome completo)
          |
          v
[1] Breach Data Check
     +-- h8mail -t <EMAIL>
     +-- HIBP web (validazione manuale)
     -> Se trovate credenziali: escalation a finding OSINT-001 (Alto)
          |
          v
[2] Email Harvesting
     +-- theHarvester -d <DOMINIO> -b all
     +-- Google Dork: site:<DOMINIO> "@gmail.com"
     -> Lista email -> input per phishing e ulteriore OSINT
          |
          v
[3] Google Dorking
     +-- site:<DOMINIO> filetype:pdf
     +-- site:<DOMINIO> inurl:login
     +-- site:<DOMINIO> intitle:"index of /"
     -> Documenti esposti, pannelli admin, directory listing
          |
          v
[4] User Enumeration
     +-- sherlock <USERNAME>
     -> Profilo social del target (verifica manuale obbligatoria)
          |
          v
[OUTPUT] Intelligence report -> input per 03-web-attacks/ e 05-social-engineering/
```

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `h8mail` | Breach data | CLI (Python) | Ricerca automatizzata credenziali in breach |
| `HaveIBeenPwned` | Breach data | Web | Validazione manuale su fonte autorevole |
| `theHarvester` | Email/Subdomain harvesting | CLI | Aggregazione email e sottodomini da motori di ricerca |
| `Sherlock` | Username enumeration | CLI (Python) | Identity correlation su 300+ piattaforme |
| Google GHDB | Sensitive data exposure | Web | Google Hacking Database - query pre-costruite |
| `Maltego` | OSINT aggregator | GUI | Visualizzazione grafo OSINT (community edition gratuita) |
| `SpiderFoot` | OSINT aggregator | CLI/Web | Automazione OSINT multi-fonte (open source) |

> **Tool moderno consigliato:** `SpiderFoot HX` - rispetto al workflow manuale, automatizza la correlazione tra email, domini, breach e social media in un unico grafo navigabile. Per ambienti enterprise sostituisce ore di ricerca manuale.

---

## Registro Finding

| ID | Descrizione | Severity | File |
| :--- | :--- | :---: | :--- |
| `OSINT-001` | Credenziali target identificate in data breach pubblici | `Alto` | `breach-data/README.md` |
| `OSINT-002` | Esposizione email su dominio personale - superficie minima | `Informativo` | `email-harvesting/README.md` |
| `OSINT-003` | Documenti e pannelli login indicizzati su nasa.gov | `Variabile (Basso / Alto)` | `google-dorks/README.md` |
| `OSINT-004` | Identity correlation tramite username riutilizzato | `Basso` | `user-enumeration/README.md` |

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Identity Info: Credentials | `T1589.001` | Ricerca credenziali compromesse su HIBP e h8mail (OSINT-001) |
| Reconnaissance | Gather Victim Identity Info: Email Addresses | `T1589.002` | Harvesting email con theHarvester e Google Dorks sul dominio target (OSINT-002) |
| Reconnaissance | Search Open Websites/Domains: Search Engines | `T1593.002` | Google Dorking per individuare file PDF, pannelli login e directory listing esposti (OSINT-003) |
| Reconnaissance | Gather Victim Identity Info: Employee Names | `T1589.003` | Correlazione identita tramite username con Sherlock su 300+ piattaforme (OSINT-004) |
| Reconnaissance | Search Open Websites/Domains: Social Media | `T1593.001` | Enumerazione presenza social del target per profilazione e Social Engineering (OSINT-004) |

---

> **Nota:** Tutte le attivita documentate in questa sezione sono state eseguite su target autorizzati: dominio personale `nicholas-arcari.github.io`, target pubblico didattico `nasa.gov` (solo query Google, nessun accesso diretto), programma bug bounty pubblico. Nessuna credenziale identificata in breach e stata utilizzata per tentare accessi non autorizzati.
