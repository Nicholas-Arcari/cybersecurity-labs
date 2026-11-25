> **English** | [Italiano](README.md)

# 11.1 - Domain enumeration

> - **Phase:** Discovery in the Active Directory domain - mapping before the attack
> - **Prerequisites:** connectivity to a Domain Controller; for authenticated enumeration a valid domain account (even low privilege); some techniques work even with a null session
> - **Nature:** methodology (illustrative outputs; Finding ID `AD-NNN` to assign in lab)

## Introduction

In Active Directory, enumeration is not a negligible preliminary step: it is the phase that determines the
success of everything else. Attack paths (who can do what to whom) emerge from the domain data, not from
blind attempts. Mapping users, groups, ACLs, sessions, delegation and AD CS configuration before acting
lets you choose the lowest-cost, lowest-noise vector. The foundations are in
[THEORETICAL-FOUNDATIONS](<../THEORETICAL-FOUNDATIONS.en.md>).

## Folder structure

| subfolder | technique | typical severity | status |
| :--- | :--- | :---: | :--- |
| `bloodhound/` | collection and analysis of the domain graph (bloodhound/sharphound) | `Informational` | written |
| `domain-enumeration/` | ldap/rpc/smb enumeration (ldapsearch, rpcclient, nxc, enum4linux-ng) | `Low` | written |
| `kerbrute-userenum/` | user enumeration and password spraying via kerberos | `Variable (Low / High)` | written |

## Recommended operational flow

1. If you have no credentials: user enumeration via Kerberos (`kerbrute-userenum/`) to build a list of valid
   usernames, then targeted password spraying.
2. With a domain account: BloodHound collection (`bloodhound/`) for the full map of attack paths, in parallel
   with LDAP/RPC enumeration (`domain-enumeration/`) for the details.
3. The enumeration output guides the choice of offensive technique in subfolders 02-05.

---

> **Note:** Educational content. Execution only in owned labs or with explicit authorization.
