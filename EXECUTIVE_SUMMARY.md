> [English](EXECUTIVE_SUMMARY.en.md) | **Italiano**

# Penetration test - executive summary

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

## 1. Contesto e scope dell'Engagement

### Obiettivo

La presente attivita di Penetration Test e stata commissionata con l'obiettivo di valutare
in modo indipendente e oggettivo la postura di sicurezza dell'infrastruttura IT interna,
delle applicazioni web esposte e dei sistemi server aziendali. L'incarico simula le
capacita e le tattiche di un attaccante esterno reale che tenta di penetrare nella rete
aziendale senza privilegi preassegnati.

### Scope

| componente | target | note |
| :--- | :--- | :--- |
| infrastruttura di rete | segmento lan `10.0.2.0/24` e `192.168.0.0/24` | host discovery, port scan, servizi esposti |
| sistema operativo server | windows 10 pro (`10.0.2.3` / `192.168.0.109`) | vulnerabilita os, servizi smb, rdp |
| sistema operativo server | ubuntu linux (`192.168.0.x`) | configurazioni insicure, privesc |
| applicazioni web | stack lamp/xampp, cms drupal, api graphql | owasp top 10, api security |
| fonti osint | profili pubblici, dns, motori di ricerca | passive reconnaissance |

### Periodo di esecuzione

| fase | descrizione | durata stimata |
| :--- | :--- | :--- |
| ricognizione passiva | osint, dns, shodan | 2 giorni |
| ricognizione attiva | network scan, service enumeration | 1 giorno |
| vulnerability assessment | scan credentialed, audit protocolli | 3 giorni |
| web application testing | owasp top 10, api, cms | 5 giorni |
| system exploitation | initial access, privilege escalation | 4 giorni |
| reporting | analisi, documentazione, raccomandazioni | 3 giorni |

### Metodologia

Il test e stato condotto seguendo le linee guida internazionali **PTES** (Penetration
Testing Execution Standard) e **OWASP Testing Guide v4**, con mappatura sistematica delle
tecniche documentate nel framework **MITRE ATT&CK**. Nessuna attivita e stata condotta
al di fuori dello scope concordato. Tutti i sistemi testati sono ambienti di laboratorio
autorizzati.

---

## 2. Metodologia - fasi dell'Engagement

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

## 3. Quadro complessivo dei rischi

### Distribuzione finding per severity

| severity | conteggio | % sul totale | impatto potenziale |
| :--- | :---: | :---: | :--- |
| **Critico** | 15 | 25% | compromissione totale, perdita dati, rce |
| **Alto** | 23 | 38% | accesso non autorizzato, escalation privilegi |
| **Medio** | 11 | 18% | information disclosure, configurazioni deboli |
| **Basso** | 3 | 5% | rischi a bassa probabilita di sfruttamento |
| **Informativo** | 8 | 14% | osservazioni senza impatto diretto immediato |
| **totale** | **60** | 100% | |

> **Lettura sintetica per il management:** Il 63% dei finding rilevati (38 su 60) e
> classificato come Critico o Alto. Questo significa che oltre meta delle vulnerabilita
> identificate e direttamente sfruttabile da un attaccante con competenze medie per
> ottenere accesso non autorizzato, esfiltrare dati o compromettere l'infrastruttura.

### Business impact per categoria

| area | finding | impatto business |
| :--- | :--- | :--- |
| infrastruttura di rete | SCAN-003, VULN-001..004 | intercettazione traffico interno, accesso a share file aziendali |
| applicazioni web | WEB-001..015 | furto dati utenti, bypass autenticazione, controllo del server |
| sistemi operativi | EXPLOIT-001..019 | controllo totale dei server, persistenza, lateral movement |
| esposizione osint | OSINT-001..004 | dati dipendenti e credenziali gia circola in database di breach |
| configurazioni insicure | EXPLOIT-016, EXPLOIT-017 | password di sistema in chiaro, binari modificabili |

---

## 4. Top 5 finding critici

I cinque finding seguenti sono stati selezionati tra i 15 critici rilevati in base alla
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

## 5. Raccomandazioni strategiche

Le raccomandazioni sono organizzate per orizzonte temporale e prioritizzate in base
al rapporto tra urgenza del rischio e sforzo di implementazione.

### Priorita urgente - entro 30 giorni

| priorita | azione | finding correlati | sforzo |
| :---: | :--- | :--- | :--- |
| 1 | applicare tutte le patch di sicurezza windows arretrate (in particolare ms17-010) | VULN-002, EXPLOIT-001 | Basso (operativo) |
| 2 | eliminare i file unattend.xml e cambiare le credenziali administrator | EXPLOIT-016 | Basso (<1 ora) |
| 3 | correggere le sql injection nell'applicazione web (prepared statements) | WEB-004, WEB-011 | Medio (3-5 gg) |
| 4 | sostituire il segreto jwt con un valore crittograficamente sicuro | WEB-012 | Basso (<2 ore) |
| 5 | implementare autorizzazione object-level nelle api (anti-idor) | WEB-014 | Medio (3-7 gg) |
| 6 | abilitare smb signing obbligatorio via group policy | SCAN-003, VULN-001 | Basso (gpo) |

### Breve termine - entro 90 giorni

| priorita | azione | finding correlati | sforzo |
| :---: | :--- | :--- | :--- |
| 7 | implementare policy password complessa (min. 14 caratteri) e mfa su tutti i sistemi privilegiati | EXPLOIT-016..019 | Medio |
| 8 | rimuovere o disabilitare il protocollo smbv1 | VULN-002 | Basso |
| 9 | correggere i permessi acl sui binari di servizio (xampp e analoghi) | EXPLOIT-017 | Basso |
| 10 | sanitizzare tutti i template engine server-side (anti-ssti) | WEB-008 | Medio |
| 11 | correggere la logica di controllo accesso nei moduli cms drupal (aggiornamento versione) | WEB-015 | Basso |
| 12 | disabilitare graphql introspection in produzione; validare tutti i parametri | WEB-013 | Basso |

### Medio termine - entro 180 giorni

| priorita | azione | note |
| :---: | :--- | :--- |
| 13 | deploying un web application firewall (waf) davanti all'applicazione web | riduce superficie di attacco per attacchi automatizzati |
| 14 | avviare un programma strutturato di vulnerability management (scan mensili automatizzati) | previene il riacumulo di debito tecnico di sicurezza |
| 15 | segmentazione della rete interna (vlan) per isolare i sistemi critici | limita il lateral movement in caso di compromissione |
| 16 | formazione sviluppatori su secure coding (owasp top 10) | riduce i finding web alla radice |

### Lungo termine - piano strategico

| iniziativa | descrizione |
| :--- | :--- |
| **secure development lifecycle (sdl)** | integrare security review nel processo di sviluppo: code review, sast/dast in ci/cd, threat modeling prima dello sviluppo di nuove feature |
| **penetration test annuale** | ripetere un'attivita di test equivalente ogni anno o dopo cambiamenti architetturali significativi, per misurare i progressi e rilevare nuovi rischi |
| **incident response plan** | definire procedure formali di risposta agli incidenti: chi chiama chi, quali sistemi isolare, come preservare le evidenze per analisi forensi |
| **asset inventory e patch management** | mantenere un registro aggiornato di tutti i sistemi, con versioni software e stato delle patch; automatizzare gli aggiornamenti ove possibile |

---

## 6. Conclusione

### Postura attuale

L'engagement ha rilevato **60 vulnerabilita in 18 giorni di test**, di cui il 63%
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

| indicatore | valore attuale | target a 6 mesi |
| :--- | :--- | :--- |
| finding critici aperti | 15 | 0 |
| finding alti aperti | 23 | < 5 |
| tempo a compromissione totale | < 3 minuti | > 30 giorni (obiettivo realistico) |
| sistemi con patch arretrate | tutti i sistemi testati | 0 sistemi critici non patchati |
| sistemi con mfa abilitato | 0% | 100% su accessi privilegiati |

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
