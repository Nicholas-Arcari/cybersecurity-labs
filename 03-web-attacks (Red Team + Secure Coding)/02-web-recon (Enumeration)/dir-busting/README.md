> [English](README.en.md) | **Italiano**

# Web Recon: Directory Busting con Gobuster

> - **Fase:** Web Attack - Web Application Enumeration
> - **Visibilita:** Media - Gobuster genera molte richieste HTTP in sequenza rapida, rilevabile da WAF e IDS
> - **Prerequisiti:** Target web identificato, wordlist disponibile (`common.txt`, `SecLists`), connessione di rete al target
> - **Output:** Lista di directory e file nascosti con codice HTTP, finding WEB-003 (CVS directory e .idea esposti)

---

**ID Finding:** `WEB-003` | **Severity:** `Alto` | **CVSS v3.1:** 7.5

---

Obiettivo: Identificare risorse nascoste (directory, file di backup, pannelli di amministrazione) non linkate direttamente nell'applicazione web, utilizzando tecniche di Brute-force.

Target: `http://testphp.vulnweb.com`

Strumenti: `Gobuster` (v3.x), `wget`, `Feroxbuster`

---

## 1 Introduzione Teorica

Il Directory Busting è una tecnica di Enumerazione Attiva.

A differenza dei crawler tradizionali che seguono i link visibili, il Directory Busting cerca di "indovinare" l'esistenza di percorsi nascosti inviando migliaia di richieste basate su una Wordlist.

I codici di stato HTTP rivelano la presenza delle risorse:

- 200 OK: La risorsa esiste.
- 301 Redirect: Spesso indica una directory esistente (es. `/admin`).
- 403 Forbidden: La risorsa esiste ma l'accesso è negato.

---

## 2 Esecuzione Tecnica: Setup & Scan

Poiché l'ambiente di test (Kali Purple) non disponeva delle wordlist standard preinstallate, è stato necessario eseguire una fase preliminare di setup per recuperare il dizionario d'attacco `common.txt`.

Fase A: Recupero Wordlist

```Bash
wget https://raw.githubusercontent.com/v0re/dirb/master/wordlists/common.txt
```

Fase B: Gobuster Scan È stato lanciato Gobuster in modalità dir (directory enumeration) contro il target.

```Bash
gobuster dir -u http://testphp.vulnweb.com -w common.txt
```

![](./img/Screenshot_2026-02-12_17_34_21.jpg)

Risultato (Output):

Analisi dei Findings: La scansione ha rivelato diverse directory critiche non visibili dalla homepage:

- `/admin` (Status 301): Un pannello di amministrazione. Questo è il punto di ingresso prioritario per tentare attacchi di SQL Injection o Brute Force sulle credenziali.
- `/secured` (Status 301): Una directory che suggerisce la presenza di dati sensibili o aree riservate.
- `/CVS` (Status 301): Esposizione di directory di versionamento (Legacy). Questo è un finding critico di "Information Disclosure" che potrebbe permettere il download del codice sorgente.
- `/cgi-bin` (Status 403): Una cartella di script server-side, protetta ma esistente.

---

## 3 Advanced Scanning: Feroxbuster (Recursive)

Per approfondire l'analisi, è stato utilizzato Feroxbuster, un tool scritto in Rust che supporta la ricorsione automatica.

A differenza di Gobuster, quando Feroxbuster individua una directory (es. `/admin`), avvia automaticamente una nuova scansione al suo interno senza intervento umano.

```Bash
feroxbuster -u http://testphp.vulnweb.com -w common.txt
```

Evidenza (Recursion in Action):

Differenze Rilevate: Grazie alla ricorsione, Feroxbuster ha mappato non solo la presenza di /admin, ma ha immediatamente identificato le risorse al suo interno (es. /admin/index.php, /admin/login.php) in un unico passaggio, riducendo drasticamente il tempo di enumerazione profonda.

---

## 4 Conclusioni

L'attività di Directory Busting ha avuto successo, rivelando una superficie di attacco molto più ampia rispetto alla semplice navigazione manuale. In uno scenario di Red Teaming reale, il passo successivo consisterebbe nel puntare strumenti di attacco specifici (come Burp Suite o SQLMap) verso la directory `/admin` appena scoperta.

---

## 5 Scenario Moderno: Docker & REST APIs (Localhost)

Le tecniche di Directory Busting non si limitano ai server web tradizionali, ma sono fondamentali anche per testare microservizi containerizzati (Docker) e RESTful APIs in fase di sviluppo (es. su `localhost:5173`).

Adattamenti necessari per l'ambiente Docker/API:

1.  Wordlist API-Specifiche:

    Le wordlist standard (`common.txt`) sono inefficaci contro le API, che usano percorsi strutturati (es. `/api/v1/user`).

    È necessario utilizzare liste dedicate come `api-endpoints.txt` (dalla raccolta SecLists) per individuare endpoint critici come `/health`, `/metrics`, `/swagger.json` o `/graphql`.

2.  Networking (VM vs Host):

    Se Kali Linux gira su una Virtual Machine e il container Docker gira sull'Host (Windows/Mac), puntare a `localhost` dalla VM non funzionerà. È necessario utilizzare l'indirizzo IP della macchina host nella rete locale (es. `gobuster dir -u http://192.168.X.X:<PORTA> ...`).

3.  Autenticazione (JWT Headers):

    Molte API restituiscono `401 Unauthorized` se non si presenta un token valido. Strumenti come Gobuster e Feroxbuster permettono di iniettare header di autenticazione per testare le aree riservate:

```Bash
# Esempio di scansione autenticata su API locale
gobuster dir -u http://localhost:<PORTA> -w api-endpoints.txt -H "Authorization: Bearer <IL_TUO_JWT_TOKEN>"
```

Valore nel Red Teaming:

Scansionare container locali permette di individuare Debug Endpoints (es. Spring Boot Actuators) dimenticati attivi, che spesso espongono variabili d'ambiente e credenziali del cloud prima ancora che l'app vada in produzione.

---

## Analisi a Basso Livello: Meccanica del Directory Busting

### Come Opera Gobuster a Livello HTTP

Gobuster invia richieste HTTP GET per ogni entry nella wordlist, analizzando il codice di risposta:

```
Gobuster                                 Web Server (Nginx/Apache)
    |                                          |
    |--- GET /admin HTTP/1.1 ----------------->|
    |<-- 301 Moved Permanently ----------------|  <-- directory ESISTE (redirect a /admin/)
    |                                          |
    |--- GET /backup HTTP/1.1 ---------------->|
    |<-- 404 Not Found ------------------------|  <-- NON esiste
    |                                          |
    |--- GET /CVS HTTP/1.1 ------------------>|
    |<-- 200 OK -------------------------------|  <-- ESISTE e accessibile
    |                                          |
    |--- GET /cgi-bin HTTP/1.1 --------------->|
    |<-- 403 Forbidden ------------------------|  <-- ESISTE ma protetta
    |                                          |
    |--- GET /.git/HEAD HTTP/1.1 ------------->|
    |<-- 200 OK "ref: refs/heads/main" --------|  <-- CRITICO: repo git esposto
```

### Codici HTTP e Significato Operativo

| Codice | Significato | Azione Red Team |
| :--- | :--- | :--- |
| `200` | Risorsa accessibile | Analizzare il contenuto, cercare credenziali/dati |
| `301/302` | Redirect (directory esiste) | Seguire il redirect, enumerare ricorsivamente |
| `401` | Autenticazione richiesta | Tentare credenziali default, brute force |
| `403` | Accesso negato | La risorsa esiste - tentare bypass (path traversal, encoding) |
| `404` | Non esiste | Skip (ma attenzione: custom 404 puo mascherare risorse) |
| `500` | Errore server | Possibile injection point (input non gestito) |

### Wordlist e Copertura

La scelta della wordlist determina l'efficacia del test:

```
/usr/share/wordlists/dirb/common.txt      ~4.600 entry   (rapida, copertura base)
/usr/share/seclists/Discovery/Web-Content/
    directory-list-2.3-medium.txt          ~220.000 entry (standard pentest)
    directory-list-2.3-big.txt             ~1.270.000 entry (esaustiva, lenta)
    raft-large-directories.txt             ~62.000 entry  (directory specifiche)
    raft-large-files.txt                   ~37.000 entry  (file specifici)
    api-endpoints.txt                      ~2.000 entry   (API REST)
    spring-boot.txt                        ~150 entry     (Spring Boot actuators)
```

### Gobuster: Flag Avanzati per Assessment Professionali

```Bash
# Scansione con estensioni file (cerca .php, .bak, .old, .conf)
gobuster dir -u http://target -w wordlist.txt -x php,bak,old,conf,txt,zip

# Scansione con thread paralleli e timeout
gobuster dir -u http://target -w wordlist.txt -t 50 --timeout 10s

# Filtrare per status code (ignorare 404 custom)
gobuster dir -u http://target -w wordlist.txt -b 404,403

# Scansione con header custom (cookie di sessione, token)
gobuster dir -u http://target -w wordlist.txt -c "PHPSESSID=abc123"

# Feroxbuster: recursion depth + output
feroxbuster -u http://target -w wordlist.txt -d 3 -o results.txt
```

---

## Scenario Reale: Da Directory Esposta a Source Code Leak (WEB-003)

Il finding `/CVS` (directory di versionamento legacy) e un esempio classico di information disclosure che porta a compromissione completa del codice sorgente.

### Kill Chain: Source Code Leak via Exposed VCS

```
Fase 1: Dir-busting rivela /CVS (WEB-003)
    |
    v
Fase 2: Download dei metadata CVS
    $ wget -r http://target/CVS/Entries
    $ wget -r http://target/CVS/Root
    [Entries contiene la lista di tutti i file nel repository]
    |
    v
Fase 3: Ricostruzione del codice sorgente
    [Per ogni file in Entries, tentare il download diretto]
    $ wget http://target/config.php
    $ wget http://target/includes/db_connect.php
    |
    v
Fase 4: Estrazione credenziali dal codice
    $ grep -r "password\|db_pass\|secret" *.php
    -> db_connect.php: $db_pass = "Pr0duction_P@ss!";
    |
    v
Fase 5: Accesso al database
    $ mysql -h db.target.com -u webapp -p'Pr0duction_P@ss!'
    -> Dump tabella utenti, dati clienti, credenziali admin
```

**Lo stesso scenario si applica a `.git/`:** se `/.git/HEAD` restituisce `200 OK`, l'intero repository puo essere ricostruito con tool come `git-dumper` o `GitTools`:

```Bash
# Ricostruzione completa di un repository git esposto
python3 git-dumper.py http://target/.git/ ./output
cd output && git log --oneline  # cronologia completa dei commit
git diff HEAD~5                  # codice sorgente + credenziali commesse per errore
```

**Impatto:** secondo HackerOne (2024), il 12% dei report di bug bounty con payout >$5.000 ha origine da directory sensibili scoperte tramite dir-busting (`.git/`, `.env`, `/backup/`, `/wp-config.php.bak`).

---

## Blue Team: Detection e Hardening

### Detection del Directory Busting

Il pattern di traffico del dir-busting e caratteristico:
- Centinaia/migliaia di richieste GET dallo stesso IP in pochi secondi
- Elevata percentuale di risposte 404 (>90% delle richieste)
- User-Agent di tool noti: `gobuster/3.x`, `feroxbuster/2.x`, `dirbuster`
- Richieste a path che non esistono nella sitemap dell'applicazione

**Regola WAF (ModSecurity):**
```
# Rate limiting: max 100 richieste 404 in 60 secondi dallo stesso IP
SecRule IP:404_COUNT "@gt 100" "phase:5,deny,status:429,id:100001,msg:'Dir busting detected'"
```

### Hardening

- **Rimuovere directory VCS:** `rm -rf .git/ .svn/ CVS/` dal webroot prima del deploy (o escluderle nel Dockerfile)
- **Bloccare l'accesso a file sensibili** nel web server:
  ```nginx
  # Nginx: bloccare accesso a directory e file sensibili
  location ~ /\.(git|svn|env|htaccess|htpasswd) {
      deny all;
      return 404;
  }
  location ~ \.(bak|old|orig|save|swp|conf)$ {
      deny all;
  }
  ```
- **Custom 404 consistente:** una pagina 404 custom che restituisce lo stesso contenuto per ogni path inesistente rende il dir-busting meno efficace (ma non impossibile - l'attaccante puo filtrare per dimensione della risposta)
- **Disabilitare directory listing:** `autoindex off;` (Nginx) / `Options -Indexes` (Apache)

---

## Esperienza di Laboratorio

Il confronto tra Gobuster e Feroxbuster ha rivelato un trade-off operativo fondamentale: Gobuster e piu veloce in modalita single-depth (una directory alla volta), ma richiede intervento manuale per esplorare le sotto-directory scoperte. Feroxbuster con ricorsione automatica (`-d 3`) ha scoperto `/admin/login.php` e `/admin/index.php` in un singolo passaggio, ma ha generato un volume di traffico significativamente maggiore - in un engagement reale con WAF attivo, la ricorsione aggressiva causerebbe un ban dell'IP sorgente.

La scelta della wordlist e stata determinante: `common.txt` (~4.600 entry) ha trovato `/admin`, `/CVS` e `/cgi-bin` in meno di 30 secondi. Una wordlist piu grande (`directory-list-2.3-medium.txt` con 220.000 entry) avrebbe impiegato minuti ma avrebbe potenzialmente scoperto file di backup (`.bak`, `.old`) e directory meno comuni. In un assessment reale, si parte dalla wordlist piccola per un triage rapido, poi si scala alla media/grande sui target piu interessanti.

La sezione Docker/API (Scenario 5) ha introdotto un aspetto critico per lo sviluppo moderno: i framework come Spring Boot espongono di default endpoint diagnostici (`/actuator/env`, `/actuator/health`, `/actuator/configprops`) che contengono credenziali e variabili d'ambiente. Cercarli con `gobuster dir -u http://localhost:8080 -w spring-boot.txt` durante lo sviluppo e una pratica di sicurezza preventiva che pochi team adottano.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Active Scanning: Vulnerability Scanning | `T1595.002` | Scansione con Gobuster e Feroxbuster su wordlist `common.txt` per identificare risorse nascoste su `testphp.vulnweb.com` |
| Reconnaissance | Active Scanning: Wordlist Scanning | `T1595.003` | Brute force delle directory con wordlist per scoprire `/admin`, `/CVS`, `.idea` e altri percorsi non linkati (WEB-003) |
| Discovery | File and Directory Discovery | `T1083` | Identificazione della directory `/CVS` (versionamento legacy) e della cartella `.idea` (configurazione IDE) esposte pubblicamente (WEB-003) |
| Collection | Data from Information Repositories | `T1213` | Accesso potenziale al codice sorgente tramite la directory `/CVS` esposta, che potrebbe permettere il download dei file sorgente dell'applicazione (WEB-003) |

---

> **Nota:** Le attivita di directory busting documentate sono state condotte su `testphp.vulnweb.com`,
> ambiente di addestramento pubblico e autorizzato. La sezione 5 documenta tecniche per ambienti
> Docker/API locali nell'ambito di test di sviluppo su applicazioni proprie. Il dir-busting su
> target in produzione non autorizzati e rilevabile dai sistemi di monitoring e costituisce un
> reato ai sensi dell'art. 615-ter c.p.