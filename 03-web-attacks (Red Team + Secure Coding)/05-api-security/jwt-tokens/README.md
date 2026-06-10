> [English](README.en.md) | **Italiano**

# JWT Authentication Mechanism

> - **Fase:** Web Attack - API Security (JWT)
> - **Visibilita:** Bassa - il brute force della firma JWT e offline, nessuna richiesta verso il server durante il crack
> - **Prerequisiti:** Token JWT valido ottenuto come utente autenticato (anche con permessi base), strumento di brute force (hashcat, jwt_tool)
> - **Output:** Chiave segreta recuperata (`secret123`), token admin forgiato, accesso a funzionalita privilegiate, finding WEB-012

---

**ID Finding:** `WEB-012` | **Severity:** `Critico` | **CVSS v3.1:** 9.8

---

## 1 Executive Summary

Durante l'analisi del meccanismo di autenticazione dell'applicazione target, è stata individuata una vulnerabilità critica nella gestione dei token di sessione (JWT - JSON Web Tokens).

L'applicazione utilizza una chiave segreta debole ("Weak Secret") per firmare digitalmente i token. Questo ha permesso all'analista di effettuare un attacco di forza bruta offline, recuperare la chiave segreta e generare token arbitrari.

Impatto: Un attaccante può impersonare qualsiasi utente, incluso l'amministratore, ottenendo il controllo completo dell'applicazione (Privilege Escalation & Account Takeover).

---

## 2 Dettagli Tecnici della Vulnerabilità
Descrizione

L'applicazione rilascia token JWT firmati con l'algoritmo HS256 (HMAC con SHA-256). Questo è un algoritmo simmetrico, il che significa che la stessa chiave viene usata sia per firmare che per verificare il token.

La sicurezza di HS256 dipende interamente dalla complessità della chiave segreta (`SECRET_KEY`). L'analisi ha rivelato che la chiave utilizzata era una stringa semplice presente in comuni dizionari di password (`secret123`).

Vettore d'Attacco

- Raccolta: L'attaccante richiede un token legittimo come utente "guest".

![](./img/Screenshot_2026-02-18_15_55_23.jpg)

- Analisi: Il token viene analizzato. L'header {`"alg": "HS256"`} conferma l'uso di crittografia simmetrica.
- Cracking: Viene lanciato uno script di brute-force (`jwt_cracker.py`) che tenta di verificare la firma del token usando un elenco di password comuni.

![](./img/Screenshot_2026-02-18_15_55_35.jpg)

- Forging (Falsificazione): Una volta trovata la password (`secret123`), l'attaccante modifica il payload del token cambiando il ruolo da `user` a `admin` e ricalcola la firma valida.

Proof of Concept (PoC)

Token Originale (Guest):

```JSON
Header: {"alg": "HS256", "typ": "JWT"}
Payload: {"user": "guest", "role": "user"}
Signature: [Firma valida con 'secret123']
```

Token Falsificato (Admin):

```JSON
Header: {"alg": "HS256", "typ": "JWT"}
Payload: {"user": "hacker", "role": "admin"}  <-- MODIFICATO
Signature: [Nuova firma calcolata dall'attaccante]
```

Quando il token falsificato viene inviato all'applicazione, questa lo accetta come autentico e garantisce i privilegi amministrativi, mostrando il messaggio: FLAG: HAI VINTO! .

![](./img/Screenshot_2026-02-18_15_55_44.jpg)

---

## 3 Root Cause Analysis (Codice Vulnerabile)

Di seguito l'analisi del codice Python responsabile della vulnerabilità.

Codice Vulnerabile (Hardcoded Weak Secret)

L'errore risiede nell'utilizzo di una stringa breve, prevedibile e hardcodata nel codice sorgente.

```Python
# VULNERABILE
import jwt

# 1. La chiave è troppo breve e semplice (suscettibile a brute-force)
# 2. La chiave è hardcodata nel codice (visibile se il codice trapela)
SECRET_KEY = "secret123" 

def create_token(user):
    payload = {"user": user, "role": "user"}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

---

## 4 Remediation (Secure Coding)

Per mitigare questa vulnerabilità, si raccomandano due approcci possibili.

#### Soluzione A: Strong Secret (Se si mantiene HS256)

Se si deve usare HS256, la chiave deve essere una stringa casuale ad alta entropia (minimo 32-64 caratteri) e non deve mai essere scritta nel codice, ma caricata da variabili d'ambiente.

```Python
# SICURO (Approccio Simmetrico)
import jwt
import os

# Carica la chiave dalle variabili d'ambiente o genera un errore
# In produzione: export JWT_SECRET='lunga_stringa_casuale_e_complessa_!@#123'
SECRET_KEY = os.environ.get("JWT_SECRET")

if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise ValueError("La chiave segreta JWT è assente o troppo debole!")

def create_token(user):
    # ... logica uguale ...
```

#### Soluzione B: Crittografia Asimmetrica (RS256) - Consigliata

L'approccio migliore per sistemi distribuiti è usare una coppia di chiavi (Privata per firmare, Pubblica per verificare). Anche se un attaccante trova la chiave pubblica, non può creare nuovi token.

```Python
# SICURO (Approccio Asimmetrico)
# private_key.pem -> Usata SOLO dal server di autenticazione per FIRMARE
# public_key.pem  -> Distribuita ai servizi per VERIFICARE

with open("private_key.pem", "rb") as f:
    PRIVATE_KEY = f.read()

def create_token(user):
    payload = {"user": user, "role": "user"}
    # RS256 usa la chiave privata
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
```

---

## 5 Conclusioni

L'utilizzo di "secret" deboli nei JWT vanifica l'intero scopo della firma crittografica. La facilità con cui è possibile eseguire il brute-force offline (senza allertare il server con traffico di rete) rende questa vulnerabilità estremamente pericolosa.

Si raccomanda l'immediata rotazione delle chiavi crittografiche e l'adozione di variabili d'ambiente per la gestione dei segreti.

---

## Analisi a Basso Livello: Struttura JWT e Vettori di Attacco

### Anatomia di un Token JWT

Un JWT e composto da tre parti separate da punti, ciascuna codificata in Base64URL:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZ3Vlc3QiLCJyb2xlIjoidXNlciJ9.xxxxx
|___________________________________|.|__________________________________|.|_____|
           HEADER (Base64)                      PAYLOAD (Base64)           SIGNATURE

Header decodificato:    {"alg": "HS256", "typ": "JWT"}
Payload decodificato:   {"user": "guest", "role": "user"}
Signature:              HMAC-SHA256(base64url(header) + "." + base64url(payload), SECRET_KEY)

Processo di verifica lato server:
1. Riceve il token dal client (header Authorization: Bearer <token>)
2. Splitta per "." -> [header, payload, signature]
3. Ricalcola: expected = HMAC-SHA256(header + "." + payload, SECRET_KEY)
4. Confronta: expected == signature_ricevuta
5. Se match -> token valido, legge il payload
6. Se mismatch -> 401 Unauthorized
```

### Attacco alg:none (CVE-2015-9235)

Un attacco classico ai JWT consiste nel modificare l'header per usare `"alg": "none"`, che dice al server di non verificare la firma:

```python
# Token con alg:none
import base64, json

header = base64.urlsafe_b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode()).rstrip(b'=')
payload = base64.urlsafe_b64encode(json.dumps({"user": "admin", "role": "admin"}).encode()).rstrip(b'=')
token = header.decode() + "." + payload.decode() + "."  # firma vuota

# Se il server accetta alg:none -> accesso admin senza chiave
# Librerie moderne (PyJWT >= 2.x) rifiutano alg:none per default
```

### Hashcat per JWT Cracking

```Bash
# Formato hashcat per JWT (mode 16500)
echo "eyJhbGci...eyJ1c2Vy...xxxxx" > jwt.txt

# Brute force con dizionario
hashcat -m 16500 jwt.txt /usr/share/wordlists/rockyou.txt

# Speed su GPU (RTX 4090):
# HS256: ~2.5 GH/s (miliardi di tentativi/sec)
# HS384: ~1.8 GH/s
# HS512: ~1.2 GH/s
# Una password da dizionario viene trovata in secondi
```

### Confronto Algoritmi JWT

| Algoritmo | Tipo | Chiave | Caso d'uso | Rischio se chiave debole |
| :--- | :--- | :--- | :--- | :--- |
| HS256 | Simmetrico | Shared secret | Monoliti (singolo server) | Brute force offline |
| RS256 | Asimmetrico | Private/Public key pair | Microservizi distribuiti | Nessuno (chiave > 2048 bit) |
| ES256 | Asimmetrico (ECDSA) | Private/Public key pair | Mobile, IoT (chiavi piccole) | Nessuno (curva P-256) |
| none | Nessuno | Nessuna | MAI in produzione | Token forgiabile senza limiti |

---

## Esperienza di Laboratorio

Il cracking offline della chiave `secret123` ha richiesto meno di un secondo con lo script `jwt_cracker.py` basato su dizionario. Questo tempo e significativo: l'attacco e completamente invisibile al server perche il cracking avviene localmente sulla macchina dell'attaccante. Non ci sono log, non ci sono richieste HTTP, nessun IDS puo rilevare la fase di cracking. L'unica richiesta al server e quella iniziale per ottenere un token valido (una singola richiesta legittima).

Il confronto tra HS256 e RS256 ha evidenziato la differenza fondamentale: con HS256, conoscere la chiave permette sia di verificare che di creare token. Con RS256, la chiave pubblica (che puo essere distribuita liberamente) permette solo la verifica, non la creazione. Per sistemi distribuiti dove piu servizi devono validare i token, RS256 e strutturalmente superiore perche elimina la necessita di condividere un segreto.

La modifica del payload da `"role": "user"` a `"role": "admin"` con successivo ricalcolo della firma ha dimostrato il concetto di privilege escalation orizzontale e verticale in un'unica operazione: l'attaccante non solo impersona un altro utente, ma sceglie arbitrariamente il livello di privilegio. La firma ricalcolata e matematicamente identica a quella che il server avrebbe generato, rendendo il token falsificato indistinguibile da uno legittimo.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Credential Access | Brute Force: Password Cracking | `T1110.002` | Brute force offline della firma HMAC-SHA256 del token JWT usando `jwt_cracker.py` con dizionario, recuperando la chiave `secret123` (WEB-012) |
| Defense Evasion | Use Alternate Authentication Material | `T1550` | Utilizzo del token JWT falsificato con payload `{"role": "admin"}` e firma ricalcolata per accedere a funzionalita amministrative (WEB-012) |
| Lateral Movement | Valid Accounts: Cloud Accounts | `T1078.003` | Impersonazione dell'account admin tramite token JWT forgiato, ottenendo accesso completo all'applicazione (WEB-012) |

---

> **Nota:** La vulnerabilita JWT e stata identificata su un'applicazione Flask/Python di laboratorio
> locale. La chiave debole `secret123` e stata scelta deliberatamente per scopi dimostrativi.
> Il finding WEB-012 dimostra che il brute force offline dei JWT e un attacco silenzioso: nessun
> log lato server, nessun rate limiting applicabile, nessun IDS puo rilevarlo durante la fase
> di cracking.