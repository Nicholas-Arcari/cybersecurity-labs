> [English](README.en.md) | **Italiano**

# Cloud Asset Discovery: Bucket S3, Azure Blob e GCP Storage Esposti

> - **Fase:** Reconnaissance - Infrastructure Intelligence (cloud attack surface)
> - **Visibilita:** Bassa - l'enumerazione dei nomi bucket avviene tramite risoluzione DNS e richieste HTTP verso gli endpoint dei cloud provider (AWS/Azure/GCP), non verso l'infrastruttura del target; alcuni tool interrogano solo database passivi (Zero)
> - **Prerequisiti:** Nome dell'organizzazione, dominio e brand del target, lista di keyword aziendali (da OSINT precedente)
> - **Output:** Bucket di storage cloud esposti, permessi di lettura/scrittura anonimi, contenuti sensibili, finding INTEL-006. Ponte diretto verso `10-cloud-security/`

---

## Introduzione

Le organizzazioni moderne archiviano una quota crescente dei propri dati in storage cloud: bucket AWS S3, Azure Blob Storage, Google Cloud Storage. Questi servizi sono progettati per essere raggiungibili via Internet tramite un URL prevedibile, e la loro sicurezza dipende interamente dalla configurazione dei permessi. Una singola misconfiguration - un bucket impostato come "public" invece che "private" - espone il contenuto a chiunque conosca o indovini il nome del bucket.

La caratteristica che rende questa tecnica potente in fase di ricognizione e la **prevedibilita del naming**. Un bucket S3 e raggiungibile a `https://<nome-bucket>.s3.amazonaws.com`, e il nome del bucket e globalmente unico ma spesso segue convenzioni prevedibili basate sul brand: `targetcorp-backups`, `target-prod-assets`, `target-dev`, `targetcorp-logs`. Un attaccante genera queste permutazioni e verifica quali esistono e quali sono leggibili anonimamente. Nessun accesso all'infrastruttura del target e richiesto: si interrogano solo gli endpoint dei cloud provider.

La severity e `Variabile`: un bucket che espone asset statici pubblici (immagini di un sito) e `Informativo/Medio`, mentre un bucket leggibile che contiene backup di database, PII o segreti e `Critico`. Un bucket **scrivibile** anonimamente e sempre `Critico`, perche permette di alterare i contenuti (es. sostituire un file JavaScript servito agli utenti, tecnica di supply chain).

Questa sezione e il ponte naturale tra la ricognizione (modulo 01) e la sicurezza cloud (modulo 10): l'asset scoperto qui viene analizzato in profondita in `10-cloud-security/01-providers-infrastructure/`.

---

## Struttura della cartella

```
cloud-asset-discovery/
+-- README.md            <- questo file (INTEL-006: storage cloud esposto)
+-- img/                 <- screenshot del lab (cloud_enum, bucket accessibile, grayhatwarfare)
```

---

## Enumerazione dei Bucket di Storage Cloud

**ID Finding:** `INTEL-006` | **Severity:** `Variabile (Medio / Critico)`

### Contesto operativo

L'enumerazione combina due approcci: **generazione di permutazioni** dei nomi bucket basata sul brand del target, e **ricerca su indici passivi** di bucket gia scoperti da terze parti (GrayHatWarfare). Il primo e attivo verso gli endpoint del provider ma invisibile al target; il secondo e completamente passivo.

### Esecuzione con cloud_enum

`cloud_enum` verifica in parallelo l'esistenza di risorse su AWS, Azure e GCP a partire da una keyword:

```Bash
# Enumerazione multi-cloud a partire dal brand del target
cloud_enum -k targetcorp -k target-corp -k target

# Con mutazioni personalizzate (dev, prod, backup, logs, assets...)
cloud_enum -k targetcorp -m mutations.txt
```

Output atteso:

```
[+] AWS S3 Bucket found: targetcorp-assets.s3.amazonaws.com
      -> ACCESS: OPEN (public read)              <-- INTEL-006 (Alto): lettura anonima
[+] AWS S3 Bucket found: targetcorp-backups.s3.amazonaws.com
      -> ACCESS: Protected (403)                 <-- esiste ma non leggibile (naming confermato)
[+] Azure Blob found: targetcorp.blob.core.windows.net
      -> Container 'public' -> OPEN
[+] GCP Bucket found: target-prod.storage.googleapis.com
      -> ACCESS: OPEN                            <-- INTEL-006 (da verificare contenuto)
```

### Verifica del contenuto (bucket leggibile)

Per i bucket AWS con lettura anonima, l'elenco dei contenuti si ottiene senza credenziali:

```Bash
# Listing anonimo del contenuto di un bucket S3 pubblico
aws s3 ls s3://targetcorp-assets --no-sign-request

# Download del contenuto (solo se autorizzato dallo scope)
aws s3 sync s3://targetcorp-assets ./loot --no-sign-request
```

Output atteso:

```
2023-11-02 14:03:22      15234 logo.png
2023-11-02 14:03:25    1048576 database_backup_2023.sql   <-- INTEL-006 (Critico): backup DB esposto
2023-11-02 14:03:28       2048 .env.production            <-- segreti applicativi (vedi OSINT-006)
```

> [Segnaposto screenshot: catturare l'output di cloud_enum con i bucket trovati e il listing del bucket leggibile (con i nomi file sensibili evidenziati e ogni contenuto reale redatto).]

<!-- screenshot placeholder: cloud_enum - bucket esposti (img/cloud-enum-PLACEHOLDER.jpg) -->

### Ricerca passiva su GrayHatWarfare

GrayHatWarfare mantiene un indice ricercabile di centinaia di milioni di file in bucket pubblici gia scoperti:

```
Ricerca web su buckets.grayhatwarfare.com:
  keyword: targetcorp
  keyword: target.com
  filtri: estensione (.sql, .bak, .env, .pem, .key)
```

> **Nota etica critica:** il listing di un bucket pubblico e generalmente considerato accesso a risorsa resa pubblica dal proprietario, ma il **download** di dati sensibili (PII, backup) puo costituire accesso non autorizzato a seconda della giurisdizione e dello scope. In un engagement, il download si concorda esplicitamente; in ricognizione didattica ci si limita a documentare l'esistenza e la leggibilita senza esfiltrare.

---

## Esperienza di Laboratorio

Per operare in sicurezza si e predisposto un lab controllato, creando un bucket S3 di test con permessi public-read e file fittizi, cosi da verificare la capacita di scoperta dello strumento senza toccare dati reali di terzi; l'enumerazione piu ampia e stata limitata a keyword di nostra proprieta o a programmi che autorizzano esplicitamente il cloud recon nello scope. L'esecuzione ha evidenziato la distinzione fondamentale tra bucket esistenti ma protetti (che rispondono 403, confermando solo la validita del naming) e bucket effettivamente aperti (con contenuto elencabile): la maggior parte dei nomi indovinati ricade nel primo caso, e il vero finding e il secondo. Quando e stato individuato contenuto accessibile si e deciso di non scaricare mai file potenzialmente sensibili: l'esposizione e stata documentata annotando nome del bucket, permessi e tipo di file elencati, sufficiente a dimostrare il rischio senza esfiltrare dati. Questa disciplina e la differenza tra un assessment e una violazione.

Punti di attenzione tipici:

- Un bucket che risponde `403 Forbidden` non e un fallimento: conferma che il nome esiste (il naming aziendale e corretto) e va annotato come asset protetto. Un `404` indica che il nome non esiste.
- I nomi bucket sono globalmente unici su AWS: se `targetcorp-backups` esiste ma e protetto, un attaccante non puo crearne uno omonimo, ma la conferma del pattern di naming guida ulteriori permutazioni (`targetcorp-backups-2`, `targetcorp-db-backups`).
- La qualita del risultato dipende dalla wordlist di mutazioni: includere termini come `backup`, `bak`, `prod`, `dev`, `staging`, `logs`, `assets`, `static`, `data`, `dump`, `private`.

### Analisi Teorica

Il modello di sicurezza dello storage cloud e basato su permessi espliciti (ACL e bucket policy), non sul segreto del nome. Il naming globalmente unico e prevedibile e una scelta di design che privilegia l'accessibilita, sotto l'assunto che il controllo di accesso sia configurato correttamente. La misconfiguration nasce quando questa assunzione viene violata: un bucket creato "public" per servire asset statici finisce per contenere anche dati sensibili, oppure una policy troppo permissiva (`"Principal": "*"`) concede lettura a chiunque.

Questa e una manifestazione del modello di **responsabilita condivisa** del cloud: il provider garantisce la sicurezza *dell'* infrastruttura (il servizio S3 e sicuro), ma la sicurezza *nell'* infrastruttura (la configurazione dei permessi del bucket) e responsabilita del cliente. La maggior parte dei data leak cloud documentati non deriva da una vulnerabilita del provider ma da una misconfiguration del cliente. Il collegamento operativo con `10-cloud-security/01-providers-infrastructure/S3-buckets-attacks/` e diretto: la ricognizione trova il bucket, il modulo cloud ne analizza policy e impatto.

---

## Flusso operativo consigliato

```
[INPUT] Brand, dominio e keyword del target
          |
          v
[1] Ricerca passiva su indici pre-esistenti
     +-- GrayHatWarfare (buckets.grayhatwarfare.com)   -> bucket gia noti
          |
          v
[2] Enumerazione per permutazione (multi-cloud)
     +-- cloud_enum -k <brand>                         -> AWS/Azure/GCP in parallelo
     +-- mutazioni: backup, prod, dev, logs, assets
     -> bucket esistenti (open / 403 protected)
          |
          v
[3] Verifica leggibilita e contenuto
     +-- aws s3 ls s3://<bucket> --no-sign-request     -> listing anonimo
     -> classificazione: Informativo (asset pubblici) / Critico (PII, backup, segreti)
          |
          v
[4] Documentazione senza esfiltrazione
     +-- registrare esistenza, permessi e tipo di dato esposto
          |
          v
[OUTPUT] Asset cloud esposti -> 10-cloud-security/01-providers-infrastructure/S3-buckets-attacks/
```

---

## Scenario Reale: Proiezione Post-Reconnaissance

> Questa sezione descrive come INTEL-006 si inserirebbe in un engagement reale.

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** un bucket S3 dell'organizzazione con lettura anonima abilitata, contenente un backup di database e un file `.env.production`.

**Passo successivo immediato:** download del `.env` per estrarre credenziali applicative e chiavi API, e del backup del database per l'accesso ai dati e ad hash di password da craccare offline.

**Kill Chain proiettata:**

```
INTEL-006: bucket S3 pubblico (backup DB + .env)
        |
        v
Estrazione credenziali da .env + hash da backup DB
        |
        v
Password cracking offline (04-system-exploitation/05-password-cracking)
        |
        v
Accesso ad applicazioni/cloud con credenziali valide (10-cloud-security)
        |
        v
Esfiltrazione dati / movimento laterale nel cloud
```

**Impatto potenziale:** l'esposizione di un bucket con dati sensibili e una delle cause piu comuni di data breach di massa (casi documentati: Accenture, Verizon, US Voter Records - tutti bucket S3 pubblici). Un singolo bucket puo esporre milioni di record senza alcuna tecnica di exploitation.

**Vettori di monetizzazione tipici:**
- Vendita dei dati esfiltrati (PII, database clienti) sul dark web
- Ransomware "leakware": minaccia di pubblicare i dati gia esfiltrati
- Supply chain: se il bucket e scrivibile, alterazione di file serviti agli utenti (JS/asset)

### Prospettiva Difensore (Blue Team)

**Rilevamento:** l'accesso anonimo a un bucket S3 e registrato in S3 Server Access Logs e CloudTrail (se abilitati). Un picco di richieste `GetObject`/`ListBucket` da IP esterni sconosciuti indica esfiltrazione in corso. AWS offre inoltre alert nativi (S3 Block Public Access, Access Analyzer) che segnalano i bucket pubblici.

**Indicatori di Compromissione (IOC):**
- Richieste `ListBucket`/`GetObject` anonime (`Requester: anonymous`) nei log S3
- Volume di download anomalo da un bucket verso IP esterni
- Alert di AWS Access Analyzer o GuardDuty su bucket con accesso pubblico

**Contenimento:** applicare immediatamente S3 Block Public Access a livello di account, revocare la bucket policy permissiva, ruotare tutti i segreti eventualmente contenuti nei file esposti.

**Eradicazione e hardening:**
- Abilitare S3 Block Public Access a livello di organizzazione (default deny)
- Cifratura server-side obbligatoria e bucket policy con principio del least privilege
- Scansione continua della configurazione con `Prowler`, `ScoutSuite` o AWS Config (vedi `10-cloud-security/Tooling/`)
- Separare fisicamente i bucket di asset pubblici da quelli con dati sensibili

**Lezione difensiva:** nel cloud, il perimetro non e la rete ma la configurazione dei permessi. Un bucket pubblico e esposto a Internet intero nel momento stesso della misconfiguration, senza bisogno che l'attaccante "entri" da nessuna parte. La prevenzione e il default "private" applicato a livello di account.

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `cloud_enum` | Cloud recon | CLI (Python) | Enumerazione multi-cloud (AWS/Azure/GCP) per keyword |
| `GrayHatWarfare` | Cloud recon | Web | Ricerca passiva su indice di bucket gia scoperti |
| `awscli` | Cloud interaction | CLI | Listing/download anonimo di bucket S3 (`--no-sign-request`) |
| `S3Scanner` | Cloud recon | CLI | Enumerazione e test permessi bucket S3 |
| `Prowler` | Cloud audit | CLI | Audit difensivo della configurazione (vedi modulo 10) |
| `ScoutSuite` | Cloud audit | CLI | Assessment multi-cloud della postura (vedi modulo 10) |

> **Tool moderno consigliato:** `cloud_enum` copre i tre principali provider in un unico passaggio ed e attivamente mantenuto. Per un target esclusivamente AWS, `S3Scanner scan -f bucket_names.txt` verifica in bulk esistenza e permessi (READ/WRITE) dei bucket. Sul lato difensivo, `Prowler` (`prowler aws`) identifica proattivamente tutti i bucket pubblici dell'account prima che lo faccia un attaccante.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Search Open Technical Databases | `T1596` | Ricerca di bucket cloud esposti su indici pubblici (GrayHatWarfare) e per permutazione dei nomi (INTEL-006) |
| Reconnaissance | Gather Victim Host Info | `T1592` | Identificazione degli asset di storage cloud di proprieta del target (INTEL-006) |
| Collection | Data from Cloud Storage | `T1530` | Enumerazione e accesso anonimo ai contenuti di bucket cloud con permessi pubblici (INTEL-006) |
| Credential Access | Unsecured Credentials: Credentials In Files | `T1552.001` | Estrazione di credenziali e segreti da file (.env, backup) contenuti nei bucket esposti (INTEL-006) |

---

> **Nota:** L'enumerazione degli asset cloud documentata in questa sezione e stata eseguita a scopo didattico su bucket propri di test o su target che autorizzano esplicitamente il cloud recon nello scope. E stata documentata unicamente l'esistenza e la leggibilita dei bucket, senza esfiltrare dati sensibili di terze parti. Nel contesto di un engagement reale, il download di contenuti va concordato nello scope e l'eventuale esposizione va gestita secondo il principio di Responsible Disclosure.
