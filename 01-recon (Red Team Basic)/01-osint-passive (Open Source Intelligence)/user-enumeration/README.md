> [English](README.en.md) | **Italiano**

# OSINT Passive: User Enumeration & Identity Correlation

> - **Fase:** Reconnaissance - Passive Information Gathering
> - **Visibilita:** Zero - il tool invia richieste HTTP a piattaforme pubbliche, non al target direttamente
> - **Prerequisiti:** Username target noto, Sherlock installato (pip o apt), Python 3
> - **Output:** OSINT-004 - Mappa della presenza digitale del target su piattaforme social e tecniche, utile per profilazione e Social Engineering

---

Obiettivo: Effettuare la correlazione dell'identità digitale (Identity Correlation) partendo da un singolo username noto per mappare la presenza del target su piattaforme diverse.

Strumenti: `Sherlock`

---

## 1 Introduzione Teorica

La User Enumeration passiva sfrutta la tendenza degli utenti a riutilizzare lo stesso handle (nome utente) su molteplici servizi.
Attraverso strumenti automatizzati, è possibile interrogare centinaia di piattaforme social, forum e servizi tecnici per verificare l'esistenza di un profilo.

Utilità per il Red Team:
- Profilazione Psicologica: Capire interessi e hobby per attacchi di Ingegneria Sociale.
- Estensione della Superficie: Trovare account meno protetti (es. un vecchio forum) che potrebbero contenere leak di password o informazioni personali.

---

## 2 Esecuzione Tecnica

**ID Finding:** `OSINT-004` | **Severity:** `Basso`

### Ricerca con Sherlock
È stato utilizzato lo strumento `Sherlock` per scansionare oltre 300 siti web alla ricerca dell'username target.

```Bash
sudo apt update
sudo apt install sherlock
sherlock <USERNAME>
```

![](./img/Screenshot_2026-02-03_17_12_56.jpg)

---

## 3 Analisi dei Falsi Positivi

Durante l'analisi è fondamentale verificare manualmente i link.

Falsi Positivi: In alcuni casi (es. forum-sconosciuto.com), l'username esiste ma appartiene a un'altra persona (omonimia digitale).

Verifica: È stato controllato manualmente il profilo GitHub e Reddit per confermare che l'immagine del profilo o la bio coincidessero, validando l'attribuzione al target.

---

## 5 Conclusioni

L'impronta digitale del target e stata valutata in base al numero di piattaforme con profilo confermato. L'uso consistente dello stesso username permette a un attore malevolo di collegare facilmente la vita professionale (GitHub) con quella personale o ludica, aumentando l'efficacia di potenziali attacchi mirati.

---

## Analisi a Basso Livello: Meccanica della User Enumeration e Tecniche di Rilevamento

### Come Sherlock Verifica l'Esistenza di un Profilo

Sherlock non utilizza API ufficiali delle piattaforme. Per ogni sito nel suo database (350+), lo script invia una richiesta HTTP GET all'URL del profilo costruito con il pattern specifico del sito e analizza la risposta:

```
Per ogni sito nel database:
  1. Costruisce URL: https://github.com/{username}
  2. Invia HTTP GET con User-Agent browser
  3. Analizza la risposta:
     - HTTP 200 + content match   -> profilo ESISTE
     - HTTP 404                   -> profilo NON esiste
     - HTTP 200 + "not found"     -> profilo NON esiste (soft 404)
     - HTTP 429 / CAPTCHA         -> rate limited (risultato incerto)
```

Il database di Sherlock (`sherlock/resources/data.json`) definisce per ogni sito il metodo di verifica:

| Metodo | Logica | Affidabilita |
| :--- | :--- | :--- |
| `status_code` | 200 = esiste, 404 = non esiste | Alta (se il sito usa 404 correttamente) |
| `message` | Cerca stringa specifica nella pagina (es. "Page not found") | Media (dipende dal layout del sito) |
| `response_url` | Verifica redirect verso pagina di errore | Bassa (redirect chain complessi) |

### Fonti di Falsi Positivi e Falsi Negativi

La user enumeration su larga scala e intrinsecamente imprecisa. I falsi positivi derivano da tre fonti principali:

1. **Omonimia digitale:** username comuni (`admin`, `test`, `john`) esistono su quasi tutti i siti ma appartengono a persone diverse
2. **Soft 404:** alcuni siti restituiscono HTTP 200 per profili inesistenti con messaggio "utente non trovato" nel body HTML - Sherlock deve parsare il contenuto per distinguerli
3. **Pagine riservate:** certi URL restituiscono 200 perche la pagina esiste come template, ma il profilo effettivo e vuoto o disabilitato

I falsi negativi derivano da:
1. **Rate limiting:** dopo troppe richieste, il sito risponde con 429 o CAPTCHA
2. **Geoblocking:** alcuni siti bloccano richieste da IP non locali (es. VK.com da IP non russi)
3. **Username diverso:** il target potrebbe usare handle diversi su piattaforme diverse

### OPSEC per l'Analista

Sherlock invia 350+ richieste HTTP in rapida successione. Ogni piattaforma vede una richiesta dal medesimo IP. Per evitare di rivelare la propria attivita:

```Bash
# Esecuzione tramite Tor per anonimizzazione
torsocks sherlock <USERNAME>

# Rate limiting manuale (piu lento ma meno rilevabile)
sherlock <USERNAME> --timeout 10
```

---

## Blue Team: Protezione della Digital Footprint Aziendale

**Monitoring:**
- Eseguire periodicamente Sherlock sugli username dei dipendenti chiave (CEO, CISO, admin IT) per mappare la loro esposizione prima che lo faccia un attaccante
- Monitorare menzioni dell'azienda e dei dipendenti su paste site (Pastebin, GitHub Gist) tramite tool come `Maltego` o `SpiderFoot`

**Hardening:**
- Formare i dipendenti sull'uso di username diversi per account personali e professionali
- Implementare policy che vietino l'uso dell'email aziendale per registrazioni su servizi personali
- Richiedere la rimozione di informazioni aziendali sensibili (ruolo, team, tecnologie utilizzate) dai profili social personali dei dipendenti

**Detection:**
- Un attaccante che esegue Sherlock non genera traffico verso l'azienda target (le richieste vanno alle piattaforme terze). L'unico punto di detection e a monte: se l'attaccante usa le informazioni raccolte per Social Engineering, il canale di rilevamento e il programma di Security Awareness (dipendenti che segnalano tentativi di contatto sospetti con riferimenti a informazioni personali)

---

## Esperienza di Laboratorio

L'esecuzione di Sherlock ha prodotto una lista di circa 20-30 match su 350+ siti scansionati. La fase piu critica dell'esercizio non e stata la scansione in se (automatica e rapida), ma la validazione manuale dei risultati. Ogni match richiede una verifica: il profilo GitHub mostrava la stessa immagine e bio del target confermato, mentre un match su un forum sconosciuto si e rivelato un falso positivo (username identico ma persona diversa, confermato dall'assenza di correlazioni nei contenuti pubblicati).

Un aspetto non ovvio emerso dal laboratorio: Sherlock non verifica la corrispondenza tra profili - se il target usa `nick123` su GitHub e `nick_123` su Twitter, il tool non li collega. Per una correlazione completa, e necessario eseguire Sherlock con le varianti note dell'username (underscore, numeri, capitalizzazione) e poi correlare manualmente. Tool come `Maltego` automatizzano questa fase con i "transforms" che collegano entita tra piattaforme diverse.

La scelta di limitare la severity a Basso e stata dettata dal fatto che le informazioni raccolte non sono direttamente sfruttabili per un attacco tecnico - richiedono una fase successiva di Social Engineering o credential reuse per avere impatto. In un engagement reale, il valore dell'user enumeration e proporzionale alla qualita dell'intelligence raccolta: un profilo GitHub con repository aziendali e infinitamente piu utile di un profilo Instagram con foto di vacanze.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Identity Info: Employee Names | `T1589.003` | Correlazione identita digitale tramite Sherlock per mappare la presenza dell'username target su 300+ piattaforme (OSINT-004) |
| Reconnaissance | Search Open Websites/Domains: Social Media | `T1593.001` | Enumerazione account social del target (GitHub, Reddit, forum) per costruire profilo utile al Social Engineering (OSINT-004) |

---

> **Nota:** Le attivita di user enumeration documentate sono state eseguite a scopo di audit personale o su target che hanno fornito autorizzazione esplicita. La tecnica e stata eseguita all'interno di un laboratorio didattico. I risultati non sono stati usati per finalita malevole.