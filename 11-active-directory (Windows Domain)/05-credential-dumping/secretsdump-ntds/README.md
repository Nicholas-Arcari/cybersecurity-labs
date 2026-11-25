> [English](README.en.md) | **Italiano**

# Dump di NTDS.dit: estrazione offline del database di dominio

> - **Fase:** Credential Access (dominio Active Directory)
> - **Visibilita:** Media-Alta su un DC - accesso ai file di sistema / creazione shadow copy / lettura degli hive; piu rumoroso di DCSync perche opera sul DC
> - **Prerequisiti:** privilegi amministrativi su un Domain Controller (o accesso a un backup del System State) per leggere `NTDS.dit` e l'hive `SYSTEM`
> - **Tecnica:** `NTDS.dit dump` | **Severity tipica:** `Critico` | **Finding ID:** da assegnare in lab (metodologia)

- Natura del documento: metodologia. Output illustrativi; hash di esempio troncati.
- Obiettivo: estrarre tutti gli hash del dominio dal database `NTDS.dit`, quando si ha gia accesso amministrativo a un DC o a un suo backup, come alternativa/complemento al DCSync.

---

## Executive summary

`NTDS.dit` e il database di Active Directory sul Domain Controller: contiene tutti gli oggetti del dominio e,
cifrati con la chiave di boot presente nell'hive `SYSTEM`, gli hash delle password di tutti gli account.
Chi ha privilegi amministrativi su un DC (o accesso a un backup del System State) puo estrarre `NTDS.dit` e
`SYSTEM` e ricavarne offline l'intero set di hash. A differenza di DCSync (che abusa della replica da
remoto, senza toccare il DC), il dump di NTDS.dit opera direttamente sul controller ed e quindi piu
rumoroso, ma e la tecnica di riferimento quando si ha gia il controllo del DC o si dispone solo di un backup.

## Contesto operativo (perche, prima del come)

Il dump di NTDS.dit si usa in due situazioni: quando si e gia ottenuto admin su un DC (e si vuole il dump
completo e definitivo), oppure quando si ha accesso a un backup (System State, Veeam, ecc.) ma non al DC
vivo. La decisione tra NTDS.dit dump e DCSync e di OPSEC e contesto: DCSync e piu discreto e remoto, il dump
e piu diretto ma tocca il DC. Sul DC vivo si privilegiano metodi che evitano di scrivere su disco (lettura
diretta via DRSUAPI o shadow copy gestita dal tool).

## Esecuzione / comandi

### Dump remoto con credenziali admin (Impacket)

```bash
# secretsdump con credenziali admin sul DC: estrae gli hash dal DIT (usa DRSUAPI o shadow copy a seconda del caso)
secretsdump.py corp.local/Administrator:'AdminPass'@10.10.10.10
```

### Da backup / file offline

```bash
# Con NTDS.dit e l'hive SYSTEM gia ottenuti (es. da backup), estrazione completamente offline
secretsdump.py -ntds NTDS.dit -system SYSTEM LOCAL
```

Output illustrativo (hash troncati):

```
Administrator:500:aad3b435b51404eeaad3b435b51404ee:<NT_HASH_TRONCATO>:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:<NT_HASH_TRONCATO>:::   <-- krbtgt: chiave per Golden Ticket
svc_sql:1103:aad3b435b51404eeaad3b435b51404ee:<NT_HASH_TRONCATO>:::
```

## Analisi dei risultati

Il dump fornisce l'intero set di hash del dominio, incluso `krbtgt`: e la compromissione totale,
equivalente nell'esito a un DCSync completo. Severity `Critico`. La differenza rispetto a DCSync e il
contesto (richiede admin sul DC o un backup) e la maggiore visibilita. Il materiale ottenuto abilita
Pass-the-Hash verso qualunque account, cracking offline e Golden Ticket.

### Analisi teorica

Gli hash in `NTDS.dit` sono cifrati con il PEK (Password Encryption Key), a sua volta protetto dalla boot
key derivata dall'hive `SYSTEM`. Per questo servono entrambi i file: `NTDS.dit` (i dati) e `SYSTEM` (la
chiave per decifrarli). Non e un bypass crittografico: con privilegi amministrativi sul DC, entrambi gli
elementi sono legittimamente accessibili, e la cifratura at-rest non protegge da un amministratore (o da chi
ne ha i privilegi). E il motivo per cui la protezione dei DC e dei loro backup e critica quanto quella delle
credenziali stesse. Vedi [THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.md>), sez. 3.3.

## Remediation (blue team)

**Rilevamento.** Accesso a `NTDS.dit`/`SYSTEM` o creazione di shadow copy su un DC (Event ID correlati a
VSS, accesso a file di sistema); esecuzione di tool di dump; accessi anomali ai backup del System State.

**Hardening.** Ridurre al minimo gli amministratori di DC (Tiering Model, Tier 0); proteggere e cifrare i
backup del System State con accesso ristretto; monitorare la creazione di shadow copy e l'accesso a
`NTDS.dit`; in caso di compromissione sospetta, considerare il reset di krbtgt (due volte) e una procedura
di bonifica del dominio.

---

## Scenario reale: proiezione Post-Exploitation

> Esito equivalente al dominio completo (severity Critico).

### Prospettiva attaccante (red team)

**Punto di partenza:** admin su un DC, oppure possesso di un backup del System State.

**Passo successivo immediato:** estrarre `NTDS.dit` + `SYSTEM` e ricavare gli hash offline.

**Kill Chain proiettata:**

```
Admin su DC (o backup System State)
        |
        v
Estrazione NTDS.dit + hive SYSTEM
        |
        v
Dump offline di tutti gli hash (incluso krbtgt)
        |
        v
Pass-the-Hash / Golden Ticket -> controllo e persistenza del dominio
        |
        v
Esfiltrazione / ransomware su tutta l'infrastruttura
```

**Impatto potenziale:** compromissione totale del dominio. Il caso del backup e particolarmente insidioso:
un backup mal protetto equivale a consegnare tutte le credenziali del dominio.

**Vettori di monetizzazione tipici:** ransomware, esfiltrazione, access brokering.

### Prospettiva difensore (blue team)

**Rilevamento:** accesso a `NTDS.dit`/shadow copy su DC; esecuzione di secretsdump o equivalenti; accessi ai
backup.

**Indicatori di Compromissione (IOC):** creazione di VSS su DC in contesti inattesi; lettura di `NTDS.dit`
da processi non di sistema; accesso anomalo ai repository di backup.

**Contenimento:** isolamento del DC; reset di krbtgt (due volte) e degli account privilegiati; indagine
sugli accessi ai backup.

**Eradicazione e hardening:** Tier 0 rigoroso; protezione e cifratura dei backup; monitoraggio VSS e accesso
a NTDS.dit.

**Lezione difensiva:** un backup di DC vale quanto il DC stesso. La protezione dei backup del System State e
parte integrante della sicurezza del dominio, non un tema separato dell'IT.

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `secretsdump.py` (impacket) | python toolkit | cli - attivo/offline | dump remoto con credenziali admin o offline da file ntds.dit + system |
| `NetExec` (`nxc`) | ad/smb toolkit | cli - attivo | modulo `ntds` per il dump del dit |
| `ntdsutil` | utility nativa | cli (sul dc) | creazione di una copia del dit (uso legittimo e abuso) |
| `vssadmin` / vss | utility nativa | cli (sul dc) | creazione shadow copy per accedere a ntds.dit in uso |

## Note di metodologia

In lab reale documentare: la via usata (admin su DC vs backup offline), l'estrazione di NTDS.dit + SYSTEM e
il dump risultante; confrontare rumore e tracce rispetto a DCSync. Trattare gli hash estratti come dati
sensibili anche in lab.

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| credential access | os credential dumping: ntds | `T1003.003` | estrazione degli hash dal database ntds.dit del domain controller. |
| credential access | steal or forge kerberos tickets: golden ticket | `T1558.001` | follow-on: uso dell'hash krbtgt estratto per il golden ticket. |
| lateral movement | use alternate authentication material: pass the hash | `T1550.002` | follow-on: autenticazione con gli hash estratti. |

## Correlazioni con altri moduli

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| [dcsync](<../dcsync/README.md>) | ntds.dit dump | due vie allo stesso esito: remota e discreta (dcsync) vs diretta sul dc/backup |
| admin su dc / accesso backup | ntds.dit dump | prerequisito di accesso privilegiato o al system state |
| ntds.dit dump | [golden ticket](<../../02-kerberos-attacks/golden-ticket/README.md>) / [hashcat](<../../../04-system-exploitation/05-password-cracking/hashcat/README.md>) | gli hash abilitano persistenza e cracking offline |

---

> **Nota:** Contenuto didattico e di metodologia. Esecuzione solo in laboratori propri o con autorizzazione esplicita. Output illustrativi, non da sistemi reali.
