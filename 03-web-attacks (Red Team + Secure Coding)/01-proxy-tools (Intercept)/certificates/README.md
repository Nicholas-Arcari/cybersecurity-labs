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