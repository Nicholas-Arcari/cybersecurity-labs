> **English** | [Italiano](README.md)

# Cloud_enum - cloud asset recon

> - **Phase:** Cloud Security - Reconnaissance (multi-cloud)
> - **Category:** Recon - discovery of exposed assets
> - **Prerequisites:** A name/keyword of the target (company, project); cloud_enum (Python)
> - **Output:** List of public cloud assets associated with the target (buckets, storage, services)

- **Main tool:** cloud_enum (multi-cloud OSINT)

---

## What it is and what it is for

`cloud_enum` is an OSINT reconnaissance tool for the cloud: given a keyword (typically the name of the company or the project), it generates plausible permutations and checks which public cloud assets exist and are accessible, across the three major providers. It is the starting point of a cloud assessment from the outside: mapping what the target exposes without authentication.

It exploits the fact that cloud assets have global and often predictable names (`company-backup`, `company-assets`, `company-prod`). By testing the permutations of a keyword, it discovers S3 buckets, Azure Blob storage, Google Storage, and other services the target has exposed - often without knowing it.

---

## Usage

```Bash
# Multi-cloud reconnaissance starting from a keyword
python3 cloud_enum.py -k companyname -k companyname-prod
```

```
[+] AWS S3 Bucket FOUND:   companyname-backup.s3.amazonaws.com   (OPEN)   <-- accessible
[+] Azure Blob FOUND:      companyname.blob.core.windows.net
[+] GCP Storage FOUND:     companyname-assets  (public)
[!] 3 public assets discovered for the keyword 'companyname'
```

---

## When to use it in the flow

- **First step of an external cloud assessment:** before having credentials, mapping the public surface of the target
- **Input for the targeted attacks:** the discovered buckets feed the S3 attacks (`../../01-providers-infrastructure (IaaS & PaaS)/AWS (Amazon Web Services)/S3-buckets-attacks/`)
- **Defensive verification:** an organization can run it on itself to discover what it inadvertently exposes (shadow IT, forgotten assets)

---

## Related tools

| tool | role | relationship |
| :--- | :--- | :--- |
| `cloud_enum` | multi-cloud recon | this tool |
| `s3scanner` | s3 enum | focused on aws buckets |
| `Prowler` / `ScoutSuite` | defensive audit | find the exposed assets from inside the account |

> **Recommended modern tool:** `cloud_enum` for the external multi-cloud recon. From the defensive side, the audit from inside the account (`Prowler`/`ScoutSuite`) is more complete because it sees all the assets, not just those with a guessable name.

---

## MITRE ATT&CK mapping

| tactic | technique | mitre id | description |
| :--- | :--- | :--- | :--- |
| reconnaissance | search open websites/domains | `T1593` | discovery of public cloud assets via name permutation |
| discovery | cloud infrastructure discovery | `T1580` | enumeration of the exposed cloud assets |

---

> **Note:** cloud_enum must be used for the recon of assets owned by the author or with explicit authorization. Targeted enumeration of third-party assets may violate the providers' terms. Documented for educational and authorized security assessment purposes.
