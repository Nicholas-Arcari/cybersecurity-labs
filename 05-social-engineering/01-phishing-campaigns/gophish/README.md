> [English](README.en.md) | **Italiano**

# GoPhish - Campaign Management & Credential Harvesting

> - **Fase:** Social Engineering - Phishing Campaign Deployment
> - **Visibilita:** Alta - email di phishing generano log SMTP, tracking pixel e URL visibili ai filtri email/proxy/SIEM; la landing page puo essere classificata da sistemi di URL reputation e Google Safe Browsing
> - **Prerequisiti:** GoPhish installato (Go binary o pacchetto Kali); SMTP relay configurato (SendGrid, Mailgun o server locale); lista target con email valide; template email e landing page preparati; dominio e certificato TLS per credibilita
> - **Output:** SE-001 (credential harvesting campaign con click rate > 30% - severity Alto); metriche complete di campagna (open/click/submit/report rate per singolo destinatario)

- **Ambiente Operativo:** Kali Linux Purple (Attaccante + GoPhish Server), Windows/Linux VM (Target simulati)
- **Target:** 20 utenti fittizi in ambiente di laboratorio
- **Framework:** GoPhish v0.12.1
- **Tecniche Documentate:** Credential Harvesting via Landing Page Clone, Email Template con Tracking Pixel

---

## Executive Summary

GoPhish e lo standard de facto per le campagne di phishing simulato in ambito aziendale. A differenza di tool come PyPhisher o Zphisher che operano tramite tunnel generici facilmente bloccabili, GoPhish offre un ecosistema completo per la gestione professionale delle simulazioni: creazione di template email personalizzati con variabili dinamiche, clonazione di landing page con credential capture, scheduling programmato degli invii, e soprattutto un sistema di tracking granulare che monitora ogni interazione del destinatario (apertura email, click sul link, inserimento credenziali, segnalazione phishing).

Queste metriche sono il deliverable primario in un assessment di security awareness: permettono di misurare il rischio umano dell'organizzazione, identificare i dipartimenti piu vulnerabili, e costruire programmi di training mirati.

---

## Campagna: Credential Harvesting via Password Reset

**ID Finding:** `SE-001` | **Severity:** `Alto`

### Contesto operativo

La campagna ha simulato un classico scenario di phishing aziendale: un'email urgente dall'IT department che richiede un reset password immediato, con link a una landing page clone del portale di autenticazione. Lo scenario e stato scelto per la sua efficacia documentata: secondo il report Proofpoint State of the Phish 2024, le email di reset password hanno un click rate medio del 25-35% nelle organizzazioni senza programmi di awareness strutturati.

### PoC - Fase 1: Setup GoPhish

```Bash
# Download e avvio GoPhish
cd /opt/gophish
sudo ./gophish
```

```
time="2026-03-15T10:00:00Z" level=info msg="Starting admin server at https://127.0.0.1:3333"    <-- Admin panel
time="2026-03-15T10:00:00Z" level=info msg="Starting phishing server at http://0.0.0.0:80"       <-- Landing page
time="2026-03-15T10:00:00Z" level=info msg="Background Worker Started Successfully"
time="2026-03-15T10:00:00Z" level=info msg="Starting IMAP monitor manager"
```

### PoC - Fase 2: Configurazione Sending Profile

```Bash
# Sending Profile (via Web UI -> Sending Profiles -> New Profile)
# Name: Lab-SMTP
# From: it-support@company-lab.local
# Host: 127.0.0.1:25
# Username/Password: (vuoti per relay locale)
# -> Send Test Email per verifica
```

### PoC - Fase 3: Creazione Landing Page

```Bash
# Landing Page (via Web UI -> Landing Pages -> New Page)
# Name: Company Portal Login
# -> "Import Site" -> URL: https://portal.company-lab.local/login
# [x] Capture Submitted Data
# [x] Capture Passwords
# Redirect to: https://portal.company-lab.local/login?reset=success
```

### PoC - Fase 4: Template Email

```Bash
# Email Template (via Web UI -> Email Templates -> New Template)
# Name: IT Password Reset
# Subject: [URGENTE] Reset password obbligatorio - IT Department
# -> "Import Email" oppure HTML editor
```

```html
<!-- Template HTML semplificato -->
<p>Gentile {{.FirstName}},</p>
<p>Il tuo account aziendale richiede un <b>reset password immediato</b>
a causa di un aggiornamento di sicurezza programmato.</p>
<p>Clicca sul link seguente per procedere al reset:</p>
<p><a href="{{.URL}}">Reimposta la tua password</a></p>
<p>Se non completi questa operazione entro 24 ore, il tuo account
verra temporaneamente sospeso.</p>
<p>IT Department<br>{{.From}}</p>

<!-- {{.Tracker}} inserisce automaticamente il tracking pixel 1x1 -->
{{.Tracker}}
```

### PoC - Fase 5: Import Target e Lancio

```Bash
# Users & Groups (via Web UI -> Users & Groups -> New Group)
# Name: Lab-Users-Q1
# -> "Bulk Import Users" -> CSV format:
# First Name,Last Name,Email,Position
# Mario,Rossi,m.rossi@company-lab.local,Accounting
# Luca,Bianchi,l.bianchi@company-lab.local,HR
# [... 20 utenti totali ...]
```

```Bash
# Campaign Launch (via Web UI -> Campaigns -> New Campaign)
# Name: Password Reset Q1 2026
# Email Template: IT Password Reset
# Landing Page: Company Portal Login
# Sending Profile: Lab-SMTP
# Groups: Lab-Users-Q1
# -> Launch Campaign
```

### PoC - Fase 6: Risultati della Campagna

```
Campaign Results - "Password Reset Q1 2026"
============================================
Status: Completed

Timeline:
  2026-03-15 10:05 - Campaign launched (20 emails queued)
  2026-03-15 10:05 - 20/20 emails sent successfully
  2026-03-15 10:12 - First email opened (m.rossi@company-lab.local)
  2026-03-15 10:15 - First link clicked (m.rossi@company-lab.local)
  2026-03-15 10:16 - First credentials submitted                       <-- SE-001

Aggregate Metrics:
  Total Recipients:     20
  Emails Sent:          20    (100%)
  Emails Opened:        14    ( 70%)     <-- tracking pixel attivato
  Links Clicked:         7    ( 35%)     <-- click rate > soglia 30%
  Data Submitted:        4    ( 20%)     <-- credential harvesting riuscito
  Email Reported:        1    (  5%)     <-- solo 1 segnalazione

Credentials Captured:
  m.rossi@company-lab.local      | Password: M4ri0R0ss1!    | 2026-03-15 10:16
  l.bianchi@company-lab.local    | Password: Luca2025       | 2026-03-15 10:22
  a.verdi@company-lab.local      | Password: Company123!    | 2026-03-15 10:31
  f.neri@company-lab.local       | Password: Firenze2026$   | 2026-03-15 11:05
```

### Remediation

- **Azione immediata:** reset password forzato per i 4 utenti che hanno inserito credenziali; verifica nei log di autenticazione per accessi anomali nelle 24 ore successive; revoca di eventuali session token attivi
- **Azione strutturale:** implementazione programma di security awareness con simulazioni phishing trimestrali (obiettivo: click rate < 10%, report rate > 30%); deploy MFA su tutti gli account aziendali; configurazione email gateway con URL sandboxing (Proofpoint TAP, Microsoft Safe Links); banner di avviso automatico su email esterne ("This email originated outside your organization")
- **Verifica:** ripetizione della campagna dopo 3 mesi di training - misurare il delta di click rate e report rate rispetto alla baseline

---

## Esperienza di Laboratorio

L'ambiente di test e stato configurato con GoPhish v0.12.1 su Kali Linux Purple, utilizzando un relay SMTP locale (Postfix) per l'invio delle email verso le caselle di posta dei 20 utenti fittizi ospitati su una seconda VM con Mailhog come server SMTP di ricezione.

La prima difficolta incontrata e stata la configurazione del Sending Profile: GoPhish richiede un SMTP relay funzionante e il test interno ("Send Test Email") ha restituito un errore `Connection refused on port 25` finche Postfix non e stato riconfigurato per accettare connessioni locali non autenticate. In un engagement reale, il relay sarebbe un servizio esterno (SendGrid, Amazon SES) con dominio e DKIM configurati per massimizzare la deliverability.

La fase piu critica e stata il design del template email. Il primo template era troppo generico e conteneva errori di formattazione HTML visibili nei client email. Dopo una revisione ispirata ai template di phishing reali (catalogati in phishtank.org), il template e stato raffinato con: urgenza temporale ("entro 24 ore"), authority impersonation ("IT Department"), e un solo call-to-action chiaro. Questa iterazione ha portato il click rate dal 15% (primo invio di test) al 35% (campagna finale).

Il dato piu significativo dell'esercizio non e il click rate in se (35% e nella media delle organizzazioni non addestrate), ma il report rate: solo 1 utente su 20 (5%) ha segnalato l'email sospetta. In un'organizzazione con un programma di awareness maturo, il report rate target e superiore al 30%.

---

## Analisi Teorica: Perche il Phishing Funziona

L'efficacia del phishing non e un problema tecnologico ma cognitivo. Il template utilizzato sfrutta tre dei sei principi di influenza di Robert Cialdini:

1. **Autorita:** l'email proviene dall'"IT Department", una fonte percepita come legittima e autorevole in ambito tecnico.
2. **Urgenza/Scarsita:** la minaccia di sospensione dell'account entro 24 ore attiva il sistema limbico (risposta fight-or-flight), bypassando l'analisi critica della corteccia prefrontale.
3. **Prova sociale implicita:** il tono formale e la struttura dell'email replicano le comunicazioni aziendali reali, creando familiarita.

Dal punto di vista tecnico, GoPhish sfrutta due meccanismi chiave: il tracking pixel (immagine 1x1 pixel trasparente caricata da un URL unico per destinatario) per misurare l'apertura email, e il parametro `rid` (recipient ID) nell'URL della landing page per tracciare quale utente ha cliccato. I credential catturati vengono salvati nel database SQLite di GoPhish e sono consultabili dalla dashboard in tempo reale.

La differenza critica tra GoPhish e i tool amatoriali (PyPhisher, Zphisher) e la tracciabilita: GoPhish produce un report strutturato con metriche per singolo destinatario, timestamp di ogni interazione, e dati aggregati per dipartimento. Questo report e il deliverable che il cliente si aspetta in un assessment di security awareness.

---

## Scenario Reale: Proiezione Post-Exploitation

> Questa sezione descrive come questo finding si inserirebbe in un engagement reale, sia dal punto di vista dell'attaccante (Red Team) che del difensore (Blue Team).

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** 4 credenziali aziendali valide ottenute tramite phishing (SE-001).

**Passo successivo immediato:** credential stuffing mirato - testare le 4 credenziali su tutti i servizi esposti dell'organizzazione (VPN, OWA, SharePoint, Citrix) per identificare il credential reuse.

**Kill Chain proiettata:**

```
[SE-001] Credenziali raccolte (4 account)
        |
        v
Credential Stuffing su VPN/OWA -> accesso remoto con account legittimo
        |
        v
Email compromise (BEC) -> invio phishing interno da account trusted
        |
        v
Lateral Movement -> accesso a share interni, escalation via Active Directory
        |
        v
Domain Admin -> esfiltrazione dati / ransomware deployment
```

**Impatto potenziale:** compromissione completa del dominio Active Directory a partire da un singolo account di livello standard. Il tempo medio da Initial Access a Domain Admin, secondo i report Mandiant M-Trends 2024, e inferiore a 48 ore nelle organizzazioni senza segmentazione di rete.

### Prospettiva Difensore (Blue Team)

**IOC da monitorare:**
- Email con tracking pixel verso domini non aziendali (URL con parametri `rid` o simili)
- Login da IP/geolocalizzazione anomala per gli account compromessi
- Accessi multipli a servizi diversi dallo stesso account in finestra temporale ridotta (credential stuffing pattern)
- Creazione di regole di inoltro email nell'account compromesso (persistence)

**Contenimento immediato:**
- Reset password forzato per tutti gli account compromessi
- Revoca session token attivi (Azure AD: `Revoke-AzureADUserAllRefreshToken`)
- Verifica regole di inoltro email create negli ultimi 7 giorni
- Analisi log di autenticazione per credential stuffing pattern

**Hardening:**
- Deploy MFA FIDO2/WebAuthn (non SMS/OTP - vulnerabili a Evilginx)
- Conditional Access: blocco login da paesi non operativi
- Email gateway: URL rewriting + time-of-click analysis
- Security awareness: training trimestrale con metriche di miglioramento

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Resource Development | Stage Capabilities: Upload Malware | `T1608.001` | Preparazione landing page clone e template email su server GoPhish (SE-001) |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | Invio email con link a landing page di credential harvesting (SE-001) |
| Execution | User Execution: Malicious Link | `T1204.001` | 7 utenti su 20 hanno cliccato il link di phishing (SE-001) |
| Credential Access | Input Capture: Web Portal Capture | `T1056.003` | 4 utenti hanno inserito credenziali nella landing page clone (SE-001) |
| Discovery | System Information Discovery | `T1082` | Tracking pixel ha rivelato User-Agent e IP di 14 utenti che hanno aperto l'email |

---

> **Nota:** Tutte le attivita documentate sono state condotte in un ambiente di laboratorio virtualizzato (VirtualBox, rete NAT/Bridge isolata). I destinatari della campagna sono utenti fittizi creati ad hoc. Nessuna email di phishing e stata inviata a indirizzi reali. Le tecniche sono documentate a scopo educativo e di security awareness testing.
