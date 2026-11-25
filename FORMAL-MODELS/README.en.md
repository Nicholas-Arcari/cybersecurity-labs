> **English** | [Italiano](README.md)

# Formal Models - Protocol Verification

> - **Level:** Formal verification (formal methods applied to a security protocol)
> - **Purpose:** Provide an executable, verified formal model of a protocol, as a research-level artifact complementing the theory (`THEORETICAL-FOUNDATIONS`) and the empirical measurement (`EVALUATION`).
> - **Prerequisites:** Python 3 (standard library only). For the optional Tamarin model: the Tamarin prover.

---

## Why this folder exists

The `THEORETICAL-FOUNDATIONS.md` argue the security properties; `EVALUATION/` *measures* them
empirically. This folder adds the third method of academic rigor: the **formal verification** of a
protocol, that is, the exhaustive demonstration - not by testing, but over the entire state space -
that a security property holds (or the mechanical exhibition of a counterexample when it does not).

The case study is the **WPA2 4-way handshake** and its **KRACK** vulnerability
(Key Reinstallation Attack, [Vanhoef & Piessens 2017]). It is the natural complement of module 06,
section 3.5, where it is argued - in words - that KRACK is a defect of the protocol *state machine*
and not of the cryptographic primitives. Here that thesis is **mechanically demonstrated**.

---

## Folder Structure

```
FORMAL-MODELS/
+-- README.md                          # this file
|
+-- wpa2-4way-handshake/
    +-- handshake_model_checker.py     # BOUNDED explicit-state model checker (EXECUTED): finds KRACK
    +-- inductive_verification.py      # UNBOUNDED verification via inductive invariant (EXECUTED): proves the fix
    +-- results.md                     # real verbatim output of BOTH + reading
    +-- wpa2_handshake.spthy           # Tamarin reference model (NOT executed here; for the tool)
```

Two executed, complementary artifacts that together form a formal verification result: the **bounded
model checker** *finds* the bug (concrete KRACK counterexample); the **inductive invariant** *proves*
its absence in the patched model for executions of arbitrary length (no bound).

---

## Result (produced by execution)

The model checker defines the state machine of the WPA2 supplicant under a Dolev-Yao adversary that
can **replay Message 3**, and verifies the *freshness* invariant:

> **The PTK is installed at most once per handshake** (equivalently: the data-frame packet-number
> counter is never reset after being advanced). Its violation IS KRACK.

Two models, exhaustively verified:

- **VULNERABLE** (the supplicant reinstalls the PTK on every M3, including a replay): the model checker
  **finds a counterexample** in 6 states - a concrete 4-step trace in which the replay of M3 induces a
  second installation (`installs=2`) that resets the counter, nonce reuse, keystream reuse. It is
  KRACK, found mechanically.
- **PATCHED** (the supplicant does not reinstall on a replayed M3): the model checker **verifies** the
  invariant over all 7 reachable states - no reinstallation is reachable.

This formally demonstrates that KRACK lives in the state logic of the protocol: the primitives (MIC,
PRF) are assumed **perfect** (Dolev-Yao) and the attack exists nonetheless; the fix (do not reinstall)
eliminates it. Verbatim output and full reading in
[`wpa2-4way-handshake/results.en.md`](wpa2-4way-handshake/results.en.md).

---

## Reproducibility

```Bash
# 1) BOUNDED model checker (executed) - finds the KRACK counterexample - < 1 s
python3 wpa2-4way-handshake/handshake_model_checker.py

# 2) UNBOUNDED verification via inductive invariant (executed) - proves the fix, no bound - < 1 s
python3 wpa2-4way-handshake/inductive_verification.py

# 3) Tamarin reference model (requires the Tamarin prover, NOT included nor executed here)
tamarin-prover --prove wpa2-4way-handshake/wpa2_handshake.spthy
```

The Python model checker is deterministic and exhaustive: every re-run reproduces `results.md` exactly.

---

## Honest methodological note (scope and integrity discipline)

- **What is "formal" here.** Explicit-state model checking is formal verification in full (exhaustive
  exploration + invariant), the same core as SPIN/TLC, here in stdlib Python to be self-contained. The
  result and the counterexample are **produced by execution**, not asserted.
- **Disclosed abstraction.** Symbolic model at the protocol-logic level: abstracted primitives
  (Dolev-Yao), only the KRACK-relevant state, bounded nonce counter (standard in finite-state model
  checking). Within the abstraction, the verification is exhaustive and exact. It is not a proof at
  the bit level nor of the full 802.11 state machine.
- **The Tamarin model was not executed here.** Tamarin is not installed in this environment:
  `wpa2_handshake.spthy` is provided as a runnable artifact to validate with the real tool, and is
  labeled as such in the file. I do not pass off as verified what I have not executed - the
  execution-verified artifact is the Python model checker.
- **Bounded vs unbounded (addressed).** The "only up to depth k" limit of the bounded model checker is
  overcome by `inductive_verification.py`, which proves the fix for executions of arbitrary length via
  an inductive invariant. What remains is the symbolic-abstraction limit (Dolev-Yao); a mechanization
  with a dedicated prover's soundness/completeness guarantees requires Tamarin/ProVerif executed (the
  `.spthy` model is ready but not executed here).
- **Out of scope (disclosed).** External peer review remains beyond the reach of a repository: see the
  adversarial self-assessment in `../SELF-ASSESSMENT.md`, which honestly addresses its *function*
  (finding the flaws) without claiming its *credential*.

---

## References

- [Vanhoef & Piessens 2017] - KRACK (Key Reinstallation Attacks), the modeled phenomenon.
- [Dolev & Yao 1983] - the adopted network adversary model.
- Related theoretical foundations in
  `../06-wireless-security/THEORETICAL-FOUNDATIONS.en.md` (section 3.3 freshness, 3.5 KRACK).
  Bibliographic details in `../REFERENCES.en.md`.
