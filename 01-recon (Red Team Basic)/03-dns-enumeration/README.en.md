> **English** | [Italiano](README.md)

# 03 - DNS Enumeration

> - **Phase:** Reconnaissance - DNS Enumeration
> - **Visibility:** Zero / Low - from passive search on CT logs to standard DNS queries
> - **Prerequisites:** Target domain identified, Internet access, `dig` / `dnsenum` / `Sublist3r` tools
> - **Output:** Successful zone transfer with complete DNS zone exposure (DNS-001), accessible hidden virtual hosts (DNS-002), 500+ enterprise target subdomains (DNS-003)

---

## Introduction

The Domain Name System is the phonebook of the Internet: it maps names to IP addresses, identifies mail servers, manages zone delegation. For a Red Team, DNS is an exceptional intelligence source: every published record reveals a piece of the target's infrastructure.

DNS Enumeration has two main objectives:

1. **Expand the attack surface:** find subdomains not linked from the main homepage (development environments, admin panels, VPN, API gateways) that often present critical vulnerabilities because they are "forgotten".

2. **Exploit misconfigurations:** Zone Transfer (AXFR) is one of the most powerful attacks in this phase - if the DNS server is misconfigured, it delivers the entire network topology to the attacker in a single command.

The fundamental distinction with the `03-web-attacks/` module is the following:
- **DNS Enumeration (this module):** we search for WHICH servers/subdomains exist (e.g., `vpn.tesla.com` exists at `1.2.3.4` with port 443 open)
- **Web Attack (03):** we analyze WHAT runs inside those servers (e.g., `vpn.tesla.com` uses Fortinet 7.0.1, vulnerable to CVE-2023-XXXX)

---

## Folder Structure

```
03-dns-enumeration/
+-- README.md                <- this file (index + finding registry)
|
+-- dns-recon/
|   +-- README.md            <- DNS-001: AXFR zone transfer, NS/MX query (dig, dnsenum)
|   +-- img/                 <- lab screenshots
|
+-- hosts-file/
|   +-- README.md            <- DNS-002: virtual host via /etc/hosts manipulation
|   +-- img/                 <- lab screenshots
|
+-- subdomain-finding/
    +-- README.md            <- DNS-003: passive subdomain enumeration (Sublist3r, Assetfinder)
    +-- img/                 <- lab screenshots
```

---

## `dns-recon/` - DNS Recon and Zone Transfer

**Finding ID:** `DNS-001` | **Severity:** `Critical`

Zone Transfer (AXFR request) is a DNS replication mechanism designed for synchronization between primary and secondary servers. If the server does not restrict access to trusted IPs, anyone can request a complete copy of the domain's DNS database.

**Lab result on `zonetransfer.me`:** zone transfer successful. Critical subdomains usually hidden were extracted: `vpn.`, `dev.`, `office.` with their respective IPs and internal TXT records.

This type of misconfiguration completely negates "Security by Obscurity": the attacker obtains the complete network map in a single `dig axfr` command.

---

## `hosts-file/` - Virtual Host Discovery via /etc/hosts

**Finding ID:** `DNS-002` | **Severity:** `Medium`

Virtual Hosts allow a single web server (Apache/Nginx) to serve multiple distinct sites based on the `Host:` header of the HTTP request. If a subdomain is not registered in public DNS but is configured on the server, it is accessible only by locally modifying the `/etc/hosts` file.

This technique is fundamental in CTF environments and internal penetration testing to access admin panels, staging environments or API endpoints that are unpublished but reachable from the server IP.

---

## `subdomain-finding/` - Passive Subdomain Enumeration

**Finding ID:** `DNS-003` | **Severity:** `Medium`

Passive subdomain enumeration leverages third-party sources without generating traffic towards the target: Certificate Transparency logs, search engine historical archives, public databases like VirusTotal.

**Lab result on `tesla.com`:** 500+ unique subdomains identified with `Sublist3r` and `Assetfinder`, including high-value targets such as `sso.tesla.com`, `vpn.tesla.com`, `dev-app.tesla.com`.

The subdomains found here become direct scope for the `03-web-attacks/02-web-recon/` module.

> **Recommended modern tool:** `amass enum -passive -d <DOMAIN>` - compared to Sublist3r (no longer actively maintained), amass queries more sources (50+), integrates Certificate Transparency logs and produces structured JSON output for automated post-processing.

---

## Recommended Operational Flow

```
[INPUT] Target domain (e.g., tesla.com)
          |
          v
[1] Name Server Identification
     +-- host -t ns <DOMAIN>
     +-- dig ns <DOMAIN>
     -> NS records list
          |
          v
[2] Zone Transfer (always test - sometimes it still works)
     +-- dig axfr @<NAMESERVER> <DOMAIN>
     +-- dnsenum <DOMAIN>
     -> If successful: DNS-001 Critical, complete network map extracted
          |
     [If it fails]
          v
[3] Passive Subdomain Enumeration
     +-- sublist3r -d <DOMAIN> -o output.txt    # search engine aggregation
     +-- assetfinder --subs-only <DOMAIN>        # Certificate Transparency
     +-- amass enum -passive -d <DOMAIN>         # more sources, structured output
     -> Subdomain list
          |
          v
[4] Virtual Host Discovery (if IPs are known)
     +-- Modify /etc/hosts: <IP> <VHOST>
     +-- ffuf -w wordlist.txt -H "Host: FUZZ.<DOMAIN>" -u http://<IP>/
     -> Unpublished accessible VHosts
          |
          v
[OUTPUT] Subdomain + IP list -> 03-web-attacks/02-web-recon/
```

---

## Reference Tools

| Tool | Type | Technique/Access | Main Use Case |
| :--- | :--- | :--- | :--- |
| `dig` | DNS query | CLI | Advanced DNS queries, AXFR zone transfer |
| `host` | DNS query | CLI | Quick DNS queries, NS/MX/A records |
| `dnsenum` | DNS query | CLI | Zone transfer automation + subdomain brute force |
| `Sublist3r` | Subdomain harvesting | CLI (Python) | Subdomain aggregation from search engines |
| `Assetfinder` | Subdomain harvesting | CLI (Go) | Enumeration via Certificate Transparency |
| `amass` | Subdomain harvesting | CLI (Go) | OWASP standard, 50+ sources, JSON output |
| `ffuf` | VHost fuzzing | CLI | Virtual host brute force via HTTP header |

> **Recommended modern tool:** `amass enum -passive -d <DOMAIN>` (OWASP) replacing Sublist3r, actively maintained with support for modern sources (Shodan, VirusTotal, Censys, BeVigil).

---

## Finding Registry

| ID | Description | Severity | File |
| :--- | :--- | :---: | :--- |
| `DNS-001` | Successful Zone Transfer on zonetransfer.me - complete DNS zone exfiltrated | `Critical` | `dns-recon/README.md` |
| `DNS-002` | Unpublished virtual host accessible via /etc/hosts manipulation | `Medium` | `hosts-file/README.md` |
| `DNS-003` | 500+ tesla.com subdomains including vpn, sso, dev-app | `Medium` | `subdomain-finding/README.md` |

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Network Info: DNS | `T1590.002` | AXFR Zone Transfer on zonetransfer.me, complete extraction of DNS records (DNS-001) |
| Reconnaissance | Search Open Technical Databases: DNS/Passive DNS | `T1596.001` | Subdomain enumeration from Certificate Transparency and search engines (DNS-001, DNS-003) |

---

> **Note:** DNS Enumeration activities were performed on targets specifically configured for educational purposes (`zonetransfer.me` by DigiNinja), on public bug bounty programs (`tesla.com`) and in a local lab. The Zone Transfer on `zonetransfer.me` is an intentional behavior of the service, designed for security training.
