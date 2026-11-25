> [English](README.en.md) | **Italiano**

# Windows Hardening - GPO, Credential Guard e Baseline CIS

> - **Fase:** Defense & Hardening - System Hardening (Prevention)
> - **Categoria:** Prevention - hardening di Windows e Active Directory
> - **Prerequisiti:** Privilegi di amministratore di dominio (per le GPO) o locale; Microsoft Security Compliance Toolkit / CIS-CAT per le baseline; ambiente di test prima della produzione
> - **Output:** Finding DEF-008; endpoint e dominio hardenizzati via GPO; contromisure a credential dumping e lateral movement; baseline CIS applicata

- **Ambiente Operativo:** Windows (workstation/server), Active Directory, Group Policy
- **Ruolo:** "Lo Scudo" - previene le tecniche offensive Windows a livello di policy
- **Tool principali:** Group Policy (GPO), Microsoft Security Baseline, LAPS, Credential Guard, CIS-CAT

---

## Executive Summary

L'hardening di Windows e la contromisura preventiva diretta alle tecniche offensive dei moduli 04 e 07: credential dumping (Mimikatz/LSASS), pass-the-hash, privilege escalation, persistenza. A differenza di Linux dove si agisce host per host, in un ambiente Windows la potenza dell'hardening sta nelle **Group Policy (GPO)**: una policy definita centralmente si applica a migliaia di endpoint contemporaneamente, rendendo l'hardening scalabile e coerente.

L'approccio e guidato dalle baseline: le **Microsoft Security Baseline** (nel Security Compliance Toolkit) e i **CIS Benchmarks** forniscono set di GPO pre-configurate e riconosciute, che chiudono i default insicuri di Windows. Il finding DEF-008 documenta l'applicazione di queste baseline e delle contromisure specifiche alle tecniche viste nel percorso offensivo.

Tre contromisure meritano risalto perche neutralizzano attacchi documentati in `07-post-exploitation`: **Credential Guard** isola LSASS in un ambiente virtualizzato, rendendo inefficace il dump delle credenziali con Mimikatz (POST-003); **LAPS** randomizza la password dell'amministratore locale per ogni macchina, spezzando il pass-the-hash laterale; la disabilitazione di **SMBv1** e dei protocolli legacy chiude vettori di lateral movement e i relay NTLM.

---

## Struttura della cartella

```
windows-hardening/
+-- README.md      # questo file: GPO, Credential Guard, LAPS, baseline CIS (DEF-008)
+-- GPO-templates/ # export delle GPO di hardening (backup/import)
+-- img/           # applicazione baseline e verifica
```

---

## Hardening di Windows via GPO e Baseline

**ID Finding:** `DEF-008` | **Severity:** `Alto` (contromisura preventiva a credential dumping, pass-the-hash e lateral movement in ambiente Windows/AD)

### Contesto operativo

La forza dell'hardening Windows e la centralizzazione via GPO: si definisce la policy una volta e Active Directory la propaga a tutti gli endpoint del dominio. Le Microsoft Security Baseline forniscono queste GPO gia configurate; il compito del difensore e importarle, adattarle al contesto e verificarne l'applicazione, non reinventarle.

### PoC - Fase 1: Import della Security Baseline

```PowerShell
# Microsoft Security Compliance Toolkit: import della baseline in GPO
# (le baseline sono set di GPO backup pronte all'import)
Import-GPO -BackupGpoName "MSFT Windows 11 - Computer" -TargetName "CIS-Baseline-Workstation" -Path C:\Baselines
```

### PoC - Fase 2: Credential Guard (contromisura a Mimikatz/LSASS - POST-003)

```PowerShell
# Abilitazione di Credential Guard via GPO / registro
# Isola LSASS in un container virtualizzato (VBS) -> Mimikatz non puo dumpare
reg add "HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard" /v EnableVirtualizationBasedSecurity /t REG_DWORD /d 1 /f
reg add "HKLM\SYSTEM\CurrentControlSet\Control\LSA" /v LsaCfgFlags /t REG_DWORD /d 1 /f
```

```PowerShell
# Verifica che Credential Guard sia attivo
(Get-CimInstance -ClassName Win32_DeviceGuard -Namespace root\Microsoft\Windows\DeviceGuard).SecurityServicesRunning
```

```
1                        <-- Credential Guard attivo: LSASS isolato (DEF-008)
                         # il dump con Mimikatz (POST-003) ora restituisce hash cifrati/inaccessibili
```

### PoC - Fase 3: Contromisure a lateral movement

```PowerShell
# Disabilita SMBv1 (vettore legacy, WannaCry/EternalBlue, relay)
Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart

# LAPS: password admin locale randomizzata e univoca per host (rompe il pass-the-hash laterale)
# (deployment via GPO + schema AD esteso)
Get-LapsADPassword -Identity "WIN-CLIENT-01"     # password unica e ruotata per host

# Blocca l'esecuzione da percorsi utente (contromisura a payload droppati)
# via AppLocker / WDAC policy
```

### Operativita Difensiva e Cautele

- **Testare prima della produzione:** una GPO mal applicata puo bloccare l'accesso a migliaia di macchine; testare in un OU pilota prima del rollout
- **Ordine di priorita:** iniziare dalle contromisure ad alto impatto (Credential Guard, LAPS, disabilitazione SMBv1, RDP NLA) prima delle regole di dettaglio
- **Compatibilita:** Credential Guard richiede hardware con virtualizzazione (VBS) e puo essere incompatibile con alcuni driver legacy; verificare prima
- **Hardening + detection:** abbinare l'hardening al monitoraggio (Wazuh/Sysmon) per rilevare i tentativi di aggirarlo o disabilitarlo

---

## Esperienza di Laboratorio

La dimostrazione piu potente e stata Credential Guard contro Mimikatz. Nel modulo 07 avevo usato Mimikatz per dumpare gli hash NTLM e i ticket Kerberos da LSASS (POST-003, finding Critico); qui, con Credential Guard abilitato, ho rieseguito lo stesso attacco e ho visto il dump restituire dati cifrati e inutilizzabili. La stessa tecnica che come attaccante mi aveva dato le chiavi del dominio, come difensore l'avevo neutralizzata con una singola policy. Vedere l'attacco fallire dove prima riusciva ha reso concreto il valore dell'hardening meglio di qualsiasi teoria.

La lezione sulla scalabilita e stata capire il potere delle GPO. Su Linux avevo hardenizzato host per host; su Windows, definire la policy una volta e vederla propagarsi a tutti gli endpoint del dominio di test ha mostrato perche l'hardening Active Directory sia strutturalmente diverso. La centralizzazione e insieme la forza (un cambiamento, migliaia di macchine) e il rischio (un errore, migliaia di macchine): la stessa GPO che protegge tutto puo rompere tutto se sbagliata.

La cautela appresa e stata sul rischio operativo delle policy aggressive. Un tentativo di applicare una baseline CIS completa senza testarla ha bloccato funzionalita legittime in una VM di test. La lezione ripete quella di Linux ma amplificata dalla scala: in AD, l'hardening non testato non danneggia un host ma potenzialmente l'intero dominio. Il rollout graduale via OU pilota non e burocrazia, e sopravvivenza operativa.

---

## Analisi Teorica: Hardening come Neutralizzazione delle Tecniche, non dei Singoli Attacchi

L'hardening Windows maturo non insegue i singoli exploit ma neutralizza le tecniche alla radice. Mimikatz e uno dei tanti tool che dumpano LSASS; inseguire il tool (bloccare Mimikatz.exe) e inutile, perche ne esistono decine di varianti e reimplementazioni (pypykatz, comsvcs.dll). Credential Guard invece neutralizza la tecnica: isola LSASS cosi che nessun tool, presente o futuro, possa leggerne la memoria. Difendere la tecnica invece del tool e il principio dell'hardening efficace.

Questo si lega al concetto di "raising the cost" - alzare il costo dell'attacco. LAPS non rende impossibile compromettere una macchina, ma spezza il pass-the-hash laterale: l'hash dell'admin locale di un host non funziona su nessun altro, perche ogni host ha una password unica. L'attaccante che compromette una macchina non ottiene piu le chiavi di tutte le altre; deve compromettere ciascuna singolarmente, moltiplicando il costo e le probabilita di essere rilevato. L'hardening non promette invulnerabilita, promette di rendere l'attacco cosi costoso da non valerne la pena.

Il fondamento e la difesa in profondita applicata all'identita. In Active Directory, l'identita e il vero perimetro: chi controlla le credenziali controlla il dominio. Le contromisure di hardening (Credential Guard sulle credenziali in memoria, LAPS sulle password locali, la baseline sui default insicuri) proteggono strati diversi della stessa risorsa critica - l'identita. Nessuna e sufficiente da sola, ma insieme trasformano un dominio da "compromissione di una macchina = compromissione del dominio" (il modello che l'offensiva sfrutta) a "ogni macchina e un ostacolo separato". E il ribaltamento dell'economia che rende difendibile un ambiente Windows.

---

## Scenario Reale: La Prevenzione in Azione

> Questa sezione descrive come questo controllo difensivo opererebbe in un incidente reale.

### Prospettiva Attaccante (cosa tenta)

L'attaccante compromette una workstation e applica il playbook di `07-post-exploitation`: dumpa LSASS con Mimikatz per ottenere hash e ticket, poi usa l'hash dell'admin locale per muoversi lateralmente (pass-the-hash) verso altri host, puntando al Domain Controller.

### Prospettiva Difensore (come il controllo risponde)

```
[DEF-008] Dominio hardenizzato: Credential Guard + LAPS + baseline via GPO
        |
        v
Attaccante lancia Mimikatz su LSASS -> Credential Guard isola LSASS
        |                                 -> dump cifrato/inaccessibile (POST-003 neutralizzato)
        v
Attaccante tenta pass-the-hash con l'admin locale -> LAPS: hash unico per host
        |                                 -> l'hash non funziona su nessun altro host
        v
Lateral movement bloccato: ogni host richiede una compromissione separata
        |
        v
Costo e rumore dell'attacco moltiplicati -> maggiore probabilita di detection
```

**Valore difensivo:** le due contromisure spezzano la kill chain nel punto critico - il passaggio da un host compromesso al dominio. Credential Guard nega le credenziali in memoria, LAPS nega la loro riutilizzabilita laterale. L'attaccante che con un solo dump avrebbe ottenuto le chiavi del regno si ritrova con credenziali inutili e ogni host come ostacolo separato.

**Sinergia con la detection:** i tentativi falliti (accesso a LSASS, pass-the-hash rifiutati) generano telemetria (Sysmon/Wazuh) che la detection rileva. L'hardening non solo previene, ma trasforma il tentativo d'attacco in un segnale rumoroso e rilevabile.

**Lezione difensiva:** in Active Directory l'identita e il perimetro. Le contromisure che proteggono le credenziali (Credential Guard, LAPS) valgono piu di qualsiasi firewall, perche attaccano il modello economico su cui si regge la compromissione di dominio: la riutilizzabilita delle credenziali.

---

## Tool di riferimento

| Tool | Tipo | Ruolo | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Group Policy` (GPO) | Policy management | AD | Applicazione centralizzata dell'hardening al dominio |
| `Microsoft Security Baseline` | Baseline (SCT) | Toolkit | GPO di hardening pre-configurate e riconosciute |
| `Credential Guard` | Credential protection | Feature | Isolamento di LSASS (contromisura a Mimikatz/POST-003) |
| `LAPS` | Password management | Feature | Password admin locale unica e ruotata per host |
| `CIS-CAT` | Compliance scanner | CLI | Verifica di conformita ai CIS Benchmarks Windows |
| `AppLocker` / `WDAC` | Application control | Feature | Blocco dell'esecuzione da percorsi non autorizzati |

> **Tool moderno consigliato:** le `Microsoft Security Baseline` (Security Compliance Toolkit) sono il punto di partenza standard, integrate con `CIS-CAT` per la verifica di conformita. `Credential Guard` e `LAPS` (ora Windows LAPS nativo) sono le due contromisure a piu alto impatto contro le tecniche di credential dumping e lateral movement. Per il controllo applicativo, `WDAC` (Windows Defender Application Control) e piu robusto di AppLocker.

---

## Mappatura MITRE ATT&CK

> La tabella mappa le tecniche d'attacco che l'hardening **previene o neutralizza**.

| Tattica (prevenuta) | Tecnica | ID MITRE | Ruolo del controllo |
| :--- | :--- | :--- | :--- |
| Credential Access | OS Credential Dumping: LSASS Memory | `T1003.001` | Credential Guard isola LSASS (neutralizza POST-003) (DEF-008) |
| Lateral Movement | Use Alternate Authentication Material: Pass the Hash | `T1550.002` | LAPS: hash admin locale unico per host (DEF-008) |
| Lateral Movement | Remote Services: SMB/Windows Admin Shares | `T1021.002` | Disabilitazione SMBv1, restrizione delle admin share |
| Execution | User Execution / payload da percorsi utente | `T1204` | AppLocker/WDAC bloccano l'esecuzione non autorizzata |
| Persistence | Boot or Logon Autostart: Registry Run Keys | `T1547.001` | Baseline restringe le chiavi di autostart e i privilegi |

| Contromisura difensiva (D3FEND) | ID D3FEND | Applicazione |
| :--- | :--- | :--- |
| Platform Hardening | `D3-PH` | Baseline CIS/Microsoft applicata via GPO |
| Credential Hardening | `D3-CH` | Credential Guard + LAPS proteggono le credenziali |
| Executable Allowlisting | `D3-EAL` | AppLocker/WDAC consentono solo eseguibili autorizzati |

---

> **Nota:** Tutte le attivita documentate sono state condotte su un ambiente Active Directory di laboratorio di proprieta dell'autore. Le GPO di hardening vanno testate in un OU pilota prima del rollout in produzione, perche una policy errata puo impattare l'intero dominio. Le tecniche sono documentate a scopo educativo e di difesa in contesto autorizzato.
