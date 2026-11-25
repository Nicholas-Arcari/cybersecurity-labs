> [English](README.en.md) | **Italiano**

# AWS (Amazon web services) - sicurezza e attacco

> - **Fase:** Cloud Security - AWS (IaaS & PaaS)
> - **Categoria:** Offensivo + Difensivo - identita e storage al centro
> - **Prerequisiti:** Account AWS di test; AWS CLI; per l'offensivo, credenziali compromesse (leak/SSRF/secret); per il difensivo, accesso in audit
> - **Output:** Finding CLOUD-001..002; comprensione della superficie d'attacco AWS e delle contromisure

---

## Introduzione

AWS e il provider cloud dominante e, di conseguenza, la piattaforma piu attaccata. La sua sicurezza ruota attorno a un principio che questo capitolo rende centrale: **nel cloud, l'identita e il nuovo perimetro**. Non c'e un firewall di frontiera da superare; chi possiede una credenziale valida e "dentro", e cio che puo fare dipende dai permessi IAM. La stragrande maggioranza delle compromissioni AWS non deriva da bug di Amazon ma da configurazioni errate lato cliente - coerentemente con lo **Shared Responsibility Model**, che assegna ad AWS la sicurezza del cloud (hardware, rete, hypervisor) e al cliente la sicurezza nel cloud (dati, accessi, configurazioni).

Il capitolo copre le due superfici d'attacco AWS piu rilevanti:

1. **IAM Enumeration & Privilege Escalation (CLOUD-001):** l'attacco all'identita. Da una credenziale limitata, l'enumerazione dei permessi e la ricerca di una catena di privilege escalation verso privilegi amministrativi. E la porta d'ingresso e il focus difensivo primario (least privilege, boundaries, audit).

2. **S3 Bucket Attacks (CLOUD-002):** l'attacco allo storage. Bucket mal configurati (pubblici o con ACL permissive) che espongono dati sensibili - una delle cause piu comuni di data breach cloud.

I due finding sono collegati: un bucket esposto contiene spesso credenziali che alimentano l'IAM enumeration, e un IAM compromesso da accesso a tutti i bucket. Il pattern reale di breach AWS e quasi sempre una combinazione di misconfigurazioni di identita e di storage.

---

## Struttura della cartella

```
AWS (Amazon Web Services)/
+-- README.md              # questo file: registro CLOUD-001..002, principi AWS
|
+-- IAM-enumeration/       # CLOUD-001: enumerazione permessi + privilege escalation
+-- S3-buckets-attacks/    # CLOUD-002: bucket esposti e misconfigurazioni
```

---

## Flusso operativo consigliato

```
[INPUT] Credenziale AWS compromessa o nome di bucket (OSINT)
         |
         v
[1] Identita (IAM-enumeration/)
     +-- chi sono? cosa posso? -> ricerca via di privesc -> admin (CLOUD-001)
              |
              v
[2] Dati (S3-buckets-attacks/)
     +-- bucket esposti -> esfiltrazione; credenziali nei bucket -> pivot IAM (CLOUD-002)
              |
              v
[3] Consolidamento
     +-- persistenza (nuove chiavi/ruoli), accesso ai datastore, esfiltrazione
              |
              v
[OUTPUT] Compromissione dell'account -> difesa: least privilege + Block Public Access + audit
```

---

## Tool di riferimento

| tool | tipo | ruolo | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `aws-cli` | cloud cli | ufficiale | interazione con le api aws |
| `Pacu` | exploitation framework | offensivo | enum, privesc, persistenza su aws |
| `enumerate-iam` / `cloud_enum` | recon | offensivo | enumerazione permessi e bucket |
| `Prowler` / `ScoutSuite` | audit | difensivo | rilevamento misconfig e vie di privesc |
| `PMapper` | iam graph | difensivo | analisi a grafo delle escalation iam |

> **Tool moderno consigliato:** `Pacu` (offensivo) e `Prowler`/`ScoutSuite` (difensivo) coprono la simmetria attacco/difesa su AWS. Vedere `../../../Tooling/` per il dettaglio di ciascuno.

---

## Registro finding - AWS

| id | descrizione | severity | sottocartella |
| :--- | :--- | :---: | :--- |
| `CLOUD-001` | iam enumeration + privilege escalation da credenziale limitata ad admin | `Critico` | `IAM-enumeration/` |
| `CLOUD-002` | s3 bucket esposto/misconfigurato: esfiltrazione dati o manomissione | `Alto` | `S3-buckets-attacks/` |

---

## Mappatura MITRE ATT&CK - aggregata

> Riferimento: MITRE ATT&CK for Cloud (IaaS).

| tattica | tecnica | id mitre | finding correlato |
| :--- | :--- | :--- | :--- |
| discovery | cloud infrastructure discovery | `T1580` | CLOUD-001 |
| privilege escalation | valid accounts: cloud accounts | `T1078.004` | CLOUD-001 |
| persistence | account manipulation: additional cloud credentials | `T1098.001` | CLOUD-001 |
| collection | data from cloud storage | `T1530` | CLOUD-002 |
| discovery | cloud storage object discovery | `T1619` | CLOUD-002 |

---

> **Nota:** Tutte le attivita documentate sono state condotte su un account AWS di laboratorio di proprieta dell'autore. Il test di sicurezza su account cloud di terzi richiede autorizzazione esplicita e il rispetto dei termini del provider. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
