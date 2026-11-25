> **English** | [Italiano](README.md)

# 01 - WiFi (802.11)

> - **Phase:** Wireless Security - Attack on 802.11 networks
> - **Visibility:** Variable - from Low (passive monitor mode, offline cracking) to High (deauthentication, rogue AP, WPS bruteforce)
> - **Prerequisites:** WiFi card with monitor mode + packet injection compatible chipset (Atheros AR9271, Realtek RTL8812AU); aircrack-ng suite; dedicated wordlists; GPU for WPA2 cracking
> - **Output:** Findings WIFI-001..005; radio spectrum map; recovered PSKs; credentials via Evil Twin; access to target networks as a legitimate client

---

## Introduction

The `01-wifi (802.11)` section is the largest of the wireless module because 802.11 is the most widespread radio technology and the richest attack surface. Here the objective is to gain access to the target WiFi network - as a credential (PSK/portal) or as a Man-in-the-Middle position - bypassing the physical perimeter of the organization.

The section covers the entire wireless kill chain in four phases:

1. **Recon & Monitor (WIFI-001):** activation of monitor mode and passive spectrum mapping. Discovery of APs, clients and hidden SSIDs via airodump-ng and Kismet. It is the technical prerequisite of every subsequent attack.

2. **Cracking (WIFI-002..003):** recovery of the WPA2 PSK via capture of the 4-way handshake (classic method) and clientless PMKID attack (modern method). Offline cracking with aircrack-ng and hashcat reduces the network's security to the robustness of the password.

3. **Rogue AP & Evil Twin (WIFI-004):** attack on the users rather than the encryption. Creation of a fake AP with captive portal for credential harvesting and the MITM position. Effective even against networks with a robust PSK.

4. **Automated Attacks (WIFI-005):** orchestration of the entire chain with Wifite2 and Airgeddon, including the WPS Pixie-Dust attack that bypasses the PSK by exploiting an implementation weakness of WPS.

Key concept on wordlists: WiFi PSKs often have specific patterns (8 numeric digits - the default of many routers, dates, phone numbers). Dedicated WiFi wordlists and hashcat rules targeting these patterns are documented in `04-system-exploitation/05-password-cracking/wordlists/`.

---

## Folder Structure

```
01-wifi (802.11)/
+-- README.md              # this file: WIFI-001..005 registry + aggregated MITRE
|
+-- recon-monitor/         # WIFI-001: monitor mode, discovery, SSID de-anon (airodump, Kismet)
+-- cracking/              # WIFI-002 WPA2 handshake, WIFI-003 PMKID (aircrack-ng, hashcat)
+-- rogue-ap/              # WIFI-004: Evil Twin + captive portal (hostapd-mana, Airgeddon)
+-- automated-attacks/     # WIFI-005: Wifite2 + WPS Pixie-Dust (Wifite2, Airgeddon, reaver)
```

---

## Recommended Operational Flow

```
[INPUT] Monitor+injection WiFi card, target area in radio range
         |
         v
[1] Recon & Monitor (recon-monitor/)
     +-- airmon-ng start wlan0 -> monitor mode
     +-- airodump-ng -> AP/client map, channel, encryption (WIFI-001)
              |
              v
[2] Strategy selection based on target
     +-- WPS enabled? ----------> automated-attacks/ (Pixie-Dust, quick win) WIFI-005
     +-- Weak PSK likely? ------> cracking/ (handshake/PMKID + dictionary) WIFI-002/003
     +-- Robust PSK / user target? -> rogue-ap/ (Evil Twin, credential harvest) WIFI-004
              |
              v
[3] Attack execution
     +-- handshake/PMKID capture -> offline cracking (hashcat -m 22000)
     +-- or Evil Twin -> captive portal -> credentials
     +-- or Wifite2 -> automated multi-target audit
              |
              v
[4] Network access
     +-- recovered PSK / captured credentials
     -> connection as a legitimate client
              |
              v
[OUTPUT] Internal network access -> 07-post-exploitation (lateral movement, internal scan)
```

---

## Reference Tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `aircrack-ng suite` | Wireless attack suite | CLI | Monitor mode, handshake capture, deauth, cracking (essential) |
| `Kismet` | WIDS / passive sniffer | CLI + Web | Passive discovery, hidden networks, temporal correlation |
| `hashcat` | GPU cracker | CLI | GPU-accelerated WPA2 cracking (mode 22000) |
| `hcxdumptool` | Clientless capture | CLI | PMKID capture without client (modern attack) |
| `Wifite2` | Attack automator | CLI | Automation of the entire wireless audit |
| `Airgeddon` | Multi-attack framework | CLI - Menu | Evil Twin, WPS, DoS in a single guided tool |
| `hostapd-mana` | Rogue AP daemon | CLI | Evil Twin with KARMA for credential harvesting |

> **Recommended modern tool:** the combination `hcxdumptool` + `hashcat -m 22000` for clientless cracking is the modern standard; `Wifite2` for automation; `eaphammer` for WPA2-Enterprise networks (802.1X).

---

## Finding Registry - WiFi Section

| ID | Description | Severity | Subfolder |
| :--- | :--- | :---: | :--- |
| `WIFI-001` | Monitor mode + de-anonymization of hidden SSID and clients via Probe Request | `Low` | `recon-monitor/` |
| `WIFI-002` | WPA2 4-way handshake captured and PSK recovered via dictionary attack | `High` | `cracking/` |
| `WIFI-003` | Clientless PMKID captured and PSK recovered without connected clients | `High` | `cracking/` |
| `WIFI-004` | Evil Twin with captive portal: credential harvesting + MITM position | `Critical` | `rogue-ap/` |
| `WIFI-005` | WPS Pixie-Dust: WPS PIN recovered in seconds, PSK compromised regardless of robustness | `High` | `automated-attacks/` |

---

## MITRE ATT&CK Mapping - Aggregated

| Tactic | Technique | MITRE ID | Related Finding |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Active Scanning | `T1595` | WIFI-001 |
| Reconnaissance | Gather Victim Network Information | `T1590` | WIFI-001 |
| Credential Access | Network Sniffing | `T1040` | WIFI-001, WIFI-002, WIFI-003, WIFI-005 |
| Credential Access | Brute Force: Password Cracking | `T1110.002` | WIFI-002, WIFI-003 |
| Credential Access | Brute Force | `T1110` | WIFI-005 |
| Credential Access | Adversary-in-the-Middle: Evil Twin | `T1557.004` | WIFI-004 |
| Collection | Adversary-in-the-Middle | `T1557` | WIFI-001, WIFI-002, WIFI-004, WIFI-005 |
| Credential Access | Input Capture: Web Portal Capture | `T1056.003` | WIFI-004 |
| Initial Access | Hardware Additions | `T1200` | WIFI-004 |
| Initial Access | Valid Accounts | `T1078` | WIFI-002, WIFI-003, WIFI-004, WIFI-005 |

---

> **Note:** All activities documented in this section were conducted on lab WiFi networks owned by the author, in an isolated radio environment. No attack was directed against third-party networks. The interception and unauthorized access to wireless networks are crimes under current law. Techniques are documented for educational and authorized security assessment purposes.
