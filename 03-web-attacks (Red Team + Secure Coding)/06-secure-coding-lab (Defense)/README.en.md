> **English** | [Italiano](README.md)

# 06 - Secure Coding Lab (Defense)

> - **Phase:** Secure Coding - Static Analysis (SAST) and Post-Remediation Verification
> - **Visibility:** Zero - local source code analysis, no traffic toward external targets
> - **Prerequisites:** Understanding of vulnerabilities documented in the `03-owasp/` and `05-api-security/` modules
> - **Output:** Vulnerable code with CWE analysis, patched code with secure patterns, remediation effectiveness verification

---

## Introduction

The Secure Coding Lab section is the component that distinguishes an expert penetration tester from a simple script runner. Understanding **why** a vulnerability exists at the source code level, and knowing how to fix it with the appropriate patterns, is the fundamental competency for:

- Writing professional technical reports that justify the recommended remediations.
- Collaborating with development teams in a DevSecOps approach.
- Verifying that implemented patches are actually effective (post-remediation re-testing).

The operational cycle of this section is: **Vulnerability identified** (in previous modules) -> **Root Cause Analysis** (vulnerable source code) -> **Fix pattern** (secure code) -> **Verification** (re-test with the same payload).

For each vulnerability documented in the offensive modules, this section preserves two artifacts:
- The **vulnerable** code with CWE annotation and explanation of the exploitation mechanism.
- The **patched** code with the secure pattern, recommended libraries, and effectiveness verification.

This defensive perspective is valued by recruiters in the field because it demonstrates that offensive knowledge is accompanied by awareness of countermeasures - a quality typical of a senior Security Analyst rather than a simple tester.

---

## Folder Structure

```
06-secure-coding-lab (Defense)/
+-- vulnerable-snippets (Bad-Code)/          # Vulnerable code with CWE analysis
+-- fixed-snippets (Good-Code)/              # Secure code post-remediation
    +-- input-sanitization-examples/         # Output encoding for XSS (htmlspecialchars)
```

---

## `vulnerable-snippets/` - Vulnerable Code (SAST)

### Operational Context

This folder contains the source code snippets analyzed during the attack phases, with annotations on the root cause and the corresponding CWE (Common Weakness Enumeration) classification.

The `vulnerable-snippets/README.md` document covers two static analysis findings:

**Finding #1: OS Command Injection (CWE-78)**
- File: `python-vuln-exec.py`
- The problem: `os.system("ping -c 1 " + target_ip)` - direct concatenation of user input into the system command.
- Proof of Concept: the payload `8.8.8.8; cat /etc/passwd` produced a dump of the `/etc/passwd` file.
- Severity: Critical (CVSS 10.0).

**Finding #2: SQL Injection (CWE-89)**
- File: `php-vuln-sql.php`
- The problem: `$query = "SELECT * FROM users WHERE id = " . $user_id;` - concatenation of the user ID into the SQL query.
- Severity: Critical (CVSS 9.8).

---

## `fixed-snippets/` - Secure Code (Post-Remediation)

### Operational Context

This folder contains the secure implementations that replace the vulnerable code documented in `vulnerable-snippets/`. For each vulnerability, it includes:

1. The secure code with the appropriate fix pattern.
2. The technical explanation of why the secure pattern neutralizes the attack vector.
3. Effectiveness verification through re-testing with the same payload.

The `fixed-snippets/README.md` document covers the SQL Injection fix using Prepared Statements (PHP PDO), with proof-of-defense: the payload `admin@example.com' OR '1'='1` no longer produces a valid login but instead a correct `Login Failed` error.

---

## `fixed-snippets/input-sanitization-examples/` - XSS Defense

### Operational Context

This subfolder documents the primary defense pattern against Cross-Site Scripting: Output Encoding via `htmlspecialchars()` in PHP.

The `input-sanitization-examples/README.md` demonstrates:
- The vulnerable code: `echo $_GET['name']` which reflects the XSS payload into the DOM.
- The secure code: `htmlspecialchars($_GET['name'], ENT_QUOTES, 'UTF-8')` which converts `<script>` to `&lt;script&gt;`.
- Visual verification: browser screenshot showing the text string instead of the JavaScript popup.

---

## Applied Secure Coding Principles

### 1. Input Validation (Allow-list)

Never trust user input. Validate that input matches the expected format before processing it:

```python
# WRONG: accept any input
target_ip = input("IP > ")
os.system("ping -c 1 " + target_ip)

# CORRECT: validate that it is a valid IP before using it
import ipaddress
try:
    ipaddress.ip_address(target_ip)  # raises ValueError if not a valid IP
    subprocess.run(["ping", "-c", "1", target_ip])
except ValueError:
    print("Error: invalid input")
```

### 2. Parameterized Queries (Prepared Statements)

Always separate the SQL command from the data:

```php
// WRONG: concatenation
$query = "SELECT * FROM users WHERE id = " . $_GET['id'];

// CORRECT: Prepared Statements with PDO
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id");
$stmt->execute(['id' => $_GET['id']]);
```

### 3. Output Encoding

Encode the output in the correct context before rendering it:

```php
// WRONG: direct echo
echo $_GET['name'];

// CORRECT: HTML entity encoding
echo htmlspecialchars($_GET['name'], ENT_QUOTES, 'UTF-8');
```

### 4. Subprocess Without Shell

Avoid command execution through shell strings:

```python
# WRONG: uses the shell, interprets metacharacters (;, |, &&)
os.system("ping -c 1 " + user_input)

# CORRECT: argument list, no intermediate shell
subprocess.run(["ping", "-c", "1", user_input], shell=False)
```

### 5. Secure Secret Management

Never hardcode keys and passwords in source code:

```python
# WRONG: hardcoded
SECRET_KEY = "secret123"

# CORRECT: environment variables
import os
SECRET_KEY = os.environ.get("JWT_SECRET")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise ValueError("JWT_SECRET missing or too weak")
```

---

## Reference SAST Tools

| Tool | Language | Type | Use Case |
| :--- | :--- | :--- | :--- |
| `bandit` | Python | SAST CLI | Static analysis for common Python vulnerabilities (os.system, eval, pickle) |
| `semgrep` | Multi-language | SAST CLI | Static analysis with custom rules, CI/CD integrable |
| `SonarQube` | Multi-language | SAST Web | Enterprise platform for continuous code review |
| `snyk` | Multi-language | SAST Web/CLI | Dependency analysis and code vulnerabilities |
| `phpcs-security-audit` | PHP | SAST CLI | Specific rules for PHP vulnerabilities (SQLi, XSS, RCE) |
| `eslint-plugin-security` | JavaScript | SAST CLI | Static analysis for Node.js applications |

---

## Recommended Operational Flow

```
[1] Vulnerability identification (offensive modules)
     +-- SQLi found in login.php
     +-- XSS found in URL parameter
     +-- Command Injection in Python script
              |
              v
[2] Root Cause Analysis (vulnerable-snippets/)
     +-- isolate the responsible code
     +-- identify the corresponding CWE
     +-- document the proof of concept
              |
              v
[3] Fix implementation (fixed-snippets/)
     +-- apply the appropriate secure pattern
     +-- unit test the edge case (malicious input)
              |
              v
[4] Verification (re-test)
     +-- re-execute the original payload on the patched code
     +-- confirm the server responds securely
     +-- document the "proof of defense"
              |
              v
[5] CI/CD Integration (optional)
     +-- add the SAST tool to the pipeline
     +-- bandit for Python, semgrep for multi-language
```

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Description (Defensive Action) |
| :--- | :--- | :--- | :--- |
| (Mitigation) | Exploit Public-Facing Application | `T1190` | Implementation of Prepared Statements (PDO) to neutralize SQLi (CWE-89) |
| (Mitigation) | Command and Scripting Interpreter: Unix Shell | `T1059.004` | Replacement of `os.system()` with `subprocess.run(list)` to neutralize OS Command Injection (CWE-78) |
| (Mitigation) | Exploit Public-Facing Application | `T1190` | Implementation of `htmlspecialchars()` to neutralize Reflected and Stored XSS |
| (Mitigation) | Brute Force: Password Cracking | `T1110.002` | Replacement of JWT weak secret with 64+ char random key from environment variables (WEB-012) |

---

> **Note:** The vulnerable code documented in this section is provided exclusively for
> educational purposes to illustrate the root causes of vulnerabilities identified during testing. It must
> not be used in production environments. The documented fix patterns follow the OWASP Secure Coding
> Practices guidelines and the MITRE CWE Top 25. For a complete code review in a real engagement
> context, integrate SAST into a formal Code Review process.
