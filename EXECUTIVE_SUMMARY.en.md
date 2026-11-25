> **English** | [Italiano](EXECUTIVE_SUMMARY.md)

# Penetration test - executive summary

---

```
RESTRICTED DOCUMENT - CONFIDENTIAL

Classification:  Restricted - Internal Use
Version:         1.0
Issue date:      March 2026
Author:          Nicholas Arcari - Security Analyst
Recipients:      Management, CTO, CISO
```

---

## 1. Context and engagement scope

### Objective

This Penetration Test engagement was commissioned with the objective of independently
and objectively assessing the security posture of the internal IT infrastructure,
exposed web applications and corporate server systems. The engagement simulates the
capabilities and tactics of a real external attacker attempting to penetrate the
corporate network without pre-assigned privileges.

### Scope

| component | target | notes |
| :--- | :--- | :--- |
| network infrastructure | lan segment `10.0.2.0/24` and `192.168.0.0/24` | host discovery, port scan, exposed services |
| server operating system | windows 10 pro (`10.0.2.3` / `192.168.0.109`) | os vulnerabilities, smb services, rdp |
| server operating system | ubuntu linux (`192.168.0.x`) | insecure configurations, privesc |
| web applications | lamp/xampp stack, drupal cms, graphql api | owasp top 10, api security |
| osint sources | public profiles, dns, search engines | passive reconnaissance |

### Execution period

| phase | description | estimated duration |
| :--- | :--- | :--- |
| passive reconnaissance | osint, dns, shodan | 2 days |
| active reconnaissance | network scan, service enumeration | 1 day |
| vulnerability assessment | credentialed scan, protocol audit | 3 days |
| web application testing | owasp top 10, api, cms | 5 days |
| system exploitation | initial access, privilege escalation | 4 days |
| reporting | analysis, documentation, recommendations | 3 days |

### Methodology

The test was conducted following the international guidelines **PTES** (Penetration
Testing Execution Standard) and **OWASP Testing Guide v4**, with systematic mapping
of documented techniques to the **MITRE ATT&CK** framework. No activity was conducted
outside the agreed scope. All tested systems are authorized lab environments.

---

## 2. Methodology - engagement phases

```
[PASSIVE RECON]          [ACTIVE RECON]          [ASSESSMENT]
OSINT - DNS - Shodan --> Nmap - Masscan -------> Nessus - SMB/SNMP/SMTP audit
        |                      |                        |
        v                      v                        v
[WEB TESTING]           [EXPLOITATION]          [POST-EXPLOIT]
OWASP Top 10 ----------> Initial Access -------> PrivEsc - Lateral Movement
SQL Injection            EternalBlue              WinPEAS - LinPEAS
XSS - SSTI - JWT         Empire - MSF             Credential Harvesting
GraphQL - IDOR           Custom payload            Pass-the-Hash
```

Each phase feeds the next: information gathered during reconnaissance guided the
choice of attack vectors, vulnerability assessment results identified the
vulnerabilities to exploit, exploitation produced initial access that enabled
privilege escalation.

---

## 3. Overall risk overview

### Finding distribution by severity

| severity | count | % of total | potential impact |
| :--- | :---: | :---: | :--- |
| **Critical** | 15 | 25% | total compromise, data loss, rce |
| **High** | 23 | 38% | unauthorized access, privilege escalation |
| **Medium** | 11 | 18% | information disclosure, weak configurations |
| **Low** | 3 | 5% | Low probability of exploitation |
| **Informational** | 8 | 14% | observations with no direct immediate impact |
| **total** | **60** | 100% | |

> **Executive takeaway:** 63% of identified findings (38 out of 60) are classified
> as Critical or High. This means that more than half of the identified vulnerabilities
> are directly exploitable by an attacker with average skills to gain unauthorized
> access, exfiltrate data or compromise the infrastructure.

### Business impact by category

| area | findings | business impact |
| :--- | :--- | :--- |
| network infrastructure | SCAN-003, VULN-001..004 | internal traffic interception, access to corporate file shares |
| web applications | WEB-001..015 | user data theft, authentication bypass, server control |
| operating systems | EXPLOIT-001..019 | total server control, persistence, lateral movement |
| osint exposure | OSINT-001..004 | employee data and credentials already circulating in breach databases |
| insecure configurations | EXPLOIT-016, EXPLOIT-017 | plaintext system passwords, modifiable binaries |

---

## 4. Top 5 critical findings

The following five findings were selected from the 15 critical findings based on the
combination of exploitability, organizational impact and attack surface coverage.
Each section is written in language accessible to management.

---

### 4.1 - Total Windows server compromise via 9-Year-Old known vulnerability

**Finding:** VULN-002 + EXPLOIT-001 | **Severity:** Critical

The production Windows server has not been updated with a security patch (MS17-010)
released by Microsoft in **May 2017**, nine years ago. This vulnerability, publicly
known as "EternalBlue", is the same one used in the global WannaCry attack that
in 2017 paralyzed hospitals, banks and companies across 150 countries.

During testing, by exploiting this vulnerability with publicly available and free
tools, it was possible to gain **complete server control** (`SYSTEM` level,
equivalent to administrator access with full privileges) in less than 3 minutes,
without any credentials and without any user interaction.

**What an attacker can do:** read and modify any file on the server, install
software, encrypt data for ransom demands (ransomware), use the server as a
base to attack other systems on the internal network.

**Required action:** immediately install Windows security patches or isolate the
system from the network. Estimated resolution time: less than 1 hour of technical work.

---

### 4.2 - Corporate database accessible through web application vulnerability

**Finding:** WEB-004 + WEB-011 | **Severity:** Critical

The web application does not properly validate data entered by users in search
and login fields. Through a technique called "SQL Injection", it was possible to:

- Access the application as any user, including the administrator, **without
  knowing the password**
- Extract the complete database contents, including **tables with user data,
  credentials, personal information and transactions**

This class of vulnerability is classified by OWASP as the leading cause of data
breaches in web applications for over 15 years. Its exploitation is partially
automatable and does not require advanced skills.

**Regulatory impact:** in the presence of personal data (names, emails, IBANs,
purchase history), this vulnerability constitutes a GDPR violation and requires,
in case of exploitation by third parties, notification to the Data Protection
Authority within 72 hours.

**Required action:** review all database access logic in the application.
Technical solution: use "prepared statements" to replace dynamic queries.
Estimated resolution time: 3-5 days of development.

---

### 4.3 - System administrator password found in an unprotected file

**Finding:** EXPLOIT-016 | **Severity:** Critical

During the file system analysis of the compromised Windows server, a configuration
file (`Unattend.xml`) was found on the server, left after an automated operating
system installation. This file contained, in plaintext and without any encryption,
the **Administrator account password**.

In practical terms: anyone with file system access to the server - including an
attacker who gained initial access with the lowest privileges - can read this
password and immediately use it to take complete control of the server and
potentially other systems sharing the same credential.

**Required action:** immediately delete the file `C:\Windows\Panther\Unattend.xml`
and all similar files. Change the Administrator password to a secure one (minimum
16 characters). Verify if the same password is used on other systems (credential
reuse). Estimated resolution time: less than 1 hour.

---

### 4.4 - Full application access as administrator without knowing the password

**Finding:** WEB-012 | **Severity:** Critical

The application uses JWT tokens (JSON Web Token) to verify user identity after
login. The mechanism is correct in theory, but the secret used to sign the tokens
was set with a trivial value present in common password lists ("secret",
"password123" and similar).

This allowed, within seconds using free tools, to **forge an identity token with
"admin" role** and access all administrative features of the application without
ever performing a real login.

**What an attacker can do:** access data of all registered users, modify
configurations, delete content, perform privileged operations as if they were
the legitimate system administrator.

**Required action:** generate a JWT secret with a secure cryptographic generator
(minimum 256 bits of entropy). Invalidate all active tokens after replacement.
Estimated resolution time: less than 2 hours of development.

---

### 4.5 - A normal user can view any other user's financial data

**Finding:** WEB-014 | **Severity:** Critical

The application API does not verify that the user requesting data is actually the
owner of that data. By modifying a parameter in the request URL (e.g., changing
`/api/account/123` to `/api/account/124`), a regularly authenticated user can
access another user's data.

This vulnerability, classified by OWASP as "BOLA/IDOR" and considered the most
widespread in modern APIs, allowed during testing to enumerate all registered
users' profiles and access their financial data (balance, transactions, payment
methods).

**Regulatory impact:** unauthorized access to third-party financial data constitutes
a GDPR violation (personal data), potentially a PCI-DSS violation (payment data)
and represents an offense under Article 615-ter of the Italian Penal Code
(unauthorized access to a computer system).

**Required action:** implement server-side authorization checks on every API
endpoint that returns user data, verifying that the requester's identity matches
the resource owner. Estimated resolution time: 3-7 days of development.

---

## 5. Strategic recommendations

Recommendations are organized by time horizon and prioritized based on the ratio
between risk urgency and implementation effort.

### Urgent priority - within 30 days

| priority | action | related findings | effort |
| :---: | :--- | :--- | :--- |
| 1 | apply all overdue windows security patches (particularly ms17-010) | VULN-002, EXPLOIT-001 | Low (operational) |
| 2 | delete unattend.xml files and change administrator credentials | EXPLOIT-016 | Low (<1 hour) |
| 3 | fix sql injections in the web application (prepared statements) | WEB-004, WEB-011 | Medium (3-5 days) |
| 4 | replace jwt secret with a cryptographically secure value | WEB-012 | Low (<2 hours) |
| 5 | implement object-level authorization in apis (anti-idor) | WEB-014 | Medium (3-7 days) |
| 6 | enable mandatory smb signing via group policy | SCAN-003, VULN-001 | Low (gpo) |

### Short term - within 90 days

| priority | action | related findings | effort |
| :---: | :--- | :--- | :--- |
| 7 | implement complex password policy (min. 14 characters) and mfa on all privileged systems | EXPLOIT-016..019 | Medium |
| 8 | remove or disable smbv1 protocol | VULN-002 | Low |
| 9 | fix acl permissions on service binaries (xampp and similar) | EXPLOIT-017 | Low |
| 10 | sanitize all server-side template engines (anti-ssti) | WEB-008 | Medium |
| 11 | fix access control logic in drupal cms modules (version update) | WEB-015 | Low |
| 12 | disable graphql introspection in production; validate all parameters | WEB-013 | Low |

### Medium term - within 180 days

| priority | action | notes |
| :---: | :--- | :--- |
| 13 | deploy a web application firewall (waf) in front of the web application | reduces attack surface for automated attacks |
| 14 | start a structured vulnerability management program (monthly automated scans) | prevents re-accumulation of security technical debt |
| 15 | internal network segmentation (vlan) to isolate critical systems | limits lateral movement in case of compromise |
| 16 | developer training on secure coding (owasp top 10) | reduces web findings at the root cause |

### Long term - strategic plan

| initiative | description |
| :--- | :--- |
| **secure development lifecycle (sdl)** | integrate security review into the development process: code review, sast/dast in ci/cd, threat modeling before developing new features |
| **annual penetration test** | repeat an equivalent testing activity every year or after significant architectural changes, to measure progress and detect new risks |
| **incident response plan** | define formal incident response procedures: who calls whom, which systems to isolate, how to preserve evidence for forensic analysis |
| **asset inventory and patch management** | maintain an updated registry of all systems, with software versions and patch status; automate updates where possible |

---

## 6. Conclusion

### Current posture

The engagement identified **60 vulnerabilities in 18 days of testing**, of which 63%
are Critical or High severity. Total compromise of the Windows server was achieved
in less than **3 minutes from the start of the exploitation phase**, without
pre-assigned credentials and exploiting a vulnerability that has been public for 9 years.

The most relevant criticalities do not require advanced techniques: most Critical
findings are exploitable with publicly available and free tools by anyone with basic
technical skills. This significantly lowers the risk threshold.

### Target posture

The recovery path is defined and realistic. Short-term measures (patching, removal
of sensitive files, SQL Injection fixes, cryptographic secrets) can reduce the
critical attack surface by **70% in less than 30 days** with predominantly technical
and low-cost interventions.

Achieving a mature security posture requires a 12-18 month plan combining immediate
technical interventions, software development process review and establishment of
continuous security practices (patch management, vulnerability scanning, periodic
penetration testing).

### Reference metrics

| indicator | current value | 6-month target |
| :--- | :--- | :--- |
| open Critical findings | 15 | 0 |
| open High findings | 23 | < 5 |
| time to total compromise | < 3 minutes | > 30 days (realistic objective) |
| systems with overdue patches | all tested systems | 0 unpatched critical systems |
| systems with mfa enabled | 0% | 100% on privileged access |

---

> **Reference methodology:** PTES (Penetration Testing Execution Standard),
> OWASP Testing Guide v4.2, MITRE ATT&CK Framework v14.
>
> **Complete technical documentation:** this Executive Summary is the summary
> document intended for management. The full technical documentation, including
> tool outputs, proof-of-concepts, detailed finding IDs and specific remediation,
> is available in the `cybersecurity-labs/` repository modules.
>
> **Disclaimer:** all documented activities were conducted exclusively on
> authorized lab infrastructure. No technique was applied to real production
> systems or third-party systems without explicit authorization.
