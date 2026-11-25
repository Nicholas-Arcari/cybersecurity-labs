> [English](THEORETICAL-FOUNDATIONS.en.md) | **Italiano**

# Fondamenti teorici - modulo 03: web attacks

> - **Livello:** Analisi accademica (complemento teorico ai README operativi del modulo)
> - **Scopo:** Formalizzare l'injection come confusione linguistica tra dati e codice, il modello del web attacker e il CSRF/SSRF come istanze del confused deputy.
> - **Prerequisiti:** README operativi del modulo 03 (finding WEB-); nozioni di base di linguaggi formali (grammatiche, alberi di parsing) e controllo degli accessi.

---

## Abstract

Le vulnerabilita web sono spesso catalogate empiricamente (SQLi, XSS, CSRF, SSRF). Questo documento le riconduce a due radici teoriche unificanti. La prima e la **confusione tra dati e codice**: l'injection e formalizzabile, secondo [Su & Wassermann 2006], come il fenomeno per cui un input dell'attaccante attraversa il confine tra la posizione di dato e la posizione di codice nell'albero di parsing di un linguaggio. La seconda e il **confused deputy** [Hardy 1988]: CSRF e SSRF sono istanze del problema per cui un componente privilegiato agisce per conto di un principale non autorizzato. Si adotta il modello del web attacker [Akhawe et al. 2010] come cornice formale e se ne derivano le contromisure come applicazioni del principio di complete mediation [Saltzer & Schroeder 1975].

---

## 1. Modello dell'Avversario

Si adotta il modello del **web attacker** formalizzato da [Akhawe et al. 2010], piu debole dell'attaccante di rete di Dolev-Yao ma piu realistico per il dominio web. Il web attacker:

- controlla uno o piu siti web (puo servire contenuto arbitrario ai visitatori);
- puo inviare richieste HTTP arbitrarie verso qualsiasi endpoint;
- puo indurre una vittima a visitare una URL sotto il suo controllo;
- **non** controlla il canale di rete (a differenza di Dolev-Yao): non puo intercettare o modificare il traffico tra la vittima e un terzo sito onesto.

Questa restrizione e cio che rende il web attacker interessante: molte vulnerabilita web (CSRF, XSS) sono sfruttabili anche senza il controllo del canale, sfruttando invece la fiducia mal riposta del browser o del server. Le proprieta di sicurezza web (Same-Origin Policy, integrita delle sessioni) sono definite [Akhawe et al. 2010] rispetto a questo avversario.

---

## 2. Proprieta di sicurezza in gioco

- **Separazione dati/codice:** l'input non fidato non deve mai essere interpretato come istruzione. E la proprieta violata da tutte le famiglie di injection (SQLi, command injection, XSS come code injection nel DOM).
- **Autorizzazione basata sull'intenzione:** un'azione privilegiata deve essere eseguita solo se realmente intesa dal principale autorizzato, non solo se la richiesta e sintatticamente valida. E la proprieta violata dal confused deputy (CSRF, SSRF).
- **Isolamento delle origini (Same-Origin Policy):** contenuto di un'origine non deve accedere a risorse di un'altra origine senza autorizzazione esplicita. E il meccanismo di access control del browser rispetto al web attacker.

---

## 3. Fondamenti teorici

### 3.1 Injection come confusione dato/codice (formalizzazione linguistica)

[Su & Wassermann 2006] forniscono la caratterizzazione formale della command injection. L'idea centrale: un'applicazione costruisce una stringa (query SQL, comando shell, markup) che sara interpretata da un parser secondo una grammatica `G`. L'input dell'attaccante e destinato a occupare una **posizione di dato** (un letterale, un valore) nell'albero di parsing. Si ha injection quando l'input, invece, altera la **struttura sintattica** dell'albero, occupando o creando posizioni di **codice** (operatori, keyword, delimitatori).

Formalmente, sia `q = f(u)` la stringa prodotta dall'applicazione componendo input fidato e input utente `u`. Definiamo l'insieme dei nodi sintattici "attesi" per `u` come i soli nodi foglia di tipo valore. Si ha injection se e solo se esiste un `u` tale che l'albero di parsing di `q` secondo `G` contiene, in corrispondenza di `u`, nodi che non sono foglie-valore, ossia `u` contribuisce alla struttura non terminale dell'albero. Questa e la definizione di [Su & Wassermann 2006], che ne derivano anche un algoritmo di rilevamento basato sul confronto tra l'albero di parsing atteso e quello effettivo.

La conseguenza teorica e forte: le contromisure che agiscono sulla stringa (escaping, blacklist) inseguono manifestazioni sintattiche e sono fragili, mentre le **query parametrizzate (prepared statements)** risolvono il problema alla radice perche vincolano strutturalmente `u` a occupare una posizione di valore, rendendo impossibile per costruzione l'alterazione dell'albero. La correttezza dei prepared statements non e euristica ma strutturale: separano il canale della struttura (la query template, fidata) dal canale dei dati (i parametri, non fidati).

### 3.2 CSRF e SSRF come confused deputy

[Hardy 1988] descrive il **confused deputy** come un programma dotato di autorita che viene indotto da un terzo a usare tale autorita per conto del terzo, non del legittimo detentore. CSRF e SSRF ne sono due istanze:

- **CSRF:** il browser della vittima e il deputy confuso. Detiene l'autorita (i cookie di sessione) e la usa per inviare una richiesta indotta dal sito dell'attaccante. Il server non distingue una richiesta *intesa* dalla vittima da una *indotta* dall'attaccante: entrambe portano credenziali valide. La difesa (anti-CSRF token, verifica dell'origine/SameSite) [Barth et al. 2008] ripristina la distinzione, richiedendo una prova di intenzione che l'attaccante non puo fornire.

- **SSRF:** il server e il deputy confuso. Detiene l'autorita di rete (raggiungibilita di endpoint interni, es. il metadata service cloud) e la usa per conto dell'attaccante che ne controlla una URL di destinazione. E lo stesso schema, spostato dal browser al server, e collega direttamente il modulo 03 al furto di credenziali cloud del modulo 10 (metadata SSRF).

L'unificazione teorica e che entrambi violano l'**autorizzazione basata sull'intenzione** (sezione 2): la richiesta e valida ma non intesa. Il confused deputy mostra che l'autenticazione (chi presenta l'autorita) e insufficiente senza la verifica dell'intenzione (chi ha voluto l'azione).

### 3.3 Complete mediation e Same-Origin policy

La Same-Origin Policy e un'istanza del principio di **complete mediation** di [Saltzer & Schroeder 1975]: ogni accesso a una risorsa deve essere verificato. Il browser media ogni accesso cross-origin secondo l'origine (schema, host, porta) del contesto richiedente. Le vulnerabilita di configurazione CORS sono, in questa cornice, allentamenti della mediazione completa che riaprono il canale che la SOP chiudeva.

---

## 4. Analisi quantitativa

### 4.1 Taint propagation e information flow

Il rilevamento dell'injection puo essere modellato come un problema di **information flow**: si etichetta (taint) ogni input non fidato e si traccia la sua propagazione fino ai sink sensibili (esecuzione query, eval, output HTML). Un flusso taint, sink senza sanitizzazione interposta e un candidato injection. La completezza di questa analisi soffre degli stessi limiti di decidibilita del modulo 02 (sezione 3.1 di quel documento): il tracciamento esatto del flusso in presenza di alias, riflessione e costrutti dinamici e indecidibile nel caso generale, per cui gli analizzatori statici sono anch'essi unsound o incomplete.

### 4.2 Il costo asimmetrico difesa/attacco nell'escaping

L'approccio basato su escaping/blacklist e quantitativamente svantaggioso: il difensore deve enumerare e neutralizzare *tutte* le sequenze sintatticamente pericolose (insieme aperto e dipendente dal parser), mentre l'attaccante deve trovarne *una* non coperta. E la stessa asimmetria "difensore ha ragione sempre, attaccante una volta" gia incontrata nel modulo 01. I prepared statements invertono l'asimmetria eliminando la classe intera (sezione 3.1): il difensore risolve una volta, strutturalmente, invece di inseguire infinite manifestazioni.

---

## 5. Rassegna della letteratura

La formalizzazione dell'injection segue [Su & Wassermann 2006], che ne hanno dato una caratterizzazione linguistica precisa e un metodo di rilevamento basato sui parse tree. Il modello di avversario e le proprieta web derivano da [Akhawe et al. 2010], riferimento fondativo dell'analisi formale della sicurezza web. La difesa contro il CSRF e analizzata rigorosamente da [Barth et al. 2008]. L'inquadramento del CSRF/SSRF come confused deputy risale a [Hardy 1988]. Le contromisure come mediazione completa e minimo privilegio si richiamano a [Saltzer & Schroeder 1975]. Il catalogo empirico delle classi (OWASP Top 10) fornisce la tassonomia operativa complementare.

---

## 6. Limiti e problemi aperti

1. **Indecidibilita dell'analisi di flusso.** Come per il modulo 02, il rilevamento esatto dei flussi da taint a sink e indecidibile nel caso generale; gli strumenti (SAST) restano approssimazioni.

2. **Sanitizzazione context-dependent.** La correttezza dell'output encoding dipende dal contesto di destinazione (HTML body, attributo, JavaScript, URL, CSS): una sanitizzazione corretta in un contesto e insufficiente in un altro. La composizione sicura di contesti multipli (es. dato che attraversa HTML e poi JavaScript) resta soggetta a errori e non completamente automatizzabile.

3. **Intenzione non osservabile.** Il confused deputy si fonda sull'impossibilita per il server di osservare direttamente l'intenzione del principale; i token anti-CSRF e SameSite sono approssimazioni della prova di intenzione, non la sua verifica diretta. La modellazione formale completa dell'intenzione dell'utente resta aperta.

---

## 7. Sintesi e collegamento alla pratica

I finding `WEB-` del modulo si mappano su questo quadro: le famiglie di injection (SQLi, command injection, XSS) sono istanze della confusione dato/codice della sezione 3.1, e la remediation raccomandata nei README (prepared statements, output encoding context-aware) e la traduzione operativa della soluzione strutturale; CSRF e SSRF sono confused deputy (sezione 3.2), con le difese (token, SameSite, allowlist di destinazione) come ripristino dell'autorizzazione basata sull'intenzione. Il collegamento al modulo 10 e diretto e teoricamente motivato: l'SSRF che ruba il token del metadata service cloud e lo stesso confused deputy, spostato sul server. Il documento fornisce alla pratica secure-coding del modulo la giustificazione formale del perche le contromisure strutturali (che eliminano la classe) siano superiori a quelle sintattiche (che inseguono le istanze).

---

## Riferimenti

Sottoinsieme della bibliografia master (`../REFERENCES.md`) rilevante per questo modulo:

- [Su & Wassermann 2006] - formalizzazione linguistica dell'injection.
- [Akhawe et al. 2010] - modello del web attacker e fondamenti formali della sicurezza web.
- [Barth et al. 2008] - difese formali contro il CSRF.
- [Hardy 1988] - il confused deputy (base concettuale di CSRF/SSRF).
- [Saltzer & Schroeder 1975] - complete mediation e minimo privilegio.
- [Bishop 2018] - politica e meccanismo.
- OWASP Top 10 / Testing Guide - tassonomia operativa.

---

> **Nota:** Documento a scopo educativo, complementare ai README operativi. Le citazioni rimandano a fonti reali elencate in `../REFERENCES.md`.
