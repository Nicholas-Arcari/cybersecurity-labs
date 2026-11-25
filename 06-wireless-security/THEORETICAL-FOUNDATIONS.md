> [English](THEORETICAL-FOUNDATIONS.en.md) | **Italiano**

# Fondamenti teorici - modulo 06: wireless security

> - **Livello:** Analisi accademica (complemento teorico ai README operativi del modulo)
> - **Scopo:** Formalizzare la sicurezza del layer radio (assenza di perimetro fisico), la caduta della security-by-obscurity (Crypto-1), la proprieta di freshness contro il replay e la distinzione identificazione/autenticazione.
> - **Prerequisiti:** README operativi del modulo 06 (finding WIFI-); nozioni di crittografia, protocolli di autenticazione e teoria dell'informazione.

---

## Abstract

Il dominio wireless espone in forma pura principi crittografici che gli altri moduli toccano indirettamente. Il documento organizza il modulo attorno a quattro nuclei: (i) l'assenza di perimetro fisico rende l'intercettazione il default, elevando la crittografia a unica difesa; (ii) la rottura di Crypto-1 [Nohl et al. 2008; Garcia et al. 2008] e la dimostrazione empirica canonica dell'inefficacia della security-by-obscurity [Kerckhoffs 1883]; (iii) il replay attack e la violazione della proprieta di **freshness**, il cui ripristino (rolling code, nonce) e un problema di teoria dei protocolli; (iv) la clonazione RFID nasce dalla confusione tra **identificazione** e **autenticazione**. L'evoluzione WEP, WPA2, WPA3, con gli attacchi KRACK [Vanhoef & Piessens 2017] e Dragonblood [Vanhoef & Ronen 2020], illustra la crittanalisi dei protocolli come processo iterativo.

---

## 1. Modello dell'Avversario

L'avversario wireless e un attaccante di rete di Dolev-Yao [Dolev & Yao 1983] realizzato fisicamente: nel raggio radio possiede **accesso completo al canale** senza necessita di compromettere alcun dispositivo. Puo osservare passivamente ogni trasmissione (i frame di gestione 802.11 sono in chiaro anche su reti cifrate), iniettare frame arbitrari (deautenticazione, association), e trasmettere segnali (rogue AP, replay RF). Rispetto al web attacker (modulo 03), e piu forte sul canale; rispetto a Dolev-Yao puro, e vincolato dalla fisica (raggio, potenza, banda). La distinzione operativa passivo/attivo del modulo 01 (sezione 1) si applica: la ricezione SDR e passiva e non rilevabile, la trasmissione e attiva e rilevabile.

---

## 2. Proprieta di sicurezza in gioco

- **Confidenzialita sul canale broadcast:** poiche chiunque nel raggio riceve, la confidenzialita puo derivare solo dalla crittografia, non dall'inaccessibilita del mezzo.
- **Autenticazione mutua:** entrambe le parti devono provare la propria identita. La sua assenza abilita l'Evil Twin (impersonazione dell'AP) e la clonazione (impersonazione del token).
- **Freshness (novita):** un messaggio di autenticazione o comando deve essere riconoscibile come non riutilizzato. E la proprieta violata dal replay (sezione 3.3).
- **Resistenza agli attacchi offline:** un handshake intercettato non deve consentire il recupero del segreto se non a costo proibitivo (sezione 3.2).

---

## 3. Fondamenti teorici

### 3.1 Crypto-1 e la caduta della security-by-obscurity

MIFARE Classic si basa su Crypto-1, cifrario a flusso proprietario con chiave a 48 bit, mantenuto segreto. [Nohl et al. 2008] ne hanno effettuato il reverse engineering dal silicio e [Garcia et al. 2008] la crittanalisi completa, rivelando due debolezze fatali: un PRNG prevedibile e una struttura del cifrario che consente attacchi a complessita drasticamente ridotta (darkside, nested). Il risultato e la dimostrazione empirica piu netta del principio di [Kerckhoffs 1883]: un algoritmo la cui sicurezza dipende dalla segretezza del design collassa non appena il design e recuperato - e ogni design distribuito in miliardi di chip e, prima o poi, recuperato. La lezione teorica e che la sicurezza deve risiedere nella chiave, con algoritmi pubblici e analizzati (AES in DESFire), non nell'oscurita.

### 3.2 WPA2-PSK: derivazione della chiave e attacco offline

WPA2-PSK deriva la Pairwise Master Key dalla passphrase via PBKDF2-HMAC-SHA1 [Kaliski 2000] con 4096 iterazioni e l'SSID come salt:

```
PMK = PBKDF2(passphrase, SSID, 4096, 256)
```

La cattura del 4-way handshake (o del PMKID) fornisce il materiale per un attacco a dizionario **offline**: non si decifra il traffico, si verifica quale candidato produce il MIC osservato. La sicurezza si riduce quindi al problema del modulo 04 (sezione 3.3): entropia della passphrase per il costo per tentativo. Le 4096 iterazioni sono key stretching deliberato; l'uso dell'SSID come salt impedisce rainbow table precomputate per SSID unici ma non per SSID comuni (da cui l'esistenza di tabelle per "linksys", "NETGEAR"). WPA2 e sicuro esattamente quanto la guessing entropy della PSK.

### 3.3 Il replay e la proprieta di freshness

Il replay attack e la violazione della **freshness**: un sistema che accetta un messaggio valido senza verificarne la novita e vulnerabile a chiunque ne possieda una copia. Formalmente, l'autenticazione deve garantire non solo che il messaggio sia *valido* (autenticita) ma che sia *fresco* (mai accettato prima). Un telecomando a codice fisso trasmette sempre la stessa sequenza: valida ma non fresca, quindi replayabile. Il rolling code introduce un contatore sincronizzato e cifrato (KeeLoq): ogni trasmissione porta un valore monotono crescente e cifrato che il ricevitore accetta una sola volta. E l'analogo, nel dominio RF, dei **nonce** nei protocolli di rete: un valore che garantisce la freshness. Questa e la stessa proprieta violata dal KRACK (sezione 3.5) a livello di protocollo WiFi, e la stessa che i token anti-CSRF (modulo 03) forniscono a livello web. La freshness e un principio unificante trasversale.

### 3.4 Identificazione contro autenticazione (RFID)

La clonazione di badge EM4100/MIFARE nasce da un errore concettuale ricorrente: usare un **identificativo** come se fosse un **segreto di autenticazione**. L'UID di un tag e progettato per l'anti-collisione (distinguere piu tag nel campo), e trasmesso in chiaro a ogni interrogazione ed e, sui tag magic, liberamente impostabile. Un sistema che concede l'accesso in base all'UID autentica "qualcosa che chiunque puo leggere e falsificare". L'autenticazione robusta richiede la prova di possesso di un segreto senza rivelarlo (challenge-response su chiave che non lascia il chip, come in DESFire AES). La distinzione identificazione/autenticazione e lo stesso principio che, nel web, separa un session ID prevedibile da un token crittografico, e che nel cloud (modulo 10) separa un nome di risorsa da una credenziale: l'identita non deve mai essere il segreto.

### 3.5 La crittanalisi dei protocolli come processo iterativo

L'evoluzione WEP, WPA, WPA2, WPA3 illustra la crittanalisi come processo. WEP cade per le debolezze del key scheduling di RC4 [Fluhrer et al. 2001]. WPA2, solido nella cifratura, subisce KRACK [Vanhoef & Piessens 2017]: non una rottura crittografica ma un difetto di **protocollo**, la reinstallazione della chiave che forza il riuso del nonce nel 4-way handshake, violando la freshness a livello di stato del protocollo. WPA3 adotta SAE (Dragonfly), resistente agli attacchi offline, ma [Vanhoef & Ronen 2020] (Dragonblood) ne rivelano side-channel e downgrade. La lezione teorica: la sicurezza di un protocollo non e la sola sicurezza delle sue primitive; le interazioni di stato, la gestione dei nonce e i canali laterali [Kocher 1996] sono superfici d'attacco autonome, e la verifica formale dei protocolli resta necessaria.

> **Verifica formale (non solo argomentata):** la tesi "KRACK e un difetto di stato del protocollo, non
> delle primitive" e **dimostrata meccanicamente** in [`../FORMAL-MODELS/wpa2-4way-handshake/`](../FORMAL-MODELS/wpa2-4way-handshake/results.md).
> Un model checker a stati espliciti del 4-way handshake sotto avversario Dolev-Yao (primitive assunte
> perfette) trova l'attacco KRACK nel modello vulnerabile (controesempio a 4 passi: il replay di M3
> reinstalla la PTK e azzera il contatore dei nonce) e verifica esaustivamente l'assenza del difetto
> nel modello corretto. Invariante violato = iniettivita dell'installazione della chiave (freshness).
> Il nome formale di questa proprieta e **injective agreement** nella gerarchia di [Lowe 1997]:
> [`../THEORY-ADVANCED.md`](../THEORY-ADVANCED.md) Parte III colloca KRACK come sua violazione, e la
> Parte II fornisce il bound di concrete security dell'attacco offline a WPA2-PSK (sez. 3.2).

---

## 4. Analisi quantitativa

### 4.1 Lo spettro di robustezza delle tecnologie RFID

Le tecnologie RFID formano uno spettro quantificabile per costo di attacco:

```
LF EM4100 (read-only, ID in chiaro)   -> costo clonazione: leggi+scrivi (~secondi)
HF MIFARE Classic (Crypto-1, 48 bit)  -> costo: recupero chiavi nested/darkside (~minuti)
HF DESFire (AES-128, challenge-resp)  -> costo: proibitivo (nessun attacco pratico via dump)
```

La progressione mostra che la robustezza non e binaria ma un continuo determinato dalla presenza e dalla forza dell'autenticazione crittografica. La scelta tecnologica deve corrispondere al modello di minaccia: una tecnologia di sola identificazione (EM4100) usata per il controllo accessi e un abuso, non una debolezza implementativa.

### 4.2 Il costo del cracking WPA2 e la memory-hardness assente

Le 4096 iterazioni PBKDF2 riducono il throughput dell'attacco di un fattore ~4096 rispetto a un hash grezzo, portando le GPU dai miliardi di tentativi/secondo (NTLM) a poche centinaia di migliaia (WPA2). Tuttavia, PBKDF2 non e memory-hard (sezione 4.2 del modulo 04): il vantaggio del parallelismo GPU/ASIC resta. Questo spiega quantitativamente perche una PSK di 8 cifre numeriche (entropia ~26 bit, ~10^8 candidati) cade in minuti mentre una passphrase di 18 caratteri ad alta entropia e irraggiungibile: l'unica leva reale, dato PBKDF2 fisso dallo standard, e l'entropia della passphrase.

---

## 5. Rassegna della letteratura

La rottura di Crypto-1 e documentata da [Nohl et al. 2008] (reverse engineering) e [Garcia et al. 2008] (crittanalisi), esemplari del fallimento della security-by-obscurity [Kerckhoffs 1883]. La caduta di WEP risale a [Fluhrer et al. 2001]. Gli attacchi ai protocolli WiFi moderni sono di [Vanhoef & Piessens 2017] (KRACK, WPA2) e [Vanhoef & Ronen 2020] (Dragonblood, WPA3). La derivazione delle chiavi WPA2 usa PBKDF2 [Kaliski 2000]; i canali laterali si richiamano a [Kocher 1996]. Il modello di avversario deriva da [Dolev & Yao 1983]; l'inquadramento entropico da [Shannon 1949]. Le botnet IoT che sfruttano dispositivi wireless deboli sono analizzate da [Antonakakis et al. 2017] (Mirai).

---

## 6. Limiti e problemi aperti

1. **Legacy irremovibile.** MIFARE Classic ed EM4100 restano deployati in miliardi di installazioni per costo e inerzia, nonostante la rottura crittografica sia nota dal 2008. La migrazione e un problema economico-logistico, non tecnico: un limite pratico irrisolto.

2. **Verifica formale dei protocolli wireless.** KRACK e Dragonblood dimostrano che difetti di protocollo sopravvivono a primitive sicure. La verifica formale esaustiva delle macchine a stati dei protocolli 802.11 (incluse le implementazioni) resta incompleta.

3. **Autenticazione mutua usabile.** L'Evil Twin e neutralizzato solo dall'autenticazione mutua con validazione del certificato server (EAP-TLS), ma la sua configurazione client corretta (rifiuto dei certificati non validi) e frequentemente disattesa, riaprendo il divario sistema-verso-umano del modulo 05.

---

## 7. Sintesi e collegamento alla pratica

I finding `WIFI-` del modulo istanziano questo quadro: il cracking WPA2/PMKID (WIFI-002/003) e l'attacco offline della sezione 3.2; l'Evil Twin (WIFI-004) e la violazione dell'autenticazione mutua e la versione radio del divario del modulo 05; il replay RF (WIFI-009) e la violazione della freshness della sezione 3.3; la clonazione MIFARE/EM4100 (WIFI-010/011/012) e la confusione identificazione/autenticazione della sezione 3.4. Le contromisure raccomandate nei README - WPA3-SAE, EAP-TLS, rolling code, DESFire AES - sono le traduzioni operative dei principi qui formalizzati. Il modulo dimostra in forma fisica e tangibile principi (freshness, autenticazione mutua, identita non-segreta, Kerckhoffs) che ricorrono in tutto il percorso, dal web (modulo 03) al cloud (modulo 10).

---

## Riferimenti

Sottoinsieme della bibliografia master (`../REFERENCES.md`) rilevante per questo modulo:

- [Nohl et al. 2008], [Garcia et al. 2008] - rottura di Crypto-1/MIFARE.
- [Fluhrer et al. 2001] - debolezze di RC4 (WEP).
- [Vanhoef & Piessens 2017] - KRACK (WPA2).
- [Vanhoef & Ronen 2020] - Dragonblood (WPA3).
- [Kerckhoffs 1883] - inefficacia della security-by-obscurity.
- [Kaliski 2000] - PBKDF2 (derivazione chiave WPA2).
- [Kocher 1996] - attacchi a canale laterale.
- [Dolev & Yao 1983], [Shannon 1949] - modello di avversario ed entropia.
- [Antonakakis et al. 2017] - Mirai (IoT).

---

> **Nota:** Documento a scopo educativo, complementare ai README operativi. Le citazioni rimandano a fonti reali elencate in `../REFERENCES.md`.
