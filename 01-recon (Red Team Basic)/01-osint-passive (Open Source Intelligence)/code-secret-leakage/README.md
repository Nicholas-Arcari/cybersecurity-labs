> [English](README.en.md) | **Italiano**

# Secret & Code Leakage: GitHub/GitLab Dorking e Segreti nei Repository Pubblici

> - **Fase:** Reconnaissance - Passive Information Gathering (source code intelligence)
> - **Visibilita:** Zero - ricerca su repository pubblici e indici di terze parti (GitHub search, GitLab, motori di ricerca); nessun contatto con l'infrastruttura del target
> - **Prerequisiti:** Nome dell'organizzazione o dominio target, account GitHub gratuito (per la ricerca autenticata), lista di email/username dei dipendenti (da `email-harvesting/` e `user-enumeration/`)
> - **Output:** Segreti esposti (API key, credenziali, token, chiavi private), configurazioni interne, finding OSINT-006

---

## Introduzione

Il leakage di segreti nei repository di codice pubblici e uno dei vettori di accesso iniziale piu frequenti e sottovalutati nelle violazioni reali. La dinamica e sempre la stessa: uno sviluppatore committa per errore un file di configurazione, una variabile d'ambiente o uno script contenente credenziali, e anche se rimuove il file nel commit successivo, il segreto resta permanentemente nella **storia git** del repository. Chiunque puo recuperarlo con un semplice `git log`.

A differenza di altre tecniche OSINT che producono indizi, il code leakage produce spesso credenziali **direttamente utilizzabili**: una AWS access key valida, un token di database, una password SMTP. Per questo la severity e tipicamente `Alto` o `Critico`: si passa dalla ricognizione all'accesso in un solo salto, senza alcuna fase di exploitation.

La superficie da analizzare e duplice:
- **Repository ufficiali dell'organizzazione:** codice pubblicato intenzionalmente ma con segreti dimenticati.
- **Repository personali dei dipendenti:** uno sviluppatore che porta a casa uno snippet aziendale in un progetto personale pubblico. Questo e il motivo per cui la lista di username raccolta in `user-enumeration/` (OSINT-004) e un prerequisito diretto di questa fase.

Questa tecnica si posiziona nella tattica `Reconnaissance` di MITRE ATT&CK come `Search Open Technical Databases` e alimenta immediatamente `07-post-exploitation/02-credential-dumping/` (le credenziali trovate) e `10-cloud-security/` (le chiavi cloud esposte).

---

## Struttura della cartella

```
code-secret-leakage/
+-- README.md            <- questo file (OSINT-006: segreti nei repository pubblici)
+-- img/                 <- screenshot del lab (GitHub search, output gitleaks/trufflehog)
```

---

## Ricerca Manuale: GitHub/GitLab Dorking

**ID Finding:** `OSINT-006` | **Severity:** `Variabile (Alto / Critico)`

### Contesto operativo

La ricerca su GitHub sfrutta gli operatori avanzati (`org:`, `filename:`, `path:`, `language:`) combinati con pattern tipici dei segreti. E l'equivalente delle Google Dorks (`google-dorks/`, OSINT-003) applicato al codice sorgente. La severity dipende dal segreto trovato: una connection string di test e `Alto`, una chiave AWS di produzione ancora valida e `Critico`.

### Esecuzione

Query da eseguire nella barra di ricerca di GitHub (richiede login), mirate all'organizzazione target:

```
# Segreti generici associati al nome dell'organizzazione o dominio
"target.com" password
"target.com" api_key
org:TargetCorp password

# File di configurazione tipici che contengono segreti
org:TargetCorp filename:.env
org:TargetCorp filename:config.php DB_PASSWORD
org:TargetCorp filename:.npmrc _auth
filename:wp-config.php DB_PASSWORD "target.com"

# Chiavi private e credenziali cloud
org:TargetCorp filename:id_rsa
org:TargetCorp "AKIA"                 # prefisso AWS Access Key ID
org:TargetCorp "-----BEGIN RSA PRIVATE KEY-----"

# Ricerca sui repository personali dei dipendenti (da user-enumeration/)
user:nome-dipendente "target.com"
```

Output atteso (risultato di ricerca GitHub):

```
Showing 3 available code results

TargetCorp/legacy-api  -  config/database.yml
  production:
    adapter: mysql2
    username: root
    password: Pr0dDB_2021!            <-- OSINT-006 (Critico): credenziali DB produzione

TargetCorp/deploy-scripts  -  .env.backup
  AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE   <-- chiave AWS in chiaro
  AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/...  <-- da validare (vedi Ethical Handling)
```

> [Segnaposto screenshot: catturare i risultati della ricerca GitHub sul target (con i segreti oscurati/redatti prima della pubblicazione) e salvarlo in `./img/`.]

<!-- screenshot placeholder: Risultati GitHub Dorking (img/github-dorking-PLACEHOLDER.jpg) -->

> **Nota etica critica:** un segreto trovato NON va mai testato per verificarne la validita accedendo all'infrastruttura del target senza autorizzazione. La validita si dichiara come "potenzialmente attiva" nel report. In un engagement autorizzato, il test si concorda esplicitamente nello scope.

---

## Ricerca Automatizzata: gitleaks e TruffleHog

### Contesto operativo

La ricerca manuale trova i segreti evidenti, ma non scala sulla **storia git** completa di un repository con migliaia di commit. gitleaks e TruffleHog automatizzano la scansione dell'intera history applicando centinaia di regex e, nel caso di TruffleHog, la **verifica attiva** della validita dei segreti (opzionale, da usare solo con autorizzazione).

### Esecuzione con gitleaks

gitleaks scansiona un repository clonato (inclusa tutta la history) o una directory:

```Bash
# Clonare il repository target pubblico
git clone https://github.com/TargetCorp/legacy-api.git
cd legacy-api

# Scansione dell'intera storia git alla ricerca di segreti
gitleaks detect --source . --report-format json --report-path leaks.json -v
```

Output atteso:

```
    Finding:     password: Pr0dDB_2021!
    Secret:      Pr0dDB_2021!
    RuleID:      generic-api-key
    Commit:      a3f9c1e8...                       <-- il segreto e nella history
    File:        config/database.yml
    Author:      dev@target.com
    Date:        2021-03-14T09:22:11Z
    ...
    leaks found: 4                                 <-- OSINT-006
```

### Esecuzione con TruffleHog

TruffleHog puo scansionare direttamente un'organizzazione GitHub e, con `--only-verified`, distinguere i segreti ancora attivi (verifica presso il provider):

```Bash
# Scansione di un intero repository remoto senza clonarlo
trufflehog github --repo=https://github.com/TargetCorp/deploy-scripts

# Scansione di un'intera organizzazione (richiede token GitHub)
trufflehog github --org=TargetCorp --only-verified
```

Output atteso:

```
Found verified result                              <-- segreto CONFERMATO attivo
Detector Type: AWS
Decoder Type: PLAIN
Raw result: AKIAIOSFODNN7EXAMPLE
Repository: https://github.com/TargetCorp/deploy-scripts
Timestamp: 2021-06-02 14:03:55
Line: 12
```

> [Segnaposto screenshot: catturare l'output di gitleaks (report JSON) e di TruffleHog con i risultati verificati, con i segreti redatti.]

### Analisi dei risultati / Finding documentato

La distinzione operativa fondamentale e tra **segreto presente** e **segreto valido**. gitleaks trova pattern che assomigliano a segreti (alto recall, molti falsi positivi); TruffleHog con `--only-verified` conferma quali sono ancora attivi presso il provider. In un report professionale:

- Un segreto trovato ma non testato: `Alto` - "credenziale potenzialmente attiva, richiede rotazione immediata".
- Un segreto verificato come attivo (solo se lo scope autorizza la verifica): `Critico` - accesso diretto disponibile.

---

## Esperienza di Laboratorio

La scansione e stata condotta su repository di nostra proprieta e su target didattici autorizzati, mai su codice di terzi. Il confronto tra i due strumenti e stato istruttivo: gitleaks, basato su pattern ed entropia, produce un numero maggiore di finding grezzi, molti dei quali falsi positivi (stringhe ad alta entropia che non sono segreti reali, come hash o identificativi), mentre TruffleHog, con la sua verifica di validita, ha ridotto sensibilmente il rumore confermando solo un sottoinsieme di credenziali. La scoperta metodologicamente piu significativa e che i segreti piu pericolosi vivono spesso nella history di git e non nel codice attuale: un file rimosso in un commit successivo resta recuperabile, per cui la scansione dell'intera history e non del solo checkout e essenziale. Sul piano etico si e deciso di non testare mai la validita reale dei segreti individuati e di redarli nel report (mostrando solo tipo, posizione e commit), trattando il finding come esposizione da rimediare e non come credenziale da usare.

Approccio consigliato per il lab in ambiente controllato: creare un repository di test contenente segreti fittizi (formato realistico ma non funzionante) e verificare che gitleaks e TruffleHog li rilevino nella history anche dopo la loro rimozione con un commit successivo. Questo dimostra il concetto chiave - "il segreto rimosso resta nella history" - senza esporre credenziali reali.

### Analisi Teorica

git e un sistema di versionamento a snapshot immutabili: ogni commit e un oggetto identificato dal suo hash SHA-1/SHA-256, e la rimozione di un file in un commit successivo crea solo un nuovo snapshot che non contiene il file, ma **non altera** gli snapshot precedenti. Il file eliminato resta raggiungibile con `git show <commit>:<path>` o `git log -p`. Per rimuovere davvero un segreto occorre riscrivere la history (`git filter-repo`, BFG Repo-Cleaner) e forzare il push, operazione che la maggior parte degli sviluppatori non esegue. Questa proprieta strutturale di git e la causa radice per cui un segreto committato deve essere considerato **compromesso in modo permanente** e ruotato, non semplicemente rimosso.

La verifica attiva di TruffleHog sfrutta il fatto che quasi ogni provider offre un endpoint di validazione a basso costo (es. `sts:GetCallerIdentity` per AWS, che conferma se una chiave e valida senza compiere azioni). Questo trasforma una lista di potenziali segreti in una lista di accessi confermati.

---

## Flusso operativo consigliato

```
[INPUT] Nome organizzazione + lista dipendenti (da OSINT-002, OSINT-004)
          |
          v
[1] GitHub/GitLab Dorking manuale
     +-- org:Target filename:.env / "AKIA" / DB_PASSWORD
     +-- user:<dipendente> "target.com"    # repo personali
     -> segreti evidenti nel codice attuale
          |
          v
[2] Scansione automatica della history (gitleaks)
     +-- gitleaks detect --source <repo> -v
     -> segreti nascosti nella storia git (alto recall)
          |
          v
[3] Verifica di validita (TruffleHog --only-verified)
     +-- distingue segreti attivi da falsi positivi
          |
          v
[4] Classificazione e Responsible Disclosure
     +-- Alto (presente) / Critico (verificato attivo)
          |
          v
[OUTPUT] Credenziali -> 07-post-exploitation; chiavi cloud -> 10-cloud-security
```

---

## Scenario Reale: Proiezione Post-Reconnaissance

> Questa sezione descrive come OSINT-006 si inserirebbe in un engagement reale.

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** una AWS access key valida trovata nella history di un repository pubblico di deploy dell'organizzazione.

**Passo successivo immediato:** enumerazione dei permessi della chiave con `aws sts get-caller-identity` e `aws iam get-user`, seguita da mappatura dei servizi accessibili (S3, EC2, IAM).

**Kill Chain proiettata:**

```
OSINT-006: AWS access key valida nella git history
        |
        v
Enumerazione permessi IAM (10-cloud-security/IAM-enumeration)
        |
        v
Accesso a bucket S3 / istanze EC2 / segreti in Secrets Manager
        |
        v
Privilege escalation IAM -> compromissione dell'account cloud
        |
        v
Esfiltrazione dati / deploy ransomware su infrastruttura cloud
```

**Impatto potenziale:** una singola chiave cloud esposta puo portare alla compromissione totale dell'infrastruttura cloud senza toccare la rete perimetrale. Casi documentati (es. Uber 2016, Codecov 2021) mostrano come segreti in repository abbiano causato violazioni multimilionarie.

**Vettori di monetizzazione tipici:**
- Data exfiltration da bucket S3 (PII, backup di database)
- Cryptomining su istanze EC2 avviate con la chiave rubata (costo a carico della vittima)
- Access Broker: rivendita dell'accesso cloud confermato

### Prospettiva Difensore (Blue Team)

**Rilevamento:** l'uso della chiave rubata genera eventi in CloudTrail (AWS) da un IP e una geolocalizzazione anomali. GitHub stesso offre "Secret Scanning" che notifica automaticamente il push di segreti riconosciuti e, per alcuni provider, ne innesca la revoca automatica.

**Indicatori di Compromissione (IOC):**
- Eventi CloudTrail (`GetCallerIdentity`, `ListBuckets`) da IP esterni non aziendali subito dopo il push di un segreto
- Alert di GitHub Secret Scanning sul repository
- Uso di una access key da una nuova regione/user-agent

**Contenimento:** revoca immediata della chiave esposta (IAM, deactivate/delete access key), rotazione di tutte le credenziali correlate, analisi CloudTrail per determinare se e gia stata usata.

**Eradicazione e hardening:**
- Integrare uno scanner di segreti nella pipeline CI/CD e come pre-commit hook (`gitleaks protect`, GitHub Secret Scanning, `pre-commit`)
- Adottare un secret manager (AWS Secrets Manager, HashiCorp Vault) e vietare i segreti nel codice tramite policy
- Usare credenziali a vita breve (STS temporary credentials, OIDC) invece di chiavi statiche
- Formazione sviluppatori: un segreto committato va ruotato, non solo rimosso

**Lezione difensiva:** la prevenzione deve avvenire **prima** del commit (pre-commit hook), perche dopo il push il segreto va considerato compromesso in modo permanente. La history di git non dimentica.

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| GitHub Code Search | Source code intel | Web (autenticato) | Dorking manuale su org e repository dei dipendenti |
| `gitleaks` | Secret scanning | CLI | Scansione della history git con regex, alto recall |
| `TruffleHog` | Secret scanning | CLI | Scansione + verifica attiva della validita dei segreti |
| `GitGraber` | Secret monitoring | CLI (Python) | Monitoraggio in tempo reale di GitHub per keyword |
| `GitHub Secret Scanning` | Secret detection | Web (nativo) | Rilevamento e revoca automatica lato provider (difensivo) |
| `noseyparker` | Secret scanning | CLI | Scanner ad alte prestazioni per grandi volumi di dati |

> **Tool moderno consigliato:** `TruffleHog v3` con l'opzione `--only-verified` e il singolo tool piu efficace per un engagement, perche elimina il rumore dei falsi positivi confermando quali segreti sono realmente attivi presso il provider. Sul lato difensivo, `gitleaks protect --staged` come pre-commit hook blocca i segreti prima che entrino nella history.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Search Open Technical Databases | `T1596` | Ricerca di segreti e configurazioni nei repository di codice pubblici del target (OSINT-006) |
| Reconnaissance | Search Open Websites/Domains: Search Engines | `T1593.002` | Uso degli operatori di ricerca GitHub/GitLab per individuare file di configurazione e credenziali (OSINT-006) |
| Credential Access | Unsecured Credentials: Credentials In Files | `T1552.001` | Estrazione di credenziali, API key e chiavi private dai file esposti nella history git (OSINT-006) |
| Credential Access | Unsecured Credentials: Cloud Instance Metadata / Keys | `T1552.005` | Recupero di chiavi di accesso cloud (AWS/Azure/GCP) esposte nel codice pubblico (OSINT-006) |

---

> **Nota:** Le ricerche di code leakage documentate in questa sezione sono state condotte a scopo didattico su repository propri o autorizzati. Nessun segreto eventualmente identificato e stato utilizzato per accedere a sistemi di terze parti. In un contesto reale, i segreti esposti vanno gestiti secondo il principio di Responsible Disclosure, notificando il proprietario per la rotazione immediata senza mai testarne l'operativita fuori dallo scope autorizzato.
