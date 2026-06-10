> **English** | [Italiano](README.md)

# Drupal Core Remote Code Execution (Drupalgeddon 2)

> - **Phase:** Web Attack - CMS Exploitation
> - **Visibility:** Medium - HTTP POST requests with payload targeting Drupal forms, detectable but often not blocked by generic WAFs
> - **Prerequisites:** Drupal instance version 6.x, 7.x (< 7.58), or 8.x (< 8.3.9) identified, network connectivity to the target
> - **Output:** Unauthenticated Remote Code Execution, Drupal admin dashboard access, PHP Web Shell deployment, server control, finding WEB-015

---

**Finding ID:** `WEB-015` | **Severity:** `Critical` | **CVSS v3.1:** 9.8

---

## 1 Executive Summary

During the Penetration Testing activity conducted on the Windows 10 test environment, a critical vulnerability was identified and successfully exploited in the Drupal CMS instance (version 7.54).

The vulnerability, known as Drupalgeddon 2 (CVE-2018-7600), resides in a lack of input sanitization in Drupal's Form API subsystem.

This flaw allowed unauthenticated arbitrary remote code execution (RCE). Despite the presence of endpoint protection (Windows Defender) that blocked automated reverse shell attempts, it was possible to achieve persistence and system control by leveraging native CMS functionality to inject a PHP Web Shell.

The exploit granted server control with the privileges of the user running the web service, exposing the entire infrastructure to data exfiltration and total compromise risks.

CVSS Score: 9.8 (Critical)

---

## 2 Technical Analysis

#### 1. Reconnaissance & Fingerprinting

The initial reconnaissance phase allowed identification of the specific Drupal version in use.

By analyzing publicly accessible files (e.g., `CHANGELOG.txt`) or HTTP headers, it was confirmed that the target runs an outdated and vulnerable version.

Evidence:

The following screenshot shows the version identification (e.g., 7.54) through analysis of the `CHANGELOG.txt` file.

![](./img/Screenshot_2026-02-16_17_55_22.jpg)

#### 2. Exploitation (CVE-2018-7600)

The vulnerability exploits the handling of AJAX requests in forms (Form API). By manipulating the `#post_render` parameters, it is possible to induce the CMS to execute arbitrary PHP functions.

Attack Vector:

- Methodology: Manual Exploitation (Bypass of automated/AV controls).
- Technique: Injection of malicious arrays through crafted POST requests.
- Payload: System command execution (`passthru`, `exec`) via curl followed by backdoor creation.

Execution:

Initially, automated exploits were attempted but were blocked by the Windows host security policies. A manual attack was then carried out by sending a specific payload to verify code execution (`RCE verification`).

#### 3. Post-Exploitation & Persistence

Once the vulnerability was confirmed, access was consolidated by transforming the RCE into a persistent Web Shell.

- Privilege Escalation / Administrative Access: Access to the Drupal administration dashboard was obtained (bypassing authentication or resetting the password via RCE).
- Vulnerable Module Activation: The core "PHP Filter" module was enabled, which allows PHP code execution within content nodes.
- Web Shell Deployment: A disguised page named "system diagnostyc" was created. A PHP payload (`<?php system("ipconfig"); ?>`) was injected into the page body, configuring the text format as "PHP code".

Evidence:

The following screenshot documents the successful operation. The CMS page returning the output of the `ipconfig` system command directly from the underlying Windows server is visible, confirming total control over the network infrastructure and the system user.

![](./img/Screenshot_2026-02-16_18_14_49.jpg)

---

## 3 Business Impact

The impact of this vulnerability is classified as CRITICAL for the following reasons:

- Confidentiality (Total Loss): The attacker has full access to the Drupal database (containing user credentials, customer data) and the Windows server files.
- Integrity (Total Loss): It is possible to modify site content (Defacement), insert persistent backdoors, or alter data in the database.
- Availability: The attacker can delete critical files, stop the web service, or encrypt data for extortion purposes (Ransomware).

Since the attack requires no authentication, the site is exposed to any malicious actor on the internet or on the local network.

---

## 4 Remediation Plan

The following corrective actions are recommended with immediate urgency:

- Patching (High Priority):

    Immediately update the Drupal core to secure versions:

    - If 7.x: Update to 7.58 or later.
    - If 8.x: Update to 8.3.9, 8.4.6, 8.5.1, or later.

- Web Application Firewall (WAF):

    Implement WAF rules to block requests containing suspicious parameters such as `#post_render`, `#markup`, or attempts to invoke functions like `passthru` or `exec`.

- Server Hardening:

    - Disable dangerous PHP functions in `php.ini` (e.g., `disable_functions = exec,passthru,shell_exec,system`).
    - Disable the "PHP Filter" module if not strictly necessary.
    - Remove unnecessary files such as `CHANGELOG.txt` or `INSTALL.txt` from the site root to complicate fingerprinting.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Active Scanning: Vulnerability Scanning | `T1595.002` | Fingerprinting of Drupal version 7.54 through access to the public `CHANGELOG.txt` file and identification of CVE-2018-7600 (WEB-015) |
| Initial Access | Exploit Public-Facing Application | `T1190` | Manual exploitation of CVE-2018-7600 through manipulation of `#post_render` parameters in Drupal's Form API to achieve unauthenticated RCE (WEB-015) |
| Persistence | Server Software Component: Web Shell | `T1505.003` | PHP Web Shell deployment through Drupal's "PHP Filter" module, creating a "system diagnostyc" page that executes system commands (WEB-015) |
| Discovery | File and Directory Discovery | `T1083` | Execution of the `ipconfig` command through the Web Shell to map the network configuration of the underlying Windows server (WEB-015) |

---

> **Note:** Finding WEB-015 was documented on a Drupal 7.54 instance installed locally
> on a Windows 10 virtual machine, configured as a test environment for educational purposes.
> CVE-2018-7600 is a high-profile 2018 vulnerability (Drupalgeddon2) with patches available
> since March 2018. Any Drupal instance not updated to version 7.58 or later in
> production environments represents an immediate critical risk.
