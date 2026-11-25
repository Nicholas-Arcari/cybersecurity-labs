> [English](README.en.md) | **Italiano**

# 01 - OSINT passivo (open source intelligence)

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
|   +-- README.md             <- OSINT-004: identity correlation (Sherlock)
|   +-- img/                  <- screenshot del lab
|
+-- osint-frameworks/
|   +-- README.md             <- OSINT-005: automazione e correlazione (SpiderFoot, recon-ng, Maltego)
|   +-- img/                  <- screenshot del lab
|
+-- code-secret-leakage/
    +-- README.md             <- OSINT-006: segreti nei repository pubblici (GitHub dorking, gitleaks, TruffleHog)
    +-- img/                  <- screenshot del lab
```

---

## `breach-data/` - Analisi credenziali compromesse

**ID Finding:** `OSINT-001` | **Severity:** `Alto`

L'analisi dei data breach pubblici permette di identificare credenziali compromesse associate al target. Se un dipendente ha riutilizzato la stessa password tra un vecchio servizio violato (es. LinkedIn 2012) e la VPN aziendale, un attaccante puo ottenere accesso immediato senza alcuna tecnica di exploitation.

Tool principali: `h8mail` (CLI), `HaveIBeenPwned` (Web).

**Lezione appresa da questo lab:** i tool CLI dipendono dalla disponibilita delle API esterne. Un risultato "non compromesso" da riga di comando va sempre validato manualmente sul portale HIBP.

---

## `email-harvesting/` - Mappatura email esposte

**ID Finding:** `OSINT-002` | **Severity:** `Informativo`

L'Email Harvesting identifica gli indirizzi email associati a un dominio target, sia attraverso tool automatizzati (`theHarvester`) sia tramite Google Dorking mirato. Le email trovate costituiscono la lista di target per campagne di Spear Phishing.

In questo lab: audit del dominio personale `nicholas-arcari.github.io`. Risultato: superficie di attacco minima, 0 email dirette indicizzate.

---

## `google-dorks/` - Sensitive data exposure tramite motori di ricerca

**ID Finding:** `OSINT-003` | **Severity:** `Variabile (Basso / Alto)`

Le Google Dorks sfruttano operatori avanzati (`site:`, `filetype:`, `inurl:`, `intitle:`) per trovare file sensibili, pannelli di login e directory listing indicizzati per errore. La severity dipende da cosa si trova: da una lista di PDF (Basso) a credenziali in chiaro o pannelli di amministrazione accessibili (Alto).

Target: `nasa.gov` (programma pubblico di divulgazione, solo scopo didattico).

---

## `user-enumeration/` - Identity correlation e user tracking

**ID Finding:** `OSINT-004` | **Severity:** `Basso`

La User Enumeration passiva sfrutta la tendenza degli utenti a riutilizzare lo stesso handle su piattaforme diverse. Con `Sherlock` si interrogano 300+ siti per verificare la presenza di un username, costruendo un profilo completo del target utile per Social Engineering.

Attenzione critica: i falsi positivi sono frequenti. Ogni hit va verificato manualmente prima di essere usato in un report.

---

## `osint-frameworks/` - Automazione e correlazione OSINT

**ID Finding:** `OSINT-005` | **Severity:** `Variabile (Informativo / Alto)`

Le tecniche manuali precedenti non scalano su target reali. I framework OSINT (`SpiderFoot`, `recon-ng`, `Maltego`) automatizzano la raccolta da centinaia di fonti e, soprattutto, la **correlazione** tra dati eterogenei, costruendo il grafo completo del target. Il valore non e il singolo dato ma la rete di relazioni: un'email che porta a un breach, a un username, a un repository con un segreto.

Documentazione completa dei tre framework, del workflow combinato e della gestione della visibilita (moduli passivi vs attivi) nel README dedicato.

---

## `code-secret-leakage/` - Segreti nei repository pubblici

**ID Finding:** `OSINT-006` | **Severity:** `Variabile (Alto / Critico)`

Il leakage di segreti nei repository di codice pubblici e uno dei vettori di accesso iniziale piu frequenti: credenziali, API key e chiavi private committate per errore e rimaste permanentemente nella **storia git**, recuperabili anche dopo la rimozione. A differenza di altre tecniche OSINT, produce spesso credenziali direttamente utilizzabili.

Il README dedicato copre il GitHub/GitLab dorking manuale, la scansione automatica della history con `gitleaks` e la verifica di validita con `TruffleHog`. La lista di username dei dipendenti da `user-enumeration/` (OSINT-004) e prerequisito diretto per la ricerca sui repository personali.

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
[5] OSINT Framework Automation (correlazione)
     +-- spiderfoot -s <TARGET> -u passive
     +-- recon-ng (workflow ripetibile) / maltego (grafo visuale)
     -> Grafo OSINT correlato da fonti multiple (OSINT-005)
          |
          v
[6] Code & Secret Leakage
     +-- github dorking (org:<TARGET> filename:.env)
     +-- gitleaks detect / trufflehog --only-verified
     -> Credenziali e chiavi esposte nei repository pubblici (OSINT-006)
          |
          v
[OUTPUT] Intelligence report -> input per 03-web-attacks/, 05-social-engineering/, 07-post-exploitation/, 10-cloud-security/
```

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `h8mail` | breach data | cli (python) | ricerca automatizzata credenziali in breach |
| `HaveIBeenPwned` | breach data | web | validazione manuale su fonte autorevole |
| `theHarvester` | email/subdomain harvesting | cli | aggregazione email e sottodomini da motori di ricerca |
| `Sherlock` | username enumeration | cli (python) | identity correlation su 300+ piattaforme |
| google ghdb | sensitive data exposure | web | google hacking database - query pre-costruite |
| `Maltego` | osint aggregator | gui | visualizzazione grafo osint (community edition gratuita) |
| `SpiderFoot` | osint aggregator | cli/web | automazione osint multi-fonte (open source) |
| `recon-ng` | osint framework | cli (modulare) | workflow osint ripetibile con database e reportistica |
| `gitleaks` | secret scanning | cli | scansione della history git alla ricerca di segreti |
| `TruffleHog` | secret scanning | cli | scansione repository con verifica di validita dei segreti |

> **Tool moderno consigliato:** `SpiderFoot HX` - rispetto al workflow manuale, automatizza la correlazione tra email, domini, breach e social media in un unico grafo navigabile. Per ambienti enterprise sostituisce ore di ricerca manuale.

---

## Registro finding

| id | descrizione | severity | file |
| :--- | :--- | :---: | :--- |
| `OSINT-001` | credenziali target identificate in data breach pubblici | `Alto` | `breach-data/README.md` |
| `OSINT-002` | esposizione email su dominio personale - superficie minima | `Informativo` | `email-harvesting/README.md` |
| `OSINT-003` | documenti e pannelli login indicizzati su nasa.gov | `Variabile (Basso / Alto)` | `google-dorks/README.md` |
| `OSINT-004` | identity correlation tramite username riutilizzato | `Basso` | `user-enumeration/README.md` |
| `OSINT-005` | correlazione osint automatica del target via framework multi-fonte | `Variabile (Informativo / Alto)` | `osint-frameworks/README.md` |
| `OSINT-006` | segreti (credenziali, api key, chiavi) esposti in repository pubblici | `Variabile (Alto / Critico)` | `code-secret-leakage/README.md` |

---

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| reconnaissance | gather victim identity info: credentials | `T1589.001` | ricerca credenziali compromesse su hibp e h8mail (OSINT-001) |
| reconnaissance | gather victim identity info: email addresses | `T1589.002` | harvesting email con theharvester e google dorks sul dominio target (OSINT-002, OSINT-005) |
| reconnaissance | search open websites/domains: search engines | `T1593.002` | google dorking e github dorking per file, pannelli login, segreti esposti (OSINT-003, OSINT-006) |
| reconnaissance | gather victim identity info: employee names | `T1589.003` | correlazione identita tramite username con sherlock su 300+ piattaforme (OSINT-004) |
| reconnaissance | search open websites/domains: social media | `T1593.001` | enumerazione presenza social del target per profilazione e social engineering (OSINT-004, OSINT-005) |
| reconnaissance | search open technical databases | `T1596` | correlazione automatica multi-fonte e ricerca di segreti nei repository di codice pubblici (OSINT-005, OSINT-006) |
| credential access | unsecured credentials: credentials in files | `T1552.001` | estrazione di credenziali e chiavi cloud dai file esposti nella history git dei repository (OSINT-006) |

---

> **Nota:** Tutte le attivita documentate in questa sezione sono state eseguite su target autorizzati: dominio personale `nicholas-arcari.github.io`, target pubblico didattico `nasa.gov` (solo query Google, nessun accesso diretto), programma bug bounty pubblico. Nessuna credenziale identificata in breach e stata utilizzata per tentare accessi non autorizzati.
