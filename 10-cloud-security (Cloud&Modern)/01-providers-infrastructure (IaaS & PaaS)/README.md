> [English](README.en.md) | **Italiano**

# 01 - Providers infrastructure (IaaS & PaaS)

> - **Fase:** Cloud Security - Provider IaaS/PaaS (AWS, Azure, GCP)
> - **Categoria:** Offensivo + Difensivo - l'identita come perimetro
> - **Prerequisiti:** Account/tenant/progetto di test sui provider; CLI ufficiali; per l'offensivo, credenziali o risorse compromesse
> - **Output:** Finding CLOUD-001..004; comprensione della superficie d'attacco dei tre provider maggiori e delle contromisure

---

## Introduzione

Questa sezione copre i tre provider cloud dominanti - AWS, Azure, GCP - accomunati da un principio che il modulo rende centrale: **nel cloud, l'identita e il nuovo perimetro**. Non esiste piu un firewall di frontiera; ogni servizio e un endpoint API e l'unico controllo di accesso e l'identita (IAM su AWS, Entra ID su Azure, Service Account su GCP). Chi possiede una credenziale valida e "dentro", e cio che puo fare dipende dai permessi - quasi sempre mal configurati.

Il quadro di riferimento e lo **Shared Responsibility Model**: il provider protegge la sicurezza *del* cloud (hardware, rete fisica, hypervisor), il cliente la sicurezza *nel* cloud (dati, configurazioni, accessi). La stragrande maggioranza delle compromissioni non deriva da bug del provider ma da misconfigurazioni lato cliente - identita sovraprivilegiate, storage esposto, permessi eccessivi.

I tre provider condividono lo stesso pattern d'attacco declinato diversamente:

1. **AWS (CLOUD-001, CLOUD-002):** IAM enumeration e privilege escalation; S3 bucket esposti. Il provider piu diffuso e piu attaccato.

2. **Azure (CLOUD-003):** enumerazione di Entra ID (l'AD cloud, con AzureHound) e abuso delle managed identity via IMDS.

3. **GCP (CLOUD-004):** furto dei token dei service account via metadata service, spesso attraverso un SSRF.

Il filo comune e trasversale: le identita non umane legate alle risorse (IAM role, managed identity, service account) sono comode ma pericolose se sovraprivilegiate, e il loro token e sempre a un passo dal metadata service. Chi impara il pattern su un provider lo ritrova sugli altri.

---

## Struttura della cartella

```
01-providers-infrastructure (IaaS & PaaS)/
+-- README.md                          # questo file: registro CLOUD-001..004
|
+-- AWS (Amazon Web Services)/         # CLOUD-001 (IAM), CLOUD-002 (S3)
+-- Azure/                             # CLOUD-003 (Entra ID + managed identity)
+-- GCP (Google Cloud Platform)/       # CLOUD-004 (metadata SSRF + service account)
```

---

## Flusso operativo consigliato

```
[INPUT] Credenziale compromessa / risorsa compromessa / web app SSRF
         |
         v
[1] Ottenere un'identita
     +-- AWS: credenziale IAM (leak)      -> AWS/IAM-enumeration/
     +-- Azure: managed identity (IMDS)   -> Azure/
     +-- GCP: service account (metadata)  -> GCP/
              |
              v
[2] Enumerare i permessi e cercare l'escalation
     +-- least privilege violato -> via verso admin/owner
              |
              v
[3] Azione sugli obiettivi
     +-- accesso ai dati (storage, DB), persistenza, esfiltrazione
              |
              v
[OUTPUT] Compromissione dell'ambiente -> difesa: least privilege + audit (Tooling/)
```

---

## Tool di riferimento

| tool | provider | tipo | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Pacu` | aws | offensivo | exploitation framework aws |
| `AzureHound` / `MicroBurst` | azure | offensivo | attack path e enumerazione entra id |
| `gcloud` + metadata | gcp | offensivo | furto token service account |
| `ScoutSuite` | multi | difensivo | audit multi-cloud della configurazione |
| `Prowler` | aws/azure/gcp | difensivo | controlli di sicurezza e compliance |

> **Tool moderno consigliato:** `ScoutSuite` per l'audit multi-cloud unificato; per provider, `Pacu` (AWS), `AzureHound` (Azure), `Prowler` (trasversale). Dettaglio in `../Tooling/`.

---

## Registro finding - providers infrastructure

| id | descrizione | severity | sottocartella |
| :--- | :--- | :---: | :--- |
| `CLOUD-001` | aws iam enumeration + privilege escalation ad admin | `Critico` | `AWS/IAM-enumeration/` |
| `CLOUD-002` | aws s3 bucket esposto/misconfigurato: esfiltrazione dati | `Alto` | `AWS/S3-buckets-attacks/` |
| `CLOUD-003` | azure: abuso managed identity (imds) + enumerazione entra id | `Alto` | `Azure/` |
| `CLOUD-004` | gcp: furto token service account via metadata/ssrf | `Alto` | `GCP/` |

---

## Mappatura MITRE ATT&CK - aggregata

> Riferimento: MITRE ATT&CK for Cloud (IaaS).

| tattica | tecnica | id mitre | finding correlato |
| :--- | :--- | :--- | :--- |
| discovery | cloud infrastructure discovery | `T1580` | CLOUD-001, CLOUD-003, CLOUD-004 |
| privilege escalation | valid accounts: cloud accounts | `T1078.004` | CLOUD-001, CLOUD-003, CLOUD-004 |
| credential access | steal application access token | `T1528` | CLOUD-003, CLOUD-004 |
| credential access | unsecured credentials: cloud instance metadata api | `T1552.005` | CLOUD-004 |
| collection | data from cloud storage | `T1530` | CLOUD-002 |
| persistence | account manipulation: additional cloud credentials | `T1098.001` | CLOUD-001 |

---

> **Nota:** Tutte le attivita documentate sono state condotte su account/tenant/progetti di laboratorio di proprieta dell'autore. Il test di sicurezza su ambienti cloud di terzi richiede autorizzazione esplicita e il rispetto dei termini del provider. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
