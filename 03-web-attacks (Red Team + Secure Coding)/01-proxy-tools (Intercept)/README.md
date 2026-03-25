# 01 - Proxy Tools (Intercept)

> - **Fase:** Web Attack - Proxy Setup & Traffic Interception
> - **Visibilita:** Locale - il traffico rimane tra browser e proxy, nessun pacchetto aggiuntivo verso il target
> - **Prerequisiti:** Browser configurato per usare il proxy (`127.0.0.1:8080`), certificato CA del proxy installato nel trust store del browser
> - **Output:** Intercettazione e manipolazione del traffico HTTP/HTTPS, log delle richieste, finding WEB-001

---

## Introduzione

Prima di testare qualsiasi applicazione web, e necessario posizionarsi tra il browser e il server. I tool di proxy intercettazione realizzano un **Man-in-the-Middle locale**: il browser invia le richieste al proxy, che le blocca, le rende ispezionabili e modificabili, poi le invia al server reale.

Senza questo stadio, ogni test e limitato a cio che e visibile nell'interfaccia utente. Con il proxy attivo, si accede all'intero livello HTTP: header nascosti, token di sessione, parametri inviati via POST, risposte del server prima che il browser le elabori.

La logica operativa e:

1. Il browser parla con il proxy (Burp Suite o OWASP ZAP).
2. Il proxy intercetta la richiesta, la blocca e la presenta all'analista.
3. L'analista la modifica (User-Agent, cookie, parametri) e la invia al server.
4. Il server risponde al proxy, che a sua volta risponde al browser.

Per il traffico HTTPS, il proxy deve generare certificati SSL falsi al volo. Il browser accetta questi certificati solo se la CA del proxy e installata nel suo trust store - da qui la necessita della configurazione dei certificati descritta in `certificates/`.

---

## Struttura della cartella

```
01-proxy-tools (Intercept)/
+-- burp-suite/       # Configurazione proxy, User-Agent spoofing, BApp Store
+-- certificates/     # Installazione CA Burp per intercettazione HTTPS
+-- owasp-zap/        # Scanner DAST automatizzato - finding WEB-001
```

---

## `burp-suite/` - Traffic Interception & Manipulation

### Contesto operativo

Burp Suite e lo standard de facto per il web application penetration testing. Si usa in modalita manuale per analizzare singole richieste, manipolare parametri, testare logiche di business e condurre attacchi mirati. La versione Community Edition limita la velocita dello Scanner; la Professional Edition e usata in engagement reali.

I casi d'uso principali:
- **User-Agent Spoofing:** fingere di essere un crawler (GoogleBot) per bypassare WAF che bloccano scanner noti.
- **Parameter Tampering:** modificare valori di form POST, ID di sessione, token CSRF.
- **Repeater:** rinviare richieste modificate al server in modo iterativo (utile per SQLi manuale e IDOR testing).
- **Intruder:** attacchi automatizzati su singoli parametri (brute force, fuzzing).

### Comandi essenziali

```Bash
# Avvio di Burp Suite Community Edition da terminale
burpsuite
```

Configurazione browser (Firefox):
- `Impostazioni -> Rete -> Impostazioni Connessione -> Proxy manuale`
- HTTP Proxy: `127.0.0.1` - Porta: `8080`

---

## `certificates/` - HTTPS Interception Setup

### Contesto operativo

Il traffico HTTPS moderno e cifrato end-to-end. Per intercettarlo, il proxy genera un certificato SSL per ogni dominio visitato, firmato dalla propria CA interna. Il browser accetta questo certificato solo se la CA e stata importata come "autorita fidata".

Senza questo passaggio, il browser mostra un errore `SEC_ERROR_UNKNOWN_ISSUER` e rifiuta di caricare le pagine HTTPS, rendendo impossibile il test di qualsiasi applicazione moderna.

### Procedura

1. Avviare Burp Suite e navigare su `http://burp` dal browser configurato con il proxy.
2. Scaricare il certificato `cacert.der`.
3. In Firefox: `Impostazioni -> Privacy -> Certificati -> Visualizza certificati -> Importa`.
4. Selezionare `cacert.der` e abilitare "Trust this CA to identify websites".
5. Verificare: visitare `https://google.com` - l'emittente del certificato deve essere "PortSwigger CA".

---

## `owasp-zap/` - DAST Scanner Automatizzato

**ID Finding:** `WEB-001` | **Severity:** `Medio` | **CVSS v3.1:** 5.4

### Contesto operativo

OWASP ZAP (Zed Attack Proxy) e lo scanner DAST open-source di riferimento. A differenza di Burp Suite (analisi manuale), ZAP e ottimizzato per la scansione automatizzata: esegue un crawler per mappare tutte le pagine e i form, poi lancia payload di test (SQLi, XSS, CSRF) su ogni parametro trovato.

Il caso d'uso primario in ambienti aziendali e l'integrazione nelle pipeline CI/CD (Jenkins, GitHub Actions) per bloccare automaticamente il deploy se vengono rilevate vulnerabilita. Per un analista, ZAP fornisce una prima baseline rapida prima dell'analisi manuale con Burp.

### Comandi

```Bash
# Avvio OWASP ZAP da terminale
zaproxy
```

Output di esempio (sezione Alerts):

```
Alert: Absence of Anti-CSRF Tokens                     <-- WEB-001
Risk: Medium
Confidence: Medium
URL: http://testphp.vulnweb.com/guestbook.php
Evidence: <form method="POST" action="/guestbook.php">
Description: No Anti-CSRF tokens were found in a HTML submission form.

Alert: User Controllable HTML Element Attribute
Risk: Medium
URL: http://testphp.vulnweb.com/listproducts.php
Parameter: cat
```

### Analisi del Finding WEB-001

Il form `guestbook.php` non implementa token CSRF. Un attaccante puo costruire una pagina web malevola che invia richieste POST al form come se provenissero dall'utente autenticato, eseguendo azioni a suo nome (post di contenuto, modifica profilo).

### Remediation

- **Azione immediata:** generare e validare un token CSRF casuale (es. usando `csurf` in Node.js, `django.middleware.csrf.CsrfViewMiddleware` in Django) per ogni form stateful.
- **Azione strutturale:** implementare il pattern Synchronizer Token Pattern o Double Submit Cookie su tutti i form POST.
- **Verifica:** rilanciare OWASP ZAP dopo la patch e confermare che l'alert `Absence of Anti-CSRF Tokens` non sia piu presente.

---

## Flusso operativo consigliato

```
[1] Configurare browser -> proxy 127.0.0.1:8080
         |
         v
[2] Installare certificato CA Burp (certificates/)
         |
         v
[3] Navigare il target con Intercept ON (burp-suite/)
         +-- analisi manuale: Repeater, Intruder
         |
         v
[4] Avviare scan automatico (owasp-zap/)
         +-- Automated Scan -> Spider -> Active Scan
         |
         v
[5] Triaging degli alert
         +-- Verifica manuale di ogni alert (elimina falsi positivi)
         +-- Documenta i finding confermati
```

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Burp Suite Community` | Proxy / Interceptor | GUI + Browser Proxy | Analisi manuale, modifica richieste, Repeater |
| `Burp Suite Professional` | Proxy / Scanner | GUI + Browser Proxy | Engagement reali, scan automatico avanzato |
| `OWASP ZAP` | DAST Scanner | GUI + CLI | Scansione automatizzata, integrazione CI/CD |
| `mitmproxy` | Proxy CLI | Terminale | Intercettazione leggera da riga di comando |
| `Caido` | Proxy moderno | Web UI | Alternativa moderna a Burp, interfaccia browser-based |

> **Tool moderno consigliato:** `Caido` - alternativa a Burp Suite con interfaccia web nativa, workflow YAML-based e ottima gestione delle sessioni. Comando: installare da `https://caido.io` con il package manager dedicato.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Collection | Man-in-the-Middle | `T1557` | Posizionamento del proxy Burp Suite tra browser e server per intercettare il traffico HTTP/HTTPS |
| Defense Evasion | Subvert Trust Controls: Install Root Certificate | `T1553.004` | Installazione del certificato CA di Burp nel trust store del browser per abilitare l'intercettazione HTTPS senza errori |
| Collection | Man-in-the-Middle: AiTM HTTPS Interception | `T1557.002` | Generazione di certificati SSL falsi per ogni dominio visitato, permettendo la lettura del traffico cifrato |
| Reconnaissance | Active Scanning: Vulnerability Scanning | `T1595.002` | Scansione DAST con OWASP ZAP che genera traffico verso il target per identificare vulnerabilita (WEB-001) |
| Initial Access | Exploit Public-Facing Application | `T1190` | Identificazione di form privi di token CSRF (WEB-001) come vettore di attacco per Cross-Site Request Forgery |

---

> **Nota:** La configurazione del proxy e dell'intercettazione HTTPS e stata eseguita in un ambiente
> di laboratorio locale. In ambienti di produzione, l'installazione di certificati CA non autorizzati
> costituisce una violazione delle policy aziendali e potenzialmente un reato. Tutte le attivita
> sono state condotte su target autorizzati (`testphp.vulnweb.com` - ambiente di test pubblico).
