> [English](README.en.md) | **Italiano**

# Tech Stack Fingerprinting: WhatWeb & BuiltWith

> - **Fase:** Reconnaissance - Infrastructure Intelligence
> - **Visibilita:** Bassa - richieste HTTP standard per fingerprinting, rilevabili dal WAF ma comuni nel traffico legittimo
> - **Prerequisiti:** WhatWeb installato, dominio target, Wappalyzer come estensione browser per analisi passiva
> - **Output:** INTEL-004 - Profilo tecnologico del target; in questo lab: WAF Akamai rilevato su tesla.com, fingerprinting backend bloccato

---

Obiettivo: Identificare le tecnologie sottostanti (CMS, Web Server, Framework, Librerie JS) utilizzate dal target per individuare versioni obsolete o vulnerabilità note (CVE).

Target: `tesla.com`

Strumenti: `WhatWeb` (CLI), `Wappalyzer` (Browser Extension), `BuiltWith` (Web)

---

## 1 Introduzione Teorica

Il Tech Stack Fingerprinting è il processo di raccolta di "impronte digitali" dal server web. Analizzando le risposte HTTP, i cookie, e il codice sorgente HTML, è possibile determinare:

- Sistema Operativo: (es. Ubuntu, CentOS, Windows Server)
- Web Server: (es. Nginx, Apache, IIS)
- Framework/CMS: (es. Drupal, WordPress, React)
- Librerie Client-side: (es. jQuery, Bootstrap)

Per un attaccante, questa fase è cruciale per selezionare gli exploit corretti (es. non lanciare attacchi PHP contro un server Java).

---

## 2 Esecuzione Tecnica: WhatWeb

**ID Finding:** `INTEL-004` | **Severity:** `Informativo`

`WhatWeb` è uno scanner di nuova generazione che identifica le tecnologie web. È stato lanciato contro il dominio target per ottenere un profilo rapido.

Comando:
```Bash
whatweb -v tesla.com
```

(Nota: L'opzione -v attiva la modalità verbosa per maggiori dettagli)

![](./img/Screenshot_2026-02-08_15_33_17.jpg)

![](./img/Screenshot_2026-02-08_15_40_42.jpg)

Analisi dell'Output:

L'output dimostra l'efficacia delle difese perimetrali di Tesla. Lo scanner non è riuscito a raggiungere l'applicazione web sottostante, venendo bloccato all'ingresso:

- Access Denied / 403 Forbidden:

    Osservazione: Lo scanner ha ricevuto uno stato HTTP `403 Forbidden` e il titolo pagina `Access Denied`, invece del classico `200 OK`.

    Analisi Tecnica: Il sistema di difesa ha identificato la firma (User-Agent o comportamento) di `WhatWeb` come traffico automatizzato/malevolo, terminando immediatamente la connessione.

- Il "Colpevole" (Akamai):

    Osservazione: sono stati rilevati i plugin: `Akamai-Global-Host` e la stringa server `AkamaiGHost`.

    Analisi Tecnica: Questo conferma che `tesla.com` utilizza Akamai come CDN e WAF (Web Application Firewall). L'IP risolto non è quello del server reale, ma quello di un nodo edge di Akamai, che agisce da scudo (Reverse Proxy) contro attacchi diretti.

- Sicurezza SSL (HSTS):

    Osservazione: È presente l'header: `Strict-Transport-Security`.

    Analisi Tecnica: Il dominio forza i browser a utilizzare esclusivamente connessioni HTTPS cifrate, prevenendo attacchi di tipo "SSL Stripping" o "Downgrade".

---

## 3 Conclusioni

Questa fase di fingerprinting ha confermato che tesla.com utilizza una strategia di "Defense in Depth". L'attacco diretto automatizzato viene mitigato efficacemente da Akamai. Per un attaccante, questo implica che l'uso di scanner attivi "rumorosi" (come Nikto o WhatWeb standard) è inefficace contro il dominio principale. Sarebbe necessario utilizzare tecniche di evasione (rotazione IP, spoofing User-Agent) o spostarsi su una ricognizione puramente passiva (Wappalyzer) per mappare le tecnologie backend (es. Drupal) senza allertare il WAF.

---

## Analisi a Basso Livello: Vettori di Fingerprinting e WAF Detection

### Come Funziona il Fingerprinting HTTP

Il tech stack fingerprinting opera analizzando elementi specifici della risposta HTTP che rivelano involontariamente le tecnologie utilizzate:

| Vettore | Esempio | Cosa rivela |
| :--- | :--- | :--- |
| **Header `Server:`** | `Server: Apache/2.4.51 (Ubuntu)` | Web server e versione esatta + OS |
| **Header `X-Powered-By:`** | `X-Powered-By: PHP/7.4.3` | Linguaggio backend e versione |
| **Cookie names** | `PHPSESSID`, `JSESSIONID`, `ASP.NET_SessionId` | PHP, Java, ASP.NET rispettivamente |
| **HTML meta/comments** | `<meta name="generator" content="WordPress 6.2">` | CMS e versione |
| **URL patterns** | `/wp-admin/`, `/administrator/`, `/user/login` | WordPress, Joomla, Drupal rispettivamente |
| **Error pages** | Stack trace con nome framework | Framework + versione + path del filesystem |
| **HTTP response headers** | `X-Drupal-Cache`, `X-Varnish`, `CF-RAY` | CMS, caching layer, CDN |
| **TLS certificate** | Issuer, Subject, SAN entries | Hosting provider, domini associati |

WhatWeb utilizza un database di oltre 1.800 plugin, ognuno dei quali cerca pattern specifici nella risposta HTTP. Il livello di aggressivita (`-a`) controlla la profondita dell'analisi:

```
-a 1 (stealthy):  singola GET /, analisi header e body
-a 3 (aggressive): richieste aggiuntive a path noti (/robots.txt, /favicon.ico, /wp-login.php)
-a 4 (heavy):     brute force di path e file per ogni plugin
```

### Meccanica del WAF Detection

Il blocco da parte di Akamai su tesla.com e avvenuto a livello di fingerprinting della richiesta. I WAF moderni analizzano:

1. **User-Agent:** WhatWeb invia di default `WhatWeb/0.5.5` - una firma nota in tutti i database di bot
2. **TLS fingerprint (JA3):** la combinazione di cipher suites e estensioni TLS negoziate identifica univocamente il client; WhatWeb (Ruby OpenSSL) ha un JA3 diverso da Chrome o Firefox
3. **Behavioral analysis:** un singolo GET sulla root senza risorse successive (CSS, JS, immagini) indica un tool automatizzato, non un browser umano
4. **Rate e pattern:** richieste sequenziali a path multipli in rapida successione

**Tecniche di evasione (per assessment autorizzati):**

```Bash
# Spoofing User-Agent per simulare un browser
whatweb -v -U "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" target.com

# httpx con randomizzazione (tool moderno, meno rilevabile)
echo "target.com" | httpx -title -tech-detect -status-code -follow-redirects
```

---

## Blue Team: Protezione contro il Fingerprinting

**Hardening:**
- Rimuovere o offuscare gli header rivelatori: `Server:`, `X-Powered-By:`, `X-AspNet-Version:`
  - Nginx: `server_tokens off;`
  - Apache: `ServerTokens Prod` + `ServerSignature Off`
  - PHP: `expose_php = Off` in php.ini
- Implementare custom error pages che non rivelino il framework backend (no stack traces in produzione)
- Rimuovere il meta tag `generator` dai CMS (WordPress: `remove_action('wp_head', 'wp_generator');`)
- Utilizzare nomi di cookie personalizzati invece dei default (rinominare `PHPSESSID`, `JSESSIONID`)

**Detection:**
- I tool di fingerprinting inviano richieste HTTP con User-Agent non standard o assente. Regola WAF su User-Agent vuoto o contenente nomi di scanner noti (WhatWeb, Nikto, Nmap, Nuclei) per bloccare o tarpit le richieste
- Monitorare sequenze di richieste a path diagnostici (`/robots.txt`, `/sitemap.xml`, `/.git/HEAD`, `/wp-login.php`) in rapida successione dallo stesso IP - pattern tipico di scanner automatizzati

---

## Esperienza di Laboratorio

L'aspetto piu istruttivo dell'esercizio e stato il fallimento: WhatWeb non ha potuto fingerprinting il backend di tesla.com a causa del WAF Akamai. Paradossalmente, il blocco stesso ha fornito informazioni di valore: la risposta `403 Forbidden` con header `AkamaiGHost` ha rivelato il provider CDN/WAF, che a sua volta indica il livello di maturita della sicurezza del target (enterprise con budget per difese perimetrali avanzate).

Questo scenario e comune negli assessment reali su target enterprise: il fingerprinting attivo viene bloccato dal WAF, e l'analista deve spostarsi su tecniche passive. Wappalyzer (estensione browser) analizza le risposte HTTP durante la navigazione manuale, producendo risultati senza generare traffico anomalo. In alternativa, l'analisi del codice sorgente HTML (View Source nel browser) rivela framework JavaScript, librerie CSS e meta tag che WhatWeb non ha potuto raggiungere.

La lezione operativa: in un assessment, il fingerprinting attivo (WhatWeb, Nikto) va tentato per primo perche e rapido, ma non ci si deve aspettare che funzioni su target con WAF. Il fingerprinting passivo (Wappalyzer, analisi manuale, Shodan historical data) e il fallback obbligatorio e spesso produce risultati piu completi perche non viene bloccato.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Host Info: Software | `T1592.002` | Fingerprinting tecnologico di tesla.com con WhatWeb per identificare CMS, web server, framework e librerie client-side (INTEL-004) |
| Reconnaissance | Active Scanning: Vulnerability Scanning | `T1595.002` | Richiesta HTTP di fingerprinting che ha rivelato la presenza di Akamai WAF come sistema di difesa perimetrale, confermando HSTS attivo (INTEL-004) |

---

> **Nota:** Il fingerprinting documentato in questa sezione e stato eseguito su tesla.com nell'ambito del programma pubblico di bug bounty. WhatWeb invia una singola richiesta HTTP GET standard, equivalente a una normale visita browser. Nessuna tecnica di exploitation o evasione WAF e stata tentata.