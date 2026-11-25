> **English** | [Italiano](README.md)

# NFC tools - reading and enumeration of HF NFC/RFID tags

> - **Phase:** Wireless Security - Physical Access Reconnaissance (NFC/RFID 13.56 MHz)
> - **Visibility:** Zero - NFC reading requires physical proximity (a few centimeters) but leaves no trace on the target system; it is a passive operation from the access control standpoint
> - **Prerequisites:** libnfc-compatible NFC reader (ACR122U, PN532); temporary physical access to the target tag/badge; libnfc and mfoc/mfcuk installed
> - **Output:** WIFI-010; identification of the tag type (UID, technology); recovery of the sector keys on MIFARE Classic tags with weak keys; dump of the tag content

- **Operating Environment:** Kali Linux (Attacker), ACR122U reader (13.56 MHz), lab NFC tags/badges
- **Target:** Test MIFARE Classic 1K badge, NTAG213 tag
- **Main tools:** libnfc (nfc-list, nfc-mfclassic), mfoc, Mifare Classic Tool

---

## Executive summary

This section enters the border zone between information security and physical security: access control badges, hotel cards, transport passes and many identification systems operate on NFC/RFID at 13.56 MHz (High Frequency). The objective is not a network but a physical token of identity, and compromising it means impersonating the person it belongs to.

The dominant technology in this space, MIFARE Classic, has been cryptographically broken since 2008 (Nohl/Plotz and Garcia et al. attacks on the proprietary Crypto-1 algorithm). Despite this, it remains very widespread in corporate badges and legacy systems for reasons of cost and inertia. Finding WIFI-010 documents the recovery of the keys of a test MIFARE Classic badge via the mfoc attack, which exploits the weaknesses of Crypto-1 to derive the sector keys starting from a single known key (often one of the default keys never changed).

This section covers reading and enumeration (identify the technology, recover the keys, make the dump); the actual cloning is documented in `../mifare-cloning/`, while `../proxmark3-client/` covers the professional hardware for the scenarios that the ACR122U does not handle (Low Frequency 125 kHz, protected tags).

---

## Folder structure

```
nfc-tools/
+-- README.md      # this file: reading, identification, MIFARE key recovery (WIFI-010)
+-- img/           # nfc-list dump and mfoc key recovery
```

---

## Tag identification and reading

**Finding ID:** `WIFI-010` | **Severity:** `Medium` (key recovery and dump of a MIFARE Classic badge; direct premise of cloning and unauthorized access)

### Operational context

The first step is to identify the type of tag: the technology (MIFARE Classic, Ultralight, NTAG, DESFire) completely determines the attack approach. `nfc-list` queries any tag in proximity and reveals its UID, type and ATQA/SAK (the parameters that identify the family).

### Execution

```Bash
# Identification of the tag in proximity to the reader
nfc-list
```

```
NFC device: ACS / ACR122U opened
1 ISO14443A passive target(s) found:
    ATQA (SENS_RES): 00  04
       UID (NFCID1): a1  b2  c3  d4              <-- UID of the badge
      SAK (SEL_RES): 08
     MIFARE Classic 1K                            <-- vulnerable technology (Crypto-1)
```

The SAK `08` and the string "MIFARE Classic 1K" identify a tag based on Crypto-1, the cryptographically broken NXP proprietary algorithm.

### Execution - key recovery with mfoc

### Operational context (key recovery)

MIFARE Classic 1K organizes the memory in 16 sectors, each protected by two keys (A and B). mfoc (MIFARE Offline Cracker) exploits a weakness of Crypto-1: if even a single key of a sector is known (typically a default key that the installer never changed), the "nested" attack recovers all the other keys by exploiting the weakness of the tag's pseudo-random number generator.

```Bash
# Recovery of all the keys starting from the known default keys, dump to file
mfoc -O badge_dump.mfd
```

```
[Key: ffffffffffff] found for sector 00 (as key A)   <-- default key never changed
Nested attack...
[Key: a0a1a2a3a4a5] recovered for sector 01           <-- key recovered via nested
[Key: d3f7d3f7d3f7] recovered for sector 02
...
Auth with all sectors succeeded, dumping keys to a file!
Card dump written to badge_dump.mfd                   <-- complete dump (WIFI-010)
```

The dump `badge_dump.mfd` now contains the entire content of the badge and all the keys: the material necessary for cloning (`../mifare-cloning/`).

### Remediation

- **Immediate action:** identify and replace the badges based on MIFARE Classic; verify that no sector uses the default keys (`FFFFFFFFFFFF`, `A0A1A2A3A4A5`)
- **Structural action:** migrate to technologies with robust encryption and mutual authentication: MIFARE DESFire EV3 (AES-128, 3DES), iCLASS SE, or Seos-based systems. These technologies are not clonable with a simple dump because they use cryptographic challenge-response; implement a second factor for critical accesses (PIN, biometrics); where the badges carry an identifier, avoid it being simply the UID (falsifiable)
- **Verification:** repeat the mfoc attack on the new badges - on DESFire with AES the attack must fail completely

---

## Lab experience

The most revealing aspect of the exercise was how much the attack depends on the default keys. The test badge used the key `FFFFFFFFFFFF` (factory default) on sector 0: from that single foothold, mfoc recovered all the other keys in a few minutes via the nested attack. This mirrors the reality of very many installations: the systems are deployed with the default keys and never reconfigured, making the attack almost immediate.

An important hardware limit emerged with the ACR122U: it is a cheap and reliable reader for MIFARE Classic 1K at 13.56 MHz, but it does not handle Low Frequency tags (125 kHz, very common in older corporate badges) or some protected variants. For those cases the Proxmark3 is needed (`../proxmark3-client/`). The choice of the reader rigidly constrains what is attackable - a recurring lesson throughout the wireless domain.

Methodological note: the entire attack requires physical proximity to the badge. In the lab the badge was available, but in a real scenario the main challenge is obtaining those few seconds of proximity - often via social engineering or a hidden reader (skimming), linking this technique directly to the `05-social-engineering` module.

---

## Theoretical analysis: why MIFARE classic is cryptographically broken

MIFARE Classic is based on Crypto-1, a proprietary NXP stream cipher with a 48-bit key, kept secret according to the (wrong) principle of security by obscurity. In 2008, the reverse engineering of the chip (Nohl and Plotz) and the cryptographic analysis (Garcia et al., Radboud University) revealed fatal weaknesses: a predictable pseudo-random number generator (PRNG) and a cipher structure that allows attacks of much reduced complexity.

Two classes of attack derive from it. The "darkside" attack (mfcuk) recovers a first key without knowing any, exploiting error responses of the tag. The "nested" attack (mfoc), faster, requires a known key (even a default one) and recovers all the others by exploiting the predictability of the PRNG: knowing one key, the attacker can predict the nonces and derive the keys of the other sectors with few authentication attempts.

The cryptographic lesson is twofold. First, security by obscurity fails: a secret algorithm is no longer secure once reverse-engineered, and every algorithm is sooner or later. The modern standards (AES in DESFire) are public and secure precisely because their security resides in the key, not in the secrecy of the algorithm (Kerckhoffs's principle). Second, the length of the key matters: 48 bits were insufficient already in 2008. The migration to DESFire (AES-128) solves both problems, which is why it is the structural remediation.

---

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `libnfc` (nfc-list) | nfc library | cli | identification and reading of iso14443a/b tags |
| `mfoc` | mifare cracker | cli | nested attack: key recovery from a known/default key |
| `mfcuk` | mifare cracker | cli | darkside attack: key recovery without known keys (slower) |
| `Mifare Classic Tool` | nfc app | android | mifare reading/writing from a smartphone with nfc |
| `nfc-mfclassic` | mifare dump/write | cli | dump and writing of the mifare classic content |
| `Proxmark3` | rfid multi-tool | hardware | professional hardware for lf/hf and protected tags (`../proxmark3-client/`) |

> **Recommended modern tool:** for field work, the `Proxmark3 RDV4` or the [Flipper Zero](https://github.com/Nicholas-Arcari/FlipperZero-guide) (with integrated NFC module) replace the ACR122U with much wider capabilities (LF 125 kHz + HF 13.56 MHz, emulation, advanced attacks). The ACR122U remains valid for MIFARE Classic 1K in the lab.

---

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| reconnaissance | gather victim host information | `T1592` | identification of the nfc/rfid tag type and its parameters (WIFI-010) |
| credential access | brute force | `T1110` | recovery of the mifare classic sector keys via nested/darkside attack (WIFI-010) |
| credential access | steal application access token | `T1528` | extraction of the badge content (access identifier) via dump (WIFI-010) |
| initial access | hardware additions | `T1200` | use of the nfc reader to acquire the badge material |

---

> **Note:** All documented activities were conducted on lab NFC/RFID tags and badges owned by the author. The reading, key recovery and dump were performed exclusively on test tokens. The cloning or unauthorized use of third-party access badges is a crime (unauthorized access, identity theft). Techniques are documented for educational and authorized physical security assessment purposes.
