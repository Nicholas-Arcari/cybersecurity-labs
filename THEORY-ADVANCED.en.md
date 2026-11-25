> **English** | [Italiano](THEORY-ADVANCED.md)

# Advanced Theory - Provable Security, Authentication, Information Flow

> - **Level:** Graduate (rigorous theory chapter: definitions, theorems, proofs).
> - **Purpose:** Bring the repository's theoretical apparatus to the level of a cryptography and formal-
>   methods textbook, filling what the per-module `THEORETICAL-FOUNDATIONS` treat conceptually: game-based
>   security definitions, proofs by reduction, the hybrid argument, the authentication hierarchy,
>   non-interference.
> - **Prerequisites:** basic algebra and probability, notions of complexity (PPT), the foundations of
>   modules 03, 04, 06, 07, 08, 10.
> - **Conventions:** `[Author Year]` notation to `REFERENCES.en.md`. Mathematics in plain text and code
>   blocks. `negl` = negligible function; `Adv` = adversary advantage; `<-$` = uniform sampling;
>   `PPT` = probabilistic polynomial-time.

---

## Contents

- Part I - Foundations of Provable Security (game-based definitions, reductions, hybrids)
- Part II - Concrete security of the offline attack: the Guessing Theorem (with proof)
- Part III - Authentication in protocols: Lowe's hierarchy and KRACK
- Part IV - Access control and non-interference

---

## Part I - Foundations of Provable Security

Provable security defines security relative to an **adversary model** and proves it by **reduction** to a
problem believed hard. This part fixes the language.

### I.1 Computational model and negligibility

**Definition I.1 (negligible function).** `mu: N -> R+` is negligible if for every polynomial `p` there
exists `N` such that `mu(n) < 1/p(n)` for all `n > N`. Written `mu(n) = negl(n)`. Intuition: it decreases
faster than the inverse of every polynomial.

**Definition I.2 (PPT adversary).** An adversary is a probabilistic algorithm terminating in polynomial
time in the security parameter `n` (typically the key length). "Asymptotic" security quantifies over all
PPT adversaries; "concrete" security (I.7) fixes explicit resources.

### I.2 Computational indistinguishability

**Definition I.3 (indistinguishability, [Goldwasser & Micali 1984]).** Two distribution ensembles
`X = {X_n}` and `Y = {Y_n}` are computationally indistinguishable, `X ~c Y`, if for every PPT
distinguisher `D`:

```
Adv_{X,Y}(D) := | Pr[ D(1^n, X_n) = 1 ] - Pr[ D(1^n, Y_n) = 1 ] |  =  negl(n).
```

This is the central notion: "secure" means "indistinguishable from an ideal" (a random function, an
encryption of zeros, etc.).

### I.3 Game-based definitions

Security properties are expressed as **games** between a challenger and the adversary; security is a
bound on the advantage.

**Definition I.4 (PRF - Pseudorandom Function).** Let `F: {0,1}^k x {0,1}^m -> {0,1}^n`. For a
distinguisher `D` with oracle access, the PRF advantage is:

```
Adv^{prf}_F(D) := | Pr[ K <-$ {0,1}^k : D^{F_K(.)} = 1 ]  -  Pr[ f <-$ Func(m,n) : D^{f(.)} = 1 ] |
```

where `Func(m,n)` is the set of all functions from `{0,1}^m` to `{0,1}^n`. `F` is a PRF if
`Adv^{prf}_F(D) = negl` for every PPT `D`. PRFs are the building blocks of MACs, ciphers, KDFs.

**Definition I.5 (IND-CPA, encryption).** In the left-or-right game, the challenger picks
`b <-$ {0,1}` and a key `K`; the adversary `A` submits equal-length pairs `(m_0, m_1)` and receives
`Enc_K(m_b)`; finally it outputs `b'`. The advantage is:

```
Adv^{ind-cpa}_{Enc}(A) := | 2 * Pr[ b' = b ] - 1 |.
```

`Enc` is IND-CPA secure if the advantage is `negl` for every PPT `A`. It implies the ciphertext reveals
nothing about the message (semantics).

**Definition I.6 (EUF-CMA, message authentication).** For a MAC `Mac_K`, the adversary has access to a
tagging oracle on chosen messages and wins if it produces `(m*, t*)` with `Vrfy_K(m*, t*) = 1` and `m*`
never queried. `Mac` is EUF-CMA (existential unforgeability under chosen-message attack) secure if

```
Adv^{euf-cma}_{Mac}(A) := Pr[ A wins ]  =  negl.
```

### I.4 The reduction method

To prove that a scheme `Pi` is secure **assuming** a primitive `P` is, one argues by contraposition: from
an adversary `A` breaking `Pi` one builds an adversary `B` breaking `P`, with related advantages. If `P`
is secure (`Adv(B) = negl`), then `Adv(A) = negl`.

**Theorem I.1 (a PRF is a secure MAC).** If `F` is a PRF, then `Mac_K(m) := F_K(m)` is EUF-CMA secure,
and for every adversary `A` making `q` queries there exists `B` (PPT, with roughly the same resources)
such that

```
Adv^{euf-cma}_{Mac}(A)  <=  Adv^{prf}_F(B)  +  2^{-n}.
```

*Proof (reduction).* `B` has an oracle `O` (either `F_K` or a random function `f`) and simulates the
EUF-CMA game for `A`: it answers every tag query `m_i` with `O(m_i)`. When `A` outputs `(m*, t*)` with
`m*` fresh, `B` queries `O(m*)` and outputs 1 iff `t* = O(m*)`.
- If `O = F_K`, `B` perfectly simulates the real MAC, so `Pr[B=1 | O=F_K] = Pr[A wins]`.
- If `O = f` random, `f(m*)` is uniform and independent of everything `A` has seen (m* is fresh), so
  `Pr[t* = f(m*)] = 2^{-n}`, i.e. `Pr[B=1 | O=f] = 2^{-n}`.
By Definition I.4, `Adv^{prf}_F(B) = |Pr[B=1|F_K] - Pr[B=1|f]| = |Adv^{euf-cma}(A) - 2^{-n}|`, giving the
claim. ∎

This is the paradigm: the security of `Mac` is *reduced* to that of `F`. The same scheme underlies the use
of HMAC (used in the 4-way handshake MIC) and the PBKDF2 key derivation.

### I.5 The hybrid argument

To go from security on *one* object to security on *many*, one uses the **hybrid argument**: a sequence of
distributions `H_0, H_1, ..., H_q` is interposed, where `H_0` is the "all real" world and `H_q` the "all
ideal" one, with `H_{i-1}` and `H_i` differing in a single element.

**Lemma I.2 (hybrid / telescoping).** If every adjacent pair is indistinguishable with advantage
`<= eps`, then `H_0` and `H_q` are indistinguishable with advantage `<= q * eps`. *Proof.* By the triangle
inequality on advantages:

```
|Pr[D(H_0)=1] - Pr[D(H_q)=1]|  <=  sum_{i=1}^{q} |Pr[D(H_{i-1})=1] - Pr[D(H_i)=1]|  <=  q * eps.  ∎
```

It is the tool by which, e.g., single-message IND-CPA security implies multi-message security, with a loss
linear in the number of ciphertexts.

### I.6 The Random Oracle Model

**Definition I.7 (ROM, [Bellare & Rogaway 1993]).** In the Random Oracle Model, a hash function `H` is
modeled as an oracle that, on each new input, returns an independent uniform value (consistent on
repeats). ROM proofs are efficient and expressive; the ROM is a *heuristic*: [Canetti et al. 1998] exhibit
schemes secure in the ROM but insecure under every concrete instantiation of `H`. It is used, disclosed,
in Part II.

### I.7 Concrete security

**Definition I.8 ((t, q, eps)-security, [Bellare et al. 1997]).** A scheme is `(t, q, eps)`-secure if
every adversary running in time `<= t` and making `<= q` queries has advantage `<= eps`. Concrete security
makes the resource-advantage link explicit, essential for choosing real parameters (key lengths, KDF
iterations). It is the register in which Part II works.

---

## Part II - Concrete Security of the Offline Attack: the Guessing Theorem

We connect the Part I formalism to the offline attack on WPA2-PSK (module 06) and to the empirical
measurement (`EVALUATION/exp02`). The result is a **tight, proven concrete-security bound** whose value
coincides with the guessing curve computed in the experiment.

### II.1 The offline guessing game

A captured handshake yields a *verification predicate* `V(w)` that equals 1 iff the candidate passphrase
`w` is the correct one (via MIC recomputation). We model the KDF/MIC as a random oracle `H` (Definition
I.7): the only way to evaluate `V(w)` is to query `H` on `w` (and the public handshake values). The real
passphrase `W` is drawn from a known distribution `D` over passwords, with ordered probabilities
`p_1 >= p_2 >= ... >= p_N`.

**Definition II.1 (offline guessing adversary).** `A` makes a set of distinct queries
`Q = {w_1, ..., w_q}` to `H` and wins iff `W in Q`. The dominant resource is `q` (number of verifications).

### II.2 The theorem and its proof

**Theorem II.1 (tight bound on offline guessing).** In the ROM, every adversary making at most `q` distinct
queries recovers `W ~ D` with probability at most

```
G_q(D) := sum_{i=1}^{q} p_i        (sum of the q largest probabilities),
```

and the bound is tight: the optimal strategy (querying the `q` most probable passwords) achieves it.

*Proof.*
(Upper bound) Since `H` is a random oracle, for every candidate `w` not yet queried the value `H(w, .)` is
uniform and independent; hence no information about `W` is obtained without querying `w`, and the only way
to verify `w` is to include it in `Q`. With `|Q| <= q` distinct candidates, the winning event is `W in Q`,
of probability `Pr[W in Q] = sum_{w in Q} Pr[W = w]`. This sum of `q` terms chosen from `{p_1, ..., p_N}`
is maximized by taking the `q` largest, so `Pr[W in Q] <= sum_{i=1}^{q} p_i = G_q(D)`.
(Tightness) The strategy `Q* = {i : 1 <= i <= q}` (the `q` most probable passwords) gives exactly
`Pr[W in Q*] = G_q(D)`. ∎

**Remark (adaptivity does not help).** Since the oracle outputs are independent and structureless, the
order and adaptivity of the queries do not change the tested set: the bound holds for adaptive adversaries
too. This isolates the fact that the only lever is *which* `q` candidates to test, not *how*.

### II.3 Corollaries: entropy, min-entropy, guessing entropy

**Corollary II.2 (min-entropy = resistance to one query).** For `q = 1`, `G_1 = p_1 = 2^{-H_inf(D)}` where
`H_inf(D) = -log2 p_1` is the min-entropy. The probability of success on the first attempt is exactly
`2^{-H_inf}`, not `2^{-H_Shannon}`. This formalizes module 04, section 3.3, and module 06, sections
3.2/4.2: **resistance is governed by the min-entropy (and in general by the curve `G_q`), not by the
Shannon entropy.**

**Corollary II.3 (expected guessing entropy, [Massey 1994]).** The expected number of attempts of the
optimal strategy is `G(D) = sum_{i>=1} i * p_i`. This is the mean guessing entropy; the empirical part
shows (consistent with [Bonneau 2012]) that the mean is tail-dominated, so `G_q` is the operational
metric, not `G`.

### II.4 Effect of key stretching: query-hardness vs time-hardness

PBKDF2 with `c` iterations (module 06, section 3.2) does not change `D` or `G_q`: the *probability* of
success after `q` verifications is invariant. What changes is the **time cost** per query.

**Proposition II.4 (time-query trade-off).** If each evaluation of `V` requires `c` evaluations of the
underlying primitive of cost `t_H`, then every adversary reaching success probability `G_q` spends time
`t >= q * c * t_H`. Hence, for a fixed target probability, the cost grows linearly in `c`.

*Proof.* By Theorem II.1, reaching probability `G_q` requires `q` distinct queries; each costs `c * t_H`;
the queries are the dominant resource. ∎

**Interpretation.** Key stretching buys **time-hardness**, not **query-hardness**: it does not reduce the
probability per number of attempts (which depends only on the passphrase distribution) but raises the time
per attempt. Effective defense therefore acts on *both*: increasing `H_inf(D)` (high-entropy passphrase,
which lowers `G_q`) and increasing `c` (which raises the time). Memory-hard functions (scrypt, Argon2,
module 04) extend the argument to silicon area, not just time.

### II.5 Connection with the executed experiment

Theorem II.1 is not abstract: `G_q(D)` is **exactly** the guessing curve computed in `EVALUATION/exp02`
for the Zipf distribution. The executed measurement (`G_1000 = 0.52`, i.e. 52% of accounts fall in
`q = 1000` queries) is a numerical instance of the tight bound proven here. Theory and measurement coincide
by construction: the bound is the curve, and the curve was computed.

---

## Part III - Authentication in Protocols: Lowe's Hierarchy and KRACK

The module 06 foundations and the formal verification (`FORMAL-MODELS/`) use the word "freshness". Here it
is placed in the formal taxonomy of authentication properties of [Lowe 1997], and it is shown precisely
which level KRACK breaks.

### III.1 Correspondence assertions

Protocol events are annotated with `begin(A, B, d)` (principal `A` starts a session with `B` and data `d`)
and `end(B, A, d)` (`B` completes believing it spoke with `A` about `d`). Authentication properties are
**correspondence assertions** between these events, of increasing strength.

### III.2 Lowe's hierarchy

From weakest to strongest [Lowe 1997]:

1. **Aliveness:** if `B` completes `end(B, A, -)`, then `A` ran the protocol *at some point* (not
   necessarily with `B`, not necessarily recently).
2. **Weak agreement:** `A` ran the protocol *apparently with B* (but the data may differ).
3. **Non-injective agreement (on `d`):** `A` ran `begin(A, B, d)` with the *same data* `d`; but the
   *same* run of `A` may correspond to *multiple* completions of `B`.
4. **Injective agreement (on `d`):** there is an **injective** correspondence between `B`'s completions
   and `A`'s runs: every `end(B, A, d)` is paired with a *distinct* `begin(A, B, d)`.

**Injectivity = absence of replay.** Injective agreement is precisely the property that denies replay: a
single `begin` cannot justify two `end`s. The *freshness* of module 06 is, formally, the injectivity clause.

### III.3 KRACK as loss of injective agreement

In the 4-way handshake, the supplicant's installation of the PTK is an `end` event that should
injectively correspond to a `begin` of the authenticator (the *fresh* sending of Message 3). The KRACK
attack replays the same Message 3: **a single `begin` is paired with two `end`s (two installations)**,
violating injectivity while preserving non-injective agreement (the data matches) and aliveness.

This is the exact bridge with the verification in `FORMAL-MODELS/`: the invariant verified there,
`n_install <= 1` (the PTK is installed at most once), is the operational encoding of **injective
agreement** on the installation event. The model checker's counterexample is an injectivity violation; the
inductive-invariant proof of the patched model is a proof of injectivity. Lowe's hierarchy provides the
formal name of the property that modules 06 and FORMAL-MODELS treat.

### III.4 Symbolic vs computational model

The verification in `FORMAL-MODELS/` is in the **symbolic model** (Dolev-Yao): the primitives are perfect
terms (a MIC is unforgeable by assumption), and one reasons about message structure and state. The
**computational model** treats primitives as algorithms with PPT adversaries and advantages (Part I). The
two are linked by **computational soundness** results [Abadi & Rogaway 2002]: under appropriate
assumptions, symbolic security implies computational security. The choice of the symbolic model for KRACK
is correct and deliberate: KRACK is a *state/structure* defect, independent of the strength of the
primitives (which in our model are assumed perfect and the attack exists nonetheless), exactly the regime
in which symbolic analysis is most suitable.

---

## Part IV - Access Control and Non-Interference

Modules 08 (hardening, access control) and 10 (cloud/tenant isolation), and the covert channels of module
07, invoke properties formalized here.

### IV.1 The information-flow lattice

**Definition IV.1 ([Denning 1976]).** A flow model is a tuple `(S, O, L, <=, join)` where `L` is a set of
security classes partially ordered by `<=` forming a **lattice** (`join` and `meet` exist). A flow from an
object of class `a` to one of class `b` is permitted iff `a <= b`. The policy is the lattice structure;
security is the absence of flows violating `<=`.

### IV.2 Bell-LaPadula and Biba

**Definition IV.2 (BLP, confidentiality, [Bell & LaPadula 1976]).** With subject clearances and object
classifications in the lattice:
- *Simple security property (no read up):* a subject of level `l_s` may read an object of level `l_o` only
  if `l_o <= l_s`.
- *Star property (no write down):* it may write `l_o` only if `l_s <= l_o`.

**Proposition IV.3.** Under BLP, no sequence of permitted operations creates a flow from a `High` object
to a `Low` subject. *Proof (sketch).* Every read respects `l_o <= l_s` and every write `l_s <= l_o`;
composing, information can only rise in the lattice, never from `High` to `Low` (by antisymmetry of `<=`). ∎

**Definition IV.4 (Biba, integrity).** Dual of BLP with the order reversed: *no read down, no write up*.
It protects integrity (a high-integrity subject does not read low-integrity data, nor is low-integrity data
written into high-integrity objects). It is the formal model behind log integrity (module 08) and evidence
integrity (module 09).

### IV.3 Non-interference

BLP/Biba are *syntactic* properties (about operations). Non-interference is a *semantic* property (about
observable behaviors), stronger because it also captures implicit channels.

**Definition IV.5 (non-interference, [Goguen & Meseguer 1982]).** Let the system be a deterministic
machine over command sequences, with users partitioned into `High` and `Low`. Let `purge_Low(w)` be the
sequence `w` with all `High` commands removed. The system is **non-interfering** if for every sequence `w`,
the observation of `Low` users alone after `w` equals the observation after `purge_Low(w)`:

```
obs_Low( run(w) )  =  obs_Low( run( purge_Low(w) ) )   for every w.
```

Intuition: what `High` users do has *no* observable effect on `Low` users. The violation of this equality
*is* a channel (explicit or covert) from `High` to `Low`.

### IV.4 Applications to the modules

- **Covert channels and exfiltration (module 07, [Lampson 1973]).** A covert channel is precisely a
  non-interference violation: a `High` activity (sensitive data) alters a `Low` observation (a timing, a
  DNS volume). The "allow and inspect" defense aims to reduce the channel's bandwidth; perfect
  non-interference (zero bandwidth) is in general unreachable ([Lampson 1973], module 07, section 6), which
  formalizes the limit declared in that module.
- **Tenant isolation (module 10, [Ristenpart et al. 2009]).** Multi-tenant isolation is the requirement of
  non-interference between distinct tenants. Cross-VM side-channels are its demonstrated violation: the
  activity of a `High` tenant (a key in use) alters an observation of the other `Low` tenant (cache
  latency). This explains, in formal language, why *logical* isolation does not imply *physical*
  non-interference.
- **Confidentiality and integrity (modules 08, 09).** BLP and Biba provide the syntactic models; immutable
  logging (module 07/09) is an instance of Biba-style integrity (the logs are not writable by the attacker
  who generates them), and its effectiveness against anti-forensics is an integrity statement.

---

## Synthesis

This chapter brought the theoretical apparatus to the graduate register along four axes: (I) the game-based
definitions, reductions and hybrid argument that constitute the provable-security method; (II) a *proven,
tight* concrete-security theorem on the offline attack, whose bound coincides with the measurement executed
in `EVALUATION/exp02` and which formalizes WPA2 passphrase resistance (module 06); (III) Lowe's
authentication hierarchy, which gives the formal name ("injective agreement") to freshness and connects the
verification in `FORMAL-MODELS/` exactly to KRACK; (IV) the lattice models and non-interference, which
formalize access control, covert channels (module 07) and tenant isolation (module 10). The per-module
`THEORETICAL-FOUNDATIONS` remain the conceptual and applied level; this document is their rigorous
counterpart.

**Level honesty.** The proofs here are rigorous but in the register of a textbook (definition - theorem -
proof or proof-sketch), not machine-checked (with the exception of the protocol verification in
`FORMAL-MODELS/`, which is executed). Theorem II.1 and Proposition II.4 are original in formulation but
standard in content (guessing in the ROM); the cited results (Theorem I.1, Lemma I.2, Prop. IV.3) are
classical and reported with proof or sketch. See `SELF-ASSESSMENT.en.md` for the threats to validity.

---

## References

Subset of `REFERENCES.en.md` relevant:

- [Goldwasser & Micali 1984], [Goldreich 2001], [Katz & Lindell 2020] - indistinguishability, PRF, reductions.
- [Bellare et al. 1997], [Shoup 2004] - concrete security, games.
- [Bellare & Rogaway 1993], [Canetti et al. 1998] - Random Oracle Model and its limits.
- [Massey 1994], [Bonneau 2012] - guessing entropy (Part II; see also EVALUATION/exp02).
- [Kaliski 2000], [Percival 2009], [Biryukov et al. 2016] - PBKDF2, scrypt, Argon2 (Part II.4).
- [Lowe 1997], [Abadi & Rogaway 2002] - authentication hierarchy, symbolic vs computational (Part III).
- [Vanhoef & Piessens 2017] - KRACK (Part III; see FORMAL-MODELS/).
- [Denning 1976], [Bell & LaPadula 1976], [Biba 1977], [Goguen & Meseguer 1982] - flow, BLP/Biba,
  non-interference (Part IV).
- [Lampson 1973], [Ristenpart et al. 2009] - covert channels, co-residency (Part IV).

---

> **Note:** Document for educational purposes, at graduate level, complementary to the per-module
> `THEORETICAL-FOUNDATIONS` (conceptual/applied) and to the executed verification in `FORMAL-MODELS/`. The
> citations refer to real and verifiable sources in `REFERENCES.en.md`.
