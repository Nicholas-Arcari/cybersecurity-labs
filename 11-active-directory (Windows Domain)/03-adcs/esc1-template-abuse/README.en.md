> **English** | [Italiano](README.md)

# AD CS ESC1: template with arbitrary Subject Alternative Name

> - **Phase:** Privilege Escalation (Active Directory domain, certificate services)
> - **Visibility:** Medium - the certificate request leaves a trace in the CA database (a request by a low-privilege user for a privileged subject)
> - **Prerequisites:** a domain account with enrollment rights on a vulnerable template (Client Authentication + Enrollee Supplies Subject + no manager approval)
> - **Technique:** `AD CS ESC1` | **Typical severity:** `Critical` | **Finding ID:** to assign in lab (methodology)

- Nature of the document: methodology. Illustrative outputs; placeholder identifiers.
- Objective: obtain, from a low-privilege domain account, a certificate valid to authenticate as a privileged user (e.g., Domain Admin), by exploiting a misconfigured template.

---

## Executive Summary

ESC1 is the most direct AD CS misconfiguration: a certificate template that (a) allows Client
Authentication, (b) lets the requester specify an arbitrary Subject Alternative Name (SAN), and (c) is
enrollable by low-privilege users, without manager approval. Under these conditions any user requests a
certificate indicating a privileged account (e.g., a Domain Admin) as the SAN: the CA issues it, and the
certificate authenticates via PKINIT as that account. It is a direct jump from domain user to Domain Admin,
without cracking and without relay.

## Operational context (why, before how)

ESC1 is exploited when enumeration ([esc-enumeration](<../esc-enumeration/README.en.md>)) reveals a template
with the vulnerable combination. It is preferred when applicable because it requires no network position and
no coercion (unlike ESC8): a domain account with enrollment on the template is enough. The operational
decision is which privileged identity to impersonate (typically a known Domain Admin from enumeration).

## Execution / Commands

```bash
# Requests a certificate on the vulnerable template, specifying a privileged user as the SAN
certipy req -u utente@corp.local -p 'Password123' -dc-ip 10.10.10.10 \
  -ca CORP-CA -template UserAuth -upn administrator@corp.local
```

```bash
# Uses the obtained certificate to authenticate as the privileged user (PKINIT) and derive TGT/hash
certipy auth -pfx administrator.pfx -dc-ip 10.10.10.10
```

Illustrative output (representative):

```
[*] Saved certificate and private key to 'administrator.pfx'
[*] Got TGT for 'administrator@CORP.LOCAL'
[*] Got NT hash for 'administrator@CORP.LOCAL': <HASH_TRUNCATED>   <-- Domain Admin
```

## Analysis of results

The result is the cryptographic identity of a Domain Admin obtained from a simple domain user, in a single
certificate request. The severity is `Critical`: domain compromise without cracking, without relay, without
coercion. As with ESC8, the certificate survives the reset of the impersonated account's password, offering
persistence too.

### Theoretical Analysis

ESC1 violates property P3 (confinement of authority) at the level of the CA policy: the template defines who
can obtain what, and a policy that lets low-privilege users issue certificates with an arbitrary SAN for
Client Authentication is equivalent to granting them impersonation of anyone. The issued certificate binds
the identity (SAN) chosen by the requester, and the DC, during PKINIT, trusts the SAN present in the
certificate signed by the CA (which is trusted). The trust chain is correct at every link: the flaw is in
the template policy, not in the cryptography. See
[THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.en.md>) sec. 3.4.

## Remediation (Blue Team)

**Detection.** Certificate requests where the SAN does not match the requester (a low-privilege user
requesting a certificate for a Domain Admin); issuance of certificates with Client Authentication from
at-risk templates; correlation with a subsequent PKINIT from an unexpected host.

**Hardening.** Disable "Enrollee Supplies Subject" on authentication templates; require manager approval for
issuance; restrict enrollment rights to only the necessary groups; remove Client Authentication from
templates that do not need it; periodic audit with Certipy/PSPKIAudit.

---

## Real-World Scenario: Post-Exploitation Projection

> ESC1 leads directly to domain privileges (severity Critical).

### Attacker Perspective (Red Team)

**Starting point:** low-privilege domain account with enrollment on an ESC1 template.

**Immediate next step:** request a certificate with SAN = Domain Admin and authenticate via PKINIT.

**Projected Kill Chain:**

```
Low-priv domain user (enrollment on an ESC1 template)
        |
        v
Certificate request with SAN = administrator -> certificate issued by the CA
        |
        v
PKINIT with the certificate -> TGT / NT hash of the Domain Admin
        |
        v
DCSync -> full domain
        |
        v
Golden Ticket / persistence (the certificate itself is persistent)
```

**Potential impact:** total domain compromise from a simple user, in a single certificate request. The
certificate-based persistence survives password resets.

**Typical monetization vectors:** ransomware and exfiltration downstream of the domain; access brokering.

### Defender Perspective (Blue Team)

**Detection:** certificate requests with a SAN different from the requester; anomalous issuances on at-risk
templates; PKINIT from an unexpected host followed by privileged activity.

**Indicators of Compromise (IOC):** CA database entry with a privileged SAN requested by a non-privileged
user; use of the certificate for authentication from an anomalous source.

**Containment:** revoke the anomalously issued certificate; disable the vulnerable template; reset and
investigate the impersonated account.

**Eradication and hardening:** fix the templates (no arbitrary SAN, manager approval, restricted enrollment);
periodic PKI audit.

**Defensive lesson:** a misconfigured template turns the PKI, built to strengthen authentication, into a
shortcut to the domain. The defense is template governance, not certificate cryptography.

---

## Reference tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `Certipy` | AD CS toolkit | CLI - Active | Certificate request with arbitrary SAN and PKINIT authentication |
| `Certify` | .NET AD CS tool | CLI - Active | Certificate request/abuse from a Windows host |
| `Rubeus` | .NET Kerberos tool | CLI - Active | Use of the certificate for PKINIT from Windows |
| `PSPKIAudit` | PowerShell audit | CLI - Active | Template audit on the blue-team side |

## Methodology notes

In a real lab document: the vulnerable template identified, the request with a privileged SAN, the PKINIT
outcome, and verification that the certificate stays valid after a password reset (persistence dimension).

## MITRE ATT&CK mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Credential Access | Steal or Forge Authentication Certificates | `T1649` | Issuance of a certificate with an arbitrary SAN to impersonate a privileged account. |
| Privilege Escalation | Valid Accounts: Domain Accounts | `T1078.002` | Use of the privileged identity obtained via certificate. |

## Links to other modules

| Source | This technique | Effect |
| :--- | :--- | :--- |
| [esc-enumeration](<../esc-enumeration/README.en.md>) | ESC1 | identifies the vulnerable template to exploit |
| ESC1 | [DCSync](<../../05-credential-dumping/dcsync/README.en.md>) | the obtained Domain Admin identity enables replication |
| [ESC8](<../esc8-relay-adcs/README.en.md>) | ESC1 | two AD CS scenarios: ESC1 without network/coercion, ESC8 via relay |

---

> **Note:** All described techniques are for educational and methodology-documentation purposes. Execution only in owned labs or with explicit authorization. Illustrative outputs, not from real systems.
