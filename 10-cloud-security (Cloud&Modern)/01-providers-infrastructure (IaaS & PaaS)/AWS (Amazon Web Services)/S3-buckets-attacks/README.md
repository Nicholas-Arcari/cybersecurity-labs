> [English](README.en.md) | **Italiano**

# AWS S3 Bucket Attacks - Storage Esposto e Misconfigurazioni

> - **Fase:** Cloud Security - Data Access (AWS S3)
> - **Visibilita:** Bassa/Media - l'accesso a un bucket pubblico non richiede autenticazione e puo non lasciare tracce lato attaccante; gli accessi autenticati sono in CloudTrail se il data event logging e attivo
> - **Prerequisiti:** Nome del bucket (da OSINT, sottodomini, leak) o credenziali con permessi S3; AWS CLI o accesso HTTP anonimo
> - **Output:** Finding CLOUD-002; accesso in lettura/scrittura a storage mal configurato; esfiltrazione o manomissione di dati

- **Ambiente Operativo:** AWS (bucket di laboratorio dell'autore), AWS CLI, accesso HTTP
- **Tool principali:** aws-cli, cloud_enum, s3scanner

---

## Executive Summary

Amazon S3 (Simple Storage Service) e il servizio di storage a oggetti di AWS, e le sue misconfigurazioni sono tra le cause piu comuni e piu gravi di data breach cloud. Il problema ricorrente e semplice: bucket configurati come pubblici o con ACL troppo permissive, che espongono a chiunque - spesso senza alcuna autenticazione - dati che dovrebbero essere privati. Backup, dump di database, documenti interni, credenziali: la cronaca delle violazioni e piena di "bucket S3 esposto".

Il finding CLOUD-002 documenta due scenari: la scoperta e l'accesso a un bucket pubblico (accessibile via HTTP anonimo o `aws s3 ls --no-sign-request`), e lo sfruttamento di ACL scrivibili che permettono non solo di leggere ma di modificare o caricare contenuti (con implicazioni gravi se il bucket serve contenuti a un sito o a un'applicazione). La radice e sempre una misconfigurazione lato cliente, coerente con lo Shared Responsibility Model: AWS fornisce lo storage sicuro, il cliente lo rende pubblico per errore.

---

## Struttura della cartella

```
S3-buckets-attacks/
+-- README.md      # questo file: bucket esposti e misconfigurazioni (CLOUD-002)
+-- img/           # enumerazione bucket e accesso ai dati
```

---

## Scoperta e Accesso a Bucket Mal Configurati

**ID Finding:** `CLOUD-002` | **Severity:** `Alto` (accesso non autorizzato a storage esposto; esfiltrazione di dati o manomissione di contenuti)

### Contesto operativo

I bucket S3 hanno nomi globalmente univoci e spesso prevedibili (`nomeazienda-backup`, `nomeazienda-assets`, `nomeazienda-logs`). Questo li rende enumerabili: un attaccante genera nomi plausibili e verifica quali esistono e quali sono accessibili. Un bucket pubblico non richiede alcuna credenziale.

### PoC - Enumerazione e accesso anonimo

```Bash
# Verifica di un bucket via HTTP anonimo
curl -s https://nomeazienda-backup.s3.amazonaws.com/ | head

# Elenco del contenuto senza autenticazione (--no-sign-request)
aws s3 ls s3://nomeazienda-backup --no-sign-request
```

```
2026-05-10 02:14:22   4200000  db_dump_2026.sql        <-- dump DB esposto (CLOUD-002)
2026-05-10 02:14:23     18400  employees.csv
2026-05-10 02:14:24    950000  backup_config.tar.gz
```

### PoC - Esfiltrazione dei dati

```Bash
# Download dell'intero bucket pubblico
aws s3 sync s3://nomeazienda-backup ./loot --no-sign-request
```

```
download: s3://nomeazienda-backup/db_dump_2026.sql -> loot/db_dump_2026.sql
[+] 3 file, 5.1 MB esfiltrati senza autenticazione   <-- data breach (CLOUD-002)
```

### PoC - ACL scrivibile (scenario piu grave)

```Bash
# Test di scrittura: se il bucket e world-writable, si puo caricare/sovrascrivere
echo "test" > poc.txt
aws s3 cp poc.txt s3://nomeazienda-assets/poc.txt --no-sign-request
```

```
upload: ./poc.txt -> s3://nomeazienda-assets/poc.txt
[!] Scrittura riuscita: se il bucket serve contenuti web -> defacement/malware injection
```

### PoC - Automazione della scoperta

```Bash
# cloud_enum e s3scanner cercano bucket con permutazioni del nome target
python3 cloud_enum.py -k nomeazienda      # (vedere ../../../Tooling/cloud-enum/)
```

### Remediation

- **Block Public Access:** abilitare "S3 Block Public Access" a livello di account (blocca ogni policy/ACL pubblica, anche future); e il singolo controllo piu efficace
- **Least privilege sui bucket:** rivedere bucket policy e ACL; nessun bucket dovrebbe essere pubblico se non per casi espliciti e controllati (es. sito statico, e comunque in sola lettura)
- **Cifratura e versioning:** cifrare i dati a riposo (SSE); abilitare il versioning per recuperare da manomissioni
- **Rilevamento:** Prowler/ScoutSuite (`../../../Tooling/`) e AWS Config individuano i bucket pubblici; abilitare il logging dei data event su CloudTrail per tracciare gli accessi agli oggetti

---

## Esperienza di Laboratorio

La lezione piu forte e stata la banalita dell'attacco rispetto alla gravita del risultato. Non c'e stato exploit, non c'e stato bypass: un bucket configurato come pubblico e semplicemente accessibile a chiunque ne conosca il nome, con un comando `aws s3 ls`. La sproporzione tra sforzo (minimo) e impatto (un dump di database esfiltrato) spiega perche i bucket esposti restino una delle prime cause di breach: non richiedono un attaccante sofisticato, solo uno attento.

L'enumerazione dei nomi si e rivelata il vero lavoro. Poiche i nomi dei bucket sono globali e spesso seguono convenzioni (`azienda-ambiente-scopo`), generarli e testarli con cloud_enum ha trasformato la ricerca in un attacco a dizionario. Questo ha reso concreto che la "sicurezza per oscurita" del nome non protegge nulla: un nome prevedibile e un nome trovabile.

Il caso della ACL scrivibile e stato il piu istruttivo sul piano dell'impatto. Un bucket pubblico in lettura e un data breach; uno scrivibile e molto peggio - se serve contenuti a un sito o distribuisce software, un attaccante puo iniettare malware o defacciare. La differenza tra `read` e `write` su una singola ACL separa la fuga di dati dalla compromissione attiva.

---

## Analisi Teorica: Il Default Sicuro e l'Errore di Configurazione

I bucket S3 sono privati per default: AWS ha reso sicura la configurazione di partenza. Eppure i breach da bucket esposti abbondano, il che rivela una verita sulla sicurezza delle configurazioni: il rischio non e il default, ma la deviazione dal default. Qualcuno, per far funzionare qualcosa in fretta ("rendilo pubblico cosi l'app lo legge"), disabilita la protezione e non la ripristina. La misconfigurazione e un atto umano, non un difetto tecnico.

Questo illustra la tensione tra funzionalita e sicurezza nel cloud. La facilita con cui si rende pubblico un bucket (un clic, un flag) e la stessa che rende facile l'errore. Il cloud democratizza l'infrastruttura - chiunque puo creare storage - ma trasferisce all'utente la responsabilita di configurarlo in modo sicuro, spesso senza la competenza per farlo. Lo Shared Responsibility Model e chiaro sulla carta ma nella pratica scarica sull'utente decisioni di sicurezza che non sempre sa di prendere.

La contromisura strutturale - "Block Public Access" a livello di account - riflette il principio giusto: rendere la deviazione insicura difficile, non solo il default sicuro. Un default sicuro protegge finche qualcuno non lo cambia; un blocco a livello di account impedisce il cambiamento pericoloso a prescindere. E la differenza tra "sicuro se nessuno sbaglia" e "sicuro anche se qualcuno sbaglia" - e solo il secondo e robusto, perche qualcuno, prima o poi, sbaglia sempre.

---

## Scenario Reale: Proiezione Post-Exploitation

> Prospettiva dell'attaccante e del difensore in un engagement reale.

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** accesso a un bucket S3 esposto contenente dati sensibili (CLOUD-002).

**Kill Chain proiettata:**

```
[CLOUD-002] Bucket pubblico scoperto -> dump DB, config, credenziali esfiltrati
        |
        v
Le config/credenziali nel bucket -> accesso ad altri servizi (DB, API, IAM)
        |
        v
Pivot: credenziali AWS nei file -> IAM enumeration (CLOUD-001)
        |
        v
Data breach completo / escalation nell'account
```

**Impatto potenziale:** un bucket esposto e spesso il punto di ingresso a compromissioni piu ampie, perche contiene frequentemente altre credenziali (file di config, `.env`, chiavi). Il data breach diretto (dati dei clienti, PII) e gia grave di per se - con conseguenze legali (GDPR) e reputazionali - ma il pivot verso altre credenziali trovate nel bucket collega questo finding a CLOUD-001 (IAM) e a una compromissione dell'intero account.

### Prospettiva Difensore (Blue Team)

**Rilevamento:** AWS Config e GuardDuty segnalano i bucket pubblici; il logging dei data event su CloudTrail traccia gli accessi agli oggetti (senza di esso, un accesso anonimo puo essere invisibile).

**Indicatori di Compromissione (IOC):**
- Bucket con ACL/policy pubbliche (audit di configurazione)
- Accessi `GetObject` massivi da IP esterni non riconosciuti (se il data logging e attivo)
- Download dell'intero contenuto di un bucket (pattern di `sync`)

**Contenimento e hardening:**
- "Block Public Access" a livello di account (contromisura primaria)
- Revisione e correzione di tutte le bucket policy/ACL pubbliche
- Cifratura, versioning, e logging dei data event
- Audit continuo con Prowler/AWS Config; rotazione di ogni credenziale trovata nei bucket esposti

**Lezione difensiva:** un bucket pubblico e un breach in attesa di accadere. La contromisura non e "controllare che nessuno renda pubblico un bucket" (fallibile) ma "impedire strutturalmente che un bucket diventi pubblico" (Block Public Access). Nel cloud, la difesa robusta rende l'errore impossibile, non solo sconsigliato.

---

## Tool di riferimento

| Tool | Tipo | Ruolo | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `aws-cli` | Cloud CLI | Ufficiale | Accesso ed enumerazione dei bucket |
| `cloud_enum` | Bucket enum | Offensivo | Scoperta di bucket via permutazioni del nome |
| `s3scanner` | S3 scanner | Offensivo | Test di massa di esistenza e permessi dei bucket |
| `Prowler` | Security scanner | Difensivo | Rilevamento dei bucket pubblici e misconfig |
| `AWS Config` | Compliance | Difensivo | Monitoraggio continuo della conformita dei bucket |

> **Tool moderno consigliato:** offensivamente `cloud_enum` (`../../../Tooling/cloud-enum/`) per la scoperta multi-cloud dei bucket. Difensivamente, `Prowler` e `AWS Config` per il rilevamento continuo, ma la contromisura decisiva resta "S3 Block Public Access" a livello di account.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Collection | Data from Cloud Storage | `T1530` | Accesso ed esfiltrazione di dati da bucket S3 esposto (CLOUD-002) |
| Discovery | Cloud Storage Object Discovery | `T1619` | Enumerazione degli oggetti nel bucket |
| Reconnaissance | Search Open Websites/Domains | `T1593` | Scoperta dei nomi dei bucket via OSINT/permutazione |
| Impact | Data Manipulation | `T1565` | Scrittura/manomissione su bucket con ACL scrivibile |

---

> **Nota:** Tutte le attivita documentate sono state condotte su bucket S3 di laboratorio di proprieta dell'autore. L'accesso a storage cloud di terzi senza autorizzazione costituisce reato (accesso abusivo) e viola i termini del provider, anche quando il bucket e tecnicamente pubblico. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
