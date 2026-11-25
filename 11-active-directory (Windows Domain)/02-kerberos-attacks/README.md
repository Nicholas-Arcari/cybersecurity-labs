> [English](README.en.md) | **Italiano**

# 11.2 - Attacchi al protocollo Kerberos

> - **Fase:** Credential Access nel dominio - abuso di funzionalita legittime di Kerberos
> - **Prerequisiti:** per Kerberoasting e AS-REP Roasting basta un account di dominio valido (basso privilegio) o, per AS-REP, anche solo una lista di username; per i ticket forgiati servono chiavi ottenute a valle (krbtgt per il Golden, chiave del servizio per il Silver)
> - **Natura:** metodologia (output illustrativi; Finding ID `AD-NNN` da assegnare in lab)

## Introduzione

Kerberos e il cuore dell'autenticazione in Active Directory. Gli attacchi qui raccolti non sfruttano
vulnerabilita del protocollo ma sue proprieta di design: qualunque principal autenticato puo richiedere
ticket di servizio (base del Kerberoasting), gli account senza pre-autenticazione espongono materiale
crackabile (AS-REP Roasting), e chi possiede le chiavi giuste puo forgiare ticket arbitrari (Silver e
Golden Ticket, con le varianti stealth Diamond e Sapphire che riducono gli indicatori di compromissione). I
fondamenti formali sono in [THEORETICAL-FOUNDATIONS](<../THEORETICAL-FOUNDATIONS.md>) (sezioni 3.1-3.2).

## Struttura della cartella

| Sottocartella | Tecnica | Severity tipica | Stato |
| :--- | :--- | :---: | :--- |
| `kerberoasting/` | Kerberoasting (furto hash service account via TGS) | `Alto` | Scritta |
| `as-rep-roasting/` | AS-REP Roasting (account senza pre-auth) | `Alto` | Scritta |
| `silver-ticket/` | Silver Ticket (TGS forgiato con chiave del servizio) | `Alto` | Scritta |
| `golden-ticket/` | Golden Ticket (TGT forgiato con chiave di krbtgt) | `Critico` | Scritta |
| `diamond-ticket/` | Diamond Ticket (TGT reale con PAC modificato - variante stealth) | `Critico` | Scritta |
| `sapphire-ticket/` | Sapphire Ticket (PAC autentico via S4U2self - massimo stealth) | `Critico` | Scritta |

## Flusso operativo consigliato

1. Con un account di dominio, enumerare gli SPN e lanciare Kerberoasting: e il vettore a piu basso costo.
2. In parallelo, AS-REP Roasting sugli account con pre-autenticazione disabilitata.
3. Crackare offline gli hash ottenuti (hashcat modi 13100/19700 per Kerberoast, 18200 per AS-REP).
4. I ticket forgiati (Silver/Golden e le varianti stealth Diamond/Sapphire) appartengono alla fase di
   escalation/persistenza e presuppongono chiavi gia ottenute (es. da
   [DCSync](<../05-credential-dumping/dcsync/README.md>)). Diamond e Sapphire si scelgono quando l'ambiente ha
   detection evolute (MDI): partono da materiale reale (TGT o PAC) invece di forgiare da zero.

---

> **Nota:** Contenuto didattico. Esecuzione solo in laboratori propri o con autorizzazione esplicita.
