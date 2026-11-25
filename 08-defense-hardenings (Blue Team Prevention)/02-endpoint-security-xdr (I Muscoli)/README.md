> [English](README.en.md) | **Italiano**

# 02 - Endpoint security & XDR (i muscoli)

> - **Fase:** Defense & Hardening - Detection & Automated Response (Endpoint)
> - **Categoria:** Detection + Prevention - sensori e risposta sull'endpoint
> - **Prerequisiti:** Manager/piattaforma XDR e agenti sugli endpoint; risorse adeguate sul server; connettivita agente-manager
> - **Output:** Finding DEF-003..004; visibilita e risposta sull'endpoint; rilevamento di persistenza, tampering e minacce; contenimento automatico

---

## Introduzione

Se il SIEM (`../01-siem-log-analysis/`) e "il cervello" che vede e correla, la sicurezza dell'endpoint e "i muscoli": e dove la difesa non solo osserva ma agisce, direttamente sul sistema dove la minaccia si manifesta. L'evoluzione va dall'antivirus classico (firme statiche) all'EDR (Endpoint Detection and Response, analisi comportamentale) fino all'XDR (Extended Detection and Response, che estende la visibilita e la risposta oltre l'endpoint, correlando rete, cloud e identita).

La differenza chiave rispetto al SIEM e la vicinanza all'azione. Il SIEM riceve i log e li analizza a posteriori; l'agente sull'endpoint vive dentro il sistema, vede i processi nascere, i file cambiare, le connessioni aprirsi, e puo intervenire in tempo reale - terminare un processo, bloccare un IP, isolare l'host. E la differenza tra un analista che legge un report e una guardia presente sul posto.

La sezione e centrata su **Wazuh**, la piattaforma XDR open source di riferimento:

1. **Installazione e configurazione:** il deployment del Manager e degli agenti su Linux, Windows e Raspberry Pi, con il troubleshooting reale (gestione RAM dell'Indexer, versioni, SSL).

2. **Integrazione Suricata:** l'unione di Wazuh (cosa succede dentro il sistema) con Suricata (cosa passa nella rete), trasformando la piattaforma in SIEM + IDS.

3. **Threat Detection & Active Response (DEF-003, DEF-004):** il File Integrity Monitoring che rileva persistenza e tampering, e l'active response che contiene automaticamente l'attaccante.

Il posizionamento nel percorso: gli agenti endpoint sono i sensori che generano gli alert, il SIEM e il cervello che li correla. Insieme, sensori e cervello formano il ciclo detection, correlazione, risposta.

---

## Struttura della cartella

```
02-endpoint-security-xdr (I Muscoli)/
+-- README.md          # questo file: registro DEF-003..004, concetto di EDR/XDR
|
+-- wazuh/             # la piattaforma XDR open source
    +-- README.md                          # cos'e Wazuh
    +-- installing&configuring/            # deployment Manager + agenti (setup)
    +-- suricata-integration/              # Wazuh + Suricata = SIEM + IDS (setup)
    +-- threat-detection&active-response/  # DEF-003 (FIM), DEF-004 (active response)
```

---

## Flusso operativo consigliato

```
[INPUT] Endpoint da proteggere (Linux/Windows/RPi)
         |
         v
[1] Deployment (wazuh/installing&configuring/)
     +-- Manager + agenti -> visibilita sull'endpoint
              |
              v
[2] Estensione alla rete (wazuh/suricata-integration/)
     +-- Suricata IDS -> Wazuh legge eve.json -> SIEM + IDS
              |
              v
[3] Detection (wazuh/threat-detection&active-response/)
     +-- FIM -> rileva persistenza/tampering (DEF-003)
              |
              v
[4] Response automatica
     +-- active response -> blocco IP attaccante in secondi (DEF-004)
              |
              v
[OUTPUT] Alert -> SIEM (01) per correlazione + contenimento automatico
```

---

## Tool di riferimento

| tool | tipo | ruolo | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Wazuh` | xdr open source | piattaforma | detection endpoint, fim, active response |
| `Wazuh Agent` | endpoint sensor | agent | telemetria e risposta su linux/windows/rpi |
| `Suricata` | ids | integrazione | detection di rete correlata in wazuh |
| `Sysmon` | endpoint sensor | agent (win) | telemetria di processo dettagliata |
| `OSSEC` | hids | alternativa | il progetto da cui wazuh deriva (legacy) |

> **Tool moderno consigliato:** `Wazuh` e lo standard open source per EDR/XDR, con FIM, rilevamento vulnerabilita, active response e integrazione MITRE. L'abbinamento con `Sysmon` sugli endpoint Windows porta la telemetria a livello EDR commerciale. Alternative commerciali: CrowdStrike Falcon, Microsoft Defender for Endpoint, SentinelOne.

---

## Registro finding - sezione endpoint security & XDR

| id | descrizione | severity | sottocartella |
| :--- | :--- | :---: | :--- |
| `DEF-003` | wazuh fim: rilevamento di persistenza, tampering di file critici e rootkit | `Alto` | `wazuh/threat-detection&active-response/` |
| `DEF-004` | wazuh active response: contenimento automatico (blocco ip) su alert | `Alto` | `wazuh/threat-detection&active-response/` |

> I file `installing&configuring/` e `suricata-integration/` sono guide di setup/configurazione (nessun finding ID, coerentemente con la convenzione dei file di installazione).

---

## Mappatura MITRE ATT&CK - aggregata

> Tecniche d'attacco **rilevate e contenute** dai controlli della sezione.

| tattica (contrastata) | tecnica | id mitre | finding correlato |
| :--- | :--- | :--- | :--- |
| persistence | account manipulation: ssh authorized keys | `T1098.004` | DEF-003 |
| persistence | boot or logon autostart: registry run keys | `T1547.001` | DEF-003 |
| defense evasion | rootkit | `T1014` | DEF-003 |
| credential access | brute force | `T1110` | DEF-004 |

---

> **Nota:** Tutte le attivita documentate in questa sezione sono state condotte su un ambiente di laboratorio di proprieta dell'autore. Le simulazioni d'attacco per validare i sensori sono state eseguite su sistemi di test. L'active response va configurata con attenzione per evitare auto-blocchi. Le tecniche sono documentate a scopo educativo e di difesa in contesto autorizzato.
