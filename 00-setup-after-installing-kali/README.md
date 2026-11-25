> [English](README.en.md) | **Italiano**

# 00 - Setup after installing Kali Linux

> - **Fase:** Pre-Operativa - System Hardening & Configuration
> - **Contesto:** Configurazione one-time da eseguire subito dopo una nuova installazione di Kali Linux, prima di qualsiasi attivita operativa (recon, exploitation, analisi forense)
> - **Prerequisiti:** Installazione Kali Linux completata (bare metal o VM); accesso con credenziali di default (`kali/kali`); connettivita di rete per il download dei pacchetti
> - **Output:** Ambiente Kali hardened, configurato per operazioni Blue Team, Threat Hunting e Analisi Forense; riduzione della superficie di attacco del sistema operativo

---

## Introduzione

Un'installazione "fresh" di Kali Linux e un sistema potente ma non hardened: password di default pubblicamente note (`kali/kali`), SSH esposto sulla porta 22, nessun firewall attivo, kernel con parametri permissivi. Usare Kali in questo stato durante un engagement e un rischio operativo: l'attaccante e vulnerabile quanto il target.

Questa cartella documenta i 20 passaggi essenziali per trasformare un'installazione pulita in un ambiente sicuro, ottimizzato e pronto per le operazioni. L'obiettivo e duplice: ridurre la superficie di attacco del sistema operativo (hardening difensivo) e configurare gli strumenti di monitoraggio e automazione che trasformano Kali in un SOC-in-a-Box personale.

---

## Struttura della cartella

| step | cartella | obiettivo |
| :---: | :--- | :--- |
| 01 | `01-update-your-system/` | aggiornamento completo pacchetti e kernel |
| 02 | `02-create-non-root-user/` | principio del minimo privilegio: utente standard |
| 03 | `03-change-default-password/` | cambio credenziali di default `kali/kali` |
| 04 | `04-enable-firewall/` | configurazione ufw: chiusura porte non necessarie |
| 05 | `05-install-essential-tools/` | toolset base: htop, curl, tmux, net-tools |
| 06 | `06-secure-ssh-access/` | hardening ssh: porta non standard, no root login |
| 07 | `07-enable-automatic-updates/` | `unattended-upgrades` per patch di sicurezza automatiche |
| 08 | `08-install-monitoring-tools/` | dashboard stato sistema (nagios/zabbix agent) |
| 09 | `09-customize-desktop-environment/` | ergonomia: xfce/gnome per sessioni di lavoro lunghe |
| 10 | `10-encrypt-sensitive-data/` | luks/veracrypt per protezione dati di engagement |
| 11 | `11-perform-vulnerability-scans/` | openvas/gvm: self-assessment vulnerabilita |
| 12 | `12-schedule-regular-maintenance/` | cronjob per update e pulizia disco automatici |
| 13 | `13-harden-the-kernel/` | `sysctl.conf`: protezione da dos, spoofing, flooding |
| 14 | `14-configure-intrusion-detection-systems/` | suricata ids: rilevamento attacchi in tempo reale |
| 15 | `15-test-defensive-tools/` | validazione empirica delle difese configurate |
| 16 | `16-automate-tasks/` | script backup log (tar) e sistema (rsync) |
| 17 | `17-join-kali-community/` | forum e discord ufficiali kali linux |
| 18 | `18-document-your-configuration/` | documentazione modifiche (markdown/obsidian) |
| 19 | `19-backup-your-system/` | disaster recovery: rsync e timeshift |
| 20 | `20-setup-logwatch-system-monitoring/` | logwatch: report giornaliero aggregato via email |

---

## Flusso di esecuzione consigliato

```
[PRIORITA ALTA - Eseguire entro i primi 10 minuti]
Step 01: apt update && upgrade       -> elimina vulnerabilita note
Step 03: passwd                      -> cambia kali/kali (credenziali pubbliche)
Step 02: adduser + usermod sudo      -> abbandona root per uso quotidiano
Step 04: ufw enable                  -> chiude porte non necessarie
Step 06: sshd_config hardening       -> porta 2222, no root login

[PRIORITA MEDIA - Configurazione ambiente]
Step 05: tool essenziali             -> htop, curl, tmux, net-tools
Step 07: unattended-upgrades         -> patch automatiche
Step 09: desktop environment         -> ergonomia per sessioni lunghe
Step 12: crontab manutenzione        -> pulizia disco automatica

[PRIORITA ALTA - Strumenti difensivi]
Step 13: sysctl.conf hardening       -> protezione kernel da DoS/spoofing
Step 14: Suricata IDS                -> rilevamento attacchi in rete
Step 08: monitoring tools            -> stato CPU/RAM/servizi
Step 20: logwatch                    -> report log aggregato

[PRIORITA ALTA - Protezione dati]
Step 10: LUKS/VeraCrypt              -> cifratura dati engagement
Step 16: script backup log           -> evidenze forensi
Step 19: backup sistema              -> disaster recovery

[MANTENIMENTO]
Step 11: OpenVAS self-assessment     -> verifica postura sicurezza periodica
Step 15: test difese                 -> validazione firewall/IDS
Step 18: documentazione              -> tracciamento modifiche
Step 17: community                   -> aggiornamento professionale
```

---

## Tool di riferimento

| tool | tipo | step | caso d'uso principale |
| :--- | :--- | :---: | :--- |
| `apt` / `unattended-upgrades` | package manager | 01, 07 | aggiornamento sistema e patch automatiche |
| `ufw` | firewall | 04 | gestione regole firewall (uncomplicated firewall) |
| `htop` | monitor risorse | 05 | visualizzazione interattiva cpu, ram, processi |
| `tmux` | terminal multiplexer | 05 | sessioni multiple, persistenza anche a disconnessione |
| `sshd_config` | demone ssh | 06 | hardening accesso ssh remoto |
| `cryptsetup` (luks) | disk encryption | 10 | cifratura a blocchi per partizioni e volumi |
| `VeraCrypt` | disk encryption | 10 | cifratura volumi singoli (alternativa cross-platform) |
| `GVM` / `OpenVAS` | vulnerability scanner | 11 | self-assessment cve sull'ambiente locale |
| `sysctl` | kernel parameters | 13 | hardening parametri rete kernel linux |
| `Suricata` | ids/ips | 14 | network intrusion detection con regole emerging threats |
| `rsync` | backup tool | 16, 19 | sincronizzazione incrementale file e directory |
| `Logwatch` | log aggregator | 20 | report giornaliero aggregato da `/var/log` |
| `Timeshift` | snapshot tool | 19 | backup point-in-time del sistema (simile time machine) |

---

> **Nota:** I passaggi documentati sono stati eseguiti su Kali Linux Purple (versione 2024.x) in ambiente di laboratorio virtualizzato (VirtualBox). Alcuni comandi potrebbero richiedere adattamenti per installazioni bare-metal o versioni differenti. La configurazione descritta rappresenta le scelte personali dell'autore e non costituisce uno standard universale.
