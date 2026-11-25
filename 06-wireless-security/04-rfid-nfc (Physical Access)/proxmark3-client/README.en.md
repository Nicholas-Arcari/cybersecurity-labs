> **English** | [Italiano](README.md)

# Proxmark3 - professional hardware for RFID LF/HF

> - **Phase:** Wireless Security - Advanced Physical Access (RFID Low & High Frequency)
> - **Visibility:** Zero toward the access control system; requires physical proximity to the tag/reader
> - **Prerequisites:** Proxmark3 (RDV4 recommended) with LF and HF antennas; Proxmark3 client (pm3) compiled; physical access to the target tag; for sniffing: proximity to the reader during a legitimate transaction
> - **Output:** WIFI-012; reading/cloning of Low Frequency tags (125 kHz) that the ACR122U does not handle; sniffing of reader-tag transactions; emulation of badges without a physical tag

- **Operating Environment:** Kali Linux (Attacker), Proxmark3 RDV4, lab LF tags (EM4100, HID Prox) and HF
- **Target:** Test LF EM4100 badge, HID Prox badge, MIFARE Classic badge
- **Main tools:** Proxmark3 client (pm3), Iceman firmware

---

## Executive summary

The Proxmark3 is the professional reference tool for RFID security: where cheap readers like the ACR122U (`../nfc-tools/`) are limited to MIFARE Classic HF at 13.56 MHz, the Proxmark3 covers the entire RFID spectrum - both Low Frequency (125/134 kHz: EM4100, HID Prox, Indala) and High Frequency (13.56 MHz: MIFARE, iCLASS, DESFire) - and adds capabilities that consumer readers do not have: transaction sniffing, tag emulation without physical hardware, and advanced attacks on protected systems.

This distinction is crucial in the real world of corporate access control. Very many corporate badges, especially in older installations, use Low Frequency technologies like EM4100 or HID Prox, which the ACR122U cannot even read. Finding WIFI-012 documents the reading and cloning of a test LF EM4100 badge, a technology even weaker than MIFARE Classic: the EM4100 simply transmits a 40-bit identifier in cleartext, without any authentication, making cloning a trivial read and rewrite operation.

---

## Folder structure

```
proxmark3-client/
+-- README.md      # this file: LF/HF, sniffing, emulation with Proxmark3 (WIFI-012)
+-- img/           # pm3 client session
```

---

## LF reading and cloning (EM4100)

**Finding ID:** `WIFI-012` | **Severity:** `High` (Low Frequency badge read and cloned - physical access; EM4100 devoid of any authentication)

### Operational context

The EM4100 is one of the most widespread and weakest RFID technologies: a read-only 125 kHz tag that transmits a 40-bit identifier in a loop, without encryption or authentication. The Proxmark3 reads it and writes a copy to a T5577 tag (rewritable LF tag), producing a clone in a few seconds.

### PoC - phase 1: LF identification and reading

```Bash
# Start the Proxmark3 client
pm3

# Automatic detection of the tag's LF technology
[usb] pm3 --> lf search
```

```
[+] Chipset detection: EM4100 / EM4102 (125 kHz)
[+] EM 410x ID found: 1A2B3C4D5E                    <-- 40-bit ID of the badge (in cleartext)
[+] Valid EM410x ID found!
```

### PoC - phase 2: cloning to T5577 tag

```Bash
# Writing the read ID to a rewritable T5577 tag
[usb] pm3 --> lf em 410x clone --id 1A2B3C4D5E
```

```
[=] Preparing to clone EM4100 to T5577 with ID 1A2B3C4D5E
[+] Done, written to T5577                            <-- LF clone completed (WIFI-012)
[?] Hint: try `lf search` to verify
```

### PoC - phase 3: emulation (without a physical tag)

```Bash
# The Proxmark3 can emulate the badge directly, without writing any tag
[usb] pm3 --> lf em 410x sim --id 1A2B3C4D5E
```

```
[=] Simulating EM410x - ID 1A2B3C4D5E
[=] Stop simulation by pressing the button           <-- the Proxmark3 IS the badge
```

Emulation allows presenting oneself to the access control reader directly with the Proxmark3, without even needing a physical clone tag.

### Remediation

- **Immediate action:** identify and replace the Low Frequency badges (EM4100, HID Prox): they transmit an ID in cleartext without any protection and are the most trivial to clone
- **Structural action:** migrate to cryptographic High Frequency technologies with mutual authentication (DESFire EV3 AES, Seos, iCLASS SE); the badge ID must never be a simple readable number but the result of a cryptographic challenge; implement multi-factor for sensitive areas and access log correlation
- **Verification:** attempt `lf search` and cloning on the new badges - the secure technologies must not expose a clonable ID nor allow the copy via dump

---

## Transaction sniffing

### Operational context

Beyond the direct reading of the tag, the Proxmark3 can intercept (sniff) the communication between a legitimate reader and a tag during a real transaction. It is useful when the tag is not directly accessible but the moment when it is used is, or to analyze proprietary protocols by observing the exchange.

```Bash
# Sniffing of an HF transaction (14443A) between reader and badge
[usb] pm3 --> hf 14a sniff
# [present the badge to the legitimate reader during the sniffing]
[usb] pm3 --> trace list -t 14a
```

```
      Src | Data                        | Annotation
      Rdr | 52                          | WUPA
      Tag | 04 00                       | ATQA
      Rdr | 93 20                       | ANTICOLL
      Tag | a1 b2 c3 d4 ...             | UID       <-- captured transaction
```

---

## Lab experience

The Proxmark3 filled exactly the limit that the ACR122U had shown in `../nfc-tools/`: the handling of Low Frequency. The test EM4100 badge, invisible to the ACR122U, was read and cloned by the Proxmark3 in a single session of a few seconds. This made concrete a reality of corporate access control: many installations still use LF, and their security is even lower than that of MIFARE Classic, because authentication is entirely absent.

The learning curve was on the pm3 client and its command syntax (which evolved significantly with the Iceman firmware, which became the de facto standard compared to the official firmware). The richness of commands (`lf`, `hf`, `emv`, `hf mf`, with dozens of subcommands) is both the strength and the difficulty of the tool: it covers practically every RFID scenario, but requires knowing exactly which technology one is attacking.

The most instructive function was emulation: the Proxmark3's ability to "become" the badge without writing any physical tag overturned my idea of cloning. There is no need to produce a physical copy; the tool itself, presented to the reader, is sufficient. For a physical security assessment this is very powerful, because it eliminates the need for specific magic tags for each technology.

---

## Theoretical analysis: the spectrum of weakness of RFID technologies

RFID technologies form a security spectrum that goes from completely open to cryptographically robust, and the Proxmark3, covering the entire spectrum, allows appreciating the differences:

1. **LF read-only (EM4100, HID Prox):** they transmit a static ID in cleartext, no authentication. Trivial cloning (read and write). Zero security: they are equivalent to a serial number shouted out loud.

2. **HF with Crypto-1 (MIFARE Classic):** encryption present but broken (see `../nfc-tools/`). Requires the recovery of the keys but is then clonable. Illusory security.

3. **HF with AES (DESFire EV3, Seos):** mutual challenge-response authentication on AES-128, key never exposed. Not clonable via dump. Real security.

The technological progression reflects the evolution of the threat model. LF was born when RFID served only to identify (warehouse, livestock), not to authenticate accesses; using it for access control is an abuse of a technology never designed to resist an adversary. The lesson, valid throughout security, is that the technological choice must correspond to the threat model: an identification technology is not an authentication technology, and treating them as equivalent (as those who use EM4100 to open doors do) is the design error at the root of these findings.

---

## Real-World scenario: Post-Exploitation projection

> This section describes how this finding would fit into a real engagement, from both the attacker (Red Team) and defender (Blue Team) perspectives.

### Attacker perspective (red team)

**Starting point:** ability to clone or emulate LF/HF RFID badges, including the technologies that consumer readers do not handle (WIFI-012).

**Immediate next step:** unauthorized physical access by presenting the clone or the emulation to the access control reader.

**Projected kill chain:**

```
[WIFI-012] Cloned or emulated LF/HF badge
        |
        v
Physical access to the building / restricted areas
        |
        v
Server room / unlocked workstations / implant drop
        |
        v
Internal foothold -> network pivoting (07-post-exploitation)
```

**Potential impact:** the Proxmark3 extends the cloning capability to all RFID technologies, including those most widespread in legacy access control (LF). Emulation even eliminates the need for a physical tag. In a physical security red team, a pocket tool that clones any read badge (even via sniffing at a distance from the reader) is the universal skeleton key. The vector fuels internal network access and combines with social engineering to obtain the necessary proximity.

### Defender perspective (blue team)

**Detection:** as with MIFARE cloning, the clone/emulation is transparent to the reader. The defense is in the analysis of the logs and in the correlation with other systems (video surveillance, attendance).

**Indicators of Compromise (IOC):**
- Accesses with LF badges in contexts that should be migrated to secure HF
- Impossible or anomalous uses of the badge ID (log analysis)
- Anti-passback violations
- Physical presence of suspicious RFID devices (Proxmark3, [Flipper](https://github.com/Nicholas-Arcari/FlipperZero-guide)) detected by inspections or metal detectors in the critical areas

**Containment:** deactivation of the badge ID; replacement with secure technology; audit of the recent accesses.

**Eradication and hardening:**
- Complete decommissioning of LF read-only technologies for access control
- Migration to DESFire/Seos with cryptographic authentication
- Anti-passback, log correlation, multi-factor for the critical areas
- RFID shielding of the issued badges and anti-skimming training

**Defensive lesson:** the ability of a single tool (the Proxmark3) to attack the entire RFID spectrum demonstrates that the defense cannot be based on the obscurity of the technology or on the rarity of the tools. The only structural defense is cryptographic: badges that prove their own authenticity with a challenge that a clone cannot pass. Everything else is apparent security.

---

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `Proxmark3 RDV4` | rfid multi-tool | hardware + client | lf+hf: reading, cloning, sniffing, emulation (professional reference) |
| `Iceman firmware` | pm3 firmware | firmware | community standard firmware, more commands and technologies than the official firmware |
| `pm3 client` | rfid cli | cli | command interface for all rfid operations |
| T5577 tag | hardware | - | rewritable lf tag for Low frequency clones |
| `Flipper Zero` | portable multi-tool | hardware | lf/hf reading and emulation in a pocket form factor |
| `ACR122U` | nfc reader | hardware | hf mifare classic only (`../nfc-tools/`); does not handle lf |

> **Recommended modern tool:** the `Proxmark3 RDV4` with `Iceman` firmware is the professional standard for complete RFID security. The `Flipper Zero` is the pocket alternative for the common LF/HF scenarios and field demonstrations, with superior usability at the cost of slightly reduced capabilities on the more protected tags.

---

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| reconnaissance | gather victim host information | `T1592` | identification of the badge's rfid technology (lf/hf) via `lf/hf search` (WIFI-012) |
| credential access | network sniffing | `T1040` | sniffing of the transaction between reader and badge (WIFI-012) |
| defense evasion | impersonation | `T1656` | cloning/emulation of the badge to impersonate the holder (WIFI-012) |
| initial access | hardware additions | `T1200` | use of the proxmark3 (clone or emulation) for unauthorized physical access (WIFI-012) |
| initial access | valid accounts: local accounts | `T1078.003` | the cloned/emulated badge is equivalent to a valid access credential of the holder |

---

> **Note:** All documented activities were conducted on lab RFID tags and badges owned by the author. Reading, cloning, sniffing and emulation were performed exclusively on test tokens. The cloning and unauthorized use of third-party access badges is a serious crime. Techniques are documented for educational and authorized physical security assessment purposes with a defined scope.
