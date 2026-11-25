> **English** | [Italiano](THEORETICAL-FOUNDATIONS.md)

# Theoretical foundations - module 08: defense & hardening

> - **Level:** Academic analysis (theoretical complement to the operational READMEs of the module)
> - **Purpose:** Quantitatively derive the base-rate problem of detection, ground anomaly detection and deception, and formalize hardening as attack surface reduction.
> - **Prerequisites:** Operational READMEs of module 08 (DEF- findings); notions of Bayesian probability, detection theory and access control.

---

## Abstract

This document provides the quantitative foundation of defense. The central result is the Bayesian derivation of the **base-rate fallacy** [Axelsson 2000]: it is shown that, given the very low base rate of malicious events, even a very accurate detector produces a poor positive predictive value, which explains why false positives dominate the operation of the SIEM. From here the value of **deception** [as a countermeasure with a structurally null false-positive rate] and of **anomaly detection** [Denning 1987; Forrest et al. 1996] is motivated, with the limits of machine learning [Sommer & Paxson 2010]. Hardening is formalized as attack surface reduction [Manadhata & Wing 2011] and application of the principles of [Saltzer & Schroeder 1975]. The D3FEND framework provides the defensive taxonomy dual to ATT&CK.

---

## 1. The Defender model

The defender observes a stream of events `E` (logs, packets, calls) and must decide for each whether it is benign or malicious, with the objective of maximizing the detection of the malicious while minimizing false alarms, under a constraint of finite analysis resources. Formally it is a problem of **detection theory** with two types of error: false positive (alarm on a benign event) and false negative (malicious event not detected). The defender does not control the base rate of malicious events, which is structurally very low: it is this asymmetry, not the accuracy of the detector, that determines the difficulty (section 3.1).

---

## 2. Security properties at stake

- **Visibility:** precondition of every detection; without observability there is no detection. Centralized logging realizes it (module 07, section 3.4).
- **Effective detection:** maximize the predictive value of detection under the base-rate constraint (section 3.1).
- **Timely containment:** reduce to zero the time between detection and response for high-confidence threats (active response), accepting the risk of automation (section 4.2).
- **Minimal attack surface:** prevent at the root by reducing the attackable points [Manadhata & Wing 2011].

---

## 3. Theoretical foundations

### 3.1 The base-rate fallacy: bayesian derivation

[Axelsson 2000] applies Bayes's theorem to intrusion detection, obtaining the most important result of detection theory in security. Let `I` be the event "intrusion" and `A` the event "alarm". The relevant quantities are:

- `P(I)` = base rate of intrusions (prior probability that an event is malicious), typically **very low** (e.g. 1 in 100,000 or less);
- `P(A|I)` = true positive rate (sensitivity of the detector);
- `P(A|~I)` = false positive rate.

The operationally relevant quantity is the **positive predictive value**, that is, the probability that an alarm corresponds to a real intrusion:

```
                    P(A|I) P(I)
P(I|A) = ---------------------------------------
          P(A|I) P(I) + P(A|~I) P(~I)
```

The point of [Axelsson 2000] is that, when `P(I)` is very small, the term `P(A|~I) P(~I)` in the denominator dominates even for minuscule false positive rates, because `P(~I)` is close to 1. Numerical example: with `P(I) = 10^-5`, `P(A|I) = 1` (perfect detector on true positives) and an excellent false positive rate `P(A|~I) = 10^-3`:

```
P(I|A) = (1 x 10^-5) / (1 x 10^-5 + 10^-3 x (1 - 10^-5))
       ~ 10^-5 / (10^-5 + 10^-3)
       ~ 0.0099   (about 1%)
```

That is: **99% of the alarms are false**, even with an almost perfect detector. This is the theoretical foundation of the false-positive overload that afflicts every SOC, and the reason why the accuracy of the detector alone does not solve the problem: one must lower `P(A|~I)` by orders of magnitude, or raise the effective base rate by narrowing the domain (correlation, context).

### 3.2 Deception as evasion of the base-rate

Deception (honeypots, canary tokens) offers a theoretical way out of the base-rate fallacy. On a decoy resource, the legitimate activity is **zero by construction**: `P(~I | interaction) = 0`. Substituting into the formula of section 3.1, the positive predictive value becomes 1: every interaction with the decoy is, with certainty, malicious. Deception does not "improve" the detector, it changes the domain so that the base rate does not degrade the predictive value. It is the theoretical reason why a single canary token alert is worth, in confidence, many correlated SIEM alerts. The cost is coverage: the decoy detects only whoever touches it (section 6).

### 3.3 Anomaly detection: models and limits

[Denning 1987] grounds intrusion detection on the premise that malicious activity statistically deviates from normal behavior. [Forrest et al. 1996] realize it at the system level by modeling the "sense of self" of a process via the system call sequences: deviations from the learned profile flag anomalies. The theoretical limit is twofold: (i) the profile of normality is itself noisy and mutable, generating false positives (section 3.1); (ii) [Sommer & Paxson 2010] show that machine learning for intrusion detection suffers from peculiar challenges - the high cost of errors, the lack of labeled attack data, the difficulty of interpretation and the non-stationarity - that limit its effectiveness compared to other application domains. Behavioral detection is powerful but does not evade the triangle of false positives / false negatives / cost.

### 3.4 Hardening as surface reduction and design principles

Hardening is the systematic application of attack surface minimization [Manadhata & Wing 2011] (module 01, section 3.1) and of the principles of [Saltzer & Schroeder 1975]: fail-safe defaults (everything denied except explicit authorization), least privilege (minimal SUID, restricted RBAC, LAPS), economy of mechanism (fewer services, less surface), complete mediation (every access verified). Credential Guard and LAPS, in particular, are formalizable as the breaking of the transitivity of trust of module 07 (section 3.2): they reduce the attack graph by eliminating edges. Hardening acts upstream of detection: a removed edge is an attack path that will never exist, not an event to detect.

---

## 4. Quantitative analysis

> **Empirical validation:** the Bayesian derivation of the base-rate fallacy (section 3.1) is
> experimentally verified on measured data in [`../EVALUATION/exp01-detection-base-rate/`](../EVALUATION/exp01-detection-base-rate/results.en.md):
> a real detector on 1,000,000 labeled events shows the PPV collapse to 0.0023 at a base rate of
> `1e-5` (99.8% false alarms), with the analytical formula confirmed by resampling.

### 4.1 Correlation as raising of the effective base rate

Multi-source correlation (SIEM) is interpretable as a method to raise the effective base rate and therefore the predictive value. Requiring the coincidence of multiple independent events (scan + successful login + endpoint alert in the same window) defines a composite event whose `P(I | composite)` is much higher than that of the single events, because the fortuitous coincidence of independent benign events has low probability. Formally, if the benign events are approximately independent, `P(A_1 ~I) P(A_2 ~I) ...` decreases multiplicatively, lowering the denominator of the formula of section 3.1. It is the quantitative theoretical justification of why correlation (module 08, Splunk/ELK) reduces false positives where the single sensor fails.

### 4.2 The trade-off of response automation

Active response compresses the dwell time (module 07, section 4.1) to zero for high-confidence threats, but transfers the risk: an automated false positive causes immediate damage (self-block). The trade-off is quantifiable: automating is advantageous when the predictive value `P(I|A)` for the specific rule is sufficiently high (section 3.1) and the cost of the false positive is limited (timeout, whitelist). Low-predictive-value rules must remain in human triage. This is the theoretical reading of the operational principle of the READMEs: automate only the responses to deterministic and high-confidence detections.

---

## 5. Literature review

The central quantitative result is by [Axelsson 2000], who brought Bayes's theorem to the heart of the difficulty of intrusion detection. The foundations of anomaly detection are by [Denning 1987] and [Forrest et al. 1996]; the limits of applied machine learning are analyzed by [Sommer & Paxson 2010]. Hardening as surface reduction rests on [Manadhata & Wing 2011] and on the principles of [Saltzer & Schroeder 1975]; log integrity on [Biba 1977]. The reference offensive taxonomy is MITRE ATT&CK [Strom et al. 2020], with the defensive dual D3FEND. The Diamond Model [Caltagirone et al. 2013] provides the analytical frame for the threat intelligence produced by deception.

---

## 6. Limitations and open problems

1. **Irreducibility of the base-rate.** Since `P(I)` is structurally very low, no realistic improvement of the detector's accuracy eliminates the domain of false positives [Axelsson 2000]. Effective detection necessarily requires correlation, context or deception to circumvent the limit - not a better detector.

2. **Limited coverage of deception.** The null-false-positive property (section 3.2) is paid for in coverage: the decoy detects only whoever crosses it. The optimal placement of the decoys to maximize the probability of intercepting the attacker is an open optimization problem.

3. **Non-stationarity.** The profiles of normality (anomaly detection) and the correlation rules degrade as the environment changes [Sommer & Paxson 2010]; maintenance is a continuous cost, not a one-off investment. Automatic adaptation without introducing new false positives remains open.

---

## 7. Synthesis and connection to practice

The `DEF-` findings of the module instantiate this framework: SIEM detection (DEF-001/002) operates under the base-rate constraint of section 3.1, and the correlation documented in the READMEs is the raising of the effective base rate of section 4.1; deception (DEF-005/006) is the base-rate evasion of section 3.2, with its unit predictive value; FIM and active response (DEF-003/004) apply the anomaly detection and the automation trade-off of sections 3.3 and 4.2; hardening (DEF-007/008) is the surface reduction and the breaking of the transitivity of trust of section 3.4. The D3FEND tables of the READMEs are the taxonomic counterpart of the framework formalized here. The document provides the defensive practice with the quantitative justification of why "a better detector" is not enough (base-rate), of why deception is disproportionately valuable (unit predictive value) and of why hardening upstream beats detection downstream (removed edges vs events to detect).

---

## References

Subset of the master bibliography (`../REFERENCES.md`) relevant to this module:

- [Axelsson 2000] - base-rate fallacy in intrusion detection (Bayesian derivation).
- [Denning 1987], [Forrest et al. 1996] - foundations of anomaly detection.
- [Sommer & Paxson 2010] - limits of machine learning for IDS.
- [Manadhata & Wing 2011] - attack surface reduction.
- [Saltzer & Schroeder 1975] - secure design principles.
- [Biba 1977] - log integrity.
- [Strom et al. 2020] - MITRE ATT&CK (and dual D3FEND).
- [Caltagirone et al. 2013] - Diamond Model (threat intelligence).

---

> **Note:** Document for educational purposes, complementary to the operational READMEs. The citations refer to real sources listed in `../REFERENCES.md`.
