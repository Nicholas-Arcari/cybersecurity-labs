> [English](README.en.md) | **Italiano**

# Kerberoasting: furto offline delle credenziali dei service account

> - **Fase:** Credential Access (dominio Active Directory)
> - **Visibilita:** Media - genera richieste TGS-REQ (Event ID 4769) per gli SPN bersaglio; rumoroso se si richiedono molti SPN o si forza l'etype RC4
> - **Prerequisiti:** un account di dominio valido qualsiasi (anche a basso privilegio); connettivita verso un Domain Controller sulla porta 88
> - **Tecnica:** `Kerberoasting` | **Severity tipica:** `Alto` | **Finding ID:** da assegnare in lab (pagina in metodologia)

- Natura del documento: metodologia. Gli output sono illustrativi e rappresentativi, non provenienti da un lab specifico; gli hash di esempio sono volutamente troncati e non craccabili.
- Obiettivo: ottenere, da un account di dominio non privilegiato, gli hash crackabili offline delle password dei service account, per poi scalare i privilegi tramite account di servizio compromessi.

---

## Executive Summary

Kerberoasting e una delle tecniche di Credential Access piu redditizie in Active Directory, e il motivo e
di design, non di bug. Qualunque utente autenticato puo chiedere al Domain Controller un ticket di servizio
(TGS) per qualunque account che abbia un Service Principal Name (SPN) associato. Quel ticket e cifrato con
la chiave a lungo termine dell'account di servizio, cioe con una chiave derivata dalla sua password.
L'attaccante non ha bisogno di interagire con il servizio: estrae il ticket e lo attacca offline, senza
ulteriore traffico verso il dominio e senza rischiare blocchi dell'account.

Il valore pratico sta nella natura dei service account: spesso hanno password impostate manualmente, non
soggette a rotazione, talvolta vecchie di anni, e non di rado godono di privilegi elevati (SQL Server,
service account applicativi, talora membri di gruppi amministrativi). Una sola password debole craccata
puo tradursi in un salto diretto verso privilegi significativi nel dominio.

## Contesto operativo (perche, prima del come)

Il punto di partenza realistico e un foothold con credenziali di dominio a basso privilegio: ottenute da
password spraying, phishing, credenziali riusate o trovate in chiaro nei moduli precedenti. In questa
posizione l'attaccante cerca vettori di escalation a basso costo e basso rischio. Kerberoasting e ideale
perche:

- non richiede privilegi particolari: basta essere un utente del dominio;
- l'attacco vero e proprio (il cracking) avviene offline, quindi e invisibile al dominio;
- i service account sono un bersaglio ad alto rendimento (password statiche, privilegi spesso elevati).

La decisione operativa chiave e la selettivita: richiedere i TGS di tutti gli SPN in un colpo e efficiente
ma rumoroso (molti Event ID 4769 ravvicinati, tipici di tool automatici). Un operatore attento alla OPSEC
prima enumera gli SPN interessanti (service account con appartenenze a gruppi privilegiati, individuati
via BloodHound) e richiede solo quelli.

## Esecuzione / Comandi

### Fase 1 - Enumerazione degli SPN

Da Linux, con Impacket, usando credenziali di dominio valide:

```bash
# Elenca gli account con SPN (potenziali bersagli Kerberoast), senza richiederne ancora gli hash
GetUserSPNs.py corp.local/utente:'Password123' -dc-ip 10.10.10.10
```

Output illustrativo (rappresentativo):

```
ServicePrincipalName    Name       MemberOf                              PasswordLastSet
----------------------  ---------  ------------------------------------  -------------------
MSSQLSvc/db01.corp.local svc_sql    CN=SQL Admins,OU=Service,DC=corp,...  2019-02-11 09:03   <-- password vecchia, bersaglio prioritario
HTTP/web01.corp.local    svc_web    CN=Domain Users,...                   2024-10-01 12:20
```

La colonna `PasswordLastSet` e un indicatore di priorita: piu la password e vecchia, piu e probabile che
sia debole e mai ruotata.

### Fase 2 - Richiesta dei TGS (il "roast")

```bash
# Richiede i TGS e salva gli hash in formato hashcat; -request per ottenere il materiale crackabile
GetUserSPNs.py corp.local/utente:'Password123' -dc-ip 10.10.10.10 -request -outputfile kerb_hashes.txt
```

Da host Windows, l'equivalente con Rubeus (mirato a un singolo account, piu OPSEC-friendly):

```
# Rubeus: roasting del solo account bersaglio
Rubeus.exe kerberoast /user:svc_sql /nowrap
```

Output illustrativo (hash troncato e non craccabile, mostrato solo per il formato):

```
$krb5tgs$23$*svc_sql$CORP.LOCAL$MSSQLSvc/db01*$a1b2c3...[TRONCATO]...9f  <-- etype 23 (RC4): crackabile offline
```

Il prefisso `$krb5tgs$23$` indica encryption type 23 (RC4-HMAC): la chiave coincide con l'hash NT della
password, senza salt ne iterazioni, quindi l'attacco offline e rapido. Un prefisso `$krb5tgs$18$` indica
AES256, molto piu lento da attaccare.

### Fase 3 - Cracking offline

```bash
# Modo 13100 = Kerberos 5 TGS-REP etype 23 (RC4). Per AES256 usare 19700, per AES128 19600
hashcat -m 13100 kerb_hashes.txt /usr/share/wordlists/rockyou.txt
```

Output illustrativo:

```
$krb5tgs$23$*svc_sql$CORP.LOCAL$MSSQLSvc/db01*$a1b2...:SqlProd2019!   <-- password recuperata
```

## Analisi dei risultati

Il recupero della password di `svc_sql` ha un doppio significato. Sul piano immediato, fornisce credenziali
valide per autenticarsi come quel service account (in questo esempio, un account con appartenenza a un
gruppo amministrativo di SQL Server). Sul piano della kill chain, trasforma un foothold a basso privilegio
in un accesso privilegiato senza aver toccato il Domain Controller e senza aver generato un singolo
tentativo di login fallito: tutto il lavoro di forza bruta e avvenuto offline, sulla macchina
dell'attaccante.

Non tutti i roast hanno successo: un service account con password lunga e casuale (o un gMSA) produce un
hash che, pur estratto, resta non craccabile in tempi utili. Il finding reale, in un lab, andrebbe
classificato in base all'esito effettivo: `Alto` se una password privilegiata viene recuperata, `Medio`
o `Informativo` se gli SPN esistono ma le password resistono.

### Analisi Teorica

Kerberoasting non viola la crittografia di Kerberos: ne sfrutta il modello di autorizzazione. Nel flusso
Kerberos (vedi [THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.md>), sezione 3.1), il KDC risponde
a una TGS-REQ emettendo un TGS cifrato con la chiave dell'account di servizio, senza verificare se il
richiedente sia autorizzato a usare quel servizio: il controllo d'accesso e demandato al servizio stesso.
Ne consegue che qualunque principal autenticato puo ottenere TGS per qualunque SPN. La violazione e della
proprieta P2 (confidenzialita delle chiavi a lungo termine): poiche con etype 23 la chiave coincide con
l'hash NT della password, il TGS e un oracolo offline sulla password.

La scelta di Impacket (`GetUserSPNs.py`) da Linux rispetto a Rubeus da Windows dipende dal foothold: su una
shell Linux o da macchina attaccante con credenziali, Impacket e naturale; su un host Windows gia
compromesso, Rubeus evita di portare tool Python e si integra con la sessione corrente. In entrambi i casi
la leva teorica e identica.

## Remediation (Blue Team)

**Rilevamento (SOC/SIEM).**

- Event ID 4769 (Kerberos Service Ticket Operation) sul Domain Controller: un volume anomalo di richieste
  da un singolo principal in pochi secondi e il pattern tipico dei tool di Kerberoasting di massa.
- Richieste 4769 con `Ticket Encryption Type = 0x17` (RC4) in un ambiente che dovrebbe usare AES: segnale
  di downgrade forzato a scopo offensivo.
- Correlazione con account honeypot: creare un account "esca" con SPN e password forte, e allertare su
  qualunque TGS richiesto per esso (nessun uso legittimo atteso).

**Hardening.**

- Usare Group Managed Service Account (gMSA): password di 240 bit gestite e ruotate dal dominio,
  praticamente non craccabili offline.
- Dove i gMSA non sono applicabili, imporre password lunghe e casuali (25+ caratteri) per i service
  account e ruotarle periodicamente.
- Disabilitare l'etype RC4 nel dominio e forzare AES, riducendo drasticamente la velocita di cracking.
- Applicare il minimo privilegio ai service account: un account di servizio non deve appartenere a gruppi
  amministrativi se non strettamente necessario.

---

## Scenario Reale: Proiezione Post-Exploitation

> Questa sezione descrive come un Kerberoasting riuscito si inserirebbe in un engagement reale, dal punto
> di vista dell'attaccante (Red Team) e del difensore (Blue Team).

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** foothold con credenziali di dominio a basso privilegio; enumerazione SPN completata.

**Passo successivo immediato:** richiesta mirata del TGS del service account privilegiato individuato
(es. `svc_sql`) e cracking offline della password.

**Kill Chain proiettata:**

```
Utente di dominio low-priv
        |
        v
Kerberoasting (svc_sql) -> password del service account recuperata offline
        |
        v
Accesso come svc_sql (admin locale su DB server / membro gruppo privilegiato)
        |
        v
Credential dumping sul server raggiunto -> hash di altri account
        |
        v
Escalation verso Domain Admin (es. via ACL/deleghe) -> DCSync
        |
        v
Golden Ticket -> persistenza di dominio
```

**Impatto potenziale:** compromissione che parte da un semplice utente e arriva, tramite un service
account dimenticato, a privilegi elevati nel dominio. Nei dati pubblici sugli incidenti (Verizon DBIR), il
vettore "credenziali compromesse" e tra i piu ricorrenti; i service account statici ne sono una causa
frequente.

**Vettori di monetizzazione tipici:**
- Ransomware enterprise dopo il raggiungimento dei privilegi di dominio.
- Esfiltrazione di dati sensibili dai sistemi raggiunti con il service account (es. database di produzione).
- Rivendita dell'accesso privilegiato come Access Broker.

### Prospettiva Difensore (Blue Team)

**Rilevamento:** picco di Event ID 4769, in particolare con etype RC4, da un singolo account in un
intervallo ristretto; richiesta di TGS per account honeypot.

**Indicatori di Compromissione (IOC):**
- Event ID 4769 in volume anomalo da un singolo principal verso molti SPN.
- Presenza di etype RC4 (0x17) in TGS dove ci si attende solo AES.
- Processi come `Rubeus` o esecuzione di `GetUserSPNs` da host non amministrativi.

**Contenimento:** reset immediato della password dei service account potenzialmente esposti; revoca delle
sessioni; indagine sugli accessi effettuati con quegli account.

**Eradicazione e hardening:** migrazione a gMSA; disabilitazione di RC4; minimo privilegio sui service
account; monitoraggio continuo dei 4769.

**Lezione difensiva:** la robustezza di Kerberos non protegge da una password debole su un service account
privilegiato. Il controllo efficace non e sul protocollo ma sulla gestione delle identita di servizio
(entropia, rotazione, privilegi).

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `GetUserSPNs.py` (Impacket) | Python toolkit | CLI - Attivo | Enumerazione SPN e roasting da Linux/macchina attaccante |
| `Rubeus` | .NET tool | CLI - Attivo | Kerberoasting da host Windows compromesso, mirato e OPSEC-friendly |
| `hashcat` | GPU cracker | CLI - Offline | Cracking degli hash TGS (13100 RC4, 19600 AES128, 19700 AES256) |
| `john` (jumbo) | CPU cracker | CLI - Offline | Alternativa a hashcat per il cracking dei TGS |
| `BloodHound` / `SharpHound` | Graph enum | CLI/GUI - Attivo | Individuare quali service account sono privilegiati, per roasting selettivo |
| `NetExec` (`nxc`) | AD/SMB toolkit | CLI - Attivo | Modulo di kerberoasting integrato e azioni correlate |

---

## Note di metodologia

Trattandosi di pagina metodologica, non vi sono output di laboratorio propri. In un lab reale (es. GOAD)
i punti di attenzione da documentare sarebbero: il tempo di cracking in funzione dell'etype (RC4 vs AES) e
della qualita della wordlist, il rumore generato sui log 4769, e la differenza pratica tra roasting di
massa e mirato. Questi dati, una volta misurati, andranno riportati come finding reale (`AD-NNN`) e,
se quantitativi, nella cartella `EVALUATION/` con la relativa nota di validita.

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Credential Access | Steal or Forge Kerberos Tickets: Kerberoasting | `T1558.003` | Richiesta di TGS per SPN di service account e cracking offline della password. |
| Discovery | Account Discovery: Domain Account | `T1087.002` | Enumerazione degli account con SPN tramite query al dominio. |
| Credential Access | Brute Force: Password Cracking | `T1110.002` | Cracking offline dell'hash TGS con wordlist/regole. |

---

## Correlazioni con altri moduli

| Provenienza | Questa tecnica | Effetto |
| :--- | :--- | :--- |
| Password spraying / phishing ([05-social-engineering](<../../../05-social-engineering/README.md>)) | Kerberoasting | fornisce l'account di dominio iniziale necessario al roasting |
| Kerberoasting | Password cracking ([04-system-exploitation/05-password-cracking](<../../../04-system-exploitation/05-password-cracking/hashcat/README.md>)) | gli hash TGS si crackano con hashcat/john gia documentati nel repo |
| Kerberoasting | [DCSync](<../../05-credential-dumping/dcsync/README.md>) | un service account privilegiato puo abilitare la catena verso i diritti di replica |

---

> **Nota:** Tutte le tecniche descritte sono a scopo didattico e di documentazione di metodologia. Vanno
> eseguite esclusivamente in laboratori di proprieta o su sistemi con autorizzazione esplicita. Gli output
> sono illustrativi e non provengono da sistemi reali o di terze parti.
