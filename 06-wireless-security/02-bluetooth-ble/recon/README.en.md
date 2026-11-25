> **English** | [Italiano](README.md)

# Bluetooth & BLE recon - discovery and GATT enumeration

> - **Phase:** Wireless Security - Reconnaissance (Bluetooth Classic & Bluetooth Low Energy)
> - **Visibility:** Low - BLE scanning is passive (listening to advertising packets); GATT service enumeration requires a connection to the device (Active but inconspicuous, typical of legitimate client behavior)
> - **Prerequisites:** Compatible Bluetooth adapter (integrated or CSR/Broadcom dongle); BlueZ stack installed; for advanced sniffing: nRF52840 dongle or Ubertooth One
> - **Output:** WIFI-006; inventory of the Bluetooth/BLE devices in range (MAC, name, RSSI, services); map of the exposed GATT services and characteristics; identification of characteristics writable without authentication

- **Operating Environment:** Kali Linux (Attacker), Bluetooth 5.0 dongle, lab IoT/BLE devices (smart lock, test fitness tracker)
- **Target:** Test BLE devices (smart lock, environmental sensor)
- **Main tools:** bluetoothctl, bettercap, gatttool, bluehydra

---

## Executive summary

Bluetooth is often the most overlooked layer of an assessment, but it has become critical with the proliferation of IoT: smart locks, medical devices, wearables, building automation systems almost all communicate via Bluetooth Low Energy (BLE). Unlike 802.11, where the objective is the network, here the objective is the single device and the services it exposes.

BLE reconnaissance is articulated in two levels. The first, discovery, passively captures the advertising packets that every BLE device transmits to announce itself, deriving MAC, name and advertised services. The second, GATT (Generic Attribute Profile) enumeration, establishes a connection to the device and maps its internal structure: services, characteristics, and - the most critical data - the permissions of each characteristic (read, write, notify) and whether they require authentication.

Finding WIFI-006 documents the discovery of GATT characteristics writable without authentication on a test device: the technical premise of the spoofing/manipulation attack documented in the `../spoofing/` section. Many cheap BLE devices delegate security entirely to the mobile application, leaving the GATT layer completely open.

---

## Folder structure

```
recon/
+-- README.md      # this file: BLE discovery + GATT enumeration (WIFI-006)
+-- img/           # bettercap ble.recon screenshots and GATT map
```

---

## Device discovery

**Finding ID:** `WIFI-006` | **Severity:** `Informational` (BLE attack surface mapping; becomes `Medium` if characteristics writable without authentication emerge)

### Operational context

Every BLE device in "connectable" mode transmits advertising packets at regular intervals on the three advertising channels (37, 38, 39). These packets are in cleartext and contain the device address, the name and the advertised services. Discovery is completely passive.

### Execution

```Bash
# Bluetooth Classic + BLE discovery with bluetoothctl
sudo bluetoothctl
[bluetooth]# scan on
```

```
[NEW] Device 4C:65:A8:DB:11:22 SmartLock-A8DB          <-- smart lock (target)
[NEW] Device 60:AB:D2:5F:33:44 Mi Band 6
[NEW] Device C8:2B:96:1A:55:66 EnvSensor-1A55
```

```Bash
# Advanced BLE discovery with bettercap (RSSI, vendor, services)
sudo bettercap
> ble.recon on
> ble.show
```

```
 RSSI │ MAC               │ Vendor         │ Flags       │ Connectable │ Name
 -42  │ 4c:65:a8:db:11:22 │ Espressif      │ BR/EDR, LE  │      yes     │ SmartLock-A8DB
 -67  │ 60:ab:d2:5f:33:44 │ Xiaomi         │ LE only     │      yes     │ Mi Band 6
```

### Execution - GATT service enumeration

```Bash
# Complete enumeration of the target's services and characteristics
> ble.enum 4c:65:a8:db:11:22
```

```
 Handles    │ Service > Characteristics                    │ Properties
 0001-0009  │ Generic Access (1800)
   0003     │   Device Name (2a00)                          │ READ
 000a-0012  │ Device Information (180a)
   000c     │   Manufacturer Name (2a29)                    │ READ
 0013-001f  │ Custom Service (ffe0)
   0015     │   Lock Control (ffe1)                         │ READ, WRITE    <-- writable, no auth (WIFI-006)
   0018     │   Lock Status (ffe2)                          │ READ, NOTIFY
```

The critical row: the characteristic `Lock Control (ffe1)` exposes the `WRITE` property without any authentication or encryption flag. An attacker can write directly to this handle, potentially commanding the lock (explored in `../spoofing/`).

### Write verification (proof of concept read)

```Bash
# Reading the current value of the characteristic with gatttool
gatttool -b 4C:65:A8:DB:11:22 --char-read -a 0x0015
```

```
Characteristic value/descriptor: 00        <-- state "unlocked=0", writable without pairing
```

### Remediation

- **Immediate action:** verify that the GATT characteristics that command sensitive functions (lock/unlock, configuration) require authentication (`Authenticated Signed Writes` flag or pairing with MITM protection)
- **Structural action:** implement BLE Secure Connections (LE Secure Connections, introduced in Bluetooth 4.2) with ECDH-based pairing; apply application-level authorization on every sensitive write (challenge-response), do not rely on the security of the transport layer alone; reduce the transmission power to limit the attack range
- **Verification:** repeat `ble.enum` and confirm that the sensitive characteristics show authentication requirements; an unauthorized write test must fail

---

## Lab experience

The initial obstacle was hardware: the laptop's integrated Bluetooth adapter supported discovery but not passive sniffing of the traffic between two already-paired devices. For discovery and GATT enumeration (direct connection to the device) the integrated adapter was sufficient; for sniffing the pairing between app and device an nRF52840 or an Ubertooth One with dedicated firmware would have been necessary.

The most interesting result emerged from the GATT enumeration of the test device: the structure of the services immediately reveals the manufacturer's security philosophy. The device exposed a `Lock Control` characteristic writable without pairing, delegating all access control to the mobile app. This pattern - security in the app, open BLE layer - is extremely common in cheap IoT devices and turns GATT enumeration from simple recon to discovery of an exploitable vulnerability.

---

## Theoretical analysis: the GATT model and its weaknesses

BLE organizes data according to the Generic Attribute Profile (GATT): the device (GATT server) exposes Services, each containing Characteristics, each with a value and a set of properties (Read, Write, Notify, Indicate) and security permissions. The client (typically the mobile app) reads, writes or subscribes to the notifications.

The BLE security model operates on three levels: pairing (key exchange), bonding (storage of the keys for future connections) and link encryption. The structural weak point is that these controls are optional and configurable per single characteristic: a manufacturer can expose a critical characteristic with write permission but without requiring either pairing or encryption. In that case, anyone in radio range can write to it.

The pre-4.2 BLE versions also used the "Legacy" pairing method with the "Just Works" mode, vulnerable to interception and MITM during the key exchange. LE Secure Connections (4.2+) introduces ECDH (P-256 curve) which protects the exchange, but its adoption depends on the implementation. In practice, the real security of a BLE device depends less on the version of the standard and more on the manufacturer's choices about which characteristics to protect - a fact that GATT enumeration makes immediately visible.

---

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `bluetoothctl` | bluez cli | cli | discovery, pairing and device management via bluez stack |
| `bettercap` | mitm framework | cli | `ble.recon`/`ble.enum` module: discovery and gatt enumeration (the ble reference) |
| `gatttool` | gatt client | cli | direct read/write of gatt characteristics (deprecated but useful) |
| `bluehydra` | bt discovery | cli | continuous bluetooth classic + ble discovery with database |
| `hcitool` / `hciconfig` | bluez legacy | cli | low-level management of the hci interface (legacy) |
| `nRF Connect` | ble explorer | gui / mobile | interactive gatt exploration (desktop and mobile, nordic) |

> **Recommended modern tool:** `bettercap` is the modern reference for BLE recon (the modules `ble.recon`, `ble.enum`, `ble.write` replace the deprecated gatttool and hcitool). For sniffing traffic and pairing, an `nRF52840` dongle with Sniffer firmware or `Ubertooth One`. The [Flipper Zero](https://github.com/Nicholas-Arcari/FlipperZero-guide) integrates a BLE scanner and some GATT functions in a portable form factor for quick physical recon.

---

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| reconnaissance | active scanning | `T1595` | discovery of ble devices via scanning of the advertising packets (WIFI-006) |
| reconnaissance | gather victim host information | `T1592` | enumeration of the gatt services, characteristics and device information (WIFI-006) |
| credential access | network sniffing | `T1040` | passive capture of the advertising packets and (with dedicated hardware) of the ble traffic |

---

> **Note:** All documented activities were conducted on lab Bluetooth/BLE devices owned by the author. The discovery and GATT enumeration were performed exclusively against test devices. Unauthorized access to third-party Bluetooth devices is a crime. Techniques are documented for educational and authorized security assessment purposes.
