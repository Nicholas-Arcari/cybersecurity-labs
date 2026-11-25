> **English** | [Italiano](README.md)

# 11.5 - Domain credential dumping

> - **Phase:** Credential Access - extraction of domain secrets
> - **Prerequisites:** variable per technique; DCSync requires replication rights (Domain Admin, Enterprise Admin or an account with explicit delegation)
> - **Nature:** methodology (illustrative outputs; Finding ID `AD-NNN` to assign in lab)

## Introduction

Dumping domain credentials is the objective that marks total compromise: obtaining the hashes of all
accounts, including `krbtgt`, opens the door to Pass-the-Hash, Silver/Golden Tickets and durable
persistence. This subfolder collects the techniques that extract these secrets without executing code on the
Domain Controller. The foundations (the MS-DRSR replication protocol) are in
[THEORETICAL-FOUNDATIONS](<../THEORETICAL-FOUNDATIONS.en.md>) (section 3.3).

## Folder structure

| subfolder | technique | typical severity | status |
| :--- | :--- | :---: | :--- |
| `dcsync/` | dcsync (abused replication to extract hashes) | `Critical` | written |
| `shadow-credentials/` | shadow credentials (msds-keycredentiallink) | `High` | written |
| `secretsdump-ntds/` | ntds.dit dump from a compromised dc or backup | `Critical` | written |

## Recommended operational flow

1. Verify the replication rights on the domain object (who can DCSync beyond the admins).
2. Perform a targeted [DCSync](<dcsync/README.en.md>) (only krbtgt and privileged accounts) to reduce noise.
3. Use the obtained hashes for Pass-the-Hash and to forge tickets (link to
   [02-kerberos-attacks](<../02-kerberos-attacks/README.en.md>)).

---

> **Note:** Educational content. Execution only in owned labs or with explicit authorization.
