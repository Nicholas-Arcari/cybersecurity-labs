> **English** | [Italiano](README.md)

# OSINT Passive: User Enumeration & Identity Correlation

> - **Phase:** Reconnaissance - Passive Information Gathering
> - **Visibility:** Zero - the tool sends HTTP requests to public platforms, not to the target directly
> - **Prerequisites:** Known target username, Sherlock installed (pip or apt), Python 3
> - **Output:** OSINT-004 - Map of the target's digital presence on social and technical platforms, useful for profiling and Social Engineering

---

Objective: Perform digital identity correlation (Identity Correlation) starting from a single known username to map the target's presence across different platforms.

Tools: `Sherlock`

---

## 1 Theoretical Introduction

Passive User Enumeration exploits users' tendency to reuse the same handle (username) across multiple services.
Through automated tools, it is possible to query hundreds of social platforms, forums and technical services to verify the existence of a profile.

Red Team Utility:
- Psychological Profiling: Understanding interests and hobbies for Social Engineering attacks.
- Surface Extension: Finding less protected accounts (e.g., an old forum) that could contain password leaks or personal information.

---

## 2 Technical Execution

**Finding ID:** `OSINT-004` | **Severity:** `Low`

### Search with Sherlock
The `Sherlock` tool was used to scan over 300 websites searching for the target username.

```Bash
sudo apt update
sudo apt install sherlock
sherlock <USERNAME>
```

![](./img/Screenshot_2026-02-03_17_12_56.jpg)

---

## 3 False Positive Analysis

During the analysis, it is essential to manually verify the links.

False Positives: In some cases (e.g., unknown-forum.com), the username exists but belongs to a different person (digital homonymy).

Verification: The GitHub and Reddit profiles were manually checked to confirm that the profile picture or bio matched, validating the attribution to the target.

---

## 5 Conclusions

The target's digital footprint is [High / Medium / Low]. The consistent use of the same username allows a malicious actor to easily connect professional life (GitHub) with personal or recreational life, increasing the effectiveness of potential targeted attacks.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Identity Info: Employee Names | `T1589.003` | Digital identity correlation through Sherlock to map the target username presence across 300+ platforms (OSINT-004) |
| Reconnaissance | Search Open Websites/Domains: Social Media | `T1593.001` | Target social account enumeration (GitHub, Reddit, forums) to build a profile useful for Social Engineering (OSINT-004) |

---

> **Note:** The user enumeration activities documented were performed for personal audit purposes or on targets that provided explicit authorization. The technique was executed within an educational lab. Results were not used for malicious purposes.
