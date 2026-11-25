> **English** | [Italiano](README.md)

# Empirical Evaluation - Reproducible Quantitative Measurements

> - **Level:** Experimental evaluation (complement to the `THEORETICAL-FOUNDATIONS.md`)
> - **Purpose:** Close the last gap toward the academic research level: move from a quantitative analysis *derived from the literature* to measurements *obtained by running reproducible experiments*.
> - **Prerequisites:** Python 3 (standard library only). No external dependencies.

---

## Why this folder exists

The `THEORETICAL-FOUNDATIONS.md` documents of each module formalize the models and cite the primary
literature, but their quantitative analysis is *derived* (the formulas come from the papers). Academic
research-level work additionally requires **empirical evaluation**: measurements obtained from one's
own experiments, and above all the **reproducibility** that allows their independent verification.
This folder provides exactly that.

I am honest about the scope. Of the three elements that separate this work from a research master's
thesis (original empirical evaluation; complete formal proofs; peer review), this folder addresses the
first and enables the third:

- **Original empirical evaluation:** runnable experiments that *measure* the theoretical phenomena.
- **Independent verifiability:** deterministic code (fixed seeds), zero dependencies, with recorded
  verbatim output. Anyone can re-run and obtain the same numbers - reproducibility is the substance
  that peer review verifies (peer review itself, which requires qualified external reviewers, remains
  beyond the reach of a repository).

**Integrity discipline (non-negotiable):** no number is invented. Every value in these documents comes
from the real execution of the code included here. The datasets are synthetic/modeled and this is
**explicitly disclosed** in every experiment: the behavior of real detectors/metrics is measured on
labeled data, a standard technique when real attack data is scarce. A fabricated "measured" number
would be an integrity violation far more serious than an incorrect citation, and it is avoided by
construction (the code is here, it re-runs).

---

## Folder Structure

```
EVALUATION/
+-- README.md                          # this file: methodology, reproducibility, synthesis
|
+-- exp01-detection-base-rate/         # Experiment A (module 08)
|   +-- generate_and_evaluate.py       # runnable code (deterministic, stdlib)
|   +-- results.md                     # verbatim output + reading of the results
|
+-- exp02-password-entropy/            # Experiment B (modules 04, 06)
    +-- guessing_entropy.py            # runnable code (deterministic, stdlib)
    +-- results.md                     # verbatim output + reading of the results
```

---

## Experiments and measured results (headline)

### Experiment A - Detection engineering and base-rate fallacy (module 08)

An SSH brute-force detector (threshold rule) evaluated on a labeled dataset of 1,000,000 observation
windows. **Measured results:**

- Real precision/recall trade-off: at recall 0.905 the precision is only 0.173; no threshold is
  simultaneously perfect.
- At the high-recall operating point, the **Positive Predictive Value collapses with the base rate**:
  `0.70 -> 0.19 -> 0.022 -> 0.0023` for base rates from `1e-2` to `1e-5`. At `1e-5`, **99.8% of the
  alarms are false**.
- The Bayesian prediction of [Axelsson 2000] (`PPV = TPR*p / (TPR*p + FPR*(1-p))`) is **confirmed** by
  the empirical verification via independent resampling (deviations < 0.5 percentage points).

Thesis tested: the difficulty of detection is determined by the base rate, not by the accuracy of the
detector (module 08 foundations, section 3.1). It quantitatively justifies correlation (section 4.1)
and deception (section 3.2). Detail: [exp01-detection-base-rate/results.en.md](exp01-detection-base-rate/results.en.md).

### Experiment B - Shannon entropy vs guessing metrics (modules 04, 06)

Comparison between nominal entropy and attacker-relevant metrics on a Zipf password distribution.
**Measured results:**

- Shannon `H1 = 13.41 bits` but min-entropy `Hinf = 3.85 bits`: Shannon **overestimates** the
  resistance to the single guess by 9.56 bits.
- Measured alpha-work-factor: **2 guesses crack 10%**, **749 crack 50%**; a dictionary attacker cracks
  the majority of accounts in ~1,000 guesses (~2^10) against 2^13.4 nominal.
- The experiment empirically reproduces the critique of [Bonneau 2012] of *mean* guessing entropy
  (which here, tail-dominated, exceeds Shannon): the correct metric is partial guessing.

Thesis tested: practical resistance depends on the guessing entropy (head of the distribution), not on
the nominal entropy (module 04 foundations, section 3.3; module 06, section 3.2/4.2). Detail:
[exp02-password-entropy/results.en.md](exp02-password-entropy/results.en.md).

---

## Reproducibility

Requirements: only Python 3 (standard library). No installation.

```Bash
# Experiment A (detection + base-rate) - takes ~4 seconds
python3 exp01-detection-base-rate/generate_and_evaluate.py

# Experiment B (password entropy) - takes < 1 second
python3 exp02-password-entropy/guessing_entropy.py
```

The scripts are **deterministic** (fixed seeds): every re-run produces exactly the values reported in
the respective `results.md`. To validate the theses on **real data** instead of modeled data, each
script isolates the dataset generation in a single function (`make_dataset()` in A, `zipf_probs()` in
B): replacing it with a loader of real data (labeled logs, frequencies of a password corpus) leaves the
measurement pipeline unchanged. This is the explicit path from the model to field measurement.

---

## Honest methodological note

These experiments measure phenomena on synthetic/modeled data, disclosed as such. What they
demonstrate - the collapse of the PPV with the base rate, the nominal-entropy / practical-resistance
gap - depends on the *structure* of the problems (rare malicious events; skewed distributions) and not
on the specific values of the model: they are robust results, not artifacts of the chosen parameters.
Genuinely out of reach remain the collection of real empirical data at scale and external peer review;
the former is substitutable in the lab (path indicated above), the latter is not. This is the honest
limit of the level achievable in a repository, and it is disclosed rather than masked.

---

## References

- [Axelsson 2000] - base-rate fallacy (Experiment A).
- [Massey 1994] - guessing entropy (Experiment B).
- [Bonneau 2012] - partial guessing metrics, critique of mean guessing entropy (Experiment B).
- [Shannon 1949] - entropy (Experiment B).

Details in `../REFERENCES.en.md`. Related theoretical foundations in
`../08-defense-hardenings (Blue Team Prevention)/THEORETICAL-FOUNDATIONS.en.md` and
`../04-system-exploitation/THEORETICAL-FOUNDATIONS.en.md`.
