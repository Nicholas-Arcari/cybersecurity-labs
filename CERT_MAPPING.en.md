> **English** | [Italiano](CERT_MAPPING.md)

# Certification Mapping - Labs vs Syllabus

This table maps each repository module to the objectives of major cybersecurity certifications. The goal is twofold: (1) demonstrate practical syllabus coverage through documented labs, (2) identify gaps to address before sitting the exam.

---

## Estimated Coverage

| Certification | Vendor | Lab Coverage | Notes |
| :--- | :--- | :--- | :--- |
| **OSCP** (PEN-200) | OffSec | ~75% of syllabus | Missing: Active Directory, client-side attacks |
| **eJPT** (v2) | INE Security | ~95% of syllabus | Near-complete coverage |
| **CEH** (v13) | EC-Council | ~70% of modules | Missing: mobile hacking, IoT, pure theory |
| **Security+** (SY0-701) | CompTIA | ~60% of domains | Practical focus, missing governance/compliance |
| **PenTest+** (PT0-002) | CompTIA | ~80% of domains | Missing: formal scoping/planning |

---

## Detailed Matrix

### Module 00 - Kali Setup

| Lab | Topic | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 00-setup | Attack platform hardening, UFW, SSH | Ch. 2-4 | - | - | 3.0 | 5.3 |

### Module 01 - Reconnaissance

| Lab | Topic | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| osint-passive | Google Dorking, theHarvester, Sherlock | Ch. 6 | 1.1 | Mod. 2 | 1.1 | 2.1 |
| google-dorks | Advanced search operators | Ch. 6 | 1.1 | Mod. 2 | - | 2.1 |
| breach-data | HIBP, DeHashed, credential correlation | Ch. 6 | - | Mod. 2 | 1.1 | 2.1 |
| email-harvesting | Email address enumeration, OSINT | Ch. 6 | 1.1 | Mod. 2 | - | 2.1 |
| user-enumeration | Username discovery, social media scraping | Ch. 6 | - | Mod. 2 | - | 2.1 |
| network-scanning | Nmap, host/port discovery, evasion | Ch. 7 | 1.2, 2.1 | Mod. 3 | 1.4 | 2.2 |
| live-host-discovery | ARP scan, ICMP sweep, SYN ping | Ch. 7 | 1.2 | Mod. 3 | - | 2.2 |
| port-scanning | SYN/TCP/UDP scan, timing, output | Ch. 7 | 1.2 | Mod. 3 | 4.1 | 2.2 |
| masscan | High-speed full-range scanning | Ch. 7 | - | Mod. 3 | - | 2.2 |
| nmap-scripts | NSE vuln, SMB/HTTP enum | Ch. 7 | 2.1 | Mod. 3 | - | 2.2 |
| dns-enumeration | Zone transfer, subdomain brute | Ch. 7 | 1.2 | Mod. 4 | - | 2.2 |
| infrastructure-intel | Shodan, Censys, tech profiling | Ch. 6 | - | Mod. 2 | 1.1 | 2.1 |

### Module 02 - Vulnerability Assessment

| Lab | Topic | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| nessus | Credentialed scan, plugin families | Ch. 8 | 2.1 | Mod. 5 | 4.1 | 2.3 |
| nmap-nse-vuln | NSE vulnerability scanning | Ch. 8 | 2.1 | Mod. 5 | 4.1 | 2.3 |
| open-vas-gvm | OpenVAS deployment, NVT config | Ch. 8 | 2.1 | Mod. 5 | 4.1 | 2.3 |
| smb-net-bios | Null session, share enum, EternalBlue | Ch. 7-8 | 2.1 | Mod. 3 | - | 2.3 |
| smtp | Open relay, VRFY/EXPN user enum | Ch. 7 | - | Mod. 3 | - | 2.3 |
| snmp | Community string brute, MIB walking | Ch. 7 | - | Mod. 3 | - | 2.3 |
| ssl-tls | Certificate chain, cipher analysis | Ch. 7 | - | Mod. 20 | 3.1 | 2.3 |
| cvss-calculator | CVSS v3.1, risk prioritization | - | - | Mod. 5 | 5.2 | 4.1 |
| reporting-templates | Executive summary, technical findings | - | - | - | - | 4.1 |

### Module 03 - Web Attacks

| Lab | Topic | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| burp-suite | Proxy, Repeater, Intruder, scope | Ch. 9 | 4.1 | Mod. 14 | - | 3.1 |
| owasp-zap | Spider, active scan, auth handling | Ch. 9 | 4.1 | Mod. 14 | - | 3.1 |
| dir-busting | Gobuster, ffuf, wordlist selection | Ch. 9 | 4.1 | Mod. 13 | - | 3.1 |
| sql-injection | UNION, blind, error-based, WAF bypass | Ch. 10 | 4.2 | Mod. 15 | 1.2 | 3.2 |
| sqlmap | Tamper scripts, dump, OS shell | Ch. 10 | 4.2 | Mod. 15 | - | 3.2 |
| xss | Reflected, Stored, DOM, filter bypass | Ch. 9 | 4.2 | Mod. 14 | 1.2 | 3.2 |
| ssti | Jinja2/Twig detection, sandbox escape, RCE | Ch. 9 | - | - | - | 3.2 |
| auth-attacks | Web bruteforce, session hijacking | Ch. 9 | 4.2 | Mod. 11 | 1.2 | 3.2 |
| jwt-tokens | None algo, key confusion, token forgery | Ch. 9 | - | - | - | 3.2 |
| graphql | Introspection, IDOR, batching, RCE | Ch. 9 | - | - | - | 3.2 |
| cms-specific | WordPress, Drupal, Joomla exploitation | Ch. 9 | 4.1 | Mod. 13 | - | 3.1 |
| secure-coding | Prepared statements, encoding, CSP | - | - | - | 1.2 | - |

### Module 04 - System Exploitation

| Lab | Topic | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| empire | Fileless C2, PowerShell stager, LotL | Ch. 20 | 3.1 | Mod. 6 | 1.2 | 3.3 |
| metasploit | reverse_tcp, migration, SOCKS pivot | Ch. 20 | 3.1 | Mod. 6 | - | 3.3 |
| compiled-exploits | Cross-compilation, in-memory shellcode | Ch. 12-14 | - | Mod. 6 | - | 3.3 |
| searchsploit | Nmap XML correlation, exploit triage | Ch. 12 | 3.1 | Mod. 5 | - | 2.3 |
| linux-priv-esc | SUID, GTFOBins, LinPEAS, cronjob | Ch. 17 | 3.2 | Mod. 6 | - | 3.4 |
| windows-priv-esc | Token impersonation, WinPEAS, Sherlock | Ch. 16 | 3.2 | Mod. 6 | - | 3.4 |
| buffer-overflow | EIP control, bad chars, JMP ESP | Ch. 12-13 | - | Mod. 6 | - | 5.2 |
| pwntools | ROP chain, ASLR bypass, GOT leak | - | - | - | - | 5.2 |
| password-cracking | Hashcat mask/rules, John, wordlists | Ch. 15 | 3.1 | Mod. 20 | - | 3.5 |

### Module 05 - Social Engineering

| Lab | Topic | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| phishing-campaigns | GoPhish, EvilGinx, PyPhisher | - | - | Mod. 9 | 1.1 | 3.6 |
| social-engineer-toolkit | SET vectors, credential harvester | Ch. 11 | - | Mod. 9 | 1.1 | 3.6 |
| payload-delivery | Macros, HTML smuggling, ISO/LNK | Ch. 11 | - | Mod. 9 | 1.2 | 3.3 |
| email-infrastructure | SPF/DKIM/DMARC, typosquatting | - | - | Mod. 9 | 1.1 | 3.6 |

### Module 06 - Wireless Security

| Lab | Topic | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| wifi | Handshake capture, WPA cracking, rogue AP | - | - | Mod. 16 | 3.4 | 3.7 |
| bluetooth-ble | BLE recon, GATT enum, spoofing | - | - | - | - | - |
| sdr | Signal analysis, replay attacks | - | - | - | - | - |
| rfid-nfc | MIFARE cloning, Proxmark3 | - | - | - | 3.4 | 3.7 |

### Module 07 - Post-Exploitation

| Lab | Topic | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| local-enumeration | Situational awareness Linux/Windows | Ch. 16-17 | 3.2 | Mod. 6 | - | 3.4 |
| mimikatz | sekurlsa, DCSync, golden ticket | Ch. 15 | - | Mod. 6 | - | 3.5 |
| la-zagne | Browser/WiFi/email credential recovery | Ch. 15 | - | Mod. 6 | - | 3.5 |
| persistence | Cron, registry, scheduled tasks, webshells | Ch. 16-17 | - | Mod. 6 | - | 3.4 |
| pivoting-tunneling | Chisel, Ligolo-ng, sshuttle, socat | Ch. 18-19 | 3.3 | Mod. 6 | - | 3.8 |
| exfiltration | Covert channels, log cleaning | - | - | Mod. 6 | - | 3.9 |

### Module 08 - Defense & Hardening

| Lab | Topic | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| siem-log-analysis | Splunk, ELK Stack, log aggregation | - | - | Mod. 12 | 4.3 | 4.2 |
| wazuh | XDR deployment, active response, Suricata | - | - | Mod. 12 | 4.3 | 4.2 |
| honeypots | T-Pot, Canary Tokens, deception | - | - | Mod. 12 | 4.4 | - |
| hardening-scripts | CIS benchmark, GPO, sysctl | - | - | Mod. 6 | 3.0 | 5.3 |

### Module 09 - Digital Forensics

| Lab | Topic | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| disk-forensics | Image acquisition, timeline, artifacts | - | - | Mod. 8 | 4.4 | - |
| wireshark | Display filters, stream reconstruction | Ch. 4 | 2.1 | Mod. 8 | 4.4 | 2.2 |

### Module 10 - Cloud Security

| Lab | Topic | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| aws | IAM enum, S3 bucket attacks | - | - | Mod. 19 | 2.2 | 3.10 |
| azure | Entra ID, RBAC abuse | - | - | Mod. 19 | 2.2 | 3.10 |
| gcp | Service account abuse, Cloud Storage | - | - | Mod. 19 | 2.2 | 3.10 |
| docker | Image scanning, runtime security | - | - | - | 2.2 | 3.10 |
| kubernetes | Pod escape, RBAC review, kube-bench | - | - | - | 2.2 | 3.10 |
| iac-security | Terraform scanning, secrets management | - | - | - | 2.2 | 5.3 |

---

## Legend

- **Ch. N**: PEN-200 (OSCP) syllabus chapter
- **N.N**: eJPTv2 (INE) syllabus section
- **Mod. N**: CEH v13 (EC-Council) syllabus module
- **N.N**: SY0-701 (Security+) domain/objective
- **N.N**: PT0-002 (PenTest+) domain/objective
- **-**: Topic not covered by that certification

---

## Gap Analysis

### For OSCP (PEN-200)
- **Covered:** Information Gathering, Vulnerability Scanning, Web Attacks, SQL Injection, Public Exploits, Password Attacks, Linux/Windows PrivEsc, Tunneling, Metasploit
- **To integrate:** Active Directory Enumeration & Exploitation (Ch. 21), advanced Client-Side Attacks (Ch. 11)

### For eJPT (v2)
- **Covered:** Assessment Methodologies, Host & Networking, Penetration Testing, Web Application Testing
- **To integrate:** no significant gaps - the repo covers all 4 modules

### For CEH (v13)
- **Covered:** Footprinting, Scanning, Enumeration, System Hacking, Social Engineering, Web Hacking, SQL Injection, Wireless, Cloud, Cryptography
- **To integrate:** Mobile Platform Hacking (Mod. 17), IoT Hacking (Mod. 18)

---

> **Note:** Chapter/module references are based on official 2024-2025 syllabi. Always verify the current version on the certification vendor's website before planning your study.
