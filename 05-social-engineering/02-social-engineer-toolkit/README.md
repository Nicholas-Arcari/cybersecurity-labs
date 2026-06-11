> [English](README.en.md) | **Italiano**

# 02 - Social-Engineer Toolkit (SET)

> - **Fase:** Social Engineering - Multi-Vector Attack Framework
> - **Visibilita:** Variabile - da Media (website cloning genera traffico HTTP anomalo) ad Alta (email con payload triggera email gateway, PowerShell execution triggera EDR)
> - **Prerequisiti:** SET installato su Kali Linux (`sudo apt install set`); per spear-phishing: SMTP relay configurato; per website attacks: porta 80/443 disponibile sul listener; payload generati con msfvenom se necessario
> - **Output:** Finding SE-003..006; credenziali raccolte via website clone; payload consegnati via email e media rimovibili; reverse shell ottenute via PowerShell encoded

---

## Introduzione

Il Social-Engineer Toolkit (SET), creato da David Kennedy (TrustedSec), e il framework offensivo piu completo per attacchi di social engineering. SET integra in un'unica interfaccia menu-driven i principali vettori di attacco che un penetration tester utilizza per compromettere il fattore umano. A differenza di GoPhish - focalizzato su campagne email con metriche - SET e orientato all'exploitation attiva: clonazione di siti per credential harvesting, generazione e delivery di payload malevoli, attacchi via media rimovibili.

Il laboratorio documenta quattro dei sei vettori principali di SET, selezionati per la loro rilevanza operativa in un engagement moderno:

1. **Website Attack Vectors (SE-003):** clonazione in tempo reale di una pagina di login e credential harvesting. Il vettore piu utilizzato: l'utente inserisce le credenziali in una replica perfetta del portale aziendale.

2. **Spear-Phishing Attack Vectors (SE-004):** generazione di email con payload allegato (.hta mascherato). SET gestisce la creazione del payload, la composizione dell'email e l'invio tramite SMTP.

3. **Infectious Media Generator (SE-005):** creazione di payload autorun per supporti rimovibili (USB). Tecnica classica ma ancora efficace in ambienti con autorun abilitato o dipendenti non formati.

4. **PowerShell Attack Vectors (SE-006):** generazione di one-liner PowerShell encoded Base64 per reverse shell. Bypassa le execution policy restrittive e opera interamente in memoria.

Nella kill chain, SET copre simultaneamente le fasi di Weaponization, Delivery e Exploitation: prepara il payload, lo consegna al target, e raccoglie il risultato (credenziali o shell).

---

## Struttura della cartella

```
02-social-engineer-toolkit/
+-- website-attack-vectors/       # Credential harvester via site clone - SE-003
+-- spear-phishing-vectors/       # Email con payload .hta - SE-004
+-- infectious-media-generator/   # Autorun USB payload - SE-005
+-- powershell-attack-vectors/    # PS-encoded reverse shell - SE-006
```

---

## `website-attack-vectors/` - Credential Harvester via Site Clone

**ID Finding:** `SE-003` | **Severity:** `Alto` (credenziali catturate in chiaro tramite pagina login clonata)

### Contesto operativo

SET clona in tempo reale la pagina di login di un servizio target e la serve su un web server locale. Quando la vittima inserisce le credenziali nella pagina clonata, SET le cattura e le visualizza nella console dell'attaccante, poi redirige la vittima al sito reale per non destare sospetti. Rispetto a GoPhish, questa tecnica e piu rapida da configurare ma non offre metriche di campagna.

### Comandi principali

```Bash
sudo setoolkit
# 1) Social-Engineering Attacks
# 2) Website Attack Vectors
# 3) Credential Harvester Attack Method
# 2) Site Cloner
# IP: 192.168.0.110
# URL to clone: https://portal.company-lab.local/login
```

---

## `spear-phishing-vectors/` - Email con Payload Allegato

**ID Finding:** `SE-004` | **Severity:** `Alto` (payload .hta eseguito tramite email spear-phishing)

### Contesto operativo

SET genera un'email personalizzata con payload allegato e la invia tramite SMTP relay. Il laboratorio ha utilizzato un file .hta (HTML Application) come vettore: quando la vittima apre l'allegato, Windows esegue il codice HTA che lancia uno stager PowerShell per la reverse shell. Il formato .hta e stato scelto perche bypassava i filtri tradizionali (non e un .exe) ed e eseguibile nativamente su Windows.

### Comandi principali

```Bash
sudo setoolkit
# 1) Social-Engineering Attacks
# 1) Spear-Phishing Attack Vectors
# 1) Perform a Mass Email Attack
# -> Selezionare payload (es. Windows Reverse Shell)
# -> Configurare LHOST, LPORT
# -> Comporre email con allegato
# -> Inviare via SMTP
```

---

## `infectious-media-generator/` - Autorun USB Payload

**ID Finding:** `SE-005` | **Severity:** `Medio` (payload eseguito via autorun su supporto rimovibile)

### Contesto operativo

SET genera un payload con file autorun.inf configurato per l'esecuzione automatica al mount del supporto USB. Sebbene l'autorun sia disabilitato di default su Windows 10+, la tecnica resta rilevante in ambienti legacy (Windows 7, sistemi industriali) e puo essere combinata con ingegneria sociale (etichetta USB "Salary_Report_2026.pdf" lasciata in area comune).

### Comandi principali

```Bash
sudo setoolkit
# 1) Social-Engineering Attacks
# 3) Infectious Media Generator
# -> Selezionare payload
# -> Configurare LHOST, LPORT
# -> Output: file per USB (autorun.inf + payload)
```

---

## `powershell-attack-vectors/` - Reverse Shell Encoded

**ID Finding:** `SE-006` | **Severity:** `Alto` (reverse shell PowerShell encoded bypassa execution policy)

### Contesto operativo

SET genera un one-liner PowerShell encoded in Base64 che, quando eseguito sul target Windows, stabilisce una reverse shell verso l'attaccante. La codifica Base64 bypassa le execution policy restrittive (`-ExecutionPolicy Bypass`) e l'esecuzione avviene interamente in memoria senza scrivere file su disco, riducendo la superficie di detection per gli AV basati su firma statica.

### Comandi principali

```Bash
sudo setoolkit
# 1) Social-Engineering Attacks
# 4) PowerShell Attack Vectors
# 1) PowerShell Alphanumeric Shellcode Injector
# -> LHOST: 192.168.0.110
# -> LPORT: 4444
# Output: one-liner PowerShell encoded da consegnare alla vittima
```

---

## Flusso operativo consigliato

```
[1] Ricognizione target
     +-- Qual e il servizio di login? -> URL per website clone
     +-- Email valide disponibili? -> spear-phishing possibile
     +-- Accesso fisico? -> infectious media
              |
              v
[2] Scelta vettore SET
     +-- Solo credenziali ----------> Website Attack Vectors (SE-003)
     +-- Code execution via email --> Spear-Phishing Vectors (SE-004)
     +-- Code execution fisico ----> Infectious Media (SE-005)
     +-- Shell rapida Windows -----> PowerShell Attack (SE-006)
              |
              v
[3] Setup listener (se code execution)
     +-- Metasploit: use exploit/multi/handler
     +-- SET: listener integrato
              |
              v
[4] Delivery & Collection
     +-- Credenziali -> console SET in real-time
     +-- Shell -> Meterpreter / reverse_tcp callback
```

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `SET (setoolkit)` | SE framework | CLI - Menu interattivo | Framework multi-vettore: clone, spear-phishing, media, PowerShell |
| `msfvenom` | Payload generator | CLI | Generazione payload custom per allegati SET |
| `Metasploit` | Exploitation framework | CLI | Handler per reverse shell generate da SET |
| `BeEF` | Browser exploitation | Web UI | Alternativa per attacchi client-side via hook JavaScript |
| `HiddenEye` | Phishing tool | CLI - Python | Alternativa moderna a SET per website cloning |

> **Tool moderno consigliato:** SET resta rilevante per la sua integrazione multi-vettore, ma per il solo credential harvesting `GoPhish` offre metriche superiori. Per payload delivery moderni, considerare le tecniche in `03-payload-delivery/` (HTML Smuggling, ISO+LNK) che bypassano i filtri attuali.

---

## Registro Finding

| ID | Descrizione | Severity | CVSS | Sottocartella |
| :--- | :--- | :---: | :---: | :--- |
| `SE-003` | SET Website Attack: credential harvester via pagina login clonata, credenziali catturate in chiaro | `Alto` | 7.5 | `website-attack-vectors/` |
| `SE-004` | SET Spear-Phishing: email con allegato .hta, stager PowerShell eseguito sulla vittima | `Alto` | 8.1 | `spear-phishing-vectors/` |
| `SE-005` | SET Infectious Media: payload autorun.inf su USB, esecuzione al mount (ambienti legacy) | `Medio` | 5.3 | `infectious-media-generator/` |
| `SE-006` | SET PowerShell Attack: reverse shell encoded Base64, bypass execution policy, esecuzione in-memory | `Alto` | 8.1 | `powershell-attack-vectors/` |

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Finding Correlato |
| :--- | :--- | :--- | :--- |
| Resource Development | Obtain Capabilities: Tool | `T1588.002` | SE-003, SE-004, SE-005, SE-006 |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | SE-003 |
| Initial Access | Phishing: Spearphishing Attachment | `T1566.001` | SE-004 |
| Initial Access | Replication Through Removable Media | `T1091` | SE-005 |
| Execution | User Execution: Malicious Link | `T1204.001` | SE-003 |
| Execution | User Execution: Malicious File | `T1204.002` | SE-004, SE-005 |
| Execution | Command and Scripting Interpreter: PowerShell | `T1059.001` | SE-006 |
| Defense Evasion | Obfuscated Files or Information | `T1027` | SE-006 |
| Credential Access | Input Capture: Web Portal Capture | `T1056.003` | SE-003 |

---

> **Nota:** Tutte le attivita documentate sono state condotte in un ambiente di laboratorio virtualizzato (VirtualBox, rete NAT/Bridge isolata). I payload sono stati eseguiti esclusivamente su macchine virtuali di proprieta dell'autore. Nessun payload e stato inviato a sistemi o persone reali.
