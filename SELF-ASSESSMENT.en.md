> **English** | [Italiano](SELF-ASSESSMENT.md)

# Critical Self-Assessment and threats to validity

> - **What it is:** an *internal adversarial* critical review of the work in this repository, written in
>   the voice of a skeptical reviewer trying to demolish it.
> - **What it is NOT:** external peer review. Peer review requires qualified, independent reviewers; no
>   self-produced document can substitute for it, and this file does not claim to. It addresses the
>   *function* of review (finding the flaws), not its *credential*.
> - **Why it exists:** an honestly disclosed limitation is worth more than a concealed strength. Serious
>   work red-teams itself. This file lists the weaknesses a competent reviewer would raise.

---

## Integrity disclaimer

The writer has an evident **conflict of interest** (they are the author). A self-assessment has a
structural incentive bias: it tends to minimize. The reader should treat this document as a *lower
bound* on the issues, not their exhaustive list. Also, for transparency: the drafting of this repository
was **assisted by a large language model (LLM)**. This imposes on the reader a duty of independent
verification on two fronts in particular - the **correctness of the citations** (which a summary may
misrepresent) and the **correctness of the numbers** (mitigated here by making all the code executable
and reproducible, see below). The internal rules adopted (cite only verified sources; never invent
"measured" numbers; run the code) reduce the risk but do not remove the reviewer's duty to verify.

---

## Threats to validity, by layer

### Operational layer (module READMEs + findings)

1. **No independent reproduction.** The findings are documented on lab systems owned by the author, in a
   single environment, by a single author. No third party has replicated them. External validity is
   therefore not established.
2. **Representative outputs, not all captured.** The READMEs mix real lab experience with **illustrative
   example outputs** (IP addresses, hashes, banners). Not every output block is the verbatim capture of
   a specific execution by the author; some are plausible exemplars for teaching. A reviewer must not
   read them as forensic evidence.
3. **Limited novelty.** Most techniques are canonical (textbook). The contribution is the *quality and
   consistency of the documentation*, not the discovery of new attacks. It is a portfolio, not original
   research on the offensive plane.

### Theoretical layer (THEORETICAL-FOUNDATIONS + REFERENCES)

1. **Derivations, not certified proofs.** The "proofs" (Bayes, entropy, birthday bound, Turing-
   completeness of ROP) are rigorous derivations but *not machine-checked*, and in some cases sketches.
   They do not substitute for the original proofs in the sources.
2. **Risk of source misrepresentation.** The bibliography cites real works, but the annotations are the
   *author's summaries*: a reviewer must verify each characterization against the primary source. The
   citation discipline reduces the risk of fabricated references, not that of imprecise interpretations.
3. **The cross-cutting unifications are framings, not theorems.** Claims such as "the confused deputy
   recurs from web to cloud" or "freshness is a unifying principle" are useful *pedagogical
   interpretations*, not proven formal results.
4. **The theoretical quantitative part is mostly recapitulative.** The quantitative analysis of the
   foundations restates known results; the *own* quantitative contribution is confined to `EVALUATION/`.

### Empirical layer (EVALUATION)

1. **Synthetic data - the biggest threat.** Both experiments run on modeled data, not on real traffic or
   breached password corpora. The results demonstrate *methodology* and *structural effects* (the
   collapse of the PPV with the base rate; the entropy/guessing gap), not measurements of a specific
   real system. External validity is explicitly limited.
2. **Parameter sensitivity not explored.** Exp B fixes Zipf `s=1.0`; real corpora vary (`s ~ 0.7-1.1`)
   and the specific numbers change with `s` (the qualitative gap is robust, but the sensitivity was not
   mapped with a sweep). Exp A hand-picks the benign/malicious distributions: the specific
   precision/recall values are artifacts of those choices (only the PPV collapse is robust).
3. **No confidence intervals.** Exp A uses a single seed and a single resampling draw per base rate,
    without multiple repetitions or variance estimation. A reviewer would ask for N repetitions and
    error bars.

### Formal layer (FORMAL-MODELS)

 1. **Heavy abstraction, built knowing the answer.** The model captures *that* KRACK is a state defect,
    but models only the KRACK-relevant state (Dolev-Yao, elided/bounded counter), not the full IEEE
    802.11 state machine. It does not *rediscover* KRACK from the raw spec: the abstraction is designed
    already knowing where to look.
 2. **Manual inductive strengthening (and a first buggy version).** The inductive invariant was found by
    hand, and the first attempt was wrong (it misclassified the patched model); the flaw surfaced by
    *executing* the code. The soundness of the abstraction is argued informally, not certified.
 3. **The Tamarin model is not executed.** `wpa2_handshake.spthy` was not verified in this environment
    (Tamarin not installed); its correctness is unverified and is labeled as such.
 4. **Reconstruction, not new knowledge.** The verification confirms a known 2017 result. It is a
    correct and instructive formal-verification exercise, not a discovery.

### Meta (cross-cutting)

 1. **Single author, single environment, no independent replication.**
 2. **Breadth at the expense of depth.** A research master's thesis goes *very* deep on a narrow problem;
    this repository is broad and applied. They are different profiles.
 3. **Self-assessment bias.** This very document is subject to the conflict of interest of the opening point.

---

## What it is, and what it is not (honest verdict)

**It is:** a full-stack security portfolio with three-plus-one layers (operational, theoretical,
empirical, formal), internally coherent, with graduate-level analysis, correctly cited primary
literature, reproducible measurements and an executed formal verification. It holds up against the
theoretical and methodological component of a good master's course, and is well above the bar for a
security-analyst portfolio.

**It is not:** peer-reviewed research. Missing - and disclosed - are real large-scale empirical data,
complete machine-checked proofs, and above all **independent external review**. The first two are
fillable in the lab with additional work (paths indicated in the respective READMEs); the third is not:
it requires a community of peers, which a repository cannot self-generate.

---

## How a reviewer can verify (reproducibility)

The quantitative and formal claims should not be taken on trust. They are independently verifiable by
re-running the code (Python 3 stdlib only, deterministic):

```Bash
python3 EVALUATION/exp01-detection-base-rate/generate_and_evaluate.py   # base-rate fallacy
python3 EVALUATION/exp02-password-entropy/guessing_entropy.py           # entropy/guessing
python3 FORMAL-MODELS/wpa2-4way-handshake/handshake_model_checker.py    # KRACK counterexample
python3 FORMAL-MODELS/wpa2-4way-handshake/inductive_verification.py     # unbounded proof of the fix
```

Every execution reproduces exactly the values reported in the respective `results.md`. The citations
should be verified against the primary sources listed in `REFERENCES.en.md`. This is the form of
verifiability a repository can offer as a partial substitute for trust; full peer review remains an
external step, here declared missing.
