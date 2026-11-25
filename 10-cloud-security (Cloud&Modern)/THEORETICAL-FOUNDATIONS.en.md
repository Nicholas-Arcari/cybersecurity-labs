> **English** | [Italiano](THEORETICAL-FOUNDATIONS.md)

# Theoretical foundations - module 10: cloud security

> - **Level:** Academic analysis (theoretical complement to the operational READMEs of the module)
> - **Purpose:** Formalize identity as the perimeter, the metadata SSRF as a confused deputy, cloud/container isolation as a configurable property and co-residency as a side channel.
> - **Prerequisites:** Operational READMEs of module 10 (CLOUD- findings); notions of access control, graph theory and system isolation.

---

## Abstract

The cloud dissolves the network perimeter and shifts security onto identity and configuration. The document formalizes it around four cores. **Identity as the perimeter** is the collapse of network-position-based access control toward credential-based access control, with IAM privilege escalation as reachability in a permission graph [Sheyner et al. 2002]. The **metadata SSRF** and the abuse of managed identities are cloud instances of the **confused deputy** [Hardy 1988]. The **isolation** of VMs and containers is a **configurable** property, not a physical barrier, with co-residency and side-channels [Ristenpart et al. 2009; Zhang et al. 2012] defining its limits. Everything is governed by the **Shared Responsibility Model** (NIST SP 800-145) and by surface reduction [Manadhata & Wing 2011], unifying module 10 with the principles of the entire path.

---

## 1. The adversary model

The cloud adversary operates in an environment where **every service is a public API endpoint** and the only access control is identity. Its typical entry paths: a leaked credential (module 04/07/09), an SSRF on an application (module 03), a compromised container or workload. The objective is escalation from a limited identity to control of the account/tenant/project, through the traversal of a permission graph (section 3.2). Compared to the other modules, the adversary does not cross a network perimeter but an **authorization graph**: its power depends on the IAM configuration, not on the topology. An honest-but-curious model of the tenancy neighbor is also adopted for co-residency (section 3.4).

---

## 2. Security properties at stake

- **Least privilege on identity:** every identity (human, managed identity, service account) must have only the necessary permissions; its violation turns a leak into an account takeover.
- **Intention-based authorization:** a privileged component must not act on behalf of an unauthorized principal (confused deputy, section 3.3).
- **Isolation of tenants and workloads:** co-residency must not allow information flows between tenants/containers (section 3.4).
- **Immutability of the secure configuration:** secure defaults must be not easily derogable (e.g. S3 Block Public Access), making the error hard and not just discouraged.

---

## 3. Theoretical foundations

### 3.1 The collapse of the perimeter and identity as access control

On-premise, access control is stratified geographically: network position (being "inside") confers implicit trust. The cloud removes this stratification: every service is reachable via API from anywhere, and position-based trust loses meaning. Access control concentrates entirely on identity: whoever presents a valid credential is authorized for what the credential permits. It is the forced realization of the Zero Trust principle, already introduced as an ideal in module 07 (section 6): the cloud does not offer the option of positional trust, so it imposes it. This theoretically unifies "identity is the new perimeter" (cloud) with the "transitivity of trust" (module 07, section 3.2): in both, the propagation of the compromise is determined by the credentials, not by the network.

### 3.2 IAM privilege escalation as reachability in a permission graph

The IAM configuration defines a **permission graph**: the nodes are identities and resources, the edges are the permissions that allow an identity to act on a resource or to assume/modify another identity. IAM privilege escalation is the search for a path from a limited identity to administrative privileges, exactly the reachability problem in attack graphs [Sheyner et al. 2002] (module 07, section 3.1). A seemingly harmless permission (`iam:CreatePolicyVersion`, `iam:PassRole`) is an edge that collapses the distance toward admin. Defense is the removal of edges (least privilege, permission boundaries, SCP) to disconnect the limited identities from the privileged nodes. This provides the theoretical basis for the fact that tools like PMapper (graph analysis of permissions) and Pacu (`iam__privesc_scan`) solve, offensively and defensively, the same reachability problem.

### 3.3 Metadata SSRF and managed identity as cloud confused deputy

Token theft via the metadata service and the abuse of managed identities/service accounts are cloud instances of the **confused deputy** [Hardy 1988] already formalized in module 03 (section 3.2). In the metadata SSRF, the web application is the deputy: it possesses the privileged position (reachability of the metadata endpoint, which delivers credentials to whoever queries it from the inside) and is induced by the attacker to use it on their behalf. In the managed identity abuse, the compromised resource is the deputy: it possesses the managed identity and inherits it to whoever controls it. The common root is **position-based trust** (the metadata trusts anyone who reaches it from the inside), the same assumption that section 3.1 identifies as dissolved in the correct model: the SSRF exploits the residue of positional trust that the cloud has not yet eliminated. The countermeasure (restricting outbound requests, Workload Identity, IMDSv2 with constraints) is the application of intention verification and least privilege.

### 3.4 Isolation as configuration: containers and co-residency

Isolation in the cloud is not a physical barrier but a **configurable** property, with two manifestations. For **containers**, isolation derives from mechanisms of the shared kernel (namespaces, cgroups, capabilities), not from a hypervisor: it is effective if configured correctly, bypassable if not (mounted Docker socket, `--privileged`). NIST SP 800-190 codifies this risk model. The correct property is "the container is isolated only as much as I configure it", and the escape is the exploitation of an incomplete isolation, not the breaking of a barrier (module 10, runtime security). For **VMs**, [Ristenpart et al. 2009] demonstrate that the co-residency of different tenants on the same physical hardware opens side channels: an attacker can deliberately place its own VM on the same host as the victim and, via side-channels of the shared cache, extract information - up to cryptographic keys [Zhang et al. 2012]. This shows that the logical isolation of tenants does not imply the physical isolation of resources, and that hardware sharing is an autonomous attack surface.

---

## 4. Quantitative analysis

### 4.1 The probability of co-residency

[Ristenpart et al. 2009] quantify the feasibility of co-residency: they show that, with targeted launch strategies, an attacker can obtain co-residency with a target victim on a public cloud with non-negligible probability and at low cost, and that co-residency is verifiable via side-channels. The theoretical consequence is that the assumption "multi-tenancy is transparent and isolated" is quantitatively falsified: physical sharing has a measurable security cost. It is the reason why very-high-sensitivity workloads resort to dedicated tenancy (dedicated instances), which eliminates co-residency at the cost of the efficiency of multi-tenancy.

### 4.2 The asymmetric cost of the insecure default

The case of public S3 buckets quantitatively illustrates the principle "make the error hard". A secure default (private bucket) protects until `n` operators make a mistake; the probability that at least one makes a bucket public grows as `1 - (1-p)^n` (the same formula as the weakest link, module 05, section 4.2), tending to 1 at scale. "Block Public Access" at the account level removes the entire class of the error: it does not reduce `p`, it zeroes the space in which the error has effect. It is the cloud translation of the principle, already seen in prepared statements (module 03), whereby structurally eliminating a class beats chasing the instances.

---

## 5. Literature review

Co-residency and cross-VM side-channels are demonstrated by [Ristenpart et al. 2009] and [Zhang et al. 2012], foundational references of cloud isolation security. The confused deputy is by [Hardy 1988]. Privilege escalation as reachability rests on the attack graphs of [Sheyner et al. 2002]. Least privilege and the design principles are by [Saltzer & Schroeder 1975]; surface reduction by [Manadhata & Wing 2011]. The normative definitions and risk models are in NIST SP 800-145 (cloud definition), NIST SP 800-190 (containers) and NIST SP 800-63B (identity). Secrets management appeals to the entropic and cost principles of modules 04 and 07.

---

## 6. Limitations and open problems

1. **IAM complexity as an irreducible surface.** The space of IAM configurations (hundreds of services, thousands of actions, policies that compose) is so vast that the exhaustive manual analysis of the privesc paths is intractable; the graph tools (PMapper) are necessary but suffer from the combinatorial explosion of attack graphs [Sheyner et al. 2002].

2. **Isolation without physical sharing.** Completely eliminating the co-residency side-channels [Ristenpart et al. 2009; Zhang et al. 2012] requires giving up multi-tenancy (dedicated tenancy), sacrificing the economic efficiency that is the raison d'etre of the cloud. The isolation/efficiency trade-off remains open.

3. **Residual positional trust.** The metadata SSRF (section 3.3) shows that the cloud has not yet eliminated every residue of position-based trust. The complete realization of Zero Trust at the workload level (every request authenticated and authorized, no implicit internal trust) is partial in real infrastructures.

---

## 7. Synthesis and connection to practice

The `CLOUD-` findings of the module instantiate this framework: IAM privilege escalation (CLOUD-001) is the reachability in the permission graph of section 3.2; the metadata SSRF and the abuse of managed identity/service account (CLOUD-003/004) are the confused deputies of section 3.3; the container escape (CLOUD-006) is the isolation-as-configuration of section 3.4; the exposed S3 buckets (CLOUD-002) illustrate the cost of the insecure default of section 4.2; auditing and hardening (CLOUD-008/010) are the edge removal and surface reduction. The documented countermeasures - least privilege, permission boundaries, Block Public Access, Workload Identity, Pod Security, shift-left - are the operational realizations of the principles formalized here. The document closes the path by showing that the cloud does not introduce new principles but takes to the extreme those already encountered: the confused deputy (module 03), the transitivity of trust (module 07), the surface reduction (modules 01, 08), the structural elimination of error classes (module 03). Identity as the perimeter is the final synthesis: where position no longer confers trust, security is the correctness of the access configuration.

---

## References

Subset of the master bibliography (`../REFERENCES.md`) relevant to this module:

- [Ristenpart et al. 2009] - co-residency and side-channels in the public cloud.
- [Zhang et al. 2012] - cross-VM side-channels and key extraction.
- [Hardy 1988] - confused deputy (basis of SSRF/metadata).
- [Sheyner et al. 2002] - attack graphs (IAM privesc as reachability).
- [Saltzer & Schroeder 1975] - least privilege and design principles.
- [Manadhata & Wing 2011] - attack surface reduction.
- NIST SP 800-145 (cloud), 800-190 (containers), 800-63B (identity).

---

> **Note:** Document for educational purposes, complementary to the operational READMEs. The citations refer to real sources listed in `../REFERENCES.md`.
