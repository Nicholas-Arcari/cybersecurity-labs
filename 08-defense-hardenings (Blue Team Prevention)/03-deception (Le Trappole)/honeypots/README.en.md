> **English** | [Italiano](README.md)

# Honeypots - defensive decoys and traps

> - **Phase:** Defense & Hardening - Deception
> - **Category:** Deception - from the single decoy to the trap infrastructure
> - **Prerequisites:** For the tokens, a generator and strategic placement; for the high-interaction honeypots, a dedicated isolated VM
> - **Output:** Base for findings DEF-005 (canary token) and DEF-006 (T-Pot)

---

## What a honeypot is

A honeypot is a system, service or artifact designed to be attacked. It has no productive purpose: its only function is to attract the attacker and detect or study their activity. The principle common to all forms of honeypot is the structurally null false-positive rate: since no legitimate user has a reason to interact with a decoy, every interaction is potentially hostile.

Honeypots are classified by level of interaction, an axis that determines depth of intelligence versus risk and cost:

- **Low interaction (passive decoy):** an artifact that records a single event on activation. A canary token (`canary-tokens/`) is the pure example: it says "someone touched the decoy", with almost null risk (there is nothing to compromise) but minimal depth (only the fact of the activation).

- **High interaction (complete decoy system):** an environment the attacker can explore and interact with at length, recording the entire session. Cowrie in T-Pot (`t-pot/`) is the example: it records tried credentials, executed commands, downloaded malware. Maximum depth (the adversary's complete TTPs) but greater risk (a real system, even if a decoy, must be carefully isolated).

The choice depends on the objective. For **early warning** - knowing immediately that someone is inside - low interaction is enough: simple, safe, high-signal. For **threat intelligence** - understanding who attacks and how - high interaction is needed, with the rigorous isolation the risk requires.

---

## Folder structure

```
honeypots/
+-- README.md          # this file: honeypot concept and taxonomy
|
+-- canary-tokens/     # DEF-005: low interaction, passive tripwire, early warning
+-- t-pot/             # DEF-006: high interaction, threat intelligence, isolated VM
```

---

## Comparison by level of interaction

```
                    Canary Token              T-Pot / Honeypot
                    (low interaction)         (high interaction)
                    ----------------------    ----------------------
Risk                almost null               significant (isolate!)
Intel depth         single event              complete session (TTP)
Cost/resources      minimal                   high (RAM, maintenance)
False positives     structurally null         structurally null
Use case            early warning             threat intelligence
Placement           anywhere (internal)       DMZ/dedicated isolated
```

---

## Reference tools

| tool | interaction | role | main use case |
| :--- | :--- | :--- | :--- |
| `Canarytokens` | Low | passive token | pinpoint early warning, null false positives |
| `OpenCanary` | low/medium | decoy services | lightweight honeypot for internal deployments |
| `T-Pot` | High | platform | multi-service threat intelligence |
| `Cowrie` | High | ssh/telnet | capture of complete attack sessions |
| `Honeytokens` (ad) | Low | decoy account | detection of active directory attacks |

> **Recommended modern tool:** start with low interaction (`canarytokens.org`) for the best value/risk ratio; move to high interaction (`T-Pot`) only with adequate isolation and an explicit intelligence purpose.

---

> **Note:** Honeypots must be deployed exclusively on networks owned by the author. High-interaction honeypots capture real malware and must be rigorously isolated from production; the samples must be handled in a sandboxed environment. Techniques are documented for educational and defensive purposes in an authorized context.
