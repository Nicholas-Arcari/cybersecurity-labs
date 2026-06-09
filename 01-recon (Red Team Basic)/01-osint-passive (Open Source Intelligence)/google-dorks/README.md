> [English](README.en.md) | **Italiano**

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

## Analisi a Basso Livello: Operatori Avanzati e Combinazioni Offensive

### Operatori Google di secondo livello

Oltre agli operatori base (`site:`, `filetype:`, `inurl:`), esistono combinazioni avanzate che amplificano drasticamente l'efficacia della ricognizione:

| Operatore | Funzione | Esempio offensivo |
| :--- | :--- | :--- |
| `intitle:"index of"` | Directory listing esposti | `intitle:"index of" site:target.com /backup/` |
| `ext:sql \| ext:bak` | Backup database indicizzati | `site:target.com ext:sql "INSERT INTO"` |
| `inurl:wp-config.php` | File di configurazione WordPress | `inurl:wp-config.php "DB_PASSWORD"` |
| `filetype:env` | File .env con credenziali | `site:target.com filetype:env "DB_PASSWORD"` |
| `"phpinfo()"` | Pagine phpinfo() esposte | `site:target.com "phpinfo()" "mysql"` |
| `inurl:"/api/" "key"` | API key esposte | `site:target.com inurl:"/api/" "Authorization"` |
| `cache:` | Versione cached di pagine rimosse | `cache:target.com/admin/config` |

**Combinazioni multi-operatore per scenari reali:**

```
# Credenziali in file di configurazione esposti
site:target.com (ext:xml | ext:conf | ext:cfg) "password"

# Documenti interni con metadati (nomi dipendenti, software)
site:target.com filetype:pdf "confidential" | "internal use only"

# Pannelli di amministrazione non protetti
site:target.com inurl:admin | inurl:login | inurl:dashboard -www

# Ambienti di staging/development dimenticati
site:*.target.com -www intitle:"index of" | inurl:staging | inurl:dev
```

### Google Hacking Database (GHDB) e Automazione

Il GHDB (exploit-db.com/google-hacking-database) cataloga oltre 6.500 dork categorizzate. Per l'automazione su scala, tool come `pagodo` scaricano le dork dal GHDB e le eseguono in batch:

```Bash
# pagodo - Passive Google Dork automation
python3 pagodo.py -d target.com -g dorks/sensitive_directories.dorks -o results.txt

# GooFuzz - Fuzzing di file e directory tramite Google
goofuzz -t target.com -e pdf,xls,doc,sql,bak -d 5
```

L'automazione richiede cautela: Google implementa rate limiting aggressivo (CAPTCHA dopo ~50-100 query automatiche). L'uso di proxy e delay randomizzati (3-10 secondi tra query) e necessario per evitare il ban temporaneo dell'IP.

---

## Blue Team: Attack Surface Management e Protezione dall'Indicizzazione

**Monitoring proattivo:**
- Eseguire periodicamente Google Dork sul proprio dominio: `site:dominio.it filetype:pdf | filetype:xls | filetype:env`
- Configurare Google Search Console per monitorare le pagine indicizzate e richiedere la rimozione d'emergenza di URL sensibili
- Utilizzare Google Alerts per `site:dominio.it "password" | "confidential" | "internal"` come early warning

**Hardening:**
- `robots.txt`: bloccare l'indicizzazione di directory sensibili (`Disallow: /admin/`, `/backup/`, `/staging/`). **Attenzione:** robots.txt e pubblico e rivela l'esistenza delle directory bloccate - usarlo in combinazione con autenticazione, non come unica protezione
- Header `X-Robots-Tag: noindex`: applicare a livello di web server per risposte HTTP che non devono essere indicizzate (pagine admin, API endpoint)
- Metadata stripping: implementare pipeline automatica per rimuovere metadati da documenti prima della pubblicazione (`exiftool -all= documento.pdf`)
- Monitorare l'esposizione su Wayback Machine (`web.archive.org/web/*/dominio.it/*`) - contenuti rimossi dal sito potrebbero essere ancora accessibili nell'archivio

**Detection:**
- I Google Dork non generano traffico verso il target (le query restano su Google). L'unico indicatore indiretto e un picco di accessi a URL poco visitati (es. `/backup/`, `/admin/config`) dopo che un attaccante ha trovato il percorso tramite dorking e lo visita direttamente. Monitorare l'accesso a path sensibili nei log del web server con alert per referrer vuoto o assente.

---

## Esperienza di Laboratorio

L'esecuzione su nasa.gov ha dimostrato la scala del problema: un dominio di grandi dimensioni espone inevitabilmente una quantita significativa di informazioni indicizzate. La dork `site:nasa.gov filetype:pdf "report"` ha restituito migliaia di risultati - la maggior parte documenti scientifici pubblici, ma tra questi si annidano documenti con metadati interni (nomi di dipendenti, versioni software, percorsi di rete interni nel campo "Author" e "Producer" del PDF).

La dork `site:nasa.gov inurl:login` ha rivelato portali di accesso dedicati ai dipendenti. In un engagement reale, questi URL sarebbero il target primario per credential stuffing (combinando le email raccolte in OSINT-002 con le password dai breach in OSINT-001). La scelta di nasa.gov come target didattico e stata intenzionale: un dominio governativo con programma di divulgazione pubblica consente di documentare le tecniche senza rischi legali.

Un aspetto critico emerso dall'esercizio: la dork `intitle:"index of"` non ha prodotto risultati su nasa.gov - segno di un hardening corretto del web server. Su target meno maturi, questa singola dork puo esporre backup completi, file di configurazione e talvolta database dump dimenticati in directory non protette.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Search Open Websites/Domains: Search Engines | `T1593.002` | Utilizzo di operatori Google avanzati (site:, filetype:, inurl:, intitle:) per individuare file PDF, pannelli login e directory listing esposti su nasa.gov (OSINT-003) |

---

> **Nota:** Le ricerche Google Dork documentate sono state eseguite su nasa.gov esclusivamente a scopo didattico, sfruttando le query come utente anonimo senza accedere ad alcun sistema. Il programma di divulgazione pubblica della NASA permette la ricerca di informazioni pubblicamente disponibili per scopi educativi.