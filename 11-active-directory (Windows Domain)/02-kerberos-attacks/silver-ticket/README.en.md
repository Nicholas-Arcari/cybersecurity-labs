> **English** | [Italiano](README.md)

# Silver ticket: forging the service ticket (TGS)

> - **Phase:** Persistence / Lateral Movement (Active Directory domain)
> - **Visibility:** Very low - the ticket is forged offline and presented directly to the service, never contacting the KDC (no TGT, no TGS-REQ logged)
> - **Prerequisites:** possession of the NT hash (or AES key) of the target service account (e.g., the machine account for CIFS/HOST) and the domain SID
> - **Technique:** `Silver Ticket` | **Typical severity:** `High` | **Finding ID:** to assign in lab (methodology)

- Nature of the document: methodology. Illustrative outputs; placeholder keys/SID.
- Objective: forge a TGS valid for a specific service, obtaining access to that service without going through the KDC, extremely silently.

---

## Executive summary

The Silver Ticket is the "surgical" counterpart of the Golden Ticket. While the Golden forges a TGT valid
for the entire domain using the krbtgt key, the Silver forges a TGS valid for a single service using that
service's account key. Since the TGS is encrypted with the service key and is presented directly to it (the
AP-REQ message), the KDC is never involved: no TGT, no TGS-REQ, hence no trace on the Domain Controller
side. This makes the Silver Ticket one of the quietest accesses available.

The price of this discretion is reach: the Silver is valid only for the service whose key you hold (e.g.,
CIFS on a server to access its shares, HOST for task execution). It is ideal for targeted persistence and
discreet lateral movement.

## Operational context (why, before how)

The Silver Ticket presupposes already having the key of a service account (a machine-account hash or a
service-account hash), obtained for example from a local dump or from DCSync. You choose the Silver over the
Golden when discretion is needed and access to a specific service is enough: by not touching the KDC, it
avoids detections based on domain-level ticket monitoring. The decision concerns the target service (the
SPN) and, once again, the use of AES instead of RC4.

## Execution / commands

```bash
# Forges a TGS for the target host's CIFS service using the machine-account hash
ticketer.py -nthash <HASH_SERVICE_ACCOUNT> -domain-sid S-1-5-21-<PLACEHOLDER> -domain corp.local \
  -spn cifs/srv01.corp.local amministratore
```

```bash
# Using the ticket to access the target service's share
export KRB5CCNAME=amministratore.ccache
smbclient.py -k -no-pass corp.local/amministratore@srv01.corp.local
```

Illustrative output (representative):

```
[*] Saving ticket in amministratore.ccache
# access to cifs/srv01 as 'amministratore' without contacting the KDC
```

## Analysis of results

The Silver Ticket provides targeted, nearly invisible access to a service. The typical severity is `High`
because, although limited to one service, that service may be critical (e.g., CIFS on a file server with
sensitive data, or HOST on a server to run code). It does not reach the `Critical` of the Golden only because
it is not domain-wide, but the combination of several Silvers on key services approaches the same effect
with much less noise.

### Theoretical analysis

In the Kerberos flow (see [THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.en.md>), sec. 3.1) the TGS
is encrypted with the service account's key, and the service validates it by decrypting it with its own key.
The service, by default, does not verify the validity of the PAC contained in the ticket with the KDC (PAC
validation is optional and often not enabled). Whoever holds the service key can therefore forge a TGS with
an arbitrary PAC and the service will accept it. It is the violation of property P1 limited to the perimeter
of a single service: the attacker forges the authentication proof toward that specific service.

## Remediation (blue team)

**Detection.** Hard on the KDC side (the Silver does not contact it). Detection shifts to the service and
the host: access to a service without a corresponding TGS-REQ logged on the DC; enable PAC validation where
possible; correlate service logons with the absence of Kerberos activity on the DC.

**Hardening.** Rotate the passwords of service accounts and machine accounts (an old key remains
exploitable); enable PAC validation; protect service keys upstream (avoid local dumps and DCSync); Tiering
Model.

---

## Real-World scenario: Post-Exploitation projection

> Applies to targeted access to a critical service (severity High).

### Attacker perspective (red team)

**Starting point:** possession of a service/machine account key (from a local dump or DCSync).

**Immediate next step:** forge a Silver Ticket for the target service and access it directly.

**Projected Kill Chain:**

```
Key of a service/machine account
        |
        v
Silver Ticket for cifs/host of the target server (no contact with the KDC)
        |
        v
Silent access to the service (sensitive shares, task execution)
        |
        v
Targeted persistence + discreet exfiltration from the server
```

**Potential impact:** persistent and hard-to-detect access to critical services and data, without the typical
signals of domain-level Kerberos activity.

**Typical monetization vectors:** discreet and prolonged exfiltration; persistence on key systems.

### Defender perspective (blue team)

**Detection:** accesses to a service lacking the corresponding TGS-REQ on the DC; enabling PAC validation to
expose forged PACs.

**Indicators of Compromise (IOC):** logon to the service without correlated Kerberos activity on the DC; use
of RC4 where AES is expected.

**Containment:** rotate the key of the compromised service/machine account; investigate the accesses.

**Eradication and hardening:** PAC validation; periodic rotation of machine/service keys; upstream protection
of keys.

**Defensive lesson:** the Silver Ticket shows that the trust a service places in mere possession of its own
key is a risk: without PAC validation, anyone with that key is indistinguishable from a legitimate user.

---

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `ticketer.py` (impacket) | kerberos tool | cli - active | silver ticket forgery from linux |
| `Mimikatz` | credential/ticket tool | cli - active | `kerberos::golden` with `/service` and `/target` for the silver from windows |
| `Rubeus` | .net kerberos tool | cli - active | ticket forgery/use from windows |

## Methodology notes

In a real lab document: the forgery from the machine/service account key, access to the target service, and
verification of the absence of a trace on the DC compared to a normal Kerberos access. Document PAC
validation as a countermeasure.

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| credential access | steal or forge kerberos tickets: silver ticket | `T1558.002` | forgery of a tgs for a service using the service account's key. |
| lateral movement | use alternate authentication material: pass the ticket | `T1550.003` | use of the forged ticket to access the target service. |
| persistence | account manipulation | `T1098` | targeted persistence on the service via forged tickets. |

## Links to other modules

| source | this technique | effect |
| :--- | :--- | :--- |
| [dcsync](<../../05-credential-dumping/dcsync/README.en.md>) / local dump | silver ticket | provides the service/machine account key |
| [golden ticket](<../golden-ticket/README.en.md>) | silver ticket | complementary variants: domain-wide vs targeted service |
| silver ticket | [07-post-exploitation](<../../../07-post-exploitation/README.en.md>) | discreet lateral movement and persistence on key services |

---

> **Note:** All described techniques are for educational and methodology-documentation purposes. Execution only in owned labs or with explicit authorization. Illustrative outputs, not from real systems.
