> [English](README.en.md) | **Italiano**

# 04 - RFID / NFC (physical access)

> - **Fase:** Wireless Security - Sicurezza fisica e controllo accessi (RFID/NFC)
> - **Visibilita:** Zero verso i sistemi di controllo accessi; richiede prossimita fisica al tag o al lettore
> - **Prerequisiti:** Lettore NFC HF (ACR122U) e/o Proxmark3 (LF+HF); tag magic e T5577 per la clonazione; accesso fisico temporaneo al badge; per il campo: [Flipper Zero](https://github.com/Nicholas-Arcari/FlipperZero-guide)
> - **Output:** Finding WIFI-010..012; chiavi e dump di badge MIFARE; cloni funzionanti LF/HF; capacita di impersonare fisicamente il titolare del badge

---

## Introduzione

La sezione `04-rfid-nfc` e la zona di confine tra sicurezza informatica e sicurezza fisica: badge aziendali, carte d'albergo, abbonamenti dei trasporti e sistemi di identificazione operano su RFID/NFC. Qui l'obiettivo non e una rete ma un token fisico di identita, e comprometterlo significa impersonare la persona a cui appartiene per ottenere accesso fisico.

Come indicato negli appunti di laboratorio, questa e la zona di confine con la sicurezza fisica, con un collegamento diretto al Flipper Zero come multi-tool NFC/RFID portatile. La scelta degli strumenti dipende dall'hardware disponibile: con un semplice lettore HF (ACR122U) o smartphone Android (libnfc, Mifare Classic Tool) si copre il MIFARE Classic; con il Proxmark3 si copre anche il Low Frequency e i tag protetti.

La sezione si articola in tre fasi:

1. **NFC Tools (WIFI-010):** lettura e identificazione dei tag HF, recupero delle chiavi di settore MIFARE Classic (mfoc) e dump del contenuto. Prerequisito della clonazione.

2. **MIFARE Cloning (WIFI-011):** produzione di un clone funzionante su tag magic, incluso l'UID. Il clone e indistinguibile dall'originale per il lettore di controllo accessi.

3. **Proxmark3 Client (WIFI-012):** hardware professionale per l'intero spettro RFID (LF 125 kHz + HF 13.56 MHz), sniffing delle transazioni ed emulazione senza tag fisico. Copre le tecnologie che i lettori consumer non gestiscono.

Il filo conduttore teorico e la distinzione tra identificazione e autenticazione: MIFARE Classic (Crypto-1 rotto) ed EM4100 (nessuna autenticazione) usano un identificativo leggibile e falsificabile come se fosse un segreto. Solo le tecnologie con autenticazione crittografica mutua (DESFire AES, Seos) resistono alla clonazione.

---

## Struttura della cartella

```
04-rfid-nfc (Physical Access)/
+-- README.md              # questo file: registro WIFI-010..012 + MITRE aggregata
|
+-- nfc-tools/             # WIFI-010: lettura, key recovery MIFARE, dump (libnfc, mfoc)
+-- mifare-cloning/        # WIFI-011: clonazione su tag magic (nfc-mfclassic)
+-- proxmark3-client/      # WIFI-012: LF/HF, sniffing, emulazione (Proxmark3)
```

---

## Flusso operativo consigliato

```
[INPUT] Accesso fisico al badge target, lettore/Proxmark3
         |
         v
[1] Identificazione della tecnologia
     +-- nfc-list / lf search / hf search
     -> LF (EM4100/HID) o HF (MIFARE/DESFire)?
              |
              +-- LF EM4100 -> proxmark3-client/ (lettura+clone diretti) WIFI-012
              |
              +-- HF MIFARE Classic -> prosegui
              v
[2] Recupero chiavi e dump (nfc-tools/)
     +-- mfoc -O dump.mfd -> chiavi + contenuto (WIFI-010)
              |
              v
[3] Clonazione (mifare-cloning/)
     +-- tag magic + nfc-mfclassic W -> clone con UID (WIFI-011)
     +-- oppure Proxmark3 -> emulazione senza tag fisico
              |
              v
[OUTPUT] Badge clone/emulato -> accesso fisico non autorizzato
     -> collegamento con 05-social-engineering (prossimita) e 07-post-exploitation (rete interna)
```

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Proxmark3 RDV4` | rfid multi-tool | hardware | lf+hf: lettura, clonazione, sniffing, emulazione (riferimento pro) |
| `libnfc` (nfc-list) | nfc library | cli | identificazione e lettura tag hf |
| `mfoc` / `mfcuk` | mifare cracker | cli | recupero chiavi mifare classic (nested/darkside) |
| `nfc-mfclassic` | mifare writer | cli | dump e scrittura del clone su tag magic |
| `Mifare Classic Tool` | nfc app | android | lettura/clonazione da smartphone |
| `Flipper Zero` | portable multi-tool | hardware | lf/hf lettura, emulazione, clonazione tascabile |
| tag magic / T5577 | hardware | - | tag scrivibili per cloni hf (magic) e lf (T5577) |

> **Tool moderno consigliato:** il `Proxmark3 RDV4` (firmware Iceman) per la copertura RFID completa e il `Flipper Zero` per gli scenari comuni sul campo. Per il solo MIFARE Classic in laboratorio, l'`ACR122U` con libnfc e sufficiente ed economico.

---

## Registro finding - sezione RFID/NFC

| id | descrizione | severity | sottocartella |
| :--- | :--- | :---: | :--- |
| `WIFI-010` | recupero chiavi e dump di un badge mifare classic con chiavi di default (attacco nested mfoc) | `Medio` | `nfc-tools/` |
| `WIFI-011` | clonazione completa del badge mifare su tag magic, incluso l'uid - clone funzionante | `Alto` | `mifare-cloning/` |
| `WIFI-012` | lettura e clonazione di badge Low frequency em4100 (nessuna autenticazione) via proxmark3 | `Alto` | `proxmark3-client/` |

---

## Mappatura MITRE ATT&CK - aggregata

| tattica | tecnica | id mitre | finding correlato |
| :--- | :--- | :--- | :--- |
| reconnaissance | gather victim host information | `T1592` | WIFI-010, WIFI-012 |
| credential access | brute force | `T1110` | WIFI-010 |
| credential access | network sniffing | `T1040` | WIFI-012 |
| credential access | steal application access token | `T1528` | WIFI-010 |
| resource development | develop capabilities | `T1587` | WIFI-011 |
| defense evasion | impersonation | `T1656` | WIFI-011, WIFI-012 |
| initial access | hardware additions | `T1200` | WIFI-010, WIFI-011, WIFI-012 |
| initial access | valid accounts: local accounts | `T1078.003` | WIFI-011, WIFI-012 |

---

> **Nota:** Tutte le attivita documentate in questa sezione sono state condotte su tag e badge RFID/NFC di laboratorio di proprieta dell'autore. Nessun badge di terzi e stato letto, clonato o utilizzato. La clonazione e l'uso non autorizzato di badge di accesso costituisce reato grave (accesso abusivo, furto d'identita, sostituzione di persona). Le tecniche sono documentate a scopo educativo e di security assessment fisico autorizzato.
