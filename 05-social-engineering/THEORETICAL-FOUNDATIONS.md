> [English](THEORETICAL-FOUNDATIONS.en.md) | **Italiano**

# Fondamenti teorici - modulo 05: social engineering

> - **Livello:** Analisi accademica (complemento teorico ai README operativi del modulo)
> - **Scopo:** Fondare l'ingegneria sociale sulla teoria del doppio processo cognitivo e sui principi dell'influenza, e formalizzare il divario di autenticazione sistema-verso-umano come limite strutturale.
> - **Prerequisiti:** README operativi del modulo 05 (finding SE-); nozioni di base di psicologia cognitiva e teoria dei sistemi socio-tecnici.

---

## Abstract

L'ingegneria sociale e spesso liquidata come "hacking umano" non tecnico. Questo documento ne mostra la struttura teorica. Il substrato cognitivo e la **teoria del doppio processo** [Kahneman 2011]: gli attacchi sfruttano l'elaborazione euristica (System 1) aggirando quella analitica (System 2), operando attraverso i principi dell'influenza di [Cialdini 1984]. Il limite empirico e stabilito da [Dhamija et al. 2006]: gli utenti falliscono sistematicamente nel distinguere il legittimo dal fraudolento. Il limite strutturale e il **divario di autenticazione**: i sistemi autenticano bene gli umani, ma gli umani autenticano male i sistemi, una direzione sotto-affrontata che connette il phishing all'Evil Twin (modulo 06) e collega la sicurezza umana a un problema tecnico irrisolto. Se ne deriva perche la sola formazione sia insufficiente e serva una difesa socio-tecnica in profondita [Reason 1990].

---

## 1. Modello dell'Avversario

L'avversario di ingegneria sociale ha come bersaglio non un sistema ma un **operatore umano** dotato di autorita (accesso, credenziali, capacita di azione). A differenza degli altri moduli, il canale d'attacco non e un'interfaccia tecnica ma la **cognizione e la fiducia** del bersaglio. Le capacita dell'avversario sono: costruire un pretesto credibile, impersonare un'autorita o un contesto fidato, indurre un'azione (cliccare, rivelare, autorizzare) prima che intervenga la valutazione analitica. Il bersaglio non e "irrazionale": e un agente a **razionalita limitata** che opera sotto vincoli di tempo, attenzione e informazione, esattamente le condizioni che l'attacco costruisce.

---

## 2. Proprieta di sicurezza in gioco

- **Autenticazione bidirezionale:** non solo il sistema deve autenticare l'utente, ma l'utente deve poter autenticare il sistema/interlocutore. Il phishing viola la seconda direzione, generalmente piu debole (sezione 3.3).
- **Integrita dell'intenzione:** un'azione privilegiata deve derivare da una decisione informata del legittimo detentore, non da una manipolazione. E la stessa proprieta violata dal confused deputy (modulo 03), qui applicata all'agente umano.
- **Resilienza socio-tecnica:** la sicurezza del sistema complessivo non deve collassare al fallimento di un singolo operatore. E la proprieta che [Reason 1990] modella con la difesa a strati.

---

## 3. Fondamenti teorici

### 3.1 Doppio processo e sfruttamento dell'euristica

[Kahneman 2011] distingue due modalita di elaborazione: **System 1** (rapido, automatico, euristico, a basso costo cognitivo) e **System 2** (lento, analitico, deliberato, costoso). La maggior parte delle decisioni quotidiane e delegata a System 1 per efficienza. L'ingegneria sociale e, in termini cognitivi, la progettazione di stimoli che inducono una risposta da System 1 impedendo l'attivazione di System 2. Le leve tipiche - urgenza, autorita, paura, familiarita - non sono casuali: sono precisamente i trigger che favoriscono l'elaborazione euristica e sopprimono la verifica analitica. L'attacco vince nella finestra temporale tra lo stimolo e l'eventuale riflessione.

### 3.2 I principi dell'influenza come vettori

[Cialdini 1984] identifica sei principi di influenza con base empirica in psicologia sociale: reciprocita, impegno/coerenza, riprova sociale, autorita, simpatia, scarsita. Ciascuno e un'euristica adattiva in contesti normali che diventa vettore d'attacco se innescata artificialmente:

- **autorita**: impersonazione di IT/dirigenza/istituzioni;
- **scarsita/urgenza**: "il tuo account sara sospeso entro 24 ore";
- **riprova sociale**: "i tuoi colleghi hanno gia completato";
- **reciprocita**: un piccolo favore che precede la richiesta;
- **simpatia**: pretesti costruiti su affinita e rapport.

Questi principi forniscono la mappa formale tra la struttura di un pretesto e il meccanismo cognitivo che sfrutta, trasformando l'ingegneria sociale da arte aneddotica a tecnica con substrato teorico.

### 3.3 Il divario di autenticazione sistema-verso-umano

Esiste un'asimmetria strutturale nell'autenticazione. La direzione **umano-verso-sistema** e matura: password, MFA, biometria, con framework di valutazione consolidati [Bonneau et al. 2012]. La direzione **sistema-verso-umano** - come un utente verifica che l'interlocutore (sito, email, chiamante, access point) sia autentico - e debole e sotto-progettata. Il phishing sfrutta esattamente questo divario: l'utente non dispone di un meccanismo affidabile e a basso costo cognitivo per autenticare la controparte, e i segnali disponibili (aspetto, logo, URL) sono falsificabili. [Dhamija et al. 2006] lo dimostrano empiricamente: indicatori di sicurezza visivi vengono ignorati o mal interpretati, e i migliori siti di phishing ingannano una frazione elevata degli utenti anche attenti.

Questo collega teoricamente il modulo 05 al modulo 06: l'Evil Twin (rogue AP) e la versione radio dello stesso divario, e la sua unica contromisura strutturale - l'autenticazione mutua con validazione del certificato server (EAP-TLS) - e proprio l'implementazione tecnica dell'autenticazione sistema-verso-umano che il phishing dimostra mancante nel dominio umano. Dove la macchina puo verificare un certificato, l'umano non ha l'equivalente.

### 3.4 Il sistema socio-tecnico e l'anello debole

[Reason 1990] modella l'errore umano e la difesa organizzativa con il "Swiss cheese model": ogni strato di difesa ha dei buchi (falle latenti), e un incidente accade quando i buchi di strati successivi si allineano. Applicato alla sicurezza: la formazione riduce ma non azzera la probabilita di fallimento del singolo operatore (uno strato bucato); la resilienza richiede strati indipendenti (controlli tecnici, verifiche procedurali, rilevamento) che non falliscano simultaneamente. Ne consegue il principio di progettazione: non affidare alla vigilanza umana singola cio che puo essere ridondato tecnicamente.

---

## 4. Analisi quantitativa

### 4.1 La base-rate a sfavore dell'utente

Un operatore riceve prevalentemente comunicazioni legittime; le fraudolente sono una piccola frazione. Questa base-rate ha una conseguenza controintuitiva speculare a quella dell'IDS (modulo 08, [Axelsson 2000]): per l'utente, essere costantemente sospettoso ha un basso ritorno atteso (la stragrande maggioranza delle verifiche confermerebbe la legittimita) e un alto costo cumulativo (attrito, tempo). L'utente e, in senso economico, razionalmente disincentivato dalla vigilanza continua. Questo spiega quantitativamente perche "basta stare attenti" fallisce come strategia: chiede all'utente un comportamento con ROI negativo dal suo punto di vista locale. La difesa efficace deve spostare il carico dalla vigilanza umana (costosa, poco affidabile) a controlli sistemici (DMARC/SPF/DKIM per l'email, filtri, MFA resistente al phishing).

### 4.2 Il costo asimmetrico della campagna

Una campagna di phishing ha costo marginale quasi nullo per bersaglio aggiuntivo, mentre il difensore deve proteggere ogni operatore. Con un tasso di successo per singolo bersaglio anche basso, la probabilita che *almeno un* operatore su `n` fallisca cresce come `1 - (1-p)^n`, tendente a 1 al crescere di `n`. E la formalizzazione dell'anello debole: in un'organizzazione sufficientemente grande, la compromissione di almeno un operatore e quasi certa se la difesa si basa solo sul fattore umano. Questo motiva quantitativamente la necessita di contromisure tecniche che non scalino con la fallibilita del singolo.

---

## 5. Rassegna della letteratura

Il substrato cognitivo dell'ingegneria sociale si fonda sulla teoria del doppio processo di [Kahneman 2011] e sui principi dell'influenza di [Cialdini 1984], entrambi con solida base empirica in psicologia. La dimostrazione empirica dell'efficacia del phishing e dei limiti percettivi umani e di [Dhamija et al. 2006]. Il framework per valutare l'autenticazione (e implicitamente il suo divario direzionale) e di [Bonneau et al. 2012]. Il modello dell'errore umano e della difesa a strati e di [Reason 1990]. L'argomento base-rate si richiama, per dualita, all'analisi di [Axelsson 2000] sviluppata nel modulo 08.

---

## 6. Limiti e problemi aperti

1. **Autenticazione sistema-verso-umano usabile.** Progettare un meccanismo con cui un umano verifichi in modo affidabile e a basso costo cognitivo l'autenticita di una controparte resta un problema aperto: le soluzioni proposte (indicatori di sicurezza, immagini personalizzate) sono ignorate o aggirate [Dhamija et al. 2006].

2. **Misura della resilienza umana.** Non esiste una metrica robusta e stabile della "suscettibilita" di un operatore o di un'organizzazione: i tassi di click delle simulazioni dipendono fortemente dal contesto e non predicono in modo affidabile il comportamento sotto attacco reale.

3. **Deepfake e collasso dei segnali.** L'avvento di sintesi vocale e video ad alta fedelta erode ulteriormente i pochi segnali di autenticazione disponibili all'umano (voce, volto), aggravando il divario della sezione 3.3 e rendendo ancora piu urgente lo spostamento verso controlli tecnici.

---

## 7. Sintesi e collegamento alla pratica

I finding `SE-` del modulo istanziano questo quadro: le campagne di phishing (GoPhish), i pretesti e i payload documentati nei README sono applicazioni dei principi di [Cialdini 1984] operanti sul System 1 [Kahneman 2011], e la loro efficacia rispecchia i risultati di [Dhamija et al. 2006]. La remediation raccomandata - MFA resistente al phishing, DMARC/SPF/DKIM, filtri, verifiche procedurali fuori banda - e la traduzione operativa della sezione 4.1: spostare il carico dalla vigilanza umana ai controlli sistemici. Il collegamento teorico al modulo 06 (Evil Twin) e al modulo 03 (confused deputy) unifica l'ingegneria sociale con il resto del percorso sotto un unico principio: dove manca l'autenticazione dell'intenzione e della controparte, l'attacco passa - che il deputy confuso sia un browser, un server o un essere umano.

---

## Riferimenti

Sottoinsieme della bibliografia master (`../REFERENCES.md`) rilevante per questo modulo:

- [Kahneman 2011] - teoria del doppio processo cognitivo.
- [Cialdini 1984] - principi dell'influenza.
- [Dhamija et al. 2006] - efficacia empirica del phishing.
- [Reason 1990] - errore umano e difesa a strati.
- [Bonneau et al. 2012] - valutazione dell'autenticazione.
- [Axelsson 2000] - argomento base-rate (per dualita, modulo 08).

---

> **Nota:** Documento a scopo educativo, complementare ai README operativi. Le citazioni rimandano a fonti reali elencate in `../REFERENCES.md`.
