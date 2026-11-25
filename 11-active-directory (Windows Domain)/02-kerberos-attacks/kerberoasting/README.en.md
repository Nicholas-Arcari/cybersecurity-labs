> **English** | [Italiano](README.md)

# Kerberoasting: offline theft of service-account credentials

> - **Phase:** Credential Access (Active Directory domain)
> - **Visibility:** Medium - generates TGS-REQ requests (Event ID 4769) for the target SPNs; noisy if many SPNs are requested or the RC4 etype is forced
> - **Prerequisites:** any valid domain account (even low privilege); connectivity to a Domain Controller on port 88
> - **Technique:** `Kerberoasting` | **Typical severity:** `High` | **Finding ID:** to assign in lab (methodology page)

- Nature of the document: methodology. Outputs are illustrative and representative, not from a specific lab; example hashes are deliberately truncated and not crackable.
- Objective: obtain, from a non-privileged domain account, the offline-crackable hashes of service-account passwords, then escalate privileges via compromised service accounts.

---

## Executive summary

Kerberoasting is one of the most profitable Credential Access techniques in Active Directory, and the reason
is by design, not a bug. Any authenticated user can ask the Domain Controller for a service ticket (TGS) for
any account that has a Service Principal Name (SPN) associated. That ticket is encrypted with the service
account's long-term key, that is, with a key derived from its password. The attacker does not need to
interact with the service: they extract the ticket and attack it offline, with no further traffic to the
domain and no risk of account lockouts.

The practical value lies in the nature of service accounts: they often have passwords set manually, not
subject to rotation, sometimes years old, and not rarely enjoy elevated privileges (SQL Server, application
service accounts, sometimes members of administrative groups). A single cracked weak password can translate
into a direct jump to significant privileges in the domain.

## Operational context (why, before how)

The realistic starting point is a foothold with low-privilege domain credentials: obtained from password
spraying, phishing, reused credentials or found in cleartext in previous modules. From this position the
attacker looks for low-cost, low-risk escalation vectors. Kerberoasting is ideal because:

- it requires no special privileges: being a domain user is enough;
- the actual attack (the cracking) happens offline, so it is invisible to the domain;
- service accounts are a high-yield target (static passwords, often elevated privileges).

The key operational decision is selectivity: requesting the TGS of all SPNs at once is efficient but noisy
(many close-together Event ID 4769, typical of automated tools). An OPSEC-aware operator first enumerates
the interesting SPNs (service accounts with privileged group memberships, identified via BloodHound) and
requests only those.

## Execution / commands

### Phase 1 - SPN enumeration

From Linux, with Impacket, using valid domain credentials:

```bash
# Lists accounts with an SPN (potential Kerberoast targets), without requesting their hashes yet
GetUserSPNs.py corp.local/utente:'Password123' -dc-ip 10.10.10.10
```

Illustrative output (representative):

```
ServicePrincipalName    Name       MemberOf                              PasswordLastSet
----------------------  ---------  ------------------------------------  -------------------
MSSQLSvc/db01.corp.local svc_sql    CN=SQL Admins,OU=Service,DC=corp,...  2019-02-11 09:03   <-- old password, priority target
HTTP/web01.corp.local    svc_web    CN=Domain Users,...                   2024-10-01 12:20
```

The `PasswordLastSet` column is a priority indicator: the older the password, the more likely it is weak and
never rotated.

### Phase 2 - TGS request (the "roast")

```bash
# Requests the TGS and saves the hashes in hashcat format; -request obtains the crackable material
GetUserSPNs.py corp.local/utente:'Password123' -dc-ip 10.10.10.10 -request -outputfile kerb_hashes.txt
```

From a Windows host, the equivalent with Rubeus (targeted at a single account, more OPSEC-friendly):

```
# Rubeus: roasting of the single target account
Rubeus.exe kerberoast /user:svc_sql /nowrap
```

Illustrative output (truncated, non-crackable hash, shown only for the format):

```
$krb5tgs$23$*svc_sql$CORP.LOCAL$MSSQLSvc/db01*$a1b2c3...[TRUNCATED]...9f  <-- etype 23 (RC4): offline crackable
```

The prefix `$krb5tgs$23$` indicates encryption type 23 (RC4-HMAC): the key coincides with the NT hash of the
password, with no salt and no iterations, so the offline attack is fast. A `$krb5tgs$18$` prefix indicates
AES256, much slower to attack.

### Phase 3 - offline cracking

```bash
# Mode 13100 = Kerberos 5 TGS-REP etype 23 (RC4). For AES256 use 19700, for AES128 19600
hashcat -m 13100 kerb_hashes.txt /usr/share/wordlists/rockyou.txt
```

Illustrative output:

```
$krb5tgs$23$*svc_sql$CORP.LOCAL$MSSQLSvc/db01*$a1b2...:SqlProd2019!   <-- recovered password
```

## Analysis of results

Recovering the password of `svc_sql` has a twofold meaning. On the immediate level, it provides valid
credentials to authenticate as that service account (in this example, an account that is a member of a SQL
Server administrative group). On the kill-chain level, it turns a low-privilege foothold into privileged
access without having touched the Domain Controller and without generating a single failed login: all the
brute-force work happened offline, on the attacker's machine.

Not all roasts succeed: a service account with a long, random password (or a gMSA) produces a hash that,
even if extracted, remains uncrackable in useful time. The real finding, in a lab, would be classified by
the actual outcome: `High` if a privileged password is recovered, `Medium` or `Informational` if the SPNs
exist but the passwords resist.

### Theoretical analysis

Kerberoasting does not break Kerberos cryptography: it exploits its authorization model. In the Kerberos
flow (see [THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.en.md>), section 3.1), the KDC responds to
a TGS-REQ by issuing a TGS encrypted with the service account's key, without verifying whether the requester
is authorized to use that service: access control is delegated to the service itself. It follows that any
authenticated principal can obtain a TGS for any SPN. The violation is of property P2 (confidentiality of
long-term keys): since with etype 23 the key coincides with the NT hash of the password, the TGS is an
offline oracle on the password.

The choice of Impacket (`GetUserSPNs.py`) from Linux versus Rubeus from Windows depends on the foothold: on a
Linux shell or an attacker machine with credentials, Impacket is natural; on an already-compromised Windows
host, Rubeus avoids bringing Python tools and integrates with the current session. In both cases the
theoretical lever is identical.

## Remediation (blue team)

**Detection (SOC/SIEM).**

- Event ID 4769 (Kerberos Service Ticket Operation) on the Domain Controller: an anomalous volume of requests
  from a single principal in a few seconds is the typical pattern of mass Kerberoasting tools.
- 4769 requests with `Ticket Encryption Type = 0x17` (RC4) in an environment that should use AES: a sign of
  a forced downgrade for offensive purposes.
- Correlation with honeypot accounts: create a "decoy" account with an SPN and a strong password, and alert
  on any TGS requested for it (no legitimate use expected).

**Hardening.**

- Use Group Managed Service Accounts (gMSA): 240-bit passwords managed and rotated by the domain, practically
  uncrackable offline.
- Where gMSA are not applicable, enforce long, random passwords (25+ characters) for service accounts and
  rotate them periodically.
- Disable the RC4 etype in the domain and force AES, drastically reducing cracking speed.
- Apply least privilege to service accounts: a service account must not belong to administrative groups
  unless strictly necessary.

---

## Real-World scenario: Post-Exploitation projection

> This section describes how a successful Kerberoasting would fit into a real engagement, from the attacker's
> (Red Team) and the defender's (Blue Team) perspective.

### Attacker perspective (red team)

**Starting point:** foothold with low-privilege domain credentials; SPN enumeration complete.

**Immediate next step:** targeted request of the TGS of the identified privileged service account (e.g.,
`svc_sql`) and offline cracking of the password.

**Projected Kill Chain:**

```
Low-priv domain user
        |
        v
Kerberoasting (svc_sql) -> service-account password recovered offline
        |
        v
Access as svc_sql (local admin on DB server / privileged group member)
        |
        v
Credential dumping on the reached server -> hashes of other accounts
        |
        v
Escalation to Domain Admin (e.g., via ACL/delegation) -> DCSync
        |
        v
Golden Ticket -> domain persistence
```

**Potential impact:** a compromise that starts from a simple user and reaches, through a forgotten service
account, elevated privileges in the domain. In public incident data (Verizon DBIR), the "compromised
credentials" vector is among the most recurrent; static service accounts are a frequent cause.

**Typical monetization vectors:**
- Enterprise ransomware after reaching domain privileges.
- Exfiltration of sensitive data from the systems reached with the service account (e.g., production
  database).
- Resale of the privileged access as an Access Broker.

### Defender perspective (blue team)

**Detection:** spike of Event ID 4769, in particular with RC4 etype, from a single account in a narrow
interval; TGS requests for honeypot accounts.

**Indicators of Compromise (IOC):**
- Event ID 4769 in anomalous volume from a single principal toward many SPNs.
- Presence of RC4 etype (0x17) in TGS where only AES is expected.
- Processes such as `Rubeus` or execution of `GetUserSPNs` from non-administrative hosts.

**Containment:** immediate password reset of potentially exposed service accounts; session revocation;
investigation of accesses made with those accounts.

**Eradication and hardening:** migration to gMSA; disabling of RC4; least privilege on service accounts;
continuous monitoring of 4769.

**Defensive lesson:** the robustness of Kerberos does not protect against a weak password on a privileged
service account. The effective control is not on the protocol but on service-identity management (entropy,
rotation, privileges).

---

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `GetUserSPNs.py` (impacket) | python toolkit | cli - active | spn enumeration and roasting from linux/attacker machine |
| `Rubeus` | .net tool | cli - active | kerberoasting from a compromised windows host, targeted and opsec-friendly |
| `hashcat` | gpu cracker | cli - offline | cracking of tgs hashes (13100 rc4, 19600 aes128, 19700 aes256) |
| `john` (jumbo) | cpu cracker | cli - offline | alternative to hashcat for cracking tgs |
| `BloodHound` / `SharpHound` | graph enum | cli/gui - active | identify which service accounts are privileged, for selective roasting |
| `NetExec` (`nxc`) | ad/smb toolkit | cli - active | integrated kerberoasting module and related actions |

---

## Methodology notes

As this is a methodology page, there are no own lab outputs. In a real lab (e.g., GOAD) the points of
attention to document would be: the cracking time as a function of etype (RC4 vs AES) and wordlist quality,
the noise generated on the 4769 logs, and the practical difference between mass and targeted roasting. Once
measured, these data must be reported as a real finding (`AD-NNN`) and, if quantitative, in the `EVALUATION/`
folder with the relevant validity note.

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| credential access | steal or forge kerberos tickets: kerberoasting | `T1558.003` | tgs request for service-account spns and offline cracking of the password. |
| discovery | account discovery: domain account | `T1087.002` | enumeration of accounts with an spn via domain queries. |
| credential access | brute force: password cracking | `T1110.002` | offline cracking of the tgs hash with wordlist/rules. |

---

## Links to other modules

| source | this technique | effect |
| :--- | :--- | :--- |
| password spraying / phishing ([05-social-engineering](<../../../05-social-engineering/README.en.md>)) | kerberoasting | provides the initial domain account needed for roasting |
| kerberoasting | password cracking ([04-system-exploitation/05-password-cracking](<../../../04-system-exploitation/05-password-cracking/hashcat/README.en.md>)) | the tgs hashes are cracked with hashcat/john already documented in the repo |
| kerberoasting | [dcsync](<../../05-credential-dumping/dcsync/README.en.md>) | a privileged service account can enable the chain toward replication rights |

---

> **Note:** All described techniques are for educational and methodology-documentation purposes. They must be
> executed only in owned labs or on systems with explicit authorization. Outputs are illustrative and do not
> come from real or third-party systems.
