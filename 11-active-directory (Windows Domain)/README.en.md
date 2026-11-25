> **English** | [Italiano](README.md)

# 11 - Active Directory (Windows Domain)

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

| Subfolder | Theme | Status |
| :--- | :--- | :--- |
| `01-enumeration/` | Domain enumeration: BloodHound, LDAP/RPC/SMB, kerbrute (user enum + spraying) | Complete (IT) |
| `02-kerberos-attacks/` | Kerberos attacks: Kerberoasting, AS-REP Roasting, Golden/Silver Ticket and the stealth variants Diamond/Sapphire | Complete |
| `03-adcs/` | AD CS abuse: ESC enumeration, ESC1 (SAN template), ESC8 (NTLM relay) | Complete |
| `04-delegation-acl/` | Kerberos delegation abuse (RBCD, unconstrained/constrained) and ACL/DACL abuse | Complete |
| `05-credential-dumping/` | Domain credential dumping: DCSync, Shadow Credentials, NTDS.dit | Complete |
| `06-domain-privesc-cve/` | Domain escalation via CVE: noPac (CVE-2021-42278/42287) | Complete |

The module is bilingual (IT + EN) and comprises 18 technique pages plus the scaffolds. What remains, per technique, is the assignment of the real Finding IDs (`AD-NNN`) upon execution in an AD lab (e.g., GOAD or HTB machines).

## Recommended operational flow

1. **Enumeration first** (`01-enumeration/`): with a domain account, map the forest with BloodHound. Attack paths emerge from the data, not from blind attempts.
2. **Low-cost credential harvesting** (`02-kerberos-attacks/`): Kerberoasting and AS-REP Roasting require no elevated privileges and often return weak service-account hashes.
3. **Escalation via misconfiguration** (`03-adcs/`, `04-delegation-acl/`): AD CS and misconfigured delegation/ACLs are today the most common vectors toward domain privileges, often more than CVEs.
4. **Full domain** (`05-credential-dumping/`): with replication rights, DCSync extracts all hashes, including `krbtgt`.
5. **Persistence**: the Golden Ticket (from krbtgt) is the domain persistence technique par excellence, covered at the boundary with module 07.

## Finding Registry

> Methodology module: no Finding ID has been assigned yet. They will be attributed (sequence `AD-001`+) upon execution in a real lab. The "Typical severity" column indicates the expected severity of the technique in a real context.

| Technique | Subfolder | Typical severity | Finding ID |
| :--- | :--- | :---: | :---: |
| BloodHound (path mapping) | `01-enumeration/bloodhound/` | `Informational` | to assign in lab |
| LDAP/RPC/SMB enumeration | `01-enumeration/domain-enumeration/` | `Low` | to assign in lab |
| Kerbrute (user enum + spraying) | `01-enumeration/kerbrute-userenum/` | `Variable (Low / High)` | to assign in lab |
| Kerberoasting | `02-kerberos-attacks/kerberoasting/` | `High` | to assign in lab |
| AS-REP Roasting | `02-kerberos-attacks/as-rep-roasting/` | `High` | to assign in lab |
| Golden Ticket | `02-kerberos-attacks/golden-ticket/` | `Critical` | to assign in lab |
| Silver Ticket | `02-kerberos-attacks/silver-ticket/` | `High` | to assign in lab |
| Diamond Ticket (stealth variant) | `02-kerberos-attacks/diamond-ticket/` | `Critical` | to assign in lab |
| Sapphire Ticket (authentic S4U2self PAC) | `02-kerberos-attacks/sapphire-ticket/` | `Critical` | to assign in lab |
| AD CS enumeration (ESC) | `03-adcs/esc-enumeration/` | `Informational` | to assign in lab |
| AD CS ESC1 (arbitrary SAN template) | `03-adcs/esc1-template-abuse/` | `Critical` | to assign in lab |
| AD CS ESC8 (NTLM relay to Web Enrollment) | `03-adcs/esc8-relay-adcs/` | `Critical` | to assign in lab |
| RBCD abuse | `04-delegation-acl/rbcd/` | `Critical` | to assign in lab |
| Unconstrained/Constrained Delegation | `04-delegation-acl/delegation-unconstrained-constrained/` | `Critical` | to assign in lab |
| ACL/DACL abuse | `04-delegation-acl/acl-abuse/` | `High` (up to `Critical`) | to assign in lab |
| DCSync | `05-credential-dumping/dcsync/` | `Critical` | to assign in lab |
| Shadow Credentials | `05-credential-dumping/shadow-credentials/` | `High` | to assign in lab |
| NTDS.dit dump | `05-credential-dumping/secretsdump-ntds/` | `Critical` | to assign in lab |
| noPac (CVE-2021-42278/42287) | `06-domain-privesc-cve/nopac/` | `Critical` | to assign in lab |

## MITRE ATT&CK mapping (aggregated)

| Tactic | Technique | MITRE ID | Related technique |
| :--- | :--- | :--- | :--- |
| Discovery | Account Discovery: Domain Account | `T1087.002` | Enumeration (BloodHound, LDAP, kerbrute) |
| Discovery | Permission Groups Discovery: Domain Groups | `T1069.002` | Group enumeration |
| Discovery | Domain Trust Discovery | `T1482` | BloodHound |
| Discovery | Password Policy Discovery | `T1201` | Pre-spraying enumeration |
| Credential Access | Brute Force: Password Spraying | `T1110.003` | Kerbrute spraying |
| Credential Access | Steal or Forge Kerberos Tickets: Kerberoasting | `T1558.003` | Kerberoasting |
| Credential Access | Steal or Forge Kerberos Tickets: AS-REP Roasting | `T1558.004` | AS-REP Roasting |
| Credential Access | Steal or Forge Kerberos Tickets: Golden Ticket | `T1558.001` | Golden Ticket / Diamond Ticket / Sapphire Ticket |
| Credential Access | Steal or Forge Kerberos Tickets: Silver Ticket | `T1558.002` | Silver Ticket |
| Credential Access | Steal or Forge Authentication Certificates | `T1649` | AD CS ESC1 / ESC8 / Shadow Credentials |
| Credential Access | Adversary-in-the-Middle: LLMNR/NBT-NS Poisoning and SMB Relay | `T1557.001` | AD CS ESC8 |
| Credential Access | Forced Authentication | `T1187` | ESC8 / unconstrained delegation (coercion) |
| Credential Access | OS Credential Dumping: DCSync | `T1003.006` | DCSync / ACL abuse (WriteDACL) / noPac |
| Credential Access | OS Credential Dumping: NTDS | `T1003.003` | NTDS.dit dump |
| Persistence | Account Manipulation | `T1098` | RBCD / ACL abuse / Shadow Credentials / Diamond / Sapphire |
| Persistence | Create Account: Domain Account | `T1136.002` | noPac (computer account creation) |
| Privilege Escalation | Exploitation for Privilege Escalation | `T1068` | noPac (CVE-2021-42278 + 42287) |
| Privilege Escalation | Domain or Tenant Policy Modification | `T1484` | ACL abuse (domain DACL) |
| Lateral Movement | Use Alternate Authentication Material: Pass the Ticket | `T1550.003` | Delegation abuse / forged tickets |
| Lateral Movement | Use Alternate Authentication Material: Pass the Hash | `T1550.002` | DCSync / NTDS (follow-on) |

## Reference tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `BloodHound` / `SharpHound` | Graph enumeration | CLI/GUI - Active | Map of domain attack paths (ACLs, sessions, delegation) |
| `NetExec` (`nxc`) | Swiss-army AD/SMB | CLI - Active | Mass enumeration and action over SMB/LDAP/WinRM; successor to CrackMapExec |
| `Impacket` (suite) | Python toolkit | CLI - Active | GetUserSPNs, secretsdump, ntlmrelayx, ticketer and others |
| `Rubeus` | .NET Kerberos tool | CLI - Active | Kerberoasting, AS-REP, ticket manipulation from a Windows host |
| `Certipy` | AD CS toolkit | CLI - Active | AD CS enumeration and abuse (ESC1-ESC16) |
| `ldapsearch` / `windapsearch` | LDAP client | CLI - Active | LDAP domain enumeration |
| `kerbrute` | Kerberos pre-auth | CLI - Active | User enumeration and password spraying via Kerberos |
| `hashcat` | GPU cracking | CLI - Offline | Cracking Kerberos hashes (modes 13100/18200) and NTLM (1000) |

## Links to other modules

- Upstream: [04-system-exploitation](<../04-system-exploitation/README.en.md>) (local access and escalation) and [07-post-exploitation](<../07-post-exploitation/README.en.md>) (local credential dumping, pivoting).
- Typical initial access: password spraying and phishing from [05-social-engineering](<../05-social-engineering/README.en.md>); credentials from relay/poisoning.
- Defense: related countermeasures in [08-defense-hardenings](<../08-defense-hardenings (Blue Team Prevention)/README.en.md>) (SIEM/XDR, hardening).

---

> **Note:** Educational and methodology documentation module. The described techniques must be executed only in owned labs or on systems with explicit authorization. Outputs are illustrative and do not come from real or third-party systems.
