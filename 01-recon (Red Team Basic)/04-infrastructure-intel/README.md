> [English](README.en.md) | **Italiano**

# 04 - Infrastructure intelligence

> - **Fase:** Reconnaissance - Infrastructure Intelligence Gathering
> - **Visibilita:** Zero / Bassa - ricerca su database pubblici, fingerprinting HTTP standard
> - **Prerequisiti:** Dominio o range IP target identificato, account Shodan/Censys (free tier sufficiente)
> - **Output:** Asset esposti con RDP/VoIP/FTP su IP pubblici (INTEL-001, INTEL-002, INTEL-003), profilo tecnologico del target (INTEL-004)

---

## Introduzione

L'Infrastructure Intelligence e la fase di ricognizione che sfrutta i database pubblici costruiti da scanner automatizzati che setacciano continuamente l'intero spazio IPv4 di Internet. Strumenti come Shodan e Censys archiviano i banner e i certificati di ogni servizio raggiungibile pubblicamente, permettendo agli analisti di "vedere" l'infrastruttura di qualsiasi organizzazione senza inviare un singolo pacchetto verso di essa.

Il vantaggio operativo e duplice:
- **Per il Red Team:** si ottiene una mappa della superficie di attacco esterna completa e storica, incluse versioni software, porte aperte, certificati TLS e configurazioni in un tempo estremamente ridotto
- **Per il difensore:** questi database sono accessibili a chiunque, inclusi i gruppi ransomware. Se un asset aziendale appare su Shodan con RDP esposto, e gia nel mirino di attori malevoli automatizzati

Questa fase completa il profilo dell'organizzazione costruito nelle fasi precedenti:
- `01-osint-passive/` ha identificato email, dipendenti e credenziali
- `03-dns-enumeration/` ha mappato i sottodomini e i record DNS
- **Questa sezione** collega i dati ai servizi esposti su Internet e identifica il tech stack

Il tech stack fingerprinting e direttamente connesso al modulo `02-vulnerability-assessment/`: conoscere che un server gira Apache 2.4.49 permette di cercare immediatamente il CVE corrispondente.

---

## Struttura della cartella

```
04-infrastructure-intel/
+-- README.md                <- questo file (indice + registro finding)
|
+-- shodan-censys/
|   +-- README.md            <- INTEL-001..003: asset RDP/VoIP/FTP esposti (Shodan, Censys, Whois)
|   +-- img/                 <- screenshot del lab
|
+-- tech-stack/
|   +-- README.md            <- INTEL-004: fingerprinting tecnologico (WhatWeb, Wappalyzer)
|   +-- img/                 <- screenshot del lab
|
+-- asn-whois-ct/
|   +-- README.md            <- INTEL-005: mappatura perimetro (ASN, WHOIS, Certificate Transparency)
|   +-- img/                 <- screenshot del lab
|
+-- cloud-asset-discovery/
    +-- README.md            <- INTEL-006: storage cloud esposto (bucket S3/Azure Blob/GCP)
    +-- img/                 <- screenshot del lab
```

---

## `shodan-censys/` - Asset intelligence da database pubblici

**ID Finding:** `INTEL-001` | **Severity:** `Alto`
**ID Finding:** `INTEL-002` | **Severity:** `Alto`
**ID Finding:** `INTEL-003` | **Severity:** `Critico`

L'analisi su Shodan e Censys della citta di Parma (caso studio didattico) ha rivelato tre categorie di asset criticamente esposti:

- **INTEL-001:** 60+ dispositivi con RDP (porta 3389) esposto pubblicamente, con Information Disclosure di nomi host e sistema operativo
- **INTEL-002:** Workstation personale/aziendale con RDP + Apache non standard + servizi di gestione esposti su IP pubblico business - il classico "PC dimenticato sotto la scrivania"
- **INTEL-003:** Server aziendale singolo che gestisce contemporaneamente VoIP (3CX), File Server (FileZilla FTP), Remote Desktop e Plex Media Server su una linea ADSL consumer - superficie di attacco critica con single point of failure

La cross-validation tra Shodan (identificazione servizi e banner) e Censys (analisi certificati TLS) ha confermato le identita dei target e scoperto servizi aggiuntivi non visibili nella prima analisi.

---

## `tech-stack/` - Tech stack fingerprinting

**ID Finding:** `INTEL-004` | **Severity:** `Informativo`

Il Tech Stack Fingerprinting identifica le tecnologie sottostanti un'applicazione web analizzando le risposte HTTP, i cookie, gli header e il codice sorgente. Conoscere il CMS, il web server e le librerie client-side permette di selezionare gli exploit corretti nella fase di exploitation.

**Risultato del lab su `tesla.com`:** WhatWeb bloccato dall'Akamai WAF (403 Forbidden). La risposta stessa ha pero rivelato l'uso di Akamai come CDN/WAF e la presenza di HSTS. Le difese perimetrali di Tesla impediscono il fingerprinting automatizzato del backend.

**Lezione operativa:** contro target con WAF enterprise (Akamai, Cloudflare, F5), il fingerprinting passivo via Wappalyzer o BuiltWith e piu efficace degli scanner attivi.

---

## `asn-whois-ct/` - Mappatura del perimetro (ASN, WHOIS, certificate transparency)

**ID Finding:** `INTEL-005` | **Severity:** `Variabile (Informativo / Medio)`

Prima di scansionare occorre sapere cosa appartiene al target. Questa sezione combina due fonti passive per ricostruire il perimetro completo: **ASN/WHOIS** per identificare i blocchi IP (CIDR) di proprieta annunciati via BGP, e **Certificate Transparency** per scoprire i sottodomini nascosti dai certificati TLS emessi (`vpn.`, `dev.`, `jenkins.`, `admin.`).

Il risultato e la mappa completa della superficie di attacco esterna - perimetro IP + perimetro DNS - in modo totalmente invisibile al target. Mentre `shodan-censys/` dice "cosa e esposto", questa sezione dice "cosa esiste e a chi appartiene". La lista di sottodomini alimenta `03-dns-enumeration/subdomain-finding/`; i range IP diventano lo scope per `02-network-scanning-active/`.

---

## `cloud-asset-discovery/` - Storage cloud esposto

**ID Finding:** `INTEL-006` | **Severity:** `Variabile (Medio / Critico)`

Le organizzazioni moderne archiviano dati crescenti in storage cloud (AWS S3, Azure Blob, GCP Storage), raggiungibili via URL prevedibili e protetti solo dalla configurazione dei permessi. Una misconfiguration (bucket "public" invece che "private") espone il contenuto a chiunque conosca o indovini il nome del bucket.

Il README dedicato copre l'enumerazione per permutazione multi-cloud (`cloud_enum`), la ricerca passiva su indici (GrayHatWarfare) e la verifica dei permessi anonimi. Un bucket leggibile con backup di database o segreti e `Critico`. Questa sezione e il ponte diretto verso `10-cloud-security/01-providers-infrastructure/S3-buckets-attacks/`.

---

## Flusso operativo consigliato

```
[INPUT] Dominio o range IP target
          |
          v
[1] Shodan Query (Zero-Touch)
     +-- ip:<IP_TARGET>                     # analisi specifico IP
     +-- hostname:<DOMINIO>                 # servizi per dominio
     +-- port:3389 org:"<AZIENDA>"          # RDP esposto per org
     +-- port:22 vuln:CVE-XXXX-YYYY         # host vulnerabili specifici
     -> Asset map: IP, porte, banner, versioni, OS
          |
          v
[2] Censys Cross-Reference (Zero-Touch)
     +-- ip:<IP_TARGET>                     # validazione e nuovi finding
     -> Analisi certificati TLS, nuovi servizi, conferma identita
          |
          v
[3] Whois (Zero-Touch)
     +-- whois <IP>                         # ISP, contatti abuso, AS number
     -> Identificazione tipo connessione (datacenter vs consumer), geolocalizzazione reale
          |
          v
[4] Tech Stack Fingerprinting (Bassa Visibilita)
     +-- whatweb -v <DOMINIO>               # richiesta HTTP singola
     +-- Wappalyzer browser extension       # analisi passiva durante navigazione
     +-- BuiltWith web                      # database storico tech stack
     -> CMS, framework, librerie, versioni
          |
          v
[5] Perimeter Mapping (Zero-Touch)
     +-- amass intel -org / whois <IP>      # ASN e blocchi CIDR di proprieta
     +-- crt.sh?q=%25.<DOMINIO>             # sottodomini da Certificate Transparency
     -> perimetro completo IP + DNS (INTEL-005)
          |
          v
[6] Cloud Asset Discovery (Bassa Visibilita)
     +-- cloud_enum -k <BRAND>              # bucket S3/Azure/GCP per keyword
     +-- aws s3 ls --no-sign-request        # verifica permessi anonimi
     -> storage cloud esposto (INTEL-006)
          |
          v
[OUTPUT] Attack surface esterna completa -> 02-vulnerability-assessment/, 10-cloud-security/
```

---

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Shodan` | scan database | web / cli (`shodan`) | ricerca asset esposti per ip, porta, banner, cve |
| `Censys` | scan database | web | analisi certificati tls, validazione shodan |
| `Whois` | osint | cli | isp, contatti abuso, geolocalizzazione reale |
| `WhatWeb` | tech fingerprint | cli | fingerprinting tecnologie web via richiesta http |
| `Wappalyzer` | tech fingerprint | browser extension | fingerprinting passivo durante navigazione |
| `BuiltWith` | tech fingerprint | web | database storico tech stack per dominio |
| `FOFA` | scan database | web | alternativa asiatica a shodan, utile per target specifici |
| `Netlas.io` | scan database | web | alternativa moderna a shodan con query avanzate |
| `amass intel` | osint/asn | cli | da nome org a asn e blocchi cidr, aggregazione ct |
| `crt.sh` | certificate transparency | web / api | sottodomini nascosti dai certificati tls emessi |
| `cloud_enum` | cloud recon | cli | enumerazione bucket s3/azure/gcp per keyword |

> **Tool moderno consigliato:** `Shodan CLI` (`pip install shodan`, `shodan init <API_KEY>`) - permette di automatizzare le query Shodan in script e integrare i risultati in workflow di OSINT automatizzato. Comando di esempio: `shodan search "port:3389 city:Parma" --fields ip_str,port,org`.

---

## Registro finding

| id | descrizione | severity | file |
| :--- | :--- | :---: | :--- |
| `INTEL-001` | 60+ dispositivi con rdp esposto a parma - nomi host e os rilevati | `Alto` | `shodan-censys/README.md` |
| `INTEL-002` | workstation con rdp + apache su porta non standard + servizi di gestione su ip pubblico | `Alto` | `shodan-censys/README.md` |
| `INTEL-003` | server aziendale con voip (3cx) + ftp (filezilla) + rdp su adsl consumer | `Critico` | `shodan-censys/README.md` |
| `INTEL-004` | tesla.com protetta da akamai waf - fingerprinting bloccato, hsts attivo | `Informativo` | `tech-stack/README.md` |
| `INTEL-005` | perimetro completo mappato via asn/whois e sottodomini da certificate transparency | `Variabile (Informativo / Medio)` | `asn-whois-ct/README.md` |
| `INTEL-006` | storage cloud esposto (bucket s3/blob) con lettura anonima di dati sensibili | `Variabile (Medio / Critico)` | `cloud-asset-discovery/README.md` |

---

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| reconnaissance | search open technical databases: scan databases | `T1596.005` | ricerca asset esposti su shodan e censys per ip e porta, identificando rdp, voip, ftp pubblici (INTEL-001, INTEL-002, INTEL-003) |
| reconnaissance | gather victim network info: network topology | `T1590.004` | mappatura infrastruttura target tramite analisi banner shodan, certificati tls e prefissi bgp annunciati dall'asn (INTEL-001..003, INTEL-005) |
| reconnaissance | gather victim host info: software | `T1592.002` | tech stack fingerprinting tramite whatweb e wappalyzer per identificare cms, web server e framework (INTEL-004) |
| reconnaissance | gather victim network info: ip addresses | `T1590.005` | identificazione dei blocchi cidr di proprieta del target tramite whois e amass intel (INTEL-005) |
| reconnaissance | search open technical databases: digital certificates | `T1596.003` | enumerazione di sottodomini nascosti tramite i log di certificate transparency (INTEL-005) |
| reconnaissance | search open technical databases | `T1596` | scoperta di storage cloud esposto tramite enumerazione per permutazione e indici pubblici (INTEL-006) |
| collection | data from cloud storage | `T1530` | accesso anonimo ai contenuti di bucket cloud con permessi pubblici (INTEL-006) |

---

> **Nota:** Le ricerche su Shodan e Censys sono state eseguite a scopo esclusivamente didattico per documentare metodologie di Infrastructure Intelligence. I target identificati (aziende reali con asset esposti) sono stati segnalati secondo il principio di Responsible Disclosure. Nessun tentativo di accesso o exploitation e stato condotto su sistemi di terze parti.
