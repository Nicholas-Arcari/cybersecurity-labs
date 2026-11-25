> [English](README.en.md) | **Italiano**

# NFC Tools - Lettura ed Enumerazione di Tag NFC/RFID HF

> - **Fase:** Wireless Security - Physical Access Reconnaissance (NFC/RFID 13.56 MHz)
> - **Visibilita:** Zero - la lettura NFC richiede prossimita fisica (pochi centimetri) ma non lascia traccia sul sistema target; e un'operazione passiva dal punto di vista del controllo accessi
> - **Prerequisiti:** Lettore NFC compatibile libnfc (ACR122U, PN532); accesso fisico temporaneo al tag/badge target; libnfc e mfoc/mfcuk installati
> - **Output:** WIFI-010; identificazione del tipo di tag (UID, tecnologia); recupero delle chiavi di settore su tag MIFARE Classic con chiavi deboli; dump del contenuto del tag

- **Ambiente Operativo:** Kali Linux (Attaccante), lettore ACR122U (13.56 MHz), tag/badge NFC di laboratorio
- **Target:** Badge MIFARE Classic 1K di test, tag NTAG213
- **Tool principali:** libnfc (nfc-list, nfc-mfclassic), mfoc, Mifare Classic Tool

---

## Executive Summary

Questa sezione entra nella zona di confine tra sicurezza informatica e sicurezza fisica: i badge di controllo accessi, le carte d'albergo, gli abbonamenti dei trasporti e molti sistemi di identificazione operano su NFC/RFID a 13.56 MHz (High Frequency). L'obiettivo non e una rete ma un token fisico di identita, e comprometterlo significa impersonare la persona a cui appartiene.

La tecnologia dominante in questo spazio, MIFARE Classic, e crittograficamente rotta dal 2008 (attacchi Nohl/Plotz e Garcia et al. all'algoritmo proprietario Crypto-1). Nonostante questo, resta diffusissima in badge aziendali e sistemi legacy per ragioni di costo e inerzia. Il finding WIFI-010 documenta il recupero delle chiavi di un badge MIFARE Classic di test tramite l'attacco mfoc, che sfrutta le debolezze di Crypto-1 per derivare le chiavi di settore a partire da una sola chiave nota (spesso una delle chiavi di default mai cambiate).

Questa sezione copre la lettura e l'enumerazione (identificare la tecnologia, recuperare le chiavi, fare il dump); la clonazione vera e propria e documentata in `../mifare-cloning/`, mentre `../proxmark3-client/` copre l'hardware professionale per gli scenari che l'ACR122U non gestisce (Low Frequency 125 kHz, tag protetti).

---

## Struttura della cartella

```
nfc-tools/
+-- README.md      # questo file: lettura, identificazione, key recovery MIFARE (WIFI-010)
+-- img/           # dump nfc-list e recupero chiavi mfoc
```

---

## Identificazione e Lettura del Tag

**ID Finding:** `WIFI-010` | **Severity:** `Medio` (recupero chiavi e dump di un badge MIFARE Classic; premessa diretta della clonazione e dell'accesso non autorizzato)

### Contesto operativo

Il primo passo e identificare il tipo di tag: la tecnologia (MIFARE Classic, Ultralight, NTAG, DESFire) determina completamente l'approccio di attacco. `nfc-list` interroga qualsiasi tag in prossimita e ne rivela UID, tipo e ATQA/SAK (i parametri che identificano la famiglia).

### Esecuzione

```Bash
# Identificazione del tag in prossimita del lettore
nfc-list
```

```
NFC device: ACS / ACR122U opened
1 ISO14443A passive target(s) found:
    ATQA (SENS_RES): 00  04
       UID (NFCID1): a1  b2  c3  d4              <-- UID del badge
      SAK (SEL_RES): 08
     MIFARE Classic 1K                            <-- tecnologia vulnerabile (Crypto-1)
```

Il SAK `08` e la stringa "MIFARE Classic 1K" identificano un tag basato su Crypto-1, l'algoritmo proprietario NXP rotto crittograficamente.

### Esecuzione - Recupero delle chiavi con mfoc

### Contesto operativo

MIFARE Classic 1K organizza la memoria in 16 settori, ciascuno protetto da due chiavi (A e B). mfoc (MIFARE Offline Cracker) sfrutta una debolezza di Crypto-1: se anche una sola chiave di un settore e nota (tipicamente una chiave di default che l'installatore non ha mai cambiato), l'attacco "nested" recupera tutte le altre chiavi sfruttando la debolezza del generatore di numeri pseudo-casuali del tag.

```Bash
# Recupero di tutte le chiavi partendo dalle chiavi di default note, dump su file
mfoc -O badge_dump.mfd
```

```
[Key: ffffffffffff] found for sector 00 (as key A)   <-- chiave di default mai cambiata
Nested attack...
[Key: a0a1a2a3a4a5] recovered for sector 01           <-- chiave recuperata via nested
[Key: d3f7d3f7d3f7] recovered for sector 02
...
Auth with all sectors succeeded, dumping keys to a file!
Card dump written to badge_dump.mfd                   <-- dump completo (WIFI-010)
```

Il dump `badge_dump.mfd` contiene ora l'intero contenuto del badge e tutte le chiavi: il materiale necessario per la clonazione (`../mifare-cloning/`).

### Remediation

- **Azione immediata:** identificare e sostituire i badge basati su MIFARE Classic; verificare che nessun settore usi le chiavi di default (`FFFFFFFFFFFF`, `A0A1A2A3A4A5`)
- **Azione strutturale:** migrare a tecnologie con crittografia robusta e autenticazione mutua: MIFARE DESFire EV3 (AES-128, 3DES), iCLASS SE, o sistemi basati su Seos. Queste tecnologie non sono clonabili con un semplice dump perche usano challenge-response crittografico; implementare un secondo fattore per gli accessi critici (PIN, biometria); ove i badge veicolino un identificativo, evitare che sia semplicemente l'UID (falsificabile)
- **Verifica:** ripetere l'attacco mfoc sui nuovi badge - su DESFire con AES l'attacco deve fallire completamente

---

## Esperienza di Laboratorio

L'aspetto piu rivelatore dell'esercizio e stato quanto l'attacco dipenda dalle chiavi di default. Il badge di test usava la chiave `FFFFFFFFFFFF` (default di fabbrica) sul settore 0: da quel singolo punto d'appoggio, mfoc ha recuperato tutte le altre chiavi in pochi minuti tramite l'attacco nested. Questo rispecchia la realta di moltissime installazioni: i sistemi vengono deployati con le chiavi di default e mai riconfigurati, rendendo l'attacco quasi immediato.

Un limite hardware importante e emerso con l'ACR122U: e un lettore economico e affidabile per MIFARE Classic 1K a 13.56 MHz, ma non gestisce i tag Low Frequency (125 kHz, molto comuni nei badge aziendali piu vecchi) ne alcune varianti protette. Per quei casi serve il Proxmark3 (`../proxmark3-client/`). La scelta del lettore vincola rigidamente cosa e attaccabile - una lezione ricorrente in tutto il dominio wireless.

Nota metodologica: l'intero attacco richiede prossimita fisica al badge. Nel laboratorio il badge era disponibile, ma in uno scenario reale la sfida principale e ottenere quei pochi secondi di prossimita - spesso tramite social engineering o un lettore nascosto (skimming), collegando questa tecnica direttamente al modulo `05-social-engineering`.

---

## Analisi Teorica: Perche MIFARE Classic e Crittograficamente Rotto

MIFARE Classic si basa su Crypto-1, un cifrario a flusso proprietario di NXP con chiave a 48 bit, mantenuto segreto secondo il principio (errato) della security by obscurity. Nel 2008, il reverse engineering del chip (Nohl e Plotz) e l'analisi crittografica (Garcia et al., Radboud University) hanno rivelato debolezze fatali: un generatore di numeri pseudo-casuali (PRNG) prevedibile e una struttura del cifrario che permette attacchi a complessita molto ridotta.

Due classi di attacco ne derivano. L'attacco "darkside" (mfcuk) recupera una prima chiave senza conoscerne alcuna, sfruttando risposte di errore del tag. L'attacco "nested" (mfoc), piu veloce, richiede una chiave nota (anche di default) e recupera tutte le altre sfruttando la prevedibilita del PRNG: conoscendo una chiave, l'attaccante puo predire i nonce e derivare le chiavi degli altri settori con pochi tentativi di autenticazione.

La lezione crittografica e duplice. Primo, la security by obscurity fallisce: un algoritmo segreto non e piu sicuro una volta reverse-engineered, e ogni algoritmo prima o poi lo e. Gli standard moderni (AES in DESFire) sono pubblici e sicuri proprio perche la loro sicurezza risiede nella chiave, non nella segretezza dell'algoritmo (principio di Kerckhoffs). Secondo, la lunghezza della chiave conta: 48 bit erano insufficienti gia nel 2008. La migrazione a DESFire (AES-128) risolve entrambi i problemi, motivo per cui e la remediation strutturale.

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `libnfc` (nfc-list) | NFC library | CLI | Identificazione e lettura di tag ISO14443A/B |
| `mfoc` | MIFARE cracker | CLI | Attacco nested: recupero chiavi da una chiave nota/default |
| `mfcuk` | MIFARE cracker | CLI | Attacco darkside: recupero chiave senza chiavi note (piu lento) |
| `Mifare Classic Tool` | NFC app | Android | Lettura/scrittura MIFARE da smartphone con NFC |
| `nfc-mfclassic` | MIFARE dump/write | CLI | Dump e scrittura del contenuto MIFARE Classic |
| `Proxmark3` | RFID multi-tool | Hardware | Hardware professionale per LF/HF e tag protetti (`../proxmark3-client/`) |

> **Tool moderno consigliato:** per il lavoro sul campo, il `Proxmark3 RDV4` o il [Flipper Zero](https://github.com/Nicholas-Arcari/FlipperZero-guide) (con modulo NFC integrato) sostituiscono l'ACR122U con capacita molto piu ampie (LF 125 kHz + HF 13.56 MHz, emulazione, attacchi avanzati). L'ACR122U resta valido per il MIFARE Classic 1K in laboratorio.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Host Information | `T1592` | Identificazione del tipo di tag NFC/RFID e dei suoi parametri (WIFI-010) |
| Credential Access | Brute Force | `T1110` | Recupero delle chiavi di settore MIFARE Classic tramite attacco nested/darkside (WIFI-010) |
| Credential Access | Steal Application Access Token | `T1528` | Estrazione del contenuto del badge (identificativo di accesso) via dump (WIFI-010) |
| Initial Access | Hardware Additions | `T1200` | Utilizzo del lettore NFC per acquisire il materiale del badge |

---

> **Nota:** Tutte le attivita documentate sono state condotte su tag e badge NFC/RFID di laboratorio di proprieta dell'autore. La lettura, il recupero delle chiavi e il dump sono stati eseguiti esclusivamente su token di test. La clonazione o l'uso non autorizzato di badge di accesso di terzi costituisce reato (accesso abusivo, furto d'identita). Le tecniche sono documentate a scopo educativo e di security assessment fisico autorizzato.
