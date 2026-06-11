> **English** | [Italiano](README.md)

# SMTP Relay - Sending Infrastructure Configuration

> - **Phase:** Social Engineering - Email Infrastructure Setup
> - **Visibility:** Medium - the relay configuration is internal, but sending emails generates SMTP logs, DNS records (SPF, DKIM, rDNS), and contributes to domain reputation trackable by services such as MXToolbox and Talos Intelligence
> - **Prerequisites:** Server with public IP (VPS) or account on transactional service (SendGrid, Mailgun, Amazon SES); registered domain with DNS management access; basic Postfix and DKIM knowledge
> - **Output:** Operational SMTP infrastructure for simulated phishing campaigns; SPF/DKIM configuration to maximize deliverability

- **Operating Environment:** Kali Linux Purple with Postfix (local relay), Mailhog (testing)
- **Documented Techniques:** Postfix Setup, DKIM Signing, Domain Warming, Deliverability Optimization

---

## Executive Summary

SMTP relay configuration is the step that transforms a phishing tool (GoPhish, SET) into an operational delivery platform. Without a properly configured relay, phishing emails end up in spam or are rejected by destination servers. This section documents three approaches with different trade-offs between ease of setup, deliverability, and operational control.

---

## Approach 1: Transactional Service (Recommended for Lab)

Services such as SendGrid, Mailgun, and Amazon SES offer high deliverability thanks to their consolidated domain reputation. They are the optimal choice for labs and authorized security awareness campaigns.

```Bash
# GoPhish configuration with SendGrid
# Sending Profile -> New Profile:
# Name: SendGrid-Relay
# SMTP From: phishing@attacker-lab.com
# Host: smtp.sendgrid.net:587
# Username: apikey
# Password: SG.xxxxxxxxx (SendGrid API key)
# -> Send Test Email
```

**Limitations:** providers have anti-abuse policies that can suspend accounts if content is classified as phishing. For testing: always use Mailhog or a local relay.

---

## Approach 2: Dedicated Server (Postfix + OpenDKIM)

```Bash
# Postfix installation on Kali
sudo apt install postfix opendkim opendkim-tools
# Configuration: select "Internet Site"

# DKIM key generation
sudo opendkim-genkey -s mail -d attacker-lab.com -D /etc/opendkim/keys/
```

```Bash
# Postfix configuration for DKIM signing
# /etc/postfix/main.cf
# milter_protocol = 6
# milter_default_action = accept
# smtpd_milters = inet:localhost:8891
# non_smtpd_milters = inet:localhost:8891
```

```Bash
# DNS records to add to the domain:
# SPF:  TXT  attacker-lab.com      "v=spf1 ip4:<SERVER_IP> -all"
# DKIM: TXT  mail._domainkey.attacker-lab.com  "v=DKIM1; k=rsa; p=<PUBLIC_KEY>"
# rDNS: PTR  <SERVER_IP>           mail.attacker-lab.com
```

```Bash
# Send test with swaks
swaks --to test@mailhog-lab.local --from noreply@attacker-lab.com --server 127.0.0.1:25 --header "Subject: Test SMTP" --body "Test delivery."
```

---

## Approach 3: Local Testing with Mailhog

```Bash
# Mailhog: fake SMTP server for testing without real sending
# Installation
go install github.com/mailhog/MailHog@latest
# or
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog

# Start
MailHog
# SMTP: 127.0.0.1:1025
# Web UI: http://127.0.0.1:8025
```

```Bash
# GoPhish configuration for Mailhog
# Sending Profile:
# Host: 127.0.0.1:1025
# (no authentication needed)
# -> all emails are visible in Mailhog's Web UI
```

---

## Domain Warming

A freshly registered domain has zero reputation. Immediately sending hundreds of phishing emails causes instant blocking. Domain warming is the process of gradually building reputation:

```
Week 1:  10-20 emails/day to your own accounts (Gmail, Outlook)
Week 2:  50-100 emails/day with legitimate content
Week 3:  200-500 emails/day, mixed content
Week 4+: target campaign volume
```

**Note:** for authorized security awareness campaigns, domain warming is often unnecessary if the internal corporate SMTP relay is used. For Red Team engagements with a dedicated domain, warming requires 2-4 weeks of preparation.

---

## Reference Tools

| Tool | Type | Technique/Access | Primary Use Case |
| :--- | :--- | :--- | :--- |
| `Postfix` | SMTP server | CLI - Config | Dedicated SMTP relay with DKIM support |
| `OpenDKIM` | DKIM signer | CLI - Config | DKIM cryptographic signing for outgoing emails |
| `Mailhog` | SMTP testing | Web UI | Local testing without real sending |
| `swaks` | SMTP testing | CLI | Send testing with custom headers/body |
| `MXToolbox` | Diagnostics | Web | SPF, DKIM, blacklist, deliverability verification |

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Resource Development | Acquire Infrastructure: Email Accounts | `T1583.002` | SMTP relay configuration for campaign email sending |
| Resource Development | Stage Capabilities: Email Accounts | `T1608.003` | Domain warming and SPF/DKIM configuration for deliverability |

---

> **Note:** The documented configurations were tested in a local environment with Mailhog. No emails were sent to real addresses or third-party servers.
