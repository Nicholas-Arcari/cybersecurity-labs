> [English](README.en.md) | **Italiano**

# Vulnerability Assessment: Reflected Cross-Site Scripting (XSS)

> - **Fase:** Web Attack - XSS Reflected
> - **Visibilita:** Bassa - richiesta singola con payload nel parametro URL, indistinguibile da normale navigazione
> - **Prerequisiti:** Parametro URL che viene riflesso nella risposta HTML senza encoding, identificato tramite web recon
> - **Output:** Esecuzione JavaScript nel browser della vittima (alert PoC), virtual defacement, vector per phishing, finding WEB-005

---

**ID Finding:** `WEB-005` | **Severity:** `Medio` | **CVSS v3.1:** 6.1

---

## 1 Executive Summary

Durante l'analisi dell'applicazione web `testphp.vulnweb.com`, è stata individuata una vulnerabilità di tipo Reflected Cross-Site Scripting (XSS).

L'applicazione non sanitizza correttamente l'input utente fornito tramite i parametri URL, riflettendolo direttamente nel codice HTML della pagina.

Questa vulnerabilità permette a un attaccante di creare link malevoli che, se visitati dalla vittima, eseguono codice JavaScript arbitrario nel contesto del browser dell'utente.

I rischi includono:

- Session Hijacking: Furto di cookie di sessione.
- Phishing: Modifica del contenuto della pagina per ingannare l'utente.
- Redirect Malevoli: Reindirizzamento dell'utente verso siti esterni.

---

## 2 Technical Analysis

#### Scenario A: URL Parameter Injection

L'endpoint `listproducts.php` accetta il parametro `cat` per filtrare i prodotti. È stato verificato che inserendo codice HTML/JavaScript nel valore del parametro, questo viene eseguito dal browser senza filtri.

Vettore d'Attacco:

L'attacco avviene tramite la manipolazione dell'URL. Un attaccante può inviare questo link via email o social engineering.

Payload (Proof of Concept):

```html
http://testphp.vulnweb.com/listproducts.php?cat=<script>alert('XSS Riuscito')</script>
```

Analisi dell'Evidenza:

Come mostrato nello screenshot sottostante, il payload iniettato nell'URL viene processato dal server e incluso nella risposta. Il browser interpreta il tag `<script>` ed esegue la funzione `alert()`, aprendo un popup con il messaggio personalizzato.

![](./img/Screenshot_2026-02-15_19_02_29.jpg)

#### Scenario B: Virtual Defacement (Phishing Vector)

Oltre all'esecuzione di codice JavaScript, è stato verificato che l'applicazione permette l'iniezione di tag HTML arbitrari (HTML Injection).

Questo vettore è particolarmente critico per attacchi di Social Engineering: un attaccante può sfruttare la fiducia dell'utente nel dominio legittimo (`testphp.vulnweb.com`) per presentare falsi messaggi di errore o moduli di login fraudolenti.

Payload (Defacement & Fake Login):

```html
http://testphp.vulnweb.com/listproducts.php?cat=<h1 style="color:red;font-size:40px">SISTEMA COMPROMESSO</h1><form>Login:<input type="text"><input type="submit"></form>
```

Analisi dell'Evidenza:

Lo screenshot sottostante mostra l'alterazione visiva della pagina. L'applicazione renderizza il titolo "SISTEMA COMPROMESSO" e un campo di input, simulando una richiesta di credenziali. L'errore SQL visibile conferma ulteriormente che l'input non è stato validato come intero.

![](./img/Screenshot_2026-02-15_19_12_03.jpg)

---

## 3 Remediation Plan

La vulnerabilità Reflected XSS deve essere corretta trattando tutto l'input utente come non fidato.

- Context-Aware Output Encoding (Fondamentale):
    
    Prima di riflettere qualsiasi dato utente nella pagina HTML, convertire i caratteri speciali nelle rispettive HTML Entities.

    - `<` diventa `&lt;`

    - `>` diventa `&gt;`

    - `"` diventa `&quot;`

    - `'` diventa `&#x27;`

Esempio PHP Sicuro:

```PHP
// NON fare questo:
echo "Categoria: " . $_GET['cat'];

// FAI questo:
echo "Categoria: " . htmlspecialchars($_GET['cat'], ENT_QUOTES, 'UTF-8');
```

Input Validation:

Se il parametro `cat` deve essere un numero (ID categoria), forzare il tipo a `Integer` e rifiutare qualsiasi input non numerico.

Content Security Policy (CSP):

Implementare header CSP per limitare le sorgenti da cui il browser può caricare ed eseguire script (es. disabilitare `unsafe-inline`).

---

## Analisi a Basso Livello: Reflected XSS - Dal Parametro URL al DOM

### Meccanica dell'Iniezione

La Reflected XSS si verifica quando l'input utente viene riflesso nella risposta HTTP senza encoding:

```
Attaccante crea URL malevolo:
http://target/list.php?cat=<script>alert(1)</script>
    |
    v
Server PHP processa la richiesta:
$cat = $_GET['cat'];  // <script>alert(1)</script>
echo "<h1>Categoria: " . $cat . "</h1>";
    |
    v
Response HTTP inviata al browser della vittima:
<h1>Categoria: <script>alert(1)</script></h1>
    |
    v
Browser HTML parser incontra il tag <script>:
-> Crea nodo Script nel DOM
-> Esegue alert(1) nel contesto della pagina
-> Cookie, localStorage, DOM accessibili allo script
```

### Virtual Defacement e Phishing: Impatto Reale

Il payload HTML Injection (Scenario B) e particolarmente insidioso perche:
- L'URL e sul dominio legittimo del target (`testphp.vulnweb.com`)
- Il certificato SSL e valido (lucchetto verde nel browser)
- La vittima non ha modo di distinguere il contenuto legittimo da quello iniettato
- Un form di login iniettato inviera le credenziali al server dell'attaccante

---

## Blue Team: Detection e Difese Anti-XSS

### Content Security Policy (CSP)

CSP e la difesa piu efficace contro XSS Reflected:

```
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-abc123'; style-src 'self'
```

Con questa policy:
- `script-src 'self'` blocca tutti gli script inline (incluso `<script>alert(1)</script>`)
- Il nonce cambia ad ogni richiesta, rendendo impossibile per l'attaccante indovinarlo
- Anche se il payload viene riflesso nel DOM, il browser rifiuta di eseguirlo

### Difese Multi-Layer

| Layer | Difesa | Cosa blocca |
| :--- | :--- | :--- |
| Input | Type validation (`cat` deve essere intero) | Rifiuta input non numerico |
| Output | `htmlspecialchars()` | Converte `<>` in entities |
| Browser | CSP header | Blocca script inline/external non autorizzati |
| Cookie | `HttpOnly` flag | Impedisce accesso JS ai cookie anche se XSS riesce |
| Session | `SameSite=Strict` | Impedisce invio cookie in richieste cross-site |

---

## Esperienza di Laboratorio

La differenza tra i due scenari (alert PoC vs virtual defacement) ha dimostrato la distanza tra il "proof of concept didattico" e l'impatto reale. Il popup `alert()` dimostra l'esecuzione di codice ma non convince un cliente; il form di login falso iniettato nel dominio legittimo dimostra un rischio di phishing concreto che anche un non-tecnico comprende immediatamente.

L'errore SQL visibile nello screenshot del defacement ha rivelato un secondo finding: il parametro `cat` atteso come intero genera un errore SQL quando riceve una stringa HTML. Questo indica che lo stesso parametro e vulnerabile sia a XSS (lato client) che potenzialmente a SQL Injection (lato server) - una doppia vulnerabilita sullo stesso endpoint.

La classificazione a `Medio` (vs `Alto` per la Stored) riflette il requisito di interazione utente: la vittima deve cliccare un link malevolo. In un assessment reale, la severity viene elevata a `Alto` se il target e un'applicazione con dati sensibili (banking, healthcare) o se l'attaccante puo distribuire il link tramite canali fidati (email aziendale, Slack interno).

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Exploitation del parametro `cat` vulnerabile a XSS Reflected su `listproducts.php`, con injection di `<script>alert('XSS Riuscito')</script>` (WEB-005) |
| Credential Access | Steal Web Session Cookie | `T1539` | Il payload XSS Reflected e il vettore primario per rubare il cookie di sessione dalla vittima che clicca il link malevolo (WEB-005) |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | Distribuzione dell'URL malevolo `listproducts.php?cat=<PAYLOAD>` tramite email o social engineering per colpire utenti specifici (WEB-005) |

---

> **Nota:** Il finding WEB-005 e stato documentato su `testphp.vulnweb.com`. La Reflected XSS
> e classificata `Medio` perche richiede interazione dell'utente (click sul link malevolo) a
> differenza della Stored XSS. In presenza di contenuto sensibile (es. token di sessione admin
> accessibile via JavaScript), la severity effettiva puo essere elevata ad `Alto`.