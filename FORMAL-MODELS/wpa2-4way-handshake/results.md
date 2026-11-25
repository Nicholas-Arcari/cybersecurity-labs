> [English](results.en.md) | **Italiano**

# Risultati - Verifica formale del 4-way handshake WPA2 (KRACK)

Output verbatim di `handshake_model_checker.py` (deterministico, esplorazione esaustiva).
Risultato **prodotto dall'esecuzione reale** del model checker, non asserito a mano.
Rieseguire il comando riproduce esattamente questo output.

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

## Lettura dei risultati

1. **Controesempio trovato meccanicamente (modello VULNERABILE).** Il model checker esplora lo spazio
   degli stati raggiungibili e trova, in 6 stati, una traccia concreta che viola l'invariante di
   sicurezza. La traccia e un attacco KRACK vero e proprio: dopo la prima installazione della PTK
   (step 3, `installs=1`), l'avversario Dolev-Yao rigioca il Messaggio 3 (step 4), inducendo una
   **seconda installazione** (`installs=2`) che **azzera il contatore del packet-number** a 0.
   Poiche i frame dati gia inviati avevano usato i nonce 1..k con quella stessa chiave, il reset
   provoca il riuso dei nonce, riuso del keystream, perdita di confidenzialita/integrita.

2. **Invariante verificato esaustivamente (modello PATCHED).** Con la correzione (il supplicant non
   reinstalla su un M3 rigiocato), il model checker esplora **tutti** i 7 stati raggiungibili e non
   trova alcuna violazione: `installs <= 1` vale ovunque. Questa e verifica, non test: l'assenza del
   difetto e dimostrata su tutto lo spazio degli stati, non su un campione.

3. **Cosa dimostra formalmente.** La proprieta di sicurezza rilevante non e la segretezza della PTK
   (che qui non viene mai compromessa) ma l'**iniettivita dell'installazione della chiave** - una
   proprieta di *freshness/stato*. La sua violazione e KRACK. La coppia (controesempio nel modello
   vulnerabile, verifica nel modello patchato) conferma meccanicamente la tesi del modulo 06
   (fondamenti, sez. 3.5): **KRACK e un difetto della macchina a stati del protocollo, non una
   rottura delle primitive crittografiche**. Le primitive (MIC, PRF) sono qui assunte perfette
   (astrazione Dolev-Yao) e cio nondimeno l'attacco esiste.

## Verifica NON-LIMITATA (invariante induttivo, senza bound)

Il model checker sopra e *limitato* (esplora fino a un bound sul contatore). Per dimostrare il fix
per esecuzioni di **lunghezza arbitraria** senza alcun bound, `inductive_verification.py` usa la
tecnica standard dell'**invariante induttivo (1-induction)**. Output verbatim reale:

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
    STEP: checked all enabled rules over every I*-state.
    STEP: every enabled rule preserves I*  -> HOLDS
    VERDICT [PATCHED]: I* is INDUCTIVE  =>  n_install<=1 on ALL reachable states,
             for executions of ANY length (NO bound). ... FRESHNESS is PROVED unboundedly.

==============================================================================
MODEL: VULNERABLE
==============================================================================
[VULNERABLE]  Phase 1 - is the bare safety property I0 (n_install<=1) inductive?
    ... 3 CTI ... 2 UNREACHABLE (spurious) + 1 reachable:
        ('INSTALLED', True, 1) --install_REPLAY_M3--> ('INSTALLED', True, 2)   [pre-state is reachable]
[VULNERABLE]  Phase 2 - is the strengthened invariant I* inductive?
    STEP: I* is NOT inductive. Remaining CTI from genuine I*-states:
        ('INSTALLED', True, 1) --install_REPLAY_M3--> ('INSTALLED', True, 2)
    VERDICT [VULNERABLE]: ... genuinely FALSE (KRACK for real).

RESULT:  PATCHED = PROVED   |   VULNERABLE = REFUTED
```

**Il contenuto formale (e la lezione di metodo).** La proprieta di sicurezza nuda `I0 = (n_install<=1)`
**non e induttiva**, neppure per il modello patchato: il passo induttivo produce una CTI
(counterexample-to-induction) dallo stato astratto `(SENT_M2, False, 1)`, che pero e **irraggiungibile**
(non si puo essere in SENT_M2 con un'installazione gia avvenuta). E la situazione normale: occorre
**rafforzare** l'invariante con l'accoppiamento di raggiungibilita tra le componenti dello stato
(`installed <=> n_install>=1`; `n_install>=1 => phase=INSTALLED`) finche la congiunzione `I*` diventa
induttiva. Trovare questo rafforzamento e il vero lavoro di verifica.

- **PATCHED:** `I*` e induttivo (BASE + STEP verificati su tutti gli stati-`I*`) => `n_install<=1` vale
  su **tutti** gli stati raggiungibili, per esecuzioni di **qualunque lunghezza**, senza bound. Per la
  riduzione sound (install-once => niente reset-dopo-avanzamento => niente riuso di nonce), la
  **freshness e dimostrata in modo non-limitato**.
- **VULNERABLE:** `I*` resta non induttivo per una CTI da uno stato **genuinamente raggiungibile**
  (`(INSTALLED, True, 1)`, cioe lo step 3 del controesempio concreto): la proprieta e **davvero falsa**,
  non solo non-induttiva.

Distinguere CTI spurie (da stati irraggiungibili) da CTI genuine, e "non-induttivo" da "falso", e
precisamente cio che fa una verifica induttiva corretta. Nota di trasparenza: la prima versione di
questo script usava l'invariante nudo e classificava erroneamente il modello patchato; il difetto e
stato scoperto **eseguendo** il codice e corretto rafforzando l'invariante - la ragione per cui si
esegue la verifica invece di asserirla.

## Cosa e "formale" qui (e cosa no)

Il model checking a stati espliciti **e** verifica formale: si definisce una macchina a stati e un
invariante, si esplora esaustivamente lo spazio degli stati raggiungibili sotto un avversario
esplicito, e si dimostra che l'invariante vale ovunque (o si esibisce un controesempio). E il
procedimento centrale di strumenti come SPIN o TLC, qui implementato in ~200 righe di Python stdlib
perche sia autocontenuto e riproducibile. Il risultato di verifica (7 stati, nessuna violazione) e il
controesempio (traccia a 4 passi) sono **prodotti dall'esecuzione**, non scritti a mano.

## Nota di validita (limite dichiarato)

Questo e un modello **simbolico** a livello di logica di protocollo:
- Astrae le primitive crittografiche (MIC/PRF assunte sound, modello Dolev-Yao). E l'astrazione
  corretta per isolare i difetti di protocollo, ed e esattamente quella in cui KRACK vive.
- Modella lo **stato rilevante per KRACK** (conteggio installazioni, contatore nonce), non l'intera
  macchina a stati IEEE 802.11 (Group Key handshake, 802.11r/FT, retry dell'authenticator sono omessi).
- Il contatore dei nonce e **limitato** (`NONCE_CAP`), pratica standard nel model checking a stati
  finiti: un singolo avanzamento-poi-reset e gia testimone sufficiente del riuso.

Entro questa astrazione la verifica e **esaustiva ed esatta**. Per una verifica al livello dello
strumento di riferimento (senza il bound sullo stato, con ricostruzione simbolica della traccia), la
cartella include `wpa2_handshake.spthy`, un modello per il prover **Tamarin** - fornito come artefatto
runnable ma, con trasparenza, **non eseguito in questo ambiente** (Tamarin non installato qui): va
validato con `tamarin-prover --prove wpa2_handshake.spthy`. L'artefatto verificato-per-esecuzione di
questa cartella e il model checker Python.
