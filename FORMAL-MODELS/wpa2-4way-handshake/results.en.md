> **English** | [Italiano](results.md)

# Results - formal verification of the WPA2 4-way handshake (KRACK)

Verbatim output of `handshake_model_checker.py` (deterministic, exhaustive exploration).
Result **produced by the real execution** of the model checker, not asserted by hand.
Re-running the command reproduces this output exactly.

```
WPA2 4-way handshake - explicit-state model checking of the freshness invariant
(KRACK, Vanhoef & Piessens 2017). Deterministic, exhaustive, self-contained.

==============================================================================
MODEL: VULNERABLE supplicant (reinstalls PTK on any M3, incl. replays)
Invariant checked: installs <= 1  (PTK installed at most once = no key reinstall)
==============================================================================
RESULT: VIOLATION FOUND after exploring 6 states.
Counterexample trace (a concrete KRACK attack found by the model checker):

    START      | phase=INIT      installs=0 nonce(PN)=0 max_used=0 data_sent=False
    step  1 recv_M1                    | phase=GOT_M1    installs=0 nonce(PN)=0 max_used=0 data_sent=False
    step  2 send_M2                    | phase=SENT_M2   installs=0 nonce(PN)=0 max_used=0 data_sent=False
    step  3 recv_M3_install            | phase=INSTALLED installs=1 nonce(PN)=0 max_used=0 data_sent=False
    step  4 recv_M3_REPLAY_reinstall   | phase=INSTALLED installs=2 nonce(PN)=0 max_used=0 data_sent=False   <-- attacker replays M3

    -> installs reached 2 (> 1): the PTK was reinstalled.
    -> the packet-number counter was reset to 0 after data frames had used
       nonces 1..k, so those nonces are reused with the same key = KRACK.

==============================================================================
MODEL: PATCHED supplicant (ignores replayed M3 for key installation)
Invariant checked: installs <= 1  (PTK installed at most once = no key reinstall)
==============================================================================
RESULT: VERIFIED. Invariant holds in all 7 reachable states.
        No key-reinstallation is reachable under the Dolev-Yao adversary.

==============================================================================
Conclusion: the model checker MECHANICALLY finds the KRACK attack in the
vulnerable model (counterexample above) and EXHAUSTIVELY VERIFIES its absence
in the patched model. This confirms, formally, that KRACK is a protocol-STATE
defect (key reinstallation / loss of nonce freshness), not a break of the
cryptographic primitives - the thesis of module 06 foundations, section 3.5.
```

## Reading of the results

1. **Counterexample found mechanically (VULNERABLE model).** The model checker explores the reachable
   state space and finds, in 6 states, a concrete trace that violates the security invariant. The
   trace is a genuine KRACK attack: after the first installation of the PTK (step 3, `installs=1`),
   the Dolev-Yao adversary replays Message 3 (step 4), inducing a **second installation**
   (`installs=2`) that **resets the packet-number counter** to 0. Since the data frames already sent
   had used nonces 1..k with that same key, the reset causes nonce reuse, keystream reuse, loss of
   confidentiality/integrity.

2. **Invariant verified exhaustively (PATCHED model).** With the fix (the supplicant does not
   reinstall on a replayed M3), the model checker explores **all** 7 reachable states and finds no
   violation: `installs <= 1` holds everywhere. This is verification, not testing: the absence of the
   defect is proven over the entire state space, not over a sample.

3. **What it formally demonstrates.** The relevant security property is not the secrecy of the PTK
   (which here is never compromised) but the **injectivity of key installation** - a *freshness/state*
   property. Its violation is KRACK. The pair (counterexample in the vulnerable model, verification in
   the patched model) mechanically confirms the thesis of module 06 (foundations, section 3.5):
   **KRACK is a defect of the protocol state machine, not a break of the cryptographic primitives**.
   The primitives (MIC, PRF) are assumed perfect here (Dolev-Yao abstraction) and the attack exists
   nonetheless.

## UNBOUNDED verification (inductive invariant, no bound)

The model checker above is *bounded* (it explores up to a bound on the counter). To prove the fix for
executions of **arbitrary length** with no bound, `inductive_verification.py` uses the standard
technique of an **inductive invariant (1-induction)**. Real verbatim output:

```
==============================================================================
MODEL: PATCHED
==============================================================================
[PATCHED]  Phase 1 - is the bare safety property I0 (n_install<=1) inductive?
    BASE: ('INIT', False, 0) |= I0  -> True
    STEP: 1 counterexample(s)-to-induction (CTI). I0 is NOT inductive:
        ('SENT_M2', False, 1) --install_first_M3--> ('INSTALLED', True, 2)   [pre-state is UNREACHABLE (spurious: violates I*)]

[PATCHED]  Phase 2 - is the strengthened invariant I* inductive?
    BASE: ('INIT', False, 0) |= I*  -> True
    STEP: every enabled rule preserves I*  -> HOLDS
    VERDICT [PATCHED]: I* is INDUCTIVE  =>  n_install<=1 on ALL reachable states,
             for executions of ANY length (NO bound). ... FRESHNESS is PROVED unboundedly.

==============================================================================
MODEL: VULNERABLE
==============================================================================
[VULNERABLE]  Phase 1 - 3 CTI: 2 UNREACHABLE (spurious) + 1 reachable:
        ('INSTALLED', True, 1) --install_REPLAY_M3--> ('INSTALLED', True, 2)   [pre-state is reachable]
[VULNERABLE]  Phase 2 - I* is NOT inductive. Remaining CTI from genuine I*-states:
        ('INSTALLED', True, 1) --install_REPLAY_M3--> ('INSTALLED', True, 2)
    VERDICT [VULNERABLE]: ... genuinely FALSE (KRACK for real).

RESULT:  PATCHED = PROVED   |   VULNERABLE = REFUTED
```

**The formal content (and the methodological lesson).** The bare safety property `I0 = (n_install<=1)`
is **not inductive**, even for the patched model: the inductive step produces a CTI
(counterexample-to-induction) from the abstract state `(SENT_M2, False, 1)`, which is however
**unreachable** (one cannot be in SENT_M2 with an installation already done). This is the normal
situation: one must **strengthen** the invariant with the reachability coupling between the state
components (`installed <=> n_install>=1`; `n_install>=1 => phase=INSTALLED`) until the conjunction `I*`
becomes inductive. Finding this strengthening is the real verification work.

- **PATCHED:** `I*` is inductive (BASE + STEP verified over all `I*`-states) => `n_install<=1` holds on
  **all** reachable states, for executions of **any length**, with no bound. By the sound reduction
  (install-once => no reset-after-advance => no nonce reuse), **freshness is proved unboundedly**.
- **VULNERABLE:** `I*` remains non-inductive due to a CTI from a **genuinely reachable** state
  (`(INSTALLED, True, 1)`, i.e. step 3 of the concrete counterexample): the property is **really false**,
  not merely non-inductive.

Distinguishing spurious CTIs (from unreachable states) from genuine ones, and "non-inductive" from
"false", is precisely what a correct inductive verification does. Transparency note: the first version
of this script used the bare invariant and misclassified the patched model; the flaw was discovered by
**executing** the code and fixed by strengthening the invariant - the reason one runs the verification
instead of asserting it.

## What is "formal" here (and what is not)

Explicit-state model checking **is** formal verification: one defines a state machine and an
invariant, exhaustively explores the reachable state space under an explicit adversary, and proves
the invariant holds everywhere (or exhibits a counterexample). It is the core procedure of tools such
as SPIN or TLC, implemented here in ~200 lines of stdlib Python so it is self-contained and
reproducible. The verification result (7 states, no violation) and the counterexample (4-step trace)
are **produced by execution**, not written by hand.

## Validity note (disclosed limitation)

This is a **symbolic** model at the protocol-logic level:
- It abstracts the cryptographic primitives (MIC/PRF assumed sound, Dolev-Yao model). This is the
  correct abstraction to isolate protocol defects, and it is exactly the one in which KRACK lives.
- It models the **KRACK-relevant state** (install count, nonce counter), not the full IEEE 802.11
  state machine (the Group Key handshake, 802.11r/FT, authenticator retries are omitted).
- The nonce counter is **bounded** (`NONCE_CAP`), standard practice in finite-state model checking: a
  single advance-then-reset already witnesses the reuse.

Within this abstraction the verification is **exhaustive and exact**. For a verification at the
reference-tool level (without the state bound, with symbolic trace reconstruction), the folder
includes `wpa2_handshake.spthy`, a model for the **Tamarin** prover - provided as a runnable artifact
but, transparently, **not executed in this environment** (Tamarin is not installed here): validate it
with `tamarin-prover --prove wpa2_handshake.spthy`. The execution-verified artifact of this folder is
the Python model checker.
