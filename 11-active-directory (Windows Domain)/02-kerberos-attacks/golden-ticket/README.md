> [English](README.en.md) | **Italiano**

# Golden ticket: persistenza di dominio tramite forgiatura del TGT

> - **Fase:** Persistence / Privilege Escalation (dominio Active Directory)
> - **Visibilita:** Bassa all'emissione (il ticket e forgiato offline, nessuna richiesta al KDC), potenzialmente rilevabile all'uso (anomalie nel ticket)
> - **Prerequisiti:** possesso dell'hash NT (o chiave AES) dell'account `krbtgt` e del SID del dominio; entrambi si ottengono tipicamente da un DCSync
> - **Tecnica:** `Golden Ticket` | **Severity tipica:** `Critico` | **Finding ID:** da assegnare in lab (metodologia)

- Natura del documento: metodologia. Output illustrativi; chiavi/SID segnaposto.
- Obiettivo: forgiare un TGT valido per qualunque identita e con privilegi arbitrari, ottenendo accesso persistente e difficile da sradicare al dominio.

---

## Executive summary

Il Golden Ticket e la persistenza di dominio per eccellenza. Il TGT (Ticket Granting Ticket) e cifrato e
firmato con la chiave dell'account `krbtgt`: chi possiede quella chiave puo forgiare TGT arbitrari, per
qualunque utente (anche inesistente) e con qualunque appartenenza di gruppo, senza interagire con il KDC per
l'emissione. Il DC accettera questi ticket come legittimi, perche sono firmati con la chiave corretta.

E lo stadio finale tipico dopo un DCSync: con l'hash di `krbtgt` ottenuto, l'attaccante si garantisce un
accesso che sopravvive al reset delle password degli utenti. L'unico modo per invalidare un Golden Ticket e
cambiare la password di `krbtgt` due volte (AD mantiene la chiave corrente e la precedente), operazione che
molte organizzazioni non eseguono mai.

## Contesto operativo (perche, prima del come)

Il Golden Ticket non e un vettore di accesso iniziale ma di persistenza e dominio totale: presuppone di
avere gia compromesso krbtgt. Si colloca a valle del [DCSync](<../../05-credential-dumping/dcsync/README.md>).
La decisione operativa riguarda la OPSEC: i Golden Ticket con parametri anomali (durata decennale, utente
inesistente, gruppi incoerenti) sono piu facili da rilevare. Un operatore attento forgia ticket con
parametri plausibili (durata standard, utente reale) per ridurre i segnali, e usa AES invece di RC4 per
evitare la detection basata su downgrade.

## Esecuzione / comandi

### Forgiatura (Impacket ticketer)

```bash
# Forgia un TGT usando l'hash NT di krbtgt e il SID del dominio; produce un file .ccache
ticketer.py -nthash <HASH_KRBTGT> -domain-sid S-1-5-21-<SEGNAPOSTO> -domain corp.local fakeadmin
```

```bash
# Uso del ticket forgiato: esportare la variabile e autenticarsi senza password
export KRB5CCNAME=fakeadmin.ccache
secretsdump.py -k -no-pass corp.local/fakeadmin@dc01.corp.local
```

### Forgiatura (Mimikatz, da Windows)

```
kerberos::golden /user:fakeadmin /domain:corp.local /sid:S-1-5-21-<SEGNAPOSTO> /krbtgt:<HASH_KRBTGT> /ptt
```

Output illustrativo (rappresentativo):

```
[*] Saving ticket in fakeadmin.ccache
# il ticket e ora utilizzabile per autenticarsi come 'fakeadmin' con privilegi arbitrari
```

## Analisi dei risultati

Il Golden Ticket trasforma il possesso di una chiave (krbtgt) in controllo persistente del dominio. Non e
un "accesso in piu": e una chiave maestra che bypassa l'autenticazione normale. La severity e `Critico`
perche l'impatto e il controllo duraturo e la difficolta di eradicazione: finche krbtgt non viene ruotato
due volte, i ticket forgiati restano validi anche dopo il reset di tutte le altre password.

### Analisi teorica

La radice del Golden Ticket e strutturale in Kerberos (vedi
[THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.md>), sez. 3.1): il TGT e cifrato e firmato con la
chiave di krbtgt, e il DC si fida di qualunque TGT firmato correttamente, senza ulteriore verifica
dell'identita del richiedente al momento dell'uso. Chi conosce la chiave di krbtgt puo quindi impersonare il
KDC nella parte di emissione. E la violazione piu profonda della proprieta P1 (autenticazione): l'attaccante
non si autentica, falsifica il materiale che prova l'autenticazione. Il fatto che la revoca richieda un
doppio reset di krbtgt deriva dalla gestione a due chiavi (corrente/precedente) pensata per la continuita
della replica, non per la sicurezza offensiva.

## Remediation (blue team)

**Rilevamento.** TGT con durata anomala (molto oltre il default di 10 ore / 7 giorni di rinnovo); ticket per
utenti inesistenti o con gruppi incoerenti rispetto all'oggetto reale; uso di RC4 dove ci si attende AES;
anomalie nel PAC. Soluzioni come la detection comportamentale di EDR/AD cercano proprio queste incoerenze.

**Hardening.** Proteggere krbtgt (la sua compromissione e il vero problema: vedi DCSync); in caso di
sospetta compromissione, ruotare la password di krbtgt due volte in sequenza controllata; applicare il
Tiering Model e limitare i diritti di replica per impedire a monte l'ottenimento della chiave; monitorare i
parametri dei TGT.

---

## Scenario reale: proiezione Post-Exploitation

> Il Golden Ticket e gia una fase avanzata: lo scenario descrive la persistenza e le sue conseguenze.

### Prospettiva attaccante (red team)

**Punto di partenza:** hash di krbtgt ottenuto (tipicamente via DCSync) e SID del dominio noto.

**Passo successivo immediato:** forgiatura di un TGT con parametri plausibili e sua iniezione in sessione.

**Kill Chain proiettata:**

```
Hash di krbtgt (da DCSync)
        |
        v
Golden Ticket forgiato (TGT arbitrario, firmato con krbtgt)
        |
        v
Accesso a qualunque servizio del dominio come qualunque utente
        |
        v
Persistenza duratura: sopravvive al reset delle password utente
        |
        v
Esfiltrazione continuativa / re-ingresso a piacere / ransomware su tutto il dominio
```

**Impatto potenziale:** controllo persistente del dominio. E uno degli scenari piu gravi in assoluto per
un'organizzazione, perche la bonifica richiede un intervento specifico (doppio reset krbtgt) spesso ignoto
ai team non specializzati.

**Vettori di monetizzazione tipici:** accesso persistente rivenduto; ransomware ritardato; esfiltrazione
prolungata di dati.

### Prospettiva difensore (blue team)

**Rilevamento:** anomalie nei TGT (durata, utente, gruppi, etype); uso di ticket per account inesistenti.

**Indicatori di Compromissione (IOC):** ticket con lifetime fuori policy; TGT RC4 in ambiente AES; attivita
privilegiata da un principal che non risulta aver fatto login al KDC.

**Contenimento:** doppio reset di krbtgt; invalidazione delle sessioni; caccia agli accessi effettuati con
ticket forgiati.

**Eradicazione e hardening:** prevenire a monte la compromissione di krbtgt (confinamento dei diritti di
replica, Tiering); rotazione pianificata di krbtgt; monitoraggio dei parametri dei ticket.

**Lezione difensiva:** una volta compromesso krbtgt, il dominio e compromesso in modo persistente. La difesa
non e "rilevare il Golden Ticket" ma impedire che krbtgt venga mai esfiltrato, e saper eseguire la rotazione
corretta quando necessario.

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `ticketer.py` (impacket) | kerberos tool | cli - attivo | forgiatura del golden ticket da linux |
| `Mimikatz` | credential/ticket tool | cli - attivo | `kerberos::golden` da host windows, con iniezione (ptt) |
| `Rubeus` | .net kerberos tool | cli - attivo | forgiatura/uso ticket e manipolazione da windows |
| `klist` / `kinit` | kerberos nativi | cli | gestione e verifica dei ticket in cache |

## Note di metodologia

In lab reale documentare: la forgiatura a partire dall'hash krbtgt ottenuto in DCSync, l'uso del ticket per
accedere a un servizio, e la prova che sopravvive al reset di una password utente. Documentare anche la
procedura di bonifica (doppio reset krbtgt) come contromisura verificata.

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| credential access | steal or forge kerberos tickets: golden ticket | `T1558.001` | forgiatura di un tgt arbitrario firmato con la chiave di krbtgt. |
| persistence | account manipulation | `T1098` | accesso persistente al dominio indipendente dalle credenziali utente. |
| lateral movement | use alternate authentication material: pass the ticket | `T1550.003` | uso del ticket forgiato per autenticarsi ai servizi. |

## Correlazioni con altri moduli

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| [dcsync](<../../05-credential-dumping/dcsync/README.md>) | golden ticket | fornisce l'hash di krbtgt, prerequisito della forgiatura |
| golden ticket | [07-post-exploitation - persistence](<../../../07-post-exploitation/README.md>) | e la forma di persistenza di dominio piu potente |
| [silver ticket](<../silver-ticket/README.md>) | golden ticket | il silver e la variante limitata a un servizio; il golden e dominio-wide |

---

> **Nota:** Contenuto didattico e di metodologia. Esecuzione solo in laboratori propri o con autorizzazione esplicita. Output illustrativi, non da sistemi reali.
