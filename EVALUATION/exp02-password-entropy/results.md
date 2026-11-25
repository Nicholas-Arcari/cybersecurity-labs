> [English](results.en.md) | **Italiano**

# Risultati - esperimento b (entropia di guessing vs shannon)

Output verbatim di `guessing_entropy.py` (deterministico, riproducibile). Numeri **calcolati**
esattamente sul modello Zipf, non stimati.

```
==========================================================================
EXPERIMENT B - Shannon entropy vs guessing metrics (Zipf password model)
V=1,000,000 ranked passwords,  Zipf exponent s=1.0
==========================================================================

Most probable password mass  p_max = 6.9480e-02  (the single most common password covers 6.95% of accounts)
Shannon entropy    H1   =   13.406 bits   (nominal 'strength' = 2^H1 candidates)
Min-entropy        Hinf =    3.847 bits   (resistance to the single best guess)
Mean guessing ent. G    = 69,480 guesses = 16.084 bits (log2 G, Massey 1994)

NOTE (methodological, Bonneau 2012): the MEAN guessing entropy G here EXCEEDS H1.
This is not an error - it is the known failure of mean guessing entropy as a security
metric: the arithmetic mean is dominated by the heavy tail (the rare passwords that need
many guesses pull the average up), hiding the fact that the HEAD of the distribution is
weak. The attacker-relevant metrics are the min-entropy and the partial guessing curve.

Shannon overestimates single-guess resistance by H1 - Hinf = 9.559 bits.

Alpha-work-factor (guesses needed to crack a fraction alpha of accounts):
   alpha |   guesses needed |  equiv. bits log2(k)
----------------------------------------------------
     10% |                2 |                 1.00
     25% |               21 |                 4.39
     50% |              749 |                 9.55
     75% |           27,373 |                14.74
     90% |          237,100 |                17.86

Guessing curve (fraction of accounts cracked after k in-order guesses):
   guesses k |   fraction cracked |  equiv. bits log2(k)
------------------------------------------------------------
           1 |             6.95% |                 0.00
          10 |            20.35% |                 3.32
         100 |            36.04% |                 6.64
       1,000 |            52.01% |                 9.97
      10,000 |            68.00% |                13.29
     100,000 |            84.00% |                16.61
```

## Lettura dei risultati

1. **Shannon sovrastima la resistenza pratica.** L'entropia di Shannon nominale e 13.4 bit, ma la
   min-entropy e solo **3.85 bit**: la password piu comune copre da sola il 6.95% degli account.
   Shannon sovrastima la resistenza al singolo tentativo di **9.56 bit** (un fattore ~750x).

2. **Sottigliezza metodologica (e conferma di Bonneau 2012).** La guessing entropy **media** (Massey)
   risulta 16.08 bit, cioe *maggiore* di Shannon. Non e un errore: e il noto fallimento della media
   come metrica di sicurezza, dominata dalla coda pesante. L'esperimento riproduce empiricamente
   proprio la critica che ha portato [Bonneau 2012] a proporre le metriche di **partial guessing**.

3. **Alpha-work-factor: la metrica corretta.** I tentativi necessari a craccare una frazione degli
   account sono bassissimi in testa alla distribuzione: **2 tentativi, 10%**, **21, 25%**,
   **749, 50%**. Un attaccante a dizionario cracca la **maggioranza** degli account (52%) in
   ~1.000 tentativi (~2^10), contro una "forza" nominale di 2^13.4 ~ 10.855 candidati.

4. **Implicazione.** La resistenza pratica e governata dalla testa della distribuzione, non
   dall'entropia nominale dello spazio dei caratteri. E il fondamento quantitativo, misurato, degli
   attacchi a dizionario e rule-based (modulo 04, sez. 3.3) e del perche la robustezza della PSK
   WPA2/WPA3 dipenda dalla guessing entropy della passphrase e non dal suo spazio nominale
   (modulo 06, sez. 3.2 e 4.2).

## Nota di validita (limite dichiarato)

La distribuzione e un **modello Zipf** (esponente `s=1.0`) parametrizzato dalla letteratura
([Bonneau 2012]; Malone & Maher), non uno specifico corpus violato. Le quantita sono esatte per il
modello. Il risultato - il divario tra entropia nominale e resistenza pratica - e guidato dalla
*forma* (fortemente sbilanciata) della distribuzione ed e robusto rispetto all'esponente esatto:
vale per qualunque popolazione realistica di password. Per una misura su corpus reale, sostituire
`zipf_probs()` con le frequenze empiriche di un dataset mantenendo invariato il calcolo delle metriche.
