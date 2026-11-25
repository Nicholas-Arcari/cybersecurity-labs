> [English](TOOLS_REFERENCE.en.md) | **Italiano**

# Tools reference - indice strumenti utilizzati

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

| tool | descrizione | usato in |
| :--- | :--- | :--- |
| **nmap** | port scanner e service/os fingerprinting - standard de facto per la network recon | [nmap-scripts](<01-recon (Red Team Basic)/02-network-scanning-active/port-scanning (Nmap)/nmap-scripts/README.md>), [live-host-discovery](<01-recon (Red Team Basic)/02-network-scanning-active/live-host-discovery/README.md>), [nmap-nse-vuln](<02-vulnerability-assessment/01-general-scanners (Infrastructure)/nmap-nse-vuln/README.md>) |
| **masscan** | port scanner asincrono ad alta velocita (100k+ pkt/s) | [masscan](<01-recon (Red Team Basic)/02-network-scanning-active/port-scanning (Nmap)/masscan/README.md>) |
| **theharvester** | osint harvester per email, sottodomini, ip da fonti pubbliche | [email-harvesting](<01-recon (Red Team Basic)/01-osint-passive (Open Source Intelligence)/email-harvesting/README.md>) |
| **sherlock** | username enumeration su 400+ social network | [user-enumeration](<01-recon (Red Team Basic)/01-osint-passive (Open Source Intelligence)/user-enumeration/README.md>) |
| **google dorks** | operatori avanzati di ricerca per information disclosure | [google-dorks](<01-recon (Red Team Basic)/01-osint-passive (Open Source Intelligence)/google-dorks/README.md>) |
| **dnsrecon** | dns enumeration: zone transfer, brute force, record lookup | [dns-recon](<01-recon (Red Team Basic)/03-dns-enumeration/dns-recon/README.md>) |
| **subfinder** | subdomain discovery passivo via api (projectdiscovery) | [subdomain-finding](<01-recon (Red Team Basic)/03-dns-enumeration/subdomain-finding/README.md>) |
| **shodan** | motore di ricerca per dispositivi esposti su internet | [shodan-censys](<01-recon (Red Team Basic)/04-infrastructure-intel/shodan-censys/README.md>) |
| **censys** | intelligence su certificati e host esposti | [shodan-censys](<01-recon (Red Team Basic)/04-infrastructure-intel/shodan-censys/README.md>) |
| **wappalyzer / whatweb** | fingerprinting dello stack tecnologico web | [tech-stack](<01-recon (Red Team Basic)/04-infrastructure-intel/tech-stack/README.md>), [tech-profiler](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/tech-profiler/README.md>) |

---

## Vulnerability assessment

| tool | descrizione | usato in |
| :--- | :--- | :--- |
| **nessus** | vulnerability scanner commerciale (tenable) - credentialed scan | [nessus](<02-vulnerability-assessment/01-general-scanners (Infrastructure)/nessus/README.md>) |
| **openvas / gvm** | vulnerability scanner open-source (greenbone) | [open-vas-gvm](<02-vulnerability-assessment/01-general-scanners (Infrastructure)/open-vas-gvm/README.md>), [perform-vulnerability-scans](<00-setup-after-installing-kali/11-perform-vulnerability-scans/README.md>) |
| **nmap nse (vuln)** | script nse per vulnerability detection (smb-vuln-*, ssl-*) | [nmap-nse-vuln](<02-vulnerability-assessment/01-general-scanners (Infrastructure)/nmap-nse-vuln/README.md>) |
| **enum4linux / enum4linux-ng** | enumerazione smb/netbios: share, utenti, policy password | [smb-net-bios](<02-vulnerability-assessment/02-protocol-specific-audit/smb-net-bios/README.md>) |
| **nbtscan** | netbios name discovery su segmenti di rete | [smb-net-bios](<02-vulnerability-assessment/02-protocol-specific-audit/smb-net-bios/README.md>) |
| **testssl.sh** | audit ssl/tls: cipher, protocolli, certificati, vulnerabilita | [ssl-tls](<02-vulnerability-assessment/02-protocol-specific-audit/ssl-tls/README.md>) |
| **searchsploit** | ricerca offline nel database exploit-db | [searchsploit-manual-lookup](<02-vulnerability-assessment/03-cve-analysis (Research)/searchsploit-manual-lookup/README.md>), [searchsploit](<04-system-exploitation/02-exploit-database/searchsploit/README.md>) |
| **cvss calculator** | calcolo score cvss v3.1 per classificare le vulnerabilita | [cvss-calculator](<02-vulnerability-assessment/03-cve-analysis (Research)/cvss-calculator/README.md>) |
| **smtp-user-enum** | enumerazione utenti smtp (vrfy/expn/rcpt) | [smtp](<02-vulnerability-assessment/02-protocol-specific-audit/smtp/README.md>) |
| **snmpwalk / onesixtyone** | enumerazione snmp community string e oid tree | [snmp](<02-vulnerability-assessment/02-protocol-specific-audit/snmp/README.md>) |

---

## Web application testing

| tool | descrizione | usato in |
| :--- | :--- | :--- |
| **burp suite** | proxy intercettante per web application testing (portswigger) | [burp-suite](<03-web-attacks (Red Team + Secure Coding)/01-proxy-tools (Intercept)/burp-suite/README.md>) |
| **owasp zap** | proxy open-source + scanner automatizzato (owasp) | [owasp-zap](<03-web-attacks (Red Team + Secure Coding)/01-proxy-tools (Intercept)/owasp-zap/README.md>) |
| **gobuster** | directory/file brute forcing (go, veloce) | [dir-busting](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/dir-busting/README.md>) |
| **feroxbuster** | content discovery ricorsivo (rust, moderno) | [dir-busting](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/dir-busting/README.md>) |
| **nikto** | web server scanner legacy (misconfig, file pericolosi) | [vulnerability-scanners](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/vulnerability-scanners/README.md>) |
| **nuclei** | template-based vulnerability scanner (projectdiscovery) | [vulnerability-scanners](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/vulnerability-scanners/README.md>) |
| **sqlmap** | sql injection automatizzata - detection, exploitation, dump | [sql-map-data](<03-web-attacks (Red Team + Secure Coding)/03-owasp (Attacks)/sql-injection (SQLi)/sql-map-data/README.md>) |
| **hydra** | brute force multi-protocollo (http, ssh, ftp, rdp, smb...) | [bruteforce-web](<03-web-attacks (Red Team + Secure Coding)/03-owasp (Attacks)/auth-attacks/bruteforce-web/README.md>) |
| **wpscan** | scanner specializzato wordpress (vuln, plugin, utenti) | [wordpress](<03-web-attacks (Red Team + Secure Coding)/04-cms-specific/wordpress/README.md>) |
| **joomscan** | scanner specializzato joomla | [joomla](<03-web-attacks (Red Team + Secure Coding)/04-cms-specific/joomla/README.md>) |
| **droopescan** | scanner multi-cms (drupal, joomla, wordpress, silverstripe) | [drupal](<03-web-attacks (Red Team + Secure Coding)/04-cms-specific/drupal/README.md>) |
| **pyjwt** | libreria python per forging/cracking jwt token | [jwt-tokens](<03-web-attacks (Red Team + Secure Coding)/05-api-security/jwt-tokens/README.md>) |
| **postman / curl** | testing manuale api rest + idor/bola exploitation | [postman](<03-web-attacks (Red Team + Secure Coding)/05-api-security/postman/README.md>) |
| **graphql voyager / inql** | introspection e analisi schema graphql | [graphql](<03-web-attacks (Red Team + Secure Coding)/05-api-security/graphql/README.md>) |
| **subfinder** | subdomain enumeration passivo per web recon | [subdomain-enum](<03-web-attacks (Red Team + Secure Coding)/02-web-recon (Enumeration)/subdomain-enum/README.md>) |

---

## System exploitation

| tool | descrizione | usato in |
| :--- | :--- | :--- |
| **metasploit framework** | framework di exploitation modulare (rapid7) | [metasploit](<04-system-exploitation/01-frameworks/metasploit/README.md>) |
| **msfvenom** | generatore payload metasploit (reverse shell, staged, encoded) | [metasploit](<04-system-exploitation/01-frameworks/metasploit/README.md>), [compiled-exploits](<04-system-exploitation/02-exploit-database/compiled-exploits/README.md>) |
| **powershell empire** | c2 framework post-exploitation (fileless, in-memory) | [empire](<04-system-exploitation/01-frameworks/empire/README.md>) |
| **mingw-w64** | cross-compilazione c/c++ per target windows da linux | [compiled-exploits](<04-system-exploitation/02-exploit-database/compiled-exploits/README.md>) |
| **printspoofer** | privilege escalation via seimpersonateprivilege (win10+) | [juicypotato-printnightmare](<04-system-exploitation/03-privilege-escalation (PrivEsc)/windows-priv-esc/juicypotato-printnightmare/README.md>) |
| **winpeas** | windows privilege escalation enumeration automatizzata | [winpeas](<04-system-exploitation/03-privilege-escalation (PrivEsc)/windows-priv-esc/winpeas/README.md>) |
| **linpeas** | linux privilege escalation enumeration automatizzata | [linpeas](<04-system-exploitation/03-privilege-escalation (PrivEsc)/linux-priv-esc/linpeas/README.md>) |
| **gtfobins** | database di binari unix sfruttabili per privesc (sudo, suid) | [gtfo-bins-notes](<04-system-exploitation/03-privilege-escalation (PrivEsc)/linux-priv-esc/gtfo-bins-notes/README.md>) |
| **sherlock.ps1** | kernel patch audit per windows (ms10-015, ms16-032...) | [sherlock](<04-system-exploitation/03-privilege-escalation (PrivEsc)/windows-priv-esc/sherlock/README.md>) |

---

## Password cracking

| tool | descrizione | usato in |
| :--- | :--- | :--- |
| **hashcat** | gpu-accelerated password cracking (ntlm, bcrypt, sha...) | [hashcat](<04-system-exploitation/05-password-cracking/hashcat/README.md>) |
| **john the ripper** | password cracker cpu-based + utility di estrazione hash | [john-the-ripper](<04-system-exploitation/05-password-cracking/john-the-ripper/README.md>) |
| **zip2john / unshadow** | estrazione hash da archivi zip e /etc/shadow | [john-the-ripper](<04-system-exploitation/05-password-cracking/john-the-ripper/README.md>) |
| **rockyou / seclists** | wordlist standard per dictionary attack | [wordlists](<04-system-exploitation/05-password-cracking/wordlists/README.md>) |

---

## Binary exploitation

| tool | descrizione | usato in |
| :--- | :--- | :--- |
| **pwntools** | framework python per exploit development (rop, shellcode) | [pwntools-scripts](<04-system-exploitation/04-binary-exploitation/pwntools-scripts/README.md>) |
| **gdb + peda/gef** | debugger con estensioni per exploit development | [buffer-overflow-prep](<04-system-exploitation/04-binary-exploitation/buffer-overflow-prep/README.md>) |
| **checksec** | verifica protezioni binarie (nx, aslr, pie, canary) | [buffer-overflow-prep](<04-system-exploitation/04-binary-exploitation/buffer-overflow-prep/README.md>) |
| **ropgadget** | ricerca gadget rop in binari elf/pe | [pwntools-scripts](<04-system-exploitation/04-binary-exploitation/pwntools-scripts/README.md>) |

---

## Defensive tools

| tool | descrizione | usato in |
| :--- | :--- | :--- |
| **ufw** | firewall frontend per iptables (uncomplicated firewall) | [enable-firewall](<00-setup-after-installing-kali/04-enable-firewall/README.md>) |
| **ssh (sshd_config)** | hardening ssh: disabilita root login, key-only auth | [secure-ssh-access](<00-setup-after-installing-kali/06-secure-ssh-access/README.md>) |
| **sysctl** | kernel hardening: aslr, syn cookies, ip forwarding | [harden-the-kernel](<00-setup-after-installing-kali/13-harden-the-kernel/README.md>) |
| **suricata** | ids/ips rule-based per traffic inspection | [configure-intrusion-detection](<00-setup-after-installing-kali/14-configure-intrusion-detection-systems/README.md>) |
| **logwatch** | log aggregation e reporting giornaliero | [setup-logwatch](<00-setup-after-installing-kali/20-setup-logwatch-system-monitoring/README.md>) |
| **luks / veracrypt** | full disk encryption e volumi cifrati | [encrypt-sensitive-data](<00-setup-after-installing-kali/10-encrypt-sensitive-data/README.md>) |
| **rsync** | backup incrementale di sistema | [backup-your-system](<00-setup-after-installing-kali/19-backup-your-system/README.md>) |

---

## Target e infrastruttura lab

| tool | descrizione | usato in |
| :--- | :--- | :--- |
| **dvwa** | damn vulnerable web application - target web per sqli, xss, csrf | [docker-compose.yml](docker-compose.yml), [sql-injection](<03-web-attacks (Red Team + Secure Coding)/03-owasp (Attacks)/sql-injection (SQLi)/README.md>) |
| **dvga** | damn vulnerable graphql application - target api graphql | [docker-compose.yml](docker-compose.yml), [graphql](<03-web-attacks (Red Team + Secure Coding)/05-api-security/graphql/README.md>) |
| **juice shop** | owasp juice shop - 100+ challenge owasp top 10 | [docker-compose.yml](docker-compose.yml) |
| **virtualbox** | hypervisor per le vm di laboratorio | [lab_setup.md](LAB_SETUP.md), [lab-setup.sh](scripts/lab-setup.sh) |
| **docker compose** | orchestrazione container per web target | [docker-compose.yml](docker-compose.yml), [lab_setup.md](LAB_SETUP.md) |
| **asciinema** | registrazione sessioni terminale per demo | [lab_setup.md](LAB_SETUP.md) |

---

## Script personalizzati

| script | descrizione | percorso |
| :--- | :--- | :--- |
| **nessus_parser.py** | parser xml nessus con filtro severity, statistiche e export csv | [02-vulnerability-assessment/code/](02-vulnerability-assessment/code/nessus_parser.py) |
| **header_security_check.py** | analisi security header http con score e suggerimenti fix | [03-web-attacks/code/](<03-web-attacks (Red Team + Secure Coding)/code/header_security_check.py>) |
| **hash_identifier.py** | identificatore tipo hash con suggerimenti hashcat/john mode | [04-system-exploitation/code/](04-system-exploitation/05-password-cracking/code/hash_identifier.py) |
| **lab-setup.sh** | automazione setup vm virtualbox (create, network, snapshot) | [scripts/](scripts/lab-setup.sh) |
| **check-finding-ids.sh** | validazione finding id (formato, univocita, sequenzialita) | [scripts/](scripts/check-finding-ids.sh) |

---

## Statistiche

| categoria | tool | file che li documentano |
| :--- | :---: | :---: |
| reconnaissance | 10 | 12 |
| vulnerability assessment | 10 | 11 |
| web application testing | 15 | 16 |
| system exploitation | 9 | 9 |
| password cracking | 4 | 4 |
| binary exploitation | 4 | 4 |
| defensive tools | 7 | 7 |
| target/infrastruttura | 6 | 8 |
| script personalizzati | 5 | 5 |
| **totale** | **70** | **76** |

---

> *Versioni e compatibilita: i tool elencati sono stati testati su Kali Linux 2024.x.
> Quando disponibili alternative moderne (es. NetExec al posto di CrackMapExec), sono
> state indicate nei rispettivi README di modulo.*
