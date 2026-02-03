# OSINT Passive: Email Harvesting (Personal Audit)

Obiettivo: Verifica dell'esposizione di indirizzi email sul dominio personale e analisi della superficie di attacco del portfolio digitale.

Target: `nicholas-arcari.github.io`
Strumenti: `theHarvester`, `Google Dorks`

---

## 1 Introduzione Teorica

L'Email Harvesting è una tecnica di ricognizione (Reconnaissance) solitamente utilizzata per mappare la struttura organigrammatica di un'organizzazione target.

Tuttavia, in un contesto di Personal Security Audit, questa tecnica viene adattata per verificare se un sito web personale espone involontariamente dati di contatto (PII) che potrebbero essere indicizzati dai motori di ricerca e successivamente bersagliati da bot di spam o campagne di Spear Phishing.

---

## 2 Esecuzione Tecnica

#### A. Scansione Automatizzata (TheHarvester)

È stato interrogato il dominio del portfolio utilizzando `theHarvester` per aggregare risultati da fonti pubbliche (OSINT) e verificare l'indicizzazione di email associate al sottodominio.

Comando:

```Bash
theHarvester -d nicholas-arcari.github.io -b all
```

Nota Tecnica: Poiché GitHub Pages è un servizio di hosting statico e non fornisce un server di posta elettronica diretto, è atteso un risultato nullo per le email strettamente legate al dominio (es. `info@nicholas-arcari.github.io`), a meno di configurazioni personalizzate errate.

#### B. Analisi dei Risultati (TheHarvester)

Fonti utilizzate: Baidu, Bing, DuckDuckGo, Yahoo, CRTsh.

|Categoria | Risultato |Analisi Tecnica|
|---------|-------------|-----------------|
|Email Esposte | 0 email found | Positiva. Non vi è esposizione diretta di contatti email indicizzati sui motori di ricerca per questo dominio specifico|
|Infrastruttura | 4 IP (es. 185.199...) | Gli indirizzi IP appartengono all'infrastruttura di GitHub Pages (Hosting Provider). Non rappresentano un server privato gestito dall'utente|
|Sottodomini | 19 Hosts (es. shop., ftp.) | Falsi Positivi. Si tratta di un artefatto dovuto ai record DNS Wildcard generati dall'infrastruttura cloud di GitHub. Una verifica manuale conferma che questi servizi non sono attivi|

#### C. Ricerca Mirata (Google Dorking)

Poiché il dominio è ospitato su GitHub, esiste il rischio che le email di contatto personali (es. Gmail) siano state lasciate "in chiaro" nel codice sorgente o nei file di documentazione (README).

Query Eseguita:

```Bash
site:nicholas-arcari.github.io "gmail.com"
```

Obiettivo: Identificare se l'indirizzo email personale è visibile in chiaro nelle pagine del portfolio.

L'analisi ha evidenziato/non ha evidenziato la presenza dell'indirizzo personale.

---

## 3 Conclusione e Remediation

Dall'analisi emerge che il dominio personale presenta una superficie di attacco minima per quanto riguarda l'harvesting automatico.

Raccomandazioni:

- Obfuscation (Offuscamento): Se è necessario pubblicare un contatto email, evitare il formato testo standard (`testo@dominio`). Utilizzare immagini o formati non machine-readable (es. `nome [at] gmail [dot] com`) per prevenire lo scraping da parte dei bot.
- Moduli di Contatto: Preferire l'integrazione di moduli backend-less (es. Formspree) che permettono il contatto senza esporre l'indirizzo di destinazione nel codice frontend.