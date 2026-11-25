> **English** | [Italiano](README.md)

# Canary tokens - digital tripwires for early breach detection

> - **Phase:** Defense & Hardening - Deception & Early Warning
> - **Category:** Deception - high-confidence alarm signals
> - **Prerequisites:** Access to a token generator (canarytokens.org or self-hosted instance); strategic placement of the tokens; notification channel (email/webhook)
> - **Output:** Finding DEF-005; tripwires distributed across the environment; immediate and high-confidence alarm when an attacker interacts with a decoy

- **Operating Environment:** Monitored environment with tokens distributed on file shares, documents, fake credentials
- **Role:** "The Traps" - they do not defend, they warn when someone is already inside
- **Main tools:** Canarytokens (Thinkst), self-hosted tokens, honeytokens

---

## Executive summary

Canary Tokens are digital tripwires: harmless decoys - a document, a credential, a URL, an AWS key - that have no legitimate function and whose only reason to exist is to be touched by an attacker. The moment someone opens the decoy document or uses the fake credential, the token "calls home" and generates an alarm. Since no legitimate user has a reason to interact with the decoy, every activation is a very high-confidence signal: almost zero false positives.

This overturns the economics of detection. SIEM rules (`../../../01-siem-log-analysis/`) must distinguish the malicious from the legitimate in a sea of normal activity, inevitably generating false positives. A canary token does not have this problem: the normal activity on the decoy is zero, so any activity is anomalous by definition. Finding DEF-005 documents this early warning capability: a token that fires means an attacker is already beyond the perimeter and is exploring.

Canary tokens are particularly effective against the post-exploitation phase (`07-post-exploitation`): the attacker who has gained access enumerates file shares, looks for saved credentials, opens "interesting" documents. A well-placed decoy (`passwords.xlsx`, `aws_keys.txt`) is exactly what they are looking for, and touching it betrays them.

---

## Folder structure

```
canary-tokens/
+-- README.md      # this file: digital tripwires for early detection (DEF-005)
+-- img/           # examples of tokens and activation alerts
```

---

## Canary token deployment

**Finding ID:** `DEF-005` | **Severity:** `Medium` (high-confidence early warning; activation indicates a compromise already in progress)

### Operational context

A canary token is generated as an artifact that, on use, produces a network request toward the token's server. There are many types: unique URLs, Office/PDF documents with an embedded beacon, DNS records, fake cloud keys, files with enticing names. The key is placement: the token must be put where an attacker would look, but a legitimate user would not.

### PoC - generation and placement of a token

```Bash
# Token generated (via canarytokens.org or self-hosted instance)
# Type: Windows Directory / decoy document / fake AWS key

# Example: decoy file with an enticing name placed on an internal share
/srv/share/finance/passwords_2026.xlsx      # <-- decoy (no legitimate use)
```

### PoC - token activation (attacker takes the bait)

```
# [Attack] the attacker in post-exploitation enumerates the share and opens the decoy
# The document contains a beacon that calls the token's server

[CANARYTOKEN ALERT] Token triggered
  Token: passwords_2026.xlsx (Excel document)
  Source IP: 10.0.5.42                       <-- host from which it was opened (DEF-005)
  Time: 2026-06-14 03:12:44
  Reminder: "Finance share decoy file"
```

### PoC - fake AWS key (honeytoken for credentials)

```
# A pair of fake AWS keys left in a config file or script.
# If the attacker finds it and tries to use it, AWS records the API call
# and the token fires - revealing that the credentials were exfiltrated and used.

[CANARYTOKEN ALERT] AWS API key used
  aws_access_key: AKIA...CANARY
  Source IP: 45.83.x.x  (attacker infrastructure)   <-- exfiltrated credential used (DEF-005)
```

### Tuning and defensive operations

- **Strategic placement:** tokens go where the attacker looks (shares "Finance"/"IT", `passwords` files, keys in scripts/config, records in Active Directory), never where a legitimate user would open them by accident
- **Credible naming:** the decoy must look real and valuable; a generic name does not attract, a targeted name (`vpn_credentials.txt`, `backup_admin.kdbx`) does
- **No internal documentation:** tokens must not be listed in accessible wikis or documentation; their effectiveness depends on only the defender knowing they are decoys
- **Immediate response:** a token that fires is an incident, not a warning to triage; the response procedure must start immediately (the attacker is already inside)

---

## Lab experience

I placed several types of tokens in the lab environment and then "wore the attacker's hat", repeating the post-exploitation enumeration of module 07. The experiment was illuminating: during the share enumeration, the file `passwords_2026.xlsx` was exactly what my attacker-self would have opened first. Opening it fired the alert within a few seconds, with the IP of the host I was operating from. The token had anticipated my offensive behavior.

The revelation was the quality of the signal. The SIEM rules I had built required continuous tuning to balance false positives and false negatives; the canary token required no tuning, because its false positive rate is structurally zero - no one accidentally opens a decoy that has no reason to exist. A single canary token alert is worth, in confidence, many correlated SIEM alerts.

The limit that emerged is coverage. A canary token detects only an attacker who touches that specific decoy; it is a trap, not a net. If the attacker does not cross the token, nothing fires. This positions it as a complement, not a substitute, to broad-coverage monitoring: the SIEM covers everything with some false positives, the token covers specific points with absolute confidence. Mature defense uses both.

---

## Theoretical analysis: the asymmetry of deception in the defender's favor

Deception overturns an asymmetry that normally favors the attacker. Usually the defender must be right always (protect every point), the attacker only once (find one hole). Deception introduces the opposite asymmetry: the attacker must avoid every decoy (they do not know which files are real and which are traps), the defender must guess just one decoy that the attacker will touch. In an environment scattered with tokens, the attacker cannot explore without risking triggering one.

This generates a valuable side effect: doubt. An attacker aware of the existence of canary tokens must move with caution, verify every file, hesitate before using every credential found. Deception not only detects, but slows down and discourages, increasing the cost and risk of the offensive operation. The value is not just the single alert, but the uncertainty it injects into the entire attack process.

The theoretical foundation is the structurally null false-positive rate. Every detection system lives on the trade-off between false positives (useless alarms that consume the analyst) and false negatives (undetected attacks). The canary token escapes this trade-off because its baseline of legitimate activity is zero by construction: it does not have to distinguish the malicious from the legitimate, because on the decoy there is no legitimate activity. It is this purity of the signal that makes deception one of the defensive tools with the best value/effort ratio.

---

## Reference tools

| tool | type | role | main use case |
| :--- | :--- | :--- | :--- |
| `Canarytokens` (thinkst) | token generator | service/self-hosted | generation of various token types (doc, url, aws, dns) |
| `Thinkst Canary` | honeypot appliance | product | physical/virtual honeypot "birds" with very low noise |
| `OpenCanary` | honeypot daemon | open source | self-hosted decoy services (ftp, ssh, http) |
| `Honeytokens` (ad) | deception account | technique | fake accounts/credentials in active directory |
| `DNS canary` | dns beacon | token | detection of exfiltration or access to decoy resources |

> **Recommended modern tool:** `canarytokens.org` (Thinkst) is the fastest way to start, free and without infrastructure. For a controlled internal deployment, self-hosted `OpenCanary` offers complete decoy services. In Active Directory environments, honeytokens (fake accounts with enticing SPNs) integrate deception with the detection of Kerberoasting and other AD attacks.

---

## MITRE ATT&CK mapping

> The table maps the attack techniques that the decoys **detect** at the moment of interaction.

| tactic (detected) | technique | mitre id | role of the control |
| :--- | :--- | :--- | :--- |
| collection | data from network shared drive | `T1039` | the decoy document on a share fires if opened (DEF-005) |
| collection | data from local system | `T1005` | local decoy files that reveal enumeration |
| credential access | unsecured credentials: credentials in files | `T1552.001` | fake credentials that fire if used (DEF-005) |
| discovery | file and directory discovery | `T1083` | interaction with the decoy reveals ongoing enumeration |

| defensive countermeasure (d3fend) | d3fend id | application |
| :--- | :--- | :--- |
| decoy file | `D3-DF` | decoy files placed to detect unauthorized access |
| decoy user credential | `D3-DUC` | fake credentials (honeytokens) that betray use |
| decoy network resource | `D3-DNR` | decoy network resources (shares, urls, dns records) |

---

> **Note:** All documented activities were conducted on a lab environment owned by the author. Canary tokens are a purely defensive tool: they detect unauthorized access to decoy resources controlled by the defender. Their use is legitimate and non-intrusive. Techniques are documented for educational and defensive purposes in an authorized context.
