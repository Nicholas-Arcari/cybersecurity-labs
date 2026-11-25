> **English** | [Italiano](README.md)

# GNU Radio Flowgraphs - Custom Signal Processing

> - **Phase:** Wireless Security - Custom DSP & Signal Processing (Software Defined Radio)
> - **Visibility:** Zero in reception; Medium in transmission (depends on the flowgraph)
> - **Prerequisites:** GNU Radio Companion installed; SDR (RTL-SDR for RX, HackRF for RX/TX); understanding of basic DSP concepts (sampling, filters, demodulation)
> - **Output:** Reusable flowgraphs for custom demodulation/modulation of protocols not supported by the ready-to-use tools

- **Operating Environment:** Kali Linux (Attacker), GNU Radio Companion, RTL-SDR/HackRF
- **Purpose:** Signal processing when URH and rtl_433 are not enough
- **Main tools:** GNU Radio Companion (GRC), gr-osmosdr

---

## Executive Summary

GNU Radio is the reference signal processing (DSP) framework for Software Defined Radio. While GQRX visualizes, rtl_433 decodes known protocols and URH handles the common cases of reverse engineering (see `../signal-analysis/`), GNU Radio steps in when one needs to build a custom processing chain: non-standard modulations, complex protocols, real-time decoding, or the integration of multiple stages (filters, demodulators, decoders) in a tailored flow.

This subfolder does not document a specific finding: it is a methodological toolbox. GNU Radio Companion (GRC) allows building flowgraphs visually by connecting functional blocks (SDR source, filters, demodulators, sink) like a block diagram, generating the underlying Python code. It is the tool to resort to when the analysis of a signal (WIFI-008) exceeds the capabilities of the ready-to-use tools.

---

## Folder Structure

```
gnu-radio-flowgraphs/
+-- README.md      # this file: GNU Radio flowgraph methodology for custom DSP
+-- img/           # GRC flowgraph screenshots
```

---

## Anatomy of a Reception Flowgraph

### Operational Context

A typical reception flowgraph for the analysis of a sub-GHz signal connects four stages: acquisition from the SDR, channel filtering, demodulation and output. Each block has configurable parameters (frequency, sample rate, filter bandwidth) that are adjusted based on the target signal.

```
RX Flowgraph (conceptual scheme):

[osmocom Source]      # acquisition from the SDR (RTL-SDR/HackRF)
  freq: 433.92M
  sample_rate: 2M
       |
       v
[Low Pass Filter]     # isolates the channel, removes out-of-band noise
  cutoff: 100k
       |
       v
[Quadrature Demod]    # FSK demodulation (or AM Demod for OOK/ASK)
       |
       v
[Binary Slicer]       # converts to a bit sequence
       |
       v
[File Sink / Scope]   # output: bit stream or visualization
```

### Execution

```Bash
# Start GNU Radio Companion (graphical flowgraph editor)
gnuradio-companion

# The .grc flowgraph automatically generates an executable Python script:
python3 rx_433_fsk.py
```

The flowgraph, once built and validated, is reusable and parameterizable: the same scheme serves for any FSK signal changing only frequency and sample rate. This is the advantage over the monolithic tools: the processing chain is completely under control and adaptable.

---

## When to Use GNU Radio instead of URH or rtl_433

### Comparative Analysis

The choice of tool depends on the nature of the signal and the objective:

- **rtl_433:** known commercial protocol (200+ supported devices). Zero configuration, immediate decoding. Always first choice.
- **Universal Radio Hacker (URH):** unknown protocol but with standard modulation (OOK/FSK/PSK) and relatively simple structure. Interactive reverse engineering. Second choice.
- **GNU Radio:** non-standard modulation, multi-stage processing, real-time decoding, or the need to integrate the processing into a larger system. Maximum flexibility, maximum complexity. Last resort when the others are not enough.

The natural progression in an RF assessment is therefore: try rtl_433, then URH, and resort to GNU Radio only for the signals that resist both. GNU Radio requires the understanding of the DSP fundamentals (sampling theorem, aliasing, decimation, types of demodulation) that the higher-level tools hide.

---

## Lab Experience

In the lab path, GNU Radio was the least used but the most formative tool. For the test devices (weather sensor, remotes), rtl_433 and URH were sufficient and GNU Radio would have been overkill. Its usefulness emerged in understanding what those tools do "under the hood": manually building an ASK demodulation flowgraph clarified concepts (decimation, channel filtering, bit slicing) that URH executes automatically but hides.

The learning curve is steep and tied to the fundamentals of signal processing, not to the interface. The operational lesson was one of priority: in a real assessment with limited time, GNU Radio is not the first tool to open, but the knowledge of its concepts is what allows correctly interpreting the results of the automatic tools and tackling the signals that these do not handle.

---

## Reference Tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `GNU Radio Companion` | DSP framework | GUI - Flowgraph | Visual construction of signal processing chains |
| `gr-osmosdr` | SDR source block | Library | GNU Radio interface toward RTL-SDR, HackRF, other SDRs |
| `Universal Radio Hacker` | Signal analyzer | GUI | Simpler alternative for most cases (see `../signal-analysis/`) |
| `Python + NumPy/SciPy` | DSP scripting | Code | Programmatic signal processing for custom cases |
| `inspectrum` | Signal visualizer | GUI | Preliminary visual analysis before building the flowgraph |

> **Recommended modern tool:** for most assessments, `Universal Radio Hacker` covers the use cases with a fraction of the complexity of GNU Radio. Reserve GNU Radio for signals with non-standard modulations or the need for real-time processing. GNU Radio remains the academic and professional standard for DSP when flexibility is a priority.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Host Information | `T1592` | Construction of custom DSP chains to demodulate and analyze non-standard RF signals |
| Credential Access | Network Sniffing | `T1040` | Signal processing to extract data from RF transmissions with custom protocols |

---

> **Note:** This subfolder documents signal processing methodology and tools, without specific findings. Every capture and transmission activity must be conducted on owned devices in a controlled environment and in compliance with the regulations on radio bands. Techniques are documented for educational and authorized security assessment purposes.
