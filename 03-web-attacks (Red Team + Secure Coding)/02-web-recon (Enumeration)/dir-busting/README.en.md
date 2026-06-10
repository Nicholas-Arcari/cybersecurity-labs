> **English** | [Italiano](README.md)

# Web Recon: Directory Busting with Gobuster

> - **Phase:** Web Attack - Web Application Enumeration
> - **Visibility:** Medium - Gobuster generates many HTTP requests in rapid sequence, detectable by WAF and IDS
> - **Prerequisites:** Web target identified, wordlist available (`common.txt`, `SecLists`), network connection to target
> - **Output:** List of hidden directories and files with HTTP code, finding WEB-003 (CVS directory and .idea exposed)

---

**Finding ID:** `WEB-003` | **Severity:** `High` | **CVSS v3.1:** 7.5

---

Objective: Identify hidden resources (directories, backup files, administration panels) not directly linked in the web application, using Brute-force techniques.

Target: `http://testphp.vulnweb.com`

Tools: `Gobuster` (v3.x), `wget`, `Feroxbuster`

---

## 1 Theoretical Introduction

Directory Busting is an Active Enumeration technique.

Unlike traditional crawlers that follow visible links, Directory Busting tries to "guess" the existence of hidden paths by sending thousands of requests based on a Wordlist.

HTTP status codes reveal the presence of resources:

- 200 OK: The resource exists.
- 301 Redirect: Often indicates an existing directory (e.g., `/admin`).
- 403 Forbidden: The resource exists but access is denied.

---

## 2 Technical Execution: Setup & Scan

Since the test environment (Kali Purple) did not have the standard preinstalled wordlists, a preliminary setup phase was required to retrieve the `common.txt` attack dictionary.

Phase A: Wordlist Retrieval

```Bash
wget https://raw.githubusercontent.com/v0re/dirb/master/wordlists/common.txt
```

Phase B: Gobuster Scan Gobuster was launched in dir mode (directory enumeration) against the target.

```Bash
gobuster dir -u http://testphp.vulnweb.com -w common.txt
```

![](./img/Screenshot_2026-02-12_17_34_21.jpg)

Result (Output):

Findings Analysis: The scan revealed several critical directories not visible from the homepage:

- `/admin` (Status 301): An administration panel. This is the priority entry point for attempting SQL Injection or credential Brute Force attacks.
- `/secured` (Status 301): A directory suggesting the presence of sensitive data or restricted areas.
- `/CVS` (Status 301): Exposure of version control directories (Legacy). This is a critical "Information Disclosure" finding that could allow source code download.
- `/cgi-bin` (Status 403): A server-side script folder, protected but existing.

---

## 3 Advanced Scanning: Feroxbuster (Recursive)

To deepen the analysis, Feroxbuster was used - a Rust-written tool that supports automatic recursion.

Unlike Gobuster, when Feroxbuster finds a directory (e.g., `/admin`), it automatically starts a new scan inside it without human intervention.

```Bash
feroxbuster -u http://testphp.vulnweb.com -w common.txt
```

Evidence (Recursion in Action):

Differences Detected: Thanks to recursion, Feroxbuster mapped not only the presence of /admin, but immediately identified the resources inside it (e.g., /admin/index.php, /admin/login.php) in a single pass, drastically reducing deep enumeration time.

---

## 4 Conclusions

The Directory Busting activity was successful, revealing a much broader attack surface than simple manual browsing. In a real Red Teaming scenario, the next step would consist of targeting specific attack tools (like Burp Suite or SQLMap) at the newly discovered `/admin` directory.

---

## 5 Modern Scenario: Docker & REST APIs (Localhost)

Directory Busting techniques are not limited to traditional web servers, but are also fundamental for testing containerized microservices (Docker) and RESTful APIs under development (e.g., on `localhost:5173`).

Necessary adaptations for Docker/API environments:

1.  API-Specific Wordlists:

    Standard wordlists (`common.txt`) are ineffective against APIs, which use structured paths (e.g., `/api/v1/user`).

    It is necessary to use dedicated lists such as `api-endpoints.txt` (from the SecLists collection) to find critical endpoints like `/health`, `/metrics`, `/swagger.json` or `/graphql`.

2.  Networking (VM vs Host):

    If Kali Linux runs on a Virtual Machine and the Docker container runs on the Host (Windows/Mac), pointing to `localhost` from the VM will not work. You need to use the host machine's IP address on the local network (e.g., `gobuster dir -u http://192.168.X.X:<PORT> ...`).

3.  Authentication (JWT Headers):

    Many APIs return `401 Unauthorized` if a valid token is not presented. Tools like Gobuster and Feroxbuster allow injecting authentication headers to test restricted areas:

```Bash
# Example of authenticated scan on local API
gobuster dir -u http://localhost:<PORT> -w api-endpoints.txt -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```

Red Teaming Value:

Scanning local containers allows discovering Debug Endpoints (e.g., Spring Boot Actuators) left active, which often expose environment variables and cloud credentials before the app goes to production.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Active Scanning: Vulnerability Scanning | `T1595.002` | Scanning with Gobuster and Feroxbuster on `common.txt` wordlist to identify hidden resources on `testphp.vulnweb.com` |
| Reconnaissance | Active Scanning: Wordlist Scanning | `T1595.003` | Directory brute force with wordlist to discover `/admin`, `/CVS`, `.idea` and other unlinked paths (WEB-003) |
| Discovery | File and Directory Discovery | `T1083` | Identification of `/CVS` directory (legacy version control) and `.idea` folder (IDE configuration) publicly exposed (WEB-003) |
| Collection | Data from Information Repositories | `T1213` | Potential access to source code through the exposed `/CVS` directory, which could allow downloading application source files (WEB-003) |

---

> **Note:** The directory busting activities documented were conducted on `testphp.vulnweb.com`, an authorized public training environment. Section 5 documents techniques for local Docker/API environments within development testing on own applications. Dir-busting on unauthorized production targets is detectable by monitoring systems and constitutes a criminal offense under applicable cybercrime legislation.
