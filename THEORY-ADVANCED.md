> [English](THEORY-ADVANCED.en.md) | **Italiano**

# Teoria avanzata - provable security, autenticazione, flusso di informazione

> - **Livello:** Magistrale (capitolo di teoria rigoroso: definizioni, teoremi, dimostrazioni).
> - **Scopo:** Portare l'apparato teorico della repository al livello di un testo di crittografia e
>   metodi formali, colmando cio che i `THEORETICAL-FOUNDATIONS` di modulo trattano a livello concettuale:
>   definizioni di sicurezza game-based, dimostrazioni per riduzione, argomento ibrido, gerarchia di
>   autenticazione, non-interferenza.
> - **Prerequisiti:** algebra e probabilita di base, nozioni di complessita (PPT), i foundations dei
>   moduli 03, 04, 06, 07, 08, 10.
> - **Convenzioni:** notazione `[Autore Anno]` verso `REFERENCES.md`. Matematica in testo semplice e
>   code block. `negl` = funzione trascurabile; `Adv` = vantaggio dell'avversario; `<-$` = campionamento
>   uniforme; `PPT` = probabilistic polynomial-time.

---

## Indice

- Parte I - Fondamenti di Provable Security (definizioni game-based, riduzioni, ibridi)
- Parte II - Concrete security dell'attacco offline: il Teorema di Guessing (con dimostrazione)
- Parte III - Autenticazione nei protocolli: la gerarchia di Lowe e KRACK
- Parte IV - Controllo degli accessi e non-interferenza

---

## Parte i - fondamenti di provable security

La provable security definisce la sicurezza come una proprieta relativa a un **modello di avversario**
e la dimostra per **riduzione** a un problema ritenuto difficile. Questa parte fissa il linguaggio.

### I.1 modello computazionale e trascurabilita

**Definizione I.1 (funzione trascurabile).** `mu: N -> R+` e trascurabile se per ogni polinomio `p`
esiste `N` tale che `mu(n) < 1/p(n)` per ogni `n > N`. Si scrive `mu(n) = negl(n)`. Intuizione: decresce
piu velocemente dell'inverso di ogni polinomio.

**Definizione I.2 (avversario PPT).** Un avversario e un algoritmo probabilistico che termina in tempo
polinomiale nel parametro di sicurezza `n` (tipicamente la lunghezza della chiave). La sicurezza
"asintotica" quantifica su tutti gli avversari PPT; la sicurezza "concreta" (I.7) fissa risorse esplicite.

### I.2 indistinguibilita computazionale

**Definizione I.3 (indistinguibilita, [Goldwasser & Micali 1984]).** Due ensemble di distribuzioni
`X = {X_n}` e `Y = {Y_n}` sono computazionalmente indistinguibili, `X ~c Y`, se per ogni distinguitore
PPT `D`:

```
Adv_{X,Y}(D) := | Pr[ D(1^n, X_n) = 1 ] - Pr[ D(1^n, Y_n) = 1 ] |  =  negl(n).
```

E la nozione centrale: "sicuro" significa "indistinguibile da un ideale" (una funzione casuale, un
cifrato di zero, ecc.).

### I.3 definizioni game-based

Le proprieta di sicurezza si esprimono come **giochi** tra un challenger e l'avversario; la sicurezza e
un limite sul vantaggio.

**Definizione I.4 (PRF - Pseudorandom Function).** Sia `F: {0,1}^k x {0,1}^m -> {0,1}^n`. Per un
distinguitore `D` con accesso a un oracolo, il vantaggio PRF e:

```
Adv^{prf}_F(D) := | Pr[ K <-$ {0,1}^k : D^{F_K(.)} = 1 ]  -  Pr[ f <-$ Func(m,n) : D^{f(.)} = 1 ] |
```

dove `Func(m,n)` e l'insieme di tutte le funzioni da `{0,1}^m` a `{0,1}^n`. `F` e una PRF se
`Adv^{prf}_F(D) = negl` per ogni `D` PPT. Le PRF sono i mattoni di MAC, cifrari, KDF.

**Definizione I.5 (IND-CPA, cifratura).** Nel gioco left-or-right, il challenger sceglie
`b <-$ {0,1}` e una chiave `K`; l'avversario `A` invia coppie `(m_0, m_1)` di egual lunghezza e riceve
`Enc_K(m_b)`; alla fine restituisce `b'`. Il vantaggio e:

```
Adv^{ind-cpa}_{Enc}(A) := | 2 * Pr[ b' = b ] - 1 |.
```

`Enc` e IND-CPA sicura se il vantaggio e `negl` per ogni `A` PPT. Implica che il cifrato non rivela
nulla sul messaggio (semantica).

**Definizione I.6 (EUF-CMA, autenticazione dei messaggi).** Per un MAC `Mac_K`, l'avversario ha accesso
a un oracolo di tag su messaggi a scelta e vince se produce `(m*, t*)` con `Vrfy_K(m*, t*) = 1` e `m*`
mai interrogato. `Mac` e EUF-CMA (existential unforgeability under chosen-message attack) sicuro se

```
Adv^{euf-cma}_{Mac}(A) := Pr[ A vince ]  =  negl.
```

### I.4 il metodo della riduzione

Per dimostrare che uno schema `Pi` e sicuro **assumendo** che una primitiva `P` lo sia, si procede per
contrapposizione: da un avversario `A` che rompe `Pi` si costruisce un avversario `B` che rompe `P`, con
vantaggi legati. Se `P` e sicura (`Adv(B) = negl`), allora `Adv(A) = negl`.

**Teorema I.1 (una PRF e un MAC sicuro).** Se `F` e una PRF, allora `Mac_K(m) := F_K(m)` e EUF-CMA
sicuro, e per ogni avversario `A` che effettua `q` query esiste `B` (PPT, con circa le stesse risorse)
tale che

```
Adv^{euf-cma}_{Mac}(A)  <=  Adv^{prf}_F(B)  +  2^{-n}.
```

*Dimostrazione (riduzione).* `B` ha un oracolo `O` (che e `F_K` oppure una funzione casuale `f`) e
simula il gioco EUF-CMA per `A`: risponde a ogni query di tag `m_i` con `O(m_i)`. Quando `A` produce
`(m*, t*)` con `m*` fresco, `B` interroga `O(m*)` e restituisce 1 sse `t* = O(m*)`.
- Se `O = F_K`, `B` simula perfettamente il MAC reale, quindi `Pr[B=1 | O=F_K] = Pr[A vince]`.
- Se `O = f` casuale, `f(m*)` e uniforme e indipendente da tutto cio che `A` ha visto (m* e fresco),
  quindi `Pr[t* = f(m*)] = 2^{-n}`, cioe `Pr[B=1 | O=f] = 2^{-n}`.
Per la Definizione I.4, `Adv^{prf}_F(B) = |Pr[B=1|F_K] - Pr[B=1|f]| = |Adv^{euf-cma}(A) - 2^{-n}|`, da
cui la tesi. ∎

Questo e il paradigma: la sicurezza di `Mac` e *ridotta* a quella di `F`. Lo stesso schema fonda l'uso
di HMAC (usato nel MIC del 4-way handshake) e la derivazione di chiave PBKDF2.

### I.5 l'argomento ibrido

Per passare dalla sicurezza su *un* oggetto a quella su *molti*, si usa l'**argomento ibrido**: si
interpone una sequenza di distribuzioni `H_0, H_1, ..., H_q` in cui `H_0` e il mondo "tutto reale" e
`H_q` il mondo "tutto ideale", con `H_{i-1}` e `H_i` che differiscono in un solo elemento.

**Lemma I.2 (ibrido / telescopico).** Se ogni coppia adiacente e indistinguibile con vantaggio `<= eps`,
allora `H_0` e `H_q` sono indistinguibili con vantaggio `<= q * eps`. *Dimostrazione.* Per la
disuguaglianza triangolare sui vantaggi:

```
|Pr[D(H_0)=1] - Pr[D(H_q)=1]|  <=  sum_{i=1}^{q} |Pr[D(H_{i-1})=1] - Pr[D(H_i)=1]|  <=  q * eps.  ∎
```

E lo strumento con cui, ad esempio, la sicurezza IND-CPA a messaggio singolo implica quella a messaggi
multipli, con perdita lineare nel numero di cifrari.

### I.6 il random oracle model

**Definizione I.7 (ROM, [Bellare & Rogaway 1993]).** Nel Random Oracle Model, una funzione hash `H` e
modellata come un oracolo che, su ogni input nuovo, restituisce un valore uniforme indipendente
(coerente sulle ripetizioni). Le prove nel ROM sono efficienti ed espressive; il ROM e una *euristica*:
[Canetti et al. 1998] esibiscono schemi sicuri nel ROM ma insicuri con ogni istanziazione concreta di
`H`. Se ne fa uso dichiarato nella Parte II.

### I.7 sicurezza concreta

**Definizione I.8 ((t, q, eps)-sicurezza, [Bellare et al. 1997]).** Uno schema e `(t, q, eps)`-sicuro se
ogni avversario che gira in tempo `<= t` ed effettua `<= q` query ha vantaggio `<= eps`. La sicurezza
concreta rende esplicito il legame risorse-vantaggio, essenziale per scegliere parametri reali (lunghezze
di chiave, iterazioni di un KDF). E il registro in cui lavora la Parte II.

---

## Parte II - concrete security dell'Attacco offline: il teorema di guessing

Colleghiamo il formalismo della Parte I all'attacco offline su WPA2-PSK (modulo 06) e alla misura
empirica (`EVALUATION/exp02`). Il risultato e un **bound di concrete security stretto**, dimostrato, il
cui valore coincide con la curva di guessing calcolata nell'esperimento.

### II.1 il gioco dell'indovinare offline

Un handshake catturato fornisce un *predicato di verifica* `V(w)` che vale 1 sse la passphrase candidata
`w` e quella corretta (via ricomputo del MIC). Modelliamo il KDF/MIC come oracolo casuale `H`
(Definizione I.7): l'unico modo per valutare `V(w)` e interrogare `H` su `w` (e sui valori pubblici
dell'handshake). La passphrase reale `W` e estratta da una distribuzione nota `D` sulle password, con
probabilita ordinate `p_1 >= p_2 >= ... >= p_N`.

**Definizione II.1 (avversario di guessing offline).** `A` effettua un insieme di query distinte
`Q = {w_1, ..., w_q}` a `H` e vince sse `W in Q`. La risorsa dominante e `q` (numero di verifiche).

### II.2 il teorema e la sua dimostrazione

**Teorema II.1 (bound stretto sul guessing offline).** Nel ROM, ogni avversario che effettua al piu `q`
query distinte recupera `W ~ D` con probabilita al piu

```
G_q(D) := sum_{i=1}^{q} p_i        (somma delle q probabilita maggiori),
```

e il bound e stretto: la strategia ottimale (interrogare le `q` password piu probabili) lo raggiunge.

*Dimostrazione.*
(Limite superiore) Poiche `H` e un oracolo casuale, per ogni candidato `w` non ancora interrogato il
valore `H(w, .)` e uniforme e indipendente; quindi nessuna informazione su `W` si ottiene senza
interrogare `w`, e la sola via per verificare `w` e includerlo in `Q`. Con `|Q| <= q` candidati distinti,
l'evento di vittoria e `W in Q`, di probabilita `Pr[W in Q] = sum_{w in Q} Pr[W = w]`. Questa somma di
`q` termini scelti da `{p_1, ..., p_N}` e massimizzata prendendo i `q` piu grandi, dunque
`Pr[W in Q] <= sum_{i=1}^{q} p_i = G_q(D)`.
(Strettezza) La strategia `Q* = {i : 1 <= i <= q}` (le `q` password piu probabili) da esattamente
`Pr[W in Q*] = G_q(D)`. ∎

**Osservazione (adattivita non aiuta).** Poiche gli output dell'oracolo sono indipendenti e privi di
struttura, l'ordine e l'adattivita delle query non cambiano l'insieme testato: il bound vale anche per
avversari adattivi. Questo isola il fatto che l'unica leva e *quali* `q` candidati testare, non *come*.

### II.3 corollari: entropia, min-entropia, guessing entropy

**Corollario II.2 (min-entropia = resistenza a una query).** Per `q = 1`,
`G_1 = p_1 = 2^{-H_inf(D)}` dove `H_inf(D) = -log2 p_1` e la min-entropia. La probabilita di successo al
primo tentativo e esattamente `2^{-H_inf}`, non `2^{-H_Shannon}`. Questo formalizza la sez. 3.3 del
modulo 04 e la sez. 3.2/4.2 del modulo 06: **la resistenza e governata dalla min-entropia (e in generale
dalla curva `G_q`), non dall'entropia di Shannon.**

**Corollario II.3 (guessing entropy attesa, [Massey 1994]).** Il numero atteso di tentativi della
strategia ottimale e `G(D) = sum_{i>=1} i * p_i`. E la guessing entropy media; la Parte empirica mostra
(coerente con [Bonneau 2012]) che la media e dominata dalla coda, per cui `G_q` e la metrica operativa,
non `G`.

### II.4 effetto del key stretching: query-hardness vs time-hardness

Il PBKDF2 con `c` iterazioni (modulo 06, sez. 3.2) non modifica `D` ne `G_q`: la *probabilita* di
successo dopo `q` verifiche e invariata. Cio che cambia e il **costo temporale** per query.

**Proposizione II.4 (trade-off tempo-query).** Se ogni valutazione di `V` richiede `c` valutazioni della
primitiva sottostante di costo `t_H`, allora ogni avversario che raggiunge probabilita di successo `G_q`
spende tempo `t >= q * c * t_H`. Dunque, a parita di probabilita bersaglio, il costo cresce linearmente
in `c`.

*Dimostrazione.* Per il Teorema II.1, raggiungere probabilita `G_q` richiede `q` query distinte; ciascuna
costa `c * t_H`; le query sono la risorsa dominante. ∎

**Interpretazione.** Il key stretching compra **time-hardness**, non **query-hardness**: non riduce la
probabilita per numero di tentativi (che dipende solo dalla distribuzione della passphrase), ma alza il
tempo per tentativo. La difesa efficace agisce quindi su *entrambi*: aumentare `H_inf(D)` (passphrase ad
alta entropia, che abbassa `G_q`) e aumentare `c` (che alza il tempo). Le funzioni memory-hard (scrypt,
Argon2, modulo 04) estendono l'argomento all'area di silicio, non solo al tempo.

### II.5 connessione con l'esperimento eseguito

Il Teorema II.1 non e astratto: `G_q(D)` e **esattamente** la curva di guessing calcolata in
`EVALUATION/exp02` per la distribuzione Zipf. La misura eseguita (`G_1000 = 0.52`, cioe il 52% degli
account cade in `q = 1000` query) e un'istanza numerica del bound stretto qui dimostrato. Teoria e misura
coincidono per costruzione: il bound e la curva, e la curva e stata calcolata.

---

## Parte III - autenticazione nei protocolli: la gerarchia di lowe e KRACK

I foundations del modulo 06 e la verifica formale (`FORMAL-MODELS/`) usano la parola "freshness". Qui la
si colloca nella tassonomia formale delle proprieta di autenticazione di [Lowe 1997], e si mostra
precisamente quale livello KRACK infrange.

### III.1 asserzioni di corrispondenza

Si annotano gli eventi di protocollo con `begin(A, B, d)` (il principale `A` inizia una sessione con `B`
e dati `d`) e `end(B, A, d)` (`B` completa credendo di aver parlato con `A` su `d`). Le proprieta di
autenticazione sono **asserzioni di corrispondenza** tra questi eventi, di forza crescente.

### III.2 la gerarchia di lowe

Dal piu debole al piu forte [Lowe 1997]:

1. **Aliveness:** se `B` completa `end(B, A, -)`, allora `A` ha eseguito il protocollo *in qualche
   momento* (non necessariamente con `B`, non necessariamente di recente).
2. **Weak agreement:** `A` ha eseguito il protocollo *apparentemente con B* (ma i dati possono differire).
3. **Non-injective agreement (su `d`):** `A` ha eseguito `begin(A, B, d)` con gli *stessi dati* `d`; puo
   pero corrispondere lo *stesso* run di `A` a *piu* completamenti di `B`.
4. **Injective agreement (su `d`):** esiste una corrispondenza **iniettiva** tra i completamenti di `B` e
   i run di `A`: ogni `end(B, A, d)` e appaiato a un `begin(A, B, d)` *distinto*.

**Iniettivita = assenza di replay.** L'injective agreement e precisamente la proprieta che nega il
replay: un singolo `begin` non puo giustificare due `end`. La *freshness* del modulo 06 e, formalmente,
la clausola di iniettivita.

### III.3 KRACK come perdita di injective agreement

Nel 4-way handshake, l'installazione della PTK da parte del supplicant e un evento `end` che dovrebbe
corrispondere iniettivamente a un `begin` dell'authenticator (l'invio *nuovo* del Messaggio 3). L'attacco
KRACK rigioca lo stesso Messaggio 3: **un unico `begin` viene appaiato a due `end` (due installazioni)**,
violando l'iniettivita pur preservando il non-injective agreement (i dati coincidono) e l'aliveness.

Questo e il ponte esatto con la verifica in `FORMAL-MODELS/`: l'invariante verificato la, `n_install <= 1`
(la PTK e installata al piu una volta), e la codifica operativa dell'**injective agreement** sull'evento
di installazione. Il controesempio del model checker e una violazione di iniettivita; la prova per
invariante induttivo del modello patchato e una prova di iniettivita. La gerarchia di Lowe fornisce il
nome formale della proprieta che i moduli 06 e FORMAL-MODELS trattano.

### III.4 modello simbolico vs computazionale

La verifica in `FORMAL-MODELS/` e nel **modello simbolico** (Dolev-Yao): le primitive sono termini
perfetti (un MIC e infalsificabile per assunzione), e si ragiona sulla struttura dei messaggi e sullo
stato. Il **modello computazionale** tratta le primitive come algoritmi con avversari PPT e vantaggi
(Parte I). I due sono legati dai risultati di **computational soundness** [Abadi & Rogaway 2002]: sotto
ipotesi appropriate, la sicurezza simbolica implica quella computazionale. La scelta del modello simbolico
per KRACK e corretta e deliberata: KRACK e un difetto di *stato/struttura*, indipendente dalla forza delle
primitive (che nel nostro modello sono assunte perfette e cio nondimeno l'attacco esiste), esattamente il
regime in cui l'analisi simbolica e piu adatta.

---

## Parte IV - controllo degli accessi e Non-Interferenza

I moduli 08 (hardening, controllo accessi) e 10 (isolamento cloud/tenant), e i canali covert del modulo
07, invocano proprieta che qui si formalizzano.

### IV.1 il reticolo del flusso di informazione

**Definizione IV.1 ([Denning 1976]).** Un modello di flusso e una tupla `(S, O, L, <=, join)` dove `L`
e un insieme di classi di sicurezza parzialmente ordinate da `<=` che formano un **reticolo** (esistono
`join` e `meet`). Un flusso da un oggetto di classe `a` a uno di classe `b` e permesso sse `a <= b`. La
politica e la struttura del reticolo; la sicurezza e l'assenza di flussi che violano `<=`.

### IV.2 Bell-LaPadula e biba

**Definizione IV.2 (BLP, confidenzialita, [Bell & LaPadula 1976]).** Con clearance dei soggetti e
classification degli oggetti nel reticolo:
- *Simple security property (no read up):* un soggetto di livello `l_s` puo leggere un oggetto di livello
  `l_o` solo se `l_o <= l_s`.
- *Star property (no write down):* puo scrivere `l_o` solo se `l_s <= l_o`.

**Proposizione IV.3.** Sotto BLP, nessuna sequenza di operazioni permesse crea un flusso da un oggetto
`High` a un soggetto `Low`. *Dimostrazione (schema).* Ogni lettura rispetta `l_o <= l_s` e ogni scrittura
`l_s <= l_o`; componendo, l'informazione puo solo salire nel reticolo, mai da `High` a `Low` (per
antisimmetria di `<=`). ∎

**Definizione IV.4 (Biba, integrita).** Duale di BLP con l'ordine invertito: *no read down, no write up*.
Protegge l'integrita (un soggetto ad alta integrita non legge dati a bassa integrita, ne quelli a bassa
integrita sono scritti in oggetti ad alta integrita). E il modello formale dietro l'integrita dei log
(modulo 08) e delle prove (modulo 09).

### IV.3 non-interferenza

BLP/Biba sono proprieta *sintattiche* (sulle operazioni). La non-interferenza e una proprieta
*semantica* (sui comportamenti osservabili), piu forte perche cattura anche i canali impliciti.

**Definizione IV.5 (non-interferenza, [Goguen & Meseguer 1982]).** Sia il sistema una macchina
deterministica su sequenze di comandi, con utenti partizionati in `High` e `Low`. Sia `purge_Low(w)` la
sequenza `w` da cui si eliminano tutti i comandi `High`. Il sistema e **non-interferente** se per ogni
sequenza `w`, l'osservazione dei soli utenti `Low` dopo `w` e uguale all'osservazione dopo `purge_Low(w)`:

```
obs_Low( run(w) )  =  obs_Low( run( purge_Low(w) ) )   per ogni w.
```

Intuizione: cio che fanno gli `High` non ha *alcun* effetto osservabile dai `Low`. La violazione di
questa uguaglianza *e* un canale (esplicito o covert) da `High` a `Low`.

### IV.4 applicazioni ai moduli

- **Canali covert ed esfiltrazione (modulo 07, [Lampson 1973]).** Un canale covert e precisamente una
  violazione di non-interferenza: un'attivita `High` (dati sensibili) altera un'osservazione `Low` (una
  temporizzazione, un volume DNS). La difesa "permetti e ispeziona" mira a ridurre la banda del canale;
  la non-interferenza perfetta (banda zero) e in generale irraggiungibile ([Lampson 1973], modulo 07,
  sez. 6), il che formalizza il limite dichiarato in quel modulo.
- **Isolamento dei tenant (modulo 10, [Ristenpart et al. 2009]).** L'isolamento multi-tenant e la
  richiesta di non-interferenza tra tenant distinti. I side-channel cross-VM sono la sua violazione
  dimostrata: l'attivita di un tenant `High` (una chiave usata) altera un'osservazione dell'altro tenant
  `Low` (latenza di cache). Cio spiega, in linguaggio formale, perche l'isolamento *logico* non implica
  la non-interferenza *fisica*.
- **Confidenzialita e integrita (moduli 08, 09).** BLP e Biba forniscono i modelli sintattici; il
  logging immutabile (modulo 07/09) e un'istanza di integrita alla Biba (i log non sono scrivibili
  dall'attaccante che li genera), e la sua efficacia contro l'anti-forensics e un enunciato di integrita.

---

## Sintesi

Questo capitolo ha portato l'apparato teorico al registro magistrale su quattro assi: (I) le definizioni
game-based, le riduzioni e l'argomento ibrido che costituiscono il metodo della provable security; (II) un
teorema di concrete security *dimostrato e stretto* sull'attacco offline, il cui bound coincide con la
misura eseguita in `EVALUATION/exp02` e che formalizza la resistenza delle passphrase WPA2 (modulo 06);
(III) la gerarchia di autenticazione di Lowe, che da il nome formale ("injective agreement") alla freshness
e collega esattamente la verifica in `FORMAL-MODELS/` a KRACK; (IV) i modelli a reticolo e la
non-interferenza, che formalizzano il controllo degli accessi, i canali covert (modulo 07) e l'isolamento
tenant (modulo 10). I `THEORETICAL-FOUNDATIONS` di modulo restano il livello concettuale e applicato;
questo documento ne e la controparte rigorosa.

**Onesta di livello.** Le dimostrazioni qui sono rigorose ma nel registro di un testo (definizione -
teorema - dimostrazione o schema di dimostrazione), non machine-checked (con l'eccezione della verifica
di protocollo in `FORMAL-MODELS/`, che e eseguita). Il Teorema II.1 e la Proposizione II.4 sono originali
nella formulazione ma standard nel contenuto (guessing nel ROM); i risultati citati (Teorema I.1, Lemma
I.2, Prop. IV.3) sono classici e riportati con dimostrazione o schema. Vedi `SELF-ASSESSMENT.md` per le
minacce alla validita.

---

## Riferimenti

Sottoinsieme di `REFERENCES.md` rilevante:

- [Goldwasser & Micali 1984], [Goldreich 2001], [Katz & Lindell 2020] - indistinguibilita, PRF, riduzioni.
- [Bellare et al. 1997], [Shoup 2004] - concrete security, giochi.
- [Bellare & Rogaway 1993], [Canetti et al. 1998] - Random Oracle Model e suoi limiti.
- [Massey 1994], [Bonneau 2012] - guessing entropy (Parte II; vedi anche EVALUATION/exp02).
- [Kaliski 2000], [Percival 2009], [Biryukov et al. 2016] - PBKDF2, scrypt, Argon2 (Parte II.4).
- [Lowe 1997], [Abadi & Rogaway 2002] - gerarchia di autenticazione, simbolico vs computazionale (Parte III).
- [Vanhoef & Piessens 2017] - KRACK (Parte III; vedi FORMAL-MODELS/).
- [Denning 1976], [Bell & LaPadula 1976], [Biba 1977], [Goguen & Meseguer 1982] - flusso, BLP/Biba,
  non-interferenza (Parte IV).
- [Lampson 1973], [Ristenpart et al. 2009] - canali covert, co-residenza (Parte IV).

---

> **Nota:** Documento a scopo educativo, di livello magistrale, complementare ai `THEORETICAL-FOUNDATIONS`
> di modulo (concettuali/applicati) e alla verifica eseguita in `FORMAL-MODELS/`. Le citazioni rimandano a
> fonti reali e verificabili in `REFERENCES.md`.
