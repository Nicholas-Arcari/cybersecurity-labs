# Drupal Core Remote Code Execution (Drupalgeddon 2)

---

## 1 Executive Summary

Durante l'attività di Penetration Testing condotta sull'ambiente di test, è stata identificata una vulnerabilità critica nell'istanza del CMS Drupal.

La vulnerabilità, nota come Drupalgeddon 2 (CVE-2018-7600), risiede in una mancata sanitizzazione degli input nel sottosistema Form API di Drupal.

Questa falla permette a un attaccante remoto e non autenticato di iniettare ed eseguire codice arbitrario sul server ospitante (Remote Code Execution).

Nel contesto analizzato, l'exploit ha permesso di ottenere il controllo totale del sistema target (Windows 10) con i privilegi dell'utente che esegue il servizio web (Apache/System), esponendo l'intera infrastruttura a rischi di esfiltrazione dati, installazione di malware e movimento laterale.

---

## 2 Technical Analysis

#### 1. Reconnaissance & Fingerprinting

La fase iniziale di ricognizione ha permesso di identificare la versione specifica di Drupal in uso.

Analizzando i file pubblici accessibili (es. `CHANGELOG.txt`) o gli header HTTP, è stato confermato che il target esegue una versione obsoleta e vulnerabile.

Evidence:

Lo screenshot seguente mostra l'identificazione della versione (es. 7.54) tramite analisi dei file statici esposti.

![](./img/Screenshot_2026-02-16_17_55_22.jpg)

#### 2. Exploitation (CVE-2018-7600)

La vulnerabilità sfrutta il modo in cui Drupal gestisce le richieste AJAX nei form (Form API).

Un attaccante può inviare una richiesta POST malevola manipolando i parametri `#post_render` (in Drupal 7) o simili array di renderizzazione. Questo induce il CMS a eseguire una funzione PHP arbitraria (come `passthru`, `exec` o `system`) passata come parametro dall'attaccante.

Vettore d'Attacco:

- Tool Utilizzato: Metasploit Framework / Script Python Custom
- Modulo: `exploit/unix/webapp/drupal_drupalgeddon2`
- Payload: PHP Meterpreter (Reverse TCP)

Esecuzione:

Lanciando l'exploit contro l'IP del target Windows, il server ha processato la richiesta malevola istanziando una connessione inversa verso la macchina attaccante (Kali Purple).

Evidence:

Lo screenshot mostra la console di Metasploit con la conferma dell'apertura della sessione Meterpreter.

![](./img/Screenshot_2026-02-16_17_17_45.jpg)

#### 3. Post-Exploitation & Access Verification

Una volta ottenuta la shell remota, è stata verificata l'esecuzione di comandi nel contesto del sistema operativo Windows.

Sono stati eseguiti comandi di enumerazione di base (`whoami`, `ipconfig`, `sysinfo`) per confermare il compromesso.

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

    Hardening del Server:

    - Disabilitare funzioni PHP pericolose nel file `php.ini` (es. `disable_functions = exec,passthru,shell_exec,system`).
    - Rimuovere file non necessari come `CHANGELOG.txt` o `INSTALL.txt` dalla root del sito per complicare il fingerprinting.
