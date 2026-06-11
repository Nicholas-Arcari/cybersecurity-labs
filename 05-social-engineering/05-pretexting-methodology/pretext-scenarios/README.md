> [English](README.en.md) | **Italiano**

# Pretext Scenarios - Template Scenari di Social Engineering

> - **Fase:** Social Engineering - Pretexting Design
> - **Visibilita:** N/A - questa sezione documenta la progettazione dei pretesti, non la loro esecuzione
> - **Prerequisiti:** Dossier target completato (da `target-profiling/`); conoscenza dei principi di Cialdini; familiarita con i framework di phishing (GoPhish, SET)
> - **Output:** Template di scenari pronti all'uso, calibrati per ruolo aziendale e contesto

- **Tecniche Documentate:** Pretexting Templates, Cialdini-Based Scenario Design, Role-Specific Calibration

---

## Executive Summary

Questa sezione fornisce template di scenari di pretexting pronti all'uso per campagne di social engineering. Ogni template e calibrato per un ruolo aziendale specifico, sfrutta uno o piu principi di Cialdini, e include le variabili da personalizzare con i dati del target profiling. I template non sono mai da utilizzare "as-is": la personalizzazione contestuale e cio che distingue un phishing generico (facilmente riconoscibile) da uno mirato (quasi indistinguibile da comunicazione legittima).

---

## Template 1: IT Department - Password Reset (Autorita + Urgenza)

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

## Template 2: CEO Fraud - Business Email Compromise (Autorita + Reciprocita)

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

## Template 3: Vendor/Fornitore - Invoice Update (Reciprocita + Coerenza)

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

## Template 4: HR - Documento Riservato (Curiosita + Riprova Sociale)

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

## Template 5: SharePoint/OneDrive - Document Sharing (Familiarita)

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

## Matrice Scenario per Ruolo

| Ruolo Target | Scenario Primario | Scenario Secondario | Principio Dominante |
| :--- | :--- | :--- | :--- |
| C-Level (CEO, CFO) | Documento riservato board | Vendor invoice update | Autorita + Esclusivita |
| Finance / Accounting | CEO fraud (BEC) | Vendor invoice update | Autorita + Urgenza |
| HR | Candidatura da valutare | Piano bonus riservato | Reciprocita + Curiosita |
| IT / Sviluppo | Aggiornamento di sicurezza | GitHub/Jira notification | Autorita + Familiarita |
| Sales / Marketing | Lead condiviso dal manager | Evento/webinar invitation | Reciprocita + Riprova Sociale |
| Operativo / Produzione | Comunicazione aziendale | Aggiornamento policy | Autorita + Coerenza |

---

## Anti-Pattern da Evitare nei Pretesti

| Anti-Pattern | Problema | Correzione |
| :--- | :--- | :--- |
| "Hai vinto un premio!" | Troppo generico, nessuno ci crede | Usare contesto aziendale specifico |
| Errori grammaticali intenzionali | I filtri moderni li rilevano | Scrivere in italiano corretto |
| Urgenza estrema ("5 minuti!") | Attiva sospetto anziche compliance | Urgenza moderata (24-48 ore) |
| Link lungo e sospetto | Visivamente riconoscibile | URL shortener o dominio typosquatting |
| Mittente esterno per comunicazione interna | Incoerenza immediata | Usare dominio spoofato o typosquatting |
| Allegato .exe | Bloccato da tutti i gateway | Usare .html (smuggling), .iso, o link |

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Resource Development | Develop Capabilities: Malware | `T1587.001` | Sviluppo template email e landing page per campagna |
| Resource Development | Establish Accounts: Social Media Accounts | `T1585.001` | Creazione profili falsi per impersonation (CEO fraud) |
| Initial Access | Phishing: Spearphishing Link | `T1566.002` | Template email con link a landing page personalizzata |
| Initial Access | Phishing: Spearphishing Attachment | `T1566.001` | Template email con allegato payload mascherato |

---

> **Nota:** I template sono forniti a scopo educativo e per campagne di security awareness autorizzate. L'utilizzo di tecniche di social engineering senza autorizzazione esplicita e illegale.
