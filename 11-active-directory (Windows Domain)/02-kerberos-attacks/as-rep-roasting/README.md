> [English](README.en.md) | **Italiano**

# AS-REP Roasting: furto offline per account senza pre-autenticazione

> - **Fase:** Credential Access (dominio Active Directory)
> - **Visibilita:** Bassa-Media - genera AS-REQ/AS-REP (Event ID 4768) per gli account bersaglio; piu discreto del Kerberoasting se mirato
> - **Prerequisiti:** esistenza di account con "Do not require Kerberos preauthentication" attivo; per scoprirli serve un account di dominio (via LDAP) oppure una lista di username (attacco senza credenziali)
> - **Tecnica:** `AS-REP Roasting` | **Severity tipica:** `Alto` | **Finding ID:** da assegnare in lab (metodologia)

- Natura del documento: metodologia. Output illustrativi; hash di esempio troncati e non craccabili.
- Obiettivo: ottenere materiale crackabile offline per gli account con pre-autenticazione Kerberos disabilitata, senza conoscerne la password.

---

## Executive Summary

AS-REP Roasting e il gemello del Kerberoasting applicato alla fase iniziale del flusso Kerberos. Quando un
account ha disabilitato la pre-autenticazione (flag `DONT_REQ_PREAUTH`), il KDC risponde a un AS-REQ con un
AS-REP contenente una porzione cifrata con la chiave derivata dalla password dell'utente, senza prima
verificare che il richiedente conosca quella password. Chiunque, anche senza credenziali, puo quindi
richiedere l'AS-REP di un account vulnerabile e attaccarne offline la password.

La pre-autenticazione disabilitata e una misconfigurazione, talvolta ereditata da applicazioni legacy o
impostata per comodita. A differenza del Kerberoasting (che colpisce i service account), AS-REP Roasting
colpisce qualunque utente con quel flag, inclusi utenti normali con password deboli.

## Contesto operativo (perche, prima del come)

Il costo e bassissimo: se l'enumerazione LDAP rivela account con `DONT_REQ_PREAUTH`, l'attacco e immediato e
offline. Puo funzionare anche senza credenziali, se si dispone di una lista di username (es. da user
enumeration via kerbrute), provando quali rispondono con un AS-REP crackabile. La decisione operativa e
mirare gli account trovati invece di spazzolare l'intero dominio, riducendo gli Event ID 4768 generati.

## Esecuzione / Comandi

### Da Linux (Impacket GetNPUsers)

```bash
# Con credenziali: trova e roasta gli account senza pre-auth
GetNPUsers.py corp.local/utente:'Password123' -dc-ip 10.10.10.10 -request -format hashcat -outputfile asrep.txt
```

```bash
# Senza credenziali: prova una lista di username (solo quelli senza pre-auth risponderanno)
GetNPUsers.py corp.local/ -dc-ip 10.10.10.10 -usersfile users.txt -format hashcat -no-pass
```

Output illustrativo (hash troncato, non craccabile):

```
$krb5asrep$23$j.legacy@CORP.LOCAL:a1b2...[TRONCATO]...9f   <-- etype 23: crackabile offline
```

### Cracking offline

```bash
# Modo 18200 = Kerberos 5 AS-REP etype 23 (RC4)
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt
```

## Analisi dei risultati

Una password recuperata fornisce un account di dominio valido (foothold) o, se l'account e privilegiato, un
salto diretto. Come per il Kerberoasting, il successo dipende dall'entropia della password: un account con
pre-auth disabilitata ma password robusta produce un hash non craccabile in tempi utili. Severity reale
`Alto` se la password viene recuperata, altrimenti il finding e la sola misconfigurazione (`Medio`:
pre-auth disabilitata e un indebolimento, anche se la password resiste).

### Analisi Teorica

Il flusso Kerberos (vedi [THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.md>), sez. 3.1) prevede la
pre-autenticazione proprio per impedire questo attacco: normalmente il client deve inviare un timestamp
cifrato con la propria chiave nell'AS-REQ, dimostrando di conoscere la password prima che il KDC emetta
l'AS-REP. Disabilitare la pre-auth rimuove questa prova e trasforma l'AS-REP in un oracolo offline sulla
password (violazione della proprieta P2). E l'esempio piu pulito di come una "comodita" di configurazione
annulli una contromisura progettata appositamente.

## Remediation (Blue Team)

**Rilevamento.** Event ID 4768 per account con pre-auth disabilitata, specie in volume o con etype RC4;
richieste AS-REP da sorgenti inattese; account honeypot con il flag impostato come esca.

**Hardening.** Rimuovere il flag `DONT_REQ_PREAUTH` ovunque non sia strettamente necessario (verifica
periodica via LDAP); dove e inevitabile per compatibilita, imporre password lunghe e casuali e monitorare;
disabilitare RC4 a favore di AES.

---

## Scenario Reale: Proiezione Post-Exploitation

> Vale per l'esito "password recuperata" (severity Alto).

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** lista di account con pre-auth disabilitata (da LDAP o tentativo su lista username).

**Passo successivo immediato:** roast e cracking offline; con la password, accesso come l'utente.

**Kill Chain proiettata:**

```
Account senza pre-auth individuato
        |
        v
AS-REP Roasting -> hash crackabile offline
        |
        v
Password recuperata -> foothold di dominio (o account privilegiato)
        |
        v
BloodHound + escalation (ACL/deleghe/ADCS) -> DCSync -> dominio
```

**Impatto potenziale:** da nessuna o bassa credenziale a foothold di dominio, per una singola
misconfigurazione combinata con una password debole.

**Vettori di monetizzazione tipici:** come per le altre catene AD (ransomware, esfiltrazione, access
brokering) a valle dell'escalation.

### Prospettiva Difensore (Blue Team)

**Rilevamento:** 4768 anomali per account con pre-auth disabilitata; etype RC4 inatteso.

**Indicatori di Compromissione (IOC):** richieste AS-REP per account `DONT_REQ_PREAUTH` da host non
legittimi; cracking seguito da login dell'account.

**Contenimento:** reset della password dell'account esposto; rimozione del flag; indagine sugli accessi.

**Eradicazione e hardening:** audit periodico del flag su tutto il dominio; password robuste dove il flag e
inevitabile; disabilitazione RC4.

**Lezione difensiva:** la pre-autenticazione esiste per impedire proprio questo. Disabilitarla "per far
funzionare un'app" reintroduce una debolezza che il protocollo aveva gia chiuso.

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `GetNPUsers.py` (Impacket) | Python toolkit | CLI - Attivo | Scoperta e roasting degli account senza pre-auth da Linux |
| `Rubeus` | .NET tool | CLI - Attivo | AS-REP Roasting da host Windows |
| `hashcat` | GPU cracker | CLI - Offline | Cracking degli hash AS-REP (modo 18200) |
| `ldapsearch` / `nxc` | Enum | CLI - Attivo | Individuazione degli account con `DONT_REQ_PREAUTH` |

## Note di metodologia

In lab reale documentare: quali account hanno pre-auth disabilitata, l'esito del cracking e la relativa
severity. Da provare anche la variante senza credenziali su una lista di username (dimostra che l'attacco
non presuppone un foothold).

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Credential Access | Steal or Forge Kerberos Tickets: AS-REP Roasting | `T1558.004` | Richiesta di AS-REP per account senza pre-auth e cracking offline. |
| Discovery | Account Discovery: Domain Account | `T1087.002` | Individuazione degli account con pre-auth disabilitata. |
| Credential Access | Brute Force: Password Cracking | `T1110.002` | Cracking offline dell'hash AS-REP. |

## Correlazioni con altri moduli

| Provenienza | Questa tecnica | Effetto |
| :--- | :--- | :--- |
| [domain-enumeration](<../../01-enumeration/domain-enumeration/README.md>) / [kerbrute](<../../01-enumeration/kerbrute-userenum/README.md>) | AS-REP Roasting | forniscono gli account bersaglio o la lista username |
| AS-REP Roasting | [hashcat](<../../../04-system-exploitation/05-password-cracking/hashcat/README.md>) | cracking offline con i tool gia nel repo |
| AS-REP Roasting | [Kerberoasting](<../kerberoasting/README.md>) | tecnica gemella: insieme coprono entrambe le estremita del flusso Kerberos |

---

> **Nota:** Contenuto didattico e di metodologia. Esecuzione solo in laboratori propri o con autorizzazione esplicita. Output illustrativi, non da sistemi reali.
