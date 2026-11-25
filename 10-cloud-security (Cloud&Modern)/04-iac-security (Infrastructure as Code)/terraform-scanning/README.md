> [English](README.en.md) | **Italiano**

# Terraform Scanning - Analisi Statica dell'Infrastructure as Code

> - **Fase:** Cloud Security - IaC Static Analysis (Defense)
> - **Categoria:** Difensivo - analisi statica della configurazione prima del deploy
> - **Prerequisiti:** Codice IaC (Terraform, CloudFormation); scanner (Checkov, tfsec, Trivy); integrazione CI/CD
> - **Output:** Finding CLOUD-010; misconfigurazioni individuate prima del deploy; blocco delle infrastrutture insicure alla build

- **Ambiente Operativo:** Repository IaC, CI/CD, Checkov/tfsec
- **Tool principali:** Checkov, tfsec, Trivy, Terrascan

---

## Executive Summary

Oggi l'infrastruttura si scrive come codice (Infrastructure as Code): un file Terraform descrive server, reti, storage e permessi, e il deploy li crea automaticamente. Questo porta enormi vantaggi (riproducibilita, versionamento, revisione) ma anche un rischio speculare: un errore nel codice diventa un errore nell'infrastruttura, replicato ovunque quel codice viene applicato. Una regola firewall sbagliata scritta una volta si deploya su ogni ambiente.

L'analisi statica dell'IaC individua queste misconfigurazioni **prima** del deploy, leggendo il codice e confrontandolo con regole di sicurezza note. Il finding CLOUD-010 documenta l'uso di Checkov e tfsec: scanner che analizzano il Terraform e segnalano gli errori classici - "hai lasciato la porta 22 (SSH) aperta a tutto Internet", "questo bucket S3 e pubblico", "questo database non e cifrato". E lo shift-left applicato all'infrastruttura: trovare l'errore nel codice, dove costa una modifica di una riga, invece che in produzione, dove costa un incidente.

Il valore e preventivo e si integra in CI/CD: una scansione a ogni modifica del Terraform blocca il deploy delle infrastrutture insicure, rendendo la sicurezza un cancello automatico della pipeline invece di una revisione manuale fallibile.

---

## Struttura della cartella

```
terraform-scanning/
+-- README.md      # questo file: analisi statica IaC (Checkov, tfsec) (CLOUD-010)
+-- img/           # report Checkov e integrazione CI/CD
```

---

## Analisi Statica con Checkov e tfsec

**ID Finding:** `CLOUD-010` | **Severity:** `Medio` (rilevamento preventivo di misconfigurazioni nell'IaC prima del deploy; la severita reale dipende dalle misconfig trovate)

### Contesto operativo

Checkov e tfsec leggono il codice Terraform (senza applicarlo) e lo valutano contro centinaia di policy di sicurezza. Individuano risorse mal configurate - accessi troppo aperti, mancanza di cifratura, logging disabilitato - e indicano la riga e la correzione. E analisi statica: trova l'errore nel codice, non nell'infrastruttura deployata.

### PoC - Scansione del Terraform (Checkov)

```Bash
# Checkov analizza il codice Terraform contro le policy di sicurezza
checkov -d terraform/
```

```
Check: CKV_AWS_24: "Ensure no security groups allow ingress from 0.0.0.0:0 to port 22"
  FAILED for resource: aws_security_group.web
  File: /terraform/main.tf:12-20
    | ingress { from_port = 22, cidr_blocks = ["0.0.0.0/0"] }   <-- SSH aperto a Internet (CLOUD-010)

Check: CKV_AWS_18: "Ensure S3 bucket has access logging enabled"
  FAILED for resource: aws_s3_bucket.data
```

### PoC - Il codice problematico

```HCL
# main.tf - ANTIPATTERN: SSH aperto al mondo
resource "aws_security_group" "web" {
  ingress {
    from_port   = 22
    to_port     = 22
    cidr_blocks = ["0.0.0.0/0"]     # <-- chiunque su Internet puo raggiungere SSH
  }
}
```

### PoC - tfsec (alternativa) e integrazione CI/CD

```Bash
# tfsec: scanner alternativo, output focalizzato sulla sicurezza
tfsec terraform/

# In pipeline: blocca il merge/deploy se ci sono FAIL ad alta severita
checkov -d terraform/ --hard-fail-on HIGH
```

```
[!] exit code non-zero: misconfig HIGH presenti -> deploy bloccato   <-- infra insicura impedita (CLOUD-010)
```

### Operativita Difensiva

- **Shift-left in CI/CD:** integrare Checkov/tfsec come cancello della pipeline; nessun Terraform con misconfig ad alta severita viene applicato
- **Baseline e soft/hard fail:** definire quali check bloccano (hard-fail) e quali avvisano (soft-fail); tarare sul contesto per evitare il rumore
- **Correzione guidata:** ogni finding indica la policy e la correzione; Checkov puo generare le patch per alcune risorse
- **Copertura ampia:** questi scanner coprono AWS, Azure, GCP, Kubernetes manifest e Dockerfile; un unico controllo per l'IaC eterogeneo. Complementare alla scoperta di segreti (`../secrets-management/`)

---

## Esperienza di Laboratorio

Il valore di Checkov e stato rendere visibili errori che nel codice sembravano innocui. Un blocco `ingress` con `cidr_blocks = ["0.0.0.0/0"]` e sintatticamente corretto e funziona perfettamente - deploya un security group che espone SSH al mondo intero. Nulla nel codice segnala il pericolo; solo lo scanner, confrontandolo con la policy CKV_AWS_24, lo evidenzia. Questo ha reso concreto che la correttezza sintattica non e sicurezza: il codice giusto puo descrivere un'infrastruttura sbagliata.

La lezione sulla replicazione dell'errore e stata la piu importante. Nell'infrastruttura tradizionale, una regola firewall sbagliata e un errore su un server; nell'IaC, e un errore nel codice che si replica su ogni ambiente dove il Terraform viene applicato - dev, staging, produzione. L'IaC amplifica sia le buone pratiche sia gli errori. Questo rende l'analisi statica non un optional ma una necessita: l'errore va colto nel codice, prima che si moltiplichi nell'infrastruttura.

L'integrazione in CI/CD ha completato il quadro dello shift-left, coerente con l'image scanning (`../../02-containers-security/image-scanning/`). Lo stesso principio - controllo automatico alla build, blocco dei difetti prima del deploy - applicato all'infrastruttura invece che ai container. Ho notato la simmetria dell'intero approccio "modern": la sicurezza si sposta a sinistra, dentro la pipeline, diventando un cancello automatico invece di una revisione umana. E il modello che rende la sicurezza scalabile quanto l'automazione che protegge.

---

## Analisi Teorica: Shift-Left e l'Infrastruttura come Codice Verificabile

L'Infrastructure as Code ha una proprieta di sicurezza preziosa: rende l'infrastruttura verificabile prima di esistere. L'infrastruttura tradizionale si ispeziona dopo il deploy (scanning attivo, audit di configurazione); l'IaC si ispeziona come codice, prima del deploy, in modo statico. Questo anticipa il controllo al momento piu economico - prima che l'infrastruttura sia creata, quando correggere e modificare una riga - realizzando lo shift-left: spostare la sicurezza il piu a monte possibile nel ciclo di vita.

Il fondamento e un'economia della correzione identica a quella dell'image scanning. Una misconfigurazione trovata nel codice costa una modifica; la stessa in produzione costa un'esposizione, potenzialmente un incidente. Poiche l'IaC replica il codice su ogni ambiente, il costo di un errore non colto si moltiplica per il numero di deploy. Anticipare il controllo non solo riduce il costo unitario della correzione, ma previene la moltiplicazione dell'errore - un doppio risparmio che rende l'analisi statica dell'IaC particolarmente vantaggiosa.

Questo colloca la sicurezza dentro il processo di sviluppo, non accanto ad esso. L'analisi statica dell'IaC, come lo scanning delle immagini e dei segreti, appartiene alla pipeline: e un cancello automatico attraversato da ogni modifica, non una revisione periodica esterna. E il modello di sicurezza dell'infrastruttura moderna - "policy as code" che verifica "infrastructure as code" - dove la difesa e automatizzata e integrata quanto cio che protegge. La sicurezza scala solo se e codice anch'essa.

---

## Tool di riferimento

| Tool | Tipo | Ruolo | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Checkov` | IaC scanner | Difensivo | Analisi statica Terraform/CloudFormation/K8s (standard) |
| `tfsec` | Terraform scanner | Difensivo | Analisi statica focalizzata su Terraform |
| `Trivy` | Multi-scanner | Difensivo | Scansione IaC + immagini + segreti (unificato) |
| `Terrascan` | IaC scanner | Difensivo | Analisi statica con policy OPA |
| `OPA/Conftest` | Policy engine | Difensivo | Policy custom "as code" sull'IaC |

> **Tool moderno consigliato:** `Checkov` (Bridgecrew) come standard per l'ampiezza (Terraform, CloudFormation, Kubernetes, Dockerfile), integrabile in ogni CI/CD. `tfsec` come alternativa focalizzata su Terraform. `Trivy` unifica IaC, immagini (`../../02-containers-security/image-scanning/`) e segreti in un unico scanner.

---

## Mappatura MITRE ATT&CK

> Tecniche d'attacco **prevenute** individuando le misconfig nell'IaC prima del deploy.

| Tattica (prevenuta) | Tecnica | ID MITRE | Ruolo del controllo |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Rilevamento di servizi esposti (es. SSH a 0.0.0.0/0) (CLOUD-010) |
| Initial Access | External Remote Services | `T1133` | Prevenzione di accessi remoti troppo aperti nell'IaC |
| Collection | Data from Cloud Storage | `T1530` | Rilevamento di bucket pubblici/non cifrati nel codice |
| Defense Evasion | Impair Defenses | `T1562` | Rilevamento di logging/monitoring disabilitato nell'IaC |

| Contromisura difensiva (D3FEND) | ID D3FEND | Applicazione |
| :--- | :--- | :--- |
| Configuration Inventory | `D3-CI` | Analisi statica della configurazione infrastrutturale |
| Platform Hardening | `D3-PH` | Correzione delle misconfig prima del deploy |

---

> **Nota:** Tutte le attivita documentate sono state condotte su codice IaC e ambienti di laboratorio di proprieta dell'autore. L'analisi statica dell'IaC e un controllo difensivo non intrusivo. Le tecniche sono documentate a scopo educativo e di difesa in contesto autorizzato.
