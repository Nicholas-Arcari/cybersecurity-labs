> **English** | [Italiano](README.md)

# 03 - SDR (Software Defined Radio)

> - **Phase:** Wireless Security - Attack on the RF spectrum via Software Defined Radio
> - **Visibility:** Zero in reception (pure passive); Medium in transmission (replay, injection)
> - **Prerequisites:** SDR receiver (RTL-SDR ~30 euro for RX; HackRF One for RX/TX); antenna suited to the band; GQRX, URH, GNU Radio; for the field: [Flipper Zero](https://github.com/Nicholas-Arcari/FlipperZero-guide)
> - **Output:** Findings WIFI-008..009; RF signals characterized and demodulated; cleartext telemetry intercepted; actuation of devices via replay

---

## Introduction

The `03-sdr` section is the most advanced of the wireless module and opens a domain historically ignored by security: the sub-GHz RF spectrum. With a cheap receiver (RTL-SDR at 30 euro) or a transmitter like the HackRF One, an entire world of devices becomes accessible - gate openers, car remotes, sensors, alarms, weather stations, industrial devices - that operate in the ISM bands (315, 433, 868, 915 MHz) almost always without encryption.

As indicated in the lab notes, this is the section where the captured radio signals are stored and analyzed (gate openers, car remotes, weather stations), with a natural link to the Flipper Zero as a portable capture and replay tool.

The section is articulated in three phases:

1. **Signal Analysis (WIFI-008):** identification of the signal in the spectrum (GQRX), capture and demodulation, automatic decoding of known protocols (rtl_433) or reverse engineering of custom ones (URH). It is the prerequisite of every active attack.

2. **Replay Attacks (WIFI-009):** capture and retransmission of the signal to replicate an action (opening a gate). Effective against fixed-code systems, neutralized by rolling code. It requires an SDR capable of transmitting (HackRF, Flipper Zero).

3. **GNU Radio Flowgraphs (no finding):** toolbox for custom signal processing, when the ready-to-use tools are not enough.

The guiding principle is that the absence of encryption at the RF layer is the norm in the cheap embedded world, due to historical constraints of cost and consumption. The critical distinction this section teaches is between fixed code (vulnerable to replay) and rolling code (protected).

---

## Folder Structure

```
03-sdr (Software Defined Radio)/
+-- README.md                # this file: WIFI-008..009 registry + aggregated MITRE
|
+-- signal-analysis/         # WIFI-008: capture, demodulation, decoding (GQRX, URH, rtl_433)
+-- replay-attacks/          # WIFI-009: RF capture and retransmission (HackRF, Flipper Zero)
+-- gnu-radio-flowgraphs/    # custom DSP, no finding (GNU Radio Companion)
```

---

## Recommended Operational Flow

```
[INPUT] SDR (RTL-SDR/HackRF), target RF device in range
         |
         v
[1] Signal identification (signal-analysis/)
     +-- GQRX -> waterfall, frequency identification
     +-- rtl_433 -> decoding if known protocol (WIFI-008)
              |
              v
[2] Protocol analysis (signal-analysis/)
     +-- URH -> demodulation, payload structure
     +-- GNU Radio -> if non-standard modulation (gnu-radio-flowgraphs/)
     -> fixed code or rolling code?
              |
              +-- rolling code -> replay ineffective, stop
              |
              +-- fixed code -> proceed
              v
[3] Replay (replay-attacks/) [requires HackRF/Flipper]
     +-- hackrf_transfer -r (capture) -> -t (replay)
     -> actuation of the device (WIFI-009)
              |
              v
[OUTPUT] Control of the RF device -> physical access
     -> link with 04-rfid-nfc and physical security
```

---

## Reference Tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `RTL-SDR` | SDR RX only | Hardware | Cheap reception for analysis (does not transmit) |
| `HackRF One` | SDR TX/RX | Hardware | Full-duplex capture and retransmission (1 MHz - 6 GHz) |
| `GQRX` | SDR receiver | GUI | Waterfall visualization, frequency identification |
| `Universal Radio Hacker` | Signal analyzer | GUI | Demodulation and protocol reverse engineering |
| `rtl_433` | Protocol decoder | CLI | Automatic decoding of 200+ ISM devices |
| `GNU Radio` | DSP framework | GUI - Flowgraph | Custom signal processing |
| `Flipper Zero` | Portable multi-tool | Hardware | Portable sub-GHz capture and replay in the field |

> **Recommended modern tool:** `Universal Radio Hacker` for analysis (capture+demod+generation in one flow), `HackRF One` for RX/TX flexibility in the lab, `Flipper Zero` for sub-GHz recon and replay in the field. Pay attention to the regulations on transmissions.

---

## Finding Registry - SDR Section

| ID | Description | Severity | Subfolder |
| :--- | :--- | :---: | :--- |
| `WIFI-008` | Cleartext RF telemetry intercepted; signal characterized and payload structure revealed | `Informational` | `signal-analysis/` |
| `WIFI-009` | Replay attack on fixed-code remote: unauthorized actuation of a test gate | `High` | `replay-attacks/` |

---

## MITRE ATT&CK Mapping - Aggregated

| Tactic | Technique | MITRE ID | Related Finding |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Host Information | `T1592` | WIFI-008 |
| Credential Access | Network Sniffing | `T1040` | WIFI-008, WIFI-009 |
| Collection | Data from Information Repositories | `T1213` | WIFI-008 |
| Collection | Adversary-in-the-Middle | `T1557` | WIFI-009 |
| Initial Access | Hardware Additions | `T1200` | WIFI-009 |
| Impact (ICS) | Manipulation of Control | `T0831` | WIFI-009 |

---

> **Note:** All activities documented in this section were conducted on lab RF devices owned by the author. Reception was limited to test signals; transmissions (replay) were confined to very low power in a controlled environment. Transmission on regulated bands is subject to regulation and the interception or manipulation of third-party devices is a crime. Techniques are documented for educational and authorized security assessment purposes.
