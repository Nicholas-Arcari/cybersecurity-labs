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