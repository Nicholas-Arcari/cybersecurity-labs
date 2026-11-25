> [English](README.en.md) | **Italiano**

# OSINT Frameworks: Automazione e Correlazione (SpiderFoot, recon-ng, Maltego)

> - **Fase:** Reconnaissance - Passive Information Gathering (automazione e correlazione)
> - **Visibilita:** Zero / Bassa - la maggior parte dei moduli interroga fonti pubbliche e API di terze parti (Zero-Touch); alcuni moduli opzionali eseguono risoluzioni DNS o richieste HTTP dirette (Bassa) e vanno disabilitati per restare invisibili
> - **Prerequisiti:** Un dato di partenza (dominio, email, nome, IP), API key gratuite per le fonti principali (Shodan, HaveIBeenPwned, VirusTotal, Hunter.io), completamento delle tecniche OSINT manuali (`breach-data/`, `email-harvesting/`, `user-enumeration/`)
> - **Output:** Grafo OSINT correlato del target, superficie di attacco aggregata da fonti multiple, finding OSINT-005

---

## Introduzione

Le tecniche OSINT manuali documentate nelle sezioni precedenti (`breach-data/`, `email-harvesting/`, `google-dorks/`, `user-enumeration/`) sono efficaci ma non scalano. Su un target reale con decine di domini, centinaia di dipendenti e infrastruttura distribuita, la raccolta e la correlazione manuale richiedono giorni e sono soggette a errori di omissione. I framework OSINT risolvono questo problema automatizzando due attivita distinte: la **raccolta** da centinaia di fonti in parallelo e la **correlazione**, cioe il collegamento automatico tra dati eterogenei (un'email porta a un breach, il breach a una password, il dominio a un sottodominio, il sottodominio a un IP esposto su Shodan).

Il valore operativo di un framework non e trovare un singolo dato, ma costruire il **grafo** del target: la rete di relazioni tra entita che trasforma frammenti isolati in intelligence azionabile. Questa e la differenza tra sapere che esiste l'email `admin@target.com` e sapere che quella stessa email compare in tre breach, riusa un username presente su GitHub dove ha committato una API key ancora valida.

Questa sezione documenta i tre framework di riferimento del settore, ciascuno con una filosofia diversa:

- **SpiderFoot:** automazione totale, oltre 200 moduli, ideale per una raccolta massiva "fire-and-forget" con reportistica automatica.
- **recon-ng:** framework modulare in stile Metasploit, ideale per un workflow controllato e ripetibile, con database interno e marketplace di moduli.
- **Maltego:** analisi visuale del grafo tramite "transforms", insostituibile quando serve comprendere le relazioni complesse tra molte entita.

I risultati prodotti alimentano direttamente `03-dns-enumeration/` (sottodomini scoperti), `04-infrastructure-intel/` (asset esposti correlati) e `05-social-engineering/` (dipendenti e email per campagne mirate).

---

## Struttura della cartella

```
osint-frameworks/
+-- README.md            <- questo file (OSINT-005: automazione e correlazione OSINT)
+-- img/                 <- screenshot del lab (grafo SpiderFoot, dashboard recon-ng, transform Maltego)
```

---

## SpiderFoot - Automazione OSINT Multi-Fonte

**ID Finding:** `OSINT-005` | **Severity:** `Variabile (Informativo / Alto)`

### Contesto operativo

SpiderFoot e il framework OSINT open source piu completo per la raccolta automatizzata. Interroga oltre 200 fonti (motori di ricerca, database di breach, registri DNS, Shodan, certificati TLS, social media, archivi storici) e correla automaticamente i risultati. La sua caratteristica distintiva e la gestione della **visibilita**: ogni modulo e classificato come passivo (interroga solo terze parti) o attivo (contatta il target), permettendo all'analista di eseguire scansioni completamente invisibili al bersaglio.

La severity di questo finding e variabile perche dipende da cosa la correlazione rivela: una scansione che restituisce solo il tech stack pubblico e `Informativo`, mentre una che correla un'email a credenziali in breach ancora valide o a un asset esposto e `Alto`.

### Esecuzione

Installazione e avvio dell'interfaccia web locale:

```Bash
# Installazione
git clone https://github.com/smicallef/spiderfoot.git
cd spiderfoot
pip3 install -r requirements.txt

# Avvio della web UI su localhost (accesso solo locale)
python3 ./sf.py -l 127.0.0.1:5001
```

Configurazione delle API key (Settings > Module Settings): senza le API key gratuite di Shodan, HaveIBeenPwned, VirusTotal e Hunter.io, i risultati sono drasticamente ridotti. Questo e il singolo fattore che piu impatta la qualita dell'output.

Avvio di una scansione **solo-passiva** da CLI (per restare Zero-Touch):

```Bash
# Scansione passiva: -u passive usa solo moduli che non contattano il target
python3 ./sf.py -s nicholas-arcari.github.io -u passive -o csv > spiderfoot_passive.csv

# Scansione per tipo di dato (esempio: solo email e sottodomini)
python3 ./sf.py -s target.com -t EMAILADDR,INTERNET_NAME
```

Output atteso (sintetico, formato CSV):

```
Source Module, Type, Data
sfp_dnsresolve, IP Address, 185.199.108.153            <-- IP GitHub Pages
sfp_hunter, Email Address, contact@target.com
sfp_haveibeenpwned, Hacked Email, contact@target.com   <-- OSINT-005: email in breach
sfp_crt, Internet Name, dev.target.com                 <-- sottodominio da Certificate Transparency
sfp_shodan, Open TCP Port, 185.199.x.x:443
sfp_github, Raw Data from Public Repos, "API_KEY=AKIA..."  <-- correlazione a secret leakage (vedi OSINT-006)
```

> [Segnaposto screenshot: catturare il grafo di correlazione di SpiderFoot (tab "Graph") e la vista "Browse" con il conteggio per tipo di dato durante l'esecuzione del lab, salvandolo in `./img/`.]

![Grafo di correlazione SpiderFoot](img/spiderfoot-graph-PLACEHOLDER.jpg)

### Esperienza di Laboratorio

L'esecuzione ha confermato quanto la configurazione delle API key incida sul volume dei risultati: senza chiavi i framework si limitano alle fonti aperte e restituiscono un grafo scarno, mentre con le chiavi gratuite dei servizi principali attivate la copertura di sottodomini, email e data breach correlati cresce in modo evidente. Si e deciso di operare in modalita strettamente passiva, disabilitando i moduli che generano traffico verso il target, per non uscire dal perimetro OSINT e non lasciare tracce: una scelta coerente con la fase di recon passiva del progetto. Il costo e il tempo - la scansione passiva e piu lenta perche interroga molte fonti esterne - e la presenza di falsi positivi nella correlazione automatica, tipicamente email o nominativi solo omonimi che non appartengono realmente al target, validati manualmente prima di considerarli. Il dato a piu alto valore si e rivelato la correlazione tra sottodomini e tecnologie esposte, che alimenta direttamente le fasi successive di scanning e web recon.

Punti di attenzione tipici di questo tipo di scansione, da verificare durante l'esecuzione:

- SpiderFoot classifica alcuni moduli DNS come passivi anche se eseguono risoluzioni: per una invisibilita assoluta usare `-u passive` e controllare manualmente la lista dei moduli attivati.
- Il modulo `sfp_github` puo restituire falsi positivi (repository di omonimi): ogni hit va validato prima di essere incluso in un report.
- La correlazione email-breach dipende dallo stato dell'API HIBP: un risultato negativo va sempre validato manualmente come descritto in `breach-data/`.

### Analisi Teorica

Un framework OSINT non aggiunge fonti nuove rispetto alla ricerca manuale: interroga le stesse API pubbliche che un analista consulterebbe una alla volta. Il valore aggiunto e nel **motore di correlazione**, che tratta ogni dato come un nodo tipizzato (email, dominio, IP, hash) e applica regole di espansione: quando un modulo produce un `INTERNET_NAME`, altri moduli lo prendono automaticamente in input e lo risolvono, lo cercano su Shodan, ne estraggono i certificati. Questo processo iterativo (chiamato "correlation cascade") ricostruisce automaticamente il grafo che manualmente richiederebbe di collegare a mano decine di risultati.

La scelta tra i tre framework dipende dall'obiettivo: SpiderFoot per la copertura massima automatica, recon-ng per un workflow controllato e ripetibile in script, Maltego quando l'analisi visuale delle relazioni e il deliverable stesso (es. mappare la struttura di un gruppo aziendale con piu controllate).

---

## recon-ng - Framework OSINT Modulare

### Contesto operativo

recon-ng adotta l'interfaccia e la filosofia di Metasploit applicata all'OSINT: workspace isolati, database interno (SQLite) che accumula i risultati, e un marketplace di moduli installabili. E il framework ideale quando serve un processo ripetibile e documentabile, perche ogni comando e tracciato e il database puo essere esportato come evidenza strutturata.

### Esecuzione

```Bash
# Avvio e creazione di un workspace dedicato al target
recon-ng
[recon-ng][default] > workspaces create target_engagement

# Installazione dei moduli dal marketplace
[recon-ng][target_engagement] > marketplace install all

# Inserimento del dato di partenza (seed)
[recon-ng][target_engagement] > db insert domains
domain (TEXT): target.com

# Enumerazione sottodomini da Certificate Transparency (passivo)
[recon-ng][target_engagement] > modules load recon/domains-hosts/certificate_transparency
[recon-ng][...][certificate_transparency] > run

# Harvesting contatti/email
[recon-ng][target_engagement] > modules load recon/domains-contacts/whois_pocs
[recon-ng][...] > run

# Esportazione del report finale
[recon-ng][target_engagement] > modules load reporting/html
[recon-ng][...][html] > options set FILENAME /home/kali/recon_report.html
[recon-ng][...][html] > run
```

Output atteso (tabella hosts nel database interno):

```
  +---------------------------------------------------------------+
  | host              | ip_address      | region  | module        |
  +---------------------------------------------------------------+
  | dev.target.com    | 10.x.x.x        |         | cert_transp.  |  <-- sottodominio dev
  | vpn.target.com    | 185.x.x.x       |         | cert_transp.  |  <-- vettore accesso remoto
  | mail.target.com   | 185.x.x.x       |         | cert_transp.  |
  +---------------------------------------------------------------+
  [*] 3 total (3 new) hosts found.
```

> [Segnaposto screenshot: catturare la dashboard di recon-ng con la tabella `hosts` popolata (`show hosts`) e il report HTML generato.]

### Analisi dei risultati

I sottodomini con nomi come `vpn`, `dev`, `sso`, `staging` sono prioritari: indicano vettori di accesso remoto o ambienti meno protetti della produzione. Questa lista diventa input diretto per `03-dns-enumeration/subdomain-finding/` e per il web recon in `03-web-attacks/02-web-recon/`.

---

## Maltego - Analisi Visuale del Grafo

### Contesto operativo

Maltego non e uno scanner ma uno strumento di **link analysis**: parte da un'entita (dominio, persona, email) e applica "transforms", cioe query verso fonti dati che restituiscono entita collegate, visualizzate come grafo. E lo strumento di riferimento per investigazioni complesse dove la struttura delle relazioni e il risultato: mappare le controllate di un gruppo, ricostruire una rete di persone, collegare infrastrutture tramite certificati condivisi.

### Esecuzione

L'uso e prevalentemente grafico (GUI):

```
[1] Creare un nuovo grafo (New Graph)
[2] Trascinare un'entita "Domain" e impostare target.com
[3] Eseguire le transform passive:
     +-- "To DNS Name [Using Robtex]"     -> sottodomini
     +-- "To Email Addresses [PGP]"       -> email da server PGP
     +-- "To Website"                     -> siti collegati
     +-- "To Entities [IBM Watson]"       -> persone e organizzazioni
[4] Espandere iterativamente i nodi di interesse
```

> [Segnaposto screenshot: catturare il grafo Maltego con il dominio target espanso in sottodomini, email ed entita collegate.]

**Limiti della Community Edition:** Maltego CE limita i risultati per transform (tipicamente 12 entita) e richiede registrazione. Per un engagement reale la versione Classic/XL rimuove i limiti. Per il lab, la CE e sufficiente a dimostrare la metodologia.

### Analisi Teorica

Il modello dati di Maltego (entita + transform) e la formalizzazione visuale dello stesso "grafo OSINT" che SpiderFoot costruisce internamente. La differenza e il controllo: in Maltego l'analista decide manualmente quale nodo espandere e con quale transform, evitando il rumore di una scansione automatica totale. Questo lo rende superiore quando il numero di entita e alto e serve discriminare quali relazioni sono rilevanti.

---

## Flusso operativo consigliato

```
[INPUT] Un dato di partenza (dominio / email / nome)
          |
          v
[1] Raccolta massiva automatica (SpiderFoot -u passive)
     +-- 200+ fonti in parallelo -> CSV/DB con tutti i dati grezzi
          |
          v
[2] Workflow controllato e ripetibile (recon-ng)
     +-- moduli selezionati -> database strutturato -> report HTML
          |
          v
[3] Analisi visuale delle relazioni (Maltego)
     +-- espansione manuale dei nodi critici -> grafo delle relazioni
          |
          v
[4] Correlazione e validazione manuale
     +-- rimozione falsi positivi, verifica hit critici
          |
          v
[OUTPUT] Grafo OSINT del target -> input per 03-dns, 04-infra-intel, 05-social-engineering
```

---

## Scenario Reale: Proiezione Post-Reconnaissance

> Questa sezione descrive come OSINT-005 si inserirebbe in un engagement reale, dal punto di vista dell'attaccante e del difensore. Applicabile quando la correlazione raggiunge severity `Alto`.

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** grafo OSINT completo del target con email dei dipendenti, sottodomini (inclusi `vpn`, `dev`), asset esposti e almeno un'email correlata a un breach.

**Passo successivo immediato:** incrocio dei sottodomini `vpn`/`sso` con le credenziali in breach per un tentativo di Credential Stuffing sul portale di accesso remoto.

**Kill Chain proiettata:**

```
OSINT-005: grafo correlato (email dipendenti + vpn.target.com + breach)
        |
        v
Credential Stuffing su vpn.target.com (password riusate dai breach)
        |
        v
Accesso VPN -> rete interna -> pivoting (07-post-exploitation)
        |
        v
Movimento laterale e persistenza
```

**Impatto potenziale:** l'aggregazione OSINT riduce drasticamente il tempo di preparazione di un attacco mirato. Un grafo completo trasforma una campagna generica in una campagna di Spear Phishing e Credential Stuffing su misura, con tassi di successo molto piu alti.

### Prospettiva Difensore (Blue Team)

**Rilevamento:** l'OSINT passivo e per definizione invisibile (nessun contatto con i sistemi target). Il rilevamento non avviene sul singolo evento ma sul risultato: monitoraggio della propria esposizione tramite gli stessi strumenti (self-OSINT periodico) e alert su tentativi di login anomali che seguono la fase di raccolta.

**Indicatori di Compromissione (IOC):**
- Picco di tentativi di autenticazione falliti su portali VPN/SSO da IP nuovi (fase di Credential Stuffing post-OSINT)
- Comparsa di nuovi sottodomini o asset aziendali nei risultati di SpiderFoot/Shodan eseguiti in self-assessment

**Contenimento:** enforcement MFA su tutti i portali esposti (neutralizza il Credential Stuffing basato su password in breach), rotazione delle credenziali dei dipendenti presenti in breach noti.

**Eradicazione e hardening:**
- Programma di self-OSINT periodico: eseguire SpiderFoot/recon-ng sul proprio perimetro per vedere cio che vede l'attaccante
- Minimizzare l'esposizione delle email aziendali in formato standard (`nome.cognome@`) su fonti pubbliche
- Formazione anti-phishing basata sui dati realmente esposti

**Lezione difensiva:** non si puo proteggere cio che non si sa di esporre. L'unico modo per difendersi dalla ricognizione passiva e conoscere in anticipo la propria impronta OSINT ed eliminarla o monitorarla.

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `SpiderFoot` | OSINT aggregator | CLI / Web (locale) | Raccolta automatica da 200+ fonti con correlazione |
| `recon-ng` | OSINT framework | CLI (modulare) | Workflow OSINT ripetibile con database e reportistica |
| `Maltego` | Link analysis | GUI | Analisi visuale del grafo di relazioni tra entita |
| `theHarvester` | Email/Subdomain harvesting | CLI | Raccolta mirata email/sottodomini (vedi `email-harvesting/`) |
| `Amass` (OWASP) | Subdomain/OSINT | CLI | Enumerazione asset e correlazione infrastruttura |

> **Tool moderno consigliato:** `SpiderFoot HX` (versione cloud commerciale) e `Amass intel` (`amass intel -org "Target Corp"` per scoprire i range IP e gli AS associati a un'organizzazione partendo dal nome). Amass e attivamente mantenuto da OWASP e integra Certificate Transparency, fonti passive DNS e correlazione ASN in un unico tool CLI, ideale per l'automazione in pipeline.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Identity Info: Email Addresses | `T1589.002` | Aggregazione automatica di email del target da fonti multiple tramite SpiderFoot e recon-ng (OSINT-005) |
| Reconnaissance | Search Open Technical Databases: WHOIS | `T1596.002` | Raccolta dati WHOIS e contatti tramite moduli recon-ng (OSINT-005) |
| Reconnaissance | Search Open Websites/Domains: Search Engines | `T1593.002` | Correlazione automatica di dati pubblici indicizzati da motori di ricerca e archivi (OSINT-005) |
| Reconnaissance | Gather Victim Network Info: DNS | `T1590.002` | Enumerazione sottodomini da Certificate Transparency tramite recon-ng e SpiderFoot (OSINT-005) |
| Reconnaissance | Search Open Websites/Domains: Social Media | `T1593.001` | Aggregazione presenza social e identity correlation nel grafo OSINT (OSINT-005) |

---

> **Nota:** Le scansioni OSINT documentate in questa sezione sono state eseguite a scopo didattico sul dominio personale `nicholas-arcari.github.io` e su target autorizzati. I moduli attivi sono stati disabilitati per mantenere l'invisibilita al target. Nessun dato correlato (email, credenziali in breach) e stato utilizzato per tentare accessi non autorizzati.
