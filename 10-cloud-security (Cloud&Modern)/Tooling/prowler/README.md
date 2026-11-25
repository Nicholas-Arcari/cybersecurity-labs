> [English](README.en.md) | **Italiano**

# Prowler - hardening e compliance cloud

> - **Fase:** Cloud Security - Audit & Compliance (Defense)
> - **Categoria:** Difensivo - lo standard di fatto per l'hardening cloud
> - **Prerequisiti:** Credenziali con permessi di sola lettura/audit sull'account; Prowler
> - **Output:** Report prioritizzato di misconfigurazioni e non-conformita (CIS, NIST, GDPR, ...)

- **Tool principale:** Prowler (multi-cloud: AWS, Azure, GCP)

---

## Cos'e e a cosa serve

`Prowler` e lo standard di fatto per l'hardening e la compliance cloud: lancia centinaia di controlli di sicurezza sull'account e produce un report di cosa non va, mappato su framework riconosciuti (CIS Benchmark, NIST, GDPR, PCI-DSS, e MITRE ATT&CK). E il tool difensivo che risponde alla domanda "quanto e sicuro il mio account cloud?" con una lista concreta e prioritizzata di correzioni.

A differenza degli scanner offensivi (Pacu), che cercano una via di attacco specifica, Prowler adotta una visione ampia e sistematica: verifica ogni servizio contro le best practice, dai bucket pubblici alle policy IAM permissive, dal logging disabilitato alla cifratura mancante. E il ciclo audit, hardening applicato al cloud, con Prowler come metro di misura oggettivo - l'equivalente cloud di Lynis/kube-bench.

---

## Utilizzo

```Bash
# Audit completo di un account AWS contro il CIS Benchmark
prowler aws --compliance cis_2.0_aws
```

```
FAIL  iam_root_mfa_enabled           Root account senza MFA          <-- critico
FAIL  s3_bucket_public_access        Bucket 'data' pubblico          <-- (correlato CLOUD-002)
FAIL  iam_policy_no_admin_priv       Policy con privilegi admin
PASS  cloudtrail_enabled             CloudTrail attivo

== 142 PASS, 23 FAIL, 8 WARN -> report HTML/JSON generato
```

```Bash
# Prowler supporta anche Azure e GCP
prowler azure
prowler gcp
```

---

## Quando usarlo nel flusso

- **Audit periodico dell'account:** eseguirlo regolarmente per misurare e mantenere la postura di sicurezza
- **Prima di un incidente:** chiudere le FAIL prioritarie (root senza MFA, bucket pubblici, IAM admin) rende l'account resiliente ai leak di credenziali
- **Compliance:** la mappatura su CIS/NIST/GDPR produce l'evidenza di conformita richiesta in contesti regolamentati
- **Complementare a Pacu:** Prowler trova sistematicamente cio che Pacu sfrutterebbe puntualmente

---

## Tool correlati

| tool | ruolo | relazione |
| :--- | :--- | :--- |
| `Prowler` | audit/compliance | questo strumento (difensivo) |
| `ScoutSuite` | audit multi-cloud | vista d'insieme complementare (`../scoutsuite/`) |
| `Pacu` | exploitation | la controparte offensiva (`../pacu/`) |
| `Trivy` | container/iac scan | copre container e iac, non l'account cloud |

> **Tool moderno consigliato:** `Prowler` per l'audit approfondito e la compliance (mappatura su framework), `ScoutSuite` per la vista d'insieme rapida. I due sono complementari: Prowler per la profondita e l'evidenza di conformita, ScoutSuite per la panoramica multi-cloud.

---

## Mappatura MITRE ATT&CK

| tattica (prevenuta) | tecnica | id mitre | ruolo del controllo |
| :--- | :--- | :--- | :--- |
| privilege escalation | valid accounts: cloud accounts | `T1078.004` | rileva le policy iam che permettono privesc |
| collection | data from cloud storage | `T1530` | rileva i bucket pubblici/non cifrati |
| defense evasion | impair defenses | `T1562` | rileva logging/monitoring disabilitato |

| contromisura difensiva (d3fend) | id d3fend | applicazione |
| :--- | :--- | :--- |
| configuration inventory | `D3-CI` | inventario e verifica della configurazione cloud |
| platform hardening | `D3-PH` | hardening guidato dai controlli di conformita |

---

> **Nota:** Prowler e un tool difensivo non intrusivo, da eseguire su account di proprieta o con autorizzazione. Documentato a scopo educativo e di difesa in contesto autorizzato.
