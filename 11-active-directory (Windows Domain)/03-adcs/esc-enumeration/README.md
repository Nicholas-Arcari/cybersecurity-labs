> [English](README.en.md) | **Italiano**

# Enumerazione AD CS: trovare le misconfigurazioni ESC

> - **Fase:** Discovery (dominio Active Directory, servizi di certificazione)
> - **Visibilita:** Bassa-Media - query LDAP sul contenitore di configurazione della PKI e richieste all'interfaccia della CA
> - **Prerequisiti:** un account di dominio valido; presenza di AD CS nella foresta
> - **Tecnica:** `AD CS enumeration` | **Severity tipica:** `Informativo` (ma rivela finding di severity alta) | **Finding ID:** da assegnare in lab (metodologia)

- Natura del documento: metodologia. Output illustrativi, non da lab specifico.
- Obiettivo: individuare le Certificate Authority, i template pubblicati e le loro impostazioni, classificando le misconfigurazioni secondo la tassonomia ESC prima di tentare qualunque abuso.

---

## Executive summary

Prima di sfruttare AD CS occorre sapere cosa e esposto. L'enumerazione raccoglie le CA della foresta, i
template di certificato pubblicati e le loro proprieta chiave: chi puo richiedere (enrollment rights), se il
richiedente puo specificare il soggetto (Subject Alternative Name, SAN) arbitrario, quali Extended Key Usage
sono presenti (in particolare Client Authentication), e se e richiesta l'approvazione del manager. La
combinazione di queste proprieta determina quale scenario ESC (ESC1-ESC16 e oltre) e applicabile. Certipy
automatizza questa raccolta e segnala le vulnerabilita note.

## Contesto operativo (perche, prima del come)

L'enumerazione AD CS e il passo che trasforma "c'e una PKI" in "ecco il vettore specifico". Senza di essa si
procederebbe alla cieca; con essa si sa esattamente quale template e sfruttabile e con quale tecnica (ESC1
se un template consente SAN arbitrario a utenti di dominio, ESC8 se c'e il Web Enrollment HTTP, e cosi via).
E un passo a basso rischio e alto valore, da eseguire appena si rileva la presenza di una CA.

## Esecuzione / comandi

```bash
# Certipy: enumerazione completa di CA e template, con segnalazione delle vulnerabilita ESC
certipy find -u utente@corp.local -p 'Password123' -dc-ip 10.10.10.10 -stdout -vulnerable
```

Output illustrativo (rappresentativo, ridotto):

```
Certificate Templates
  0
    Template Name              : UserAuth
    Client Authentication      : True
    Enrollee Supplies Subject  : True          <-- SAN arbitrario: candidato ESC1
    Enrollment Rights          : CORP\Domain Users
  [!] Vulnerabilities
        ESC1 : 'CORP\\Domain Users' can enroll and supply arbitrary SAN
```

## Analisi dei risultati

L'output classifica i template secondo gli scenari ESC. La pagina di enumerazione e in se `Informativo`, ma
cio che rivela puo essere `Critico`: un template ESC1 enrollabile da Domain Users significa che qualunque
utente puo ottenere un certificato per autenticarsi come Domain Admin. Il finding reale vive nella tecnica
specifica (es. [ESC1](<../esc1-template-abuse/README.md>)), ma l'enumerazione e cio che lo rende possibile e
va documentata come punto di partenza.

### Analisi teorica

AD CS pubblica la propria configurazione (CA, template) nel contesto di configurazione di AD, leggibile dagli
utenti di dominio. Questo e coerente con il modello di AD (la struttura non e segreta), ma espone tutte le
informazioni necessarie a individuare le misconfigurazioni. La tassonomia ESC (Schroeder, Christensen 2021;
vedi [THEORETICAL-FOUNDATIONS](<../../THEORETICAL-FOUNDATIONS.md>), sez. 3.4) formalizza quali combinazioni di
proprieta rendono un template o un endpoint abusabile: l'enumerazione e l'applicazione pratica di quella
tassonomia ai dati reali della PKI.

## Remediation (blue team)

**Rilevamento.** Query LDAP mirate al contenitore della PKI da account inattesi; esecuzione di tool di
enumerazione AD CS (pattern di richieste caratteristico).

**Hardening.** Eseguire periodicamente l'enumerazione come blue team (Certipy, PSPKIAudit) per scoprire e
correggere i template vulnerabili prima di un attaccante; rimuovere i template non utilizzati; restringere
gli enrollment rights; disattivare "Enrollee Supplies Subject" dove non necessario.

## Tool di riferimento

| tool | tipo | tecnica/accesso | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Certipy` | ad cs toolkit | cli - attivo | enumerazione e classificazione esc (`find -vulnerable`) |
| `Certify` | .net ad cs tool | cli - attivo | enumerazione ad cs da host windows |
| `PSPKIAudit` | powershell audit | cli - attivo | audit della pki lato blue team |

## Note di metodologia

In lab reale documentare: CA presenti, template pubblicati e, per ciascuno, le proprieta rilevanti; la
classificazione ESC risultante guida la scelta della tecnica di abuso.

## Mappatura MITRE ATT&CK

| tattica | tecnica | id mitre | descrizione dell'azione |
| :--- | :--- | :--- | :--- |
| discovery | account discovery: domain account | `T1087.002` | lettura della configurazione pki e degli enrollment rights via ldap. |
| credential access | steal or forge authentication certificates | `T1649` | individuazione dei template/endpoint abusabili per ottenere certificati. |

## Correlazioni con altri moduli

| provenienza | questa tecnica | effetto |
| :--- | :--- | :--- |
| account di dominio | ad cs enumeration | individua i vettori esc applicabili |
| ad cs enumeration | [esc1](<../esc1-template-abuse/README.md>) / [esc8](<../esc8-relay-adcs/README.md>) | indica quale scenario di abuso perseguire |

---

> **Nota:** Contenuto didattico e di metodologia. Esecuzione solo in laboratori propri o con autorizzazione esplicita. Output illustrativi, non da sistemi reali.
