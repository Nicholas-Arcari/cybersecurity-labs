> **English** | [Italiano](README.md)

# 04 - RFID / NFC (physical access)

> - **Phase:** Wireless Security - Physical security and access control (RFID/NFC)
> - **Visibility:** Zero toward the access control systems; requires physical proximity to the tag or the reader
> - **Prerequisites:** HF NFC reader (ACR122U) and/or Proxmark3 (LF+HF); magic and T5577 tags for cloning; temporary physical access to the badge; for the field: [Flipper Zero](https://github.com/Nicholas-Arcari/FlipperZero-guide)
> - **Output:** Findings WIFI-010..012; keys and dumps of MIFARE badges; working LF/HF clones; ability to physically impersonate the badge holder

---

## Introduction

The `04-rfid-nfc` section is the border zone between information security and physical security: corporate badges, hotel cards, transport passes and identification systems operate on RFID/NFC. Here the objective is not a network but a physical token of identity, and compromising it means impersonating the person it belongs to in order to gain physical access.

As indicated in the lab notes, this is the border zone with physical security, with a direct link to the Flipper Zero as a portable NFC/RFID multi-tool. The choice of tools depends on the available hardware: with a simple HF reader (ACR122U) or an Android smartphone (libnfc, Mifare Classic Tool) one covers MIFARE Classic; with the Proxmark3 one also covers Low Frequency and protected tags.

The section is articulated in three phases:

1. **NFC Tools (WIFI-010):** reading and identification of HF tags, recovery of MIFARE Classic sector keys (mfoc) and dump of the content. Prerequisite of cloning.

2. **MIFARE Cloning (WIFI-011):** production of a working clone on a magic tag, including the UID. The clone is indistinguishable from the original for the access control reader.

3. **Proxmark3 Client (WIFI-012):** professional hardware for the entire RFID spectrum (LF 125 kHz + HF 13.56 MHz), transaction sniffing and emulation without a physical tag. Covers the technologies that consumer readers do not handle.

The theoretical common thread is the distinction between identification and authentication: MIFARE Classic (Crypto-1 broken) and EM4100 (no authentication) use a readable and falsifiable identifier as if it were a secret. Only the technologies with mutual cryptographic authentication (DESFire AES, Seos) resist cloning.

---

## Folder structure

```
04-rfid-nfc (Physical Access)/
+-- README.md              # this file: WIFI-010..012 registry + aggregated MITRE
|
+-- nfc-tools/             # WIFI-010: reading, MIFARE key recovery, dump (libnfc, mfoc)
+-- mifare-cloning/        # WIFI-011: cloning on magic tag (nfc-mfclassic)
+-- proxmark3-client/      # WIFI-012: LF/HF, sniffing, emulation (Proxmark3)
```

---

## Recommended operational flow

```
[INPUT] Physical access to the target badge, reader/Proxmark3
         |
         v
[1] Technology identification
     +-- nfc-list / lf search / hf search
     -> LF (EM4100/HID) or HF (MIFARE/DESFire)?
              |
              +-- LF EM4100 -> proxmark3-client/ (direct read+clone) WIFI-012
              |
              +-- HF MIFARE Classic -> proceed
              v
[2] Key recovery and dump (nfc-tools/)
     +-- mfoc -O dump.mfd -> keys + content (WIFI-010)
              |
              v
[3] Cloning (mifare-cloning/)
     +-- magic tag + nfc-mfclassic W -> clone with UID (WIFI-011)
     +-- or Proxmark3 -> emulation without physical tag
              |
              v
[OUTPUT] Cloned/emulated badge -> unauthorized physical access
     -> link with 05-social-engineering (proximity) and 07-post-exploitation (internal network)
```

---

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `Proxmark3 RDV4` | rfid multi-tool | hardware | lf+hf: reading, cloning, sniffing, emulation (pro reference) |
| `libnfc` (nfc-list) | nfc library | cli | identification and reading of hf tags |
| `mfoc` / `mfcuk` | mifare cracker | cli | recovery of mifare classic keys (nested/darkside) |
| `nfc-mfclassic` | mifare writer | cli | dump and writing of the clone on a magic tag |
| `Mifare Classic Tool` | nfc app | android | reading/cloning from a smartphone |
| `Flipper Zero` | portable multi-tool | hardware | lf/hf reading, emulation, pocket cloning |
| magic tag / T5577 | hardware | - | writable tags for hf (magic) and lf (T5577) clones |

> **Recommended modern tool:** the `Proxmark3 RDV4` (Iceman firmware) for complete RFID coverage and the `Flipper Zero` for the common field scenarios. For MIFARE Classic only in the lab, the `ACR122U` with libnfc is sufficient and cheap.

---

## Finding registry - RFID/NFC section

| id | description | severity | subfolder |
| :--- | :--- | :---: | :--- |
| `WIFI-010` | key recovery and dump of a mifare classic badge with default keys (nested mfoc attack) | `Medium` | `nfc-tools/` |
| `WIFI-011` | complete cloning of the mifare badge on a magic tag, including the uid - working clone | `High` | `mifare-cloning/` |
| `WIFI-012` | reading and cloning of a Low frequency em4100 badge (no authentication) via proxmark3 | `High` | `proxmark3-client/` |

---

## MITRE ATT&CK mapping - aggregated

| tactic | technique | mitre id | related finding |
| :--- | :--- | :--- | :--- |
| reconnaissance | gather victim host information | `T1592` | WIFI-010, WIFI-012 |
| credential access | brute force | `T1110` | WIFI-010 |
| credential access | network sniffing | `T1040` | WIFI-012 |
| credential access | steal application access token | `T1528` | WIFI-010 |
| resource development | develop capabilities | `T1587` | WIFI-011 |
| defense evasion | impersonation | `T1656` | WIFI-011, WIFI-012 |
| initial access | hardware additions | `T1200` | WIFI-010, WIFI-011, WIFI-012 |
| initial access | valid accounts: local accounts | `T1078.003` | WIFI-011, WIFI-012 |

---

> **Note:** All activities documented in this section were conducted on lab RFID/NFC tags and badges owned by the author. No third-party badge was read, cloned or used. The cloning and unauthorized use of access badges is a serious crime (unauthorized access, identity theft, impersonation). Techniques are documented for educational and authorized physical security assessment purposes.
