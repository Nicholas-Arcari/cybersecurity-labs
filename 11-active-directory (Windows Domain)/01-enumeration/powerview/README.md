> [English](README.en.md) | **Italiano**

# PowerView - enumerazione di Active Directory da Windows

> - **Fase:** Credential Access / Discovery nel dominio - enumerazione offensiva di AD da un host Windows
> - **Visibilita:** Media - genera query LDAP verso il DC; con PowerShell Script Block Logging (Event ID 4104) le funzioni sono tracciabili
> - **Prerequisiti:** un contesto utente di dominio (anche basso privilegio) su un host Windows nel dominio; PowerView caricato in memoria (modulo di PowerSploit/dev)
> - **Tecnica:** `PowerView (enum AD)` | **Severity tipica:** `Informativo` | **Finding ID:** da assegnare in lab (metodologia)

- Obiettivo: mappare utenti, gruppi, computer, ACL, trust e percorsi di attacco del dominio da un host Windows, complementando [BloodHound](<../bloodhound/README.md>) con query mirate e scriptabili.

---

## Executive summary

PowerView e lo strumento PowerShell di riferimento per l'enumerazione offensiva di Active Directory: interroga
il dominio via LDAP e restituisce oggetti PowerShell filtrabili. Dove BloodHound raccoglie tutto e lo
visualizza come grafo, PowerView e chirurgico e scriptabile: utile per domande mirate ("chi ha diritti su
questo oggetto?", "dove sono local admin?") e per concatenare l'enumerazione con l'azione. E il coltellino
svizzero del lato enumerazione, da caricare in memoria (evita file su disco).

## Esecuzione / comandi

### Enumerazione di base

```powershell
Get-Domain                                   # info sul dominio corrente
Get-DomainController                          # i domain controller
Get-DomainUser -Identity amministratore       # dettagli di un utente
Get-DomainUser -Properties samaccountname,description,memberof   # campi selezionati
Get-DomainGroup "Domain Admins" | Get-DomainGroupMember          # membri di un gruppo privilegiato
Get-DomainComputer -Properties dnshostname,operatingsystem       # i computer del dominio
```

### Percorsi di attacco e sessioni

```powershell
Find-LocalAdminAccess                         # dove l'utente corrente e local admin
Find-DomainUserLocation -UserGroupIdentity "Domain Admins"   # dove sono loggati i DA (user hunting)
Get-NetSession -ComputerName srv01            # sessioni attive su un host
Invoke-UserHunter -CheckAccess                # incrocio: target con DA loggati e accesso
```

### ACL, delega e trust (preludio all'escalation)

```powershell
# ACL sfruttabili: chi puo scrivere su oggetti privilegiati (GenericAll/WriteDACL/WriteOwner)
Get-DomainObjectAcl -Identity "Domain Admins" -ResolveGUIDs | ? {$_.ActiveDirectoryRights -match "GenericAll|WriteDacl|WriteOwner"}
Invoke-ACLScanner -ResolveGUIDs               # scansione ampia di ACL interessanti

Get-DomainUser -SPN                           # account con SPN (candidati Kerberoasting)
Get-DomainUser -PreauthNotRequired            # account senza pre-auth (candidati AS-REP)
Get-DomainComputer -Unconstrained             # delega unconstrained
Get-DomainComputer -TrustedToAuth             # delega constrained
Get-DomainTrust                               # relazioni di trust del dominio/foresta
```

Output illustrativo (rappresentativo):

```
samaccountname : svc_sql
ActiveDirectoryRights : GenericAll        <-- l'utente corrente puo prendere controllo di svc_sql
```

## Analisi dei risultati

PowerView trasforma l'accesso a basso privilegio in una mappa di cio che e attaccabile: SPN per il
[Kerberoasting](<../../02-kerberos-attacks/kerberoasting/README.md>), account senza pre-auth per
[AS-REP](<../../02-kerberos-attacks/as-rep-roasting/README.md>), ACL sfruttabili per l'
[ACL abuse](<../../04-delegation-acl/acl-abuse/README.md>), deleghe per il
[delegation abuse](<../../04-delegation-acl/delegation-unconstrained-constrained/README.md>). La severity propria
e `Informativo` (enumerazione), ma e il passo che abilita le escalation successive.

## Remediation (blue team)

**Rilevamento.** PowerShell Script Block Logging (Event ID 4104) con pattern tipici di PowerView
(`Get-Domain*`, `Invoke-ACLScanner`); volume anomalo di query LDAP da un singolo host; `Find-LocalAdminAccess`
che genera molte connessioni.

**Hardening.** Ridurre l'esposizione delle ACL (modello Tiering); limitare le sessioni dei DA sui workstation;
abilitare logging PowerShell e AMSI; monitorare le query LDAP massive.

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `PowerView` | enum ad (powershell) | cli - attivo | enumerazione mirata e scriptabile del dominio da host windows |
| `BloodHound` / `SharpHound` | graph enum | cli/gui - attivo | raccolta massiva e visualizzazione dei percorsi di attacco |
| `ldapsearch` / `windapsearch` | ldap client | cli - attivo | enumerazione ldap da linux (equivalente cross-platform) |

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| discovery | account discovery: domain account | `T1087.002` | enumerazione di utenti, gruppi e computer del dominio. |
| discovery | permission groups discovery: domain groups | `T1069.002` | enumerazione dell'appartenenza ai gruppi privilegiati. |
| discovery | domain trust discovery | `T1482` | enumerazione delle relazioni di trust. |

---

## Correlazioni con altri moduli

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| accesso di dominio (basso privilegio) | powerview | fornisce il contesto per interrogare il dominio |
| powerview (spn/acl/deleghe) | [02-kerberos-attacks](<../../02-kerberos-attacks/README.md>) / [04-delegation-acl](<../../04-delegation-acl/README.md>) | individua i bersagli delle escalation |
| powerview | [bloodhound](<../bloodhound/README.md>) | complementare: query mirate vs grafo completo |

---

> **Nota:** Contenuto didattico. Esecuzione solo in laboratori propri o con autorizzazione esplicita. Output illustrativi, non da sistemi reali.
