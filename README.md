# Cybersecurity Labs

Raccolta strutturata di laboratori, esercitazioni, PoC e simulazioni didattiche utilizzate per lo studio e la pratica in ambito Cybersecurity Offensive & Defensive, secondo metodologie ispirate al Certified Ethical Hacker (CEH)

---

## Tutto il materiale è finalizzato esclusivamente alla formazione
Nessun codice deve essere utilizzato al di fuori di ambienti autorizzati, controllati o di proprietà dell’utente

---

## Obiettivo della repository

Questa repo raccoglie tecniche, procedure e PoC utili per:

- Comprendere il ciclo completo di un penetration test
- Sperimentare in laboratorio attacchi e difese reali
- Costruire competenze per certificazioni professionali (CEH, eJPT, OSCP, ecc.)
- Migliorare la comprensione dei rischi, delle vulnerabilità e delle contromisure

---

## Struttura della repository

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
└── README.md
```

---

## 01 - Reconnaissance

Tecniche di raccolta informazioni (active & passive recon), tra cui:

- scansioni Nmap
- analisi DNS
- OSINT
- fingerprinting servizi

Obiettivo: identificare superficie d’attacco e tecnologie utilizzate dal target

---

## 02 - Vulnerability Assessment

Analisi delle vulnerabilità con strumenti automatici e manuali:

- Scanner come OpenVAS/Nessus
- NSE scripts
- Validazione CVE e CVSS

Obiettivo: individuare debolezze prima dello sfruttamento

---

## 03 - Web Attacks

Riproduzione di vulnerabilità OWASP Top 10:

- SQL Injection
- XSS
- CSRF
- File Upload Abuse

Obiettivo: comprendere cause, exploit e mitigazioni applicative

---

## 04 - System Exploitation

Tecniche di sfruttamento per sistemi operativi e servizi:

- RCE
- Privilege Escalation
- Exploit pubblici (Searchsploit)

Obiettivo: ottenere accesso controllato a un sistema vulnerabile

---

## 05 - Social Engineering

Sezione dedicata all’ingegneria sociale:

- overview dei vettori SE
- demo mock di pagine fake
- analisi di payload e IOC

Obiettivo: comprendere debolezze umane e come prevenire attacchi sociali

---

## 06 - Wireless Security

Laboratori su:

- cattura handshake
- audit sicurezza WPA2/WPA3
- access point rogue educativi

Obiettivo: analizzare la sicurezza di reti wireless controllate

---

## 07 - Post Exploitation

Tecniche controllate post-accesso:

- persistence
- enumeration avanzata
- movimento laterale (mock)

Obiettivo: comprendere cosa accade dopo una compromissione e come difendersi

---

## 08 - Defense & Hardenings

Misure difensive:

- firewalling
- intrusion detection
- honeypots

Obiettivo: rafforzare sistemi e rilevare attività sospette

---

## Note Etiche e Legali

Questo repository è destinato solo ed esclusivamente all’apprendimento.

Ogni tecnica deve essere utilizzata soltanto su:

- sistemi propri
- ambienti di laboratorio
- contesti per cui si possiede esplicita autorizzazione scritta

Qualsiasi uso improprio può costituire reato