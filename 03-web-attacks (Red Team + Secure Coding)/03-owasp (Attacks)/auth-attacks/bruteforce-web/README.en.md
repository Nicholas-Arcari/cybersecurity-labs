> **English** | [Italiano](README.md)

# Auth Attacks: Brute-Force Web (Hydra)

> - **Phase:** Web Attack - Authentication Brute Force
> - **Visibility:** High - Hydra generates many login requests in short time, easily detectable by IDS and monitoring systems
> - **Prerequisites:** Login form identified and analyzed with DevTools (POST parameters, endpoint URL), wordlist available
> - **Output:** Valid credentials for application access, finding WEB-009 (missing rate limiting and account lockout)

---

**Finding ID:** `WEB-009` | **Severity:** `High` | **CVSS v3.1:** 7.5

---

Objective: Execute a Dictionary Attack against a web login form to identify weak credentials.

Target: `http://testphp.vulnweb.com` and local application

Tools: `THC-Hydra` (Network Login Cracker), `Firefox DevTools`

---

## 1 Theoretical Introduction

Web Brute-Force consists of systematically trying numerous username and password combinations.

Unlike standard services, the web attack requires configuring Hydra to handle the HTTP/POST protocol, correctly identifying server responses to distinguish a failed login from a successful one.

Risk (OWASP): Broken Authentication. The lack of protection mechanisms (Rate Limiting, Account Lockout) allows an attacker to try millions of passwords undisturbed.

---

## 2 Target Analysis and "False Positive Trap"

Preliminary analysis with Developer Tools revealed the form parameters (`uname`, `pass`) sent to `/userinfo.php`.

The Redirect (302) Challenge:

During initial tests, it was noticed that the server responds with an HTTP 302 Found (Redirect) code both on success and failure, rendering the classic error string search ("Login Failed") ineffective. This generated False Positives (all passwords were marked as valid).

![](./img/Screenshot_2026-02-14_19_18_22.jpg)

Solution:

Hydra's logic was inverted: instead of searching for the error, the tool was configured to search for a Success string (`S=Logout`), present only on the restricted page accessible after authentication.

---

## 3 Attack Execution

A targeted wordlist (`passlist.txt`) was created containing the correct credential mixed with false ones.

![](./img/Screenshot_2026-02-14_19_24_50.jpg)

```Bash
# S=Logout : Tells Hydra the login is valid IF it finds the word "Logout" in the response
hydra -l test -P passlist.txt testphp.vulnweb.com http-post-form "/userinfo.php:uname=^USER^&pass=^PASS^:S=Logout" -V
```

![](./img/Screenshot_2026-02-14_19_31_18.jpg)

Result (Proof of Concept):

Analysis:

Hydra correctly discarded wrong passwords (like admin or 123456) and uniquely identified the only valid credential:

- Login: `test`
- Password: `test`

---

## 4 Secure Coding & Defense

To mitigate these attacks:

- Rate Limiting: Limit requests per IP (e.g., max 5 logins/minute).
- Delay Response: Add an artificial delay (e.g., 1-2 seconds) after a failed login to drastically slow down massive brute-force attacks.
- MFA (Multi-Factor Authentication): The only definitive defense against password theft.
- Message Generation: Avoid generic messages. Ensure error responses have predictable status codes and content for monitoring, but not useful to the attacker for user enumeration.

---

## 5 Docker & Localhost Scenario (Lab Setup)

The attack was replicated against a real containerized infrastructure (Docker) to simulate an "Internal Penetration Test" scenario.

Technical Challenges faced:

- Networking (VM vs Host):
    
    Running the attack from a Virtual Machine (Kali) against Docker (running on the Host), the target `localhost` (127.0.0.1) is not valid. It was necessary to identify the physical network adapter's IP (`192.168.x.x`) to reach the containers.

- Port Mapping & Service Discovery:
    
    A common mistake is attacking the port exposed by the Frontend (e.g., `:5173` for Vite/React).

    - Recon: Through `docker ps` and browser Network tab analysis, it was identified that the authentication logic resided on a separate container (`<backend_container_name>`) exposed on port 80.

- Blue Team Monitoring:
    
    The advantage of attacking a local environment is total visibility. It was possible to observe the attack "from inside" by monitoring backend container logs:

```Bash
docker logs -f <backend_container_name>
```

This confirmed that requests were reaching the server, but were being rejected.

---

## 6 Case Study: "The Laravel Wall" (Defensive Analysis)

During the attempt to brute force the Laravel application's authentication, the attack evolved through several troubleshooting phases that highlighted modern web framework defenses.

#### Phase 1: The "Frontend Trap"

Initially, the attack was directed at the URL visible in the browser: `http://host:5173/login`.

- Result: `HTTP 404 Not Found`.
- Analysis: Being a Single Page Application (SPA), the `/login` route on port 5173 is virtual (managed by JavaScript). The real API endpoint resided on port 80.

#### Phase 2: Protocol Complexity (JSON vs Form)

Hydra is optimized for standard HTML forms (`application/x-www-form-urlencoded`). The target API required a JSON payload.

- Problem: Attempts to adapt Hydra with `http-post-json` modules or manual escaping (`{\"email\":...}`) generated syntax errors and false negatives due to tool rigidity.
- Solution: A custom Bash script (based on `curl`) was developed to have granular control over Headers and Body format.

```Bash
#!/bin/bash

# Configuration
TARGET="http://192.168.xxx.xxx:80/login"    # replace xxx with real ip address
USER="<USERNAME>"                           # replace with real username

echo "Attack started on: $TARGET"
echo "Target user: $USER"
echo "------------------------------------------------"

# Read passlist.txt file line by line
while read PASS; do
    # Execute CURL request and save response (silent -s)
    # Note: We use timeout 2s to not block if server is slow
    RESPONSE=$(curl -s --max-time 2 -X POST "$TARGET" \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -d "{\"email\":\"$USER\",\"password\":\"$PASS\"}")

    # Response analysis
    if echo "$RESPONSE" | grep -q "CSRF"; then
         echo "BLOCKED BY CSRF (Laravel Sanctum/Missing Token)"
         echo "-> Attack cannot proceed without a valid token."
         break
    elif echo "$RESPONSE" | grep -q "Invalid credentials"; then
         echo "Failed attempt: $PASS"
    elif echo "$RESPONSE" | grep -q "The route"; then
         echo "Error 404: Route is not correct."
         break
    else
         # If not a known error, it could be a success or redirect
         echo "SUCCESS!! (or anomalous response)"
         echo "Password: $PASS"
         echo "Server Response: $RESPONSE"
         break
    fi

done < passlist.txt
```

![](./img/Screenshot_2026-02-14_21_38_45.jpg)

#### Phase 3: The CSRF Clash (Sanctum)

Once the `/login` endpoint on port 80 was correctly reached with the custom script, the server systematically responded with an `HTTP 419` error.

```JSON
{
    "message": "CSRF token mismatch.",
    "exception": "Symfony\\Component\\HttpKernel\\Exception\\HttpException"
}
```

Defense Analysis:

Laravel (through the Sanctum/Web Middleware package) protects login routes by requiring a valid CSRF Token.

- The real browser obtains this token by making a preliminary `GET /sanctum/csrf-cookie` request.
- Hydra (or the simple Bash script) is "stateless": it sends the direct POST request without first negotiating the token.
- The server rejects the request regardless of password correctness.

Conclusion:

This test demonstrated that modern MVC/API frameworks (like Laravel, Django, Rails), when correctly configured with Anti-CSRF protections and Stateful Authentication, are intrinsically resistant to "simple" brute-force attacks executed with generic tools like Hydra. To bypass this defense, an advanced script capable of managing sessions and cookies (e.g., Python with `requests.Session()`) would be necessary.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Credential Access | Brute Force: Password Guessing | `T1110.001` | Attack with Hydra on login form `testphp.vulnweb.com/userinfo.php` using `passlist.txt`, identifying credentials `test:test` (WEB-009) |
| Credential Access | Brute Force: Password Spraying | `T1110.004` | Testing common passwords (`admin`, `123456`, `password`) against user `test` as preliminary phase (WEB-009) |
| Credential Access | Modify Authentication Process | `T1556` | Analysis and bypass of Laravel Sanctum Anti-CSRF protection (HTTP 419) demonstrating Hydra's ineffectiveness on modern frameworks |
| Initial Access | Exploit Public-Facing Application | `T1190` | Exploitation of missing rate limiting and account lockout on login form for unblocked brute force (WEB-009) |

---

> **Note:** Brute force activities documented were conducted on `testphp.vulnweb.com` (Acunetix environment) and on a local Docker Laravel application (owned by the author). The case study "The Laravel Wall" documents the defenses of a correctly configured modern framework, demonstrating that Hydra is ineffective against CSRF Token + Sanctum. Performing brute force on real systems without authorization is a criminal offense.
