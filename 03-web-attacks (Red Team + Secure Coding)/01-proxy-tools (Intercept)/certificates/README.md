> [English](README.en.md) | **Italiano**

# Proxy Tools: SSL/TLS Certificates & HTTPS Interception

> - **Fase:** Web Attack - HTTPS Interception Setup
> - **Visibilita:** Locale - la configurazione avviene esclusivamente sul browser locale, nessun traffico aggiuntivo verso il target
> - **Prerequisiti:** Burp Suite avviato con listener su `127.0.0.1:8080`, browser configurato per usare il proxy
> - **Output:** Intercettazione trasparente del traffico HTTPS, certificati SSL falsi firmati dalla CA Burp accettati dal browser senza errori

---

Obiettivo: Configurare la "Chain of Trust" tra il browser e Burp Suite per consentire l'intercettazione e la decifrazione del traffico HTTPS (SSL/TLS).

Target: Configurazione Locale (Browser + Burp CA)

Strumenti: `Burp Suite`, `Firefox Certificate Manager`

---

## 1 Introduzione Teorica: La rottura della crittografia

Il protocollo HTTPS protegge la riservatezza dei dati cifrandoli tra il client e il server. Un Proxy "Man-in-the-Middle" (come Burp) interrompe questa connessione.

Per poter leggere i dati cifrati, il Proxy deve:

1.  Presentarsi al browser come se fosse il sito target (es. `google.com`).

2.  Generare un certificato SSL falso "al volo" per quel dominio.

Affinché il browser accetti questo certificato falso senza mostrare errori di sicurezza (`SEC_ERROR_UNKNOWN_ISSUER`), è necessario installare la Certificate Authority (CA) di Burp nello store dei certificati affidabili del browser (Trusted Root Store).

---

## 2 Procedura Tecnica: Installazione CA

È stata eseguita l'installazione del certificato radice di PortSwigger per abilitare la Deep Packet Inspection.

Passaggi eseguiti:

1.  Download del certificato `cacert.der` da `http://burp`.

2.  Importazione nel Trust Store di Firefox (`Authorities` tab).

3.  Abilitazione del flag: "Trust this CA to identify websites".

Verifica dell'Intercettazione HTTPS:

Dopo la configurazione, è stato visitato un sito protetto (`google.com`). Il browser non ha mostrato warning.

Ispezionando il certificato del sito, l'emittente risulta essere PortSwigger CA, confermando che il traffico sta venendo decifrato e ri-cifrato da Burp.

---

## 3 Scenari Avanzati: SSL Pinning

Mentre questa tecnica funziona sui browser desktop, le applicazioni mobili moderne (Android/iOS) implementano l'SSL Pinning.

L'app non si fida ciecamente del Trust Store del dispositivo, ma accetta solo un certificato specifico hardcodato dagli sviluppatori. In uno scenario di Mobile Pentesting, sarebbe necessario utilizzare framework come Frida o Objection per iniettare codice a runtime e disabilitare questo controllo.

---

## 4 Conclusioni

La corretta gestione dei certificati è il prerequisito per analizzare il traffico moderno. Senza questa configurazione, l'attività di Red Teaming sarebbe limitata al solo traffico HTTP (in chiaro), rendendo impossibile testare form di login, transazioni bancarie o API protette.

---

## Analisi a Basso Livello: Chain of Trust e TLS Interception

### Come il Browser Valida i Certificati

Il browser esegue una catena di verifiche per ogni connessione HTTPS:

```
Browser riceve certificato dal server (o dal proxy)
    |
    v
1. Verifica firma: il certificato e firmato da una CA nel trust store?
   - Se SI: prosegue
   - Se NO: errore SEC_ERROR_UNKNOWN_ISSUER
    |
    v
2. Verifica validita temporale: Not Before <= now <= Not After?
   - Se scaduto: errore SSL_ERROR_EXPIRED_CERT_ALERT
    |
    v
3. Verifica hostname: CN o SAN contiene il dominio richiesto?
   - Se non corrisponde: errore SSL_ERROR_BAD_CERT_DOMAIN
    |
    v
4. Verifica revoca: OCSP/CRL indica che il certificato e revocato?
   - Se revocato: errore SEC_ERROR_REVOKED_CERTIFICATE
    |
    v
5. Verifica HSTS: il dominio ha HSTS preloaded?
   - Se SI e il cert non e valido: nessun override possibile
    |
    v
Connessione HTTPS stabilita (lucchetto verde)
```

### Perche il Certificato Burp Viene Accettato

Dopo l'installazione della CA Burp nel trust store di Firefox:

```
Senza CA Burp:
Browser -> tesla.com -> Cert: CN=tesla.com, Issuer=PortSwigger CA
                        PortSwigger CA NON nel trust store -> ERRORE

Con CA Burp installata:
Browser -> tesla.com -> Cert: CN=tesla.com, Issuer=PortSwigger CA
                        PortSwigger CA nel trust store -> OK (fidata)
```

Burp genera un certificato nuovo "al volo" per ogni dominio visitato, firmandolo con la sua CA privata. Il browser si fida perche abbiamo aggiunto quella CA come "trusted root".

### SSL Pinning: La Contromisura

Le applicazioni mobili implementano il certificate pinning per prevenire esattamente questo tipo di intercettazione:

| Tipo di pinning | Meccanismo | Bypass |
| :--- | :--- | :--- |
| **Certificate pinning** | L'app contiene il certificato esatto del server | Frida: hook `X509TrustManager.checkServerTrusted()` |
| **Public key pinning** | L'app contiene solo la chiave pubblica | Objection: `android sslpinning disable` |
| **HPKP (deprecato)** | Header HTTP con hash della chiave pubblica | Rimosso dai browser per rischio di DoS |
| **Network Security Config** (Android) | XML config che definisce trust anchors | Modifica del file XML + repack APK |

---

## Blue Team: Protezione contro Intercettazione TLS

- **Certificate Transparency monitoring:** monitorare i CT logs per certificati emessi per il proprio dominio da CA non autorizzate
- **HSTS preload:** inserire il dominio nella preload list dei browser impedisce l'override dei certificati non validi anche per utenti che cliccano "Accetto il rischio"
- **Corporate proxy awareness:** in ambienti aziendali, documentare quale CA viene usata per l'ispezione TLS e comunicarlo ai dipendenti (trasparenza)
- **Rimuovere la CA al termine del test:** la CA Burp installata nel trust store rende la macchina vulnerabile se un attaccante ottiene la chiave privata corrispondente

---

## Esperienza di Laboratorio

L'errore `SEC_ERROR_UNKNOWN_ISSUER` prima dell'installazione della CA e stato istruttivo: il browser ha funzionato esattamente come previsto, rifiutando un certificato firmato da una CA sconosciuta. Questo ha reso tangibile il concetto di "chain of trust" che nei corsi teorici rimane astratto.

La verifica post-installazione (ispezionare il certificato di google.com e vedere "Issuer: PortSwigger CA" invece di "Google Trust Services") ha dimostrato visivamente il MitM in azione: il browser mostrava il lucchetto verde nonostante il traffico fosse decifrato e leggibile in Burp. Questo e esattamente quello che accade quando un corporate proxy ispeziona il traffico HTTPS dei dipendenti.

La menzione dell'SSL Pinning e stata necessaria per contestualizzare i limiti della tecnica: sulle app mobili moderne, l'installazione della CA nel trust store del dispositivo non e sufficiente. Il bypass richiede runtime instrumentation (Frida/Objection) che opera a un livello completamente diverso, hooking le funzioni di validazione del certificato direttamente nel codice dell'app.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Defense Evasion | Subvert Trust Controls: Install Root Certificate | `T1553.004` | Installazione del certificato CA di PortSwigger (Burp Suite) nel trust store di Firefox per abilitare l'intercettazione HTTPS senza errori di certificato |
| Collection | Man-in-the-Middle: AiTM HTTPS Interception | `T1557.002` | Generazione di certificati SSL falsi per ogni dominio visitato (es. `google.com`), con emittente `PortSwigger CA`, permettendo la decifrazione del traffico TLS in transito |

---

> **Nota:** La procedura di installazione del certificato CA documentata e valida esclusivamente
> per ambienti di laboratorio e macchine di test dedicate. Installare certificati CA di terze parti
> su macchine aziendali o di produzione senza autorizzazione e una violazione delle policy di
> sicurezza aziendale e, in alcuni contesti, un reato. La CA Burp deve essere rimossa al termine
> dell'engagement.