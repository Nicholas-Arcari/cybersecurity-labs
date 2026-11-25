> [English](README.en.md) | **Italiano**

# Azure - Enumerazione Entra ID e Abuso delle Managed Identity

> - **Fase:** Cloud Security - Azure (IaaS & PaaS)
> - **Visibilita:** Media - le attivita su Entra ID e ARM sono registrate nei log di Azure (Sign-in, Activity, Audit); l'abuso di managed identity via IMDS e piu silenzioso
> - **Prerequisiti:** Credenziali Azure/Entra o accesso a una risorsa con managed identity (es. una VM compromessa); Azure CLI, AzureHound, ROADtools
> - **Output:** Finding CLOUD-003; mappa di Entra ID; token di managed identity; percorso verso privilegi elevati

- **Ambiente Operativo:** Azure (tenant di laboratorio dell'autore), Azure CLI, AzureHound
- **Tool principali:** az cli, AzureHound, ROADtools, MicroBurst

---

## Executive Summary

Azure organizza l'identita attorno a **Entra ID** (l'ex Azure Active Directory), il che rende la sicurezza Azure profondamente legata ai concetti di Active Directory on-premise visti nel modulo 07 - ma trasposti nel cloud. Chi ha familiarita con l'enumerazione AD (utenti, gruppi, ruoli, relazioni) ritrova qui gli stessi principi, con BloodHound che diventa AzureHound per mappare i percorsi di attacco nel tenant.

La superficie d'attacco distintiva di Azure sono le **Managed Identity**: identita gestite automaticamente e assegnate a risorse (VM, App Service, Function) per accedere ad altri servizi senza credenziali hardcoded. Sono una buona pratica di sicurezza, ma se un attaccante compromette la risorsa puo abusarne: interrogando l'**Instance Metadata Service (IMDS)** dalla risorsa, ottiene un token della managed identity e ne eredita i permessi. Il finding CLOUD-003 documenta questo abuso, il vettore Azure equivalente al furto di credenziali del metadata service.

Il principio resta quello comune al cloud: l'identita e il perimetro, e la misconfigurazione dei permessi (managed identity con ruoli eccessivi, Entra ID con relazioni sfruttabili) e la via d'attacco primaria.

---

## Struttura della cartella

```
Azure/
+-- README.md      # questo file: Entra ID enum + managed identity abuse (CLOUD-003)
+-- img/           # AzureHound graph e token IMDS
```

---

## Enumerazione Entra ID e Abuso delle Managed Identity

**ID Finding:** `CLOUD-003` | **Severity:** `Alto` (abuso di managed identity per ereditare privilegi; enumerazione di Entra ID per il percorso d'attacco nel tenant)

### Contesto operativo

Due vettori si combinano. L'enumerazione di Entra ID (con AzureHound) mappa utenti, gruppi, ruoli e relazioni, rivelando i percorsi verso i privilegi elevati - come BloodHound per l'AD on-premise. L'abuso della managed identity parte da una risorsa compromessa: interrogando l'IMDS locale, si ottiene un token con i permessi dell'identita assegnata alla risorsa.

### PoC - Furto del token della Managed Identity (da risorsa compromessa)

```Bash
# Da una VM Azure compromessa: richiesta di un token al metadata service (IMDS)
curl -s -H "Metadata: true" \
  "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/"
```

```
{ "access_token": "eyJ0eXA...", "resource": "https://management.azure.com/" }
                                              <-- token della managed identity (CLOUD-003)
```

### PoC - Uso del token e enumerazione dei permessi

```Bash
# Il token eredita i ruoli della managed identity: enumerazione delle risorse accessibili
az login --identity
az role assignment list --assignee <identity> -o table
```

```
Principal              Role           Scope
vm-managed-identity    Contributor    /subscriptions/.../rg-prod   <-- ruolo eccessivo (CLOUD-003)
# "Contributor" sull'intero resource group = controllo di tutte le risorse
```

### PoC - Mappatura di Entra ID (AzureHound)

```Bash
# AzureHound raccoglie i dati per BloodHound: percorsi di attacco nel tenant
azurehound -u user@tenant --tenant <id> list -o azure-data.json
# Import in BloodHound -> visualizzazione dei percorsi verso Global Admin
```

### Remediation

- **Least privilege sulle managed identity:** assegnare ruoli minimi e con scope ristretto (non "Contributor" sull'intera subscription); una managed identity compromessa non deve dare il controllo dell'ambiente
- **Protezione dell'IMDS:** limitare l'accesso al metadata service dai workload; monitorare le richieste di token anomale
- **Hardening di Entra ID:** MFA, Conditional Access, revisione dei ruoli privilegiati (Global Admin, Privileged Role Admin); PIM (Privileged Identity Management) per l'accesso just-in-time
- **Rilevamento:** audit con ScoutSuite/Prowler (multi-cloud); monitoraggio dei log di sign-in e delle attivita ARM per pattern anomali

---

## Esperienza di Laboratorio

La continuita con il modulo 07 (Active Directory) e stata la chiave di comprensione. Entra ID non e un mondo nuovo ma la trasposizione cloud dell'AD: gli stessi concetti di utenti, gruppi, ruoli e relazioni sfruttabili, con AzureHound che genera per BloodHound gli stessi grafi di attacco. Chi ha imparato a mappare un dominio AD ritrova qui il metodo, adattato alle API di Microsoft Graph e ARM. Questo ha reso l'apprendimento di Azure piu rapido del previsto.

L'abuso della managed identity e stato il concetto piu istruttivo perche mostra un buon controllo di sicurezza usato contro se stesso. Le managed identity esistono per eliminare le credenziali hardcoded - un'ottima pratica. Ma trasferiscono la fiducia alla risorsa: chi compromette la VM eredita l'identita. Interrogare l'IMDS e ottenere un token con ruolo "Contributor" ha reso concreto che la sicurezza della managed identity dipende interamente dallo scope dei suoi permessi. Un'identita gestita ma con privilegi eccessivi e comoda per lo sviluppatore e per l'attaccante.

---

## Analisi Teorica: La Fiducia Trasferita alla Risorsa

Le managed identity risolvono un problema reale (le credenziali hardcoded) spostando la fiducia dall'utente alla risorsa: non e piu "questa persona con questa password", ma "questa VM, per il fatto di essere questa VM". E un modello elegante, ma sposta il rischio invece di eliminarlo. Il segreto non e piu nel codice (dove poteva trapelare), ma la sua sostituzione - l'identita legata alla risorsa - e accessibile a chiunque controlli la risorsa. Si scambia il rischio di leak del segreto con il rischio di compromissione della risorsa.

Questo definisce il principio di difesa: se la fiducia e nella risorsa, lo scope dei permessi della risorsa e tutto. Una managed identity con ruolo minimo e scope ristretto limita il danno di una risorsa compromessa a quel minimo; una con "Contributor" sull'intera subscription trasforma la compromissione di una singola VM nel controllo dell'intero ambiente. Il least privilege non e un dettaglio ma la sola cosa che separa un incidente contenuto da una catastrofe, perche la managed identity elimina il leak del segreto ma non l'ereditarieta dei permessi.

---

## Scenario Reale: Proiezione Post-Exploitation

> Prospettiva dell'attaccante e del difensore.

### Prospettiva Attaccante (Red Team)

**Kill Chain proiettata:**

```
[CLOUD-003] VM compromessa -> IMDS -> token managed identity (Contributor)
        |
        v
Controllo del resource group: accesso a storage, DB, altre VM
        |
        v
AzureHound: percorso da Contributor verso Global Admin nel tenant
        |
        v
Compromissione del tenant Entra ID -> controllo dell'intera organizzazione cloud
```

**Impatto potenziale:** in Azure, la compromissione di Entra ID equivale al controllo dell'intera organizzazione cloud - identita, risorse, dati. Il percorso VM, managed identity, escalation nel tenant e il vettore che AzureHound rende visibile e che un attaccante percorre. L'integrazione ibrida frequente tra Entra ID e AD on-premise puo estendere la compromissione anche all'infrastruttura tradizionale.

### Prospettiva Difensore (Blue Team)

**IOC:** richieste IMDS anomale da workload; uso di token managed identity da contesti inattesi; enumerazione di Entra ID (pattern AzureHound/Graph); assegnazioni di ruolo o sign-in anomali.

**Hardening:** least privilege e scope ristretto sulle managed identity; MFA e Conditional Access; PIM per l'accesso privilegiato just-in-time; audit continuo con ScoutSuite; monitoraggio dei log di sign-in e attivita.

**Lezione difensiva:** le managed identity sono una buona pratica solo se accompagnate dal least privilege. Eliminare le credenziali hardcoded senza limitare i permessi dell'identita sposta il problema, non lo risolve. Nel cloud, ogni identita - umana o gestita - va trattata con il minimo privilegio, perche ognuna e un potenziale punto di escalation.

---

## Tool di riferimento

| Tool | Tipo | Ruolo | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `az cli` | Cloud CLI | Ufficiale | Interazione con le API Azure/ARM |
| `AzureHound` | Attack path mapping | Offensivo | Grafo dei percorsi d'attacco in Entra ID (BloodHound) |
| `ROADtools` | Entra ID recon | Offensivo | Enumerazione e analisi di Entra ID |
| `MicroBurst` | Azure toolkit | Offensivo | Enumerazione servizi, abuso managed identity |
| `ScoutSuite` | Multi-cloud audit | Difensivo | Audit della configurazione Azure |

> **Tool moderno consigliato:** `AzureHound` + BloodHound per i percorsi d'attacco (la continuita con l'AD del modulo 07), `MicroBurst` e `ROADtools` per l'enumerazione. Difensivamente `ScoutSuite` (`../../../Tooling/scoutsuite/`) per l'audit multi-cloud.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Credential Access | Steal Application Access Token | `T1528` | Furto del token della managed identity via IMDS (CLOUD-003) |
| Discovery | Cloud Infrastructure Discovery | `T1580` | Enumerazione di Entra ID e delle risorse (CLOUD-003) |
| Privilege Escalation | Valid Accounts: Cloud Accounts | `T1078.004` | Escalation via ruoli eccessivi della managed identity |
| Discovery | Permission Groups Discovery: Cloud Groups | `T1069.003` | Mappatura di ruoli e gruppi Entra ID (AzureHound) |

---

> **Nota:** Tutte le attivita documentate sono state condotte su un tenant Azure di laboratorio di proprieta dell'autore. Il test di sicurezza su tenant di terzi richiede autorizzazione esplicita e il rispetto dei termini Microsoft. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
