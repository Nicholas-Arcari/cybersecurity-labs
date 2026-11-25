> **English** | [Italiano](README.md)

# 11.6 - Domain privilege escalation via CVE

> - **Phase:** Privilege Escalation in the domain - exploitation of vulnerabilities (CVEs) in core Active Directory components
> - **Prerequisites:** vary per CVE; typically the credentials of a low-privilege domain user and an unpatched Domain Controller
> - **Nature:** methodology (illustrative outputs; Finding ID `AD-NNN` to assign in lab)

## Introduction

Unlike the previous sub-areas, which abuse **design properties** of Kerberos/AD (feature abuse), this one
collects the escalations based on actual **vulnerabilities** (CVEs) in core domain components. These are
high-impact chains and, where present, low-cost: often from any domain user to Domain Admin in a few steps. The
common trait is that the primary countermeasure is always **patching** (plus supporting hardening), not a
reconfiguration.

CVEs of this class have a life cycle: they become rare in well-managed environments but remain very dangerous on
legacy or poorly updated infrastructure. They must therefore always be verified during an assessment.

## Folder Structure

| Subfolder | Technique | CVE | Typical severity | Status |
| :--- | :--- | :--- | :---: | :--- |
| `nopac/` | noPac (sAMAccountName spoofing) - from user to DA | CVE-2021-42278 + CVE-2021-42287 | `Critical` | Written |

> Extensible sub-area: other domain CVEs candidate to this section are ZeroLogon (CVE-2020-1472), PrintNightmare
> (CVE-2021-34527) and dMSA/BadSuccessor (abuse of delegated Managed Service Accounts). They should be added when
> documented in a lab, with the same standard.

## Recommended Operational Flow

1. With valid domain user credentials, check the patch status of the Domain Controllers and the specific
   prerequisites (e.g., `MachineAccountQuota` for noPac).
2. In scan/verify mode before the exploit, so as not to needlessly touch the DC.
3. If the CVE is exploitable, the chain often leads to DC impersonation and
   [DCSync](<../05-credential-dumping/dcsync/README.en.md>): from there the domain is compromised.
4. Document evidence and patch status; the remediation is patching plus supporting hardening.

---

> **Note:** Educational content. Execution only in owned labs or with explicit authorization.
