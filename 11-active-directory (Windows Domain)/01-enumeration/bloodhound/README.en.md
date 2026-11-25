> **English** | [Italiano](README.md)

# BloodHound: mapping domain attack paths

> - **Phase:** Discovery (Active Directory domain)
> - **Visibility:** Medium - collection generates many LDAP queries and, with session collection, SMB connections to many hosts; a pattern detectable as mass enumeration
> - **Prerequisites:** a valid domain account (even low privilege); connectivity to the DC (LDAP 389/636) and, for session collection, to member hosts (SMB 445)
> - **Technique:** `BloodHound / SharpHound` | **Typical severity:** `Informational` | **Finding ID:** to assign in lab (methodology)

- Nature of the document: methodology. Illustrative outputs, not from a specific lab.
- Objective: collect the domain structure and compute the shortest paths to high-value targets (Domain Admins), turning a set of AD objects into a navigable graph of exploitable relationships.

---

## Executive summary

BloodHound changed the way Active Directory is attacked, shifting enumeration from static lists to a graph
of relationships. A collector (SharpHound on Windows, bloodhound-python on Linux) gathers from LDAP and from
active sessions the domain objects (users, groups, computers, GPOs, ACLs, delegation, trusts) and imports
them into a graph database. BloodHound then computes the shortest paths between a starting point (the
compromised account) and a target (e.g., Domain Admins), highlighting abuse chains that would be invisible
to the naked eye (e.g., "user A can reset B's password, who is in a group with GenericAll over C, who is
Domain Admin").

For the attacker it is the starting point after initial access: instead of trying techniques at random, one
follows the paths the graph indicates. For the defender it is just as valuable: the same paths reveal where
permission inheritance and delegation have created unintended shortcuts to the domain.

## Operational context (why, before how)

After obtaining a first domain account, the question is not "which exploit do I use" but "where can I get to
from here". BloodHound answers with a graph. Collection must be calibrated for OPSEC: base collection (LDAP)
is relatively discreet; user-session collection (who is logged in where) requires querying many hosts over
SMB and is noisier. A careful operator chooses the collection methods based on the acceptable noise level.

## Execution / commands

### Collection from Linux (bloodhound-python)

```bash
# Remote collection with domain credentials; -c All includes sessions and ACLs
bloodhound-python -u utente -p 'Password123' -d corp.local -ns 10.10.10.10 -c All
```

### Collection from Windows (SharpHound)

```
# Native collector; produces a ZIP archive to import into BloodHound
SharpHound.exe -c All
```

Illustrative output (representative):

```
INFO: Found 312 users, 74 groups, 41 computers
INFO: Compressing data to 20260101_bloodhound.zip   <-- archive to import into the GUI
```

### Analysis in the graph

In the BloodHound GUI you import the ZIPs and use the prebuilt queries, for example "Shortest Path to Domain
Admins" or "Find Principals with DCSync Rights". The highlighted paths become the escalation plan.

## Analysis of results

The value is not the list of objects but the relationships: a path linking the current account to Domain
Admins through three chained abuses is a ready attack plan. In a real lab the finding would be classified
based on what the graph reveals: the mere map is `Informational`, but the existence of a short, direct path to
Domain Admins from a low-privilege user is effectively a higher-severity finding, to be documented in the
specific technique the path exploits.

### Theoretical analysis

BloodHound models the domain as a directed graph whose nodes are principals and whose edges are control
relationships (MemberOf, GenericAll, WriteDacl, AddKeyCredentialLink, AllowedToDelegate, HasSession, ...).
The problem "can I become Domain Admin from here" reduces to a reachability problem in the graph. This
reduction is what makes abuse chains visible: no single relationship is a vulnerability per se, but their
composition is. It is the practical application of the principle that AD security is a property of the whole
authorization graph, not of individual objects.

## Remediation (blue team)

**Detection (SOC/SIEM).**
- Anomalous volume of LDAP queries from a single account in a short time.
- Session enumeration: SMB connections to a large number of hosts from a single host in rapid sequence.
- Honeypot: decoy accounts/objects whose enumeration access generates an alert.

**Hardening.**
- Periodically run BloodHound as a blue team to find and remove attack paths (unnecessary delegation and
  ACLs) before an attacker does.
- Apply the Tiering Model and least privilege to shorten or eliminate paths toward Tier 0.
- Limit enumeration: reduce the information readable by low-privilege users where possible.

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `bloodhound-python` | python collector | cli - active | remote graph collection from linux with credentials |
| `SharpHound` | .net collector | cli - active | collection from a windows host in the domain |
| `BloodHound` / `BloodHound CE` | graph analysis | gui | attack-path analysis, prebuilt queries |
| `NetExec` (`nxc`) | ad/smb toolkit | cli - active | complementary collection and enumeration |
| `AzureHound` | collector | cli - active | extension of the graph to entra id / azure |

## Methodology notes

In a real lab (e.g., GOAD) the finding to document would be the existence and length of the shortest path to
Domain Admins from the initial account, and which relationships (edges) compose it. These outcomes guide the
techniques of the other subfolders.

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| discovery | account discovery: domain account | `T1087.002` | enumeration of domain users and computers via ldap. |
| discovery | permission groups discovery: domain groups | `T1069.002` | enumeration of groups and memberships. |
| discovery | domain trust discovery | `T1482` | mapping of trusts and relationships between domains/forests. |
| discovery | system network connections discovery | `T1049` | collection of active user sessions on hosts. |

## Links to other modules

| source | this technique | effect |
| :--- | :--- | :--- |
| first domain access | bloodhound | provides the map of paths to choose the escalation technique |
| bloodhound | [acl abuse](<../../04-delegation-acl/acl-abuse/README.en.md>), [rbcd](<../../04-delegation-acl/rbcd/README.en.md>), [dcsync](<../../05-credential-dumping/dcsync/README.en.md>) | the identified paths indicate which abuse to chain |

---

> **Note:** Educational and methodology content. Execution only in owned labs or with explicit authorization. Illustrative outputs, not from real systems.
