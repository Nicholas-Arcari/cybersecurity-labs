> **English** | [Italiano](README.md)

# OSINT Passive: Breach Data Analysis

> - **Phase:** Reconnaissance - Passive Information Gathering
> - **Visibility:** Zero - no packets sent to the target, search on public third-party databases
> - **Prerequisites:** Target email or domain, HaveIBeenPwned account, Python 3 for h8mail
> - **Output:** OSINT-001 - Identification of compromised credentials associated with the target in public data breaches

---

Objective: Identify compromised credentials (Email/Password) exposed in public data breaches to assess the Credential Reuse risk.

Tools: h8mail, HaveIBeenPwned (HIBP).

---

## 1 Theoretical Introduction

Breach Data are collections of confidential information (credentials, PII) exfiltrated during cyber attacks and made public.

For a Red Team, analyzing this data is fundamental for Credential Stuffing: users tend to reuse the same password across multiple services. If an attacker finds an employee's password in an old LinkedIn leak, they could attempt to use it to access the corporate VPN.

Key Concepts:

- Combo List: Lists of `email:password` pairs ready for use in automated attacks.
- Hash: The password is often not readable (e.g., `5e884898da28...`), but if it's a common hash (e.g., MD5) it can be "cracked" (recovered in plaintext).

---

## 2 Research Activity (Practical Exercise)

**Finding ID:** `OSINT-001` | **Severity:** `High`

A check was performed on a sample target to identify exposure in known security incidents.

### Scan with h8mail

The `h8mail` tool queries OSINT and Breach Data services to find matches.

```Bash
python3 -m venv venv
source venv/bin/activate
pip3 install h8mail
h8mail -t <TARGET_EMAIL>
```

![](./img/Screenshot_2026-02-03_13_03_35.jpg)

```Bash
deactivate                  # run when finished
```

### Manual Scan with HaveIBeenPwned

For result validation, a manual search was performed through the official HIBP web portal, the authoritative source for data breaches.

- Portal access: `https://haveibeenpwned.com/`
- Target input: `<TARGET_EMAIL>`
- Result verification.

---

## 3 Technical Deep Dive: Digital Footprint vs Breach

1. Conceptual Difference

|Type|Description|Example|Tools|
|-------|-------------|---------|--------|
|Digital footprint|Indicates that the user exists and operates online. Does not necessarily imply a security risk, but provides information for Social Engineering|LinkedIn profile, GitHub commits, Amazon reviews|Google Dorks, Sherlock, TheHarvester|
|Breach Data|Indicates that the user's data has been STOLEN and made illegally public. Carries an immediate critical risk|Password present in a database dump (e.g., LinkedIn 2012 leak)|h8mail, HaveIBeenPwned, Intelligence X|

2. Methodological Differences

The discrepancy between results obtained via web and via command line (CLI) is due to the data access method:

- Have I Been Pwned (Website): It is the original source ("Source of Truth"). It directly queries the "Master" database maintained by the maintainers. It is always up-to-date and free for manual consultation.
- h8mail (CLI Tool): Works as a "connector" or aggregator. It does not own the data, but queries third-party services via API.
    - Limitation: To query the HIBP database via script, a paid API Key is required.
    - Fallback: Without keys, the tool attempts to use free engines (e.g., scylla.so), which may be offline or incomplete, leading to false negatives.

---

## 4 Critical Analysis: Limitations of Automated Tools

During the activity, a significant discrepancy between tool results was found:

1. Automated Tool (`h8mail`): Returned 0 results (False Negative).
    - Cause: The integrated free search engine (`scylla.so`) was offline during the test and no proprietary API Keys were configured.
2. Manual Verification (HIBP Web): Confirmed that the email is present in breach databases.

Lesson Learned:

Automated OSINT tools depend on the availability of external sources (APIs). A "Not Compromised" result from a command-line tool does not guarantee security. It is essential to perform Cross-Validation manually on authoritative sources (Source of Truth) such as the Have I Been Pwned web portal.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Identity Info: Credentials | `T1589.001` | Search for compromised target credentials on h8mail and HaveIBeenPwned to assess Credential Reuse risk (OSINT-001) |

---

> **Note:** The activities documented in this section were performed on a sample target for personal audit and training purposes. No credentials identified in breaches were used to attempt unauthorized access to third-party systems.
