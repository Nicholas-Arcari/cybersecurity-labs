> [English](README.en.md) | **Italiano**

# Valutazione Empirica - Misure Quantitative Riproducibili

> - **Livello:** Valutazione sperimentale (complemento ai `THEORETICAL-FOUNDATIONS.md`)
> - **Scopo:** Colmare l'ultimo divario verso il livello accademico di ricerca: passare da un'analisi quantitativa *derivata dalla letteratura* a misure *ottenute eseguendo esperimenti riproducibili*.
> - **Prerequisiti:** Python 3 (solo standard library). Nessuna dipendenza esterna.

---

## Perche esiste questa cartella

I documenti `THEORETICAL-FOUNDATIONS.md` di ciascun modulo formalizzano i modelli e citano la
letteratura primaria, ma la loro analisi quantitativa e *derivata* (le formule vengono dai paper).
Un lavoro di livello accademico di ricerca richiede in piu la **valutazione empirica**: misure
ottenute da esperimenti propri, e soprattutto la **riproducibilita** che ne permette la verifica
indipendente. Questa cartella fornisce esattamente questo.

Sono onesto sul perimetro. Dei tre elementi che separano questo lavoro da una tesi magistrale di
ricerca (valutazione empirica originale; dimostrazioni formali complete; peer review), questa
cartella affronta il primo e abilita il terzo:

- **Valutazione empirica originale:** esperimenti eseguibili che *misurano* i fenomeni teorici.
- **Verificabilita indipendente:** codice deterministico (seed fissi), a dipendenza zero, con
  output verbatim registrato. Chiunque puo rieseguire e ottenere gli stessi numeri - la
  riproducibilita e la sostanza che la peer review verifica (la peer review in se, che richiede
  revisori esterni qualificati, resta fuori dalla portata di un repository).

**Disciplina di integrita (non negoziabile):** nessun numero e inventato. Ogni valore in questi
documenti proviene dall'esecuzione reale del codice qui incluso. I dataset sono sintetici/modellati
e questo e **dichiarato esplicitamente** in ogni esperimento: si misura il comportamento di
detector/metriche reali su dati etichettati, tecnica standard quando i dati reali di attacco sono
scarsi. Un numero "misurato" fabbricato sarebbe una violazione di integrita ben piu grave di una
citazione errata, ed e evitato per costruzione (il codice e li, si riesegue).

---

## Struttura della cartella

```
EVALUATION/
+-- README.md                          # questo file: metodologia, riproducibilita, sintesi
|
+-- exp01-detection-base-rate/         # Esperimento A (modulo 08)
|   +-- generate_and_evaluate.py       # codice eseguibile (deterministico, stdlib)
|   +-- results.md                     # output verbatim + lettura dei risultati
|
+-- exp02-password-entropy/            # Esperimento B (moduli 04, 06)
    +-- guessing_entropy.py            # codice eseguibile (deterministico, stdlib)
    +-- results.md                     # output verbatim + lettura dei risultati
```

---

## Esperimenti e risultati misurati (headline)

### Esperimento A - Detection engineering e base-rate fallacy (modulo 08)

Un rilevatore di brute-force SSH (regola a soglia) valutato su un dataset etichettato di 1.000.000
di finestre di osservazione. **Risultati misurati:**

- Compromesso precision/recall reale: a recall 0.905 la precision e solo 0.173; nessuna soglia e
  simultaneamente perfetta.
- Al punto operativo ad alta recall, la **Positive Predictive Value crolla col tasso base**:
  `0.70 -> 0.19 -> 0.022 -> 0.0023` per base rate da `1e-2` a `1e-5`. A `1e-5`, il **99.8% degli
  allarmi e falso**.
- La previsione bayesiana di [Axelsson 2000] (`PPV = TPR*p / (TPR*p + FPR*(1-p))`) e **confermata**
  dalla verifica empirica per resampling indipendente (scarti < 0.5 punti percentuali).

Tesi testata: la difficolta del rilevamento e determinata dal tasso base, non dall'accuratezza del
detector (foundations modulo 08, sez. 3.1). Giustifica quantitativamente correlazione (sez. 4.1) e
deception (sez. 3.2). Dettaglio: [exp01-detection-base-rate/results.md](exp01-detection-base-rate/results.md).

### Esperimento B - Entropia di Shannon vs metriche di guessing (moduli 04, 06)

Confronto tra entropia nominale e metriche rilevanti per l'attaccante su una distribuzione di
password Zipf. **Risultati misurati:**

- Shannon `H1 = 13.41 bit` ma min-entropy `Hinf = 3.85 bit`: Shannon **sovrastima** la resistenza al
  singolo tentativo di 9.56 bit.
- Alpha-work-factor misurato: **2 tentativi craccano il 10%**, **749 il 50%**; un attaccante a
  dizionario cracca la maggioranza degli account in ~1.000 tentativi (~2^10) contro 2^13.4 nominali.
- L'esperimento riproduce empiricamente la critica di [Bonneau 2012] alla guessing entropy *media*
  (che qui, dominata dalla coda, supera Shannon): la metrica corretta e il partial guessing.

Tesi testata: la resistenza pratica dipende dalla guessing entropy (testa della distribuzione), non
dall'entropia nominale (foundations modulo 04, sez. 3.3; modulo 06, sez. 3.2/4.2). Dettaglio:
[exp02-password-entropy/results.md](exp02-password-entropy/results.md).

---

## Riproducibilita

Requisiti: solo Python 3 (standard library). Nessuna installazione.

```Bash
# Esperimento A (detection + base-rate) - richiede ~4 secondi
python3 exp01-detection-base-rate/generate_and_evaluate.py

# Esperimento B (entropia password) - richiede < 1 secondo
python3 exp02-password-entropy/guessing_entropy.py
```

Gli script sono **deterministici** (seed fissi): ogni riesecuzione produce esattamente i valori
riportati nei rispettivi `results.md`. Per validare le tesi su **dati reali** invece che modellati,
ogni script isola la generazione del dataset in una singola funzione (`make_dataset()` in A,
`zipf_probs()` in B): sostituendola con un caricatore di dati reali (log etichettati, frequenze di un
corpus di password) la pipeline di misura resta invariata. Questo e il percorso esplicito dal modello
alla misura su campo.

---

## Nota metodologica onesta

Questi esperimenti misurano fenomeni su dati sintetici/modellati, dichiarati come tali. Cio che
dimostrano - il crollo della PPV col base-rate, il divario entropia-nominale / resistenza-pratica -
dipende dalla *struttura* dei problemi (eventi malevoli rari; distribuzioni sbilanciate) e non dai
valori specifici del modello: sono risultati robusti, non artefatti dei parametri scelti. Restano
genuinamente fuori portata la raccolta di dati empirici reali su larga scala e la peer review
esterna; la prima e sostituibile in laboratorio (percorso indicato sopra), la seconda no. Questo e il
limite onesto del livello raggiungibile in un repository, ed e dichiarato invece che mascherato.

---

## Riferimenti

- [Axelsson 2000] - base-rate fallacy (Esperimento A).
- [Massey 1994] - guessing entropy (Esperimento B).
- [Bonneau 2012] - partial guessing metrics, critica della guessing entropy media (Esperimento B).
- [Shannon 1949] - entropia (Esperimento B).

Dettagli in `../REFERENCES.md`. Fondamenti teorici collegati in
`../08-defense-hardenings (Blue Team Prevention)/THEORETICAL-FOUNDATIONS.md` e
`../04-system-exploitation/THEORETICAL-FOUNDATIONS.md`.
