> [English](README.en.md) | **Italiano**

# Sapphire Ticket: PAC autentico via S4U2self

> - **Fase:** Persistence / Privilege Escalation (dominio Active Directory)
> - **Visibilita:** Estremamente bassa - come il Diamond c'e un flusso Kerberos reale, ma in piu il PAC inserito e autentico (emesso dal KDC per un utente privilegiato reale), non modificato
> - **Prerequisiti:** chiave (AES) dell'account `krbtgt`, un account di dominio con cui eseguire la richiesta S4U2self, e l'identificazione di un utente privilegiato bersaglio
> - **Tecnica:** `Sapphire Ticket` | **Severity tipica:** `Critico` | **Finding ID:** da assegnare in lab (metodologia)

- Natura del documento: metodologia. Output illustrativi; chiavi/SID segnaposto. Nessun payload operativo riprodotto.
- Obiettivo: ottenere un ticket dominio-wide il cui PAC e quello autentico di un utente privilegiato reale, ottenuto via S4U2self, eliminando anche la discrepanza di PAC che caratterizza il Diamond.

---

## Executive Summary

Il Sapphire Ticket e l'evoluzione piu furtiva della famiglia Golden/Diamond. Tutte e tre richiedono la chiave di
`krbtgt`, ma si distinguono per la provenienza del PAC (la struttura che elenca i gruppi dell'utente, cioe i
privilegi):

- **Golden**: PAC inventato da zero (nessun AS-REQ a registro: anomalia rilevabile).
- **[Diamond](<../diamond-ticket/README.md>)**: PAC reale ma **modificato** (c'e AS-REQ, ma il PAC presentato non
  coincide con quello emesso).
- **Sapphire**: PAC **autentico** di un utente privilegiato reale, ottenuto legittimamente via **S4U2self** e
  inserito nel ticket.

Poiche il PAC proviene dal KDC per un account realmente privilegiato, non c'e ne l'assenza di AS-REQ del Golden
ne la discrepanza di PAC del Diamond. E l'accesso dominio-wide piu difficile da distinguere dall'attivita
legittima disponibile una volta compromessa la chiave di `krbtgt`.

## Contesto operativo (perche, prima del come)

Si sceglie il Sapphire quando l'ambiente ha detection evolute (MDI, correlazione del PAC) che potrebbero
intercettare anche il Diamond. Il meccanismo sfrutta **S4U2self**: una funzionalita legittima dell'estensione
Kerberos per la delega che permette a un servizio di richiedere, per conto proprio, un ticket a nome di un altro
utente, ottenendo un PAC valido per quell'utente. Combinando S4U2self (per ottenere il PAC autentico di un
amministratore) con la chiave di `krbtgt` (per confezionare il ticket finale), si ottiene un ticket con
privilegi massimi e un PAC genuino. Serve un account di dominio per la richiesta e l'identificazione di un
utente bersaglio ad alto privilegio.

## Esecuzione / Comandi

```bash
# Impacket ticketer: tecnica sapphire - usa S4U2self per ottenere il PAC autentico di un utente privilegiato
# (-request con -impersonate), poi confeziona il ticket con la chiave di krbtgt
ticketer.py -request -impersonate amministratore \
  -domain corp.local -user utente_standard -password '<SEGNAPOSTO>' \
  -aesKey <AES256_KRBTGT_SEGNAPOSTO> -domain-sid S-1-5-21-<SEGNAPOSTO> amministratore
```

Output illustrativo (rappresentativo):

```
[*] Richiesta S4U2self per 'amministratore' -> PAC autentico ricevuto dal KDC
[*] Ticket confezionato con la chiave di krbtgt e PAC genuino
[*] Salvato in amministratore.ccache   <-- ticket "sapphire": PAC autentico, non modificato
```

## Analisi dei risultati

Il Sapphire fornisce potere dominio-wide (severity `Critico`) come Golden e Diamond, ma con la traccia piu
pulita. Il valore di questa tecnica, in un assessment, e dimostrativo: se funziona, significa che nemmeno le
detection basate sulla coerenza del PAC (che smaschererebbero il Diamond) sono sufficienti, e che la difesa deve
necessariamente spostarsi sulla protezione della chiave di `krbtgt` e sulla sua rotazione. Rispetto al Diamond,
elimina l'ultimo indicatore residuo (la discrepanza di PAC), a costo di un'interazione un po' piu complessa col
KDC (la richiesta S4U2self).

### Analisi Teorica

Il Sapphire combina due elementi legittimi di Kerberos usati in modo malevolo. S4U2self (vedi
[THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.md>), sez. 3.1-3.2, e la pagina
[deleghe](<../../04-delegation-acl/delegation-unconstrained-constrained/README.md>)) e pensato per la delega di
protocollo: consente di ottenere un PAC valido a nome di un utente. La chiave di `krbtgt` consente di firmare un
TGT. Isolati non sono abuso; insieme permettono di confezionare un ticket dominio-wide il cui PAC e
indistinguibile da quello di un login reale dell'amministratore, perche lo e: e stato emesso dal KDC. E la
dimostrazione che, compromessa la radice di fiducia (`krbtgt`), anche i controlli sull'autenticita del PAC
perdono valore. L'unica contromisura resta invalidare la chiave.

## Remediation (Blue Team)

**Rilevamento.** Il piu difficile della famiglia. Il PAC e autentico, l'AS-REQ (o la richiesta S4U) e reale.
Si punta su: monitoraggio delle richieste **S4U2self** anomale (un account che richiede ticket a nome di altri
senza esserne il servizio delegato atteso); correlazione tra l'uso di un ticket ad alto privilegio e l'assenza
di un login interattivo corrispondente dell'amministratore; analitiche comportamentali MDI.

**Hardening.** Come per Golden e Diamond, la contromisura radicale e il **doppio reset di `krbtgt`**. A monte:
proteggere `krbtgt` (evitare DC compromise e DCSync); limitare e monitorare le configurazioni di delega;
Tiering Model.

---

## Scenario Reale: Proiezione Post-Exploitation

> Vale per il controllo dominio-wide con PAC autentico (severity Critico).

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** chiave di `krbtgt` (da DCSync) e un account di dominio per la richiesta S4U2self.

**Passo successivo immediato:** ottenere via S4U2self il PAC autentico di un amministratore e confezionare il
ticket finale.

**Kill Chain proiettata:**

```
Chiave di krbtgt (da DCSync) + account di dominio
        |
        v
S4U2self -> PAC autentico dell'amministratore (emesso dal KDC)
        |
        v
Sapphire Ticket: ticket dominio-wide con PAC genuino (nessuna discrepanza)
        |
        v
Persistenza dominio-wide praticamente indistinguibile dall'attivita legittima
```

**Impatto potenziale:** controllo del dominio con la traccia piu pulita della famiglia; la persistenza resiste
finche `krbtgt` non viene ruotato due volte.

**Vettori di monetizzazione tipici:** persistenza di lungo periodo in ambienti ad alta maturita difensiva;
accesso indisturbato a dati e sistemi critici.

### Prospettiva Difensore (Blue Team)

**Rilevamento:** richieste S4U2self anomale; uso di ticket privilegiati senza login interattivo corrispondente;
analitiche comportamentali MDI.

**Indicatori di Compromissione (IOC):** attivita S4U da account non deputati alla delega; comparsa di privilegi
elevati senza eventi di logon coerenti; uso inatteso di RC4.

**Contenimento:** doppio reset di `krbtgt`; revisione delle deleghe; indagine sugli accessi privilegiati.

**Eradicazione e hardening:** rotazione `krbtgt` (x2); protezione del DC; controllo e riduzione delle
configurazioni di delega; Tiering Model.

**Lezione difensiva:** il Sapphire chiude il cerchio Golden/Diamond: non esiste controllo sul ticket o sul PAC
che regga alla compromissione di `krbtgt`. La difesa e tutta a monte (proteggere la chiave) e nella rotazione.

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `ticketer.py` (Impacket) | Kerberos tool | CLI - Attivo | Tecnica sapphire: PAC autentico via S4U2self + confezionamento con krbtgt |
| `Rubeus` | .NET Kerberos tool | CLI - Attivo | Richieste S4U e manipolazione ticket da Windows |
| `getST.py` (Impacket) | Kerberos tool | CLI - Attivo | Richieste S4U2self/S4U2proxy a supporto |

## Note di metodologia

In lab reale documentare: la richiesta S4U2self per ottenere il PAC autentico, il confezionamento del ticket, e
il confronto delle tracce con Golden e Diamond (assenza sia dell'anomalia AS-REQ sia della discrepanza di PAC).
Documentare il doppio reset di `krbtgt` come unica contromisura risolutiva. Chiavi e SID reali vanno redatti.

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Credential Access | Steal or Forge Kerberos Tickets: Golden Ticket | `T1558.001` | Ticket dominio-wide con PAC autentico ottenuto via S4U2self e chiave di krbtgt. |
| Lateral Movement | Use Alternate Authentication Material: Pass the Ticket | `T1550.003` | Uso del ticket per accedere ai servizi del dominio come amministratore. |
| Persistence | Account Manipulation | `T1098` | Persistenza dominio-wide con PAC genuino. |

## Correlazioni con altri moduli

| Provenienza | Questa tecnica | Effetto |
| :--- | :--- | :--- |
| [DCSync](<../../05-credential-dumping/dcsync/README.md>) | Sapphire Ticket | fornisce la chiave di krbtgt |
| [Diamond Ticket](<../diamond-ticket/README.md>) | Sapphire Ticket | Sapphire usa un PAC autentico (S4U2self) invece di modificarlo: piu stealth |
| [Deleghe Kerberos](<../../04-delegation-acl/delegation-unconstrained-constrained/README.md>) | Sapphire Ticket | S4U2self e la primitiva di delega sfruttata per ottenere il PAC |

---

> **Nota:** Contenuto didattico e di metodologia. Esecuzione solo in laboratori propri o con autorizzazione esplicita. Output illustrativi, non da sistemi reali.
