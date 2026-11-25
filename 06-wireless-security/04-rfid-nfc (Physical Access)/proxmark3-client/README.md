> [English](README.en.md) | **Italiano**

# Proxmark3 - hardware professionale per RFID LF/HF

> - **Fase:** Wireless Security - Advanced Physical Access (RFID Low & High Frequency)
> - **Visibilita:** Zero verso il sistema di controllo accessi; richiede prossimita fisica al tag/lettore
> - **Prerequisiti:** Proxmark3 (RDV4 consigliato) con antenne LF e HF; client Proxmark3 (pm3) compilato; accesso fisico al tag target; per lo sniffing: prossimita al lettore durante una transazione legittima
> - **Output:** WIFI-012; lettura/clonazione di tag Low Frequency (125 kHz) che l'ACR122U non gestisce; sniffing delle transazioni lettore-tag; emulazione di badge senza tag fisico

- **Ambiente Operativo:** Kali Linux (Attaccante), Proxmark3 RDV4, tag LF (EM4100, HID Prox) e HF di laboratorio
- **Target:** Badge LF EM4100 di test, badge HID Prox, badge MIFARE Classic
- **Tool principali:** Proxmark3 client (pm3), Iceman firmware

---

## Executive summary

Il Proxmark3 e lo strumento professionale di riferimento per la sicurezza RFID: dove i lettori economici come l'ACR122U (`../nfc-tools/`) si limitano al MIFARE Classic HF a 13.56 MHz, il Proxmark3 copre l'intero spettro RFID - sia Low Frequency (125/134 kHz: EM4100, HID Prox, Indala) sia High Frequency (13.56 MHz: MIFARE, iCLASS, DESFire) - e aggiunge capacita che i lettori consumer non hanno: sniffing delle transazioni, emulazione di tag senza hardware fisico, e attacchi avanzati ai sistemi protetti.

Questa distinzione e cruciale nel mondo reale del controllo accessi aziendale. Moltissimi badge aziendali, specie nelle installazioni meno recenti, usano tecnologie Low Frequency come EM4100 o HID Prox, che l'ACR122U non puo nemmeno leggere. Il finding WIFI-012 documenta la lettura e clonazione di un badge LF EM4100 di test, una tecnologia ancora piu debole del MIFARE Classic: l'EM4100 trasmette semplicemente un identificativo a 40 bit in chiaro, senza alcuna autenticazione, rendendo la clonazione un'operazione di lettura e riscrittura banale.

---

## Struttura della cartella

```
proxmark3-client/
+-- README.md      # questo file: LF/HF, sniffing, emulazione con Proxmark3 (WIFI-012)
+-- img/           # sessione client pm3
```

---

## Lettura e clonazione LF (EM4100)

**ID Finding:** `WIFI-012` | **Severity:** `Alto` (badge Low Frequency letto e clonato - accesso fisico; EM4100 privo di qualsiasi autenticazione)

### Contesto operativo

L'EM4100 e una delle tecnologie RFID piu diffuse e piu deboli: un tag read-only a 125 kHz che trasmette in loop un identificativo a 40 bit, senza cifratura ne autenticazione. Il Proxmark3 lo legge e ne scrive una copia su un tag T5577 (tag LF riscrivibile), producendo un clone in pochi secondi.

### PoC - fase 1: identificazione e lettura LF

```Bash
# Avvio del client Proxmark3
pm3

# Rilevamento automatico della tecnologia LF del tag
[usb] pm3 --> lf search
```

```
[+] Chipset detection: EM4100 / EM4102 (125 kHz)
[+] EM 410x ID found: 1A2B3C4D5E                    <-- ID a 40 bit del badge (in chiaro)
[+] Valid EM410x ID found!
```

### PoC - fase 2: clonazione su tag T5577

```Bash
# Scrittura dell'ID letto su un tag T5577 riscrivibile
[usb] pm3 --> lf em 410x clone --id 1A2B3C4D5E
```

```
[=] Preparing to clone EM4100 to T5577 with ID 1A2B3C4D5E
[+] Done, written to T5577                            <-- clone LF completato (WIFI-012)
[?] Hint: try `lf search` to verify
```

### PoC - fase 3: emulazione (senza tag fisico)

```Bash
# Il Proxmark3 puo emulare direttamente il badge, senza scrivere alcun tag
[usb] pm3 --> lf em 410x sim --id 1A2B3C4D5E
```

```
[=] Simulating EM410x - ID 1A2B3C4D5E
[=] Stop simulation by pressing the button           <-- il Proxmark3 E il badge
```

L'emulazione permette di presentarsi al lettore di controllo accessi direttamente con il Proxmark3, senza nemmeno bisogno di un tag fisico clone.

### Remediation

- **Azione immediata:** identificare e sostituire i badge Low Frequency (EM4100, HID Prox): trasmettono un ID in chiaro senza alcuna protezione e sono i piu banali da clonare
- **Azione strutturale:** migrare a tecnologie High Frequency crittografiche con autenticazione mutua (DESFire EV3 AES, Seos, iCLASS SE); l'ID del badge non deve mai essere un semplice numero leggibile ma il risultato di una sfida crittografica; implementare multi-fattore per le aree sensibili e correlazione dei log di accesso
- **Verifica:** tentare `lf search` e la clonazione sui nuovi badge - le tecnologie sicure non devono esporre un ID clonabile ne permettere la copia via dump

---

## Sniffing delle transazioni

### Contesto operativo

Oltre alla lettura diretta del tag, il Proxmark3 puo intercettare (sniffing) la comunicazione tra un lettore legittimo e un tag durante una transazione reale. E utile quando il tag non e accessibile direttamente ma lo e il momento in cui viene usato, o per analizzare protocolli proprietari osservando lo scambio.

```Bash
# Sniffing di una transazione HF (14443A) tra lettore e badge
[usb] pm3 --> hf 14a sniff
# [presentare il badge al lettore legittimo durante lo sniffing]
[usb] pm3 --> trace list -t 14a
```

```
      Src | Data                        | Annotation
      Rdr | 52                          | WUPA
      Tag | 04 00                       | ATQA
      Rdr | 93 20                       | ANTICOLL
      Tag | a1 b2 c3 d4 ...             | UID       <-- transazione catturata
```

---

## Esperienza di laboratorio

Il Proxmark3 ha colmato esattamente il limite che l'ACR122U aveva mostrato in `../nfc-tools/`: la gestione del Low Frequency. Il badge EM4100 di test, invisibile all'ACR122U, e stato letto e clonato dal Proxmark3 in un'unica sessione di pochi secondi. Questo ha reso concreta una realta del controllo accessi aziendale: molte installazioni usano ancora LF, e la loro sicurezza e persino inferiore a quella del MIFARE Classic, perche manca del tutto l'autenticazione.

La curva di apprendimento e stata sul client pm3 e sulla sua sintassi a comandi (evoluta significativamente con il firmware Iceman, che e diventato lo standard de facto rispetto al firmware ufficiale). La ricchezza di comandi (`lf`, `hf`, `emv`, `hf mf`, con decine di sottocomandi) e insieme la forza e la difficolta dello strumento: copre praticamente ogni scenario RFID, ma richiede di sapere esattamente quale tecnologia si sta attaccando.

La funzione piu istruttiva e stata l'emulazione: la capacita del Proxmark3 di "diventare" il badge senza scrivere alcun tag fisico ha ribaltato la mia idea di clonazione. Non serve produrre una copia fisica; lo strumento stesso, presentato al lettore, e sufficiente. Per un assessment di sicurezza fisica questo e potentissimo, perche elimina la necessita di tag magic specifici per ogni tecnologia.

---

## Analisi teorica: lo spettro di debolezza delle tecnologie RFID

Le tecnologie RFID formano uno spettro di sicurezza che va dal completamente aperto al crittograficamente robusto, e il Proxmark3, coprendo tutto lo spettro, permette di apprezzarne le differenze:

1. **LF read-only (EM4100, HID Prox):** trasmettono un ID statico in chiaro, nessuna autenticazione. Clonazione banale (leggi e scrivi). Sicurezza nulla: equivalgono a un numero di serie stampato ad alta voce.

2. **HF con Crypto-1 (MIFARE Classic):** cifratura presente ma rotta (vedere `../nfc-tools/`). Richiede il recupero delle chiavi ma poi e clonabile. Sicurezza illusoria.

3. **HF con AES (DESFire EV3, Seos):** autenticazione mutua challenge-response su AES-128, chiave mai esposta. Non clonabile tramite dump. Sicurezza reale.

La progressione tecnologica riflette l'evoluzione del modello di minaccia. LF nasce quando l'RFID serviva solo a identificare (magazzino, bestiame), non ad autenticare accessi; usarlo per il controllo accessi e un abuso di una tecnologia mai progettata per resistere a un avversario. La lezione, valida in tutta la sicurezza, e che la scelta tecnologica deve corrispondere al modello di minaccia: una tecnologia di identificazione non e una tecnologia di autenticazione, e trattarle come equivalenti (come fa chi usa EM4100 per aprire le porte) e l'errore di progettazione alla radice di questi finding.

---

## Scenario reale: proiezione Post-Exploitation

> Questa sezione descrive come questo finding si inserirebbe in un engagement reale, sia dal punto di vista dell'attaccante (Red Team) che del difensore (Blue Team).

### Prospettiva attaccante (red team)

**Punto di partenza:** capacita di clonare o emulare badge RFID LF/HF, incluse le tecnologie che i lettori consumer non gestiscono (WIFI-012).

**Passo successivo immediato:** accesso fisico non autorizzato presentando il clone o l'emulazione al lettore di controllo accessi.

**Kill Chain proiettata:**

```
[WIFI-012] Badge LF/HF clonato o emulato
        |
        v
Accesso fisico all'edificio / aree riservate
        |
        v
Server room / postazioni non bloccate / drop di implant
        |
        v
Foothold interno -> pivoting di rete (07-post-exploitation)
```

**Impatto potenziale:** il Proxmark3 estende la capacita di clonazione a tutte le tecnologie RFID, incluse quelle piu diffuse nel controllo accessi legacy (LF). L'emulazione elimina persino la necessita di un tag fisico. In un red team di sicurezza fisica, uno strumento tascabile che clona qualsiasi badge letto (anche via sniffing a distanza dal lettore) e il grimaldello universale. Il vettore alimenta l'accesso alla rete interna e si combina con il social engineering per ottenere la prossimita necessaria.

### Prospettiva difensore (blue team)

**Rilevamento:** come per la clonazione MIFARE, il clone/emulazione e trasparente al lettore. La difesa e nell'analisi dei log e nella correlazione con altri sistemi (videosorveglianza, presenze).

**Indicatori di Compromissione (IOC):**
- Accessi con badge LF in contesti che dovrebbero essere migrati a HF sicuro
- Usi impossibili o anomali del badge ID (log analysis)
- Violazioni anti-passback
- Presenza fisica di dispositivi RFID sospetti (Proxmark3, [Flipper](https://github.com/Nicholas-Arcari/FlipperZero-guide)) rilevata da ispezioni o metal detector nelle aree critiche

**Contenimento:** disattivazione del badge ID; sostituzione con tecnologia sicura; audit degli accessi recenti.

**Eradicazione e hardening:**
- Dismissione completa delle tecnologie LF read-only per il controllo accessi
- Migrazione a DESFire/Seos con autenticazione crittografica
- Anti-passback, correlazione log, multi-fattore per le aree critiche
- Schermatura RFID dei badge in dotazione e formazione anti-skimming

**Lezione difensiva:** la capacita di un singolo strumento (il Proxmark3) di attaccare l'intero spettro RFID dimostra che la difesa non puo basarsi sull'oscurita della tecnologia o sulla rarita degli strumenti. L'unica difesa strutturale e crittografica: badge che dimostrano la propria autenticita con una sfida che un clone non puo superare. Tutto il resto e sicurezza apparente.

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Proxmark3 RDV4` | rfid multi-tool | hardware + client | lf+hf: lettura, clonazione, sniffing, emulazione (riferimento professionale) |
| `Iceman firmware` | pm3 firmware | firmware | firmware community standard, piu comandi e tecnologie del firmware ufficiale |
| `pm3 client` | rfid cli | cli | interfaccia a comandi per tutte le operazioni rfid |
| tag T5577 | hardware | - | tag lf riscrivibile per i cloni Low frequency |
| `Flipper Zero` | portable multi-tool | hardware | lf/hf lettura ed emulazione in form factor tascabile |
| `ACR122U` | nfc reader | hardware | solo hf mifare classic (`../nfc-tools/`); non gestisce lf |

> **Tool moderno consigliato:** il `Proxmark3 RDV4` con firmware `Iceman` e lo standard professionale per la sicurezza RFID completa. Il `Flipper Zero` e l'alternativa tascabile per gli scenari LF/HF comuni e le dimostrazioni sul campo, con un'usabilita superiore a fronte di capacita leggermente ridotte sui tag piu protetti.

---

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| reconnaissance | gather victim host information | `T1592` | identificazione della tecnologia rfid (lf/hf) del badge tramite `lf/hf search` (WIFI-012) |
| credential access | network sniffing | `T1040` | sniffing della transazione tra lettore e badge (WIFI-012) |
| defense evasion | impersonation | `T1656` | clonazione/emulazione del badge per impersonare il titolare (WIFI-012) |
| initial access | hardware additions | `T1200` | utilizzo del proxmark3 (clone o emulazione) per l'accesso fisico non autorizzato (WIFI-012) |
| initial access | valid accounts: local accounts | `T1078.003` | il badge clonato/emulato equivale a una credenziale di accesso valida del titolare |

---

> **Nota:** Tutte le attivita documentate sono state condotte su tag e badge RFID di laboratorio di proprieta dell'autore. Lettura, clonazione, sniffing ed emulazione sono stati eseguiti esclusivamente su token di test. La clonazione e l'uso non autorizzato di badge di accesso di terzi costituisce reato grave. Le tecniche sono documentate a scopo educativo e di security assessment fisico autorizzato con perimetro definito.
