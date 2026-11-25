> [English](README.en.md) | **Italiano**

# 11 - Active Directory (Windows domain)

> - **Fase:** Exploitation e Post-Exploitation del dominio Windows - dal primo accesso autenticato al Domain Admin
> - **Visibilita:** Variabile - alcune tecniche sono rumorose (Kerberoasting, NTLM relay), altre quasi silenti (DCSync, abuso di ACL con credenziali legittime)
> - **Prerequisiti:** connettivita verso un Domain Controller; in genere un primo set di credenziali di dominio valide (anche basso privilegio) ottenute dai moduli precedenti (phishing, password spraying, credenziali in chiaro, relay)
> - **Natura del modulo:** metodologia. Gli output mostrati sono illustrativi e rappresentativi, non provenienti da un lab specifico. I Finding ID (`AD-NNN`) sono riservati e verranno assegnati quando le tecniche saranno eseguite in un laboratorio AD reale (es. GOAD - Game of Active Directory). Severity indicate come "tipiche" della tecnica.

## Introduzione

Active Directory (AD) e il sistema di gestione delle identita della quasi totalita delle reti aziendali Windows. In un penetration test interno, raramente la compromissione passa per un singolo exploit: passa quasi sempre per l'abuso di funzionalita legittime di AD (Kerberos, repliche, deleghe, autorita di certificazione). Per questo AD merita un modulo dedicato invece di comparire come nota sparsa nel post-exploitation.

Il modulo si colloca a valle dell'accesso iniziale e dell'eventuale escalation locale (moduli 04 e 07) e a monte della persistenza di dominio. Il filo conduttore e il percorso tipico di un operatore red team dentro un dominio:

```
Credenziali di dominio (anche low-priv)
        |
        v
Enumerazione (BloodHound, ldapsearch) -> mappa di utenti, gruppi, ACL, percorsi di attacco
        |
        v
Furto credenziali (Kerberoasting, AS-REP) -> hash crackabili offline di service account
        |
        v
Abuso di configurazioni (AD CS / ESC, deleghe RBCD, ACL) -> escalation a privilegi elevati
        |
        v
Dominio completo (DCSync) -> dump di tutti gli hash, incluso krbtgt
        |
        v
Persistenza (Golden Ticket) -> accesso duraturo e difficile da sradicare
```

Il modulo e volutamente orientato anche alla difesa: AD e terreno comune di red e blue team, e ogni tecnica porta con se indicatori di rilevamento e contromisure concrete.

## Struttura della cartella

| sottocartella | tema | stato |
| :--- | :--- | :--- |
| `01-enumeration/` | enumerazione del dominio: bloodhound, ldap/rpc/smb, kerbrute (user enum + spraying) | completa (it) |
| `02-kerberos-attacks/` | attacchi a kerberos: kerberoasting, as-rep roasting, golden/silver ticket e le varianti stealth diamond/sapphire | completa |
| `03-adcs/` | abuso di ad cs: enumerazione esc, esc1 (template san), esc8 (ntlm relay) | completa |
| `04-delegation-acl/` | abuso di deleghe kerberos (rbcd, unconstrained/constrained) e di acl/dacl | completa |
| `05-credential-dumping/` | dump credenziali di dominio: dcsync, shadow credentials, ntds.dit | completa |
| `06-domain-privesc-cve/` | escalation di dominio via cve: nopac (CVE-2021-42278/42287) | completa |

Il modulo e bilingue (IT + EN) e comprende 18 pagine tecniche piu gli scaffold. Resta, per ogni tecnica,
l'assegnazione dei Finding ID reali (`AD-NNN`) all'esecuzione in un laboratorio AD (es. GOAD o macchine HTB).

## Flusso operativo consigliato

1. **Enumerazione prima di tutto** (`01-enumeration/`): con un account di dominio, mappare la foresta con BloodHound. I percorsi di attacco emergono dai dati, non da tentativi ciechi.
2. **Raccolta credenziali a basso costo** (`02-kerberos-attacks/`): Kerberoasting e AS-REP Roasting non richiedono privilegi elevati e spesso restituiscono hash di service account deboli.
3. **Escalation per misconfiguration** (`03-adcs/`, `04-delegation-acl/`): AD CS e le deleghe/ACL mal configurate sono oggi i vettori piu comuni verso privilegi di dominio, spesso piu delle CVE.
4. **Dominio completo** (`05-credential-dumping/`): con privilegi di replica, DCSync estrae tutti gli hash, incluso quello di `krbtgt`.
5. **Persistenza**: il Golden Ticket (da krbtgt) e la persistenza di dominio per eccellenza, trattata al confine con il modulo 07.

## Registro finding

> Modulo in metodologia: nessun Finding ID e ancora assegnato. Verranno attribuiti (sequenza `AD-001`+) all'esecuzione in laboratorio reale. La colonna "Severity tipica" indica la gravita attesa della tecnica in un contesto reale.

| tecnica | sottocartella | severity tipica | finding id |
| :--- | :--- | :---: | :---: |
| bloodhound (mappatura percorsi) | `01-enumeration/bloodhound/` | `Informativo` | da assegnare in lab |
| enumerazione ldap/rpc/smb | `01-enumeration/domain-enumeration/` | `Basso` | da assegnare in lab |
| kerbrute (user enum + spraying) | `01-enumeration/kerbrute-userenum/` | `Variabile (Basso / Alto)` | da assegnare in lab |
| kerberoasting | `02-kerberos-attacks/kerberoasting/` | `Alto` | da assegnare in lab |
| as-rep roasting | `02-kerberos-attacks/as-rep-roasting/` | `Alto` | da assegnare in lab |
| golden ticket | `02-kerberos-attacks/golden-ticket/` | `Critico` | da assegnare in lab |
| silver ticket | `02-kerberos-attacks/silver-ticket/` | `Alto` | da assegnare in lab |
| diamond ticket (variante stealth) | `02-kerberos-attacks/diamond-ticket/` | `Critico` | da assegnare in lab |
| sapphire ticket (pac autentico s4u2self) | `02-kerberos-attacks/sapphire-ticket/` | `Critico` | da assegnare in lab |
| ad cs enumeration (esc) | `03-adcs/esc-enumeration/` | `Informativo` | da assegnare in lab |
| ad cs esc1 (template san arbitrario) | `03-adcs/esc1-template-abuse/` | `Critico` | da assegnare in lab |
| ad cs esc8 (ntlm relay to web enrollment) | `03-adcs/esc8-relay-adcs/` | `Critico` | da assegnare in lab |
| rbcd abuse | `04-delegation-acl/rbcd/` | `Critico` | da assegnare in lab |
| unconstrained/constrained delegation | `04-delegation-acl/delegation-unconstrained-constrained/` | `Critico` | da assegnare in lab |
| acl/dacl abuse | `04-delegation-acl/acl-abuse/` | `Alto` (fino a `Critico`) | da assegnare in lab |
| dcsync | `05-credential-dumping/dcsync/` | `Critico` | da assegnare in lab |
| shadow credentials | `05-credential-dumping/shadow-credentials/` | `Alto` | da assegnare in lab |
| ntds.dit dump | `05-credential-dumping/secretsdump-ntds/` | `Critico` | da assegnare in lab |
| nopac (CVE-2021-42278/42287) | `06-domain-privesc-cve/nopac/` | `Critico` | da assegnare in lab |

## Mappatura MITRE ATT&CK (aggregata)

| tattica | tecnica | id mitre | tecnica correlata |
| :--- | :--- | :--- | :--- |
| discovery | account discovery: domain account | `T1087.002` | enumerazione (bloodhound, ldap, kerbrute) |
| discovery | permission groups discovery: domain groups | `T1069.002` | enumerazione gruppi |
| discovery | domain trust discovery | `T1482` | bloodhound |
| discovery | password policy discovery | `T1201` | enumerazione pre-spraying |
| credential access | brute force: password spraying | `T1110.003` | kerbrute spraying |
| credential access | steal or forge kerberos tickets: kerberoasting | `T1558.003` | kerberoasting |
| credential access | steal or forge kerberos tickets: as-rep roasting | `T1558.004` | as-rep roasting |
| credential access | steal or forge kerberos tickets: golden ticket | `T1558.001` | golden ticket / diamond ticket / sapphire ticket |
| credential access | steal or forge kerberos tickets: silver ticket | `T1558.002` | silver ticket |
| credential access | steal or forge authentication certificates | `T1649` | ad cs esc1 / esc8 / shadow credentials |
| credential access | adversary-in-the-middle: llmnr/nbt-ns poisoning and smb relay | `T1557.001` | ad cs esc8 |
| credential access | forced authentication | `T1187` | esc8 / unconstrained delegation (coercizione) |
| credential access | os credential dumping: dcsync | `T1003.006` | dcsync / acl abuse (writedacl) / nopac |
| credential access | os credential dumping: ntds | `T1003.003` | ntds.dit dump |
| persistence | account manipulation | `T1098` | rbcd / acl abuse / shadow credentials / diamond / sapphire |
| persistence | create account: domain account | `T1136.002` | nopac (creazione computer account) |
| privilege escalation | exploitation for privilege escalation | `T1068` | nopac (CVE-2021-42278 + 42287) |
| privilege escalation | domain or tenant policy modification | `T1484` | acl abuse (dacl dominio) |
| lateral movement | use alternate authentication material: pass the ticket | `T1550.003` | delegation abuse / ticket forgiati |
| lateral movement | use alternate authentication material: pass the hash | `T1550.002` | dcsync / ntds (follow-on) |

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `BloodHound` / `SharpHound` | graph enumeration | cli/gui - attivo | mappa dei percorsi di attacco nel dominio (acl, sessioni, deleghe) |
| `NetExec` (`nxc`) | swiss-army ad/smb | cli - attivo | enumerazione e azione di massa su smb/ldap/winrm; successore di crackmapexec |
| `Impacket` (suite) | python toolkit | cli - attivo | getuserspns, secretsdump, ntlmrelayx, ticketer e altri |
| `Rubeus` | .net kerberos tool | cli - attivo | kerberoasting, as-rep, manipolazione ticket da host windows |
| `Certipy` | ad cs toolkit | cli - attivo | enumerazione e abuso di ad cs (esc1-esc16) |
| `ldapsearch` / `windapsearch` | ldap client | cli - attivo | enumerazione ldap del dominio |
| `kerbrute` | kerberos pre-auth | cli - attivo | user enumeration e password spraying via kerberos |
| `hashcat` | gpu cracking | cli - offline | cracking di hash kerberos (modi 13100/18200) e ntlm (1000) |

## Collegamento ad altri moduli

- A monte: [04-system-exploitation](<../04-system-exploitation/README.md>) (accesso ed escalation locale) e [07-post-exploitation](<../07-post-exploitation/README.md>) (credential dumping locale, pivoting).
- Primo accesso tipico: password spraying e phishing da [05-social-engineering](<../05-social-engineering/README.md>); credenziali da relay/poisoning.
- Difesa: contromisure correlate in [08-defense-hardenings](<../08-defense-hardenings (Blue Team Prevention)/README.md>) (SIEM/XDR, hardening).

---

> **Nota:** Modulo a scopo didattico e di documentazione di metodologia. Le tecniche descritte vanno eseguite esclusivamente in laboratori di proprieta o su sistemi con autorizzazione esplicita. Gli output sono illustrativi e non provengono da sistemi reali o di terze parti.
