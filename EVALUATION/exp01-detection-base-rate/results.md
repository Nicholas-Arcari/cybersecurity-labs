> [English](results.en.md) | **Italiano**

# Risultati - Esperimento A (detection + base-rate)

Output verbatim di `generate_and_evaluate.py` (seed=42, riproducibile). Numeri **misurati**,
non stimati. Rieseguire il comando riproduce esattamente questi valori.

```
==========================================================================
EXPERIMENT A - SSH brute-force detection + base-rate effect on PPV
seed=42  N=1,000,000  base_rate(main)=0.001
==========================================================================

Dataset: 1,000,000 windows, 909 malicious (9.09e-04 empirical base rate)

Threshold sweep (detector: alert iff failed_logins > T):
  T |     TP       FP     FN |    Prec  Recall      F1 |       FPR     TPR
--------------------------------------------------------------------------
  0 |    909   399158      0 |  0.0023  1.0000  0.0045 |  4.00e-01  1.0000
  1 |    909    98954      0 |  0.0091  1.0000  0.0180 |  9.90e-02  1.0000
  2 |    904    23454      5 |  0.0371  0.9945  0.0716 |  2.35e-02  0.9945
  3 |    900    10180      9 |  0.0812  0.9901  0.1501 |  1.02e-02  0.9901
  4 |    886     7298     23 |  0.1083  0.9747  0.1949 |  7.30e-03  0.9747
  5 |    853     5610     56 |  0.1320  0.9384  0.2314 |  5.62e-03  0.9384
  6 |    823     3944     86 |  0.1726  0.9054  0.2900 |  3.95e-03  0.9054
  7 |    786     2544    123 |  0.2360  0.8647  0.3708 |  2.55e-03  0.8647
  8 |    743     1524    166 |  0.3277  0.8174  0.4679 |  1.53e-03  0.8174
  9 |    713      801    196 |  0.4709  0.7844  0.5885 |  8.02e-04  0.7844
 10 |    686      423    223 |  0.6186  0.7547  0.6799 |  4.23e-04  0.7547
 11 |    668      197    241 |  0.7723  0.7349  0.7531 |  1.97e-04  0.7349
 12 |    649       97    260 |  0.8700  0.7140  0.7843 |  9.71e-05  0.7140
 13 |    639       42    270 |  0.9383  0.7030  0.8038 |  4.20e-05  0.7030
 14 |    634       16    275 |  0.9754  0.6975  0.8133 |  1.60e-05  0.6975
 15 |    632        7    277 |  0.9890  0.6953  0.8165 |  7.01e-06  0.6953
 16 |    631        1    278 |  0.9984  0.6942  0.8189 |  1.00e-06  0.6942
 17 |    631        0    278 |  1.0000  0.6942  0.8195 |  0.00e+00  0.6942
 18 |    631        0    278 |  1.0000  0.6942  0.8195 |  0.00e+00  0.6942
 19 |    631        0    278 |  1.0000  0.6942  0.8195 |  0.00e+00  0.6942
 20 |    631        0    278 |  1.0000  0.6942  0.8195 |  0.00e+00  0.6942
--------------------------------------------------------------------------
Max-F1 operating point (precision-oriented): T=17  F1=0.8195  precision=1.0000  recall=0.6942  FPR=0.00e+00
High-recall operating point (recall >= 0.90, SOC that prioritizes detection):
  T=6  recall(TPR)=0.9054  FPR=3.95e-03  precision=0.1726

==========================================================================
Base-rate effect on Positive Predictive Value at the high-recall operating point
(fixed detector: TPR=0.9054, FPR=3.95e-03)
==========================================================================
   base rate p |   analytical PPV |    empirical PPV |  alarms that are FALSE
--------------------------------------------------------------------------
         1e-02 |           0.6985 |           0.6970 |                 30.2%
         1e-03 |           0.1867 |           0.1914 |                 81.3%
         1e-04 |           0.0224 |           0.0237 |                 97.8%
         1e-05 |           0.0023 |           0.0020 |                 99.8%
```

## Lettura dei risultati

1. **Compromesso precision/recall misurato.** Lo sweep della soglia mostra il classico
   trade-off: a `T=6` il rilevatore ha recall 0.905 ma precision 0.173 (molti falsi positivi);
   a `T=17` ha precision 1.000 ma recall 0.694 (perde il 30% degli attacchi, i "low-and-slow").
   Nessuna soglia e simultaneamente perfetta - conferma operativa del triangolo
   falsi positivi / falsi negativi / copertura.

2. **Crollo della PPV col base-rate (risultato centrale).** Fissato un punto operativo realistico
   ad alta recall (`T=6`, come opererebbe un SOC che vuole catturare gli attacchi), la Positive
   Predictive Value **crolla** al calare del tasso base: 0.70, 0.19, 0.022, 0.0023 per
   `p` da `1e-2` a `1e-5`. A `p=1e-5` il **99.8% degli allarmi e falso**.

3. **Conferma di Axelsson (2000).** La colonna analitica (formula bayesiana
   `PPV = TPR*p / (TPR*p + FPR*(1-p))`) coincide con la colonna empirica ottenuta per resampling
   indipendente (0.6985 vs 0.6970; 0.1867 vs 0.1914; 0.0224 vs 0.0237; 0.0023 vs 0.0020). La
   previsione teorica del base-rate fallacy e verificata empiricamente su dati misurati.

4. **Implicazione difensiva.** Poiche la PPV e determinata dal tasso base (non migliorabile) e non
   dalla sola accuratezza del rilevatore, l'unica via per recuperare valore predittivo e alzare il
   base-rate effettivo via **correlazione** (modulo 08, sez. 4.1) o azzerare i falsi positivi via
   **deception** (modulo 08, sez. 3.2). Questo esperimento e la giustificazione quantitativa,
   misurata, di quelle due contromisure.

## Nota di validita (limite dichiarato)

Il dataset e **sintetico**: le distribuzioni dei login falliti (benigni vs brute-force) sono una
scelta di modellazione, non traffico di produzione catturato. Le metriche sono quindi valide
rispetto al modello. Il valore dell'esperimento e (a) la metodologia riproducibile e (b) la
dimostrazione dell'effetto base-rate, che dipende dalla forma del problema (eventi malevoli rari)
e non dai valori specifici del modello. Per una validazione su traffico reale, sostituire
`make_dataset()` con un caricatore di log etichettati reali mantenendo invariata la pipeline di misura.
