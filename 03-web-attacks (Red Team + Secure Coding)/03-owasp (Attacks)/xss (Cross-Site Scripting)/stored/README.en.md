> **English** | [Italiano](README.md)

# Vulnerability Assessment: Stored Cross-Site Scripting (XSS)

> - **Phase:** Web Attack - XSS Stored
> - **Visibility:** Low - the payload is inserted once and then affects all page visitors without further requests from the attacker
> - **Prerequisites:** Input field persistent in database (comment, profile, guestbook) without input and output sanitization
> - **Output:** Persistent JavaScript payload in database, automatic execution on every page visit, user session cookie theft, finding WEB-006

---

**Finding ID:** `WEB-006` | **Severity:** `High` | **CVSS v3.1:** 8.2

---

## 1 Executive Summary

During the analysis of the application `testphp.vulnweb.com`, a critical Stored Cross-Site Scripting (XSS) vulnerability was identified.

Unlike the "Reflected" variant, in this case the malicious code is permanently saved in the application's database.

The vulnerability resides in the user registration and profile modification process. The application stores user input without sanitization and presents it to anyone viewing that profile (including the user themselves or an administrator).

The impact is critical since the attack does not require the victim to click on a specific link: simply viewing the infected page is sufficient to execute the code (e.g., admin cookie theft).

---

## 2 Technical Analysis

#### Scenario: Profile Persistence Injection

The registration module allows entry of personal data. It was verified that the "Address" field accepts and saves HTML tags and JavaScript.

Exploitation Procedure:

1.  The attacker accesses the registration page (`/signup.php`).

2.  Fills in the form inserting the malicious payload in the Address field.

3.  Submits the form. The server saves the payload in the database.

Payload Used:

```html
Via Roma 1 <script>alert('XSS SALVATO NEL DB!')</script>
```

Evidence Analysis:

As shown in the screenshot below, as soon as the application retrieves data from the database to display it (in the registration confirmation or profile panel), the script is injected into the DOM and executed.

The popup confirms that the JavaScript code was persisted and executed from the application's context.

![](./img/Screenshot_2026-02-15_22_46_03.jpg)

---

## 3 Remediation Plan

Stored XSS mitigation requires rigorous interventions both on input and output.

- Input Validation (Allow-list):
    
    Validate incoming data. The "Address" field should not contain characters like `<` or `>`. Reject the input if non-compliant.

- Output Encoding (Crucial):
    
    Every time data is retrieved from the database and inserted into an HTML page, it must be encoded.

    - PHP: Use `htmlspecialchars($address, ENT_QUOTES, 'UTF-8')`.

    - This transforms `<script>` into `&lt;script&gt;`, which is displayed as safe text and not executed.

- Sanitization Libraries:
    
    If it is necessary to allow some HTML (e.g., bold or italic), use trusted sanitization libraries (like DOMPurify for JS or HTML Purifier for PHP) that remove only dangerous tags (script, iframe, object).

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Injection of XSS payload in the "Address" field of the registration form on `testphp.vulnweb.com`, persisted in database without sanitization (WEB-006) |
| Persistence | Server Software Component: Web Shell | `T1505.003` | The Stored XSS payload is equivalent to a persistent server-side malicious component that executes automatically every time the page is viewed (WEB-006) |
| Credential Access | Steal Web Session Cookie | `T1539` | The Stored XSS payload is the vector for stealing the administrator's session cookie when viewing the infected profile, without requiring attacker interaction (WEB-006) |

---

> **Note:** Finding WEB-006 was documented on `testphp.vulnweb.com` exploiting the "Address" field of the registration form. Stored XSS is classified `High` (vs `Medium` for Reflected) because it affects all page visitors including administrators, without requiring the victim to click on a specific link.
