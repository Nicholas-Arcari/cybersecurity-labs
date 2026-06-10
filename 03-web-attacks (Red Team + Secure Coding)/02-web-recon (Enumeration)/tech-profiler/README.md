> [English](README.en.md) | **Italiano**

# Web Recon: Tech Profiling & Fingerprinting

> - **Fase:** Web Attack - Technology Fingerprinting
> - **Visibilita:** Bassa - richieste HTTP standard simili a normale navigazione browser
> - **Prerequisiti:** Target web identificato, `whatweb` preinstallato su Kali, estensione `Wappalyzer` nel browser
> - **Output:** Stack tecnologico completo (web server, linguaggio, CMS, versioni), finding WEB-002 (PHP 5.6.40 EOL + header X-Powered-By)

---

**ID Finding:** `WEB-002` | **Severity:** `Alto` | **CVSS v3.1:** 7.5

---

Obiettivo: Identificare lo "Stack Tecnologico" (Sistema Operativo, Web Server, Framework, Linguaggi) del target per mirare la ricerca di vulnerabilità note (CVE).

Target: `http://testphp.vulnweb.com`

Strumenti: `WhatWeb` (CLI), `Wappalyzer` (Browser Extension)

---

## 1 Introduzione Teorica

Il Fingerprinting è l'arte di capire "di cosa è fatto" un sito web analizzando le risposte del server.

Le tecnologie web lasciano impronte digitali uniche:

- Header HTTP: `Server: Apache/2.4.41` o `X-Powered-By: PHP/7.4`.
- Codice Sorgente: Struttura delle cartelle (es. `/wp-content/` indica WordPress).
- Cookie: Nomi specifici come `JSESSIONID` (Java) o `PHPSESSID` (PHP).

Questa fase è cruciale per un attaccante: conoscere la versione esatta di un software permette di cercare Public Exploits specifici su database come Exploit-DB.

Perché un Red Teamer vuole sapere queste cose?

- CVE Mapping (Il motivo principale):

    - Se WhatWeb mi dice che il sito usa PHP 5.6.40, io vado su Google e cerco: "PHP 5.6.40 vulnerabilities". Scoprirò che è vecchio e pieno di buchi.
    - Se mi dice WordPress 4.8, cerco exploit per quella versione specifica. Non perdo tempo a lanciare attacchi per Joomla se il sito è WordPress.

- Default Credentials:

    - Se scopro che il server è Tomcat, proverò a loggarmi con tomcat:s3cret.
    - Se è Jenkins, proverò admin:password.
    - Sapere la tecnologia ti dà la chiave per indovinare la password di default.

- WAF Detection:

    - Questi tool ti dicono spesso se c'è un WAF (Web Application Firewall) come Cloudflare o Imperva. Se lo sai, sai che devi usare tecniche di evasione (o lasciar perdere per non farti bannare).
        
---

## 2 Strumenti Utilizzati

### WhatWeb (Active Scanner)

Strumento a riga di comando preinstallato su Kali Linux. Esegue una scansione rapida identificando CMS, piattaforme di blogging, librerie JavaScript e server web. Supporta diversi livelli di aggressività.

### Wappalyzer (Passive)

Utilizzato solitamente come estensione del browser, identifica le tecnologie analizzando passivamente la pagina caricata. Utile per una verifica visiva immediata senza inviare pacchetti di scansione sospetti.

---

## 3 Esecuzione Tecnica: WhatWeb Scan

È stata eseguita una scansione dettagliata (`-v`) contro il target per estrarre le versioni software.

```Bash
whatweb -v http://testphp.vulnweb.com
```

![](./img/Screenshot_2026-02-12_19_12_54.jpg)

![](./img/Screenshot_2026-02-12_19_13_00.jpg)

Analisi dei Findings: L'output rivela informazioni critiche per la fase successiva di attacco:

- Web Server: Nginx 1.19.0. Sapere che è Nginx e non Apache cambia le tecniche di configurazione e i file da cercare (es. .htaccess non funziona su Nginx).
- Linguaggio: PHP 5.6.40. Finding Critico. Questa versione di PHP è obsoleta (End of Life) e soffre di numerose vulnerabilità note che potrebbero permettere Remote Code Execution (RCE).
- Framework: Nessun CMS complesso (come WordPress) rilevato, suggerendo un'applicazione custom ("Home of Acunetix Art").

---

## 4 Conclusioni

Il Tech Profiling ha confermato che il target gira su un'infrastruttura legacy (PHP 5.6). Questa informazione restringe il campo d'azione: invece di lanciare attacchi generici, un Red Team cercherebbe ora exploit specifici per PHP 5.6 o vulnerabilità di configurazione tipiche di Nginx 1.19.

---

## 5 Scenari Speciali: Localhost & Static Sites

Il Tech Profiling assume significati diversi a seconda dell'ambiente target.

#### A. Localhost / Docker (Hardening)

Lanciando WhatWeb contro ambienti di sviluppo locali (`localhost:5173`), l'obiettivo non è l'attacco ma l'Hardening.

I framework moderni (es. Express.js, Flask, Spring Boot) espongono di default header come `X-Powered-By` o `Server` che rivelano versioni precise del runtime.

Best Practice: Identificare questi leak in locale permette allo sviluppatore di disabilitarli (es. `app.disable('x-powered-by')` in Express) prima del deploy in produzione.

#### B. Static Hosting (GitHub Pages)

Analizzando siti statici come `https://nicholas-arcari.github.io`, il server web è gestito dal provider (GitHub) e quindi fuori dallo scope di attacco.
L'attenzione si sposta sulle Librerie Client-Side.

WhatWeb e Wappalyzer sono fondamentali per rilevare versioni obsolete di librerie JavaScript (es. jQuery < 3.0, Bootstrap vecchi) che spesso contengono vulnerabilità note di tipo DOM-based XSS, sfruttabili direttamente nel browser della vittima senza toccare il server.

---

## Analisi a Basso Livello: Vettori di Fingerprinting e Information Disclosure

### Fonti di Informazione nel Response HTTP

Ogni risposta HTTP contiene molteplici vettori di fingerprinting:

```
HTTP/1.1 200 OK
Server: nginx/1.19.0                     <-- Web server + versione esatta
X-Powered-By: PHP/5.6.40                 <-- Linguaggio + versione (CRITICO)
Set-Cookie: PHPSESSID=abc123             <-- Conferma PHP (nome cookie default)
Content-Type: text/html; charset=UTF-8
X-Frame-Options: SAMEORIGIN              <-- Security header presente
ETag: "5f3c8a6d-1234"                    <-- Formato rivela il web server

<!DOCTYPE html>
<html>
<head>
  <meta name="generator" content="WordPress 6.2">  <-- CMS + versione
  <script src="/wp-includes/js/jquery/jquery.min.js?ver=3.6.0">  <-- jQuery version
  <!-- Built with React 18.2.0 -->       <-- Framework frontend
</head>
```

### Catena di CVE da Fingerprinting: PHP 5.6.40

Il finding WEB-002 (PHP 5.6.40) e particolarmente critico perche questa versione e in End of Life dal 31 dicembre 2018. Le CVE note includono:

| CVE | CVSS | Impatto | Classe |
| :--- | :--- | :--- | :--- |
| CVE-2019-11043 | 9.8 | Remote Code Execution via path_info in php-fpm | RCE |
| CVE-2019-11041 | 7.1 | Heap buffer over-read in EXIF parsing | Information Disclosure |
| CVE-2018-20783 | 7.5 | Buffer over-read in phar_parse_pharfile | DoS/Info Leak |
| CVE-2016-5385 | 8.1 | HTTPoxy - HTTP_PROXY env injection | SSRF/RCE |

Un attaccante che identifica PHP 5.6.40 tramite WhatWeb puo immediatamente consultare queste CVE e selezionare l'exploit appropriato.

### WhatWeb: Livelli di Aggressivita e Plugin Engine

WhatWeb utilizza un sistema di plugin (1.800+) con 4 livelli di aggressivita:

| Livello | Flag | Richieste | Detection | Rischio rilevamento |
| :--- | :--- | :--- | :--- | :--- |
| 1 (Passive) | `-a 1` | 1 GET (solo root) | Header + body della homepage | Minimo |
| 2 | `-a 2` | GET root + follow redirect | + header redirect + cookie | Basso |
| 3 (Aggressive) | `-a 3` | + GET su path noti | + /robots.txt, /favicon.ico, /wp-login.php | Medio |
| 4 (Heavy) | `-a 4` | Brute force path per ogni plugin | + test specifici per ogni tecnologia | Alto |

Nel lab, il livello default (1) e stato sufficiente perche il target non aveva WAF e gli header HTTP rivelavano tutto. Su target protetti (come tesla.com nel lab infrastructure-intel), il livello 1 viene bloccato dal WAF e servono tecniche passive (Wappalyzer).

---

## Scenario Reale: Da Information Disclosure a RCE (WEB-002)

Il finding WEB-002 (PHP 5.6.40 + header X-Powered-By) e il punto di partenza per una kill chain che porta a Remote Code Execution.

### Kill Chain: Version Disclosure -> CVE -> RCE

```
Fase 1: Fingerprinting (WEB-002)
    $ whatweb -v http://target
    -> PHP/5.6.40, Nginx/1.19.0
    |
    v
Fase 2: CVE Lookup
    $ searchsploit php 5.6
    -> CVE-2019-11043: PHP-FPM RCE (CVSS 9.8)
    |
    v
Fase 3: Verifica PHP-FPM
    $ curl -I http://target/index.php/test%0d%0a
    -> 502 Bad Gateway  <-- PHP-FPM raggiungibile (Nginx passa a php-fpm)
    |
    v
Fase 4: Exploitation
    $ python3 phuip-fpizdam.py http://target/index.php
    [*] Sending exploit payload...
    [*] Remote Code Execution achieved!
    $ curl "http://target/index.php?a=id"
    -> uid=33(www-data) gid=33(www-data)
    |
    v
Fase 5: Post-Exploitation
    -> Reverse shell, escalation, pivot nella rete interna
```

**Statistica (Rapid7 2024):** il 34% dei web server pubblici espone la versione del software negli header HTTP. Di questi, il 18% esegue versioni con CVE critiche note (CVSS >= 9.0).

---

## Blue Team: Hardening degli Header e Monitoring

### Rimozione Information Disclosure

```Bash
# Nginx: rimuovere versione server
server_tokens off;

# Apache: rimuovere versione e moduli
ServerTokens Prod
ServerSignature Off

# PHP: rimuovere header X-Powered-By
# In php.ini:
expose_php = Off

# Express.js: rimuovere X-Powered-By
app.disable('x-powered-by');

# Spring Boot: personalizzare header Server
server.server-header=
```

### Monitoring

- Alert su richieste con User-Agent di scanner noti (`WhatWeb`, `Nikto`, `Wappalyzer CLI`)
- Monitorare accessi a path diagnostici tipici del fingerprinting: `/robots.txt`, `/sitemap.xml`, `/.well-known/`, `/server-info`, `/server-status`
- Verificare periodicamente i propri header con: `curl -I https://proprio-sito.com` per confermare che le versioni non siano esposte

---

## Esperienza di Laboratorio

Il finding piu immediato e stato l'header `X-Powered-By: PHP/5.6.40`: un singolo header HTTP ha rivelato che il target esegue una versione di PHP fuori supporto da oltre 7 anni, con decine di CVE note. In un assessment reale, questo finding da solo giustifica una raccomandazione di upgrade urgente, indipendentemente dalle altre vulnerabilita.

Il confronto tra WhatWeb (attivo, CLI) e Wappalyzer (passivo, browser) ha mostrato risultati complementari: WhatWeb ha estratto le versioni precise dagli header HTTP, mentre Wappalyzer ha identificato le librerie JavaScript client-side analizzando i tag `<script>` e i pattern CSS. In un assessment completo, si usano entrambi: WhatWeb per le informazioni server-side, Wappalyzer per il frontend.

La distinzione tra fingerprinting attivo e passivo e cruciale quando si opera contro target con WAF: su tesla.com (documentato nel lab 01-recon/infrastructure-intel), WhatWeb e stato bloccato da Akamai con un 403 Forbidden, mentre Wappalyzer (che analizza la pagina caricata normalmente dal browser) ha funzionato senza problemi. La lezione: il fingerprinting attivo va tentato per primo (e piu rapido e completo), ma il fallback passivo deve sempre essere pronto.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Host Info: Software | `T1592.002` | Tech profiling con WhatWeb e Wappalyzer per identificare PHP 5.6.40, Nginx 1.19.0 e lo stack tecnologico completo di `testphp.vulnweb.com` (WEB-002) |
| Reconnaissance | Active Scanning: Vulnerability Scanning | `T1595.002` | Analisi degli header HTTP (es. `X-Powered-By: PHP/5.6.40`) per mappare le versioni software e identificare CVE applicabili (WEB-002) |

---

> **Nota:** Il tech profiling e stato condotto su `testphp.vulnweb.com` (Acunetix) e su
> `nicholas-arcari.github.io` (sito personale statico). Il finding WEB-002 (PHP 5.6.40 EOL)
> e documentato come esempio di misconfiguration tipica. In un engagement reale, questa
> informazione sarebbe classificata come "Confidential" e utilizzata esclusivamente per
> pianificare le fasi successive del test.