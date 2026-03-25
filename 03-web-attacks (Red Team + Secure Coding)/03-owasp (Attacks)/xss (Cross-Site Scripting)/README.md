# Cross-Site Scripting (XSS)

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

## 3 [XSS Hunter Payloads](./xss-hunter-payloads/) (Blind XSS)

Risorse per attacchi "Blind XSS". In questo scenario, l'attaccante inietta il payload alla cieca (es. in un form di "Contattaci" o nei Log del server) e non vede il risultato immediato.

Il payload è progettato per "chiamare casa" (inviare una notifica all'attaccante) solo quando un Amministratore visualizza quel dato nel pannello di gestione protetto.

- Impatto: Critico (Spesso compromette account Amministratore/Backend).

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Initial Access | Exploit Public-Facing Application | `T1190` | Sfruttamento di input non sanitizzati per iniettare codice JavaScript nell'applicazione (WEB-005, WEB-006, WEB-007) |
| Credential Access | Steal Web Session Cookie | `T1539` | Furto del cookie di sessione tramite `document.cookie` iniettato via XSS (WEB-005, WEB-006) |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | Distribuzione di URL malevoli con payload XSS Reflected per colpire utenti specifici (WEB-005) |
| Persistence | Server Software Component: Web Shell | `T1505.003` | XSS Stored persistente nel database che esegue codice su ogni visualizzazione della pagina (WEB-006) |
| Collection | Browser Session Hijacking | `T1185` | Redirect della vittima verso server attaccante tramite XSS Stored per catturare il cookie in modo silente (WEB-007) |
| Reconnaissance | Gather Victim Identity Information | `T1589` | XSS Blind/OOB tramite tag img per ottenere IP e User-Agent dell'amministratore che visualizza il profilo (WEB-007) |

---

> **Nota:** Le tre varianti di XSS documentate nelle sottocartelle (`reflected/`, `stored/`,
> `xss-hunter-payloads/`) sono state praticate su `testphp.vulnweb.com` (ambiente Acunetix).
> I finding WEB-005, WEB-006, WEB-007 documentano vulnerabilita reali dello stesso target,
> progressivamente piu critiche in termini di impatto e difficolta di rilevamento.