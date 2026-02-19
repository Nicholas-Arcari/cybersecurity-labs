# Source Code Review

---

## 1 Executive Summary

Durante la revisione statica del codice sorgente (SAST) effettuata sui moduli backend, sono state identificate due vulnerabilità critiche legate alla gestione insicura dell'input utente. Entrambi gli script ispezionati permettono l'iniezione di comandi (sul database o sul sistema operativo locale) a causa dell'assenza di sanificazione e dell'uso di funzioni non sicure.

Se questi snippet venissero distribuiti in un ambiente di produzione, esporrebbero l'infrastruttura aziendale a una compromissione totale (Remote Code Execution) e all'esfiltrazione massiva di dati (Data Breach).

---

## 2 Finding n1: OS Command Injection (RCE)

- File: `python-vuln-exec.py`
- Vulnerabilità: CWE-78 (Improper Neutralization of Special Elements used in an OS Command)
- Severity: CRITICA (CVSS: 10.0)

Analisi del Problema

Lo script Python utilizza la funzione deprecata e insicura `os.system()` per eseguire un ping verso un indirizzo IP fornito dall'utente. L'input dell'utente (`target_ip`) viene concatenato direttamente alla stringa del comando di sistema senza alcuna validazione.

Codice Vulnerabile:

```Python
target_ip = input("Inserisci un IP > ")
command = "ping -c 1 " + target_ip
os.system(command) # ESECUZIONE INSICURA
```

Impatto di Business

Un attaccante può inserire metacaratteri della shell (come `;`, `&&`, o `|`) seguiti da comandi arbitrari (es. `127.0.0.1; cat /etc/passwd`). Questo porta a una Remote Code Execution (RCE), permettendo il controllo totale del server che ospita l'applicazione.
Remediation (Soluzione)

- Evitare l'uso di `os.system()`.
- Utilizzare il modulo `subprocess` passando gli argomenti come una lista (array) anziché come una singola stringa. Questo impedisce alla shell di interpretare i caratteri speciali.
- (Opzionale ma raccomandato) Validare che l'input sia effettivamente un indirizzo IP valido tramite Regular Expressions o la libreria `ipaddress`.

Codice Sicuro:

```Python
import subprocess
import shlex

target_ip = input("Inserisci un IP > ")
# L'input viene disarmato e passato come argomento sicuro
subprocess.run(["ping", "-c", "1", target_ip]) 
```

#### Proof of Concept (PoC):

Per confermare l'effettiva sfruttabilità della vulnerabilità, è stato iniettato il payload `8.8.8.8; cat /etc/passwd` all'interno dell'input richiesto dallo script.

L'applicazione ha eseguito prima il comando legittimo (`ping`) e immediatamente dopo il comando arbitrario iniettato, restituendo il contenuto del file di sistema delle password.

Output (Redacted per OPSEC):

```Plaintext
[DEBUG] Sto eseguendo: ping -c 1 8.8.8.8; cat /etc/passwd

PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=115 time=24.8 ms

--- 8.8.8.8 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 24.792/24.792/24.792/0.000 ms

root:x:0:0:root:/root:/usr/bin/zsh
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
[... REDACTED - Altri 40+ utenti di sistema omessi ...]
```

---

## 3 Finding n2: SQL Injection (SQLi)

- File: `php-vuln-sql.php`
- Vulnerabilità: CWE-89 (Improper Neutralization of Special Elements used in an SQL Command)
- Severity: CRITICA (CVSS: 9.8)

Analisi del Problema

Lo script PHP acquisisce il parametro id tramite una richiesta GET HTTP e lo concatena direttamente all'interno di una query SQL di tipo SELECT. Non vi è alcun controllo sul tipo di dato (es. verifica che sia un intero) né alcuna codifica.

Codice Vulnerabile:

```PHP
$user_id = $_GET['id'];
$query = "SELECT * FROM users WHERE id = " . $user_id; // CONCATENAZIONE INSICURA
```

Impatto di Business

Un attaccante può manipolare il parametro `id` nell'URL (es. `?id=1 OR 1=1`) per alterare la logica della query. Questo permette di bypassare i meccanismi di autenticazione, leggere dati di altri utenti, o, in scenari peggiori, modificare/cancellare l'intero database.

Remediation (Soluzione)

Sostituire immediatamente la concatenazione manuale delle stringhe con i Prepared Statements utilizzando la libreria PDO (PHP Data Objects).

Codice Sicuro:

```PHP
$user_id = $_GET['id'];
// La query e i dati vengono inviati separatamente
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id");
$stmt->execute(['id' => $user_id]);
```

---

## 4 Conclusioni

Il pattern di vulnerabilità riscontrato indica una mancata adozione delle pratiche di "Secure by Design". La concatenazione diretta dell'input utente con interpreti di comandi (Database o Sistema Operativo) è la causa principale (Root Cause) di entrambi i difetti. Si raccomanda un training immediato sulle pratiche di Input Validation e Parameterized Queries per il team di sviluppo.