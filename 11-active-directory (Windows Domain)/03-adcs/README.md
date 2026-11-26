> [English](README.en.md) | **Italiano**

# 11.3 - Abuso di Active Directory certificate services (AD CS)

> - **Fase:** Credential Access / Privilege Escalation nel dominio tramite l'autorita di certificazione
> - **Prerequisiti:** presenza di AD CS nel dominio; a seconda dello scenario ESC, un account di dominio (ESC1) o una posizione di rete con capacita di coercizione e relay (ESC8)
> - **Natura:** metodologia (output illustrativi; Finding ID `AD-NNN` da assegnare in lab)

## Introduzione

AD CS lega l'identita a certificati X.509. La ricerca "Certified Pre-Owned" (Schroeder, Christensen 2021)
ha catalogato una famiglia di misconfigurazioni (ESC1-ESC16 e oltre) che permettono di ottenere
certificati utilizzabili per autenticarsi come altri principal, spesso fino al Domain Controller. E oggi
uno dei vettori di escalation piu usati nei domini reali, e nel repository era completamente assente. I
fondamenti sono in [THEORETICAL-FOUNDATIONS](<../THEORETICAL-FOUNDATIONS.md>) (sezione 3.4).

## Struttura della cartella

| sottocartella | tecnica | severity tipica | stato |
| :--- | :--- | :---: | :--- |
| `esc8-relay-adcs/` | esc8: ntlm relay verso il web enrollment di ad cs | `Critico` | scritta |
| `esc1-template-abuse/` | esc1: template che consente san arbitrario | `Critico` | scritta |
| `esc-enumeration/` | enumerazione ad cs con certipy/certify | `Informativo` | scritta |
| `certipy/` | riferimento operativo consolidato di certipy (find/req/auth/shadow/relay) | `Critico` | scritta |

## Flusso operativo consigliato

1. Enumerare AD CS (CA, template, endpoint di enrollment) con Certipy (riferimento comandi completo in
   [certipy](<certipy/README.md>)).
2. Classificare le misconfigurazioni trovate secondo la tassonomia ESC.
3. Sfruttare lo scenario applicabile: ESC1 se esiste un account di dominio con accesso a template deboli;
   [ESC8](<esc8-relay-adcs/README.md>) se e presente l'endpoint HTTP di Web Enrollment e si puo coercere
   un'autenticazione da rilanciare.
4. Il certificato ottenuto si usa per autenticazione PKINIT e, a cascata, per il dominio completo.

---

> **Nota:** Contenuto didattico. Esecuzione solo in laboratori propri o con autorizzazione esplicita.
