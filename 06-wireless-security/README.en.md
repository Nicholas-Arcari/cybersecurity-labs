> **English** | [Italiano](README.md)

# 06 - Wireless security

> - **Phase:** Wireless Security - Attack on radio technologies (WiFi, Bluetooth, SDR, RFID/NFC)
> - **Visibility:** Variable - from Zero (passive SDR reception, offline cracking) to High (deauthentication, rogue AP, RF transmission)
> - **Prerequisites:** Dedicated radio hardware (monitor+injection WiFi card, BLE adapter, SDR RTL-SDR/HackRF, RFID reader/Proxmark3); Kali Linux with the wireless suite; optional but recommended: [Flipper Zero](https://github.com/Nicholas-Arcari/FlipperZero-guide) as a portable multi-tool
> - **Output:** Findings WIFI-001..012; access to WiFi networks; control of BLE devices; actuation of RF devices; clones of physical access badges

---

## Introduction

The `06-wireless-security` module is dedicated to everything that travels "over the air". Unlike the previous modules that operate on cables, IP and servers, here the transmission medium is the ether and the attack surface is organized by protocol and radio frequency. The common characteristic of all these vectors is that they bypass the traditional physical and network perimeter: an attacker does not need to cross the firewall if they can enter through the WiFi network, unlock a door via BLE, open a gate via RF or clone a badge.

The module structure divides the tools based on the radio technology they attack, covering the entire spectrum of interest for a complete wireless assessment:

1. **WiFi 802.11 (WIFI-001..005):** the richest surface. Monitor mode and recon, WPA2 cracking (handshake and PMKID), Evil Twin with captive portal, automation with Wifite2 and WPS attack. The objective is access to the internal network, beyond the perimeter.

2. **Bluetooth & BLE (WIFI-006..007):** the IoT layer. GATT discovery and enumeration, exploitation of unprotected characteristics to manipulate devices (smart locks, wearables). Often overlooked but critical with the proliferation of connected devices.

3. **SDR - Software Defined Radio (WIFI-008..009):** the sub-GHz RF spectrum. Signal analysis and demodulation, replay attack on fixed-code remotes (gates, garages). With hardware costing a few tens of euros one accesses a domain historically devoid of encryption.

4. **RFID/NFC (WIFI-010..012):** the border with physical security. Key recovery and cloning of access badges (MIFARE Classic, EM4100), up to emulation with Proxmark3. Compromising them means physically impersonating the holder.

A cross-cutting thread, recalled in the lab notes, is the Flipper Zero: a pocket multi-tool that touches WiFi (with dev board), sub-GHz, BLE and RFID/NFC, ideal for recon and quick field attacks, complementary to the specialized hardware used in the lab.

In the MITRE ATT&CK matrix, the module mainly covers Reconnaissance (TA0043), Credential Access (TA0006), Initial Access (TA0001) and Collection (TA0009), with the addition of physical security techniques (Hardware Additions) and, for IoT/OT devices, some ICS techniques. The module is the bridge between the logical security of the previous modules and physical security: its findings open the access that fuels the `07-post-exploitation` module.

---

## Folder structure

```
06-wireless-security/
+-- README.md                          <- this file: finding registry + aggregated MITRE
|
+-- 01-wifi (802.11)/
|   +-- README.md                      <- WIFI-001..005 registry, WiFi MITRE
|   +-- recon-monitor/                 <- WIFI-001 (monitor mode, de-anon SSID)
|   +-- cracking/                      <- WIFI-002 WPA2 handshake, WIFI-003 PMKID
|   +-- rogue-ap/                      <- WIFI-004 (Evil Twin + captive portal - Critical)
|   +-- automated-attacks/             <- WIFI-005 (Wifite2 + WPS Pixie-Dust)
|
+-- 02-bluetooth-ble/
|   +-- README.md                      <- WIFI-006..007 registry, BLE MITRE
|   +-- recon/                         <- WIFI-006 (discovery + GATT enumeration)
|   +-- spoofing/                      <- WIFI-007 (unauthorized GATT write)
|
+-- 03-sdr (Software Defined Radio)/
|   +-- README.md                      <- WIFI-008..009 registry, SDR MITRE
|   +-- signal-analysis/               <- WIFI-008 (capture, demodulation, rtl_433/URH)
|   +-- replay-attacks/                <- WIFI-009 (RF replay on fixed code)
|   +-- gnu-radio-flowgraphs/          <- custom DSP (no finding)
|
+-- 04-rfid-nfc (Physical Access)/
    +-- README.md                      <- WIFI-010..012 registry, RFID/NFC MITRE
    +-- nfc-tools/                     <- WIFI-010 (MIFARE key recovery, dump)
    +-- mifare-cloning/                <- WIFI-011 (cloning on magic tag)
    +-- proxmark3-client/              <- WIFI-012 (LF/HF, emulation)
```

---

## Recommended operational flow

```
[INPUT] Radio hardware (WiFi monitor, BLE, SDR, RFID), target in range
         |
         v
[1] WiFi 802.11 (01-wifi/)
     +-- monitor mode -> WPA2 cracking / Evil Twin / WPS
     -> access to the internal network (WIFI-001..005)
         |
         v
[2] Bluetooth & BLE (02-bluetooth-ble/)
     +-- GATT enumeration -> IoT device manipulation
     -> control of unprotected locks/wearables (WIFI-006..007)
         |
         v
[3] SDR (03-sdr/)
     +-- signal analysis -> replay on fixed code
     -> actuation of gates/remotes (WIFI-008..009)
         |
         v
[4] RFID/NFC (04-rfid-nfc/)
     +-- key recovery -> badge cloning/emulation
     -> physical access impersonating the holder (WIFI-010..012)
         |
         v
[OUTPUT] Access (network / physical / devices)
     -> 07-post-exploitation (lateral movement, persistence)
     -> 05-social-engineering (proximity for skimming, credential reuse)
```

---

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `aircrack-ng suite` | wifi attack suite | cli | monitor mode, handshake, deauth, wpa2 cracking |
| `hashcat` + `hcxdumptool` | wifi cracking | cli | clientless pmkid/handshake cracking (mode 22000) |
| `Wifite2` / `Airgeddon` | wifi automation | cli | automated wireless audit + wps |
| `bettercap` | ble/mitm framework | cli | recon and gatt enumeration, ble manipulation |
| `HackRF One` / `RTL-SDR` | sdr | hardware | capture and replay of sub-ghz rf signals |
| `Universal Radio Hacker` | signal analyzer | gui | rf demodulation and reverse engineering |
| `Proxmark3 RDV4` | rfid multi-tool | hardware | rfid lf/hf cloning, sniffing, emulation |
| `Flipper Zero` | portable multi-tool | hardware | sub-ghz, ble, rfid/nfc in a pocket device |

> **Recommended modern tool:** the combination `hcxdumptool` + `hashcat -m 22000` for WiFi, `bettercap` for BLE, `Universal Radio Hacker` + `HackRF` for RF, `Proxmark3 RDV4` (Iceman) for RFID. The `Flipper Zero` as a cross-cutting multi-tool for recon and quick field attacks.

---

## Finding registry - module 06

| id | description | severity | subfolder |
| :--- | :--- | :---: | :--- |
| `WIFI-001` | monitor mode + de-anonymization of hidden ssid and clients via probe request | `Low` | `01-wifi/recon-monitor/` |
| `WIFI-002` | wpa2 4-way handshake captured and psk recovered via dictionary attack | `High` | `01-wifi/cracking/` |
| `WIFI-003` | clientless pmkid captured and psk recovered without connected clients | `High` | `01-wifi/cracking/` |
| `WIFI-004` | evil twin with captive portal: credential harvesting + mitm position | `Critical` | `01-wifi/rogue-ap/` |
| `WIFI-005` | wps pixie-dust: wps pin recovered in seconds, psk compromised regardless of robustness | `High` | `01-wifi/automated-attacks/` |
| `WIFI-006` | gatt enumeration: control characteristic writable without authentication on iot device | `Informational` | `02-bluetooth-ble/recon/` |
| `WIFI-007` | unauthorized gatt write: manipulation of the state of a test smart lock | `Medium` | `02-bluetooth-ble/spoofing/` |
| `WIFI-008` | cleartext rf telemetry intercepted; signal characterized and payload revealed | `Informational` | `03-sdr/signal-analysis/` |
| `WIFI-009` | replay attack on fixed-code remote: unauthorized actuation of a test gate | `High` | `03-sdr/replay-attacks/` |
| `WIFI-010` | key recovery and dump of a mifare classic badge with default keys (nested mfoc) | `Medium` | `04-rfid-nfc/nfc-tools/` |
| `WIFI-011` | complete cloning of the mifare badge on magic tag, including the uid - working clone | `High` | `04-rfid-nfc/mifare-cloning/` |
| `WIFI-012` | reading and cloning of Low frequency em4100 badge (no authentication) via proxmark3 | `High` | `04-rfid-nfc/proxmark3-client/` |

---

## MITRE ATT&CK mapping - aggregated

| tactic | technique | mitre id | related finding |
| :--- | :--- | :--- | :--- |
| reconnaissance | active scanning | `T1595` | WIFI-001, WIFI-006 |
| reconnaissance | gather victim network information | `T1590` | WIFI-001 |
| reconnaissance | gather victim host information | `T1592` | WIFI-006, WIFI-008, WIFI-010, WIFI-012 |
| credential access | network sniffing | `T1040` | WIFI-001, WIFI-002, WIFI-003, WIFI-006, WIFI-008, WIFI-009, WIFI-012 |
| credential access | brute force: password cracking | `T1110.002` | WIFI-002, WIFI-003 |
| credential access | brute force | `T1110` | WIFI-005, WIFI-010 |
| credential access | adversary-in-the-middle: evil twin | `T1557.004` | WIFI-004 |
| credential access | steal application access token | `T1528` | WIFI-010 |
| collection | adversary-in-the-middle | `T1557` | WIFI-004, WIFI-007, WIFI-009 |
| collection | data from information repositories | `T1213` | WIFI-008 |
| credential access | input capture: web portal capture | `T1056.003` | WIFI-004 |
| resource development | develop capabilities | `T1587` | WIFI-011 |
| defense evasion | impersonation | `T1656` | WIFI-007, WIFI-011, WIFI-012 |
| impact (ics) | manipulation of control | `T0831` | WIFI-007, WIFI-009 |
| initial access | hardware additions | `T1200` | WIFI-004, WIFI-009, WIFI-010, WIFI-011, WIFI-012 |
| initial access | valid accounts | `T1078` | WIFI-002, WIFI-003, WIFI-004, WIFI-005 |
| initial access | valid accounts: local accounts | `T1078.003` | WIFI-011, WIFI-012 |

---

> **Note:** All activities documented in this module were conducted on lab networks, devices and radio tokens owned by the author, in a controlled and isolated environment. No attack was directed against third-party networks, devices or badges. The interception of radio communications, unauthorized access to wireless networks, device manipulation and access badge cloning are crimes under current law. RF transmissions are subject to band regulation. Techniques are documented for educational and authorized security assessment purposes with an explicitly defined scope.
