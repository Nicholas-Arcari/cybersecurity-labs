> [English](README.en.md) | **Italiano**

# Honeypots - Esche e Trappole Difensive

> - **Fase:** Defense & Hardening - Deception
> - **Categoria:** Deception - dalla singola esca all'infrastruttura trappola
> - **Prerequisiti:** Per i token, un generatore e un posizionamento strategico; per gli honeypot ad alta interazione, VM isolata dedicata
> - **Output:** Base per i finding DEF-005 (canary token) e DEF-006 (T-Pot)

---

## Cos'e un Honeypot

Un honeypot e un sistema, servizio o artefatto progettato per essere attaccato. Non ha scopo produttivo: la sua unica funzione e attirare l'attaccante e rilevarne o studiarne l'attivita. Il principio che accomuna tutte le forme di honeypot e il tasso di falsi positivi strutturalmente nullo: poiche nessun utente legittimo ha motivo di interagire con un'esca, ogni interazione e potenzialmente ostile.

Gli honeypot si classificano per livello di interazione, un asse che determina profondita dell'intelligence contro rischio e costo:

- **Bassa interazione (esca passiva):** un artefatto che registra un singolo evento all'attivazione. Un canary token (`canary-tokens/`) e l'esempio puro: dice "qualcuno ha toccato l'esca", con rischio quasi nullo (non c'e nulla da compromettere) ma profondita minima (solo il fatto dell'attivazione).

- **Alta interazione (sistema esca completo):** un ambiente che l'attaccante puo esplorare e con cui puo interagire a lungo, registrando l'intera sessione. Cowrie in T-Pot (`t-pot/`) ne e l'esempio: registra credenziali provate, comandi eseguiti, malware scaricato. Profondita massima (le TTP complete dell'avversario) ma rischio maggiore (un sistema reale, anche se esca, va isolato con cura).

La scelta dipende dall'obiettivo. Per l'**early warning** - sapere subito che qualcuno e dentro - basta la bassa interazione: semplice, sicura, ad alto segnale. Per la **threat intelligence** - capire chi attacca e come - serve l'alta interazione, con l'isolamento rigoroso che il rischio richiede.

---

## Struttura della cartella

```
honeypots/
+-- README.md          # questo file: concetto e tassonomia degli honeypot
|
+-- canary-tokens/     # DEF-005: bassa interazione, tripwire passivo, early warning
+-- t-pot/             # DEF-006: alta interazione, threat intelligence, VM isolata
```

---

## Confronto per livello di interazione

```
                    Canary Token              T-Pot / Honeypot AI
                    (bassa interazione)       (alta interazione)
                    ----------------------    ----------------------
Rischio             quasi nullo               significativo (isolare!)
Profondita intel    evento singolo            sessione completa (TTP)
Costo/risorse       minimo                    alto (RAM, manutenzione)
Falsi positivi      strutturalmente nulli     strutturalmente nulli
Caso d'uso          early warning             threat intelligence
Posizionamento      ovunque (interno)         DMZ/isolato dedicato
```

---

## Tool di riferimento

| Tool | Interazione | Ruolo | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Canarytokens` | Bassa | Token passivo | Early warning puntuale, falsi positivi nulli |
| `OpenCanary` | Bassa/media | Servizi esca | Honeypot leggero per deployment interni |
| `T-Pot` | Alta | Piattaforma | Threat intelligence multi-servizio |
| `Cowrie` | Alta | SSH/Telnet | Cattura sessioni d'attacco complete |
| `Honeytokens` (AD) | Bassa | Account esca | Detection di attacchi Active Directory |

> **Tool moderno consigliato:** iniziare con la bassa interazione (`canarytokens.org`) per il miglior rapporto valore/rischio; passare all'alta interazione (`T-Pot`) solo con l'isolamento adeguato e uno scopo di intelligence esplicito.

---

> **Nota:** Gli honeypot vanno deployati esclusivamente su reti di proprieta dell'autore. Gli honeypot ad alta interazione catturano malware reale e vanno rigorosamente isolati dalla produzione; i sample vanno gestiti in ambiente sandboxato. Le tecniche sono documentate a scopo educativo e di difesa in contesto autorizzato.
