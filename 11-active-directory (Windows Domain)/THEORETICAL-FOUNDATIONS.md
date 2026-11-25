> [English](THEORETICAL-FOUNDATIONS.en.md) | **Italiano**

# Fondamenti Teorici - Active Directory e Kerberos

> Apparato teorico-accademico del modulo 11. Complementa i README operativi (metodologia, comandi, MITRE)
> fornendone le basi formali. Non li sostituisce: li fonda e vi rimanda. Citazioni: solo fonti reali e
> verificate (vedi Riferimenti; voci da integrare nel master `REFERENCES.md`).

## Abstract

Active Directory basa l'autenticazione su Kerberos v5 (RFC 4120), un protocollo a ticket derivato dal
modello Needham-Schroeder a chiave simmetrica. La sicurezza del dominio non dipende dalla robustezza
crittografica di Kerberos in se, che e solida, ma dalle assunzioni che il protocollo fa sul deployment:
che le chiavi a lungo termine dei service account siano ad alta entropia, che i privilegi di replica siano
confinati ai Domain Controller, e che le configurazioni accessorie (deleghe, autorita di certificazione,
ACL) rispettino il principio del minimo privilegio. Questo capitolo formalizza il modello dell'avversario,
le proprieta di sicurezza attese e i meccanismi teorici alla base delle tre tecniche documentate nel
modulo (Kerberoasting, AD CS ESC8, DCSync), mostrando che ciascuna e la violazione di una specifica
assunzione di deployment, non una rottura del protocollo.

## 1. Modello dell'Avversario

Si adotta un modello alla Dolev-Yao [Dolev & Yao 1983] adattato al contesto di rete interna: l'avversario
non e un attaccante remoto non autenticato, ma un attore che ha gia ottenuto un punto d'appoggio nel
dominio. Si distinguono tre livelli di capacita:

- **A1 - Insider autenticato a basso privilegio:** possiede credenziali di un account di dominio qualsiasi
  (ottenute via phishing, password spraying, credenziali riusate). Puo richiedere ticket Kerberos per
  qualsiasi SPN (presupposto di Kerberoasting) e interrogare LDAP in lettura.
- **A2 - Attore in posizione di rete:** puo intercettare e inoltrare traffico sul segmento (presupposto
  del relay NTLM) e indurre autenticazioni tramite coercizione (es. PetitPotam, PrinterBug).
- **A3 - Account con privilegi delegati:** possiede un account a cui, per misconfigurazione, sono stati
  concessi diritti sensibili (replica di dominio, scrittura su oggetti privilegiati), senza essere
  Domain Admin.

L'avversario non ha accesso fisico al Domain Controller ne la capacita di rompere primitive
crittografiche standard (AES, SHA-2). Il canale e assunto osservabile e manipolabile nei limiti della
posizione di rete (A2). Questo modello e coerente con la realta documentata negli incident report, in cui
il vettore iniziale e quasi sempre la credenziale compromessa, non lo zero-day [Verizon DBIR].

## 2. Proprieta di Sicurezza

Kerberos mira a garantire alcune proprieta che le tecniche del modulo violano o aggirano:

- **P1 - Autenticazione mutua.** Client e servizio si autenticano a vicenda tramite ticket cifrati con
  chiavi che solo il legittimo detentore conosce. Nel senso di Lowe [Lowe 1997], la proprieta desiderata
  e l'*injective agreement*: a ogni esecuzione completata dal servizio corrisponde una e una sola
  esecuzione intesa dal client legittimo.
- **P2 - Confidenzialita delle chiavi a lungo termine.** La chiave di un account (derivata dalla password,
  o l'hash NT per l'etype RC4) non deve essere ricavabile da materiale osservabile. Kerberoasting viola
  questa proprieta sfruttando il fatto che il TGS e cifrato proprio con quella chiave.
- **P3 - Confinamento dell'autorita.** Operazioni critiche (replica del database di dominio, emissione di
  certificati per conto di altri) devono essere limitate a principal fidati. DCSync viola il confinamento
  della replica; ESC8 viola quello dell'autorita di certificazione.
- **P4 - Binding dell'autenticazione al canale.** L'autenticazione dovrebbe essere legata al canale su cui
  avviene, per impedirne il riuso altrove. NTLM non fornisce questo binding per default (manca EPA/Channel
  Binding e SMB/LDAP signing), ed e questa l'assunzione mancante che il relay sfrutta.

## 3. Fondamenti Teorici

### 3.1 Kerberos come protocollo a terza parte fidata

Kerberos v5 [Neuman et al. 2005, RFC 4120] discende dal protocollo Needham-Schroeder a chiave simmetrica
[Needham & Schroeder 1978], che introduce un Key Distribution Center (KDC) come terza parte fidata. Il
flusso in sei messaggi e:

```
AS-REQ  : C  -> KDC   richiesta di TGT, con pre-autenticazione (timestamp cifrato con chiave di C)
AS-REP  : KDC -> C    TGT (cifrato con chiave di krbtgt) + chiave di sessione
TGS-REQ : C  -> KDC   presenta il TGT, chiede un ticket per uno SPN
TGS-REP : KDC -> C    TGS (cifrato con la chiave dell'account di servizio) + chiave di sessione
AP-REQ  : C  -> S     presenta il TGS al servizio
AP-REP  : S  -> C     conferma (autenticazione mutua)
```

Il punto cruciale per la sicurezza offensiva: il KDC non verifica, al momento della TGS-REP, se il client
sia autorizzato a usare il servizio; demanda il controllo d'accesso al servizio stesso, che legge i gruppi
dal PAC (Privilege Attribute Certificate) dentro il ticket. Ne consegue che qualunque principal
autenticato puo ottenere un TGS per qualunque SPN (base teorica del Kerberoasting).

### 3.2 Derivazione delle chiavi ed etype

La chiave a lungo termine di un account dipende dall'encryption type (etype) negoziato:

- etype 23 (RC4-HMAC): la chiave coincide con l'hash NT della password (MD4 della password in UTF-16LE).
  Nessun salt, nessuna iterazione: un TGS con etype 23 e crackabile offline a velocita elevata.
- etype 17/18 (AES128/AES256-CTS-HMAC-SHA1): la chiave deriva dalla password con string-to-key basato su
  PBKDF2, 4096 iterazioni [Raeburn 2005, RFC 3962], con salt = realm + nome utente. Molto piu lento da
  attaccare offline, ma comunque vulnerabile se la password e debole.

Questa asimmetria spiega perche gli attaccanti forzano quando possibile l'etype RC4 nelle richieste
Kerberoast: non e una debolezza di Kerberos, ma della primitiva legacy ancora abilitata per
compatibilita.

### 3.3 Replica di dominio (MS-DRSR) e DCSync

I Domain Controller sincronizzano il database (NTDS.dit) tramite il protocollo MS-DRSR (Directory
Replication Service Remote Protocol). La chiamata `IDL_DRSGetNCChanges` restituisce gli attributi di un
oggetto, inclusi i segreti (hash NT, chiavi Kerberos), a un richiedente che possieda i diritti estesi di
replica. DCSync [Delpy & Le Toux 2015] non rompe nulla: impersona un DC ed emette una richiesta di replica
legittima. Il controllo d'accesso del DC verifica solo che il richiedente abbia i tre diritti estesi
(DS-Replication-Get-Changes, -All, -In-Filtered-Set), non che sia davvero un DC. E la violazione della
proprieta P3 (confinamento dell'autorita di replica) per misconfigurazione dell'ACL dell'oggetto dominio.

### 3.4 AD CS e la fiducia nei certificati (ESC)

Active Directory Certificate Services lega l'identita a certificati X.509. La ricerca "Certified
Pre-Owned" [Schroeder & Christensen 2021] ha catalogato una famiglia di misconfigurazioni (ESC1-ESC8+) che
permettono di ottenere certificati utilizzabili per autenticarsi come altri principal. ESC8 in
particolare combina due debolezze: (a) l'endpoint di Web Enrollment di AD CS accetta autenticazione NTLM,
e (b) NTLM non e legato al canale (P4). Un attaccante in posizione A2 coerce un DC ad autenticarsi (T1187)
e ne rilancia l'autenticazione (T1557.001) verso l'endpoint HTTP di AD CS, ottenendo un certificato per
l'account macchina del DC, con cui poi si autentica via PKINIT e ottiene i segreti del dominio. Il
certificato, inoltre, resta valido anche dopo il reset della password: ne consegue una persistenza che le
contromisure basate su password non eliminano.

## 4. Analisi Quantitativa

- **Kerberoasting - superficie offline.** Con etype 23 (RC4) l'hash e un MD4 senza salt ne stretching:
  l'attacco offline e limitato solo dalla velocita dell'hardware e dall'entropia della password. Con etype
  18 (AES256) il PBKDF2 a 4096 iterazioni [RFC 3962] riduce di ordini di grandezza i tentativi al secondo,
  ma non protegge password a bassa entropia. Modi hashcat di riferimento: 13100 (TGS-REP RC4), 19600
  (TGS-REP AES128), 19700 (TGS-REP AES256); per AS-REP Roasting 18200 (etype 23).
- **Service account e rotazione.** Il rischio del Kerberoasting cresce con l'eta e la staticita della
  password del service account: questi account spesso hanno password impostate manualmente anni prima e
  mai ruotate. I Group Managed Service Account (gMSA) mitigano con password di 240 bit gestite e ruotate
  automaticamente dal dominio, riportando l'attacco offline oltre la soglia di fattibilita pratica
  (ricerca su spazio dei 2^240 infattibile).
- **Golden Ticket e krbtgt.** La chiave di `krbtgt` firma tutti i TGT; un Golden Ticket resta valido
  finche la password di krbtgt non viene cambiata due volte (AD mantiene chiave corrente e precedente).
  Questo e il motivo per cui il reset di krbtgt va eseguito due volte in sequenza controllata.

Nota di validita: i valori sopra (iterazioni PBKDF2, bit gMSA, modi hashcat) provengono da specifiche e
documentazione ufficiali, non da misure di laboratorio. Eventuali benchmark di cracking andranno misurati
realmente ed etichettati come tali (coerentemente con la disciplina della cartella `EVALUATION/`).

## 5. Rassegna della Letteratura

Il concetto di Kerberoasting e stato introdotto operativamente da Tim Medin [Medin 2014] a DerbyCon. La
sistematizzazione degli attacchi AD CS e dovuta a Schroeder e Christensen [Schroeder & Christensen 2021].
DCSync e opera di Benjamin Delpy e Vincent Le Toux nell'ambito di Mimikatz [Delpy & Le Toux 2015]. Sul
versante formale, le analisi classiche di Kerberos risalgono a Bellovin e Merritt [Bellovin & Merritt 1991]
(limiti del protocollo) e alla linea di lavori sulla verifica dei protocolli di autenticazione avviata da
Needham-Schroeder [Needham & Schroeder 1978] e raffinata, sul piano delle proprieta, da Lowe [Lowe 1997],
gia citato nell'apparato THEORY-ADVANCED del repository. Il modello d'avversario di riferimento resta
quello di Dolev e Yao [Dolev & Yao 1983].

## 6. Limiti e Problemi Aperti

- Il modulo documenta metodologia, non misure: i tempi di cracking, i tassi di successo del relay e la
  latenza della replica andranno quantificati in laboratorio reale prima di qualsiasi affermazione numerica.
- La tassonomia ESC e in evoluzione (ESC1-ESC16 e oltre): la trattazione copre ESC8 come caso
  rappresentativo del binding mancante, non l'intera famiglia.
- Le contromisure (gMSA, SMB/LDAP signing, Extended Protection for Authentication, Protected Users, reset
  di krbtgt) interagiscono tra loro: una modellazione formale della loro efficacia combinata e un problema
  aperto, parzialmente affrontabile con i metodi della cartella `FORMAL-MODELS/`.

## 7. Sintesi e Collegamento alla Pratica

Le tre tecniche del modulo condividono una struttura comune: nessuna rompe la crittografia, ciascuna
sfrutta un'assunzione di deployment non soddisfatta (P2 per Kerberoasting, P4 per ESC8, P3 per DCSync).
Questa e la lezione trasversale per il blue team: l'hardening di AD non consiste nel "rendere Kerberos piu
forte", ma nel far valere le assunzioni che il protocollo da per scontate (password forti e ruotate per i
service account, binding dell'autenticazione al canale, confinamento rigoroso dei diritti di replica e di
emissione certificati). I dettagli operativi, i comandi e la mappatura MITRE sono nei README delle
rispettive sottocartelle.

## Riferimenti

> Sottoinsieme del master `REFERENCES.md` (+ `.en.md`), sezione O "Active Directory, Kerberos e PKI".
> Chiavi `[Autore Anno]` allineate al master.

- [Needham & Schroeder 1978] R. Needham, M. Schroeder, "Using Encryption for Authentication in Large
  Networks of Computers", Communications of the ACM, 21(12), 1978.
- [Dolev & Yao 1983] D. Dolev, A. Yao, "On the Security of Public Key Protocols", IEEE Transactions on
  Information Theory, 29(2), 1983.
- [Bellovin & Merritt 1991] S. Bellovin, M. Merritt, "Limitations of the Kerberos Authentication System",
  USENIX Winter 1991.
- [Lowe 1997] G. Lowe, "A Hierarchy of Authentication Specifications", IEEE CSFW, 1997.
- [Neuman et al. 2005] C. Neuman, T. Yu, S. Hartman, K. Raeburn, "The Kerberos Network Authentication
  Service (V5)", RFC 4120, 2005.
- [Raeburn 2005] K. Raeburn, "Advanced Encryption Standard (AES) Encryption for Kerberos 5", RFC 3962, 2005.
- [Medin 2014] T. Medin, "Attacking Microsoft Kerberos: Kicking the Guard Dog of Hades", DerbyCon, 2014.
- [Delpy & Le Toux 2015] B. Delpy, V. Le Toux, "DCSync" (Mimikatz `lsadump::dcsync`), 2015.
- [Schroeder & Christensen 2021] W. Schroeder, L. Christensen, "Certified Pre-Owned: Abusing Active
  Directory Certificate Services", SpecterOps, 2021.
- [Verizon DBIR] Verizon, "Data Breach Investigations Report" (edizioni annuali), per la prevalenza del
  vettore "credenziali compromesse". Citare l'edizione specifica quando usata per un dato puntuale.
