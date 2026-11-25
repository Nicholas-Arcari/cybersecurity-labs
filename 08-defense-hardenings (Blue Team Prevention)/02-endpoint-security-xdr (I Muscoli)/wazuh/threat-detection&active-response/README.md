> [English](README.en.md) | **Italiano**

# Wazuh - threat detection & Active response

> - **Fase:** Defense & Hardening - Detection & Automated Response (Endpoint/XDR)
> - **Categoria:** Detection + Prevention - rilevamento minacce e risposta automatica
> - **Prerequisiti:** Wazuh Manager e agenti operativi (vedere `../installing&configuring/`); regole e decoder configurati; per l'active response: script di risposta abilitati sull'agente
> - **Output:** Finding DEF-003 (FIM/threat detection), DEF-004 (active response); rilevamento di manomissioni e rootkit; blocco automatico degli attaccanti

- **Ambiente Operativo:** Wazuh Manager (Kali), agenti su Linux/Windows/Raspberry Pi
- **Ruolo:** "I Muscoli" - non solo vede la minaccia, ma reagisce
- **Tool principali:** Wazuh (FIM/Syscheck, Rootcheck, Active Response)

---

## Executive summary

Se il SIEM (`../../../01-siem-log-analysis/`) e "il cervello" che vede e correla, Wazuh e "i muscoli": non si limita a rilevare, agisce. Questo file documenta le due capacita che trasformano Wazuh da semplice sensore a sistema di difesa attivo (XDR - Extended Detection and Response): il rilevamento delle minacce sull'endpoint e la risposta automatica.

Il **File Integrity Monitoring (FIM)**, tramite il modulo Syscheck, sorveglia file e directory critici e allerta a ogni modifica non autorizzata: e la contromisura diretta alla persistenza e alla manomissione viste in `07-post-exploitation` (un attaccante che modifica `/etc/passwd`, aggiunge una chiave SSH o altera un binario di sistema viene rilevato). Il **Rootcheck** cerca rootkit e anomalie note. Il finding DEF-003 documenta questa capacita di detection sull'endpoint.

L'**Active Response** e il salto di qualita: Wazuh puo eseguire automaticamente uno script di risposta quando scatta una regola - tipicamente bloccare l'IP di un attaccante a livello firewall. Il finding DEF-004 documenta questa risposta automatica, che riduce a secondi il tempo tra rilevamento e contenimento, senza intervento umano.

---

## Struttura della cartella

```
threat-detection&active-response/
+-- README.md      # questo file: FIM/threat detection (DEF-003) + active response (DEF-004)
+-- img/           # alert FIM e log di active response
```

---

## File integrity monitoring e threat detection

**ID Finding:** `DEF-003` | **Severity:** `Alto` (rilevamento di manomissione di file critici, persistenza e rootkit sull'endpoint)

### Contesto operativo

Il modulo Syscheck di Wazuh calcola e memorizza gli hash (checksum), i permessi e gli attributi dei file monitorati; a intervalli regolari (o in tempo reale con `<realtime>`) ricalcola e confronta, generando un alert a ogni discrepanza. E la contromisura diretta alle tecniche di persistenza: modifiche a `/etc/passwd`, `/etc/sudoers`, `authorized_keys`, chiavi di registro Run su Windows, o ai binari di sistema.

### PoC - configurazione del FIM (syscheck)

```XML
<!-- /var/ossec/etc/ossec.conf sull'agente (o via gruppo dal Manager) -->
<syscheck>
  <directories realtime="yes" check_all="yes">/etc,/usr/bin,/usr/sbin</directories>
  <directories realtime="yes" check_all="yes">/root/.ssh</directories>
  <!-- allerta su modifiche a file critici di autenticazione -->
</syscheck>
```

### PoC - rilevamento di una modifica non autorizzata

```Bash
# [Simulazione attacco] aggiunta di una chiave SSH backdoor
echo "ssh-rsa AAAA...attacker" >> /root/.ssh/authorized_keys
```

```
# Alert generato dal Manager (rule 550: Integrity checksum changed)
** Alert 1699887766.12345: - ossec,syscheck,
Rule: 550 (level 7) -> 'Integrity checksum changed.'
File '/root/.ssh/authorized_keys' modified          <-- persistenza rilevata (DEF-003)
Attributes: size, md5, sha256 changed
```

```Bash
# Rootcheck: scansione per rootkit e anomalie note
/var/ossec/bin/wazuh-control restart
# Gli alert rootcheck appaiono nella Dashboard sotto rule.groups:rootcheck
```

### Tuning e operativita difensiva

- **Selezione mirata:** monitorare in `realtime` solo i path critici (autenticazione, binari, cron, chiavi); il FIM su directory grandi e volatili genera rumore
- **Ignore list:** escludere file legittimamente volatili (log, cache, temp) per ridurre i falsi positivi
- **Baseline:** stabilire una baseline pulita subito dopo l'hardening (`../../../04-hardening-scripts/`), cosi ogni deviazione successiva e significativa
- **Correlazione:** inoltrare gli alert FIM al SIEM per correlarli con altri eventi (una modifica a `authorized_keys` + un login SSH riuscito e una kill chain)

---

## Active response - contenimento automatico

**ID Finding:** `DEF-004` | **Severity:** `Alto` (risposta automatica che contiene l'attaccante in secondi, senza intervento umano)

### Contesto operativo

L'Active Response collega una regola a uno script eseguito automaticamente sull'agente (o sul Manager) quando la regola scatta. Il caso d'uso classico e il blocco firewall di un IP che ha superato una soglia di login falliti: la stessa detection di brute force vista nel SIEM (`../../../01-siem-log-analysis/elk-stack/`, DEF-001), ma con contenimento automatico invece della sola notifica.

### PoC - configurazione dell'Active response (firewall-drop)

```XML
<!-- /var/ossec/etc/ossec.conf sul Manager -->
<active-response>
  <command>firewall-drop</command>
  <location>local</location>
  <rules_id>5763</rules_id>        <!-- rule: SSH brute force (piu tentativi falliti) -->
  <timeout>600</timeout>           <!-- blocco IP per 600 secondi -->
</active-response>
```

### PoC - blocco automatico in azione

```
# [Attacco] brute force SSH dall'IP 10.0.2.15 -> supera la soglia della rule 5763
** Alert: Rule 5763 (level 10) -> 'sshd: brute force trying to get access'

# Active Response eseguita automaticamente:
active-response/bin/firewall-drop: Adding IP 10.0.2.15 to iptables DROP   <-- IP bloccato (DEF-004)
```

```Bash
# Verifica sull'agente: l'IP dell'attaccante e ora bloccato
iptables -L INPUT -n | grep 10.0.2.15
```

```
DROP   all  --  10.0.2.15    0.0.0.0/0        <-- attaccante contenuto in automatico
```

Dopo il `timeout` (600 secondi), Wazuh rimuove automaticamente la regola, evitando che un falso positivo blocchi permanentemente un IP legittimo.

### Tuning e operativita difensiva

- **Timeout e non-permanenza:** preferire blocchi temporizzati per contenere l'impatto dei falsi positivi; un blocco permanente va riservato a IOC ad alta confidenza
- **Whitelist:** inserire in whitelist gli IP di gestione e i bastion host, per non auto-bloccarsi (un errore classico e bloccare il proprio IP di amministrazione)
- **Escalation graduata:** azioni diverse per severita diverse (log, blocco temporaneo, isolamento host)
- **Auditing:** ogni active response va loggata e rivista; l'automazione senza revisione puo essere sfruttata da un attaccante per causare un self-DoS (indurre il blocco di IP legittimi)

---

## Esperienza di laboratorio

Il FIM ha dato la soddisfazione difensiva piu immediata di tutto il modulo. Avevo documentato le tecniche di persistenza in `07-post-exploitation` (aggiunta di chiavi SSH, modifica di file di sistema); vederle rilevate in tempo reale da Wazuh - l'alert `authorized_keys modified` comparso in Dashboard nel momento stesso in cui simulavo la backdoor - ha chiuso il cerchio tra attacco e difesa. La stessa azione che come attaccante mi garantiva l'accesso, come difensore mi tradiva istantaneamente.

L'Active Response e stata la parte piu delicata da tarare. Il primo test ha funzionato troppo bene: durante una prova di configurazione mi sono auto-bloccato l'IP di amministrazione, perdendo l'accesso SSH all'agente per 600 secondi. Questa "lezione dolorosa" ha reso concreto il principio che l'automazione difensiva e potente ma a doppio taglio: una regola mal tarata puo trasformarsi in un self-DoS. La whitelist degli IP di gestione, che inizialmente sembrava un dettaglio, si e rivelata essenziale.

La riflessione operativa e stata sul compromesso tra velocita e rischio. L'active response riduce il tempo di contenimento da minuti/ore (intervento umano) a secondi (automazione), ma trasferisce il rischio: un falso positivo automatizzato causa danno immediato. Il timeout temporizzato e la whitelist sono i due controlli che rendono accettabile questo compromesso, contenendo l'impatto di un errore.

---

## Analisi teorica: detection senza response e solo meta della difesa

Il modello XDR (Extended Detection and Response) unisce due funzioni che storicamente erano separate: rilevare e reagire. Un IDS classico rileva e notifica, lasciando la risposta all'operatore umano; questo introduce una finestra temporale - il "dwell time" tra rilevamento e contenimento - durante la quale l'attaccante continua indisturbato. In quella finestra si consuma gran parte del danno: escalation, movimento laterale, esfiltrazione.

L'active response comprime questa finestra a zero per le minacce note e ad alta confidenza. Non sostituisce l'analista (le decisioni complesse restano umane), ma automatizza le risposte deterministiche: se un IP fa brute force, bloccarlo non richiede giudizio, richiede velocita. Delegare all'automazione le decisioni ovvie libera l'analista per quelle che richiedono contesto.

Il rischio speculare e che l'automazione, priva di giudizio, esegue anche gli errori alla stessa velocita. Un falso positivo che in un sistema manuale sarebbe filtrato dall'analista, in un sistema automatico diventa un'azione immediata (blocco di un IP legittimo, isolamento di un host produttivo). Questo definisce il principio di progettazione dell'active response: automatizzare solo le risposte a detection ad alta confidenza, con controlli di sicurezza (timeout, whitelist) che limitano il danno di un errore. La difesa attiva e potente esattamente quanto e disciplinata la sua configurazione.

---

## Scenario reale: detection e response in azione

> Questa sezione descrive come questi controlli difensivi opererebbero in un incidente reale.

### Prospettiva attaccante (cosa tenta)

L'attaccante, ottenuto un accesso iniziale, tenta di stabilire persistenza aggiungendo una chiave SSH e poi di espandersi con un brute force verso altri host interni. Confida che le modifiche ai file passino inosservate e che il brute force, se abbastanza lento, non superi le soglie.

### Prospettiva difensore (come i controlli rispondono)

```
[DEF-003] FIM rileva la modifica di /root/.ssh/authorized_keys in tempo reale
        |
        v
Alert immediato: persistenza tentata su host X
        |
        v
[DEF-004] Il brute force verso host interni supera la rule 5763
        |
        v
Active Response: IP attaccante bloccato in iptables in <1s, timeout 600s
        |
        v
SOC: correlazione FIM + brute force -> host X compromesso, contenimento e bonifica
```

**Valore difensivo:** il FIM tradisce la persistenza nel momento in cui viene stabilita, negando all'attaccante il vantaggio della permanenza silenziosa. L'active response contiene l'espansione prima che riesca, riducendo il dwell time a secondi. Insieme, detection e response spezzano la kill chain in due punti: la persistenza e il movimento laterale.

**Indicatori monitorati (IOC):** modifiche a file di autenticazione/binari di sistema (rule 550), brute force (rule 5763), alert rootcheck, sequenze FIM + accesso correlate nel SIEM.

**Lezione difensiva:** rilevare non basta se la risposta e lenta. L'attaccante opera alla velocita della macchina; una difesa che risponde alla velocita dell'uomo gli concede la finestra di cui ha bisogno. L'active response, tarata con disciplina, riporta la difesa alla stessa velocita dell'attacco.

---

## Tool di riferimento

| tool | tipo | ruolo | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Wazuh Syscheck` (fim) | file integrity monitoring | modulo | rilevamento di modifiche a file/directory critici |
| `Wazuh Rootcheck` | anomaly/rootkit detection | modulo | ricerca di rootkit e configurazioni anomale |
| `Wazuh Active Response` | automated response | modulo | esecuzione di script (blocco ip, kill processo) su alert |
| `firewall-drop` | ar script | script | blocco di un ip a livello iptables/netsh |
| `Sysmon` + wazuh | endpoint telemetry | agent (win) | telemetria di processo dettagliata per detection avanzata |
| `Suricata` + wazuh | ids integration | integrazione | detection di rete correlata (vedere `../suricata-integration/`) |

> **Tool moderno consigliato:** l'integrazione `Sysmon` + Wazuh sugli endpoint Windows fornisce una telemetria di processo (creazione processi, connessioni di rete, caricamento DLL) che porta la detection dell'endpoint a livello EDR. Per la risposta, valutare l'integrazione con SOAR per orchestrare azioni complesse oltre il semplice blocco IP.

---

## Mappatura MITRE ATT&CK

> La tabella mappa le tecniche d'attacco che i controlli **rilevano e contengono**.

| tattica (contrastata) | tecnica | id mitre | ruolo del controllo |
| :--- | :--- | :--- | :--- |
| persistence | account manipulation: ssh authorized keys | `T1098.004` | fim rileva la modifica di authorized_keys (DEF-003) |
| persistence | boot or logon autostart: registry run keys | `T1547.001` | fim rileva modifiche alle chiavi run su windows (DEF-003) |
| defense evasion | rootkit | `T1014` | rootcheck rileva rootkit e anomalie (DEF-003) |
| credential access | brute force | `T1110` | active response blocca l'ip che fa brute force (DEF-004) |
| impact | account access removal | `T1531` | (rischio) l'active response mal tarata puo auto-bloccare account/ip legittimi |

| contromisura difensiva (d3fend) | id d3fend | applicazione |
| :--- | :--- | :--- |
| file integrity monitoring | `D3-FIM` | sorveglianza degli hash dei file critici (DEF-003) |
| network traffic filtering | `D3-NTF` | blocco automatico dell'ip ostile a livello firewall (DEF-004) |

---

> **Nota:** Tutte le attivita documentate sono state condotte su un ambiente di laboratorio di proprieta dell'autore. Le simulazioni di attacco (backdoor SSH, brute force) sono state eseguite su sistemi di test per validare i controlli difensivi. L'active response va configurata con attenzione in produzione per evitare auto-blocchi e self-DoS. Le tecniche sono documentate a scopo educativo e di difesa in contesto autorizzato.
