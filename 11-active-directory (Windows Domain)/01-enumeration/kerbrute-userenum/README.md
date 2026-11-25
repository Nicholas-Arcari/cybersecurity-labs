> [English](README.en.md) | **Italiano**

# Kerbrute: user enumeration e password spraying via Kerberos

> - **Fase:** Discovery e Credential Access (dominio Active Directory)
> - **Visibilita:** Variabile - la user enumeration via AS-REQ e relativamente silente (non genera logon falliti standard); il password spraying genera eventi di pre-autenticazione e va dosato per non bloccare account
> - **Prerequisiti:** connettivita verso il DC sulla porta 88 (Kerberos); per la user enumeration non servono credenziali; per lo spraying serve una lista di username e una o poche password candidate
> - **Tecnica:** `Kerbrute (user enum + password spraying)` | **Severity tipica:** `Variabile (Basso / Alto)` | **Finding ID:** da assegnare in lab (metodologia)

- Natura del documento: metodologia. Output illustrativi, non da lab specifico.
- Obiettivo: costruire una lista di username validi senza autenticazione (user enumeration) e, da questa, ottenere credenziali valide con un password spraying prudente, rispettando la lockout policy.

---

## Executive summary

Kerbrute sfrutta una caratteristica del pre-autenticazione Kerberos: quando si invia un AS-REQ per un
utente, il KDC risponde in modo diverso a seconda che l'utente esista o meno, prima ancora di verificare la
password. Questo permette di enumerare username validi senza generare i classici eventi di logon fallito, e
quindi in modo relativamente silenzioso. Dalla lista di username validi si passa al password spraying:
provare una singola password comune (es. stagionale o di default) su molti account, invece di molte password
su un account (che causerebbe lockout).

Lo spraying e la fase ad alto valore e alto rischio: una sola credenziale valida fornisce il foothold di
dominio necessario a tutto il modulo, ma uno spraying mal dosato blocca gli account e rivela l'attacco. La
regola e leggere prima la lockout policy (vedi [domain-enumeration](<../domain-enumeration/README.md>)).

## Contesto operativo (perche, prima del come)

Quando non si hanno ancora credenziali di dominio, Kerbrute e spesso il primo passo. La user enumeration
costa poco ed e discreta; costruisce la lista di bersagli per lo spraying. Lo spraying va calibrato sulla
policy: se il lockout e a 5 tentativi su finestra di 30 minuti, si provano al massimo 3-4 password per
finestra, distanziate. La decisione prudente e privilegiare poche password ad alta probabilita
(es. `Nomeazienda<Anno>!`, `Stagione<Anno>!`) su tutta la lista, piuttosto che molte password su pochi
account.

## Esecuzione / comandi

### User enumeration

```bash
# Enumerazione username validi da una wordlist, senza credenziali
kerbrute userenum -d corp.local --dc 10.10.10.10 usernames.txt
```

Output illustrativo (rappresentativo):

```
[+] VALID USERNAME:  j.smith@corp.local
[+] VALID USERNAME:  svc_sql@corp.local   <-- username validi confermati
```

### Password spraying (dopo aver letto la lockout policy)

```bash
# Una sola password su tutti gli username validi (spraying); dosare per non superare il lockout
kerbrute passwordspray -d corp.local --dc 10.10.10.10 valid_users.txt 'Autunno2026!'
```

Output illustrativo:

```
[+] VALID LOGIN:  j.smith@corp.local:Autunno2026!   <-- credenziale valida: foothold di dominio ottenuto
```

## Analisi dei risultati

La user enumeration e di per se `Basso` (information disclosure di username validi). Il password spraying,
se riesce, e `Alto`: una credenziale valida e il foothold che abilita l'intero modulo AD (enumerazione
autenticata, Kerberoasting, e la catena di escalation). Il finding reale va classificato in base all'esito:
nessuna credenziale trovata lascia il finding a `Basso` (solo enumerazione); una credenziale valida, specie
se di un account privilegiato, alza la severity.

### Analisi teorica

La user enumeration sfrutta una fuga di informazione nel pre-auth Kerberos: il KDC distingue "utente
inesistente" (KDC_ERR_C_PRINCIPAL_UNKNOWN) da "utente esistente, pre-auth richiesta"
(KDC_ERR_PREAUTH_REQUIRED) prima di qualunque verifica di password. E un canale laterale a livello di
protocollo, non un bug di implementazione. Lo spraying sfrutta invece un fatto statistico: in una
popolazione di centinaia di utenti, la probabilita che almeno uno usi una password comune e alta, mentre il
costo per account (un tentativo) resta sotto la soglia di lockout. La difesa combina policy di lockout
sensate, password non prevedibili (contro lo spraying) e monitoraggio dei pattern di pre-auth (contro
l'enumerazione).

## Remediation (blue team)

**Rilevamento.** Molti AS-REQ per username diversi dalla stessa sorgente in breve tempo (enumerazione);
Event ID 4768/4771 su molti account con la stessa finestra temporale (spraying); un singolo tentativo di
pre-auth fallito distribuito su molti utenti e la firma classica dello spraying.

**Hardening.** Lockout policy sensata; password non prevedibili (bandire pattern stagionali/aziendali con
filtri come quelli di Azure AD Password Protection); MFA dove possibile; monitoraggio e alert sui pattern di
spraying; disabilitazione di account inutilizzati che allargano la superficie.

---

## Scenario reale: proiezione Post-Exploitation

> Vale per l'esito "spraying riuscito" (severity Alto).

### Prospettiva attaccante (red team)

**Punto di partenza:** nessuna credenziale; lista di username validi ottenuta via enumeration.

**Passo successivo immediato:** spraying prudente con una password stagionale; alla prima credenziale
valida, passaggio all'enumerazione autenticata.

**Kill Chain proiettata:**

```
Nessuna credenziale
        |
        v
Kerbrute userenum -> lista username validi
        |
        v
Password spraying -> prima credenziale di dominio valida (foothold)
        |
        v
BloodHound + Kerberoasting -> percorsi di escalation
        |
        v
Escalation (ACL/deleghe/ADCS) -> DCSync -> dominio completo
```

**Impatto potenziale:** da zero credenziali al foothold di dominio in una sola password indovinata, da cui
parte l'intera catena AD.

**Vettori di monetizzazione tipici:** ransomware e esfiltrazione a valle del controllo di dominio; rivendita
dell'accesso iniziale.

### Prospettiva difensore (blue team)

**Rilevamento:** pattern di spraying (un tentativo su molti account); enumerazione via AS-REQ di massa.

**Indicatori di Compromissione (IOC):** Event ID 4768/4771 distribuiti su molti account nella stessa
finestra; sorgente singola con molti AS-REQ per utenti diversi.

**Contenimento:** blocco della sorgente; reset dell'account compromesso; indagine sugli accessi effettuati.

**Eradicazione e hardening:** MFA; password protection contro pattern prevedibili; lockout calibrato;
disabilitazione account dormienti.

**Lezione difensiva:** lo spraying non rompe nulla, sfrutta password prevedibili in una grande popolazione.
La difesa efficace e rendere le password non indovinabili (filtri e MFA), non solo allungarle.

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `kerbrute` | kerberos pre-auth | cli - attivo | user enumeration e password spraying via kerberos |
| `NetExec` (`nxc`) | ad/smb toolkit | cli - attivo | password spraying su smb/ldap/winrm, con controllo del lockout |
| `kerbrute` + wordlist utenti | - | - | liste come seclists per username comuni e pattern aziendali |

## Note di metodologia

In lab reale i dati da documentare: la lockout policy effettiva (per giustificare il dosaggio), gli username
validi enumerati, e l'esito dello spraying. Attenzione operativa reale: uno spraying senza aver letto la
policy puo bloccare account e va evitato anche in lab per acquisire l'abitudine corretta.

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| discovery | account discovery: domain account | `T1087.002` | enumerazione di username validi via pre-auth kerberos. |
| credential access | brute force: password spraying | `T1110.003` | tentativo di una password comune su molti account. |

## Correlazioni con altri moduli

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| [domain-enumeration](<../domain-enumeration/README.md>) | kerbrute spraying | la lockout policy letta qui determina il dosaggio sicuro |
| kerbrute (credenziale ottenuta) | [bloodhound](<../bloodhound/README.md>) / modulo intero | fornisce il foothold di dominio iniziale |
| password spraying | [05-social-engineering](<../../../05-social-engineering/README.md>) | alternativa/complemento al phishing per l'accesso iniziale |

---

> **Nota:** Contenuto didattico e di metodologia. Esecuzione solo in laboratori propri o con autorizzazione esplicita. Output illustrativi, non da sistemi reali.
