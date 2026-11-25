> [English](README.en.md) | **Italiano**

# MIFARE Cloning - Clonazione di Badge di Accesso

> - **Fase:** Wireless Security - Physical Access / Badge Impersonation (NFC/RFID 13.56 MHz)
> - **Visibilita:** Zero verso il sistema di controllo accessi - un badge clonato e indistinguibile dall'originale; l'unica traccia e nei log di accesso (un badge usato in due luoghi/tempi incompatibili)
> - **Prerequisiti:** Dump completo e chiavi del badge target (da `../nfc-tools/`, WIFI-010); tag "magic" scrivibile (Gen1a/Gen2 con blocco 0 modificabile); lettore/scrittore compatibile
> - **Output:** WIFI-011; badge clone funzionante con UID e contenuto identici all'originale; capacita di impersonare il titolare del badge per l'accesso fisico

- **Ambiente Operativo:** Kali Linux (Attaccante), ACR122U + tag "magic" UID-changeable, badge di laboratorio
- **Target:** Badge MIFARE Classic 1K di test (dump e chiavi da WIFI-010)
- **Tool principali:** nfc-mfclassic, libnfc, Mifare Classic Tool, Proxmark3

---

## Executive Summary

La clonazione trasforma il dump di un badge (`../nfc-tools/`, WIFI-010) in un token fisico funzionante e indistinguibile dall'originale. E il passo che concretizza l'attacco: non basta leggere un badge, bisogna produrne una copia che il lettore di controllo accessi accetti come autentica.

L'ostacolo tecnico principale e l'UID. Su un tag MIFARE Classic normale, l'UID (blocco 0, settore 0) e impostato di fabbrica e non modificabile. Se il sistema di controllo accessi verifica l'UID (pratica comune), un clone su tag standard fallisce. La soluzione sono i tag "magic" (Gen1a, Gen2, Gen3): tag speciali il cui blocco 0 e scrivibile, permettendo di impostare qualsiasi UID e ottenere un clone perfetto.

Il finding WIFI-011 documenta la produzione di un clone completo del badge di test su un tag magic. Il clone replica UID, chiavi e contenuto: presentato al lettore, e accettato come il badge originale. Questo dimostra il fallimento di sicurezza dei sistemi che si affidano a MIFARE Classic o alla sola verifica dell'UID per l'autenticazione degli accessi.

---

## Struttura della cartella

```
mifare-cloning/
+-- README.md      # questo file: clonazione badge MIFARE su tag magic (WIFI-011)
+-- img/           # scrittura del clone e verifica
```

---

## Clonazione su Tag Magic

**ID Finding:** `WIFI-011` | **Severity:** `Alto` (badge di accesso clonato e funzionante - impersonation fisica del titolare)

### Contesto operativo

Il dump ottenuto in WIFI-010 (`badge_dump.mfd`) contiene l'intero contenuto del badge originale, inclusi UID e chiavi. Per creare un clone accettato anche dai sistemi che verificano l'UID, si scrive il dump su un tag magic il cui blocco 0 e modificabile.

### PoC - Fase 1: Verifica del tag magic

```Bash
# Identificazione del tag magic (accetta comandi di scrittura del blocco 0)
nfc-list
```

```
    UID (NFCID1): 00  00  00  00       <-- tag magic vergine (UID di default)
    MIFARE Classic 1K (Gen1a magic)     <-- blocco 0 scrivibile
```

### PoC - Fase 2: Scrittura del clone

```Bash
# Scrittura dell'intero dump (incluso blocco 0/UID) sul tag magic
nfc-mfclassic W a u badge_dump.mfd badge_dump.mfd
# W = write, a = usa chiavi A, u = scrivi anche il blocco 0 (UID) - richiede tag magic
```

```
Writing 64 blocks |................................................................|
Done, 64 of 64 blocks written.
Writing block 0 (UID)...                          <-- UID clonato (solo su magic)
Done.                                             <-- clone completo scritto (WIFI-011)
```

### PoC - Fase 3: Verifica del clone

```Bash
# Rilettura del clone per confronto con l'originale
nfc-list
```

```
    UID (NFCID1): a1  b2  c3  d4       <-- UID identico all'originale (a1b2c3d4)
    MIFARE Classic 1K
```

L'UID del clone (`a1b2c3d4`) corrisponde esattamente a quello del badge originale letto in WIFI-010. Il clone e ora indistinguibile dall'originale per il lettore di controllo accessi.

### Remediation

- **Azione immediata:** non affidarsi mai all'UID come unico fattore di autenticazione (e falsificabile su tag magic); sostituire i badge MIFARE Classic con tecnologie crittografiche
- **Azione strutturale:** migrare a MIFARE DESFire EV3 (AES-128) o Seos/iCLASS SE con autenticazione mutua challenge-response: questi sistemi non sono clonabili tramite dump perche il segreto crittografico non lascia mai il chip e ogni autenticazione e una sfida crittografica unica; implementare rilevamento anti-passback (un badge non puo entrare due volte senza essere uscito) e correlazione dei log; aggiungere un secondo fattore (PIN, biometria) per le aree critiche
- **Verifica:** tentare la clonazione sui nuovi badge DESFire - deve fallire perche le chiavi AES non sono estraibili dal dump; verificare che l'anti-passback rilevi l'uso simultaneo di due badge con stesso ID

---

## Esperienza di Laboratorio

Il punto di svolta e stata la comprensione del ruolo dei tag magic. Il primo tentativo di clonazione su un tag MIFARE Classic standard e fallito nella scrittura del blocco 0: l'UID era immutabile, e il clone risultante aveva un UID diverso dall'originale. Il sistema di controllo accessi di test, che verificava l'UID, lo rifiutava. Il passaggio a un tag magic Gen1a - il cui blocco 0 accetta la scrittura - ha risolto il problema producendo un clone con UID identico.

Questo ha chiarito una distinzione operativa fondamentale: la clonabilita di un badge dipende sia dalla debolezza crittografica del sistema (MIFARE Classic, chiavi recuperabili) sia dalla disponibilita dell'hardware giusto (tag magic per l'UID). Entrambe le condizioni erano soddisfatte nel laboratorio, come lo sono in moltissime installazioni reali dove i tag magic costano pochi euro e MIFARE Classic e ancora lo standard.

L'osservazione conclusiva riguarda la rilevabilita: un clone e perfetto per il lettore, ma non per i log. Un badge che registra un accesso in due sedi distanti a pochi minuti di distanza e un indicatore di clonazione evidente per chi analizza i log - il motivo per cui l'anti-passback e la correlazione dei log sono contromisure preziose anche quando la clonazione non e prevenibile a monte.

---

## Analisi Teorica: UID Spoofing e il Fallimento dell'Identita come Segreto

La clonazione MIFARE illustra un errore concettuale ricorrente: usare un identificativo pubblico come se fosse un segreto di autenticazione. L'UID di un tag e progettato per l'anti-collisione (distinguere piu tag nel campo del lettore), non per l'autenticazione: e trasmesso in chiaro a ogni interrogazione e, sui tag magic, e liberamente impostabile. Un sistema che concede l'accesso basandosi sull'UID sta autenticando "qualcosa che chiunque puo leggere e chiunque puo falsificare".

L'autenticazione robusta richiede la dimostrazione del possesso di un segreto senza rivelarlo. E cio che fa DESFire con AES: il lettore invia una sfida (challenge), il tag la cifra con una chiave AES che non lascia mai il chip, e il lettore verifica la risposta. Un attaccante che clona il contenuto leggibile non ottiene la chiave (che non e leggibile) e non puo rispondere correttamente alla sfida. La sicurezza risiede nella chiave segreta e nel protocollo challenge-response, non nell'identificativo.

Questo e lo stesso principio che distingue, in ambito web, un ID di sessione prevedibile da un token crittografico, o l'invio di una password dal suo hash challenge-response. La lezione trasversale: l'identita non deve mai essere il segreto. Un sistema sicuro separa "chi dici di essere" (UID, pubblico) da "la prova che lo sei" (challenge-response su chiave segreta), e MIFARE Classic collassa proprio perche non mantiene questa separazione.

---

## Scenario Reale: Proiezione Post-Exploitation

> Questa sezione descrive come questo finding si inserirebbe in un engagement reale, sia dal punto di vista dell'attaccante (Red Team) che del difensore (Blue Team).

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** badge di accesso clonato e funzionante, indistinguibile dall'originale (WIFI-011).

**Passo successivo immediato:** accesso fisico non autorizzato all'edificio o alle aree riservate presentando il clone al lettore, impersonando il titolare legittimo.

**Kill Chain proiettata:**

```
[WIFI-011] Badge clonato funzionante
        |
        v
Accesso fisico all'edificio (impersonando il titolare)
        |
        v
Accesso ad aree riservate (server room, uffici)
        |
        v
Drop di implant di rete / accesso a postazioni sbloccate / furto dati
        |
        v
Foothold interno -> pivoting verso la rete (07-post-exploitation)
```

**Impatto potenziale:** un badge clonato annulla il perimetro di sicurezza fisica. L'attaccante ottiene, con pochi secondi di prossimita al badge originale (via skimming o social engineering) e materiale da pochi euro, la stessa capacita di accesso del dipendente legittimo. In contesti ad alta sicurezza (data center, aree industriali), questo e spesso il punto di ingresso piu economico e silenzioso. Il vettore si integra con `05-social-engineering/` (ottenere la prossimita) e apre la fase di accesso alla rete interna.

### Prospettiva Difensore (Blue Team)

**Rilevamento:** un badge clonato e identico all'originale per il lettore, quindi non rilevabile al momento dell'accesso. La rilevazione avviene tramite l'analisi dei log: usi impossibili (stessa card in due luoghi in tempi incompatibili) o anomali (accessi fuori orario, aree mai usate dal titolare).

**Indicatori di Compromissione (IOC):**
- Stesso badge ID registrato in sedi diverse in una finestra temporale incompatibile
- Accessi del badge in orari o aree anomali rispetto al pattern del titolare
- Violazioni anti-passback (ingresso senza precedente uscita)
- Correlazione negativa badge/videosorveglianza (badge del dipendente X usato mentre X e altrove)

**Contenimento:** disattivazione immediata del badge ID compromesso; emissione di un nuovo badge su tecnologia sicura; revisione degli accessi recenti del badge.

**Eradicazione e hardening:**
- Migrazione a DESFire EV3 (AES) o Seos: eliminazione strutturale della clonabilita
- Anti-passback e correlazione automatica dei log di accesso
- Multi-fattore per le aree critiche (badge + PIN/biometria)
- Formazione anti-skimming: proteggere il badge (custodie schermate RFID) e diffidare dei lettori sospetti

**Lezione difensiva:** la sicurezza fisica basata su token clonabili e sicurezza apparente. Un sistema di controllo accessi deve autenticare crittograficamente il token, non fidarsi di un identificativo leggibile e falsificabile. Dove la migrazione tecnologica non e immediata, la correlazione dei log e il rilevamento comportamentale sono l'unica rete di sicurezza contro la clonazione.

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `nfc-mfclassic` | MIFARE writer | CLI | Scrittura del dump su tag (incluso blocco 0 su magic) |
| `libnfc` | NFC library | CLI | Interfaccia con lettori NFC per lettura/scrittura |
| `Mifare Classic Tool` | NFC app | Android | Clonazione da smartphone con NFC (lettura+scrittura) |
| Tag magic Gen1a/Gen2 | Hardware | - | Tag con blocco 0 (UID) scrivibile per clone perfetto |
| `Proxmark3` | RFID multi-tool | Hardware | Clonazione avanzata, tag protetti, LF+HF (`../proxmark3-client/`) |
| [Flipper Zero](https://github.com/Nicholas-Arcari/FlipperZero-guide) | Portable multi-tool | Hardware | Lettura/emulazione/clonazione NFC portatile |

> **Tool moderno consigliato:** il `Proxmark3 RDV4` e lo standard professionale per la clonazione (gestisce tag magic, protetti, LF e HF, ed emula i badge senza tag fisico). Il `Flipper Zero` offre emulazione e clonazione NFC in un dispositivo tascabile, ideale per dimostrazioni e assessment sul campo.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Resource Development | Develop Capabilities | `T1587` | Produzione di un badge clone funzionante su tag magic (WIFI-011) |
| Defense Evasion | Impersonation | `T1656` | Il badge clonato impersona il titolare legittimo verso il controllo accessi (WIFI-011) |
| Initial Access | Hardware Additions | `T1200` | Utilizzo del badge clonato per ottenere accesso fisico non autorizzato (WIFI-011) |
| Initial Access | Valid Accounts: Local Accounts | `T1078.003` | Il clone equivale a una credenziale di accesso fisico valida del titolare |

---

> **Nota:** Tutte le attivita documentate sono state condotte su badge NFC/RFID di laboratorio di proprieta dell'autore. La clonazione e stata eseguita esclusivamente su token di test. La clonazione e l'uso di badge di accesso di terzi senza autorizzazione costituisce reato grave (accesso abusivo a sistemi/luoghi, furto d'identita, sostituzione di persona). Le tecniche sono documentate a scopo educativo e di security assessment fisico autorizzato con perimetro definito.
