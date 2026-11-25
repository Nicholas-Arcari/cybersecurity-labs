> **English** | [Italiano](README.md)

# Cloud Asset Discovery: Exposed S3 Buckets, Azure Blob and GCP Storage

> - **Phase:** Reconnaissance - Infrastructure Intelligence (cloud attack surface)
> - **Visibility:** Low - the enumeration of the bucket names happens via DNS resolution and HTTP requests toward the cloud providers' endpoints (AWS/Azure/GCP), not toward the target's infrastructure; some tools query only passive databases (Zero)
> - **Prerequisites:** Name of the organization, domain and brand of the target, list of corporate keywords (from previous OSINT)
> - **Output:** Exposed cloud storage buckets, anonymous read/write permissions, sensitive contents, finding INTEL-006. Direct bridge toward `10-cloud-security/`

---

## Introduction

Modern organizations store a growing share of their data in cloud storage: AWS S3 buckets, Azure Blob Storage, Google Cloud Storage. These services are designed to be reachable via the Internet through a predictable URL, and their security depends entirely on the configuration of the permissions. A single misconfiguration - a bucket set as "public" instead of "private" - exposes the content to anyone who knows or guesses the bucket name.

The characteristic that makes this technique powerful in the reconnaissance phase is the **predictability of the naming**. An S3 bucket is reachable at `https://<bucket-name>.s3.amazonaws.com`, and the bucket name is globally unique but often follows predictable conventions based on the brand: `targetcorp-backups`, `target-prod-assets`, `target-dev`, `targetcorp-logs`. An attacker generates these permutations and checks which ones exist and which are readable anonymously. No access to the target's infrastructure is required: one queries only the cloud providers' endpoints.

The severity is `Variable`: a bucket exposing public static assets (images of a site) is `Informational/Medium`, while a readable bucket containing database backups, PII or secrets is `Critical`. An anonymously **writable** bucket is always `Critical`, because it allows altering the contents (e.g. replacing a JavaScript file served to users, a supply chain technique).

This section is the natural bridge between reconnaissance (module 01) and cloud security (module 10): the asset discovered here is analyzed in depth in `10-cloud-security/01-providers-infrastructure/`.

---

## Folder Structure

```
cloud-asset-discovery/
+-- README.md            <- this file (INTEL-006: exposed cloud storage)
+-- img/                 <- lab screenshots (cloud_enum, accessible bucket, grayhatwarfare)
```

---

## Enumeration of the Cloud Storage Buckets

**Finding ID:** `INTEL-006` | **Severity:** `Variable (Medium / Critical)`

### Operational Context

The enumeration combines two approaches: **permutation generation** of the bucket names based on the target's brand, and **search on passive indexes** of buckets already discovered by third parties (GrayHatWarfare). The first is active toward the provider's endpoints but invisible to the target; the second is completely passive.

### Execution with cloud_enum

`cloud_enum` checks in parallel the existence of resources on AWS, Azure and GCP starting from a keyword:

```Bash
# Multi-cloud enumeration starting from the target's brand
cloud_enum -k targetcorp -k target-corp -k target

# With custom mutations (dev, prod, backup, logs, assets...)
cloud_enum -k targetcorp -m mutations.txt
```

Expected output:

```
[+] AWS S3 Bucket found: targetcorp-assets.s3.amazonaws.com
      -> ACCESS: OPEN (public read)              <-- INTEL-006 (High): anonymous read
[+] AWS S3 Bucket found: targetcorp-backups.s3.amazonaws.com
      -> ACCESS: Protected (403)                 <-- exists but not readable (naming confirmed)
[+] Azure Blob found: targetcorp.blob.core.windows.net
      -> Container 'public' -> OPEN
[+] GCP Bucket found: target-prod.storage.googleapis.com
      -> ACCESS: OPEN                            <-- INTEL-006 (content to verify)
```

### Content verification (readable bucket)

For AWS buckets with anonymous read, the list of contents is obtained without credentials:

```Bash
# Anonymous listing of the content of a public S3 bucket
aws s3 ls s3://targetcorp-assets --no-sign-request

# Download of the content (only if authorized by the scope)
aws s3 sync s3://targetcorp-assets ./loot --no-sign-request
```

Expected output:

```
2023-11-02 14:03:22      15234 logo.png
2023-11-02 14:03:25    1048576 database_backup_2023.sql   <-- INTEL-006 (Critical): exposed DB backup
2023-11-02 14:03:28       2048 .env.production            <-- application secrets (see OSINT-006)
```

> [Screenshot placeholder: capture the output of cloud_enum with the found buckets and the listing of the readable bucket (with the sensitive file names highlighted and any real content redacted).]

<!-- screenshot placeholder: cloud_enum - exposed buckets (img/cloud-enum-PLACEHOLDER.jpg) -->

### Passive search on GrayHatWarfare

GrayHatWarfare maintains a searchable index of hundreds of millions of files in already-discovered public buckets:

```
Web search on buckets.grayhatwarfare.com:
  keyword: targetcorp
  keyword: target.com
  filters: extension (.sql, .bak, .env, .pem, .key)
```

> **Critical ethical note:** the listing of a public bucket is generally considered access to a resource made public by the owner, but the **download** of sensitive data (PII, backups) may constitute unauthorized access depending on the jurisdiction and the scope. In an engagement, the download is explicitly agreed; in educational reconnaissance one limits oneself to documenting the existence and readability without exfiltrating.

---

## Lab Experience

To operate safely, a controlled lab was set up by creating a test S3 bucket with public-read permissions and fake files, so as to verify the tool's discovery capability without touching real third-party data; the broader enumeration was limited to keywords we own or to programs that explicitly authorize cloud recon in the scope. Execution highlighted the fundamental distinction between existing but protected buckets (which respond 403, confirming only the validity of the naming) and actually open buckets (with listable content): most of the guessed names fall into the first case, and the real finding is the second. When accessible content was identified, we decided never to download potentially sensitive files: the exposure was documented by noting the bucket name, permissions and type of files listed, enough to demonstrate the risk without exfiltrating data. This discipline is the difference between an assessment and a breach.

Typical attention points:

- A bucket that responds `403 Forbidden` is not a failure: it confirms that the name exists (the corporate naming is correct) and must be noted as a protected asset. A `404` indicates that the name does not exist.
- The bucket names are globally unique on AWS: if `targetcorp-backups` exists but is protected, an attacker cannot create a namesake, but the confirmation of the naming pattern guides further permutations (`targetcorp-backups-2`, `targetcorp-db-backups`).
- The quality of the result depends on the mutation wordlist: include terms like `backup`, `bak`, `prod`, `dev`, `staging`, `logs`, `assets`, `static`, `data`, `dump`, `private`.

### Theoretical Analysis

The security model of cloud storage is based on explicit permissions (ACLs and bucket policies), not on the secrecy of the name. The globally unique and predictable naming is a design choice that favors accessibility, under the assumption that the access control is configured correctly. The misconfiguration arises when this assumption is violated: a bucket created "public" to serve static assets ends up also containing sensitive data, or a too-permissive policy (`"Principal": "*"`) grants read to anyone.

This is a manifestation of the cloud **shared responsibility** model: the provider guarantees the security *of* the infrastructure (the S3 service is secure), but the security *in* the infrastructure (the configuration of the bucket permissions) is the customer's responsibility. Most documented cloud data leaks do not derive from a provider vulnerability but from a customer misconfiguration. The operational link with `10-cloud-security/01-providers-infrastructure/S3-buckets-attacks/` is direct: reconnaissance finds the bucket, the cloud module analyzes its policy and impact.

---

## Recommended Operational Flow

```
[INPUT] Brand, domain and keywords of the target
          |
          v
[1] Passive search on pre-existing indexes
     +-- GrayHatWarfare (buckets.grayhatwarfare.com)   -> already-known buckets
          |
          v
[2] Enumeration by permutation (multi-cloud)
     +-- cloud_enum -k <brand>                         -> AWS/Azure/GCP in parallel
     +-- mutations: backup, prod, dev, logs, assets
     -> existing buckets (open / 403 protected)
          |
          v
[3] Readability and content verification
     +-- aws s3 ls s3://<bucket> --no-sign-request     -> anonymous listing
     -> classification: Informational (public assets) / Critical (PII, backups, secrets)
          |
          v
[4] Documentation without exfiltration
     +-- record existence, permissions and type of exposed data
          |
          v
[OUTPUT] Exposed cloud assets -> 10-cloud-security/01-providers-infrastructure/S3-buckets-attacks/
```

---

## Real-World Scenario: Post-Reconnaissance Projection

> This section describes how INTEL-006 would fit into a real engagement.

### Attacker Perspective (Red Team)

**Starting point:** an S3 bucket of the organization with anonymous read enabled, containing a database backup and a `.env.production` file.

**Immediate next step:** download of the `.env` to extract application credentials and API keys, and of the database backup for access to the data and to password hashes to crack offline.

**Projected kill chain:**

```
INTEL-006: public S3 bucket (DB backup + .env)
        |
        v
Credential extraction from .env + hashes from DB backup
        |
        v
Offline password cracking (04-system-exploitation/05-password-cracking)
        |
        v
Access to applications/cloud with valid credentials (10-cloud-security)
        |
        v
Data exfiltration / lateral movement in the cloud
```

**Potential impact:** the exposure of a bucket with sensitive data is one of the most common causes of mass data breaches (documented cases: Accenture, Verizon, US Voter Records - all public S3 buckets). A single bucket can expose millions of records without any exploitation technique.

**Typical monetization vectors:**
- Sale of the exfiltrated data (PII, customer databases) on the dark web
- "Leakware" ransomware: threat to publish the already-exfiltrated data
- Supply chain: if the bucket is writable, alteration of files served to users (JS/assets)

### Defender Perspective (Blue Team)

**Detection:** anonymous access to an S3 bucket is recorded in S3 Server Access Logs and CloudTrail (if enabled). A spike of `GetObject`/`ListBucket` requests from unknown external IPs indicates exfiltration in progress. AWS also offers native alerts (S3 Block Public Access, Access Analyzer) that flag public buckets.

**Indicators of Compromise (IOC):**
- Anonymous `ListBucket`/`GetObject` requests (`Requester: anonymous`) in the S3 logs
- Anomalous download volume from a bucket toward external IPs
- AWS Access Analyzer or GuardDuty alerts on buckets with public access

**Containment:** immediately apply S3 Block Public Access at the account level, revoke the permissive bucket policy, rotate all the secrets possibly contained in the exposed files.

**Eradication and hardening:**
- Enable S3 Block Public Access at the organization level (default deny)
- Mandatory server-side encryption and bucket policy with the least-privilege principle
- Continuous scanning of the configuration with `Prowler`, `ScoutSuite` or AWS Config (see `10-cloud-security/Tooling/`)
- Physically separate the buckets of public assets from those with sensitive data

**Defensive lesson:** in the cloud, the perimeter is not the network but the configuration of the permissions. A public bucket is exposed to the entire Internet at the very moment of the misconfiguration, without the attacker needing to "get in" anywhere. Prevention is the "private" default applied at the account level.

---

## Reference Tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `cloud_enum` | Cloud recon | CLI (Python) | Multi-cloud enumeration (AWS/Azure/GCP) by keyword |
| `GrayHatWarfare` | Cloud recon | Web | Passive search on an index of already-discovered buckets |
| `awscli` | Cloud interaction | CLI | Anonymous listing/download of S3 buckets (`--no-sign-request`) |
| `S3Scanner` | Cloud recon | CLI | Enumeration and permission test of S3 buckets |
| `Prowler` | Cloud audit | CLI | Defensive audit of the configuration (see module 10) |
| `ScoutSuite` | Cloud audit | CLI | Multi-cloud posture assessment (see module 10) |

> **Recommended modern tool:** `cloud_enum` covers the three main providers in a single pass and is actively maintained. For an exclusively AWS target, `S3Scanner scan -f bucket_names.txt` checks in bulk the existence and permissions (READ/WRITE) of the buckets. On the defensive side, `Prowler` (`prowler aws`) proactively identifies all the public buckets of the account before an attacker does.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Search Open Technical Databases | `T1596` | Search for exposed cloud buckets on public indexes (GrayHatWarfare) and by name permutation (INTEL-006) |
| Reconnaissance | Gather Victim Host Info | `T1592` | Identification of the cloud storage assets owned by the target (INTEL-006) |
| Collection | Data from Cloud Storage | `T1530` | Enumeration and anonymous access to the contents of cloud buckets with public permissions (INTEL-006) |
| Credential Access | Unsecured Credentials: Credentials In Files | `T1552.001` | Extraction of credentials and secrets from files (.env, backups) contained in the exposed buckets (INTEL-006) |

---

> **Note:** The cloud asset enumeration documented in this section was performed for educational purposes on own test buckets or on targets that explicitly authorize cloud recon in the scope. Only the existence and readability of the buckets was documented, without exfiltrating third-party sensitive data. In the context of a real engagement, the download of contents must be agreed in the scope and any exposure must be handled according to the principle of Responsible Disclosure.
