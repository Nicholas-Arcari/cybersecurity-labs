> **English** | [Italiano](README.md)

# Recon & Monitor Mode - 802.11 Spectrum Mapping

> - **Phase:** Wireless Security - Reconnaissance & Passive Discovery (802.11)
> - **Visibility:** Low - the card in monitor mode listens without transmitting (no packet toward the target networks); de-anonymization of hidden SSIDs requires sending deauthentication frames (Active - generates traffic detectable by a WIDS)
> - **Prerequisites:** WiFi card with monitor mode and packet injection compatible chipset (Atheros AR9271, Ralink RT3070, Realtek RTL8812AU); drivers and aircrack-ng suite installed; external antenna recommended for extended coverage
> - **Output:** WIFI-001; complete map of the 802.11 networks in range (BSSID, ESSID, channel, encryption, signal power); list of associated clients for each AP; de-anonymized hidden SSIDs; database for the cracking and rogue AP phases

- **Operating Environment:** Kali Linux (Attacker), Alfa AWUS036ACH card (monitor mode + injection), isolated lab WiFi network
- **Target:** Test WPA2-PSK access point (SSID `LAB-CORP`) + an AP with hidden SSID (`LAB-HIDDEN`)
- **Main tools:** airmon-ng, airodump-ng, Kismet

---

## Executive Summary

Wireless reconnaissance is the first act of every attack on the 802.11 physical layer: before one can attack a network one must see it. Unlike traditional network recon (module 01-recon) which operates on IP and ports, here the transmission medium is the ether and the unit of observation is the 802.11 management frame, which stations transmit in cleartext even on WPA2-encrypted networks.

Monitor mode turns the WiFi card into a passive receiver that captures all the frames in the air, not just those destined for the attacker. From these frames the entire radio topology is reconstructed: which APs exist, with what encryption, on which channel, which clients are associated and - the most valuable data - which clients are looking for networks they connected to in the past (Probe Request), revealing their mobility patterns.

Finding WIFI-001 documents the de-anonymization of a hidden SSID: the widespread practice of "hiding" the network name as a security measure is ineffective, because the name is still transmitted in cleartext in the association frames every time a legitimate client connects.

---

## Folder Structure

```
recon-monitor/
+-- README.md      # this file: monitor mode setup, discovery, hidden SSID de-anon
+-- img/           # airodump-ng screenshots and Kismet dashboard
```

---

## Monitor Mode Activation

**Finding ID:** `WIFI-001` | **Severity:** `Low` (information disclosure: hidden SSID de-anonymized + clients de-anonymized via Probe Request)

### Operational Context

The WiFi card in normal mode (managed) processes only the frames destined for its own MAC address. Monitor mode disables this filter and allows the capture of all radio frames on the current channel. It is the technical prerequisite of every subsequent wireless activity: without monitor mode it is possible neither to capture handshakes nor to perform injection.

### Execution

```Bash
# Identification of the wireless interface and interfering processes
sudo airmon-ng
sudo airmon-ng check kill        # terminates NetworkManager and wpa_supplicant

# Monitor mode activation (creates wlan0mon)
sudo airmon-ng start wlan0

# Status check
iwconfig wlan0mon
```

```
PHY     Interface       Driver          Chipset
phy0    wlan0           88XXau          Realtek RTL8812AU

        (mac80211 monitor mode vif enabled for [phy0]wlan0 on [phy0]wlan0mon)   <-- monitor active
        (mac80211 station mode vif disabled for [phy0]wlan0)
```

---

## Network Discovery with airodump-ng

### Operational Context

airodump-ng performs automatic channel hopping across all 2.4 GHz channels (and 5 GHz if the chipset supports it), capturing the Beacon frames transmitted by the APs and the client frames. It produces in real time the complete map of the spectrum.

### Execution

```Bash
# Complete spectrum scan (automatic channel hopping)
sudo airodump-ng wlan0mon

# Targeted capture on a specific AP (fixed BSSID + channel) with file saving
sudo airodump-ng --bssid AA:BB:CC:DD:EE:FF -c 6 -w capture_lab wlan0mon
```

```
 CH  6 ][ Elapsed: 2 mins ][ 2026-05-12 14:30

 BSSID              PWR  Beacons    #Data, #/s  CH   MB   ENC  CIPHER  AUTH ESSID

 AA:BB:CC:DD:EE:FF  -42      312      1240   12   6  270   WPA2 CCMP   PSK  LAB-CORP        <-- WPA2 target
 11:22:33:44:55:66  -58      201        45    0  11  130   WPA2 CCMP   PSK  <length: 10>    <-- hidden SSID
 99:88:77:66:55:44  -71      145         3    0   1   54   OPN              GuestFree       <-- open network

 BSSID              STATION            PWR   Rate    Lost    Frames  Notes  Probes

 AA:BB:CC:DD:EE:FF  A0:B1:C2:D3:E4:F5  -48    1e-6e     0       340         LAB-CORP
 11:22:33:44:55:66  60:70:80:90:A0:B0  -62    1e-1e    12        88         LAB-HIDDEN,HomeNet   <-- Probe Request
```

The most significant rows: the AP `11:22:33:44:55:66` exposes `<length: 10>` as ESSID (hidden SSID, 10 characters), but one of its clients in the Probes column reveals `LAB-HIDDEN` - the real network name was intercepted from the client's Probe Request.

---

## Hidden SSID De-anonymization

### Operational Context

If no client is transmitting Probe Requests, the SSID revelation can be forced by sending a deauthentication frame to an associated client: the client disconnects and re-associates immediately, and during re-association it transmits the SSID in cleartext in the Association Request frame.

### Execution

```Bash
# Targeted deauthentication of a client (forces re-association)
sudo aireplay-ng --deauth 5 -a 11:22:33:44:55:66 -c 60:70:80:90:A0:B0 wlan0mon
```

```
14:35:02  Waiting for beacon frame (BSSID: 11:22:33:44:55:66) on channel 11
14:35:02  Sending 64 directed DeAuth (code 7). STMAC: [60:70:80:90:A0:B0]  [ 8|12 ACKs]
14:35:04  Sending 64 directed DeAuth (code 7). STMAC: [60:70:80:90:A0:B0]  [ 6|10 ACKs]
```

```
 BSSID              CH   ENC  ESSID
 11:22:33:44:55:66  11   WPA2  LAB-HIDDEN         <-- SSID revealed after re-association
```

### Remediation

- **Immediate action:** do not rely on SSID hiding as a security measure; the name is transmitted in cleartext anyway. Removing SSID hiding eliminates a false sense of security without reducing the real protection (which depends exclusively on the robustness of the PSK and the encryption protocol)
- **Structural action:** adopt WPA3-SAE where supported (protects against offline attacks on the PSK); configure mandatory Protected Management Frames (PMF, 802.11w) to prevent forged deauthentication frames; on corporate networks migrate to WPA2/WPA3-Enterprise (802.1X) which eliminates the shared PSK
- **Verification:** a WIDS (Wireless IDS) like Kismet or the wireless module of a corporate controller must generate alerts on deauth flood patterns

---

## Kismet - Continuous Monitoring and WIDS

### Operational Context

Airodump-ng is ideal for the pinpoint attack session; Kismet is the choice for continuous monitoring and extended passive analysis. Kismet correlates the data over time, maintains an SQLite database of all seen devices, geolocates the APs if connected to a GPS, and operates as a Wireless IDS detecting deauth floods and rogue APs.

### Execution

```Bash
# Start Kismet on the interface in monitor mode
sudo kismet -c wlan0mon
# Web interface: http://localhost:2501
```

Kismet also captures the devices that airodump-ng ignores: Bluetooth devices (with a dedicated datasource), hidden networks correlated over time, and "silent" clients that transmit only sporadic Probe Requests. The web dashboard allows filtering by type, visualization of the signal power over time and export in Wigle format for wardriving mapping.

---

## Recommended Operational Flow

```
[1] Interface setup
     +-- airmon-ng check kill        # removes interfering processes
     +-- airmon-ng start wlan0       # creates wlan0mon
              |
              v
[2] Broad-spectrum discovery
     +-- airodump-ng wlan0mon        # channel hopping, maps all networks
     -> identification of BSSID, channel, encryption, clients
              |
              v
[3] Targeted capture
     +-- airodump-ng --bssid <BSSID> -c <CH> -w capture wlan0mon
     -> data collection on the single target
              |
              v
[4] De-anonymization (if hidden SSID)
     +-- aireplay-ng --deauth 5 -a <BSSID> -c <CLIENT> wlan0mon
     -> SSID revealed in Association Request (WIFI-001)
              |
              v
[5] Extended monitoring / WIDS
     +-- kismet -c wlan0mon          # temporal correlation, rogue detection
              |
              v
[OUTPUT] Complete radio map -> input for cracking/ and rogue-ap/
```

---

## Reference Tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `airmon-ng` | Monitor mode manager | CLI | Monitor mode activation and management of interfering processes |
| `airodump-ng` | Wireless sniffer | CLI | Network/client discovery, handshake capture, channel hopping |
| `aireplay-ng` | Frame injector | CLI | Deauthentication, forcing re-association for SSID de-anon |
| `Kismet` | WIDS / passive sniffer | CLI + Web UI | Continuous monitoring, temporal correlation, rogue detection |
| `iw` | Wireless config | CLI | Interface configuration, verification of chipset capabilities |
| `hcxdumptool` | Modern capture | CLI | PMKID and handshake capture (modern alternative to airodump) |

> **Recommended modern tool:** `hcxdumptool` (ZerBea) replaces airodump-ng for clientless capture: it acquires the PMKID directly from vulnerable APs without waiting for a complete handshake, drastically reducing collection times. It integrates with `hcxtools` for conversion to the hashcat format. See `../cracking/` for the PMKID attack (WIFI-003).

---

## Theoretical Analysis: Why Management Frames Are in Cleartext

The 802.11 standard encrypts exclusively the payload of the data frames (Data frames) via WPA2/WPA3. The management frames (Management frames: Beacon, Probe Request/Response, Association, Deauthentication) and the control frames travel in cleartext by design necessity: a client must be able to discover and negotiate the association to a network before establishing the session keys. This is the intrinsic Achilles' heel of the protocol.

It follows that three categories of information are always extractable passively, regardless of the robustness of the encryption:

1. **Network metadata:** BSSID, ESSID (even if "hidden", it is revealed in the Association), channel, capabilities, type of encryption.
2. **Client topology:** which stations are associated to which AP, reconstructable from the address field of the Data frames.
3. **Mobility history:** the Probe Requests contain the names of the networks the device connected to in the past (Preferred Network List), allowing device tracking and - in finding WIFI-001 - de-anonymization.

The introduction of Protected Management Frames (802.11w) only mitigates the forgery of deauth/disassoc frames, but does not encrypt Beacon and Probe. The real defense is not to hide these metadata (impossible), but to make their knowledge useless via a robust PSK or 802.1X authentication.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Active Scanning | `T1595` | Channel hopping and 802.11 spectrum scanning to map APs and clients (WIFI-001) |
| Reconnaissance | Gather Victim Network Information | `T1590` | Collection of BSSID, ESSID, encryption and client topology from the 802.11 management frames |
| Credential Access | Network Sniffing | `T1040` | Passive capture of radio frames in monitor mode for metadata and Probe Request extraction |
| Collection | Adversary-in-the-Middle | `T1557` | Deauthentication of a client to force re-association and reveal the hidden SSID (WIFI-001) |

---

> **Note:** All documented activities were conducted on a lab WiFi network owned by the author, in an isolated radio environment. The traffic capture and the deauthentication frames were directed exclusively against test APs and clients. Intercepting third-party WiFi networks without explicit authorization is a crime under current legislation on electronic communications.
