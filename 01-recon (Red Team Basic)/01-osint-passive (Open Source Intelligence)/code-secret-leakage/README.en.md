> **English** | [Italiano](README.md)

# Secret & Code Leakage: GitHub/GitLab Dorking and Secrets in Public Repositories

> - **Phase:** Reconnaissance - Passive Information Gathering (source code intelligence)
> - **Visibility:** Zero - search on public repositories and third-party indexes (GitHub search, GitLab, search engines); no contact with the target's infrastructure
> - **Prerequisites:** Name of the organization or target domain, free GitHub account (for authenticated search), list of employee emails/usernames (from `email-harvesting/` and `user-enumeration/`)
> - **Output:** Exposed secrets (API keys, credentials, tokens, private keys), internal configurations, finding OSINT-006

---

## Introduction

The leakage of secrets in public code repositories is one of the most frequent and underestimated initial-access vectors in real breaches. The dynamic is always the same: a developer mistakenly commits a configuration file, an environment variable or a script containing credentials, and even if they remove the file in the next commit, the secret remains permanently in the repository's **git history**. Anyone can recover it with a simple `git log`.

Unlike other OSINT techniques that produce clues, code leakage often produces **directly usable** credentials: a valid AWS access key, a database token, an SMTP password. This is why the severity is typically `High` or `Critical`: one goes from reconnaissance to access in a single jump, without any exploitation phase.

The surface to analyze is twofold:
- **Official repositories of the organization:** code published intentionally but with forgotten secrets.
- **Personal repositories of the employees:** a developer who brings a corporate snippet home into a public personal project. This is the reason why the list of usernames collected in `user-enumeration/` (OSINT-004) is a direct prerequisite of this phase.

This technique sits in the `Reconnaissance` tactic of MITRE ATT&CK as `Search Open Technical Databases` and immediately feeds `07-post-exploitation/02-credential-dumping/` (the credentials found) and `10-cloud-security/` (the exposed cloud keys).

---

## Folder Structure

```
code-secret-leakage/
+-- README.md            <- this file (OSINT-006: secrets in public repositories)
+-- img/                 <- lab screenshots (GitHub search, gitleaks/trufflehog output)
```

---

## Manual Search: GitHub/GitLab Dorking

**Finding ID:** `OSINT-006` | **Severity:** `Variable (High / Critical)`

### Operational Context

Searching on GitHub exploits the advanced operators (`org:`, `filename:`, `path:`, `language:`) combined with typical secret patterns. It is the equivalent of Google Dorks (`google-dorks/`, OSINT-003) applied to source code. The severity depends on the secret found: a test connection string is `High`, a still-valid production AWS key is `Critical`.

### Execution

Queries to run in the GitHub search bar (requires login), targeting the target organization:

```
# Generic secrets associated with the organization name or domain
"target.com" password
"target.com" api_key
org:TargetCorp password

# Typical configuration files that contain secrets
org:TargetCorp filename:.env
org:TargetCorp filename:config.php DB_PASSWORD
org:TargetCorp filename:.npmrc _auth
filename:wp-config.php DB_PASSWORD "target.com"

# Private keys and cloud credentials
org:TargetCorp filename:id_rsa
org:TargetCorp "AKIA"                 # AWS Access Key ID prefix
org:TargetCorp "-----BEGIN RSA PRIVATE KEY-----"

# Search on the employees' personal repositories (from user-enumeration/)
user:employee-name "target.com"
```

Expected output (GitHub search result):

```
Showing 3 available code results

TargetCorp/legacy-api  -  config/database.yml
  production:
    adapter: mysql2
    username: root
    password: Pr0dDB_2021!            <-- OSINT-006 (Critical): production DB credentials

TargetCorp/deploy-scripts  -  .env.backup
  AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE   <-- AWS key in cleartext
  AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/...  <-- to validate (see Ethical Handling)
```

> [Screenshot placeholder: capture the GitHub search results on the target (with the secrets obscured/redacted before publication) and save it to `./img/`.]

<!-- screenshot placeholder: GitHub Dorking results (img/github-dorking-PLACEHOLDER.jpg) -->

> **Critical ethical note:** a secret found must NEVER be tested to verify its validity by accessing the target's infrastructure without authorization. Validity is declared as "potentially active" in the report. In an authorized engagement, the test is explicitly agreed in the scope.

---

## Automated Search: gitleaks and TruffleHog

### Operational Context

Manual search finds the obvious secrets, but does not scale over the complete **git history** of a repository with thousands of commits. gitleaks and TruffleHog automate the scan of the entire history by applying hundreds of regexes and, in the case of TruffleHog, the **active verification** of the validity of the secrets (optional, to be used only with authorization).

### Execution with gitleaks

gitleaks scans a cloned repository (including all history) or a directory:

```Bash
# Clone the public target repository
git clone https://github.com/TargetCorp/legacy-api.git
cd legacy-api

# Scan the entire git history looking for secrets
gitleaks detect --source . --report-format json --report-path leaks.json -v
```

Expected output:

```
    Finding:     password: Pr0dDB_2021!
    Secret:      Pr0dDB_2021!
    RuleID:      generic-api-key
    Commit:      a3f9c1e8...                       <-- the secret is in the history
    File:        config/database.yml
    Author:      dev@target.com
    Date:        2021-03-14T09:22:11Z
    ...
    leaks found: 4                                 <-- OSINT-006
```

### Execution with TruffleHog

TruffleHog can scan a GitHub organization directly and, with `--only-verified`, distinguish the still-active secrets (verification with the provider):

```Bash
# Scan an entire remote repository without cloning it
trufflehog github --repo=https://github.com/TargetCorp/deploy-scripts

# Scan an entire organization (requires a GitHub token)
trufflehog github --org=TargetCorp --only-verified
```

Expected output:

```
Found verified result                              <-- secret CONFIRMED active
Detector Type: AWS
Decoder Type: PLAIN
Raw result: AKIAIOSFODNN7EXAMPLE
Repository: https://github.com/TargetCorp/deploy-scripts
Timestamp: 2021-06-02 14:03:55
Line: 12
```

> [Screenshot placeholder: capture the output of gitleaks (JSON report) and of TruffleHog with the verified results, with the secrets redacted.]

### Analysis of the Results / Documented Finding

The fundamental operational distinction is between **secret present** and **secret valid**. gitleaks finds patterns that resemble secrets (high recall, many false positives); TruffleHog with `--only-verified` confirms which ones are still active with the provider. In a professional report:

- A secret found but not tested: `High` - "potentially active credential, requires immediate rotation".
- A secret verified as active (only if the scope authorizes the verification): `Critical` - direct access available.

---

## Lab Experience

The scan was conducted on repositories we own and on authorized educational targets, never on third-party code. The comparison between the two tools was instructive: gitleaks, based on patterns and entropy, produces a larger number of raw findings, many of them false positives (high-entropy strings that are not real secrets, such as hashes or identifiers), whereas TruffleHog, with its validity verification, significantly reduced the noise by confirming only a subset of credentials. The methodologically most significant discovery is that the most dangerous secrets often live in the git history and not in the current code: a file removed in a later commit remains recoverable, which is why scanning the entire history and not just the checkout is essential. On the ethical side, we decided never to test the real validity of the identified secrets and to redact them in the report (showing only type, location and commit), treating the finding as an exposure to remediate and not as a credential to use.

Recommended approach for the lab in a controlled environment: create a test repository containing fake secrets (realistic but non-functional format) and verify that gitleaks and TruffleHog detect them in the history even after their removal with a subsequent commit. This demonstrates the key concept - "the removed secret remains in the history" - without exposing real credentials.

### Theoretical Analysis

git is a version control system based on immutable snapshots: every commit is an object identified by its SHA-1/SHA-256 hash, and the removal of a file in a subsequent commit only creates a new snapshot that does not contain the file, but **does not alter** the previous snapshots. The deleted file remains reachable with `git show <commit>:<path>` or `git log -p`. To really remove a secret one must rewrite the history (`git filter-repo`, BFG Repo-Cleaner) and force the push, an operation most developers do not perform. This structural property of git is the root cause why a committed secret must be considered **permanently compromised** and rotated, not simply removed.

TruffleHog's active verification exploits the fact that almost every provider offers a low-cost validation endpoint (e.g. `sts:GetCallerIdentity` for AWS, which confirms whether a key is valid without performing actions). This turns a list of potential secrets into a list of confirmed accesses.

---

## Recommended Operational Flow

```
[INPUT] Organization name + employee list (from OSINT-002, OSINT-004)
          |
          v
[1] Manual GitHub/GitLab Dorking
     +-- org:Target filename:.env / "AKIA" / DB_PASSWORD
     +-- user:<employee> "target.com"    # personal repos
     -> obvious secrets in the current code
          |
          v
[2] Automatic scan of the history (gitleaks)
     +-- gitleaks detect --source <repo> -v
     -> secrets hidden in the git history (high recall)
          |
          v
[3] Validity verification (TruffleHog --only-verified)
     +-- distinguishes active secrets from false positives
          |
          v
[4] Classification and Responsible Disclosure
     +-- High (present) / Critical (verified active)
          |
          v
[OUTPUT] Credentials -> 07-post-exploitation; cloud keys -> 10-cloud-security
```

---

## Real-World Scenario: Post-Reconnaissance Projection

> This section describes how OSINT-006 would fit into a real engagement.

### Attacker Perspective (Red Team)

**Starting point:** a valid AWS access key found in the history of a public deploy repository of the organization.

**Immediate next step:** enumeration of the key's permissions with `aws sts get-caller-identity` and `aws iam get-user`, followed by mapping of the accessible services (S3, EC2, IAM).

**Projected kill chain:**

```
OSINT-006: valid AWS access key in the git history
        |
        v
IAM permission enumeration (10-cloud-security/IAM-enumeration)
        |
        v
Access to S3 buckets / EC2 instances / secrets in Secrets Manager
        |
        v
IAM privilege escalation -> compromise of the cloud account
        |
        v
Data exfiltration / ransomware deployment on cloud infrastructure
```

**Potential impact:** a single exposed cloud key can lead to the total compromise of the cloud infrastructure without touching the perimeter network. Documented cases (e.g. Uber 2016, Codecov 2021) show how secrets in repositories caused multi-million-dollar breaches.

**Typical monetization vectors:**
- Data exfiltration from S3 buckets (PII, database backups)
- Cryptomining on EC2 instances launched with the stolen key (cost charged to the victim)
- Access Broker: resale of the confirmed cloud access

### Defender Perspective (Blue Team)

**Detection:** the use of the stolen key generates events in CloudTrail (AWS) from an anomalous IP and geolocation. GitHub itself offers "Secret Scanning" which automatically notifies the push of recognized secrets and, for some providers, triggers their automatic revocation.

**Indicators of Compromise (IOC):**
- CloudTrail events (`GetCallerIdentity`, `ListBuckets`) from external non-corporate IPs right after the push of a secret
- GitHub Secret Scanning alerts on the repository
- Use of an access key from a new region/user-agent

**Containment:** immediate revocation of the exposed key (IAM, deactivate/delete access key), rotation of all correlated credentials, CloudTrail analysis to determine whether it has already been used.

**Eradication and hardening:**
- Integrate a secret scanner into the CI/CD pipeline and as a pre-commit hook (`gitleaks protect`, GitHub Secret Scanning, `pre-commit`)
- Adopt a secret manager (AWS Secrets Manager, HashiCorp Vault) and forbid secrets in the code via policy
- Use short-lived credentials (STS temporary credentials, OIDC) instead of static keys
- Developer training: a committed secret must be rotated, not just removed

**Defensive lesson:** prevention must happen **before** the commit (pre-commit hook), because after the push the secret must be considered permanently compromised. The git history does not forget.

---

## Reference Tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| GitHub Code Search | Source code intel | Web (authenticated) | Manual dorking on org and employee repositories |
| `gitleaks` | Secret scanning | CLI | Git history scan with regex, high recall |
| `TruffleHog` | Secret scanning | CLI | Scan + active verification of the validity of the secrets |
| `GitGraber` | Secret monitoring | CLI (Python) | Real-time monitoring of GitHub for keywords |
| `GitHub Secret Scanning` | Secret detection | Web (native) | Provider-side automatic detection and revocation (defensive) |
| `noseyparker` | Secret scanning | CLI | High-performance scanner for large data volumes |

> **Recommended modern tool:** `TruffleHog v3` with the `--only-verified` option is the single most effective tool for an engagement, because it eliminates the noise of false positives by confirming which secrets are really active with the provider. On the defensive side, `gitleaks protect --staged` as a pre-commit hook blocks secrets before they enter the history.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Search Open Technical Databases | `T1596` | Search for secrets and configurations in the target's public code repositories (OSINT-006) |
| Reconnaissance | Search Open Websites/Domains: Search Engines | `T1593.002` | Use of the GitHub/GitLab search operators to locate configuration files and credentials (OSINT-006) |
| Credential Access | Unsecured Credentials: Credentials In Files | `T1552.001` | Extraction of credentials, API keys and private keys from the files exposed in the git history (OSINT-006) |
| Credential Access | Unsecured Credentials: Cloud Instance Metadata / Keys | `T1552.005` | Recovery of cloud access keys (AWS/Azure/GCP) exposed in the public code (OSINT-006) |

---

> **Note:** The code leakage searches documented in this section were conducted for educational purposes on own or authorized repositories. No secret possibly identified was used to access third-party systems. In a real context, exposed secrets must be handled according to the principle of Responsible Disclosure, notifying the owner for immediate rotation without ever testing their operability outside the authorized scope.
