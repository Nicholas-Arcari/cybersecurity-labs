> **English** | [Italiano](README.md)

# Golden Ticket: domain persistence via TGT forgery

> - **Phase:** Persistence / Privilege Escalation (Active Directory domain)
> - **Visibility:** Low at issuance (the ticket is forged offline, no request to the KDC), potentially detectable at use (anomalies in the ticket)
> - **Prerequisites:** possession of the NT hash (or AES key) of the `krbtgt` account and the domain SID; both are typically obtained from a DCSync
> - **Technique:** `Golden Ticket` | **Typical severity:** `Critical` | **Finding ID:** to assign in lab (methodology)

- Nature of the document: methodology. Illustrative outputs; placeholder keys/SID.
- Objective: forge a TGT valid for any identity and with arbitrary privileges, obtaining persistent and hard-to-eradicate access to the domain.

---

## Executive Summary

The Golden Ticket is domain persistence par excellence. The TGT (Ticket Granting Ticket) is encrypted and
signed with the `krbtgt` account's key: whoever holds that key can forge arbitrary TGTs, for any user (even
nonexistent) and with any group membership, without interacting with the KDC for issuance. The DC will
accept these tickets as legitimate, because they are signed with the correct key.

It is the typical final stage after a DCSync: with the obtained `krbtgt` hash, the attacker secures access
that survives the reset of user passwords. The only way to invalidate a Golden Ticket is to change the
`krbtgt` password twice (AD keeps the current and the previous key), an operation many organizations never
perform.

## Operational context (why, before how)

The Golden Ticket is not an initial-access vector but one of persistence and total domain control: it
presupposes having already compromised krbtgt. It sits downstream of
[DCSync](<../../05-credential-dumping/dcsync/README.en.md>). The operational decision concerns OPSEC: Golden
Tickets with anomalous parameters (decade-long lifetime, nonexistent user, inconsistent groups) are easier
to detect. A careful operator forges tickets with plausible parameters (standard lifetime, real user) to
reduce signals, and uses AES instead of RC4 to avoid downgrade-based detection.

## Execution / Commands

### Forgery (Impacket ticketer)

```bash
# Forges a TGT using the krbtgt NT hash and the domain SID; produces a .ccache file
ticketer.py -nthash <HASH_KRBTGT> -domain-sid S-1-5-21-<PLACEHOLDER> -domain corp.local fakeadmin
```

```bash
# Using the forged ticket: export the variable and authenticate without a password
export KRB5CCNAME=fakeadmin.ccache
secretsdump.py -k -no-pass corp.local/fakeadmin@dc01.corp.local
```

### Forgery (Mimikatz, from Windows)

```
kerberos::golden /user:fakeadmin /domain:corp.local /sid:S-1-5-21-<PLACEHOLDER> /krbtgt:<HASH_KRBTGT> /ptt
```

Illustrative output (representative):

```
[*] Saving ticket in fakeadmin.ccache
# the ticket is now usable to authenticate as 'fakeadmin' with arbitrary privileges
```

## Analysis of results

The Golden Ticket turns possession of a key (krbtgt) into persistent control of the domain. It is not "one
more access": it is a master key that bypasses normal authentication. The severity is `Critical` because the
impact is durable control and the difficulty of eradication: until krbtgt is rotated twice, the forged
tickets remain valid even after resetting all other passwords.

### Theoretical Analysis

The root of the Golden Ticket is structural in Kerberos (see
[THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.en.md>), sec. 3.1): the TGT is encrypted and signed
with the krbtgt key, and the DC trusts any correctly signed TGT, with no further verification of the
requester's identity at use time. Whoever knows the krbtgt key can therefore impersonate the KDC in the
issuance part. It is the deepest violation of property P1 (authentication): the attacker does not
authenticate, they forge the material that proves authentication. The fact that revocation requires a double
krbtgt reset derives from the two-key (current/previous) management designed for replication continuity, not
for offensive security.

## Remediation (Blue Team)

**Detection.** TGT with anomalous lifetime (well beyond the default 10 hours / 7 days of renewal); tickets
for nonexistent users or with groups inconsistent with the real object; use of RC4 where AES is expected;
PAC anomalies. Solutions such as EDR/AD behavioral detection look precisely for these inconsistencies.

**Hardening.** Protect krbtgt (its compromise is the real problem: see DCSync); in case of suspected
compromise, rotate the krbtgt password twice in a controlled sequence; apply the Tiering Model and limit
replication rights to prevent obtaining the key upstream; monitor TGT parameters.

---

## Real-World Scenario: Post-Exploitation Projection

> The Golden Ticket is already an advanced stage: the scenario describes persistence and its consequences.

### Attacker Perspective (Red Team)

**Starting point:** krbtgt hash obtained (typically via DCSync) and domain SID known.

**Immediate next step:** forge a TGT with plausible parameters and inject it into the session.

**Projected Kill Chain:**

```
krbtgt hash (from DCSync)
        |
        v
Golden Ticket forged (arbitrary TGT, signed with krbtgt)
        |
        v
Access to any domain service as any user
        |
        v
Durable persistence: survives the reset of user passwords
        |
        v
Continuous exfiltration / re-entry at will / ransomware across the whole domain
```

**Potential impact:** persistent control of the domain. One of the most severe scenarios overall for an
organization, because remediation requires a specific action (double krbtgt reset) often unknown to
non-specialized teams.

**Typical monetization vectors:** persistent access resold; delayed ransomware; prolonged data exfiltration.

### Defender Perspective (Blue Team)

**Detection:** TGT anomalies (lifetime, user, groups, etype); use of tickets for nonexistent accounts.

**Indicators of Compromise (IOC):** tickets with out-of-policy lifetime; RC4 TGT in an AES environment;
privileged activity from a principal with no record of having logged in to the KDC.

**Containment:** double krbtgt reset; session invalidation; hunting for accesses made with forged tickets.

**Eradication and hardening:** prevent krbtgt compromise upstream (confinement of replication rights,
Tiering); planned krbtgt rotation; monitoring of ticket parameters.

**Defensive lesson:** once krbtgt is compromised, the domain is persistently compromised. The defense is not
"detecting the Golden Ticket" but preventing krbtgt from ever being exfiltrated, and knowing how to perform
the correct rotation when needed.

---

## Reference tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `ticketer.py` (Impacket) | Kerberos tool | CLI - Active | Golden Ticket forgery from Linux |
| `Mimikatz` | Credential/ticket tool | CLI - Active | `kerberos::golden` from a Windows host, with injection (ptt) |
| `Rubeus` | .NET Kerberos tool | CLI - Active | Ticket forgery/use and manipulation from Windows |
| `klist` / `kinit` | Native Kerberos | CLI | Management and verification of tickets in cache |

## Methodology notes

In a real lab document: the forgery from the krbtgt hash obtained in DCSync, the use of the ticket to access
a service, and the proof that it survives a user password reset. Also document the remediation procedure
(double krbtgt reset) as a verified countermeasure.

## MITRE ATT&CK mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Credential Access | Steal or Forge Kerberos Tickets: Golden Ticket | `T1558.001` | Forgery of an arbitrary TGT signed with the krbtgt key. |
| Persistence | Account Manipulation | `T1098` | Persistent domain access independent of user credentials. |
| Lateral Movement | Use Alternate Authentication Material: Pass the Ticket | `T1550.003` | Use of the forged ticket to authenticate to services. |

## Links to other modules

| Source | This technique | Effect |
| :--- | :--- | :--- |
| [DCSync](<../../05-credential-dumping/dcsync/README.en.md>) | Golden Ticket | provides the krbtgt hash, a prerequisite of the forgery |
| Golden Ticket | [07-post-exploitation - persistence](<../../../07-post-exploitation/README.en.md>) | it is the most powerful form of domain persistence |
| [Silver Ticket](<../silver-ticket/README.en.md>) | Golden Ticket | the Silver is the service-limited variant; the Golden is domain-wide |

---

> **Note:** All described techniques are for educational and methodology-documentation purposes. Execution only in owned labs or with explicit authorization. Illustrative outputs, not from real systems.
