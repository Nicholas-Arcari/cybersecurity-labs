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

| Sottocartella | Tecnica | Severity tipica | Stato |
| :--- | :--- | :---: | :--- |
| `bloodhound/` | Raccolta e analisi del grafo del dominio (BloodHound/SharpHound) | `Informativo` | Scritta |
| `domain-enumeration/` | Enumerazione LDAP/RPC/SMB (ldapsearch, rpcclient, nxc, enum4linux-ng) | `Basso` | Scritta |
| `kerbrute-userenum/` | User enumeration e password spraying via Kerberos | `Variabile (Basso / Alto)` | Scritta |

## Flusso operativo consigliato

1. Se non si hanno credenziali: user enumeration via Kerberos (`kerbrute-userenum/`) per costruire una lista
   di username validi, poi password spraying mirato.
2. Con un account di dominio: raccolta BloodHound (`bloodhound/`) per la mappa completa dei percorsi di
   attacco, in parallelo a enumerazione LDAP/RPC (`domain-enumeration/`) per i dettagli.
3. L'output dell'enumerazione guida la scelta della tecnica offensiva nelle sotto-aree 02-05.

---

> **Nota:** Contenuto didattico. Esecuzione solo in laboratori propri o con autorizzazione esplicita.
