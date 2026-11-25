> **English** | [Italiano](README.md)

# Shadow Credentials: certificate-based authentication by abusing msDS-KeyCredentialLink

> - **Phase:** Credential Access / Persistence (Active Directory domain)
> - **Visibility:** Low-Medium - writing the attribute is a directory modification (Event ID 5136); subsequent use is a PKINIT
> - **Prerequisites:** write access to the `msDS-KeyCredentialLink` attribute of the target object (user or computer), typically from GenericWrite/GenericAll identified with BloodHound; presence of a PKI supporting PKINIT (AD CS or key trust)
> - **Technique:** `Shadow Credentials` | **Typical severity:** `High` | **Finding ID:** to assign in lab (methodology)

- Nature of the document: methodology. Illustrative outputs; placeholder identifiers.
- Objective: obtain the ability to authenticate as a target account without knowing its password, by adding a controlled public key to its key-credential attribute.

---

## Executive Summary

Shadow Credentials abuses the `msDS-KeyCredentialLink` attribute, used by Windows Hello for Business and by
key trust to bind a public key to an account for Kerberos authentication via PKINIT. If an attacker can write
this attribute on a target object (user or computer), they add a key pair they control; from then on they can
authenticate as the target by presenting that key, obtaining a TGT and, via UnPAC-the-hash, also the
account's NT hash. There is no need to know or reset the password: it is a more discreet alternative to the
password reset typical of ACL abuse.

## Operational context (why, before how)

Shadow Credentials is often preferred over a password reset when you have GenericWrite/GenericAll on an
object, because it is less invasive: it does not change the victim's password (which keeps working, avoiding
suspicion and disruption) and leaves the attacker an additional means of authentication. It is therefore also
a form of persistence. The operational decision is to choose the target (a privileged computer or a
high-value user identified with BloodHound) and to remember to clean up the attribute at the end of the test.

## Execution / Commands

```bash
# Adds a controlled key credential to the target object (produces a certificate/key to use)
certipy shadow auto -u utente@corp.local -p 'Password123' -dc-ip 10.10.10.10 -account 'TARGET$'
```

Illustrative output (representative):

```
[*] Adding Key Credential to 'TARGET$'
[*] Authenticating as 'TARGET$' via PKINIT
[*] Got NT hash for 'TARGET$@CORP.LOCAL': <HASH_TRUNCATED>   <-- target account's hash
[*] Restoring msDS-KeyCredentialLink                        <-- attribute cleanup
```

## Analysis of results

The result is the ability to authenticate as the target (and its NT hash), obtained without touching the
password. If the target is a privileged computer or a high-value user, the severity is `High` and the chain
continues toward the domain. The advantage over a password reset is discretion and persistence: as long as
the attribute remains written, the attacker keeps access.

### Theoretical Analysis

`msDS-KeyCredentialLink` implements "key trust": AD trusts a public key associated with the account for
PKINIT authentication. Whoever controls writing the attribute effectively controls the list of trusted keys
for that account, and can add their own. It is the violation of property P3 (confinement of authority)
applied to cryptographic trust: the right to write an attribute translates into the power to authenticate as
the object. Unlike a password reset, there is no shared secret to change: the countermeasure is to remove the
write right and monitor the attribute. See
[THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.en.md>), sec. 3.4.

## Remediation (Blue Team)

**Detection.** Event ID 5136 on modifications of `msDS-KeyCredentialLink`; appearance of key credentials on
accounts that do not use Windows Hello for Business; PKINIT followed by privileged activity from an unexpected
host.

**Hardening.** Restrict write rights on objects (BloodHound audit); specifically monitor modifications to
`msDS-KeyCredentialLink`; where WHfB is not used, consider alerting on any write to the attribute; Tiering
Model.

---

## Real-World Scenario: Post-Exploitation Projection

> Shadow Credentials as discreet escalation and persistence (severity High).

### Attacker Perspective (Red Team)

**Starting point:** GenericWrite/GenericAll on a target object (from BloodHound).

**Immediate next step:** write a controlled key credential and authenticate via PKINIT as the target.

**Projected Kill Chain:**

```
GenericWrite on an object (from BloodHound)
        |
        v
Write msDS-KeyCredentialLink -> controlled key added
        |
        v
PKINIT as the target -> TGT + NT hash (without touching the password)
        |
        v
Privileged access / DCSync (if a high-value target) -> domain
        |
        v
Persistence: the attribute remains a means of access until removed
```

**Potential impact:** discreet escalation and persistence, without the "noise" and disruption of a password
reset.

**Typical monetization vectors:** persistence and prolonged access; downstream, ransomware/exfiltration.

### Defender Perspective (Blue Team)

**Detection:** modifications to `msDS-KeyCredentialLink` (Event ID 5136); anomalous PKINIT.

**Indicators of Compromise (IOC):** key credentials on accounts without WHfB; certificate-based
authentication from an unexpected host.

**Containment:** remove the malicious key credential; investigate accesses; reset if necessary.

**Eradication and hardening:** remediate excessive write rights; continuous monitoring of the attribute;
Tiering Model.

**Defensive lesson:** the right to write a "technical" attribute like the key credential is equivalent to
being able to become that account. The defense is ACL auditing and attribute monitoring, not password
management alone.

---

## Reference tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `Certipy` | AD CS toolkit | CLI - Active | `shadow auto`: key-credential addition, PKINIT and cleanup |
| `pywhisker` | AD tool | CLI - Active | Manipulation of `msDS-KeyCredentialLink` from Linux |
| `Whisker` | .NET tool | CLI - Active | Shadow Credentials from a Windows host |
| `BloodHound` | Graph enum | GUI | Identification of the write right (AddKeyCredentialLink/GenericWrite) |

## Methodology notes

In a real lab document: the right exploited (from BloodHound), the attribute write, the PKINIT outcome
(TGT/hash) and verification of the cleanup. Emphasize the discretion compared to a password reset.

## MITRE ATT&CK mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Persistence | Account Manipulation | `T1098` | Writing a controlled key credential on the target object. |
| Credential Access | Steal or Forge Authentication Certificates | `T1649` | Use of key trust (PKINIT) to authenticate as the target. |

## Links to other modules

| Source | This technique | Effect |
| :--- | :--- | :--- |
| [ACL abuse](<../../04-delegation-acl/acl-abuse/README.en.md>) | Shadow Credentials | the write right (AddKeyCredentialLink/GenericWrite) enables the technique |
| Shadow Credentials | [DCSync](<../dcsync/README.en.md>) | if the target is privileged, it opens the way to abused replication |
| [ESC1/ESC8](<../../03-adcs/README.en.md>) | Shadow Credentials | variants of the same idea: authentication via certificate/key instead of password |

---

> **Note:** All described techniques are for educational and methodology-documentation purposes. Execution only in owned labs or with explicit authorization. Illustrative outputs, not from real systems.
