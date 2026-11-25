> [English](SELF-ASSESSMENT.en.md) | **Italiano**

# Autovalutazione critica e minacce alla validita

> - **Cos'e:** una revisione critica *avversariale interna* del lavoro contenuto in questa repository,
>   scritta nella voce di un revisore scettico che cerca di demolirlo.
> - **Cosa NON e:** peer review esterna. La peer review richiede revisori qualificati e indipendenti;
>   nessun documento autoprodotto puo sostituirla, e questo file non lo pretende. Affronta la *funzione*
>   della revisione (individuare i difetti), non ne rivendica il *credenziale*.
> - **Perche esiste:** una limitazione dichiarata onestamente vale piu di un pregio taciuto. Un lavoro
>   serio red-teamma se stesso. Questo file elenca le debolezze che un revisore competente solleverebbe.

---

## Disclaimer di integrita

Chi scrive ha un evidente **conflitto di interesse** (e l'autore). Un'autovalutazione ha bias di
incentivo strutturale: tende a minimizzare. Il lettore tratti questo documento come un *limite
inferiore* alle criticita, non come il loro elenco esaustivo. Inoltre, per trasparenza: la stesura di
questa repository e stata **assistita da un modello linguistico (LLM)**. Cio impone al lettore un dovere
di verifica indipendente su due fronti in particolare - la **correttezza delle citazioni** (che una
sintesi puo travisare) e la **correttezza dei numeri** (mitigata qui rendendo tutto il codice
eseguibile e riproducibile, vedi sotto). Le regole interne adottate (citare solo fonti verificate; mai
inventare numeri "misurati"; eseguire il codice) riducono il rischio ma non azzerano il dovere di
verifica del revisore.

---

## Minacce alla validita, per strato

### Strato operativo (README di modulo + finding)

1. **Nessuna riproduzione indipendente.** I finding sono documentati su sistemi di laboratorio di
   proprieta dell'autore, in un unico ambiente, da un solo autore. Nessun terzo li ha replicati. La
   validita esterna e quindi non stabilita.
2. **Output rappresentativi, non tutti catturati.** I README mescolano l'esperienza reale di laboratorio
   con **output di esempio illustrativi** (indirizzi IP, hash, banner). Non ogni blocco di output e la
   cattura verbatim di una specifica esecuzione dell'autore; alcuni sono esemplari plausibili a scopo
   didattico. Un revisore non deve leggerli come evidenza forense.
3. **Novita limitata.** La maggior parte delle tecniche e canonica (da manuale). Il contributo e la
   *qualita e coerenza della documentazione*, non la scoperta di attacchi nuovi. E un portfolio, non
   una ricerca originale sul piano offensivo.

### Strato teorico (THEORETICAL-FOUNDATIONS + REFERENCES)

1. **Derivazioni, non dimostrazioni certificate.** Le "prove" (Bayes, entropia, birthday bound,
   Turing-completezza del ROP) sono derivazioni rigorose ma *non machine-checked* e in alcuni casi
   sketch. Non sostituiscono le dimostrazioni originali delle fonti.
2. **Rischio di travisamento delle fonti.** La bibliografia cita opere reali, ma le annotazioni sono
   *sintesi dell'autore*: un revisore deve verificare ogni caratterizzazione contro la fonte primaria.
   La disciplina di citazione riduce il rischio di riferimenti fabbricati, non quello di interpretazioni
   imprecise.
3. **Le unificazioni trasversali sono framing, non teoremi.** Affermazioni come "il confused deputy
   ricorre dal web al cloud" o "la freshness e un principio unificante" sono *interpretazioni
   pedagogiche* utili, non risultati formali dimostrati.
4. **La parte quantitativa teorica e per lo piu ricapitolativa.** L'analisi quantitativa dei foundations
   riespone risultati noti; il contributo quantitativo *proprio* e confinato in `EVALUATION/`.

### Strato empirico (EVALUATION)

1. **Dati sintetici - la minaccia maggiore.** Entrambi gli esperimenti girano su dati modellati, non su
   traffico reale o corpora di password violati. I risultati dimostrano *metodologia* ed *effetti
   strutturali* (il crollo della PPV col base-rate; il divario entropia/guessing), non misure di uno
   specifico sistema reale. La validita esterna e esplicitamente limitata.
2. **Sensibilita ai parametri non esplorata.** Exp B fissa Zipf `s=1.0`; i corpora reali variano
   (`s ~ 0.7-1.1`) e i numeri specifici cambiano con `s` (il divario qualitativo e robusto, ma la
   sensibilita non e stata mappata con uno sweep). Exp A sceglie a mano le distribuzioni benigna/maligna:
   i valori specifici di precision/recall sono artefatti di quelle scelte (solo il crollo della PPV e
   robusto).
3. **Assenza di intervalli di confidenza.** Exp A usa un solo seed e una singola estrazione di
    resampling per base rate, senza ripetizioni multiple ne stima della varianza. Un revisore chiederebbe
    N ripetizioni e barre d'errore.

### Strato formale (FORMAL-MODELS)

 1. **Astrazione pesante, costruita conoscendo la risposta.** Il modello cattura *che* KRACK e un
    difetto di stato, ma modella solo lo stato KRACK-rilevante (Dolev-Yao, contatore eliso/limitato),
    non l'intera macchina a stati IEEE 802.11. Non *riscopre* KRACK dalla specifica grezza: l'astrazione
    e disegnata gia sapendo dove guardare.
 2. **Rafforzamento induttivo manuale (e prima versione errata).** L'invariante induttivo e stato
    trovato a mano, e il primo tentativo era sbagliato (classificava male il modello patchato); il
    difetto e emerso *eseguendo* il codice. La soundness dell'astrazione e argomentata informalmente,
    non certificata.
 3. **Il modello Tamarin non e eseguito.** `wpa2_handshake.spthy` non e stato verificato in questo
    ambiente (Tamarin non installato); la sua correttezza e non verificata ed e etichettata come tale.
 4. **Ricostruzione, non nuova conoscenza.** La verifica conferma un risultato noto del 2017. E un
    esercizio di verifica formale corretto e istruttivo, non una scoperta.

### Meta (trasversale)

 1. **Autore unico, ambiente unico, nessuna replica indipendente.**
 2. **Ampiezza a scapito della profondita.** Una tesi magistrale di ricerca va *molto* a fondo su un
    problema stretto; questa repository e ampia e applicata. Sono profili diversi.
 3. **Bias dell'autovalutazione.** Questo stesso documento e soggetto al conflitto di interesse del
    punto iniziale.

---

## Cosa e, e cosa non e (verdetto onesto)

**E:** un portfolio di sicurezza full-stack a tre-piu-un strati (operativo, teorico, empirico, formale),
internamente coerente, con analisi di livello graduate, letteratura primaria citata correttamente,
misure riproducibili e una verifica formale eseguita. Regge il confronto con la componente teorica e
metodologica di un buon corso magistrale, ed e ben sopra l'asticella per un portfolio da security analyst.

**Non e:** una ricerca peer-reviewed. Mancano - e sono dichiarati - dati empirici reali su larga scala,
dimostrazioni machine-checked complete, e soprattutto la **revisione esterna indipendente**. Le prime
due sono colmabili in laboratorio con lavoro aggiuntivo (percorsi indicati nei rispettivi README); la
terza no: richiede una comunita di pari, che un repository non puo autogenerare.

---

## Come un revisore puo verificare (riproducibilita)

Le affermazioni quantitative e formali non vanno prese sulla fiducia. Sono verificabili in modo
indipendente rieseguendo il codice (solo Python 3 stdlib, deterministico):

```Bash
python3 EVALUATION/exp01-detection-base-rate/generate_and_evaluate.py   # base-rate fallacy
python3 EVALUATION/exp02-password-entropy/guessing_entropy.py           # entropia/guessing
python3 FORMAL-MODELS/wpa2-4way-handshake/handshake_model_checker.py    # controesempio KRACK
python3 FORMAL-MODELS/wpa2-4way-handshake/inductive_verification.py     # prova non-limitata del fix
```

Ogni esecuzione riproduce esattamente i valori riportati nei rispettivi `results.md`. Le citazioni
vanno verificate contro le fonti primarie elencate in `REFERENCES.md`. Questa e la forma di
verificabilita che un repository puo offrire in sostituzione parziale della fiducia; la peer review
completa resta un passo esterno che qui si dichiara mancante.
