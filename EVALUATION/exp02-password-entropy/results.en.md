> **English** | [Italiano](results.md)

# Results - Experiment B (guessing entropy vs Shannon)

Verbatim output of `guessing_entropy.py` (deterministic, reproducible). Numbers **computed**
exactly on the Zipf model, not estimated.

```
==========================================================================
EXPERIMENT B - Shannon entropy vs guessing metrics (Zipf password model)
V=1,000,000 ranked passwords,  Zipf exponent s=1.0
==========================================================================

Most probable password mass  p_max = 6.9480e-02  (the single most common password covers 6.95% of accounts)
Shannon entropy    H1   =   13.406 bits   (nominal 'strength' = 2^H1 candidates)
Min-entropy        Hinf =    3.847 bits   (resistance to the single best guess)
Mean guessing ent. G    = 69,480 guesses = 16.084 bits (log2 G, Massey 1994)

NOTE (methodological, Bonneau 2012): the MEAN guessing entropy G here EXCEEDS H1.
This is not an error - it is the known failure of mean guessing entropy as a security
metric: the arithmetic mean is dominated by the heavy tail (the rare passwords that need
many guesses pull the average up), hiding the fact that the HEAD of the distribution is
weak. The attacker-relevant metrics are the min-entropy and the partial guessing curve.

Shannon overestimates single-guess resistance by H1 - Hinf = 9.559 bits.

Alpha-work-factor (guesses needed to crack a fraction alpha of accounts):
   alpha |   guesses needed |  equiv. bits log2(k)
----------------------------------------------------
     10% |                2 |                 1.00
     25% |               21 |                 4.39
     50% |              749 |                 9.55
     75% |           27,373 |                14.74
     90% |          237,100 |                17.86

Guessing curve (fraction of accounts cracked after k in-order guesses):
   guesses k |   fraction cracked |  equiv. bits log2(k)
------------------------------------------------------------
           1 |             6.95% |                 0.00
          10 |            20.35% |                 3.32
         100 |            36.04% |                 6.64
       1,000 |            52.01% |                 9.97
      10,000 |            68.00% |                13.29
     100,000 |            84.00% |                16.61
```

## Reading of the results

1. **Shannon overestimates practical resistance.** The nominal Shannon entropy is 13.4 bits, but the
   min-entropy is only **3.85 bits**: the single most common password alone covers 6.95% of accounts.
   Shannon overestimates single-guess resistance by **9.56 bits** (a factor of ~750x).

2. **Methodological subtlety (and confirmation of Bonneau 2012).** The **mean** guessing entropy
   (Massey) turns out to be 16.08 bits, that is *greater* than Shannon. This is not an error: it is
   the known failure of the mean as a security metric, dominated by the heavy tail. The experiment
   empirically reproduces precisely the critique that led [Bonneau 2012] to propose the **partial
   guessing** metrics.

3. **Alpha-work-factor: the correct metric.** The guesses needed to crack a fraction of accounts are
   very low at the head of the distribution: **2 guesses, 10%**, **21, 25%**, **749, 50%**. A
   dictionary attacker cracks the **majority** of accounts (52%) in ~1,000 guesses (~2^10), against a
   nominal "strength" of 2^13.4 ~ 10,855 candidates.

4. **Implication.** Practical resistance is governed by the head of the distribution, not by the
   nominal character-space entropy. It is the quantitative, measured foundation of dictionary and
   rule-based attacks (module 04, section 3.3) and of why WPA2/WPA3 PSK robustness depends on the
   guessing entropy of the passphrase and not on its nominal space (module 06, section 3.2 and 4.2).

## Validity note (disclosed limitation)

The distribution is a **Zipf model** (exponent `s=1.0`) parameterized from the literature
([Bonneau 2012]; Malone & Maher), not a specific breached corpus. The quantities are exact for the
model. The result - the gap between nominal entropy and practical resistance - is driven by the
*shape* (strongly skewed) of the distribution and is robust with respect to the exact exponent: it
holds for any realistic password population. For a measurement on a real corpus, replace `zipf_probs()`
with the empirical frequencies of a dataset, keeping the metric computation unchanged.
