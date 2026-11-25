> [English](README.en.md) | **Italiano**

# Wazuh - Piattaforma XDR Open Source

> - **Fase:** Defense & Hardening - Endpoint Detection & Response (XDR)
> - **Categoria:** Detection + Prevention - la piattaforma difensiva centrale del modulo
> - **Prerequisiti:** Server con risorse adeguate (RAM per l'Indexer); endpoint da monitorare; connettivita agente-manager (porte 1514/1515)
> - **Output:** Piattaforma di detection e response operativa; base per i finding DEF-003, DEF-004

---

## Cos'e Wazuh

Wazuh e una piattaforma di sicurezza open source che unifica in un'unica soluzione funzioni che tradizionalmente richiedevano strumenti separati: XDR (Extended Detection and Response) e SIEM. Nato come fork di OSSEC (un HIDS storico), Wazuh lo ha esteso con un motore di analisi moderno basato su OpenSearch (un fork di Elasticsearch), una dashboard web e un ricco set di funzionalita difensive.

Le sue capacita coprono l'intero spettro della difesa dell'endpoint:

- **File Integrity Monitoring (FIM):** sorveglia file e directory critici, rilevando modifiche non autorizzate (persistenza, tampering).
- **Threat Detection:** analizza log ed eventi contro un set di regole per rilevare anomalie e minacce note.
- **Rootcheck:** cerca rootkit, malware e configurazioni anomale.
- **Vulnerability Detection:** correla il software installato con i database CVE per segnalare le vulnerabilita note.
- **Active Response:** esegue automaticamente azioni di contenimento (blocco IP, kill processo) quando scatta una regola.
- **Compliance:** mappa gli eventi su framework di conformita (PCI DSS, GDPR, HIPAA, NIST) e su MITRE ATT&CK.

L'architettura e client-server: gli **agenti** installati sugli endpoint (Linux, Windows, macOS, Raspberry Pi) raccolgono telemetria e la inviano al **Manager**, che la decodifica, la analizza contro le regole e genera gli alert; l'**Indexer** (OpenSearch) li archivia e li rende ricercabili; la **Dashboard** li visualizza. Questa separazione tra raccolta (agente) e analisi (Manager) e cio che rende Wazuh sia un sensore endpoint sia un SIEM leggero.

---

## Struttura della cartella

```
wazuh/
+-- README.md                          # questo file: cos'e Wazuh (concetto e architettura)
|
+-- installing&configuring/            # deployment Manager + agenti + troubleshooting reale
+-- suricata-integration/              # Wazuh + Suricata = SIEM + IDS
+-- threat-detection&active-response/  # DEF-003 (FIM/detection), DEF-004 (active response)
```

---

## Percorso consigliato

```
[1] installing&configuring/
     +-- deployment del Manager su Kali + agenti su Windows/RPi
     +-- troubleshooting: RAM Indexer, versioni, SSL/TLS
              |
              v
[2] suricata-integration/
     +-- Suricata come IDS di rete -> Wazuh legge eve.json
     +-- da endpoint monitoring a SIEM + IDS completo
              |
              v
[3] threat-detection&active-response/
     +-- FIM: rileva persistenza e tampering (DEF-003)
     +-- active response: contenimento automatico (DEF-004)
```

---

## Tool di riferimento

| Componente | Ruolo | Funzione |
| :--- | :--- | :--- |
| `Wazuh Manager` | Analisi | Decodifica log, applica regole, genera alert, gestisce active response |
| `Wazuh Indexer` | Storage | Indicizzazione e ricerca (OpenSearch); esoso di RAM |
| `Wazuh Dashboard` | Visualizzazione | Interfaccia web, threat hunting, gestione |
| `Wazuh Agent` | Raccolta | Telemetria e risposta sugli endpoint |
| `Suricata` | IDS di rete | Detection di rete integrata (`suricata-integration/`) |

> **Nota sull'architettura:** l'Indexer e il componente piu esoso di risorse (JVM/OpenSearch). Come documentato in `installing&configuring/`, la gestione della RAM (limitazione dell'heap JVM) e la principale criticita di un deployment su hardware limitato. E lo stesso vincolo dell'ELK Stack (`../../01-siem-log-analysis/elk-stack/`), data la comune base OpenSearch/Elasticsearch.

---

> **Nota:** Wazuh e uno strumento puramente difensivo. Tutte le attivita documentate nelle sottocartelle sono state condotte su un ambiente di laboratorio di proprieta dell'autore. Le tecniche sono documentate a scopo educativo e di difesa in contesto autorizzato.
