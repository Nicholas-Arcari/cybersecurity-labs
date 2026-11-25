> [English](README.en.md) | **Italiano**

# Container image scanning - CVE nelle immagini Docker

> - **Fase:** Cloud Security - Container Security (Supply Chain / Vulnerability Management)
> - **Categoria:** Difensivo - analisi statica delle immagini prima del deploy
> - **Prerequisiti:** Immagini Docker da analizzare; Trivy/Grype/Dive; integrazione nella pipeline CI/CD (idealmente)
> - **Output:** Finding CLOUD-005; inventario delle vulnerabilita note nelle immagini; base per il patching e il blocco dei deploy vulnerabili

- **Ambiente Operativo:** Workstation/CI, Docker, Trivy
- **Tool principali:** Trivy, Grype, Clair, Dive

---

## Executive summary

Un'immagine Docker non e un artefatto atomico: e una pila di layer che include un sistema operativo di base, librerie, dipendenze applicative e il codice. Ognuno di questi strati puo contenere vulnerabilita note (CVE), e un'immagine "tirata giu" da un registry - anche una ufficiale - eredita tutte le vulnerabilita dei suoi componenti. L'image scanning e l'analisi statica che le individua prima che l'immagine venga deployata in produzione.

Il finding CLOUD-005 documenta la scansione delle immagini con Trivy, lo standard di fatto: uno scanner che confronta i pacchetti presenti in ogni layer con i database di vulnerabilita note e produce un inventario dei CVE, ordinato per severita. E un controllo di **supply chain security**: garantisce che cio che si mette in produzione non porti con se vulnerabilita conosciute e correggibili.

Il valore e preventivo e si integra nella pipeline CI/CD: una scansione automatica a ogni build blocca il deploy delle immagini con vulnerabilita critiche, spostando la sicurezza "a sinistra" (shift-left) - dal runtime, dove il problema e costoso, alla build, dove e economico correggerlo.

---

## Struttura della cartella

```
image-scanning/
+-- README.md      # questo file: scansione CVE delle immagini (CLOUD-005)
+-- img/           # report Trivy e analisi dei layer con Dive
```

---

## Scansione delle immagini con trivy

**ID Finding:** `CLOUD-005` | **Severity:** `Medio` (rilevamento di vulnerabilita note nelle immagini prima del deploy; la severita reale dipende dai CVE trovati)

### Contesto operativo

Trivy scansiona un'immagine strato per strato, identifica i pacchetti installati (OS e applicativi) e li confronta con i database CVE. Il risultato e un elenco di vulnerabilita con severita, versione affetta e versione che le corregge - una lista d'azione per il patching.

### PoC - scansione di un'immagine

```Bash
# Scansione completa di un'immagine (CVE OS + dipendenze applicative)
trivy image nomeimmagine:tag
```

```
nomeimmagine:tag (debian 11.3)
Total: 47 (UNKNOWN: 0, LOW: 12, MEDIUM: 23, HIGH: 10, CRITICAL: 2)

LIBRARY        VULNERABILITY   SEVERITY   INSTALLED   FIXED       TITLE
openssl        CVE-2022-....   CRITICAL   1.1.1k      1.1.1n      OpenSSL infinite loop   <-- (CLOUD-005)
libc6          CVE-2021-....   HIGH       2.31        2.31-13     glibc buffer overflow
```

### PoC - analisi dei layer (dive)

```Bash
# Dive: analizza i layer per capire dove sono introdotte le vulnerabilita/lo spreco
dive nomeimmagine:tag
```

```
# Dive mostra layer per layer cosa aggiunge peso e cosa introduce pacchetti vulnerabili
# -> spesso l'immagine di base obsoleta e la causa: aggiornarla risolve molti CVE
```

### PoC - integrazione CI/CD (shift-left)

```Bash
# In pipeline: fallisce la build se ci sono CVE CRITICAL (blocca il deploy vulnerabile)
trivy image --exit-code 1 --severity CRITICAL nomeimmagine:tag
```

```
[!] exit code 1: CVE CRITICAL presenti -> build bloccata   <-- deploy vulnerabile impedito (CLOUD-005)
```

### Remediation e operativita

- **Immagini di base minimali e aggiornate:** partire da immagini piccole (distroless, alpine) e aggiornate riduce drasticamente la superficie; molti CVE spariscono aggiornando il base layer
- **Patching guidato dal fixed version:** Trivy indica la versione che corregge; aggiornare le dipendenze a quella versione
- **Shift-left in CI/CD:** scansione automatica a ogni build, con blocco sui CVE critici; la sicurezza va spostata alla build, non lasciata al runtime
- **Scansione del registry:** scansionare periodicamente anche le immagini gia nel registry (nuovi CVE emergono dopo la build); Trivy/Grype supportano la scansione continua

---

## Esperienza di laboratorio

La lezione piu immediata e stata quanto vulnerabilita porti un'immagine "innocente". Un'immagine basata su una versione non aggiornata di Debian, scaricata senza pensarci, portava con se decine di CVE ereditati dal sistema di base - nessuno introdotto dal mio codice, tutti dalle fondamenta. Questo ha reso concreto il concetto di supply chain: la sicurezza di un container non e solo il codice che ci metto, ma tutto cio che eredito dai layer sottostanti.

Dive ha aggiunto la dimensione della causa. Vedere layer per layer da dove venivano i pacchetti vulnerabili ha chiarito che la contromisura piu efficace non e patchare singoli pacchetti ma partire da un'immagine di base migliore: passando a un'immagine minimale e aggiornata, la maggior parte dei CVE spariva in un colpo. La scelta del base layer e la decisione di sicurezza piu impattante nella costruzione di un'immagine.

L'integrazione in CI/CD ha chiuso il cerchio del valore preventivo. Un `trivy image --exit-code 1` in pipeline trasforma la scansione da attivita occasionale a controllo automatico: nessuna immagine con CVE critici raggiunge la produzione, senza dipendere dalla diligenza manuale. E l'essenza dello shift-left: rendere la sicurezza un passaggio automatico della build, non un controllo successivo.

---

## Analisi teorica: supply chain e la sicurezza ereditata

Un container incarna il principio che la sicurezza si eredita lungo la catena di fornitura. L'immagine finale e la somma di componenti che l'autore non ha scritto: il sistema di base, le librerie di sistema, le dipendenze del linguaggio, i pacchetti di terze parti. Ognuno e un potenziale vettore, e la sicurezza dell'insieme non e migliore di quella del suo componente piu vulnerabile. Il codice applicativo, spesso l'unico su cui l'autore si concentra, e frequentemente la parte piu piccola della superficie.

Questo ribalta il focus della sicurezza dallo scrivere codice sicuro al gestire dipendenze sicure. La maggior parte delle vulnerabilita di un'immagine non e nel codice ma nelle sue fondamenta ereditate, e la loro gestione e un problema di inventario e aggiornamento, non di programmazione. L'image scanning e lo strumento che rende visibile questa superficie ereditata, altrimenti invisibile: senza scansione, le vulnerabilita dei layer sottostanti sono presenti ma ignote.

Il principio dello shift-left riflette un'economia della correzione: un CVE trovato alla build costa un aggiornamento di versione; lo stesso CVE sfruttato in produzione costa un incidente. Spostare il controllo il piu a monte possibile (build invece di runtime) minimizza il costo della correzione e massimizza la probabilita che avvenga. La sicurezza della supply chain non si aggiunge alla fine, si integra all'inizio - ed e per questo che l'image scanning appartiene alla pipeline, non al SOC.

---

## Tool di riferimento

| tool | tipo | ruolo | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Trivy` | vulnerability scanner | difensivo | scansione cve di immagini, filesystem, iac (standard) |
| `Grype` | vulnerability scanner | difensivo | alternativa a trivy, integrazione con sbom (syft) |
| `Clair` | vulnerability scanner | difensivo | scansione statica integrata nei registry |
| `Dive` | layer analysis | analisi | ispezione dei layer, ottimizzazione e origine dei pacchetti |
| `Docker Scout` | vulnerability scanner | difensivo | scanner integrato in docker |

> **Tool moderno consigliato:** `Trivy` (Aqua Security) e lo standard di fatto: leggero, veloce, scansiona immagini, filesystem, repository e IaC, e si integra in ogni pipeline CI/CD. `Dive` come complemento per capire l'origine dei problemi nei layer. Vedere anche `../../Tooling/`.

---

## Mappatura MITRE ATT&CK

| tattica (prevenuta) | tecnica | id mitre | ruolo del controllo |
| :--- | :--- | :--- | :--- |
| initial access | supply chain compromise | `T1195` | rilevamento di componenti vulnerabili nelle immagini (CLOUD-005) |
| execution | exploitation for client execution | `T1203` | prevenzione dello sfruttamento di cve noti in container |
| initial access | exploit public-facing application | `T1190` | riduzione della superficie sfruttabile nei container esposti |

| contromisura difensiva (d3fend) | id d3fend | applicazione |
| :--- | :--- | :--- |
| application vulnerability assessment | `D3-AVA` | scansione delle immagini per vulnerabilita note |
| software update | `D3-SU` | patching guidato dalle versioni corrette indicate da trivy |

---

> **Nota:** Tutte le attivita documentate sono state condotte su immagini e ambienti di laboratorio di proprieta dell'autore. L'image scanning e un controllo difensivo e non intrusivo. Le tecniche sono documentate a scopo educativo e di difesa in contesto autorizzato.
