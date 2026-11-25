> **English** | [Italiano](README.md)

# Signal Analysis - Capture and Demodulation with SDR

> - **Phase:** Wireless Security - RF Reconnaissance & Signal Analysis (Software Defined Radio)
> - **Visibility:** Zero - SDR reception is completely passive; no transmission, no detectable emission (pure reception of the radio spectrum)
> - **Prerequisites:** SDR receiver (RTL-SDR 30 euro for reception only, HackRF One for RX/TX); antenna suited to the target band; GQRX/URH installed; knowledge of the target signal's band
> - **Output:** WIFI-008; identification and characterization of RF signals (frequency, modulation, encoding); demodulation of cleartext telemetry; base for the replay attacks (`../replay-attacks/`)

- **Operating Environment:** Kali Linux (Attacker), RTL-SDR v3 + HackRF One, lab RF devices
- **Target:** Test 433 MHz remote, wireless weather sensor, test garage remote
- **Main tools:** GQRX, Universal Radio Hacker (URH), rtl_433

---

## Executive Summary

Software Defined Radio (SDR) shifts radio signal processing from dedicated hardware to software: a cheap receiver (RTL-SDR at 30 euro) captures the entire RF spectrum and the software handles demodulation and decoding. This opens to security a huge and historically ignored domain - remotes, sensors, alarm systems, gate openers, car keys, industrial devices - that operates in the ISM bands (315, 433, 868, 915 MHz) often without any encryption.

This section covers the analysis phase: identifying a signal in the spectrum (GQRX), capturing and demodulating it to understand its structure (URH), and - where the protocol is known - decoding it directly (rtl_433). It is the indispensable prerequisite of the active attacks: before one can repeat or forge a signal (`../replay-attacks/`) one must understand its modulation, encoding and payload structure.

Finding WIFI-008 documents the cleartext capture of the telemetry of a wireless sensor: many devices transmit data (temperature, status, identifiers) without encryption or authentication, exposing information and allowing falsification. It is the demonstration that the absence of encryption at the RF layer is the norm, not the exception, in the world of cheap embedded devices.

---

## Folder Structure

```
signal-analysis/
+-- README.md      # this file: capture, demodulation and analysis of RF signals (WIFI-008)
+-- img/           # GQRX waterfall and URH analysis
```

---

## Signal Identification with GQRX

**Finding ID:** `WIFI-008` | **Severity:** `Informational` (cleartext RF telemetry intercepted; enables the replay attacks documented separately)

### Operational Context

The first step is to locate the signal in the spectrum. GQRX provides a waterfall visualization (frequency on the X axis, time on the Y axis, intensity in colors) that makes every transmission visible. Actuating the target device (pressing the remote) one observes the "burst" appear at a precise frequency, which becomes the starting point for the targeted capture.

### Execution

```Bash
# Start GQRX with RTL-SDR, tuned to the ISM 433 MHz band
gqrx
# Device: RTL-SDR, Center freq: 433.920 MHz, Sample rate: 2.4 Msps
# Actuate the remote -> observe the burst in the waterfall
```

```
Waterfall @ 433.920 MHz:
  433.900   433.920   433.940
     |         |         |
     .    ####BURST####   .        <-- OOK transmission at ~433.92 MHz (remote)
     .         |         .
```

```Bash
# Automatic decoding if the protocol is known (rtl_433 knows 200+ devices)
rtl_433 -f 433920000
```

```
time      : 2026-05-14 16:22:10
model     : Nexus-TH   House Code: 210   Channel: 1
Temperature: 21.5 C     Humidity: 48 %          <-- cleartext telemetry (WIFI-008)
Integrity : CRC
```

rtl_433 recognizes and decodes the weather sensor directly: temperature, humidity and house code are transmitted in cleartext, without encryption or authentication.

---

## Protocol Analysis with Universal Radio Hacker (URH)

### Operational Context

When the protocol is not known to rtl_433, one moves to URH: it captures the raw signal (IQ samples), demodulates it (ASK/OOK, FSK, PSK), and allows analyzing the bit sequence to reverse-engineer the protocol. URH is the tool that turns a radio burst into an interpretable bit sequence.

### Execution

```
URH Workflow:
[1] Record Signal -> IQ capture of the burst (RTL-SDR @ 433.92 MHz)
[2] Interpretation -> demodulation:
       Modulation: ASK/OOK
       Bit length: 350 samples
       -> binary sequence: 1010 0011 1100 0101 ...
[3] Analysis -> identification of the structure:
       [Preamble] [Device ID] [Command] [CRC]
       AAAA        C5A3        01(open)   E7
[4] Generation -> synthesis of a new signal modifying the payload
```

The revealed structure (preamble, device ID, command, CRC) shows a static protocol without rolling code: the same command always produces the same sequence, which makes it vulnerable to replay (explored in `../replay-attacks/`).

### Remediation

- **Immediate action:** treat as public all the information transmitted via RF in cleartext; do not rely on the secrecy of the protocol (security by obscurity)
- **Structural action:** for devices that transmit sensitive data or commands, adopt payload encryption and authentication; for commands (remotes, keys), implement rolling code (KeeLoq, AES) which prevents replay; for telemetry, if confidentiality is required, encrypt at the application level
- **Verification:** re-capture the signal after the hardening and confirm that the payload is encrypted and that identical commands produce different sequences (rolling code)

---

## Lab Experience

The learning curve was mostly on the concepts of signal processing, not on the tools. The first difficulty was the choice of the sample rate and gain in GQRX: a gain too high saturated the receiver, one too low made the signal indistinguishable from noise. The empirical adjustment by observing the waterfall was more effective than any theoretical value.

The key moment was the use of rtl_433: its ability to automatically decode 200+ commercial protocols made the interception of the weather sensor trivial. This resized my perception of the difficulty: many RF devices use standard and well-documented protocols, and their decoding does not require reverse engineering but only the right tool. URH was needed only for the garage remote, whose custom protocol required manual demodulation and analysis of the bit structure.

The most significant observation was the systematic absence of encryption: every test device transmitted in cleartext. This is not an isolated case of the lab but the norm for cheap embedded RF, where the constraints of cost, consumption and simplicity have historically prevailed over security.

---

## Theoretical Analysis: Why Embedded RF Is Historically Insecure

Sub-GHz RF devices (315/433/868 MHz) were born in an era and in a market segment where security was not a concern: low-cost and low-consumption microcontrollers, minimal memory, no cryptographic capability. The implicit threat model was the low probability that someone had the equipment to intercept - an assumption demolished by the advent of cheap SDRs.

Technically, most of these devices use simple modulations (OOK/ASK - On-Off Keying, or FSK) with elementary line encodings (Manchester, PWM) and static payloads. There is no nonce, no timestamp, no challenge-response: the receiver accepts any signal that matches the expected pattern. This makes them transparent to analysis and vulnerable to replay.

The critical distinction is between fixed-code systems and rolling-code systems. A fixed code always transmits the same sequence for the same command (vulnerable). A rolling code (KeeLoq, used in modern car keys) uses a synchronized and encrypted counter: every transmission is different and valid only once, neutralizing replay. The presence or absence of rolling code, revealed by the URH analysis (do identical commands produce identical or different sequences?), determines whether the device is vulnerable - the direct bridge toward `../replay-attacks/`.

---

## Reference Tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `GQRX` | SDR receiver | GUI | Waterfall visualization, frequency identification of the signals |
| `Universal Radio Hacker` | Signal analyzer | GUI | Demodulation, protocol reverse engineering, signal generation |
| `rtl_433` | Protocol decoder | CLI | Automatic decoding of 200+ commercial ISM devices |
| `SDR++` / `CubicSDR` | SDR receiver | GUI | Modern alternatives to GQRX for spectrum visualization |
| `GNU Radio` | DSP framework | GUI - Flowgraph | Custom signal processing (see `../gnu-radio-flowgraphs/`) |
| `inspectrum` | Signal visualizer | GUI | Visual analysis and measurement of captured signals |

> **Recommended modern tool:** `Universal Radio Hacker` (URH) is the reference for the analysis and reverse engineering of RF protocols: it integrates capture, demodulation, analysis and generation in a single flow. The [Flipper Zero](https://github.com/Nicholas-Arcari/FlipperZero-guide) brings sub-GHz analysis and capture into a pocket device, ideal for RF recon in the field.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Host Information | `T1592` | Identification and characterization of RF devices via spectrum analysis (WIFI-008) |
| Credential Access | Network Sniffing | `T1040` | Passive capture and demodulation of RF signals and cleartext telemetry (WIFI-008) |
| Collection | Data from Information Repositories | `T1213` | Extraction of telemetry data (temperature, ID, status) transmitted in cleartext |

---

> **Note:** All documented activities were conducted in passive reception on lab RF devices owned by the author. Reception was limited to test signals in ISM bands. The interception of third-party radio communications may violate the regulations on electronic communications. Transmissions (`../replay-attacks/`) require further attention to the permitted bands. Techniques are documented for educational and authorized security assessment purposes.
