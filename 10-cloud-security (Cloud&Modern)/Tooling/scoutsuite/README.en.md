> **English** | [Italiano](README.md)

# ScoutSuite - Multi-Cloud Configuration Audit

> - **Phase:** Cloud Security - Multi-Cloud Audit (Defense)
> - **Category:** Defensive - big picture of the security posture
> - **Prerequisites:** Read-only/audit credentials on the environment; ScoutSuite (NCC Group)
> - **Output:** Navigable HTML report of the multi-cloud security posture

- **Main tool:** ScoutSuite (NCC Group, multi-cloud)

---

## What It Is and What It Is For

`ScoutSuite` is a multi-cloud audit tool that produces a navigable big-picture view of the security posture of an environment. It collects the configuration through the provider's APIs (AWS, Azure, GCP, and others) and generates an HTML report that highlights the misconfigurations per service, with a snapshot of what is at risk.

Its strength is the overview. Where Prowler (`../prowler/`) excels in depth and compliance mapping, ScoutSuite excels in quickly giving the overall picture: which services have problems, where the risks concentrate, how the environment is configured as a whole. It is often the first tool to launch in a cloud audit to orient oneself, before going deep with Prowler.

---

## Usage

```Bash
# Audit of an AWS environment (generates a navigable HTML report)
scout aws
```

```
[+] Collecting the configuration via API...
[+] Analysis of 40+ services (IAM, S3, EC2, RDS, ...)
[+] Report generated: scoutsuite-report/aws-<account>.html

Dashboard: 12 Danger findings, 34 Warning
  IAM      -> 4 Danger (permissive policies, root without MFA)
  S3       -> 3 Danger (public buckets)                    <-- related CLOUD-002
  Security Groups -> 5 Danger (ports open to 0.0.0.0/0)
```

```Bash
# ScoutSuite supports multiple providers
scout azure
scout gcp
```

---

## When to Use It in the Flow

- **First orientation audit:** to quickly understand where the risks are in an unknown environment
- **Unified multi-cloud view:** useful in organizations that use multiple providers, for an overall posture
- **Complementary to Prowler:** ScoutSuite for the overview and the navigation, Prowler for the depth and the formal compliance
- **Post-hardening verification:** re-run it after the corrections to confirm the reduction of the findings

---

## Related Tools

| Tool | Role | Relationship |
| :--- | :--- | :--- |
| `ScoutSuite` | Multi-cloud audit | This tool (defensive) |
| `Prowler` | Audit/compliance | Complementary: depth vs overview (`../prowler/`) |
| `Pacu` / `AzureHound` | Exploitation | The offensive counterparts |
| `PMapper` | IAM graph | Targeted analysis of the IAM privesc paths |

> **Recommended modern tool:** use `ScoutSuite` for the quick overview and `Prowler` for the in-depth audit and compliance. In a multi-cloud environment, ScoutSuite offers a unified posture; for specific providers, the native tools (AWS Security Hub, Azure Defender for Cloud) complete the picture.

---

## MITRE ATT&CK Mapping

| Tactic (prevented) | Technique | MITRE ID | Role of the control |
| :--- | :--- | :--- | :--- |
| Privilege Escalation | Valid Accounts: Cloud Accounts | `T1078.004` | Detects the IAM configurations at risk |
| Collection | Data from Cloud Storage | `T1530` | Detects the exposed buckets/storage |
| Initial Access | Exploit Public-Facing Application | `T1190` | Detects the too-open security groups |

| Defensive countermeasure (D3FEND) | D3FEND ID | Application |
| :--- | :--- | :--- |
| Configuration Inventory | `D3-CI` | Navigable inventory of the multi-cloud configuration |
| Platform Hardening | `D3-PH` | Identification of the misconfig to correct |

---

> **Note:** ScoutSuite is a non-intrusive defensive tool, to be run on environments owned or with authorization. Documented for educational and defensive purposes in an authorized context.
