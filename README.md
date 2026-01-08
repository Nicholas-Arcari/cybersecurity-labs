# Cybersecurity Labs

![Security Status](https://img.shields.io/badge/Security-Red%20%26%26%20Blue-blueviolet?style=for-the-badge&logo=kali-linux)
![Maintenance](https://img.shields.io/badge/Maintained-Yes-green?style=for-the-badge)
![Focus](https://img.shields.io/badge/Focus-Full%20Stack%20Sec-orange?style=for-the-badge)

---

Benvenuto nella repository centrale per le operazioni di sicurezza offensiva (Red Team), difensiva (Blue Team) e cloud.

Questa struttura è organizzata seguendo il flusso logico di un **Penetration Test** reale e le fasi della **Cyber Kill Chain**, con l'aggiunta di moduli specifici per la difesa e le infrastrutture moderne.

---

## Architettura della Repository

```bash
cybersecurity-labs/
│
├── 01-recon/
├── 02-vulnerability-assessment/
├── 03-web-attacks/
├── 04-system-exploitation/
├── 05-social-engineering/
├── 06-wireless-security/
├── 07-post-exploitation/
├── 08-defense-hardenings/
├── 09-digital-forensics/
├── 10-cloud-security/
└── README.md
```

---

## Legal Disclaimer

> **ATTENZIONE:** Tutto il materiale, gli script e le metodologie contenute in questa repository sono a scopo puramente **educativo** e di **ricerca**. L'autore non si assume alcuna responsabilità per l'uso improprio di queste informazioni.
>
> *Non testare mai sistemi senza un'autorizzazione scritta esplicita.*

---

## Mappa di Navigazione

| Fase / Dominio | Cartella | Scopo Principale |
| :--- | :--- | :--- |
| **I. Intelligence** | [01-recon](#-01-recon-red-team-basic) | Mappatura infrastruttura, OSINT, Port Scanning |
| **II. Assessment** | [02-vuln-assessment](#-02-vulnerability-assessment) | Scansione vulnerabilità (CVE), Analisi rischi |
| **III. Web Ops** | [03-web-attacks](#-03-web-attacks-red-team--secure-coding) | SQLi, XSS, OWASP, Secure Coding |
| **IV. System Ops** | [04-system-exploitation](#-04-system-exploitation) | Shell, PrivEsc, Buffer Overflow |
| **V. Human Ops** | [05-social-engineering](#-05-social-engineering-toolingpython) | Phishing, Payload Delivery, Cloning |
| **VI. Wireless** | [06-wireless-security](#-06-wireless-security) | WiFi, Bluetooth, SDR, RFID |
| **VII. Post-Exploit** | [07-post-exploitation](#-07-post-exploitation) | Persistence, Pivoting, Looting, Exfiltration |
| **VIII. Defense** | [08-defense-hardenings](#-08-defense-hardenings-blue-team-prevention) | **Wazuh**, Hardening, Honeypots |
| **IX. Analysis** | [09-digital-forensics](#-09-digital-forensics-blue-team-analysis) | **Wireshark**, Malware Analysis, Disk Forensics |
| **X. Modern Infra** | [10-cloud-security](#-10-cloud-security-cloudmodern) | AWS/Azure/GCP, Docker, Kubernetes |

---

## Struttura della Repository


### 01-recon (Red Team Basic)

**Obiettivo:** Allargare la superficie d'attacco

Qui trovi tutto ciò che serve per scoprire "cosa esiste"

- **Contenuto:** Script per OSINT (TheHarvester), scansione attiva (Nmap), enumerazione DNS e Subdomain discovery

- **Nota:** Diviso in *Passivo* (invisibile) e *Attivo* (rumoroso)


### 02-vulnerability-assessment

**Obiettivo:** Identificare i difetti

Analisi automatizzata e manuale per trovare CVE e misconfigurazioni

- **Contenuto:** Report di Nessus/OpenVAS, script Nmap NSE specifici per vulnerabilità, audit di protocolli (SMB, SSL)


### 03-web-attacks (Red Team + Secure Coding)

**Obiettivo:** Compromettere applicazioni Web e API

Il focus è sulle vulnerabilità OWASP Top 10. Include anche una sezione di difesa (Secure Coding)

- **Contenuto:** Burp Suite projects, SQLMap, Fuzzing (Gobuster), e snippet di codice *Vulnerabile vs Fixato*


### 04-system-exploitation

**Obiettivo:** Ottenere una Shell (RCE) e diventare Root/Admin

Dedicato all'attacco infrastrutturale puro: exploit del kernel, servizi e binari

- **Contenuto:** Metasploit resources, Exploit-DB mirror locale, script per Privilege Escalation (LinPEAS/WinPEAS)


### 05-social-engineering (Tooling&Python)

**Obiettivo:** Hacking del fattore umano

Strumenti per simulazioni di phishing e creazione di payload ingannevoli

- **Contenuto:** GoPhish templates, script Python personalizzati (PyPhisher), generatori di payload Office/HTA


### 06-wireless-security

**Obiettivo:** Intercettazione e attacco su frequenze radio

Tutto ciò che viaggia "nell'aria"

- **Contenuto:** WiFi (Aircrack-ng), Bluetooth/BLE (Bettercap), SDR (Radiofrequenza) e RFID/NFC


### 07-post-exploitation

**Obiettivo:** Mantenere l'accesso e muoversi nella rete

Cosa fare *dopo* aver ottenuto la shell

- **Contenuto:** Credential Dumping (Mimikatz), Persistence (Backdoors), Pivoting (Tunneling/Chisel) ed Esfiltrazione dati


### 08-defense-hardenings (Blue Team Prevention)

**Obiettivo:** Proteggere e Monitorare

Strumenti di difesa attiva e configurazione sicura

- **Tool Chiave:** **Wazuh** (SIEM/XDR) si trova qui

- **Contenuto:** Honeypots, script di Hardening (CIS Benchmarks), configurazioni Firewall


### 09-digital-forensics (Blue Team Analysis)

**Obiettivo:** Indagare sull'incidente

Strumenti per capire "cosa è successo" analizzando le tracce digitali

- **Tool Chiave:** **Wireshark** (Analisi di rete) si trova qui

- **Contenuto:** Network Forensics (PCAP analysis), Disk Forensics (Autopsy), Memory Forensics (Volatility)


### 10-cloud-security (Cloud&Modern)

**Obiettivo:** Sicurezza per infrastrutture moderne

Container, Orchestratori e Cloud Provider Pubblici

- **Contenuto:**
    - **Cloud:** AWS/Azure/GCP (Enumeration & Exploitation)
    - **Containers:** Docker Security (Trivy, Image scanning)
    - **Orchestration:** Kubernetes (Audit & Attacks)
    - **IaC:** Terraform security scanning

---

## Prerequisiti & Setup

Per utilizzare al meglio gli script contenuti in questa repo, si consiglia un ambiente basato su:

- **OS:** Kali Linux / Parrot OS (o una VM dedicata)
- **Python:** 3.x (con `requirements.txt` installati nelle singole cartelle)
- **Docker:** Necessario per avviare rapidamente container vulnerabili (o tool nella cartella `10`)

---

> *Repository manutenuta da Nicholas Arcari*