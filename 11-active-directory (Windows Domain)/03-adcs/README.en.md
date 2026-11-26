> **English** | [Italiano](README.md)

# 11.3 - Active Directory certificate services (AD CS) abuse

> - **Phase:** Credential Access / Privilege Escalation in the domain via the certificate authority
> - **Prerequisites:** presence of AD CS in the domain; depending on the ESC scenario, a domain account (ESC1) or a network position with coercion and relay capability (ESC8)
> - **Nature:** methodology (illustrative outputs; Finding ID `AD-NNN` to assign in lab)

## Introduction

AD CS binds identity to X.509 certificates. The "Certified Pre-Owned" research (Schroeder & Christensen 2021)
catalogued a family of misconfigurations (ESC1-ESC16 and beyond) that allow obtaining certificates usable to
authenticate as other principals, often up to the Domain Controller. It is today one of the most used
escalation vectors in real domains, and it was completely absent from the repository. The foundations are in
[THEORETICAL-FOUNDATIONS](<../THEORETICAL-FOUNDATIONS.en.md>) (section 3.4).

## Folder structure

| subfolder | technique | typical severity | status |
| :--- | :--- | :---: | :--- |
| `esc8-relay-adcs/` | esc8: ntlm relay to the ad cs web enrollment | `Critical` | written |
| `esc1-template-abuse/` | esc1: template allowing an arbitrary san | `Critical` | written |
| `esc-enumeration/` | ad cs enumeration with certipy/certify | `Informational` | written |
| `certipy/` | consolidated operational reference for certipy (find/req/auth/shadow/relay) | `Critical` | written |

## Recommended operational flow

1. Enumerate AD CS (CA, templates, enrollment endpoints) with Certipy (full command reference in
   [certipy](<certipy/README.en.md>)).
2. Classify the misconfigurations found according to the ESC taxonomy.
3. Exploit the applicable scenario: ESC1 if a domain account has access to weak templates;
   [ESC8](<esc8-relay-adcs/README.en.md>) if the HTTP Web Enrollment endpoint is present and an
   authentication can be coerced for relaying.
4. The obtained certificate is used for PKINIT authentication and, in cascade, for the full domain.

---

> **Note:** Educational content. Execution only in owned labs or with explicit authorization.
