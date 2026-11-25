> **English** | [Italiano](README.md)

# AD CS enumeration: finding the ESC misconfigurations

> - **Phase:** Discovery (Active Directory domain, certificate services)
> - **Visibility:** Low-Medium - LDAP queries on the PKI configuration container and requests to the CA interface
> - **Prerequisites:** a valid domain account; presence of AD CS in the forest
> - **Technique:** `AD CS enumeration` | **Typical severity:** `Informational` (but reveals high-severity findings) | **Finding ID:** to assign in lab (methodology)

- Nature of the document: methodology. Illustrative outputs, not from a specific lab.
- Objective: identify the Certificate Authorities, the published templates and their settings, classifying the misconfigurations according to the ESC taxonomy before attempting any abuse.

---

## Executive Summary

Before exploiting AD CS you must know what is exposed. Enumeration collects the forest's CAs, the published
certificate templates and their key properties: who can enroll (enrollment rights), whether the requester
can specify the subject (arbitrary Subject Alternative Name, SAN), which Extended Key Usages are present (in
particular Client Authentication), and whether manager approval is required. The combination of these
properties determines which ESC scenario (ESC1-ESC16 and beyond) is applicable. Certipy automates this
collection and flags the known vulnerabilities.

## Operational context (why, before how)

AD CS enumeration is the step that turns "there is a PKI" into "here is the specific vector". Without it, you
would proceed blindly; with it, you know exactly which template is exploitable and with which technique (ESC1
if a template allows an arbitrary SAN to domain users, ESC8 if there is an HTTP Web Enrollment, and so on).
It is a low-risk, high-value step, to perform as soon as a CA is detected.

## Execution / Commands

```bash
# Certipy: full enumeration of CAs and templates, flagging ESC vulnerabilities
certipy find -u utente@corp.local -p 'Password123' -dc-ip 10.10.10.10 -stdout -vulnerable
```

Illustrative output (representative, reduced):

```
Certificate Templates
  0
    Template Name              : UserAuth
    Client Authentication      : True
    Enrollee Supplies Subject  : True          <-- arbitrary SAN: ESC1 candidate
    Enrollment Rights          : CORP\Domain Users
  [!] Vulnerabilities
        ESC1 : 'CORP\\Domain Users' can enroll and supply arbitrary SAN
```

## Analysis of results

The output classifies the templates according to the ESC scenarios. The enumeration page is `Informational` in
itself, but what it reveals can be `Critical`: an ESC1 template enrollable by Domain Users means any user can
obtain a certificate to authenticate as Domain Admin. The real finding lives in the specific technique (e.g.,
[ESC1](<../esc1-template-abuse/README.en.md>)), but enumeration is what makes it possible and must be
documented as the starting point.

### Theoretical Analysis

AD CS publishes its configuration (CA, templates) in the AD configuration context, readable by domain users.
This is consistent with the AD model (the structure is not secret), but it exposes all the information needed
to identify the misconfigurations. The ESC taxonomy (Schroeder & Christensen 2021; see
[THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.en.md>), sec. 3.4) formalizes which combinations of
properties make a template or an endpoint abusable: enumeration is the practical application of that taxonomy
to the real PKI data.

## Remediation (Blue Team)

**Detection.** LDAP queries targeted at the PKI container from unexpected accounts; execution of AD CS
enumeration tools (characteristic request pattern).

**Hardening.** Periodically run enumeration as a blue team (Certipy, PSPKIAudit) to discover and fix
vulnerable templates before an attacker; remove unused templates; restrict enrollment rights; disable
"Enrollee Supplies Subject" where unnecessary.

## Reference tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `Certipy` | AD CS toolkit | CLI - Active | Enumeration and ESC classification (`find -vulnerable`) |
| `Certify` | .NET AD CS tool | CLI - Active | AD CS enumeration from a Windows host |
| `PSPKIAudit` | PowerShell audit | CLI - Active | PKI audit on the blue-team side |

## Methodology notes

In a real lab document: the CAs present, the published templates and, for each, the relevant properties; the
resulting ESC classification guides the choice of the abuse technique.

## MITRE ATT&CK mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Discovery | Account Discovery: Domain Account | `T1087.002` | Reading of the PKI configuration and enrollment rights via LDAP. |
| Credential Access | Steal or Forge Authentication Certificates | `T1649` | Identification of abusable templates/endpoints to obtain certificates. |

## Links to other modules

| Source | This technique | Effect |
| :--- | :--- | :--- |
| Domain account | AD CS enumeration | identifies the applicable ESC vectors |
| AD CS enumeration | [ESC1](<../esc1-template-abuse/README.en.md>) / [ESC8](<../esc8-relay-adcs/README.en.md>) | indicates which abuse scenario to pursue |

---

> **Note:** Educational and methodology content. Execution only in owned labs or with explicit authorization. Illustrative outputs, not from real systems.
