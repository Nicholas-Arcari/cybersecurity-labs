> **English** | [Italiano](README.md)

# 02 - Bluetooth & BLE

> - **Phase:** Wireless Security - Attack on Bluetooth Classic and Bluetooth Low Energy
> - **Visibility:** Low - passive/inconspicuous discovery and enumeration; the GATT write is an apparently legitimate client connection
> - **Prerequisites:** Bluetooth 4.2+ adapter (integrated or CSR/Broadcom dongle); BlueZ stack; for advanced sniffing: nRF52840 or Ubertooth One
> - **Output:** Findings WIFI-006..007; BLE device inventory and GATT map; manipulation of the state of unprotected IoT devices

---

## Introduction

The `02-bluetooth-ble` section covers a layer often overlooked in assessments but increasingly critical: with the proliferation of IoT, Bluetooth Low Energy (BLE) is the control protocol of smart locks, wearables, medical devices and building automation systems. Unlike 802.11, where the target is the network, here the target is the single device and the services it exposes.

The section is divided into two complementary phases:

1. **Recon (WIFI-006):** discovery of BLE devices via advertising packets and enumeration of the GATT structure (services, characteristics, permissions). The enumeration immediately reveals the manufacturer's security model: which characteristics are protected and which are exposed without authentication.

2. **Spoofing (WIFI-007):** exploitation of the unprotected characteristics identified in the recon. Unauthorized GATT write to manipulate the state of the device (in the test, unlocking of a smart lock) and device impersonation to substitute for a trusted device.

The common thread of the section is a principle of IoT security: many devices delegate security entirely to the mobile application, leaving the BLE transport layer completely open. Since anyone in radio range can connect to the BLE layer, this delegation is a structural error that GATT enumeration makes immediately visible and spoofing exploits.

---

## Folder structure

```
02-bluetooth-ble/
+-- README.md      # this file: WIFI-006..007 registry + aggregated MITRE
|
+-- recon/         # WIFI-006: BLE discovery + GATT enumeration (bettercap, gatttool)
+-- spoofing/      # WIFI-007: unauthorized GATT write + impersonation (bettercap, spooftooph)
```

---

## Recommended operational flow

```
[INPUT] BLE adapter, IoT devices in radio range
         |
         v
[1] Discovery (recon/)
     +-- bettercap ble.recon -> device list (MAC, name, vendor, RSSI)
              |
              v
[2] GATT enumeration (recon/)
     +-- bettercap ble.enum <MAC> -> services, characteristics, permissions (WIFI-006)
     -> identification of WRITE characteristics without authentication
              |
              v
[3] Manipulation (spoofing/)
     +-- ble.write <MAC> <char> <value> -> unauthorized command (WIFI-007)
     +-- or spooftooph -> device impersonation
              |
              v
[OUTPUT] Control of the device -> physical access / data injection
     -> link with 04-rfid-nfc (physical security) and 07-post-exploitation
```

---

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `bettercap` | mitm framework | cli | the ble reference: `ble.recon`, `ble.enum`, `ble.write` |
| `gatttool` | gatt client | cli | direct read/write of characteristics (legacy but precise) |
| `bluetoothctl` | bluez cli | cli | discovery, pairing and device management |
| `spooftooph` | bt address spoofer | cli | bluetooth address cloning for impersonation |
| `btlejack` | ble hijacker | cli | hijacking of active ble connections (micro:bit hardware) |
| `nRF Connect` | ble explorer | gui / mobile | interactive gatt exploration |

> **Recommended modern tool:** `bettercap` is the undisputed reference for BLE recon and manipulation (it replaces the deprecated gatttool/hcitool). For pairing sniffing dedicated hardware is needed (`nRF52840`, `Ubertooth One`); the [Flipper Zero](https://github.com/Nicholas-Arcari/FlipperZero-guide) covers portable recon/replay scenarios.

---

## Finding registry - bluetooth & BLE section

| id | description | severity | subfolder |
| :--- | :--- | :---: | :--- |
| `WIFI-006` | gatt enumeration: control characteristic writable without authentication on iot device | `Informational` | `recon/` |
| `WIFI-007` | unauthorized gatt write: manipulation of the state of a test smart lock | `Medium` | `spoofing/` |

---

## MITRE ATT&CK mapping - aggregated

| tactic | technique | mitre id | related finding |
| :--- | :--- | :--- | :--- |
| reconnaissance | active scanning | `T1595` | WIFI-006 |
| reconnaissance | gather victim host information | `T1592` | WIFI-006 |
| credential access | network sniffing | `T1040` | WIFI-006 |
| collection | adversary-in-the-middle | `T1557` | WIFI-007 |
| defense evasion | impersonation | `T1656` | WIFI-007 |
| impact (ics) | manipulation of control | `T0831` | WIFI-007 |
| initial access | hardware additions | `T1200` | WIFI-007 |

---

> **Note:** All activities documented in this section were conducted on lab Bluetooth/BLE devices owned by the author. No attack was directed against third-party devices. The unauthorized manipulation of Bluetooth devices is a crime. Techniques are documented for educational and authorized security assessment purposes.
