> **English** | [Italiano](README.md)

# API Broken Object Level Authorization (BOLA/IDOR)

> - **Phase:** Web Attack - API Security (REST/IDOR)
> - **Visibility:** Low - legitimate HTTP requests to an authenticated endpoint, only the resource ID changes
> - **Prerequisites:** Valid user account with API access, endpoint that accepts a resource ID in the URL path, authentication token
> - **Output:** Access to financial data of all users (balance, IBAN), massive exfiltration, GDPR violation, finding WEB-014

---

**Finding ID:** `WEB-014` | **Severity:** `Critical` | **CVSS v3.1:** 9.1

---

## 1 Executive Summary

During the Security Assessment activity conducted on the target banking application's APIs, a critical IDOR (Insecure Direct Object Reference) vulnerability was identified, classified in the OWASP API Top 10 as API1:2023 - Broken Object Level Authorization.

The API allows access to bank account details (balance, IBAN, owner name) simply by knowing or guessing the numeric account ID.

Using automation techniques (Postman Collection Runner simulation), it was possible to enumerate and exfiltrate the financial data of all users in the database, including privileged accounts (CEO/Admin), without any authorization.

Business Impact: Massive privacy violation (GDPR), financial data loss, irreparable reputational damage.

---

## 2 Technical Vulnerability Details
Description

The `/api/balance/<account_id>` endpoint accepts an integer parameter (`account_id`) in the URL to identify the resource to return.

The backend does not verify whether the user making the request is actually the owner of that account. It relies exclusively on the input provided by the client.

Attack Vector

- Discovery: The analyst identified the endpoint through documentation analysis or network traffic.
- Manual Test: It was verified that changing the ID from `1000` (legitimate user) to `1001`, the API returned another user's data instead of a "403 Forbidden" error.
- Automation (Fuzzing): An automation script (equivalent to Postman Collection Runner) was used to iterate over a range of IDs (from 998 to 1005).

Proof of Concept (PoC) & Evidence

The automated attack allowed the exfiltration of the following sensitive data in a few milliseconds:

- ID 1001: Bob (Victim) - Balance: EUR 150,000
- ID 1002: Charlie (CEO) - Balance: EUR 9,999,999
- ID 1003: Dave (Admin) - Balance: EUR 2,500

![](./img/Screenshot_2026-02-18_16_10_41.jpg)

---

## 3 Root Cause Analysis (Vulnerable Code)

Analysis of the source code (`vulnerable_bank.py`) that caused the flaw.

The problem lies in the lack of an Authorization Check before returning the object.

```Python
@app.route('/api/balance/<int:account_id>', methods=['GET'])
def get_balance(account_id):
    # ERROR: The API blindly trusts the ID passed in the URL.
    # There is no check on WHO is making the request.
    account = accounts.get(account_id)
    
    if account:
        return jsonify(account) # Returns data to anyone!
```

---

## 4 Remediation (Secure Coding)

To fix this vulnerability, it is necessary to implement an access control mechanism based on the logged-in user's identity (Session or JWT).

The API must compare the requested ID with the authenticated user's ID.

```Python
# ASSUMPTION: We use a library such as Flask-Login or JWT Extended
from flask_jwt_extended import get_jwt_identity, jwt_required

@app.route('/api/balance/<int:requested_account_id>', methods=['GET'])
@jwt_required()  # 1. Requires the user to be logged in
def get_balance_SECURE(requested_account_id):
    
    # 2. Get the ID of the user making the request (from Token/Session)
    current_user_id = get_jwt_identity() 
    
    # 3. SECURITY CHECK (Authorization Check)
    # "Is the logged-in user the owner of the requested account?"
    if current_user_id != requested_account_id:
        # If they try to request a different ID from their own -> BLOCK
        return jsonify({"error": "Forbidden: You cannot access this account"}), 403

    # If the check passes, return the data
    account = accounts.get(requested_account_id)
    return jsonify(account)
```

Additional Recommendations:

- Use UUIDs: Replace sequential IDs (1000, 1001...) with UUIDs (e.g., `a1b2-c3d4...`). This makes it impossible for an attacker to "guess" the next account number (Enumeration defense), although it does not resolve the root authorization problem.
- Rate Limiting: Implement a request limit (e.g., 10 requests per minute) to block automated scanning attempts like those performed with Postman/Python.

---

## 5 Conclusions

The detected IDOR vulnerability is critical and allows total compromise of banking data confidentiality. The absence of horizontal authorization controls is a common but devastating error.

Immediate deployment of the proposed patch (Ownership Check) and execution of a new testing cycle with Postman to verify the fix are recommended.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Discovery | Account Discovery | `T1087` | Enumeration of account IDs on the `/api/balance/<id>` endpoint from 998 to 1005 to map all users present in the system (WEB-014) |
| Collection | Data from Information Repositories | `T1213` | Access to sensitive financial data (balance, name) of Bob, Charlie/CEO, and Dave/Admin without any authorization through IDOR (WEB-014) |
| Lateral Movement | Valid Accounts | `T1078` | Use of an ordinary user's authentication token to access data from accounts with higher privileges (CEO, Admin) (WEB-014) |

---

> **Note:** Finding WEB-014 was documented on a local Flask/Python lab application
> (`vulnerable_bank.py`) developed to simulate a vulnerable banking API. IDOR/BOLA
> is the number 1 vulnerability in the OWASP API Top 10:2023 by frequency and impact. Its
> simplicity of exploitation (changing a number in the URL) contrasts with the severity of
> the impact: massive GDPR and reputational violation for the affected organization.
