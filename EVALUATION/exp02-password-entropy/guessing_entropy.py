#!/usr/bin/env python3
"""
Experiment B - Empirical comparison of Shannon entropy vs attacker-relevant guessing
metrics on a skewed (Zipf) password distribution.

Ties to: 04-system-exploitation THEORETICAL-FOUNDATIONS section 3.3 (guessing entropy
vs Shannon entropy) and 06-wireless-security section 3.2/4.2 (WPA2 offline attack cost).

Method (fully reproducible, pure stdlib):
  Real password frequency distributions are empirically well approximated by a Zipf law
  (Bonneau 2012; Malone & Maher). We build a Zipf distribution over V ranked passwords
  and COMPUTE:
    - Shannon entropy  H1     = - sum p_i log2 p_i          (nominal "strength")
    - Min-entropy      Hinf   = - log2(p_max)               (single best guess)
    - Guessing entropy G      =   sum_i i * p_i             (Massey 1994; expected guesses)
    - Guessing curve          =   sum_{i<=k} p_i            (fraction cracked after k guesses)
  and compare the "bits" implied by each.

Result claim under test (module 04, section 3.3): for skewed distributions the Shannon
entropy MASSIVELY overestimates resistance relative to the attacker-optimal guessing
metrics; a dictionary attacker who tries in order of decreasing probability cracks a
large fraction of accounts in far fewer guesses than 2^H1.

LIMITATION (disclosed): the distribution is a Zipf MODEL parameterized from the
literature, not a specific breached corpus. The computed quantities are exact for the
model; the value is the reproducible demonstration of the entropy/guessing gap, which is
distribution-shape-driven and holds for any realistic (skewed) password population.
"""

import math

V = 1_000_000        # vocabulary: number of distinct ranked passwords
S = 1.0              # Zipf exponent (password corpora fit s ~ 0.7-1.1; s=1 is canonical)


def zipf_probs(v, s):
    """Return normalized Zipf probabilities p_i for ranks i=1..v."""
    weights = [1.0 / (i ** s) for i in range(1, v + 1)]
    Z = sum(weights)
    return [w / Z for w in weights]


def shannon_entropy_bits(p):
    return -sum(pi * math.log2(pi) for pi in p if pi > 0)


def min_entropy_bits(p):
    return -math.log2(max(p))


def guessing_entropy(p):
    """Massey 1994: expected number of guesses of an optimal attacker (probs already sorted desc)."""
    return sum(i * pi for i, pi in enumerate(p, start=1))


def guessing_curve(p, ks):
    """Fraction of the population cracked after k in-order guesses."""
    out = {}
    cum = 0.0
    ks_sorted = sorted(ks)
    target = 0
    for i, pi in enumerate(p, start=1):
        cum += pi
        while target < len(ks_sorted) and i == ks_sorted[target]:
            out[ks_sorted[target]] = cum
            target += 1
        if target >= len(ks_sorted):
            break
    return out


def alpha_work_factor(p, alphas):
    """Guesses needed to crack a fraction alpha of accounts (partial guessing metric).
    Returns {alpha: (k, cumulative_fraction_at_k)}."""
    out = {}
    cum = 0.0
    alphas_sorted = sorted(alphas)
    target = 0
    for i, pi in enumerate(p, start=1):
        cum += pi
        while target < len(alphas_sorted) and cum >= alphas_sorted[target]:
            out[alphas_sorted[target]] = (i, cum)
            target += 1
        if target >= len(alphas_sorted):
            break
    return out


def main():
    print("=" * 74)
    print("EXPERIMENT B - Shannon entropy vs guessing metrics (Zipf password model)")
    print(f"V={V:,} ranked passwords,  Zipf exponent s={S}")
    print("=" * 74)

    p = zipf_probs(V, S)   # already sorted descending (rank 1 = most probable)

    H1 = shannon_entropy_bits(p)
    Hinf = min_entropy_bits(p)
    G = guessing_entropy(p)
    G_bits = math.log2(G)

    print(f"\nMost probable password mass  p_max = {p[0]:.4e}  "
          f"(the single most common password covers {p[0]:.2%} of accounts)")
    print(f"Shannon entropy    H1   = {H1:8.3f} bits   (nominal 'strength' = 2^H1 candidates)")
    print(f"Min-entropy        Hinf = {Hinf:8.3f} bits   (resistance to the single best guess)")
    print(f"Mean guessing ent. G    = {G:,.0f} guesses = {G_bits:.3f} bits (log2 G, Massey 1994)")

    print("\nNOTE (methodological, Bonneau 2012): the MEAN guessing entropy G here EXCEEDS H1.")
    print("This is not an error - it is the known failure of mean guessing entropy as a security")
    print("metric: the arithmetic mean is dominated by the heavy tail (the rare passwords that need")
    print("many guesses pull the average up), hiding the fact that the HEAD of the distribution is")
    print("weak. The attacker-relevant metrics are the min-entropy and the partial guessing curve.")

    print(f"\nShannon overestimates single-guess resistance by H1 - Hinf = {H1 - Hinf:.3f} bits.")

    print("\nAlpha-work-factor (guesses needed to crack a fraction alpha of accounts):")
    print(f"{'alpha':>8} | {'guesses needed':>16} | {'equiv. bits log2(k)':>20}")
    print("-" * 52)
    awf = alpha_work_factor(p, [0.10, 0.25, 0.50, 0.75, 0.90])
    for a in (0.10, 0.25, 0.50, 0.75, 0.90):
        k, _ = awf[a]
        print(f"{a:>8.0%} | {k:>16,} | {math.log2(k):>20.2f}")

    print("\nGuessing curve (fraction of accounts cracked after k in-order guesses):")
    ks = [1, 10, 100, 1_000, 10_000, 100_000]
    curve = guessing_curve(p, ks)
    print(f"{'guesses k':>12} | {'fraction cracked':>18} | {'equiv. bits log2(k)':>20}")
    print("-" * 60)
    for k in ks:
        frac = curve.get(k, float('nan'))
        print(f"{k:>12,} | {frac:>17.2%} | {math.log2(k):>20.2f}")

    print("\nInterpretation: a dictionary attacker trying passwords in order of decreasing")
    print(f"probability cracks the MAJORITY of accounts (52%) in just 1,000 guesses (~2^10),")
    print(f"against a nominal Shannon strength of 2^H1 = 2^{H1:.1f} ~ {2**H1:,.0f} candidates.")
    print("The head of the distribution, not the nominal entropy, governs practical resistance.")
    print("The correct attacker-relevant metrics are min-entropy and the alpha-work-factor, not")
    print("Shannon entropy (nor mean guessing entropy). This is the quantitative basis of dictionary")
    print("and rule-based attacks (module 04) and of why WPA2/WPA3 PSK strength depends on guessing")
    print("entropy of the passphrase (module 06), not on nominal character-space entropy.")


if __name__ == "__main__":
    main()
