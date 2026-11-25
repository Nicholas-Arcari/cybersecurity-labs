> [English](README.en.md) | **Italiano**

# Secrets management - segreti hardcoded e HashiCorp vault

> - **Fase:** Cloud Security - Secrets Management (IaC & Supply Chain)
> - **Categoria:** Offensivo (scoperta) + Difensivo (gestione con Vault)
> - **Prerequisiti:** Codice/IaC/repository da analizzare; scanner di segreti (gitleaks/trufflehog); per la soluzione, HashiCorp Vault
> - **Output:** Finding CLOUD-009; segreti hardcoded individuati; architettura di secrets management che li elimina alla radice

- **Ambiente Operativo:** Repository di codice/IaC, CI/CD, HashiCorp Vault (lab)
- **Tool principali:** gitleaks, trufflehog, HashiCorp Vault

---

## Executive summary

I segreti hardcoded sono una delle vulnerabilita piu diffuse e persistenti nell'infrastruttura moderna: chiavi API, password di database, token cloud scritti direttamente nel codice, nei file di configurazione o nell'Infrastructure as Code (Terraform). Il problema e aggravato dal versionamento: un segreto committato in git resta nella storia del repository anche se rimosso in un commit successivo, e chiunque acceda al repo (o a un suo fork/clone) puo recuperarlo. E lo stesso vettore visto in `01-recon` (code secret leakage) e in `07-post-exploitation` (credenziali nei file), qui affrontato dal punto di vista della gestione.

Il finding CLOUD-009 documenta due facce del problema. La scoperta: scanner come gitleaks e trufflehog trovano i segreti nel codice e nella storia git - lo stesso che farebbe un attaccante. La soluzione: HashiCorp Vault, che elimina i segreti hardcoded alla radice fornendo un archivio centralizzato e, soprattutto, **segreti dinamici** a vita breve, generati su richiesta e revocati automaticamente. Con Vault, il codice non contiene segreti ma solo il riferimento per richiederli a runtime.

Il principio e che i segreti non devono mai vivere nel codice. Il codice descrive la logica; i segreti sono dati sensibili che vanno gestiti da un sistema dedicato, con controllo d'accesso, rotazione e audit - responsabilita che un file di testo in un repository non puo assolvere.

---

## Struttura della cartella

```
secrets-management/
+-- README.md      # questo file: segreti hardcoded + Vault (CLOUD-009)
+-- img/           # scansione gitleaks e flusso Vault
```

---

## Scoperta dei segreti e gestione con vault

**ID Finding:** `CLOUD-009` | **Severity:** `Alto` (segreti hardcoded esposti nel codice/storia git; credenziali direttamente utilizzabili da chiunque acceda al repository)

### Contesto operativo

Il primo passo, sia per l'attaccante che per il difensore, e scoprire i segreti. gitleaks e trufflehog scansionano il codice e - fondamentale - l'intera storia git, dove i segreti "rimossi" sopravvivono. La soluzione difensiva non e solo rimuoverli ma cambiare architettura: spostare i segreti in Vault e referenziarli a runtime.

### PoC - scoperta dei segreti (gitleaks)

```Bash
# Scansione del repository e della sua intera storia git
gitleaks detect --source . --report-format json
```

```
Finding:     AWS Access Key
File:        terraform/main.tf
Secret:      AKIA...EXAMPLE
Commit:      a3f9c1  (3 mesi fa, "rimosso" nel commit successivo)   <-- ancora nella storia (CLOUD-009)
Rule:        aws-access-token
```

### PoC - il problema: segreto hardcoded in IaC

```HCL
# terraform/main.tf - ANTIPATTERN: segreto in chiaro nel codice
resource "aws_db_instance" "prod" {
  username = "admin"
  password = "SuperSecret123!"          # <-- hardcoded, finisce in git e nello state
}
```

### PoC - la soluzione: segreti dinamici con vault

```Bash
# Vault genera credenziali di database dinamiche, a vita breve, su richiesta
vault read database/creds/prod-role
```

```
Key                Value
lease_duration     1h                    <-- credenziale valida 1 ora, poi revocata
username           v-token-prod-x7f2...   <-- utente generato al volo, non hardcoded
password           A1b2-dynamic-...       <-- mai scritto nel codice (CLOUD-009 risolto)
```

```HCL
# Il codice ora referenzia Vault, non contiene il segreto
data "vault_database_secret" "db" {
  path = "database/creds/prod-role"      # <-- riferimento, non segreto
}
```

### Remediation

- **Scansione in CI/CD:** gitleaks/trufflehog come pre-commit hook e in pipeline bloccano i segreti prima che entrino in git; lo scanning e il primo controllo
- **Bonifica della storia:** un segreto committato va considerato compromesso e ruotato immediatamente; rimuoverlo dal commit corrente non basta (resta nella storia e va gia considerato trapelato)
- **Vault (o equivalente):** centralizzare i segreti in Vault/AWS Secrets Manager/Azure Key Vault; preferire i segreti dinamici a vita breve, che limitano la finestra di validita di un'eventuale fuga
- **Mai nello state Terraform:** lo state file contiene i valori in chiaro; proteggerlo (backend cifrato, accesso ristretto) e non committarlo mai

---

## Esperienza di laboratorio

La scoperta piu istruttiva e stata la persistenza dei segreti nella storia git. Avevo "rimosso" una chiave da un file e committato la rimozione, credendo il problema risolto; gitleaks l'ha trovata comunque, nel commit precedente. Questo ha reso concreto un principio che avevo incontrato nel modulo di recon: git non dimentica. Un segreto committato e compromesso per sempre, a prescindere dai commit successivi, e l'unica risposta corretta e ruotarlo - non rimuoverlo e sperare.

Vault ha cambiato il mio modello mentale sui segreti. Ero abituato a pensare i segreti come valori statici da nascondere bene; i segreti dinamici di Vault li rendono effimeri per costruzione - una credenziale di database generata al volo, valida un'ora, poi revocata automaticamente. Anche se trapela, la finestra di sfruttamento e minima. Questo sposta la difesa da "nascondi bene il segreto" (fragile) a "il segreto vale cosi poco a lungo che nasconderlo conta meno" (robusto). E la stessa filosofia delle credenziali a vita breve (ruoli STS) vista su AWS.

La riflessione e stata sull'inevitabilita dell'errore umano. Nessuno hardcoda un segreto per malizia; lo si fa per fretta, per fare funzionare qualcosa. La difesa efficace non e chiedere agli sviluppatori di non sbagliare mai (fallira), ma rendere l'errore innocuo (segreti dinamici a vita breve) e intercettabile (scanning in CI/CD). Come per i bucket S3, la sicurezza robusta contiene l'errore invece di pretendere che non accada.

---

## Analisi teorica: il segreto come dato, non come codice

L'errore concettuale alla radice dei segreti hardcoded e trattare un dato sensibile come se fosse codice. Il codice descrive la logica ed e fatto per essere versionato, condiviso, ispezionato; un segreto e un dato riservato che richiede l'opposto - controllo d'accesso, rotazione, audit, riservatezza. Metterli nello stesso file significa applicare al segreto le proprieta del codice (versionato, condiviso, permanente in git), che sono esattamente le sbagliate per un segreto. La separazione tra codice e segreti non e una convenzione ma una necessita derivante dalla loro natura opposta.

I segreti dinamici aggiungono una dimensione temporale alla difesa. Un segreto statico e vulnerabile finche esiste: piu vive, piu opportunita ha di trapelare. Un segreto dinamico a vita breve inverte l'equazione: esiste solo per il tempo necessario e poi cessa di essere valido. Questo riduce la superficie temporale dell'esposizione - non elimina la possibilita di una fuga, ma ne limita drasticamente lo sfruttamento. E l'applicazione ai segreti del principio di minimizzazione: minimo privilegio nel tempo, oltre che nello spazio.

Il legame con il resto del percorso e diretto e ricorrente. I segreti hardcoded sono cio che l'attaccante cerca ovunque: nei repository (recon), nei file di sistema (post-exploitation), nei bucket (cloud), nei container. La gestione centralizzata e dinamica dei segreti e la contromisura trasversale che priva l'attaccante di questo bottino. Ogni modulo del percorso ha mostrato l'attaccante raccogliere credenziali; questo mostra il difensore renderle irraggiungibili e effimere, spezzando il vettore alla fonte.

---

## Scenario reale: proiezione Post-Exploitation

> Prospettiva dell'attaccante e del difensore.

### Prospettiva attaccante (red team)

**Kill Chain proiettata:**

```
[CLOUD-009] gitleaks/trufflehog sul repo pubblico o clonato -> chiave AWS nella storia git
        |
        v
La chiave e ancora valida (segreto statico mai ruotato)
        |
        v
Accesso AWS -> IAM enumeration (CLOUD-001) -> escalation
        |
        v
Compromissione dell'account cloud
```

**Impatto potenziale:** un singolo segreto hardcoded in un repository (specie se pubblico o esposto) e spesso il punto d'ingresso a una compromissione cloud completa. Il pattern "chiave AWS su GitHub, account compromesso in minuti" e documentato ampiamente: bot automatizzati scansionano i repository pubblici in tempo reale cercando esattamente questi segreti. Il collegamento con CLOUD-001 (IAM) e diretto: la chiave trapelata e il punto di partenza dell'escalation.

### Prospettiva difensore (blue team)

**Rilevamento:** scanning continuo dei repository (gitleaks/trufflehog in CI/CD e sui repo esistenti); monitoraggio dell'uso delle credenziali (CloudTrail) per segreti che appaiono usati da contesti anomali.

**IOC:** uso di una credenziale da un IP/geolocalizzazione mai vista; segreti individuati dallo scanning; credenziali di lunga durata mai ruotate.

**Contenimento e hardening:**
- Rotazione immediata di ogni segreto trovato (considerarlo compromesso)
- Vault/Secrets Manager con segreti dinamici a vita breve
- Scanning obbligatorio in CI/CD e pre-commit hook
- State Terraform protetto e mai committato

**Lezione difensiva:** la gestione dei segreti e una difesa trasversale che priva l'attaccante del bottino piu prezioso - le credenziali. Due controlli si combinano: intercettare i segreti prima che entrino in git (scanning) e renderli effimeri quando esistono (Vault dinamico). Insieme trasformano un segreto da vulnerabilita permanente a esposizione contenuta e temporanea.

---

## Tool di riferimento

| tool | tipo | ruolo | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `gitleaks` | secret scanner | difensivo/offensivo | scansione di codice e storia git per segreti |
| `trufflehog` | secret scanner | difensivo/offensivo | scoperta di segreti con verifica di validita |
| `HashiCorp Vault` | secrets manager | difensivo | archivio centralizzato e segreti dinamici |
| `AWS Secrets Manager` | secrets manager | difensivo | gestione segreti nativa aws con rotazione |
| `Azure Key Vault` | secrets manager | difensivo | gestione segreti nativa azure |
| `git-secrets` | pre-commit hook | difensivo | blocco dei segreti prima del commit |

> **Tool moderno consigliato:** `gitleaks`/`trufflehog` per lo scanning (in CI/CD e pre-commit), `HashiCorp Vault` per la gestione centralizzata con segreti dinamici. I secrets manager nativi (AWS/Azure/GCP) sono ottime alternative integrate col provider. Il principio comune: segreti fuori dal codice, a vita breve, con audit.

---

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| credential access | unsecured credentials: credentials in files | `T1552.001` | segreti hardcoded in codice/iac (CLOUD-009) |
| credential access | unsecured credentials: credentials in repositories | `T1552.008` | segreti nella storia git dei repository (CLOUD-009) |
| reconnaissance | search open technical databases / repos | `T1596` | scansione dei repository per segreti esposti |
| privilege escalation | valid accounts: cloud accounts | `T1078.004` | uso del segreto trapelato per accedere al cloud |

| contromisura difensiva (d3fend) | id d3fend | applicazione |
| :--- | :--- | :--- |
| credential rotation | `D3-CR` | rotazione dei segreti compromessi / dinamici a vita breve |
| file analysis | `D3-FA` | scanning del codice e della storia git per segreti |

---

> **Nota:** Tutte le attivita documentate sono state condotte su repository e ambienti di laboratorio di proprieta dell'autore. La scansione di repository di terzi alla ricerca di segreti senza autorizzazione, e l'uso di credenziali trapelate, costituiscono reato. Le tecniche sono documentate a scopo educativo e di difesa/security assessment autorizzato.
