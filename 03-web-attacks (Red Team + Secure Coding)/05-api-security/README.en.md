> **English** | [Italiano](README.md)

# 05 - API Security

> - **Phase:** Web Attack - API Security Testing (OWASP API Top 10:2023)
> - **Visibility:** Variable - Low (JWT offline crack) / Medium (GraphQL, REST with curl) / Low (IDOR - legitimate requests)
> - **Prerequisites:** API endpoints identified, JWT token from an ordinary user available, API documentation or retrievable GraphQL schema
> - **Output:** Finding WEB-012 (JWT), WEB-013 (GraphQL RCE), WEB-014 (IDOR), admin access, user data dump

---

## Introduction

The modern web is built on APIs (Application Programming Interfaces). Where once there was server-rendered HTML, today there are JSON endpoints consumed by JavaScript clients, mobile applications, microservices, and B2B integrations. This architectural shift has also shifted the attack surface.

API vulnerabilities differ from those of traditional web applications because:

- **No visible interface:** there is no form to analyze, only HTTP endpoints with JSON/XML payloads.
- **Token-based authentication:** JWT, OAuth 2.0, and API Keys replace session cookies.
- **Implicit access control:** the application trusts the ID provided in the request without verifying that the user is authorized to read that resource (IDOR/BOLA).
- **Hidden schema:** GraphQL exposes an entire data structure through Introspection, which is often not disabled.

The OWASP API Security Top 10:2023 documents the most critical vulnerabilities in modern APIs:

| Category | Finding | Subdirectory |
| :--- | :--- | :--- |
| API2:2023 - Broken Authentication | WEB-012 (JWT weak secret) | `jwt-tokens/` |
| API8:2023 - Security Misconfiguration | WEB-013 (GraphQL Introspection) | `graphql/` |
| API3:2023 - Broken Object Property Level Authorization | WEB-013 (Command Injection via GraphQL) | `graphql/` |
| API1:2023 - Broken Object Level Authorization (BOLA) | WEB-014 (IDOR) | `postman/` |

---

## Directory Structure

```
05-api-security/
+-- jwt-tokens/   # JWT weak secret, brute force offline, token forging - WEB-012
+-- graphql/      # GraphQL Introspection + Command Injection RCE - WEB-013
+-- postman/      # IDOR/BOLA on banking API - WEB-014
```

---

## `jwt-tokens/` - JWT Authentication Exploitation

**Finding ID:** `WEB-012` | **Severity:** `Critical` | **CVSS v3.1:** 9.8

### Operational Context

JSON Web Tokens (JWT) are the most widespread authentication mechanism in modern APIs. A JWT contains three Base64-encoded parts: header (algorithm), payload (claims: user, role, expiration), signature (HMAC hash or RSA signature).

The vulnerability documented in `jwt-tokens/README.md` involves the use of a weak secret key (`secret123`) to sign tokens with the HS256 algorithm (symmetric). An attacker who obtains a valid token can perform an offline brute force attack (without generating traffic toward the server) to recover the key and then forge arbitrary tokens with any role, including `admin`.

The danger is amplified by the offline nature of the brute force: no IDS, no rate limiting, and no lockout mechanisms can block this attack.

---

## `graphql/` - GraphQL Introspection & Command Injection

**Finding ID:** `WEB-013` | **Severity:** `Critical` | **CVSS v3.1:** 9.8

### Operational Context

GraphQL is an API query language developed by Facebook. Its distinctive feature is the single endpoint (`/graphql`) that serves all requests, and the **Introspection** functionality: a special query (`__schema`) that returns the entire database structure, available queries, data types, and fields.

In production, Introspection should be disabled because it provides the attacker with a complete map of the API (including undocumented functionality). The document `graphql/README.md` details the complete kill chain:
1. Introspection via curl (bypassing the block on the graphical interface).
2. Discovery of undocumented queries: `systemDebug`, `systemDiagnostics`.
3. Command Injection on the `systemDebug(arg: String)` query.
4. Remote Code Execution confirmed with `; id`.
5. Exfiltration of the `config.py` file containing admin credentials in cleartext.

---

## `postman/` - IDOR/BOLA Testing

**Finding ID:** `WEB-014` | **Severity:** `Critical` | **CVSS v3.1:** 9.1

### Operational Context

IDOR (Insecure Direct Object Reference), classified as BOLA (Broken Object Level Authorization) in the OWASP API Top 10:2023, is the most common and critical vulnerability in APIs. The application accepts a resource ID in the URL (e.g., `/api/balance/1001`) and returns the corresponding data **without verifying whether the authenticated user is the owner of that resource**.

The document `postman/README.md` details:
- Identification of the vulnerable endpoint `/api/balance/<account_id>`.
- Manual test: changing the ID from 1000 to 1001 returns another user's data (instead of `403 Forbidden`).
- Automation with Python script: enumeration of all IDs from 998 to 1005 and dump of financial data.
- Exfiltrated data: Bob's balance (150,000 EUR), Charlie/CEO (9,999,999 EUR), Dave/Admin (2,500 EUR).

---

## Recommended Operational Flow

```
[1] Identify the authentication mechanism
     +-- Cookie: JWT? OAuth? Session?
     +-- Header: Authorization: Bearer <TOKEN>?
     +-- Intercept with Burp Suite to analyze the format
              |
              v
[2] JWT? -> jwt-tokens/
     +-- decode the token (jwt.io or jwt_tool)
     +-- verify algorithm: HS256 (symmetric) or RS256 (asymmetric)?
     +-- if HS256 -> offline brute force: hashcat -m 16500 <TOKEN> rockyou.txt
     +-- if key found -> forge token with admin role
              |
              v
[3] GraphQL? -> graphql/
     +-- curl -X POST /graphql -d '{"query":"{ __schema { types { name } } }"}'
     +-- if Introspection enabled -> map all queries
     +-- look for queries with String parameters -> test Command Injection
              |
              v
[4] REST API with ID parameters? -> postman/
     +-- change the ID in the request -> does the data change without a 403 error?
     +-- IDOR confirmed -> enumerate ID range
     +-- document exfiltrated data
```

---

## Finding Registry - API Security

| ID | Description | Severity | CVSS | Subdirectory |
| :--- | :--- | :---: | :---: | :--- |
| `WEB-012` | JWT weak secret (`secret123`) - admin token forging via offline brute force | `Critical` | 9.8 | `jwt-tokens/` |
| `WEB-013` | GraphQL Introspection enabled + Command Injection RCE via `systemDebug` | `Critical` | 9.8 | `graphql/` |
| `WEB-014` | IDOR/BOLA - access to financial data of all users without authorization | `Critical` | 9.1 | `postman/` |

---

## Reference Tools

| Tool | Type | Technique/Access | Primary Use Case |
| :--- | :--- | :--- | :--- |
| `jwt_tool` | JWT analyzer | CLI - Offline | JWT analysis, brute force, and forging |
| `hashcat` | Password cracker | CLI - Offline | JWT hash brute force with GPU acceleration |
| `Burp Suite` | Web proxy | GUI - Manual | Interception and modification of API requests with JWT |
| `curl` | HTTP client | CLI | Manual testing of GraphQL and REST endpoints |
| `Postman` | API client | GUI | Interactive REST API testing, Collections, scripting |
| `graphql-voyager` | GraphQL visualizer | Web UI | Graphical visualization of the GraphQL schema |
| `clairvoyance` | GraphQL enum | CLI - Active | GraphQL schema enumeration even without Introspection |
| `nuclei` | Template-based | CLI - Active | OWASP API Top 10 and JWT vulnerability templates |

> **Recommended modern tool:** `jwt_tool` (ticarpi/jwt_tool) - dedicated JWT tool with support for brute force, payload modification, vulnerability testing (alg:none, RS256 to HS256). Installation: `pip3 install jwt_tool`.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Credential Access | Brute Force: Password Cracking | `T1110.002` | Offline brute force of the JWT HS256 signature using a dictionary to recover the key `secret123` (WEB-012) |
| Defense Evasion | Use Alternate Authentication Material | `T1550` | Use of the forged JWT token with admin role to access privileged functionality (WEB-012) |
| Lateral Movement | Valid Accounts: Cloud Accounts | `T1078.003` | Impersonation of the admin account through a forged JWT token (WEB-012) |
| Reconnaissance | Active Scanning: Wordlist Scanning | `T1595.003` | GraphQL Introspection to map all available queries, including undocumented ones (WEB-013) |
| Execution | Command and Scripting Interpreter: Unix Shell | `T1059.004` | Command Injection through the `arg` parameter of the `systemDebug` query -> RCE with `; id` (WEB-013) |
| Collection | Data from Information Repositories | `T1213` | Exfiltration of admin credentials from `config.py` and SQLite database dump through RCE (WEB-013) |
| Discovery | Account Discovery | `T1087` | Enumeration of account IDs on the `/api/balance/<id>` endpoint to map all users (WEB-014) |
| Collection | Data from Information Repositories | `T1213` | Access to financial data of unauthorized users through IDOR/BOLA (WEB-014) |
| Lateral Movement | Valid Accounts | `T1078` | Use of a legitimate account to perform IDOR requests against other users' accounts (WEB-014) |

---

> **Note:** The documented API vulnerabilities were identified and exploited in lab environments:
> DVGA (Damn Vulnerable GraphQL Application) in a local Docker container for WEB-013,
> a custom Flask/Python application for WEB-012 and WEB-014. All activities were
> conducted within an authorized perimeter. Exploiting these vulnerabilities on production APIs
> without authorization violates terms of service and constitutes a computer crime.
