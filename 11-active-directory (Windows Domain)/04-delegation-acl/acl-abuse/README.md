> [English](README.en.md) | **Italiano**

# ACL / DACL abuse: GenericAll, WriteDACL, WriteOwner, AddKeyCredentialLink

> - **Fase:** Privilege Escalation (dominio Active Directory)
> - **Visibilita:** Media - le modifiche agli oggetti AD (reset password, aggiunta a gruppo, scrittura attributi) lasciano eventi di modifica directory (Event ID 5136/4728/4738)
> - **Prerequisiti:** possesso di un diritto esteso o di scrittura su un oggetto AD (utente, gruppo, computer o oggetto dominio), individuato tipicamente con BloodHound
> - **Tecnica:** `ACL/DACL abuse` | **Severity tipica:** `Alto` (fino a `Critico` se porta a DCSync) | **Finding ID:** da assegnare in lab (metodologia)

- Natura del documento: metodologia. Output illustrativi; identificativi segnaposto.
- Obiettivo: convertire un diritto su un oggetto AD in un'escalation concreta (reset di password, aggiunta a un gruppo privilegiato, concessione a se stessi dei diritti di replica).

---

## Executive summary

Le ACL di Active Directory definiscono chi puo fare cosa su ogni oggetto. Alcuni diritti, se concessi a
principal non fidati (per errore, ereditarieta o deleghe amministrative troppo ampie), si traducono
direttamente in escalation:

- **GenericAll / GenericWrite:** controllo pieno o scrittura sull'oggetto, da cui reset password (su un
  utente), aggiunta di membri (su un gruppo), o scrittura di attributi sensibili.
- **WriteDACL:** possibilita di modificare la stessa ACL dell'oggetto, quindi di concedersi qualunque altro
  diritto (incluso, sull'oggetto dominio, i diritti di replica per DCSync).
- **WriteOwner:** diventare proprietario dell'oggetto e poi riscriverne l'ACL.
- **AddKeyCredentialLink:** scrivere `msDS-KeyCredentialLink` per abilitare l'autenticazione via certificato
  come la vittima (Shadow Credentials).

BloodHound evidenzia queste relazioni come archi nel grafo: una catena di ACL mal poste e un percorso verso
il dominio.

## Contesto operativo (perche, prima del come)

L'abuso di ACL e il "collante" di molte catene BloodHound: raramente un singolo diritto porta a Domain
Admin, ma una sequenza (A puo resettare B, B ha WriteDACL su C, C e in un gruppo privilegiato) si. La
decisione operativa e scegliere l'azione meno rumorosa e piu reversibile che avanza nella catena: spesso
l'aggiunta temporanea a un gruppo o un reset di password, da annullare a fine test per ridurre l'impatto sul
cliente.

## Esecuzione / comandi

### GenericAll su un utente: reset password

```bash
# Con GenericAll/ForceChangePassword su un utente, ne imposta una nuova password
net rpc password "utente_bersaglio" "NuovaPass123!" -U "corp.local/utente%Password123" -S 10.10.10.10
```

### GenericAll su un gruppo: aggiunta membro

```bash
# Con diritti sul gruppo, aggiunge l'account controllato a un gruppo privilegiato
net rpc group addmem "GruppoPrivilegiato" "utente" -U "corp.local/utente%Password123" -S 10.10.10.10
```

### WriteDACL sull'oggetto dominio: concedersi DCSync

```bash
# Si concede all'account i diritti di replica (DS-Replication-Get-Changes*) -> abilita DCSync
dacledit.py -action write -rights DCSync -principal utente -target-dn 'DC=corp,DC=local' \
  corp.local/utente:'Password123'
```

Output illustrativo (rappresentativo):

```
[*] DACL modified successfully! 'utente' now has replication rights   <-- ora puo fare DCSync
```

## Analisi dei risultati

L'esito dipende dal diritto e dall'oggetto: un reset password fornisce un account aggiuntivo, l'aggiunta a
un gruppo privilegiato fornisce i privilegi del gruppo, la concessione dei diritti di replica porta
direttamente a DCSync (severity `Critico`). La severity tipica e `Alto`, ma sale a `Critico` quando la
catena termina nel dominio completo. Il finding reale va documentato indicando il diritto sfruttato,
l'azione eseguita e il risultato.

### Analisi teorica

Le ACL sono il meccanismo con cui AD implementa il controllo d'accesso discrezionale sugli oggetti. La loro
sicurezza e una proprieta dell'intero grafo delle autorizzazioni (proprieta P3): un singolo diritto puo
essere innocuo, ma la composizione di piu diritti crea percorsi di escalation. WriteDACL e particolarmente
critico perche e "meta": permette di modificare i permessi stessi, quindi di auto-concedersi qualunque altro
diritto, incluso quello di replica che abilita DCSync. E il motivo per cui BloodHound modella queste
relazioni come archi: il problema non e il singolo permesso ma la raggiungibilita nel grafo. Vedi
[THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.md>).

## Remediation (blue team)

**Rilevamento.** Event ID 5136 (modifica oggetto directory) su oggetti/attributi sensibili; 4728/4732
(aggiunta a gruppo privilegiato); 4724 (reset password); modifiche alla DACL dell'oggetto dominio.

**Hardening.** Audit periodico delle ACL con BloodHound/strumenti dedicati per individuare e rimuovere i
diritti eccessivi; applicare il Tiering Model; limitare le deleghe amministrative ampie; monitorare in
modo prioritario le modifiche alla DACL dell'oggetto dominio (precursore di DCSync).

---

## Scenario reale: proiezione Post-Exploitation

> Quando la catena ACL termina con i diritti di replica, l'esito e il dominio (severity Critico).

### Prospettiva attaccante (red team)

**Punto di partenza:** un diritto su un oggetto AD (da BloodHound), es. WriteDACL su un gruppo o sull'oggetto
dominio.

**Passo successivo immediato:** sfruttare il diritto per avanzare nella catena (reset, add-member, o
concessione DCSync).

**Kill Chain proiettata:**

```
Diritto ACL su un oggetto (da BloodHound)
        |
        v
Avanzamento nella catena (reset password / add a gruppo / WriteDACL)
        |
        v
WriteDACL sull'oggetto dominio -> auto-concessione dei diritti di replica
        |
        v
DCSync -> dominio completo -> Golden Ticket / persistenza
```

**Impatto potenziale:** compromissione del dominio tramite concatenazione di diritti ACL, spesso senza un
singolo exploit.

**Vettori di monetizzazione tipici:** ransomware/esfiltrazione a valle del dominio; access brokering.

### Prospettiva difensore (blue team)

**Rilevamento:** Event ID 5136 sulla DACL del dominio; 4728/4724 per aggiunte a gruppo e reset password
anomali.

**Indicatori di Compromissione (IOC):** concessione di diritti di replica a un account non-DC; aggiunta
inattesa a gruppi privilegiati; reset di password non richiesti dall'help desk.

**Contenimento:** revoca dei diritti concessi in modo anomalo; rimozione dai gruppi; reset degli account
coinvolti; indagine sulle repliche recenti (se concessi i diritti DCSync).

**Eradicazione e hardening:** bonifica delle ACL eccessive (audit BloodHound); Tiering Model; monitoraggio
prioritario della DACL del dominio.

**Lezione difensiva:** la sicurezza di AD e una proprieta del grafo complessivo dei permessi. Un diritto
"piccolo" nel posto sbagliato puo essere l'anello che apre la catena verso il dominio. La difesa e l'audit
sistematico delle ACL, non il controllo del singolo oggetto.

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `dacledit.py` (impacket) | ad tool | cli - attivo | lettura/scrittura delle dacl (es. concessione diritti dcsync) |
| `net rpc` (samba) | ad tool | cli - attivo | reset password e gestione gruppi via rpc |
| `PowerView` | powershell | cli - attivo | enumerazione e abuso acl da host windows |
| `BloodHound` | graph enum | gui | individuazione delle relazioni acl sfruttabili |
| `bloodyAD` | ad tool | cli - attivo | manipolazione di oggetti e attributi ad da linux |

## Note di metodologia

In lab reale documentare: il diritto ACL individuato (da BloodHound), l'azione eseguita (reset/add/WriteDACL)
e il risultato. Importante lato etico/operativo: annullare le modifiche (rimuovere da gruppi, ripristinare
ACL) a fine test per non lasciare il dominio in stato alterato.

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| persistence | account manipulation | `T1098` | modifica di oggetti/attributi ad (reset password, add a gruppo, dacl). |
| privilege escalation | domain or tenant policy modification | `T1484` | modifica di permessi a livello di dominio (writedacl sull'oggetto dominio). |
| credential access | os credential dumping: dcsync | `T1003.006` | esito: auto-concessione dei diritti di replica e dcsync. |

## Correlazioni con altri moduli

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| [bloodhound](<../../01-enumeration/bloodhound/README.md>) | acl abuse | individua i diritti acl e le catene sfruttabili |
| acl abuse (writedacl su dominio) | [dcsync](<../../05-credential-dumping/dcsync/README.md>) | l'auto-concessione dei diritti di replica abilita dcsync |
| acl abuse (addkeycredentiallink) | [shadow credentials](<../../05-credential-dumping/shadow-credentials/README.md>) | scrittura di msds-keycredentiallink per auth via certificato |

---

> **Nota:** Contenuto didattico e di metodologia. Esecuzione solo in laboratori propri o con autorizzazione esplicita. Output illustrativi, non da sistemi reali.
