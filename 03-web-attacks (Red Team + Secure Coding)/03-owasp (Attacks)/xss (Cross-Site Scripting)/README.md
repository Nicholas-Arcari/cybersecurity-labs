# Cross-Site Scripting (XSS)

Il Cross-Site Scripting (XSS) è una vulnerabilità che permette a un attaccante di iniettare script malevoli all'interno di pagine web visualizzate da altri utenti.

Questa repository contiene esempi pratici delle due principali tipologie di XSS:

## 1 [Reflected XSS](./reflected/)

Lo script viene iniettato nella richiesta (es. parametro URL) e riflesso immediatamente dal server. Richiede che la vittima clicchi su un link malevolo.

- Impatto: Phishing, Session Hijacking (Richiede interazione dell'utente).

## 2 [Stored XSS](./stored/)

Lo script viene salvato permanentemente sul server target (es. in un database). La vittima esegue lo script semplicemente visualizzando la pagina infetta.

- Impatto: Critico (Nessuna interazione utente richiesta, colpisce molteplici utenti/amministratori).

## 3 [XSS Hunter Payloads](./xss-hunter-payloads/) (Blind XSS)

Risorse per attacchi "Blind XSS". In questo scenario, l'attaccante inietta il payload alla cieca (es. in un form di "Contattaci" o nei Log del server) e non vede il risultato immediato.

Il payload è progettato per "chiamare casa" (inviare una notifica all'attaccante) solo quando un Amministratore visualizza quel dato nel pannello di gestione protetto.

- Impatto: Critico (Spesso compromette account Amministratore/Backend).