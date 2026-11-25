> **English** | [Italiano](results.md)

# Results - Experiment A (detection + base-rate)

Verbatim output of `generate_and_evaluate.py` (seed=42, reproducible). **Measured** numbers,
not estimated. Re-running the command reproduces these values exactly.

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

## Reading of the results

1. **Measured precision/recall trade-off.** The threshold sweep shows the classic trade-off: at
   `T=6` the detector has recall 0.905 but precision 0.173 (many false positives); at `T=17` it has
   precision 1.000 but recall 0.694 (it misses 30% of the attacks, the "low-and-slow" ones). No
   threshold is simultaneously perfect - operational confirmation of the false positives / false
   negatives / coverage triangle.

2. **PPV collapse with the base-rate (central result).** Fixing a realistic high-recall operating
   point (`T=6`, as a SOC that wants to catch attacks would operate), the Positive Predictive Value
   **collapses** as the base rate falls: 0.70, 0.19, 0.022, 0.0023 for `p` from `1e-2` to
   `1e-5`. At `p=1e-5`, **99.8% of the alarms are false**.

3. **Confirmation of Axelsson (2000).** The analytical column (Bayesian formula
   `PPV = TPR*p / (TPR*p + FPR*(1-p))`) coincides with the empirical column obtained by independent
   resampling (0.6985 vs 0.6970; 0.1867 vs 0.1914; 0.0224 vs 0.0237; 0.0023 vs 0.0020). The
   theoretical prediction of the base-rate fallacy is empirically verified on measured data.

4. **Defensive implication.** Since the PPV is determined by the base rate (not improvable) and not by
   the accuracy of the detector alone, the only way to recover predictive value is to raise the
   effective base rate via **correlation** (module 08, section 4.1) or to zero out the false positives
   via **deception** (module 08, section 3.2). This experiment is the quantitative, measured
   justification of those two countermeasures.

## Validity note (disclosed limitation)

The dataset is **synthetic**: the failed-login distributions (benign vs brute-force) are a modeling
choice, not captured production traffic. The metrics are therefore valid relative to the model. The
value of the experiment is (a) the reproducible methodology and (b) the demonstration of the base-rate
effect, which depends on the shape of the problem (rare malicious events) and not on the specific
values of the model. For validation on real traffic, replace `make_dataset()` with a loader of real
labeled logs, keeping the measurement pipeline unchanged.
