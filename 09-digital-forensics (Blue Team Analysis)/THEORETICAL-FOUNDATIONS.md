> [English](THEORETICAL-FOUNDATIONS.en.md) | **Italiano**

# Fondamenti teorici - modulo 09: digital forensics

> - **Livello:** Analisi accademica (complemento teorico ai README operativi del modulo)
> - **Scopo:** Fondare la forense sull'ordine di volatilita, sull'integrita crittografica delle prove, sul principio di scambio e sull'inferenza inversa dallo stato presente al passato.
> - **Prerequisiti:** README operativi del modulo 09 (finding FOR-); nozioni di crittografia (funzioni hash), teoria dell'inferenza e diritto della prova.

---

## Abstract

La forense digitale e la ricostruzione inferenziale di un evento passato dalle sue tracce materiali. Il documento la fonda su quattro pilastri. Il **principio di scambio** (Locard) garantisce che ogni azione lasci traccia, rendendo la ricostruzione possibile in linea di principio. L'**ordine di volatilita** [Brezinski & Killalea 2002; Farmer & Venema 2005] governa la sequenza di acquisizione secondo la fisica della persistenza dell'informazione, con la remanenza della memoria [Halderman et al. 2008] a definirne i limiti. L'**integrita crittografica** (hashing) fornisce la garanzia matematica di non-alterazione, fondamento dell'ammissibilita. Infine, la forense e un problema di **inferenza inversa**: ricostruire lo stato passato dallo stato presente, con i limiti epistemici che ne conseguono. Il conflitto con l'anti-forensics (modulo 07) si risolve sul terreno dell'immutabilita.

---

## 1. Modello dell'Analista e dell'Anti-Analista

Il modulo 09 ha due agenti in opposizione. L'**analista forense** `F` mira a ricostruire la sequenza di eventi `sigma = (e_1, ..., e_n)` che ha portato il sistema dallo stato iniziale allo stato osservato, a partire dalle sole tracce presenti. L'**anti-analista** (l'attaccante del modulo 07 in modalita anti-forensics) mira a impedire, degradare o falsificare tale ricostruzione. La tensione tra i due si gioca sull'integrita e sulla persistenza delle tracce: `F` vince se le tracce sono complete, integre e correttamente interpretate; l'anti-analista vince se puo cancellarle o alterarle prima che siano preservate. La sezione 3.4 mostra che l'immutabilita sposta strutturalmente l'equilibrio a favore di `F`.

---

## 2. Proprieta di sicurezza e prova in gioco

- **Integrita della prova:** la prova deve essere dimostrabilmente non alterata dall'acquisizione all'analisi. E la proprieta [Biba 1977] che l'hashing crittografico garantisce (sezione 3.3).
- **Autenticita e catena di custodia:** deve essere tracciabile chi ha maneggiato la prova, quando e come; una custodia non documentata la rende inammissibile.
- **Completezza dell'acquisizione:** le tracce volatili devono essere catturate prima che decadano (sezione 3.2).
- **Riproducibilita:** l'analisi deve essere ripetibile e verificabile da terzi, requisito di validita scientifica (sezione 6).

---

## 3. Fondamenti teorici

### 3.1 Il principio di scambio come assioma di ricostruibilita

Il principio di scambio di Locard, assioma fondativo della criminalistica, afferma che ogni contatto lascia una traccia. Trasposto al digitale: ogni azione su un sistema informatico altera lo stato (file creati, timestamp modificati, voci di log, blocchi allocati/deallocati, pagine in RAM). Questo assioma e cio che rende la forense possibile in linea di principio: non esiste attivita senza traccia, quindi la ricostruzione ha sempre, teoricamente, del materiale su cui operare. L'anti-forensics non nega l'assioma (non puo non lasciare tracce) ma cerca di renderle irrecuperabili o non interpretabili - un obiettivo piu debole e, come mostra la sezione 3.4, spesso irraggiungibile contro un'infrastruttura di preservazione adeguata.

### 3.2 L'ordine di volatilita e la fisica della persistenza

[Brezinski & Killalea 2002] (RFC 3227) e [Farmer & Venema 2005] codificano l'**ordine di volatilita**: le tracce hanno tempi di persistenza diversi, dai registri della CPU e la cache (nanosecondi), alla RAM (fino allo spegnimento), alle connessioni di rete e ai processi, fino al disco (persistente). La regola di acquisizione - catturare prima cio che e piu volatile - deriva dalla fisica dell'informazione, non da convenzione. La conseguenza controintuitiva e che l'azione istintiva di spegnere un sistema compromesso e l'errore che distrugge la classe piu preziosa di prove (lo stato vivo). [Halderman et al. 2008] ne definiscono un limite fisico sorprendente con gli attacchi cold boot: la RAM conserva il proprio contenuto per secondi o minuti dopo lo spegnimento (remanenza), e il raffreddamento estende questa finestra - dimostrando che il confine tra volatile e persistente e esso stesso fisico e manipolabile.

### 3.3 Integrita crittografica come garanzia matematica

L'ammissibilita di una prova digitale poggia sulla dimostrabilita della sua non-alterazione. La funzione hash crittografica fornisce questa garanzia matematicamente: se `H(immagine_acquisita) = H(originale)` e `H` e resistente alle collisioni, allora l'immagine e (salvo probabilita trascurabile) identica all'originale. La resistenza alle collisioni di seconda preimmagine e la proprieta rilevante: dato l'originale, e computazionalmente proibitivo produrre un dato diverso con lo stesso hash. E la ragione dell'uso di SHA-256 (spazio 2^256, bound di collisione ~2^128 per il paradosso del compleanno) al posto di funzioni rotte. La catena di custodia e il complemento procedurale: l'hashing garantisce che il dato non e cambiato, la catena documenta chi lo ha maneggiato. Insieme realizzano l'integrita [Biba 1977] in forma verificabile.

### 3.4 Anti-forensics e il teorema pratico dell'immutabilita

Il conflitto tra `F` e l'anti-analista si risolve sul terreno dell'immutabilita, con un argomento gia introdotto nel modulo 07 (sezione 3.4) e qui completato dal lato forense. Separando la **generazione** della traccia (sull'host, sotto potenziale controllo dell'attaccante) dalla sua **conservazione** (su un sistema append-only/WORM esterno), la traccia diventa immutabile nel momento della generazione. L'attaccante, anche con privilegi massimi sull'host di origine, non puo alterare cio che e gia stato inoltrato e sigillato altrove. Questo trasforma l'anti-forensics locale in un'azione non solo inefficace ma controproducente: la cancellazione stessa e un evento generato e inoltrato, un forte indicatore. In termini teorici, l'immutabilita rende la funzione "stato osservato, eventi" (sezione 3.5) robusta alla manomissione a posteriori, chiudendo lo spazio di manovra dell'anti-analista.

### 3.5 La forense come inferenza inversa (abduzione)

Ricostruire `sigma` dallo stato osservato e un problema di **inferenza inversa**: data la funzione (in generale non iniettiva) che mappa sequenze di eventi in stati finali, trovare la sequenza che ha prodotto lo stato osservato. Poiche piu sequenze possono produrre lo stesso stato, l'inferenza non e deduttiva ma **abduttiva** (inferenza alla spiegazione migliore): l'analista propone la sequenza piu plausibile compatibile con tutte le tracce, corroborata dalla convergenza di evidenze indipendenti (timeline su disco, artefatti in memoria, traffico di rete). La forza della conclusione forense cresce con il numero di tracce indipendenti che convergono sulla stessa ricostruzione. Questo inquadra epistemologicamente la forense: non produce certezza deduttiva ma la migliore spiegazione corroborata, ed e per questo che la molteplicita e l'indipendenza delle fonti (disco + memoria + rete) sono metodologicamente cruciali.

---

## 4. Analisi quantitativa

### 4.1 Robustezza dell'integrita e paradosso del compleanno

La garanzia di integrita dell'hashing e quantificata dalla resistenza alle collisioni. Per una funzione con output di `n` bit, una collisione casuale richiede in media ~`2^(n/2)` tentativi (paradosso del compleanno). SHA-256 (`n = 256`) offre quindi un bound di ~`2^128`, computazionalmente proibitivo, mentre MD5 e SHA-1 sono rotti (collisioni pratiche note) e inadatti all'uso forense probatorio. La scelta della funzione hash non e dettaglio implementativo ma determina la solidita giuridica della prova.

### 4.2 Il valore informativo della convergenza

Se `k` tracce indipendenti supportano ciascuna la stessa ipotesi di ricostruzione con probabilita di falsa corrispondenza `p_i`, la probabilita che tutte convergano per caso su una ricostruzione errata e ~`prod_i p_i`, decrescente esponenzialmente in `k`. Questo formalizza il valore della triangolazione forense (disco + memoria + rete): ogni fonte indipendente aggiuntiva riduce moltiplicativamente la probabilita di una ricostruzione erronea, rafforzando la conclusione abduttiva della sezione 3.5. E il duale, sul lato difensivo/investigativo, della correlazione multi-sorgente del modulo 08 (sezione 4.1).

---

## 5. Rassegna della letteratura

L'ordine di volatilita e le best practice di acquisizione sono codificati da [Brezinski & Killalea 2002] (RFC 3227) e [Farmer & Venema 2005]. I limiti fisici della volatilita della memoria sono dimostrati da [Halderman et al. 2008]. La proprieta di integrita richiamata e di [Biba 1977]. Le sfide programmatiche e la maturazione della disciplina sono discusse da [Garfinkel 2010]. La cornice analitica per l'interpretazione dell'intrusione ricostruita e il Diamond Model [Caltagirone et al. 2013]. Il principio di scambio di Locard (criminalistica classica) e lo standard di ammissibilita scientifica (nel diritto statunitense, il criterio Daubert) sono riferimenti fondativi trasversali richiamati come principi consolidati.

---

## 6. Limiti e problemi aperti

1. **Non iniettivita della ricostruzione.** Poiche piu sequenze di eventi producono lo stesso stato osservato (sezione 3.5), la ricostruzione forense e intrinsecamente abduttiva e non deduttiva: esiste sempre incertezza residua, riducibile ma non azzerabile dalla convergenza delle fonti. E un limite epistemico, non tecnologico.

2. **Anti-forensics contro sistemi immaturi.** L'argomento dell'immutabilita (sezione 3.4) vale solo se esiste un'infrastruttura di preservazione esterna. Su sistemi senza logging centralizzato, l'anti-forensics resta efficace: la difesa e organizzativa, non intrinseca.

3. **Scalabilita e validita scientifica.** [Garfinkel 2010] evidenzia la tensione tra il volume crescente dei dati e il requisito di riproducibilita e validita scientifica (criterio di ammissibilita): l'automazione dell'analisi forense su larga scala senza compromettere la difendibilita del metodo e un problema aperto.

---

## 7. Sintesi e collegamento alla pratica

I finding `FOR-` del modulo istanziano questo quadro: la disk & memory forensics (FOR-001) applica l'ordine di volatilita della sezione 3.2, l'integrita crittografica della sezione 3.3 e il recupero degli artefatti cancellati come esempio del principio di scambio della sezione 3.1; la network forensics (FOR-002) e la fonte indipendente immune alla manomissione a posteriori (sezione 3.4) che rafforza la convergenza della sezione 4.2. La catena di custodia e la verifica dell'hash documentate nei README sono le realizzazioni operative delle sezioni 3.3 e 2. Il documento fornisce alla pratica forense la giustificazione teorica del perche l'ordine di volatilita, l'integrita e la molteplicita delle fonti non siano formalita ma condizioni di validita del risultato, e chiude il conflitto con il modulo 07: cio che l'anti-forensics tenta di distruggere, l'immutabilita della preservazione conserva, spostando l'equilibrio a favore dell'analista.

---

## Riferimenti

Sottoinsieme della bibliografia master (`../REFERENCES.md`) rilevante per questo modulo:

- [Brezinski & Killalea 2002] - RFC 3227, ordine di volatilita.
- [Farmer & Venema 2005] - forense post-mortem e volatilita.
- [Halderman et al. 2008] - cold boot e remanenza della memoria.
- [Biba 1977] - integrita.
- [Garfinkel 2010] - sfide della forense digitale.
- [Caltagirone et al. 2013] - Diamond Model.

Riferimenti fondativi esterni alla bibliografia di sicurezza: principio di scambio di Locard (criminalistica); criterio Daubert (ammissibilita della prova scientifica, diritto USA).

---

> **Nota:** Documento a scopo educativo, complementare ai README operativi. Le citazioni rimandano a fonti reali elencate in `../REFERENCES.md`.
