> **English** | [Italiano](README.md)

# Proxy Tools: SSL/TLS Certificates & HTTPS Interception

> - **Phase:** Web Attack - HTTPS Interception Setup
> - **Visibility:** Local - configuration is performed exclusively on the local browser, no additional traffic towards the target
> - **Prerequisites:** Burp Suite started with listener on `127.0.0.1:8080`, browser configured to use the proxy
> - **Output:** Transparent HTTPS traffic interception, fake SSL certificates signed by Burp CA accepted by the browser without errors

---

Objective: Configure the "Chain of Trust" between the browser and Burp Suite to enable interception and decryption of HTTPS (SSL/TLS) traffic.

Target: Local Configuration (Browser + Burp CA)

Tools: `Burp Suite`, `Firefox Certificate Manager`

---

## 1 Theoretical Introduction: Breaking Encryption

The HTTPS protocol protects data confidentiality by encrypting them between client and server. A "Man-in-the-Middle" Proxy (like Burp) breaks this connection.

To be able to read encrypted data, the Proxy must:

1.  Present itself to the browser as if it were the target site (e.g., `google.com`).

2.  Generate a fake SSL certificate "on the fly" for that domain.

For the browser to accept this fake certificate without displaying security errors (`SEC_ERROR_UNKNOWN_ISSUER`), it is necessary to install the Burp Certificate Authority (CA) in the browser's trusted certificates store (Trusted Root Store).

---

## 2 Technical Procedure: CA Installation

The PortSwigger root certificate installation was performed to enable Deep Packet Inspection.

Steps performed:

1.  Download of the `cacert.der` certificate from `http://burp`.

2.  Import into Firefox's Trust Store (`Authorities` tab).

3.  Enabling the flag: "Trust this CA to identify websites".

HTTPS Interception Verification:

After configuration, a protected site (`google.com`) was visited. The browser showed no warnings.

Inspecting the site's certificate, the issuer is PortSwigger CA, confirming that traffic is being decrypted and re-encrypted by Burp.

---

## 3 Advanced Scenarios: SSL Pinning

While this technique works on desktop browsers, modern mobile applications (Android/iOS) implement SSL Pinning.

The app does not blindly trust the device's Trust Store, but only accepts a specific certificate hardcoded by the developers. In a Mobile Pentesting scenario, frameworks like Frida or Objection would be needed to inject code at runtime and disable this control.

---

## 4 Conclusions

Proper certificate management is the prerequisite for analyzing modern traffic. Without this configuration, Red Teaming activity would be limited to HTTP-only (plaintext) traffic, making it impossible to test login forms, banking transactions or protected APIs.

---

## MITRE ATT&CK Mapping

| Tactic | Technique | MITRE ID | Action Description |
| :--- | :--- | :--- | :--- |
| Defense Evasion | Subvert Trust Controls: Install Root Certificate | `T1553.004` | Installation of the PortSwigger (Burp Suite) CA certificate in Firefox's trust store to enable HTTPS interception without certificate errors |
| Collection | Man-in-the-Middle: AiTM HTTPS Interception | `T1557.002` | Generation of fake SSL certificates for each visited domain (e.g., `google.com`), with issuer `PortSwigger CA`, allowing decryption of TLS traffic in transit |

---

> **Note:** The CA certificate installation procedure documented here is valid exclusively for lab environments and dedicated test machines. Installing third-party CA certificates on corporate or production machines without authorization is a violation of corporate security policies and, in some contexts, a criminal offense. The Burp CA should be removed at the end of the engagement.
