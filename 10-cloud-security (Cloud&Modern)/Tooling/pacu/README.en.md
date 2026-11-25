> **English** | [Italiano](README.md)

# Pacu - AWS Exploitation Framework

> - **Phase:** Cloud Security - AWS Exploitation
> - **Category:** Offensive - the post-exploitation framework for AWS
> - **Prerequisites:** AWS credentials (even low-privilege); Pacu (Rhino Security Labs)
> - **Output:** Automated enumeration, privilege escalation and persistence on AWS

- **Main tool:** Pacu (Rhino Security Labs)

---

## What It Is and What It Is For

`Pacu` is often described as "the Metasploit for AWS": a modular exploitation framework to test the security of Amazon environments. As Metasploit organizes exploits into modules, Pacu organizes the cloud techniques (enumeration, privilege escalation, persistence, exfiltration) into modules callable on a set of imported credentials.

Its value is to automate what would manually require dozens of API calls. The `iam__privesc_scan` module, in particular, automatically checks the 20+ IAM privilege escalation techniques documented by Rhino Security, identifying whether a limited credential can elevate to administrator. It is the central tool of the AWS findings (`../../01-providers-infrastructure (IaaS & PaaS)/AWS (Amazon Web Services)/`, CLOUD-001).

---

## Usage

```Bash
# Start Pacu and import the credentials
pacu
> import_keys svc-deploy               # imports the compromised AWS keys
> run iam__enum_permissions            # enumerates the identity's permissions
> run iam__privesc_scan                # searches for the privilege escalation paths
```

```
[iam__privesc_scan] Confirmed path: CreatePolicyVersion -> AdministratorAccess
[iam__privesc_scan] The identity can elevate to admin   <-- privesc found
```

```Bash
# Other useful modules
> run s3__download_bucket              # exfiltration of accessible buckets
> run iam__backdoor_users              # persistence (new credentials)
```

---

## When to Use It in the Flow

- **After obtaining an AWS credential:** import and automatic enumeration of the permissions
- **Search for privilege escalation:** `iam__privesc_scan` as the first check on every credential
- **Attack simulation for the defender:** running Pacu on your own account reveals the privesc paths to close (the offensive equivalent of the Prowler/ScoutSuite audit)

---

## Related Tools

| Tool | Role | Relationship |
| :--- | :--- | :--- |
| `Pacu` | AWS exploitation | This tool (offensive) |
| `enumerate-iam` | Permission enum | Quick recon of the permissions |
| `Prowler` / `ScoutSuite` | Defensive audit | Find the same weaknesses from the defense side |
| `PMapper` | IAM graph | Graph analysis of the escalation paths |

> **Recommended modern tool:** `Pacu` is the standard for AWS exploitation. Its defensive symmetry are `Prowler`, `ScoutSuite` and `PMapper`: the same privesc paths Pacu exploits, these tools identify to close them. Using them together covers attack and defense.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Description |
| :--- | :--- | :--- | :--- |
| Discovery | Cloud Infrastructure Discovery | `T1580` | Automated enumeration of permissions and resources |
| Privilege Escalation | Valid Accounts: Cloud Accounts | `T1078.004` | Search for and exploitation of the IAM privesc paths |
| Persistence | Account Manipulation: Additional Cloud Credentials | `T1098.001` | Creation of persistence credentials |
| Collection | Data from Cloud Storage | `T1530` | Exfiltration of accessible buckets |

---

> **Note:** Pacu must be used exclusively on AWS accounts owned by the author or with explicit penetration test authorization. Using it on third-party accounts without permission is a crime and violates the AWS terms. Documented for educational and authorized security assessment purposes.
