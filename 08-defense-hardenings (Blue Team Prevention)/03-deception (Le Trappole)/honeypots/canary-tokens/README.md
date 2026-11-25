> [English](README.en.md) | **Italiano**

# Canary Tokens - Tripwire Digitali per Early Breach Detection

> - **Fase:** Defense & Hardening - Deception & Early Warning
> - **Categoria:** Deception - segnali d'allarme ad alta confidenza
> - **Prerequisiti:** Accesso a un generatore di token (canarytokens.org o istanza self-hosted); posizionamento strategico dei token; canale di notifica (email/webhook)
> - **Output:** Finding DEF-005; tripwire distribuiti nell'ambiente; allarme immediato e ad alta confidenza quando un attaccante interagisce con un'esca

- **Ambiente Operativo:** Ambiente monitorato con token distribuiti su file share, documenti, credenziali fittizie
- **Ruolo:** "Le Trappole" - non difendono, avvisano quando qualcuno e gia dentro
- **Tool principali:** Canarytokens (Thinkst), token self-hosted, honeytoken

---

## Executive Summary

I Canary Token sono tripwire digitali: esche innocue - un documento, una credenziale, un URL, una chiave AWS - che non hanno alcuna funzione legittima e la cui unica ragione di esistere e essere toccate da un attaccante. Nel momento in cui qualcuno apre il documento-esca o usa la credenziale fittizia, il token "chiama casa" e genera un allarme. Poiche nessun utente legittimo ha motivo di interagire con l'esca, ogni attivazione e un segnale ad altissima confidenza: quasi zero falsi positivi.

Questo capovolge l'economia della detection. Le regole SIEM (`../../../01-siem-log-analysis/`) devono distinguere il malevolo dal legittimo in un mare di attivita normale, generando inevitabilmente falsi positivi. Un canary token non ha questo problema: l'attivita normale sull'esca e zero, quindi qualsiasi attivita e anomala per definizione. Il finding DEF-005 documenta questa capacita di early warning: un token che scatta significa che un attaccante e gia oltre il perimetro e sta esplorando.

I canary token sono particolarmente efficaci contro la fase di post-exploitation (`07-post-exploitation`): l'attaccante che ha ottenuto accesso enumera file share, cerca credenziali salvate, apre documenti "interessanti". Un'esca ben posizionata (`passwords.xlsx`, `aws_keys.txt`) e esattamente cio che cerca, e toccarla lo tradisce.

---

## Struttura della cartella

```
canary-tokens/
+-- README.md      # questo file: tripwire digitali per early detection (DEF-005)
+-- img/           # esempi di token e alert di attivazione
```

---

## Deployment di Canary Token

**ID Finding:** `DEF-005` | **Severity:** `Medio` (early warning ad alta confidenza; l'attivazione indica una compromissione gia in corso)

### Contesto operativo

Un canary token e generato come un artefatto che, all'uso, produce una richiesta di rete verso il server del token. Ne esistono molti tipi: URL univoci, documenti Office/PDF con un beacon incorporato, record DNS, chiavi cloud fittizie, file con nomi allettanti. La chiave e il posizionamento: il token va messo dove un attaccante guarderebbe, ma un utente legittimo no.

### PoC - Generazione e posizionamento di un token

```Bash
# Token generato (via canarytokens.org o istanza self-hosted)
# Tipo: Windows Directory / documento esca / chiave AWS fittizia

# Esempio: file esca con nome allettante posizionato su una share interna
/srv/share/finance/passwords_2026.xlsx      # <-- esca (nessun uso legittimo)
```

### PoC - Attivazione del token (attaccante che abbocca)

```
# [Attacco] l'attaccante in post-exploitation enumera la share e apre l'esca
# Il documento contiene un beacon che chiama il server del token

[CANARYTOKEN ALERT] Token triggered
  Token: passwords_2026.xlsx (Excel document)
  Source IP: 10.0.5.42                       <-- host da cui e stato aperto (DEF-005)
  Time: 2026-06-14 03:12:44
  Reminder: "File esca share Finance"
```

### PoC - Chiave AWS fittizia (honeytoken per credenziali)

```
# Una coppia di chiavi AWS fittizie lasciata in un file di config o script.
# Se l'attaccante la trova e prova a usarla, AWS registra la chiamata API
# e il token scatta - rivelando che le credenziali sono state esfiltrate e usate.

[CANARYTOKEN ALERT] AWS API key used
  aws_access_key: AKIA...CANARY
  Source IP: 45.83.x.x  (infrastruttura attaccante)   <-- credenziale esfiltrata usata (DEF-005)
```

### Tuning e Operativita Difensiva

- **Posizionamento strategico:** i token vanno dove l'attaccante cerca (share "Finance"/"IT", file `passwords`, chiavi in script/config, record in Active Directory), mai dove un utente legittimo li aprirebbe per caso
- **Naming credibile:** l'esca deve sembrare vera e preziosa; un nome generico non attira, un nome mirato (`vpn_credentials.txt`, `backup_admin.kdbx`) si
- **Nessuna documentazione interna:** i token non vanno elencati in wiki o documentazione accessibile; la loro efficacia dipende dal fatto che solo il difensore sappia che sono esche
- **Risposta immediata:** un token che scatta e un incidente, non un warning da triage; la procedura di risposta deve partire subito (l'attaccante e gia dentro)

---

## Esperienza di Laboratorio

Ho posizionato diversi tipi di token nell'ambiente di laboratorio e poi ho "indossato il cappello dell'attaccante", ripetendo l'enumerazione post-exploitation del modulo 07. L'esperimento e stato illuminante: durante l'enumerazione della share, il file `passwords_2026.xlsx` era esattamente cio che il mio io-attaccante avrebbe aperto per primo. Aprirlo ha fatto scattare l'alert in pochi secondi, con l'IP dell'host da cui operavo. Il token aveva anticipato il mio comportamento offensivo.

La rivelazione e stata la qualita del segnale. Le regole SIEM che avevo costruito richiedevano tuning continuo per bilanciare falsi positivi e falsi negativi; il canary token non richiedeva alcun tuning, perche il suo tasso di falsi positivi e strutturalmente zero - nessuno apre per sbaglio un'esca che non ha motivo di esistere. Un singolo alert di canary token vale, per confidenza, molti alert SIEM correlati.

Il limite emerso e la copertura. Un canary token rileva solo un attaccante che tocca quella specifica esca; e una trappola, non una rete. Se l'attaccante non incrocia il token, non scatta nulla. Questo lo colloca come complemento, non sostituto, del monitoraggio a copertura ampia: il SIEM copre tutto con qualche falso positivo, il token copre punti specifici con confidenza assoluta. La difesa matura usa entrambi.

---

## Analisi Teorica: L'Asimmetria della Deception a Favore del Difensore

La deception ribalta un'asimmetria che normalmente favorisce l'attaccante. Di solito il difensore deve avere ragione sempre (proteggere ogni punto), l'attaccante una volta sola (trovare un buco). La deception introduce l'asimmetria opposta: l'attaccante deve evitare ogni esca (non sa quali file sono reali e quali trappole), il difensore deve indovinare una sola esca che l'attaccante tocchera. In un ambiente disseminato di token, l'attaccante non puo esplorare senza rischiare di attivarne uno.

Questo genera un effetto secondario prezioso: il dubbio. Un attaccante consapevole dell'esistenza di canary token deve muoversi con cautela, verificare ogni file, esitare prima di usare ogni credenziale trovata. La deception non solo rileva, ma rallenta e scoraggia, aumentando il costo e il rischio dell'operazione offensiva. Il valore non e solo il singolo alert, ma l'incertezza che inietta nell'intero processo d'attacco.

Il fondamento teorico e il tasso di falsi positivi strutturalmente nullo. Ogni sistema di detection vive sul compromesso tra falsi positivi (allarmi inutili che consumano l'analista) e falsi negativi (attacchi non rilevati). Il canary token sfugge a questo compromesso perche il suo baseline di attivita legittima e zero per costruzione: non deve distinguere il malevolo dal legittimo, perche sull'esca non esiste attivita legittima. E questa purezza del segnale a rendere la deception uno degli strumenti difensivi con il miglior rapporto valore/sforzo.

---

## Tool di riferimento

| Tool | Tipo | Ruolo | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Canarytokens` (Thinkst) | Token generator | Servizio/self-hosted | Generazione di token di vario tipo (doc, URL, AWS, DNS) |
| `Thinkst Canary` | Honeypot appliance | Prodotto | Honeypot fisici/virtuali "birds" a bassissimo rumore |
| `OpenCanary` | Honeypot daemon | Open source | Servizi esca (FTP, SSH, HTTP) self-hosted |
| `Honeytokens` (AD) | Deception account | Tecnica | Account/credenziali fittizie in Active Directory |
| `DNS canary` | DNS beacon | Token | Rilevamento di esfiltrazione o accesso a risorse esca |

> **Tool moderno consigliato:** `canarytokens.org` (Thinkst) e il modo piu rapido per iniziare, gratuito e senza infrastruttura. Per un deployment interno controllato, `OpenCanary` self-hosted offre servizi esca completi. In ambienti Active Directory, gli honeytoken (account fittizi con SPN allettanti) integrano la deception con il rilevamento di Kerberoasting e altri attacchi AD.

---

## Mappatura MITRE ATT&CK

> La tabella mappa le tecniche d'attacco che le esche **rilevano** al momento dell'interazione.

| Tattica (rilevata) | Tecnica | ID MITRE | Ruolo del controllo |
| :--- | :--- | :--- | :--- |
| Collection | Data from Network Shared Drive | `T1039` | Il documento esca su share scatta se aperto (DEF-005) |
| Collection | Data from Local System | `T1005` | File esca locali che rivelano l'enumerazione |
| Credential Access | Unsecured Credentials: Credentials In Files | `T1552.001` | Credenziali fittizie che scattano se usate (DEF-005) |
| Discovery | File and Directory Discovery | `T1083` | L'interazione con l'esca rivela l'enumerazione in corso |

| Contromisura difensiva (D3FEND) | ID D3FEND | Applicazione |
| :--- | :--- | :--- |
| Decoy File | `D3-DF` | File esca posizionati per rilevare l'accesso non autorizzato |
| Decoy User Credential | `D3-DUC` | Credenziali fittizie (honeytoken) che tradiscono l'uso |
| Decoy Network Resource | `D3-DNR` | Risorse di rete esca (share, URL, record DNS) |

---

> **Nota:** Tutte le attivita documentate sono state condotte su un ambiente di laboratorio di proprieta dell'autore. I canary token sono uno strumento puramente difensivo: rilevano l'accesso non autorizzato a risorse esca controllate dal difensore. Il loro uso e legittimo e non intrusivo. Le tecniche sono documentate a scopo educativo e di difesa in contesto autorizzato.
