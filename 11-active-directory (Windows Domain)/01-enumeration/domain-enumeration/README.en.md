> **English** | [Italiano](README.md)

# LDAP / RPC / SMB domain enumeration

> - **Phase:** Discovery (Active Directory domain)
> - **Visibility:** Low-Medium - LDAP and RPC queries are common traffic; null-session RID cycling is more characteristic
> - **Prerequisites:** connectivity to the DC (LDAP 389/636, SMB 445, RPC 135); some queries work with a null session, most require a domain account
> - **Technique:** `Domain enumeration (LDAP/RPC/SMB)` | **Typical severity:** `Low` | **Finding ID:** to assign in lab (methodology)

- Nature of the document: methodology. Illustrative outputs, not from a specific lab.
- Objective: collect, with targeted CLI tools, users, groups, policies and domain configurations, complementing BloodHound's graph view with precise, verifiable details.

---

## Executive summary

Alongside BloodHound, targeted enumeration with CLI tools remains indispensable for answering specific
questions: which users exist and their attributes, what the password policy is (essential before a spray),
who belongs to privileged groups, which accounts have SPNs or disabled pre-authentication. LDAP is the
richest source (the entire domain database is readable by an authenticated user); RPC and SMB add user and
share enumeration, in some cases even without credentials (null session) on misconfigured domains.

## Operational context (why, before how)

Targeted enumeration serves to prepare the subsequent techniques with precise data. Before a password spray,
for example, it is essential to read the lockout policy so as not to lock accounts out (a mistake that
reveals the attack and harms the client). Before Kerberoasting, you need the list of SPNs. This data is best
extracted with targeted LDAP queries rather than a graph collection.

## Execution / commands

### LDAP (ldapsearch)

```bash
# Domain password policy (lockout threshold, duration): read BEFORE any spraying
ldapsearch -x -H ldap://10.10.10.10 -D 'utente@corp.local' -w 'Password123' \
  -b 'DC=corp,DC=local' "(objectClass=domain)" lockoutThreshold lockoutDuration
```

```bash
# Users with SPN (Kerberoast targets) and accounts without pre-auth (AS-REP targets)
ldapsearch -x -H ldap://10.10.10.10 -D 'utente@corp.local' -w 'Password123' \
  -b 'DC=corp,DC=local' "(servicePrincipalName=*)" sAMAccountName servicePrincipalName
```

Illustrative output (representative):

```
lockoutThreshold: 5         <-- 5 attempts: spraying possible but with care (max 4 per window)
sAMAccountName: svc_sql
servicePrincipalName: MSSQLSvc/db01.corp.local   <-- Kerberoast target
```

### RPC / SMB (rpcclient, nxc, enum4linux-ng)

```bash
# User and group enumeration via RPC with credentials
rpcclient -U 'corp.local\utente%Password123' 10.10.10.10 -c "enumdomusers;enumdomgroups"
```

```bash
# NetExec: user enumeration, password policy and RID brute forcing in one go
nxc smb 10.10.10.10 -u utente -p 'Password123' --users --pass-pol --rid-brute
```

```bash
# enum4linux-ng: overall SMB/RPC enumeration (successor to enum4linux)
enum4linux-ng -A 10.10.10.10 -u utente -p 'Password123'
```

## Analysis of results

Targeted enumeration returns the data that feeds the offensive techniques: the password policy enables a
safe spray, the SPN list enables Kerberoasting, the list of accounts without pre-auth enables AS-REP
Roasting. On its own, enumeration is `Informational`/`Low`; its value lies in reducing the risk and noise of
the later phases. A null session exposing the entire user list is a `Low` finding in itself (information
disclosure), because it gives an unauthenticated attacker the raw material for spraying.

### Theoretical analysis

The richness of LDAP enumeration derives from an AD design choice: the domain database is readable by any
authenticated user, because the model assumes that knowledge of the structure is not itself a secret
(security lies in access controls, not in concealment). This assumption is reasonable but has an offensive
cost: the attacker with a single account obtains a detailed map. The defense cannot "turn off LDAP", but it
can reduce the readable sensitive attributes and, where unnecessary, eliminate null sessions (a legacy
configuration remnant).

## Remediation (blue team)

**Detection.** Anomalous volume of LDAP/RPC queries from a single account; RID cycling (sequences of SAMR
queries over increasing RIDs); anonymous/null-session access to the DCs.

**Hardening.** Disable null sessions and anonymous LDAP/SMB access on the DCs; apply least privilege to the
reading of sensitive attributes; monitor mass enumeration; maintain a sensible lockout policy (which,
however, does not open the door to account DoS).

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `ldapsearch` | ldap client | cli - active | targeted queries on users, groups, policies, spns |
| `windapsearch` | ldap wrapper | cli - active | common prepackaged ldap queries |
| `rpcclient` | rpc client | cli - active | user/group enumeration via rpc, including null session |
| `NetExec` (`nxc`) | ad/smb toolkit | cli - active | user enumeration, password policy, rid brute, shares |
| `enum4linux-ng` | enum wrapper | cli - active | overall smb/rpc enumeration (successor to enum4linux) |

## Methodology notes

In a real lab the data to document as a finding would be: the password policy (to justify the spray
parameters), the list of SPNs and of accounts without pre-auth, and any null session present (information
disclosure). These become direct inputs to techniques 02-05.

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| discovery | account discovery: domain account | `T1087.002` | enumeration of domain accounts via ldap/rpc. |
| discovery | permission groups discovery: domain groups | `T1069.002` | enumeration of groups and memberships. |
| discovery | password policy discovery | `T1201` | reading lockout and password policy before spraying. |

## Links to other modules

| source | this technique | effect |
| :--- | :--- | :--- |
| [bloodhound](<../bloodhound/README.en.md>) | domain enumeration | complements the graph with precise details (policy, spns) |
| domain enumeration | [kerberoasting](<../../02-kerberos-attacks/kerberoasting/README.en.md>) / [kerbrute spraying](<../kerbrute-userenum/README.en.md>) | provides spns, accounts without pre-auth and policy for safe spraying |
| smb enumeration | [module 02 - smb-net-bios](<../../../02-vulnerability-assessment/02-protocol-specific-audit/smb-net-bios/README.en.md>) | continuity with the smb audit already in the repo |

---

> **Note:** Educational and methodology content. Execution only in owned labs or with explicit authorization. Illustrative outputs, not from real systems.
