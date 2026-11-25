> **English** | [Italiano](README.md)

# 03 - Deception (The Traps)

> - **Phase:** Defense & Hardening - Deception & Early Warning
> - **Category:** Deception - high-confidence traps and threat intelligence
> - **Prerequisites:** An environment in which to place decoys (shares, documents, credentials); for the honeypots, a dedicated isolated VM; notification channel
> - **Output:** Findings DEF-005..006; very high-confidence tripwires; collection of real TTPs and IOCs

---

## Introduction

Deception is "the traps": a defensive philosophy that does not protect and does not block, but warns. The principle is to scatter the environment with decoys - files, credentials, services, entire systems - that have no legitimate function and whose only reason to exist is to be touched by an attacker. Since no authorized user has a reason to interact with a decoy, every activation is a very high-confidence signal.

This overturns the economics of detection. SIEM rules (`../01-siem-log-analysis/`) must distinguish the malicious from the legitimate in a sea of normal activity, with inevitable false positives. Deception does not have this problem: the normal activity on a decoy is zero, so any activity is anomalous by definition. A single deception alert is worth, in confidence, many correlated alerts.

Deception also introduces an asymmetry in the defender's favor. Normally the attacker must be right only once, the defender always. Deception inverts this: the attacker must avoid every decoy (without knowing which files are real and which are traps), the defender must guess just one that the attacker will touch. Moreover, it injects doubt - an attacker aware of the decoys must move with caution, slowing down.

The section covers two levels of deception:

1. **Canary Tokens (DEF-005):** passive digital tripwires - a document, a credential, a decoy URL that alerts on use. Maximum simplicity, pinpoint coverage, structurally null false positives.

2. **T-Pot / Honeypot (DEF-006):** an entire high-interaction decoy infrastructure, which not only detects but studies the attackers, collecting real TTPs and IOCs (threat intelligence).

They are particularly effective against post-exploitation (`07-post-exploitation`): the attacker who enumerates shares, looks for credentials and opens "interesting" documents finds exactly the decoys prepared for them.

---

## Folder Structure

```
03-deception (Le Trappole)/
+-- README.md          # this file: DEF-005..006 registry, deception philosophy
|
+-- honeypots/         # decoys and traps
    +-- README.md          # honeypot concept and taxonomy
    +-- canary-tokens/     # DEF-005: passive digital tripwires
    +-- t-pot/             # DEF-006: multi-service honeypot platform
```

---

## Recommended Operational Flow

```
[INPUT] Environment to protect / study
         |
         v
[1] Choice of the deception type
     +-- pinpoint early warning, simple -> canary-tokens/ (DEF-005)
     +-- threat intelligence, TTP study --> t-pot/ (DEF-006, isolated VM)
              |
              v
[2] Strategic placement
     +-- decoys where the attacker looks, not where the legitimate user goes
              |
              v
[3] Activation (attacker takes the bait)
     +-- immediate high-confidence alert
              |
              v
[4] Response and intelligence
     +-- token -> incident, immediate response (attacker already inside)
     +-- honeypot -> IOC/TTP -> blocklist and rules in the SIEM (01)
              |
              v
[OUTPUT] Breach detected early + intelligence to strengthen the real defenses
```

---

## Reference Tools

| Tool | Type | Role | Main use case |
| :--- | :--- | :--- | :--- |
| `Canarytokens` (Thinkst) | Token generator | Service/self-hosted | Digital tripwires (doc, URL, AWS, DNS) |
| `T-Pot` (Telekom) | Honeypot platform | Platform | Multi-service honeypot + threat intel |
| `OpenCanary` | Honeypot daemon | Open source | Lightweight self-hosted decoy services |
| `Cowrie` | SSH/Telnet honeypot | Container | Capture of SSH attack sessions |
| `Honeytokens` (AD) | Deception account | Technique | Fake accounts in Active Directory |

> **Recommended modern tool:** `canarytokens.org` to start without infrastructure; `OpenCanary` or AD honeytokens for targeted internal deployments (lateral movement detection); `T-Pot` for research and threat intelligence collection on an isolated VM.

---

## Finding Registry - Deception Section

| ID | Description | Severity | Subfolder |
| :--- | :--- | :---: | :--- |
| `DEF-005` | Canary Tokens: digital tripwires for early breach detection (null false positives) | `Medium` | `honeypots/canary-tokens/` |
| `DEF-006` | T-Pot: multi-service honeypot platform, collection of real TTPs/IOCs | `Medium` | `honeypots/t-pot/` |

---

## MITRE ATT&CK Mapping - Aggregated

> Attack techniques **detected/observed** by the decoys of the section.

| Tactic (detected) | Technique | MITRE ID | Related Finding |
| :--- | :--- | :--- | :--- |
| Collection | Data from Network Shared Drive | `T1039` | DEF-005 |
| Credential Access | Unsecured Credentials: Credentials In Files | `T1552.001` | DEF-005 |
| Credential Access | Brute Force | `T1110` | DEF-006 |
| Command and Control | Ingress Tool Transfer | `T1105` | DEF-006 |
| Discovery | File and Directory Discovery | `T1083` | DEF-005 |

---

> **Note:** Deception is a purely defensive tool. Canary tokens detect access to decoy resources controlled by the author; honeypots must be deployed exclusively on isolated networks owned by the author, never in production. Captured malware samples must be handled in a sandboxed environment. Techniques are documented for educational and defensive purposes in an authorized context.
