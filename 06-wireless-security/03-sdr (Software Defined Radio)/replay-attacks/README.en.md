> **English** | [Italiano](README.md)

# Replay Attacks - Capture and Retransmission of RF Signals

> - **Phase:** Wireless Security - RF Replay & Signal Injection (Software Defined Radio)
> - **Visibility:** Medium - the capture is passive; the retransmission emits an RF signal on the target band, potentially detectable by a receiver and - if on a regulated band - by control authorities
> - **Prerequisites:** SDR with transmission capability (HackRF One, not the RTL-SDR which is RX only; or [Flipper Zero](https://github.com/Nicholas-Arcari/FlipperZero-guide) for sub-GHz); signal analysis completed (`../signal-analysis/`, WIFI-008); absence of rolling code confirmed
> - **Output:** WIFI-009; unauthorized actuation of RF-controlled devices (gates, remotes) via retransmission of the captured signal

- **Operating Environment:** Kali Linux (Attacker), HackRF One (RX/TX), Flipper Zero, lab RF devices
- **Target:** Test gate-opener remote (433 MHz, fixed code), test garage remote
- **Main tools:** hackrf_transfer, Universal Radio Hacker (URH), Flipper Zero

---

## Executive Summary

The replay attack is the most direct and conceptually simple RF attack: one captures the signal transmitted by a legitimate remote and retransmits it at a later time to replicate the original action. There is no reverse engineering necessary, there is no cryptography to break: one records and plays back, exactly like an audio recorder.

This triviality is also its danger. Every fixed-code RF device - a huge slice of gate openers, garage remotes, some alarm systems and cheap intercoms - is vulnerable. Finding WIFI-009 documents the actuation of a test gate via replay of the captured signal: an attacker does not need the physical remote, it is enough to have been in radio range when the owner used it once.

The only effective defense is the rolling code, which invalidates every signal after a single use. The section demonstrates both the attack (against fixed code) and the reason why the rolling code neutralizes it, clarifying the fundamental distinction that every physical security assessor must be able to make.

---

## Folder Structure

```
replay-attacks/
+-- README.md      # this file: RF capture and retransmission, fixed vs rolling code (WIFI-009)
+-- img/           # URH capture and HackRF/Flipper Zero setup
```

---

## Replay Attack on Fixed Code

**Finding ID:** `WIFI-009` | **Severity:** `High` (unauthorized actuation of an RF-controlled device - physical access to gates/garages)

### Operational Context

The previous analysis (`../signal-analysis/`, WIFI-008) confirmed that the test gate-opener remote uses a fixed code: repeated actuations produce identical sequences. This is the premise of the replay. With a HackRF (capable of transmitting, unlike the RTL-SDR) or a Flipper Zero, the captured signal is retransmitted to replicate the "open" command.

### PoC - Phase 1: Capture of the raw signal

```Bash
# IQ capture of the burst while actuating the remote (HackRF, 433.92 MHz)
hackrf_transfer -r gate_capture.iq -f 433920000 -s 2000000 -g 40 -l 40
# Press the remote during the capture, then Ctrl+C
```

```
Stop with Ctrl-C
 4.2 MiB / 1.000 sec = 4.2 MiB/second
Exiting... (captured 8388608 samples)      <-- signal recorded in gate_capture.iq
```

### PoC - Phase 2: Retransmission (replay)

```Bash
# Retransmission of the captured signal on the same frequency
hackrf_transfer -t gate_capture.iq -f 433920000 -s 2000000 -x 40
```

```
 4.2 MiB / 1.000 sec = 4.2 MiB/second
Exiting...                                 <-- gate actuated (WIFI-009)
```

The test gate opened: the retransmitted signal is indistinguishable from the original because it is the original, sample by sample.

### PoC - Alternative with Flipper Zero

```
Flipper Zero -> Sub-GHz -> Read (RAW)
   [capture while actuating the remote]
   -> Save "gate_signal"
Flipper Zero -> Sub-GHz -> Saved -> gate_signal -> Send
   -> gate actuated
```

The Flipper Zero makes the attack portable and immediate: capture and replay in a few taps, without a laptop or configuration, directly in the field.

### Remediation

- **Immediate action:** replace the fixed-code remotes with rolling-code devices; this is the only truly effective countermeasure against replay
- **Structural action:** adopt systems with cryptographic rolling code (KeeLoq, AES-128) for every RF access control; where possible, add a second factor (RFID tag, PIN); for critical installations, evaluate systems with bidirectional challenge-response instead of the simple unidirectional transmission
- **Verification:** capture two consecutive actuations and compare them - if they are identical, the system is fixed-code and vulnerable; a rolling code produces different sequences at each press

---

## Why the Rolling Code Neutralizes the Replay

### Operational Context

Repeating the capture on a modern car remote (rolling code), the replay fails: the retransmitted signal is rejected by the receiver. This practically demonstrates the difference between the two models.

```
Fixed code (vulnerable):
   Press 1 -> C5A3-01-E7
   Press 2 -> C5A3-01-E7        <-- identical, replay works

Rolling code (secure):
   Press 1 -> C5A3-[counter:1042]-encrypted-9F2A
   Press 2 -> C5A3-[counter:1043]-encrypted-3B71   <-- different, replay rejected
```

The receiver maintains a synchronized counter and accepts only subsequent never-seen values: an already-used signal (replay) has an obsolete counter and is discarded.

---

## Lab Experience

The switch from the RTL-SDR to the HackRF was the fundamental hardware lesson: the RTL-SDR, used for all the previous analysis, only receives. For the replay a device capable of transmitting is needed, and this required the HackRF One (or, as a portable alternative, the Flipper Zero). It is a reminder that in the RF domain the capabilities of the hardware rigidly define what is possible.

The replay via `hackrf_transfer` of the raw IQ signal worked on the first attempt on the fixed-code remote, confirming how trivial the attack is: I did not have to understand the protocol, only record and play back the samples. The contrast with the attempt on the rolling-code remote was didactically perfect: exact same procedure, null result. Seeing the replay fail made the value of the rolling code tangible much more than any theoretical explanation.

An important practical and legal caution emerged in the exercise: RF transmission is not passive like reception. Transmitting on regulated bands, even at low power, can interfere with legitimate services and is subject to regulation. All the test transmissions were confined to owned devices in a controlled environment and at very low power.

---

## Theoretical Analysis: The Replay as a Failure of Temporal Authentication

The replay attack, in an abstract sense, is the failure of authentication to guarantee the "freshness" of a message. A fixed-code system verifies only that the message is valid (it matches the expected pattern), but not that it is recent or never used before. It lacks the temporal dimension of authentication: any copy of a valid message is accepted, regardless of when it was generated.

This is the same principle that makes digital systems without nonce or timestamp vulnerable - from the replay of session tokens to the replay of network authentication packets. The rolling code solves the problem exactly like nonces in network protocols: it introduces a value that changes at each message (a counter) and that the receiver verifies for uniqueness, rejecting the already-seen values.

The KeeLoq implementation combines the counter with encryption: the counter is encrypted with a shared device-receiver key, so an attacker cannot simply increment it and retransmit - they do not know the key to produce the correct ciphertext of the next counter. Known attacks on KeeLoq exist (Samy Kamkar's RollJam, which intercepts and blocks the signal to reuse it, and cryptographic attacks on the key), but they require techniques much more sophisticated than the simple replay, confirming that the rolling code drastically raises the attack barrier.

---

## Real-World Scenario: Post-Exploitation Projection

> This section describes how this finding would fit into a real engagement, from both the attacker (Red Team) and defender (Blue Team) perspectives.

### Attacker Perspective (Red Team)

**Starting point:** ability to actuate a fixed-code RF-controlled physical access device (WIFI-009) - gate, garage, barrier.

**Immediate next step:** obtaining physical access to the protected area without forcing, silently and repeatably.

**Projected kill chain:**

```
[WIFI-009] Signal replay -> gate/garage opening
        |
        v
Physical access to the perimeter area (parking, courtyard)
        |
        v
Access to physical network points / secondary doors / social engineering (tailgating)
        |
        v
Drop of an implant or access to workstations -> internal foothold
```

**Potential impact:** the control of unprotected RF physical accesses nullifies the physical perimeter security. An attacker who has observed the owner actuate the remote just once (even at a distance, with a directional antenna) can replicate the access at will. The vector links RF security to physical security and internal network access, analogously to badge cloning (`../../04-rfid-nfc (Physical Access)/`).

### Defender Perspective (Blue Team)

**Detection:** cheap RF systems do not log or detect replays. More evolved systems can detect anomalies (actuations at unusual times, duplicate signal patterns with a monitoring receiver).

**Indicators of Compromise (IOC):**
- Gate/garage actuations not correlated to the presence of authorized personnel
- Identical duplicate RF signals detected by a spectrum monitor
- Presence of SDR/Flipper Zero devices detected in the vicinity (physical inspection)

**Containment:** immediate replacement of the fixed-code remotes; reprogramming of the receivers to accept only the new rolling-code devices.

**Eradication and hardening:**
- RF access systems exclusively with cryptographic rolling code
- Two-factor authentication for critical accesses (RF + RFID/PIN)
- Spectrum monitoring in high-value installations
- Video surveillance on the access points to correlate actuations and presences

**Defensive lesson:** an access control system must guarantee that every command is unique and non-reproducible. The convenience of a remote that "always works the same way" is exactly the property that makes it vulnerable: in security, the repeatability of an authentication is a defect, not a feature.

---

## Reference Tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `HackRF One` | SDR TX/RX | Hardware + CLI | Full-duplex RF capture and retransmission (1 MHz - 6 GHz) |
| `hackrf_transfer` | SDR utility | CLI | Capture (`-r`) and replay (`-t`) of raw IQ signals |
| `Universal Radio Hacker` | Signal analyzer | GUI | Capture, analysis and generation/retransmission of signals |
| `Flipper Zero` | Portable multi-tool | Hardware | Portable sub-GHz capture and replay (fixed code) |
| `RTL-SDR` | SDR RX only | Hardware | Reception only (analysis); does not transmit, does not replay |
| `rpitx` / `PortaPack` | TX platform | Hardware | Alternative RF transmission platforms |

> **Recommended modern tool:** the `HackRF One` for flexible lab work (RX+TX on a very wide band) and the `Flipper Zero` for sub-GHz replay in the field. Caution: the Flipper Zero blocks transmission by default on some regulated bands for regulatory compliance.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Credential Access | Network Sniffing | `T1040` | Capture of the remote's RF signal during actuation (WIFI-009) |
| Collection | Adversary-in-the-Middle | `T1557` | Interception of the signal for the purpose of subsequent retransmission |
| Initial Access | Hardware Additions | `T1200` | Use of SDR/Flipper hardware for replay and physical access (WIFI-009) |
| Impact (ICS) | Manipulation of Control | `T0831` | Retransmission of the signal to actuate a physical device (gate) without authorization |

---

> **Note:** All documented activities were conducted on lab RF devices owned by the author, with very low power transmissions in a controlled environment. RF transmission on regulated bands is subject to regulation and the retransmission of signals to actuate third-party devices is a crime. Techniques are documented for educational and authorized security assessment purposes.
