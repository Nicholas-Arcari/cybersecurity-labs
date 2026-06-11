> [English](README.en.md) | **Italiano**

# 01 - Phishing Campaigns

> - **Fase:** Social Engineering - Phishing Campaign Deployment & Credential Harvesting
> - **Visibilita:** Alta - le email phishing generano log SMTP, gli URL di tracking sono visibili ai filtri email/proxy, le landing page possono essere classificate da sistemi di URL reputation; Evilginx genera traffico TLS anomalo (doppio handshake)
> - **Prerequisiti:** Completamento fase di target profiling (email aziendali, organigramma); infrastruttura email configurata (dominio, SMTP relay, SPF/DKIM); per Evilginx: dominio valido con certificato TLS e record DNS controllati
> - **Output:** Finding SE-001..002; credenziali raccolte tramite landing page GoPhish; session token MFA intercettati via Evilginx; metriche di campagna (open/click/submit rate)

---

## Introduzione

La campagna di phishing e il momento in cui l'intera preparazione (pretexting, infrastruttura, payload) viene eseguita contro il target. I framework documentati in questa sezione coprono tre livelli di complessita:

**GoPhish (SE-001):** piattaforma open-source che rappresenta lo standard aziendale per le simulazioni di phishing. GoPhish gestisce l'intero ciclo: creazione template email, landing page con credential harvesting, invio programmato, tracking granulare (apertura email, click link, inserimento credenziali). Le metriche prodotte sono il deliverable primario in un assessment di security awareness.

**Evilginx (SE-002):** reverse proxy phishing framework che opera come Man-in-the-Middle tra il target e il servizio legittimo (Microsoft 365, Google Workspace, Okta). A differenza del phishing tradizionale che cattura solo username e password, Evilginx intercetta i session cookie post-autenticazione, bypassando completamente l'MFA. E la tecnica di phishing piu avanzata documentata in questa repository e rappresenta la minaccia principale per le organizzazioni che considerano l'MFA una protezione sufficiente.

**PyPhisher:** wrapper automatizzato con 77 template pre-costruiti e 4 provider di tunneling. Utile per test rapidi e PoC, ma inadatto a campagne professionali (tunnel generici facilmente bloccati, nessuna metrica, nessuna personalizzazione avanzata).

Nella kill chain, questa sezione copre le fasi di Delivery ed Exploitation: l'email raggiunge la vittima (Delivery), la vittima interagisce con il contenuto (Exploitation), e le credenziali/sessioni vengono raccolte (Collection).

---

## Struttura della cartella

```
01-phishing-campaigns/
+-- gophish/       # Standard aziendale: campaign management + analytics - SE-001
+-- evilginx/      # MFA bypass reverse proxy - SE-002
+-- pyphisher/     # Quick testing: 77 template, tunnel automatico (no finding)
```

---

## `gophish/` - Campaign Management & Credential Harvesting

**ID Finding:** `SE-001` | **Severity:** `Alto` (click rate > 30% su campagna simulata con credential submission)

### Contesto operativo

GoPhish e stato utilizzato per progettare e lanciare una campagna phishing simulata contro un gruppo di 20 utenti fittizi in ambiente di laboratorio. La campagna ha replicato un tipico scenario aziendale: email di reset password proveniente dall'IT department, con link a una landing page clone del portale di autenticazione interno. Il risultato - click rate superiore al 30% e credential submission rate significativo - dimostra l'efficacia del vettore phishing anche in assenza di sofisticazione tecnica.

### Comandi principali

```Bash
# Avvio GoPhish
cd /opt/gophish && sudo ./gophish
# Admin panel: https://127.0.0.1:3333
# Phishing server: http://0.0.0.0:80
```

```Bash
# Workflow via Web UI:
# 1. Sending Profile -> SMTP relay (SendGrid/locale)
# 2. Landing Page -> "Import Site" -> clone del portale target
# 3. Email Template -> HTML con {{.URL}} e {{.Tracker}}
# 4. Users & Groups -> import CSV (nome, cognome, email, ruolo)
# 5. Campaign -> associazione componenti -> Launch
```

---

## `evilginx/` - MFA Bypass via Reverse Proxy

**ID Finding:** `SE-002` | **Severity:** `Critico` (session token MFA intercettato - accesso completo senza password)

### Contesto operativo

Evilginx opera come un reverse proxy trasparente tra la vittima e il servizio di autenticazione legittimo. La vittima completa l'intero flusso di login (password + MFA) interagendo con il servizio reale, ma Evilginx intercetta i session cookie emessi post-autenticazione. L'attaccante importa questi cookie nel proprio browser per accedere all'account senza conoscere la password e senza ripetere l'MFA.

### Comandi principali

```Bash
# Setup Evilginx
sudo ./evilginx -p ./phishlets -developer
config domain lab.local
config ipv4 192.168.0.110

# Phishlet Microsoft 365
phishlets hostname o365 login.lab.local
phishlets enable o365

# Creazione URL di phishing
lures create o365
lures get-url 0
# Output: https://login.lab.local/NeKzw3E

# Sessioni catturate
sessions
# -> session cookie Azure AD catturato post-MFA
```

---

## `pyphisher/` - Quick Testing & Proof of Concept

### Contesto operativo

PyPhisher e un tool Python che automatizza la creazione di pagine di phishing con 77 template pre-costruiti e 4 provider di tunneling (Ngrok, Cloudflared, LocalXpose, LocalHostRun). Utile per PoC rapidi e dimostrazioni didattiche, ma con limitazioni significative per uso professionale: tunnel generici facilmente bloccati, nessuna metrica, template non personalizzabili. La documentazione completa e nel README dedicato nella sottocartella.

---

## Flusso operativo consigliato

```
[1] Analisi del target
     +-- MFA abilitato? -----> SI -> Evilginx (bypass MFA)
     |                   +--> NO -> GoPhish (credential harvesting standard)
     +-- Solo PoC/demo? -----> PyPhisher (test rapido con tunnel)
              |
              v
[2] Setup infrastruttura
     +-- GoPhish:   SMTP relay + landing page + template email
     +-- Evilginx:  dominio + DNS + certificato TLS + phishlet
     +-- PyPhisher: installazione locale + scelta tunnel
              |
              v
[3] Crafting & Lancio
     +-- Email template personalizzato (pretesto da 05-pretexting)
     +-- Landing page clone del portale target
     +-- Monitoraggio metriche in tempo reale
              |
              v
[4] Collection & Reporting
     +-- Credenziali raccolte -> verifica validita
     +-- Session token -> replay in browser
     +-- Report per il cliente con metriche e raccomandazioni
```

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `GoPhish` | Phishing platform | Web UI | Standard aziendale: campaign management, template, analytics |
| `Evilginx 3.x` | Reverse proxy phisher | CLI | MFA bypass via session hijacking, phishlet per servizi cloud |
| `PyPhisher` | Automated phishing | CLI - Python | Quick PoC con 77 template e tunnel automatico |
| `King Phisher` | Phishing platform | GUI + CLI | Alternativa a GoPhish con reporting avanzato |
| `Modlishka` | Reverse proxy | CLI - Go | Alternativa a Evilginx, piu leggero |
| `Mailhog` | SMTP testing | Web UI | Fake SMTP server per test locali |

> **Tool moderno consigliato:** `Evilginx 3.x` e il tool di riferimento per phishing avanzato nel 2024-2026. Per campagne enterprise, `GoPhish` + `Mailhog` permette testing completo senza rischio di invio a indirizzi reali.

---

## Registro Finding

| ID | Descrizione | Severity | CVSS | Sottocartella |
| :--- | :--- | :---: | :---: | :--- |
| `SE-001` | GoPhish campaign: credential harvesting con click rate > 30% e submission rate 20% su 20 utenti simulati | `Alto` | 8.1 | `gophish/` |
| `SE-002` | Evilginx: MFA bypass via reverse proxy - session token Microsoft 365 intercettato dopo autenticazione MFA completa | `Critico` | 9.3 | `evilginx/` |

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Finding Correlato |
| :--- | :--- | :--- | :--- |
| Resource Development | Stage Capabilities: Upload Malware | `T1608.001` | SE-001, SE-002 |
| Resource Development | Acquire Infrastructure: Domains | `T1583.001` | SE-002 |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | SE-001, SE-002 |
| Execution | User Execution: Malicious Link | `T1204.001` | SE-001, SE-002 |
| Credential Access | Input Capture: Web Portal Capture | `T1056.003` | SE-001 |
| Credential Access | Steal Web Session Cookie | `T1539` | SE-002 |
| Credential Access | Adversary-in-the-Middle | `T1557` | SE-002 |

---

> **Nota:** Tutte le attivita documentate sono state condotte in un ambiente di laboratorio virtualizzato (VirtualBox, rete NAT/Bridge isolata). Le campagne phishing sono state dirette esclusivamente contro utenti fittizi su macchine virtuali di proprieta dell'autore. Nessuna email e stata inviata a indirizzi reali.
