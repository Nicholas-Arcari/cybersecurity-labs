> **English** | [Italiano](README.md)

# Domain Typosquatting - Confusable Domain Generation

> - **Phase:** Social Engineering - Resource Development (Attack Infrastructure)
> - **Visibility:** Low - domain generation and analysis is passive (DNS/WHOIS queries); registering a domain is trackable via WHOIS and Certificate Transparency logs
> - **Prerequisites:** dnstwist or URLCrazy installed; Internet access for real-time DNS queries; for purchase: domain registrar with anonymous payment (optional)
> - **Output:** SE-012 (unregistered confusable domains identified for the target domain - severity Informational)

- **Operating Environment:** Kali Linux Purple
- **Target:** Simulated corporate domain (target-lab.com)
- **Framework:** dnstwist 20240812, URLCrazy
- **Documented Techniques:** Homoglyph Generation, Bit-flip Domains, TLD Swap, Omission/Transposition

---

## Executive Summary

Typosquatting is the technique of registering domains that are visually similar to the target domain in order to deceive users. A domain like `target-1ab.com` (with digit "1" instead of the letter "l") is nearly indistinguishable from `target-lab.com` in most fonts. Combined with a valid TLS certificate (Let's Encrypt is free and automatic), the typosquatting domain makes phishing emails and landing pages extremely credible.

The lab used `dnstwist` to systematically generate all variations of the target domain and identify those not yet registered, available for purchase by an attacker.

---

## Typosquatting: Domain Permutation Analysis

**Finding ID:** `SE-012` | **Severity:** `Informational`

### PoC - Phase 1: Variation Generation

```Bash
dnstwist --all --registered target-lab.com
```

```
     _           _            _     _
  __| |_ __  ___| |___      _(_)___| |_
 / _` | '_ \/ __| __\ \ /\ / / / __| __|
| (_| | | | \__ \ |_ \ V  V /| \__ \ |_
 \__,_|_| |_|___/\__| \_/\_/ |_|___/\__|

domain                type           a             mx
target-lab.com        original       93.184.216.34 mx.target-lab.com
targat-lab.com        replacement    -             -                  <-- available
target-1ab.com        homoglyph      -             -                  <-- available (l->1)
targt-lab.com         omission       -             -                  <-- available (e omitted)
targe-tlab.com        insertion      -             -                  <-- available
target-alb.com        transposition  -             -                  <-- available
target-lab.co         tld-swap       203.0.113.5   -                  <-- registered
targetlab.com         omission       198.51.100.1  mx.parked.com     <-- registered (parked)
target-lab.net        tld-swap       -             -                  <-- available
target-lab.org        tld-swap       -             -                  <-- available
```

### PoC - Phase 2: Risk Analysis by Type

```Bash
# Variation count by type
dnstwist --all target-lab.com --format csv | tail -n +2 | cut -d',' -f2 | sort | uniq -c | sort -rn
```

```
  12 replacement        <-- single character substitution
   8 homoglyph          <-- visually similar characters (l/1, O/0, rn/m)
   6 omission           <-- missing character
   5 insertion          <-- additional character
   4 transposition      <-- swapped characters
   3 tld-swap           <-- TLD change (.com->.net/.org)
   2 addition           <-- trailing character
   1 bitsquatting       <-- hardware bit-flip (rare but documented)
```

### PoC - Phase 3: Visual Impact Assessment

The most dangerous domains are those with the lowest visual distance from the original:

```
HIGH RISK (indistinguishable in many fonts):
  target-1ab.com   (l -> 1)    <- homoglyph: nearly impossible to distinguish
  target-Iab.com   (l -> I)    <- uppercase homoglyph
  tarqet-lab.com   (g -> q)    <- low-distance substitution

MEDIUM RISK (require attention):
  targat-lab.com   (e -> a)    <- substitution close on keyboard
  target-alb.com   (lab -> alb) <- transposition

LOW RISK (distinguishable with attention):
  target-lab.net   (different TLD)
  targt-lab.com    (missing character)
```

### Remediation

- **Immediate action:** preemptive registration of high-risk domains (homoglyphs with minimal visual distance)
- **Structural action:** continuous monitoring with scheduled dnstwist (weekly cron); defensive registration of main TLDs (.com, .net, .org, .it) for the most obvious variations; configure alerts on Certificate Transparency logs (crt.sh) for new certificates issued for similar domains
- **Verification:** re-run dnstwist - critical domains must appear under the organization's control

---

## Lab Experience

Running dnstwist on the test domain generated over 40 variations in a few seconds. The main surprise was the number of homoglyph domains that are visually identical to the original domain: the substitution of `l` (lowercase L) with `1` (one) is practically invisible in the sans-serif fonts used by most email clients and browsers.

A critical aspect: dnstwist with the `--all` flag also includes Unicode homoglyphs (IDN homograph attack), such as the substitution of the Latin letter "a" with the Cyrillic letter "a" (U+0430). These domains are technically different but visually identical. Modern browsers partially mitigate this attack by displaying the URL in Punycode format (xn--...) when they detect script mixing, but not all email clients implement this protection.

---

## Theoretical Analysis: Domain Attack Taxonomy

Typosquatting exploits the limited human capacity to visually process long alphanumeric strings. Verizon's research (DBIR 2024) shows that the average time spent analyzing a URL before clicking is less than 2 seconds - insufficient to identify a single character substitution.

The main permutation categories are:
- **Homoglyphs:** visually identical characters (`l`/`1`, `O`/`0`, `rn`/`m`). The most dangerous.
- **Keyboard typos:** errors based on key proximity (QWERTY/QWERTZ).
- **Bitsquatting:** variations caused by hardware bit-flips in DNS resolution. Rare but documented in academic research (Dinaburg, 2011).
- **IDN Homograph:** use of visually identical Unicode characters from different scripts. Partially mitigated by browsers but not by email clients.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Search Open Technical Databases: DNS/Passive DNS | `T1596.001` | DNS analysis of generated typosquatting domains (SE-012) |
| Resource Development | Acquire Infrastructure: Domains | `T1583.001` | Identification of unregistered confusable domains for potential purchase |
| Resource Development | Compromise Infrastructure: Domains | `T1584.001` | Assessment of typosquatting domains already registered by third parties (parked) |

---

> **Note:** The analysis was conducted on a test domain. No typosquatting domains were registered. The techniques are documented for defensive purposes (monitoring and preemptive registration).
