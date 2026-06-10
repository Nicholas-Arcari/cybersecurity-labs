> **English** | [Italiano](README.md)

# Vulnerability Assessment: Server-Side Template Injection (SSTI)

> - **Phase:** Web Attack - Server Side Template Injection
> - **Visibility:** Medium - HTTP requests with `{{ }}` payload in URL parameter, similar to normal user input
> - **Prerequisites:** Web application with server-side template engine (Jinja2, Twig, Freemarker), input parameter reflected in the response
> - **Output:** SSTI confirmation (math injection), Remote Code Execution via Python MRO, `/etc/passwd` dump, finding WEB-008

---

**Finding ID:** `WEB-008` | **Severity:** `Critical` | **CVSS v3.1:** 9.8

---

## 1 Executive Summary

During the security analysis of the web application (lab environment), a critical Server-Side Template Injection (SSTI) vulnerability was identified.

The flaw resides in the insecure handling of user input within the Jinja2 template engine.

This vulnerability allows a remote unauthenticated attacker to escape the application sandbox and execute arbitrary commands on the underlying operating system (Remote Code Execution).

The impact is assessed as CRITICAL since it grants the attacker total server control, access to sensitive files (e.g., `/etc/passwd`, SSH keys) and the ability to pivot towards the internal network.

---

## 2 Technical Analysis

#### Phase 1: Detection & Verification

Reconnaissance activity revealed that the `name` parameter is reflected in the HTML response without adequate sanitization.
To confirm the use of a server-side template engine, a mathematical payload was injected.

- Payload: `{{ 7*7 }}`
- Result: The server rendered `49`. This behavior confirms that the input is evaluated and executed by the Jinja2 engine before being sent to the client.

![](./img/Screenshot_2026-02-15_17_52_58.jpg)

#### Phase 2: Exploitation (Remote Code Execution)

Leveraging the template engine's ability to access Python internal objects (through Method Resolution Order - MRO), an exploit chain was constructed to access the `os` module and execute system commands.

Exploit Payload:

```Python
{{ self.__init__.__globals__.__builtins__.__import__('os').popen('cat /etc/passwd').read() }}
```

![](./img/Screenshot_2026-02-15_17_55_07.jpg)

Evidence Analysis:

The payload injection was successful. The server executed the shell command `cat /etc/passwd` and returned its standard output in the HTTP response body.

As shown in the screenshot below, it was possible to exfiltrate the system user list (including the `root` user), demonstrating the complete compromise of system confidentiality and integrity.

---

## 3 Root Cause Analysis (Code Review)

Source code analysis (`ssti_vuln.py`) revealed the problem's root cause. The application uses string concatenation (f-string) to insert user input into the template before it is processed by the rendering engine.

Vulnerable Code (Insecure Implementation):

```Python
# VULNERABILITY: Input is concatenated directly into the template structure.
person = request.args.get('name', 'Hacker')
template = f"<h1>Ciao, {person}!</h1>" 
return render_template_string(template)
```

In this configuration, any special characters (like `{{` or `}}`) entered by the user are interpreted as code instructions by the Jinja2 engine.

---

## 4 Remediation Plan

To mitigate the vulnerability, it is necessary to strictly separate presentation logic from data. User input must never be concatenated directly into a template string.

Secure Coding Pattern:

Use the native context mechanism of Flask/Jinja2. Pass variables as named arguments to the rendering function. The engine will automatically handle escaping of dangerous characters, treating input as simple text and not executable code.

Corrected Code (Fix):

```Python
# SOLUTION: Pass input as a context variable.
person = request.args.get('name', 'Guest')
return render_template_string("<h1>Ciao, {{ person }}!</h1>", person=person)
```

---

## 5 Post-Remediation Verification

After implementing the Remediation Plan, a new test session was performed to verify the effectiveness of the countermeasures adopted in the source code.

1. Patch Confirmation

The source code was updated using Jinja2 Context Variables, eliminating direct concatenation through f-strings:

```Python
# Updated and verified code
person = request.args.get('name', 'Hacker')
return render_template_string("<h1>Ciao, {{ person }}!</h1>", person=person)
```

2. Verification Test Results

The previously successful attack vectors were repeated.

- Detection Test (Math Injection): Inserting the payload `{{ 7*7 }}` no longer produced server-side calculation execution.
- Result: The application returned the literal string `{{ 7*7 }}` in the browser. This confirms that the template engine now performs automatic escaping of special characters, treating input exclusively as Plain Text.

![](./img/Screenshot_2026-02-15_18_11_00.jpg)

Mitigation Evidence:

As shown in the screenshot, the malicious input is reflected faithfully without being interpreted by the server, neutralizing any escalation attempt towards RCE.

---

## 6 Conclusions

The SSTI vulnerability was correctly mitigated through the adoption of Secure Coding practices. It is recommended to maintain the separation approach between logic and data for all future developments involving template engines.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Jinja2 SSTI exploitation through payload `{{ 7*7 }}` to confirm server-side code execution, followed by escalation to RCE (WEB-008) |
| Execution | Command and Scripting Interpreter: Python | `T1059.006` | Access to Python's `os` module through Method Resolution Order (MRO) to execute system commands: `popen('cat /etc/passwd').read()` (WEB-008) |
| Discovery | File and Directory Discovery | `T1083` | Reading of `/etc/passwd` file through RCE, revealing the system user list including `root` (WEB-008) |

---

> **Note:** The SSTI vulnerability was identified and exploited on a local lab Flask/Jinja2 application, developed specifically to demonstrate the insecure pattern of input concatenation in the template. The finding includes both the exploitation PoC and post-remediation verification, documenting the entire vulnerability lifecycle from discovery to correction.
