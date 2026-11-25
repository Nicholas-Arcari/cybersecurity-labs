> [English](README.en.md) | **Italiano**

# Linux hardening - riduzione della superficie d'Attacco

> - **Fase:** Defense & Hardening - System Hardening (Prevention)
> - **Categoria:** Prevention - riduzione della superficie d'attacco e baseline di sicurezza
> - **Prerequisiti:** Accesso root al sistema da hardenizzare; Lynis per l'audit; snapshot/backup prima delle modifiche; conoscenza del ruolo del sistema (per non rompere servizi legittimi)
> - **Output:** Finding DEF-007; sistema hardenizzato secondo baseline CIS; superficie d'attacco ridotta; audit score misurabile e ripetibile

- **Ambiente Operativo:** Server/workstation Linux (Debian/Ubuntu), Lynis come auditor
- **Ruolo:** "Lo Scudo" - previene, non rileva: chiude le porte prima che l'attaccante bussi
- **Tool principali:** Lynis, Bastille, CIS Benchmarks, auditd

---

## Executive summary

L'hardening e la difesa preventiva: mentre SIEM (`../../01-siem-log-analysis/`) e Wazuh rilevano gli attacchi in corso, l'hardening li previene riducendo cio che l'attaccante puo sfruttare. Ogni servizio non necessario disattivato, ogni permesso ristretto, ogni default insicuro corretto e una porta chiusa prima ancora che l'attaccante la trovi. E lo strato piu economico ed efficace della difesa, perche agisce sulla causa (superficie d'attacco) invece che sul sintomo (attacco in corso).

L'approccio non e improvvisato ma guidato da baseline standard. I **CIS Benchmarks** definiscono configurazioni di sicurezza riconosciute per ogni sistema operativo; **Lynis** e lo strumento di audit che misura quanto un sistema vi si conforma, producendo un "hardening index" numerico e una lista prioritizzata di raccomandazioni. Il finding DEF-007 documenta il ciclo audit, hardening, ri-audit, con Lynis come metro di misura oggettivo del miglioramento.

Il valore per questo percorso e speculare all'offensiva: le tecniche di privilege escalation Linux di `04-system-exploitation` (SUID abusabili, sudo mal configurati, cron scrivibili, credenziali in chiaro) sono esattamente cio che l'hardening chiude. Ogni finding EXPLOIT del modulo offensivo ha qui la sua contromisura preventiva.

---

## Struttura della cartella

```
linux-hardening/
+-- README.md      # questo file: audit Lynis + baseline CIS (DEF-007)
+-- img/           # report Lynis e hardening index
```

---

## Audit e hardening con lynis

**ID Finding:** `DEF-007` | **Severity:** `Alto` (riduzione strutturale della superficie d'attacco; previene intere classi di privilege escalation e lateral movement)

### Contesto operativo

Il ciclo di hardening corretto parte dalla misura, non dall'azione: prima si audita il sistema per sapere dove si e (Lynis produce un hardening index e una lista di warning), poi si interviene sulle raccomandazioni prioritarie, infine si ri-audita per verificare il miglioramento. Questo rende l'hardening oggettivo e ripetibile, non una collezione di comandi applicati a caso.

### PoC - fase 1: audit iniziale (baseline)

```Bash
# Installazione e audit completo del sistema
sudo apt install lynis
sudo lynis audit system
```

```
[+] Hardening
    Hardening index : 58 [########------------]        <-- baseline pre-hardening (DEF-007)

  Warnings:
  - [SSH-7408] SSH PermitRootLogin is enabled          <-- root SSH attivo
  - [AUTH-9282] Password aging limits not configured
  - [KRNL-5820] core dumps not disabled
  Suggestions: 47 hardening opportunities
```

### PoC - fase 2: applicazione dell'hardening (esempi mirati)

```Bash
# SSH hardening: nega login root, forza chiavi
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# Rimozione bit SUID non necessari (contromisura a GTFOBins privesc)
sudo chmod u-s /usr/bin/<binario_non_necessario>

# Kernel hardening (sysctl): disabilita core dump, protegge la rete
echo "kernel.core_pattern=|/bin/false" | sudo tee -a /etc/sysctl.d/99-hardening.conf
sudo sysctl --system
```

### PoC - fase 3: ri-audit (misura del miglioramento)

```Bash
sudo lynis audit system
```

```
[+] Hardening
    Hardening index : 84 [################----]        <-- post-hardening (DEF-007)
    # da 58 a 84: superficie d'attacco ridotta in modo misurabile
```

### Operativita difensiva e cautele

- **Misura sempre prima e dopo:** l'hardening index rende il progresso oggettivo; senza baseline non si sa se si e migliorato
- **Non rompere i servizi:** ogni modifica va valutata rispetto al ruolo del sistema (disabilitare un servizio "inutile" che invece serve causa un'interruzione); snapshot prima, test dopo
- **Automazione idempotente:** per parchi macchine, gli hardening vanno applicati via Ansible/script idempotenti allineati a un CIS Benchmark, non a mano host per host
- **Hardening + detection:** l'hardening riduce la superficie ma non elimina il rischio; va abbinato al monitoraggio (Wazuh FIM sui file di config hardenizzati, per rilevare tentativi di annullare l'hardening)

---

## Esperienza di laboratorio

Il valore di Lynis e stato rendere l'hardening misurabile invece che aneddotico. Prima conoscevo le singole contromisure (disabilita root SSH, rimuovi SUID inutili) ma non avevo un modo per sapere "quanto" un sistema fosse sicuro. L'hardening index - da 58 a 84 nel mio ciclo di test - ha trasformato una sensazione ("ora e piu sicuro") in un dato. Questo cambia l'hardening da attivita soggettiva a processo verificabile, ed e esattamente cio che un report professionale richiede.

La soddisfazione difensiva e stata chiudere, una per una, le porte che avevo aperto nel modulo offensivo. Nel modulo 04 avevo sfruttato SUID abusabili e sudo mal configurati per l'escalation; qui li rimuovevo e li restringevo, vedendo Lynis confermare la chiusura di quelle specifiche vie. Il collegamento diretto tra un finding offensivo (EXPLOIT-008, GTFOBins) e la sua contromisura preventiva ha reso tangibile la simmetria attacco/difesa.

La cautela appresa e stata il rovescio dell'entusiasmo. Nel tentativo di massimizzare l'hardening index, ho disabilitato un servizio che credevo inutile e ho rotto una funzionalita di test. La lezione: l'hardening massimo non e l'obiettivo, l'hardening appropriato al ruolo del sistema lo e. Un server ha bisogni diversi da una workstation; applicare una baseline alla cieca senza capire il contesto operativo causa piu danni che benefici. Snapshot prima, test dopo, sempre.

---

## Analisi teorica: L'Hardening come riduzione della superficie d'Attacco

La superficie d'attacco di un sistema e l'insieme di tutti i punti attraverso cui un attaccante puo tentare di interagire con esso: servizi in ascolto, account, binari privilegiati, permessi sui file, configurazioni esposte. L'hardening e l'applicazione sistematica di un principio: minimizzare questa superficie. Ogni elemento non necessario e un rischio senza beneficio; rimuoverlo elimina un potenziale vettore a costo zero funzionale.

Questo si fonda sul principio del minimo privilegio e del "secure by default" rovesciato. I sistemi arrivano configurati per la massima compatibilita e facilita d'uso, non per la sicurezza: servizi attivi "per ogni evenienza", permessi larghi, default permissivi. L'hardening inverte questa impostazione, partendo dal presupposto opposto - tutto disabilitato finche non c'e una ragione esplicita per abilitarlo. E il passaggio da "aperto salvo divieto" a "chiuso salvo necessita".

Il legame con il resto della difesa e gerarchico. L'hardening e il primo strato (prevenzione): riduce cio che puo essere attaccato. Il monitoraggio e il secondo (detection): rileva cio che supera la prevenzione. La risposta e il terzo (reaction): contiene cio che viene rilevato. L'hardening e il piu efficiente perche agisce a monte: un attacco prevenuto non deve essere rilevato ne contenuto. Ma non e sufficiente da solo - nessuna superficie e mai zero - motivo per cui si integra con la detection e la response degli altri strati. La difesa in profondita e la somma di questi strati, e l'hardening ne e le fondamenta.

---

## Scenario reale: la prevenzione in azione

> Questa sezione descrive come questo controllo difensivo opererebbe in un incidente reale.

### Prospettiva attaccante (cosa tenta)

L'attaccante, ottenuto un accesso iniziale come utente non privilegiato, cerca una via di privilege escalation: enumera i binari SUID, verifica le regole sudo, cerca cron job scrivibili e credenziali in chiaro - esattamente il playbook di `04-system-exploitation`.

### Prospettiva difensore (come il controllo risponde)

```
[DEF-007] Sistema hardenizzato secondo baseline CIS (Lynis index 84)
        |
        v
Attaccante enumera SUID -> i binari abusabili sono stati rimossi (chmod u-s)
        |
        v
Attaccante verifica sudo -> configurazione minima, nessun NOPASSWD abusabile
        |
        v
Attaccante cerca cron scrivibili -> permessi ristretti, nessuna via
        |
        v
Escalation fallita: la superficie che l'attacco richiede non esiste piu
```

**Valore difensivo:** l'hardening non genera un alert, genera un non-evento: l'escalation semplicemente non trova appigli. Le classi di privilege escalation piu comuni (SUID, sudo, cron, permessi) sono chiuse a monte, prima che l'attaccante possa provarle. Questo e il valore silenzioso della prevenzione: l'attacco migliore e quello che non ha mai avuto una superficie su cui aggrapparsi.

**Sinergia con la detection:** abbinare il FIM (Wazuh, DEF-003) ai file di configurazione hardenizzati significa rilevare anche i tentativi di annullare l'hardening (un attaccante che prova a rimettere il SUID o a riabilitare root SSH genera un alert FIM). Prevenzione e detection si rafforzano a vicenda.

**Lezione difensiva:** la prevenzione e invisibile quando funziona - non ci sono alert, solo attacchi che falliscono in silenzio. Questo la rende sottovalutata ma e lo strato piu efficiente: ogni vettore chiuso dall'hardening e un incidente che non accadra mai.

---

## Tool di riferimento

| tool | tipo | ruolo | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Lynis` | security auditor | cli | audit di hardening con index numerico e raccomandazioni |
| `CIS Benchmarks` | baseline standard | documento | configurazioni di sicurezza riconosciute per os/servizi |
| `Bastille` | hardening script | cli | hardening guidato interattivo (legacy ma didattico) |
| `auditd` | audit framework | daemon | logging degli eventi di sistema per detection e compliance |
| `OpenSCAP` | compliance scanner | cli | verifica di conformita a profili di sicurezza (scap) |
| `Ansible` (hardening role) | automation | iac | applicazione idempotente dell'hardening su parchi macchine |

> **Tool moderno consigliato:** `Lynis` per l'audit e la misura (l'hardening index rende il progresso oggettivo). Per l'applicazione su scala, i ruoli Ansible allineati ai `CIS Benchmarks` (es. le collection di DevSec Hardening Framework) rendono l'hardening idempotente e ripetibile. `OpenSCAP` per la verifica di compliance formale. Bastille resta didatticamente utile ma e datato.

---

## Mappatura MITRE ATT&CK

> La tabella mappa le tecniche d'attacco che l'hardening **previene** riducendo la superficie.

| tattica (prevenuta) | tecnica | id mitre | ruolo del controllo |
| :--- | :--- | :--- | :--- |
| privilege escalation | abuse elevation control: sudo and sudo caching | `T1548.003` | configurazione sudo minima, nessun nopasswd abusabile (DEF-007) |
| privilege escalation | setuid and setgid | `T1548.001` | rimozione dei bit suid non necessari (DEF-007) |
| privilege escalation | scheduled task/job: cron | `T1053.003` | permessi ristretti su cron e directory (DEF-007) |
| persistence | account manipulation: ssh authorized keys | `T1098.004` | disabilitazione root login, forzatura chiavi, permessi ristretti |
| credential access | unsecured credentials: credentials in files | `T1552.001` | bonifica delle credenziali in chiaro nei file di config |

| contromisura difensiva (d3fend) | id d3fend | applicazione |
| :--- | :--- | :--- |
| platform hardening | `D3-PH` | riduzione della superficie d'attacco via baseline cis |
| local account monitoring | `D3-LAM` | audit e restrizione degli account e dei privilegi |
| executable denylisting | `D3-EDL` | rimozione/restrizione dei binari privilegiati abusabili |

---

> **Nota:** Tutte le attivita documentate sono state condotte su sistemi di laboratorio di proprieta dell'autore. L'hardening va applicato con attenzione al ruolo del sistema per non interrompere servizi legittimi (snapshot e test obbligatori). Le tecniche sono documentate a scopo educativo e di difesa in contesto autorizzato.
