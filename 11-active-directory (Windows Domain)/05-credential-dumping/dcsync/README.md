> [English](README.en.md) | **Italiano**

# DCSync: estrazione degli hash di dominio tramite replica abusata

> - **Fase:** Credential Access (dominio Active Directory) - capstone verso il dominio completo
> - **Visibilita:** Bassa-Media - nessun codice eseguito sul Domain Controller e nessun file toccato; traccia principale e la richiesta di replica da un principal/host inatteso (Event ID 4662)
> - **Prerequisiti:** un account con i diritti estesi di replica sull'oggetto dominio (Domain Admin, Enterprise Admin, account macchina di un DC, o un account con delega esplicita di tali diritti); connettivita verso un Domain Controller
> - **Tecnica:** `DCSync` | **Severity tipica:** `Critico` | **Finding ID:** da assegnare in lab (pagina in metodologia)

- Natura del documento: metodologia. Output illustrativi e rappresentativi, non da lab specifico; hash di esempio troncati o segnaposto.
- Obiettivo: estrarre gli hash delle password di qualunque account del dominio - incluso `krbtgt` e i Domain Admin - senza eseguire codice sul Domain Controller e senza accedere fisicamente al file NTDS.dit.

---

## Executive Summary

DCSync e la tecnica che segna, in pratica, la compromissione totale del dominio. Sfrutta il protocollo di
replica dei Domain Controller (MS-DRSR): un DC che si aggiunge alla foresta deve ricevere una copia del
database delle identita dagli altri DC, e periodicamente i DC si sincronizzano. DCSync impersona un DC ed
emette una richiesta di replica legittima, chiedendo al DC bersaglio gli attributi di un account, inclusi i
segreti (hash NT, chiavi Kerberos). Il DC risponde credendo di parlare con un altro Domain Controller.

Il punto cruciale e che il DC non verifica se il richiedente sia davvero un DC: verifica solo se l'account
che fa la richiesta possiede i diritti estesi di replica nell'ACL dell'oggetto dominio. Questo rende DCSync
molto piu silenzioso delle alternative storiche (compromettere il DC, copiare NTDS.dit, estrarre offline):
non serve accedere al DC ne lasciare file sospetti. Con l'hash di `krbtgt` ottenuto da DCSync si forgia poi
un Golden Ticket, la persistenza di dominio per eccellenza.

## Contesto operativo (perche, prima del come)

DCSync e il passo che trasforma "privilegi elevati" in "dominio completo". Si arriva a poter eseguire
DCSync in due modi: avendo ottenuto un account gia privilegiato (Domain Admin via escalation, o l'account
macchina di un DC via ESC8), oppure avendo compromesso un account non-admin a cui, per misconfigurazione,
sono stati delegati i diritti di replica (pattern tipico: service account di backup o di sincronizzazione
di AD).

La decisione operativa chiave e la selettivita, per OPSEC: un DCSync completo dell'intero dominio e molto
piu visibile di un DCSync mirato al solo `krbtgt` e a pochi account privilegiati. Un operatore attento
richiede prima solo cio che serve (krbtgt per il Golden Ticket, l'Administrator di dominio), riducendo il
volume di richieste di replica anomale.

## Esecuzione / Comandi

### Fase 1 - Verifica dei diritti di replica

Prima di agire, l'operatore verifica chi possiede i diritti di replica sull'oggetto dominio (per capire se
l'account corrente puo fare DCSync, o quale account prendere di mira).

```bash
# Enumerazione delle ACL del dominio alla ricerca dei diritti di replica (da Linux, con BloodHound/ldap)
# In BloodHound: cercare il privilegio "DCSync" / "GetChanges + GetChangesAll" sugli account
```

Output illustrativo (rappresentativo):

```
svc_backup  ha  DS-Replication-Get-Changes + DS-Replication-Get-Changes-All  sull'oggetto dominio
                                                     <-- account non-admin con diritti di replica delegati: vettore
```

I diritti rilevanti sono tre (vedi [THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.md>), sez. 3.3):
DS-Replication-Get-Changes, DS-Replication-Get-Changes-All, DS-Replication-Get-Changes-In-Filtered-Set.

### Fase 2 - DCSync mirato (OPSEC)

```bash
# secretsdump (Impacket): DCSync del solo krbtgt. -just-dc-user limita la richiesta a un singolo account
secretsdump.py corp.local/svc_backup:'Password123'@10.10.10.10 -just-dc-user krbtgt
```

Output illustrativo (hash troncato, non utilizzabile):

```
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:<NT_HASH_TRONCATO>:::   <-- chiave per il Golden Ticket
```

La porzione `aad3b435b51404eeaad3b435b51404ee` e la costante dell'hash LM vuoto (LM disabilitato nelle
versioni moderne di Windows): e normale e non e un segreto.

### Fase 3 - DCSync completo (se autorizzato dallo scope)

```bash
# Dump di tutti gli account di dominio (piu rumoroso): -just-dc estrae hash NT e chiavi Kerberos
secretsdump.py corp.local/svc_backup:'Password123'@10.10.10.10 -just-dc
```

Da host Windows, l'equivalente con Mimikatz:

```
lsadump::dcsync /domain:corp.local /user:krbtgt
```

## Analisi dei risultati

Il risultato di un DCSync mirato a `krbtgt` non e "una credenziale in piu": e la chiave che firma tutti i
TGT del dominio. Da essa si forgia un Golden Ticket valido per qualunque utente (anche inesistente) con
privilegi arbitrari. Il DCSync completo fornisce invece l'intero materiale credenziale del dominio, da cui
Pass-the-Hash verso qualunque account e cracking offline dei service account.

La severity e `Critico` perche l'esito, in entrambi i casi, e il controllo effettivo e duraturo del
dominio. E importante notare cosa DCSync non richiede: nessun login interattivo sul DC, nessun file copiato,
nessun processo sospetto in esecuzione sul controller. Questo lo rende tanto potente quanto difficile da
rilevare senza monitoraggio specifico della replica.

### Analisi Teorica

DCSync non rompe nulla: abusa del protocollo MS-DRSR esattamente come e progettato (vedi
[THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.md>), sez. 3.3). La violazione e della proprieta
P3 (confinamento dell'autorita): i diritti di replica dovrebbero essere confinati ai Domain Controller, ma
l'ACL dell'oggetto dominio puo concederli - per errore o per prassi - a principal che DC non sono. Il
controllo d'accesso del DC e corretto nel suo riferimento (verifica i diritti nell'ACL), ma l'ACL stessa e
l'anello debole.

La scelta di secretsdump da Linux rispetto a Mimikatz da Windows dipende dal foothold: con credenziali e
una macchina attaccante Linux, Impacket e immediato e non richiede codice sul target; su un host Windows
gia in sessione, Mimikatz sfrutta il contesto corrente. In entrambi i casi la leva e il diritto di replica,
non un difetto crittografico.

## Remediation (Blue Team)

**Rilevamento (SOC/SIEM).**

- Event ID 4662 sul Domain Controller con i GUID dei diritti estesi di replica
  (`1131f6aa-...` e `1131f6ad-...`): una richiesta di questo tipo da un account o host che non e un DC e un
  indicatore ad alta fedelta di DCSync.
- Traffico di replica DRSUAPI (`IDL_DRSGetNCChanges`) proveniente da un IP che non appartiene a un Domain
  Controller noto.
- Correlazione: un account di servizio (es. backup) che improvvisamente effettua richieste di replica.

**Hardening.**

- Rivedere e ridurre i diritti di replica sull'oggetto dominio: solo i DC e gli account strettamente
  necessari devono possederli. Rimuovere deleghe storiche non piu giustificate.
- Adottare un Tiering Model per gli account amministrativi (separazione netta tra account di dominio e
  account di lavoro).
- Monitorare in modo specifico l'Event ID 4662 con i GUID di replica e la replica da sorgenti non-DC.
- In caso di sospetto Golden Ticket, resettare la password di `krbtgt` due volte in sequenza controllata
  (AD mantiene chiave corrente e precedente, quindi un solo reset non invalida i ticket forgiati).

---

## Scenario Reale: Proiezione Post-Exploitation

> Come DCSync si inserirebbe in un engagement reale, dal punto di vista dell'attaccante e del difensore.

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** possesso di un account con diritti di replica (Domain Admin ottenuto via escalation,
account macchina di un DC via ESC8, o service account con delega di replica).

**Passo successivo immediato:** DCSync mirato all'hash di `krbtgt` per predisporre la persistenza.

**Kill Chain proiettata:**

```
Account con diritti di replica
        |
        v
DCSync mirato (krbtgt + Domain Admin) -> hash NT e chiavi Kerberos
        |
        v
Golden Ticket (da krbtgt) -> impersonazione di qualunque utente, privilegi arbitrari
        |
        v
Pass-the-Hash verso qualunque sistema del dominio -> accesso totale
        |
        v
Persistenza: Golden Ticket a lunga validita; eventuale creazione account/backdoor
        |
        v
Esfiltrazione dati / deployment ransomware su tutto il dominio
```

**Impatto potenziale:** compromissione totale e persistente del dominio. Il Golden Ticket derivato e
particolarmente insidioso perche non viene invalidato da un singolo reset di krbtgt.

**Vettori di monetizzazione tipici:**
- Ransomware enterprise con cifratura di massa via GPO/strumenti di gestione.
- Double extortion con esfiltrazione dei dati sensibili del dominio.
- Access brokering del controllo Domain Admin.

### Prospettiva Difensore (Blue Team)

**Rilevamento:** Event ID 4662 con i GUID di replica da principal/host non-DC; replica DRSUAPI da IP non
appartenente ai DC.

**Indicatori di Compromissione (IOC):**
- 4662 con `DS-Replication-Get-Changes-All` richiesto da un account non-DC (es. `svc_backup`).
- Richieste di replica da workstation o da IP attaccante anziche tra DC.
- Comparsa successiva di TGT a validita anomala (sintomo di Golden Ticket).

**Contenimento:** disabilitazione dell'account abusato; isolamento dell'host sorgente; reset di `krbtgt`
due volte; indagine sulle sessioni e sui ticket emessi.

**Eradicazione e hardening:** riduzione dei diritti di replica alle sole entita necessarie; Tiering Model;
monitoraggio continuo dei 4662; revisione periodica delle deleghe sull'oggetto dominio.

**Lezione difensiva:** un diritto potente (la replica) concesso con leggerezza a un account non-DC annulla
la separazione tra "controller" e "resto del dominio". La difesa e la gestione rigorosa delle ACL privilegiate,
non una patch: non c'e nulla da patchare, solo da confinare.

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `secretsdump.py` (Impacket) | Python toolkit | CLI - Attivo | DCSync da Linux (`-just-dc`, `-just-dc-user`), senza codice sul DC |
| `Mimikatz` | Credential tool | CLI - Attivo | `lsadump::dcsync` da host Windows in sessione privilegiata |
| `NetExec` (`nxc`) | AD/SMB toolkit | CLI - Attivo | Modulo `ntdsutil`/`dcsync` e azioni correlate |
| `BloodHound` / `SharpHound` | Graph enum | CLI/GUI - Attivo | Individuare chi possiede i diritti di replica (privilegio "DCSync") |
| `ticketer.py` (Impacket) | Kerberos tool | CLI - Attivo | Forgiatura del Golden Ticket a valle, con l'hash krbtgt ottenuto |

---

## Note di metodologia

In un lab reale (es. GOAD) il finding da documentare comprenderebbe: quale account possiede i diritti di
replica (e se si tratta di una delega non giustificata), l'esito del DCSync mirato vs completo, e la
verifica del rilevamento lato blue team (comparsa dell'Event ID 4662 con i GUID di replica). Questi esiti,
una volta osservati, diventano il finding reale (`AD-NNN`).

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Credential Access | OS Credential Dumping: DCSync | `T1003.006` | Richiesta di replica abusata (MS-DRSR) per estrarre hash e chiavi dal DC. |
| Credential Access | Steal or Forge Kerberos Tickets: Golden Ticket | `T1558.001` | Follow-on: forgiatura del Golden Ticket con l'hash di krbtgt ottenuto. |
| Lateral Movement | Use Alternate Authentication Material: Pass the Hash | `T1550.002` | Follow-on: autenticazione con gli hash NT estratti. |

---

## Correlazioni con altri moduli

| Provenienza | Questa tecnica | Effetto |
| :--- | :--- | :--- |
| [Kerberoasting](<../../02-kerberos-attacks/kerberoasting/README.md>) / [ESC8](<../../03-adcs/esc8-relay-adcs/README.md>) | DCSync | forniscono l'account privilegiato (o le credenziali del DC) con diritti di replica |
| DCSync (hash krbtgt) | Golden Ticket ([02-kerberos-attacks](<../../02-kerberos-attacks/README.md>)) | la chiave di krbtgt abilita la persistenza di dominio |
| DCSync (hash NT) | Pass-the-Hash ([07-post-exploitation](<../../../07-post-exploitation/README.md>)) | gli hash estratti abilitano il movimento laterale senza cracking |

---

> **Nota:** Tutte le tecniche descritte sono a scopo didattico e di documentazione di metodologia. Vanno
> eseguite esclusivamente in laboratori di proprieta o su sistemi con autorizzazione esplicita. Gli output
> sono illustrativi e non provengono da sistemi reali o di terze parti.
