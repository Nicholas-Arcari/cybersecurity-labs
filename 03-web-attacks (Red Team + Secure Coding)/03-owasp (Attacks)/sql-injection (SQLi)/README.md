# SQL Injection (SQLi)

> - **Fase:** Web Attack - SQL Injection Testing
> - **Visibilita:** Media - richieste HTTP con payload nel parametro URL o nel corpo POST
> - **Prerequisiti:** Endpoint con parametri dinamici identificato, stack database noto (MySQL, MSSQL, PostgreSQL), proxy configurato
> - **Output:** Finding WEB-004 (injection manuale), WEB-011 (sqlmap), dump database completo, proof of concept auth bypass

---

## Introduzione

La SQL Injection e una delle vulnerabilita piu longeve e devastanti nel panorama della sicurezza web. Classificata da OWASP come A03:2021 (Injection), permette a un attaccante di inserire comandi SQL arbitrari nell'input dell'applicazione, manipolando le query al database backend.

La causa radice e quasi sempre la stessa: **concatenazione diretta dell'input utente nella stringa SQL** invece di usare Prepared Statements (query parametrizzate). Questa pratica permette all'attaccante di modificare la struttura logica della query, non solo i suoi valori.

Le tipologie principali di SQLi e il loro meccanismo:

| Tipologia | Meccanismo | Quando usarla |
| :--- | :--- | :--- |
| Error-based | Il database restituisce messaggi di errore con info sulla struttura | Stack tecnologico noto, messaggi verbosi |
| UNION-based | Aggiunge risultati di query arbitrarie alla risposta normale | La query originale restituisce output visibile |
| Boolean-based Blind | L'app risponde diversamente a condizioni vere/false | Nessun output diretto, solo comportamento binario |
| Time-based Blind | Si usa `SLEEP(N)` per inferire informazioni dal ritardo | Nessun output, nessuna differenza di comportamento |
| Out-of-Band | L'app esfiltra dati verso un server esterno (DNS, HTTP) | Difese perimetrali bloccano le altre tecniche |

---

## Struttura della cartella

```
sql-injection (SQLi)/
+-- manual-payloads/   # Auth bypass, UNION-based, data dump manuale - WEB-004
+-- sql-map-data/      # sqlmap automatizzato - WEB-011
```

---

## `manual-payloads/` - SQL Injection Manuale

**ID Finding:** `WEB-004` | **Severity:** `Critico` | **CVSS v3.1:** 9.8

### Contesto operativo

L'approccio manuale alla SQLi e fondamentale per due motivi. Primo, permette di comprendere esattamente come funziona la query vulnerabile, rendendosi conto della struttura del database e delle difese presenti. Secondo, e spesso necessario quando sqlmap e bloccato dal WAF o quando il formato di risposta del server e non standard.

Il documento `manual-payloads/README.md` copre tre scenari progressivi:
- **Scenario A (Auth Bypass):** payload `admin' #` per bypassare il login senza conoscere la password. Il carattere `#` commenta il controllo della password nella query MySQL.
- **Scenario B (UNION-based):** enumerazione del numero di colonne, identificazione delle colonne visibili, fingerprinting del database (versione, utente corrente).
- **Scenario C (Data Dump completo):** accesso a `information_schema.tables` per elencare le tabelle, poi dump di username, password e dati di carte di credito dalla tabella `users`.

### Remediation

- **Azione immediata:** disabilitare i messaggi di errore verbose del database in produzione (impedisce il fingerprinting).
- **Azione strutturale:** riscrivere tutte le query usando Prepared Statements (PDO in PHP, `PreparedStatement` in Java, ORM con query parametrizzate).
- **Principio del minimo privilegio:** l'utente del database usato dall'app non dovrebbe avere accesso a `information_schema` ne permessi di scrittura non necessari.
- **Verifica:** usare sqlmap (`--level=5 --risk=3`) sul codice patchato per confermare che non ci siano piu vettori di iniezione.

---

## `sql-map-data/` - SQLi Automatizzata con sqlmap

**ID Finding:** `WEB-011` | **Severity:** `Critico` | **CVSS v3.1:** 9.8

### Contesto operativo

sqlmap e lo strumento standard per la verifica automatizzata e l'exploitation della SQL Injection. A differenza dell'approccio manuale, sqlmap rileva automaticamente il tipo di injection (boolean, error, union, time-based), il database backend e la sua versione, e automatizza l'intero processo di data exfiltration.

Il documento `sql-map-data/README.md` documenta l'exploitation completa dell'endpoint `artists.php`:
- **Phase 1 (Fingerprinting):** identificazione del DBMS (MySQL 5.1+), utente corrente (`acuart@localhost`) e database attivo (`acuart`).
- **Phase 2 (Database Enum):** dump delle 8 tabelle del database `acuart`.
- **Phase 3 (Data Exfiltration):** dump completo della tabella `users` con salvataggio in CSV locale.

Il finding WEB-011 presenta una violazione PCI-DSS critica: i numeri di carte di credito (PAN) sono memorizzati in chiaro nel database, configurando una violazione diretta del PCI-DSS Requirement 3.4.

### Remediation

- **Immediate:** Prepared Statements su tutti gli endpoint (vedi `manual-payloads/`).
- **Password:** migrare a bcrypt/Argon2id con salting. Mai salvare password in chiaro.
- **PAN cards:** tokenizzazione tramite Payment Gateway certificato PCI-DSS. Non memorizzare mai il numero completo della carta se non strettamente necessario.
- **WAF:** ModSecurity o Cloudflare WAF con ruleset SQLi per bloccare pattern sqlmap noti.

---

## Flusso operativo consigliato

```
[1] Identificare endpoint con parametri dinamici
     +-- URL GET: ?id=1, ?artist=1, ?cat=3
     +-- Form POST: login, ricerca, filtri
              |
              v
[2] Test di conferma manuale (manual-payloads/)
     +-- payload: ' -> errore SQL? (conferma iniezione)
     +-- payload: ' OR 1=1 -- -> auth bypass?
     +-- payload: ORDER BY N -> numero colonne
              |
              v
[3] Enumerazione UNION-based (se output visibile)
     +-- UNION SELECT 1,2,3 -> quali colonne sono visibili?
     +-- UNION SELECT 1,version(),user() -> fingerprinting
     +-- UNION SELECT ... FROM information_schema.tables -> elenco tabelle
              |
              v
[4] Automatizzare con sqlmap (sql-map-data/)
     +-- sqlmap -u "URL?param=1" --banner --current-db --current-user
     +-- sqlmap -u "URL?param=1" -D <DB> --tables
     +-- sqlmap -u "URL?param=1" -D <DB> -T users --dump
```

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `sqlmap` | SQL Injection framework | CLI - Attiva | Exploitation automatizzata, dump database |
| `Burp Suite Repeater` | Web proxy | GUI - Manuale | Test manuale iterativo di payload SQL |
| `Burp Suite Intruder` | Web proxy | GUI - Semi-auto | Fuzzing parametri con payload list |
| `ghauri` | SQLi tool moderno | CLI - Attiva | Alternativa a sqlmap, evasione WAF migliorata |
| `havij` | SQLi framework | GUI - Attiva | Tool legacy (non mantenuto), evitare in prod |

> **Tool moderno consigliato:** `ghauri` - alternativa moderna a sqlmap con migliori capacita di evasione WAF e supporto per tecniche di injection avanzate. Installazione: `pip3 install ghauri`.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Exploitation della SQL Injection sul parametro `artist` e form di login di `testphp.vulnweb.com` (WEB-004, WEB-011) |
| Discovery | Account Discovery: Local Account | `T1087.001` | Enumerazione degli utenti del database tramite UNION injection su `information_schema.tables` (WEB-004) |
| Collection | Data from Information Repositories | `T1213` | Dump completo della tabella `users` con credenziali in chiaro e PAN di carte di credito (WEB-004, WEB-011) |
| Exfiltration | Exfiltration Over Web Service | `T1567` | Salvataggio del dump del database in file CSV locale tramite sqlmap (WEB-011) |
| Credential Access | Brute Force: Password Guessing | `T1110.001` | Utilizzo delle credenziali estratte (`test:test`) per accedere all'applicazione (WEB-004) |

---

> **Nota:** Le attivita di SQL Injection documentate sono state condotte su `testphp.vulnweb.com`,
> ambiente di addestramento pubblico di Acunetix intenzionalmente vulnerabile. I dump del database
> contenenti credenziali e numeri di carte di credito sono stati trattati come dati sensibili e
> non pubblicati in questo repository. In un engagement reale, tali dati sarebbero classificati
> come "Strictly Confidential" e consegnati esclusivamente al cliente in forma cifrata.
