> **English** | [Italiano](README.md)

# OSINT Passive: Google Dorking (Google Hacking)

> - **Phase:** Reconnaissance - Passive Information Gathering
> - **Visibility:** Zero - queries remain on Google servers, no direct contact with the target
> - **Prerequisites:** Google Search access, knowledge of advanced operators, Google Hacking Database (GHDB)
> - **Output:** OSINT-003 - Sensitive files, login panels and directory listings inadvertently indexed by the target

---

Objective: Use advanced search techniques (Google Dorks) to identify sensitive information, exposed files and administration panels inadvertently indexed by search engines.

Target: `nasa.gov` (Target chosen for public disclosure program/educational purposes)
Tools: Web Browser (Google Search Engine), Google Hacking Database (GHDB).

---

## 1 Theoretical Introduction

Google Dorks (or Google Hacking) consist of using advanced search operators to query Google's index in a granular way.

Unlike a normal Search Query (which searches for keywords in text), a Dork allows filtering by:

- File type (`filetype:`)
- URL structure (`inurl:`)
- Specific domain (`site:`)

This Passive OSINT technique allows identifying Sensitive Data Exposure vulnerabilities without sending any direct packet to the victim's server, making the activity invisible to the target's logs.

---

## 2 Technical Execution

**Finding ID:** `OSINT-003` | **Severity:** `Variable (Low / High)`

The actual severity depends on what is found: PDF files with generic metadata (Low), plaintext credentials or admin panels accessible without authentication (High).

#### A. Exposed Document Search (PDF/XLSX)

A search was performed to locate PDF documents indexed on the target domain, potentially containing metadata or internal information.

Dork Executed:

```Text
site:nasa.gov filetype:pdf "report"
```

#### B. Subdomain and Login Identification

A search was performed to map exposed access portals or administrative areas.

Dork Executed:

```Text
site:nasa.gov inurl:login
```

Result: Several access portals were identified (e.g., employee portals, restricted areas) publicly reachable. [INSERT SCREENSHOT OF URL LIST HERE]

#### C. Directory Listing (Index of)

The presence of servers with "Directory Listing" enabled was verified, which expose the contents of web server folders.

Dork Executed:

```Text
site:nasa.gov intitle:"index of /"
```

Note: A positive result would indicate a web server misconfiguration (Information Disclosure).

---

## 3 Analysis and Conclusions

The Google Dorking activity allowed:
- Extending the attack surface: Identifying subdomains not linked from the main home page.
- Information Gathering: Collecting documents that could reveal software in use, employee names or internal procedures.

Remediation: To mitigate this risk, organizations should:
- Use the `robots.txt` file to prevent indexing of sensitive areas.
- Regularly perform Dorking on their own domain to verify what is public.
- Remove metadata from public documents (PDF/DOCX).

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Search Open Websites/Domains: Search Engines | `T1593.002` | Use of advanced Google operators (site:, filetype:, inurl:, intitle:) to locate exposed PDF files, login panels and directory listings on nasa.gov (OSINT-003) |

---

> **Note:** The Google Dork searches documented were performed on nasa.gov exclusively for educational purposes, executing queries as an anonymous user without accessing any system. NASA's public disclosure program allows searching for publicly available information for educational purposes.
