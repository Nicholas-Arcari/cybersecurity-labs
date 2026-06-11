> [English](README.en.md) | **Italiano**

# 05 - Pretexting Methodology

> - **Fase:** Social Engineering - Pretexting & Target Profiling (dimensione umana dell'attacco)
> - **Visibilita:** Zero (ricerca OSINT passiva) / Bassa (interazione telefonica/email con pretesto)
> - **Prerequisiti:** Completamento modulo 01-recon (OSINT passivo); accesso a fonti pubbliche (LinkedIn, social media, sito aziendale target); comprensione dei principi di influenza psicologica
> - **Output:** Finding SE-013 (dossier target completo via OSINT - severity Informativo); template scenari di pretexting pronti all'uso; metodologia di target profiling riproducibile

---

## Introduzione

Il pretexting e la dimensione umana e psicologica del social engineering - quella che distingue un penetration tester senior da un operatore di tool. Mentre le sezioni precedenti documentano il "come" tecnico (quale tool, quale payload, quale infrastruttura), questa sezione documenta il "perche" e il "chi": come scegliere il target giusto, come costruire una narrativa credibile, e come sfruttare i principi psicologici di influenza per massimizzare la probabilita di successo.

In un engagement professionale, la qualita del pretexting determina direttamente il click rate e il success rate della campagna. Un'email tecnicamente perfetta con un pretesto debole ("Hai vinto un premio!") ha un click rate del 2-5%. La stessa email con un pretesto contestuale ("Il tuo manager Marco ha condiviso un documento su SharePoint") raggiunge il 30-50%.

La sezione documenta due competenze complementari:

1. **Target Profiling (SE-013):** raccolta e aggregazione di informazioni OSINT per costruire un dossier sul target. Ruolo aziendale, contatti, stack tecnologico, abitudini social media - ogni dato diventa un elemento del pretesto.

2. **Pretext Scenarios:** template di scenari di pretexting basati sui principi di Cialdini, calibrati per ruolo aziendale e contesto. Dalla classica "email dall'IT department" al sofisticato "CEO fraud" e "vendor impersonation".

---

## Struttura della cartella

```
05-pretexting-methodology/
+-- target-profiling/     # OSINT aggregation per dossier target - SE-013
+-- pretext-scenarios/    # Template scenari calibrati per ruolo e contesto
```

---

## `target-profiling/` - OSINT-Based Dossier Construction

**ID Finding:** `SE-013` | **Severity:** `Informativo` (dossier completo su target via fonti pubbliche)

### Contesto operativo

Il target profiling e la fase di raccolta informazioni focalizzata sulla persona (non sul sistema). L'obiettivo e costruire un dossier che risponda a cinque domande: chi e il target (ruolo, responsabilita), con chi interagisce (manager, colleghi, fornitori), quale stack tecnologico usa, quali sono le sue abitudini digitali (social media, post, commenti), e quali sono i trigger psicologici piu efficaci (urgenza, autorita, paura).

### Comandi principali

```Bash
# OSINT email: theHarvester per raccolta email aziendali
theHarvester -d target-lab.com -b google,linkedin,bing -l 200
```

```
[*] Emails found:
m.rossi@target-lab.com                                      <-- target primario (CFO)
l.bianchi@target-lab.com                                    <-- target secondario (HR)
a.verdi@target-lab.com                                      <-- target terziario (IT)
info@target-lab.com                                         <-- generico
```

```Bash
# LinkedIn OSINT: enumerazione ruoli e organigramma
# (ricerca manuale o con linkedin2username)
linkedin2username -c target-lab -s "Italy"
```

```Bash
# Social media footprint
# Ricerca manuale su:
# - LinkedIn: ruolo, competenze, connessioni, post recenti
# - Twitter/X: opinioni, interessi, tecnologie menzionate
# - GitHub: progetti, linguaggi, email nei commit
# - Facebook/Instagram: informazioni personali, geolocalizzazione
```

---

## `pretext-scenarios/` - Template Scenari di Pretexting

### Contesto operativo

I template di pretexting sono scenari pre-costruiti calibrati per ruolo aziendale e principio psicologico. Ogni template include: il pretesto narrativo, il principio di Cialdini sfruttato, il vettore di delivery consigliato, e le variabili da personalizzare con i dati del target profiling.

---

## I Sei Principi di Cialdini nel Social Engineering

| Principio | Definizione | Applicazione SE |
| :--- | :--- | :--- |
| **Autorita** | Tendiamo a obbedire a figure di autorita | Email dal CEO, dall'IT, dal fornitore |
| **Urgenza/Scarsita** | Agiamo impulsivamente sotto pressione temporale | "Entro 24 ore", "Account sara sospeso" |
| **Reciprocita** | Ci sentiamo obbligati a ricambiare un favore | "Ti ho inviato il report, puoi confermare?" |
| **Riprova Sociale** | Seguiamo il comportamento degli altri | "Il 90% dei colleghi ha gia completato" |
| **Impegno/Coerenza** | Manteniamo coerenza con azioni precedenti | Follow-up a una richiesta gia accettata |
| **Simpatia** | Siamo influenzati da persone che ci piacciono | Tono amichevole, interessi comuni |

---

## Flusso operativo consigliato

```
[1] Identificazione target (da 01-recon OSINT)
     +-- Email aziendali
     +-- Organigramma: chi e il manager, chi sono i colleghi
     +-- Ruolo e responsabilita
              |
              v
[2] Deep profiling
     +-- LinkedIn: competenze, post recenti, connessioni
     +-- Social media: interessi, abitudini, geolocalizzazione
     +-- GitHub/siti personali: stack tech, email nei commit
              |
              v
[3] Costruzione dossier
     +-- Scheda target: nome, ruolo, email, manager, interessi
     +-- Trigger psicologici: quale principio Cialdini e piu efficace
     +-- Vettore consigliato: email, telefono, di persona
              |
              v
[4] Selezione pretesto
     +-- Ruolo IT/Tech -> "Aggiornamento di sicurezza" (Autorita)
     +-- Ruolo Finance -> "Fattura in sospeso" (Urgenza)
     +-- Ruolo HR -> "Candidatura da valutare" (Reciprocita)
     +-- C-Level -> "CEO fraud" (Autorita + Urgenza)
              |
              v
[5] Personalizzazione e Delivery
     +-- Inserimento dettagli contestuali dal dossier
     +-- Scelta framework (GoPhish, SET, Evilginx)
     +-- Lancio campagna
```

---

## Tool di riferimento

| Tool | Tipo | Tecnica/Accesso | Caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `theHarvester` | OSINT email | CLI | Raccolta email e sottodomini da fonti pubbliche |
| `linkedin2username` | OSINT sociale | CLI - Python | Generazione username da profili LinkedIn |
| `Maltego` | OSINT aggregator | GUI | Visualizzazione relazioni tra entita (persone, email, domini) |
| `SpiderFoot` | OSINT automation | Web UI | Raccolta automatizzata OSINT da 200+ fonti |
| `Recon-ng` | OSINT framework | CLI | Framework modulare per ricognizione con moduli per social media |

> **Tool moderno consigliato:** `SpiderFoot HX` (hosted) o `SpiderFoot` (self-hosted) per automazione OSINT completa. `Maltego CE` per visualizzazione grafica delle relazioni. Per LinkedIn, `linkedin2username` combinato con ricerca manuale per contesto qualitativo.

---

## Registro Finding

| ID | Descrizione | Severity | CVSS | Sottocartella |
| :--- | :--- | :---: | :---: | :--- |
| `SE-013` | Target profiling OSINT: dossier completo su target (ruolo, contatti, stack tech, abitudini social) costruito interamente da fonti pubbliche | `Informativo` | 2.1 | `target-profiling/` |

---

## Mappatura MITRE ATT&CK

| Tattica | Tecnica | ID MITRE | Finding Correlato |
| :--- | :--- | :--- | :--- |
| Reconnaissance | Gather Victim Identity Information: Email Addresses | `T1589.002` | SE-013 |
| Reconnaissance | Gather Victim Identity Information: Employee Names | `T1589.003` | SE-013 |
| Reconnaissance | Gather Victim Org Information: Identify Roles | `T1591.004` | SE-013 |
| Reconnaissance | Gather Victim Org Information: Identify Business Tempo | `T1591.003` | SE-013 |
| Reconnaissance | Search Open Websites/Domains: Social Media | `T1593.001` | SE-013 |
| Reconnaissance | Search Victim-Owned Websites | `T1594` | SE-013 |

---

> **Nota:** Le attivita di target profiling documentate sono state condotte su profili fittizi creati ad hoc. Nessuna informazione personale reale e stata raccolta o utilizzata senza autorizzazione.
