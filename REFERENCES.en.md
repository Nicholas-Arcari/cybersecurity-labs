> **English** | [Italiano](REFERENCES.md)

# Bibliography - primary literature and standards

> Annotated bibliography supporting the `THEORETICAL-FOUNDATIONS.md` documents of each module.
> It collects the peer-reviewed scientific literature, the technical standards and the reference texts
> on which the theoretical analysis of the repository is founded.

---

## Methodological note on citation

This bibliography adopts a rigorous citation discipline: only works of which author, title, publication
venue and year are certain are included. Each entry is annotated with a relevance note indicating the
module and the concept to which it applies. The works are grouped by thematic area consistent with the
module structure. Standards (NIST SP, RFC, MITRE frameworks, CIS, OWASP) are listed separately as
normative grey literature.

In-text reference convention: `[Author Year]` (e.g. `[Saltzer & Schroeder 1975]`).

---

## A. foundational principles and formal models

- **[Saltzer & Schroeder 1975]** Saltzer, J. H., & Schroeder, M. D. (1975). "The Protection of Information in Computer Systems." *Proceedings of the IEEE*, 63(9), 1278-1308.
  - Source of the eight secure design principles (economy of mechanism, fail-safe defaults, least privilege, complete mediation, open design, separation of privilege, least common mechanism, psychological acceptability). Cross-cutting foundation, central to hardening (module 08) and cloud IAM (module 10).

- **[Kerckhoffs 1883]** Kerckhoffs, A. (1883). "La cryptographie militaire." *Journal des sciences militaires*, IX, 5-38.
  - Kerckhoffs's principle: security must reside in the key, not in the secrecy of the algorithm. Foundation for the analysis of Crypto-1/MIFARE (module 06) and cryptography (module 04).

- **[Shannon 1949]** Shannon, C. E. (1949). "Communication Theory of Secrecy Systems." *Bell System Technical Journal*, 28(4), 656-715.
  - Information-theoretic foundations of secrecy; entropy, confusion and diffusion. Basis for the quantitative analysis of password entropy (module 04) and of information in reconnaissance (module 01).

- **[Dolev & Yao 1983]** Dolev, D., & Yao, A. (1983). "On the Security of Public Key Protocols." *IEEE Transactions on Information Theory*, 29(2), 198-208.
  - Formal model of the network attacker (the Dolev-Yao adversary controls the channel but does not break cryptography). Baseline of the adversary model for the network modules (01, 02, 06).

- **[Lampson 1973]** Lampson, B. W. (1973). "A Note on the Confinement Problem." *Communications of the ACM*, 16(10), 613-615.
  - Confinement problem and covert channels. Relevant to exfiltration and tunneling (module 07) and container isolation (module 10).

- **[Hardy 1988]** Hardy, N. (1988). "The Confused Deputy (or why capabilities might have been invented)." *ACM SIGOPS Operating Systems Review*, 22(4), 36-38.
  - The "confused deputy" problem, conceptual model of SSRF and of the abuse of managed identities in the cloud (module 10).

- **[Bell & LaPadula 1976]** Bell, D. E., & LaPadula, L. J. (1976). "Secure Computer System: Unified Exposition and Multics Interpretation." MITRE Technical Report MTR-2997.
  - Formal confidentiality model (no read up, no write down). Reference for access control (modules 08, 10).

- **[Biba 1977]** Biba, K. J. (1977). "Integrity Considerations for Secure Computer Systems." MITRE Technical Report MTR-3153.
  - Formal integrity model, dual of Bell-LaPadula. Reference for FIM and log integrity (module 08) and evidence integrity (module 09).

---

## B. cryptography, authentication and passwords

- **[Diffie & Hellman 1976]** Diffie, W., & Hellman, M. (1976). "New Directions in Cryptography." *IEEE Transactions on Information Theory*, 22(6), 644-654.
  - Public-key cryptography and key exchange. Theoretical basis for TLS, SSH, WPA3-SAE (modules 02, 06).

- **[Kocher 1996]** Kocher, P. C. (1996). "Timing Attacks on Implementations of Diffie-Hellman, RSA, DSS, and Other Systems." *CRYPTO '96*, LNCS 1109, 104-113.
  - Timing side-channel attacks. Foundation of the analysis of covert/side channels (modules 06, 10).

- **[Morris & Thompson 1979]** Morris, R., & Thompson, K. (1979). "Password Security: A Case History." *Communications of the ACM*, 22(11), 594-597.
  - Historical study on salting and hashing of passwords. Basis for password cracking (module 04).

- **[Kaliski 2000]** Kaliski, B. (2000). "PKCS #5: Password-Based Cryptography Specification Version 2.0." RFC 2898.
  - Definition of PBKDF2 and key stretching. Central to the analysis of the cost of WPA2 cracking (module 06) and passwords (module 04).

- **[Percival 2009]** Percival, C. (2009). "Stronger Key Derivation via Sequential Memory-Hard Functions." *BSDCan '09*.
  - scrypt and memory-hard functions. Extends the cracking cost analysis beyond PBKDF2 (module 04).

- **[Biryukov et al. 2016]** Biryukov, A., Dinu, D., & Khovratovich, D. (2016). "Argon2: New Generation of Memory-Hard Functions for Password Hashing and Other Applications." *IEEE European Symposium on Security and Privacy (EuroS&P)*, 292-302.
  - Winner of the Password Hashing Competition (2015). State of the art of password hashing (module 04).

- **[Bonneau et al. 2012]** Bonneau, J., Herley, C., van Oorschot, P. C., & Stajano, F. (2012). "The Quest to Replace Passwords: A Framework for Comparative Evaluation of Web Authentication Schemes." *IEEE Symposium on Security and Privacy*, 553-567.
  - Comparative evaluation framework for authentication. Relevant to credentials and MFA (modules 04, 07, 10).

- **[Massey 1994]** Massey, J. L. (1994). "Guessing and Entropy." *IEEE International Symposium on Information Theory (ISIT)*, 204.
  - Definition of guessing entropy (expected number of attempts of an optimal attacker). Basis of the empirical evaluation EVALUATION/exp02 (module 04).

- **[Bonneau 2012]** Bonneau, J. (2012). "The Science of Guessing: Analyzing an Anonymized Corpus of 70 Million Passwords." *IEEE Symposium on Security and Privacy*, 538-552.
  - Empirical analysis of 70 million passwords; critique of mean guessing entropy and introduction of partial guessing metrics (alpha-work-factor). Foundation of EVALUATION/exp02 (module 04).

---

## C. web security and language theory

- **[Su & Wassermann 2006]** Su, Z., & Wassermann, G. (2006). "The Essence of Command Injection Attacks in Web Applications." *ACM SIGPLAN-SIGACT Symposium on Principles of Programming Languages (POPL)*, 372-382.
  - Formal treatment of injection as data/code confusion at the grammar/parser level. Theoretical foundation of module 03.

- **[Akhawe et al. 2010]** Akhawe, D., Barth, A., Lam, P. E., Mitchell, J., & Song, D. (2010). "Towards a Formal Foundation of Web Security." *IEEE Computer Security Foundations Symposium (CSF)*, 290-304.
  - Formalization of the "web attacker" model and web security properties. Basis of the adversary model of module 03.

- **[Barth et al. 2008]** Barth, A., Jackson, C., & Mitchell, J. C. (2008). "Robust Defenses for Cross-Site Request Forgery." *ACM CCS*, 75-88.
  - Formal analysis of CSRF and defenses (tokens, origin verification). Relevant to module 03.

- **[Dhamija et al. 2006]** Dhamija, R., Tygar, J. D., & Hearst, M. (2006). "Why Phishing Works." *ACM CHI Conference on Human Factors in Computing Systems*, 581-590.
  - Empirical study on the effectiveness of phishing and the limits of human perception. Basis for module 05.

---

## D. networks, intrusion detection and detection theory

- **[Denning 1987]** Denning, D. E. (1987). "An Intrusion-Detection Model." *IEEE Transactions on Software Engineering*, SE-13(2), 222-232.
  - Foundational model of intrusion detection. Historical basis of module 08.

- **[Forrest et al. 1996]** Forrest, S., Hofmeyr, S. A., Somayaji, A., & Longstaff, T. A. (1996). "A Sense of Self for Unix Processes." *IEEE Symposium on Security and Privacy*, 120-128.
  - Anomaly detection based on system call sequences. Theoretical foundation of behavioral detection (modules 08, 10 - Falco).

- **[Axelsson 2000]** Axelsson, S. (2000). "The Base-Rate Fallacy and the Difficulty of Intrusion Detection." *ACM Transactions on Information and System Security (TISSEC)*, 3(3), 186-205.
  - Quantitative Bayesian argument on why false positives make IDS fundamentally difficult. Central quantitative reference for SIEM and deception (module 08).

- **[Ptacek & Newsham 1998]** Ptacek, T. H., & Newsham, T. N. (1998). "Insertion, Evasion, and Denial of Service: Eluding Network Intrusion Detection." Technical Report, Secure Networks Inc.
  - Network IDS evasion techniques. Relevant to network detection (modules 08, 09).

- **[Sommer & Paxson 2010]** Sommer, R., & Paxson, V. (2010). "Outside the Closed World: On Using Machine Learning for Network Intrusion Detection." *IEEE Symposium on Security and Privacy*, 305-316.
  - Critical analysis of the limits of machine learning in intrusion detection. Relevant to modern detection (module 08).

---

## E. attack graphs, kill chain and adversary modeling

- **[Phillips & Swiler 1998]** Phillips, C., & Swiler, L. P. (1998). "A Graph-Based System for Network-Vulnerability Analysis." *New Security Paradigms Workshop (NSPW)*, 71-79.
  - Introduction of attack graphs. Theoretical foundation of lateral movement and pivoting (module 07).

- **[Sheyner et al. 2002]** Sheyner, O., Haines, J., Jha, S., Lippmann, R., & Wing, J. M. (2002). "Automated Generation and Analysis of Attack Graphs." *IEEE Symposium on Security and Privacy*, 273-284.
  - Automated generation and model checking of attack graphs. Formalizes the composition of vulnerabilities into kill chains (modules 04, 07, 10).

- **[Hutchins et al. 2011]** Hutchins, E. M., Cloppert, M. J., & Amin, R. M. (2011). "Intelligence-Driven Computer Network Defense Informed by Analysis of Adversary Campaigns and Intrusion Kill Chains." *Leading Issues in Information Warfare & Security Research*, 1(1). (Lockheed Martin)
  - The Cyber Kill Chain. Cross-cutting conceptual structure of the entire offensive path (modules 01-07).

- **[Caltagirone et al. 2013]** Caltagirone, S., Pendergast, A., & Betz, C. (2013). "The Diamond Model of Intrusion Analysis." Technical Report, Center for Cyber Intelligence Analysis and Threat Research.
  - The Diamond Model for intrusion analysis. Relevant to threat intelligence and forensics (modules 08, 09).

- **[Strom et al. 2020]** Strom, B. E., Applebaum, A., Miller, D. P., Nickels, K. C., Pennington, A. G., & Thomas, C. B. (2020). "MITRE ATT&CK: Design and Philosophy." MITRE Technical Report.
  - Methodological foundation of the ATT&CK framework used in all modules.

---

## F. wireless and RFID security

- **[Fluhrer et al. 2001]** Fluhrer, S., Mantin, I., & Shamir, A. (2001). "Weaknesses in the Key Scheduling Algorithm of RC4." *Selected Areas in Cryptography (SAC)*, LNCS 2259, 1-24.
  - Breaking of WEP via RC4 weaknesses. Historical reference for the evolution of WiFi security (module 06).

- **[Nohl et al. 2008]** Nohl, K., Evans, D., Starbug, & Plotz, H. (2008). "Reverse-Engineering a Cryptographic RFID Tag." *USENIX Security Symposium*, 185-193.
  - Reverse engineering and breaking of Crypto-1 (MIFARE Classic). Foundation of module 06 (RFID/NFC).

- **[Garcia et al. 2008]** Garcia, F. D., de Koning Gans, G., Muijrers, R., van Rossum, P., Verdult, R., Schreur, R. W., & Jacobs, B. (2008). "Dismantling MIFARE Classic." *ESORICS 2008*, LNCS 5283, 97-114.
  - Complete cryptanalysis of MIFARE Classic (darkside/nested attacks). Theoretical basis of RFID cracking (module 06).

- **[Vanhoef & Piessens 2017]** Vanhoef, M., & Piessens, F. (2017). "Key Reinstallation Attacks: Forcing Nonce Reuse in WPA2." *ACM Conference on Computer and Communications Security (CCS)*, 1313-1328.
  - The KRACK attack against WPA2. Relevant to the analysis of the 4-way handshake (module 06).

- **[Vanhoef & Ronen 2020]** Vanhoef, M., & Ronen, E. (2020). "Dragonblood: Analyzing the Dragonfly Handshake of WPA3 and EAP-pwd." *IEEE Symposium on Security and Privacy*, 517-533.
  - Analysis of the weaknesses of the WPA3 Dragonfly handshake. Relevant to the evaluation of WiFi countermeasures (module 06).

---

## G. digital forensics

- **[Brezinski & Killalea 2002]** Brezinski, D., & Killalea, T. (2002). "Guidelines for Evidence Collection and Archiving." RFC 3227 (BCP 55).
  - Defines the order of volatility and the best practices of evidence collection. Foundation of module 09.

- **[Farmer & Venema 2005]** Farmer, D., & Venema, W. (2005). *Forensic Discovery*. Addison-Wesley.
  - Reference text on post-mortem forensics and data volatility. Basis of module 09.

- **[Halderman et al. 2008]** Halderman, J. A., Schoen, S. D., Heninger, N., Clarkson, W., Paul, W., Calandrino, J. A., Feldman, A. J., Appelbaum, J., & Felten, E. W. (2008). "Lest We Remember: Cold Boot Attacks on Encryption Keys." *USENIX Security Symposium*, 45-60.
  - Cold boot attacks and data persistence in RAM. Foundation of memory analysis (module 09).

- **[Garfinkel 2010]** Garfinkel, S. L. (2010). "Digital Forensics Research: The Next 10 Years." *Digital Investigation*, 7, S64-S73. (DFRWS)
  - Programmatic review of the challenges of digital forensics. Context of module 09.

---

## H. cloud, virtualization and container security

- **[Ristenpart et al. 2009]** Ristenpart, T., Tromer, E., Shacham, H., & Savage, S. (2009). "Hey, You, Get Off of My Cloud: Exploring Information Leakage in Third-Party Compute Clouds." *ACM CCS*, 199-212.
  - Co-residency and side-channels between VMs in the public cloud. Theoretical foundation of module 10.

- **[Zhang et al. 2012]** Zhang, Y., Juels, A., Reiter, M. K., & Ristenpart, T. (2012). "Cross-VM Side Channels and Their Use to Extract Private Keys." *ACM CCS*, 305-316.
  - Extraction of keys via cross-VM side-channels. Extends the analysis of isolation in the cloud (module 10).

- **[Antonakakis et al. 2017]** Antonakakis, M., et al. (2017). "Understanding the Mirai Botnet." *USENIX Security Symposium*, 1093-1110.
  - Empirical analysis of the Mirai botnet (IoT). Relevant to honeypots and IoT threats (modules 06, 08).

---

## I. reconnaissance and attack surface

- **[Manadhata & Wing 2011]** Manadhata, P. K., & Wing, J. M. (2011). "An Attack Surface Metric." *IEEE Transactions on Software Engineering*, 37(3), 371-386.
  - Quantitative formalization of the attack surface. Theoretical foundation of module 01 (reconnaissance) and hardening (module 08).

- **[Durumeric et al. 2013a]** Durumeric, Z., Wustrow, E., & Halderman, J. A. (2013). "ZMap: Fast Internet-Wide Scanning and Its Security Applications." *USENIX Security Symposium*, 605-620.
  - Scanning of the entire IPv4 space in reduced time; changes the economics of reconnaissance. Quantitative basis of module 01.

- **[Durumeric et al. 2013b]** Durumeric, Z., Kasten, J., Bailey, M., & Halderman, J. A. (2013). "Analysis of the HTTPS Certificate Ecosystem." *ACM Internet Measurement Conference (IMC)*, 291-304.
  - Empirical measurement of the certificate ecosystem; relevant to reconnaissance via Certificate Transparency (module 01).

---

## J. social engineering (psychological foundations)

- **[Cialdini 1984]** Cialdini, R. B. (1984). *Influence: The Psychology of Persuasion*. Harper Business.
  - The six principles of influence (reciprocity, commitment/consistency, social proof, authority, liking, scarcity). Psychological foundation of module 05.

- **[Kahneman 2011]** Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.
  - Dual-process theory (heuristic System 1 / analytic System 2). Foundation of why heuristic processing is exploitable by social engineering (module 05).

- **[Reason 1990]** Reason, J. (1990). *Human Error*. Cambridge University Press.
  - Model of human error (Swiss cheese model, slips/lapses/mistakes). Basis for the socio-technical analysis of the weakest link (module 05).

---

## M. exploitation, memory safety and theory of computation

- **[Aleph One 1996]** Aleph One (Levy, E.). (1996). "Smashing the Stack for Fun and Profit." *Phrack Magazine*, 7(49), file 14.
  - Seminal exposition of the stack buffer overflow. Historical reference of module 04 (binary exploitation).

- **[Shacham 2007]** Shacham, H. (2007). "The Geometry of Innocent Flesh on the Bone: Return-into-libc without Function Calls (on the x86)." *ACM CCS*, 552-561.
  - Introduction of Return-Oriented Programming (ROP) and proof of its Turing-completeness. Theoretical foundation of the DEP/W^X bypass (module 04).

- **[Abadi et al. 2005]** Abadi, M., Budiu, M., Erlingsson, U., & Ligatti, J. (2005). "Control-Flow Integrity." *ACM CCS*, 340-353.
  - Formal definition of Control-Flow Integrity as a security property. Reference for memory corruption countermeasures (modules 04, 08).

- **[Bratus et al. 2011]** Bratus, S., Locasto, M. E., Patterson, M. L., Shubina, A., & Sassaman, L. (2011). "Exploit Programming: From Buffer Overflows to Weird Machines and Theory of Computation." *USENIX ;login:*, 36(6), 13-21.
  - Framing of exploitation as programming an unintended "weird machine". Theoretical foundation of module 04.

- **[Szekeres et al. 2013]** Szekeres, L., Payer, M., Wei, T., & Song, D. (2013). "SoK: Eternal War in Memory." *IEEE Symposium on Security and Privacy*, 48-62.
  - Systematization of Knowledge on memory corruption and countermeasures (DEP, ASLR, canaries, CFI). Reference survey of module 04.

---

## N. provable security, formal models and semantics (graduate level)

- **[Goldwasser & Micali 1984]** Goldwasser, S., & Micali, S. (1984). "Probabilistic Encryption." *Journal of Computer and System Sciences*, 28(2), 270-299.
  - Notion of semantic security and computational indistinguishability. Foundation of provable security (THEORY-ADVANCED, Part I).

- **[Bellare & Rogaway 1993]** Bellare, M., & Rogaway, P. (1993). "Random Oracles are Practical: A Paradigm for Designing Efficient Protocols." *ACM CCS*, 62-73.
  - The Random Oracle Model. Basis of the concrete-security analysis of the offline attack (THEORY-ADVANCED, Parts I-II).

- **[Bellare et al. 1997]** Bellare, M., Desai, A., Jokipii, E., & Rogaway, P. (1997). "A Concrete Security Treatment of Symmetric Encryption." *IEEE FOCS*, 394-403.
  - Concrete-security treatment ((t, eps)-secure notions). Reference for Part I of THEORY-ADVANCED.

- **[Shoup 2004]** Shoup, V. (2004). "Sequences of Games: A Tool for Taming Complexity in Security Proofs." IACR ePrint 2004/332.
  - The game-hopping proof methodology. Methodological reference (THEORY-ADVANCED, Part I).

- **[Canetti et al. 1998]** Canetti, R., Goldreich, O., & Halevi, S. (1998). "The Random Oracle Methodology, Revisited." *ACM STOC*, 209-218.
  - Limits of the ROM (schemes secure in the ROM but not instantiable). Caveat disclosed in Part I.

- **[Massey 1994]** (already in section B) - guessing entropy; used formally in Part II.

- **[Lowe 1997]** Lowe, G. (1997). "A Hierarchy of Authentication Specifications." *IEEE Computer Security Foundations Workshop (CSFW)*, 31-43.
  - Authentication hierarchy (aliveness, weak/non-injective/injective agreement). Basis of Part III and of reading KRACK as loss of injective agreement.

- **[Abadi & Rogaway 2002]** Abadi, M., & Rogaway, P. (2002). "Reconciling Two Views of Cryptography (The Computational Soundness of Formal Encryption)." *Journal of Cryptology*, 15(2), 103-127.
  - Relation between the symbolic (Dolev-Yao) and computational models. Part III.

- **[Denning 1976]** Denning, D. E. (1976). "A Lattice Model of Secure Information Flow." *Communications of the ACM*, 19(5), 236-243.
  - Lattice model of information flow. Part IV.

- **[Goguen & Meseguer 1982]** Goguen, J. A., & Meseguer, J. (1982). "Security Policies and Security Models." *IEEE Symposium on Security and Privacy*, 11-20.
  - Formal definition of non-interference. Part IV, applied to covert channels (module 07) and tenant isolation (module 10).

- **[Katz & Lindell 2020]** Katz, J., & Lindell, Y. (2020). *Introduction to Modern Cryptography* (3rd ed.). CRC Press.
  - Reference text for game-based definitions, reductions and the hybrid argument (THEORY-ADVANCED, Part I).

- **[Goldreich 2001]** Goldreich, O. (2001). *Foundations of Cryptography, Volume I: Basic Tools*. Cambridge University Press.
  - Rigorous treatment of PRFs, indistinguishability and reductions. Part I.

---

## K. reference monographs

- **[Anderson 2020]** Anderson, R. (2020). *Security Engineering: A Guide to Building Dependable Distributed Systems* (3rd ed.). Wiley.
- **[Bishop 2018]** Bishop, M. (2018). *Computer Security: Art and Science* (2nd ed.). Addison-Wesley.
- **[Shostack 2014]** Shostack, A. (2014). *Threat Modeling: Designing for Security*. Wiley.

---

## L. standards and normative grey literature

- **NIST SP 800-61 Rev. 2** - Computer Security Incident Handling Guide (modules 08, 09).
- **NIST SP 800-63B** - Digital Identity Guidelines: Authentication and Lifecycle Management (modules 04, 07, 10).
- **NIST SP 800-115** - Technical Guide to Information Security Testing and Assessment (modules 01, 02).
- **NIST SP 800-145** - The NIST Definition of Cloud Computing (module 10).
- **NIST SP 800-190** - Application Container Security Guide (module 10).
- **MITRE ATT&CK** - Adversarial Tactics, Techniques, and Common Knowledge (all modules).
- **MITRE D3FEND** - A Knowledge Graph of Cybersecurity Countermeasures (modules 08, 09, 10).
- **CVSS v3.1** - Common Vulnerability Scoring System Specification, FIRST.org (module 02).
- **CIS Benchmarks** - Center for Internet Security (modules 08, 10).
- **OWASP Top 10 / OWASP Testing Guide** (module 03).
- **RFC 6962** - Certificate Transparency (module 01).
- **Verizon DBIR** - Data Breach Investigations Report (annual; cross-cutting empirical context).

---

## O. Active Directory, Kerberos and PKI

- **[Needham & Schroeder 1978]** Needham, R. M., & Schroeder, M. D. (1978). "Using Encryption for Authentication in Large Networks of Computers." *Communications of the ACM*, 21(12), 993-999.
  - Trusted-third-party authentication protocol, conceptual ancestor of Kerberos (module 11).
- **[Bellovin & Merritt 1991]** Bellovin, S. M., & Merritt, M. (1991). "Limitations of the Kerberos Authentication System." *USENIX Winter Technical Conference*.
  - Classic critical analysis of Kerberos: assumptions, offline password attacks (module 11).
- **[Neuman et al. 2005]** Neuman, C., Yu, T., Hartman, S., & Raeburn, K. (2005). "The Kerberos Network Authentication Service (V5)." RFC 4120.
  - Kerberos v5 specification: AS/TGS/AP flow, TGT/TGS, pre-authentication (module 11).
- **[Raeburn 2005]** Raeburn, K. (2005). "Advanced Encryption Standard (AES) Encryption for Kerberos 5." RFC 3962.
  - AES string-to-key (PBKDF2, 4096 iterations): basis of the Kerberoasting quantitative analysis (module 11).
- **[Medin 2014]** Medin, T. (2014). "Attacking Microsoft Kerberos: Kicking the Guard Dog of Hades." DerbyCon 4.0.
  - Operational introduction of Kerberoasting (module 11).
- **[Delpy & Le Toux 2015]** Delpy, B., & Le Toux, V. (2015). "DCSync" (Mimikatz `lsadump::dcsync`).
  - Abused replication (MS-DRSR) to extract domain secrets (module 11).
- **[Schroeder & Christensen 2021]** Schroeder, W., & Christensen, L. (2021). "Certified Pre-Owned: Abusing Active Directory Certificate Services." SpecterOps.
  - Systematization of AD CS attacks (ESC1-ESC8+) (module 11).

---

> **Note:** This bibliography lists real and verifiable sources. The citations are provided for
> educational purposes and to give scientific framing to the lab work. Direct consultation of the
> primary sources is recommended: the annotations summarize their relevance but do not substitute reading them.
