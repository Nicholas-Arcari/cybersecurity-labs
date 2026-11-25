> **English** | [Italiano](THEORETICAL-FOUNDATIONS.md)

# Theoretical Foundations - Active Directory and Kerberos

> Academic apparatus for module 11. It complements the operational READMEs (methodology, commands, MITRE)
> by providing their formal basis. It does not replace them: it grounds them and refers back to them.
> Citations: only real and verified sources (see References; entries merged into the master `REFERENCES.md`,
> section O).

## Abstract

Active Directory bases authentication on Kerberos v5 (RFC 4120), a ticket protocol derived from the
Needham-Schroeder symmetric-key model. The security of the domain does not depend on the cryptographic
robustness of Kerberos itself, which is sound, but on the assumptions the protocol makes about the
deployment: that the long-term keys of service accounts have high entropy, that replication privileges are
confined to Domain Controllers, and that accessory configurations (delegation, certificate authorities,
ACLs) respect the principle of least privilege. This chapter formalizes the adversary model, the expected
security properties, and the theoretical mechanisms behind the three techniques documented in the module
(Kerberoasting, AD CS ESC8, DCSync), showing that each is the violation of a specific deployment
assumption, not a break of the protocol.

## 1. Adversary Model

We adopt a Dolev-Yao style model [Dolev & Yao 1983] adapted to the internal-network context: the adversary
is not an unauthenticated remote attacker but an actor who has already gained a foothold in the domain.
Three capability levels are distinguished:

- **A1 - Authenticated low-privilege insider:** holds credentials of any domain account (obtained via
  phishing, password spraying, reused credentials). Can request Kerberos tickets for any SPN (the premise
  of Kerberoasting) and query LDAP read-only.
- **A2 - Network-positioned actor:** can intercept and forward traffic on the segment (the premise of NTLM
  relay) and induce authentications through coercion (e.g., PetitPotam, PrinterBug).
- **A3 - Account with delegated privileges:** holds an account that, through misconfiguration, has been
  granted sensitive rights (domain replication, write access to privileged objects) without being Domain
  Admin.

The adversary has neither physical access to the Domain Controller nor the ability to break standard
cryptographic primitives (AES, SHA-2). The channel is assumed observable and manipulable within the limits
of the network position (A2). This model is consistent with the reality documented in incident reports,
where the initial vector is almost always the compromised credential, not the zero-day [Verizon DBIR].

## 2. Security Properties

Kerberos aims to guarantee certain properties that the module's techniques violate or bypass:

- **P1 - Mutual authentication.** Client and service authenticate to each other via tickets encrypted with
  keys only the legitimate holder knows. In Lowe's sense [Lowe 1997], the desired property is *injective
  agreement*: each run completed by the service corresponds to one and only one run intended by the
  legitimate client.
- **P2 - Confidentiality of long-term keys.** An account's key (derived from the password, or the NT hash
  for the RC4 etype) must not be recoverable from observable material. Kerberoasting violates this property
  by exploiting the fact that the TGS is encrypted precisely with that key.
- **P3 - Confinement of authority.** Critical operations (replication of the domain database, issuing
  certificates on behalf of others) must be limited to trusted principals. DCSync violates the confinement
  of replication; ESC8 violates that of the certificate authority.
- **P4 - Binding of authentication to the channel.** Authentication should be bound to the channel on which
  it occurs, to prevent reuse elsewhere. NTLM does not provide this binding by default (no EPA/Channel
  Binding, no SMB/LDAP signing), and this is the missing assumption that relay exploits.

## 3. Theoretical Foundations

### 3.1 Kerberos as a trusted-third-party protocol

Kerberos v5 [Neuman et al. 2005, RFC 4120] descends from the Needham-Schroeder symmetric-key protocol
[Needham & Schroeder 1978], which introduces a Key Distribution Center (KDC) as a trusted third party. The
six-message flow is:

```
AS-REQ  : C  -> KDC   request for a TGT, with pre-authentication (timestamp encrypted with C's key)
AS-REP  : KDC -> C    TGT (encrypted with krbtgt's key) + session key
TGS-REQ : C  -> KDC   presents the TGT, requests a ticket for an SPN
TGS-REP : KDC -> C    TGS (encrypted with the service account's key) + session key
AP-REQ  : C  -> S     presents the TGS to the service
AP-REP  : S  -> C     confirmation (mutual authentication)
```

The crucial point for offensive security: the KDC does not verify, at TGS-REP time, whether the client is
authorized to use the service; it delegates access control to the service itself, which reads groups from
the PAC (Privilege Attribute Certificate) inside the ticket. It follows that any authenticated principal
can obtain a TGS for any SPN (the theoretical basis of Kerberoasting).

### 3.2 Key derivation and etype

An account's long-term key depends on the negotiated encryption type (etype):

- etype 23 (RC4-HMAC): the key coincides with the NT hash of the password (MD4 of the password in
  UTF-16LE). No salt, no iterations: a TGS with etype 23 is crackable offline at high speed.
- etype 17/18 (AES128/AES256-CTS-HMAC-SHA1): the key derives from the password via a string-to-key based on
  PBKDF2, 4096 iterations [Raeburn 2005, RFC 3962], with salt = realm + username. Much slower to attack
  offline, but still vulnerable if the password is weak.

This asymmetry explains why attackers force the RC4 etype when possible in Kerberoast requests: it is not a
weakness of Kerberos but of the legacy primitive still enabled for compatibility.

### 3.3 Domain replication (MS-DRSR) and DCSync

Domain Controllers synchronize the database (NTDS.dit) via the MS-DRSR protocol (Directory Replication
Service Remote Protocol). The `IDL_DRSGetNCChanges` call returns an object's attributes, including the
secrets (NT hashes, Kerberos keys), to a requester that holds the extended replication rights. DCSync
[Delpy & Le Toux 2015] breaks nothing: it impersonates a DC and issues a legitimate replication request.
The DC's access control checks only that the requester has the three extended rights
(DS-Replication-Get-Changes, -All, -In-Filtered-Set), not that it really is a DC. This is the violation of
property P3 (confinement of replication authority) through misconfiguration of the domain object's ACL.

### 3.4 AD CS and certificate trust (ESC)

Active Directory Certificate Services binds identity to X.509 certificates. The "Certified Pre-Owned"
research [Schroeder & Christensen 2021] catalogued a family of misconfigurations (ESC1-ESC8+) that allow
obtaining certificates usable to authenticate as other principals. ESC8 in particular combines two
weaknesses: (a) the AD CS Web Enrollment endpoint accepts NTLM authentication, and (b) NTLM is not bound to
the channel (P4). An attacker in position A2 coerces a DC to authenticate (T1187) and relays its
authentication (T1557.001) to the AD CS HTTP endpoint, obtaining a certificate for the DC's machine
account, which is then used to authenticate via PKINIT and obtain the domain's secrets. The certificate,
moreover, stays valid even after a password reset: hence a persistence that password-based countermeasures
do not remove.

## 4. Quantitative Analysis

- **Kerberoasting - offline surface.** With etype 23 (RC4) the hash is an MD4 with no salt and no
  stretching: the offline attack is limited only by hardware speed and password entropy. With etype 18
  (AES256) the PBKDF2 at 4096 iterations [RFC 3962] reduces attempts per second by orders of magnitude, but
  does not protect low-entropy passwords. Reference hashcat modes: 13100 (TGS-REP RC4), 19600 (TGS-REP
  AES128), 19700 (TGS-REP AES256); for AS-REP Roasting 18200 (etype 23).
- **Service accounts and rotation.** The Kerberoasting risk grows with the age and staticity of the service
  account's password: these accounts often have passwords set manually years earlier and never rotated.
  Group Managed Service Accounts (gMSA) mitigate with 240-bit passwords managed and rotated automatically by
  the domain, pushing the offline attack beyond practical feasibility (a search over 2^240 is infeasible).
- **Golden Ticket and krbtgt.** The `krbtgt` key signs all TGTs; a Golden Ticket stays valid until the
  krbtgt password is changed twice (AD keeps the current and previous key). This is why the krbtgt reset
  must be performed twice in a controlled sequence.

Validity note: the values above (PBKDF2 iterations, gMSA bits, hashcat modes) come from official
specifications and documentation, not from lab measurements. Any cracking benchmarks must be measured for
real and labeled as such (consistently with the discipline of the `EVALUATION/` folder).

## 5. Literature Review

Kerberoasting was introduced operationally by Tim Medin [Medin 2014] at DerbyCon. The systematization of AD
CS attacks is due to Schroeder and Christensen [Schroeder & Christensen 2021]. DCSync is the work of
Benjamin Delpy and Vincent Le Toux within Mimikatz [Delpy & Le Toux 2015]. On the formal side, the classic
analyses of Kerberos date back to Bellovin and Merritt [Bellovin & Merritt 1991] (limitations of the
protocol) and to the line of work on authentication-protocol verification started by Needham-Schroeder
[Needham & Schroeder 1978] and refined, on the properties side, by Lowe [Lowe 1997], already cited in the
repository's THEORY-ADVANCED apparatus. The reference adversary model remains that of Dolev and Yao [Dolev &
Yao 1983].

## 6. Limits and Open Problems

- The module documents methodology, not measurements: cracking times, relay success rates and replication
  latency must be quantified in a real lab before any numerical claim.
- The ESC taxonomy is evolving (ESC1-ESC16 and beyond): the treatment covers ESC8 as a representative case
  of the missing binding, not the entire family.
- Countermeasures (gMSA, SMB/LDAP signing, Extended Protection for Authentication, Protected Users, krbtgt
  reset) interact with each other: a formal modeling of their combined effectiveness is an open problem,
  partly addressable with the methods of the `FORMAL-MODELS/` folder.

## 7. Synthesis and Link to Practice

The three techniques of the module share a common structure: none breaks the cryptography, each exploits an
unmet deployment assumption (P2 for Kerberoasting, P4 for ESC8, P3 for DCSync). This is the cross-cutting
lesson for the blue team: hardening AD does not consist of "making Kerberos stronger" but of enforcing the
assumptions the protocol takes for granted (strong, rotated passwords for service accounts, binding of
authentication to the channel, rigorous confinement of replication and certificate-issuance rights). The
operational details, commands and MITRE mapping are in the READMEs of the respective subfolders.

## References

> Subset of the master `REFERENCES.md` (+ `.en.md`), section O "Active Directory, Kerberos and PKI".
> `[Author Year]` keys aligned with the master.

- [Needham & Schroeder 1978] R. Needham, M. Schroeder, "Using Encryption for Authentication in Large
  Networks of Computers", Communications of the ACM, 21(12), 1978.
- [Dolev & Yao 1983] D. Dolev, A. Yao, "On the Security of Public Key Protocols", IEEE Transactions on
  Information Theory, 29(2), 1983.
- [Bellovin & Merritt 1991] S. Bellovin, M. Merritt, "Limitations of the Kerberos Authentication System",
  USENIX Winter 1991.
- [Lowe 1997] G. Lowe, "A Hierarchy of Authentication Specifications", IEEE CSFW, 1997.
- [Neuman et al. 2005] C. Neuman, T. Yu, S. Hartman, K. Raeburn, "The Kerberos Network Authentication
  Service (V5)", RFC 4120, 2005.
- [Raeburn 2005] K. Raeburn, "Advanced Encryption Standard (AES) Encryption for Kerberos 5", RFC 3962, 2005.
- [Medin 2014] T. Medin, "Attacking Microsoft Kerberos: Kicking the Guard Dog of Hades", DerbyCon, 2014.
- [Delpy & Le Toux 2015] B. Delpy, V. Le Toux, "DCSync" (Mimikatz `lsadump::dcsync`), 2015.
- [Schroeder & Christensen 2021] W. Schroeder, L. Christensen, "Certified Pre-Owned: Abusing Active
  Directory Certificate Services", SpecterOps, 2021.
- [Verizon DBIR] Verizon, "Data Breach Investigations Report" (annual editions), for the prevalence of the
  "compromised credentials" vector. Cite the specific edition when used for a precise figure.
