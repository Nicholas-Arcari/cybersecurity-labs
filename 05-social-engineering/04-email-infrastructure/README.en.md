> **English** | [Italiano](README.md)

# 04 - Email Infrastructure

> - **Phase:** Social Engineering - Email Infrastructure Setup & Audit
> - **Visibility:** Low (SPF/DKIM/DMARC audit is passive: public DNS queries) / Medium (SMTP relay configuration and typosquatting domain purchase leave trackable traces)
> - **Prerequisites:** Access to DNS query tools (dig, nslookup, spoofcheck); for SMTP relay: account on transactional email service (SendGrid, Mailgun) or Postfix server; for typosquatting: domain generation tools (dnstwist, urlcrazy)
> - **Output:** Finding SE-011..012; SPF/DKIM/DMARC audit of target domain; operational SMTP relay configuration; list of available typosquatting domains

---

## Introduction

Email infrastructure is the technical foundation that determines the success or failure of a phishing campaign. A technically perfect email (convincing pretext, effective payload) is useless if it ends up in spam or if the sender domain is obviously fake.

This section documents three complementary components:

1. **SPF/DKIM/DMARC Audit (SE-011):** analysis of the target domain's email configuration to identify misconfigurations that allow spoofing. A domain without DMARC in `reject` or `quarantine` mode accepts spoofed emails - the attacker can send emails that appear to come from `ceo@target.com`.

2. **SMTP Relay:** configuration of the sending infrastructure for campaigns. A properly configured relay (SPF, DKIM, domain reputation) maximizes deliverability and reduces the risk of being blacklisted.

3. **Domain Typosquatting (SE-012):** generation and analysis of domains that are confusable with the target domain (e.g., `g00gle.com`, `microsfot.com`). Purchasing a typosquatting domain with a valid TLS certificate makes emails and landing pages nearly indistinguishable from the original.

---

## Folder Structure

```
04-email-infrastructure/
+-- spf-dkim-dmarc/        # Target email configuration audit - SE-011
+-- smtp-relay/             # SMTP configuration for campaigns (guide)
+-- domain-typosquatting/   # Confusable domain generation - SE-012
```

---

## `spf-dkim-dmarc/` - Email Security Audit

**Finding ID:** `SE-011` | **Severity:** `Medium` (DMARC policy `none` - spoofing possible)

### Operational Context

The audit verified the SPF, DKIM, and DMARC configuration of the simulated target domain to determine whether it was possible to send spoofed emails. The result - DMARC with policy `none` - means that the domain does not block or quarantine emails that fail SPF/DKIM checks. An attacker can send emails with the `@target-lab.com` sender without being blocked.

### Key Commands

```Bash
# Verify SPF record
dig +short TXT target-lab.com | grep spf
```

```
"v=spf1 include:_spf.google.com ~all"                      <-- softfail (~all), not hardfail (-all)
```

```Bash
# Verify DMARC record
dig +short TXT _dmarc.target-lab.com
```

```
"v=DMARC1; p=none; rua=mailto:dmarc@target-lab.com"        <-- SE-011: policy "none" = no enforcement
```

```Bash
# Verify with spoofcheck (dedicated tool)
git clone https://github.com/BishopFox/spoofcheck.git
cd spoofcheck && pip install -r requirements.txt
python3 spoofcheck.py target-lab.com
```

```
[+] target-lab.com
[+] SPF record found: v=spf1 include:_spf.google.com ~all
[-] SPF softfail (~all) - spoofing may be possible          <-- not hardfail
[+] DMARC record found
[-] DMARC policy is 'none' - no enforcement                 <-- SE-011
[!] Spoofing possible for target-lab.com                    <-- vulnerable domain
```

### Remediation

- **Immediate action:** set DMARC policy to `quarantine` as a first step, then migrate to `reject` after verifying RUA/RUF reports
- **Structural action:** SPF with `-all` (hardfail); active DKIM signing on all authorized sending servers; DMARC `p=reject` with reporting enabled; continuous monitoring of DMARC aggregate reports to identify unauthorized sending sources
- **Verification:** `dig +short TXT _dmarc.target.com` must return `p=reject`; sending a spoofed test email must be rejected by the destination server

---

## `smtp-relay/` - SMTP Configuration for Campaigns

### Operational Context

SMTP relay configuration is fundamental for phishing email deliverability. The section documents three approaches:

1. **Transactional service (SendGrid, Mailgun, Amazon SES):** high deliverability, domain reputation managed by the provider, automatic SPF/DKIM configuration. Limitation: providers have anti-abuse policies that can block suspicious content.

2. **Dedicated server (Postfix/Haraka):** full control, no content limitations. Requires manual SPF, DKIM, rDNS configuration, and domain warming (gradual sending to build reputation).

3. **GoPhish built-in SMTP:** GoPhish can function as a direct SMTP server, but without domain reputation the delivery rate is low.

### Key Commands

```Bash
# Postfix configuration as relay (Kali)
sudo apt install postfix
# Select "Internet Site" during setup

# DKIM configuration with opendkim
sudo apt install opendkim opendkim-tools
opendkim-genkey -s mail -d attacker-lab.com
# Add the generated TXT record to the domain's DNS
```

```Bash
# Email send test with swaks
swaks --to victim@target-lab.com \
  --from ceo@attacker-lab.com \
  --server 127.0.0.1:25 \
  --header "Subject: Riunione urgente" \
  --body "Conferma la tua disponibilita."
```

---

## `domain-typosquatting/` - Confusable Domain Generation

**Finding ID:** `SE-012` | **Severity:** `Informational` (unregistered confusable domains identified)

### Operational Context

Typosquatting exploits the visual similarity between characters to create domains that appear identical or nearly identical to the target domain. The `dnstwist` tool automatically generates domain variations (character substitution, homoglyphs, transpositions) and verifies which are already registered and which are available for purchase.

### Key Commands

```Bash
# dnstwist installation
sudo apt install dnstwist
# or
pip install dnstwist

# Generate variations for target domain
dnstwist --registered target-lab.com
```

```
     _           _            _     _
  __| |_ __  ___| |___      _(_)___| |_
 / _` | '_ \/ __| __\ \ /\ / / / __| __|
| (_| | | | \__ \ |_ \ V  V /| \__ \ |_
 \__,_|_| |_|___/\__| \_/\_/ |_|___/\__|

domain               type          ip            mx
target-lab.com       original      93.184.216.34 mx.target-lab.com
targat-lab.com       replacement   -             -                     <-- available
target-1ab.com       homoglyph     -             -                     <-- available
targetlab.com        omission      198.51.100.1  mx.parked.com        <-- registered (parked)
targt-lab.com        omission      -             -                     <-- available
target-lab.co        tld-swap      203.0.113.5   -                     <-- registered
```

```Bash
# Filter only available (unregistered) domains
dnstwist --registered target-lab.com | grep -v "^\*" | awk '$3 == "-" {print $1}'
```

```
targat-lab.com                                              <-- SE-012: purchasable
target-1ab.com                                              <-- SE-012: purchasable (homoglyph)
targt-lab.com                                               <-- SE-012: purchasable
```

### Remediation

- **Immediate action:** preemptive registration of the most critical typosquatting domains (those with a single character substitution)
- **Structural action:** continuous monitoring with dnstwist/URLCrazy scheduled weekly; defensive registration of domains (.com, .org, .net for the most obvious variations); reporting active typosquatting domains to registrars for abuse
- **Verification:** re-run dnstwist - critical domains must appear as registered and under the organization's control

---

## Reference Tools

| Tool | Type | Technique/Access | Primary Use Case |
| :--- | :--- | :--- | :--- |
| `spoofcheck` | Email audit | CLI - Python | SPF/DKIM/DMARC verification and spoofing possibility assessment |
| `dnstwist` | Domain analysis | CLI - Python | Typosquatting domain generation and verification |
| `URLCrazy` | Domain analysis | CLI - Ruby | Alternative to dnstwist with focus on typos and bit-flips |
| `Postfix` | SMTP server | CLI - Config | SMTP server for email relay with DKIM signing |
| `opendkim` | DKIM signer | CLI - Config | DKIM key generation and signing for outgoing email |
| `swaks` | SMTP testing | CLI | Swiss Army Knife for SMTP: send testing, headers, attachments |
| `Mailhog` | SMTP testing | Web UI | Fake SMTP for local testing without real sending |

> **Recommended modern tool:** `dnstwist` with `--all` flag to include Unicode homoglyphs and IDN homograph attacks. For continuous monitoring, services like `PhishLabs` or `Bolster` automate detection of active typosquatting domains.

---

## Finding Registry

| ID | Description | Severity | CVSS | Subfolder |
| :--- | :--- | :---: | :---: | :--- |
| `SE-011` | SPF/DKIM/DMARC audit: target domain with SPF softfail and DMARC policy `none` - email spoofing possible | `Medium` | 5.3 | `spf-dkim-dmarc/` |
| `SE-012` | Domain typosquatting: 3+ confusable domains unregistered and purchasable by an attacker | `Informational` | 3.1 | `domain-typosquatting/` |

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Related Finding |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Network Information: DNS | `T1590.002` | SE-011 |
| Reconnaissance | Search Open Technical Databases: DNS/Passive DNS | `T1596.001` | SE-011, SE-012 |
| Resource Development | Acquire Infrastructure: Domains | `T1583.001` | SE-012 |
| Resource Development | Acquire Infrastructure: Email Accounts | `T1583.002` | SE-011 |
| Resource Development | Compromise Infrastructure: Domains | `T1584.001` | SE-012 |

---

> **Note:** All documented activities were conducted on test domains created ad hoc in a lab environment. No audit was performed on third-party domains without authorization. Identified typosquatting domains were not registered.
