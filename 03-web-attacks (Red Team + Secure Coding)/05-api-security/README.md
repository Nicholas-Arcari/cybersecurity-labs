# 05 - API Security

> - **Fase:** Web Attack - API Security Testing (OWASP API Top 10:2023)
> - **Visibilita:** Variabile - Bassa (JWT crack offline) / Media (GraphQL, REST con curl) / Bassa (IDOR - richieste legittime)
> - **Prerequisiti:** Endpoint API identificati, token JWT di un utente ordinario disponibile, documentazione API o schema GraphQL recuperabile
> - **Output:** Finding WEB-012 (JWT), WEB-013 (GraphQL RCE), WEB-014 (IDOR), accesso admin, dump dati utenti

---

## Introduzione

Il web moderno e costruito su API (Application Programming Interface). Dove una volta c'era HTML renderizzato dal server, oggi ci sono endpoint JSON consumati da client JavaScript, applicazioni mobile, microservizi e integrazioni B2B. Questo spostamento architetturale ha spostato anche la superficie di attacco.

Le vulnerabilita delle API differiscono da quelle delle applicazioni web tradizionali perche:

- **Nessuna interfaccia visibile:** non c'e un form da analizzare, solo endpoint HTTP con payload JSON/XML.
- **Autenticazione token-based:** JWT, OAuth 2.0 e API Key sostituiscono i cookie di sessione.
- **Controllo accessi implicito:** l'app si fida dell'ID fornito nella richiesta senza verificare che l'utente sia autorizzato a leggere quella risorsa (IDOR/BOLA).
- **Schema nascosto:** GraphQL espone un'intera struttura di dati tramite Introspection, spesso non disabilitata.

L'OWASP API Security Top 10:2023 documenta le vulnerabilita piu critiche nelle API moderne:

| Categoria | Finding | Sottocartella |
| :--- | :--- | :--- |
| API2:2023 - Broken Authentication | WEB-012 (JWT weak secret) | `jwt-tokens/` |
| API8:2023 - Security Misconfiguration | WEB-013 (GraphQL Introspection) | `graphql/` |
| API3:2023 - Broken Object Property Level Authorization | WEB-013 (Command Injection via GraphQL) | `graphql/` |
| API1:2023 - Broken Object Level Authorization (BOLA) | WEB-014 (IDOR) | `postman/` |

---

## Struttura della cartella

```
05-api-security/
+-- jwt-tokens/   # JWT weak secret, brute force offline, token forging - WEB-012
+-- graphql/      # GraphQL Introspection + Command Injection RCE - WEB-013
+-- postman/      # IDOR/BOLA su API bancaria - WEB-014
```

---

## `jwt-tokens/` - JWT Authentication Exploitation

**ID Finding:** `WEB-012` | **Severity:** `Critico` | **CVSS v3.1:** 9.8

### Contesto operativo

I JSON Web Token (JWT) sono il meccanismo di autenticazione piu diffuso nelle API moderne. Un JWT contiene tre parti codificate in Base64: header (algoritmo), payload (claims: utente, ruolo, scadenza), firma (hash HMAC o firma RSA).

La vulnerabilita documentata in `jwt-tokens/README.md` riguarda l'uso di una chiave segreta debole (`secret123`) per firmare token con l'algoritmo HS256 (simmetrico). Un attaccante che ottiene un token valido puo eseguire un brute force offline (senza generare traffico verso il server) per recuperare la chiave e quindi forgiare token arbitrari con qualsiasi ruolo, incluso `admin`.

La pericolosita e amplificata dalla natura offline del brute force: nessun IDS, nessun rate limiting, nessun lockout possono bloccare questo attacco.

---

## `graphql/` - GraphQL Introspection & Command Injection

**ID Finding:** `WEB-013` | **Severity:** `Critico` | **CVSS v3.1:** 9.8

### Contesto operativo

GraphQL e un linguaggio di query per API sviluppato da Facebook. La sua caratteristica distintiva e l'endpoint singolo (`/graphql`) che serve tutte le richieste, e la funzionalita di **Introspection**: una query speciale (`__schema`) che ritorna l'intera struttura del database, le query disponibili, i tipi di dato e i campi.

In produzione, l'Introspection dovrebbe essere disabilitata perche fornisce all'attaccante una mappa completa dell'API (incluse funzionalita non documentate). Il documento `graphql/README.md` documenta la kill chain completa:
1. Introspection via curl (bypass del blocco su interfaccia grafica).
2. Discovery di query non documentate: `systemDebug`, `systemDiagnostics`.
3. Command Injection sulla query `systemDebug(arg: String)`.
4. Remote Code Execution confermata con `; id`.
5. Esfiltrazione del file `config.py` con credenziali admin in chiaro.

---

## `postman/` - IDOR/BOLA Testing

**ID Finding:** `WEB-014` | **Severity:** `Critico` | **CVSS v3.1:** 9.1

### Contesto operativo

IDOR (Insecure Direct Object Reference), classificata come BOLA (Broken Object Level Authorization) nell'OWASP API Top 10:2023, e la vulnerabilita piu comune e critica nelle API. L'applicazione accetta un ID di risorsa nell'URL (es. `/api/balance/1001`) e restituisce i dati corrispondenti **senza verificare se l'utente autenticato e il proprietario di quella risorsa**.

Il documento `postman/README.md` documenta:
- Identificazione dell'endpoint vulnerabile `/api/balance/<account_id>`.
- Test manuale: cambio dell'ID da 1000 a 1001 restituisce i dati di un altro utente (invece di `403 Forbidden`).
- Automazione con script Python: enumerazione di tutti gli ID da 998 a 1005 e dump dei dati finanziari.
- Dati esfiltrati: saldo di Bob (150.000 €), Charlie/CEO (9.999.999 €), Dave/Admin (2.500 €).

---

## Flusso operativo consigliato

```
[1] Identificare il meccanismo di autenticazione
     +-- Cookie: JWT? OAuth? Session?
     +-- Header: Authorization: Bearer <TOKEN>?
     +-- Intercettare con Burp Suite per analizzare il formato
              |
              v
[2] JWT? -> jwt-tokens/
     +-- decodificare il token (jwt.io o jwt_tool)
     +-- verificare algoritmo: HS256 (simmetrico) o RS256 (asimmetrico)?
     +-- se HS256 -> brute force offline: hashcat -m 16500 <TOKEN> rockyou.txt
     +-- se chiave trovata -> forgere token con ruolo admin
              |
              v
[3] GraphQL? -> graphql/
     +-- curl -X POST /graphql -d '{"query":"{ __schema { types { name } } }"}'
     +-- se Introspection abilitata -> mappare tutte le query
     +-- cercare query con parametri String -> test Command Injection
              |
              v
[4] REST API con parametri ID? -> postman/
     +-- cambiare l'ID nella richiesta -> i dati cambiano senza errore 403?
     +-- IDOR confermata -> enumerare range di ID
     +-- documentare i dati esfiltrati
```

---

## Registro Finding - API Security

| ID | Descrizione | Severity | CVSS | Sottocartella |
| :--- | :--- | :---: | :---: | :--- |
| `WEB-012` | JWT weak secret (`secret123`) - forging token admin via brute force offline | `Critico` | 9.8 | `jwt-tokens/` |
| `WEB-013` | GraphQL Introspection abilitata + Command Injection RCE via `systemDebug` | `Critico` | 9.8 | `graphql/` |
| `WEB-014` | IDOR/BOLA - accesso dati finanziari di tutti gli utenti senza autorizzazione | `Critico` | 9.1 | `postman/` |

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `jwt_tool` | JWT analyzer | CLI - Offline | Analisi, brute force e forging di JWT |
| `hashcat` | Password cracker | CLI - Offline | Brute force hash JWT con GPU acceleration |
| `Burp Suite` | Web proxy | GUI - Manuale | Intercettazione e modifica di richieste API con JWT |
| `curl` | HTTP client | CLI | Test manuale endpoint GraphQL e REST |
| `Postman` | API client | GUI | Test interattivo API REST, Collections, scripting |
| `graphql-voyager` | GraphQL visualizer | Web UI | Visualizzazione grafica dello schema GraphQL |
| `clairvoyance` | GraphQL enum | CLI - Attiva | Enumerazione schema GraphQL anche senza Introspection |
| `nuclei` | Template-based | CLI - Attiva | Template OWASP API Top 10 e JWT vulnerabilities |

> **Tool moderno consigliato:** `jwt_tool` (ticarpi/jwt_tool) - strumento dedicato ai JWT, con supporto per brute force, modifica del payload, test di vulnerabilita (alg:none, RS256 to HS256). Installazione: `pip3 install jwt_tool`.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Credential Access | Brute Force: Password Cracking | `T1110.002` | Brute force offline della firma JWT HS256 con dizionario per recuperare la chiave `secret123` (WEB-012) |
| Defense Evasion | Use Alternate Authentication Material | `T1550` | Utilizzo del token JWT falsificato con ruolo admin per accedere a funzionalita privilegiate (WEB-012) |
| Lateral Movement | Valid Accounts: Cloud Accounts | `T1078.003` | Impersonazione dell'account admin tramite token JWT forgiato (WEB-012) |
| Reconnaissance | Active Scanning: Wordlist Scanning | `T1595.003` | GraphQL Introspection per mappare tutte le query disponibili, incluse quelle non documentate (WEB-013) |
| Execution | Command and Scripting Interpreter: Unix Shell | `T1059.004` | Command Injection tramite parametro `arg` della query `systemDebug` -> RCE con `; id` (WEB-013) |
| Collection | Data from Information Repositories | `T1213` | Esfiltrazione di credenziali admin da `config.py` e dump del database SQLite tramite RCE (WEB-013) |
| Discovery | Account Discovery | `T1087` | Enumerazione degli ID account sull'endpoint `/api/balance/<id>` per mappare tutti gli utenti (WEB-014) |
| Collection | Data from Information Repositories | `T1213` | Accesso ai dati finanziari di utenti non autorizzati tramite IDOR/BOLA (WEB-014) |
| Lateral Movement | Valid Accounts | `T1078` | Utilizzo dell'account legittimo per effettuare richieste IDOR su account altrui (WEB-014) |

---

> **Nota:** Le vulnerabilita API documentate sono state identificate e sfruttate su ambienti
> di laboratorio: DVGA (Damn Vulnerable GraphQL Application) in Docker locale per WEB-013,
> un'applicazione Flask/Python custom per WEB-012 e WEB-014. Tutte le attivita sono state
> condotte in perimetro autorizzato. L'exploitation di queste vulnerabilita su API di produzione
> senza autorizzazione viola i termini di servizio e costituisce un reato informatico.
