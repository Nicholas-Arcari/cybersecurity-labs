> **English** | [Italiano](CERT_MAPPING.md)

# Certification mapping - labs vs syllabus

This table maps each repository module to the objectives of major cybersecurity certifications. The goal is twofold: (1) demonstrate practical syllabus coverage through documented labs, (2) identify gaps to address before sitting the exam.

---

## Estimated coverage

| certification | vendor | lab coverage | notes |
| :--- | :--- | :--- | :--- |
| **oscp** (pen-200) | offsec | ~75% of syllabus | missing: active directory, client-side attacks |
| **ejpt** (v2) | ine security | ~95% of syllabus | near-complete coverage |
| **ceh** (v13) | ec-council | ~70% of modules | missing: mobile hacking, iot, pure theory |
| **security+** (sy0-701) | comptia | ~60% of domains | practical focus, missing governance/compliance |
| **pentest+** (pt0-002) | comptia | ~80% of domains | missing: formal scoping/planning |

---

## Detailed matrix

### Module 00 - Kali setup

| lab | topic | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 00-setup | attack platform hardening, ufw, ssh | ch. 2-4 | - | - | 3.0 | 5.3 |

### Module 01 - reconnaissance

| lab | topic | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| osint-passive | google dorking, theharvester, sherlock | ch. 6 | 1.1 | mod. 2 | 1.1 | 2.1 |
| google-dorks | advanced search operators | ch. 6 | 1.1 | mod. 2 | - | 2.1 |
| breach-data | hibp, dehashed, credential correlation | ch. 6 | - | mod. 2 | 1.1 | 2.1 |
| email-harvesting | email address enumeration, osint | ch. 6 | 1.1 | mod. 2 | - | 2.1 |
| user-enumeration | username discovery, social media scraping | ch. 6 | - | mod. 2 | - | 2.1 |
| network-scanning | nmap, host/port discovery, evasion | ch. 7 | 1.2, 2.1 | mod. 3 | 1.4 | 2.2 |
| live-host-discovery | arp scan, icmp sweep, syn ping | ch. 7 | 1.2 | mod. 3 | - | 2.2 |
| port-scanning | syn/tcp/udp scan, timing, output | ch. 7 | 1.2 | mod. 3 | 4.1 | 2.2 |
| masscan | high-speed full-range scanning | ch. 7 | - | mod. 3 | - | 2.2 |
| nmap-scripts | nse vuln, smb/http enum | ch. 7 | 2.1 | mod. 3 | - | 2.2 |
| dns-enumeration | zone transfer, subdomain brute | ch. 7 | 1.2 | mod. 4 | - | 2.2 |
| infrastructure-intel | shodan, censys, tech profiling | ch. 6 | - | mod. 2 | 1.1 | 2.1 |

### Module 02 - vulnerability assessment

| lab | topic | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| nessus | credentialed scan, plugin families | ch. 8 | 2.1 | mod. 5 | 4.1 | 2.3 |
| nmap-nse-vuln | nse vulnerability scanning | ch. 8 | 2.1 | mod. 5 | 4.1 | 2.3 |
| open-vas-gvm | openvas deployment, nvt config | ch. 8 | 2.1 | mod. 5 | 4.1 | 2.3 |
| smb-net-bios | null session, share enum, eternalblue | ch. 7-8 | 2.1 | mod. 3 | - | 2.3 |
| smtp | open relay, vrfy/expn user enum | ch. 7 | - | mod. 3 | - | 2.3 |
| snmp | community string brute, mib walking | ch. 7 | - | mod. 3 | - | 2.3 |
| ssl-tls | certificate chain, cipher analysis | ch. 7 | - | mod. 20 | 3.1 | 2.3 |
| cvss-calculator | cvss v3.1, risk prioritization | - | - | mod. 5 | 5.2 | 4.1 |
| reporting-templates | executive summary, technical findings | - | - | - | - | 4.1 |

### Module 03 - web attacks

| lab | topic | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| burp-suite | proxy, repeater, intruder, scope | ch. 9 | 4.1 | mod. 14 | - | 3.1 |
| owasp-zap | spider, active scan, auth handling | ch. 9 | 4.1 | mod. 14 | - | 3.1 |
| dir-busting | gobuster, ffuf, wordlist selection | ch. 9 | 4.1 | mod. 13 | - | 3.1 |
| sql-injection | union, blind, error-based, waf bypass | ch. 10 | 4.2 | mod. 15 | 1.2 | 3.2 |
| sqlmap | tamper scripts, dump, os shell | ch. 10 | 4.2 | mod. 15 | - | 3.2 |
| xss | reflected, stored, dom, filter bypass | ch. 9 | 4.2 | mod. 14 | 1.2 | 3.2 |
| ssti | jinja2/twig detection, sandbox escape, rce | ch. 9 | - | - | - | 3.2 |
| auth-attacks | web bruteforce, session hijacking | ch. 9 | 4.2 | mod. 11 | 1.2 | 3.2 |
| jwt-tokens | none algo, key confusion, token forgery | ch. 9 | - | - | - | 3.2 |
| graphql | introspection, idor, batching, rce | ch. 9 | - | - | - | 3.2 |
| cms-specific | wordpress, drupal, joomla exploitation | ch. 9 | 4.1 | mod. 13 | - | 3.1 |
| secure-coding | prepared statements, encoding, csp | - | - | - | 1.2 | - |

### Module 04 - system exploitation

| lab | topic | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| empire | fileless c2, powershell stager, lotl | ch. 20 | 3.1 | mod. 6 | 1.2 | 3.3 |
| metasploit | reverse_tcp, migration, socks pivot | ch. 20 | 3.1 | mod. 6 | - | 3.3 |
| compiled-exploits | cross-compilation, in-memory shellcode | ch. 12-14 | - | mod. 6 | - | 3.3 |
| searchsploit | nmap xml correlation, exploit triage | ch. 12 | 3.1 | mod. 5 | - | 2.3 |
| linux-priv-esc | suid, gtfobins, linpeas, cronjob | ch. 17 | 3.2 | mod. 6 | - | 3.4 |
| windows-priv-esc | token impersonation, winpeas, sherlock | ch. 16 | 3.2 | mod. 6 | - | 3.4 |
| buffer-overflow | eip control, bad chars, jmp esp | ch. 12-13 | - | mod. 6 | - | 5.2 |
| pwntools | rop chain, aslr bypass, got leak | - | - | - | - | 5.2 |
| password-cracking | hashcat mask/rules, john, wordlists | ch. 15 | 3.1 | mod. 20 | - | 3.5 |

### Module 05 - social engineering

| lab | topic | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| phishing-campaigns | gophish, evilginx, pyphisher | - | - | mod. 9 | 1.1 | 3.6 |
| social-engineer-toolkit | set vectors, credential harvester | ch. 11 | - | mod. 9 | 1.1 | 3.6 |
| payload-delivery | macros, html smuggling, iso/lnk | ch. 11 | - | mod. 9 | 1.2 | 3.3 |
| email-infrastructure | spf/dkim/dmarc, typosquatting | - | - | mod. 9 | 1.1 | 3.6 |

### Module 06 - wireless security

| lab | topic | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| wifi | handshake capture, wpa cracking, rogue ap | - | - | mod. 16 | 3.4 | 3.7 |
| bluetooth-ble | ble recon, gatt enum, spoofing | - | - | - | - | - |
| sdr | signal analysis, replay attacks | - | - | - | - | - |
| rfid-nfc | mifare cloning, proxmark3 | - | - | - | 3.4 | 3.7 |

### Module 07 - Post-Exploitation

| lab | topic | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| local-enumeration | situational awareness linux/windows | ch. 16-17 | 3.2 | mod. 6 | - | 3.4 |
| mimikatz | sekurlsa, dcsync, golden ticket | ch. 15 | - | mod. 6 | - | 3.5 |
| la-zagne | browser/wifi/email credential recovery | ch. 15 | - | mod. 6 | - | 3.5 |
| persistence | cron, registry, scheduled tasks, webshells | ch. 16-17 | - | mod. 6 | - | 3.4 |
| pivoting-tunneling | chisel, ligolo-ng, sshuttle, socat | ch. 18-19 | 3.3 | mod. 6 | - | 3.8 |
| exfiltration | covert channels, log cleaning | - | - | mod. 6 | - | 3.9 |

### Module 08 - defense & hardening

| lab | topic | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| siem-log-analysis | splunk, elk stack, log aggregation | - | - | mod. 12 | 4.3 | 4.2 |
| wazuh | xdr deployment, active response, suricata | - | - | mod. 12 | 4.3 | 4.2 |
| honeypots | t-pot, canary tokens, deception | - | - | mod. 12 | 4.4 | - |
| hardening-scripts | cis benchmark, gpo, sysctl | - | - | mod. 6 | 3.0 | 5.3 |

### Module 09 - digital forensics

| lab | topic | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| disk-forensics | image acquisition, timeline, artifacts | - | - | mod. 8 | 4.4 | - |
| wireshark | display filters, stream reconstruction | ch. 4 | 2.1 | mod. 8 | 4.4 | 2.2 |

### Module 10 - cloud security

| lab | topic | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| aws | iam enum, s3 bucket attacks | - | - | mod. 19 | 2.2 | 3.10 |
| azure | entra id, rbac abuse | - | - | mod. 19 | 2.2 | 3.10 |
| gcp | service account abuse, cloud storage | - | - | mod. 19 | 2.2 | 3.10 |
| docker | image scanning, runtime security | - | - | - | 2.2 | 3.10 |
| kubernetes | pod escape, rbac review, kube-bench | - | - | - | 2.2 | 3.10 |
| iac-security | terraform scanning, secrets management | - | - | - | 2.2 | 5.3 |

---

## Legend

- **Ch. N**: PEN-200 (OSCP) syllabus chapter
- **N.N**: eJPTv2 (INE) syllabus section
- **Mod. N**: CEH v13 (EC-Council) syllabus module
- **N.N**: SY0-701 (Security+) domain/objective
- **N.N**: PT0-002 (PenTest+) domain/objective
- **-**: Topic not covered by that certification

---

## Gap analysis

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
