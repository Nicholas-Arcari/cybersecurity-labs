> [English](README.en.md) | **Italiano**

# 04 - IaC Security (Infrastructure as Code)

> - **Fase:** Cloud Security - Infrastructure as Code
> - **Categoria:** Difensivo - sicurezza "shift-left" dell'infrastruttura
> - **Prerequisiti:** Codice IaC (Terraform); scanner (Checkov, tfsec, gitleaks); integrazione CI/CD
> - **Output:** Finding CLOUD-009..010; segreti e misconfigurazioni individuati prima del deploy

---

## Introduzione

Oggi le infrastrutture si scrivono come codice: un file Terraform descrive server, reti, storage e permessi, e il deploy li crea automaticamente. L'Infrastructure as Code (IaC) porta riproducibilita, versionamento e revisione, ma introduce un rischio speculare - un errore nel codice diventa un errore nell'infrastruttura, replicato su ogni ambiente dove il codice viene applicato. L'IaC amplifica sia le buone pratiche sia gli errori.

La sicurezza dell'IaC e "shift-left": spostare i controlli il piu a monte possibile, nel codice, prima che l'infrastruttura esista. E il momento piu economico per correggere (una riga invece di un incidente) e l'unico che previene la moltiplicazione dell'errore attraverso i deploy. La sezione copre i due controlli fondamentali:

1. **Secrets Management (CLOUD-009):** i segreti non devono vivere nel codice. Scoperta dei segreti hardcoded (gitleaks/trufflehog, anche nella storia git) e gestione con Vault (segreti dinamici a vita breve). Contromisura trasversale al bottino piu prezioso dell'attaccante.

2. **Terraform Scanning (CLOUD-010):** analisi statica dell'IaC (Checkov, tfsec) che individua le misconfigurazioni prima del deploy - "porta SSH aperta a Internet", "bucket pubblico", "database non cifrato".

Entrambi si integrano in CI/CD come cancelli automatici: nessun segreto entra in git, nessuna infrastruttura insicura viene deployata. E il modello di sicurezza dell'infrastruttura moderna - policy as code che verifica infrastructure as code - dove la difesa e automatizzata quanto cio che protegge.

---

## Struttura della cartella

```
04-iac-security (Infrastructure as Code)/
+-- README.md              # questo file: registro CLOUD-009..010
|
+-- secrets-management/    # CLOUD-009: segreti hardcoded + Vault
+-- terraform-scanning/    # CLOUD-010: analisi statica IaC (Checkov, tfsec)
```

---

## Flusso operativo consigliato

```
[CODICE] IaC scritto (Terraform) + segreti da gestire
         |
         v
[1] Secrets (secrets-management/)
     +-- gitleaks/trufflehog -> nessun segreto in git; Vault -> segreti dinamici (CLOUD-009)
              |
              v
[2] Static analysis (terraform-scanning/)
     +-- Checkov/tfsec -> misconfig individuate e bloccate prima del deploy (CLOUD-010)
              |
              v
[CI/CD] cancelli automatici -> deploy solo se sicuro
              |
              v
[OUTPUT] Infrastruttura senza segreti hardcoded e senza misconfig note
```

---

## Tool di riferimento

| Tool | Tipo | Ruolo | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `gitleaks` / `trufflehog` | Secret scanner | Difensivo | Scoperta segreti in codice e storia git |
| `HashiCorp Vault` | Secrets manager | Difensivo | Archivio centralizzato, segreti dinamici |
| `Checkov` | IaC scanner | Difensivo | Analisi statica multi-piattaforma (standard) |
| `tfsec` | Terraform scanner | Difensivo | Analisi statica focalizzata su Terraform |
| `Trivy` | Multi-scanner | Difensivo | IaC + immagini + segreti unificati |

> **Tool moderno consigliato:** `gitleaks` + `Vault` per i segreti, `Checkov`/`tfsec` per le misconfig, il tutto in CI/CD. `Trivy` come scanner unificato (IaC, immagini, segreti). Il principio comune: shift-left, controlli automatici nella pipeline.

---

## Registro Finding - IaC Security

| ID | Descrizione | Severity | Sottocartella |
| :--- | :--- | :---: | :--- |
| `CLOUD-009` | Segreti hardcoded in codice/IaC/git + gestione con Vault (segreti dinamici) | `Alto` | `secrets-management/` |
| `CLOUD-010` | Terraform scanning: misconfigurazioni IaC individuate prima del deploy | `Medio` | `terraform-scanning/` |

---

## Mappatura MITRE ATT&CK - Aggregata

| Tattica | Tecnica | ID MITRE | Finding Correlato |
| :--- | :--- | :--- | :--- |
| Credential Access | Unsecured Credentials: Credentials In Files | `T1552.001` | CLOUD-009 |
| Credential Access | Unsecured Credentials: Credentials in Repositories | `T1552.008` | CLOUD-009 |
| Initial Access | Exploit Public-Facing Application | `T1190` | CLOUD-010 |
| Initial Access | External Remote Services | `T1133` | CLOUD-010 |
| Privilege Escalation | Valid Accounts: Cloud Accounts | `T1078.004` | CLOUD-009 |

---

> **Nota:** Tutte le attivita documentate sono state condotte su codice e ambienti di laboratorio di proprieta dell'autore. Lo scanning di IaC e segreti e un controllo difensivo; la scansione di repository di terzi senza autorizzazione e l'uso di credenziali trapelate costituiscono reato. Le tecniche sono documentate a scopo educativo e di difesa in contesto autorizzato.
