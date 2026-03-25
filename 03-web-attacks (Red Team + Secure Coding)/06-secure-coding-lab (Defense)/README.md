# 06 - Secure Coding Lab (Defense)

> - **Fase:** Secure Coding - Static Analysis (SAST) e Post-Remediation Verification
> - **Visibilita:** Zero - analisi locale del codice sorgente, nessun traffico verso target esterni
> - **Prerequisiti:** Comprensione delle vulnerabilita documentate nel modulo `03-owasp/` e `05-api-security/`
> - **Output:** Codice vulnerabile con analisi CWE, codice patchato con pattern sicuri, verifica dell'efficacia della remediation

---

## Introduzione

La sezione Secure Coding Lab e la componente che distingue un penetration tester esperto da un semplice esecutore di script. Comprendere **perche** una vulnerabilita esiste a livello di codice sorgente, e sapere come correggerla con i pattern appropriati, e la competenza fondamentale per:

- Redigere report tecnici professionali che giustificano le remediation raccomandate.
- Collaborare con i team di sviluppo in una logica DevSecOps.
- Verificare che le patch implementate siano effettivamente efficaci (re-testing post-remediation).

Il ciclo operativo di questa sezione e: **Vulnerabilita identificata** (nei moduli precedenti) -> **Analisi causa radice** (codice sorgente vulnerabile) -> **Pattern di fix** (codice sicuro) -> **Verifica** (re-test con lo stesso payload).

Per ogni vulnerabilita documentata nei moduli offensivi, questa sezione conserva i due artefatti:
- Il codice **vulnerabile** con annotazione CWE e spiegazione del meccanismo di sfruttamento.
- Il codice **patchato** con il pattern sicuro, le librerie raccomandate e la verifica dell'efficacia.

Questa prospettiva difensiva e valorizzata dai recruiter nel settore perche dimostra che la conoscenza offensiva e accompagnata dalla consapevolezza delle contromisure, qualita tipica di un Security Analyst senior piuttosto che di un semplice tester.

---

## Struttura della cartella

```
06-secure-coding-lab (Defense)/
+-- vulnerable-snippets (Bad-Code)/          # Codice vulnerabile con analisi CWE
+-- fixed-snippets (Good-Code)/              # Codice sicuro post-remediation
    +-- input-sanitization-examples/         # Output encoding per XSS (htmlspecialchars)
```

---

## `vulnerable-snippets/` - Codice Vulnerabile (SAST)

### Contesto operativo

Questa cartella contiene gli snippet di codice sorgente analizzati durante le fasi di attacco, con annotazioni sulla causa radice e la classificazione CWE (Common Weakness Enumeration) corrispondente.

Il documento `vulnerable-snippets/README.md` documenta due finding di analisi statica:

**Finding n.1: OS Command Injection (CWE-78)**
- File: `python-vuln-exec.py`
- Il problema: `os.system("ping -c 1 " + target_ip)` - concatenazione diretta dell'input utente nel comando di sistema.
- Proof of Concept: payload `8.8.8.8; cat /etc/passwd` ha prodotto il dump del file `/etc/passwd`.
- Severity: Critica (CVSS 10.0).

**Finding n.2: SQL Injection (CWE-89)**
- File: `php-vuln-sql.php`
- Il problema: `$query = "SELECT * FROM users WHERE id = " . $user_id;` - concatenazione dell'ID utente nella query SQL.
- Severity: Critica (CVSS 9.8).

---

## `fixed-snippets/` - Codice Sicuro (Post-Remediation)

### Contesto operativo

Questa cartella contiene le implementazioni sicure che sostituiscono il codice vulnerabile documentato in `vulnerable-snippets/`. Per ogni vulnerability, e presente:

1. Il codice sicuro con il pattern di fix appropriato.
2. La spiegazione tecnica del perche il pattern sicuro neutralizza il vettore di attacco.
3. La verifica dell'efficacia tramite re-test con lo stesso payload.

Il documento `fixed-snippets/README.md` documenta la correzione della SQL Injection tramite Prepared Statements (PHP PDO), con proof-of-defense: il payload `admin@example.com' OR '1'='1` non produce piu un login valido ma un errore corretto `Login Fallito`.

---

## `fixed-snippets/input-sanitization-examples/` - XSS Defense

### Contesto operativo

Questa sottocartella documenta il pattern di difesa primario contro il Cross-Site Scripting: l'Output Encoding tramite `htmlspecialchars()` in PHP.

Il documento `input-sanitization-examples/README.md` dimostra:
- Il codice vulnerabile: `echo $_GET['name']` che riflette il payload XSS nel DOM.
- Il codice sicuro: `htmlspecialchars($_GET['name'], ENT_QUOTES, 'UTF-8')` che converte `<script>` in `&lt;script&gt;`.
- Verifica visiva: screenshot del browser che mostra la stringa testuale invece del popup JavaScript.

---

## Principi di Secure Coding Applicati

### 1. Input Validation (Allow-list)

Non fidarsi mai dell'input utente. Validare che l'input sia nel formato atteso prima di elaborarlo:

```python
# SBAGLIATO: accettare qualsiasi input
target_ip = input("IP > ")
os.system("ping -c 1 " + target_ip)

# CORRETTO: validare che sia un IP valido prima di usarlo
import ipaddress
try:
    ipaddress.ip_address(target_ip)  # lancia ValueError se non e un IP valido
    subprocess.run(["ping", "-c", "1", target_ip])
except ValueError:
    print("Errore: input non valido")
```

### 2. Parameterized Queries (Prepared Statements)

Separare sempre il comando SQL dai dati:

```php
// SBAGLIATO: concatenazione
$query = "SELECT * FROM users WHERE id = " . $_GET['id'];

// CORRETTO: Prepared Statements con PDO
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id");
$stmt->execute(['id' => $_GET['id']]);
```

### 3. Output Encoding

Codificare l'output nel contesto corretto prima di renderizzarlo:

```php
// SBAGLIATO: echo diretto
echo $_GET['name'];

// CORRETTO: HTML entity encoding
echo htmlspecialchars($_GET['name'], ENT_QUOTES, 'UTF-8');
```

### 4. Subprocess senza Shell

Evitare l'esecuzione di comandi tramite shell string:

```python
# SBAGLIATO: usa la shell, interpreta metacaratteri (;, |, &&)
os.system("ping -c 1 " + user_input)

# CORRETTO: lista di argomenti, nessuna shell intermedia
subprocess.run(["ping", "-c", "1", user_input], shell=False)
```

### 5. Gestione sicura dei segreti

Non hardcodare mai chiavi e password nel codice sorgente:

```python
# SBAGLIATO: hardcoded
SECRET_KEY = "secret123"

# CORRETTO: variabili d'ambiente
import os
SECRET_KEY = os.environ.get("JWT_SECRET")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise ValueError("JWT_SECRET mancante o troppo debole")
```

---

## Tool SAST di riferimento

| Tool | Linguaggio | Tipo | Caso d'uso |
| :--- | :--- | :--- | :--- |
| `bandit` | Python | SAST CLI | Analisi statica per vulnerabilita comuni in Python (os.system, eval, pickle) |
| `semgrep` | Multi-language | SAST CLI | Analisi statica con regole custom, integrabile in CI/CD |
| `SonarQube` | Multi-language | SAST Web | Piattaforma enterprise per code review continuo |
| `snyk` | Multi-language | SAST Web/CLI | Analisi dipendenze e vulnerabilita nel codice |
| `phpcs-security-audit` | PHP | SAST CLI | Regole specifiche per vulnerabilita PHP (SQLi, XSS, RCE) |
| `eslint-plugin-security` | JavaScript | SAST CLI | Analisi statica per applicazioni Node.js |

---

## Flusso operativo consigliato

```
[1] Identificazione vulnerabilita (moduli offensivi)
     +-- SQLi trovata in login.php
     +-- XSS trovata in parametro URL
     +-- Command Injection in script Python
              |
              v
[2] Root Cause Analysis (vulnerable-snippets/)
     +-- isolare il codice responsabile
     +-- identificare il CWE corrispondente
     +-- documentare il proof of concept
              |
              v
[3] Implementazione fix (fixed-snippets/)
     +-- applicare il pattern sicuro appropriato
     +-- test unitario del caso limite (input malevolo)
              |
              v
[4] Verifica (re-test)
     +-- rieseguire il payload originale sul codice patchato
     +-- confermare che il server risponda in modo sicuro
     +-- documentare il "proof of defense"
              |
              v
[5] Integrazione CI/CD (opzionale)
     +-- aggiungere il tool SAST nella pipeline
     +-- bandit per Python, semgrep per multi-language
```

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione (difensiva) |
| :--- | :--- | :--- | :--- |
| (Mitigazione) | Exploit Public-Facing Application | `T1190` | Implementazione di Prepared Statements (PDO) per neutralizzare SQLi (CWE-89) |
| (Mitigazione) | Command and Scripting Interpreter: Unix Shell | `T1059.004` | Sostituzione di `os.system()` con `subprocess.run(list)` per neutralizzare OS Command Injection (CWE-78) |
| (Mitigazione) | Exploit Public-Facing Application | `T1190` | Implementazione di `htmlspecialchars()` per neutralizzare XSS Reflected e Stored |
| (Mitigazione) | Brute Force: Password Cracking | `T1110.002` | Sostituzione di JWT weak secret con chiave random 64+ char da variabili d'ambiente (WEB-012) |

---

> **Nota:** Il codice vulnerabile documentato in questa sezione e fornito esclusivamente a scopo
> didattico per illustrare le cause radice delle vulnerabilita identificate nei test. Non deve
> essere utilizzato in ambienti di produzione. I pattern di fix documentati seguono le linee guida
> OWASP Secure Coding Practices e i CWE Top 25 del MITRE. Per una revisione completa del codice
> in un contesto di engagement reale, integrare il SAST in un processo di Code Review formale.
