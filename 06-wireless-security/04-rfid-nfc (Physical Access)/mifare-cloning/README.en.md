> **English** | [Italiano](README.md)

# MIFARE Cloning - Access Badge Cloning

> - **Phase:** Wireless Security - Physical Access / Badge Impersonation (NFC/RFID 13.56 MHz)
> - **Visibility:** Zero toward the access control system - a cloned badge is indistinguishable from the original; the only trace is in the access logs (a badge used in two incompatible places/times)
> - **Prerequisites:** Complete dump and keys of the target badge (from `../nfc-tools/`, WIFI-010); writable "magic" tag (Gen1a/Gen2 with modifiable block 0); compatible reader/writer
> - **Output:** WIFI-011; working clone badge with UID and content identical to the original; ability to impersonate the badge holder for physical access

- **Operating Environment:** Kali Linux (Attacker), ACR122U + UID-changeable "magic" tag, lab badge
- **Target:** Test MIFARE Classic 1K badge (dump and keys from WIFI-010)
- **Main tools:** nfc-mfclassic, libnfc, Mifare Classic Tool, Proxmark3

---

## Executive Summary

Cloning turns the dump of a badge (`../nfc-tools/`, WIFI-010) into a working physical token indistinguishable from the original. It is the step that makes the attack concrete: it is not enough to read a badge, one must produce a copy that the access control reader accepts as authentic.

The main technical obstacle is the UID. On a normal MIFARE Classic tag, the UID (block 0, sector 0) is factory-set and non-modifiable. If the access control system verifies the UID (common practice), a clone on a standard tag fails. The solution is the "magic" tags (Gen1a, Gen2, Gen3): special tags whose block 0 is writable, allowing setting any UID and obtaining a perfect clone.

Finding WIFI-011 documents the production of a complete clone of the test badge on a magic tag. The clone replicates UID, keys and content: presented to the reader, it is accepted as the original badge. This demonstrates the security failure of the systems that rely on MIFARE Classic or on UID verification alone for access authentication.

---

## Folder Structure

```
mifare-cloning/
+-- README.md      # this file: MIFARE badge cloning on magic tag (WIFI-011)
+-- img/           # clone writing and verification
```

---

## Cloning on Magic Tag

**Finding ID:** `WIFI-011` | **Severity:** `High` (cloned and working access badge - physical impersonation of the holder)

### Operational Context

The dump obtained in WIFI-010 (`badge_dump.mfd`) contains the entire content of the original badge, including UID and keys. To create a clone accepted even by the systems that verify the UID, the dump is written to a magic tag whose block 0 is modifiable.

### PoC - Phase 1: Magic tag verification

```Bash
# Identification of the magic tag (accepts block 0 write commands)
nfc-list
```

```
    UID (NFCID1): 00  00  00  00       <-- virgin magic tag (default UID)
    MIFARE Classic 1K (Gen1a magic)     <-- writable block 0
```

### PoC - Phase 2: Writing the clone

```Bash
# Writing the entire dump (including block 0/UID) to the magic tag
nfc-mfclassic W a u badge_dump.mfd badge_dump.mfd
# W = write, a = use A keys, u = write also block 0 (UID) - requires magic tag
```

```
Writing 64 blocks |................................................................|
Done, 64 of 64 blocks written.
Writing block 0 (UID)...                          <-- UID cloned (only on magic)
Done.                                             <-- complete clone written (WIFI-011)
```

### PoC - Phase 3: Clone verification

```Bash
# Re-reading the clone for comparison with the original
nfc-list
```

```
    UID (NFCID1): a1  b2  c3  d4       <-- UID identical to the original (a1b2c3d4)
    MIFARE Classic 1K
```

The UID of the clone (`a1b2c3d4`) corresponds exactly to that of the original badge read in WIFI-010. The clone is now indistinguishable from the original for the access control reader.

### Remediation

- **Immediate action:** never rely on the UID as the only authentication factor (it is falsifiable on magic tags); replace the MIFARE Classic badges with cryptographic technologies
- **Structural action:** migrate to MIFARE DESFire EV3 (AES-128) or Seos/iCLASS SE with mutual challenge-response authentication: these systems are not clonable via dump because the cryptographic secret never leaves the chip and every authentication is a unique cryptographic challenge; implement anti-passback detection (a badge cannot enter twice without having exited) and log correlation; add a second factor (PIN, biometrics) for critical areas
- **Verification:** attempt the cloning on the new DESFire badges - it must fail because the AES keys are not extractable from the dump; verify that the anti-passback detects the simultaneous use of two badges with the same ID

---

## Lab Experience

The turning point was understanding the role of the magic tags. The first cloning attempt on a standard MIFARE Classic tag failed in writing block 0: the UID was immutable, and the resulting clone had a UID different from the original. The test access control system, which verified the UID, rejected it. The switch to a Gen1a magic tag - whose block 0 accepts the write - solved the problem by producing a clone with an identical UID.

This clarified a fundamental operational distinction: the clonability of a badge depends both on the cryptographic weakness of the system (MIFARE Classic, recoverable keys) and on the availability of the right hardware (magic tag for the UID). Both conditions were met in the lab, as they are in very many real installations where magic tags cost a few euros and MIFARE Classic is still the standard.

The concluding observation concerns detectability: a clone is perfect for the reader, but not for the logs. A badge that registers an access in two distant sites a few minutes apart is an evident cloning indicator for whoever analyzes the logs - the reason why anti-passback and log correlation are valuable countermeasures even when cloning is not preventable upstream.

---

## Theoretical Analysis: UID Spoofing and the Failure of Identity as a Secret

MIFARE cloning illustrates a recurring conceptual error: using a public identifier as if it were an authentication secret. The UID of a tag is designed for anti-collision (distinguishing multiple tags in the reader's field), not for authentication: it is transmitted in cleartext at every query and, on magic tags, is freely settable. A system that grants access based on the UID is authenticating "something that anyone can read and anyone can falsify".

Robust authentication requires the proof of possession of a secret without revealing it. This is what DESFire does with AES: the reader sends a challenge, the tag encrypts it with an AES key that never leaves the chip, and the reader verifies the response. An attacker who clones the readable content does not obtain the key (which is not readable) and cannot respond correctly to the challenge. Security resides in the secret key and in the challenge-response protocol, not in the identifier.

This is the same principle that distinguishes, in the web domain, a predictable session ID from a cryptographic token, or the sending of a password from its challenge-response hash. The cross-cutting lesson: identity must never be the secret. A secure system separates "who you claim to be" (UID, public) from "the proof that you are" (challenge-response on a secret key), and MIFARE Classic collapses precisely because it does not maintain this separation.

---

## Real-World Scenario: Post-Exploitation Projection

> This section describes how this finding would fit into a real engagement, from both the attacker (Red Team) and defender (Blue Team) perspectives.

### Attacker Perspective (Red Team)

**Starting point:** cloned and working access badge, indistinguishable from the original (WIFI-011).

**Immediate next step:** unauthorized physical access to the building or the restricted areas by presenting the clone to the reader, impersonating the legitimate holder.

**Projected kill chain:**

```
[WIFI-011] Working cloned badge
        |
        v
Physical access to the building (impersonating the holder)
        |
        v
Access to restricted areas (server room, offices)
        |
        v
Drop of network implant / access to unlocked workstations / data theft
        |
        v
Internal foothold -> pivoting toward the network (07-post-exploitation)
```

**Potential impact:** a cloned badge nullifies the physical security perimeter. The attacker obtains, with a few seconds of proximity to the original badge (via skimming or social engineering) and material costing a few euros, the same access capability as the legitimate employee. In high-security contexts (data centers, industrial areas), this is often the cheapest and quietest entry point. The vector integrates with `05-social-engineering/` (obtaining the proximity) and opens the internal network access phase.

### Defender Perspective (Blue Team)

**Detection:** a cloned badge is identical to the original for the reader, so it is not detectable at the moment of access. Detection occurs via log analysis: impossible uses (same card in two places at incompatible times) or anomalous ones (accesses outside hours, areas never used by the holder).

**Indicators of Compromise (IOC):**
- Same badge ID registered in different sites within an incompatible time window
- Badge accesses at anomalous times or areas compared to the holder's pattern
- Anti-passback violations (entry without a previous exit)
- Negative badge/video surveillance correlation (employee X's badge used while X is elsewhere)

**Containment:** immediate deactivation of the compromised badge ID; issuance of a new badge on secure technology; review of the badge's recent accesses.

**Eradication and hardening:**
- Migration to DESFire EV3 (AES) or Seos: structural elimination of clonability
- Anti-passback and automatic correlation of the access logs
- Multi-factor for critical areas (badge + PIN/biometrics)
- Anti-skimming training: protect the badge (RFID-shielded holders) and be wary of suspicious readers

**Defensive lesson:** physical security based on clonable tokens is apparent security. An access control system must cryptographically authenticate the token, not trust a readable and falsifiable identifier. Where technological migration is not immediate, log correlation and behavioral detection are the only safety net against cloning.

---

## Reference Tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `nfc-mfclassic` | MIFARE writer | CLI | Writing the dump to a tag (including block 0 on magic) |
| `libnfc` | NFC library | CLI | Interface with NFC readers for reading/writing |
| `Mifare Classic Tool` | NFC app | Android | Cloning from a smartphone with NFC (reading+writing) |
| Magic tag Gen1a/Gen2 | Hardware | - | Tag with writable block 0 (UID) for a perfect clone |
| `Proxmark3` | RFID multi-tool | Hardware | Advanced cloning, protected tags, LF+HF (`../proxmark3-client/`) |
| [Flipper Zero](https://github.com/Nicholas-Arcari/FlipperZero-guide) | Portable multi-tool | Hardware | Portable NFC reading/emulation/cloning |

> **Recommended modern tool:** the `Proxmark3 RDV4` is the professional standard for cloning (it handles magic, protected, LF and HF tags, and emulates badges without a physical tag). The `Flipper Zero` offers NFC emulation and cloning in a pocket device, ideal for demonstrations and field assessments.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Resource Development | Develop Capabilities | `T1587` | Production of a working clone badge on a magic tag (WIFI-011) |
| Defense Evasion | Impersonation | `T1656` | The cloned badge impersonates the legitimate holder toward the access control (WIFI-011) |
| Initial Access | Hardware Additions | `T1200` | Use of the cloned badge to gain unauthorized physical access (WIFI-011) |
| Initial Access | Valid Accounts: Local Accounts | `T1078.003` | The clone is equivalent to a valid physical access credential of the holder |

---

> **Note:** All documented activities were conducted on lab NFC/RFID badges owned by the author. The cloning was performed exclusively on test tokens. The cloning and use of third-party access badges without authorization is a serious crime (unauthorized access to systems/places, identity theft, impersonation). Techniques are documented for educational and authorized physical security assessment purposes with a defined scope.
