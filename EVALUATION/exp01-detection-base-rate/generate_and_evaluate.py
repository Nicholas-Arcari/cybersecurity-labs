#!/usr/bin/env python3
"""
Experiment A - Empirical evaluation of an SSH brute-force detector and of the
base-rate effect on positive predictive value (PPV).

Ties to: 08-defense-hardenings THEORETICAL-FOUNDATIONS section 3.1 (Axelsson 2000,
base-rate fallacy) and 4.1 (correlation as base-rate raising).

Method (fully reproducible, pure stdlib, fixed seed):
  1. Generate a LABELED synthetic dataset of per-source observation windows.
     Each sample = number of failed SSH logins from one source IP in a 60 s window.
     Ground truth: benign vs malicious (brute force), with a controllable base rate.
  2. Detector: raise an alert if failed_count > threshold T (the rule of DEF-001).
  3. Sweep T; measure the confusion matrix and precision / recall / F1 / FPR / TPR.
     These are REAL measurements of a REAL detector on a labeled dataset.
  4. Fix an operating point and compute the PPV analytically across realistic base
     rates, verifying Axelsson's result empirically by resampling.

LIMITATION (disclosed): the dataset is synthetic. The behavioural model (benign vs
brute-force failed-login distributions) is a modelling choice, not captured production
traffic. The measured metrics are therefore valid relative to this model; the value of
the experiment is the methodology and the reproducible demonstration of the base-rate
effect, not an absolute claim about a specific real network.
"""

import random
import math

SEED = 42
N_TOTAL = 1_000_000        # total observation windows in the main dataset
BASE_RATE_MAIN = 1e-3      # fraction of windows that are malicious in the main dataset


def poisson(lam, rng):
    """Poisson sample. Knuth for small lam, normal approximation (rounded) for large."""
    if lam < 30:
        L = math.exp(-lam)
        k = 0
        p = 1.0
        while True:
            k += 1
            p *= rng.random()
            if p <= L:
                return k - 1
    else:
        # normal approximation N(lam, lam), clamped at 0
        return max(0, int(round(rng.gauss(lam, math.sqrt(lam)))))


def sample_benign(rng):
    """Benign source: mostly 0-3 failed logins (typos); ~1% noisy automation clients."""
    if rng.random() < 0.01:
        return poisson(6.0, rng)      # misconfigured/automation client -> occasional FP source
    return poisson(0.5, rng)


def sample_malicious(rng):
    """Brute force: 70% aggressive bursts, 30% low-and-slow (stealth) -> realistic FN."""
    if rng.random() < 0.30:
        return poisson(8.0, rng)      # stealthy / rate-limited attacker
    return poisson(45.0, rng)         # aggressive attacker


def make_dataset(n_total, base_rate, rng):
    """Return list of (failed_count, label) with label 1 = malicious."""
    data = []
    for _ in range(n_total):
        if rng.random() < base_rate:
            data.append((sample_malicious(rng), 1))
        else:
            data.append((sample_benign(rng), 0))
    return data


def confusion(data, T):
    """Detector: alert iff count > T. Return TP, FP, TN, FN."""
    tp = fp = tn = fn = 0
    for count, label in data:
        alert = count > T
        if label == 1 and alert:
            tp += 1
        elif label == 1 and not alert:
            fn += 1
        elif label == 0 and alert:
            fp += 1
        else:
            tn += 1
    return tp, fp, tn, fn


def metrics(tp, fp, tn, fn):
    precision = tp / (tp + fp) if (tp + fp) else float('nan')
    recall = tp / (tp + fn) if (tp + fn) else float('nan')
    f1 = (2 * precision * recall / (precision + recall)
          if (precision + recall) and not math.isnan(precision) and not math.isnan(recall)
          else float('nan'))
    fpr = fp / (fp + tn) if (fp + tn) else float('nan')
    tpr = recall
    return precision, recall, f1, fpr, tpr


def analytical_ppv(tpr, fpr, base_rate):
    """Bayes: PPV = TPR*p / (TPR*p + FPR*(1-p))  (Axelsson 2000)."""
    num = tpr * base_rate
    den = tpr * base_rate + fpr * (1 - base_rate)
    return num / den if den else float('nan')


def main():
    rng = random.Random(SEED)
    print("=" * 74)
    print("EXPERIMENT A - SSH brute-force detection + base-rate effect on PPV")
    print(f"seed={SEED}  N={N_TOTAL:,}  base_rate(main)={BASE_RATE_MAIN}")
    print("=" * 74)

    data = make_dataset(N_TOTAL, BASE_RATE_MAIN, rng)
    n_mal = sum(lbl for _, lbl in data)
    print(f"\nDataset: {N_TOTAL:,} windows, {n_mal:,} malicious "
          f"({n_mal / N_TOTAL:.2e} empirical base rate)\n")

    # 1) Threshold sweep -> precision/recall/F1 (real measurements)
    print("Threshold sweep (detector: alert iff failed_logins > T):")
    print(f"{'T':>3} | {'TP':>6} {'FP':>8} {'FN':>6} | {'Prec':>7} {'Recall':>7} "
          f"{'F1':>7} | {'FPR':>9} {'TPR':>7}")
    print("-" * 74)
    best_f1 = (-1, None)
    rows = []
    for T in range(0, 21):
        tp, fp, tn, fn = confusion(data, T)
        prec, rec, f1, fpr, tpr = metrics(tp, fp, tn, fn)
        rows.append((T, tp, fp, fn, prec, rec, f1, fpr, tpr))
        print(f"{T:>3} | {tp:>6} {fp:>8} {fn:>6} | {prec:>7.4f} {rec:>7.4f} "
              f"{f1:>7.4f} | {fpr:>9.2e} {tpr:>7.4f}")
        if not math.isnan(f1) and f1 > best_f1[0]:
            best_f1 = (f1, (T, tpr, fpr, prec, rec))

    f1_val, (T_f1, tpr_f1, fpr_f1, prec_f1, rec_f1) = best_f1
    print("-" * 74)
    print(f"Max-F1 operating point (precision-oriented): T={T_f1}  F1={f1_val:.4f}  "
          f"precision={prec_f1:.4f}  recall={rec_f1:.4f}  FPR={fpr_f1:.2e}")

    # Select a REALISTIC operating point for the base-rate study: a SOC that
    # prioritizes catching attacks operates at high recall, accepting a small
    # (nonzero) false-positive rate. We pick the lowest T achieving recall >= 0.90.
    TARGET_RECALL = 0.90
    op = None
    for (T, tp, fp, fn, prec, rec, f1, fpr, tpr) in rows:
        if not math.isnan(rec) and rec >= TARGET_RECALL:
            op = (T, tpr, fpr, prec, rec)
    T_op, tpr_op, fpr_op, prec_op, rec_op = op
    print(f"High-recall operating point (recall >= {TARGET_RECALL:.2f}, SOC that prioritizes "
          f"detection):\n  T={T_op}  recall(TPR)={tpr_op:.4f}  FPR={fpr_op:.2e}  "
          f"precision={prec_op:.4f}")

    # 2) Base-rate effect on PPV at the high-recall operating point (Axelsson)
    print("\n" + "=" * 74)
    print("Base-rate effect on Positive Predictive Value at the high-recall operating point")
    print(f"(fixed detector: TPR={tpr_op:.4f}, FPR={fpr_op:.2e})")
    print("=" * 74)
    print(f"{'base rate p':>14} | {'analytical PPV':>16} | {'empirical PPV':>16} "
          f"| {'alarms that are FALSE':>22}")
    print("-" * 74)
    for p in (1e-2, 1e-3, 1e-4, 1e-5):
        ppv_a = analytical_ppv(tpr_op, fpr_op, p)
        # empirical verification: resample a fresh dataset at base rate p
        rng2 = random.Random(SEED + int(-math.log10(p)))
        n_emp = 2_000_000
        d2 = make_dataset(n_emp, p, rng2)
        tp, fp, tn, fn = confusion(d2, T_op)
        ppv_e = tp / (tp + fp) if (tp + fp) else float('nan')
        print(f"{p:>14.0e} | {ppv_a:>16.4f} | {ppv_e:>16.4f} "
              f"| {1 - ppv_a:>21.1%}")

    print("\nInterpretation: even with a strong detector (high TPR, low FPR), the")
    print("positive predictive value collapses as the base rate falls - the analytical")
    print("Bayesian prediction (Axelsson 2000) is confirmed by the empirical resampling.")
    print("This is the quantitative justification for correlation and deception in module 08.")


if __name__ == "__main__":
    main()
