> [English](README.en.md) | **Italiano**

# 03 - Deception (Le Trappole)

> - **Fase:** Defense & Hardening - Deception & Early Warning
> - **Categoria:** Deception - trappole ad alta confidenza e threat intelligence
> - **Prerequisiti:** Ambiente in cui posizionare esche (share, documenti, credenziali); per gli honeypot, VM isolata dedicata; canale di notifica
> - **Output:** Finding DEF-005..006; tripwire ad altissima confidenza; raccolta di TTP e IOC reali

---

## Introduzione

La deception e "le trappole": una filosofia difensiva che non protegge e non blocca, ma avvisa. Il principio e disseminare l'ambiente di esche - file, credenziali, servizi, interi sistemi - che non hanno alcuna funzione legittima e la cui unica ragione di esistere e essere toccate da un attaccante. Poiche nessun utente autorizzato ha motivo di interagire con un'esca, ogni attivazione e un segnale ad altissima confidenza.

Questo capovolge l'economia della detection. Le regole SIEM (`../01-siem-log-analysis/`) devono distinguere il malevolo dal legittimo in un mare di attivita normale, con inevitabili falsi positivi. La deception non ha questo problema: l'attivita normale su un'esca e zero, quindi qualsiasi attivita e anomala per definizione. Un singolo alert di deception vale, per confidenza, molti alert correlati.

La deception introduce anche un'asimmetria a favore del difensore. Normalmente l'attaccante deve avere ragione una volta sola, il difensore sempre. La deception inverte: l'attaccante deve evitare ogni esca (senza sapere quali file sono reali e quali trappole), il difensore deve indovinarne una sola che l'attaccante tocchera. In piu, inietta il dubbio - un attaccante consapevole delle esche deve muoversi con cautela, rallentando.

La sezione copre due livelli di deception:

1. **Canary Tokens (DEF-005):** tripwire digitali passivi - un documento, una credenziale, un URL esca che allerta all'uso. Massima semplicita, copertura puntuale, falsi positivi strutturalmente nulli.

2. **T-Pot / Honeypot (DEF-006):** un'intera infrastruttura esca ad alta interazione, che non solo rileva ma studia gli attaccanti, raccogliendo TTP e IOC reali (threat intelligence).

Sono particolarmente efficaci contro la post-exploitation (`07-post-exploitation`): l'attaccante che enumera share, cerca credenziali e apre documenti "interessanti" trova esattamente le esche predisposte per lui.

---

## Struttura della cartella

```
03-deception (Le Trappole)/
+-- README.md          # questo file: registro DEF-005..006, filosofia della deception
|
+-- honeypots/         # esche e trappole
    +-- README.md          # concetto di honeypot e tassonomia
    +-- canary-tokens/     # DEF-005: tripwire digitali passivi
    +-- t-pot/             # DEF-006: piattaforma honeypot multi-servizio
```

---

## Flusso operativo consigliato

```
[INPUT] Ambiente da proteggere / studiare
         |
         v
[1] Scelta del tipo di deception
     +-- early warning puntuale, semplice -> canary-tokens/ (DEF-005)
     +-- threat intelligence, studio TTP --> t-pot/ (DEF-006, VM isolata)
              |
              v
[2] Posizionamento strategico
     +-- esche dove l'attaccante guarda, non dove l'utente legittimo va
              |
              v
[3] Attivazione (attaccante abbocca)
     +-- alert immediato ad alta confidenza
              |
              v
[4] Risposta e intelligence
     +-- token -> incidente, risposta immediata (attaccante gia dentro)
     +-- honeypot -> IOC/TTP -> blocklist e regole nel SIEM (01)
              |
              v
[OUTPUT] Breach rilevato precocemente + intelligence per rafforzare le difese reali
```

---

## Tool di riferimento

| Tool | Tipo | Ruolo | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Canarytokens` (Thinkst) | Token generator | Servizio/self-hosted | Tripwire digitali (doc, URL, AWS, DNS) |
| `T-Pot` (Telekom) | Honeypot platform | Piattaforma | Honeypot multi-servizio + threat intel |
| `OpenCanary` | Honeypot daemon | Open source | Servizi esca leggeri self-hosted |
| `Cowrie` | SSH/Telnet honeypot | Container | Cattura sessioni d'attacco SSH |
| `Honeytokens` (AD) | Deception account | Tecnica | Account fittizi in Active Directory |

> **Tool moderno consigliato:** `canarytokens.org` per iniziare senza infrastruttura; `OpenCanary` o honeytoken AD per deployment interni mirati (detection di movimento laterale); `T-Pot` per la ricerca e la raccolta di threat intelligence su VM isolata.

---

## Registro Finding - Sezione Deception

| ID | Descrizione | Severity | Sottocartella |
| :--- | :--- | :---: | :--- |
| `DEF-005` | Canary Tokens: tripwire digitali per early breach detection (falsi positivi nulli) | `Medio` | `honeypots/canary-tokens/` |
| `DEF-006` | T-Pot: piattaforma honeypot multi-servizio, raccolta TTP/IOC reali | `Medio` | `honeypots/t-pot/` |

---

## Mappatura MITRE ATT&CK - Aggregata

> Tecniche d'attacco **rilevate/osservate** dalle esche della sezione.

| Tattica (rilevata) | Tecnica | ID MITRE | Finding Correlato |
| :--- | :--- | :--- | :--- |
| Collection | Data from Network Shared Drive | `T1039` | DEF-005 |
| Credential Access | Unsecured Credentials: Credentials In Files | `T1552.001` | DEF-005 |
| Credential Access | Brute Force | `T1110` | DEF-006 |
| Command and Control | Ingress Tool Transfer | `T1105` | DEF-006 |
| Discovery | File and Directory Discovery | `T1083` | DEF-005 |

---

> **Nota:** La deception e uno strumento puramente difensivo. I canary token rilevano l'accesso a risorse esca controllate dall'autore; gli honeypot vanno deployati esclusivamente su reti isolate di proprieta, mai in produzione. I sample di malware catturati vanno gestiti in ambiente sandboxato. Le tecniche sono documentate a scopo educativo e di difesa in contesto autorizzato.
