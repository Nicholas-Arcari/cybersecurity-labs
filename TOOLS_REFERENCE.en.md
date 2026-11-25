> **English** | [Italiano](TOOLS_REFERENCE.md)

# Tools Reference - Complete Tool Index

> Quick reference of all tools used across the labs, with direct links to the files
> documenting their practical usage. For each tool: category, description, and every
> README that employs it.

---

## Table of Contents

- [Reconnaissance](#reconnaissance)
- [Vulnerability Assessment](#vulnerability-assessment)
- [Web Application Testing](#web-application-testing)
- [System Exploitation](#system-exploitation)
- [Password Cracking](#password-cracking)
- [Binary Exploitation](#binary-exploitation)
- [Defensive Tools](#defensive-tools)
- [Targets and Lab Infrastructure](#targets-and-lab-infrastructure)
- [Custom Scripts](#custom-scripts)

---

## Reconnaissance

| Tool | Description | Used in |
| :--- | :--- | :--- |
| **Nmap** | Port scanner and service/OS fingerprinting - de facto standard for network recon | [nmap-scripts](<01-recon (Red Team Basic)/02-network-scanning-active/port-scanning (Nmap)/nmap-scripts/README.en.md>), [live-host-discovery](<01-recon (Red Team Basic)/02-network-scanning-active/live-host-discovery/README.en.md>), [nmap-nse-vuln](<02-vulnerability-assessment/01-general-scanners (Infrastructure)/nmap-nse-vuln/README.en.md>) |
| **Masscan** | Asynchronous high-speed port scanner (100k+ pkt/s) | [masscan](<01-recon (Red Team Basic)/02-network-scanning-active/port-scanning (Nmap)/masscan/README.en.md>) |
| **TheHarvester** | OSINT harvester for emails, subdomains, IPs from public sources | [email-harvesting](<01-recon (Red Team Basic)/01-osint-passive (Open Source Intelligence)/email-harvesting/README.en.md>) |
| **Sherlock** | Username enumeration across 400+ social networks | [user-enumeration](<01-recon (Red Team Basic)/01-osint-passive (Open Source Intelligence)/user-enumeration/README.en.md>) |
| **Google Dorks** | Advanced search operators for information disclosure | [google-dorks](<01-recon (Red Team Basic)/01-osint-passive (Open Source Intelligence)/google-dorks/README.en.md>) |
| **dnsrecon** | DNS enumeration: zone transfer, brute force, record lookup | [dns-recon](<01-recon (Red Team Basic)/03-dns-enumeration/dns-recon/README.en.md>) |
| **Subfinder** | Passive subdomain discovery via APIs (ProjectDiscovery) | [subdomain-finding](<01-recon (Red Team Basic)/03-dns-enumeration/subdomain-finding/README.en.md>) |
| **Shodan** | Search engine for Internet-exposed devices | [shodan-censys](<01-recon (Red Team Basic)/04-infrastructure-intel/shodan-censys/README.en.md>) |
| **Censys** | Certificate and exposed host intelligence | [shodan-censys](<01-recon (Red Team Basic)/04-infrastructure-intel/shodan-censys/README.en.md>) |
| **Wappalyzer / WhatWeb** | Web technology stack fingerprinting | [tech-stack](<01-recon (Red Team Basic)/04-infrastructure-intel/tech-stack/README.en.md>), [tech-profiler](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/tech-profiler/README.en.md>) |

---

## Vulnerability Assessment

| Tool | Description | Used in |
| :--- | :--- | :--- |
| **Nessus** | Commercial vulnerability scanner (Tenable) - credentialed scan | [nessus](<02-vulnerability-assessment/01-general-scanners (Infrastructure)/nessus/README.en.md>) |
| **OpenVAS / GVM** | Open-source vulnerability scanner (Greenbone) | [open-vas-gvm](<02-vulnerability-assessment/01-general-scanners (Infrastructure)/open-vas-gvm/README.en.md>), [perform-vulnerability-scans](<00-setup-after-installing-kali/11-perform-vulnerability-scans/README.en.md>) |
| **Nmap NSE (vuln)** | NSE scripts for vulnerability detection (smb-vuln-*, ssl-*) | [nmap-nse-vuln](<02-vulnerability-assessment/01-general-scanners (Infrastructure)/nmap-nse-vuln/README.en.md>) |
| **enum4linux / enum4linux-ng** | SMB/NetBIOS enumeration: shares, users, password policies | [smb-net-bios](<02-vulnerability-assessment/02-protocol-specific-audit/smb-net-bios/README.en.md>) |
| **nbtscan** | NetBIOS name discovery on network segments | [smb-net-bios](<02-vulnerability-assessment/02-protocol-specific-audit/smb-net-bios/README.en.md>) |
| **testssl.sh** | SSL/TLS audit: ciphers, protocols, certificates, vulnerabilities | [ssl-tls](<02-vulnerability-assessment/02-protocol-specific-audit/ssl-tls/README.en.md>) |
| **searchsploit** | Offline search in the Exploit-DB database | [searchsploit-manual-lookup](<02-vulnerability-assessment/03-cve-analysis (Research)/searchsploit-manual-lookup/README.en.md>), [searchsploit](<04-system-exploitation/02-exploit-database/searchsploit/README.en.md>) |
| **CVSS Calculator** | CVSS v3.1 score calculation for vulnerability classification | [cvss-calculator](<02-vulnerability-assessment/03-cve-analysis (Research)/cvss-calculator/README.en.md>) |
| **smtp-user-enum** | SMTP user enumeration (VRFY/EXPN/RCPT) | [smtp](<02-vulnerability-assessment/02-protocol-specific-audit/smtp/README.en.md>) |
| **snmpwalk / onesixtyone** | SNMP community string and OID tree enumeration | [snmp](<02-vulnerability-assessment/02-protocol-specific-audit/snmp/README.en.md>) |

---

## Web Application Testing

| Tool | Description | Used in |
| :--- | :--- | :--- |
| **Burp Suite** | Intercepting proxy for web application testing (PortSwigger) | [burp-suite](<03-web-attacks (Red Team + Secure Coding)/01-proxy-tools (Intercept)/burp-suite/README.en.md>) |
| **OWASP ZAP** | Open-source proxy + automated scanner (OWASP) | [owasp-zap](<03-web-attacks (Red Team + Secure Coding)/01-proxy-tools (Intercept)/owasp-zap/README.en.md>) |
| **Gobuster** | Directory/file brute forcing (Go, fast) | [dir-busting](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/dir-busting/README.en.md>) |
| **Feroxbuster** | Recursive content discovery (Rust, modern) | [dir-busting](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/dir-busting/README.en.md>) |
| **Nikto** | Legacy web server scanner (misconfigs, dangerous files) | [vulnerability-scanners](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/vulnerability-scanners/README.en.md>) |
| **Nuclei** | Template-based vulnerability scanner (ProjectDiscovery) | [vulnerability-scanners](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/vulnerability-scanners/README.en.md>) |
| **sqlmap** | Automated SQL Injection - detection, exploitation, dump | [sql-map-data](<03-web-attacks (Red Team + Secure Coding)/03-owasp (Attacks)/sql-injection (SQLi)/sql-map-data/README.en.md>) |
| **Hydra** | Multi-protocol brute force (HTTP, SSH, FTP, RDP, SMB...) | [bruteforce-web](<03-web-attacks (Red Team + Secure Coding)/03-owasp (Attacks)/auth-attacks/bruteforce-web/README.en.md>) |
| **WPScan** | WordPress-specific scanner (vulns, plugins, users) | [wordpress](<03-web-attacks (Red Team + Secure Coding)/04-cms-specific/wordpress/README.en.md>) |
| **JoomScan** | Joomla-specific scanner | [joomla](<03-web-attacks (Red Team + Secure Coding)/04-cms-specific/joomla/README.en.md>) |
| **Droopescan** | Multi-CMS scanner (Drupal, Joomla, WordPress, SilverStripe) | [drupal](<03-web-attacks (Red Team + Secure Coding)/04-cms-specific/drupal/README.en.md>) |
| **PyJWT** | Python library for JWT token forging/cracking | [jwt-tokens](<03-web-attacks (Red Team + Secure Coding)/05-api-security/jwt-tokens/README.en.md>) |
| **Postman / curl** | Manual REST API testing + IDOR/BOLA exploitation | [postman](<03-web-attacks (Red Team + Secure Coding)/05-api-security/postman/README.en.md>) |
| **GraphQL Voyager / InQL** | GraphQL schema introspection and analysis | [graphql](<03-web-attacks (Red Team + Secure Coding)/05-api-security/graphql/README.en.md>) |
| **Subfinder** | Passive subdomain enumeration for web recon | [subdomain-enum](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/subdomain-enum/README.en.md>) |

---

## System Exploitation

| Tool | Description | Used in |
| :--- | :--- | :--- |
| **Metasploit Framework** | Modular exploitation framework (Rapid7) | [metasploit](<04-system-exploitation/01-frameworks/metasploit/README.en.md>) |
| **msfvenom** | Metasploit payload generator (reverse shell, staged, encoded) | [metasploit](<04-system-exploitation/01-frameworks/metasploit/README.en.md>), [compiled-exploits](<04-system-exploitation/02-exploit-database/compiled-exploits/README.en.md>) |
| **PowerShell Empire** | Post-exploitation C2 framework (fileless, in-memory) | [empire](<04-system-exploitation/01-frameworks/empire/README.en.md>) |
| **MinGW-w64** | C/C++ cross-compilation for Windows targets from Linux | [compiled-exploits](<04-system-exploitation/02-exploit-database/compiled-exploits/README.en.md>) |
| **PrintSpoofer** | Privilege escalation via SeImpersonatePrivilege (Win10+) | [juicypotato-printnightmare](<04-system-exploitation/03-privilege-escalation (PrivEsc)/windows-priv-esc/juicypotato-printnightmare/README.en.md>) |
| **WinPEAS** | Windows Privilege Escalation automated enumeration | [winpeas](<04-system-exploitation/03-privilege-escalation (PrivEsc)/windows-priv-esc/winpeas/README.en.md>) |
| **LinPEAS** | Linux Privilege Escalation automated enumeration | [linpeas](<04-system-exploitation/03-privilege-escalation (PrivEsc)/linux-priv-esc/linpeas/README.en.md>) |
| **GTFOBins** | Database of Unix binaries exploitable for PrivEsc (sudo, SUID) | [gtfo-bins-notes](<04-system-exploitation/03-privilege-escalation (PrivEsc)/linux-priv-esc/gtfo-bins-notes/README.en.md>) |
| **Sherlock.ps1** | Windows kernel patch audit (MS10-015, MS16-032...) | [sherlock](<04-system-exploitation/03-privilege-escalation (PrivEsc)/windows-priv-esc/sherlock/README.en.md>) |

---

## Password Cracking

| Tool | Description | Used in |
| :--- | :--- | :--- |
| **Hashcat** | GPU-accelerated password cracking (NTLM, bcrypt, SHA...) | [hashcat](<04-system-exploitation/05-password-cracking/hashcat/README.en.md>) |
| **John the Ripper** | CPU-based password cracker + hash extraction utilities | [john-the-ripper](<04-system-exploitation/05-password-cracking/john-the-ripper/README.en.md>) |
| **zip2john / unshadow** | Hash extraction from ZIP archives and /etc/shadow | [john-the-ripper](<04-system-exploitation/05-password-cracking/john-the-ripper/README.en.md>) |
| **RockYou / SecLists** | Standard wordlists for dictionary attacks | [wordlists](<04-system-exploitation/05-password-cracking/wordlists/README.en.md>) |

---

## Binary Exploitation

| Tool | Description | Used in |
| :--- | :--- | :--- |
| **pwntools** | Python framework for exploit development (ROP, shellcode) | [pwntools-scripts](<04-system-exploitation/04-binary-exploitation/pwntools-scripts/README.en.md>) |
| **GDB + PEDA/GEF** | Debugger with exploit development extensions | [buffer-overflow-prep](<04-system-exploitation/04-binary-exploitation/buffer-overflow-prep/README.en.md>) |
| **checksec** | Binary protection verification (NX, ASLR, PIE, canary) | [buffer-overflow-prep](<04-system-exploitation/04-binary-exploitation/buffer-overflow-prep/README.en.md>) |
| **ROPgadget** | ROP gadget search in ELF/PE binaries | [pwntools-scripts](<04-system-exploitation/04-binary-exploitation/pwntools-scripts/README.en.md>) |

---

## Targets and Lab Infrastructure

| Tool | Description | Used in |
| :--- | :--- | :--- |
| **DVWA** | Damn Vulnerable Web Application - web target for SQLi, XSS, CSRF | [docker-compose.yml](docker-compose.yml), [sql-injection](<03-web-attacks (Red Team + Secure Coding)/03-owasp (Attacks)/sql-injection (SQLi)/README.en.md>) |
| **DVGA** | Damn Vulnerable GraphQL Application - GraphQL API target | [docker-compose.yml](docker-compose.yml), [graphql](<03-web-attacks (Red Team + Secure Coding)/05-api-security/graphql/README.en.md>) |
| **Juice Shop** | OWASP Juice Shop - 100+ OWASP Top 10 challenges | [docker-compose.yml](docker-compose.yml) |
| **VirtualBox** | Hypervisor for lab VMs | [LAB_SETUP.en.md](LAB_SETUP.en.md), [lab-setup.sh](scripts/lab-setup.sh) |
| **Docker Compose** | Container orchestration for web targets | [docker-compose.yml](docker-compose.yml), [LAB_SETUP.en.md](LAB_SETUP.en.md) |
| **Asciinema** | Terminal session recording for demos | [LAB_SETUP.en.md](LAB_SETUP.en.md) |

---

## Custom Scripts

| Script | Description | Path |
| :--- | :--- | :--- |
| **nessus_parser.py** | Nessus XML parser with severity filter, statistics and CSV export | [02-vulnerability-assessment/code/](02-vulnerability-assessment/code/nessus_parser.py) |
| **header_security_check.py** | HTTP security header analysis with score and fix suggestions | [03-web-attacks/code/](<03-web-attacks (Red Team + Secure Coding)/code/header_security_check.py>) |
| **hash_identifier.py** | Hash type identifier with hashcat/john mode suggestions | [04-system-exploitation/code/](04-system-exploitation/05-password-cracking/code/hash_identifier.py) |
| **lab-setup.sh** | VirtualBox VM setup automation (create, network, snapshot) | [scripts/](scripts/lab-setup.sh) |
| **check-finding-ids.sh** | Finding ID validation (format, uniqueness, sequentiality) | [scripts/](scripts/check-finding-ids.sh) |

---

## Statistics

| Category | Tools | Files documenting them |
| :--- | :---: | :---: |
| Reconnaissance | 10 | 12 |
| Vulnerability Assessment | 10 | 11 |
| Web Application Testing | 15 | 16 |
| System Exploitation | 9 | 9 |
| Password Cracking | 4 | 4 |
| Binary Exploitation | 4 | 4 |
| Defensive Tools | 7 | 7 |
| Targets/Infrastructure | 6 | 8 |
| Custom scripts | 5 | 5 |
| **Total** | **70** | **76** |

---

> *Versions and compatibility: all listed tools were tested on Kali Linux 2024.x.
> When modern alternatives are available (e.g., NetExec instead of CrackMapExec), they
> are noted in the respective module READMEs.*
