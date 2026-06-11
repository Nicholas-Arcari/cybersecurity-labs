> [English](README.en.md) | **Italiano**

# SPF/DKIM/DMARC - Email Authentication Audit

> - **Fase:** Social Engineering - Email Infrastructure Reconnaissance
> - **Visibilita:** Zero - l'audit si basa su query DNS pubbliche (record TXT), nessun pacchetto inviato al mail server del target, nessun log generato
> - **Prerequisiti:** Accesso a strumenti di query DNS (dig, nslookup); spoofcheck (BishopFox) per analisi automatizzata; conoscenza dei meccanismi SPF, DKIM e DMARC
> - **Output:** SE-011 (DMARC policy `none` - spoofing email possibile - severity Medio)

- **Ambiente Operativo:** Kali Linux Purple (Attaccante)
- **Target:** Dominio email del target simulato (target-lab.com)
- **Framework:** dig, spoofcheck, dmarcian.com (reference)
- **Tecniche Documentate:** DNS TXT Record Analysis, SPF Validation, DMARC Policy Assessment

---

## Executive Summary

SPF (Sender Policy Framework), DKIM (DomainKeys Identified Mail) e DMARC (Domain-based Message Authentication, Reporting and Conformance) sono i tre pilastri dell'autenticazione email. La loro configurazione corretta impedisce a un attaccante di inviare email spoofate che appaiono provenire dal dominio del target. La loro misconfiguration - in particolare DMARC con policy `none` - e uno dei finding piu comuni e impattanti in un assessment di social engineering: permette all'attaccante di impersonare qualsiasi indirizzo email del dominio senza che il server destinatario blocchi il messaggio.

Il laboratorio ha documentato l'audit completo della configurazione email di un dominio target simulato, identificando una catena di debolezze: SPF con softfail (`~all` anziche `-all`), DKIM non verificato, e DMARC con policy `none`. Questa combinazione permette lo spoofing completo del dominio.

---

## SPF/DKIM/DMARC Audit: Spoofing Assessment

**ID Finding:** `SE-011` | **Severity:** `Medio`

### PoC - Fase 1: Verifica SPF

```Bash
dig +short TXT target-lab.com | grep spf
```

```
"v=spf1 include:_spf.google.com ~all"
```

**Analisi:** Il record SPF e presente ma utilizza `~all` (softfail) anziche `-all` (hardfail). Con softfail, le email provenienti da IP non autorizzati vengono marcate come sospette ma non rifiutate. In assenza di DMARC enforcement, il softfail non ha alcun effetto pratico.

### PoC - Fase 2: Verifica DKIM

```Bash
# DKIM richiede il selettore specifico (spesso "google", "mail", "selector1")
dig +short TXT google._domainkey.target-lab.com
dig +short TXT mail._domainkey.target-lab.com
dig +short TXT selector1._domainkey.target-lab.com
```

```
# Nessun record trovato per i selettori comuni                 <-- DKIM non configurato o selettore non standard
```

### PoC - Fase 3: Verifica DMARC

```Bash
dig +short TXT _dmarc.target-lab.com
```

```
"v=DMARC1; p=none; rua=mailto:dmarc@target-lab.com"            <-- SE-011: policy "none"
```

**Analisi:** `p=none` significa che il dominio istruisce i server destinatari a non intraprendere alcuna azione sulle email che falliscono SPF e DKIM. L'unico effetto e l'invio di report aggregati all'indirizzo RUA - utili per il monitoraggio ma inutili come difesa.

### PoC - Fase 4: Verifica Automatizzata con spoofcheck

```Bash
python3 spoofcheck.py target-lab.com
```

```
[+] target-lab.com
[+] SPF record found!
[-] SPF record uses ~all (softfail) - not strict enough
[+] DMARC record found!
[-] DMARC policy is set to 'none' - NOT enforced               <-- SE-011
[!] DOMAIN IS SPOOFABLE                                         <-- conclusione: spoofing possibile
```

### PoC - Fase 5: Verifica Pratica di Spoofing

```Bash
# Test di invio email spoofata (verso Mailhog di test, NON verso server reali)
swaks --to victim@test-lab.local \
  --from ceo@target-lab.com \
  --server 127.0.0.1:25 \
  --header "Subject: Richiesta urgente dal CEO" \
  --header "Reply-To: attacker@evil.com" \
  --body "Puoi effettuare un bonifico urgente? Dettagli nel prossimo messaggio."
```

```
=== Trying 127.0.0.1:25...
=== Connected to 127.0.0.1.
<-  250 Ok: queued                                              <-- email accettata senza errori
```

### Remediation

- **Azione immediata:** impostare DMARC a `p=quarantine; pct=100` come step intermedio
- **Azione strutturale:** SPF: cambiare `~all` in `-all` (hardfail); DKIM: configurare firma DKIM su tutti i server di invio autorizzati; DMARC: migrare a `p=reject` dopo 30 giorni di monitoraggio report RUA per verificare che nessun servizio legittimo venga bloccato; abilitare report forensici RUF per analisi dettagliata dei tentativi di spoofing
- **Verifica:** `dig +short TXT _dmarc.target.com` restituisce `p=reject`; invio email spoofata di test viene rifiutata con errore 550

---

## Esperienza di Laboratorio

L'audit e stato eseguito interamente tramite query DNS pubbliche, senza alcuna interazione diretta con il mail server del target. Questo aspetto e fondamentale: l'analisi SPF/DKIM/DMARC e completamente passiva e non genera log sul sistema target, rendendola una delle prime attivita di reconnaissance in un engagement di social engineering.

La difficolta principale e stata la verifica DKIM: a differenza di SPF e DMARC che hanno record DNS prevedibili, DKIM richiede la conoscenza del selettore specifico utilizzato dal dominio. I selettori piu comuni (`google`, `mail`, `selector1`, `selector2`, `s1`, `s2`) sono stati testati senza risultati. In un engagement reale, il selettore puo essere estratto dagli header di email legittime provenienti dal dominio target (header `DKIM-Signature: s=<selettore>`).

Un'osservazione critica: anche con SPF `-all` e DKIM attivo, senza DMARC `reject` lo spoofing puo comunque avere successo con alcuni provider email che non implementano controlli rigorosi. DMARC `reject` e l'unica configurazione che garantisce il blocco sistematico delle email spoofate.

---

## Analisi Teorica: Il Triangolo SPF/DKIM/DMARC

**SPF** definisce quali server IP sono autorizzati a inviare email per un dominio. Il record DNS TXT contiene una lista di IP/range/include autorizzati e un qualificatore finale: `-all` (hardfail: rifiuta tutto il resto), `~all` (softfail: marca come sospetto), `?all` (neutral: nessuna indicazione). Il problema di SPF da solo: opera sull'envelope sender (MAIL FROM), non sull'header From visualizzato dall'utente. Un attaccante puo utilizzare un envelope sender diverso e mostrare comunque `ceo@target.com` nell'header.

**DKIM** aggiunge una firma crittografica all'email che permette al destinatario di verificare che il messaggio non sia stato alterato in transito e che provenga effettivamente dal dominio dichiarato. La firma e basata su coppie di chiavi RSA: la chiave privata firma sul server di invio, la chiave pubblica e nel record DNS per la verifica.

**DMARC** e il collante che rende SPF e DKIM effettivamente utili come difesa anti-spoofing. DMARC introduce il concetto di "alignment": l'header From deve corrispondere al dominio verificato da SPF o DKIM. Senza DMARC, un attaccante puo inviare email che passano SPF (con il proprio dominio come envelope sender) ma mostrano un header From arbitrario. DMARC con policy `reject` chiude questa lacuna.

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Network Information: DNS | `T1590.002` | Query DNS TXT per record SPF, DKIM, DMARC del dominio target |
| Reconnaissance | Search Open Technical Databases: DNS/Passive DNS | `T1596.001` | Analisi automatizzata con spoofcheck (SE-011) |
| Resource Development | Acquire Infrastructure: Email Accounts | `T1583.002` | La misconfiguration DMARC abilita l'uso del dominio target per spoofing |

---

> **Nota:** L'audit e stato condotto su un dominio di test creato ad hoc. Nessun audit e stato effettuato su domini di terze parti senza autorizzazione.
