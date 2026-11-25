> **English** | [Italiano](README.md)

# Kerbrute: user enumeration and password spraying via Kerberos

> - **Phase:** Discovery and Credential Access (Active Directory domain)
> - **Visibility:** Variable - user enumeration via AS-REQ is relatively silent (it does not generate standard failed logons); password spraying generates pre-authentication events and must be dosed so as not to lock accounts
> - **Prerequisites:** connectivity to the DC on port 88 (Kerberos); no credentials needed for user enumeration; for spraying, a list of usernames and one or a few candidate passwords
> - **Technique:** `Kerbrute (user enum + password spraying)` | **Typical severity:** `Variable (Low / High)` | **Finding ID:** to assign in lab (methodology)

- Nature of the document: methodology. Illustrative outputs, not from a specific lab.
- Objective: build a list of valid usernames without authentication (user enumeration) and, from it, obtain valid credentials with a prudent password spray, respecting the lockout policy.

---

## Executive summary

Kerbrute exploits a feature of Kerberos pre-authentication: when you send an AS-REQ for a user, the KDC
responds differently depending on whether the user exists or not, even before verifying the password. This
allows enumerating valid usernames without generating the classic failed-logon events, and therefore
relatively silently. From the list of valid usernames you move to password spraying: trying a single common
password (e.g., seasonal or default) against many accounts, instead of many passwords against one account
(which would cause lockout).

Spraying is the high-value, high-risk phase: a single valid credential provides the domain foothold needed
by the whole module, but a poorly dosed spray locks accounts and reveals the attack. The rule is to read the
lockout policy first (see [domain-enumeration](<../domain-enumeration/README.en.md>)).

## Operational context (why, before how)

When you do not yet have domain credentials, Kerbrute is often the first step. User enumeration is cheap and
discreet; it builds the target list for spraying. Spraying must be calibrated to the policy: if lockout is 5
attempts over a 30-minute window, try at most 3-4 passwords per window, spaced out. The prudent decision is
to favor a few high-probability passwords (e.g., `CompanyName<Year>!`, `Season<Year>!`) across the whole
list, rather than many passwords against a few accounts.

## Execution / commands

### User enumeration

```bash
# Enumerate valid usernames from a wordlist, without credentials
kerbrute userenum -d corp.local --dc 10.10.10.10 usernames.txt
```

Illustrative output (representative):

```
[+] VALID USERNAME:  j.smith@corp.local
[+] VALID USERNAME:  svc_sql@corp.local   <-- confirmed valid usernames
```

### Password spraying (after reading the lockout policy)

```bash
# A single password against all valid usernames (spraying); dose it so as not to exceed lockout
kerbrute passwordspray -d corp.local --dc 10.10.10.10 valid_users.txt 'Autunno2026!'
```

Illustrative output:

```
[+] VALID LOGIN:  j.smith@corp.local:Autunno2026!   <-- valid credential: domain foothold obtained
```

## Analysis of results

User enumeration is `Low` in itself (information disclosure of valid usernames). Password spraying, if
successful, is `High`: a valid credential is the foothold that enables the whole AD module (authenticated
enumeration, Kerberoasting, and the escalation chain). The real finding is classified by outcome: no
credential found leaves the finding at `Low` (enumeration only); a valid credential, especially of a
privileged account, raises the severity.

### Theoretical analysis

User enumeration exploits an information leak in Kerberos pre-auth: the KDC distinguishes "nonexistent user"
(KDC_ERR_C_PRINCIPAL_UNKNOWN) from "existing user, pre-auth required" (KDC_ERR_PREAUTH_REQUIRED) before any
password verification. It is a protocol-level side channel, not an implementation bug. Spraying, in turn,
exploits a statistical fact: in a population of hundreds of users, the probability that at least one uses a
common password is high, while the cost per account (one attempt) stays below the lockout threshold. The
defense combines sensible lockout policies, unpredictable passwords (against spraying) and monitoring of
pre-auth patterns (against enumeration).

## Remediation (blue team)

**Detection.** Many AS-REQs for different usernames from the same source in a short time (enumeration);
Event ID 4768/4771 on many accounts within the same time window (spraying); a single failed pre-auth attempt
spread across many users is the classic spraying signature.

**Hardening.** Sensible lockout policy; unpredictable passwords (ban seasonal/corporate patterns with
filters such as Azure AD Password Protection); MFA where possible; monitoring and alerting on spraying
patterns; disabling unused accounts that widen the surface.

---

## Real-World scenario: Post-Exploitation projection

> Applies to the "spraying successful" outcome (severity High).

### Attacker perspective (red team)

**Starting point:** no credentials; a list of valid usernames obtained via enumeration.

**Immediate next step:** prudent spraying with a seasonal password; on the first valid credential, move to
authenticated enumeration.

**Projected Kill Chain:**

```
No credentials
        |
        v
Kerbrute userenum -> list of valid usernames
        |
        v
Password spraying -> first valid domain credential (foothold)
        |
        v
BloodHound + Kerberoasting -> escalation paths
        |
        v
Escalation (ACL/delegation/ADCS) -> DCSync -> full domain
```

**Potential impact:** from zero credentials to a domain foothold with a single guessed password, from which
the whole AD chain starts.

**Typical monetization vectors:** ransomware and exfiltration downstream of domain control; resale of the
initial access.

### Defender perspective (blue team)

**Detection:** spraying patterns (one attempt across many accounts); mass AS-REQ enumeration.

**Indicators of Compromise (IOC):** Event ID 4768/4771 spread across many accounts in the same window; a
single source with many AS-REQs for different users.

**Containment:** block the source; reset the compromised account; investigate the accesses made.

**Eradication and hardening:** MFA; password protection against predictable patterns; calibrated lockout;
disabling of dormant accounts.

**Defensive lesson:** spraying breaks nothing, it exploits predictable passwords in a large population. The
effective defense is making passwords unguessable (filters and MFA), not just longer.

---

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `kerbrute` | kerberos pre-auth | cli - active | user enumeration and password spraying via kerberos |
| `NetExec` (`nxc`) | ad/smb toolkit | cli - active | password spraying over smb/ldap/winrm, with lockout control |
| `kerbrute` + user wordlist | - | - | lists such as seclists for common usernames and corporate patterns |

## Methodology notes

In a real lab the data to document: the effective lockout policy (to justify the dosing), the enumerated
valid usernames, and the spraying outcome. Real operational caution: a spray without having read the policy
can lock accounts and must be avoided even in a lab, to build the correct habit.

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| discovery | account discovery: domain account | `T1087.002` | enumeration of valid usernames via kerberos pre-auth. |
| credential access | brute force: password spraying | `T1110.003` | attempt of one common password against many accounts. |

## Links to other modules

| source | this technique | effect |
| :--- | :--- | :--- |
| [domain-enumeration](<../domain-enumeration/README.en.md>) | kerbrute spraying | the lockout policy read there determines the safe dosing |
| kerbrute (obtained credential) | [bloodhound](<../bloodhound/README.en.md>) / whole module | provides the initial domain foothold |
| password spraying | [05-social-engineering](<../../../05-social-engineering/README.en.md>) | alternative/complement to phishing for initial access |

---

> **Note:** Educational and methodology content. Execution only in owned labs or with explicit authorization. Illustrative outputs, not from real systems.
