> **English** | [Italiano](README.md)

# 11.2 - Kerberos protocol attacks

> - **Phase:** Credential Access in the domain - abuse of legitimate Kerberos features
> - **Prerequisites:** Kerberoasting and AS-REP Roasting need only a valid (low-privilege) domain account or, for AS-REP, even just a list of usernames; forged tickets require keys obtained downstream (krbtgt for the Golden, the service key for the Silver)
> - **Nature:** methodology (illustrative outputs; Finding ID `AD-NNN` to assign in lab)

## Introduction

Kerberos is the heart of authentication in Active Directory. The attacks collected here do not exploit
protocol vulnerabilities but design properties: any authenticated principal can request service tickets
(the basis of Kerberoasting), accounts without pre-authentication expose crackable material (AS-REP
Roasting), and whoever holds the right keys can forge arbitrary tickets (Silver and Golden Ticket, with the
stealth variants Diamond and Sapphire that reduce the indicators of compromise). The formal foundations are in
[THEORETICAL-FOUNDATIONS](<../THEORETICAL-FOUNDATIONS.en.md>) (sections 3.1-3.2).

## Folder structure

| subfolder | technique | typical severity | status |
| :--- | :--- | :---: | :--- |
| `kerberoasting/` | kerberoasting (service-account hash theft via tgs) | `High` | written |
| `as-rep-roasting/` | as-rep roasting (accounts without pre-auth) | `High` | written |
| `silver-ticket/` | silver ticket (tgs forged with the service key) | `High` | written |
| `golden-ticket/` | golden ticket (tgt forged with the krbtgt key) | `Critical` | written |
| `diamond-ticket/` | diamond ticket (real tgt with modified pac - stealth variant) | `Critical` | written |
| `sapphire-ticket/` | sapphire ticket (authentic pac via s4u2self - maximum stealth) | `Critical` | written |

## Recommended operational flow

1. With a domain account, enumerate SPNs and launch Kerberoasting: it is the lowest-cost vector.
2. In parallel, AS-REP Roasting on accounts with pre-authentication disabled.
3. Crack the obtained hashes offline (hashcat modes 13100/19700 for Kerberoast, 18200 for AS-REP).
4. Forged tickets (Silver/Golden and the stealth variants Diamond/Sapphire) belong to the
   escalation/persistence phase and presuppose keys already obtained (e.g., from
   [DCSync](<../05-credential-dumping/dcsync/README.en.md>)). Diamond and Sapphire are chosen when the
   environment has advanced detection (MDI): they start from real material (a TGT or PAC) instead of forging
   from scratch.

---

> **Note:** Educational content. Execution only in owned labs or with explicit authorization.
