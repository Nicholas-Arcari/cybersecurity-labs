> [English](README.en.md) | **Italiano**

# Pretext scenarios - template scenari di social engineering

> - **Fase:** Social Engineering - Pretexting Design
> - **Visibilita:** N/A - questa sezione documenta la progettazione dei pretesti, non la loro esecuzione
> - **Prerequisiti:** Dossier target completato (da `target-profiling/`); conoscenza dei principi di Cialdini; familiarita con i framework di phishing (GoPhish, SET)
> - **Output:** Template di scenari pronti all'uso, calibrati per ruolo aziendale e contesto

- **Tecniche Documentate:** Pretexting Templates, Cialdini-Based Scenario Design, Role-Specific Calibration

---

## Executive summary

Questa sezione fornisce template di scenari di pretexting pronti all'uso per campagne di social engineering. Ogni template e calibrato per un ruolo aziendale specifico, sfrutta uno o piu principi di Cialdini, e include le variabili da personalizzare con i dati del target profiling. I template non sono mai da utilizzare "as-is": la personalizzazione contestuale e cio che distingue un phishing generico (facilmente riconoscibile) da uno mirato (quasi indistinguibile da comunicazione legittima).

---

## Template 1: IT department - password reset (autorita + urgenza)

**Target ideale:** qualsiasi dipendente
**Principio:** Autorita (IT department) + Urgenza (scadenza temporale)
**Click rate atteso:** 25-35% (senza training), 5-10% (post-training)

```
Subject: [AZIONE RICHIESTA] Reset password obbligatorio - Scadenza {{SCADENZA}}

Gentile {{NOME}},

A seguito dell'aggiornamento di sicurezza programmato dal team IT,
e necessario reimpostare la password del tuo account aziendale entro
{{SCADENZA}}.

Clicca sul link seguente per procedere:
{{URL}}

Se non completi questa operazione, il tuo account verra
temporaneamente sospeso fino alla verifica manuale.

IT Security Team
{{AZIENDA}}
```

**Variabili da profiling:** `{{NOME}}`, `{{AZIENDA}}`, `{{SCADENZA}}` (24-48 ore)
**Landing page:** clone del portale di autenticazione aziendale

---

## Template 2: CEO fraud - business email compromise (autorita + reciprocita)

**Target ideale:** CFO, Finance department, Executive Assistant
**Principio:** Autorita (CEO) + Reciprocita (richiesta personale)
**Click rate atteso:** 15-25% (l'assenza di link riduce i sospetti)

```
Subject: Richiesta riservata

{{NOME}},

Ho bisogno di un favore urgente e riservato. Sono in riunione
e non posso chiamare.

Puoi verificare se il bonifico verso {{FORNITORE}} e stato
processato? Il documento con i dettagli e qui:
{{URL}}

Non coinvolgere altri per ora, te ne parlo dopo la riunione.

{{NOME_CEO}}
Inviato da iPhone
```

**Variabili da profiling:** `{{NOME_CEO}}` (da LinkedIn), `{{FORNITORE}}` (da sito aziendale/fatture)
**Nota:** la firma "Inviato da iPhone" giustifica il tono informale e l'assenza di firma aziendale

---

## Template 3: Vendor/Fornitore - invoice update (reciprocita + coerenza)

**Target ideale:** Accounting, Procurement, Operations
**Principio:** Reciprocita (servizio gia utilizzato) + Coerenza (processo noto)
**Click rate atteso:** 20-30%

```
Subject: Aggiornamento coordinate bancarie - {{FORNITORE}}

Gentile {{NOME}},

Con la presente comunichiamo l'aggiornamento delle nostre
coordinate bancarie per i prossimi pagamenti.

Si prega di scaricare il documento aggiornato al link seguente
e procedere con l'aggiornamento nel vostro sistema:
{{URL}}

Per qualsiasi chiarimento, non esitate a contattarci.

Amministrazione
{{FORNITORE}}
```

**Variabili:** `{{FORNITORE}}` (fornitore reale dell'azienda, da LinkedIn/sito/fatture pubbliche)

---

## Template 4: HR - documento riservato (curiosita + riprova sociale)

**Target ideale:** tutti i dipendenti
**Principio:** Curiosita (documento riservato) + Riprova Sociale (gia condiviso)
**Click rate atteso:** 30-40% (la curiosita e un trigger potente)

```
Subject: Piano bonus 2026 - Documento riservato per il tuo team

{{NOME}},

In allegato trovi il piano bonus Q2 2026 per il dipartimento
{{DIPARTIMENTO}}. Il documento e stato gia condiviso con i
responsabili di area.

{{URL}}

Ti chiedo di non condividerlo al di fuori del team fino
alla comunicazione ufficiale.

{{NOME_HR}}
Human Resources
{{AZIENDA}}
```

**Nota:** "Non condividerlo" sfrutta l'effetto Streisand (la proibizione aumenta la curiosita)

---

## Template 5: SharePoint/OneDrive - document sharing (familiarita)

**Target ideale:** qualsiasi utente Microsoft 365
**Principio:** Familiarita (notifica standard Microsoft)
**Click rate atteso:** 35-45% (replica esatta di notifica legittima)

```
Subject: {{NOME_COLLEGA}} ha condiviso "{{NOME_DOCUMENTO}}" con te

{{NOME_COLLEGA}} ha condiviso un file con te.

{{NOME_DOCUMENTO}}
"Ho bisogno del tuo feedback su questo entro venerdi."

Apri in SharePoint
{{URL}}

Microsoft SharePoint
```

**Variabili:** `{{NOME_COLLEGA}}` (collega reale del target, da LinkedIn)
**Landing page:** clone della pagina di login Microsoft 365

---

## Matrice scenario per ruolo

| ruolo target | scenario primario | scenario secondario | principio dominante |
| :--- | :--- | :--- | :--- |
| c-level (ceo, cfo) | documento riservato board | vendor invoice update | autorita + esclusivita |
| finance / accounting | ceo fraud (bec) | vendor invoice update | autorita + urgenza |
| hr | candidatura da valutare | piano bonus riservato | reciprocita + curiosita |
| it / sviluppo | aggiornamento di sicurezza | github/jira notification | autorita + familiarita |
| sales / marketing | lead condiviso dal manager | evento/webinar invitation | reciprocita + riprova sociale |
| operativo / produzione | comunicazione aziendale | aggiornamento policy | autorita + coerenza |

---

## Anti-Pattern da evitare nei pretesti

| anti-pattern | problema | correzione |
| :--- | :--- | :--- |
| "hai vinto un premio!" | troppo generico, nessuno ci crede | usare contesto aziendale specifico |
| errori grammaticali intenzionali | i filtri moderni li rilevano | scrivere in italiano corretto |
| urgenza estrema ("5 minuti!") | attiva sospetto anziche compliance | urgenza moderata (24-48 ore) |
| link lungo e sospetto | visivamente riconoscibile | url shortener o dominio typosquatting |
| mittente esterno per comunicazione interna | incoerenza immediata | usare dominio spoofato o typosquatting |
| allegato .exe | bloccato da tutti i gateway | usare .html (smuggling), .iso, o link |

---

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| resource development | develop capabilities: malware | `T1587.001` | sviluppo template email e landing page per campagna |
| resource development | establish accounts: social media accounts | `T1585.001` | creazione profili falsi per impersonation (ceo fraud) |
| initial access | phishing: spearphishing link | `T1566.002` | template email con link a landing page personalizzata |
| initial access | phishing: spearphishing attachment | `T1566.001` | template email con allegato payload mascherato |

---

> **Nota:** I template sono forniti a scopo educativo e per campagne di security awareness autorizzate. L'utilizzo di tecniche di social engineering senza autorizzazione esplicita e illegale.
