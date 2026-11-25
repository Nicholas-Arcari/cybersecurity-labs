> [English](README.en.md) | **Italiano**

# Tooling - Strumenti per la Sicurezza Cloud

> - **Fase:** Cloud Security - Toolkit trasversale
> - **Categoria:** Riferimento strumenti (offensivi e difensivi)
> - **Prerequisiti:** Credenziali/accesso agli ambienti cloud da testare o auditare
> - **Output:** Guida di riferimento ai tool cloud usati trasversalmente nel modulo

---

## Introduzione

Questa cartella raccoglie i tool "must-have" per la sicurezza cloud, usati trasversalmente nelle sezioni del modulo. A differenza delle cartelle tematiche (che documentano finding e tecniche), questa e una guida di riferimento agli strumenti: cosa fanno, quando usarli, come integrarli nel flusso di lavoro. Non contiene finding propri - i tool sono applicati nei finding delle rispettive sezioni.

Gli strumenti si dividono per prospettiva, riflettendo la doppia natura del modulo:

- **Offensivi:** `Pacu` (exploitation framework AWS), `cloud-enum` (scoperta di asset e bucket). Simulano l'attaccante per trovare le debolezze.
- **Difensivi:** `Prowler` (hardening e compliance), `ScoutSuite` (audit multi-cloud). Verificano la postura di sicurezza per correggerla prima dell'attaccante.

La simmetria e il tema centrale della sicurezza cloud: gli stessi percorsi che un tool offensivo (Pacu) sfrutta, un tool difensivo (Prowler/ScoutSuite) li individua e aiuta a chiudere. Padroneggiare entrambe le prospettive e cio che distingue un security analyst cloud completo.

---

## Struttura della cartella

```
Tooling/
+-- README.md          # questo file: guida di riferimento ai tool cloud
|
+-- cloud-enum/        # Recon: scoperta di asset e bucket (multi-cloud)
+-- pacu/              # Offensivo: exploitation framework per AWS
+-- prowler/           # Difensivo: hardening e compliance (AWS/Azure/GCP)
+-- scoutsuite/        # Difensivo: audit multi-cloud della configurazione
```

---

## Quando usare quale strumento

```
[RECON]      cloud-enum   -> scoperta di asset, bucket, servizi esposti (multi-cloud)
                |
                v
[OFFENSIVO]  Pacu         -> exploitation AWS: enum permessi, privesc, persistenza
                |
                v
[DIFENSIVO]  Prowler      -> centinaia di controlli di sicurezza/compliance, report prioritizzato
             ScoutSuite   -> audit multi-cloud, vista d'insieme della postura
                |
                v
[CORREZIONE] i finding difensivi guidano l'hardening (least privilege, block public access, ...)
```

---

## Tool di riferimento

| Tool | Prospettiva | Provider | Ruolo principale |
| :--- | :--- | :--- | :--- |
| `cloud_enum` | Recon | Multi | Scoperta di asset e bucket via permutazione dei nomi |
| `Pacu` | Offensivo | AWS | "Metasploit per AWS": enum, privesc, exploitation |
| `Prowler` | Difensivo | AWS/Azure/GCP | Controlli di sicurezza e compliance (CIS, ...) |
| `ScoutSuite` | Difensivo | Multi | Audit della configurazione multi-cloud |
| `Trivy` | Difensivo | (container/IaC) | Scanner universale (vedere `../02-.../image-scanning/`) |

> **Tool moderno consigliato:** per un assessment cloud completo, `cloud_enum` per il recon, `Pacu` per l'exploitation AWS, `Prowler` e `ScoutSuite` per l'audit difensivo. `Trivy` (documentato in `../02-containers-security/image-scanning/`) come scanner universale per container e IaC.

---

> **Nota:** Questa cartella e una guida di riferimento agli strumenti, senza finding propri. Ogni tool va usato esclusivamente su ambienti cloud di proprieta dell'autore o con autorizzazione esplicita; l'uso su ambienti di terzi senza permesso costituisce reato e viola i termini dei provider. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
