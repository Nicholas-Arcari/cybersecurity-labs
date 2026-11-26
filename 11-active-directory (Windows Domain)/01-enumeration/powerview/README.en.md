> **English** | [Italiano](README.md)

# PowerView - Active Directory enumeration from Windows

> - **Phase:** Credential Access / Discovery in the domain - offensive AD enumeration from a Windows host
> - **Visibility:** Medium - generates LDAP queries toward the DC; with PowerShell Script Block Logging (Event ID 4104) the functions are traceable
> - **Prerequisites:** a domain user context (even low-privilege) on a Windows host in the domain; PowerView loaded in memory (PowerSploit/dev module)
> - **Technique:** `PowerView (AD enum)` | **Typical severity:** `Informational` | **Finding ID:** to assign in lab (methodology)

- Objective: map users, groups, computers, ACLs, trusts and attack paths of the domain from a Windows host, complementing [BloodHound](<../bloodhound/README.en.md>) with targeted, scriptable queries.

---

## Executive summary

PowerView is the reference PowerShell tool for offensive Active Directory enumeration: it queries the domain
over LDAP and returns filterable PowerShell objects. Where BloodHound collects everything and visualizes it as a
graph, PowerView is surgical and scriptable: useful for targeted questions ("who has rights over this object?",
"where am I local admin?") and for chaining enumeration with action. It is the swiss-army knife of the
enumeration side, to be loaded in memory (avoids files on disk).

## Execution / commands

### Basic enumeration

```powershell
Get-Domain                                   # current domain info
Get-DomainController                          # the domain controllers
Get-DomainUser -Identity administrator        # details of a user
Get-DomainUser -Properties samaccountname,description,memberof   # selected fields
Get-DomainGroup "Domain Admins" | Get-DomainGroupMember          # members of a privileged group
Get-DomainComputer -Properties dnshostname,operatingsystem       # the domain computers
```

### Attack paths and sessions

```powershell
Find-LocalAdminAccess                         # where the current user is local admin
Find-DomainUserLocation -UserGroupIdentity "Domain Admins"   # where DAs are logged in (user hunting)
Get-NetSession -ComputerName srv01            # active sessions on a host
Invoke-UserHunter -CheckAccess                # cross-reference: targets with DAs logged in and access
```

### ACLs, delegation and trusts (prelude to escalation)

```powershell
# Exploitable ACLs: who can write over privileged objects (GenericAll/WriteDACL/WriteOwner)
Get-DomainObjectAcl -Identity "Domain Admins" -ResolveGUIDs | ? {$_.ActiveDirectoryRights -match "GenericAll|WriteDacl|WriteOwner"}
Invoke-ACLScanner -ResolveGUIDs               # broad scan of interesting ACLs

Get-DomainUser -SPN                           # accounts with an SPN (Kerberoasting candidates)
Get-DomainUser -PreauthNotRequired            # accounts without pre-auth (AS-REP candidates)
Get-DomainComputer -Unconstrained             # unconstrained delegation
Get-DomainComputer -TrustedToAuth             # constrained delegation
Get-DomainTrust                               # domain/forest trust relationships
```

Illustrative output (representative):

```
samaccountname : svc_sql
ActiveDirectoryRights : GenericAll        <-- the current user can take over svc_sql
```

## Analysis of results

PowerView turns low-privilege access into a map of what is attackable: SPNs for
[Kerberoasting](<../../02-kerberos-attacks/kerberoasting/README.en.md>), accounts without pre-auth for
[AS-REP](<../../02-kerberos-attacks/as-rep-roasting/README.en.md>), exploitable ACLs for
[ACL abuse](<../../04-delegation-acl/acl-abuse/README.en.md>), delegations for
[delegation abuse](<../../04-delegation-acl/delegation-unconstrained-constrained/README.en.md>). Its own
severity is `Informational` (enumeration), but it is the step that enables the subsequent escalations.

## Remediation (blue team)

**Detection.** PowerShell Script Block Logging (Event ID 4104) with typical PowerView patterns (`Get-Domain*`,
`Invoke-ACLScanner`); anomalous volume of LDAP queries from a single host; `Find-LocalAdminAccess` generating
many connections.

**Hardening.** Reduce ACL exposure (Tiering model); limit DA sessions on workstations; enable PowerShell logging
and AMSI; monitor massive LDAP queries.

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `PowerView` | ad enum (powershell) | cli - active | targeted, scriptable domain enumeration from a windows host |
| `BloodHound` / `SharpHound` | graph enum | cli/gui - active | massive collection and visualization of attack paths |
| `ldapsearch` / `windapsearch` | ldap client | cli - active | ldap enumeration from linux (cross-platform equivalent) |

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| discovery | account discovery: domain account | `T1087.002` | enumeration of domain users, groups and computers. |
| discovery | permission groups discovery: domain groups | `T1069.002` | enumeration of privileged group membership. |
| discovery | domain trust discovery | `T1482` | enumeration of trust relationships. |

---

## Links to other modules

| source | this technique | effect |
| :--- | :--- | :--- |
| domain access (low-privilege) | powerview | provides the context to query the domain |
| powerview (spn/acl/delegation) | [02-kerberos-attacks](<../../02-kerberos-attacks/README.en.md>) / [04-delegation-acl](<../../04-delegation-acl/README.en.md>) | pinpoints the targets of the escalations |
| powerview | [bloodhound](<../bloodhound/README.en.md>) | complementary: targeted queries vs full graph |

---

> **Note:** Educational content. Execution only in owned labs or with explicit authorization. Illustrative outputs, not from real systems.
