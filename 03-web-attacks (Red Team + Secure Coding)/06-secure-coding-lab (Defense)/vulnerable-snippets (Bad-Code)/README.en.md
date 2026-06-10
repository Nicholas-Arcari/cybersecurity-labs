> **English** | [Italiano](README.md)

# Source Code Review

> - **Phase:** Secure Coding - Static Analysis (SAST)
> - **Visibility:** Zero - local source code analysis, no network requests toward external targets
> - **Prerequisites:** Access to the application source code (black-box: N/A; white-box: repository)
> - **Output:** Identification of CWE-78 (OS Command Injection) and CWE-89 (SQL Injection) with proof of concept, remediation recommendations

---

## 1 Executive Summary

During the static source code review (SAST) performed on the backend modules, two critical vulnerabilities were identified related to insecure handling of user input. Both inspected scripts allow command injection (against the database or the local operating system) due to the absence of sanitization and the use of insecure functions.

If these snippets were deployed in a production environment, they would expose the corporate infrastructure to full compromise (Remote Code Execution) and massive data exfiltration (Data Breach).

---

## 2 Finding #1: OS Command Injection (RCE)

- File: `python-vuln-exec.py`
- Vulnerability: CWE-78 (Improper Neutralization of Special Elements used in an OS Command)
- Severity: CRITICAL (CVSS: 10.0)

Problem Analysis

The Python script uses the deprecated and insecure `os.system()` function to perform a ping against an IP address provided by the user. The user input (`target_ip`) is directly concatenated to the system command string without any validation.

Vulnerable Code:

```Python
target_ip = input("Inserisci un IP > ")
command = "ping -c 1 " + target_ip
os.system(command) # ESECUZIONE INSICURA
```

Business Impact

An attacker can insert shell metacharacters (such as `;`, `&&`, or `|`) followed by arbitrary commands (e.g., `127.0.0.1; cat /etc/passwd`). This leads to Remote Code Execution (RCE), allowing full control of the server hosting the application.

Remediation (Solution)

- Avoid using `os.system()`.
- Use the `subprocess` module passing arguments as a list (array) instead of a single string. This prevents the shell from interpreting special characters.
- (Optional but recommended) Validate that the input is actually a valid IP address using Regular Expressions or the `ipaddress` library.

Secure Code:

```Python
import subprocess
import shlex

target_ip = input("Inserisci un IP > ")
# L'input viene disarmato e passato come argomento sicuro
subprocess.run(["ping", "-c", "1", target_ip]) 
```

#### Proof of Concept (PoC):

To confirm the actual exploitability of the vulnerability, the payload `8.8.8.8; cat /etc/passwd` was injected into the input requested by the script.

The application executed the legitimate command (`ping`) first and immediately after the injected arbitrary command, returning the contents of the system password file.

Output (Redacted for OPSEC):

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
[... REDACTED - 40+ additional system users omitted ...]
```

---

## 3 Finding #2: SQL Injection (SQLi)

- File: `php-vuln-sql.php`
- Vulnerability: CWE-89 (Improper Neutralization of Special Elements used in an SQL Command)
- Severity: CRITICAL (CVSS: 9.8)

Problem Analysis

The PHP script acquires the `id` parameter via an HTTP GET request and concatenates it directly into a SELECT SQL query. There is no data type validation (e.g., verifying it is an integer) nor any encoding.

Vulnerable Code:

```PHP
$user_id = $_GET['id'];
$query = "SELECT * FROM users WHERE id = " . $user_id; // CONCATENAZIONE INSICURA
```

Business Impact

An attacker can manipulate the `id` parameter in the URL (e.g., `?id=1 OR 1=1`) to alter the query logic. This allows bypassing authentication mechanisms, reading other users' data, or, in worst-case scenarios, modifying/deleting the entire database.

Remediation (Solution)

Immediately replace the manual string concatenation with Prepared Statements using the PDO (PHP Data Objects) library.

Secure Code:

```PHP
$user_id = $_GET['id'];
// La query e i dati vengono inviati separatamente
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id");
$stmt->execute(['id' => $user_id]);
```

---

## 4 Conclusions

The vulnerability pattern found indicates a failure to adopt "Secure by Design" practices. Direct concatenation of user input with command interpreters (Database or Operating System) is the main root cause of both defects. Immediate training on Input Validation and Parameterized Queries practices is recommended for the development team.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Description (SAST - Defensive Analysis) |
| :--- | :--- | :--- | :--- |
| Execution | Command and Scripting Interpreter: Unix Shell | `T1059.004` | CWE-78: `os.system()` with direct concatenation allows Command Injection (`8.8.8.8; cat /etc/passwd`) executing arbitrary commands as the application user |
| Initial Access | Exploit Public-Facing Application | `T1190` | CWE-89: `$user_id` concatenation in the SQL query allows SQL Injection (`?id=1 OR 1=1`) to read other users' data or bypass authentication |

---

> **Note:** The snippets analyzed in this section were developed or identified during
> the testing phases documented in the offensive modules. The vulnerable code is presented exclusively
> to illustrate the root cause of the vulnerabilities and MUST NOT be used in
> production environments. The fix patterns were verified through re-testing with the same payloads.
