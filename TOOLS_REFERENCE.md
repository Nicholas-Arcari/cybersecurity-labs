> [English](TOOLS_REFERENCE.en.md) | **Italiano**

# Tools Reference - Indice Strumenti Utilizzati

> Riferimento rapido di tutti i tool utilizzati nei laboratori, con link diretto ai file
> che ne documentano l'uso pratico. Per ogni tool: categoria, versione, link ufficiale
> e tutti i README che lo impiegano.

---

## Indice

- [Reconnaissance](#reconnaissance)
- [Vulnerability Assessment](#vulnerability-assessment)
- [Web Application Testing](#web-application-testing)
- [System Exploitation](#system-exploitation)
- [Password Cracking](#password-cracking)
- [Binary Exploitation](#binary-exploitation)
- [Defensive Tools](#defensive-tools)
- [Target e Infrastruttura Lab](#target-e-infrastruttura-lab)
- [Script Personalizzati](#script-personalizzati)

---

## Reconnaissance

| Tool | Descrizione | Usato in |
| :--- | :--- | :--- |
| **Nmap** | Port scanner e service/OS fingerprinting - standard de facto per la network recon | [nmap-scripts](<01-recon (Red Team Basic)/02-network-scanning-active/port-scanning (Nmap)/nmap-scripts/README.md>), [live-host-discovery](<01-recon (Red Team Basic)/02-network-scanning-active/live-host-discovery/README.md>), [nmap-nse-vuln](<02-vulnerability-assessment/01-general-scanners (Infrastructure)/nmap-nse-vuln/README.md>) |
| **Masscan** | Port scanner asincrono ad alta velocita (100k+ pkt/s) | [masscan](<01-recon (Red Team Basic)/02-network-scanning-active/port-scanning (Nmap)/masscan/README.md>) |
| **TheHarvester** | OSINT harvester per email, sottodomini, IP da fonti pubbliche | [email-harvesting](<01-recon (Red Team Basic)/01-osint-passive (Open Source Intelligence)/email-harvesting/README.md>) |
| **Sherlock** | Username enumeration su 400+ social network | [user-enumeration](<01-recon (Red Team Basic)/01-osint-passive (Open Source Intelligence)/user-enumeration/README.md>) |
| **Google Dorks** | Operatori avanzati di ricerca per information disclosure | [google-dorks](<01-recon (Red Team Basic)/01-osint-passive (Open Source Intelligence)/google-dorks/README.md>) |
| **dnsrecon** | DNS enumeration: zone transfer, brute force, record lookup | [dns-recon](<01-recon (Red Team Basic)/03-dns-enumeration/dns-recon/README.md>) |
| **Subfinder** | Subdomain discovery passivo via API (ProjectDiscovery) | [subdomain-finding](<01-recon (Red Team Basic)/03-dns-enumeration/subdomain-finding/README.md>) |
| **Shodan** | Motore di ricerca per dispositivi esposti su Internet | [shodan-censys](<01-recon (Red Team Basic)/04-infrastructure-intel/shodan-censys/README.md>) |
| **Censys** | Intelligence su certificati e host esposti | [shodan-censys](<01-recon (Red Team Basic)/04-infrastructure-intel/shodan-censys/README.md>) |
| **Wappalyzer / WhatWeb** | Fingerprinting dello stack tecnologico web | [tech-stack](<01-recon (Red Team Basic)/04-infrastructure-intel/tech-stack/README.md>), [tech-profiler](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/tech-profiler/README.md>) |

---

## Vulnerability Assessment

| Tool | Descrizione | Usato in |
| :--- | :--- | :--- |
| **Nessus** | Vulnerability scanner commerciale (Tenable) - credentialed scan | [nessus](<02-vulnerability-assessment/01-general-scanners (Infrastructure)/nessus/README.md>) |
| **OpenVAS / GVM** | Vulnerability scanner open-source (Greenbone) | [open-vas-gvm](<02-vulnerability-assessment/01-general-scanners (Infrastructure)/open-vas-gvm/README.md>), [perform-vulnerability-scans](<00-setup-after-installing-kali/11-perform-vulnerability-scans/README.md>) |
| **Nmap NSE (vuln)** | Script NSE per vulnerability detection (smb-vuln-*, ssl-*) | [nmap-nse-vuln](<02-vulnerability-assessment/01-general-scanners (Infrastructure)/nmap-nse-vuln/README.md>) |
| **enum4linux / enum4linux-ng** | Enumerazione SMB/NetBIOS: share, utenti, policy password | [smb-net-bios](<02-vulnerability-assessment/02-protocol-specific-audit/smb-net-bios/README.md>) |
| **nbtscan** | NetBIOS name discovery su segmenti di rete | [smb-net-bios](<02-vulnerability-assessment/02-protocol-specific-audit/smb-net-bios/README.md>) |
| **testssl.sh** | Audit SSL/TLS: cipher, protocolli, certificati, vulnerabilita | [ssl-tls](<02-vulnerability-assessment/02-protocol-specific-audit/ssl-tls/README.md>) |
| **searchsploit** | Ricerca offline nel database Exploit-DB | [searchsploit-manual-lookup](<02-vulnerability-assessment/03-cve-analysis (Research)/searchsploit-manual-lookup/README.md>), [searchsploit](<04-system-exploitation/02-exploit-database/searchsploit/README.md>) |
| **CVSS Calculator** | Calcolo score CVSS v3.1 per classificare le vulnerabilita | [cvss-calculator](<02-vulnerability-assessment/03-cve-analysis (Research)/cvss-calculator/README.md>) |
| **smtp-user-enum** | Enumerazione utenti SMTP (VRFY/EXPN/RCPT) | [smtp](<02-vulnerability-assessment/02-protocol-specific-audit/smtp/README.md>) |
| **snmpwalk / onesixtyone** | Enumerazione SNMP community string e OID tree | [snmp](<02-vulnerability-assessment/02-protocol-specific-audit/snmp/README.md>) |

---

## Web Application Testing

| Tool | Descrizione | Usato in |
| :--- | :--- | :--- |
| **Burp Suite** | Proxy intercettante per web application testing (PortSwigger) | [burp-suite](<03-web-attacks (Red Team + Secure Coding)/01-proxy-tools (Intercept)/burp-suite/README.md>) |
| **OWASP ZAP** | Proxy open-source + scanner automatizzato (OWASP) | [owasp-zap](<03-web-attacks (Red Team + Secure Coding)/01-proxy-tools (Intercept)/owasp-zap/README.md>) |
| **Gobuster** | Directory/file brute forcing (Go, veloce) | [dir-busting](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/dir-busting/README.md>) |
| **Feroxbuster** | Content discovery ricorsivo (Rust, moderno) | [dir-busting](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/dir-busting/README.md>) |
| **Nikto** | Web server scanner legacy (misconfig, file pericolosi) | [vulnerability-scanners](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/vulnerability-scanners/README.md>) |
| **Nuclei** | Template-based vulnerability scanner (ProjectDiscovery) | [vulnerability-scanners](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/vulnerability-scanners/README.md>) |
| **sqlmap** | SQL Injection automatizzata - detection, exploitation, dump | [sql-map-data](<03-web-attacks (Red Team + Secure Coding)/03-owasp (Attacks)/sql-injection (SQLi)/sql-map-data/README.md>) |
| **Hydra** | Brute force multi-protocollo (HTTP, SSH, FTP, RDP, SMB...) | [bruteforce-web](<03-web-attacks (Red Team + Secure Coding)/03-owasp (Attacks)/auth-attacks/bruteforce-web/README.md>) |
| **WPScan** | Scanner specializzato WordPress (vuln, plugin, utenti) | [wordpress](<03-web-attacks (Red Team + Secure Coding)/04-cms-specific/wordpress/README.md>) |
| **JoomScan** | Scanner specializzato Joomla | [joomla](<03-web-attacks (Red Team + Secure Coding)/04-cms-specific/joomla/README.md>) |
| **Droopescan** | Scanner multi-CMS (Drupal, Joomla, WordPress, SilverStripe) | [drupal](<03-web-attacks (Red Team + Secure Coding)/04-cms-specific/drupal/README.md>) |
| **PyJWT** | Libreria Python per forging/cracking JWT token | [jwt-tokens](<03-web-attacks (Red Team + Secure Coding)/05-api-security/jwt-tokens/README.md>) |
| **Postman / curl** | Testing manuale API REST + IDOR/BOLA exploitation | [postman](<03-web-attacks (Red Team + Secure Coding)/05-api-security/postman/README.md>) |
| **GraphQL Voyager / InQL** | Introspection e analisi schema GraphQL | [graphql](<03-web-attacks (Red Team + Secure Coding)/05-api-security/graphql/README.md>) |
| **Subfinder** | Subdomain enumeration passivo per web recon | [subdomain-enum](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/subdomain-enum/README.md>) |

---

## System Exploitation

| Tool | Descrizione | Usato in |
| :--- | :--- | :--- |
| **Metasploit Framework** | Framework di exploitation modulare (Rapid7) | [metasploit](<04-system-exploitation/01-frameworks/metasploit/README.md>) |
| **msfvenom** | Generatore payload Metasploit (reverse shell, staged, encoded) | [metasploit](<04-system-exploitation/01-frameworks/metasploit/README.md>), [compiled-exploits](<04-system-exploitation/02-exploit-database/compiled-exploits/README.md>) |
| **PowerShell Empire** | C2 framework post-exploitation (fileless, in-memory) | [empire](<04-system-exploitation/01-frameworks/empire/README.md>) |
| **MinGW-w64** | Cross-compilazione C/C++ per target Windows da Linux | [compiled-exploits](<04-system-exploitation/02-exploit-database/compiled-exploits/README.md>) |
| **PrintSpoofer** | Privilege escalation via SeImpersonatePrivilege (Win10+) | [juicypotato-printnightmare](<04-system-exploitation/03-privilege-escalation (PrivEsc)/windows-priv-esc/juicypotato-printnightmare/README.md>) |
| **WinPEAS** | Windows Privilege Escalation enumeration automatizzata | [winpeas](<04-system-exploitation/03-privilege-escalation (PrivEsc)/windows-priv-esc/winpeas/README.md>) |
| **LinPEAS** | Linux Privilege Escalation enumeration automatizzata | [linpeas](<04-system-exploitation/03-privilege-escalation (PrivEsc)/linux-priv-esc/linpeas/README.md>) |
| **GTFOBins** | Database di binari Unix sfruttabili per PrivEsc (sudo, SUID) | [gtfo-bins-notes](<04-system-exploitation/03-privilege-escalation (PrivEsc)/linux-priv-esc/gtfo-bins-notes/README.md>) |
| **Sherlock.ps1** | Kernel patch audit per Windows (MS10-015, MS16-032...) | [sherlock](<04-system-exploitation/03-privilege-escalation (PrivEsc)/windows-priv-esc/sherlock/README.md>) |

---

## Password Cracking

| Tool | Descrizione | Usato in |
| :--- | :--- | :--- |
| **Hashcat** | GPU-accelerated password cracking (NTLM, bcrypt, SHA...) | [hashcat](<04-system-exploitation/05-password-cracking/hashcat/README.md>) |
| **John the Ripper** | Password cracker CPU-based + utility di estrazione hash | [john-the-ripper](<04-system-exploitation/05-password-cracking/john-the-ripper/README.md>) |
| **zip2john / unshadow** | Estrazione hash da archivi ZIP e /etc/shadow | [john-the-ripper](<04-system-exploitation/05-password-cracking/john-the-ripper/README.md>) |
| **RockYou / SecLists** | Wordlist standard per dictionary attack | [wordlists](<04-system-exploitation/05-password-cracking/wordlists/README.md>) |

---

## Binary Exploitation

| Tool | Descrizione | Usato in |
| :--- | :--- | :--- |
| **pwntools** | Framework Python per exploit development (ROP, shellcode) | [pwntools-scripts](<04-system-exploitation/04-binary-exploitation/pwntools-scripts/README.md>) |
| **GDB + PEDA/GEF** | Debugger con estensioni per exploit development | [buffer-overflow-prep](<04-system-exploitation/04-binary-exploitation/buffer-overflow-prep/README.md>) |
| **checksec** | Verifica protezioni binarie (NX, ASLR, PIE, canary) | [buffer-overflow-prep](<04-system-exploitation/04-binary-exploitation/buffer-overflow-prep/README.md>) |
| **ROPgadget** | Ricerca gadget ROP in binari ELF/PE | [pwntools-scripts](<04-system-exploitation/04-binary-exploitation/pwntools-scripts/README.md>) |

---

## Defensive Tools

| Tool | Descrizione | Usato in |
| :--- | :--- | :--- |
| **UFW** | Firewall frontend per iptables (Uncomplicated Firewall) | [enable-firewall](<00-setup-after-installing-kali/04-enable-firewall/README.md>) |
| **SSH (sshd_config)** | Hardening SSH: disabilita root login, key-only auth | [secure-ssh-access](<00-setup-after-installing-kali/06-secure-ssh-access/README.md>) |
| **sysctl** | Kernel hardening: ASLR, SYN cookies, IP forwarding | [harden-the-kernel](<00-setup-after-installing-kali/13-harden-the-kernel/README.md>) |
| **Suricata** | IDS/IPS rule-based per traffic inspection | [configure-intrusion-detection](<00-setup-after-installing-kali/14-configure-intrusion-detection-systems/README.md>) |
| **Logwatch** | Log aggregation e reporting giornaliero | [setup-logwatch](<00-setup-after-installing-kali/20-setup-logwatch-system-monitoring/README.md>) |
| **LUKS / VeraCrypt** | Full disk encryption e volumi cifrati | [encrypt-sensitive-data](<00-setup-after-installing-kali/10-encrypt-sensitive-data/README.md>) |
| **rsync** | Backup incrementale di sistema | [backup-your-system](<00-setup-after-installing-kali/19-backup-your-system/README.md>) |

---

## Target e Infrastruttura Lab

| Tool | Descrizione | Usato in |
| :--- | :--- | :--- |
| **DVWA** | Damn Vulnerable Web Application - target web per SQLi, XSS, CSRF | [docker-compose.yml](docker-compose.yml), [sql-injection](<03-web-attacks (Red Team + Secure Coding)/03-owasp (Attacks)/sql-injection (SQLi)/README.md>) |
| **DVGA** | Damn Vulnerable GraphQL Application - target API GraphQL | [docker-compose.yml](docker-compose.yml), [graphql](<03-web-attacks (Red Team + Secure Coding)/05-api-security/graphql/README.md>) |
| **Juice Shop** | OWASP Juice Shop - 100+ challenge OWASP Top 10 | [docker-compose.yml](docker-compose.yml) |
| **VirtualBox** | Hypervisor per le VM di laboratorio | [LAB_SETUP.md](LAB_SETUP.md), [lab-setup.sh](scripts/lab-setup.sh) |
| **Docker Compose** | Orchestrazione container per web target | [docker-compose.yml](docker-compose.yml), [LAB_SETUP.md](LAB_SETUP.md) |
| **Asciinema** | Registrazione sessioni terminale per demo | [LAB_SETUP.md](LAB_SETUP.md) |

---

## Script Personalizzati

| Script | Descrizione | Percorso |
| :--- | :--- | :--- |
| **nessus_parser.py** | Parser XML Nessus con filtro severity, statistiche e export CSV | [02-vulnerability-assessment/code/](02-vulnerability-assessment/code/nessus_parser.py) |
| **header_security_check.py** | Analisi security header HTTP con score e suggerimenti fix | [03-web-attacks/code/](<03-web-attacks (Red Team + Secure Coding)/code/header_security_check.py>) |
| **hash_identifier.py** | Identificatore tipo hash con suggerimenti hashcat/john mode | [04-system-exploitation/code/](04-system-exploitation/05-password-cracking/code/hash_identifier.py) |
| **lab-setup.sh** | Automazione setup VM VirtualBox (create, network, snapshot) | [scripts/](scripts/lab-setup.sh) |
| **check-finding-ids.sh** | Validazione Finding ID (formato, univocita, sequenzialita) | [scripts/](scripts/check-finding-ids.sh) |

---

## Statistiche

| Categoria | Tool | File che li documentano |
| :--- | :---: | :---: |
| Reconnaissance | 10 | 12 |
| Vulnerability Assessment | 10 | 11 |
| Web Application Testing | 15 | 16 |
| System Exploitation | 9 | 9 |
| Password Cracking | 4 | 4 |
| Binary Exploitation | 4 | 4 |
| Defensive Tools | 7 | 7 |
| Target/Infrastruttura | 6 | 8 |
| Script personalizzati | 5 | 5 |
| **Totale** | **70** | **76** |

---

> *Versioni e compatibilita: i tool elencati sono stati testati su Kali Linux 2024.x.
> Quando disponibili alternative moderne (es. NetExec al posto di CrackMapExec), sono
> state indicate nei rispettivi README di modulo.*
