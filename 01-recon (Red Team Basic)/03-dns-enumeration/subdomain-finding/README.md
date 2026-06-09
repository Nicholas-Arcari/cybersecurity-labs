> [English](README.en.md) | **Italiano**

# Subdomain Discovery

> - **Fase:** Reconnaissance - DNS Enumeration
> - **Visibilita:** Bassa (passivo) - interrogazione di fonti di terze parti (CT logs, motori ricerca) senza contattare i server del target
> - **Prerequisiti:** Dominio target noto, Sublist3r e Assetfinder installati, accesso a Internet
> - **Output:** DNS-003 - 500+ sottodomini di tesla.com inclusi target ad alto valore (vpn, sso, dev-app, toolbox)

---

Obiettivo: Mappatura della superficie di attacco esterna di un'organizzazione Enterprise tramite tecniche di OSINT (Open Source Intelligence), senza interagire direttamente con i sistemi.

Target: `tesla.com` (Public Bug Bounty Program)

Strumenti: `Sublist3r`, `Assetfinder`

---

## 1 Introduzione Teorica

La Passive Subdomain Enumeration consiste nel raccogliere informazioni sui sottodomini di un target interrogando fonti di terze parti (Motori di ricerca, Log di "Certificate Transparency", VirusTotal, ecc.) invece di interrogare direttamente i server DNS dell'azienda.

Perché è importante?

- Stealth: Essendo passiva, non genera traffico diretto verso il bersaglio e non fa scattare allarmi (IDS/IPS).
- Shadow IT: Permette di scoprire vecchi pannelli di amministrazione, ambienti di sviluppo (`dev-app`, `staging`) o servizi dimenticati che spesso presentano vulnerabilità critiche.
- Certificate Transparency: Sfrutta i log pubblici dei certificati SSL per individuare domini creati anche poche ore fa.

---

## 2 Esecuzione Tecnica

**ID Finding:** `DNS-003` | **Severity:** `Medio`

#### A. Aggregazione OSINT (Sublist3r)

È stato utilizzato `Sublist3r` per interrogare molteplici motori di ricerca (Google, Bing, Yahoo, Baidu) e aggregare i risultati storici.

Comando:

```Bash
sublist3r -d tesla.com -o tesla_sublist3r.txt
```

![](./img/Screenshot_2026-02-08_10_38_13.jpg)

Analisi: Il tool ha impiegato diversi minuti per interrogare le API dei motori di ricerca, restituendo una lista di sottodomini "storici" e ben indicizzati.

#### B. Certificate Transparency Analysis (Assetfinder)

È stato utilizzato assetfinder per un'enumerazione rapida basata sui certificati SSL. Questa tecnica è estremamente efficace per trovare infrastrutture interne esposte (VPN, Mail Server) che hanno un certificato valido ma non sono indicizzate su Google.

Comando:

```Bash
assetfinder --subs-only tesla.com > tesla_assetfinder.txt
```

(Nota: L'output è stato troncato con head per leggibilità, dato l'elevato numero di risultati)

Comando:

```Bash
head -n 20 tesla_assetfinder.txt
```

![](./img/Screenshot_2026-02-08_10_37_47.jpg)

Ricerca mirata di sottodomini di sviluppo o amministrazione.

Comando:

```Bash
grep "dev" tesla_assetfinder.txt
grep "admin" tesla_assetfinder.txt
```

![](./img/Screenshot_2026-02-08_10_37_28.jpg)

---

## 3 Analisi dei Risultati (Attack Surface)

Dall'unione dei risultati dei due tool, è stata compilata una lista di oltre 500+ sottodomini unici. Di seguito alcuni esempi di "High Value Targets" identificati che richiederebbero ulteriore investigazione (Active Recon):

| Sottodominio Rilevato | Categoria | Interesse per Bug Bounty |
|-----------------------|-----------|--------------------------|
| toolbox.tesla.com | Internal Tool | Alto (Pannelli strumenti interni) |
| sso.tesla.com | Authentication | Critico (Single Sign-On, target phishing) |
| vpn.tesla.com | Network Access | Alto (Punto di ingresso infrastrutturale) |
| energysupport.tesla.com | Customer Support | Medio (Ticket systems, possibili XSS) |
| dev-app.tesla.com | Development | Alto (Ambienti di test spesso vulnerabili) |

Nota Tecnica: A differenza di un laboratorio controllato, in un target reale come Tesla la quantità di dati richiede post-processing (filtraggio dei domini morti con tool come `httprobe`) prima di procedere con gli attacchi.

---

## 4 Conclusioni

L'utilizzo combinato di `Sublist3r` e `Assetfinder` su un target Enterprise ha dimostrato come la "Security through Obscurity" sia inefficace. Grazie ai log di Certificate Transparency, qualsiasi nuovo servizio esposto su Internet dotato di HTTPS viene immediatamente reso visibile agli attaccanti, permettendo di mappare l'infrastruttura senza inviare un singolo pacchetto verso i server di Tesla.

---

## Analisi a Basso Livello: Certificate Transparency e Fonti di Subdomain Discovery

### Certificate Transparency (CT) Logs

I CT logs (RFC 6962) sono registri pubblici append-only gestiti da operatori indipendenti (Google, Cloudflare, DigiCert). Ogni Certificate Authority (CA) e obbligata a registrare ogni certificato SSL/TLS emesso in almeno due CT log prima che il certificato sia considerato valido dai browser (Chrome richiede SCT - Signed Certificate Timestamp).

```
Flusso di emissione certificato:
Azienda richiede cert per "dev-app.tesla.com"
        |
        v
CA (es. Let's Encrypt) emette il certificato
        |
        v
CA registra il certificato su CT log (es. Google Argon, Cloudflare Nimbus)
        |
        v
CT log restituisce SCT (Signed Certificate Timestamp)
        |
        v
Certificato emesso con SCT incorporato
        |
        v
crt.sh / Censys indicizzano il CT log -> sottodominio PUBBLICAMENTE visibile
```

**Implicazione per la sicurezza:** ogni certificato SSL emesso per un sottodominio interno (staging, dev, vpn, admin) diventa immediatamente visibile a chiunque interroghi i CT logs. Questo rende impossibile nascondere infrastrutture HTTPS dietro la "Security through Obscurity". I tool come Assetfinder interrogano direttamente `crt.sh` (interfaccia web/API ai CT logs di Comodo) e aggregano i risultati.

### Confronto delle Fonti di Discovery

| Fonte | Tecnica | Copertura | Latenza |
| :--- | :--- | :--- | :--- |
| **CT Logs** (crt.sh) | Certificati SSL emessi | Tutti i sottodomini con HTTPS | Minuti (quasi real-time) |
| **Motori di ricerca** (Google, Bing) | Crawling e indicizzazione | Solo pagine web linkate/crawlate | Giorni-settimane |
| **VirusTotal** | Correlazione DNS passivo | Sottodomini visti in sample malware/URL | Variabile |
| **DNS Brute Force** | Query DNS per wordlist | Limitata alla qualita della wordlist | Tempo di esecuzione |
| **GitHub/Pastebin** | Scraping codice sorgente | Sottodomini hardcoded nel codice | Variabile |

### Tool Moderno: Subfinder (ProjectDiscovery)

Sublist3r e un tool datato (ultimo aggiornamento 2019) con fonti spesso non funzionanti. L'alternativa moderna e `subfinder` (ProjectDiscovery), che supporta 40+ fonti dati e API key configurabili:

```Bash
# Installazione
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# Enumerazione con tutte le fonti
subfinder -d tesla.com -all -o tesla_subfinder.txt

# Pipeline operativa completa: discovery -> risoluzione -> probing HTTP
subfinder -d tesla.com -silent | dnsx -silent | httpx -silent -title -status-code
```

---

## Blue Team: Monitoraggio della Superficie di Attacco Esterna

**Monitoring proattivo:**
- Configurare alert su crt.sh per il proprio dominio: `https://crt.sh/?q=%.dominio.it` monitora tutti i certificati emessi per qualsiasi sottodominio - rileva sia certificati legittimi che certificati fraudolenti emessi da attaccanti per phishing
- Implementare Certificate Transparency Monitoring con tool come `certstream` (real-time) o `Facebook Certificate Transparency Monitoring` per rilevare certificati sospetti emessi per il proprio dominio

**Hardening:**
- Limitare l'emissione di certificati per il proprio dominio tramite record DNS CAA (Certification Authority Authorization): `dominio.it. CAA 0 issue "letsencrypt.org"` - solo la CA specificata puo emettere certificati
- Per sottodomini interni che non devono essere visibili nei CT logs, utilizzare certificati self-signed o CA interna (non registrata nei CT log pubblici) - con il trade-off che i browser mostreranno un warning
- Eseguire periodicamente subdomain enumeration sul proprio dominio per identificare asset dimenticati o non autorizzati (Shadow IT)

---

## Esperienza di Laboratorio

L'enumerazione su tesla.com ha prodotto oltre 500 sottodomini unici, un volume che in un assessment reale richiederebbe post-processing significativo. La fase critica non e stata la raccolta (automatica e veloce) ma il triage: separare i sottodomini ad alto valore (vpn, sso, dev-app, toolbox) dai sottodomini a basso interesse (cdn, static, assets).

Il confronto tra Sublist3r e Assetfinder ha rivelato una sovrapposizione parziale (~60%) nei risultati: Assetfinder ha trovato sottodomini tramite CT logs che Sublist3r aveva mancato (perche le API di alcuni motori di ricerca erano rate-limited o offline), mentre Sublist3r ha identificato sottodomini storici indicizzati su Google non piu presenti nei CT logs correnti. La lezione: in un assessment reale, la combinazione di piu tool e obbligatoria per massimizzare la copertura. La pipeline moderna `subfinder | dnsx | httpx` automatizza questo workflow in un singolo comando.

Un dettaglio operativo: il filtering con `grep "dev"` e `grep "admin"` e una tecnica rapida ma grezza. In un assessment professionale, si utilizza `httpx` per risolvere e probare ogni sottodominio, ottenendo status code, titolo della pagina e tecnologie - informazioni che permettono di prioritizzare i target senza visitarli manualmente uno per uno.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Search Open Technical Databases: DNS/Passive DNS | `T1596.001` | Enumerazione sottodomini di tesla.com tramite Certificate Transparency logs con Assetfinder, identificando 500+ host inclusi vpn e sso (DNS-003) |
| Reconnaissance | Gather Victim Network Info: DNS | `T1590.002` | Aggregazione sottodomini da motori di ricerca (Sublist3r) per mappare la superficie di attacco esterna del target (DNS-003) |

---

> **Nota:** Le attivita di subdomain enumeration sono state eseguite su tesla.com nell'ambito del programma pubblico di bug bounty dell'azienda, che autorizza esplicitamente la ricognizione passiva dell'infrastruttura. I risultati sono stati documentati a scopo esclusivamente didattico e non sono stati utilizzati per tentativi di accesso non autorizzato.