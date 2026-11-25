> **English** | [Italiano](README.md)

# ScoutSuite - Multi-Cloud configuration audit

> - **Phase:** Cloud Security - Multi-Cloud Audit (Defense)
> - **Category:** Defensive - big picture of the security posture
> - **Prerequisites:** Read-only/audit credentials on the environment; ScoutSuite (NCC Group)
> - **Output:** Navigable HTML report of the multi-cloud security posture

- **Main tool:** ScoutSuite (NCC Group, multi-cloud)

---

## What it is and what it is for

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

## When to use it in the flow

- **First orientation audit:** to quickly understand where the risks are in an unknown environment
- **Unified multi-cloud view:** useful in organizations that use multiple providers, for an overall posture
- **Complementary to Prowler:** ScoutSuite for the overview and the navigation, Prowler for the depth and the formal compliance
- **Post-hardening verification:** re-run it after the corrections to confirm the reduction of the findings

---

## Related tools

| tool | role | relationship |
| :--- | :--- | :--- |
| `ScoutSuite` | multi-cloud audit | this tool (defensive) |
| `Prowler` | audit/compliance | complementary: depth vs overview (`../prowler/`) |
| `Pacu` / `AzureHound` | exploitation | the offensive counterparts |
| `PMapper` | iam graph | targeted analysis of the iam privesc paths |

> **Recommended modern tool:** use `ScoutSuite` for the quick overview and `Prowler` for the in-depth audit and compliance. In a multi-cloud environment, ScoutSuite offers a unified posture; for specific providers, the native tools (AWS Security Hub, Azure Defender for Cloud) complete the picture.

---

## MITRE ATT&CK mapping

| tactic (prevented) | technique | mitre id | role of the control |
| :--- | :--- | :--- | :--- |
| privilege escalation | valid accounts: cloud accounts | `T1078.004` | detects the iam configurations at risk |
| collection | data from cloud storage | `T1530` | detects the exposed buckets/storage |
| initial access | exploit public-facing application | `T1190` | detects the too-open security groups |

| defensive countermeasure (d3fend) | d3fend id | application |
| :--- | :--- | :--- |
| configuration inventory | `D3-CI` | navigable inventory of the multi-cloud configuration |
| platform hardening | `D3-PH` | identification of the misconfig to correct |

---

> **Note:** ScoutSuite is a non-intrusive defensive tool, to be run on environments owned or with authorization. Documented for educational and defensive purposes in an authorized context.
