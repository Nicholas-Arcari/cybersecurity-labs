> [English](README.en.md) | **Italiano**

# 11 - Active Directory (Windows Domain)

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

| Sottocartella | Tema | Stato |
| :--- | :--- | :--- |
| `01-enumeration/` | Enumerazione del dominio: BloodHound, LDAP/RPC/SMB, kerbrute (user enum + spraying) | Completa (IT) |
| `02-kerberos-attacks/` | Attacchi a Kerberos: Kerberoasting, AS-REP Roasting, Golden/Silver Ticket e le varianti stealth Diamond/Sapphire | Completa |
| `03-adcs/` | Abuso di AD CS: enumerazione ESC, ESC1 (template SAN), ESC8 (NTLM relay) | Completa |
| `04-delegation-acl/` | Abuso di deleghe Kerberos (RBCD, unconstrained/constrained) e di ACL/DACL | Completa |
| `05-credential-dumping/` | Dump credenziali di dominio: DCSync, Shadow Credentials, NTDS.dit | Completa |
| `06-domain-privesc-cve/` | Escalation di dominio via CVE: noPac (CVE-2021-42278/42287) | Completa |

Il modulo e bilingue (IT + EN) e comprende 18 pagine tecniche piu gli scaffold. Resta, per ogni tecnica,
l'assegnazione dei Finding ID reali (`AD-NNN`) all'esecuzione in un laboratorio AD (es. GOAD o macchine HTB).

## Flusso operativo consigliato

1. **Enumerazione prima di tutto** (`01-enumeration/`): con un account di dominio, mappare la foresta con BloodHound. I percorsi di attacco emergono dai dati, non da tentativi ciechi.
2. **Raccolta credenziali a basso costo** (`02-kerberos-attacks/`): Kerberoasting e AS-REP Roasting non richiedono privilegi elevati e spesso restituiscono hash di service account deboli.
3. **Escalation per misconfiguration** (`03-adcs/`, `04-delegation-acl/`): AD CS e le deleghe/ACL mal configurate sono oggi i vettori piu comuni verso privilegi di dominio, spesso piu delle CVE.
4. **Dominio completo** (`05-credential-dumping/`): con privilegi di replica, DCSync estrae tutti gli hash, incluso quello di `krbtgt`.
5. **Persistenza**: il Golden Ticket (da krbtgt) e la persistenza di dominio per eccellenza, trattata al confine con il modulo 07.

## Registro Finding

> Modulo in metodologia: nessun Finding ID e ancora assegnato. Verranno attribuiti (sequenza `AD-001`+) all'esecuzione in laboratorio reale. La colonna "Severity tipica" indica la gravita attesa della tecnica in un contesto reale.

| Tecnica | Sottocartella | Severity tipica | Finding ID |
| :--- | :--- | :---: | :---: |
| BloodHound (mappatura percorsi) | `01-enumeration/bloodhound/` | `Informativo` | da assegnare in lab |
| Enumerazione LDAP/RPC/SMB | `01-enumeration/domain-enumeration/` | `Basso` | da assegnare in lab |
| Kerbrute (user enum + spraying) | `01-enumeration/kerbrute-userenum/` | `Variabile (Basso / Alto)` | da assegnare in lab |
| Kerberoasting | `02-kerberos-attacks/kerberoasting/` | `Alto` | da assegnare in lab |
| AS-REP Roasting | `02-kerberos-attacks/as-rep-roasting/` | `Alto` | da assegnare in lab |
| Golden Ticket | `02-kerberos-attacks/golden-ticket/` | `Critico` | da assegnare in lab |
| Silver Ticket | `02-kerberos-attacks/silver-ticket/` | `Alto` | da assegnare in lab |
| Diamond Ticket (variante stealth) | `02-kerberos-attacks/diamond-ticket/` | `Critico` | da assegnare in lab |
| Sapphire Ticket (PAC autentico S4U2self) | `02-kerberos-attacks/sapphire-ticket/` | `Critico` | da assegnare in lab |
| AD CS enumeration (ESC) | `03-adcs/esc-enumeration/` | `Informativo` | da assegnare in lab |
| AD CS ESC1 (template SAN arbitrario) | `03-adcs/esc1-template-abuse/` | `Critico` | da assegnare in lab |
| AD CS ESC8 (NTLM relay to Web Enrollment) | `03-adcs/esc8-relay-adcs/` | `Critico` | da assegnare in lab |
| RBCD abuse | `04-delegation-acl/rbcd/` | `Critico` | da assegnare in lab |
| Unconstrained/Constrained Delegation | `04-delegation-acl/delegation-unconstrained-constrained/` | `Critico` | da assegnare in lab |
| ACL/DACL abuse | `04-delegation-acl/acl-abuse/` | `Alto` (fino a `Critico`) | da assegnare in lab |
| DCSync | `05-credential-dumping/dcsync/` | `Critico` | da assegnare in lab |
| Shadow Credentials | `05-credential-dumping/shadow-credentials/` | `Alto` | da assegnare in lab |
| NTDS.dit dump | `05-credential-dumping/secretsdump-ntds/` | `Critico` | da assegnare in lab |
| noPac (CVE-2021-42278/42287) | `06-domain-privesc-cve/nopac/` | `Critico` | da assegnare in lab |

## Mappatura MITRE ATT&CK (aggregata)

| Tattica | Tecnica | ID MITRE | Tecnica correlata |
| :--- | :--- | :--- | :--- |
| Discovery | Account Discovery: Domain Account | `T1087.002` | Enumerazione (BloodHound, LDAP, kerbrute) |
| Discovery | Permission Groups Discovery: Domain Groups | `T1069.002` | Enumerazione gruppi |
| Discovery | Domain Trust Discovery | `T1482` | BloodHound |
| Discovery | Password Policy Discovery | `T1201` | Enumerazione pre-spraying |
| Credential Access | Brute Force: Password Spraying | `T1110.003` | Kerbrute spraying |
| Credential Access | Steal or Forge Kerberos Tickets: Kerberoasting | `T1558.003` | Kerberoasting |
| Credential Access | Steal or Forge Kerberos Tickets: AS-REP Roasting | `T1558.004` | AS-REP Roasting |
| Credential Access | Steal or Forge Kerberos Tickets: Golden Ticket | `T1558.001` | Golden Ticket / Diamond Ticket / Sapphire Ticket |
| Credential Access | Steal or Forge Kerberos Tickets: Silver Ticket | `T1558.002` | Silver Ticket |
| Credential Access | Steal or Forge Authentication Certificates | `T1649` | AD CS ESC1 / ESC8 / Shadow Credentials |
| Credential Access | Adversary-in-the-Middle: LLMNR/NBT-NS Poisoning and SMB Relay | `T1557.001` | AD CS ESC8 |
| Credential Access | Forced Authentication | `T1187` | ESC8 / unconstrained delegation (coercizione) |
| Credential Access | OS Credential Dumping: DCSync | `T1003.006` | DCSync / ACL abuse (WriteDACL) / noPac |
| Credential Access | OS Credential Dumping: NTDS | `T1003.003` | NTDS.dit dump |
| Persistence | Account Manipulation | `T1098` | RBCD / ACL abuse / Shadow Credentials / Diamond / Sapphire |
| Persistence | Create Account: Domain Account | `T1136.002` | noPac (creazione computer account) |
| Privilege Escalation | Exploitation for Privilege Escalation | `T1068` | noPac (CVE-2021-42278 + 42287) |
| Privilege Escalation | Domain or Tenant Policy Modification | `T1484` | ACL abuse (DACL dominio) |
| Lateral Movement | Use Alternate Authentication Material: Pass the Ticket | `T1550.003` | Delegation abuse / ticket forgiati |
| Lateral Movement | Use Alternate Authentication Material: Pass the Hash | `T1550.002` | DCSync / NTDS (follow-on) |

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `BloodHound` / `SharpHound` | Graph enumeration | CLI/GUI - Attivo | Mappa dei percorsi di attacco nel dominio (ACL, sessioni, deleghe) |
| `NetExec` (`nxc`) | Swiss-army AD/SMB | CLI - Attivo | Enumerazione e azione di massa su SMB/LDAP/WinRM; successore di CrackMapExec |
| `Impacket` (suite) | Python toolkit | CLI - Attivo | GetUserSPNs, secretsdump, ntlmrelayx, ticketer e altri |
| `Rubeus` | .NET Kerberos tool | CLI - Attivo | Kerberoasting, AS-REP, manipolazione ticket da host Windows |
| `Certipy` | AD CS toolkit | CLI - Attivo | Enumerazione e abuso di AD CS (ESC1-ESC16) |
| `ldapsearch` / `windapsearch` | LDAP client | CLI - Attivo | Enumerazione LDAP del dominio |
| `kerbrute` | Kerberos pre-auth | CLI - Attivo | User enumeration e password spraying via Kerberos |
| `hashcat` | GPU cracking | CLI - Offline | Cracking di hash Kerberos (modi 13100/18200) e NTLM (1000) |

## Collegamento ad altri moduli

- A monte: [04-system-exploitation](<../04-system-exploitation/README.md>) (accesso ed escalation locale) e [07-post-exploitation](<../07-post-exploitation/README.md>) (credential dumping locale, pivoting).
- Primo accesso tipico: password spraying e phishing da [05-social-engineering](<../05-social-engineering/README.md>); credenziali da relay/poisoning.
- Difesa: contromisure correlate in [08-defense-hardenings](<../08-defense-hardenings (Blue Team Prevention)/README.md>) (SIEM/XDR, hardening).

---

> **Nota:** Modulo a scopo didattico e di documentazione di metodologia. Le tecniche descritte vanno eseguite esclusivamente in laboratori di proprieta o su sistemi con autorizzazione esplicita. Gli output sono illustrativi e non provengono da sistemi reali o di terze parti.
