> [English](README.en.md) | **Italiano**

# Target Profiling - OSINT-Based Dossier Construction

> - **Fase:** Social Engineering - Reconnaissance sul fattore umano
> - **Visibilita:** Zero - tutte le informazioni sono raccolte da fonti pubbliche (LinkedIn, social media, motori di ricerca, DNS) senza interazione diretta con il target
> - **Prerequisiti:** theHarvester, linkedin2username, SpiderFoot o Maltego; accesso a fonti OSINT pubbliche; risultati del modulo 01-recon (email, domini)
> - **Output:** SE-013 (dossier OSINT completo su target - severity Informativo); scheda target con ruolo, contatti, stack tech, trigger psicologici

- **Ambiente Operativo:** Kali Linux Purple (ricognizione)
- **Target:** Profilo aziendale simulato
- **Framework:** theHarvester, linkedin2username, ricerca manuale
- **Tecniche Documentate:** Email Harvesting, Social Media Profiling, Organigramma Reconstruction

---

## Executive Summary

Il target profiling trasforma dati OSINT grezzi (email, nomi, ruoli) in un dossier operativo che guida la personalizzazione della campagna di social engineering. La differenza tra un phishing generico (click rate 5%) e uno mirato (click rate 40%+) e interamente nella qualita del profiling: conoscere il nome del manager del target, il progetto su cui sta lavorando, o il tool che ha menzionato in un post LinkedIn permette di costruire pretesti quasi impossibili da riconoscere come fraudolenti.

---

## Target Profiling: Costruzione Dossier OSINT

**ID Finding:** `SE-013` | **Severity:** `Informativo`

### PoC - Fase 1: Email Harvesting

```Bash
theHarvester -d target-lab.com -b google,linkedin,bing,crtsh -l 500
```

```
[*] Emails found: 12
m.rossi@target-lab.com
l.bianchi@target-lab.com
a.verdi@target-lab.com
g.ferrari@target-lab.com
[... 8 ulteriori ...]

[*] Hosts found: 4
mail.target-lab.com: 93.184.216.34
vpn.target-lab.com: 93.184.216.35                          <-- VPN esposta
sharepoint.target-lab.com: 93.184.216.36                    <-- SharePoint esterno
```

### PoC - Fase 2: Profiling LinkedIn

```Bash
# Generazione lista username da LinkedIn
linkedin2username -c target-lab -s "Italy" -d target-lab.com
```

```
Mario Rossi - Chief Financial Officer                       <-- C-Level: target ad alto valore
Luca Bianchi - HR Manager                                   <-- HR: accesso a dati personali
Anna Verdi - IT System Administrator                        <-- IT: accesso privilegiato
Giovanni Ferrari - Sales Director                           <-- Sales: meno consapevole di security
```

### PoC - Fase 3: Deep Profiling (Ricerca Manuale)

```
=== DOSSIER TARGET: Mario Rossi (CFO) ===

IDENTITA:
  Nome:        Mario Rossi
  Ruolo:       Chief Financial Officer
  Email:       m.rossi@target-lab.com
  Manager:     CEO (nome da LinkedIn: Paolo Conti)
  Team:        Finance (4 persone)

STACK TECNOLOGICO:
  Email:       Microsoft 365 (da record MX: outlook.com)
  VPN:         Presente (vpn.target-lab.com)
  Collaboration: SharePoint (sharepoint.target-lab.com)

SOCIAL FOOTPRINT:
  LinkedIn:    Attivo, 500+ connessioni, post su fintech
  Twitter:     @mrossi_fin - tweet su economia, Serie A
  GitHub:      Nessun profilo trovato
  Facebook:    Profilo privato, foto profilo visibile

TRIGGER PSICOLOGICI CONSIGLIATI:
  Primario:    Autorita (email dal CEO Paolo Conti)
  Secondario:  Urgenza (scadenza fiscale, audit)
  Terziario:   Reciprocita (documento condiviso dal collega)

PRETESTO RACCOMANDATO:
  "Paolo Conti ha condiviso un documento riservato su SharePoint:
   Budget_Revisione_Q2_2026.xlsx - Richiesta approvazione urgente"
  Vettore: Email con link a landing page GoPhish (clone SharePoint)
```

### Remediation

- **Azione immediata:** sensibilizzazione del personale sulla quantita di informazioni personali esposte pubblicamente; revisione delle impostazioni di privacy sui profili social
- **Azione strutturale:** policy aziendale sulla presenza social media (cosa condividere e cosa no); training specifico per C-Level e ruoli con accesso a dati sensibili; rimozione di informazioni non necessarie dal sito aziendale (nomi completi, email dirette, organigramma dettagliato)
- **Verifica:** ripetizione del profiling dopo l'implementazione delle misure - la superficie informativa esposta deve essere ridotta

---

## Esperienza di Laboratorio

Il profiling e stato condotto su profili fittizi creati appositamente su LinkedIn e social media di test. Il dato piu significativo e stato il tempo necessario: un dossier operativo completo per un singolo target richiede circa 30-45 minuti di ricerca manuale. In un engagement con 20 target, il profiling puo richiedere 2-3 giorni di lavoro - un investimento che si ripaga interamente nel click rate della campagna.

La sfida principale e stata la correlazione delle informazioni tra piattaforme diverse. Il nome "Mario Rossi" su LinkedIn non e immediatamente collegabile al profilo Twitter "@mrossi_fin" senza un punto di connessione (email condivisa, foto profilo simile, interessi sovrapposti). Tool come Maltego automatizzano questa correlazione tramite grafi di relazione, ma il giudizio umano resta essenziale per validare i collegamenti.

---

## Analisi Teorica: OSINT come Moltiplicatore di Forza

Il valore del target profiling nel social engineering e quantificabile: secondo lo studio Verizon DBIR 2024, le campagne di spear-phishing mirate (basate su profiling) hanno un success rate 10x superiore rispetto al phishing generico. Il motivo e cognitivo: il cervello umano utilizza la familiarita come proxy per la fiducia. Un'email che menziona il nome del manager, il progetto corrente, o il tool utilizzato attiva circuiti di riconoscimento che bypassano l'analisi critica.

Il profiling OSINT opera sulla superficie informativa pubblica dell'organizzazione e dei suoi dipendenti. Ogni dato pubblicato - dal post LinkedIn alla pagina "Chi siamo" del sito aziendale - e un potenziale componente di un pretesto. La difesa non e eliminare la presenza online (impraticabile), ma educare il personale a riconoscere come le informazioni pubbliche possono essere weaponizzate e adottare un approccio di "minimum viable exposure".

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Descrizione dell'Azione |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Identity Information: Email Addresses | `T1589.002` | Raccolta email via theHarvester (SE-013) |
| Reconnaissance | Gather Victim Identity Information: Employee Names | `T1589.003` | Enumerazione nomi e ruoli via LinkedIn (SE-013) |
| Reconnaissance | Gather Victim Org Information: Identify Roles | `T1591.004` | Ricostruzione organigramma e catena di comando |
| Reconnaissance | Search Open Websites/Domains: Social Media | `T1593.001` | Profiling social media per trigger psicologici |
| Reconnaissance | Search Victim-Owned Websites | `T1594` | Analisi sito aziendale per stack tecnologico |

---

> **Nota:** Il profiling e stato condotto su profili fittizi. Nessuna informazione personale reale e stata raccolta senza autorizzazione.
