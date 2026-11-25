> **English** | [Italiano](README.md)

# NTDS.dit dump: offline extraction of the domain database

> - **Phase:** Credential Access (Active Directory domain)
> - **Visibility:** Medium-High on a DC - access to system files / shadow copy creation / reading of the hives; noisier than DCSync because it operates on the DC
> - **Prerequisites:** administrative privileges on a Domain Controller (or access to a System State backup) to read `NTDS.dit` and the `SYSTEM` hive
> - **Technique:** `NTDS.dit dump` | **Typical severity:** `Critical` | **Finding ID:** to assign in lab (methodology)

- Nature of the document: methodology. Illustrative outputs; example hashes truncated.
- Objective: extract all domain hashes from the `NTDS.dit` database, when you already have administrative access to a DC or one of its backups, as an alternative/complement to DCSync.

---

## Executive Summary

`NTDS.dit` is the Active Directory database on the Domain Controller: it contains all domain objects and,
encrypted with the boot key present in the `SYSTEM` hive, the password hashes of all accounts. Whoever has
administrative privileges on a DC (or access to a System State backup) can extract `NTDS.dit` and `SYSTEM`
and derive the entire set of hashes offline. Unlike DCSync (which abuses remote replication, without touching
the DC), the NTDS.dit dump operates directly on the controller and is therefore noisier, but it is the
reference technique when you already control the DC or only have a backup available.

## Operational context (why, before how)

The NTDS.dit dump is used in two situations: when you have already obtained admin on a DC (and want the
complete, definitive dump), or when you have access to a backup (System State, Veeam, etc.) but not the live
DC. The choice between NTDS.dit dump and DCSync is one of OPSEC and context: DCSync is more discreet and
remote, the dump is more direct but touches the DC. On a live DC, methods that avoid writing to disk are
preferred (direct reading via DRSUAPI or a tool-managed shadow copy).

## Execution / Commands

### Remote dump with admin credentials (Impacket)

```bash
# secretsdump with admin credentials on the DC: extracts the hashes from the DIT (uses DRSUAPI or a shadow copy as appropriate)
secretsdump.py corp.local/Administrator:'AdminPass'@10.10.10.10
```

### From a backup / offline file

```bash
# With NTDS.dit and the SYSTEM hive already obtained (e.g., from a backup), fully offline extraction
secretsdump.py -ntds NTDS.dit -system SYSTEM LOCAL
```

Illustrative output (truncated hashes):

```
Administrator:500:aad3b435b51404eeaad3b435b51404ee:<NT_HASH_TRUNCATED>:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:<NT_HASH_TRUNCATED>:::   <-- krbtgt: key for the Golden Ticket
svc_sql:1103:aad3b435b51404eeaad3b435b51404ee:<NT_HASH_TRUNCATED>:::
```

## Analysis of results

The dump provides the entire set of domain hashes, including `krbtgt`: it is total compromise, equivalent in
outcome to a full DCSync. Severity `Critical`. The difference from DCSync is the context (it requires admin on
the DC or a backup) and the higher visibility. The obtained material enables Pass-the-Hash toward any
account, offline cracking and Golden Ticket.

### Theoretical Analysis

The hashes in `NTDS.dit` are encrypted with the PEK (Password Encryption Key), which is in turn protected by
the boot key derived from the `SYSTEM` hive. This is why both files are needed: `NTDS.dit` (the data) and
`SYSTEM` (the key to decrypt them). It is not a cryptographic bypass: with administrative privileges on the
DC, both elements are legitimately accessible, and at-rest encryption does not protect against an
administrator (or whoever has their privileges). This is why protecting the DCs and their backups is as
critical as protecting the credentials themselves. See
[THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.en.md>), sec. 3.3.

## Remediation (Blue Team)

**Detection.** Access to `NTDS.dit`/`SYSTEM` or creation of a shadow copy on a DC (VSS-related Event IDs,
access to system files); execution of dump tools; anomalous access to System State backups.

**Hardening.** Minimize the number of DC administrators (Tiering Model, Tier 0); protect and encrypt System
State backups with restricted access; monitor shadow-copy creation and access to `NTDS.dit`; in case of
suspected compromise, consider the krbtgt reset (twice) and a domain remediation procedure.

---

## Real-World Scenario: Post-Exploitation Projection

> Outcome equivalent to the full domain (severity Critical).

### Attacker Perspective (Red Team)

**Starting point:** admin on a DC, or possession of a System State backup.

**Immediate next step:** extract `NTDS.dit` + `SYSTEM` and derive the hashes offline.

**Projected Kill Chain:**

```
Admin on DC (or System State backup)
        |
        v
Extraction of NTDS.dit + SYSTEM hive
        |
        v
Offline dump of all hashes (including krbtgt)
        |
        v
Pass-the-Hash / Golden Ticket -> control and persistence of the domain
        |
        v
Exfiltration / ransomware across the whole infrastructure
```

**Potential impact:** total domain compromise. The backup case is particularly insidious: a poorly protected
backup is equivalent to handing over all the domain's credentials.

**Typical monetization vectors:** ransomware, exfiltration, access brokering.

### Defender Perspective (Blue Team)

**Detection:** access to `NTDS.dit`/shadow copy on a DC; execution of secretsdump or equivalents; access to
backups.

**Indicators of Compromise (IOC):** VSS creation on a DC in unexpected contexts; reading of `NTDS.dit` by
non-system processes; anomalous access to backup repositories.

**Containment:** isolate the DC; reset krbtgt (twice) and the privileged accounts; investigate access to the
backups.

**Eradication and hardening:** strict Tier 0; backup protection and encryption; VSS and NTDS.dit access
monitoring.

**Defensive lesson:** a DC backup is worth as much as the DC itself. Protecting System State backups is an
integral part of domain security, not a separate IT topic.

---

## Reference tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `secretsdump.py` (Impacket) | Python toolkit | CLI - Active/Offline | Remote dump with admin credentials or offline from NTDS.dit + SYSTEM files |
| `NetExec` (`nxc`) | AD/SMB toolkit | CLI - Active | `ntds` module for dumping the DIT |
| `ntdsutil` | Native utility | CLI (on the DC) | Creating a copy of the DIT (legitimate use and abuse) |
| `vssadmin` / VSS | Native utility | CLI (on the DC) | Creating a shadow copy to access NTDS.dit in use |

## Methodology notes

In a real lab document: the route used (admin on DC vs offline backup), the extraction of NTDS.dit + SYSTEM
and the resulting dump; compare noise and traces to DCSync. Treat the extracted hashes as sensitive data even
in a lab.

## MITRE ATT&CK mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Credential Access | OS Credential Dumping: NTDS | `T1003.003` | Extraction of hashes from the Domain Controller's NTDS.dit database. |
| Credential Access | Steal or Forge Kerberos Tickets: Golden Ticket | `T1558.001` | Follow-on: use of the extracted krbtgt hash for the Golden Ticket. |
| Lateral Movement | Use Alternate Authentication Material: Pass the Hash | `T1550.002` | Follow-on: authentication with the extracted hashes. |

## Links to other modules

| Source | This technique | Effect |
| :--- | :--- | :--- |
| [DCSync](<../dcsync/README.en.md>) | NTDS.dit dump | two routes to the same outcome: remote and discreet (DCSync) vs direct on the DC/backup |
| Admin on DC / backup access | NTDS.dit dump | prerequisite of privileged access or access to the System State |
| NTDS.dit dump | [Golden Ticket](<../../02-kerberos-attacks/golden-ticket/README.en.md>) / [hashcat](<../../../04-system-exploitation/05-password-cracking/hashcat/README.en.md>) | the hashes enable persistence and offline cracking |

---

> **Note:** All described techniques are for educational and methodology-documentation purposes. Execution only in owned labs or with explicit authorization. Illustrative outputs, not from real systems.
