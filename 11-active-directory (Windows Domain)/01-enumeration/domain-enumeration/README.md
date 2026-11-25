> [English](README.en.md) | **Italiano**

# Enumerazione LDAP / RPC / SMB del dominio

> - **Fase:** Discovery (dominio Active Directory)
> - **Visibilita:** Bassa-Media - query LDAP e RPC sono traffico comune; il RID cycling via null session e piu caratteristico
> - **Prerequisiti:** connettivita verso DC (LDAP 389/636, SMB 445, RPC 135); alcune query funzionano con null session, la maggior parte richiede un account di dominio
> - **Tecnica:** `Domain enumeration (LDAP/RPC/SMB)` | **Severity tipica:** `Basso` | **Finding ID:** da assegnare in lab (metodologia)

- Natura del documento: metodologia. Output illustrativi, non da lab specifico.
- Obiettivo: raccogliere, con strumenti CLI mirati, utenti, gruppi, policy e configurazioni del dominio, complementando la vista a grafo di BloodHound con dettagli puntuali e verificabili.

---

## Executive Summary

Accanto a BloodHound, l'enumerazione mirata con strumenti CLI resta indispensabile per rispondere a domande
specifiche: quali sono gli utenti e i loro attributi, qual e la password policy (fondamentale prima di uno
spraying), chi appartiene ai gruppi privilegiati, quali account hanno SPN o pre-autenticazione disabilitata.
LDAP e la fonte piu ricca (l'intero database di dominio e interrogabile in lettura da un utente
autenticato); RPC e SMB aggiungono enumerazione di utenti e share, in alcuni casi anche senza credenziali
(null session) su domini mal configurati.

## Contesto operativo (perche, prima del come)

L'enumerazione mirata serve a preparare le tecniche successive con dati precisi. Prima di un password
spraying, per esempio, e essenziale leggere la lockout policy per non bloccare gli account (un errore che
rivela l'attacco e danneggia il cliente). Prima del Kerberoasting, serve la lista degli SPN. Questi dati si
estraggono meglio con query LDAP puntuali che con una raccolta a grafo.

## Esecuzione / Comandi

### LDAP (ldapsearch)

```bash
# Password policy del dominio (lockout threshold, durata): leggere PRIMA di qualunque spraying
ldapsearch -x -H ldap://10.10.10.10 -D 'utente@corp.local' -w 'Password123' \
  -b 'DC=corp,DC=local' "(objectClass=domain)" lockoutThreshold lockoutDuration
```

```bash
# Utenti con SPN (bersagli Kerberoast) e account senza pre-auth (bersagli AS-REP)
ldapsearch -x -H ldap://10.10.10.10 -D 'utente@corp.local' -w 'Password123' \
  -b 'DC=corp,DC=local' "(servicePrincipalName=*)" sAMAccountName servicePrincipalName
```

Output illustrativo (rappresentativo):

```
lockoutThreshold: 5         <-- 5 tentativi: spraying possibile ma con cautela (max 4 per finestra)
sAMAccountName: svc_sql
servicePrincipalName: MSSQLSvc/db01.corp.local   <-- bersaglio Kerberoast
```

### RPC / SMB (rpcclient, nxc, enum4linux-ng)

```bash
# Enumerazione utenti e gruppi via RPC con credenziali
rpcclient -U 'corp.local\utente%Password123' 10.10.10.10 -c "enumdomusers;enumdomgroups"
```

```bash
# NetExec: enumerazione utenti, password policy e RID brute forcing in un colpo
nxc smb 10.10.10.10 -u utente -p 'Password123' --users --pass-pol --rid-brute
```

```bash
# enum4linux-ng: enumerazione SMB/RPC complessiva (successore di enum4linux)
enum4linux-ng -A 10.10.10.10 -u utente -p 'Password123'
```

## Analisi dei risultati

L'enumerazione mirata restituisce i dati che fanno da input alle tecniche offensive: la password policy
abilita uno spraying sicuro, la lista SPN abilita il Kerberoasting, l'elenco degli account senza pre-auth
abilita l'AS-REP Roasting. Da sola, l'enumerazione e `Informativo`/`Basso`; il suo valore sta nel ridurre
il rischio e il rumore delle fasi successive. Una null session che espone l'intero elenco utenti e un
finding `Basso` a se (information disclosure), perche fornisce a un attaccante non autenticato la materia
prima per lo spraying.

### Analisi Teorica

La ricchezza dell'enumerazione LDAP deriva da una scelta di design di AD: il database di dominio e
leggibile da qualunque utente autenticato, perche il modello assume che la conoscenza della struttura non
sia essa stessa un segreto (la sicurezza sta nei controlli d'accesso, non nell'occultamento). Questa
assunzione e ragionevole ma ha un costo offensivo: l'attaccante con un solo account ottiene una mappa
dettagliata. La difesa non puo "spegnere LDAP", ma puo ridurre gli attributi sensibili leggibili e, dove
non servono, eliminare le null session (retaggio di configurazioni legacy).

## Remediation (Blue Team)

**Rilevamento.** Volume anomalo di query LDAP/RPC da un singolo account; RID cycling (sequenze di query
SAMR su RID crescenti); accessi anonimi/null session ai DC.

**Hardening.** Disabilitare le null session e l'accesso anonimo a LDAP/SMB sui DC; applicare il minimo
privilegio alla lettura di attributi sensibili; monitorare l'enumerazione di massa; mantenere una lockout
policy sensata (che pero non apra a DoS sugli account).

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `ldapsearch` | LDAP client | CLI - Attivo | Query mirate su utenti, gruppi, policy, SPN |
| `windapsearch` | LDAP wrapper | CLI - Attivo | Query LDAP comuni preconfezionate |
| `rpcclient` | RPC client | CLI - Attivo | Enumerazione utenti/gruppi via RPC, anche null session |
| `NetExec` (`nxc`) | AD/SMB toolkit | CLI - Attivo | Enumerazione utenti, password policy, RID brute, share |
| `enum4linux-ng` | Enum wrapper | CLI - Attivo | Enumerazione SMB/RPC complessiva (successore di enum4linux) |

## Note di metodologia

In lab reale i dati da documentare come finding sarebbero: la password policy (per giustificare i parametri
dello spraying), l'elenco SPN e degli account senza pre-auth, e l'eventuale presenza di null session
(information disclosure). Questi diventano input diretti alle tecniche 02-05.

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Discovery | Account Discovery: Domain Account | `T1087.002` | Enumerazione degli account di dominio via LDAP/RPC. |
| Discovery | Permission Groups Discovery: Domain Groups | `T1069.002` | Enumerazione dei gruppi e delle appartenenze. |
| Discovery | Password Policy Discovery | `T1201` | Lettura di lockout e password policy prima dello spraying. |

## Correlazioni con altri moduli

| Provenienza | Questa tecnica | Effetto |
| :--- | :--- | :--- |
| [BloodHound](<../bloodhound/README.md>) | Domain enumeration | complementa il grafo con dettagli puntuali (policy, SPN) |
| Domain enumeration | [Kerberoasting](<../../02-kerberos-attacks/kerberoasting/README.md>) / [kerbrute spraying](<../kerbrute-userenum/README.md>) | fornisce SPN, account senza pre-auth e policy per spraying sicuro |
| Enumerazione SMB | [modulo 02 - smb-net-bios](<../../../02-vulnerability-assessment/02-protocol-specific-audit/smb-net-bios/README.md>) | continuita con l'audit SMB gia presente nel repo |

---

> **Nota:** Contenuto didattico e di metodologia. Esecuzione solo in laboratori propri o con autorizzazione esplicita. Output illustrativi, non da sistemi reali.
