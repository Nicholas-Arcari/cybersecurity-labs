> [English](README.en.md) | **Italiano**

# BloodHound: mappatura dei percorsi di attacco nel dominio

> - **Fase:** Discovery (dominio Active Directory)
> - **Visibilita:** Media - la raccolta genera numerose query LDAP e, con la raccolta delle sessioni, connessioni SMB verso molti host; pattern rilevabile come enumerazione di massa
> - **Prerequisiti:** un account di dominio valido (anche a basso privilegio); connettivita verso DC (LDAP 389/636) e, per la raccolta sessioni, verso gli host membri (SMB 445)
> - **Tecnica:** `BloodHound / SharpHound` | **Severity tipica:** `Informativo` | **Finding ID:** da assegnare in lab (metodologia)

- Natura del documento: metodologia. Output illustrativi, non da lab specifico.
- Obiettivo: raccogliere la struttura del dominio e calcolare i percorsi piu brevi verso obiettivi ad alto valore (Domain Admins), trasformando un insieme di oggetti AD in un grafo navigabile di relazioni sfruttabili.

---

## Executive summary

BloodHound e lo strumento che ha cambiato il modo di attaccare Active Directory, spostando l'enumerazione da
liste statiche a un grafo di relazioni. Un collector (SharpHound su Windows, bloodhound-python su Linux)
raccoglie da LDAP e dalle sessioni attive gli oggetti del dominio (utenti, gruppi, computer, GPO, ACL,
deleghe, trust) e li importa in un database a grafo. BloodHound calcola poi i percorsi piu brevi tra un
punto di partenza (l'account compromesso) e un obiettivo (es. Domain Admins), evidenziando catene di abuso
che a occhio nudo sarebbero invisibili (es. "l'utente A puo resettare la password di B, che e in un gruppo
con GenericAll su C, che e Domain Admin").

Per l'attaccante e il punto di partenza dopo il primo accesso: invece di tentare tecniche a caso, segue i
percorsi che il grafo indica. Per il difensore e altrettanto prezioso: gli stessi percorsi rivelano dove
l'ereditarieta di permessi e le deleghe hanno creato scorciatoie non intenzionali verso il dominio.

## Contesto operativo (perche, prima del come)

Dopo aver ottenuto un primo account di dominio, la domanda non e "quale exploit uso" ma "dove posso
arrivare da qui". BloodHound risponde con un grafo. La raccolta va calibrata sulla OPSEC: la raccolta base
(LDAP) e relativamente discreta; la raccolta delle sessioni utente (chi e loggato dove) richiede di
interrogare molti host via SMB ed e piu rumorosa. Un operatore attento sceglie i metodi di raccolta in base
al livello di rumore accettabile.

## Esecuzione / comandi

### Raccolta da Linux (bloodhound-python)

```bash
# Raccolta remota con credenziali di dominio; -c All include sessioni e ACL
bloodhound-python -u utente -p 'Password123' -d corp.local -ns 10.10.10.10 -c All
```

### Raccolta da Windows (SharpHound)

```
# Collector nativo; genera un archivio ZIP da importare in BloodHound
SharpHound.exe -c All
```

Output illustrativo (rappresentativo):

```
INFO: Found 312 users, 74 groups, 41 computers
INFO: Compressing data to 20260101_bloodhound.zip   <-- archivio da importare nella GUI
```

### Analisi nel grafo

Nella GUI di BloodHound si importano gli ZIP e si usano le query predefinite, ad esempio "Shortest Path to
Domain Admins" o "Find Principals with DCSync Rights". I percorsi evidenziati diventano il piano di
escalation.

## Analisi dei risultati

Il valore non e la lista degli oggetti ma le relazioni: un percorso che collega l'account corrente a Domain
Admins attraverso tre abusi concatenati e un piano d'attacco pronto. In un lab reale il finding andrebbe
classificato in base a cosa il grafo rivela: la semplice mappa e `Informativo`, ma l'esistenza di un
percorso breve e diretto verso Domain Admins da un utente a basso privilegio e di fatto un finding di
severity piu alta, da documentare nella tecnica specifica che il percorso sfrutta.

### Analisi teorica

BloodHound modella il dominio come grafo diretto in cui i nodi sono i principal e gli archi sono le
relazioni di controllo (MemberOf, GenericAll, WriteDacl, AddKeyCredentialLink, AllowedToDelegate, HasSession,
...). Il problema "posso diventare Domain Admin da qui" si riduce a un problema di raggiungibilita nel grafo.
Questa riduzione e cio che rende visibili le catene di abuso: nessuna singola relazione e di per se una
vulnerabilita, ma la loro composizione lo e. E l'applicazione pratica del principio per cui la sicurezza di
AD e una proprieta dell'intero grafo delle autorizzazioni, non dei singoli oggetti.

## Remediation (blue team)

**Rilevamento (SOC/SIEM).**
- Volume anomalo di query LDAP da un singolo account in breve tempo.
- Enumerazione di sessioni: connessioni SMB verso un gran numero di host da un unico host in sequenza rapida.
- Honeypot: account/oggetti esca il cui accesso in enumerazione genera alert.

**Hardening.**
- Eseguire periodicamente BloodHound come blue team per individuare e rimuovere i percorsi di attacco
  (deleghe e ACL non necessarie) prima che lo faccia un attaccante.
- Applicare il Tiering Model e il minimo privilegio per accorciare o eliminare i percorsi verso i Tier 0.
- Limitare l'enumerazione: ridurre le informazioni leggibili da utenti a basso privilegio dove possibile.

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `bloodhound-python` | python collector | cli - attivo | raccolta remota del grafo da linux con credenziali |
| `SharpHound` | .net collector | cli - attivo | raccolta da host windows nel dominio |
| `BloodHound` / `BloodHound CE` | graph analysis | gui | analisi dei percorsi di attacco, query predefinite |
| `NetExec` (`nxc`) | ad/smb toolkit | cli - attivo | raccolta e enumerazione complementare |
| `AzureHound` | collector | cli - attivo | estensione del grafo a entra id / azure |

## Note di metodologia

In lab reale (es. GOAD) il finding da documentare sarebbe l'esistenza e la lunghezza del percorso piu breve
verso Domain Admins dall'account iniziale, e quali relazioni (archi) lo compongono. Questi esiti guidano le
tecniche delle altre sotto-aree.

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| discovery | account discovery: domain account | `T1087.002` | enumerazione di utenti e computer del dominio via ldap. |
| discovery | permission groups discovery: domain groups | `T1069.002` | enumerazione di gruppi e appartenenze. |
| discovery | domain trust discovery | `T1482` | mappatura di trust e relazioni tra domini/foreste. |
| discovery | system network connections discovery | `T1049` | raccolta delle sessioni utente attive sugli host. |

## Correlazioni con altri moduli

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| primo accesso di dominio | bloodhound | fornisce la mappa dei percorsi per scegliere la tecnica di escalation |
| bloodhound | [acl abuse](<../../04-delegation-acl/acl-abuse/README.md>), [rbcd](<../../04-delegation-acl/rbcd/README.md>), [dcsync](<../../05-credential-dumping/dcsync/README.md>) | i percorsi individuati indicano quale abuso concatenare |

---

> **Nota:** Contenuto didattico e di metodologia. Esecuzione solo in laboratori propri o con autorizzazione esplicita. Output illustrativi, non da sistemi reali.
