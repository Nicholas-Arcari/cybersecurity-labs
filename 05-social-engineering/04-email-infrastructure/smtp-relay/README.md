> [English](README.en.md) | **Italiano**

# SMTP Relay - Configurazione Infrastruttura di Invio

> - **Fase:** Social Engineering - Email Infrastructure Setup
> - **Visibilita:** Media - la configurazione del relay e interna, ma l'invio di email genera log SMTP, record DNS (SPF, DKIM, rDNS) e contribuisce alla domain reputation tracciabile da servizi come MXToolbox e Talos Intelligence
> - **Prerequisiti:** Server con IP pubblico (VPS) o account su servizio transazionale (SendGrid, Mailgun, Amazon SES); dominio registrato con accesso alla gestione DNS; conoscenza base di Postfix e DKIM
> - **Output:** Infrastruttura SMTP operativa per campagne phishing simulate; configurazione SPF/DKIM per massimizzare deliverability

- **Ambiente Operativo:** Kali Linux Purple con Postfix (relay locale), Mailhog (testing)
- **Tecniche Documentate:** Postfix Setup, DKIM Signing, Domain Warming, Deliverability Optimization

---

## Executive Summary

La configurazione del relay SMTP e il passaggio che trasforma un tool di phishing (GoPhish, SET) in una piattaforma di delivery operativa. Senza un relay correttamente configurato, le email di phishing finiscono nello spam o vengono rifiutate dai server destinatari. La sezione documenta tre approcci con trade-off diversi tra facilita di setup, deliverability e controllo operativo.

---

## Approccio 1: Servizio Transazionale (Raccomandato per Lab)

I servizi come SendGrid, Mailgun e Amazon SES offrono deliverability elevata grazie alla domain reputation consolidata. Sono la scelta ottimale per laboratori e campagne di security awareness autorizzate.

```Bash
# Configurazione GoPhish con SendGrid
# Sending Profile -> New Profile:
# Name: SendGrid-Relay
# SMTP From: phishing@attacker-lab.com
# Host: smtp.sendgrid.net:587
# Username: apikey
# Password: SG.xxxxxxxxx (API key SendGrid)
# -> Send Test Email
```

**Limitazioni:** i provider hanno policy anti-abuse che possono sospendere l'account se il contenuto viene classificato come phishing. Per testing: usare sempre Mailhog o un relay locale.

---

## Approccio 2: Server Dedicato (Postfix + OpenDKIM)

```Bash
# Installazione Postfix su Kali
sudo apt install postfix opendkim opendkim-tools
# Configurazione: selezionare "Internet Site"

# Generazione chiavi DKIM
sudo opendkim-genkey -s mail -d attacker-lab.com -D /etc/opendkim/keys/
```

```Bash
# Configurazione Postfix per DKIM signing
# /etc/postfix/main.cf
# milter_protocol = 6
# milter_default_action = accept
# smtpd_milters = inet:localhost:8891
# non_smtpd_milters = inet:localhost:8891
```

```Bash
# Record DNS da aggiungere al dominio:
# SPF:  TXT  attacker-lab.com      "v=spf1 ip4:<IP_SERVER> -all"
# DKIM: TXT  mail._domainkey.attacker-lab.com  "v=DKIM1; k=rsa; p=<CHIAVE_PUBBLICA>"
# rDNS: PTR  <IP_SERVER>           mail.attacker-lab.com
```

```Bash
# Test invio con swaks
swaks --to test@mailhog-lab.local --from noreply@attacker-lab.com --server 127.0.0.1:25 --header "Subject: Test SMTP" --body "Test delivery."
```

---

## Approccio 3: Testing Locale con Mailhog

```Bash
# Mailhog: fake SMTP server per test senza invio reale
# Installazione
go install github.com/mailhog/MailHog@latest
# oppure
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog

# Avvio
MailHog
# SMTP: 127.0.0.1:1025
# Web UI: http://127.0.0.1:8025
```

```Bash
# Configurazione GoPhish per Mailhog
# Sending Profile:
# Host: 127.0.0.1:1025
# (nessuna autenticazione necessaria)
# -> tutte le email sono visibili nella Web UI di Mailhog
```

---

## Domain Warming

Un dominio appena registrato ha reputation zero. Inviare immediatamente centinaia di email di phishing causa il blocco istantaneo. Il domain warming e il processo di costruzione graduale della reputation:

```
Settimana 1:  10-20 email/giorno verso account propri (Gmail, Outlook)
Settimana 2:  50-100 email/giorno con contenuto legittimo
Settimana 3:  200-500 email/giorno, mix di contenuto
Settimana 4+: volume target della campagna
```

**Nota:** per campagne di security awareness autorizzate, il domain warming e spesso non necessario se si usa il relay SMTP aziendale interno. Per Red Team engagement con dominio dedicato, il warming richiede 2-4 settimane di preparazione.

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Postfix` | SMTP server | CLI - Config | Relay SMTP dedicato con supporto DKIM |
| `OpenDKIM` | DKIM signer | CLI - Config | Firma crittografica DKIM per email in uscita |
| `Mailhog` | SMTP testing | Web UI | Test locale senza invio reale |
| `swaks` | SMTP testing | CLI | Test invio con header/body personalizzati |
| `MXToolbox` | Diagnostica | Web | Verifica SPF, DKIM, blacklist, deliverability |

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Resource Development | Acquire Infrastructure: Email Accounts | `T1583.002` | Configurazione SMTP relay per invio email di campagna |
| Resource Development | Stage Capabilities: Email Accounts | `T1608.003` | Domain warming e configurazione SPF/DKIM per deliverability |

---

> **Nota:** Le configurazioni documentate sono state testate in ambiente locale con Mailhog. Nessuna email e stata inviata a indirizzi reali o verso server di terze parti.
