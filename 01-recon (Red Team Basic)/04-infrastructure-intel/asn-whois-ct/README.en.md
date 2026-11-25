> **English** | [Italiano](README.md)

# Perimeter Mapping: ASN, WHOIS and Certificate Transparency

> - **Phase:** Reconnaissance - Infrastructure Intelligence (perimeter mapping)
> - **Visibility:** Zero - querying of public registries (RIR, WHOIS) and Certificate Transparency logs; no packet sent to the target's infrastructure
> - **Prerequisites:** Name of the organization or target domain, Internet access
> - **Output:** IP ranges owned by the target (CIDR blocks), Autonomous System Number, subdomains hidden by certificates, complete network perimeter, finding INTEL-005

---

## Introduction

Before scanning, an attacker must know **what belongs** to the target. Many organizations do not own a single IP but entire address blocks (CIDR) announced under their own Autonomous System (AS). Identifying the ASN and the associated IP ranges means discovering the entire owned network perimeter - including servers, services and environments that do not appear in a simple DNS resolution of the main domain.

In parallel, the **Certificate Transparency (CT)** logs offer a source of subdomains that traditional DNS enumeration does not find. Every time a TLS certificate is issued, the Certificate Authority records it in public, append-only logs (provided by the RFC 6962 standard). These logs contain the Common Name and the Subject Alternative Names of the certificate: that is, the domain names, including internal subdomains (`vpn.`, `dev.`, `jenkins.`, `admin.`) that the organization never published but for which it requested a certificate.

The combination of ASN/WHOIS (IP perimeter) and Certificate Transparency (DNS perimeter) produces the complete map of the external attack surface, in a totally passive way. This section completes the Infrastructure Intelligence phase started with `shodan-censys/` (INTEL-001..003): while Shodan says "what is exposed", ASN/WHOIS and CT say "what exists and who it belongs to".

---

## Folder Structure

```
asn-whois-ct/
+-- README.md            <- this file (INTEL-005: perimeter mapping)
+-- img/                 <- lab screenshots (crt.sh, amass intel output, bgp.he.net)
```

---

## ASN and WHOIS - Identification of the Owned IP Ranges

**Finding ID:** `INTEL-005` | **Severity:** `Variable (Informational / Medium)`

### Operational Context

The Autonomous System Number identifies a network that announces its IP prefixes via BGP. Large organizations have their own ASN; small ones use the ISP's. Starting from the organization name or a single known IP, one traces back to the ASN and from it to all the announced CIDR blocks. The severity is `Informational` for the mapping alone, but rises to `Medium` when the mapping reveals ranges or services not foreseen by the target (shadow IT, forgotten environments).

### Execution

WHOIS resolution of a known IP to extract the ASN and the network block:

```Bash
# WHOIS of an IP to obtain netname, org and CIDR range
whois 8.8.8.8 | grep -Ei "netname|origin|route|orgname|cidr"
```

Expected output:

```
NetRange:       8.8.8.0 - 8.8.8.255
CIDR:           8.8.8.0/24                     <-- owned IP block
OriginAS:       AS15169                        <-- target's ASN
OrgName:        Google LLC                     <-- owner
```

Enumeration of all the prefixes announced by an ASN (via RIR WHOIS or dedicated tools):

```Bash
# All the IPv4 prefixes announced by an ASN
whois -h whois.radb.net -- '-i origin AS15169' | grep -Eo "([0-9.]+){4}/[0-9]+" | sort -u

# Alternatively, amass intel traces from org name to IP ranges and ASN
amass intel -org "Target Corp"
amass intel -asn 15169
```

Expected output (amass intel):

```
15169, GOOGLE - Google LLC, US
8.8.8.0/24
8.8.4.0/24
34.64.0.0/10                                   <-- range to include in the scan scope
...
```

> [Screenshot placeholder: capture the view of `bgp.he.net` (Hurricane Electric BGP Toolkit) for the target's ASN, which graphically shows all the announced prefixes and the peers.]

<!-- screenshot placeholder: BGP Toolkit - ASN prefixes (img/asn-bgp-PLACEHOLDER.jpg) -->

### Analysis of the Results

The identified CIDR blocks become the **IP scope** for the active network scanning phase (`02-network-scanning-active/`). Finding an undocumented range or services in a "forgotten" block is a finding in itself: it indicates shadow IT or assets not managed by the security team, often the most vulnerable.

---

## Certificate Transparency - Subdomains Hidden by the Certificates

### Operational Context

The Certificate Transparency logs are the most effective and most passive subdomain enumeration source available. They do not require interaction with the target's DNS: one queries a public index (crt.sh, Censys, the `ctfr` tool) of the issued certificates. Since today almost all services use HTTPS, every subdomain almost certainly has a certificate, and therefore appears in the CT logs - even the internal subdomains never published.

### Execution

Querying crt.sh via the JSON API (entirely passive):

```Bash
# Extraction of all the names from the certificates issued for the target domain
curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | sort -u

# Dedicated tool that queries the CT logs
ctfr -d target.com
```

Expected output:

```
target.com
www.target.com
mail.target.com
vpn.target.com                                 <-- remote access vector
dev.target.com                                 <-- development environment (less protected)
jenkins.target.com                             <-- INTEL-005: CI/CD exposed in CT
staging-admin.target.com                       <-- internal admin panel
*.internal.target.com                          <-- internal wildcard revealed by the certificate
```

> [Screenshot placeholder: capture the crt.sh web view for the target domain with the list of issued certificates and their SANs.]

### Analysis of the Results / Documented Finding

Subdomains with names like `jenkins`, `dev`, `staging`, `admin`, `vpn`, `gitlab` are the most valuable: they represent support infrastructure (CI/CD, non-production environments, management panels) typically less protected than production and not designed for exposure. An internal wildcard certificate (`*.internal.target.com`) appearing in the CT logs even reveals the naming convention of the internal network.

The produced list is direct input for:
- `03-dns-enumeration/subdomain-finding/` (DNS-003) for resolution and validation
- `03-web-attacks/02-web-recon/` for the probing of the live subdomains
- `shodan-censys/` to verify which of these are publicly exposed

---

## Lab Experience

The enumeration was run on domains authorized for educational purposes or included in public bug bounty programs, without sending any packet to the target's infrastructure. The comparison between Certificate Transparency enumeration and classic DNS enumeration showed the value of the CT logs: support subdomains emerge (development environments, panels, internal services) that DNS resolution alone does not reveal, because their existence is betrayed by the issued certificates. The trade-off, verified during the lab, is that the CT logs also contain old or revoked certificates: some of the names found are no longer resolvable or no longer point to a live host, so a validation step (DNS resolution and probing) was necessary before considering them a real part of the surface. The main decision was precisely in the filtering: distinguishing active subdomains from historical ones and prioritizing non-production environments and remote accesses, which are the highest-value targets for the subsequent phases.

Typical attention points, to verify during execution:

- The CT logs also contain expired or revoked certificates: a subdomain present in CT is not necessarily active. It must be validated with DNS resolution (semi-passive) or HTTP probing (active) in the subsequent phases.
- Wildcard certificates (`*.target.com`) hide the specific subdomains: in that case CT reveals the existence of the wildcard but not the single hosts, which must be sought with other techniques.
- crt.sh can be slow or rate-limited on domains with thousands of certificates: in that case prefer the Censys API or `subfinder` (which also aggregates CT sources).

### Theoretical Analysis

Certificate Transparency was born as a defensive countermeasure: after cases of compromised CAs issuing fraudulent certificates (e.g. DigiNotar 2011), Google mandated that every trusted certificate be recorded in verifiable public logs, so that a domain can notice certificates issued without its knowledge. The side effect for reconnaissance is that these same logs reveal the entire subdomain structure of an organization. It is a perfect example of the principle whereby a security measure (certificate transparency) creates a new informational surface exploitable in the recon phase.

On the routing plane, the ASN-prefix association is based on BGP: BGP announcements are public by necessity (they serve to route the traffic on the Internet), so anyone can observe which prefixes an AS announces. There is no way to "hide" this information without giving up reachability. This makes ASN and CT the two most reliable and unavoidable sources of passive perimeter reconnaissance.

---

## Recommended Operational Flow

```
[INPUT] Organization name or target domain
          |
          v
[1] From org name to IP/ASN
     +-- amass intel -org "Target Corp"    -> candidate ASNs
     +-- whois <known_IP>                   -> netname, OriginAS, CIDR
          |
          v
[2] From ASN to all the CIDR prefixes
     +-- amass intel -asn <ASN>             -> list of IP blocks
     +-- bgp.he.net (BGP Toolkit web)       -> prefixes + peers
     -> IP scope for active network scanning
          |
          v
[3] Subdomains from Certificate Transparency
     +-- curl crt.sh?q=%25.target.com       -> all the names in the certificates
     +-- ctfr -d target.com / subfinder     -> aggregation of CT sources
     -> hidden subdomains (vpn, dev, jenkins, admin)
          |
          v
[4] Validation and prioritization
     +-- filter live hosts, prioritize non-prod environments and remote accesses
          |
          v
[OUTPUT] Complete perimeter (IP + DNS) -> 02-network-scanning, 03-web-attacks, shodan-censys
```

---

## Reference Tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `whois` | OSINT | CLI | IP/domain resolution to netname, ASN, contacts, CIDR |
| `amass intel` | OSINT/ASN | CLI | From org name to ASN and IP ranges, CT aggregation |
| `crt.sh` | Certificate Transparency | Web / API | Subdomain enumeration from the CT logs |
| `ctfr` | Certificate Transparency | CLI (Python) | Subdomain enumeration via CT logs |
| `subfinder` | Subdomain enum | CLI | Multi-source aggregation (including CT) of subdomains |
| `bgp.he.net` | ASN/BGP | Web | BGP Toolkit: prefixes, peers, AS graph |
| `dnsx` / `httpx` | Validation | CLI | Validation of live hosts from the found subdomains |

> **Recommended modern tool:** `amass` (OWASP) integrates in a single tool the ASN intelligence (`amass intel`), the enumeration from Certificate Transparency and the passive DNS correlation, replacing the combination of whois + crt.sh + separate tools. For CT alone, `subfinder -d target.com -all` is faster and aggregates dozens of passive sources.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Network Info: IP Addresses | `T1590.005` | Identification of the CIDR blocks owned by the target via WHOIS and amass intel (INTEL-005) |
| Reconnaissance | Gather Victim Network Info: Network Topology | `T1590.004` | Reconstruction of the network perimeter via ASN and announced BGP prefixes (INTEL-005) |
| Reconnaissance | Search Open Technical Databases: WHOIS | `T1596.002` | Querying of the RIR WHOIS registries to associate IP, organization and ASN (INTEL-005) |
| Reconnaissance | Search Open Technical Databases: Digital Certificates | `T1596.003` | Enumeration of hidden subdomains via the Certificate Transparency logs (INTEL-005) |
| Reconnaissance | Gather Victim Network Info: DNS | `T1590.002` | Discovery of internal subdomains (vpn, dev, jenkins) from the Subject Alternative Names of the certificates (INTEL-005) |

---

> **Note:** The WHOIS, ASN and Certificate Transparency queries documented in this section were performed on public registries and logs, without any contact with the targets' infrastructure. The domains used are authorized targets for educational purposes or public bug bounty programs. Perimeter enumeration alone does not constitute access: no active scan or connection attempt was performed on the identified ranges without explicit authorization.
