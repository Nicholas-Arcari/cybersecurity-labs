> **English** | [Italiano](README.md)

# 11 - Active Directory (Windows domain)

> - **Phase:** Exploitation and Post-Exploitation of the Windows domain - from first authenticated access to Domain Admin
> - **Visibility:** Variable - some techniques are noisy (Kerberoasting, NTLM relay), others nearly silent (DCSync, ACL abuse with legitimate credentials)
> - **Prerequisites:** connectivity to a Domain Controller; usually an initial set of valid domain credentials (even low privilege) obtained from previous modules (phishing, password spraying, cleartext credentials, relay)
> - **Nature of the module:** methodology. The outputs shown are illustrative and representative, not taken from a specific lab. Finding IDs (`AD-NNN`) are reserved and will be assigned once the techniques are executed in a real AD lab (e.g., GOAD - Game of Active Directory). Severities are given as "typical" for the technique.

## Introduction

Active Directory (AD) is the identity management system of nearly every Windows enterprise network. In an internal penetration test, compromise rarely goes through a single exploit: it almost always goes through the abuse of legitimate AD features (Kerberos, replication, delegation, certificate authorities). This is why AD deserves a dedicated module instead of appearing as a scattered note in post-exploitation.

The module sits downstream of initial access and any local escalation (modules 04 and 07) and upstream of domain persistence. The common thread is the typical path of a red team operator inside a domain:

```
Domain credentials (even low-priv)
        |
        v
Enumeration (BloodHound, ldapsearch) -> map of users, groups, ACLs, attack paths
        |
        v
Credential theft (Kerberoasting, AS-REP) -> crackable offline hashes of service accounts
        |
        v
Misconfiguration abuse (AD CS / ESC, RBCD delegation, ACLs) -> escalation to elevated privileges
        |
        v
Full domain (DCSync) -> dump of all hashes, including krbtgt
        |
        v
Persistence (Golden Ticket) -> durable, hard-to-eradicate access
```

The module is deliberately defense-oriented too: AD is common ground for red and blue teams, and every technique carries its detection indicators and concrete countermeasures.

## Folder structure

| subfolder | theme | status |
| :--- | :--- | :--- |
| `01-enumeration/` | domain enumeration: bloodhound, ldap/rpc/smb, kerbrute (user enum + spraying) | complete (it) |
| `02-kerberos-attacks/` | kerberos attacks: kerberoasting, as-rep roasting, golden/silver ticket and the stealth variants diamond/sapphire | complete |
| `03-adcs/` | ad cs abuse: esc enumeration, esc1 (san template), esc8 (ntlm relay) | complete |
| `04-delegation-acl/` | kerberos delegation abuse (rbcd, unconstrained/constrained) and acl/dacl abuse | complete |
| `05-credential-dumping/` | domain credential dumping: dcsync, shadow credentials, ntds.dit | complete |
| `06-domain-privesc-cve/` | domain escalation via cve: nopac (CVE-2021-42278/42287) | complete |

The module is bilingual (IT + EN) and comprises 18 technique pages plus the scaffolds. What remains, per technique, is the assignment of the real Finding IDs (`AD-NNN`) upon execution in an AD lab (e.g., GOAD or HTB machines).

## Recommended operational flow

1. **Enumeration first** (`01-enumeration/`): with a domain account, map the forest with BloodHound. Attack paths emerge from the data, not from blind attempts.
2. **Low-cost credential harvesting** (`02-kerberos-attacks/`): Kerberoasting and AS-REP Roasting require no elevated privileges and often return weak service-account hashes.
3. **Escalation via misconfiguration** (`03-adcs/`, `04-delegation-acl/`): AD CS and misconfigured delegation/ACLs are today the most common vectors toward domain privileges, often more than CVEs.
4. **Full domain** (`05-credential-dumping/`): with replication rights, DCSync extracts all hashes, including `krbtgt`.
5. **Persistence**: the Golden Ticket (from krbtgt) is the domain persistence technique par excellence, covered at the boundary with module 07.

## Finding registry

> Methodology module: no Finding ID has been assigned yet. They will be attributed (sequence `AD-001`+) upon execution in a real lab. The "Typical severity" column indicates the expected severity of the technique in a real context.

| technique | subfolder | typical severity | finding id |
| :--- | :--- | :---: | :---: |
| bloodhound (path mapping) | `01-enumeration/bloodhound/` | `Informational` | to assign in lab |
| ldap/rpc/smb enumeration | `01-enumeration/domain-enumeration/` | `Low` | to assign in lab |
| kerbrute (user enum + spraying) | `01-enumeration/kerbrute-userenum/` | `Variable (Low / High)` | to assign in lab |
| kerberoasting | `02-kerberos-attacks/kerberoasting/` | `High` | to assign in lab |
| as-rep roasting | `02-kerberos-attacks/as-rep-roasting/` | `High` | to assign in lab |
| golden ticket | `02-kerberos-attacks/golden-ticket/` | `Critical` | to assign in lab |
| silver ticket | `02-kerberos-attacks/silver-ticket/` | `High` | to assign in lab |
| diamond ticket (stealth variant) | `02-kerberos-attacks/diamond-ticket/` | `Critical` | to assign in lab |
| sapphire ticket (authentic s4u2self pac) | `02-kerberos-attacks/sapphire-ticket/` | `Critical` | to assign in lab |
| ad cs enumeration (esc) | `03-adcs/esc-enumeration/` | `Informational` | to assign in lab |
| ad cs esc1 (arbitrary san template) | `03-adcs/esc1-template-abuse/` | `Critical` | to assign in lab |
| ad cs esc8 (ntlm relay to web enrollment) | `03-adcs/esc8-relay-adcs/` | `Critical` | to assign in lab |
| rbcd abuse | `04-delegation-acl/rbcd/` | `Critical` | to assign in lab |
| unconstrained/constrained delegation | `04-delegation-acl/delegation-unconstrained-constrained/` | `Critical` | to assign in lab |
| acl/dacl abuse | `04-delegation-acl/acl-abuse/` | `High` (up to `Critical`) | to assign in lab |
| dcsync | `05-credential-dumping/dcsync/` | `Critical` | to assign in lab |
| shadow credentials | `05-credential-dumping/shadow-credentials/` | `High` | to assign in lab |
| ntds.dit dump | `05-credential-dumping/secretsdump-ntds/` | `Critical` | to assign in lab |
| nopac (CVE-2021-42278/42287) | `06-domain-privesc-cve/nopac/` | `Critical` | to assign in lab |

## MITRE ATT&CK mapping (aggregated)

| tactic | technique | mitre id | related technique |
| :--- | :--- | :--- | :--- |
| discovery | account discovery: domain account | `T1087.002` | enumeration (bloodhound, ldap, kerbrute) |
| discovery | permission groups discovery: domain groups | `T1069.002` | group enumeration |
| discovery | domain trust discovery | `T1482` | bloodhound |
| discovery | password policy discovery | `T1201` | pre-spraying enumeration |
| credential access | brute force: password spraying | `T1110.003` | kerbrute spraying |
| credential access | steal or forge kerberos tickets: kerberoasting | `T1558.003` | kerberoasting |
| credential access | steal or forge kerberos tickets: as-rep roasting | `T1558.004` | as-rep roasting |
| credential access | steal or forge kerberos tickets: golden ticket | `T1558.001` | golden ticket / diamond ticket / sapphire ticket |
| credential access | steal or forge kerberos tickets: silver ticket | `T1558.002` | silver ticket |
| credential access | steal or forge authentication certificates | `T1649` | ad cs esc1 / esc8 / shadow credentials |
| credential access | adversary-in-the-middle: llmnr/nbt-ns poisoning and smb relay | `T1557.001` | ad cs esc8 |
| credential access | forced authentication | `T1187` | esc8 / unconstrained delegation (coercion) |
| credential access | os credential dumping: dcsync | `T1003.006` | dcsync / acl abuse (writedacl) / nopac |
| credential access | os credential dumping: ntds | `T1003.003` | ntds.dit dump |
| persistence | account manipulation | `T1098` | rbcd / acl abuse / shadow credentials / diamond / sapphire |
| persistence | create account: domain account | `T1136.002` | nopac (computer account creation) |
| privilege escalation | exploitation for privilege escalation | `T1068` | nopac (CVE-2021-42278 + 42287) |
| privilege escalation | domain or tenant policy modification | `T1484` | acl abuse (domain dacl) |
| lateral movement | use alternate authentication material: pass the ticket | `T1550.003` | delegation abuse / forged tickets |
| lateral movement | use alternate authentication material: pass the hash | `T1550.002` | dcsync / ntds (follow-on) |

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `BloodHound` / `SharpHound` | graph enumeration | cli/gui - active | map of domain attack paths (acls, sessions, delegation) |
| `NetExec` (`nxc`) | swiss-army ad/smb | cli - active | mass enumeration and action over smb/ldap/winrm; successor to crackmapexec |
| `Impacket` (suite) | python toolkit | cli - active | getuserspns, secretsdump, ntlmrelayx, ticketer and others |
| `Rubeus` | .net kerberos tool | cli - active | kerberoasting, as-rep, ticket manipulation from a windows host |
| `Certipy` | ad cs toolkit | cli - active | ad cs enumeration and abuse (esc1-esc16) |
| `ldapsearch` / `windapsearch` | ldap client | cli - active | ldap domain enumeration |
| `kerbrute` | kerberos pre-auth | cli - active | user enumeration and password spraying via kerberos |
| `hashcat` | gpu cracking | cli - offline | cracking kerberos hashes (modes 13100/18200) and ntlm (1000) |

## Links to other modules

- Upstream: [04-system-exploitation](<../04-system-exploitation/README.en.md>) (local access and escalation) and [07-post-exploitation](<../07-post-exploitation/README.en.md>) (local credential dumping, pivoting).
- Typical initial access: password spraying and phishing from [05-social-engineering](<../05-social-engineering/README.en.md>); credentials from relay/poisoning.
- Defense: related countermeasures in [08-defense-hardenings](<../08-defense-hardenings (Blue Team Prevention)/README.en.md>) (SIEM/XDR, hardening).

---

> **Note:** Educational and methodology documentation module. The described techniques must be executed only in owned labs or on systems with explicit authorization. Outputs are illustrative and do not come from real or third-party systems.
