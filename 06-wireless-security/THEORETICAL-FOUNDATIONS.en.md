> **English** | [Italiano](THEORETICAL-FOUNDATIONS.md)

# Theoretical Foundations - Module 06: Wireless Security

> - **Level:** Academic analysis (theoretical complement to the operational READMEs of the module)
> - **Purpose:** Formalize the security of the radio layer (absence of a physical perimeter), the fall of security-by-obscurity (Crypto-1), the freshness property against replay and the identification/authentication distinction.
> - **Prerequisites:** Operational READMEs of module 06 (WIFI- findings); notions of cryptography, authentication protocols and information theory.

---

## Abstract

The wireless domain exposes in pure form cryptographic principles that the other modules touch indirectly. The document organizes the module around four cores: (i) the absence of a physical perimeter makes interception the default, elevating cryptography to the only defense; (ii) the breaking of Crypto-1 [Nohl et al. 2008; Garcia et al. 2008] is the canonical empirical demonstration of the ineffectiveness of security-by-obscurity [Kerckhoffs 1883]; (iii) the replay attack is the violation of the **freshness** property, whose restoration (rolling code, nonce) is a problem of protocol theory; (iv) RFID cloning arises from the confusion between **identification** and **authentication**. The evolution WEP, WPA2, WPA3, with the attacks KRACK [Vanhoef & Piessens 2017] and Dragonblood [Vanhoef & Ronen 2020], illustrates protocol cryptanalysis as an iterative process.

---

## 1. The Adversary Model

The wireless adversary is a Dolev-Yao network attacker [Dolev & Yao 1983] physically realized: within radio range it possesses **complete access to the channel** without needing to compromise any device. It can passively observe every transmission (the 802.11 management frames are in cleartext even on encrypted networks), inject arbitrary frames (deauthentication, association), and transmit signals (rogue AP, RF replay). Compared to the web attacker (module 03), it is stronger on the channel; compared to pure Dolev-Yao, it is constrained by physics (range, power, band). The passive/active operational distinction of module 01 (section 1) applies: SDR reception is passive and undetectable, transmission is active and detectable.

---

## 2. Security Properties at Stake

- **Confidentiality on the broadcast channel:** since anyone in range receives, confidentiality can derive only from cryptography, not from the inaccessibility of the medium.
- **Mutual authentication:** both parties must prove their identity. Its absence enables the Evil Twin (impersonation of the AP) and cloning (impersonation of the token).
- **Freshness (novelty):** an authentication message or command must be recognizable as not reused. It is the property violated by replay (section 3.3).
- **Resistance to offline attacks:** an intercepted handshake must not allow the recovery of the secret except at prohibitive cost (section 3.2).

---

## 3. Theoretical Foundations

### 3.1 Crypto-1 and the fall of security-by-obscurity

MIFARE Classic is based on Crypto-1, a proprietary stream cipher with a 48-bit key, kept secret. [Nohl et al. 2008] performed its reverse engineering from the silicon and [Garcia et al. 2008] the complete cryptanalysis, revealing two fatal weaknesses: a predictable PRNG and a cipher structure that allows attacks of drastically reduced complexity (darkside, nested). The result is the sharpest empirical demonstration of the principle of [Kerckhoffs 1883]: an algorithm whose security depends on the secrecy of the design collapses as soon as the design is recovered - and every design distributed in billions of chips is, sooner or later, recovered. The theoretical lesson is that security must reside in the key, with public and analyzed algorithms (AES in DESFire), not in obscurity.

### 3.2 WPA2-PSK: key derivation and offline attack

WPA2-PSK derives the Pairwise Master Key from the passphrase via PBKDF2-HMAC-SHA1 [Kaliski 2000] with 4096 iterations and the SSID as salt:

```
PMK = PBKDF2(passphrase, SSID, 4096, 256)
```

The capture of the 4-way handshake (or of the PMKID) provides the material for an **offline** dictionary attack: the traffic is not decrypted, one verifies which candidate produces the observed MIC. Security therefore reduces to the problem of module 04 (section 3.3): passphrase entropy against cost per attempt. The 4096 iterations are deliberate key stretching; the use of the SSID as salt prevents precomputed rainbow tables for unique SSIDs but not for common ones (hence the existence of tables for "linksys", "NETGEAR"). WPA2 is secure exactly as much as the guessing entropy of the PSK.

### 3.3 Replay and the freshness property

The replay attack is the violation of **freshness**: a system that accepts a valid message without verifying its novelty is vulnerable to anyone who possesses a copy of it. Formally, authentication must guarantee not only that the message is *valid* (authenticity) but that it is *fresh* (never accepted before). A fixed-code remote always transmits the same sequence: valid but not fresh, therefore replayable. The rolling code introduces a synchronized and encrypted counter (KeeLoq): every transmission carries a monotonically increasing and encrypted value that the receiver accepts only once. It is the analog, in the RF domain, of **nonces** in network protocols: a value that guarantees freshness. This is the same property violated by KRACK (section 3.5) at the WiFi protocol level, and the same that anti-CSRF tokens (module 03) provide at the web level. Freshness is a cross-cutting unifying principle.

### 3.4 Identification versus authentication (RFID)

The cloning of EM4100/MIFARE badges arises from a recurring conceptual error: using an **identifier** as if it were an **authentication secret**. The UID of a tag is designed for anti-collision (distinguishing multiple tags in the field), is transmitted in cleartext at every query and is, on magic tags, freely settable. A system that grants access based on the UID authenticates "something that anyone can read and falsify". Robust authentication requires proof of possession of a secret without revealing it (challenge-response on a key that never leaves the chip, as in DESFire AES). The identification/authentication distinction is the same principle that, in the web, separates a predictable session ID from a cryptographic token, and that in the cloud (module 10) separates a resource name from a credential: identity must never be the secret.

### 3.5 Protocol cryptanalysis as an iterative process

The evolution WEP, WPA, WPA2, WPA3 illustrates cryptanalysis as a process. WEP falls due to the weaknesses of the RC4 key scheduling [Fluhrer et al. 2001]. WPA2, solid in encryption, suffers KRACK [Vanhoef & Piessens 2017]: not a cryptographic break but a **protocol** defect, the key reinstallation that forces nonce reuse in the 4-way handshake, violating freshness at the protocol state level. WPA3 adopts SAE (Dragonfly), resistant to offline attacks, but [Vanhoef & Ronen 2020] (Dragonblood) reveal side-channels and downgrades. The theoretical lesson: the security of a protocol is not just the security of its primitives; the state interactions, the management of nonces and the side channels [Kocher 1996] are autonomous attack surfaces, and the formal verification of protocols remains necessary.

> **Formal verification (not merely argued):** the thesis "KRACK is a protocol-state defect, not a
> primitive break" is **mechanically demonstrated** in [`../FORMAL-MODELS/wpa2-4way-handshake/`](../FORMAL-MODELS/wpa2-4way-handshake/results.en.md).
> An explicit-state model checker of the 4-way handshake under a Dolev-Yao adversary (primitives assumed
> perfect) finds the KRACK attack in the vulnerable model (4-step counterexample: the replay of M3
> reinstalls the PTK and resets the nonce counter) and exhaustively verifies the absence of the defect
> in the patched model. Violated invariant = injectivity of key installation (freshness).
> The formal name of this property is **injective agreement** in the hierarchy of [Lowe 1997]:
> [`../THEORY-ADVANCED.en.md`](../THEORY-ADVANCED.en.md) Part III places KRACK as its violation, and
> Part II gives the concrete-security bound of the offline attack on WPA2-PSK (section 3.2).

---

## 4. Quantitative Analysis

### 4.1 The robustness spectrum of RFID technologies

RFID technologies form a spectrum quantifiable by attack cost:

```
LF EM4100 (read-only, ID in cleartext)  -> cloning cost: read+write (~seconds)
HF MIFARE Classic (Crypto-1, 48 bits)   -> cost: nested/darkside key recovery (~minutes)
HF DESFire (AES-128, challenge-resp)     -> cost: prohibitive (no practical attack via dump)
```

The progression shows that robustness is not binary but a continuum determined by the presence and strength of cryptographic authentication. The technological choice must correspond to the threat model: an identification-only technology (EM4100) used for access control is an abuse, not an implementation weakness.

### 4.2 The cost of WPA2 cracking and the absent memory-hardness

The 4096 PBKDF2 iterations reduce the attack throughput by a factor of ~4096 compared to a raw hash, bringing GPUs from billions of attempts/second (NTLM) to a few hundred thousand (WPA2). However, PBKDF2 is not memory-hard (section 4.2 of module 04): the advantage of GPU/ASIC parallelism remains. This quantitatively explains why an 8-numeric-digit PSK (entropy ~26 bits, ~10^8 candidates) falls in minutes while an 18-character high-entropy passphrase is unreachable: the only real lever, given PBKDF2 fixed by the standard, is the entropy of the passphrase.

---

## 5. Literature Review

The breaking of Crypto-1 is documented by [Nohl et al. 2008] (reverse engineering) and [Garcia et al. 2008] (cryptanalysis), exemplars of the failure of security-by-obscurity [Kerckhoffs 1883]. The fall of WEP goes back to [Fluhrer et al. 2001]. The attacks on modern WiFi protocols are by [Vanhoef & Piessens 2017] (KRACK, WPA2) and [Vanhoef & Ronen 2020] (Dragonblood, WPA3). The WPA2 key derivation uses PBKDF2 [Kaliski 2000]; the side channels appeal to [Kocher 1996]. The adversary model derives from [Dolev & Yao 1983]; the entropic framing from [Shannon 1949]. The IoT botnets that exploit weak wireless devices are analyzed by [Antonakakis et al. 2017] (Mirai).

---

## 6. Limitations and Open Problems

1. **Irremovable legacy.** MIFARE Classic and EM4100 remain deployed in billions of installations for cost and inertia, despite the cryptographic break being known since 2008. The migration is an economic-logistical problem, not a technical one: an unresolved practical limit.

2. **Formal verification of wireless protocols.** KRACK and Dragonblood demonstrate that protocol defects survive secure primitives. The exhaustive formal verification of the state machines of the 802.11 protocols (including the implementations) remains incomplete.

3. **Usable mutual authentication.** The Evil Twin is neutralized only by mutual authentication with server certificate validation (EAP-TLS), but its correct client configuration (rejection of invalid certificates) is frequently disregarded, reopening the system-to-human gap of module 05.

---

## 7. Synthesis and Connection to Practice

The `WIFI-` findings of the module instantiate this framework: WPA2/PMKID cracking (WIFI-002/003) is the offline attack of section 3.2; the Evil Twin (WIFI-004) is the violation of mutual authentication and the radio version of the gap of module 05; the RF replay (WIFI-009) is the violation of freshness of section 3.3; MIFARE/EM4100 cloning (WIFI-010/011/012) is the identification/authentication confusion of section 3.4. The countermeasures recommended in the READMEs - WPA3-SAE, EAP-TLS, rolling code, DESFire AES - are the operational translations of the principles formalized here. The module demonstrates in physical and tangible form principles (freshness, mutual authentication, non-secret identity, Kerckhoffs) that recur throughout the path, from the web (module 03) to the cloud (module 10).

---

## References

Subset of the master bibliography (`../REFERENCES.md`) relevant to this module:

- [Nohl et al. 2008], [Garcia et al. 2008] - breaking of Crypto-1/MIFARE.
- [Fluhrer et al. 2001] - weaknesses of RC4 (WEP).
- [Vanhoef & Piessens 2017] - KRACK (WPA2).
- [Vanhoef & Ronen 2020] - Dragonblood (WPA3).
- [Kerckhoffs 1883] - ineffectiveness of security-by-obscurity.
- [Kaliski 2000] - PBKDF2 (WPA2 key derivation).
- [Kocher 1996] - side-channel attacks.
- [Dolev & Yao 1983], [Shannon 1949] - adversary model and entropy.
- [Antonakakis et al. 2017] - Mirai (IoT).

---

> **Note:** Document for educational purposes, complementary to the operational READMEs. The citations refer to real sources listed in `../REFERENCES.md`.
