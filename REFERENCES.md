> [English](REFERENCES.en.md) | **Italiano**

# Riferimenti bibliografici - letteratura primaria e standard

> Bibliografia annotata a supporto dei documenti `THEORETICAL-FOUNDATIONS.md` di ciascun modulo.
> Raccoglie la letteratura scientifica peer-reviewed, gli standard tecnici e i testi di riferimento
> su cui si fonda l'analisi teorica del repository.

---

## Nota metodologica sulla citazione

Questa bibliografia adotta una disciplina di citazione rigorosa: sono incluse esclusivamente opere di
cui si ha certezza di autore, titolo, sede di pubblicazione (venue) e anno. Ogni voce e annotata con
una nota di rilevanza che indica il modulo e il concetto a cui si applica. Le opere sono raggruppate
per area tematica coerente con la struttura dei moduli. Gli standard (NIST SP, RFC, framework MITRE,
CIS, OWASP) sono elencati separatamente come letteratura grigia normativa.

Convenzione di riferimento nel testo: `[Autore Anno]` (es. `[Saltzer & Schroeder 1975]`).

---

## A. principi fondazionali e modelli formali

- **[Saltzer & Schroeder 1975]** Saltzer, J. H., & Schroeder, M. D. (1975). "The Protection of Information in Computer Systems." *Proceedings of the IEEE*, 63(9), 1278-1308.
  - Fonte degli otto principi di progettazione sicura (economy of mechanism, fail-safe defaults, least privilege, complete mediation, open design, separation of privilege, least common mechanism, psychological acceptability). Fondamento trasversale, centrale per hardening (modulo 08) e cloud IAM (modulo 10).

- **[Kerckhoffs 1883]** Kerckhoffs, A. (1883). "La cryptographie militaire." *Journal des sciences militaires*, IX, 5-38.
  - Principio di Kerckhoffs: la sicurezza deve risiedere nella chiave, non nella segretezza dell'algoritmo. Fondamento per l'analisi di Crypto-1/MIFARE (modulo 06) e crittografia (modulo 04).

- **[Shannon 1949]** Shannon, C. E. (1949). "Communication Theory of Secrecy Systems." *Bell System Technical Journal*, 28(4), 656-715.
  - Fondamenti teorico-informativi della segretezza; entropia, confusione e diffusione. Base per l'analisi quantitativa dell'entropia delle password (modulo 04) e dell'informazione nella ricognizione (modulo 01).

- **[Dolev & Yao 1983]** Dolev, D., & Yao, A. (1983). "On the Security of Public Key Protocols." *IEEE Transactions on Information Theory*, 29(2), 198-208.
  - Modello formale dell'attaccante di rete (l'avversario Dolev-Yao controlla il canale ma non rompe la crittografia). Baseline del modello di avversario per i moduli di rete (01, 02, 06).

- **[Lampson 1973]** Lampson, B. W. (1973). "A Note on the Confinement Problem." *Communications of the ACM*, 16(10), 613-615.
  - Problema del confinamento e canali covert. Rilevante per esfiltrazione e tunneling (modulo 07) e isolamento dei container (modulo 10).

- **[Hardy 1988]** Hardy, N. (1988). "The Confused Deputy (or why capabilities might have been invented)." *ACM SIGOPS Operating Systems Review*, 22(4), 36-38.
  - Il problema del "vice confuso", modello concettuale dell'SSRF e dell'abuso di identita gestite nel cloud (modulo 10).

- **[Bell & LaPadula 1976]** Bell, D. E., & LaPadula, L. J. (1976). "Secure Computer System: Unified Exposition and Multics Interpretation." MITRE Technical Report MTR-2997.
  - Modello formale di confidenzialita (no read up, no write down). Riferimento per il controllo degli accessi (moduli 08, 10).

- **[Biba 1977]** Biba, K. J. (1977). "Integrity Considerations for Secure Computer Systems." MITRE Technical Report MTR-3153.
  - Modello formale di integrita, duale di Bell-LaPadula. Riferimento per FIM e integrita dei log (modulo 08) e delle prove (modulo 09).

---

## B. crittografia, autenticazione e password

- **[Diffie & Hellman 1976]** Diffie, W., & Hellman, M. (1976). "New Directions in Cryptography." *IEEE Transactions on Information Theory*, 22(6), 644-654.
  - Crittografia a chiave pubblica e scambio di chiavi. Base teorica per TLS, SSH, WPA3-SAE (moduli 02, 06).

- **[Kocher 1996]** Kocher, P. C. (1996). "Timing Attacks on Implementations of Diffie-Hellman, RSA, DSS, and Other Systems." *CRYPTO '96*, LNCS 1109, 104-113.
  - Attacchi a canale laterale temporale. Fondamento dell'analisi dei canali covert/side-channel (moduli 06, 10).

- **[Morris & Thompson 1979]** Morris, R., & Thompson, K. (1979). "Password Security: A Case History." *Communications of the ACM*, 22(11), 594-597.
  - Studio storico su salting e hashing delle password. Base per il password cracking (modulo 04).

- **[Kaliski 2000]** Kaliski, B. (2000). "PKCS #5: Password-Based Cryptography Specification Version 2.0." RFC 2898.
  - Definizione di PBKDF2 e del key stretching. Centrale per l'analisi del costo del cracking WPA2 (modulo 06) e delle password (modulo 04).

- **[Percival 2009]** Percival, C. (2009). "Stronger Key Derivation via Sequential Memory-Hard Functions." *BSDCan '09*.
  - scrypt e le funzioni memory-hard. Estende l'analisi del costo del cracking oltre PBKDF2 (modulo 04).

- **[Biryukov et al. 2016]** Biryukov, A., Dinu, D., & Khovratovich, D. (2016). "Argon2: New Generation of Memory-Hard Functions for Password Hashing and Other Applications." *IEEE European Symposium on Security and Privacy (EuroS&P)*, 292-302.
  - Vincitore della Password Hashing Competition (2015). Stato dell'arte dell'hashing delle password (modulo 04).

- **[Bonneau et al. 2012]** Bonneau, J., Herley, C., van Oorschot, P. C., & Stajano, F. (2012). "The Quest to Replace Passwords: A Framework for Comparative Evaluation of Web Authentication Schemes." *IEEE Symposium on Security and Privacy*, 553-567.
  - Framework di valutazione comparativa dell'autenticazione. Rilevante per credenziali e MFA (moduli 04, 07, 10).

- **[Massey 1994]** Massey, J. L. (1994). "Guessing and Entropy." *IEEE International Symposium on Information Theory (ISIT)*, 204.
  - Definizione della guessing entropy (numero atteso di tentativi di un attaccante ottimale). Base della valutazione empirica EVALUATION/exp02 (modulo 04).

- **[Bonneau 2012]** Bonneau, J. (2012). "The Science of Guessing: Analyzing an Anonymized Corpus of 70 Million Passwords." *IEEE Symposium on Security and Privacy*, 538-552.
  - Analisi empirica di 70 milioni di password; critica della guessing entropy media e introduzione delle metriche di partial guessing (alpha-work-factor). Fondamento di EVALUATION/exp02 (modulo 04).

---

## C. sicurezza web e teoria dei linguaggi

- **[Su & Wassermann 2006]** Su, Z., & Wassermann, G. (2006). "The Essence of Command Injection Attacks in Web Applications." *ACM SIGPLAN-SIGACT Symposium on Principles of Programming Languages (POPL)*, 372-382.
  - Trattazione formale dell'injection come confusione tra dati e codice a livello di grammatica/parser. Fondamento teorico del modulo 03.

- **[Akhawe et al. 2010]** Akhawe, D., Barth, A., Lam, P. E., Mitchell, J., & Song, D. (2010). "Towards a Formal Foundation of Web Security." *IEEE Computer Security Foundations Symposium (CSF)*, 290-304.
  - Formalizzazione del modello del "web attacker" e delle proprieta di sicurezza web. Base del modello di avversario del modulo 03.

- **[Barth et al. 2008]** Barth, A., Jackson, C., & Mitchell, J. C. (2008). "Robust Defenses for Cross-Site Request Forgery." *ACM CCS*, 75-88.
  - Analisi formale del CSRF e delle difese (token, verifica dell'origine). Rilevante per il modulo 03.

- **[Dhamija et al. 2006]** Dhamija, R., Tygar, J. D., & Hearst, M. (2006). "Why Phishing Works." *ACM CHI Conference on Human Factors in Computing Systems*, 581-590.
  - Studio empirico sull'efficacia del phishing e i limiti percettivi umani. Base per il modulo 05.

---

## D. reti, intrusion detection e teoria del rilevamento

- **[Denning 1987]** Denning, D. E. (1987). "An Intrusion-Detection Model." *IEEE Transactions on Software Engineering*, SE-13(2), 222-232.
  - Modello fondativo dell'intrusion detection. Base storica del modulo 08.

- **[Forrest et al. 1996]** Forrest, S., Hofmeyr, S. A., Somayaji, A., & Longstaff, T. A. (1996). "A Sense of Self for Unix Processes." *IEEE Symposium on Security and Privacy*, 120-128.
  - Anomaly detection basato sulle sequenze di system call. Fondamento teorico della detection comportamentale (moduli 08, 10 - Falco).

- **[Axelsson 2000]** Axelsson, S. (2000). "The Base-Rate Fallacy and the Difficulty of Intrusion Detection." *ACM Transactions on Information and System Security (TISSEC)*, 3(3), 186-205.
  - Argomento bayesiano quantitativo sul perche i falsi positivi rendono l'IDS fondamentalmente difficile. Riferimento quantitativo centrale per SIEM e deception (modulo 08).

- **[Ptacek & Newsham 1998]** Ptacek, T. H., & Newsham, T. N. (1998). "Insertion, Evasion, and Denial of Service: Eluding Network Intrusion Detection." Technical Report, Secure Networks Inc.
  - Tecniche di evasione degli IDS di rete. Rilevante per la detection di rete (moduli 08, 09).

- **[Sommer & Paxson 2010]** Sommer, R., & Paxson, V. (2010). "Outside the Closed World: On Using Machine Learning for Network Intrusion Detection." *IEEE Symposium on Security and Privacy*, 305-316.
  - Analisi critica dei limiti del machine learning nell'intrusion detection. Rilevante per la detection moderna (modulo 08).

---

## E. grafi di attacco, kill chain e modellazione dell'avversario

- **[Phillips & Swiler 1998]** Phillips, C., & Swiler, L. P. (1998). "A Graph-Based System for Network-Vulnerability Analysis." *New Security Paradigms Workshop (NSPW)*, 71-79.
  - Introduzione dei grafi di attacco. Fondamento teorico del lateral movement e pivoting (modulo 07).

- **[Sheyner et al. 2002]** Sheyner, O., Haines, J., Jha, S., Lippmann, R., & Wing, J. M. (2002). "Automated Generation and Analysis of Attack Graphs." *IEEE Symposium on Security and Privacy*, 273-284.
  - Generazione automatica e model checking dei grafi di attacco. Formalizza la composizione di vulnerabilita in kill chain (moduli 04, 07, 10).

- **[Hutchins et al. 2011]** Hutchins, E. M., Cloppert, M. J., & Amin, R. M. (2011). "Intelligence-Driven Computer Network Defense Informed by Analysis of Adversary Campaigns and Intrusion Kill Chains." *Leading Issues in Information Warfare & Security Research*, 1(1). (Lockheed Martin)
  - Il Cyber Kill Chain. Struttura concettuale trasversale dell'intero percorso offensivo (moduli 01-07).

- **[Caltagirone et al. 2013]** Caltagirone, S., Pendergast, A., & Betz, C. (2013). "The Diamond Model of Intrusion Analysis." Technical Report, Center for Cyber Intelligence Analysis and Threat Research.
  - Modello del Diamante per l'analisi delle intrusioni. Rilevante per threat intelligence e forense (moduli 08, 09).

- **[Strom et al. 2020]** Strom, B. E., Applebaum, A., Miller, D. P., Nickels, K. C., Pennington, A. G., & Thomas, C. B. (2020). "MITRE ATT&CK: Design and Philosophy." MITRE Technical Report.
  - Fondamento metodologico del framework ATT&CK usato in tutti i moduli.

---

## F. sicurezza wireless e RFID

- **[Fluhrer et al. 2001]** Fluhrer, S., Mantin, I., & Shamir, A. (2001). "Weaknesses in the Key Scheduling Algorithm of RC4." *Selected Areas in Cryptography (SAC)*, LNCS 2259, 1-24.
  - Rottura di WEP tramite debolezze di RC4. Riferimento storico per l'evoluzione della sicurezza WiFi (modulo 06).

- **[Nohl et al. 2008]** Nohl, K., Evans, D., Starbug, & Plotz, H. (2008). "Reverse-Engineering a Cryptographic RFID Tag." *USENIX Security Symposium*, 185-193.
  - Reverse engineering e rottura di Crypto-1 (MIFARE Classic). Fondamento del modulo 06 (RFID/NFC).

- **[Garcia et al. 2008]** Garcia, F. D., de Koning Gans, G., Muijrers, R., van Rossum, P., Verdult, R., Schreur, R. W., & Jacobs, B. (2008). "Dismantling MIFARE Classic." *ESORICS 2008*, LNCS 5283, 97-114.
  - Crittanalisi completa di MIFARE Classic (attacchi darkside/nested). Base teorica del cracking RFID (modulo 06).

- **[Vanhoef & Piessens 2017]** Vanhoef, M., & Piessens, F. (2017). "Key Reinstallation Attacks: Forcing Nonce Reuse in WPA2." *ACM Conference on Computer and Communications Security (CCS)*, 1313-1328.
  - L'attacco KRACK contro WPA2. Rilevante per l'analisi del 4-way handshake (modulo 06).

- **[Vanhoef & Ronen 2020]** Vanhoef, M., & Ronen, E. (2020). "Dragonblood: Analyzing the Dragonfly Handshake of WPA3 and EAP-pwd." *IEEE Symposium on Security and Privacy*, 517-533.
  - Analisi delle debolezze del handshake Dragonfly di WPA3. Rilevante per la valutazione delle contromisure WiFi (modulo 06).

---

## M. sfruttamento, memory safety e teoria della computazione

- **[Aleph One 1996]** Aleph One (Levy, E.). (1996). "Smashing the Stack for Fun and Profit." *Phrack Magazine*, 7(49), file 14.
  - Esposizione seminale dello stack buffer overflow. Riferimento storico del modulo 04 (binary exploitation).

- **[Shacham 2007]** Shacham, H. (2007). "The Geometry of Innocent Flesh on the Bone: Return-into-libc without Function Calls (on the x86)." *ACM CCS*, 552-561.
  - Introduzione del Return-Oriented Programming (ROP) e dimostrazione della sua Turing-completezza. Fondamento teorico del bypass di DEP/W^X (modulo 04).

- **[Abadi et al. 2005]** Abadi, M., Budiu, M., Erlingsson, U., & Ligatti, J. (2005). "Control-Flow Integrity." *ACM CCS*, 340-353.
  - Definizione formale della Control-Flow Integrity come proprieta di sicurezza. Riferimento per le contromisure alla memory corruption (moduli 04, 08).

- **[Bratus et al. 2011]** Bratus, S., Locasto, M. E., Patterson, M. L., Shubina, A., & Sassaman, L. (2011). "Exploit Programming: From Buffer Overflows to Weird Machines and Theory of Computation." *USENIX ;login:*, 36(6), 13-21.
  - Inquadramento dello sfruttamento come programmazione di una "weird machine" non intenzionale. Fondamento teorico del modulo 04.

- **[Szekeres et al. 2013]** Szekeres, L., Payer, M., Wei, T., & Song, D. (2013). "SoK: Eternal War in Memory." *IEEE Symposium on Security and Privacy*, 48-62.
  - Systematization of Knowledge sulla memory corruption e le contromisure (DEP, ASLR, canaries, CFI). Rassegna di riferimento del modulo 04.

---

## G. forense digitale

- **[Brezinski & Killalea 2002]** Brezinski, D., & Killalea, T. (2002). "Guidelines for Evidence Collection and Archiving." RFC 3227 (BCP 55).
  - Definisce l'ordine di volatilita e le best practice di raccolta delle prove. Fondamento del modulo 09.

- **[Farmer & Venema 2005]** Farmer, D., & Venema, W. (2005). *Forensic Discovery*. Addison-Wesley.
  - Testo di riferimento sulla forense post-mortem e la volatilita dei dati. Base del modulo 09.

- **[Halderman et al. 2008]** Halderman, J. A., Schoen, S. D., Heninger, N., Clarkson, W., Paul, W., Calandrino, J. A., Feldman, A. J., Appelbaum, J., & Felten, E. W. (2008). "Lest We Remember: Cold Boot Attacks on Encryption Keys." *USENIX Security Symposium*, 45-60.
  - Attacchi cold boot e persistenza dei dati in RAM. Fondamento dell'analisi della memoria (modulo 09).

- **[Garfinkel 2010]** Garfinkel, S. L. (2010). "Digital Forensics Research: The Next 10 Years." *Digital Investigation*, 7, S64-S73. (DFRWS)
  - Rassegna programmatica delle sfide della forense digitale. Contesto del modulo 09.

---

## H. sicurezza cloud, virtualizzazione e container

- **[Ristenpart et al. 2009]** Ristenpart, T., Tromer, E., Shacham, H., & Savage, S. (2009). "Hey, You, Get Off of My Cloud: Exploring Information Leakage in Third-Party Compute Clouds." *ACM CCS*, 199-212.
  - Co-residenza e side-channel tra VM nel cloud pubblico. Fondamento teorico del modulo 10.

- **[Zhang et al. 2012]** Zhang, Y., Juels, A., Reiter, M. K., & Ristenpart, T. (2012). "Cross-VM Side Channels and Their Use to Extract Private Keys." *ACM CCS*, 305-316.
  - Estrazione di chiavi via side-channel cross-VM. Estende l'analisi dell'isolamento nel cloud (modulo 10).

- **[Antonakakis et al. 2017]** Antonakakis, M., et al. (2017). "Understanding the Mirai Botnet." *USENIX Security Symposium*, 1093-1110.
  - Analisi empirica della botnet Mirai (IoT). Rilevante per honeypot e minacce IoT (moduli 06, 08).

---

## I. ricognizione e superficie d'attacco

- **[Manadhata & Wing 2011]** Manadhata, P. K., & Wing, J. M. (2011). "An Attack Surface Metric." *IEEE Transactions on Software Engineering*, 37(3), 371-386.
  - Formalizzazione quantitativa della superficie d'attacco. Fondamento teorico del modulo 01 (ricognizione) e dell'hardening (modulo 08).

- **[Durumeric et al. 2013a]** Durumeric, Z., Wustrow, E., & Halderman, J. A. (2013). "ZMap: Fast Internet-Wide Scanning and Its Security Applications." *USENIX Security Symposium*, 605-620.
  - Scansione dell'intero spazio IPv4 in tempi ridotti; cambia l'economia della ricognizione. Base quantitativa del modulo 01.

- **[Durumeric et al. 2013b]** Durumeric, Z., Kasten, J., Bailey, M., & Halderman, J. A. (2013). "Analysis of the HTTPS Certificate Ecosystem." *ACM Internet Measurement Conference (IMC)*, 291-304.
  - Misurazione empirica dell'ecosistema dei certificati; rilevante per la ricognizione via Certificate Transparency (modulo 01).

---

## J. ingegneria sociale (fondamenti psicologici)

- **[Cialdini 1984]** Cialdini, R. B. (1984). *Influence: The Psychology of Persuasion*. Harper Business.
  - I sei principi dell'influenza (reciprocita, impegno/coerenza, riprova sociale, autorita, simpatia, scarsita). Fondamento psicologico del modulo 05.

- **[Kahneman 2011]** Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.
  - Teoria del doppio processo (System 1 euristico / System 2 analitico). Fondamento del perche l'elaborazione euristica e sfruttabile dall'ingegneria sociale (modulo 05).

- **[Reason 1990]** Reason, J. (1990). *Human Error*. Cambridge University Press.
  - Modello dell'errore umano (Swiss cheese model, slips/lapses/mistakes). Base per l'analisi socio-tecnica dell'anello debole (modulo 05).

---

## N. provable security, modelli formali e semantica (livello magistrale)

- **[Goldwasser & Micali 1984]** Goldwasser, S., & Micali, S. (1984). "Probabilistic Encryption." *Journal of Computer and System Sciences*, 28(2), 270-299.
  - Nozione di sicurezza semantica e indistinguibilita computazionale. Fondamento della provable security (THEORY-ADVANCED, Parte I).

- **[Bellare & Rogaway 1993]** Bellare, M., & Rogaway, P. (1993). "Random Oracles are Practical: A Paradigm for Designing Efficient Protocols." *ACM CCS*, 62-73.
  - Il Random Oracle Model. Base dell'analisi di concrete security dell'attacco offline (THEORY-ADVANCED, Parti I-II).

- **[Bellare et al. 1997]** Bellare, M., Desai, A., Jokipii, E., & Rogaway, P. (1997). "A Concrete Security Treatment of Symmetric Encryption." *IEEE FOCS*, 394-403.
  - Trattamento di concrete security (nozioni (t, eps)-sicure). Riferimento per la Parte I di THEORY-ADVANCED.

- **[Shoup 2004]** Shoup, V. (2004). "Sequences of Games: A Tool for Taming Complexity in Security Proofs." IACR ePrint 2004/332.
  - Metodologia delle dimostrazioni per sequenze di giochi. Riferimento metodologico (THEORY-ADVANCED, Parte I).

- **[Canetti et al. 1998]** Canetti, R., Goldreich, O., & Halevi, S. (1998). "The Random Oracle Methodology, Revisited." *ACM STOC*, 209-218.
  - Limiti del ROM (schemi sicuri nel ROM ma non istanziabili). Caveat dichiarato nella Parte I.

- **[Massey 1994]** (gia in sezione B) - guessing entropy; usato formalmente nella Parte II.

- **[Lowe 1997]** Lowe, G. (1997). "A Hierarchy of Authentication Specifications." *IEEE Computer Security Foundations Workshop (CSFW)*, 31-43.
  - Gerarchia di autenticazione (aliveness, weak/non-injective/injective agreement). Base della Parte III e della lettura di KRACK come perdita di injective agreement.

- **[Abadi & Rogaway 2002]** Abadi, M., & Rogaway, P. (2002). "Reconciling Two Views of Cryptography (The Computational Soundness of Formal Encryption)." *Journal of Cryptology*, 15(2), 103-127.
  - Relazione tra modello simbolico (Dolev-Yao) e computazionale. Parte III.

- **[Denning 1976]** Denning, D. E. (1976). "A Lattice Model of Secure Information Flow." *Communications of the ACM*, 19(5), 236-243.
  - Modello a reticolo del flusso di informazione. Parte IV.

- **[Goguen & Meseguer 1982]** Goguen, J. A., & Meseguer, J. (1982). "Security Policies and Security Models." *IEEE Symposium on Security and Privacy*, 11-20.
  - Definizione formale di non-interferenza. Parte IV, applicata a canali covert (modulo 07) e isolamento tenant (modulo 10).

- **[Katz & Lindell 2020]** Katz, J., & Lindell, Y. (2020). *Introduction to Modern Cryptography* (3rd ed.). CRC Press.
  - Testo di riferimento per definizioni game-based, riduzioni e argomento ibrido (THEORY-ADVANCED, Parte I).

- **[Goldreich 2001]** Goldreich, O. (2001). *Foundations of Cryptography, Volume I: Basic Tools*. Cambridge University Press.
  - Trattazione rigorosa di PRF, indistinguibilita e riduzioni. Parte I.

---

## K. testi di riferimento (monografie)

- **[Anderson 2020]** Anderson, R. (2020). *Security Engineering: A Guide to Building Dependable Distributed Systems* (3rd ed.). Wiley.
- **[Bishop 2018]** Bishop, M. (2018). *Computer Security: Art and Science* (2nd ed.). Addison-Wesley.
- **[Shostack 2014]** Shostack, A. (2014). *Threat Modeling: Designing for Security*. Wiley.

---

## L. standard e letteratura grigia normativa

- **NIST SP 800-61 Rev. 2** - Computer Security Incident Handling Guide (moduli 08, 09).
- **NIST SP 800-63B** - Digital Identity Guidelines: Authentication and Lifecycle Management (moduli 04, 07, 10).
- **NIST SP 800-115** - Technical Guide to Information Security Testing and Assessment (moduli 01, 02).
- **NIST SP 800-145** - The NIST Definition of Cloud Computing (modulo 10).
- **NIST SP 800-190** - Application Container Security Guide (modulo 10).
- **MITRE ATT&CK** - Adversarial Tactics, Techniques, and Common Knowledge (tutti i moduli).
- **MITRE D3FEND** - A Knowledge Graph of Cybersecurity Countermeasures (moduli 08, 09, 10).
- **CVSS v3.1** - Common Vulnerability Scoring System Specification, FIRST.org (modulo 02).
- **CIS Benchmarks** - Center for Internet Security (moduli 08, 10).
- **OWASP Top 10 / OWASP Testing Guide** (modulo 03).
- **RFC 6962** - Certificate Transparency (modulo 01).
- **Verizon DBIR** - Data Breach Investigations Report (annuale; contesto empirico trasversale).

---

## O. Active Directory, Kerberos e PKI

- **[Needham & Schroeder 1978]** Needham, R. M., & Schroeder, M. D. (1978). "Using Encryption for Authentication in Large Networks of Computers." *Communications of the ACM*, 21(12), 993-999.
  - Protocollo di autenticazione a terza parte fidata, antenato concettuale di Kerberos (modulo 11).
- **[Bellovin & Merritt 1991]** Bellovin, S. M., & Merritt, M. (1991). "Limitations of the Kerberos Authentication System." *USENIX Winter Technical Conference*.
  - Analisi critica classica di Kerberos: assunzioni, attacchi offline su password (modulo 11).
- **[Neuman et al. 2005]** Neuman, C., Yu, T., Hartman, S., & Raeburn, K. (2005). "The Kerberos Network Authentication Service (V5)." RFC 4120.
  - Specifica di Kerberos v5: flusso AS/TGS/AP, TGT/TGS, pre-autenticazione (modulo 11).
- **[Raeburn 2005]** Raeburn, K. (2005). "Advanced Encryption Standard (AES) Encryption for Kerberos 5." RFC 3962.
  - String-to-key AES (PBKDF2, 4096 iterazioni): base dell'analisi quantitativa del Kerberoasting (modulo 11).
- **[Medin 2014]** Medin, T. (2014). "Attacking Microsoft Kerberos: Kicking the Guard Dog of Hades." DerbyCon 4.0.
  - Introduzione operativa del Kerberoasting (modulo 11).
- **[Delpy & Le Toux 2015]** Delpy, B., & Le Toux, V. (2015). "DCSync" (Mimikatz `lsadump::dcsync`).
  - Replica abusata (MS-DRSR) per estrarre i segreti di dominio (modulo 11).
- **[Schroeder & Christensen 2021]** Schroeder, W., & Christensen, L. (2021). "Certified Pre-Owned: Abusing Active Directory Certificate Services." SpecterOps.
  - Sistematizzazione degli attacchi AD CS (ESC1-ESC8+) (modulo 11).

---

> **Nota:** Questa bibliografia elenca fonti reali e verificabili. Le citazioni sono fornite a scopo
> educativo e di inquadramento scientifico del lavoro di laboratorio. Si raccomanda la consultazione
> diretta delle fonti primarie: le annotazioni ne riassumono la rilevanza ma non ne sostituiscono la lettura.
