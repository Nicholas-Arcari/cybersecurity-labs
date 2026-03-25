# 04 - CMS Specific

> - **Fase:** Web Attack - CMS Fingerprinting & Targeted Exploitation
> - **Visibilita:** Media - richieste HTTP con payload specifici per il CMS
> - **Prerequisiti:** CMS identificato dalla fase di tech profiling (`02-web-recon/tech-profiler/`), versione confermata
> - **Output:** Finding WEB-015 (Drupal RCE), enumerazione utenti e plugin (WordPress, Joomla), report specifico per CMS

---

## Introduzione

Quando il target usa un Content Management System (CMS) noto, la strategia cambia radicalmente rispetto agli attacchi generici: ogni CMS ha i propri pattern di vulnerabilita, strumenti di enumerazione dedicati e database di exploit specifici.

I motivi per cui i CMS sono target privilegiati nei penetration test:

- **Superficie di attacco ampia:** un CMS e un'applicazione complessa con molte componenti (core, plugin, temi, API REST). Ognuna e un potenziale punto di ingresso.
- **Versioni obsolete:** gli aggiornamenti automatici sono spesso disabilitati in produzione (timore di breaking changes). Le installazioni non aggiornate rimangono esposte per mesi o anni.
- **Plugin di terze parti:** la maggior parte delle vulnerabilita in WordPress, per esempio, non e nel core ma nei plugin. Una singola installazione puo avere decine di plugin non monitorati.
- **Credenziali di default:** molti CMS hanno username di default (`admin`) prevedibili e password deboli o mai cambiate dall'installazione.
- **File esposti:** i CMS lasciano spesso file di configurazione o di versioning accessibili (`CHANGELOG.txt`, `README.txt`, `wp-config.php.bak`).

La fase di fingerprinting (identificare il CMS e la versione) e il prerequisito: inutile usare WPScan su un target Joomla.

---

## Struttura della cartella

```
04-cms-specific/
+-- drupal/      # CVE-2018-7600 Drupalgeddon2 RCE - finding WEB-015
+-- wordpress/   # WPScan: enumerazione utenti, plugin, brute force
+-- joomla/      # JoomScan: fingerprinting, CVE-2023-23752
```

---

## Fingerprinting: Come Identificare il CMS

Prima di scegliere lo strumento corretto, e necessario identificare il CMS. I segnali rilevatori:

| Indizio | WordPress | Joomla | Drupal |
| :--- | :--- | :--- | :--- |
| Path risorse | `/wp-content/`, `/wp-admin/` | `/administrator/`, `/components/` | `/sites/`, `/modules/` |
| Cookie | `wordpress_`, `wp-settings-` | `joomla_user_state` | `Drupal.visitor` |
| Meta tag | `<meta name="generator" content="WordPress...">` | `<meta name="generator" content="Joomla!...">` | `<meta name="Generator" content="Drupal...">` |
| File di versione | `/readme.html`, `/wp-login.php` | `/CHANGELOG.txt` | `/CHANGELOG.txt`, `/core/CHANGELOG.txt` |
| Risposta HTTP | Header `X-Pingback` | - | - |

Strumenti automatici per il fingerprinting:
- `whatweb -v <TARGET>`: identifica il CMS e la versione.
- `wappalyzer` (browser): fingerprint visivo immediato.
- `nuclei -u <TARGET> -t cms/`: template nuclei specifici per CMS.

---

## `drupal/` - Drupalgeddon2 (CVE-2018-7600)

**ID Finding:** `WEB-015` | **Severity:** `Critico` | **CVSS v3.1:** 9.8

### Contesto operativo

Drupal e un CMS enterprise-grade usato da governi, universita e grandi aziende. CVE-2018-7600, soprannominata "Drupalgeddon2", e una Remote Code Execution non autenticata nel Form API. Le versioni Drupal 6.x, 7.x (prima di 7.58) e 8.x (prima di 8.3.9, 8.4.6, 8.5.1) sono vulnerabili.

L'exploitation documentata in `drupal/README.md` ha prodotto:
- Accesso alla dashboard amministrativa di Drupal.
- Deploy di una Web Shell PHP nascosta come pagina di contenuto.
- Esecuzione di comandi Windows (`ipconfig`) tramite la Web Shell, confermando il controllo totale del server.

La particolarita di questo test e stato il bypass manuale di Windows Defender: gli exploit automatici generano firme rilevabili dall'antivirus, rendendo necessario un approccio manuale tramite payload PHP standard del modulo "PHP Filter" di Drupal.

---

## `wordpress/` - WPScan & WordPress Exploitation

### Contesto operativo

WordPress detiene circa il 43% delle quote di mercato dei CMS mondiali, rendendolo il target piu comune nel web application pentesting. WPScan e lo strumento dedicato: un black-box security scanner specifico per WordPress.

Le fasi principali di un test WordPress:

1. **Fingerprinting:** confermare la versione di WordPress e del tema attivo.
2. **Enumerazione plugin:** identificare tutti i plugin installati e le loro versioni (`--enumerate p`).
3. **Enumerazione utenti:** recuperare gli username degli utenti (`--enumerate u`).
4. **Verifica CVE:** controllare se i plugin/temi/versione core hanno CVE note.
5. **Brute Force:** se la pagina `/wp-login.php` e accessibile e non protetta da CAPTCHA/2FA, eseguire password guessing.

Vedere `wordpress/README.md` per la guida tecnica completa con comandi e output.

---

## `joomla/` - JoomScan & Joomla Exploitation

### Contesto operativo

Joomla e il secondo CMS piu diffuso, con una presenza significativa in ambienti istituzionali e governativi. JoomScan (OWASP) e lo scanner dedicato per l'enumerazione di componenti, plugin e vulnerabilita note.

CVE-2023-23752 e una vulnerabilita di information disclosure non autenticata che permette di accedere alle configurazioni del database (host, username, password) tramite l'API REST di Joomla. L'endpoint vulnerabile e `/api/index.php/v1/config/application?public=true`.

Vedere `joomla/README.md` per la guida tecnica completa con comandi e output.

---

## Flusso operativo consigliato

```
[1] Fingerprinting CMS (02-web-recon/tech-profiler/)
     +-- whatweb -v <TARGET> -> identifica CMS e versione
     +-- nuclei -u <TARGET> -t cms/ -> verifica CVE specifiche
              |
              v
[2] WordPress?
     +-- wpscan --url <TARGET> --enumerate vp,vt,u
     +-- wpscan --url <TARGET> -U utenti.txt -P rockyou.txt
              |
       Joomla?
     +-- joomscan -u <TARGET>
     +-- curl /api/index.php/v1/config/application?public=true (CVE-2023-23752)
              |
       Drupal?
     +-- verificare versione tramite /CHANGELOG.txt
     +-- se 7.x < 7.58 -> CVE-2018-7600 Drupalgeddon2
              |
              v
[3] Post-Exploitation
     +-- accesso admin -> caricare Web Shell
     +-- dump database credenziali
     +-- lateral movement
```

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `wpscan` | WordPress scanner | CLI - Attiva | Enumerazione plugin, utenti, CVE WordPress |
| `joomscan` | Joomla scanner | CLI - Attiva | Fingerprinting e CVE Joomla |
| `droopescan` | CMS scanner | CLI - Attiva | Scansione Drupal, SilverStripe, Wordpress |
| `cmsmap` | Multi-CMS scanner | CLI - Attiva | Scanner generalista per WordPress, Joomla, Drupal |
| `nuclei` | Template-based | CLI - Attiva | Template CMS-specifici aggiornati dalla community |
| `metasploit` | Exploitation framework | CLI/GUI - Attiva | Exploit automatizzati per CVE CMS note |
| `curl` | HTTP client | CLI - Attiva | Test manuale endpoint API CMS (CVE-2023-23752) |

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Active Scanning: Vulnerability Scanning | `T1595.002` | Fingerprinting della versione Drupal tramite `CHANGELOG.txt` e identificazione della vulnerabilita CVE-2018-7600 |
| Initial Access | Exploit Public-Facing Application | `T1190` | Exploitation di CVE-2018-7600 (Drupalgeddon2) sul Form API per ottenere RCE non autenticata (WEB-015) |
| Persistence | Server Software Component: Web Shell | `T1505.003` | Deploy di Web Shell PHP attraverso il modulo "PHP Filter" di Drupal nel nodo di contenuto (WEB-015) |
| Discovery | File and Directory Discovery | `T1083` | Enumerazione del file system del server Windows tramite comandi iniettati nella Web Shell |
| Credential Access | Brute Force: Password Guessing | `T1110.001` | Brute force su `/wp-login.php` con WPScan (WordPress) |
| Discovery | Account Discovery | `T1087` | Enumerazione utenti WordPress con `--enumerate u` (WPScan) |

---

> **Nota:** Il test CVE-2018-7600 (WEB-015) e stato condotto su un'istanza Drupal 7.54 installata
> in locale su una macchina virtuale Windows 10 appositamente configurata per scopi didattici.
> Le attivita WPScan e JoomScan sono state condotte su ambienti di laboratorio autorizzati.
> Lo sfruttamento di CVE note su istanze di produzione senza autorizzazione e un reato penale.
