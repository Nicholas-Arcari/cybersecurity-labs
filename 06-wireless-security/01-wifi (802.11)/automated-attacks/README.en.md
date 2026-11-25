> **English** | [Italiano](README.md)

# Automated Attacks - Wifite2 & Airgeddon

> - **Phase:** Wireless Security - Attack Automation & Orchestration (802.11)
> - **Visibility:** High - the automated attacks include deauthentication, WPS PIN bruteforce and handshake capture, all detectable by a WIDS
> - **Prerequisites:** Active monitor mode (see `../recon-monitor/`); configured wordlists; understanding of the individual attacks (`../cracking/`, `../rogue-ap/`) to interpret the results
> - **Output:** WIFI-005; complete automated wireless audit on multiple targets; captured handshakes/PMKIDs; recovered WPS PINs; cracked PSKs in a single session

- **Operating Environment:** Kali Linux (Attacker), monitor + injection card, lab WPA2/WPS networks
- **Target:** Multiple test networks, including an AP with WPS enabled
- **Main tools:** Wifite2, Airgeddon, reaver, bully

---

## Executive Summary

The manual attacks documented in the previous sections (`recon-monitor`, `cracking`, `rogue-ap`) are didactically essential but do not scale on a real audit with dozens of networks. Wifite2 and Airgeddon automate the entire chain: scanning, prioritization of targets by signal power and vulnerability, sequential execution of all applicable attacks (handshake, PMKID, WPS Pixie-Dust, WPS PIN bruteforce), and final cracking.

The value of these orchestrators is not to do something that the manual tools do not do, but to do it in a systematic and repeatable way: Wifite2 automatically tries the most efficient attack for each target and moves to the next, producing a complete audit while the operator analyzes something else. Finding WIFI-005 documents in particular the WPS Pixie-Dust attack, which exploits an implementation weakness to recover the WPS PIN (and therefore the PSK) in seconds, regardless of the robustness of the password.

---

## Folder Structure

```
automated-attacks/
+-- README.md      # this file: Wifite2 orchestration + WPS Pixie-Dust (WIFI-005)
+-- img/           # Wifite2 session screenshots
```

---

## Wifite2 - Automated Wireless Audit

**Finding ID:** `WIFI-005` | **Severity:** `High` (WPS Pixie-Dust: WPS PIN recovered in seconds, PSK compromised regardless of robustness)

### Operational Context

Wifite2 is a Python wrapper around the entire aircrack-ng, hcxdumptool, reaver and bully suite. It presents a list of targets ordered by power and allows selecting the objectives; for each it automatically executes the most promising sequence of attacks, handling deauth, capture and cracking without manual intervention.

### PoC - Wifite2 session

```Bash
# Start with targeting on WPA/WPS and use of the default wordlist
sudo wifite --wpa --wps --dict /usr/share/wordlists/rockyou.txt
```

```
   NUM  ESSID              CH  ENCR   POWER  WPS  CLIENT
   ---  --------           --  -----  -----  ---  ------
   1    LAB-CORP            6  WPA2    58db   no    1
   2    LAB-WPS-AP         11  WPA2    52db   yes   0        <-- WPS enabled (vulnerable)
   3    LAB-GUEST           1  WPA2    41db   no    0

[+] select target(s) (1-3): 2

[+] LAB-WPS-AP (11): WPS Pixie-Dust attack
[+] Pixie-Dust: collecting WPS hash from the first EAP exchange...
[+] Pixie-Dust: PIN found: 12345670                          <-- WPS PIN recovered (WIFI-005)
[+] WPS PIN 12345670 -> PSK recovery...
[+] PSK: SummerBreeze2025                                    <-- PSK obtained without dictionary
[+] results saved in cracked.txt
```

The critical aspect: the PSK `SummerBreeze2025` is not present in rockyou.txt and would resist a dictionary attack. But WPS Pixie-Dust bypasses it completely, first recovering the WPS PIN (an implementation weakness) and then deriving the PSK from the PIN.

### Remediation

- **Immediate action:** disable WPS on all access points (`WPS: Disabled` in the administration panel). WPS is the vulnerability: its disabling neutralizes both Pixie-Dust and PIN bruteforce, without impact on connectivity (users use the PSK)
- **Structural action:** on managed AP fleets, apply via controller a global policy that forces WPS disabled; verify during procurement that the APs allow complete disabling (some firmware keep WPS active internally even if the interface shows it disabled); migrate to WPA3, which does not provide WPS
- **Verification:** re-run Wifite2 after the change to confirm that the WPS column shows `no` on all APs

---

## Airgeddon - Multi-Attack Framework

### Operational Context

Where Wifite2 excels in command-line automation, Airgeddon offers a complete interactive menu that also covers the Evil Twin attacks (see `../rogue-ap/`), the legacy WEP attacks and integrated interface management. It is useful as a wireless "swiss army knife" in a single guided tool.

```Bash
sudo airgeddon
# Main menu: interface management -> DoS -> Handshake tools ->
#            Offline WPA/WPA2 decrypt -> Evil Twin -> WPS attacks
```

---

## Lab Experience

Automation immediately showed its value: in a single session Wifite2 audited three networks, capturing a handshake on `LAB-CORP` and recovering the PSK of `LAB-WPS-AP` via WPS in less than a minute. The contrast with the manual flow (section `cracking`) is stark: what manually requires the coordination of three terminals (airodump, aireplay, aircrack) here is a single target choice.

The most instructive result was the WPS Pixie-Dust on `LAB-WPS-AP`. The PSK was robust and would have been immune to a dictionary attack, but the enabled WPS made the password irrelevant. This reversed my audit priority: first look for active WPS (quick and certain win), then attempt handshake/PMKID (dependent on the wordlist). Automation not only speeds up, but teaches the correct priority order of the attacks.

A practical limit observed: the orchestrators hide the details, and when an attack fails it is harder to diagnose why compared to manual execution. Wifite2 is ideal for broad coverage, but understanding the underlying tools remains indispensable for troubleshooting and for non-standard scenarios.

---

## Theoretical Analysis: The WPS Pixie-Dust Weakness

WPS (Wi-Fi Protected Setup) was born to simplify the connection via an 8-digit PIN. Its first weakness (2011, Viehbock) is structural: the PIN is validated in two separate halves (first 4 digits + last 3 + 1 checksum), reducing the search space from 10^8 to about 11,000 combinations - bruteforce feasible in hours (reaver/bully attack).

Pixie-Dust (2014, Bongard) is more devastating: it exploits the weak generation of random numbers (the nonces E-S1 and E-S2) in many chipsets (Ralink, Broadcom, Realtek). If these nonces are predictable or null, the PIN can be derived offline from the values exchanged in the first EAP message, without any online bruteforce: from hours to seconds.

The theoretical consequence is important: WPS introduces a parallel authentication channel weaker than the PSK. Even a perfect WPA2 passphrase is useless if WPS is enabled with a vulnerable chipset, because the attacker does not attack the PSK but the PIN, from which the AP itself derives and delivers the PSK. It is the textbook example of how a convenience function (simplified setup) can nullify a robust defense: the security of a system is that of its weakest link, not of its strongest component.

---

## Reference Tools

| Tool | Type | Technique/Access | Main use case |
| :--- | :--- | :--- | :--- |
| `Wifite2` | Attack automator | CLI | Automated audit: handshake, PMKID, WPS on multiple targets |
| `Airgeddon` | Multi-attack framework | CLI - Menu | Wireless swiss army knife: DoS, handshake, Evil Twin, WPS |
| `reaver` | WPS PIN attack | CLI | Online bruteforce of the WPS PIN (8 digits, reduced space) |
| `bully` | WPS PIN attack | CLI | Alternative to reaver, more robust on some chipsets |
| `hcxdumptool` | Clientless capture | CLI | PMKID capture integrated in the automated flows |

> **Recommended modern tool:** `Wifite2` remains the standard for automation in 2024-2026 thanks to the integration of hcxdumptool for the PMKID and the support of the hashcat 22000 format. For enterprise audits on 802.1X, pair it with `eaphammer` (see `../rogue-ap/`).

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Credential Access | Brute Force | `T1110` | WPS PIN bruteforce (reaver/bully) and Pixie-Dust to recover the PIN and derive the PSK (WIFI-005) |
| Credential Access | Network Sniffing | `T1040` | Automated capture of handshakes and PMKIDs on multiple targets |
| Collection | Adversary-in-the-Middle | `T1557` | Automated deauthentication to force the handshake capture |
| Initial Access | Valid Accounts | `T1078` | Use of the recovered PSKs to access the target networks |

---

> **Note:** All documented activities were conducted on lab WiFi networks owned by the author. The automated attacks (deauth, WPS, handshake capture) were performed exclusively against test APs in an isolated radio environment. The use of these tools against third-party networks without authorization is a crime. Techniques are documented for educational and authorized security assessment purposes.
