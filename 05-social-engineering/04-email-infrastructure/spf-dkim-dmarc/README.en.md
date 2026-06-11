> **English** | [Italiano](README.md)

# SPF/DKIM/DMARC - Email Authentication Audit

> - **Phase:** Social Engineering - Email Infrastructure Reconnaissance
> - **Visibility:** Zero - the audit is based on public DNS queries (TXT records), no packets sent to the target's mail server, no logs generated
> - **Prerequisites:** Access to DNS query tools (dig, nslookup); spoofcheck (BishopFox) for automated analysis; understanding of SPF, DKIM, and DMARC mechanisms
> - **Output:** SE-011 (DMARC policy `none` - email spoofing possible - severity Medium)

- **Operating Environment:** Kali Linux Purple (Attacker)
- **Target:** Simulated target email domain (target-lab.com)
- **Framework:** dig, spoofcheck, dmarcian.com (reference)
- **Documented Techniques:** DNS TXT Record Analysis, SPF Validation, DMARC Policy Assessment

---

## Executive Summary

SPF (Sender Policy Framework), DKIM (DomainKeys Identified Mail), and DMARC (Domain-based Message Authentication, Reporting and Conformance) are the three pillars of email authentication. Their correct configuration prevents an attacker from sending spoofed emails that appear to originate from the target's domain. Their misconfiguration - particularly DMARC with policy `none` - is one of the most common and impactful findings in a social engineering assessment: it allows the attacker to impersonate any email address on the domain without the destination server blocking the message.

The lab documented the complete email configuration audit of a simulated target domain, identifying a chain of weaknesses: SPF with softfail (`~all` instead of `-all`), DKIM not verified, and DMARC with policy `none`. This combination allows complete domain spoofing.

---

## SPF/DKIM/DMARC Audit: Spoofing Assessment

**Finding ID:** `SE-011` | **Severity:** `Medium`

### PoC - Phase 1: SPF Verification

```Bash
dig +short TXT target-lab.com | grep spf
```

```
"v=spf1 include:_spf.google.com ~all"
```

**Analysis:** The SPF record is present but uses `~all` (softfail) instead of `-all` (hardfail). With softfail, emails from unauthorized IPs are marked as suspicious but not rejected. In the absence of DMARC enforcement, the softfail has no practical effect.

### PoC - Phase 2: DKIM Verification

```Bash
# DKIM requires the specific selector (often "google", "mail", "selector1")
dig +short TXT google._domainkey.target-lab.com
dig +short TXT mail._domainkey.target-lab.com
dig +short TXT selector1._domainkey.target-lab.com
```

```
# No records found for common selectors                        <-- DKIM not configured or non-standard selector
```

### PoC - Phase 3: DMARC Verification

```Bash
dig +short TXT _dmarc.target-lab.com
```

```
"v=DMARC1; p=none; rua=mailto:dmarc@target-lab.com"            <-- SE-011: policy "none"
```

**Analysis:** `p=none` means the domain instructs destination servers to take no action on emails that fail SPF and DKIM checks. The only effect is sending aggregate reports to the RUA address - useful for monitoring but useless as a defense.

### PoC - Phase 4: Automated Verification with spoofcheck

```Bash
python3 spoofcheck.py target-lab.com
```

```
[+] target-lab.com
[+] SPF record found!
[-] SPF record uses ~all (softfail) - not strict enough
[+] DMARC record found!
[-] DMARC policy is set to 'none' - NOT enforced               <-- SE-011
[!] DOMAIN IS SPOOFABLE                                         <-- conclusion: spoofing possible
```

### PoC - Phase 5: Practical Spoofing Verification

```Bash
# Spoofed email send test (to test Mailhog, NOT to real servers)
swaks --to victim@test-lab.local \
  --from ceo@target-lab.com \
  --server 127.0.0.1:25 \
  --header "Subject: Richiesta urgente dal CEO" \
  --header "Reply-To: attacker@evil.com" \
  --body "Puoi effettuare un bonifico urgente? Dettagli nel prossimo messaggio."
```

```
=== Trying 127.0.0.1:25...
=== Connected to 127.0.0.1.
<-  250 Ok: queued                                              <-- email accepted without errors
```

### Remediation

- **Immediate action:** set DMARC to `p=quarantine; pct=100` as an intermediate step
- **Structural action:** SPF: change `~all` to `-all` (hardfail); DKIM: configure DKIM signing on all authorized sending servers; DMARC: migrate to `p=reject` after 30 days of RUA report monitoring to verify no legitimate service gets blocked; enable RUF forensic reports for detailed analysis of spoofing attempts
- **Verification:** `dig +short TXT _dmarc.target.com` returns `p=reject`; sending a spoofed test email is rejected with error 550

---

## Lab Experience

The audit was performed entirely through public DNS queries, without any direct interaction with the target's mail server. This aspect is fundamental: SPF/DKIM/DMARC analysis is completely passive and generates no logs on the target system, making it one of the first reconnaissance activities in a social engineering engagement.

The main difficulty was DKIM verification: unlike SPF and DMARC which have predictable DNS records, DKIM requires knowledge of the specific selector used by the domain. The most common selectors (`google`, `mail`, `selector1`, `selector2`, `s1`, `s2`) were tested without results. In a real engagement, the selector can be extracted from headers of legitimate emails originating from the target domain (`DKIM-Signature: s=<selector>` header).

A critical observation: even with SPF `-all` and active DKIM, without DMARC `reject`, spoofing can still succeed with some email providers that do not implement strict checks. DMARC `reject` is the only configuration that guarantees systematic blocking of spoofed emails.

---

## Theoretical Analysis: The SPF/DKIM/DMARC Triangle

**SPF** defines which server IPs are authorized to send email for a domain. The DNS TXT record contains a list of authorized IPs/ranges/includes and a final qualifier: `-all` (hardfail: reject everything else), `~all` (softfail: mark as suspicious), `?all` (neutral: no indication). The problem with SPF alone: it operates on the envelope sender (MAIL FROM), not on the header From displayed to the user. An attacker can use a different envelope sender and still display `ceo@target.com` in the header.

**DKIM** adds a cryptographic signature to the email that allows the recipient to verify that the message was not altered in transit and that it genuinely originated from the declared domain. The signature is based on RSA key pairs: the private key signs on the sending server, the public key is in the DNS record for verification.

**DMARC** is the glue that makes SPF and DKIM actually useful as an anti-spoofing defense. DMARC introduces the concept of "alignment": the header From must match the domain verified by SPF or DKIM. Without DMARC, an attacker can send emails that pass SPF (with their own domain as envelope sender) but display an arbitrary header From. DMARC with policy `reject` closes this gap.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Network Information: DNS | `T1590.002` | DNS TXT queries for SPF, DKIM, DMARC records of target domain |
| Reconnaissance | Search Open Technical Databases: DNS/Passive DNS | `T1596.001` | Automated analysis with spoofcheck (SE-011) |
| Resource Development | Acquire Infrastructure: Email Accounts | `T1583.002` | DMARC misconfiguration enables use of target domain for spoofing |

---

> **Note:** The audit was conducted on a test domain created ad hoc. No audit was performed on third-party domains without authorization.
