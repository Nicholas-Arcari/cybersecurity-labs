> [English](README.en.md) | **Italiano**

# 04 - Email Infrastructure

> - **Fase:** Social Engineering - Email Infrastructure Setup & Audit
> - **Visibilita:** Bassa (l'audit SPF/DKIM/DMARC e passivo: query DNS pubbliche) / Media (la configurazione SMTP relay e l'acquisto di domini typosquatting lasciano tracce registrabili)
> - **Prerequisiti:** Accesso a strumenti di query DNS (dig, nslookup, spoofcheck); per SMTP relay: account su servizio email transazionale (SendGrid, Mailgun) o server Postfix; per typosquatting: strumenti di generazione domini (dnstwist, urlcrazy)
> - **Output:** Finding SE-011..012; audit SPF/DKIM/DMARC del dominio target; configurazione SMTP relay operativa; lista domini typosquatting disponibili

---

## Introduzione

L'infrastruttura email e il fondamento tecnico che determina il successo o il fallimento di una campagna di phishing. Un'email tecnicamente perfetta (pretesto convincente, payload efficace) e inutile se finisce nello spam o se il dominio mittente e palesemente falso.

Questa sezione documenta tre componenti complementari:

1. **SPF/DKIM/DMARC Audit (SE-011):** analisi della configurazione email del dominio target per identificare misconfiguration che permettono lo spoofing. Un dominio senza DMARC in modalita `reject` o `quarantine` accetta email spoofate - l'attaccante puo inviare email che appaiono provenire da `ceo@target.com`.

2. **SMTP Relay:** configurazione dell'infrastruttura di invio per le campagne. Un relay configurato correttamente (SPF, DKIM, domain reputation) massimizza la deliverability e riduce il rischio di finire in blacklist.

3. **Domain Typosquatting (SE-012):** generazione e analisi di domini confondibili con il dominio target (es. `g00gle.com`, `microsfot.com`). L'acquisto di un dominio typosquatting con certificato TLS valido rende le email e le landing page quasi indistinguibili dall'originale.

---

## Struttura della cartella

```
04-email-infrastructure/
+-- spf-dkim-dmarc/        # Audit configurazione email target - SE-011
+-- smtp-relay/             # Configurazione SMTP per campagne (guida)
+-- domain-typosquatting/   # Generazione domini confondibili - SE-012
```

---

## `spf-dkim-dmarc/` - Email Security Audit

**ID Finding:** `SE-011` | **Severity:** `Medio` (DMARC policy `none` - spoofing possibile)

### Contesto operativo

L'audit ha verificato la configurazione SPF, DKIM e DMARC del dominio target simulato per determinare se fosse possibile inviare email spoofate. Il risultato - DMARC con policy `none` - significa che il dominio non blocca ne mette in quarantena le email che falliscono i controlli SPF/DKIM. Un attaccante puo inviare email con mittente `@target-lab.com` senza essere bloccato.

### Comandi principali

```Bash
# Verifica record SPF
dig +short TXT target-lab.com | grep spf
```

```
"v=spf1 include:_spf.google.com ~all"                      <-- softfail (~all), non hardfail (-all)
```

```Bash
# Verifica record DMARC
dig +short TXT _dmarc.target-lab.com
```

```
"v=DMARC1; p=none; rua=mailto:dmarc@target-lab.com"        <-- SE-011: policy "none" = no enforcement
```

```Bash
# Verifica con spoofcheck (tool dedicato)
git clone https://github.com/BishopFox/spoofcheck.git
cd spoofcheck && pip install -r requirements.txt
python3 spoofcheck.py target-lab.com
```

```
[+] target-lab.com
[+] SPF record found: v=spf1 include:_spf.google.com ~all
[-] SPF softfail (~all) - spoofing may be possible          <-- non hardfail
[+] DMARC record found
[-] DMARC policy is 'none' - no enforcement                 <-- SE-011
[!] Spoofing possible for target-lab.com                    <-- dominio vulnerabile
```

### Remediation

- **Azione immediata:** impostare DMARC policy a `quarantine` come primo step, poi migrare a `reject` dopo verifica dei report RUA/RUF
- **Azione strutturale:** SPF con `-all` (hardfail); DKIM signing attivo su tutti i server di invio; DMARC `p=reject` con reporting abilitato; monitoraggio continuo dei DMARC aggregate reports per identificare fonti di invio non autorizzate
- **Verifica:** `dig +short TXT _dmarc.target.com` deve restituire `p=reject`; invio di email spoofata di test deve essere rifiutata dal server destinatario

---

## `smtp-relay/` - Configurazione SMTP per Campagne

### Contesto operativo

La configurazione del relay SMTP e fondamentale per la deliverability delle email di phishing. La sezione documenta tre approcci:

1. **Servizio transazionale (SendGrid, Mailgun, Amazon SES):** deliverability elevata, domain reputation gestita dal provider, configurazione SPF/DKIM automatica. Limitazione: i provider hanno policy anti-abuse che possono bloccare contenuto sospetto.

2. **Server dedicato (Postfix/Haraka):** controllo completo, nessuna limitazione di contenuto. Richiede configurazione manuale di SPF, DKIM, rDNS, e domain warming (invio graduale per costruire reputation).

3. **GoPhish built-in SMTP:** GoPhish puo funzionare come server SMTP diretto, ma senza domain reputation il tasso di recapito e basso.

### Comandi principali

```Bash
# Configurazione Postfix come relay (Kali)
sudo apt install postfix
# Selezionare "Internet Site" durante il setup

# Configurazione DKIM con opendkim
sudo apt install opendkim opendkim-tools
opendkim-genkey -s mail -d attacker-lab.com
# Aggiungere il record TXT generato ai DNS del dominio
```

```Bash
# Test invio email con swaks
swaks --to victim@target-lab.com \
  --from ceo@attacker-lab.com \
  --server 127.0.0.1:25 \
  --header "Subject: Riunione urgente" \
  --body "Conferma la tua disponibilita."
```

---

## `domain-typosquatting/` - Generazione Domini Confondibili

**ID Finding:** `SE-012` | **Severity:** `Informativo` (domini confondibili non registrati identificati)

### Contesto operativo

Il typosquatting sfrutta la somiglianza visiva tra caratteri per creare domini che appaiono identici o quasi identici al dominio target. Il tool `dnstwist` genera automaticamente variazioni del dominio (sostituzione caratteri, omoglifi, trasposizioni) e verifica quali sono gia registrati e quali sono disponibili per l'acquisto.

### Comandi principali

```Bash
# Installazione dnstwist
sudo apt install dnstwist
# oppure
pip install dnstwist

# Generazione variazioni per il dominio target
dnstwist --registered target-lab.com
```

```
     _           _            _     _
  __| |_ __  ___| |___      _(_)___| |_
 / _` | '_ \/ __| __\ \ /\ / / / __| __|
| (_| | | | \__ \ |_ \ V  V /| \__ \ |_
 \__,_|_| |_|___/\__| \_/\_/ |_|___/\__|

domain               type          ip            mx
target-lab.com       original      93.184.216.34 mx.target-lab.com
targat-lab.com       replacement   -             -                     <-- disponibile
target-1ab.com       homoglyph     -             -                     <-- disponibile
targetlab.com        omission      198.51.100.1  mx.parked.com        <-- registrato (parked)
targt-lab.com        omission      -             -                     <-- disponibile
target-lab.co        tld-swap      203.0.113.5   -                     <-- registrato
```

```Bash
# Filtro solo domini disponibili (non registrati)
dnstwist --registered target-lab.com | grep -v "^\*" | awk '$3 == "-" {print $1}'
```

```
targat-lab.com                                              <-- SE-012: acquistabile
target-1ab.com                                              <-- SE-012: acquistabile (omoglifo)
targt-lab.com                                               <-- SE-012: acquistabile
```

### Remediation

- **Azione immediata:** registrazione preventiva dei domini typosquatting piu critici (quelli con singola sostituzione di carattere)
- **Azione strutturale:** monitoraggio continuo con dnstwist/URLCrazy schedulato settimanalmente; registrazione di domini difensivi (.com, .org, .net per le variazioni piu ovvie); segnalazione ai registrar di domini typosquatting attivi per abuse
- **Verifica:** riesecuzione di dnstwist - i domini critici devono risultare registrati e sotto il controllo dell'organizzazione

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `spoofcheck` | Email audit | CLI - Python | Verifica SPF/DKIM/DMARC e possibilita di spoofing |
| `dnstwist` | Domain analysis | CLI - Python | Generazione e verifica domini typosquatting |
| `URLCrazy` | Domain analysis | CLI - Ruby | Alternativa a dnstwist con focus su typo e bit-flip |
| `Postfix` | SMTP server | CLI - Config | Server SMTP per relay email con DKIM signing |
| `opendkim` | DKIM signer | CLI - Config | Generazione chiavi e firma DKIM per email in uscita |
| `swaks` | SMTP testing | CLI | Swiss Army Knife per SMTP: test invio, header, allegati |
| `Mailhog` | SMTP testing | Web UI | Fake SMTP per test locali senza invio reale |

> **Tool moderno consigliato:** `dnstwist` con flag `--all` per includere omoglifi Unicode e IDN homograph attacks. Per il monitoraggio continuo, servizi come `PhishLabs` o `Bolster` automatizzano la detection di domini typosquatting attivi.

---

## Registro Finding

| ID | Descrizione | Severity | CVSS | Sottocartella |
| :--- | :--- | :---: | :---: | :--- |
| `SE-011` | SPF/DKIM/DMARC audit: dominio target con SPF softfail e DMARC policy `none` - email spoofing possibile | `Medio` | 5.3 | `spf-dkim-dmarc/` |
| `SE-012` | Domain typosquatting: 3+ domini confondibili non registrati e acquistabili da un attaccante | `Informativo` | 3.1 | `domain-typosquatting/` |

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Finding Correlato |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Network Information: DNS | `T1590.002` | SE-011 |
| Reconnaissance | Search Open Technical Databases: DNS/Passive DNS | `T1596.001` | SE-011, SE-012 |
| Resource Development | Acquire Infrastructure: Domains | `T1583.001` | SE-012 |
| Resource Development | Acquire Infrastructure: Email Accounts | `T1583.002` | SE-011 |
| Resource Development | Compromise Infrastructure: Domains | `T1584.001` | SE-012 |

---

> **Nota:** Tutte le attivita documentate sono state condotte su domini di test creati ad hoc in ambiente di laboratorio. Nessun audit e stato effettuato su domini di terze parti senza autorizzazione. I domini typosquatting identificati non sono stati registrati.
