> **English** | [Italiano](README.md)

# 05 - API security

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

| category | finding | subdirectory |
| :--- | :--- | :--- |
| api2:2023 - broken authentication | WEB-012 (jwt weak secret) | `jwt-tokens/` |
| api8:2023 - security misconfiguration | WEB-013 (graphql introspection) | `graphql/` |
| api3:2023 - broken object property level authorization | WEB-013 (command injection via graphql) | `graphql/` |
| api1:2023 - broken object level authorization (bola) | WEB-014 (idor) | `postman/` |

---

## Directory structure

```
05-api-security/
+-- jwt-tokens/   # JWT weak secret, brute force offline, token forging - WEB-012
+-- graphql/      # GraphQL Introspection + Command Injection RCE - WEB-013
+-- postman/      # IDOR/BOLA on banking API - WEB-014
```

---

## `jwt-tokens/` - JWT authentication exploitation

**Finding ID:** `WEB-012` | **Severity:** `Critical` | **CVSS v3.1:** 9.8

### Operational context

JSON Web Tokens (JWT) are the most widespread authentication mechanism in modern APIs. A JWT contains three Base64-encoded parts: header (algorithm), payload (claims: user, role, expiration), signature (HMAC hash or RSA signature).

The vulnerability documented in `jwt-tokens/README.md` involves the use of a weak secret key (`secret123`) to sign tokens with the HS256 algorithm (symmetric). An attacker who obtains a valid token can perform an offline brute force attack (without generating traffic toward the server) to recover the key and then forge arbitrary tokens with any role, including `admin`.

The danger is amplified by the offline nature of the brute force: no IDS, no rate limiting, and no lockout mechanisms can block this attack.

---

## `graphql/` - GraphQL introspection & command injection

**Finding ID:** `WEB-013` | **Severity:** `Critical` | **CVSS v3.1:** 9.8

### Operational context

GraphQL is an API query language developed by Facebook. Its distinctive feature is the single endpoint (`/graphql`) that serves all requests, and the **Introspection** functionality: a special query (`__schema`) that returns the entire database structure, available queries, data types, and fields.

In production, Introspection should be disabled because it provides the attacker with a complete map of the API (including undocumented functionality). The document `graphql/README.md` details the complete kill chain:
1. Introspection via curl (bypassing the block on the graphical interface).
2. Discovery of undocumented queries: `systemDebug`, `systemDiagnostics`.
3. Command Injection on the `systemDebug(arg: String)` query.
4. Remote Code Execution confirmed with `; id`.
5. Exfiltration of the `config.py` file containing admin credentials in cleartext.

---

## `postman/` - IDOR/BOLA testing

**Finding ID:** `WEB-014` | **Severity:** `Critical` | **CVSS v3.1:** 9.1

### Operational context

IDOR (Insecure Direct Object Reference), classified as BOLA (Broken Object Level Authorization) in the OWASP API Top 10:2023, is the most common and critical vulnerability in APIs. The application accepts a resource ID in the URL (e.g., `/api/balance/1001`) and returns the corresponding data **without verifying whether the authenticated user is the owner of that resource**.

The document `postman/README.md` details:
- Identification of the vulnerable endpoint `/api/balance/<account_id>`.
- Manual test: changing the ID from 1000 to 1001 returns another user's data (instead of `403 Forbidden`).
- Automation with Python script: enumeration of all IDs from 998 to 1005 and dump of financial data.
- Exfiltrated data: Bob's balance (150,000 EUR), Charlie/CEO (9,999,999 EUR), Dave/Admin (2,500 EUR).

---

## Recommended operational flow

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

## Finding registry - API security

| id | description | severity | cvss | subdirectory |
| :--- | :--- | :---: | :---: | :--- |
| `WEB-012` | jwt weak secret (`secret123`) - admin token forging via offline brute force | `Critical` | 9.8 | `jwt-tokens/` |
| `WEB-013` | graphql introspection enabled + command injection rce via `systemDebug` | `Critical` | 9.8 | `graphql/` |
| `WEB-014` | idor/bola - access to financial data of all users without authorization | `Critical` | 9.1 | `postman/` |

---

## Reference tools

| tool | type | technique/access | primary use case |
| :--- | :--- | :--- | :--- |
| `jwt_tool` | jwt analyzer | cli - offline | jwt analysis, brute force, and forging |
| `hashcat` | password cracker | cli - offline | jwt hash brute force with gpu acceleration |
| `Burp Suite` | web proxy | gui - manual | interception and modification of api requests with jwt |
| `curl` | http client | cli | manual testing of graphql and rest endpoints |
| `Postman` | api client | gui | interactive rest api testing, collections, scripting |
| `graphql-voyager` | graphql visualizer | web ui | graphical visualization of the graphql schema |
| `clairvoyance` | graphql enum | cli - active | graphql schema enumeration even without introspection |
| `nuclei` | template-based | cli - active | owasp api top 10 and jwt vulnerability templates |

> **Recommended modern tool:** `jwt_tool` (ticarpi/jwt_tool) - dedicated JWT tool with support for brute force, payload modification, vulnerability testing (alg:none, RS256 to HS256). Installation: `pip3 install jwt_tool`.

---

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| credential access | brute force: password cracking | `T1110.002` | offline brute force of the jwt hs256 signature using a dictionary to recover the key `secret123` (WEB-012) |
| defense evasion | use alternate authentication material | `T1550` | use of the forged jwt token with admin role to access privileged functionality (WEB-012) |
| lateral movement | valid accounts: cloud accounts | `T1078.003` | impersonation of the admin account through a forged jwt token (WEB-012) |
| reconnaissance | active scanning: wordlist scanning | `T1595.003` | graphql introspection to map all available queries, including undocumented ones (WEB-013) |
| execution | command and scripting interpreter: unix shell | `T1059.004` | command injection through the `arg` parameter of the `systemDebug` query -> rce with `; id` (WEB-013) |
| collection | data from information repositories | `T1213` | exfiltration of admin credentials from `config.py` and sqlite database dump through rce (WEB-013) |
| discovery | account discovery | `T1087` | enumeration of account ids on the `/api/balance/<id>` endpoint to map all users (WEB-014) |
| collection | data from information repositories | `T1213` | access to financial data of unauthorized users through idor/bola (WEB-014) |
| lateral movement | valid accounts | `T1078` | use of a legitimate account to perform idor requests against other users' accounts (WEB-014) |

---

> **Note:** The documented API vulnerabilities were identified and exploited in lab environments:
> DVGA (Damn Vulnerable GraphQL Application) in a local Docker container for WEB-013,
> a custom Flask/Python application for WEB-012 and WEB-014. All activities were
> conducted within an authorized perimeter. Exploiting these vulnerabilities on production APIs
> without authorization violates terms of service and constitutes a computer crime.
