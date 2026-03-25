# Penetration Test - Executive Summary

---

```
DOCUMENTO RISERVATO - CONFIDENZIALE

Classificazione:  Riservato - Uso Interno
Versione:         1.0
Data emissione:   Marzo 2026
Autore:           Nicholas Arcari - Security Analyst
Destinatari:      Management, CTO, CISO
```

---

## 1. Contesto e Scope dell'Engagement

### Obiettivo

La presente attivita di Penetration Test e stata commissionata con l'obiettivo di valutare
in modo indipendente e oggettivo la postura di sicurezza dell'infrastruttura IT interna,
delle applicazioni web esposte e dei sistemi server aziendali. L'incarico simula le
capacita e le tattiche di un attaccante esterno reale che tenta di penetrare nella rete
aziendale senza privilegi preassegnati.

### Scope

| Componente | Target | Note |
| :--- | :--- | :--- |
| Infrastruttura di rete | Segmento LAN `10.0.2.0/24` e `192.168.0.0/24` | Host discovery, port scan, servizi esposti |
| Sistema operativo server | Windows 10 Pro (`10.0.2.3` / `192.168.0.109`) | Vulnerabilita OS, servizi SMB, RDP |
| Sistema operativo server | Ubuntu Linux (`192.168.0.x`) | Configurazioni insicure, PrivEsc |
| Applicazioni web | Stack LAMP/XAMPP, CMS Drupal, API GraphQL | OWASP Top 10, API security |
| Fonti OSINT | Profili pubblici, DNS, motori di ricerca | Passive reconnaissance |

### Periodo di esecuzione

| Fase | Descrizione | Durata stimata |
| :--- | :--- | :--- |
| Ricognizione passiva | OSINT, DNS, Shodan | 2 giorni |
| Ricognizione attiva | Network scan, service enumeration | 1 giorno |
| Vulnerability Assessment | Scan credentialed, audit protocolli | 3 giorni |
| Web Application Testing | OWASP Top 10, API, CMS | 5 giorni |
| System Exploitation | Initial access, privilege escalation | 4 giorni |
| Reporting | Analisi, documentazione, raccomandazioni | 3 giorni |

### Metodologia

Il test e stato condotto seguendo le linee guida internazionali **PTES** (Penetration
Testing Execution Standard) e **OWASP Testing Guide v4**, con mappatura sistematica delle
tecniche documentate nel framework **MITRE ATT&CK**. Nessuna attivita e stata condotta
al di fuori dello scope concordato. Tutti i sistemi testati sono ambienti di laboratorio
autorizzati.

---

## 2. Metodologia - Fasi dell'Engagement

```
[RECON PASSIVA]          [RECON ATTIVA]          [ASSESSMENT]
OSINT · DNS · Shodan --> Nmap · Masscan -------> Nessus · audit SMB/SNMP/SMTP
        |                      |                        |
        v                      v                        v
[WEB TESTING]           [EXPLOITATION]          [POST-EXPLOIT]
OWASP Top 10 ----------> Initial Access -------> PrivEsc · Lateral Movement
SQL Injection            EternalBlue              WinPEAS · LinPEAS
XSS · SSTI · JWT         Empire · MSF             Credential Harvesting
GraphQL · IDOR           Payload custom            Pass-the-Hash
```

Ogni fase alimenta la successiva: le informazioni raccolte in ricognizione hanno guidato
la scelta dei vettori di attacco, i risultati del vulnerability assessment hanno
identificato le vulnerabilita da sfruttare, l'exploitation ha prodotto accesso iniziale
che ha permesso l'escalation dei privilegi.

---

## 3. Quadro Complessivo dei Rischi

### Distribuzione finding per severity

| Severity | Conteggio | % sul totale | Impatto Potenziale |
| :--- | :---: | :---: | :--- |
| **Critico** | 13 | 24% | Compromissione totale, perdita dati, RCE |
| **Alto** | 20 | 37% | Accesso non autorizzato, escalation privilegi |
| **Medio** | 10 | 18% | Information disclosure, configurazioni deboli |
| **Basso** | 3 | 6% | Rischi a bassa probabilita di sfruttamento |
| **Informativo** | 8 | 15% | Osservazioni senza impatto diretto immediato |
| **Totale** | **54** | 100% | |

> **Lettura sintetica per il management:** Il 61% dei finding rilevati (33 su 54) e
> classificato come Critico o Alto. Questo significa che oltre meta delle vulnerabilita
> identificate e direttamente sfruttabile da un attaccante con competenze medie per
> ottenere accesso non autorizzato, esfiltrare dati o compromettere l'infrastruttura.

### Business Impact per categoria

| Area | Finding | Impatto Business |
| :--- | :--- | :--- |
| Infrastruttura di rete | SCAN-003, VULN-001..004 | Intercettazione traffico interno, accesso a share file aziendali |
| Applicazioni web | WEB-001..015 | Furto dati utenti, bypass autenticazione, controllo del server |
| Sistemi operativi | EXPLOIT-001..019 | Controllo totale dei server, persistenza, lateral movement |
| Esposizione OSINT | OSINT-001..004 | Dati dipendenti e credenziali gia circola in database di breach |
| Configurazioni insicure | EXPLOIT-016, EXPLOIT-017 | Password di sistema in chiaro, binari modificabili |

---

## 4. Top 5 Finding Critici

I cinque finding seguenti sono stati selezionati tra i 13 critici rilevati in base alla
combinazione di facilita di sfruttamento, impatto sull'organizzazione e copertura
della superficie di attacco. Ogni sezione e scritta in linguaggio accessibile al management.

---

### 4.1 - Compromissione totale del server Windows via vulnerabilita nota da 9 anni

**Finding:** VULN-002 + EXPLOIT-001 | **Severity:** Critico

Il server Windows in produzione non e stato aggiornato con una patch di sicurezza
(MS17-010) rilasciata da Microsoft nel **maggio 2017**, nove anni fa. Questa vulnerabilita,
nota al pubblico con il nome "EternalBlue", e la stessa utilizzata nell'attacco globale
WannaCry che nel 2017 paralizza ospedali, banche e aziende in 150 paesi.

Durante il test, sfruttando questa vulnerabilita con strumenti pubblicamente disponibili
e gratuiti, e stato possibile ottenere il **controllo completo del server** (livello
`SYSTEM`, equivalente a un accesso da amministratore con pieni privilegi) in meno di
3 minuti, senza nessuna credenziale e senza interazione da parte di nessun utente.

**Cosa puo fare un attaccante:** leggere e modificare qualsiasi file sul server,
installare software, crittografare i dati per richiedere un riscatto (ransomware),
usare il server come base per attaccare altri sistemi nella rete interna.

**Azione richiesta:** installare immediatamente le patch di sicurezza Windows o isolare
il sistema dalla rete. Stima di risoluzione: meno di 1 ora di lavoro tecnico.

---

### 4.2 - Database aziendale accessibile tramite vulnerabilita nell'applicazione web

**Finding:** WEB-004 + WEB-011 | **Severity:** Critico

L'applicazione web non valida correttamente i dati inseriti dagli utenti nei campi di
ricerca e di login. Attraverso una tecnica chiamata "SQL Injection", e stato possibile:

- Accedere all'applicazione come qualsiasi utente, compreso l'amministratore, **senza
  conoscere la password**
- Estrarre il contenuto completo del database, incluse **tabelle con dati utenti,
  credenziali, informazioni personali e transazioni**

Questa classe di vulnerabilita e classificata da OWASP come la prima causa di violazione
dei dati nelle applicazioni web da oltre 15 anni. Il suo sfruttamento e parzialmente
automatizzabile e non richiede competenze avanzate.

**Impatto normativo:** in presenza di dati personali (nomi, email, IBAN, storico
acquisti), questa vulnerabilita costituisce una violazione del GDPR e impone, in caso
di sfruttamento da parte di terzi, la notifica all'Autorita Garante entro 72 ore.

**Azione richiesta:** rivedere tutta la logica di accesso al database nell'applicazione.
Soluzione tecnica: uso di "prepared statements" in sostituzione delle query dinamiche.
Stima di risoluzione: 3-5 giorni di sviluppo.

---

### 4.3 - Password dell'amministratore di sistema trovata in un file non protetto

**Finding:** EXPLOIT-016 | **Severity:** Critico

Durante l'analisi del file system del server Windows compromesso, e stato individuato
un file di configurazione (`Unattend.xml`) lasciato sul server dopo un'installazione
automatizzata del sistema operativo. Questo file conteneva, in chiaro e senza alcuna
cifratura, la **password dell'account Administrator** del sistema.

In termini pratici: chiunque abbia accesso al file system del server - incluso un
attaccante che ha ottenuto un accesso iniziale con i privilegi piu bassi - puo leggere
questa password e usarla immediatamente per prendere il controllo completo del server
e potenzialmente di altri sistemi che condividono la stessa credenziale.

**Azione richiesta:** eliminare immediatamente il file `C:\Windows\Panther\Unattend.xml`
e tutti i file analoghi. Cambiare la password Administrator con una sicura (minimo 16
caratteri). Verificare se la stessa password e usata su altri sistemi (riutilizzo delle
credenziali). Stima di risoluzione: meno di 1 ora.

---

### 4.4 - Accesso completo all'applicazione come amministratore senza conoscere la password

**Finding:** WEB-012 | **Severity:** Critico

L'applicazione utilizza i token JWT (JSON Web Token) per verificare l'identita degli
utenti dopo il login. Il meccanismo e corretto in teoria, ma il segreto usato per firmare
i token e stato impostato con un valore banale e presente nelle liste di password comuni
("secret", "password123" e simili).

Questo ha permesso, in pochi secondi con strumenti gratuiti, di **falsificare un token
di identita con ruolo "admin"** e accedere a tutte le funzionalita amministrative
dell'applicazione senza mai effettuare un login reale.

**Cosa puo fare un attaccante:** accedere ai dati di tutti gli utenti registrati,
modificare configurazioni, eliminare contenuti, eseguire operazioni privilegiate come
se fosse l'amministratore legittimo del sistema.

**Azione richiesta:** generare un segreto JWT con un generatore crittografico sicuro
(minimo 256 bit di entropia). Invalidare tutti i token attivi dopo la sostituzione.
Stima di risoluzione: meno di 2 ore di sviluppo.

---

### 4.5 - Un utente normale puo vedere i dati finanziari di qualsiasi altro utente

**Finding:** WEB-014 | **Severity:** Critico

L'API dell'applicazione non verifica che l'utente che richiede un dato sia
effettivamente il proprietario di quel dato. Modificando un parametro nell'URL della
richiesta (es. cambiando `/api/account/123` in `/api/account/124`), un utente
regolarmente autenticato riesce ad accedere ai dati di un altro utente.

Questa vulnerabilita, classificata da OWASP come "BOLA/IDOR" ed e considerata la piu
diffusa nelle API moderne, ha permesso durante il test di enumerare i profili di tutti
gli utenti registrati e accedere ai loro dati finanziari (saldo, movimenti, metodi
di pagamento).

**Impatto normativo:** accesso non autorizzato a dati finanziari di terzi configura
una violazione del GDPR (dati personali), potenzialmente del PCI-DSS (dati di pagamento)
e costituisce un illecito ai sensi dell'art. 615-ter del Codice Penale italiano
(accesso abusivo a sistema informatico).

**Azione richiesta:** implementare controlli di autorizzazione server-side su ogni
endpoint API che restituisce dati utente, verificando che l'identita del richiedente
corrisponda al proprietario della risorsa. Stima di risoluzione: 3-7 giorni di sviluppo.

---

## 5. Raccomandazioni Strategiche

Le raccomandazioni sono organizzate per orizzonte temporale e prioritizzate in base
al rapporto tra urgenza del rischio e sforzo di implementazione.

### Priorita Urgente - entro 30 giorni

| Priorita | Azione | Finding correlati | Sforzo |
| :---: | :--- | :--- | :--- |
| 1 | Applicare tutte le patch di sicurezza Windows arretrate (in particolare MS17-010) | VULN-002, EXPLOIT-001 | Basso (operativo) |
| 2 | Eliminare i file Unattend.xml e cambiare le credenziali Administrator | EXPLOIT-016 | Basso (<1 ora) |
| 3 | Correggere le SQL Injection nell'applicazione web (prepared statements) | WEB-004, WEB-011 | Medio (3-5 gg) |
| 4 | Sostituire il segreto JWT con un valore crittograficamente sicuro | WEB-012 | Basso (<2 ore) |
| 5 | Implementare autorizzazione object-level nelle API (anti-IDOR) | WEB-014 | Medio (3-7 gg) |
| 6 | Abilitare SMB Signing obbligatorio via Group Policy | SCAN-003, VULN-001 | Basso (GPO) |

### Breve Termine - entro 90 giorni

| Priorita | Azione | Finding correlati | Sforzo |
| :---: | :--- | :--- | :--- |
| 7 | Implementare policy password complessa (min. 14 caratteri) e MFA su tutti i sistemi privilegiati | EXPLOIT-016..019 | Medio |
| 8 | Rimuovere o disabilitare il protocollo SMBv1 | VULN-002 | Basso |
| 9 | Correggere i permessi ACL sui binari di servizio (XAMPP e analoghi) | EXPLOIT-017 | Basso |
| 10 | Sanitizzare tutti i template engine server-side (anti-SSTI) | WEB-008 | Medio |
| 11 | Correggere la logica di controllo accesso nei moduli CMS Drupal (aggiornamento versione) | WEB-015 | Basso |
| 12 | Disabilitare GraphQL Introspection in produzione; validare tutti i parametri | WEB-013 | Basso |

### Medio Termine - entro 180 giorni

| Priorita | Azione | Note |
| :---: | :--- | :--- |
| 13 | Deploying un Web Application Firewall (WAF) davanti all'applicazione web | Riduce superficie di attacco per attacchi automatizzati |
| 14 | Avviare un programma strutturato di Vulnerability Management (scan mensili automatizzati) | Previene il riacumulo di debito tecnico di sicurezza |
| 15 | Segmentazione della rete interna (VLAN) per isolare i sistemi critici | Limita il lateral movement in caso di compromissione |
| 16 | Formazione sviluppatori su secure coding (OWASP Top 10) | Riduce i finding web alla radice |

### Lungo Termine - piano strategico

| Iniziativa | Descrizione |
| :--- | :--- |
| **Secure Development Lifecycle (SDL)** | Integrare security review nel processo di sviluppo: code review, SAST/DAST in CI/CD, threat modeling prima dello sviluppo di nuove feature |
| **Penetration Test annuale** | Ripetere un'attivita di test equivalente ogni anno o dopo cambiamenti architetturali significativi, per misurare i progressi e rilevare nuovi rischi |
| **Incident Response Plan** | Definire procedure formali di risposta agli incidenti: chi chiama chi, quali sistemi isolare, come preservare le evidenze per analisi forensi |
| **Asset Inventory e Patch Management** | Mantenere un registro aggiornato di tutti i sistemi, con versioni software e stato delle patch; automatizzare gli aggiornamenti ove possibile |

---

## 6. Conclusione

### Postura attuale

L'engagement ha rilevato **54 vulnerabilita in 18 giorni di test**, di cui il 61%
di severita Critica o Alta. La compromissione totale del server Windows e stata
ottenuta in meno di **3 minuti dall'inizio della fase di exploitation**, senza
credenziali preassegnate e sfruttando una vulnerabilita pubblica da 9 anni.

Le criticita piu rilevanti non richiedono tecniche avanzate: la maggior parte dei
finding Critici e sfruttabile con strumenti pubblici e gratuiti da chiunque abbia
competenze tecniche di base. Questo abbassa significativamente la soglia di rischio.

### Postura target

Il percorso di rientro e definito e realistico. Le misure di breve termine (patch,
rimozione file sensibili, correzione SQL Injection, segreti crittografici) possono
ridurre la superficie di attacco critica del **70% in meno di 30 giorni** con
interventi prevalentemente tecnici e a basso costo.

Il raggiungimento di una postura di sicurezza matura richiede un piano a 12-18 mesi
che combini interventi tecnici immediati, revisione del processo di sviluppo software
e istituzione di pratiche di sicurezza continue (patch management, vulnerability
scanning, penetration test periodici).

### Metriche di riferimento

| Indicatore | Valore attuale | Target a 6 mesi |
| :--- | :--- | :--- |
| Finding Critici aperti | 13 | 0 |
| Finding Alti aperti | 20 | < 5 |
| Tempo a compromissione totale | < 3 minuti | > 30 giorni (obiettivo realistico) |
| Sistemi con patch arretrate | Tutti i sistemi testati | 0 sistemi critici non patchati |
| Sistemi con MFA abilitato | 0% | 100% su accessi privilegiati |

---

> **Metodologia di riferimento:** PTES (Penetration Testing Execution Standard),
> OWASP Testing Guide v4.2, MITRE ATT&CK Framework v14.
>
> **Documentazione tecnica completa:** la presente Executive Summary e il documento
> di sintesi destinato al management. La documentazione tecnica integrale, comprensiva
> di output degli strumenti, proof-of-concept, finding ID dettagliati e remediation
> specifiche, e disponibile nei moduli del repository `cybersecurity-labs/`.
>
> **Disclaimer:** tutte le attivita documentate sono state condotte esclusivamente
> su infrastruttura di laboratorio autorizzata. Nessuna tecnica e stata applicata a
> sistemi di produzione reali o di terze parti senza autorizzazione esplicita.
