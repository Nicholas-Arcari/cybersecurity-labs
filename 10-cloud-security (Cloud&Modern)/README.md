> [English](README.en.md) | **Italiano**

# 10 - Cloud security (cloud & modern)

> - **Fase:** Cloud & Modern Infrastructure Security
> - **Categoria:** Offensivo + Difensivo - l'identita e la configurazione come perimetro
> - **Prerequisiti:** Account/tenant/progetti cloud di test; CLI dei provider; Docker/Kubernetes di laboratorio; comprensione dei moduli 01-09 (le tecniche si traspongono nel cloud)
> - **Output:** Finding CLOUD-001..010; comprensione della superficie d'attacco cloud (IaaS/PaaS, container, orchestrazione, IaC) e delle relative difese

---

## Introduzione

Il modulo `10-cloud-security` copre la sicurezza dell'infrastruttura moderna: i provider cloud (AWS, Azure, GCP), i container (Docker), l'orchestrazione (Kubernetes) e l'Infrastructure as Code (Terraform). Il "Modern" nel nome segna il passaggio dal mondo on-premise dei moduli precedenti a quello dove l'infrastruttura e software, effimera e definita da API. E il modulo dove le tecniche di tutto il percorso si traspongono e si trasformano nel contesto cloud.

Un principio domina l'intero modulo: **nel cloud, il perimetro non e piu di rete ma di identita e configurazione**. On-premise ci si difende con firewall e segmentazione; nel cloud, ogni servizio e un endpoint API pubblico e l'unico controllo di accesso e l'identita (IAM, managed identity, service account). La stragrande maggioranza delle compromissioni cloud non deriva da bug dei provider ma da misconfigurazioni lato cliente - identita sovraprivilegiate, storage esposto, container mal configurati, segreti hardcoded. Il quadro e lo **Shared Responsibility Model**: il provider protegge la sicurezza *del* cloud, il cliente la sicurezza *nel* cloud.

Il modulo intreccia costantemente le due prospettive, offensiva e difensiva, mostrando la loro simmetria: gli stessi percorsi che un attaccante sfrutta (Pacu, kube-hunter), un difensore li individua e chiude (Prowler, kube-bench). Padroneggiare entrambe e cio che definisce un security analyst cloud completo.

Le quattro aree del modulo:

1. **Providers Infrastructure (`01-providers-infrastructure/`, CLOUD-001..004):** AWS (IAM privesc, S3), Azure (Entra ID, managed identity), GCP (metadata SSRF, service account). L'identita come perimetro, declinata sui tre provider maggiori.

2. **Containers Security (`02-containers-security/`, CLOUD-005..006):** la supply chain delle immagini (Trivy) e l'isolamento del runtime (container escape). Cosa c'e dentro e quanto e contenuto.

3. **Orchestration (`03-orchestration/`, CLOUD-007..008):** Kubernetes, il sistema operativo del cloud - attacchi al cluster (etcd, API esposti) e hardening (CIS, Pod Security).

4. **IaC Security (`04-iac-security/`, CLOUD-009..010):** l'infrastruttura come codice - gestione dei segreti (Vault) e analisi statica (Checkov). Sicurezza shift-left, dentro la pipeline.

La sezione **Tooling** (`Tooling/`) raccoglie gli strumenti trasversali (Pacu, cloud_enum, Prowler, ScoutSuite) come guida di riferimento.

Il modulo chiude il percorso collegandosi a tutti i precedenti: l'SSRF (03) diventa furto di credenziali cloud, la privilege escalation (04) si traspone su IAM, la persistenza e l'esfiltrazione (07) hanno il loro equivalente cloud, l'hardening e l'audit (08) si applicano a cluster e account, e la gestione dei segreti richiama recon (01) e post-exploitation (07). Il cloud non e un mondo separato: e dove tutte le competenze del percorso convergono e si aggiornano al presente.

---

## Struttura della cartella

```
10-cloud-security (Cloud&Modern)/
+-- README.md                                      <- questo file: registro CLOUD-001..010 + MITRE
|
+-- 01-providers-infrastructure (IaaS & PaaS)/
|   +-- README.md                                  <- registro CLOUD-001..004
|   +-- AWS (Amazon Web Services)/
|   |   +-- IAM-enumeration/                        <- CLOUD-001 (IAM privesc)
|   |   +-- S3-buckets-attacks/                     <- CLOUD-002 (S3 esposto)
|   +-- Azure/                                      <- CLOUD-003 (Entra ID + managed identity)
|   +-- GCP (Google Cloud Platform)/                <- CLOUD-004 (metadata SSRF)
|
+-- 02-containers-security (Docker)/
|   +-- README.md                                  <- registro CLOUD-005..006
|   +-- image-scanning/                             <- CLOUD-005 (Trivy, supply chain)
|   +-- runtime-security/                           <- CLOUD-006 (container escape)
|
+-- 03-orchestration (Kubernetes)/
|   +-- README.md                                  <- registro CLOUD-007..008
|   +-- K8s-attacks/                                <- CLOUD-007 (cluster esposti)
|   +-- K8s-auditing/                               <- CLOUD-008 (kube-bench, Pod Security)
|
+-- 04-iac-security (Infrastructure as Code)/
|   +-- README.md                                  <- registro CLOUD-009..010
|   +-- secrets-management/                         <- CLOUD-009 (segreti + Vault)
|   +-- terraform-scanning/                         <- CLOUD-010 (Checkov, tfsec)
|
+-- Tooling/                                        <- guida ai tool (Pacu, cloud_enum, Prowler, ScoutSuite)
```

---

## Flusso operativo consigliato

```
[INPUT] Ambiente cloud da testare/difendere (account, cluster, IaC)
         |
         v
[1] Recon (Tooling/cloud-enum) -> asset e superficie pubblica
         |
         v
[2] Providers (01) -> identita: IAM/Entra/SA -> privesc (CLOUD-001..004)
         |
         v
[3] Containers (02) -> supply chain (CLOUD-005) + escape (CLOUD-006)
         |
         v
[4] Orchestration (03) -> cluster K8s: attacco (CLOUD-007) e hardening (CLOUD-008)
         |
         v
[5] IaC (04) -> segreti (CLOUD-009) + misconfig (CLOUD-010), shift-left in CI/CD
         |
         v
[DIFESA] audit trasversale (Prowler/ScoutSuite) -> least privilege + hardening
         |
         v
[OUTPUT] Ambiente cloud compreso da entrambi i lati: attaccabile e difendibile
```

---

## Tool di riferimento

| tool | area | prospettiva | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Pacu` | aws | offensivo | exploitation framework (enum, privesc) |
| `AzureHound` / `MicroBurst` | azure | offensivo | attack path e enumerazione entra id |
| `cloud_enum` | multi | recon | scoperta di asset e bucket |
| `Trivy` | container/iac | difensivo | scansione cve e misconfig |
| `Falco` | container/k8s | difensivo | runtime detection (escape, anomalie) |
| `kube-bench` / `kube-hunter` | kubernetes | dif./off. | audit cis / scoperta esposizioni |
| `Checkov` / `gitleaks` | iac | difensivo | analisi statica e scoperta segreti |
| `Prowler` / `ScoutSuite` | multi | difensivo | audit e compliance dell'account |

> **Tool moderno consigliato:** uno stack cloud completo combina `Pacu`/`kube-hunter` (offensivo), `Prowler`/`ScoutSuite`/`kube-bench` (audit difensivo), `Trivy`/`Checkov`/`gitleaks` (shift-left in CI/CD) e `Falco` (runtime detection). Dettaglio in `Tooling/` e nelle rispettive sezioni.

---

## Registro finding - modulo 10

| id | descrizione | severity | sottocartella |
| :--- | :--- | :---: | :--- |
| `CLOUD-001` | aws iam enumeration + privilege escalation ad admin | `Critico` | `01-.../AWS/IAM-enumeration/` |
| `CLOUD-002` | aws s3 bucket esposto/misconfigurato: esfiltrazione dati | `Alto` | `01-.../AWS/S3-buckets-attacks/` |
| `CLOUD-003` | azure: abuso managed identity (imds) + enumerazione entra id | `Alto` | `01-.../Azure/` |
| `CLOUD-004` | gcp: furto token service account via metadata/ssrf | `Alto` | `01-.../GCP/` |
| `CLOUD-005` | container image scanning: cve nelle immagini prima del deploy | `Medio` | `02-.../image-scanning/` |
| `CLOUD-006` | container escape via docker socket: root sull'host | `Critico` | `02-.../runtime-security/` |
| `CLOUD-007` | k8s cluster esposto: furto secret e controllo del control plane | `Critico` | `03-.../K8s-attacks/` |
| `CLOUD-008` | k8s auditing: cis (kube-bench) + pod security standards | `Alto` | `03-.../K8s-auditing/` |
| `CLOUD-009` | segreti hardcoded in codice/iac/git + gestione con vault | `Alto` | `04-.../secrets-management/` |
| `CLOUD-010` | terraform scanning: misconfigurazioni iac prima del deploy | `Medio` | `04-.../terraform-scanning/` |

---

## Mappatura MITRE ATT&CK - aggregata

> Riferimento: MITRE ATT&CK for Cloud (IaaS) e for Containers. Framework difensivo complementare: MITRE D3FEND.

| tattica | tecnica | id mitre | finding correlato |
| :--- | :--- | :--- | :--- |
| discovery | cloud infrastructure discovery | `T1580` | CLOUD-001, CLOUD-003, CLOUD-004 |
| privilege escalation | valid accounts: cloud accounts | `T1078.004` | CLOUD-001, CLOUD-003, CLOUD-004, CLOUD-009 |
| credential access | steal application access token | `T1528` | CLOUD-003, CLOUD-004 |
| credential access | unsecured credentials: cloud instance metadata api | `T1552.005` | CLOUD-004 |
| credential access | unsecured credentials: credentials in files | `T1552.001` | CLOUD-009 |
| credential access | unsecured credentials: credentials in repositories | `T1552.008` | CLOUD-009 |
| credential access | unsecured credentials: container api | `T1552.007` | CLOUD-007, CLOUD-008 |
| collection | data from cloud storage | `T1530` | CLOUD-002 |
| persistence | account manipulation: additional cloud credentials | `T1098.001` | CLOUD-001 |
| initial access | supply chain compromise | `T1195` | CLOUD-005 |
| initial access | exploit public-facing application | `T1190` | CLOUD-007, CLOUD-008, CLOUD-010 |
| privilege escalation | escape to host | `T1611` | CLOUD-006, CLOUD-008 |
| execution | deploy container | `T1610` | CLOUD-006, CLOUD-007 |
| discovery | container and resource discovery | `T1613` | CLOUD-006, CLOUD-007 |

| contromisura difensiva (d3fend) | id d3fend | area |
| :--- | :--- | :--- |
| configuration inventory | `D3-CI` | audit cloud (prowler/scoutsuite), iac (checkov) |
| platform hardening | `D3-PH` | least privilege, kube-bench, hardening iac |
| application vulnerability assessment | `D3-AVA` | image scanning (trivy) |
| mandatory access control | `D3-MAC` | pod security, seccomp/apparmor |
| credential rotation | `D3-CR` | secrets management (vault, segreti dinamici) |

---

> **Nota:** Tutte le attivita documentate in questo modulo sono state condotte su account, tenant, progetti, cluster e ambienti di laboratorio di proprieta dell'autore. Il test di sicurezza su infrastrutture cloud di terzi richiede autorizzazione esplicita e, per alcune attivita, la notifica preventiva al provider (ogni provider ha una propria policy di penetration testing). L'accesso non autorizzato ad ambienti cloud, container e cluster di terzi costituisce reato e viola i termini di servizio. Numerose sezioni documentano con pari enfasi le contromisure difensive (least privilege, hardening, audit, shift-left), coerentemente con l'obiettivo di comprendere l'attacco per rafforzare la difesa. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato con perimetro esplicitamente definito.
