> [English](README.en.md) | **Italiano**

# 11.4 - Abuso di deleghe Kerberos e ACL

> - **Fase:** Privilege Escalation / Lateral Movement (dominio Active Directory)
> - **Prerequisiti:** variabili per tecnica; in genere il controllo (scrittura) su un oggetto AD o su un attributo specifico, individuato con BloodHound
> - **Natura:** metodologia (output illustrativi; Finding ID `AD-NNN` da assegnare in lab)

## Introduzione

Deleghe Kerberos e ACL sono le due famiglie di misconfigurazione che BloodHound evidenzia piu spesso come
percorsi verso il dominio. Le deleghe (unconstrained, constrained, resource-based) permettono a un account
di agire per conto di altri; se mal configurate, consentono l'impersonazione di utenti privilegiati. Le ACL
mal impostate (GenericAll, WriteDACL, WriteOwner, AddKeyCredentialLink) concedono su oggetti AD diritti che
si traducono in reset di password, aggiunta a gruppi privilegiati o concessione a se stessi dei diritti di
replica. Nessuna di queste e una vulnerabilita di codice: sono abusi di funzionalita legittime.

I fondamenti (deleghe e modello di autorizzazione) sono in
[THEORETICAL-FOUNDATIONS](<../THEORETICAL-FOUNDATIONS.md>).

## Struttura della cartella

| sottocartella | tecnica | severity tipica | stato |
| :--- | :--- | :---: | :--- |
| `rbcd/` | resource-based constrained delegation abuse | `Critico` | scritta |
| `delegation-unconstrained-constrained/` | unconstrained e constrained delegation abuse | `Critico` | scritta |
| `acl-abuse/` | abuso di acl/dacl (genericall, writedacl, writeowner, ...) | `Alto` (fino a `Critico`) | scritta |

## Flusso operativo consigliato

1. Da BloodHound, identificare quale delega o ACL collega l'account corrente a un obiettivo piu privilegiato.
2. Sfruttare la relazione: scrittura dell'attributo di delega ([RBCD](<rbcd/README.md>)), abuso di una delega
   esistente ([unconstrained/constrained](<delegation-unconstrained-constrained/README.md>)), o abuso del
   diritto di ACL ([acl-abuse](<acl-abuse/README.md>)).
3. L'esito e tipicamente l'impersonazione di un account privilegiato o la concessione a se stessi di diritti
   (es. DCSync), che porta alla sotto-area 05.

---

> **Nota:** Contenuto didattico. Esecuzione solo in laboratori propri o con autorizzazione esplicita.
