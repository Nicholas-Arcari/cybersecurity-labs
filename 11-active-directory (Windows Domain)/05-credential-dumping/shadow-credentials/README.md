> [English](README.en.md) | **Italiano**

# Shadow Credentials: autenticazione via certificato abusando di msDS-KeyCredentialLink

> - **Fase:** Credential Access / Persistence (dominio Active Directory)
> - **Visibilita:** Bassa-Media - la scrittura dell'attributo e una modifica directory (Event ID 5136); l'uso successivo e un PKINIT
> - **Prerequisiti:** diritto di scrittura sull'attributo `msDS-KeyCredentialLink` dell'oggetto bersaglio (utente o computer), tipicamente da GenericWrite/GenericAll individuato con BloodHound; presenza di una PKI che supporti PKINIT (AD CS o key trust)
> - **Tecnica:** `Shadow Credentials` | **Severity tipica:** `Alto` | **Finding ID:** da assegnare in lab (metodologia)

- Natura del documento: metodologia. Output illustrativi; identificativi segnaposto.
- Obiettivo: ottenere la capacita di autenticarsi come un account bersaglio senza conoscerne la password, aggiungendo una chiave pubblica controllata al suo attributo di key credential.

---

## Executive Summary

Shadow Credentials sfrutta l'attributo `msDS-KeyCredentialLink`, usato da Windows Hello for Business e dal
key trust per legare una chiave pubblica a un account ai fini dell'autenticazione Kerberos via PKINIT. Se un
attaccante puo scrivere questo attributo su un oggetto bersaglio (utente o computer), vi aggiunge una coppia
di chiavi che controlla; da quel momento puo autenticarsi come il bersaglio presentando quella chiave,
ottenendo un TGT e, tramite UnPAC-the-hash, anche l'hash NT dell'account. Non serve conoscere ne resettare
la password: e un'alternativa piu discreta al reset password tipico dell'abuso di ACL.

## Contesto operativo (perche, prima del come)

Shadow Credentials e spesso preferito al reset di password quando si ha GenericWrite/GenericAll su un
oggetto, perche e meno invasivo: non cambia la password della vittima (che continua a funzionare, evitando
sospetti e disservizi) e lascia all'attaccante un mezzo di autenticazione aggiuntivo. E quindi anche una
forma di persistenza. La decisione operativa e scegliere il bersaglio (un computer privilegiato o un utente
ad alto valore individuato con BloodHound) e ricordarsi di ripulire l'attributo a fine test.

## Esecuzione / Comandi

```bash
# Aggiunge una key credential controllata all'oggetto bersaglio (produce un certificato/chiave da usare)
certipy shadow auto -u utente@corp.local -p 'Password123' -dc-ip 10.10.10.10 -account 'TARGET$'
```

Output illustrativo (rappresentativo):

```
[*] Adding Key Credential to 'TARGET$'
[*] Authenticating as 'TARGET$' via PKINIT
[*] Got NT hash for 'TARGET$@CORP.LOCAL': <HASH_TRONCATO>   <-- hash dell'account bersaglio
[*] Restoring msDS-KeyCredentialLink                        <-- cleanup dell'attributo
```

## Analisi dei risultati

Il risultato e la capacita di autenticarsi come il bersaglio (e il suo hash NT), ottenuta senza toccare la
password. Se il bersaglio e un computer privilegiato o un utente ad alto valore, la severity e `Alto` e la
catena prosegue verso il dominio. Il vantaggio rispetto al reset password e la discrezione e la persistenza:
finche l'attributo resta scritto, l'attaccante mantiene l'accesso.

### Analisi Teorica

`msDS-KeyCredentialLink` implementa il "key trust": AD si fida di una chiave pubblica associata all'account
per l'autenticazione PKINIT. Chi controlla la scrittura dell'attributo controlla di fatto la lista delle
chiavi fidate per quell'account, e puo aggiungere la propria. E la violazione della proprieta P3
(confinamento dell'autorita) applicata alla fiducia crittografica: il diritto di scrivere un attributo si
traduce nel potere di autenticarsi come l'oggetto. A differenza del reset password, non c'e un segreto
condiviso da cambiare: la contromisura e rimuovere il diritto di scrittura e monitorare l'attributo. Vedi
[THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.md>), sez. 3.4.

## Remediation (Blue Team)

**Rilevamento.** Event ID 5136 sulle modifiche di `msDS-KeyCredentialLink`; comparsa di key credential su
account che non usano Windows Hello for Business; PKINIT seguito da attivita privilegiata da host inatteso.

**Hardening.** Restringere i diritti di scrittura sugli oggetti (audit BloodHound); monitorare
specificamente le modifiche a `msDS-KeyCredentialLink`; dove WHfB non e usato, considerare alert su qualunque
scrittura dell'attributo; Tiering Model.

---

## Scenario Reale: Proiezione Post-Exploitation

> Shadow Credentials come escalation discreta e persistenza (severity Alto).

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** GenericWrite/GenericAll su un oggetto bersaglio (da BloodHound).

**Passo successivo immediato:** scrivere una key credential controllata e autenticarsi via PKINIT come il
bersaglio.

**Kill Chain proiettata:**

```
GenericWrite su un oggetto (da BloodHound)
        |
        v
Scrittura msDS-KeyCredentialLink -> chiave controllata aggiunta
        |
        v
PKINIT come il bersaglio -> TGT + hash NT (senza toccare la password)
        |
        v
Accesso privilegiato / DCSync (se bersaglio ad alto valore) -> dominio
        |
        v
Persistenza: l'attributo resta un mezzo d'accesso finche non rimosso
```

**Impatto potenziale:** escalation e persistenza discrete, senza il "rumore" e il disservizio di un reset
password.

**Vettori di monetizzazione tipici:** persistenza e accesso prolungato; a valle, ransomware/esfiltrazione.

### Prospettiva Difensore (Blue Team)

**Rilevamento:** modifiche a `msDS-KeyCredentialLink` (Event ID 5136); PKINIT anomali.

**Indicatori di Compromissione (IOC):** key credential su account senza WHfB; autenticazione via certificato
da host inatteso.

**Contenimento:** rimozione della key credential malevola; indagine sugli accessi; reset se necessario.

**Eradicazione e hardening:** bonifica dei diritti di scrittura eccessivi; monitoraggio continuo
dell'attributo; Tiering Model.

**Lezione difensiva:** il diritto di scrivere un attributo "tecnico" come la key credential equivale a
poter diventare quell'account. La difesa e l'audit delle ACL e il monitoraggio dell'attributo, non la sola
gestione delle password.

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Certipy` | AD CS toolkit | CLI - Attivo | `shadow auto`: aggiunta key credential, PKINIT e cleanup |
| `pywhisker` | AD tool | CLI - Attivo | Manipolazione di `msDS-KeyCredentialLink` da Linux |
| `Whisker` | .NET tool | CLI - Attivo | Shadow Credentials da host Windows |
| `BloodHound` | Graph enum | GUI | Individuazione del diritto di scrittura (AddKeyCredentialLink/GenericWrite) |

## Note di metodologia

In lab reale documentare: il diritto sfruttato (da BloodHound), la scrittura dell'attributo, l'esito del
PKINIT (TGT/hash) e la verifica del cleanup. Sottolineare la discrezione rispetto al reset password.

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Persistence | Account Manipulation | `T1098` | Scrittura di una key credential controllata sull'oggetto bersaglio. |
| Credential Access | Steal or Forge Authentication Certificates | `T1649` | Uso del key trust (PKINIT) per autenticarsi come il bersaglio. |

## Correlazioni con altri moduli

| Provenienza | Questa tecnica | Effetto |
| :--- | :--- | :--- |
| [ACL abuse](<../../04-delegation-acl/acl-abuse/README.md>) | Shadow Credentials | il diritto di scrittura (AddKeyCredentialLink/GenericWrite) abilita la tecnica |
| Shadow Credentials | [DCSync](<../dcsync/README.md>) | se il bersaglio e privilegiato, apre la strada alla replica abusata |
| [ESC1/ESC8](<../../03-adcs/README.md>) | Shadow Credentials | varianti della stessa idea: autenticazione via certificato/chiave invece che password |

---

> **Nota:** Contenuto didattico e di metodologia. Esecuzione solo in laboratori propri o con autorizzazione esplicita. Output illustrativi, non da sistemi reali.
