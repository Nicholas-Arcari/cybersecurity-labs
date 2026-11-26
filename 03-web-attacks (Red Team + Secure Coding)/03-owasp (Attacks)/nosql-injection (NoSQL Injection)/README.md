> [English](README.en.md) | **Italiano**

# NoSQL injection

> - **Fase:** Web exploitation - OWASP A03:2021 Injection (query NoSQL costruita con input non sanitizzato)
> - **Visibilita:** Media - richieste con operatori NoSQL nei parametri; l'estrazione blind genera molte richieste con differenze booleane o ritardi
> - **Prerequisiti:** un'applicazione che costruisce una query verso un database NoSQL (tipicamente MongoDB) inserendo input dell'utente senza sanitizzazione/type-check
> - **Natura del documento:** metodologia + payload pratici per ambiente di laboratorio. Valori di esempio; nessun Finding ID fabbricato (prossimo `WEB-016`, da assegnare in lab).

- Obiettivo: manipolare una query NoSQL iniettando operatori (`$ne`, `$gt`, `$regex`, `$where`) per bypassare l'autenticazione, estrarre dati o, con `$where`, eseguire codice lato server.

---

## Executive summary

La NoSQL injection colpisce i database non relazionali (MongoDB in primis). A differenza della SQLi, non si
rompe una stringa di query ma si abusa del fatto che molti framework accettano come input **strutture dati**
(oggetti/array), non solo stringhe: un parametro atteso come stringa puo diventare un oggetto con un operatore
MongoDB (`{"$ne": null}`), alterando la logica della query. Gli impatti principali sono il bypass
dell'autenticazione, l'estrazione blind dei dati e, quando l'app usa l'operatore `$where` (che valuta
JavaScript lato server), l'esecuzione di codice.

La severity tipica e `Alto` (bypass auth + estrazione dati); sale a `Critico` quando `$where` porta a RCE.

## Contesto operativo (perche, prima del come)

Si cerca dove l'app riceve parametri che finiscono in una query MongoDB: login, filtri, ricerche. Il punto
chiave e il **type juggling**: se l'app legge `req.body.user` senza forzarlo a stringa, l'attaccante puo
inviare un oggetto. In JSON si inietta direttamente l'operatore; in form URL-encoded si usa la notazione a
bracket (`param[$ne]=valore`) che molti parser convertono in oggetto. La decisione operativa e distinguere
bypass diretto, estrazione blind (booleana con `$regex`) e `$where` (RCE).

## Esecuzione / comandi

### Bypass dell'autenticazione

```
# Corpo JSON: la password diventa un oggetto con $ne (diverso da null) -> sempre vero
{"username": "admin", "password": {"$ne": null}}

# Variante form URL-encoded (bracket notation, convertita in oggetto da molti parser)
username=admin&password[$ne]=

# Seleziona il primo utente senza conoscere lo username
username[$ne]=&password[$ne]=
```

### Estrazione blind (booleana) con $regex

```
# Conferma carattere per carattere la password/campo di 'admin'
{"username": "admin", "password": {"$regex": "^a"}}   -> risposta "login ok" se inizia per 'a'
{"username": "admin", "password": {"$regex": "^ad"}}  -> ... fino alla stringa completa
```

### Operatori utili e $where (RCE)

```
{"age": {"$gt": ""}}                 # confronti per filtrare/estrarre
{"$where": "sleep(5000)"}            # time-based: conferma l'esecuzione JS lato server (blind)
{"$where": "this.password.length>8"} # valutazione JavaScript sui documenti
```

Output illustrativo (rappresentativo):

```
# con password[$ne]= il login riesce senza password valida
HTTP/1.1 302 Found   Location: /dashboard   <-- autenticazione bypassata
```

## Analisi dei risultati

Il bypass conferma che l'input non e vincolato a stringa (type juggling). L'estrazione `$regex` recupera campi
sensibili carattere per carattere; un `$where` che introduce un ritardo misurabile dimostra l'esecuzione di
JavaScript lato server (RCE, severity `Critico`). Se l'app forza i tipi (cast a stringa) e disabilita `$where`,
il vettore e chiuso.

### Analisi teorica

E il problema dati/istruzioni [Su & Wassermann 2006] nella variante "struttura dati": l'app si aspetta un valore
scalare ma il protocollo (JSON/bracket) permette di passare un operatore, che il driver interpreta come logica.
La contromisura e il **type enforcement**: validare che l'input sia del tipo atteso (stringa, non oggetto),
usare query parametrizzate/ODM con schema, e disabilitare l'esecuzione di JavaScript server-side (`$where`,
`mapReduce`).

## Remediation (blue team)

**Rilevamento (WAF/SIEM).**
- Parametri contenenti operatori NoSQL (`$ne`, `$gt`, `$regex`, `$where`) o bracket notation (`param[$...]`).
- Corpi di richiesta in cui un campo atteso scalare arriva come oggetto/array.
- Query con `$where`/`mapReduce` originate da input utente.

**Hardening (secure coding).**
- Forzare il tipo dell'input (cast a stringa) prima di costruire la query; validare con uno schema (Mongoose).
- Non passare mai oggetti grezzi dell'utente al driver; sanitizzare le chiavi che iniziano con `$`.
- Disabilitare l'esecuzione di JavaScript server-side (`$where`, `mapReduce`) se non necessaria.

---

## Scenario reale: proiezione post-exploitation

> Vale per l'esito "bypass auth / estrazione / RCE via $where" (severity Alto/Critico).

### Prospettiva attaccante (red team)

**Punto di partenza:** endpoint con backend MongoDB e input non tipizzato.

**Passo successivo immediato:** bypass dell'autenticazione come admin, poi estrazione blind dei dati o RCE con
`$where`.

**Kill chain proiettata:**

```
NoSQL injection (type juggling)
        |
        v
Bypass auth come admin / estrazione blind di credenziali
        |
        v
$where -> esecuzione JavaScript lato server (RCE) dove supportato
        |
        v
Accesso ai dati / compromissione del server applicativo
```

**Impatto potenziale:** dall'accesso non autorizzato all'esfiltrazione dell'intera collezione; con `$where`,
esecuzione di codice.

**Vettori di monetizzazione tipici:** furto e rivendita dei dati; accesso ad aree riservate; pivot sul server.

### Prospettiva difensore (blue team)

**Rilevamento:** operatori `$` nei parametri; campi scalari ricevuti come oggetti; uso di `$where`.

**Indicatori di compromissione (IoC):** richieste con `[$ne]`/`[$regex]`; picchi di richieste quasi identiche
(estrazione blind); query `$where` con funzioni come `sleep`.

**Contenimento:** blocco del pattern via WAF; rotazione delle credenziali esposte; indagine sugli accessi.

**Eradicazione e hardening:** type enforcement, schema validation, disabilitazione di `$where`.

**Lezione difensiva:** la NoSQL injection mostra che "niente stringhe concatenate" non basta: se l'input puo
essere una struttura dati, va vincolato il tipo. La difesa e nel type enforcement, non nel filtro dei caratteri.

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Burp Suite` | proxy/scanner | web - attivo | modifica dei parametri in oggetti/operatori; test del type juggling |
| `NoSQLMap` | exploit tool | cli - attivo | automazione di nosql injection (mongodb): bypass, estrazione, `$where` |
| `nosqli` | scanner | cli - attivo | rilevamento automatizzato di nosql injection |

## Note di metodologia

In lab reale (app Node/Express + MongoDB o un target didattico) i dati da documentare: il bypass riuscito, i
campi estratti via `$regex` e l'eventuale RCE con `$where`. Le credenziali reali vanno redatte nel report.

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | sfruttamento della query nosql non sanitizzata su un'applicazione esposta. |
| collection | data from information repositories | `T1213` | estrazione di dati dal database nosql via operatori di injection. |
| execution | command and scripting interpreter | `T1059` | esecuzione di javascript lato server tramite l'operatore `$where`. |

---

## Correlazioni con altri finding

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| [sql injection](<../sql-injection (SQLi)/README.md>) | nosql injection | stessa classe (injection), motore nosql; bypass via type juggling |
| [02-web-recon](<../../02-web-recon (Enumeration)/README.md>) | nosql injection | l'enumerazione individua gli stack con backend nosql (mongodb) |
| nosql injection | [secure-coding-lab](<../../06-secure-coding-lab (Defense)/README.md>) | la remediation (type enforcement, schema) si collega al secure coding |

---

> **Nota:** Contenuto didattico. I payload sono funzionanti e vanno eseguiti esclusivamente su applicazioni di proprieta o con autorizzazione esplicita, in ambiente di laboratorio. Gli output sono illustrativi.
