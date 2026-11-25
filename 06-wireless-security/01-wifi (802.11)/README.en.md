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

## Folder structure

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

## Recommended operational flow

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

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `aircrack-ng suite` | wireless attack suite | cli | monitor mode, handshake capture, deauth, cracking (essential) |
| `Kismet` | wids / passive sniffer | cli + web | passive discovery, hidden networks, temporal correlation |
| `hashcat` | gpu cracker | cli | gpu-accelerated wpa2 cracking (mode 22000) |
| `hcxdumptool` | clientless capture | cli | pmkid capture without client (modern attack) |
| `Wifite2` | attack automator | cli | automation of the entire wireless audit |
| `Airgeddon` | multi-attack framework | cli - menu | evil twin, wps, dos in a single guided tool |
| `hostapd-mana` | rogue ap daemon | cli | evil twin with karma for credential harvesting |

> **Recommended modern tool:** the combination `hcxdumptool` + `hashcat -m 22000` for clientless cracking is the modern standard; `Wifite2` for automation; `eaphammer` for WPA2-Enterprise networks (802.1X).

---

## Finding registry - WiFi section

| id | description | severity | subfolder |
| :--- | :--- | :---: | :--- |
| `WIFI-001` | monitor mode + de-anonymization of hidden ssid and clients via probe request | `Low` | `recon-monitor/` |
| `WIFI-002` | wpa2 4-way handshake captured and psk recovered via dictionary attack | `High` | `cracking/` |
| `WIFI-003` | clientless pmkid captured and psk recovered without connected clients | `High` | `cracking/` |
| `WIFI-004` | evil twin with captive portal: credential harvesting + mitm position | `Critical` | `rogue-ap/` |
| `WIFI-005` | wps pixie-dust: wps pin recovered in seconds, psk compromised regardless of robustness | `High` | `automated-attacks/` |

---

## MITRE ATT&CK mapping - aggregated

| tactic | technique | mitre id | related finding |
| :--- | :--- | :--- | :--- |
| reconnaissance | active scanning | `T1595` | WIFI-001 |
| reconnaissance | gather victim network information | `T1590` | WIFI-001 |
| credential access | network sniffing | `T1040` | WIFI-001, WIFI-002, WIFI-003, WIFI-005 |
| credential access | brute force: password cracking | `T1110.002` | WIFI-002, WIFI-003 |
| credential access | brute force | `T1110` | WIFI-005 |
| credential access | adversary-in-the-middle: evil twin | `T1557.004` | WIFI-004 |
| collection | adversary-in-the-middle | `T1557` | WIFI-001, WIFI-002, WIFI-004, WIFI-005 |
| credential access | input capture: web portal capture | `T1056.003` | WIFI-004 |
| initial access | hardware additions | `T1200` | WIFI-004 |
| initial access | valid accounts | `T1078` | WIFI-002, WIFI-003, WIFI-004, WIFI-005 |

---

> **Note:** All activities documented in this section were conducted on lab WiFi networks owned by the author, in an isolated radio environment. No attack was directed against third-party networks. The interception and unauthorized access to wireless networks are crimes under current law. Techniques are documented for educational and authorized security assessment purposes.
