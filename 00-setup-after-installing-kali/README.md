# 00 - Setup After Installing Kali Linux

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

| Step | Cartella | Obiettivo |
| :---: | :--- | :--- |
| 01 | `01-update-your-system/` | Aggiornamento completo pacchetti e kernel |
| 02 | `02-create-non-root-user/` | Principio del minimo privilegio: utente standard |
| 03 | `03-change-default-password/` | Cambio credenziali di default `kali/kali` |
| 04 | `04-enable-firewall/` | Configurazione UFW: chiusura porte non necessarie |
| 05 | `05-install-essential-tools/` | Toolset base: htop, curl, tmux, net-tools |
| 06 | `06-secure-ssh-access/` | Hardening SSH: porta non standard, no root login |
| 07 | `07-enable-automatic-updates/` | `unattended-upgrades` per patch di sicurezza automatiche |
| 08 | `08-install-monitoring-tools/` | Dashboard stato sistema (Nagios/Zabbix agent) |
| 09 | `09-customize-desktop-environment/` | Ergonomia: XFCE/Gnome per sessioni di lavoro lunghe |
| 10 | `10-encrypt-sensitive-data/` | LUKS/VeraCrypt per protezione dati di engagement |
| 11 | `11-perform-vulnerability-scans/` | OpenVAS/GVM: self-assessment vulnerabilita |
| 12 | `12-schedule-regular-maintenance/` | Cronjob per update e pulizia disco automatici |
| 13 | `13-harden-the-kernel/` | `sysctl.conf`: protezione da DoS, spoofing, flooding |
| 14 | `14-configure-intrusion-detection-systems/` | Suricata IDS: rilevamento attacchi in tempo reale |
| 15 | `15-test-defensive-tools/` | Validazione empirica delle difese configurate |
| 16 | `16-automate-tasks/` | Script backup log (tar) e sistema (rsync) |
| 17 | `17-join-kali-community/` | Forum e Discord ufficiali Kali Linux |
| 18 | `18-document-your-configuration/` | Documentazione modifiche (Markdown/Obsidian) |
| 19 | `19-backup-your-system/` | Disaster recovery: rsync e Timeshift |
| 20 | `20-setup-logwatch-system-monitoring/` | Logwatch: report giornaliero aggregato via email |

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

| Tool | Tipo | Step | Caso d'uso principale |
| :--- | :--- | :---: | :--- |
| `apt` / `unattended-upgrades` | Package manager | 01, 07 | Aggiornamento sistema e patch automatiche |
| `ufw` | Firewall | 04 | Gestione regole firewall (Uncomplicated Firewall) |
| `htop` | Monitor risorse | 05 | Visualizzazione interattiva CPU, RAM, processi |
| `tmux` | Terminal multiplexer | 05 | Sessioni multiple, persistenza anche a disconnessione |
| `sshd_config` | Demone SSH | 06 | Hardening accesso SSH remoto |
| `cryptsetup` (LUKS) | Disk encryption | 10 | Cifratura a blocchi per partizioni e volumi |
| `VeraCrypt` | Disk encryption | 10 | Cifratura volumi singoli (alternativa cross-platform) |
| `GVM` / `OpenVAS` | Vulnerability scanner | 11 | Self-assessment CVE sull'ambiente locale |
| `sysctl` | Kernel parameters | 13 | Hardening parametri rete kernel Linux |
| `Suricata` | IDS/IPS | 14 | Network Intrusion Detection con regole Emerging Threats |
| `rsync` | Backup tool | 16, 19 | Sincronizzazione incrementale file e directory |
| `Logwatch` | Log aggregator | 20 | Report giornaliero aggregato da `/var/log` |
| `Timeshift` | Snapshot tool | 19 | Backup point-in-time del sistema (simile Time Machine) |

---

> **Nota:** I passaggi documentati sono stati eseguiti su Kali Linux Purple (versione 2024.x) in ambiente di laboratorio virtualizzato (VirtualBox). Alcuni comandi potrebbero richiedere adattamenti per installazioni bare-metal o versioni differenti. La configurazione descritta rappresenta le scelte personali dell'autore e non costituisce uno standard universale.
