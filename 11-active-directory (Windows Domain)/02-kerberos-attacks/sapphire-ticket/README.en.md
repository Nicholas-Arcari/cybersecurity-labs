> **English** | [Italiano](README.md)

# Sapphire Ticket: authentic PAC via S4U2self

> - **Phase:** Persistence / Privilege Escalation (Active Directory domain)
> - **Visibility:** Extremely low - like the Diamond there is a real Kerberos flow, but additionally the inserted PAC is authentic (issued by the KDC for a real privileged user), not modified
> - **Prerequisites:** the (AES) key of the `krbtgt` account, a domain account with which to perform the S4U2self request, and the identification of a target privileged user
> - **Technique:** `Sapphire Ticket` | **Typical severity:** `Critical` | **Finding ID:** to assign in lab (methodology)

- Nature of the document: methodology. Illustrative outputs; placeholder keys/SID. No operational payload reproduced.
- Objective: obtain a domain-wide ticket whose PAC is the authentic one of a real privileged user, obtained via S4U2self, eliminating even the PAC discrepancy that characterizes the Diamond.

---

## Executive Summary

The Sapphire Ticket is the stealthiest evolution of the Golden/Diamond family. All three require the `krbtgt`
key, but they differ in the origin of the PAC (the structure that lists the user's groups, i.e., the
privileges):

- **Golden**: PAC invented from scratch (no AS-REQ logged: a detectable anomaly).
- **[Diamond](<../diamond-ticket/README.en.md>)**: a real but **modified** PAC (there is an AS-REQ, but the
  presented PAC does not match the one issued).
- **Sapphire**: the **authentic** PAC of a real privileged user, obtained legitimately via **S4U2self** and
  inserted into the ticket.

Because the PAC comes from the KDC for a genuinely privileged account, there is neither the Golden's absence of
AS-REQ nor the Diamond's PAC discrepancy. It is the domain-wide access hardest to distinguish from legitimate
activity available once the `krbtgt` key is compromised.

## Operational context (why, before how)

You choose the Sapphire when the environment has advanced detections (MDI, PAC correlation) that might intercept
even the Diamond. The mechanism leverages **S4U2self**: a legitimate feature of the Kerberos delegation
extension that allows a service to request, on its own behalf, a ticket in the name of another user, obtaining a
valid PAC for that user. By combining S4U2self (to obtain the authentic PAC of an administrator) with the
`krbtgt` key (to assemble the final ticket), you obtain a ticket with maximum privileges and a genuine PAC. A
domain account is needed for the request, along with the identification of a high-privilege target user.

## Execution / Commands

```bash
# Impacket ticketer: sapphire technique - uses S4U2self to obtain the authentic PAC of a privileged user
# (-request with -impersonate), then assembles the ticket with the krbtgt key
ticketer.py -request -impersonate amministratore \
  -domain corp.local -user standard_user -password '<PLACEHOLDER>' \
  -aesKey <AES256_KRBTGT_PLACEHOLDER> -domain-sid S-1-5-21-<PLACEHOLDER> amministratore
```

Illustrative output (representative):

```
[*] S4U2self request for 'amministratore' -> authentic PAC received from the KDC
[*] Ticket assembled with the krbtgt key and genuine PAC
[*] Saved in amministratore.ccache   <-- "sapphire" ticket: authentic, non-modified PAC
```

## Analysis of results

The Sapphire provides domain-wide power (severity `Critical`) like Golden and Diamond, but with the cleanest
trace. The value of this technique, in an assessment, is demonstrative: if it works, it means that not even
detections based on PAC consistency (which would expose the Diamond) are sufficient, and that the defense must
necessarily shift to protecting the `krbtgt` key and rotating it. Compared to the Diamond, it eliminates the last
residual indicator (the PAC discrepancy), at the cost of a slightly more complex interaction with the KDC (the
S4U2self request).

### Theoretical Analysis

The Sapphire combines two legitimate Kerberos elements used maliciously. S4U2self (see
[THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.en.md>), sec. 3.1-3.2, and the
[delegation](<../../04-delegation-acl/delegation-unconstrained-constrained/README.en.md>) page) is meant for
protocol transition: it allows obtaining a valid PAC in a user's name. The `krbtgt` key allows signing a TGT. In
isolation they are not abuse; together they allow assembling a domain-wide ticket whose PAC is indistinguishable
from that of a real administrator login, because it is: it was issued by the KDC. It is the demonstration that,
once the root of trust (`krbtgt`) is compromised, even controls on PAC authenticity lose value. The only
countermeasure remains invalidating the key.

## Remediation (Blue Team)

**Detection.** The hardest of the family. The PAC is authentic, the AS-REQ (or S4U request) is real. You rely on:
monitoring of anomalous **S4U2self** requests (an account requesting tickets in the name of others without being
the expected delegated service); correlation between the use of a high-privilege ticket and the absence of a
corresponding interactive administrator login; MDI behavioral analytics.

**Hardening.** As for Golden and Diamond, the radical countermeasure is the **double reset of `krbtgt`**.
Upstream: protect `krbtgt` (avoid DC compromise and DCSync); limit and monitor delegation configurations;
Tiering Model.

---

## Real-World Scenario: Post-Exploitation Projection

> Applies to domain-wide control with an authentic PAC (severity Critical).

### Attacker Perspective (Red Team)

**Starting point:** the `krbtgt` key (from DCSync) and a domain account for the S4U2self request.

**Immediate next step:** obtain via S4U2self the authentic PAC of an administrator and assemble the final ticket.

**Projected Kill Chain:**

```
krbtgt key (from DCSync) + domain account
        |
        v
S4U2self -> authentic administrator PAC (issued by the KDC)
        |
        v
Sapphire Ticket: domain-wide ticket with a genuine PAC (no discrepancy)
        |
        v
Domain-wide persistence virtually indistinguishable from legitimate activity
```

**Potential impact:** domain control with the cleanest trace of the family; the persistence survives until
`krbtgt` is rotated twice.

**Typical monetization vectors:** long-term persistence in high-maturity defensive environments; undisturbed
access to critical data and systems.

### Defender Perspective (Blue Team)

**Detection:** anomalous S4U2self requests; use of privileged tickets without a corresponding interactive login;
MDI behavioral analytics.

**Indicators of Compromise (IOC):** S4U activity from accounts not meant for delegation; appearance of elevated
privileges without coherent logon events; unexpected use of RC4.

**Containment:** double reset of `krbtgt`; review of delegations; investigation of privileged accesses.

**Eradication and hardening:** rotate `krbtgt` (x2); protect the DC; audit and reduce delegation configurations;
Tiering Model.

**Defensive lesson:** the Sapphire closes the Golden/Diamond circle: no control on the ticket or the PAC
withstands the compromise of `krbtgt`. The defense is entirely upstream (protecting the key) and in rotation.

---

## Reference tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `ticketer.py` (Impacket) | Kerberos tool | CLI - Active | Sapphire technique: authentic PAC via S4U2self + assembly with krbtgt |
| `Rubeus` | .NET Kerberos tool | CLI - Active | S4U requests and ticket manipulation from Windows |
| `getST.py` (Impacket) | Kerberos tool | CLI - Active | Supporting S4U2self/S4U2proxy requests |

## Methodology notes

In a real lab document: the S4U2self request to obtain the authentic PAC, the ticket assembly, and the comparison
of traces with Golden and Diamond (absence of both the AS-REQ anomaly and the PAC discrepancy). Document the
double `krbtgt` reset as the only resolving countermeasure. Real keys and SIDs must be redacted.

## MITRE ATT&CK mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Credential Access | Steal or Forge Kerberos Tickets: Golden Ticket | `T1558.001` | Domain-wide ticket with an authentic PAC obtained via S4U2self and the krbtgt key. |
| Lateral Movement | Use Alternate Authentication Material: Pass the Ticket | `T1550.003` | Use of the ticket to access domain services as an administrator. |
| Persistence | Account Manipulation | `T1098` | Domain-wide persistence with a genuine PAC. |

## Links to other modules

| Source | This technique | Effect |
| :--- | :--- | :--- |
| [DCSync](<../../05-credential-dumping/dcsync/README.en.md>) | Sapphire Ticket | provides the krbtgt key |
| [Diamond Ticket](<../diamond-ticket/README.en.md>) | Sapphire Ticket | the Sapphire uses an authentic PAC (S4U2self) instead of modifying it: stealthier |
| [Kerberos delegation](<../../04-delegation-acl/delegation-unconstrained-constrained/README.en.md>) | Sapphire Ticket | S4U2self is the delegation primitive leveraged to obtain the PAC |

---

> **Note:** All described techniques are for educational and methodology-documentation purposes. Execution only in owned labs or with explicit authorization. Illustrative outputs, not from real systems.
