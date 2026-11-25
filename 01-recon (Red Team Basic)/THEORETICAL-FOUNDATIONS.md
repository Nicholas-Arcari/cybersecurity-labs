> [English](THEORETICAL-FOUNDATIONS.en.md) | **Italiano**

# Fondamenti teorici - modulo 01: reconnaissance

> - **Livello:** Analisi accademica (complemento teorico ai README operativi del modulo)
> - **Scopo:** Fornire il modello formale dell'avversario, i fondamenti teorico-informativi e l'analisi quantitativa della ricognizione, con riferimento alla letteratura primaria.
> - **Prerequisiti:** README operativi del modulo 01 (OSINT-, SCAN-, DNS-, INTEL-); nozioni di base di teoria dell'informazione e teoria della probabilita.

---

## Abstract

La ricognizione e comunemente presentata come una collezione di tecniche e strumenti (OSINT, port scanning, DNS enumeration). Questo documento la inquadra invece come un problema formale: la riduzione dell'incertezza dell'avversario sulla configurazione del bersaglio. Adottando il modello di avversario di Dolev-Yao come baseline e la metrica di superficie d'attacco di [Manadhata & Wing 2011], si mostra che la ricognizione e quantificabile in termini teorico-informativi (guadagno di informazione per osservazione) e che l'avvento della scansione Internet-wide [Durumeric et al. 2013a] ha modificato strutturalmente l'economia della fase. Se ne derivano le implicazioni difensive: poiche l'informazione pubblica e irreversibile, l'unica leva difensiva efficace e la minimizzazione della superficie d'attacco, non l'occultamento.

---

## 1. Modello dell'Avversario

Si definisce l'avversario di ricognizione `A_rec` come una specializzazione dell'attaccante di rete formalizzato da [Dolev & Yao 1983]. Nel modello Dolev-Yao l'avversario controlla il canale di comunicazione (puo osservare, intercettare, ritardare e iniettare messaggi) ma e computazionalmente limitato: non puo rompere le primitive crittografiche assunte sicure. Per la fase di ricognizione si restringe questo modello a due profili distinti per capacita e osservabilita:

1. **Avversario passivo `A_pass` (OSINT):** non interagisce con il bersaglio. Raccoglie esclusivamente informazione gia pubblica o esposta a terzi (registri WHOIS, DNS, Certificate Transparency, archivi, metadati). La sua osservabilita per il difensore e nulla: non genera traffico verso il perimetro bersaglio. E il profilo di [Durumeric et al. 2013b] applicato all'ecosistema dei certificati.

2. **Avversario attivo `A_act` (scanning):** interagisce direttamente con il bersaglio (port scan, banner grabbing, query DNS dirette). Ottiene informazione piu ricca e aggiornata, ma a costo di una osservabilita non nulla: ogni probe e potenzialmente registrabile da un IDS o da un log perimetrale.

L'obiettivo formale di entrambi i profili non e "trovare vulnerabilita" ma un obiettivo intermedio piu preciso: **massimizzare l'informazione sulla configurazione del bersaglio** (topologia, servizi, versioni, tecnologie, superficie esposta) che alimentera le fasi successive della kill chain [Hutchins et al. 2011]. Questa distinzione e cruciale: la ricognizione e uno stadio di riduzione dell'incertezza, non di sfruttamento.

---

## 2. Proprieta di sicurezza in gioco

La ricognizione minaccia la **confidenzialita dei metadati infrastrutturali**: non i dati degli utenti, ma le informazioni sulla struttura del sistema (quali host esistono, quali servizi espongono, quali tecnologie usano). Occorre distinguere due proprieta difensive frequentemente confuse:

- **Oscurita (proprieta debole):** l'assunzione che l'ignoranza dell'attaccante circa la configurazione fornisca protezione. E strutturalmente fragile e viola il principio di [Kerckhoffs 1883] trasposto all'architettura: la sicurezza non deve dipendere dalla segretezza della configurazione. Un SSID nascosto, una porta su numero non standard, un servizio non documentato sono forme di oscurita.

- **Minimizzazione della superficie d'attacco (proprieta forte):** la riduzione oggettiva del numero di punti attraverso cui il sistema puo essere attaccato. E la proprieta che la ricognizione non puo aggirare, perche agisce sull'esistenza dei punti d'ingresso, non sulla loro conoscibilita.

Il documento sostiene, con [Manadhata & Wing 2011], che solo la seconda proprieta e difensivamente significativa: la ricognizione dimostra empiricamente l'inefficacia dell'oscurita.

---

## 3. Fondamenti teorici

### 3.1 Formalizzazione della superficie d'attacco

[Manadhata & Wing 2011] definiscono la superficie d'attacco di un sistema come una misura tridimensionale sull'insieme delle risorse attraverso cui un avversario puo interagire con il sistema: i **metodi** (punti d'ingresso/uscita, es. porte e API), i **canali** (es. TCP, UDP, socket), e gli **elementi dati** non fidati che attraversano il confine. Ogni risorsa contribuisce alla superficie in proporzione al suo rapporto danno/costo di accesso (damage-effort ratio). La ricognizione e, in questa cornice, il processo di enumerazione empirica della superficie d'attacco: l'attaccante ricostruisce dall'esterno la stessa misura che il difensore dovrebbe minimizzare dall'interno.

### 3.2 Interpretazione teorico-informativa

Sia `X` la variabile aleatoria che rappresenta la configurazione ignota del bersaglio, con entropia di Shannon iniziale [Shannon 1949]:

```
H(X) = - sum_i  p(x_i) log2 p(x_i)
```

Ogni osservazione di ricognizione `o` (una risposta a un probe, un record DNS, un certificato) e un'evidenza che aggiorna la distribuzione a posteriori su `X`. Il guadagno di informazione di un'osservazione e:

```
IG(o) = H(X) - H(X | o)
```

La ricognizione ottimale, in questa cornice, e la sequenza di osservazioni che massimizza il guadagno di informazione cumulativo per unita di costo (dove il costo include il tempo e l'osservabilita). Questa formulazione spiega perche l'OSINT passivo (`A_pass`) e preferito quando disponibile: ha costo di osservabilita nullo pur riducendo `H(X)`. Spiega inoltre perche tecniche come l'enumerazione dei sottodomini via Certificate Transparency [Durumeric et al. 2013b] sono cosi efficaci: i log CT sono un canale che espone deterministicamente (non probabilisticamente) l'esistenza di host, azzerando l'entropia relativa a quella porzione della configurazione.

### 3.3 L'asimmetria dell'irreversibilita

Un'informazione una volta pubblicata non puo essere de-pubblicata in senso teorico-informativo: copie, cache, archivi e log di terzi la rendono persistente. Questo genera un'asimmetria fondamentale: il difensore deve prevenire l'esposizione *prima* che avvenga, mentre l'attaccante puo raccoglierla in qualsiasi momento successivo. E il corrispettivo, sul piano informativo, del principio secondo cui un segreto trapelato e compromesso per sempre (rilevante anche per la gestione dei segreti, modulo 10).

---

## 4. Analisi quantitativa

### 4.1 L'economia della scansione dopo ZMap

[Durumeric et al. 2013a] hanno dimostrato che l'intero spazio di indirizzamento IPv4 pubblico (circa 3.7 miliardi di indirizzi instradabili) puo essere scansionato su una singola porta in circa 45 minuti da una singola macchina con connettivita gigabit, con hardware commodity. Questo risultato ha una implicazione quantitativa sul modello di minaccia: il costo marginale per l'attaccante di enumerare l'intera Internet e crollato di ordini di grandezza rispetto agli scanner sequenziali (nmap su liste, Masscan). La conseguenza teorica e che l'assunzione "il mio host non sara trovato perche non e indicizzato" e falsificata: ogni host pubblico e, in pratica, continuamente enumerato. La difesa non puo basarsi sulla probabilita di non essere scoperti, che tende a 1 per l'essere scoperti.

### 4.2 Esaustivita dei canali deterministici

Mentre il port scanning e un campionamento probabilistico (soggetto a perdita di pacchetti, rate limiting, filtri), alcuni canali di ricognizione sono **deterministici ed esaustivi**. I log di Certificate Transparency (RFC 6962) registrano ogni certificato emesso da una CA conforme: un attaccante che interroga i log CT ottiene l'enumerazione completa dei sottodomini per cui e stato emesso un certificato, senza inviare un solo pacchetto al bersaglio. In termini della sezione 3.2, questi canali portano `H(X | o)` a zero per la componente enumerata, con costo di osservabilita nullo. E il caso in cui `A_pass` domina `A_act`.

---

## 5. Rassegna della letteratura

Il modello dell'attaccante di rete adottato deriva da [Dolev & Yao 1983], il cui contributo fondativo e stato astrarre l'avversario dalle specifiche implementazioni a un insieme di capacita sul canale; la loro formalizzazione resta la baseline dei protocolli di sicurezza. La quantificazione della superficie d'attacco poggia su [Manadhata & Wing 2011], che per primi hanno proposto una metrica sistematica e misurabile, superando le definizioni qualitative precedenti. Sul piano empirico, la coppia di lavori di [Durumeric et al. 2013a] (ZMap) e [Durumeric et al. 2013b] (ecosistema HTTPS) ha ridefinito la comprensione della ricognizione su scala Internet, dimostrando sia la fattibilita della scansione esaustiva sia la ricchezza informativa dei canali deterministici come CT. L'inquadramento teorico-informativo si richiama a [Shannon 1949]; l'inefficacia dell'oscurita al principio di [Kerckhoffs 1883]. Il posizionamento della ricognizione come primo stadio di una sequenza segue il Cyber Kill Chain di [Hutchins et al. 2011].

---

## 6. Limiti e problemi aperti

1. **Non prevenibilita della ricognizione passiva.** Poiche `A_pass` opera esclusivamente su informazione gia pubblica, non esiste una contromisura che la rilevi o la impedisca: il difensore puo solo ridurre l'informazione esposta a priori. Questo pone un limite teorico invalicabile alla difesa contro la ricognizione OSINT.

2. **Quantificazione della sufficienza.** Non esiste una metrica consolidata che stabilisca *quando* la ricognizione e "sufficiente" per l'avversario, ossia quando il guadagno di informazione marginale scende sotto la soglia utile per la fase successiva. La formulazione della sezione 3.2 e descrittiva, non predittiva.

3. **Deception come rumore informativo.** Un problema aperto e la progettazione ottimale di contromisure che aumentino `H(X | o)` per l'attaccante iniettando informazione falsa ma credibile (honeypot, honeytoken, banner falsificati). La teoria di quanto rumore sia necessario per degradare efficacemente la ricognizione avversaria - senza degradare l'operativita legittima - non e risolta e connette il modulo 01 al modulo 08 (deception).

---

## 7. Sintesi e collegamento alla pratica

I README operativi del modulo 01 (finding con prefissi `OSINT-`, `SCAN-`, `DNS-`, `INTEL-`) istanziano concretamente il quadro qui formalizzato: l'OSINT passivo corrisponde ad `A_pass`, il network scanning attivo ad `A_act`, l'enumerazione via Certificate Transparency e la manifestazione pratica del canale deterministico della sezione 4.2. La lezione unificante e che ogni finding di ricognizione riduce `H(X)` per l'attaccante e amplia la conoscenza empirica della superficie d'attacco [Manadhata & Wing 2011]; la contromisura corretta, coerente con la sezione 2, non e occultare (oscurita, debole) ma ridurre la superficie e iniettare rumore controllato (minimizzazione + deception, forti). Questo collega direttamente il modulo 01 alle contromisure di hardening (modulo 08) e chiude il cerchio tra la prospettiva offensiva e quella difensiva.

---

## Riferimenti

Sottoinsieme della bibliografia master (`../REFERENCES.md`) rilevante per questo modulo:

- [Dolev & Yao 1983] - modello formale dell'avversario di rete.
- [Shannon 1949] - fondamenti teorico-informativi.
- [Kerckhoffs 1883] - inefficacia della segretezza architetturale.
- [Manadhata & Wing 2011] - metrica della superficie d'attacco.
- [Durumeric et al. 2013a] - ZMap, scansione Internet-wide.
- [Durumeric et al. 2013b] - ecosistema dei certificati HTTPS.
- [Hutchins et al. 2011] - Cyber Kill Chain.
- RFC 6962 - Certificate Transparency.
- NIST SP 800-115 - metodologia di testing tecnico.

---

> **Nota:** Questo documento e un complemento teorico a scopo educativo e non sostituisce i README operativi del modulo, che contengono le procedure, i comandi e i finding. Le citazioni rimandano a fonti reali e verificabili elencate in `../REFERENCES.md`.
