> [English](README.en.md) | **Italiano**

# 11.1 - Enumerazione del dominio

> - **Fase:** Discovery nel dominio Active Directory - mappatura prima dell'attacco
> - **Prerequisiti:** connettivita verso un Domain Controller; per l'enumerazione autenticata un account di dominio valido (anche a basso privilegio); alcune tecniche funzionano anche con null session
> - **Natura:** metodologia (output illustrativi; Finding ID `AD-NNN` da assegnare in lab)

## Introduzione

In Active Directory l'enumerazione non e un passaggio preliminare trascurabile: e la fase che determina il
successo di tutto il resto. I percorsi di attacco (chi puo cosa su chi) emergono dai dati del dominio, non
da tentativi ciechi. Mappare utenti, gruppi, ACL, sessioni, deleghe e configurazione di AD CS prima di
agire permette di scegliere il vettore a piu basso costo e minor rumore. I fondamenti sono in
[THEORETICAL-FOUNDATIONS](<../THEORETICAL-FOUNDATIONS.md>).

## Struttura della cartella

| sottocartella | tecnica | severity tipica | stato |
| :--- | :--- | :---: | :--- |
| `bloodhound/` | raccolta e analisi del grafo del dominio (bloodhound/sharphound) | `Informativo` | scritta |
| `domain-enumeration/` | enumerazione ldap/rpc/smb (ldapsearch, rpcclient, nxc, enum4linux-ng) | `Basso` | scritta |
| `kerbrute-userenum/` | user enumeration e password spraying via kerberos | `Variabile (Basso / Alto)` | scritta |
| `powerview/` | enumerazione mirata e scriptabile del dominio da windows (powerview) | `Informativo` | scritta |

## Flusso operativo consigliato

1. Se non si hanno credenziali: user enumeration via Kerberos (`kerbrute-userenum/`) per costruire una lista
   di username validi, poi password spraying mirato.
2. Con un account di dominio: raccolta BloodHound (`bloodhound/`) per la mappa completa dei percorsi di
   attacco, in parallelo a enumerazione LDAP/RPC (`domain-enumeration/`) per i dettagli e a query mirate con
   PowerView (`powerview/`) per domande puntuali (ACL, SPN, deleghe, sessioni).
3. L'output dell'enumerazione guida la scelta della tecnica offensiva nelle sotto-aree 02-05.

---

> **Nota:** Contenuto didattico. Esecuzione solo in laboratori propri o con autorizzazione esplicita.
