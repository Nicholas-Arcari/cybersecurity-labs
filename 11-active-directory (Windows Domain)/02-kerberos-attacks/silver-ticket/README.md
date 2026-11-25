> [English](README.en.md) | **Italiano**

# Silver ticket: forgiatura del ticket di servizio (TGS)

> - **Fase:** Persistence / Lateral Movement (dominio Active Directory)
> - **Visibilita:** Molto bassa - il ticket e forgiato offline e presentato direttamente al servizio, senza mai contattare il KDC (ne TGT ne TGS-REQ a registro)
> - **Prerequisiti:** possesso dell'hash NT (o chiave AES) dell'account di servizio bersaglio (es. account macchina per CIFS/HOST) e del SID del dominio
> - **Tecnica:** `Silver Ticket` | **Severity tipica:** `Alto` | **Finding ID:** da assegnare in lab (metodologia)

- Natura del documento: metodologia. Output illustrativi; chiavi/SID segnaposto.
- Obiettivo: forgiare un TGS valido per un servizio specifico, ottenendo accesso a quel servizio senza passare dal KDC, in modo estremamente silenzioso.

---

## Executive summary

Il Silver Ticket e la controparte "chirurgica" del Golden Ticket. Mentre il Golden forgia un TGT valido per
l'intero dominio usando la chiave di krbtgt, il Silver forgia un TGS valido per un singolo servizio usando
la chiave dell'account di quel servizio. Poiche il TGS e cifrato con la chiave del servizio e viene
presentato direttamente ad esso (messaggio AP-REQ), il KDC non e mai coinvolto: non c'e TGT, non c'e
TGS-REQ, quindi niente traccia lato Domain Controller. Questo rende il Silver Ticket uno degli accessi piu
silenziosi disponibili.

Il prezzo della discrezione e la portata: il Silver vale solo per il servizio la cui chiave si possiede
(es. CIFS su un server per accedere alle sue share, HOST per l'esecuzione di task). E ideale per persistenza
mirata e lateral movement discreto.

## Contesto operativo (perche, prima del come)

Il Silver Ticket presuppone di avere gia la chiave di un account di servizio (hash dell'account macchina o
di un service account), ottenuta ad esempio da un dump locale o da DCSync. Si sceglie il Silver rispetto al
Golden quando serve discrezione e basta l'accesso a un servizio specifico: non toccando il KDC, evita le
detection basate sul monitoraggio dei ticket a livello di dominio. La decisione riguarda il servizio
bersaglio (lo SPN) e, ancora una volta, l'uso di AES invece di RC4.

## Esecuzione / comandi

```bash
# Forgia un TGS per il servizio CIFS dell'host target usando l'hash dell'account macchina
ticketer.py -nthash <HASH_ACCOUNT_SERVIZIO> -domain-sid S-1-5-21-<SEGNAPOSTO> -domain corp.local \
  -spn cifs/srv01.corp.local amministratore
```

```bash
# Uso del ticket per accedere alla share del servizio bersaglio
export KRB5CCNAME=amministratore.ccache
smbclient.py -k -no-pass corp.local/amministratore@srv01.corp.local
```

Output illustrativo (rappresentativo):

```
[*] Saving ticket in amministratore.ccache
# accesso a cifs/srv01 come 'amministratore' senza contattare il KDC
```

## Analisi dei risultati

Il Silver Ticket fornisce accesso mirato e quasi invisibile a un servizio. La severity tipica e `Alto`
perche, pur limitato a un servizio, quel servizio puo essere critico (es. CIFS su un file server con dati
sensibili, o HOST su un server per eseguire codice). Non raggiunge il `Critico` del Golden solo perche non e
dominio-wide, ma la combinazione di piu Silver su servizi chiave si avvicina allo stesso effetto, con molto
meno rumore.

### Analisi teorica

Nel flusso Kerberos (vedi [THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.md>), sez. 3.1) il TGS e
cifrato con la chiave dell'account di servizio, e il servizio lo valida decifrandolo con la propria chiave.
Il servizio, per default, non verifica presso il KDC la validita del PAC contenuto nel ticket (la verifica
del PAC e opzionale e spesso non attiva). Chi possiede la chiave del servizio puo quindi forgiare un TGS con
un PAC arbitrario e il servizio lo accettera. E la violazione della proprieta P1 limitata al perimetro di un
singolo servizio: l'attaccante falsifica la prova di autenticazione verso quel servizio specifico.

## Remediation (blue team)

**Rilevamento.** Difficile lato KDC (il Silver non lo contatta). La detection si sposta sul servizio e
sull'host: accessi a un servizio senza corrispondente TGS-REQ a registro sul DC; abilitare la verifica del
PAC dove possibile; correlare logon sul servizio con l'assenza di attivita Kerberos sul DC.

**Hardening.** Ruotare le password degli account di servizio e degli account macchina (una chiave vecchia
resta sfruttabile); abilitare la PAC validation; proteggere a monte le chiavi di servizio (evitare dump
locali e DCSync); Tiering Model.

---

## Scenario reale: proiezione Post-Exploitation

> Vale per l'accesso mirato a un servizio critico (severity Alto).

### Prospettiva attaccante (red team)

**Punto di partenza:** possesso della chiave di un account di servizio/macchina (da dump locale o DCSync).

**Passo successivo immediato:** forgiatura di un Silver Ticket per il servizio bersaglio e accesso diretto.

**Kill Chain proiettata:**

```
Chiave di un account di servizio/macchina
        |
        v
Silver Ticket per cifs/host del server bersaglio (nessun contatto col KDC)
        |
        v
Accesso silenzioso al servizio (share sensibili, esecuzione task)
        |
        v
Persistenza mirata + esfiltrazione discreta dal server
```

**Impatto potenziale:** accesso persistente e difficile da rilevare a servizi e dati critici, senza i
segnali tipici dell'attivita Kerberos a livello di dominio.

**Vettori di monetizzazione tipici:** esfiltrazione discreta e prolungata; persistenza su sistemi chiave.

### Prospettiva difensore (blue team)

**Rilevamento:** accessi a un servizio privi del corrispondente TGS-REQ sul DC; abilitazione della PAC
validation per smascherare PAC forgiati.

**Indicatori di Compromissione (IOC):** logon sul servizio senza attivita Kerberos correlata sul DC; uso di
RC4 dove ci si attende AES.

**Contenimento:** rotazione della chiave del servizio/account macchina compromesso; indagine sugli accessi.

**Eradicazione e hardening:** PAC validation; rotazione periodica delle chiavi macchina/servizio;
protezione a monte delle chiavi.

**Lezione difensiva:** il Silver Ticket mostra che la fiducia riposta da un servizio nel solo possesso della
propria chiave e un rischio: senza PAC validation, chiunque abbia quella chiave e indistinguibile da un
utente legittimo.

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `ticketer.py` (impacket) | kerberos tool | cli - attivo | forgiatura del silver ticket da linux |
| `Mimikatz` | credential/ticket tool | cli - attivo | `kerberos::golden` con `/service` e `/target` per il silver da windows |
| `Rubeus` | .net kerberos tool | cli - attivo | forgiatura/uso ticket da windows |

## Note di metodologia

In lab reale documentare: la forgiatura a partire dalla chiave dell'account macchina/servizio, l'accesso al
servizio bersaglio, e la verifica dell'assenza di traccia sul DC rispetto a un accesso Kerberos normale.
Documentare la PAC validation come contromisura.

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| credential access | steal or forge kerberos tickets: silver ticket | `T1558.002` | forgiatura di un tgs per un servizio usando la chiave dell'account di servizio. |
| lateral movement | use alternate authentication material: pass the ticket | `T1550.003` | uso del ticket forgiato per accedere al servizio bersaglio. |
| persistence | account manipulation | `T1098` | persistenza mirata sul servizio tramite ticket forgiati. |

## Correlazioni con altri moduli

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| [dcsync](<../../05-credential-dumping/dcsync/README.md>) / dump locale | silver ticket | fornisce la chiave dell'account di servizio/macchina |
| [golden ticket](<../golden-ticket/README.md>) | silver ticket | varianti complementari: dominio-wide vs servizio mirato |
| silver ticket | [07-post-exploitation](<../../../07-post-exploitation/README.md>) | lateral movement e persistenza discreti su servizi chiave |

---

> **Nota:** Contenuto didattico e di metodologia. Esecuzione solo in laboratori propri o con autorizzazione esplicita. Output illustrativi, non da sistemi reali.
