# OSINT Passive: Google Dorking (Google Hacking)

> - **Fase:** Reconnaissance - Passive Information Gathering
> - **Visibilita:** Zero - le query rimangono sui server di Google, nessun contatto diretto con il target
> - **Prerequisiti:** Accesso a Google Search, conoscenza degli operatori avanzati, Google Hacking Database (GHDB)
> - **Output:** OSINT-003 - File sensibili, pannelli di login e directory listing indicizzati involontariamente dal target

---

Obiettivo: Utilizzare tecniche di ricerca avanzata (Google Dorks) per identificare informazioni sensibili, file esposti e pannelli di amministrazione indicizzati involontariamente dai motori di ricerca.

Target: `nasa.gov` (Target scelto per programma pubblico di divulgazione/scopo didattico)
Strumenti: Browser Web (Google Search Engine), Google Hacking Database (GHDB).

---

## 1 Introduzione Teorica

Le Google Dorks (o Google Hacking) consistono nell'utilizzo di operatori di ricerca avanzati per interrogare l'indice di Google in modo granulare.

A differenza di una normale Search Query (che cerca parole chiave nel testo), una Dork permette di filtrare per:

- Tipologia di file (`filetype:`)
- Struttura dell'URL (`inurl:`)
- Dominio specifico (`site:`)

Questa tecnica di OSINT Passiva permette di individuare vulnerabilità di Sensitive Data Exposure senza inviare alcun pacchetto diretto al server della vittima, rendendo l'attività invisibile ai log del target.

---

## 2 Esecuzione Tecnica

**ID Finding:** `OSINT-003` | **Severity:** `Variabile (Basso / Alto)`

La severity effettiva dipende da cio che si trova: file PDF con metadati generici (Basso), credenziali in chiaro o pannelli admin accessibili senza autenticazione (Alto).

#### A. Ricerca di Documenti Esposti (PDF/XLSX)

È stata eseguita una ricerca per individuare documenti PDF indicizzati sul dominio target, potenzialmente contenenti metadati o informazioni interne.

Dork Eseguita:

```Text
site:nasa.gov filetype:pdf "report"
```

#### B. Individuazione Sottodomini e Login

È stata effettuata una ricerca per mappare i portali di accesso o aree amministrative esposte.

Dork Eseguita:

```Text
site:nasa.gov inurl:login
```

Risultato: Sono stati identificati diversi portali di accesso (es. portali dipendenti, aree riservate) pubblicamente raggiungibili. [INSERISCI QUI LO SCREENSHOT DELLA LISTA DI URL]

#### C. Directory Listing (Index of)

È stata verificata la presenza di server con "Directory Listing" abilitato, che espongono il contenuto delle cartelle del server web.

Dork Eseguita:

```Text
site:nasa.gov intitle:"index of /"
```

Nota: Un risultato positivo indicherebbe una misconfiguration del server web (Information Disclosure).

---

## 3 Analisi e Conclusioni

L'attività di Google Dorking ha permesso di:
- Estendere la superficie di attacco: Individuando sottodomini non linkati dalla home page principale.
- Information Gathering: Raccogliendo documenti che potrebbero rivelare software in uso, nomi di dipendenti o procedure interne.

Remediation: Per mitigare questo rischio, le organizzazioni dovrebbero:
- Utilizzare il file `robots.txt` per impedire l'indicizzazione di aree sensibili.
- Eseguire regolarmente Dorking sul proprio dominio per verificare cosa è pubblico.
- Rimuovere i metadati dai documenti pubblici (PDF/DOCX).

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Search Open Websites/Domains: Search Engines | `T1593.002` | Utilizzo di operatori Google avanzati (site:, filetype:, inurl:, intitle:) per individuare file PDF, pannelli login e directory listing esposti su nasa.gov (OSINT-003) |

---

> **Nota:** Le ricerche Google Dork documentate sono state eseguite su nasa.gov esclusivamente a scopo didattico, sfruttando le query come utente anonimo senza accedere ad alcun sistema. Il programma di divulgazione pubblica della NASA permette la ricerca di informazioni pubblicamente disponibili per scopi educativi.