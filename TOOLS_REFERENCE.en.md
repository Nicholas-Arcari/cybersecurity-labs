> **English** | [Italiano](TOOLS_REFERENCE.md)

# Tools reference - complete tool index

> Quick reference of all tools used across the labs, with direct links to the files
> documenting their practical usage. For each tool: category, description, and every
> README that employs it.

---

## Table of contents

- [Reconnaissance](#reconnaissance)
- [Vulnerability Assessment](#vulnerability-assessment)
- [Web Application Testing](#web-application-testing)
- [System Exploitation](#system-exploitation)
- [Password Cracking](#password-cracking)
- [Binary Exploitation](#binary-exploitation)
- [Targets and Lab Infrastructure](#targets-and-lab-infrastructure)
- [Custom Scripts](#custom-scripts)

---

## Reconnaissance

| tool | description | used in |
| :--- | :--- | :--- |
| **nmap** | port scanner and service/os fingerprinting - de facto standard for network recon | [nmap-scripts](<01-recon (Red Team Basic)/02-network-scanning-active/port-scanning (Nmap)/nmap-scripts/README.en.md>), [live-host-discovery](<01-recon (Red Team Basic)/02-network-scanning-active/live-host-discovery/README.en.md>), [nmap-nse-vuln](<02-vulnerability-assessment/01-general-scanners (Infrastructure)/nmap-nse-vuln/README.en.md>) |
| **masscan** | asynchronous high-speed port scanner (100k+ pkt/s) | [masscan](<01-recon (Red Team Basic)/02-network-scanning-active/port-scanning (Nmap)/masscan/README.en.md>) |
| **theharvester** | osint harvester for emails, subdomains, ips from public sources | [email-harvesting](<01-recon (Red Team Basic)/01-osint-passive (Open Source Intelligence)/email-harvesting/README.en.md>) |
| **sherlock** | username enumeration across 400+ social networks | [user-enumeration](<01-recon (Red Team Basic)/01-osint-passive (Open Source Intelligence)/user-enumeration/README.en.md>) |
| **google dorks** | advanced search operators for information disclosure | [google-dorks](<01-recon (Red Team Basic)/01-osint-passive (Open Source Intelligence)/google-dorks/README.en.md>) |
| **dnsrecon** | dns enumeration: zone transfer, brute force, record lookup | [dns-recon](<01-recon (Red Team Basic)/03-dns-enumeration/dns-recon/README.en.md>) |
| **subfinder** | passive subdomain discovery via apis (projectdiscovery) | [subdomain-finding](<01-recon (Red Team Basic)/03-dns-enumeration/subdomain-finding/README.en.md>) |
| **shodan** | search engine for internet-exposed devices | [shodan-censys](<01-recon (Red Team Basic)/04-infrastructure-intel/shodan-censys/README.en.md>) |
| **censys** | certificate and exposed host intelligence | [shodan-censys](<01-recon (Red Team Basic)/04-infrastructure-intel/shodan-censys/README.en.md>) |
| **wappalyzer / whatweb** | web technology stack fingerprinting | [tech-stack](<01-recon (Red Team Basic)/04-infrastructure-intel/tech-stack/README.en.md>), [tech-profiler](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/tech-profiler/README.en.md>) |

---

## Vulnerability assessment

| tool | description | used in |
| :--- | :--- | :--- |
| **nessus** | commercial vulnerability scanner (tenable) - credentialed scan | [nessus](<02-vulnerability-assessment/01-general-scanners (Infrastructure)/nessus/README.en.md>) |
| **openvas / gvm** | open-source vulnerability scanner (greenbone) | [open-vas-gvm](<02-vulnerability-assessment/01-general-scanners (Infrastructure)/open-vas-gvm/README.en.md>), [perform-vulnerability-scans](<00-setup-after-installing-kali/11-perform-vulnerability-scans/README.en.md>) |
| **nmap nse (vuln)** | nse scripts for vulnerability detection (smb-vuln-*, ssl-*) | [nmap-nse-vuln](<02-vulnerability-assessment/01-general-scanners (Infrastructure)/nmap-nse-vuln/README.en.md>) |
| **enum4linux / enum4linux-ng** | smb/netbios enumeration: shares, users, password policies | [smb-net-bios](<02-vulnerability-assessment/02-protocol-specific-audit/smb-net-bios/README.en.md>) |
| **nbtscan** | netbios name discovery on network segments | [smb-net-bios](<02-vulnerability-assessment/02-protocol-specific-audit/smb-net-bios/README.en.md>) |
| **testssl.sh** | ssl/tls audit: ciphers, protocols, certificates, vulnerabilities | [ssl-tls](<02-vulnerability-assessment/02-protocol-specific-audit/ssl-tls/README.en.md>) |
| **searchsploit** | offline search in the exploit-db database | [searchsploit-manual-lookup](<02-vulnerability-assessment/03-cve-analysis (Research)/searchsploit-manual-lookup/README.en.md>), [searchsploit](<04-system-exploitation/02-exploit-database/searchsploit/README.en.md>) |
| **cvss calculator** | cvss v3.1 score calculation for vulnerability classification | [cvss-calculator](<02-vulnerability-assessment/03-cve-analysis (Research)/cvss-calculator/README.en.md>) |
| **smtp-user-enum** | smtp user enumeration (vrfy/expn/rcpt) | [smtp](<02-vulnerability-assessment/02-protocol-specific-audit/smtp/README.en.md>) |
| **snmpwalk / onesixtyone** | snmp community string and oid tree enumeration | [snmp](<02-vulnerability-assessment/02-protocol-specific-audit/snmp/README.en.md>) |

---

## Web application testing

| tool | description | used in |
| :--- | :--- | :--- |
| **burp suite** | intercepting proxy for web application testing (portswigger) | [burp-suite](<03-web-attacks (Red Team + Secure Coding)/01-proxy-tools (Intercept)/burp-suite/README.en.md>) |
| **owasp zap** | open-source proxy + automated scanner (owasp) | [owasp-zap](<03-web-attacks (Red Team + Secure Coding)/01-proxy-tools (Intercept)/owasp-zap/README.en.md>) |
| **gobuster** | directory/file brute forcing (go, fast) | [dir-busting](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/dir-busting/README.en.md>) |
| **feroxbuster** | recursive content discovery (rust, modern) | [dir-busting](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/dir-busting/README.en.md>) |
| **nikto** | legacy web server scanner (misconfigs, dangerous files) | [vulnerability-scanners](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/vulnerability-scanners/README.en.md>) |
| **nuclei** | template-based vulnerability scanner (projectdiscovery) | [vulnerability-scanners](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/vulnerability-scanners/README.en.md>) |
| **sqlmap** | automated sql injection - detection, exploitation, dump | [sql-map-data](<03-web-attacks (Red Team + Secure Coding)/03-owasp (Attacks)/sql-injection (SQLi)/sql-map-data/README.en.md>) |
| **hydra** | multi-protocol brute force (http, ssh, ftp, rdp, smb...) | [bruteforce-web](<03-web-attacks (Red Team + Secure Coding)/03-owasp (Attacks)/auth-attacks/bruteforce-web/README.en.md>) |
| **wpscan** | wordpress-specific scanner (vulns, plugins, users) | [wordpress](<03-web-attacks (Red Team + Secure Coding)/04-cms-specific/wordpress/README.en.md>) |
| **joomscan** | joomla-specific scanner | [joomla](<03-web-attacks (Red Team + Secure Coding)/04-cms-specific/joomla/README.en.md>) |
| **droopescan** | multi-cms scanner (drupal, joomla, wordpress, silverstripe) | [drupal](<03-web-attacks (Red Team + Secure Coding)/04-cms-specific/drupal/README.en.md>) |
| **pyjwt** | python library for jwt token forging/cracking | [jwt-tokens](<03-web-attacks (Red Team + Secure Coding)/05-api-security/jwt-tokens/README.en.md>) |
| **postman / curl** | manual rest api testing + idor/bola exploitation | [postman](<03-web-attacks (Red Team + Secure Coding)/05-api-security/postman/README.en.md>) |
| **graphql voyager / inql** | graphql schema introspection and analysis | [graphql](<03-web-attacks (Red Team + Secure Coding)/05-api-security/graphql/README.en.md>) |
| **subfinder** | passive subdomain enumeration for web recon | [subdomain-enum](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/subdomain-enum/README.en.md>) |

---

## System exploitation

| tool | description | used in |
| :--- | :--- | :--- |
| **metasploit framework** | modular exploitation framework (rapid7) | [metasploit](<04-system-exploitation/01-frameworks/metasploit/README.en.md>) |
| **msfvenom** | metasploit payload generator (reverse shell, staged, encoded) | [metasploit](<04-system-exploitation/01-frameworks/metasploit/README.en.md>), [compiled-exploits](<04-system-exploitation/02-exploit-database/compiled-exploits/README.en.md>) |
| **powershell empire** | post-exploitation c2 framework (fileless, in-memory) | [empire](<04-system-exploitation/01-frameworks/empire/README.en.md>) |
| **mingw-w64** | c/c++ cross-compilation for windows targets from linux | [compiled-exploits](<04-system-exploitation/02-exploit-database/compiled-exploits/README.en.md>) |
| **printspoofer** | privilege escalation via seimpersonateprivilege (win10+) | [juicypotato-printnightmare](<04-system-exploitation/03-privilege-escalation (PrivEsc)/windows-priv-esc/juicypotato-printnightmare/README.en.md>) |
| **winpeas** | windows privilege escalation automated enumeration | [winpeas](<04-system-exploitation/03-privilege-escalation (PrivEsc)/windows-priv-esc/winpeas/README.en.md>) |
| **linpeas** | linux privilege escalation automated enumeration | [linpeas](<04-system-exploitation/03-privilege-escalation (PrivEsc)/linux-priv-esc/linpeas/README.en.md>) |
| **gtfobins** | database of unix binaries exploitable for privesc (sudo, suid) | [gtfo-bins-notes](<04-system-exploitation/03-privilege-escalation (PrivEsc)/linux-priv-esc/gtfo-bins-notes/README.en.md>) |
| **sherlock.ps1** | windows kernel patch audit (ms10-015, ms16-032...) | [sherlock](<04-system-exploitation/03-privilege-escalation (PrivEsc)/windows-priv-esc/sherlock/README.en.md>) |

---

## Password cracking

| tool | description | used in |
| :--- | :--- | :--- |
| **hashcat** | gpu-accelerated password cracking (ntlm, bcrypt, sha...) | [hashcat](<04-system-exploitation/05-password-cracking/hashcat/README.en.md>) |
| **john the ripper** | cpu-based password cracker + hash extraction utilities | [john-the-ripper](<04-system-exploitation/05-password-cracking/john-the-ripper/README.en.md>) |
| **zip2john / unshadow** | hash extraction from zip archives and /etc/shadow | [john-the-ripper](<04-system-exploitation/05-password-cracking/john-the-ripper/README.en.md>) |
| **rockyou / seclists** | standard wordlists for dictionary attacks | [wordlists](<04-system-exploitation/05-password-cracking/wordlists/README.en.md>) |

---

## Binary exploitation

| tool | description | used in |
| :--- | :--- | :--- |
| **pwntools** | python framework for exploit development (rop, shellcode) | [pwntools-scripts](<04-system-exploitation/04-binary-exploitation/pwntools-scripts/README.en.md>) |
| **gdb + peda/gef** | debugger with exploit development extensions | [buffer-overflow-prep](<04-system-exploitation/04-binary-exploitation/buffer-overflow-prep/README.en.md>) |
| **checksec** | binary protection verification (nx, aslr, pie, canary) | [buffer-overflow-prep](<04-system-exploitation/04-binary-exploitation/buffer-overflow-prep/README.en.md>) |
| **ropgadget** | rop gadget search in elf/pe binaries | [pwntools-scripts](<04-system-exploitation/04-binary-exploitation/pwntools-scripts/README.en.md>) |

---

## Targets and lab infrastructure

| tool | description | used in |
| :--- | :--- | :--- |
| **dvwa** | damn vulnerable web application - web target for sqli, xss, csrf | [docker-compose.yml](docker-compose.yml), [sql-injection](<03-web-attacks (Red Team + Secure Coding)/03-owasp (Attacks)/sql-injection (SQLi)/README.en.md>) |
| **dvga** | damn vulnerable graphql application - graphql api target | [docker-compose.yml](docker-compose.yml), [graphql](<03-web-attacks (Red Team + Secure Coding)/05-api-security/graphql/README.en.md>) |
| **juice shop** | owasp juice shop - 100+ owasp top 10 challenges | [docker-compose.yml](docker-compose.yml) |
| **virtualbox** | hypervisor for lab vms | [lab_setup.en.md](LAB_SETUP.en.md), [lab-setup.sh](scripts/lab-setup.sh) |
| **docker compose** | container orchestration for web targets | [docker-compose.yml](docker-compose.yml), [lab_setup.en.md](LAB_SETUP.en.md) |
| **asciinema** | terminal session recording for demos | [lab_setup.en.md](LAB_SETUP.en.md) |

---

## Custom scripts

| script | description | path |
| :--- | :--- | :--- |
| **nessus_parser.py** | nessus xml parser with severity filter, statistics and csv export | [02-vulnerability-assessment/code/](02-vulnerability-assessment/code/nessus_parser.py) |
| **header_security_check.py** | http security header analysis with score and fix suggestions | [03-web-attacks/code/](<03-web-attacks (Red Team + Secure Coding)/code/header_security_check.py>) |
| **hash_identifier.py** | hash type identifier with hashcat/john mode suggestions | [04-system-exploitation/code/](04-system-exploitation/05-password-cracking/code/hash_identifier.py) |
| **lab-setup.sh** | virtualbox vm setup automation (create, network, snapshot) | [scripts/](scripts/lab-setup.sh) |
| **check-finding-ids.sh** | finding id validation (format, uniqueness, sequentiality) | [scripts/](scripts/check-finding-ids.sh) |

---

## Statistics

| category | tools | files documenting them |
| :--- | :---: | :---: |
| reconnaissance | 10 | 12 |
| vulnerability assessment | 10 | 11 |
| web application testing | 15 | 16 |
| system exploitation | 9 | 9 |
| password cracking | 4 | 4 |
| binary exploitation | 4 | 4 |
| defensive tools | 7 | 7 |
| targets/infrastructure | 6 | 8 |
| custom scripts | 5 | 5 |
| **total** | **70** | **76** |

---

> *Versions and compatibility: all listed tools were tested on Kali Linux 2024.x.
> When modern alternatives are available (e.g., NetExec instead of CrackMapExec), they
> are noted in the respective module READMEs.*
