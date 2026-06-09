> [English](README.en.md) | **Italiano**

# Active Scanning: Nmap Scripting Engine (NSE)

> - **Fase:** Reconnaissance - Active Network Scanning
> - **Visibilita:** Media - gli script NSE generano traffico identificabile (richieste SMB, NetBIOS, banner grabbing) rilevabile da IDS
> - **Prerequisiti:** Nmap installato, porte target identificate da scansione precedente (SCAN-001/SCAN-002), accesso root
> - **Output:** SCAN-003 - SMB Signing non obbligatorio (vettore SMB Relay) e NetBIOS name disclosure su 10.0.2.3

---

Obiettivo: Utilizzo di script avanzati per l'enumerazione dei servizi e la rilevazione di vulnerabilità di configurazione.

---

## 1 Introduzione Teorica

L'Nmap Scripting Engine (NSE) permette di automatizzare l'interazione con i servizi per estrarre informazioni che il semplice port scanning non rivela.

In particolare, gli script di default (`-sC`) eseguono una batteria di test sicuri per identificare nomi NetBIOS, orari di sistema e configurazioni di sicurezza del protocollo SMB.

---

## 2 Esecuzione Tecnica

Default Scripts & Security Mode

È stata eseguita una scansione completa utilizzando gli script di default (`-sC`) combinati con la verifica della modalità di sicurezza SMB2.

```Bash
sudo nmap -p 445 -sC 10.0.2.3
```

![](./img/Screenshot_2026-02-04_11_59_34.jpg)

---

## 3 Analisi dei Risultati

**ID Finding:** `SCAN-003` | **Severity:** `Alto`

Dall'output dello script sono emersi due dati fondamentali per la fase di Enumeration:

#### A. Information Disclosure (NetBIOS)

- Dato Rilevato: `NetBIOS name: WINDOWS-TEST`
- Significato: Nonostante il blocco di `smb-os-discovery`, il servizio NetBIOS ha rivelato il nome host della macchina. Questo permette di identificare la macchina all'interno di un dominio o workgroup.

#### B. Vulnerabilità di Configurazione (SMB Signing)

- Dato Rilevato: `Message signing enabled but not required`
- Significato: Il target supporta la firma digitale dei pacchetti SMB ma non la impone.
- Impatto di Sicurezza (Red Team): Questa configurazione espone la rete ad attacchi di tipo SMB Relay (Man-in-the-Middle). Un attaccante posizionato nella stessa rete locale potrebbe intercettare un tentativo di autenticazione verso questo server e "rilanciarlo" verso un altro host per ottenere accesso non autorizzato.

---

## 4 Remediation (Blue Team)

Per mitigare il rischio di SMB Relay:

- Impostare la policy di gruppo (GPO) "Microsoft network server: Digitally sign communications (always)" su Enabled.
- Disabilitare NetBIOS se non strettamente necessario per ridurre la visibilità del nome host.

---

## Analisi a Basso Livello: NSE Engine e SMB Signing Protocol

### Architettura del Nmap Scripting Engine

L'NSE e un interprete Lua integrato in Nmap che esegue script organizzati in categorie funzionali. Quando si invoca `-sC` (equivalente a `--script=default`), Nmap carica tutti gli script con la categoria `default` e li esegue contro le porte aperte identificate. Il motore opera in pipeline:

```
Port scan -> Service detection (-sV) -> Script selection (category match)
                                              |
                                              v
                                    Script execution (Lua VM)
                                              |
                                              v
                                    Output parsing + formatting
```

Ogni script NSE dichiara le proprie dipendenze nel header Lua: `categories`, `portrule` (condizione di attivazione basata su porta/servizio), e `action` (funzione principale). Lo script `smb2-security-mode` si attiva quando Nmap rileva il servizio `microsoft-ds` sulla porta 445 e negozia una sessione SMB2 per interrogare le Security Mode flags.

### SMB Signing: Meccanismo a Livello di Protocollo

La firma dei pacchetti SMB opera a livello di sessione nel protocollo SMB2/3 (RFC MS-SMB2, sezione 3.2.4.1.1). Durante la negoziazione iniziale (`SMB2 NEGOTIATE`), client e server scambiano le rispettive capability flags:

```
SMB2 NEGOTIATE Request:
  SecurityMode: 0x01 (Signing Enabled)          <-- il client supporta la firma

SMB2 NEGOTIATE Response:
  SecurityMode: 0x01 (Signing Enabled)          <-- il server supporta ma NON richiede
  vs.
  SecurityMode: 0x03 (Signing Enabled + Required) <-- configurazione sicura
```

Il valore `0x01` (Signing Enabled but not Required) e esattamente la condizione rilevata da SCAN-003. In questo stato, la firma viene negoziata solo se entrambi gli endpoint la richiedono - il che in pratica significa che non viene mai applicata, perche il client malevolo (l'attaccante) non la richiede.

**Perche questo abilita SMB Relay:**

In un attacco SMB Relay (NTLM Relay), l'attaccante si posiziona come Man-in-the-Middle tra un client legittimo e il server target. Il client invia una challenge NTLM, l'attaccante la inoltra al server, riceve la risposta e la rilancia al client. Senza firma obbligatoria, il server non puo verificare che i pacchetti provengano effettivamente dal client originale - l'attaccante puo iniettare comandi arbitrari nella sessione autenticata.

Con SMB Signing Required (`0x03`), ogni pacchetto contiene un HMAC-SHA256 calcolato con la Session Key derivata dall'autenticazione NTLM. L'attaccante in posizione MitM non possiede questa chiave, quindi non puo forgiare pacchetti validi - l'attacco fallisce.

---

## Scenario Reale: Proiezione in un Engagement di Penetration Testing

> Questa sezione descrive come SCAN-003 si inserirebbe in un engagement reale su una rete Active Directory aziendale.

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** accesso alla rete interna (via VPN compromessa, phishing, o accesso fisico); scansione NSE identifica SMB Signing non obbligatorio su uno o piu host Windows.

**Kill Chain proiettata:**

```
SCAN-003: nmap -sC -p 445 -> SMB Signing "enabled but not required"
        |
        v
Responder.py in ascolto sulla rete (LLMNR/NBT-NS poisoning)
        |
        v
Utente legittimo tenta accesso a share inesistente -> NTLM challenge intercettata
        |
        v
ntlmrelayx.py -t smb://10.0.2.3 -> relay dell'autenticazione al target senza signing
        |
        v
Esecuzione comandi come utente vittima sul target (se admin locale -> SYSTEM)
        |
        v
Mimikatz / secretsdump.py -> hash NTLM di tutti gli utenti locali
        |
        v
Pass-the-Hash laterale -> Domain Controller -> compromissione AD completa
```

**Impatto potenziale:** SMB Relay e uno degli attacchi piu devastanti in ambiente Active Directory. Non richiede la conoscenza di alcuna password - sfrutta autenticazioni legittime gia in corso sulla rete. In un engagement CrowdStrike del 2023, il 68% delle reti AD testate presentava almeno un host con SMB Signing non obbligatorio. L'attacco e particolarmente efficace in combinazione con LLMNR/NBT-NS poisoning (Responder.py), che forza i client a inviare hash NTLM all'attaccante.

**Vettori di monetizzazione tipici:**
- Ransomware: SMB Relay -> admin locale -> Mimikatz -> Domain Admin -> cifratura di massa via GPO
- Data exfiltration: accesso a file share con credenziali relay per esfiltrazione documenti riservati
- Persistenza: creazione account backdoor o Golden Ticket post-relay

### Prospettiva Difensore (Blue Team)

**Rilevamento:** l'attacco SMB Relay genera traffico NTLM anomalo: un singolo hash NTLM viene utilizzato in due sessioni SMB distinte (quella originale e quella relayed) in una finestra temporale di millisecondi. Event ID 4624 con LogonType 3 (Network) da IP sorgente diverso da quello atteso per l'utente.

**Indicatori di Compromissione (IOC):**
- Event ID 4624 (LogonType 3) con source IP corrispondente alla macchina dell'attaccante, non dell'utente legittimo
- Traffico LLMNR (porta UDP 5355) e NBT-NS (porta UDP 137) verso IP non DNS - indica Responder attivo
- Due sessioni SMB2 con lo stesso NTLM challenge/response ma source IP diversi entro 1 secondo
- Processo `cmd.exe` o `powershell.exe` figlio di `svchost.exe` (SMB service) su host relayed

**Contenimento:** abilitare immediatamente SMB Signing Required via GPO; disabilitare LLMNR e NBT-NS su tutta la rete; verificare sessioni attive anomale con `net session` sugli host target.

**Hardening strutturale:**
- GPO obbligatoria: `Microsoft network server: Digitally sign communications (always)` = Enabled su tutti gli host del dominio
- GPO supplementare: `Microsoft network client: Digitally sign communications (always)` = Enabled
- Disabilitare LLMNR via GPO: `Computer Configuration -> Administrative Templates -> Network -> DNS Client -> Turn off Multicast Name Resolution`
- Disabilitare NBT-NS via DHCP option o interfaccia di rete
- Implementare EPA (Extended Protection for Authentication) su tutti i servizi HTTP che accettano NTLM
- Migrare progressivamente da NTLM a Kerberos-only authentication

---

## Esperienza di Laboratorio

La scansione NSE ha rivelato un aspetto che non sarebbe emerso dal semplice port scan: la porta 445 era aperta e il servizio SMB funzionante, ma l'informazione critica (signing non obbligatorio) era nascosta nelle capability flags negoziate a livello di protocollo. Senza `-sC`, il risultato sarebbe stato un generico "445/tcp open microsoft-ds" - tecnicamente corretto ma operativamente inutile.

L'output ha mostrato anche il blocco di `smb-os-discovery` - lo script che avrebbe rivelato versione OS, dominio e FQDN. Il target aveva apparentemente limitato le query anonime (RestrictAnonymous), ma il nome NetBIOS e sfuggito al filtro perche opera su un canale diverso (datagram service, porta 138/UDP). Questa discrepanza evidenzia un pattern comune negli ambienti Windows: l'hardening parziale crea un falso senso di sicurezza mentre lascia aperti vettori alternativi.

La scoperta del signing non obbligatorio ha immediatamente aperto la strada alla catena documentata nei moduli successivi (VULN-001 via Nessus, VULN-004 via accesso C$, EXPLOIT-018 via Pass-the-Hash). In un engagement reale, questo singolo finding NSE avrebbe giustificato l'intera fase di exploitation successiva.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Discovery | Network Service Discovery | `T1046` | Scansione NSE con script default (-sC) su porta 445 del target 10.0.2.3 per identificare configurazioni SMB e servizi esposti (SCAN-003) |
| Reconnaissance | Gather Victim Host Info: Software | `T1592.002` | Enumerazione versione protocollo SMB2 e configurazione Message Signing tramite script smb2-security-mode (SCAN-003) |

---

---

## Correlazioni con altri finding

Il finding SCAN-003 (SMB Signing not required) e il punto di partenza di una catena di attacco documentata nel laboratorio:

| Questo finding | Porta a | Modulo |
| :--- | :--- | :--- |
| SCAN-003 - SMB Signing disabled | [VULN-001](<../../../../02-vulnerability-assessment/01-general-scanners (Infrastructure)/nessus/README.md>) - Conferma via Nessus credentialed | 02-vuln-assessment |
| SCAN-003 - NetBIOS exposure | [VULN-003](<../../../../02-vulnerability-assessment/02-protocol-specific-audit/smb-net-bios/README.md>) - NetBIOS Name Disclosure | 02-vuln-assessment |
| SCAN-003 - Credenziali nick/1234 | [VULN-004](<../../../../02-vulnerability-assessment/02-protocol-specific-audit/smb-net-bios/README.md>) - Accesso C$ con credenziali standard | 02-vuln-assessment |
| VULN-001 + VULN-004 (catena) | [EXPLOIT-018](<../../../../04-system-exploitation/03-privilege-escalation (PrivEsc)/windows-priv-esc/winpeas/README.md>) - Pass-the-Hash lateral movement | 04-exploitation |

> **Nota:** Le attivita di enumeration con Nmap NSE sono state eseguite esclusivamente all'interno di un laboratorio VirtualBox isolato con target Windows 10 autorizzato (10.0.2.3). La misconfiguration SMB Signing documentata e stata rilevata a scopo di analisi e documentazione della superficie di attacco.
