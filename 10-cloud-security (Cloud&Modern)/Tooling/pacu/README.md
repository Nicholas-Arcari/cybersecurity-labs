> [English](README.en.md) | **Italiano**

# Pacu - AWS Exploitation Framework

> - **Fase:** Cloud Security - AWS Exploitation
> - **Categoria:** Offensivo - il framework di post-exploitation per AWS
> - **Prerequisiti:** Credenziali AWS (anche a basso privilegio); Pacu (Rhino Security Labs)
> - **Output:** Enumerazione, privilege escalation e persistenza automatizzate su AWS

- **Tool principale:** Pacu (Rhino Security Labs)

---

## Cos'e e a cosa serve

`Pacu` e spesso definito "il Metasploit per AWS": un framework di exploitation modulare per testare la sicurezza degli ambienti Amazon. Come Metasploit organizza gli exploit in moduli, Pacu organizza le tecniche cloud (enumerazione, privilege escalation, persistenza, esfiltrazione) in moduli richiamabili su un set di credenziali importate.

Il suo valore e automatizzare cio che manualmente richiederebbe decine di chiamate API. Il modulo `iam__privesc_scan`, in particolare, verifica automaticamente le oltre 20 tecniche di privilege escalation IAM documentate da Rhino Security, individuando se una credenziale limitata puo elevarsi ad amministratore. E lo strumento centrale dei finding AWS (`../../01-providers-infrastructure (IaaS & PaaS)/AWS (Amazon Web Services)/`, CLOUD-001).

---

## Utilizzo

```Bash
# Avvio di Pacu e import delle credenziali
pacu
> import_keys svc-deploy               # importa le chiavi AWS compromesse
> run iam__enum_permissions            # enumera i permessi dell'identita
> run iam__privesc_scan                # cerca le vie di privilege escalation
```

```
[iam__privesc_scan] Confirmed path: CreatePolicyVersion -> AdministratorAccess
[iam__privesc_scan] L'identita puo elevarsi a admin   <-- privesc trovata
```

```Bash
# Altri moduli utili
> run s3__download_bucket              # esfiltrazione di bucket accessibili
> run iam__backdoor_users              # persistenza (nuove credenziali)
```

---

## Quando usarlo nel flusso

- **Dopo aver ottenuto una credenziale AWS:** import ed enumerazione automatica dei permessi
- **Ricerca di privilege escalation:** `iam__privesc_scan` come primo controllo su ogni credenziale
- **Simulazione d'attacco per il difensore:** eseguire Pacu sul proprio account rivela le vie di privesc da chiudere (l'equivalente offensivo dell'audit Prowler/ScoutSuite)

---

## Tool correlati

| Tool | Ruolo | Relazione |
| :--- | :--- | :--- |
| `Pacu` | Exploitation AWS | Questo strumento (offensivo) |
| `enumerate-iam` | Permission enum | Recon rapido dei permessi |
| `Prowler` / `ScoutSuite` | Audit difensivo | Trovano le stesse debolezze dal lato difesa |
| `PMapper` | IAM graph | Analisi a grafo delle vie di escalation |

> **Tool moderno consigliato:** `Pacu` e lo standard per l'exploitation AWS. La sua simmetria difensiva sono `Prowler`, `ScoutSuite` e `PMapper`: gli stessi percorsi di privesc che Pacu sfrutta, questi tool li individuano per chiuderli. Usarli insieme copre attacco e difesa.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione |
| :--- | :--- | :--- | :--- |
| Discovery | Cloud Infrastructure Discovery | `T1580` | Enumerazione automatizzata di permessi e risorse |
| Privilege Escalation | Valid Accounts: Cloud Accounts | `T1078.004` | Ricerca e sfruttamento delle vie di privesc IAM |
| Persistence | Account Manipulation: Additional Cloud Credentials | `T1098.001` | Creazione di credenziali di persistenza |
| Collection | Data from Cloud Storage | `T1530` | Esfiltrazione di bucket accessibili |

---

> **Nota:** Pacu va usato esclusivamente su account AWS di proprieta dell'autore o con autorizzazione esplicita di penetration test. L'uso su account di terzi senza permesso costituisce reato e viola i termini AWS. Documentato a scopo educativo e di security assessment autorizzato.
