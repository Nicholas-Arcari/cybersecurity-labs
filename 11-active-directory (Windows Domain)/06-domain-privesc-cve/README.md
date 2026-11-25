> [English](README.en.md) | **Italiano**

# 11.6 - Privilege escalation di dominio via CVE

> - **Fase:** Privilege Escalation nel dominio - sfruttamento di vulnerabilita (CVE) di componenti core di Active Directory
> - **Prerequisiti:** variano per CVE; tipicamente credenziali di un utente di dominio a basso privilegio e un Domain Controller non patchato
> - **Natura:** metodologia (output illustrativi; Finding ID `AD-NNN` da assegnare in lab)

## Introduzione

A differenza delle sotto-aree precedenti, che sfruttano **proprieta di design** di Kerberos/AD (feature abuse),
questa raccoglie le escalation basate su **vulnerabilita vere e proprie** (CVE) di componenti core del dominio.
Sono catene ad alto impatto e, dove presenti, a basso costo: spesso da un utente di dominio qualunque si arriva
a Domain Admin in pochi passi. Il tratto comune e che la contromisura primaria e sempre il **patching** (piu
hardening di supporto), non una riconfigurazione.

Le CVE di questa classe hanno un ciclo di vita: diventano rare negli ambienti ben gestiti ma restano molto
pericolose su infrastrutture legacy o aggiornate male. Vanno quindi sempre verificate in fase di assessment.

## Struttura della cartella

| sottocartella | tecnica | cve | severity tipica | stato |
| :--- | :--- | :--- | :---: | :--- |
| `nopac/` | nopac (samaccountname spoofing) - da utente a da | CVE-2021-42278 + CVE-2021-42287 | `Critico` | scritta |

> Sotto-area estensibile: altre CVE di dominio candidate a questa sezione sono ZeroLogon (CVE-2020-1472),
> PrintNightmare (CVE-2021-34527) e dMSA/BadSuccessor (abuso delle delegated Managed Service Account). Vanno
> aggiunte quando documentate in lab, con lo stesso standard.

## Flusso operativo consigliato

1. Con credenziali di un utente di dominio valido, verificare lo stato di patch dei Domain Controller e i
   prerequisiti specifici (es. `MachineAccountQuota` per noPac).
2. In modalita scan/verifica prima dell'exploit, per non toccare inutilmente il DC.
3. Se la CVE e sfruttabile, la catena porta spesso a impersonation del DC e
   [DCSync](<../05-credential-dumping/dcsync/README.md>): da li il dominio e compromesso.
4. Documentare evidenze e stato di patch; la remediation e il patching piu l'hardening di supporto.

---

> **Nota:** Contenuto didattico. Esecuzione solo in laboratori propri o con autorizzazione esplicita.
