> [English](CERT_MAPPING.en.md) | **Italiano**

# Mappatura certificazioni - lab vs syllabus

Questa tabella mappa ogni modulo della repository agli obiettivi delle principali certificazioni di cybersecurity. L'obiettivo e duplice: (1) dimostrare la copertura pratica del syllabus attraverso lab documentati, (2) identificare eventuali gap da colmare prima di sostenere l'esame.

---

## Copertura stimata

| certificazione | ente | copertura lab | note |
| :--- | :--- | :--- | :--- |
| **oscp** (pen-200) | offsec | ~75% del syllabus | mancano: active directory, client-side attacks |
| **ejpt** (v2) | ine security | ~95% del syllabus | copertura quasi completa |
| **ceh** (v13) | ec-council | ~70% dei moduli | mancano: mobile hacking, iot, teoria pura |
| **security+** (sy0-701) | comptia | ~60% dei domini | focus pratico, manca governance/compliance |
| **pentest+** (pt0-002) | comptia | ~80% dei domini | manca: scoping/planning formale |

---

## Matrice dettagliata

### Modulo 00 - Kali setup

| lab | argomento | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 00-setup | hardening piattaforma attacco, ufw, ssh | ch. 2-4 | - | - | 3.0 | 5.3 |

### Modulo 01 - reconnaissance

| lab | argomento | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| osint-passive | google dorking, theharvester, sherlock | ch. 6 | 1.1 | mod. 2 | 1.1 | 2.1 |
| google-dorks | operatori di ricerca avanzati | ch. 6 | 1.1 | mod. 2 | - | 2.1 |
| breach-data | hibp, dehashed, correlazione credenziali | ch. 6 | - | mod. 2 | 1.1 | 2.1 |
| email-harvesting | enumerazione indirizzi email, osint | ch. 6 | 1.1 | mod. 2 | - | 2.1 |
| user-enumeration | username discovery, social media scraping | ch. 6 | - | mod. 2 | - | 2.1 |
| network-scanning | nmap, host/port discovery, evasion | ch. 7 | 1.2, 2.1 | mod. 3 | 1.4 | 2.2 |
| live-host-discovery | arp scan, icmp sweep, syn ping | ch. 7 | 1.2 | mod. 3 | - | 2.2 |
| port-scanning | syn/tcp/udp scan, timing, output | ch. 7 | 1.2 | mod. 3 | 4.1 | 2.2 |
| masscan | scansione ad alta velocita, full-range | ch. 7 | - | mod. 3 | - | 2.2 |
| nmap-scripts | nse vuln, smb/http enum | ch. 7 | 2.1 | mod. 3 | - | 2.2 |
| dns-enumeration | zone transfer, subdomain brute | ch. 7 | 1.2 | mod. 4 | - | 2.2 |
| infrastructure-intel | shodan, censys, tech profiling | ch. 6 | - | mod. 2 | 1.1 | 2.1 |

### Modulo 02 - vulnerability assessment

| lab | argomento | oscp | ejpt | ceh | sec+ | pentest+ |
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

### Modulo 03 - web attacks

| lab | argomento | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| burp-suite | proxy, repeater, intruder, scope | ch. 9 | 4.1 | mod. 14 | - | 3.1 |
| owasp-zap | spider, active scan, auth handling | ch. 9 | 4.1 | mod. 14 | - | 3.1 |
| dir-busting | gobuster, ffuf, wordlist selection | ch. 9 | 4.1 | mod. 13 | - | 3.1 |
| sql-injection | union, blind, error-based, waf bypass | ch. 10 | 4.2 | mod. 15 | 1.2 | 3.2 |
| sqlmap | tamper scripts, dump, os shell | ch. 10 | 4.2 | mod. 15 | - | 3.2 |
| xss | reflected, stored, dom, filter bypass | ch. 9 | 4.2 | mod. 14 | 1.2 | 3.2 |
| ssti | jinja2/twig detection, sandbox escape, rce | ch. 9 | - | - | - | 3.2 |
| auth-attacks | bruteforce web, session hijacking | ch. 9 | 4.2 | mod. 11 | 1.2 | 3.2 |
| jwt-tokens | none algo, key confusion, token forgery | ch. 9 | - | - | - | 3.2 |
| graphql | introspection, idor, batching, rce | ch. 9 | - | - | - | 3.2 |
| cms-specific | wordpress, drupal, joomla exploitation | ch. 9 | 4.1 | mod. 13 | - | 3.1 |
| secure-coding | prepared statements, encoding, csp | - | - | - | 1.2 | - |

### Modulo 04 - system exploitation

| lab | argomento | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| empire | c2 fileless, powershell stager, lotl | ch. 20 | 3.1 | mod. 6 | 1.2 | 3.3 |
| metasploit | reverse_tcp, migration, socks pivot | ch. 20 | 3.1 | mod. 6 | - | 3.3 |
| compiled-exploits | cross-compilation, in-memory shellcode | ch. 12-14 | - | mod. 6 | - | 3.3 |
| searchsploit | nmap xml correlation, exploit triage | ch. 12 | 3.1 | mod. 5 | - | 2.3 |
| linux-priv-esc | suid, gtfobins, linpeas, cronjob | ch. 17 | 3.2 | mod. 6 | - | 3.4 |
| windows-priv-esc | token impersonation, winpeas, sherlock | ch. 16 | 3.2 | mod. 6 | - | 3.4 |
| buffer-overflow | eip control, bad chars, jmp esp | ch. 12-13 | - | mod. 6 | - | 5.2 |
| pwntools | rop chain, aslr bypass, got leak | - | - | - | - | 5.2 |
| password-cracking | hashcat mask/rules, john, wordlists | ch. 15 | 3.1 | mod. 20 | - | 3.5 |

### Modulo 05 - social engineering

| lab | argomento | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| phishing-campaigns | gophish, evilginx, pyphisher | - | - | mod. 9 | 1.1 | 3.6 |
| social-engineer-toolkit | set vectors, credential harvester | ch. 11 | - | mod. 9 | 1.1 | 3.6 |
| payload-delivery | macro, html smuggling, iso/lnk | ch. 11 | - | mod. 9 | 1.2 | 3.3 |
| email-infrastructure | spf/dkim/dmarc, typosquatting | - | - | mod. 9 | 1.1 | 3.6 |

### Modulo 06 - wireless security

| lab | argomento | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| wifi | handshake capture, wpa cracking, rogue ap | - | - | mod. 16 | 3.4 | 3.7 |
| bluetooth-ble | ble recon, gatt enum, spoofing | - | - | - | - | - |
| sdr | signal analysis, replay attacks | - | - | - | - | - |
| rfid-nfc | mifare cloning, proxmark3 | - | - | - | 3.4 | 3.7 |

### Modulo 07 - Post-Exploitation

| lab | argomento | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| local-enumeration | situational awareness linux/windows | ch. 16-17 | 3.2 | mod. 6 | - | 3.4 |
| mimikatz | sekurlsa, dcsync, golden ticket | ch. 15 | - | mod. 6 | - | 3.5 |
| la-zagne | browser/wifi/email credential recovery | ch. 15 | - | mod. 6 | - | 3.5 |
| persistence | cron, registry, scheduled tasks, webshells | ch. 16-17 | - | mod. 6 | - | 3.4 |
| pivoting-tunneling | chisel, ligolo-ng, sshuttle, socat | ch. 18-19 | 3.3 | mod. 6 | - | 3.8 |
| exfiltration | covert channels, log cleaning | - | - | mod. 6 | - | 3.9 |

### Modulo 08 - defense & hardening

| lab | argomento | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| siem-log-analysis | splunk, elk stack, log aggregation | - | - | mod. 12 | 4.3 | 4.2 |
| wazuh | xdr deployment, active response, suricata | - | - | mod. 12 | 4.3 | 4.2 |
| honeypots | t-pot, canary tokens, deception | - | - | mod. 12 | 4.4 | - |
| hardening-scripts | cis benchmark, gpo, sysctl | - | - | mod. 6 | 3.0 | 5.3 |

### Modulo 09 - digital forensics

| lab | argomento | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| disk-forensics | image acquisition, timeline, artifacts | - | - | mod. 8 | 4.4 | - |
| wireshark | display filters, stream reconstruction | ch. 4 | 2.1 | mod. 8 | 4.4 | 2.2 |

### Modulo 10 - cloud security

| lab | argomento | oscp | ejpt | ceh | sec+ | pentest+ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| aws | iam enum, s3 bucket attacks | - | - | mod. 19 | 2.2 | 3.10 |
| azure | entra id, rbac abuse | - | - | mod. 19 | 2.2 | 3.10 |
| gcp | service account abuse, cloud storage | - | - | mod. 19 | 2.2 | 3.10 |
| docker | image scanning, runtime security | - | - | - | 2.2 | 3.10 |
| kubernetes | pod escape, rbac review, kube-bench | - | - | - | 2.2 | 3.10 |
| iac-security | terraform scanning, secrets management | - | - | - | 2.2 | 5.3 |

---

## Legenda

- **Ch. N**: Capitolo del syllabus PEN-200 (OSCP)
- **N.N**: Sezione del syllabus eJPTv2 (INE)
- **Mod. N**: Modulo del syllabus CEH v13 (EC-Council)
- **N.N**: Dominio/obiettivo del syllabus SY0-701 (Security+)
- **N.N**: Dominio/obiettivo del syllabus PT0-002 (PenTest+)
- **-**: Argomento non coperto da quella certificazione

---

## Gap analysis

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
