# Kali Post-Installation Toolkit

Una guida pratica e una suite di script per trasformare un'installazione pulita di Kali in una fortezza difensiva (SOC-in-a-Box)

---

Questa cartella nasce per automatizzare e documentare i passaggi essenziali da eseguire dopo una nuova installazione di Kali Linux

L'obiettivo è passare da un'installazione "bare metal" a un ambiente sicuro, ottimizzato e pronto per operazioni di Difesa (Blue Teaming), Threat Hunting e Analisi Forense

---

## Obiettivi del Progetto

- Hardening: Ridurre la superficie di attacco del sistema operativo

- Ottimizzazione: Configurare il sistema per prestazioni elevate durante i task intensivi

- Monitoraggio: Implementare strumenti di logging e IDS per la sorveglianza interna

- Automazione: Ridurre il lavoro manuale ripetitivo tramite script Bash

---

## Checklist dei 20 Passaggi

Ogni punto corrisponde a una configurazione manuale o a uno script automatizzato presente nelle cartelle del progetto

01. Aggiornamento Sistema: `apt update && upgrade` completo

02. Utente Non-Root: Creazione utente standard per operazioni quotidiane

03. Password Sicure: Cambio credenziali di default (`kali/kali`)

04. Firewall (UFW): Configurazione regole e chiusura porte non necessarie

05. Tool Essenziali: Installazione di `htop`, `curl`, `tmux`, ecc...

06. Hardening SSH: Disabilitazione root login e cambio porta standard

07. Auto-Updates: Configurazione `unattended-upgrades`

08. Monitoraggio: Setup di Nagios/Zabbix per lo stato del sistema

09. Desktop Environment: Personalizzazione XFCE/Gnome per produttività

10. Crittografia: Setup volumi cifrati (LUKS) per dati sensibili

11. Vulnerability Scan: Installazione e setup di OpenVAS (GVM)

12. Manutenzione: Cron jobs per pulizia e update

13. Kernel Hardening: Modifiche a `sysctl.conf` contro IP spoofing/flooding

14. IDS Setup: Installazione e configurazione di Suricata

15. Testing Difensivo: Validazione delle difese tramite simulazioni

16. Automazione Log: Script per backup e rotazione log locali

17. Community: Integrazione con risorse ufficiali Kali

18. Documentazione: Template per tracciare le modifiche (come questo repo)

19. System Backup: Strategie di disaster recovery

20. Logwatch: Reportistica automatizzata via email