> **English** | [Italiano](README.md)

# Unconstrained and Constrained Delegation abuse

> - **Phase:** Privilege Escalation / Lateral Movement (Active Directory domain)
> - **Visibility:** Medium - Kerberos S4U requests (constrained) or capture of TGTs in memory (unconstrained); the associated coercion generates anomalous RPC traffic
> - **Prerequisites:** control of an account/host configured with delegation (unconstrained or constrained to a service); for unconstrained, typically local admin on a host with that delegation
> - **Technique:** `Kerberos delegation abuse` | **Typical severity:** `Critical` | **Finding ID:** to assign in lab (methodology)

- Nature of the document: methodology. Illustrative outputs; placeholder identifiers.
- Objective: impersonate privileged users by exploiting misconfigured Kerberos delegation, up to the compromise of a DC.

---

## Executive Summary

Kerberos provides delegation so that a service (e.g., a web server) can act on behalf of the user toward
another service (e.g., a database). Two classic forms exist, both abusable:

- **Unconstrained Delegation:** a host with this delegation receives and stores the TGT of users who
  authenticate to it. Whoever compromises that host can extract from memory the TGTs of anyone who connects
  to it, including - if a DC is induced (coerced) to connect - the TGT of the DC's machine account.
- **Constrained Delegation:** an account can request, via S4U, tickets toward specific services on behalf of
  any user. Whoever controls that account can impersonate privileged users toward those services.

Both turn control of a delegated account/host into impersonation of privileged identities.

## Operational context (why, before how)

Delegations are legitimate but dangerous configurations: BloodHound highlights hosts with unconstrained
delegation and accounts with constrained delegation as high-value targets. The operational decision for
unconstrained is to combine host compromise with the coercion of a privileged account (e.g., a DC) to
connect, so as to capture its TGT. For constrained, you exploit S4U to impersonate a privileged user toward
the allowed service, also considering "protocol transition" if configured.

## Execution / Commands

### Unconstrained: TGT capture + coercion

```bash
# Monitoring/extraction of incoming TGTs on the host with unconstrained delegation (run as admin on that host)
# A DC is then induced to connect to the host, to capture its TGT (coercion)
Coercer coerce -l <unconstrained_host> -t <DOMAIN_CONTROLLER_IP> -u utente -p 'Password123' -d corp.local
```

Illustrative output (representative):

```
[*] Captured TGT for DC01$@CORP.LOCAL   <-- TGT of the DC's machine account
```

### Constrained: impersonation via S4U

```bash
# The account with constrained delegation requests a TGS toward the allowed service impersonating an admin
getST.py -spn 'cifs/target.corp.local' -impersonate administrator \
  corp.local/'SVC$':'Password123' -dc-ip 10.10.10.10
```

## Analysis of results

In unconstrained, capturing a DC's TGT is equivalent to being able to impersonate its machine account, from
which DCSync and the full domain follow: severity `Critical`. In constrained, the impact depends on the
allowed service, but impersonating an admin toward a critical service is serious nonetheless. In both cases
the real finding must be measured in a lab (which identity you manage to impersonate, toward which service).

### Theoretical Analysis

Unconstrained delegation is a dangerous design choice because the host receives the user's complete TGT
("unlimited" delegation): it is maximal trust, and whoever compromises the host inherits that trust.
Constrained delegation limits delegation to specific services (S4U2proxy), but when combined with "protocol
transition" (S4U2self) it allows obtaining tickets for users who have never authenticated. In both cases the
violation (property P3) arises from the fact that control of the delegated account/host grants the
impersonation authority the delegation represents. Coercion (T1187) is the lever that, in unconstrained,
brings the right TGT (that of a DC) onto the compromised host. See
[THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.en.md>).

## Remediation (Blue Team)

**Detection.** Hosts with unconstrained delegation receiving connections from DCs at unexpected times/
contexts; RPC coercion traffic; anomalous S4U requests from accounts with constrained delegation.

**Hardening.** Eliminate unconstrained delegation (replace it with more limited constrained delegation or
RBCD); mark sensitive accounts as "Account is sensitive and cannot be delegated" and add them to the
Protected Users group; mitigate coercion; monitor delegation configurations (BloodHound on the blue-team
side).

---

## Real-World Scenario: Post-Exploitation Projection

> In unconstrained with coercion of a DC, the outcome is the full domain (severity Critical).

### Attacker Perspective (Red Team)

**Starting point:** local admin on a host with unconstrained delegation (or control of an account with
constrained delegation).

**Immediate next step (unconstrained):** monitor incoming TGTs and coerce a DC to connect.

**Projected Kill Chain:**

```
Host with unconstrained delegation compromised
        |
        v
Coercion of the DC to connect (MS-RPRN/MS-EFSRPC)
        |
        v
Capture of the DC machine account's TGT
        |
        v
Impersonation of the DC -> DCSync -> full domain
        |
        v
Golden Ticket / persistence
```

**Potential impact:** domain compromise starting from a single misconfigured host with unconstrained
delegation.

**Typical monetization vectors:** ransomware/exfiltration downstream of the domain.

### Defender Perspective (Blue Team)

**Detection:** DC connections toward hosts with unconstrained delegation; RPC coercion; anomalous S4U.

**Indicators of Compromise (IOC):** DC machine-account TGTs present on non-DC hosts; MS-RPRN/MS-EFSRPC traffic
toward the DCs; S4U impersonations toward sensitive services.

**Containment:** isolate the delegated host; reset the involved DC's machine account; investigate.

**Eradication and hardening:** elimination of unconstrained delegation; Protected Users and the "cannot be
delegated" flag on sensitive accounts; coercion mitigation.

**Defensive lesson:** unconstrained delegation grants a host the full trust of users who connect to it. It is
a configuration to eliminate, not just monitor.

---

## Reference tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `Rubeus` | .NET Kerberos tool | CLI - Active | TGT monitoring/capture (unconstrained) and S4U (constrained) from Windows |
| `getST.py` (Impacket) | Kerberos tool | CLI - Active | Impersonation via S4U in constrained delegation |
| `Coercer` / `PetitPotam` | Coercion | CLI - Active | Coercion of the DC to connect to the unconstrained host |
| `BloodHound` | Graph enum | GUI | Identification of hosts/accounts with delegation |

## Methodology notes

In a real lab document: which hosts/accounts have delegation, the outcome of the TGT capture (unconstrained)
or S4U impersonation (constrained), and the effectiveness of countermeasures (Protected Users, removal of
unconstrained).

## MITRE ATT&CK mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Credential Access | Steal or Forge Kerberos Tickets | `T1558` | Capture or request of tickets to impersonate privileged accounts. |
| Credential Access | Forced Authentication | `T1187` | Coercion of a DC to connect to the host with unconstrained delegation. |
| Lateral Movement | Use Alternate Authentication Material: Pass the Ticket | `T1550.003` | Use of the captured/forged tickets to authenticate. |

## Links to other modules

| Source | This technique | Effect |
| :--- | :--- | :--- |
| [BloodHound](<../../01-enumeration/bloodhound/README.en.md>) | Delegation abuse | identifies hosts/accounts with exploitable delegation |
| Delegation abuse | [DCSync](<../../05-credential-dumping/dcsync/README.en.md>) | capturing the DC's TGT leads to abused replication |
| [RBCD](<../rbcd/README.en.md>) | Delegation abuse | RBCD is the third (resource-based) form of the same family |

---

> **Note:** All described techniques are for educational and methodology-documentation purposes. Execution only in owned labs or with explicit authorization. Illustrative outputs, not from real systems.
