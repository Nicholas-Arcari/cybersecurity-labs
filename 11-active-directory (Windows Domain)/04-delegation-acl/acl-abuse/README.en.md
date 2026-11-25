> **English** | [Italiano](README.md)

# ACL / DACL abuse: GenericAll, WriteDACL, WriteOwner, AddKeyCredentialLink

> - **Phase:** Privilege Escalation (Active Directory domain)
> - **Visibility:** Medium - modifications to AD objects (password reset, group addition, attribute writes) leave directory-modification events (Event ID 5136/4728/4738)
> - **Prerequisites:** possession of an extended or write right over an AD object (user, group, computer or domain object), typically identified with BloodHound
> - **Technique:** `ACL/DACL abuse` | **Typical severity:** `High` (up to `Critical` if it leads to DCSync) | **Finding ID:** to assign in lab (methodology)

- Nature of the document: methodology. Illustrative outputs; placeholder identifiers.
- Objective: convert a right over an AD object into a concrete escalation (password reset, addition to a privileged group, granting oneself replication rights).

---

## Executive Summary

Active Directory ACLs define who can do what on each object. Some rights, if granted to untrusted principals
(by mistake, inheritance or overly broad administrative delegation), translate directly into escalation:

- **GenericAll / GenericWrite:** full control or write over the object, enabling a password reset (on a
  user), member addition (on a group), or writing sensitive attributes.
- **WriteDACL:** the ability to modify the object's own ACL, hence to grant oneself any other right
  (including, on the domain object, the replication rights for DCSync).
- **WriteOwner:** becoming the object's owner and then rewriting its ACL.
- **AddKeyCredentialLink:** writing `msDS-KeyCredentialLink` to enable certificate-based authentication as
  the victim (Shadow Credentials).

BloodHound highlights these relationships as edges in the graph: a chain of misconfigured ACLs is a path to
the domain.

## Operational context (why, before how)

ACL abuse is the "glue" of many BloodHound chains: rarely does a single right lead to Domain Admin, but a
sequence (A can reset B, B has WriteDACL on C, C is in a privileged group) does. The operational decision is
to choose the least noisy and most reversible action that advances the chain: often a temporary group
addition or a password reset, to be undone at the end of the test to reduce client impact.

## Execution / Commands

### GenericAll on a user: password reset

```bash
# With GenericAll/ForceChangePassword on a user, set a new password for them
net rpc password "utente_bersaglio" "NuovaPass123!" -U "corp.local/utente%Password123" -S 10.10.10.10
```

### GenericAll on a group: member addition

```bash
# With rights on the group, add the controlled account to a privileged group
net rpc group addmem "GruppoPrivilegiato" "utente" -U "corp.local/utente%Password123" -S 10.10.10.10
```

### WriteDACL on the domain object: grant oneself DCSync

```bash
# Grants the account the replication rights (DS-Replication-Get-Changes*) -> enables DCSync
dacledit.py -action write -rights DCSync -principal utente -target-dn 'DC=corp,DC=local' \
  corp.local/utente:'Password123'
```

Illustrative output (representative):

```
[*] DACL modified successfully! 'utente' now has replication rights   <-- can now DCSync
```

## Analysis of results

The outcome depends on the right and the object: a password reset provides an additional account, addition to
a privileged group provides the group's privileges, granting replication rights leads directly to DCSync
(severity `Critical`). The typical severity is `High`, but it rises to `Critical` when the chain ends in the
full domain. The real finding must be documented specifying the right exploited, the action performed and the
result.

### Theoretical Analysis

ACLs are the mechanism with which AD implements discretionary access control over objects. Their security is
a property of the whole authorization graph (property P3): a single right may be harmless, but the
composition of several rights creates escalation paths. WriteDACL is particularly critical because it is
"meta": it allows modifying the permissions themselves, hence self-granting any other right, including the
replication right that enables DCSync. This is why BloodHound models these relationships as edges: the problem
is not the single permission but the reachability in the graph. See
[THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.en.md>).

## Remediation (Blue Team)

**Detection.** Event ID 5136 (directory object modification) on sensitive objects/attributes; 4728/4732
(addition to a privileged group); 4724 (password reset); modifications to the domain object's DACL.

**Hardening.** Periodic ACL audit with BloodHound/dedicated tools to identify and remove excessive rights;
apply the Tiering Model; limit broad administrative delegation; prioritize monitoring of changes to the
domain object's DACL (precursor to DCSync).

---

## Real-World Scenario: Post-Exploitation Projection

> When the ACL chain ends with replication rights, the outcome is the domain (severity Critical).

### Attacker Perspective (Red Team)

**Starting point:** a right over an AD object (from BloodHound), e.g., WriteDACL on a group or on the domain
object.

**Immediate next step:** exploit the right to advance the chain (reset, add-member, or grant DCSync).

**Projected Kill Chain:**

```
ACL right over an object (from BloodHound)
        |
        v
Advance in the chain (password reset / add to group / WriteDACL)
        |
        v
WriteDACL on the domain object -> self-grant of replication rights
        |
        v
DCSync -> full domain -> Golden Ticket / persistence
```

**Potential impact:** domain compromise through chaining of ACL rights, often without a single exploit.

**Typical monetization vectors:** ransomware/exfiltration downstream of the domain; access brokering.

### Defender Perspective (Blue Team)

**Detection:** Event ID 5136 on the domain DACL; 4728/4724 for anomalous group additions and password resets.

**Indicators of Compromise (IOC):** granting of replication rights to a non-DC account; unexpected addition
to privileged groups; password resets not requested by the help desk.

**Containment:** revoke the anomalously granted rights; remove from groups; reset the involved accounts;
investigate recent replications (if DCSync rights were granted).

**Eradication and hardening:** remediate excessive ACLs (BloodHound audit); Tiering Model; priority
monitoring of the domain DACL.

**Defensive lesson:** AD security is a property of the overall permission graph. A "small" right in the wrong
place can be the link that opens the chain to the domain. The defense is systematic ACL auditing, not control
of the single object.

---

## Reference tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `dacledit.py` (Impacket) | AD tool | CLI - Active | Reading/writing DACLs (e.g., granting DCSync rights) |
| `net rpc` (Samba) | AD tool | CLI - Active | Password reset and group management via RPC |
| `PowerView` | PowerShell | CLI - Active | ACL enumeration and abuse from a Windows host |
| `BloodHound` | Graph enum | GUI | Identification of exploitable ACL relationships |
| `bloodyAD` | AD tool | CLI - Active | Manipulation of AD objects and attributes from Linux |

## Methodology notes

In a real lab document: the ACL right identified (from BloodHound), the action performed
(reset/add/WriteDACL) and the result. Important on the ethical/operational side: undo the changes (remove
from groups, restore ACLs) at the end of the test to avoid leaving the domain in an altered state.

## MITRE ATT&CK mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Persistence | Account Manipulation | `T1098` | Modification of AD objects/attributes (password reset, group addition, DACL). |
| Privilege Escalation | Domain or Tenant Policy Modification | `T1484` | Modification of domain-level permissions (WriteDACL on the domain object). |
| Credential Access | OS Credential Dumping: DCSync | `T1003.006` | Outcome: self-granting of replication rights and DCSync. |

## Links to other modules

| Source | This technique | Effect |
| :--- | :--- | :--- |
| [BloodHound](<../../01-enumeration/bloodhound/README.en.md>) | ACL abuse | identifies the ACL rights and exploitable chains |
| ACL abuse (WriteDACL on domain) | [DCSync](<../../05-credential-dumping/dcsync/README.en.md>) | self-granting replication rights enables DCSync |
| ACL abuse (AddKeyCredentialLink) | [Shadow Credentials](<../../05-credential-dumping/shadow-credentials/README.en.md>) | writing msDS-KeyCredentialLink for certificate-based auth |

---

> **Note:** All described techniques are for educational and methodology-documentation purposes. Execution only in owned labs or with explicit authorization. Illustrative outputs, not from real systems.
