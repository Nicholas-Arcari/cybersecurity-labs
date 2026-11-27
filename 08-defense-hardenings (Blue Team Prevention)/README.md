> [English](README.en.md) | **Italiano**

# 08 - Defense & hardening (blue team prevention)

> - **Fase:** Difesa - Prevention, Detection & Response (Blue Team)
> - **Categoria:** Il ribaltamento di prospettiva: dall'attacco alla difesa
> - **Prerequisiti:** Comprensione delle tecniche offensive dei moduli 01-07 (si difende cio che si sa attaccare); host per SIEM/XDR con risorse adeguate; ambiente di test
> - **Output:** Finding DEF-001..008; architettura difensiva a piu strati; detection, deception e hardening validati contro gli attacchi dei moduli precedenti

---

## Introduzione

Il modulo `08-defense-hardenings` e il ribaltamento di prospettiva del percorso: dopo sette moduli dedicati all'attacco (Red Team), qui si passa alla difesa (Blue Team). E il modulo in cui ogni tecnica offensiva studiata trova la sua contromisura, e in cui il principio guida diventa esplicito: si difende bene solo cio che si sa attaccare. La conoscenza offensiva dei moduli precedenti non e un fine ma lo strumento per costruire difese che reggono contro avversari reali.

La filosofia difensiva del modulo e la **difesa in profondita**: nessun singolo controllo e sufficiente, ma la loro stratificazione rende l'attacco progressivamente piu costoso, rumoroso e improbabile. Il modulo e organizzato secondo una metafora anatomica che ne chiarisce i ruoli complementari:

1. **Il Cervello - SIEM & Log Analysis (`01-siem-log-analysis/`, DEF-001..002):** il centro nervoso che vede tutto e correla. ELK Stack e Splunk aggregano i log dell'ambiente e trasformano eventi isolati in detection. Senza visibilita non c'e difesa.

2. **I Muscoli - Endpoint Security & XDR (`02-endpoint-security-xdr/`, DEF-003..004):** i sensori che agiscono sull'endpoint. Wazuh non solo rileva (File Integrity Monitoring) ma reagisce (active response), contenendo l'attaccante in secondi.

3. **Le Trappole - Deception (`03-deception/`, DEF-005..006):** le esche ad alta confidenza. Canary token e honeypot avvisano quando l'attaccante e gia dentro e ne studiano le tecniche, con falsi positivi strutturalmente nulli.

4. **Lo Scudo - Hardening Scripts (`04-hardening-scripts/`, DEF-007..008):** la prevenzione alla radice. L'hardening di Linux e Windows riduce la superficie d'attacco, chiudendo intere classi di privilege escalation e lateral movement prima che l'attaccante le provi.

Questi quattro strati coprono il ciclo difensivo completo: **prevenire** (hardening), **rilevare** (SIEM + XDR + deception), **rispondere** (active response). Un attacco che supera la prevenzione viene rilevato; uno che elude un sensore ne incontra un altro; uno che tocca un'esca si tradisce. La forza non e nel singolo strato ma nella loro somma.

### Nota sul framing dei finding difensivi

In un modulo difensivo, il **Finding** (`DEF-NNN`) non rappresenta una vulnerabilita dell'ambiente ma un **controllo di detection/prevention/deception validato**. La **Severity** indica la criticita della minaccia che il controllo indirizza (un controllo `Alto` contrasta tecniche d'attacco ad alto impatto). Le tabelle **MITRE ATT&CK** mappano le tecniche che ogni controllo rileva, previene o osserva; dove utile, si affianca il framework **MITRE D3FEND** (contromisure difensive). Questo mantiene la struttura uniforme al resto della repository, invertendone la prospettiva.

---

## Struttura della cartella

```
08-defense-hardenings (Blue Team Prevention)/
+-- README.md                              <- questo file: registro DEF-001..008 + MITRE aggregata
|
+-- 01-siem-log-analysis (Il Cervello)/
|   +-- README.md                          <- registro DEF-001..002, concetto di SIEM
|   +-- elk-stack/                         <- DEF-001 (ELK: centralizzazione + detection)
|   +-- splunk/                            <- DEF-002 (Splunk: correlazione SPL)
|
+-- 02-endpoint-security-xdr (I Muscoli)/
|   +-- README.md                          <- registro DEF-003..004, concetto di EDR/XDR
|   +-- wazuh/                             <- piattaforma XDR open source
|       +-- installing&configuring/        <- deployment Manager + agenti (setup)
|       +-- suricata-integration/          <- Wazuh + Suricata = SIEM + IDS (setup)
|       +-- threat-detection&active-response/  <- DEF-003 (FIM), DEF-004 (active response)
|
+-- 03-deception (Le Trappole)/
|   +-- README.md                          <- registro DEF-005..006, filosofia deception
|   +-- honeypots/
|       +-- canary-tokens/                 <- DEF-005 (tripwire digitali)
|       +-- t-pot/                         <- DEF-006 (honeypot + threat intel)
|
+-- 04-hardening-scripts (Lo Scudo)/
    +-- README.md                          <- registro DEF-007..008, filosofia hardening
    +-- linux-hardening/                   <- DEF-007 (Lynis + CIS)
    +-- windows-hardening/                 <- DEF-008 (GPO, Credential Guard, LAPS)
```

---

## Flusso operativo consigliato

```
[INPUT] Ambiente da difendere + conoscenza offensiva (moduli 01-07)
         |
         v
[1] Prevenire - Lo Scudo (04-hardening)
     +-- riduci la superficie: hardening Linux/Windows (DEF-007..008)
              |
              v
[2] Vedere - Il Cervello (01-siem)
     +-- centralizza i log, correla: ELK/Splunk (DEF-001..002)
              |
              v
[3] Rilevare e Reagire - I Muscoli (02-xdr)
     +-- sensori endpoint + active response: Wazuh (DEF-003..004)
              |
              v
[4] Ingannare - Le Trappole (03-deception)
     +-- esche ad alta confidenza: canary token, honeypot (DEF-005..006)
              |
              v
[CICLO] Gli alert (02, 03) confluiscono nel SIEM (01) per la correlazione;
        l'hardening (04) riduce cio che deve essere rilevato
              |
              v
[OUTPUT] Difesa in profondita: attacco prevenuto, o rilevato, o tradito da un'esca
```

---

## Tool di riferimento

| tool | strato | ruolo | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `ELK Stack` / `Splunk` | il cervello | siem | centralizzazione, correlazione, detection |
| `Wazuh` | i muscoli | xdr | detection endpoint, fim, active response |
| `Suricata` | i muscoli | ids | detection di rete integrata in wazuh |
| `Canarytokens` / `T-Pot` | le trappole | deception | early warning e threat intelligence |
| `Lynis` / `CIS-CAT` | lo scudo | auditor | misura e applicazione dell'hardening |
| `Credential Guard` / `LAPS` | lo scudo | contromisura | protezione credenziali windows |

> **Tool moderno consigliato:** un'architettura difensiva open source completa si costruisce con `Wazuh` (XDR + SIEM leggero) o `ELK/Elastic Security` come cervello, `Suricata` per la rete, `canarytokens`/`OpenCanary` per la deception, e `Lynis`/`CIS Benchmarks` con `Ansible` per l'hardening idempotente. Questo stack copre l'intero ciclo prevenire-rilevare-rispondere senza costi di licenza.

---

## Registro finding - modulo 08

| id | descrizione | severity | sottocartella |
| :--- | :--- | :---: | :--- |
| `DEF-001` | elk stack: centralizzazione dei log e detection (brute force ssh) | `Alto` | `01-siem/elk-stack/` |
| `DEF-002` | splunk: correlazione multi-sorgente via spl (kill chain scan - accesso) | `Alto` | `01-siem/splunk/` |
| `DEF-003` | wazuh fim: rilevamento di persistenza, tampering e rootkit | `Alto` | `02-xdr/wazuh/threat-detection.../` |
| `DEF-004` | wazuh active response: contenimento automatico (blocco ip) su alert | `Alto` | `02-xdr/wazuh/threat-detection.../` |
| `DEF-005` | canary tokens: tripwire digitali per early breach detection | `Medio` | `03-deception/honeypots/canary-tokens/` |
| `DEF-006` | t-pot: piattaforma honeypot multi-servizio, raccolta ttp/ioc | `Medio` | `03-deception/honeypots/t-pot/` |
| `DEF-007` | linux hardening: audit lynis + baseline cis (anti privilege escalation) | `Alto` | `04-hardening/linux-hardening/` |
| `DEF-008` | windows hardening: gpo, credential guard, laps (anti credential dumping / pth) | `Alto` | `04-hardening/windows-hardening/` |

---

## Mappatura MITRE ATT&CK - aggregata

> Il modulo difensivo mappa le tecniche d'attacco che i suoi controlli **rilevano, prevengono o osservano**. Framework complementare: MITRE D3FEND (contromisure difensive).

| tattica (contrastata) | tecnica | id mitre | finding correlato |
| :--- | :--- | :--- | :--- |
| credential access | brute force | `T1110` | DEF-001, DEF-002, DEF-004, DEF-006 |
| reconnaissance | active scanning | `T1595` | DEF-002 |
| initial access | valid accounts | `T1078` | DEF-001, DEF-002, DEF-006 |
| lateral movement | remote services | `T1021` | DEF-002 |
| lateral movement | use alternate authentication material: pass the hash | `T1550.002` | DEF-008 |
| persistence | account manipulation: ssh authorized keys | `T1098.004` | DEF-003, DEF-007 |
| persistence | boot or logon autostart: registry run keys | `T1547.001` | DEF-003, DEF-008 |
| credential access | os credential dumping: lsass memory | `T1003.001` | DEF-008 |
| privilege escalation | abuse elevation control: sudo | `T1548.003` | DEF-007 |
| privilege escalation | setuid and setgid | `T1548.001` | DEF-007 |
| defense evasion | rootkit | `T1014` | DEF-003 |
| defense evasion | indicator removal: clear logs | `T1070` | DEF-001 |
| collection | data from network shared drive | `T1039` | DEF-005 |
| credential access | unsecured credentials: credentials in files | `T1552.001` | DEF-005, DEF-007 |
| command and control | ingress tool transfer | `T1105` | DEF-006 |

| contromisura difensiva (d3fend) | id d3fend | strato |
| :--- | :--- | :--- |
| platform monitoring | `D3-PM` | il cervello (siem) |
| file integrity monitoring | `D3-FIM` | i muscoli (wazuh) |
| network traffic filtering | `D3-NTF` | i muscoli (active response) |
| decoy file / credential / environment | `D3-DF`/`D3-DUC`/`D3-DE` | le trappole (deception) |
| platform / credential hardening | `D3-PH`/`D3-CH` | lo scudo (hardening) |

---

> **Nota:** Tutte le attivita documentate in questo modulo sono state condotte su un ambiente di laboratorio di proprieta dell'autore, in contesto controllato. Gli strumenti difensivi (SIEM, XDR, honeypot, hardening) sono per natura legittimi; le uniche cautele riguardano l'isolamento degli honeypot (che catturano malware reale), la taratura dell'active response (per evitare auto-blocchi) e il test dell'hardening (per non interrompere servizi legittimi). Il monitoraggio dei log in contesti reali deve rispettare la normativa su privacy e trattamento dei dati. Le tecniche sono documentate a scopo educativo e di difesa in contesto autorizzato.
