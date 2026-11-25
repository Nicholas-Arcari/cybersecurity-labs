> [English](README.en.md) | **Italiano**

# 04 - Hardening scripts (lo scudo)

> - **Fase:** Defense & Hardening - System Hardening (Prevention)
> - **Categoria:** Prevention - riduzione della superficie d'attacco
> - **Prerequisiti:** Accesso privilegiato ai sistemi; strumenti di audit (Lynis, CIS-CAT); baseline di riferimento (CIS Benchmarks); ambiente di test
> - **Output:** Finding DEF-007..008; sistemi Linux e Windows hardenizzati; superficie d'attacco ridotta e misurabile

---

## Introduzione

L'hardening e "lo scudo": la difesa preventiva che agisce prima dell'attacco, riducendo cio che l'attaccante puo sfruttare. Mentre SIEM (`../01-siem-log-analysis/`) e XDR (`../02-endpoint-security-xdr/`) rilevano gli attacchi in corso e la deception (`../03-deception/`) li tradisce, l'hardening li previene alla radice - chiude le porte prima che l'attaccante bussi.

E lo strato piu efficiente della difesa perche agisce sulla causa, non sul sintomo: un attacco prevenuto non deve essere rilevato ne contenuto. Ogni servizio non necessario disattivato, ogni permesso ristretto, ogni default insicuro corretto elimina un vettore a costo funzionale zero. Il principio guida e la minimizzazione della superficie d'attacco: tutto cio che non serve e un rischio senza beneficio.

L'approccio non e improvvisato ma guidato da baseline riconosciute (CIS Benchmarks, Microsoft Security Baseline) e misurato da strumenti di audit (Lynis, CIS-CAT) che rendono l'hardening oggettivo e ripetibile - un ciclo audit, hardening, ri-audit con un punteggio misurabile, non una collezione di comandi applicati a caso.

La sezione e la contromisura speculare al percorso offensivo:

1. **Linux Hardening (DEF-007):** audit con Lynis e baseline CIS. Chiude le classi di privilege escalation del modulo 04 (SUID abusabili, sudo mal configurati, cron scrivibili, credenziali in chiaro).

2. **Windows Hardening (DEF-008):** GPO, Credential Guard, LAPS e baseline CIS. Neutralizza le tecniche di credential dumping (Mimikatz/LSASS) e lateral movement (pass-the-hash) del modulo 07.

Ogni finding offensivo del percorso ha qui la sua contromisura preventiva: l'hardening e il modulo dove l'attacco studiato diventa difesa applicata.

---

## Struttura della cartella

```
04-hardening-scripts (Lo Scudo)/
+-- README.md              # questo file: registro DEF-007..008, filosofia dell'hardening
|
+-- linux-hardening/       # DEF-007: audit Lynis + baseline CIS Linux
+-- windows-hardening/     # DEF-008: GPO, Credential Guard, LAPS, baseline CIS
```

---

## Flusso operativo consigliato

```
[INPUT] Sistema da hardenizzare (Linux/Windows)
         |
         v
[1] Audit iniziale (baseline)
     +-- Lynis (Linux) / CIS-CAT (Windows) -> hardening index + warning
              |
              v
[2] Applicazione dell'hardening
     +-- Linux: SSH, SUID, sudo, sysctl (DEF-007)
     +-- Windows: GPO, Credential Guard, LAPS, SMBv1 (DEF-008)
     +-- SEMPRE: snapshot prima, test dopo (non rompere i servizi)
              |
              v
[3] Ri-audit (misura del miglioramento)
     +-- l'hardening index conferma la riduzione oggettiva della superficie
              |
              v
[4] Hardening + detection
     +-- FIM (Wazuh DEF-003) sui file hardenizzati -> rileva i tentativi di annullare l'hardening
              |
              v
[OUTPUT] Superficie d'attacco ridotta -> intere classi di attacco prevenute
```

---

## Tool di riferimento

| tool | piattaforma | ruolo | caso d'uso principale |
| :--- | :--- | :--- | :--- |
| `Lynis` | linux | auditor | audit di hardening con index e raccomandazioni |
| `CIS Benchmarks` | multi | baseline | configurazioni di sicurezza riconosciute |
| `Microsoft Security Baseline` | windows | baseline | gpo di hardening pre-configurate |
| `Credential Guard` / `LAPS` | windows | contromisura | protezione credenziali (anti mimikatz/pth) |
| `OpenSCAP` / `CIS-CAT` | multi | compliance | verifica di conformita ai profili di sicurezza |
| `Ansible` (hardening role) | multi | automation | hardening idempotente su parchi macchine |

> **Tool moderno consigliato:** `Lynis` (Linux) e `CIS-CAT` (Windows) per audit e misura; le baseline `CIS`/`Microsoft` come riferimento; `Ansible` (DevSec Hardening Framework) per l'applicazione idempotente su scala. Su Windows, `Credential Guard` e `LAPS` sono le contromisure a piu alto impatto.

---

## Registro finding - sezione hardening scripts

| id | descrizione | severity | sottocartella |
| :--- | :--- | :---: | :--- |
| `DEF-007` | linux hardening: audit lynis + baseline cis, riduzione superficie (anti privesc) | `Alto` | `linux-hardening/` |
| `DEF-008` | windows hardening: gpo, credential guard, laps (anti credential dumping / pth) | `Alto` | `windows-hardening/` |

---

## Mappatura MITRE ATT&CK - aggregata

> Tecniche d'attacco **prevenute** dall'hardening della sezione.

| tattica (prevenuta) | tecnica | id mitre | finding correlato |
| :--- | :--- | :--- | :--- |
| privilege escalation | abuse elevation control: sudo | `T1548.003` | DEF-007 |
| privilege escalation | setuid and setgid | `T1548.001` | DEF-007 |
| credential access | os credential dumping: lsass memory | `T1003.001` | DEF-008 |
| lateral movement | use alternate authentication material: pass the hash | `T1550.002` | DEF-008 |
| persistence | boot or logon autostart: registry run keys | `T1547.001` | DEF-008 |
| credential access | unsecured credentials: credentials in files | `T1552.001` | DEF-007 |

---

> **Nota:** Tutte le attivita documentate in questa sezione sono state condotte su sistemi di laboratorio di proprieta dell'autore. L'hardening va applicato con attenzione al ruolo del sistema (snapshot e test obbligatori): una policy errata puo interrompere servizi legittimi o, in Active Directory, impattare l'intero dominio. Le tecniche sono documentate a scopo educativo e di difesa in contesto autorizzato.
