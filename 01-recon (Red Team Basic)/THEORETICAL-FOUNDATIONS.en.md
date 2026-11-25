> **English** | [Italiano](THEORETICAL-FOUNDATIONS.md)

# Theoretical foundations - module 01: reconnaissance

> - **Level:** Academic analysis (theoretical complement to the operational READMEs of the module)
> - **Purpose:** Provide the formal adversary model, the information-theoretic foundations and the quantitative analysis of reconnaissance, with reference to the primary literature.
> - **Prerequisites:** Operational READMEs of module 01 (OSINT-, SCAN-, DNS-, INTEL-); basic notions of information theory and probability theory.

---

## Abstract

Reconnaissance is commonly presented as a collection of techniques and tools (OSINT, port scanning, DNS enumeration). This document instead frames it as a formal problem: the reduction of the adversary's uncertainty about the target's configuration. Adopting the Dolev-Yao adversary model as a baseline and the attack surface metric of [Manadhata & Wing 2011], it shows that reconnaissance is quantifiable in information-theoretic terms (information gain per observation) and that the advent of Internet-wide scanning [Durumeric et al. 2013a] structurally changed the economics of the phase. The defensive implications are derived: since public information is irreversible, the only effective defensive lever is attack surface minimization, not concealment.

---

## 1. The adversary model

The reconnaissance adversary `A_rec` is defined as a specialization of the network attacker formalized by [Dolev & Yao 1983]. In the Dolev-Yao model the adversary controls the communication channel (can observe, intercept, delay and inject messages) but is computationally bounded: it cannot break the cryptographic primitives assumed secure. For the reconnaissance phase this model is restricted to two profiles distinct in capability and observability:

1. **Passive adversary `A_pass` (OSINT):** does not interact with the target. It collects exclusively information already public or exposed to third parties (WHOIS registries, DNS, Certificate Transparency, archives, metadata). Its observability by the defender is null: it generates no traffic toward the target perimeter. It is the profile of [Durumeric et al. 2013b] applied to the certificate ecosystem.

2. **Active adversary `A_act` (scanning):** interacts directly with the target (port scan, banner grabbing, direct DNS queries). It obtains richer and more up-to-date information, but at the cost of non-null observability: every probe is potentially recordable by an IDS or a perimeter log.

The formal objective of both profiles is not "to find vulnerabilities" but a more precise intermediate objective: **to maximize the information about the target's configuration** (topology, services, versions, technologies, exposed surface) that will feed the subsequent phases of the kill chain [Hutchins et al. 2011]. This distinction is crucial: reconnaissance is a stage of uncertainty reduction, not of exploitation.

---

## 2. Security properties at stake

Reconnaissance threatens the **confidentiality of infrastructural metadata**: not user data, but information about the structure of the system (which hosts exist, which services they expose, which technologies they use). Two frequently confused defensive properties must be distinguished:

- **Obscurity (weak property):** the assumption that the attacker's ignorance of the configuration provides protection. It is structurally fragile and violates the principle of [Kerckhoffs 1883] transposed to architecture: security must not depend on the secrecy of the configuration. A hidden SSID, a port on a non-standard number, an undocumented service are forms of obscurity.

- **Attack surface minimization (strong property):** the objective reduction of the number of points through which the system can be attacked. It is the property that reconnaissance cannot circumvent, because it acts on the existence of the entry points, not on their knowability.

The document argues, with [Manadhata & Wing 2011], that only the second property is defensively significant: reconnaissance empirically demonstrates the ineffectiveness of obscurity.

---

## 3. Theoretical foundations

### 3.1 Formalization of the attack surface

[Manadhata & Wing 2011] define the attack surface of a system as a three-dimensional measure over the set of resources through which an adversary can interact with the system: the **methods** (entry/exit points, e.g. ports and APIs), the **channels** (e.g. TCP, UDP, sockets), and the untrusted **data items** that cross the boundary. Each resource contributes to the surface in proportion to its damage-effort ratio. Reconnaissance is, in this frame, the process of empirical enumeration of the attack surface: the attacker reconstructs from the outside the same measure the defender should minimize from the inside.

### 3.2 Information-theoretic interpretation

Let `X` be the random variable representing the unknown configuration of the target, with initial Shannon entropy [Shannon 1949]:

```
H(X) = - sum_i  p(x_i) log2 p(x_i)
```

Every reconnaissance observation `o` (a response to a probe, a DNS record, a certificate) is evidence that updates the posterior distribution over `X`. The information gain of an observation is:

```
IG(o) = H(X) - H(X | o)
```

Optimal reconnaissance, in this frame, is the sequence of observations that maximizes the cumulative information gain per unit of cost (where the cost includes time and observability). This formulation explains why passive OSINT (`A_pass`) is preferred when available: it has null observability cost while reducing `H(X)`. It also explains why techniques such as subdomain enumeration via Certificate Transparency [Durumeric et al. 2013b] are so effective: the CT logs are a channel that deterministically (not probabilistically) exposes the existence of hosts, zeroing the entropy relative to that portion of the configuration.

### 3.3 The asymmetry of irreversibility

Information once published cannot be un-published in an information-theoretic sense: copies, caches, archives and third-party logs make it persistent. This generates a fundamental asymmetry: the defender must prevent the exposure *before* it happens, while the attacker can collect it at any subsequent moment. It is the counterpart, on the informational plane, of the principle that a leaked secret is compromised forever (also relevant to secrets management, module 10).

---

## 4. Quantitative analysis

### 4.1 The economics of scanning after ZMap

[Durumeric et al. 2013a] demonstrated that the entire public IPv4 addressing space (about 3.7 billion routable addresses) can be scanned on a single port in about 45 minutes from a single machine with gigabit connectivity, on commodity hardware. This result has a quantitative implication on the threat model: the marginal cost for the attacker of enumerating the entire Internet has collapsed by orders of magnitude compared to sequential scanners (nmap over lists, Masscan). The theoretical consequence is that the assumption "my host will not be found because it is not indexed" is falsified: every public host is, in practice, continuously enumerated. Defense cannot be based on the probability of not being discovered, which tends to 1 for being discovered.

### 4.2 Exhaustiveness of deterministic channels

While port scanning is a probabilistic sampling (subject to packet loss, rate limiting, filters), some reconnaissance channels are **deterministic and exhaustive**. The Certificate Transparency logs (RFC 6962) record every certificate issued by a compliant CA: an attacker who queries the CT logs obtains the complete enumeration of the subdomains for which a certificate has been issued, without sending a single packet to the target. In terms of section 3.2, these channels bring `H(X | o)` to zero for the enumerated component, with null observability cost. It is the case where `A_pass` dominates `A_act`.

---

## 5. Literature review

The adopted network attacker model derives from [Dolev & Yao 1983], whose foundational contribution was to abstract the adversary from specific implementations to a set of capabilities over the channel; their formalization remains the baseline of security protocols. The quantification of the attack surface rests on [Manadhata & Wing 2011], who first proposed a systematic and measurable metric, surpassing the earlier qualitative definitions. On the empirical plane, the pair of works by [Durumeric et al. 2013a] (ZMap) and [Durumeric et al. 2013b] (HTTPS ecosystem) redefined the understanding of Internet-scale reconnaissance, demonstrating both the feasibility of exhaustive scanning and the informational richness of deterministic channels such as CT. The information-theoretic framing appeals to [Shannon 1949]; the ineffectiveness of obscurity to the principle of [Kerckhoffs 1883]. The positioning of reconnaissance as the first stage of a sequence follows the Cyber Kill Chain of [Hutchins et al. 2011].

---

## 6. Limitations and open problems

1. **Non-preventability of passive reconnaissance.** Since `A_pass` operates exclusively on already-public information, no countermeasure exists that detects or prevents it: the defender can only reduce the information exposed a priori. This poses an insurmountable theoretical limit to defense against OSINT reconnaissance.

2. **Quantification of sufficiency.** There is no established metric that establishes *when* reconnaissance is "sufficient" for the adversary, that is, when the marginal information gain drops below the threshold useful for the subsequent phase. The formulation of section 3.2 is descriptive, not predictive.

3. **Deception as informational noise.** An open problem is the optimal design of countermeasures that increase `H(X | o)` for the attacker by injecting false but credible information (honeypots, honeytokens, falsified banners). The theory of how much noise is necessary to effectively degrade adversarial reconnaissance - without degrading legitimate operations - is unresolved and connects module 01 to module 08 (deception).

---

## 7. Synthesis and connection to practice

The operational READMEs of module 01 (findings with prefixes `OSINT-`, `SCAN-`, `DNS-`, `INTEL-`) concretely instantiate the framework formalized here: passive OSINT corresponds to `A_pass`, active network scanning to `A_act`, enumeration via Certificate Transparency is the practical manifestation of the deterministic channel of section 4.2. The unifying lesson is that every reconnaissance finding reduces `H(X)` for the attacker and expands the empirical knowledge of the attack surface [Manadhata & Wing 2011]; the correct countermeasure, consistent with section 2, is not to conceal (obscurity, weak) but to reduce the surface and inject controlled noise (minimization + deception, strong). This directly links module 01 to the hardening countermeasures (module 08) and closes the loop between the offensive and defensive perspectives.

---

## References

Subset of the master bibliography (`../REFERENCES.md`) relevant to this module:

- [Dolev & Yao 1983] - formal model of the network adversary.
- [Shannon 1949] - information-theoretic foundations.
- [Kerckhoffs 1883] - ineffectiveness of architectural secrecy.
- [Manadhata & Wing 2011] - attack surface metric.
- [Durumeric et al. 2013a] - ZMap, Internet-wide scanning.
- [Durumeric et al. 2013b] - HTTPS certificate ecosystem.
- [Hutchins et al. 2011] - Cyber Kill Chain.
- RFC 6962 - Certificate Transparency.
- NIST SP 800-115 - technical testing methodology.

---

> **Note:** This document is a theoretical complement for educational purposes and does not substitute the operational READMEs of the module, which contain the procedures, commands and findings. The citations refer to real and verifiable sources listed in `../REFERENCES.md`.
