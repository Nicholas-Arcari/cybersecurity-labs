# OSINT Passive: Breach Data Analysis

Obiettivo: Identificare credenziali compromesse (Email/Password) esposte in data breach pubblici per valutare il rischio di Credential Reuse.

Strumenti: h8mail, HaveIBeenPwned (HIBP).

---

## 1 Introduzione Teorica

I Breach Data sono collezioni di informazioni riservate (credenziali, PII) esfiltrate durante attacchi informatici e rese pubbliche.

Per un Red Team, l'analisi di questi dati è fondamentale per il Credential Stuffing: gli utenti tendono a riutilizzare la stessa password su più servizi. Se un attaccante trova una password di un dipendente in un vecchio leak di LinkedIn, potrebbe tentare di usarla per accedere alla VPN aziendale.

Concetti Chiave:

- Combo List: Liste di `email:password` pronte per l'uso in attacchi automatici.
- Hash: La password spesso non è leggibile (es. `5e884898da28...`), ma se è un hash comune (es. MD5) può essere "craccata" (riportata in chiaro).

---

## 2 Attività di Ricerca (Esercizio Pratico)

È stata effettuata una verifica su un target campione per identificare l'esposizione in incidenti di sicurezza noti.

### Scansione con h8mail

Lo strumento `h8mail` interroga servizi di OSINT e Breach Data per trovare corrispondenze.

```Bash
python3 -m venv venv
source venv/bin/activate
pip3 install h8mail
h8mail -t <TARGET_EMAIL>
```

![](./img/Screenshot_2026-02-03_13_03_35.jpg)

```bash
deactivate                  # eseguire quando si è finito
```

### Scansione manuale con HaveIBeenPwned

Per la validazione dei risultati, è stata effettuata una ricerca manuale tramite il portale web ufficiale di HIBP, fonte autorevole per i data breach.

- Accesso al portale: `https://haveibeenpwned.com/`
- Input del target: `<TARGET_EMAIL>`
- Verifica dei risultati.

---

## 3 Approfondimento Tecnico: Digital Footprint vs Breach

1. Differenza Concettuale

|Tipologia|Descrizione|Esempio|Strumenti|
|-------|-------------|---------|--------|
|Digital footprint|Indica che l'utente esiste e opera online. Non implica necessariamente un rischio di sicurezza, ma fornisce informazioni per il Social Engineering|Profilo LinkedIn, Commit su GitHub, Recensioni Amazon|Google Dorks, Sherlock, TheHarvester|
|Brench Data|Indica che i dati dell'utente sono stati RUBATI e resi pubblici illegalmente. Comporta un rischio critico immediato|Password presente in un dump di database (es. LinkedIn 2012 leak)|h8mail, HaveIBeenPwned, Intelligence X|

2. Differenze Metodologiche

La discrepanza tra i risultati ottenuti via web e via riga di comando (CLI) è dovuta al metodo di accesso ai dati:

- Have I Been Pwned (Sito Web): È la fonte originale ("Source of Truth"). Interroga direttamente il database "Master" gestito dai manutentori. È sempre aggiornato e gratuito per la consultazione manuale.
- h8mail (Tool CLI): Funziona come un "connettore" o aggregatore. Non possiede i dati, ma interroga servizi terzi tramite API.
    - Limitazione: Per interrogare il database HIBP tramite script, è necessaria una Chiave API a pagamento.
    - Fallback: In assenza di chiavi, il tool tenta di usare motori gratuiti (es. scylla.so), che possono essere offline o incompleti, portando a falsi negativi.

---

## 4 Analisi Critica: Limiti degli Strumenti Automatizzati

Durante l'attività è stata riscontrata una discrepanza significativa tra i risultati degli strumenti:

1. Tool Automatico (`h8mail`): Ha restituito 0 risultati (Falso Negativo).
    - Causa: Il motore di ricerca gratuito integrato (`scylla.so`) era offline durante il test e non erano configurate le API Key proprietarie.
2. Verifica Manuale (HIBP Web): Ha confermato che l'email è presente in database di breach.

Lezione Appresa:

Gli strumenti di OSINT automatici dipendono dalla disponibilità delle fonti esterne (API). Un risultato "Not Compromised" da un tool da riga di comando non garantisce la sicurezza. È fondamentale eseguire una Cross-Validation manuale sulle fonti autoritarie (Source of Truth) come il portale web di Have I Been Pwned.