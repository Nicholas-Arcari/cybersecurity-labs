> [English](README.en.md) | **Italiano**

# Modelli formali - verifica di protocollo

> - **Livello:** Verifica formale (metodi formali applicati a un protocollo di sicurezza)
> - **Scopo:** Fornire un modello formale eseguibile e verificato di un protocollo, come artefatto di livello di ricerca complementare alla teoria (`THEORETICAL-FOUNDATIONS`) e alla misura empirica (`EVALUATION`).
> - **Prerequisiti:** Python 3 (solo standard library). Per il modello Tamarin opzionale: Tamarin prover.

---

## Perche esiste questa cartella

I `THEORETICAL-FOUNDATIONS.md` argomentano le proprieta di sicurezza; `EVALUATION/` le *misura*
empiricamente. Questa cartella aggiunge il terzo metodo del rigore accademico: la **verifica formale**
di un protocollo, ossia la dimostrazione esaustiva - non per test, ma su tutto lo spazio degli stati -
che una proprieta di sicurezza vale (o l'esibizione meccanica di un controesempio quando non vale).

Il caso di studio e il **4-way handshake di WPA2** e la sua vulnerabilita **KRACK**
(Key Reinstallation Attack, [Vanhoef & Piessens 2017]). E il complemento naturale del modulo 06,
sez. 3.5, dove si sostiene - a parole - che KRACK e un difetto della *macchina a stati* del protocollo
e non delle primitive crittografiche. Qui quella tesi e **dimostrata meccanicamente**.

---

## Struttura della cartella

```
FORMAL-MODELS/
+-- README.md                          # questo file
|
+-- wpa2-4way-handshake/
    +-- handshake_model_checker.py     # model checker a stati espliciti LIMITATO (ESEGUITO): trova KRACK
    +-- inductive_verification.py      # verifica NON-LIMITATA via invariante induttivo (ESEGUITO): prova il fix
    +-- results.md                     # output verbatim reale di ENTRAMBI + lettura
    +-- wpa2_handshake.spthy           # modello Tamarin di riferimento (NON eseguito qui; per il tool)
```

Due artefatti eseguiti, complementari, che insieme costituiscono un risultato di verifica formale:
il **model checker limitato** *trova* il bug (controesempio KRACK concreto), l'**invariante induttivo**
*dimostra* la sua assenza nel modello patchato per esecuzioni di lunghezza arbitraria (senza bound).

---

## Risultato (prodotto dall'esecuzione)

Il model checker definisce la macchina a stati del supplicant WPA2 sotto un avversario Dolev-Yao che
puo **rigiocare il Messaggio 3**, e verifica l'invariante di *freshness*:

> **La PTK e installata al piu una volta per handshake** (equivalente: il contatore del packet-number
> dei frame dati non viene mai azzerato dopo essere stato avanzato). La sua violazione E KRACK.

Due modelli, verificati esaustivamente:

- **VULNERABILE** (il supplicant reinstalla la PTK su ogni M3, anche rigiocato): il model checker
  **trova un controesempio** in 6 stati - una traccia concreta a 4 passi in cui il replay di M3
  induce una seconda installazione (`installs=2`) che azzera il contatore, riuso dei nonce, 
  riuso del keystream. E KRACK, trovato meccanicamente.
- **PATCHED** (il supplicant non reinstalla su un M3 rigiocato): il model checker **verifica**
  l'invariante su tutti i 7 stati raggiungibili - nessuna reinstallazione e raggiungibile.

Cio dimostra formalmente che KRACK vive nella logica di stato del protocollo: le primitive (MIC, PRF)
sono assunte **perfette** (Dolev-Yao) e l'attacco esiste comunque; il fix (non reinstallare) lo
elimina. Output verbatim e lettura completa in
[`wpa2-4way-handshake/results.md`](wpa2-4way-handshake/results.md).

---

## Riproducibilita

```Bash
# 1) Model checker LIMITATO (eseguito) - trova il controesempio KRACK - < 1 s
python3 wpa2-4way-handshake/handshake_model_checker.py

# 2) Verifica NON-LIMITATA via invariante induttivo (eseguito) - prova il fix senza bound - < 1 s
python3 wpa2-4way-handshake/inductive_verification.py

# 3) Modello Tamarin di riferimento (richiede il prover Tamarin, NON incluso ne eseguito qui)
tamarin-prover --prove wpa2-4way-handshake/wpa2_handshake.spthy
```

Il model checker Python e deterministico ed esaustivo: ogni riesecuzione riproduce esattamente il
`results.md`.

---

## Nota metodologica onesta (perimetro e disciplina di integrita)

- **Cosa e "formale" qui.** Il model checking a stati espliciti e verifica formale a pieno titolo
  (esplorazione esaustiva + invariante), lo stesso nucleo di SPIN/TLC, qui in Python stdlib per essere
  autocontenuto. Il risultato e il controesempio sono **prodotti dall'esecuzione**, non asseriti.
- **Astrazione dichiarata.** Modello simbolico a livello di logica di protocollo: primitive astratte
  (Dolev-Yao), solo lo stato rilevante per KRACK, contatore dei nonce limitato (standard nel model
  checking a stati finiti). Entro l'astrazione, la verifica e esaustiva ed esatta. Non e una prova
  al livello del bit ne dell'intera macchina a stati 802.11.
- **Il modello Tamarin non e stato eseguito qui.** Tamarin non e installato in questo ambiente:
  `wpa2_handshake.spthy` e fornito come artefatto runnable da validare col tool reale, e cosi
  etichettato nel file. Non spaccio come verificato cio che non ho eseguito - l'artefatto
  verificato-per-esecuzione e il model checker Python.
- **Bounded vs unbounded (affrontato).** Il limite "solo fino a profondita k" del model checker
  limitato e superato da `inductive_verification.py`, che dimostra il fix per esecuzioni di lunghezza
  arbitraria via invariante induttivo. Resta il limite dell'astrazione simbolica (Dolev-Yao); una
  meccanizzazione con le garanzie di soundness/completeness di un prover dedicato richiede Tamarin/
  ProVerif eseguiti (il modello `.spthy` e pronto ma non eseguito qui).
- **Fuori portata (dichiarato).** La peer review esterna resta fuori dalla portata di un repository:
  vedi la self-assessment avversariale in `../SELF-ASSESSMENT.md`, che ne affronta onestamente la
  *funzione* (trovare i difetti) senza rivendicarne il *credenziale*.

---

## Riferimenti

- [Vanhoef & Piessens 2017] - KRACK (Key Reinstallation Attacks), il fenomeno modellato.
- [Dolev & Yao 1983] - modello dell'avversario di rete adottato.
- Fondamenti teorici collegati in
  `../06-wireless-security/THEORETICAL-FOUNDATIONS.md` (sez. 3.3 freshness, 3.5 KRACK).
  Dettagli bibliografici in `../REFERENCES.md`.
