> **English** | [Italiano](README.md)

# Diamond Ticket: stealth variant of the Golden Ticket

> - **Phase:** Persistence / Privilege Escalation (Active Directory domain)
> - **Visibility:** Very low - unlike the Golden, a real AS-REQ/AS-REP is logged (Event ID 4768), so the typical indicators of a from-scratch forged ticket are absent
> - **Prerequisites:** the key (AES hash, preferable to RC4) of the `krbtgt` account - the same as the Golden - and the ability to obtain a legitimate TGT (credentials or a session of any user)
> - **Technique:** `Diamond Ticket` | **Typical severity:** `Critical` | **Finding ID:** to assign in lab (methodology)

- Nature of the document: methodology. Illustrative outputs; placeholder keys/SID. No operational payload reproduced.
- Objective: obtain a real TGT, modify its PAC to add privileges (e.g., Domain Admins) and re-inject it, obtaining domain-wide power with a trace far closer to legitimate activity than the Golden Ticket.

---

## Executive Summary

The Diamond Ticket is the "stealth" evolution of the [Golden Ticket](<../golden-ticket/README.en.md>). Both
require the `krbtgt` key, but the mechanism is opposite. The Golden forges a TGT **from scratch**, offline,
never contacting the KDC: this leaves a detectable anomaly (a Kerberos logon without the corresponding AS-REQ
logged). The Diamond instead starts from a **real TGT**: the attacker requests a TGT normally (so there is a
legitimate AS-REQ/AS-REP, Event ID 4768), decrypts it with the `krbtgt` key, **modifies the PAC** (adding
membership in privileged groups), **re-encrypts and re-signs** it with the same key and re-injects it.

The result is a TGT that is born legitimate in the logs: the only inconsistency is between the PAC issued by the
KDC and the PAC presented in subsequent requests, a discrepancy much harder to detect than the absence of an
AS-REQ. It is the technique of choice in environments with Microsoft Defender for Identity (MDI), Sentinel or
behavioral correlation systems on Kerberos.

## Operational context (why, before how)

You choose the Diamond over the Golden when the environment has detections looking for the Golden's anomaly (a
Kerberos logon without AS-REQ). The prerequisite is identical (the `krbtgt` key, typically obtained via
[DCSync](<../../05-credential-dumping/dcsync/README.en.md>)), but additionally you must be able to obtain a real
TGT - a session or the credentials of any user, even unprivileged, is enough. The operational decision concerns
the consistency of the forged PAC: modern tools (Rubeus with `/ldap` and `/opsec`) build the PAC from real
attributes read via LDAP and align the ticket options to native Windows behavior, further reducing indicators.
As for all tickets, AES is preferred over RC4, which is itself a signal.

## Execution / Commands

```bash
# (Windows) Rubeus: obtains a real TGT, modifies its PAC and re-injects it
# /ldap builds the PAC with real attributes from AD; /opsec aligns the KDCOptions to native behavior
Rubeus.exe diamond /krbkey:<AES256_KRBTGT_PLACEHOLDER> /ldap /opsec \
  /ticketuser:amministratore /domain:corp.local /dc:dc01.corp.local
```

```bash
# (Linux) Impacket: conceptually equivalent approach - request a real TGT and manipulate the PAC
ticketer.py -aesKey <AES256_KRBTGT_PLACEHOLDER> -domain-sid S-1-5-21-<PLACEHOLDER> \
  -domain corp.local -request -user standard_user amministratore
```

Illustrative output (representative):

```
[*] Real AS-REQ sent to the KDC (legitimate Event ID 4768 logged)
[*] PAC modified: added Domain Admins group (RID 512)
[*] Ticket re-signed with the krbtgt key and saved in amministratore.ccache   <-- "diamond" TGT
```

## Analysis of results

The Diamond Ticket provides the same power as the Golden (a domain-wide TGT with arbitrary groups), hence
severity `Critical`: it grants access to any domain service as an administrator. The difference is not in impact
but in detectability: where the Golden would betray itself with a logon lacking an AS-REQ, the Diamond presents
an apparently normal Kerberos flow. In an assessment, finding a domain where the Diamond works undisturbed means
that the sole "4624 without 4768" detection is insufficient and that PAC validation or finer correlation is
missing.

### Theoretical Analysis

In the Kerberos flow (see [THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.en.md>), sec. 3.1-3.2) the PAC
inside the TGT is signed with the KDC key (`krbtgt`): it is this signature that guarantees its integrity.
Whoever holds the `krbtgt` key can therefore decrypt a real TGT, alter the PAC and re-sign it validly. It is the
same violation as the Golden (compromise of the Kerberos root of trust), but applied to a genuine ticket rather
than a forged one: everything that makes the ticket "normal" (the real AS-REQ, the coherent fields) is preserved
and only the authorization (the PAC) is forged. The theoretical lesson is that, once the `krbtgt` key is
compromised, no signature protects anything anymore: the only remedy is rotation (a double reset).

## Remediation (Blue Team)

**Detection.** Hard with classic rules (the AS-REQ is real). Shift detection to **PAC consistency** (service-side
PAC validation and correlation between issued PAC and presented PAC) and to fine indicators: use of RC4 where AES
is expected, anomalous KDCOptions (mitigated however by `/opsec`), TGTs with unusual lifetimes or flags. MDI and
SIEMs with behavioral Kerberos analytics remain the most effective line.

**Hardening.** The radical countermeasure is the same as the Golden: a **double reset of the `krbtgt` password**
(twice, to invalidate current and previous keys). Upstream: protect `krbtgt` by avoiding DC compromise and
DCSync; Tiering Model; monitoring of replication access.

---

## Real-World Scenario: Post-Exploitation Projection

> Applies to stealth domain-wide control (severity Critical).

### Attacker Perspective (Red Team)

**Starting point:** possession of the `krbtgt` key (from DCSync) and of a user session/credentials.

**Immediate next step:** obtain a real TGT, modify its PAC and re-inject it to operate as Domain Admin without
the Golden's anomaly.

**Projected Kill Chain:**

```
krbtgt key (from DCSync) + standard user credentials
        |
        v
Diamond Ticket: real TGT with modified PAC (Domain Admins)
        |
        v
Domain-wide access as administrator, with an apparently legitimate Kerberos flow
        |
        v
Long-term persistence hard to distinguish from normal activity
```

**Potential impact:** full domain control with a trace that evades detections based on the absence of AS-REQ.
The persistence survives until `krbtgt` is rotated twice.

**Typical monetization vectors:** prolonged persistence in monitored environments; access to critical data and
systems without alerting MDI.

### Defender Perspective (Blue Team)

**Detection:** behavioral Kerberos analytics (MDI); PAC validation; correlation between the PAC issued by the KDC
and the PAC presented; unexpected use of RC4.

**Indicators of Compromise (IOC):** a TGT whose PAC is inconsistent with the one issued at the AS-REQ; tickets
with anomalous encryption or flags; privileged activity from normally unprivileged accounts.

**Containment:** double reset of `krbtgt`; investigation of recent privileged accesses; review of DCSync events.

**Eradication and hardening:** rotate `krbtgt` (x2); protect the DC against credential dumping; Tiering Model;
enable PAC validation where possible.

**Defensive lesson:** the Diamond shows that hardening the Golden's detection (looking for the absence of AS-REQ)
is not enough: without protecting the `krbtgt` key and without PAC controls, an adversary can make the compromise
indistinguishable from legitimate activity.

---

## Reference tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `Rubeus` | .NET Kerberos tool | CLI - Active | `diamond` command with `/ldap` and `/opsec` from Windows |
| `ticketer.py` (Impacket) | Kerberos tool | CLI - Active | Manipulation of a real TGT's PAC from Linux |
| `Mimikatz` | Credential/ticket tool | CLI - Active | Extraction of the `krbtgt` key and ticket manipulation |

## Methodology notes

In a real lab (e.g., GOAD or an HTB machine with a DC) document: the real TGT request (AS-REQ logged), the PAC
modification, the use of the ticket and the comparison of traces with respect to a Golden Ticket. Document the
double `krbtgt` reset and PAC validation as countermeasures. Real keys and SIDs must be treated as sensitive data
and redacted in the report.

## MITRE ATT&CK mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Credential Access | Steal or Forge Kerberos Tickets: Golden Ticket | `T1558.001` | Manipulation of a real TGT with the krbtgt key (stealth variant of the Golden). |
| Lateral Movement | Use Alternate Authentication Material: Pass the Ticket | `T1550.003` | Use of the modified TGT to access domain services. |
| Persistence | Account Manipulation | `T1098` | Domain-wide persistence via a ticket with an altered PAC. |

## Links to other modules

| Source | This technique | Effect |
| :--- | :--- | :--- |
| [DCSync](<../../05-credential-dumping/dcsync/README.en.md>) | Diamond Ticket | provides the krbtgt key, the prerequisite common to Golden and Diamond |
| [Golden Ticket](<../golden-ticket/README.en.md>) | Diamond Ticket | same root of trust, but the Diamond starts from a real TGT (stealthier) |
| Diamond Ticket | [Sapphire Ticket](<../sapphire-ticket/README.en.md>) | further evolution: authentic PAC via S4U2self rather than modified |

---

> **Note:** All described techniques are for educational and methodology-documentation purposes. Execution only in owned labs or with explicit authorization. Illustrative outputs, not from real systems.
