> [English](CERT_MAPPING.en.md) | **Italiano**

# Mappatura Certificazioni - Lab vs Syllabus

Questa tabella mappa ogni modulo della repository agli obiettivi delle principali certificazioni di cybersecurity. L'obiettivo e duplice: (1) dimostrare la copertura pratica del syllabus attraverso lab documentati, (2) identificare eventuali gap da colmare prima di sostenere l'esame.

---

## Copertura Stimata

| Certificazione | Ente | Copertura Lab | Note |
| :--- | :--- | :--- | :--- |
| **OSCP** (PEN-200) | OffSec | ~75% del syllabus | Mancano: Active Directory, client-side attacks |
| **eJPT** (v2) | INE Security | ~95% del syllabus | Copertura quasi completa |
| **CEH** (v13) | EC-Council | ~70% dei moduli | Mancano: mobile hacking, IoT, teoria pura |
| **Security+** (SY0-701) | CompTIA | ~60% dei domini | Focus pratico, manca governance/compliance |
| **PenTest+** (PT0-002) | CompTIA | ~80% dei domini | Manca: scoping/planning formale |

---

## Matrice Dettagliata

### Modulo 00 - Kali Setup

| Lab | Argomento | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 00-setup | Hardening piattaforma attacco, UFW, SSH | Ch. 2-4 | - | - | 3.0 | 5.3 |

### Modulo 01 - Reconnaissance

| Lab | Argomento | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| osint-passive | Google Dorking, theHarvester, Sherlock | Ch. 6 | 1.1 | Mod. 2 | 1.1 | 2.1 |
| google-dorks | Operatori di ricerca avanzati | Ch. 6 | 1.1 | Mod. 2 | - | 2.1 |
| breach-data | HIBP, DeHashed, correlazione credenziali | Ch. 6 | - | Mod. 2 | 1.1 | 2.1 |
| email-harvesting | Enumerazione indirizzi email, OSINT | Ch. 6 | 1.1 | Mod. 2 | - | 2.1 |
| user-enumeration | Username discovery, social media scraping | Ch. 6 | - | Mod. 2 | - | 2.1 |
| network-scanning | Nmap, host/port discovery, evasion | Ch. 7 | 1.2, 2.1 | Mod. 3 | 1.4 | 2.2 |
| live-host-discovery | ARP scan, ICMP sweep, SYN ping | Ch. 7 | 1.2 | Mod. 3 | - | 2.2 |
| port-scanning | SYN/TCP/UDP scan, timing, output | Ch. 7 | 1.2 | Mod. 3 | 4.1 | 2.2 |
| masscan | Scansione ad alta velocita, full-range | Ch. 7 | - | Mod. 3 | - | 2.2 |
| nmap-scripts | NSE vuln, SMB/HTTP enum | Ch. 7 | 2.1 | Mod. 3 | - | 2.2 |
| dns-enumeration | Zone transfer, subdomain brute | Ch. 7 | 1.2 | Mod. 4 | - | 2.2 |
| infrastructure-intel | Shodan, Censys, tech profiling | Ch. 6 | - | Mod. 2 | 1.1 | 2.1 |

### Modulo 02 - Vulnerability Assessment

| Lab | Argomento | OSCP | eJPT | CEH | Sec+ | PenTest+ |
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

### Modulo 03 - Web Attacks

| Lab | Argomento | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| burp-suite | Proxy, Repeater, Intruder, scope | Ch. 9 | 4.1 | Mod. 14 | - | 3.1 |
| owasp-zap | Spider, active scan, auth handling | Ch. 9 | 4.1 | Mod. 14 | - | 3.1 |
| dir-busting | Gobuster, ffuf, wordlist selection | Ch. 9 | 4.1 | Mod. 13 | - | 3.1 |
| sql-injection | UNION, blind, error-based, WAF bypass | Ch. 10 | 4.2 | Mod. 15 | 1.2 | 3.2 |
| sqlmap | Tamper scripts, dump, OS shell | Ch. 10 | 4.2 | Mod. 15 | - | 3.2 |
| xss | Reflected, Stored, DOM, filter bypass | Ch. 9 | 4.2 | Mod. 14 | 1.2 | 3.2 |
| ssti | Jinja2/Twig detection, sandbox escape, RCE | Ch. 9 | - | - | - | 3.2 |
| auth-attacks | Bruteforce web, session hijacking | Ch. 9 | 4.2 | Mod. 11 | 1.2 | 3.2 |
| jwt-tokens | None algo, key confusion, token forgery | Ch. 9 | - | - | - | 3.2 |
| graphql | Introspection, IDOR, batching, RCE | Ch. 9 | - | - | - | 3.2 |
| cms-specific | WordPress, Drupal, Joomla exploitation | Ch. 9 | 4.1 | Mod. 13 | - | 3.1 |
| secure-coding | Prepared statements, encoding, CSP | - | - | - | 1.2 | - |

### Modulo 04 - System Exploitation

| Lab | Argomento | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| empire | C2 fileless, PowerShell stager, LotL | Ch. 20 | 3.1 | Mod. 6 | 1.2 | 3.3 |
| metasploit | reverse_tcp, migration, SOCKS pivot | Ch. 20 | 3.1 | Mod. 6 | - | 3.3 |
| compiled-exploits | Cross-compilation, in-memory shellcode | Ch. 12-14 | - | Mod. 6 | - | 3.3 |
| searchsploit | Nmap XML correlation, exploit triage | Ch. 12 | 3.1 | Mod. 5 | - | 2.3 |
| linux-priv-esc | SUID, GTFOBins, LinPEAS, cronjob | Ch. 17 | 3.2 | Mod. 6 | - | 3.4 |
| windows-priv-esc | Token impersonation, WinPEAS, Sherlock | Ch. 16 | 3.2 | Mod. 6 | - | 3.4 |
| buffer-overflow | EIP control, bad chars, JMP ESP | Ch. 12-13 | - | Mod. 6 | - | 5.2 |
| pwntools | ROP chain, ASLR bypass, GOT leak | - | - | - | - | 5.2 |
| password-cracking | Hashcat mask/rules, John, wordlists | Ch. 15 | 3.1 | Mod. 20 | - | 3.5 |

### Modulo 05 - Social Engineering

| Lab | Argomento | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| phishing-campaigns | GoPhish, EvilGinx, PyPhisher | - | - | Mod. 9 | 1.1 | 3.6 |
| social-engineer-toolkit | SET vectors, credential harvester | Ch. 11 | - | Mod. 9 | 1.1 | 3.6 |
| payload-delivery | Macro, HTML smuggling, ISO/LNK | Ch. 11 | - | Mod. 9 | 1.2 | 3.3 |
| email-infrastructure | SPF/DKIM/DMARC, typosquatting | - | - | Mod. 9 | 1.1 | 3.6 |

### Modulo 06 - Wireless Security

| Lab | Argomento | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| wifi | Handshake capture, WPA cracking, rogue AP | - | - | Mod. 16 | 3.4 | 3.7 |
| bluetooth-ble | BLE recon, GATT enum, spoofing | - | - | - | - | - |
| sdr | Signal analysis, replay attacks | - | - | - | - | - |
| rfid-nfc | MIFARE cloning, Proxmark3 | - | - | - | 3.4 | 3.7 |

### Modulo 07 - Post-Exploitation

| Lab | Argomento | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| local-enumeration | Situational awareness Linux/Windows | Ch. 16-17 | 3.2 | Mod. 6 | - | 3.4 |
| mimikatz | sekurlsa, DCSync, golden ticket | Ch. 15 | - | Mod. 6 | - | 3.5 |
| la-zagne | Browser/WiFi/email credential recovery | Ch. 15 | - | Mod. 6 | - | 3.5 |
| persistence | Cron, registry, scheduled tasks, webshells | Ch. 16-17 | - | Mod. 6 | - | 3.4 |
| pivoting-tunneling | Chisel, Ligolo-ng, sshuttle, socat | Ch. 18-19 | 3.3 | Mod. 6 | - | 3.8 |
| exfiltration | Covert channels, log cleaning | - | - | Mod. 6 | - | 3.9 |

### Modulo 08 - Defense & Hardening

| Lab | Argomento | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| siem-log-analysis | Splunk, ELK Stack, log aggregation | - | - | Mod. 12 | 4.3 | 4.2 |
| wazuh | XDR deployment, active response, Suricata | - | - | Mod. 12 | 4.3 | 4.2 |
| honeypots | T-Pot, Canary Tokens, deception | - | - | Mod. 12 | 4.4 | - |
| hardening-scripts | CIS benchmark, GPO, sysctl | - | - | Mod. 6 | 3.0 | 5.3 |

### Modulo 09 - Digital Forensics

| Lab | Argomento | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| disk-forensics | Image acquisition, timeline, artifacts | - | - | Mod. 8 | 4.4 | - |
| wireshark | Display filters, stream reconstruction | Ch. 4 | 2.1 | Mod. 8 | 4.4 | 2.2 |

### Modulo 10 - Cloud Security

| Lab | Argomento | OSCP | eJPT | CEH | Sec+ | PenTest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| aws | IAM enum, S3 bucket attacks | - | - | Mod. 19 | 2.2 | 3.10 |
| azure | Entra ID, RBAC abuse | - | - | Mod. 19 | 2.2 | 3.10 |
| gcp | Service account abuse, Cloud Storage | - | - | Mod. 19 | 2.2 | 3.10 |
| docker | Image scanning, runtime security | - | - | - | 2.2 | 3.10 |
| kubernetes | Pod escape, RBAC review, kube-bench | - | - | - | 2.2 | 3.10 |
| iac-security | Terraform scanning, secrets management | - | - | - | 2.2 | 5.3 |

---

## Legenda

- **Ch. N**: Capitolo del syllabus PEN-200 (OSCP)
- **N.N**: Sezione del syllabus eJPTv2 (INE)
- **Mod. N**: Modulo del syllabus CEH v13 (EC-Council)
- **N.N**: Dominio/obiettivo del syllabus SY0-701 (Security+)
- **N.N**: Dominio/obiettivo del syllabus PT0-002 (PenTest+)
- **-**: Argomento non coperto da quella certificazione

---

## Gap Analysis

### Per OSCP (PEN-200)
- **Coperto:** Information Gathering, Vulnerability Scanning, Web Attacks, SQL Injection, Public Exploits, Password Attacks, Linux/Windows PrivEsc, Tunneling, Metasploit
- **Da integrare:** Active Directory Enumeration & Exploitation (Ch. 21), Client-Side Attacks avanzati (Ch. 11)

### Per eJPT (v2)
- **Coperto:** Assessment Methodologies, Host & Networking, Penetration Testing, Web Application Testing
- **Da integrare:** nessun gap significativo - la repo copre tutti e 4 i moduli

### Per CEH (v13)
- **Coperto:** Footprinting, Scanning, Enumeration, System Hacking, Social Engineering, Web Hacking, SQL Injection, Wireless, Cloud, Cryptography
- **Da integrare:** Mobile Platform Hacking (Mod. 17), IoT Hacking (Mod. 18)

---

> **Nota:** I riferimenti ai capitoli/moduli sono basati sui syllabus ufficiali 2024-2025. Verificare sempre la versione corrente sul sito dell'ente certificatore prima di pianificare lo studio.
