> **English** | [Italiano](README.md)

# OS Command Injection

> - **Phase:** Web Exploitation - OWASP A03:2021 Injection (user input concatenated into a system command)
> - **Visibility:** Medium/High - the web process spawns shell child processes (a pattern very detectable by EDR/auditd); blind variants generate outbound traffic or measurable delays
> - **Prerequisites:** an application that builds and executes a system command including user input (ping, conversions, utilities, calls to external binaries)
> - **Nature of the document:** methodology. Illustrative and benign payloads (only verification commands such as `id`/`whoami`), no reverse shell reproduced, no fabricated Finding ID (next `WEB-016`, to assign in lab).

- Objective: execute arbitrary commands on the server's operating system by exploiting the unsafe concatenation of user input into a shell call; here limited to non-destructive verification commands.

---

## Executive Summary

OS Command Injection is among the highest-impact web vulnerabilities: it leads directly to **Remote Code
Execution (RCE)** on the server. It occurs when an application builds a system command by concatenating user
input and passes it to a shell (`system()`, `exec()`, backticks, `os.system`, `Runtime.exec` with a shell).
Using the shell metacharacters (`;`, `|`, `&&`, `$()`, backticks), the attacker appends their own commands to
the intended one.

Unlike SQLi/LDAP/XPath, which stay in the data domain, Command Injection leaves the application and reaches the
operating system: the attacker executes code with the privileges of the web process. From there they can read
files, move laterally and aim for escalation. The typical severity is `Critical` (CVSS around 9.8). It can be
"in-band" (the command output appears in the response) or "blind" (no output: time-based or out-of-band is used).

## Operational context (why, before how)

Command Injection is sought where the app invokes system features from input: network tools (ping, traceroute,
nslookup), file conversions, report generation, calls to external binaries. The operational decision is to
distinguish the in-band case (visible output: immediate verification) from the blind one (an indirect channel is
needed: a time delay or an outbound request to a controlled server). The initial verification is minimal and
**non-destructive**: you append an innocuous command (`id`, `whoami`) after a separator and observe the output.

## Execution / Commands

### Phase 1 - Confirm the vulnerability (benign command)

Assuming a `host` parameter passed to a `ping` command, you append an innocuous verification command via a shell
separator:

```
# parameter value (didactic form, NON-destructive verification command)
127.0.0.1; id
```

Illustrative output (representative, in the app response):

```
PING 127.0.0.1 ... 64 bytes from 127.0.0.1
uid=33(www-data) gid=33(www-data) groups=33(www-data)   <-- 'id' executed: command injection confirmed
```

The execution of `id`/`whoami` confirms RCE with the privileges of the web process. Common separators are `;`,
`|`, `&&`, `$()` and backticks; the choice depends on the context (shell, filters present).

### Phase 2 - Blind variant (conceptual)

If the output is not reflected, you confirm indirectly: a command that introduces a **measurable delay**
(time-based) or that makes an **outbound request** to a controlled server (out-of-band). You verify execution
from the delay or the received request, without needing to see the output in the response.

> Note: no reverse shells or post-exploitation chains are reproduced. Confirming execution (with benign commands)
> is sufficient to demonstrate the impact in an assessment.

## Analysis of results

Confirming the execution of a benign command demonstrates RCE: the attacker can run arbitrary commands with the
privileges of the web process (typically a service user such as `www-data`). The real severity is `Critical`:
from here file read/write, access to local credentials, lateral movement and escalation open up (see module 04).
If the web process runs with elevated privileges or if one can escalate from it to root, the entire host is
compromised. If the application never invokes a shell (it uses APIs that pass the arguments as an array), the
vector is closed.

### Theoretical Analysis

OS Command Injection is the most direct form of the data/instructions problem [Su & Wassermann 2006]: the user
input (data) is interpreted by the shell as a command (instruction). The root is the use of a shell to execute
commands built by concatenation. The definitive countermeasure is to **not use the shell**: invoke binaries with
APIs that pass arguments as a list (`execve`, `subprocess.run([...])` without `shell=True`, `ProcessBuilder` with
separate arguments), so the metacharacters remain inert data. Secondarily: strict input whitelisting and the
principle of least privilege for the web process (damage containment).

## Remediation (Blue Team)

**Detection (EDR/auditd/SIEM).**
- The web server process spawning shell child processes (`sh`, `bash`, `cmd`, `powershell`): a very anomalous and
  highly indicative pattern.
- Input containing shell metacharacters (`;`, `|`, `&&`, `$()`, backticks) in the parameters.
- Anomalous response delays (time-based) or unexpected outbound traffic from the web server (out-of-band).

**Hardening (secure coding).**
- Do not invoke a shell: use APIs that pass the arguments as an array, with no shell interpretation (the primary
  countermeasure).
- Where possible, avoid the external-command call entirely by using native libraries.
- Strict input whitelisting (e.g., for a host: only valid hostname/IP characters).
- Run the web process with minimal privileges; segment and limit what it can reach.

---

## Real-World Scenario: Post-Exploitation Projection

> Applies to the "confirmed RCE" outcome (severity Critical).

### Attacker Perspective (Red Team)

**Starting point:** a parameter that ends up in a system command, with execution confirmed (Phase 1).

**Immediate next step:** reconnaissance of the context (user, privileges, reachable files) with benign commands,
then evaluation of the escalation path.

**Projected Kill Chain:**

```
OS Command Injection (RCE as the web user)
        |
        v
Local reconnaissance: user, privileges, reachable configuration files
        |
        v
Credential reading / access to internal services (see 04-system-exploitation)
        |
        v
Local privilege escalation -> root -> host compromise and pivoting
```

**Potential impact:** from a single web vulnerability to server compromise and, via pivoting, to the internal
network. The natural link is with [04-system-exploitation](<../../../04-system-exploitation/README.en.md>).

**Typical monetization vectors:** server compromise (ransomware, cryptomining), exfiltration, pivoting toward the
internal infrastructure.

### Defender Perspective (Blue Team)

**Detection:** web server spawning a shell; metacharacters in the parameters; anomalous delays or outbound
traffic.

**Indicators of Compromise (IOC):**
- `sh`/`bash`/`cmd` processes that are children of the web server process.
- Parameters with `;`, `|`, `&&`, `$()`, backticks.
- Outbound connections from the web server toward unexpected hosts (OOB variant).

**Containment:** block the pattern via WAF; isolate the host; verify recent processes and connections.

**Eradication and hardening:** eliminate the shell call (APIs with array arguments); input whitelist; least
privilege; code review of the points that invoke external commands.

**Defensive lesson:** Command Injection is the case where injection leaves the data and becomes code on the
system. The defense is not filtering "bad characters" but not using the shell at all: separating command and
arguments at the API level.

---

## Reference tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `Burp Suite` | Proxy/scanner | Web - Active | Intercepts and modifies the parameters; injection test with benign commands |
| `commix` | Exploit tool | CLI - Active | Automated detection and exploitation (in an authorized lab) of command injection |
| `curl` | HTTP client | CLI - Active | Manual sending of requests with verification payloads |
| `subprocess` (array) / `ProcessBuilder` | Safe APIs | Secure coding | Shell-free execution for the remediation (Blue Team) |

## Methodology notes

In a real lab (e.g., DVWA, WebGoat or a target with network features) the data to document as a finding: the
confirmation of execution (with a benign command), the privilege context and any escalation path, without
reproducing reverse shells or destructive actions. Evidence must be collected with non-destructive commands.

## MITRE ATT&CK mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Exploitation of the unsafe concatenation of input into a system command. |
| Execution | Command and Scripting Interpreter: Unix Shell | `T1059.004` | Execution of commands on the server via a shell (Linux context). |
| Execution | Command and Scripting Interpreter: Windows Command Shell | `T1059.003` | Execution of commands on the server via cmd (Windows context). |

---

## Links to other findings

| Source | This technique | Effect |
| :--- | :--- | :--- |
| [02-web-recon](<../../02-web-recon (Enumeration)/README.en.md>) | OS Command Injection | enumeration identifies the features that invoke system commands |
| OS Command Injection (RCE) | [04-system-exploitation](<../../../04-system-exploitation/README.en.md>) | RCE as the web user opens local privilege escalation |
| OS Command Injection | [secure-coding-lab](<../../06-secure-coding-lab (Defense)/README.en.md>) | the remediation (no shell, APIs with array arguments) links to secure coding |

---

> **Note:** All described techniques are for educational and methodology-documentation purposes. Execution only on owned applications or with explicit authorization. The payloads are verification-only (benign commands); no reverse shell or destructive action is reproduced. Outputs are illustrative.
