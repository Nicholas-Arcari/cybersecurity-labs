> [English](THEORETICAL-FOUNDATIONS.en.md) | **Italiano**

# Fondamenti teorici - modulo 08: defense & hardening

> - **Livello:** Analisi accademica (complemento teorico ai README operativi del modulo)
> - **Scopo:** Derivare quantitativamente il problema base-rate del rilevamento, fondare l'anomaly detection e la deception, e formalizzare l'hardening come riduzione della superficie d'attacco.
> - **Prerequisiti:** README operativi del modulo 08 (finding DEF-); nozioni di probabilita bayesiana, teoria del rilevamento e controllo degli accessi.

---

## Abstract

Questo documento fornisce il fondamento quantitativo della difesa. Il risultato centrale e la derivazione bayesiana del **base-rate fallacy** [Axelsson 2000]: si dimostra che, dato il tasso base bassissimo degli eventi malevoli, anche un rilevatore molto accurato produce un valore predittivo positivo scarso, il che spiega perche i falsi positivi dominano l'operativita del SIEM. Da qui si motiva il valore della **deception** [come contromisura a falso positivo strutturalmente nullo] e dell'**anomaly detection** [Denning 1987; Forrest et al. 1996], con i limiti del machine learning [Sommer & Paxson 2010]. L'hardening e formalizzato come riduzione della superficie d'attacco [Manadhata & Wing 2011] e applicazione dei principi di [Saltzer & Schroeder 1975]. Il framework D3FEND fornisce la tassonomia difensiva duale ad ATT&CK.

---

## 1. Modello del difensore

Il difensore osserva un flusso di eventi `E` (log, pacchetti, chiamate) e deve decidere per ciascuno se e benigno o malevolo, con l'obiettivo di massimizzare il rilevamento dei malevoli minimizzando i falsi allarmi, sotto vincolo di risorse di analisi finite. Formalmente e un problema di **teoria del rilevamento** (detection theory) con due tipi di errore: falso positivo (allarme su evento benigno) e falso negativo (evento malevolo non rilevato). Il difensore non controlla il tasso base degli eventi malevoli, che e strutturalmente bassissimo: e questa asimmetria, non l'accuratezza del rilevatore, a determinare la difficolta (sezione 3.1).

---

## 2. Proprieta di sicurezza in gioco

- **Visibilita:** precondizione di ogni rilevamento; senza osservabilita non c'e detection. Il logging centralizzato la realizza (modulo 07, sezione 3.4).
- **Detection efficace:** massimizzare il valore predittivo del rilevamento sotto il vincolo del base-rate (sezione 3.1).
- **Contenimento tempestivo:** ridurre a zero il tempo tra rilevamento e risposta per le minacce ad alta confidenza (active response), accettando il rischio dell'automazione (sezione 4.2).
- **Superficie d'attacco minima:** prevenire alla radice riducendo i punti attaccabili [Manadhata & Wing 2011].

---

## 3. Fondamenti teorici

### 3.1 Il base-rate fallacy: derivazione bayesiana

[Axelsson 2000] applica il teorema di Bayes all'intrusion detection ottenendo il risultato piu importante della teoria del rilevamento in sicurezza. Sia `I` l'evento "intrusione" e `A` l'evento "allarme". Le grandezze rilevanti sono:

- `P(I)` = tasso base delle intrusioni (probabilita a priori che un evento sia malevolo), tipicamente **bassissimo** (es. 1 su 100.000 o meno);
- `P(A|I)` = tasso di veri positivi (sensibilita del rilevatore);
- `P(A|~I)` = tasso di falsi positivi.

La grandezza che conta operativamente e il **valore predittivo positivo**, ossia la probabilita che un allarme corrisponda a una reale intrusione:

```
                    P(A|I) P(I)
P(I|A) = ---------------------------------------
          P(A|I) P(I) + P(A|~I) P(~I)
```

Il punto di [Axelsson 2000] e che, quando `P(I)` e molto piccolo, il termine `P(A|~I) P(~I)` al denominatore domina anche per tassi di falsi positivi minuscoli, perche `P(~I)` e vicino a 1. Esempio numerico: con `P(I) = 10^-5`, `P(A|I) = 1` (rilevatore perfetto sui veri positivi) e un tasso di falsi positivi eccellente `P(A|~I) = 10^-3`:

```
P(I|A) = (1 x 10^-5) / (1 x 10^-5 + 10^-3 x (1 - 10^-5))
       ~ 10^-5 / (10^-5 + 10^-3)
       ~ 0.0099   (circa 1%)
```

Ossia: **il 99% degli allarmi e falso**, pur con un rilevatore quasi perfetto. Questo e il fondamento teorico del sovraccarico da falsi positivi che affligge ogni SOC, e la ragione per cui la sola accuratezza del rilevatore non risolve il problema: occorre abbattere `P(A|~I)` di ordini di grandezza, o alzare il tasso base effettivo restringendo il dominio (correlazione, contesto).

### 3.2 Deception come evasione del base-rate

La deception (honeypot, canary token) offre una via d'uscita teorica dal base-rate fallacy. Su una risorsa esca, l'attivita legittima e **zero per costruzione**: `P(~I | interazione) = 0`. Sostituendo nella formula della sezione 3.1, il valore predittivo positivo diventa 1: ogni interazione con l'esca e, con certezza, malevola. La deception non "migliora" il rilevatore, cambia il dominio in modo che il base-rate non degradi il valore predittivo. E la ragione teorica per cui un singolo alert di canary token vale, in confidenza, molti alert SIEM correlati. Il costo e la copertura: l'esca rileva solo chi la tocca (sezione 6).

### 3.3 Anomaly detection: modelli e limiti

[Denning 1987] fonda l'intrusion detection sulla premessa che l'attivita malevola devia statisticamente dal comportamento normale. [Forrest et al. 1996] la realizzano a livello di sistema modellando il "senso di se" di un processo tramite le sequenze di system call: le deviazioni dal profilo appreso segnalano anomalie. Il limite teorico e duplice: (i) il profilo di normalita e esso stesso rumoroso e mutevole, generando falsi positivi (sezione 3.1); (ii) [Sommer & Paxson 2010] mostrano che il machine learning per l'intrusion detection soffre di sfide peculiari - l'alto costo degli errori, la mancanza di dati di attacco etichettati, la difficolta di interpretazione e la non-stazionarieta - che ne limitano l'efficacia rispetto ad altri domini applicativi. La detection comportamentale e potente ma non elude il triangolo falsi positivi / falsi negativi / costo.

### 3.4 Hardening come riduzione della superficie e principi di progettazione

L'hardening e l'applicazione sistematica della minimizzazione della superficie d'attacco [Manadhata & Wing 2011] (modulo 01, sezione 3.1) e dei principi di [Saltzer & Schroeder 1975]: fail-safe defaults (tutto negato salvo autorizzazione esplicita), least privilege (SUID minimi, RBAC ristretto, LAPS), economy of mechanism (meno servizi, meno superficie), complete mediation (ogni accesso verificato). Credential Guard e LAPS, in particolare, sono formalizzabili come rottura della transitivita della fiducia del modulo 07 (sezione 3.2): riducono il grafo di attacco eliminando archi. L'hardening agisce a monte della detection: un arco rimosso e un cammino di attacco che non esistera mai, non un evento da rilevare.

---

## 4. Analisi quantitativa

> **Validazione empirica:** la derivazione bayesiana del base-rate fallacy (sez. 3.1) e verificata
> sperimentalmente su dati misurati in [`../EVALUATION/exp01-detection-base-rate/`](../EVALUATION/exp01-detection-base-rate/results.md):
> un rilevatore reale su 1.000.000 di eventi etichettati mostra la PPV crollare a 0.0023 al base rate
> `1e-5` (99.8% di allarmi falsi), con la formula analitica confermata per resampling.

### 4.1 Correlazione come innalzamento del base-rate effettivo

La correlazione multi-sorgente (SIEM) e interpretabile come un metodo per innalzare il tasso base effettivo e quindi il valore predittivo. Richiedere la coincidenza di piu eventi indipendenti (scan + login riuscito + alert endpoint nella stessa finestra) definisce un evento composto il cui `P(I | composto)` e molto piu alto di quello dei singoli eventi, perche la coincidenza fortuita di eventi benigni indipendenti ha probabilita bassa. Formalmente, se gli eventi benigni sono approssimativamente indipendenti, `P(A_1 ~I) P(A_2 ~I) ...` decresce moltiplicativamente, abbattendo il denominatore della formula della sezione 3.1. E la giustificazione teorica quantitativa del perche la correlazione (modulo 08, Splunk/ELK) riduca i falsi positivi la' dove il singolo sensore fallisce.

### 4.2 Il compromesso dell'automazione della risposta

L'active response comprime il dwell time (modulo 07, sezione 4.1) a zero per le minacce ad alta confidenza, ma trasferisce il rischio: un falso positivo automatizzato causa danno immediato (auto-blocco). Il compromesso e quantificabile: automatizzare e vantaggioso quando il valore predittivo `P(I|A)` per la regola specifica e sufficientemente alto (sezione 3.1) e il costo del falso positivo e limitato (timeout, whitelist). Le regole a basso valore predittivo devono restare in triage umano. Questa e la lettura teorica del principio operativo dei README: automatizzare solo le risposte a detection deterministiche e ad alta confidenza.

---

## 5. Rassegna della letteratura

Il risultato quantitativo centrale e di [Axelsson 2000], che ha portato il teorema di Bayes al cuore della difficolta dell'intrusion detection. Le fondamenta dell'anomaly detection sono di [Denning 1987] e [Forrest et al. 1996]; i limiti del machine learning applicato sono analizzati da [Sommer & Paxson 2010]. L'hardening come riduzione della superficie si fonda su [Manadhata & Wing 2011] e sui principi di [Saltzer & Schroeder 1975]; l'integrita dei log su [Biba 1977]. La tassonomia offensiva di riferimento e MITRE ATT&CK [Strom et al. 2020], con la duale difensiva D3FEND. Il modello del Diamante [Caltagirone et al. 2013] fornisce la cornice analitica per la threat intelligence prodotta dalla deception.

---

## 6. Limiti e problemi aperti

1. **Irriducibilita del base-rate.** Poiche `P(I)` e strutturalmente bassissimo, nessun miglioramento realistico dell'accuratezza del rilevatore elimina il dominio dei falsi positivi [Axelsson 2000]. La detection efficace richiede necessariamente correlazione, contesto o deception per aggirare il limite - non un rilevatore migliore.

2. **Copertura limitata della deception.** La proprieta di falso positivo nullo (sezione 3.2) si paga in copertura: l'esca rileva solo chi la incrocia. Il posizionamento ottimale delle esche per massimizzare la probabilita di intercettazione dell'attaccante e un problema di ottimizzazione aperto.

3. **Non-stazionarieta.** I profili di normalita (anomaly detection) e le regole di correlazione degradano al mutare dell'ambiente [Sommer & Paxson 2010]; il mantenimento e un costo continuo, non un investimento una tantum. L'adattamento automatico senza introdurre nuovi falsi positivi resta aperto.

---

## 7. Sintesi e collegamento alla pratica

I finding `DEF-` del modulo istanziano questo quadro: la detection SIEM (DEF-001/002) opera sotto il vincolo base-rate della sezione 3.1, e la correlazione documentata nei README e l'innalzamento del base-rate effettivo della sezione 4.1; la deception (DEF-005/006) e l'evasione del base-rate della sezione 3.2, con il suo valore predittivo unitario; il FIM e l'active response (DEF-003/004) applicano l'anomaly detection e il compromesso di automazione delle sezioni 3.3 e 4.2; l'hardening (DEF-007/008) e la riduzione della superficie e la rottura della transitivita della fiducia della sezione 3.4. Le tabelle D3FEND dei README sono la controparte tassonomica del quadro qui formalizzato. Il documento fornisce alla pratica difensiva la giustificazione quantitativa del perche non basti "un rilevatore migliore" (base-rate), del perche la deception sia sproporzionatamente preziosa (valore predittivo unitario) e del perche l'hardening a monte batta la detection a valle (archi rimossi contro eventi da rilevare).

---

## Riferimenti

Sottoinsieme della bibliografia master (`../REFERENCES.md`) rilevante per questo modulo:

- [Axelsson 2000] - base-rate fallacy nell'intrusion detection (derivazione bayesiana).
- [Denning 1987], [Forrest et al. 1996] - fondamenti dell'anomaly detection.
- [Sommer & Paxson 2010] - limiti del machine learning per l'IDS.
- [Manadhata & Wing 2011] - riduzione della superficie d'attacco.
- [Saltzer & Schroeder 1975] - principi di progettazione sicura.
- [Biba 1977] - integrita dei log.
- [Strom et al. 2020] - MITRE ATT&CK (e D3FEND duale).
- [Caltagirone et al. 2013] - Diamond Model (threat intelligence).

---

> **Nota:** Documento a scopo educativo, complementare ai README operativi. Le citazioni rimandano a fonti reali elencate in `../REFERENCES.md`.
