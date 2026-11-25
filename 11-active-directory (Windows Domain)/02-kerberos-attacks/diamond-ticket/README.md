> [English](README.en.md) | **Italiano**

# Diamond Ticket: variante stealth del Golden Ticket

> - **Fase:** Persistence / Privilege Escalation (dominio Active Directory)
> - **Visibilita:** Molto bassa - a differenza del Golden, esiste un AS-REQ/AS-REP reale a registro (Event ID 4768), quindi mancano gli indicatori tipici del ticket forgiato da zero
> - **Prerequisiti:** chiave (hash AES, preferibile al RC4) dell'account `krbtgt` - lo stesso del Golden - e la capacita di ottenere un TGT legittimo (credenziali o sessione di un utente qualunque)
> - **Tecnica:** `Diamond Ticket` | **Severity tipica:** `Critico` | **Finding ID:** da assegnare in lab (metodologia)

- Natura del documento: metodologia. Output illustrativi; chiavi/SID segnaposto. Nessun payload operativo riprodotto.
- Obiettivo: ottenere un TGT reale, modificarne il PAC per aggiungere privilegi (es. Domain Admins) e re-iniettarlo, ottenendo potere dominio-wide con una traccia molto piu simile all'attivita legittima rispetto al Golden Ticket.

---

## Executive Summary

Il Diamond Ticket e l'evoluzione "stealth" del [Golden Ticket](<../golden-ticket/README.md>). Entrambi
richiedono la chiave di `krbtgt`, ma il meccanismo e opposto. Il Golden forgia un TGT **da zero**, offline,
senza mai contattare il KDC: questo lascia un'anomalia rilevabile (un logon Kerberos senza il corrispondente
AS-REQ a registro). Il Diamond invece parte da un **TGT reale**: l'attaccante richiede normalmente un TGT (c'e
quindi un AS-REQ/AS-REP legittimo, Event ID 4768), lo decifra con la chiave di `krbtgt`, ne **modifica il PAC**
(aggiungendo l'appartenenza a gruppi privilegiati), lo **re-cifra e re-firma** con la stessa chiave e lo
re-inietta.

Il risultato e un TGT che a registro nasce come legittimo: l'unica incoerenza e tra il PAC emesso dal KDC e il
PAC presentato nelle richieste successive, una discrepanza molto piu difficile da rilevare dell'assenza di
AS-REQ. E la tecnica di scelta negli ambienti con Microsoft Defender for Identity (MDI), Sentinel o sistemi di
correlazione comportamentale su Kerberos.

## Contesto operativo (perche, prima del come)

Si sceglie il Diamond rispetto al Golden quando l'ambiente ha detection che cercano l'anomalia del Golden (logon
Kerberos senza AS-REQ). Il prerequisito e identico (chiave di `krbtgt`, tipicamente ottenuta via
[DCSync](<../../05-credential-dumping/dcsync/README.md>)), ma in piu serve poter ottenere un TGT reale - basta
una sessione o le credenziali di un utente qualunque, anche non privilegiato. La decisione operativa riguarda la
coerenza del PAC falsificato: strumenti moderni (Rubeus con `/ldap` e `/opsec`) costruiscono il PAC a partire da
attributi reali letti via LDAP e allineano le opzioni del ticket al comportamento nativo di Windows, riducendo
ulteriormente gli indicatori. Come per tutti i ticket, si preferisce AES al RC4, che e di per se un segnale.

## Esecuzione / Comandi

```bash
# (Windows) Rubeus: ottiene un TGT reale, ne modifica il PAC e lo re-inietta
# /ldap costruisce il PAC con attributi reali dall'AD; /opsec allinea i KDCOptions al comportamento nativo
Rubeus.exe diamond /krbkey:<AES256_KRBTGT_SEGNAPOSTO> /ldap /opsec \
  /ticketuser:amministratore /domain:corp.local /dc:dc01.corp.local
```

```bash
# (Linux) Impacket: approccio concettuale equivalente - richiesta di un TGT reale e manipolazione del PAC
ticketer.py -aesKey <AES256_KRBTGT_SEGNAPOSTO> -domain-sid S-1-5-21-<SEGNAPOSTO> \
  -domain corp.local -request -user utente_standard amministratore
```

Output illustrativo (rappresentativo):

```
[*] AS-REQ reale inviato al KDC (Event ID 4768 legittimo a registro)
[*] PAC modificato: aggiunto gruppo Domain Admins (RID 512)
[*] Ticket re-firmato con la chiave di krbtgt e salvato in amministratore.ccache   <-- TGT "diamante"
```

## Analisi dei risultati

Il Diamond Ticket fornisce lo stesso potere del Golden (TGT dominio-wide con gruppi arbitrari), quindi severity
`Critico`: consente accesso a qualunque servizio del dominio come amministratore. La differenza non e
nell'impatto ma nella rilevabilita: dove il Golden si tradirebbe con un logon privo di AS-REQ, il Diamond
presenta un flusso Kerberos apparentemente normale. In un assessment, trovare un dominio in cui il Diamond
funziona indisturbato significa che la sola detection "4624 senza 4768" non basta e che manca una PAC validation
o una correlazione piu fine.

### Analisi Teorica

Nel flusso Kerberos (vedi [THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.md>), sez. 3.1-3.2) il PAC
all'interno del TGT e firmato con la chiave del KDC (`krbtgt`): e questa firma a garantirne l'integrita. Chi
possiede la chiave di `krbtgt` puo quindi decifrare un TGT reale, alterare il PAC e ri-firmarlo in modo valido.
E la stessa violazione del Golden (compromissione della radice di fiducia Kerberos), ma applicata a un ticket
genuino anziche a uno forgiato: si preserva tutto cio che rende il ticket "normale" (l'AS-REQ reale, i campi
coerenti) e si falsifica solo l'autorizzazione (il PAC). La lezione teorica e che, una volta compromessa la
chiave di `krbtgt`, nessuna firma protegge piu nulla: l'unico rimedio e la rotazione (doppio reset).

## Remediation (Blue Team)

**Rilevamento.** Difficile con le regole classiche (l'AS-REQ e reale). Spostare la detection sulla **coerenza
del PAC** (PAC validation lato servizio e correlazione tra PAC emesso e PAC presentato) e su indicatori fini:
uso di RC4 dove ci si attende AES, KDCOptions anomali (mitigati pero da `/opsec`), TGT con tempi di vita o flag
insoliti. MDI e i SIEM con analitiche comportamentali su Kerberos restano la linea piu efficace.

**Hardening.** La contromisura radicale e la stessa del Golden: **doppio reset della password di `krbtgt`**
(due volte, per invalidare le chiavi correnti e precedenti). A monte: proteggere `krbtgt` evitando la
compromissione del DC e il DCSync; Tiering Model; monitoraggio dell'accesso alle repliche.

---

## Scenario Reale: Proiezione Post-Exploitation

> Vale per il controllo dominio-wide stealth (severity Critico).

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** possesso della chiave di `krbtgt` (da DCSync) e di una sessione/credenziali utente.

**Passo successivo immediato:** ottenere un TGT reale, modificarne il PAC e re-iniettarlo per operare come
Domain Admin senza l'anomalia del Golden.

**Kill Chain proiettata:**

```
Chiave di krbtgt (da DCSync) + credenziali utente standard
        |
        v
Diamond Ticket: TGT reale con PAC modificato (Domain Admins)
        |
        v
Accesso dominio-wide come amministratore, con flusso Kerberos apparentemente legittimo
        |
        v
Persistenza a lungo termine difficile da distinguere dall'attivita normale
```

**Impatto potenziale:** controllo completo del dominio con una traccia che elude le detection basate sull'assenza
di AS-REQ. La persistenza sopravvive finche `krbtgt` non viene ruotato due volte.

**Vettori di monetizzazione tipici:** persistenza prolungata in ambienti monitorati; accesso a dati e sistemi
critici senza allertare l'MDI.

### Prospettiva Difensore (Blue Team)

**Rilevamento:** analitiche comportamentali su Kerberos (MDI); PAC validation; correlazione tra PAC emesso dal
KDC e PAC presentato; uso inatteso di RC4.

**Indicatori di Compromissione (IOC):** TGT il cui PAC non e coerente con quello emesso all'AS-REQ; ticket con
cifratura o flag anomali; attivita privilegiata da account normalmente non privilegiati.

**Contenimento:** doppio reset di `krbtgt`; indagine sugli accessi privilegiati recenti; revisione dei DCSync.

**Eradicazione e hardening:** rotazione `krbtgt` (x2); protezione del DC contro il dump delle credenziali;
Tiering Model; abilitazione della PAC validation dove possibile.

**Lezione difensiva:** il Diamond mostra che irrobustire la detection del Golden (cercare l'assenza di AS-REQ)
non basta: senza protezione della chiave di `krbtgt` e senza controlli sul PAC, un avversario puo rendere la
compromissione indistinguibile dall'attivita legittima.

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Rubeus` | .NET Kerberos tool | CLI - Attivo | Comando `diamond` con `/ldap` e `/opsec` da Windows |
| `ticketer.py` (Impacket) | Kerberos tool | CLI - Attivo | Manipolazione del PAC di un TGT reale da Linux |
| `Mimikatz` | Credential/ticket tool | CLI - Attivo | Estrazione della chiave `krbtgt` e manipolazione ticket |

## Note di metodologia

In lab reale (es. GOAD o una macchina HTB con DC) documentare: la richiesta del TGT reale (AS-REQ a registro), la
modifica del PAC, l'uso del ticket e il confronto delle tracce rispetto a un Golden Ticket. Documentare il doppio
reset di `krbtgt` e la PAC validation come contromisure. Chiavi reali e SID vanno trattati come dati sensibili e
redatti nel report.

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Credential Access | Steal or Forge Kerberos Tickets: Golden Ticket | `T1558.001` | Manipolazione di un TGT reale con la chiave di krbtgt (variante stealth del Golden). |
| Lateral Movement | Use Alternate Authentication Material: Pass the Ticket | `T1550.003` | Uso del TGT modificato per accedere ai servizi del dominio. |
| Persistence | Account Manipulation | `T1098` | Persistenza dominio-wide tramite ticket con PAC alterato. |

## Correlazioni con altri moduli

| Provenienza | Questa tecnica | Effetto |
| :--- | :--- | :--- |
| [DCSync](<../../05-credential-dumping/dcsync/README.md>) | Diamond Ticket | fornisce la chiave di krbtgt, prerequisito comune a Golden e Diamond |
| [Golden Ticket](<../golden-ticket/README.md>) | Diamond Ticket | stessa radice di fiducia, ma Diamond parte da un TGT reale (piu stealth) |
| Diamond Ticket | [Sapphire Ticket](<../sapphire-ticket/README.md>) | evoluzione ulteriore: PAC autentico via S4U2self anziche modificato |

---

> **Nota:** Contenuto didattico e di metodologia. Esecuzione solo in laboratori propri o con autorizzazione esplicita. Output illustrativi, non da sistemi reali.
