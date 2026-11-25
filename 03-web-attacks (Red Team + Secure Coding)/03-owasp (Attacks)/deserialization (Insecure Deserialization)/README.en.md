> **English** | [Italiano](README.md)

# Insecure Deserialization (gadget chain, ysoserial)

> - **Phase:** Web Exploitation - OWASP A08:2021 Software and Data Integrity Failures (deserialization of untrusted data)
> - **Visibility:** Medium - sending of anomalous serialized objects; executing the gadget chain spawns child processes from the application process
> - **Prerequisites:** an application that deserializes user-supplied data (cookies, parameters, messages) with a library that, given gadgets available in the classpath, allows code execution
> - **Nature of the document:** methodology. Illustrative payloads (gadget-chain concept, no armed copy-paste RCE payload), no fabricated Finding ID (next `WEB-016`, to assign in a lab).

- Objective: obtain remote code execution (RCE) by exploiting the deserialization of untrusted data, when the application rebuilds objects from attacker-controlled input.

---

## Executive Summary

Serialization converts an in-memory object into a byte stream (to save or transmit it); deserialization does
the reverse. The problem arises when an application deserializes user-supplied data: during object
reconstruction, some languages automatically execute "magic" methods (e.g., `readObject` in Java,
`__wakeup`/`__destruct` in PHP, `__reduce__` in Python pickle). If classes exist in the application's
classpath whose combinations of methods (a "gadget chain") lead to command execution, an attacker can craft a
malicious serialized object that, once deserialized, executes code on the server.

In Java this is systematized by ysoserial, a tool that generates payloads for dozens of known gadget chains
(Commons-Collections, Spring, etc.). The typical impact is direct RCE, hence severity `Critical`. The vector
is insidious because deserialization often happens in non-obvious places: serialized session cookies,
`ViewState` parameters, queue messages, tokens.

## Operational context (why, before how)

You look for deserialization wherever the app accepts "opaque" structured data: cookies or parameters
containing Base64 blobs that start with known markers (e.g., `rO0` for serialized Java, `gASV` for Python
pickle). The key operational decision is to identify the format (Java, PHP, .NET, Python) and which gadget
chains are available in the app's classpath/environment: it is not enough that the app deserializes, an
exploitable gadget chain is needed. ysoserial automates generation for Java by trying the known chains.

## Execution / Commands

### Phase 1 - Identify the serialized format

```bash
# A Base64 blob decoding to bytes starting with 0xAC 0xED (or 'rO0' in Base64) = serialized Java object
echo "rO0ABXNy..." | base64 -d | xxd | head -1
```

Illustrative output:

```
00000000: aced 0005 7372 ...        <-- Java serialization magic bytes: candidate for insecure deserialization
```

### Phase 2 - Payload generation (concept, ysoserial)

ysoserial generates a serialized object based on a known gadget chain. Conceptually:

```bash
# Generates a payload for the CommonsCollections gadget chain that runs a command (educational form)
java -jar ysoserial.jar CommonsCollections5 '<command>' > payload.bin
```

The embedded command, in a lab test, is typically a simple verifiable marker (e.g., a `ping` toward the
attacker machine or writing a file), NOT a destructive payload. The OOB verification (the server contacts the
attacker) confirms the RCE without needing a full shell.

### Phase 3 - Sending and confirmation

The payload is sent at the deserialization point (cookie, parameter, body) and the effect of the command is
observed (network callback, file created). Illustrative output on the attacker side:

```
# listener receiving the ping/callback from the target server
ICMP echo request from 10.10.10.40   <-- the server deserialized and executed: RCE confirmed
```

## Analysis of results

The callback confirmation proves code execution on the server: it is RCE, severity `Critical`. From here, in
an engagement, you would move from a "marker" command to a reverse shell for interactive access, but
demonstrating the finding does not require going beyond the OOB proof. If the app deserializes but no
exploitable gadget chain exists in the classpath, the impact is reduced (possible DoS or no effect): the real
finding is classified by the actual outcome in a lab.

### Theoretical Analysis

Insecure deserialization is an extreme case of confusion between data and code: the application treats a byte
stream as the recipe to rebuild arbitrary objects, and the reconstruction has side effects (the magic
methods). A gadget chain is a path, through already-present and legitimate classes, that chains these side
effects up to command execution: the attacker does not inject code, they orchestrate existing code (similar
in spirit to ROP in binary exploitation). The theoretical countermeasure is never to deserialize untrusted
data with mechanisms that allow arbitrary types; where unavoidable, use a type allow-list and formats that
carry only data (JSON) without instructions.

## Remediation (Blue Team)

**Detection (WAF/SIEM/EDR).**
- Input with serialization markers (`rO0`/`0xACED` for Java, `gASV`/`\x80\x04` for pickle, `TypeError` in
  .NET BinaryFormatter) in cookies/parameters.
- Child processes (`sh`, `cmd`, `powershell`) spawned by the Java/web application process right after
  receiving a serialized input.
- Outbound network callbacks from the server toward unexpected destinations.

**Hardening (secure coding).**
- Do not deserialize untrusted data. Where persistence/transport is needed, use data-only formats (JSON) with
  a schema, not native object serialization.
- If native deserialization is unavoidable: strict allow-list of allowed types (e.g., `ObjectInputFilter` in
  Java), signature/HMAC of the serialized data to guarantee its integrity.
- Remove libraries with known gadget chains from the classpath if unnecessary; keep dependencies updated.
- Sign and encrypt cookies/ViewState (prevents tampering with the serialized blob).

---

## Real-World Scenario: Post-Exploitation Projection

> Applies to the "RCE confirmed" outcome (severity Critical).

### Attacker Perspective (Red Team)

**Starting point:** deserialization point identified (e.g., a serialized Java cookie) and an available gadget
chain.

**Immediate next step:** payload with a marker command to confirm RCE (OOB), then a reverse shell for
interactive access.

**Projected Kill Chain:**

```
Attacker-controlled serialized input
        |
        v
Gadget chain (ysoserial) -> command execution on the server (RCE)
        |
        v
Reverse shell -> access to the application process context
        |
        v
Local enumeration + privesc (module 04) -> lateral movement
```

**Potential impact:** RCE on the application server, from which the whole post-exploitation chain follows.
Often the process runs with non-trivial privileges (service account), shortening the path to system
compromise.

**Typical monetization vectors:** ransomware/exfiltration downstream of RCE; use of the server as a pivot
into the internal network.

### Defender Perspective (Blue Team)

**Detection:** serialization markers in input; anomalous child processes from the application process;
outbound callbacks.

**Indicators of Compromise (IOC):**
- Cookies/parameters with tampered `rO0...`/`0xACED` blobs.
- `java` (or the web process) spawning `sh -c`/`cmd.exe` right after a request.
- Outbound connections from the application server toward unexpected external IPs.

**Containment:** block the pattern via WAF; isolate the server; analyze child processes and connections.

**Eradication and hardening:** eliminate deserialization of untrusted data; ObjectInputFilter/allow-list;
signing of serialized data; dependency updates; removal of gadget chains from the classpath.

**Defensive lesson:** the problem is not to "validate better" the serialized blob, but not to deserialize
untrusted data as objects. The effective defense is architectural (data-only formats, type allow-list), not a
downstream filter.

---

## Reference tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `ysoserial` | Exploit generator | CLI - Active | Generates Java payloads for known gadget chains (CommonsCollections, Spring, ...) |
| `ysoserial.net` | Exploit generator | CLI - Active | Equivalent for .NET (BinaryFormatter, Json.NET, ...) |
| `Burp Suite` | Proxy/scanner | Web - Active | Identifies and modifies serialized input; "Java Deserialization Scanner" extension |
| `phpggc` | Exploit generator | CLI - Active | Gadget chains for PHP (unserialize) |

## Methodology notes

In a real lab (e.g., a vulnerable Java app or a dedicated target) the data to document as a finding: the
deserialization point, the format, the working gadget chain and the OOB confirmation of execution. The
integrity rules apply: real outputs, never fabricated. In a lab the embedded command remains a non-destructive
marker to demonstrate RCE.

## MITRE ATT&CK mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Exploitation of insecure deserialization on an exposed endpoint. |
| Execution | Command and Scripting Interpreter | `T1059` | Command execution on the server via the deserialized gadget chain. |

---

## Correlations with other findings

| Source | This technique | Effect |
| :--- | :--- | :--- |
| [02-web-recon](../../02-web-recon (Enumeration)/README.en.md) | Deserialization | identifies serialized input (cookies/parameters with known markers) |
| Deserialization (RCE) | [04-system-exploitation](../../../04-system-exploitation/README.en.md) | RCE opens the way to local enumeration and privilege escalation |
| Deserialization | [secure-coding-lab](../../06-secure-coding-lab (Defense)/README.en.md) | the remediation (no deserialization of untrusted data) links to secure coding |

---

> **Note:** Educational and methodology content. The techniques must be executed only on owned applications or with explicit authorization. The payloads are illustrative and do not come from real or third-party systems.
