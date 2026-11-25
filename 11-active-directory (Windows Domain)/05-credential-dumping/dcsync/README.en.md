> **English** | [Italiano](README.md)

# DCSync: extracting domain hashes via abused replication

> - **Phase:** Credential Access (Active Directory domain) - capstone toward the full domain
> - **Visibility:** Low-Medium - no code executed on the Domain Controller and no file touched; the main trace is the replication request from an unexpected principal/host (Event ID 4662)
> - **Prerequisites:** an account with the extended replication rights on the domain object (Domain Admin, Enterprise Admin, a DC's machine account, or an account with explicit delegation of those rights); connectivity to a Domain Controller
> - **Technique:** `DCSync` | **Typical severity:** `Critical` | **Finding ID:** to assign in lab (methodology)

- Nature of the document: methodology. Illustrative outputs; example hashes truncated or placeholder.
- Objective: extract the password hashes of any domain account - including `krbtgt` and the Domain Admins - without executing code on the Domain Controller and without physically accessing the NTDS.dit file.

---

## Executive Summary

DCSync is the technique that, in practice, marks total domain compromise. It exploits the Domain Controller
replication protocol (MS-DRSR): a DC that joins the forest must receive a copy of the identity database from
the other DCs, and periodically the DCs synchronize. DCSync impersonates a DC and issues a legitimate
replication request, asking the target DC for an account's attributes, including the secrets (NT hashes,
Kerberos keys). The DC responds believing it is talking to another Domain Controller.

The crucial point is that the DC does not verify whether the requester really is a DC: it only verifies
whether the requesting account holds the extended replication rights in the domain object's ACL. This makes
DCSync much quieter than the historical alternatives (compromise the DC, copy NTDS.dit, extract offline): no
access to the DC is needed and no suspicious files are left behind. With the `krbtgt` hash obtained from
DCSync, you then forge a Golden Ticket, domain persistence par excellence.

## Operational context (why, before how)

DCSync is the step that turns "elevated privileges" into "full domain". You reach the point of being able to
DCSync in two ways: by having obtained an already-privileged account (Domain Admin via escalation, or a DC's
machine account via ESC8), or by having compromised a non-admin account that, through misconfiguration, has
been delegated the replication rights (a typical pattern: an AD backup or synchronization service account).

The key operational decision is selectivity, for OPSEC: a full DCSync of the entire domain is far more
visible than a targeted DCSync of just `krbtgt` and a few privileged accounts. A careful operator first
requests only what is needed (krbtgt for the Golden Ticket, the domain Administrator), reducing the volume of
anomalous replication requests.

## Execution / Commands

### Phase 1 - Verify the replication rights

Before acting, the operator verifies who holds the replication rights on the domain object (to understand
whether the current account can DCSync, or which account to target).

```bash
# Enumeration of the domain ACLs looking for the replication rights (from Linux, with BloodHound/ldap)
# In BloodHound: look for the "DCSync" / "GetChanges + GetChangesAll" privilege on the accounts
```

Illustrative output (representative):

```
svc_backup  has  DS-Replication-Get-Changes + DS-Replication-Get-Changes-All  on the domain object
                                                     <-- non-admin account with delegated replication rights: vector
```

The relevant rights are three (see [THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.en.md>), sec. 3.3):
DS-Replication-Get-Changes, DS-Replication-Get-Changes-All, DS-Replication-Get-Changes-In-Filtered-Set.

### Phase 2 - Targeted DCSync (OPSEC)

```bash
# secretsdump (Impacket): DCSync of krbtgt only. -just-dc-user limits the request to a single account
secretsdump.py corp.local/svc_backup:'Password123'@10.10.10.10 -just-dc-user krbtgt
```

Illustrative output (truncated, unusable hash):

```
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:<NT_HASH_TRUNCATED>:::   <-- key for the Golden Ticket
```

The `aad3b435b51404eeaad3b435b51404ee` portion is the empty-LM hash constant (LM disabled in modern Windows
versions): it is normal and not a secret.

### Phase 3 - Full DCSync (if allowed by scope)

```bash
# Dump of all domain accounts (noisier): -just-dc extracts NT hashes and Kerberos keys
secretsdump.py corp.local/svc_backup:'Password123'@10.10.10.10 -just-dc
```

From a Windows host, the equivalent with Mimikatz:

```
lsadump::dcsync /domain:corp.local /user:krbtgt
```

## Analysis of results

The result of a DCSync targeted at `krbtgt` is not "one more credential": it is the key that signs all the
domain's TGTs. From it you forge a Golden Ticket valid for any user (even nonexistent) with arbitrary
privileges. The full DCSync instead provides the entire domain credential material, from which Pass-the-Hash
toward any account and offline cracking of service accounts.

The severity is `Critical` because the outcome, in both cases, is effective and durable control of the domain.
It is important to note what DCSync does not require: no interactive login on the DC, no files copied, no
suspicious process running on the controller. This makes it as powerful as it is hard to detect without
specific replication monitoring.

### Theoretical Analysis

DCSync breaks nothing: it abuses the MS-DRSR protocol exactly as it is designed (see
[THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.en.md>), sec. 3.3). The violation is of property P3
(confinement of authority): replication rights should be confined to Domain Controllers, but the domain
object's ACL can grant them - by mistake or by practice - to principals that are not DCs. The DC's access
control is correct in its reference (it checks the rights in the ACL), but the ACL itself is the weak link.

The choice of secretsdump from Linux versus Mimikatz from Windows depends on the foothold: with credentials
and a Linux attacker machine, Impacket is immediate and requires no code on the target; on a Windows host
already in session, Mimikatz exploits the current context. In both cases the lever is the replication right,
not a cryptographic flaw.

## Remediation (Blue Team)

**Detection (SOC/SIEM).**

- Event ID 4662 on the Domain Controller with the GUIDs of the extended replication rights
  (`1131f6aa-...` and `1131f6ad-...`): a request of this kind from an account or host that is not a DC is a
  high-fidelity indicator of DCSync.
- DRSUAPI replication traffic (`IDL_DRSGetNCChanges`) coming from an IP that does not belong to a known
  Domain Controller.
- Correlation: a service account (e.g., backup) that suddenly makes replication requests.

**Hardening.**

- Review and reduce the replication rights on the domain object: only DCs and strictly necessary accounts
  should hold them. Remove historical delegations no longer justified.
- Adopt a Tiering Model for administrative accounts (clear separation between domain accounts and work
  accounts).
- Specifically monitor Event ID 4662 with the replication GUIDs and replication from non-DC sources.
- In case of a suspected Golden Ticket, reset the `krbtgt` password twice in a controlled sequence (AD keeps
  the current and the previous key, so a single reset does not invalidate the forged tickets).

---

## Real-World Scenario: Post-Exploitation Projection

> How DCSync would fit into a real engagement, from the attacker's and the defender's perspective.

### Attacker Perspective (Red Team)

**Starting point:** possession of an account with replication rights (Domain Admin obtained via escalation, a
DC's machine account via ESC8, or a service account with delegated replication).

**Immediate next step:** DCSync targeted at the `krbtgt` hash to set up persistence.

**Projected Kill Chain:**

```
Account with replication rights
        |
        v
Targeted DCSync (krbtgt + Domain Admin) -> NT hashes and Kerberos keys
        |
        v
Golden Ticket (from krbtgt) -> impersonation of any user, arbitrary privileges
        |
        v
Pass-the-Hash toward any system in the domain -> total access
        |
        v
Persistence: long-lived Golden Ticket; possible creation of a backdoor account
        |
        v
Data exfiltration / ransomware deployment across the whole domain
```

**Potential impact:** total and persistent domain compromise. The derived Golden Ticket is particularly
insidious because it is not invalidated by a single krbtgt reset.

**Typical monetization vectors:**
- Enterprise ransomware with mass encryption via GPO/management tools.
- Double extortion with exfiltration of the domain's sensitive data.
- Access brokering of the Domain Admin control.

### Defender Perspective (Blue Team)

**Detection:** Event ID 4662 with the replication GUIDs from non-DC principals/hosts; DRSUAPI replication
from an IP not belonging to the DCs.

**Indicators of Compromise (IOC):**
- 4662 with `DS-Replication-Get-Changes-All` requested by a non-DC account (e.g., `svc_backup`).
- Replication requests from workstations or from an attacker IP instead of between DCs.
- Subsequent appearance of TGTs with an anomalous lifetime (a symptom of a Golden Ticket).

**Containment:** disable the abused account; isolate the source host; reset `krbtgt` twice; investigate
sessions and issued tickets.

**Eradication and hardening:** reduce replication rights to the only necessary entities; Tiering Model;
continuous monitoring of 4662; periodic review of delegations on the domain object.

**Defensive lesson:** a powerful right (replication) granted lightly to a non-DC account nullifies the
separation between "controller" and "rest of the domain". The defense is rigorous management of privileged
ACLs, not a patch: there is nothing to patch, only to confine.

---

## Reference tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `secretsdump.py` (Impacket) | Python toolkit | CLI - Active | DCSync from Linux (`-just-dc`, `-just-dc-user`), without code on the DC |
| `Mimikatz` | Credential tool | CLI - Active | `lsadump::dcsync` from a Windows host in a privileged session |
| `NetExec` (`nxc`) | AD/SMB toolkit | CLI - Active | `ntdsutil`/`dcsync` module and related actions |
| `BloodHound` / `SharpHound` | Graph enum | CLI/GUI - Active | Identify who holds the replication rights (the "DCSync" privilege) |
| `ticketer.py` (Impacket) | Kerberos tool | CLI - Active | Forging the Golden Ticket downstream, with the obtained krbtgt hash |

---

## Methodology notes

In a real lab (e.g., GOAD) the finding to document would include: which account holds the replication rights
(and whether it is an unjustified delegation), the outcome of the targeted vs full DCSync, and verification of
detection on the blue-team side (appearance of Event ID 4662 with the replication GUIDs). Once observed, these
outcomes become the real finding (`AD-NNN`).

## MITRE ATT&CK mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Credential Access | OS Credential Dumping: DCSync | `T1003.006` | Abused replication request (MS-DRSR) to extract hashes and keys from the DC. |
| Credential Access | Steal or Forge Kerberos Tickets: Golden Ticket | `T1558.001` | Follow-on: use of the obtained krbtgt hash for the Golden Ticket. |
| Lateral Movement | Use Alternate Authentication Material: Pass the Hash | `T1550.002` | Follow-on: authentication with the extracted NT hashes. |

## Links to other modules

| Source | This technique | Effect |
| :--- | :--- | :--- |
| [Kerberoasting](<../../02-kerberos-attacks/kerberoasting/README.en.md>) / [ESC8](<../../03-adcs/esc8-relay-adcs/README.en.md>) | DCSync | provide the privileged account (or the DC's credentials) with replication rights |
| DCSync (krbtgt hash) | Golden Ticket ([02-kerberos-attacks](<../../02-kerberos-attacks/README.en.md>)) | the krbtgt key enables domain persistence |
| DCSync (NT hashes) | Pass-the-Hash ([07-post-exploitation](<../../../07-post-exploitation/README.en.md>)) | the extracted hashes enable lateral movement without cracking |

---

> **Note:** All described techniques are for educational and methodology-documentation purposes. Execution only in owned labs or with explicit authorization. Illustrative outputs, not from real systems.
