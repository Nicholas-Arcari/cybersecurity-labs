> [English](README.en.md) | **Italiano**

# AD CS ESC1: template con subject alternative name arbitrario

> - **Fase:** Privilege Escalation (dominio Active Directory, servizi di certificazione)
> - **Visibilita:** Media - la richiesta di certificato lascia traccia nel database della CA (richiesta da un utente a basso privilegio per un soggetto privilegiato)
> - **Prerequisiti:** un account di dominio con diritto di enrollment su un template vulnerabile (Client Authentication + Enrollee Supplies Subject + nessuna approvazione manager)
> - **Tecnica:** `AD CS ESC1` | **Severity tipica:** `Critico` | **Finding ID:** da assegnare in lab (metodologia)

- Natura del documento: metodologia. Output illustrativi; identificativi segnaposto.
- Obiettivo: ottenere, da un account di dominio a basso privilegio, un certificato valido per autenticarsi come un utente privilegiato (es. Domain Admin), sfruttando un template mal configurato.

---

## Executive summary

ESC1 e la misconfigurazione di AD CS piu diretta: un template di certificato che (a) consente la Client
Authentication, (b) permette al richiedente di specificare un Subject Alternative Name (SAN) arbitrario, e
(c) e enrollabile da utenti a basso privilegio, senza approvazione del manager. In queste condizioni un
utente qualsiasi richiede un certificato indicando come SAN un account privilegiato (es. un Domain Admin):
la CA lo emette, e il certificato autentica via PKINIT come quell'account. E un salto diretto da utente di
dominio a Domain Admin, senza cracking e senza relay.

## Contesto operativo (perche, prima del come)

ESC1 si sfrutta quando l'enumerazione ([esc-enumeration](<../esc-enumeration/README.md>)) rivela un template
con la combinazione vulnerabile. E preferito quando applicabile perche non richiede posizione di rete ne
coercizione (a differenza di ESC8): basta un account di dominio con enrollment sul template. La decisione
operativa e scegliere quale identita privilegiata impersonare (tipicamente un Domain Admin noto
dall'enumerazione).

## Esecuzione / comandi

```bash
# Richiede un certificato sul template vulnerabile, specificando come SAN un utente privilegiato
certipy req -u utente@corp.local -p 'Password123' -dc-ip 10.10.10.10 \
  -ca CORP-CA -template UserAuth -upn administrator@corp.local
```

```bash
# Usa il certificato ottenuto per autenticarsi come l'utente privilegiato (PKINIT) e ricavarne TGT/hash
certipy auth -pfx administrator.pfx -dc-ip 10.10.10.10
```

Output illustrativo (rappresentativo):

```
[*] Saved certificate and private key to 'administrator.pfx'
[*] Got TGT for 'administrator@CORP.LOCAL'
[*] Got NT hash for 'administrator@CORP.LOCAL': <HASH_TRONCATO>   <-- Domain Admin
```

## Analisi dei risultati

Il risultato e l'identita crittografica di un Domain Admin ottenuta da un semplice utente di dominio, in una
singola richiesta di certificato. La severity e `Critico`: compromissione del dominio senza cracking, senza
relay, senza coercizione. Come per ESC8, il certificato sopravvive al reset della password dell'account
impersonato, offrendo anche persistenza.

### Analisi teorica

ESC1 viola la proprieta P3 (confinamento dell'autorita) a livello di policy della CA: il template definisce
chi puo ottenere cosa, e una policy che consente a utenti a basso privilegio di emettere certificati con SAN
arbitrario per Client Authentication equivale a concedere loro l'impersonazione di chiunque. Il certificato
emesso lega l'identita (SAN) scelta dal richiedente, e il DC, in fase di PKINIT, si fida del SAN presente nel
certificato firmato dalla CA (che e trusted). La catena di fiducia e corretta in ogni anello: il difetto e
nella policy del template, non nella crittografia. Vedi [THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.md>)
sez. 3.4.

## Remediation (blue team)

**Rilevamento.** Richieste di certificato in cui il SAN non corrisponde al richiedente (un utente a basso
privilegio che richiede un certificato per un Domain Admin); emissione di certificati con Client
Authentication da template a rischio; correlazione con un successivo PKINIT da host inatteso.

**Hardening.** Disattivare "Enrollee Supplies Subject" sui template per autenticazione; richiedere
l'approvazione del manager per l'emissione; restringere gli enrollment rights ai soli gruppi necessari;
rimuovere Client Authentication dai template che non ne hanno bisogno; audit periodico con Certipy/PSPKIAudit.

---

## Scenario reale: proiezione Post-Exploitation

> ESC1 porta direttamente a privilegi di dominio (severity Critico).

### Prospettiva attaccante (red team)

**Punto di partenza:** account di dominio a basso privilegio con enrollment su un template ESC1.

**Passo successivo immediato:** richiesta di un certificato con SAN = Domain Admin e autenticazione PKINIT.

**Kill Chain proiettata:**

```
Utente di dominio low-priv (enrollment su template ESC1)
        |
        v
Richiesta certificato con SAN = administrator -> certificato emesso dalla CA
        |
        v
PKINIT con il certificato -> TGT / hash NT del Domain Admin
        |
        v
DCSync -> dominio completo
        |
        v
Golden Ticket / persistenza (il certificato stesso e persistente)
```

**Impatto potenziale:** compromissione totale del dominio da un semplice utente, in una singola richiesta di
certificato. La persistenza basata su certificato sopravvive ai reset di password.

**Vettori di monetizzazione tipici:** ransomware e esfiltrazione a valle del dominio; access brokering.

### Prospettiva difensore (blue team)

**Rilevamento:** richieste di certificato con SAN diverso dal richiedente; emissioni anomale su template a
rischio; PKINIT da host inatteso seguito da attivita privilegiata.

**Indicatori di Compromissione (IOC):** entry nel database della CA con SAN privilegiato richiesto da utente
non privilegiato; uso del certificato per autenticazione da origine anomala.

**Contenimento:** revoca del certificato emesso in modo anomalo; disabilitazione del template vulnerabile;
reset e indagine sull'account impersonato.

**Eradicazione e hardening:** correzione dei template (no SAN arbitrario, approvazione manager, enrollment
ristretto); audit periodico della PKI.

**Lezione difensiva:** un template mal configurato trasforma la PKI, nata per rafforzare l'autenticazione, in
una scorciatoia verso il dominio. La difesa e la governance dei template, non la crittografia dei certificati.

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Certipy` | ad cs toolkit | cli - attivo | richiesta certificato con san arbitrario e autenticazione pkinit |
| `Certify` | .net ad cs tool | cli - attivo | richiesta/abuso certificati da host windows |
| `Rubeus` | .net kerberos tool | cli - attivo | uso del certificato per pkinit da windows |
| `PSPKIAudit` | powershell audit | cli - attivo | audit dei template lato blue team |

## Note di metodologia

In lab reale documentare: il template vulnerabile individuato, la richiesta con SAN privilegiato, l'esito del
PKINIT, e la verifica che il certificato resta valido dopo un reset di password (dimensione persistenza).

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| credential access | steal or forge authentication certificates | `T1649` | emissione di un certificato con san arbitrario per impersonare un account privilegiato. |
| privilege escalation | valid accounts: domain accounts | `T1078.002` | uso dell'identita privilegiata ottenuta via certificato. |

## Correlazioni con altri moduli

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| [esc-enumeration](<../esc-enumeration/README.md>) | esc1 | individua il template vulnerabile da sfruttare |
| esc1 | [dcsync](<../../05-credential-dumping/dcsync/README.md>) | l'identita domain admin ottenuta abilita la replica |
| [esc8](<../esc8-relay-adcs/README.md>) | esc1 | due scenari ad cs: esc1 senza rete/coercizione, esc8 via relay |

---

> **Nota:** Contenuto didattico e di metodologia. Esecuzione solo in laboratori propri o con autorizzazione esplicita. Output illustrativi, non da sistemi reali.
