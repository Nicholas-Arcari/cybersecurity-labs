> **English** | [Italiano](README.md)

# Cross-Site Scripting (XSS) - Post-Remediation Verification

> - **Phase:** Secure Coding - XSS Mitigation (Output Encoding)
> - **Visibility:** Zero - local analysis and testing in local PHP environment (`localhost:8000`)
> - **Prerequisites:** Vulnerable code identified (direct echo), fix implemented with `htmlspecialchars()`, local PHP server for testing
> - **Output:** Confirmation that the XSS payload is no longer executed but displayed as safe text, secure code documented

---

## 1 Executive Summary

During the source code analysis of the web application, a Reflected XSS vulnerability was found in the GET parameter `name`.

This vulnerability allowed an attacker to inject arbitrary JavaScript code that would be executed in the victim's browser.

A fix based on Output Encoding was implemented. Tests confirm that the malicious code is now neutralized and displayed as harmless text.

---

## 2 Vulnerability Analysis

Technical Description

The application accepted user input via the URL and printed it directly into the HTML page without any sanitization or encoding. This allowed the browser to interpret special characters (`<`, `>`, `"`) as valid HTML tags.

Attack Vector (Proof of Concept)

- Endpoint: `http://localhost:8000/xss-defense.php`
- Vulnerable Parameter: `name`
- Payload: `<script>alert('Hacked')</script>` or `<img src=x onerror=alert('XSS')>`

![](./img/Screenshot_2026-02-18_20_55_46.jpg)

Attack Evidence:

Executing the payload generated a JavaScript popup ("Hacked"), confirming the execution of unauthorized code in the browser context.

---

## 3 Root Cause Analysis (Vulnerable Code)

The defect resided in the use of the `echo` statement directly on a user-controlled variable.

```PHP
<div class="box bad">
    <p>Ciao, <?php echo $_GET['name']; ?></p>
</div>
```

The input `<script>...` is written as-is into the DOM, triggering execution.

---

## 4 Remediation (Secure Coding)

To mitigate the vulnerability, the Context-Aware Output Encoding technique was applied.

In PHP, this is achieved using the `htmlspecialchars()` function, which converts special characters into HTML Entities (e.g., `<` becomes `&lt;`).

```PHP
<div class="box good">
    <p>Ciao, 
    <?php 
        // Converte i caratteri speciali in entità HTML sicure
        echo htmlspecialchars($_GET['name'], ENT_QUOTES, 'UTF-8'); 
    ?>
    </p>
</div>
```

---

## 5 Fix Verification (Verification)

The same attack was re-executed against the patched code block.

- Test: Injection of the payload `<img src=x onerror=alert('XSS')>`.
- Expected Result: The JavaScript code must not be executed.
- Actual Result: The browser displayed the payload as plain text. No popup appeared and the page layout was not compromised.


![](./img/Screenshot_2026-02-18_20_56_06.jpg)

Mitigation Evidence:

The screenshot clearly shows the difference: the red box (vulnerable) shows an error icon (execution attempt), while the green box (secure) shows the sanitized text string.

---

## 6 Conclusions

The implementation of `htmlspecialchars()` has effectively eliminated the XSS vulnerability on this endpoint. The system now treats user input as data (text) and not as executable code.

It is recommended to extend this "Output Encoding" practice to all variables printed in the application.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Description (Defensive - XSS Mitigation) |
| :--- | :--- | :--- | :--- |
| (Mitigation) | Exploit Public-Facing Application | `T1190` | Implementation of `htmlspecialchars($_GET['name'], ENT_QUOTES, 'UTF-8')` which converts special characters (`<`, `>`, `"`, `'`) into safe HTML entities, neutralizing the Reflected XSS vector (CWE-79) |

---

> **Note:** The documented fix (htmlspecialchars + ENT_QUOTES + UTF-8) is the remediation pattern
> recommended by OWASP for Output Encoding in HTML contexts. The combination of the
> `ENT_QUOTES` and `'UTF-8'` parameters ensures protection even against encoding variants and character
> set attacks. The post-patch verification with `<img src=x onerror=alert('XSS')>` confirms that the
> payload is now displayed as text, not executed as code.
