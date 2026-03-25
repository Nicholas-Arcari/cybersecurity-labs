# 03 - OWASP Attacks

> - **Fase:** Web Attack - OWASP Top 10:2021 Exploitation
> - **Visibilita:** Variabile - da Media (richieste HTTP con payload) ad Alta (scanner automatici e attacchi brute force)
> - **Prerequisiti:** Stack tecnologico identificato (`02-web-recon`), proxy configurato (`01-proxy-tools`), endpoint di input identificati
> - **Output:** Finding WEB-004..011, proof of concept per ogni vulnerabilita OWASP, remediation con codice sicuro

---

## Introduzione

L'OWASP Top 10 e la lista delle vulnerabilita piu critiche nelle applicazioni web, aggiornata periodicamente dalla Open Web Application Security Project Foundation. La versione 2021 introduce categorie nuove rispetto alle precedenti: Insecure Design (A04), Security Logging and Monitoring Failures (A09) e Server-Side Request Forgery (A10).

Questa sezione documenta l'exploitation pratica delle categorie OWASP piu rilevanti identificate nel target `testphp.vulnweb.com` e negli ambienti di laboratorio locali:

| Categoria OWASP Top 10:2021 | Finding Correlato | Sottocartella |
| :--- | :--- | :--- |
| A01:2021 - Broken Access Control | WEB-010 (Session Hijacking) | `auth-attacks/` |
| A02:2021 - Cryptographic Failures | WEB-010 (cookie senza flag Secure) | `auth-attacks/` |
| A03:2021 - Injection | WEB-004, WEB-008, WEB-011 | `sql-injection/`, `ssti/` |
| A07:2021 - Identification & Auth Failures | WEB-009 (Brute Force), WEB-010 | `auth-attacks/` |
| A03:2021 - Injection (XSS) | WEB-005, WEB-006, WEB-007 | `xss/` |

La filosofia di questa sezione e la **doppia prospettiva**: ogni tecnica offensiva e accompagnata dalla root cause analysis e dal pattern di fix sicuro, perche comprendere il perche di una vulnerabilita e altrettanto importante per un analista quanto saperla sfruttare.

---

## Struttura della cartella

```
03-owasp (Attacks)/
+-- auth-attacks/             # Autenticazione e gestione sessioni
|   +-- bruteforce-web/       # Hydra su form HTTP/POST - WEB-009
|   +-- session-hijacking/    # Cookie stealing, XSS, ARP spoofing - WEB-010
+-- sql-injection (SQLi)/     # SQL Injection su MySQL
|   +-- manual-payloads/      # Auth bypass, UNION-based, data dump - WEB-004
|   +-- sql-map-data/         # sqlmap automatizzato + violazione PCI-DSS - WEB-011
+-- ssti/                     # Server-Side Template Injection Jinja2 - WEB-008
+-- xss (Cross-Site Scripting)/  # Cross-Site Scripting
    +-- reflected/            # Reflected XSS su parametro URL - WEB-005
    +-- stored/               # Stored XSS su campo profilo - WEB-006
    +-- xss-hunter-payloads/  # Blind XSS con OOB callback - WEB-007
```

---

## `auth-attacks/` - Authentication & Session Attacks

### Contesto operativo

Le vulnerabilita di autenticazione e gestione delle sessioni sono tra le piu impattanti perche permettono di impersonare utenti legittimi, compresi gli amministratori. La differenza tra Brute Force e Session Hijacking e il punto di attacco: il primo attacca le credenziali (prima del login), il secondo attacca la sessione gia stabilita (dopo il login).

Vedere `auth-attacks/README.md` per la guida completa.

**Finding:** `WEB-009` (Brute Force) e `WEB-010` (Session Hijacking).

---

## `sql-injection (SQLi)/` - SQL Injection

### Contesto operativo

La SQL Injection e una delle vulnerabilita piu longeve e devastanti nel panorama web. Consiste nell'iniezione di comandi SQL arbitrari attraverso input utente non sanitizzato, permettendo all'attaccante di manipolare le query al database.

Le tipologie principali:
- **Error-based:** il database restituisce messaggi di errore con informazioni sulla struttura.
- **UNION-based:** permette di aggiungere risultati di query arbitrarie alla risposta.
- **Blind Boolean-based:** l'applicazione risponde in modo diverso a condizioni vere/false.
- **Time-based Blind:** si usa il ritardo di risposta per inferire informazioni (es. `SLEEP(5)`).

La causa radice e quasi sempre la stessa: concatenazione diretta dell'input utente nella stringa SQL, invece di usare Prepared Statements.

Vedere `sql-injection/README.md` per la guida completa.

**Finding:** `WEB-004` (manuale) e `WEB-011` (sqlmap automatizzato).

---

## `ssti/` - Server Side Template Injection

### Contesto operativo

La SSTI e una vulnerabilita critica che si verifica quando l'input utente viene inserito direttamente nel template prima che il motore di rendering lo elabori. Il motore interpreta allora l'input come codice di template (es. `{{ 7*7 }}` in Jinja2) invece che come semplice testo.

La SSTI permette spesso di raggiungere la Remote Code Execution perche i motori di template moderni (Jinja2, Twig, Freemarker) hanno accesso a classi del linguaggio sottostante che permettono di invocare comandi di sistema.

**Finding:** `WEB-008` (SSTI Jinja2 RCE).

---

## `xss (Cross-Site Scripting)/` - XSS

### Contesto operativo

Il Cross-Site Scripting permette a un attaccante di iniettare codice JavaScript arbitrario che viene eseguito nel browser della vittima nel contesto del dominio legittimo. Questo bypassa la Same-Origin Policy e permette l'accesso ai cookie, al DOM e alle credenziali salvate.

Le tre varianti hanno impatto e visibilita diversi:

| Variante | Persistenza | Target | Visibilita |
| :--- | :--- | :--- | :--- |
| Reflected (WEB-005) | No (per richiesta) | Chi clicca il link malevolo | Bassa (URL con payload) |
| Stored (WEB-006) | Si (nel database) | Tutti i visitatori della pagina | Zero (il payload e nel DB) |
| Blind/OOB (WEB-007) | Si | Admin del pannello di gestione | Zero (il payload e lato server) |

La XSS Stored (WEB-006) e la piu critica in termini di impatto perche colpisce tutti gli utenti senza richiedere interazione specifica, e spesso conduce al furto di cookie di sessione degli amministratori.

---

## Flusso operativo consigliato

```
[1] Identificare i punti di input
     +-- form login, di ricerca, di commento
     +-- parametri URL (GET)
     +-- header HTTP (User-Agent, Referer)
              |
              v
[2] Test per SQL Injection (sql-injection/)
     +-- payload manuale: ' OR 1=1 --
     +-- se vulnerabile: UNION-based dump -> sqlmap --dump
              |
              v
[3] Test per XSS (xss/)
     +-- payload: <script>alert(1)</script>
     +-- se riflesso -> Reflected XSS (WEB-005)
     +-- se persistente -> Stored XSS (WEB-006)
     +-- se in area admin -> Blind XSS (WEB-007)
              |
              v
[4] Test per SSTI (ssti/)
     +-- payload: {{ 7*7 }} -> se ritorna 49 -> SSTI confermata
     +-- escalation a RCE: {{ self.__init__.__globals__ ... }}
              |
              v
[5] Test autenticazione (auth-attacks/)
     +-- brute force: hydra -l <USER> -P passlist.txt
     +-- session hijacking: XSS + document.cookie
```

---

## Registro Finding - OWASP Attacks

| ID | Descrizione | Severity | CVSS | Sottocartella |
| :--- | :--- | :---: | :---: | :--- |
| `WEB-004` | SQL Injection manuale: auth bypass e UNION-based data exfiltration | `Critico` | 9.8 | `sql-injection/manual-payloads/` |
| `WEB-005` | XSS Reflected - input URL riflesso senza encoding | `Medio` | 6.1 | `xss/reflected/` |
| `WEB-006` | XSS Stored - payload persistente nel database | `Alto` | 8.2 | `xss/stored/` |
| `WEB-007` | XSS Blind/OOB - callback su webhook.site da area admin | `Alto` | 8.2 | `xss/xss-hunter-payloads/` |
| `WEB-008` | SSTI Jinja2 - Remote Code Execution tramite template injection | `Critico` | 9.8 | `ssti/` |
| `WEB-009` | Brute Force autenticazione web - assenza rate limiting | `Alto` | 7.5 | `auth-attacks/bruteforce-web/` |
| `WEB-010` | Session Hijacking - cookie privo di flag HttpOnly e Secure | `Alto` | 8.0 | `auth-attacks/session-hijacking/` |
| `WEB-011` | SQLi automatizzata - dump DB completo con PAN carte di credito | `Critico` | 9.8 | `sql-injection/sql-map-data/` |

---

## Mappatura MITRE ATT&CK - Aggregata

| Tattica | Tecnica | ID MITRE | Finding Correlato |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | WEB-004, WEB-005, WEB-006, WEB-008, WEB-011 |
| Credential Access | Brute Force: Password Guessing | `T1110.001` | WEB-009 |
| Credential Access | Brute Force: Password Spraying | `T1110.004` | WEB-009 |
| Credential Access | Steal Web Session Cookie | `T1539` | WEB-005, WEB-006, WEB-007, WEB-010 |
| Collection | Man-in-the-Middle: AiTM HTTPS Interception | `T1557.002` | WEB-010 |
| Collection | Browser Session Hijacking | `T1185` | WEB-007, WEB-010 |
| Execution | Command and Scripting Interpreter: Python | `T1059.006` | WEB-008 |
| Execution | Command and Scripting Interpreter: Unix Shell | `T1059.004` | WEB-008 |
| Persistence | Server Software Component: Web Shell | `T1505.003` | WEB-006 |
| Defense Evasion | Use Alternate Authentication Material: Web Session Cookie | `T1550.004` | WEB-010 |
| Discovery | Account Discovery: Local Account | `T1087.001` | WEB-004 |
| Discovery | File and Directory Discovery | `T1083` | WEB-008 |
| Collection | Data from Information Repositories | `T1213` | WEB-004, WEB-011 |
| Exfiltration | Exfiltration Over Web Service | `T1567` | WEB-011 |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | WEB-005 |
| Reconnaissance | Gather Victim Identity Information | `T1589` | WEB-007 |
| Credential Access | Modify Authentication Process | `T1556` | WEB-009 |

---

> **Nota:** Tutte le attivita di exploitation documentate in questa sezione sono state condotte su
> ambienti di laboratorio intenzionalmente vulnerabili: `testphp.vulnweb.com` (Acunetix Art,
> ambiente pubblico di test) e applicazioni Flask/Python in ambiente locale. Qualsiasi attivita
> analoga su sistemi reali richiede autorizzazione scritta preventiva da parte del proprietario.
