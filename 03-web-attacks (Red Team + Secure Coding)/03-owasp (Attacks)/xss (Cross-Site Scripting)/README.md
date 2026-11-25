> [English](README.en.md) | **Italiano**

# Cross-Site scripting (XSS)

> - **Fase:** Web Attack - Cross-Site Scripting (XSS)
> - **Visibilita:** Variabile - Bassa (Reflected e Stored: richieste standard) / Zero (Blind: payload dormiente)
> - **Prerequisiti:** Punto di input che riflette o persiste l'input utente senza encoding, proxy configurato per intercettare
> - **Output:** Esecuzione di JavaScript arbitrario nel browser della vittima, furto cookie, defacement, finding WEB-005..007

---

Il Cross-Site Scripting (XSS) è una vulnerabilità che permette a un attaccante di iniettare script malevoli all'interno di pagine web visualizzate da altri utenti.

Questa repository contiene esempi pratici delle due principali tipologie di XSS:

## 1 [Reflected XSS](./reflected/)

Lo script viene iniettato nella richiesta (es. parametro URL) e riflesso immediatamente dal server. Richiede che la vittima clicchi su un link malevolo.

- Impatto: Phishing, Session Hijacking (Richiede interazione dell'utente).

## 2 [Stored XSS](./stored/)

Lo script viene salvato permanentemente sul server target (es. in un database). La vittima esegue lo script semplicemente visualizzando la pagina infetta.

- Impatto: Critico (Nessuna interazione utente richiesta, colpisce molteplici utenti/amministratori).

## 3 [XSS hunter payloads](./xss-hunter-payloads/) (blind XSS)

Risorse per attacchi "Blind XSS". In questo scenario, l'attaccante inietta il payload alla cieca (es. in un form di "Contattaci" o nei Log del server) e non vede il risultato immediato.

Il payload è progettato per "chiamare casa" (inviare una notifica all'attaccante) solo quando un Amministratore visualizza quel dato nel pannello di gestione protetto.

- Impatto: Critico (Spesso compromette account Amministratore/Backend).

---

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| initial access | exploit public-facing application | `T1190` | sfruttamento di input non sanitizzati per iniettare codice javascript nell'applicazione (WEB-005, WEB-006, WEB-007) |
| credential access | steal web session cookie | `T1539` | furto del cookie di sessione tramite `document.cookie` iniettato via xss (WEB-005, WEB-006) |
| initial access | phishing: spearphishing link | `T1566.002` | distribuzione di url malevoli con payload xss reflected per colpire utenti specifici (WEB-005) |
| persistence | server software component: web shell | `T1505.003` | xss stored persistente nel database che esegue codice su ogni visualizzazione della pagina (WEB-006) |
| collection | browser session hijacking | `T1185` | redirect della vittima verso server attaccante tramite xss stored per catturare il cookie in modo silente (WEB-007) |
| reconnaissance | gather victim identity information | `T1589` | xss blind/oob tramite tag img per ottenere ip e user-agent dell'amministratore che visualizza il profilo (WEB-007) |

---

> **Nota:** Le tre varianti di XSS documentate nelle sottocartelle (`reflected/`, `stored/`,
> `xss-hunter-payloads/`) sono state praticate su `testphp.vulnweb.com` (ambiente Acunetix).
> I finding WEB-005, WEB-006, WEB-007 documentano vulnerabilita reali dello stesso target,
> progressivamente piu critiche in termini di impatto e difficolta di rilevamento.
