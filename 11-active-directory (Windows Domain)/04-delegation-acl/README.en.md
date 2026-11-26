> **English** | [Italiano](README.md)

# 11.4 - Kerberos delegation and ACL abuse

> - **Phase:** Privilege Escalation / Lateral Movement in the domain
> - **Prerequisites:** variable per technique; generally control (write access) over an AD object or a specific attribute, identified with BloodHound
> - **Nature:** methodology (illustrative outputs; Finding ID `AD-NNN` to assign in lab)

## Introduction

Kerberos delegation and ACLs are the two families of misconfiguration that BloodHound most often highlights
as paths to the domain. Delegation (unconstrained, constrained, resource-based) lets an account act on
behalf of others; if misconfigured, it allows impersonation of privileged users. Misconfigured ACLs
(GenericAll, WriteDACL, WriteOwner, AddKeyCredentialLink) grant rights over AD objects that translate into
password resets, addition to privileged groups, or granting oneself replication rights. None of these is a
code vulnerability: they are abuses of legitimate features.

The foundations (delegation and the authorization model) are in
[THEORETICAL-FOUNDATIONS](<../THEORETICAL-FOUNDATIONS.en.md>).

## Folder structure

| subfolder | technique | typical severity | status |
| :--- | :--- | :---: | :--- |
| `rbcd/` | resource-based constrained delegation abuse | `Critical` | written |
| `delegation-unconstrained-constrained/` | unconstrained and constrained delegation abuse | `Critical` | written |
| `acl-abuse/` | acl/dacl abuse (genericall, writedacl, writeowner, ...) | `High` (up to `Critical`) | written |
| `bloodyad/` | execution of acl/delegation-abuse primitives via ldap writes (bloodyad) | `High` (up to `Critical`) | written |

## Recommended operational flow

1. From BloodHound, identify which delegation or ACL links the current account to a more privileged target.
2. Exploit the relationship: writing the delegation attribute ([RBCD](<rbcd/README.en.md>)), abusing an
   existing delegation ([unconstrained/constrained](<delegation-unconstrained-constrained/README.en.md>)), or
   abusing the ACL right ([acl-abuse](<acl-abuse/README.en.md>)).
3. The outcome is typically the impersonation of a privileged account or granting oneself rights (e.g.,
   DCSync), leading to subfolder 05. The primitives are conveniently executed from Linux over LDAP with
   [bloodyAD](<bloodyad/README.en.md>) (password reset, add member, RBCD, shadow credentials, DCSync rights).

---

> **Note:** Educational content. Execution only in owned labs or with explicit authorization.
