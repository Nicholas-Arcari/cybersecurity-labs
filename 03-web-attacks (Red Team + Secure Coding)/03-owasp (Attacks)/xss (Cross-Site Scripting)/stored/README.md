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