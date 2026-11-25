> [English](README.en.md) | **Italiano**

# 11.5 - Dump di credenziali di dominio

> - **Fase:** Credential Access - estrazione dei segreti del dominio
> - **Prerequisiti:** variabili per tecnica; DCSync richiede i diritti di replica (Domain Admin, Enterprise Admin o un account con delega esplicita)
> - **Natura:** metodologia (output illustrativi; Finding ID `AD-NNN` da assegnare in lab)

## Introduzione

Il dump delle credenziali di dominio e l'obiettivo che segna la compromissione totale: ottenere gli hash
di tutti gli account, incluso `krbtgt`, apre a Pass-the-Hash, Silver/Golden Ticket e persistenza duratura.
Questa sotto-area raccoglie le tecniche che estraggono questi segreti senza eseguire codice sul Domain
Controller. I fondamenti (protocollo di replica MS-DRSR) sono in
[THEORETICAL-FOUNDATIONS](<../THEORETICAL-FOUNDATIONS.md>) (sezione 3.3).

## Struttura della cartella

| Sottocartella | Tecnica | Severity tipica | Stato |
| :--- | :--- | :---: | :--- |
| `dcsync/` | DCSync (replica abusata per estrarre gli hash) | `Critico` | Scritta |
| `shadow-credentials/` | Shadow Credentials (msDS-KeyCredentialLink) | `Alto` | Scritta |
| `secretsdump-ntds/` | Dump NTDS.dit da DC compromesso o backup | `Critico` | Scritta |

## Flusso operativo consigliato

1. Verificare i diritti di replica sull'oggetto dominio (chi puo fare DCSync oltre agli admin).
2. Eseguire [DCSync](<dcsync/README.md>) mirato (solo krbtgt e account privilegiati) per ridurre il rumore.
3. Usare gli hash ottenuti per Pass-the-Hash e per forgiare ticket (collegamento a
   [02-kerberos-attacks](<../02-kerberos-attacks/README.md>)).

---

> **Nota:** Contenuto didattico. Esecuzione solo in laboratori propri o con autorizzazione esplicita.
