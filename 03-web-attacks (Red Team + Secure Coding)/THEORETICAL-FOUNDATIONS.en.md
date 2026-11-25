> **English** | [Italiano](THEORETICAL-FOUNDATIONS.md)

# Theoretical foundations - module 03: web attacks

> - **Level:** Academic analysis (theoretical complement to the operational READMEs of the module)
> - **Purpose:** Formalize injection as linguistic confusion between data and code, the web attacker model, and CSRF/SSRF as instances of the confused deputy.
> - **Prerequisites:** Operational READMEs of module 03 (WEB- findings); basic notions of formal languages (grammars, parse trees) and access control.

---

## Abstract

Web vulnerabilities are often cataloged empirically (SQLi, XSS, CSRF, SSRF). This document traces them back to two unifying theoretical roots. The first is the **confusion between data and code**: injection is formalizable, according to [Su & Wassermann 2006], as the phenomenon by which an attacker's input crosses the boundary between the data position and the code position in the parse tree of a language. The second is the **confused deputy** [Hardy 1988]: CSRF and SSRF are instances of the problem whereby a privileged component acts on behalf of an unauthorized principal. The web attacker model [Akhawe et al. 2010] is adopted as a formal frame, and the countermeasures are derived as applications of the principle of complete mediation [Saltzer & Schroeder 1975].

---

## 1. The adversary model

The **web attacker** model formalized by [Akhawe et al. 2010] is adopted, weaker than the Dolev-Yao network attacker but more realistic for the web domain. The web attacker:

- controls one or more websites (can serve arbitrary content to visitors);
- can send arbitrary HTTP requests toward any endpoint;
- can induce a victim to visit a URL under its control;
- does **not** control the network channel (unlike Dolev-Yao): it cannot intercept or modify the traffic between the victim and a third honest site.

This restriction is what makes the web attacker interesting: many web vulnerabilities (CSRF, XSS) are exploitable even without control of the channel, exploiting instead the misplaced trust of the browser or the server. The web security properties (Same-Origin Policy, session integrity) are defined [Akhawe et al. 2010] with respect to this adversary.

---

## 2. Security properties at stake

- **Data/code separation:** untrusted input must never be interpreted as an instruction. It is the property violated by all injection families (SQLi, command injection, XSS as code injection in the DOM).
- **Intention-based authorization:** a privileged action must be executed only if actually intended by the authorized principal, not merely if the request is syntactically valid. It is the property violated by the confused deputy (CSRF, SSRF).
- **Origin isolation (Same-Origin Policy):** content of one origin must not access resources of another origin without explicit authorization. It is the browser's access control mechanism with respect to the web attacker.

---

## 3. Theoretical foundations

### 3.1 Injection as data/code confusion (linguistic formalization)

[Su & Wassermann 2006] provide the formal characterization of command injection. The central idea: an application builds a string (SQL query, shell command, markup) that will be interpreted by a parser according to a grammar `G`. The attacker's input is intended to occupy a **data position** (a literal, a value) in the parse tree. Injection occurs when the input, instead, alters the **syntactic structure** of the tree, occupying or creating **code** positions (operators, keywords, delimiters).

Formally, let `q = f(u)` be the string produced by the application by composing trusted input and user input `u`. Define the set of "expected" syntactic nodes for `u` as the leaf value-nodes only. Injection occurs if and only if there exists a `u` such that the parse tree of `q` according to `G` contains, in correspondence with `u`, nodes that are not value-leaves, that is, `u` contributes to the non-terminal structure of the tree. This is the definition of [Su & Wassermann 2006], who also derive a detection algorithm based on comparing the expected parse tree with the actual one.

The theoretical consequence is strong: countermeasures that act on the string (escaping, blacklists) chase syntactic manifestations and are fragile, while **parametrized queries (prepared statements)** solve the problem at the root because they structurally constrain `u` to occupy a value position, making it impossible by construction to alter the tree. The correctness of prepared statements is not heuristic but structural: they separate the structure channel (the query template, trusted) from the data channel (the parameters, untrusted).

### 3.2 CSRF and SSRF as confused deputy

[Hardy 1988] describes the **confused deputy** as a program endowed with authority that is induced by a third party to use that authority on behalf of the third party, not of the legitimate holder. CSRF and SSRF are two instances of it:

- **CSRF:** the victim's browser is the confused deputy. It holds the authority (session cookies) and uses it to send a request induced by the attacker's site. The server does not distinguish a request *intended* by the victim from one *induced* by the attacker: both carry valid credentials. The defense (anti-CSRF token, origin/SameSite verification) [Barth et al. 2008] restores the distinction, requiring a proof of intention that the attacker cannot provide.

- **SSRF:** the server is the confused deputy. It holds the network authority (reachability of internal endpoints, e.g. the cloud metadata service) and uses it on behalf of the attacker who controls a destination URL. It is the same scheme, moved from the browser to the server, and directly links module 03 to the cloud credential theft of module 10 (metadata SSRF).

The theoretical unification is that both violate the **intention-based authorization** (section 2): the request is valid but not intended. The confused deputy shows that authentication (who presents the authority) is insufficient without the verification of intention (who wanted the action).

### 3.3 Complete mediation and Same-Origin policy

The Same-Origin Policy is an instance of the principle of **complete mediation** of [Saltzer & Schroeder 1975]: every access to a resource must be verified. The browser mediates every cross-origin access according to the origin (scheme, host, port) of the requesting context. CORS configuration vulnerabilities are, in this frame, loosenings of complete mediation that reopen the channel the SOP was closing.

---

## 4. Quantitative analysis

### 4.1 Taint propagation and information flow

The detection of injection can be modeled as an **information flow** problem: each untrusted input is labeled (tainted) and its propagation is traced to the sensitive sinks (query execution, eval, HTML output). A taint, sink flow without interposed sanitization is an injection candidate. The completeness of this analysis suffers the same decidability limits of module 02 (section 3.1 of that document): the exact tracing of the flow in the presence of aliasing, reflection and dynamic constructs is undecidable in the general case, so static analyzers are also unsound or incomplete.

### 4.2 The asymmetric defense/attack cost in escaping

The escaping/blacklist approach is quantitatively disadvantageous: the defender must enumerate and neutralize *all* the syntactically dangerous sequences (an open set dependent on the parser), while the attacker must find just *one* not covered. It is the same asymmetry "the defender must be right always, the attacker only once" already encountered in module 01. Prepared statements invert the asymmetry by eliminating the entire class (section 3.1): the defender solves once, structurally, instead of chasing infinite manifestations.

---

## 5. Literature review

The formalization of injection follows [Su & Wassermann 2006], who gave it a precise linguistic characterization and a parse-tree-based detection method. The adversary model and web properties derive from [Akhawe et al. 2010], the foundational reference of the formal analysis of web security. The defense against CSRF is rigorously analyzed by [Barth et al. 2008]. The framing of CSRF/SSRF as a confused deputy goes back to [Hardy 1988]. The countermeasures as complete mediation and least privilege appeal to [Saltzer & Schroeder 1975]. The empirical catalog of the classes (OWASP Top 10) provides the complementary operational taxonomy.

---

## 6. Limitations and open problems

1. **Undecidability of flow analysis.** As for module 02, the exact detection of taint-to-sink flows is undecidable in the general case; the tools (SAST) remain approximations.

2. **Context-dependent sanitization.** The correctness of output encoding depends on the destination context (HTML body, attribute, JavaScript, URL, CSS): a sanitization correct in one context is insufficient in another. The secure composition of multiple contexts (e.g. data that crosses HTML and then JavaScript) remains error-prone and not fully automatable.

3. **Non-observable intention.** The confused deputy rests on the impossibility for the server to directly observe the principal's intention; anti-CSRF tokens and SameSite are approximations of the proof of intention, not its direct verification. The complete formal modeling of the user's intention remains open.

---

## 7. Synthesis and connection to practice

The `WEB-` findings of the module map onto this framework: the injection families (SQLi, command injection, XSS) are instances of the data/code confusion of section 3.1, and the remediation recommended in the READMEs (prepared statements, context-aware output encoding) is the operational translation of the structural solution; CSRF and SSRF are confused deputies (section 3.2), with the defenses (tokens, SameSite, destination allowlist) as a restoration of intention-based authorization. The link to module 10 is direct and theoretically motivated: the SSRF that steals the cloud metadata service token is the same confused deputy, moved to the server. The document provides the module's secure-coding practice with the formal justification of why structural countermeasures (which eliminate the class) are superior to syntactic ones (which chase the instances).

---

## References

Subset of the master bibliography (`../REFERENCES.md`) relevant to this module:

- [Su & Wassermann 2006] - linguistic formalization of injection.
- [Akhawe et al. 2010] - web attacker model and formal foundations of web security.
- [Barth et al. 2008] - formal defenses against CSRF.
- [Hardy 1988] - the confused deputy (conceptual basis of CSRF/SSRF).
- [Saltzer & Schroeder 1975] - complete mediation and least privilege.
- [Bishop 2018] - policy and mechanism.
- OWASP Top 10 / Testing Guide - operational taxonomy.

---

> **Note:** Document for educational purposes, complementary to the operational READMEs. The citations refer to real sources listed in `../REFERENCES.md`.
