# Active Scanning: Port Scanning Phase

Obiettivo: Identificazione dei servizi attivi, filtraggio delle porte e analisi approfondita delle configurazioni esposte sul target. Strumenti: Masscan, Nmap

Questa directory documenta due approcci distinti e complementari al port scanning: la velocità (Masscan) e la profondità (Nmap Scripts).

---

## Struttura della Directory

1. High-Speed Scanning (Masscan)

In questa sezione viene esplorato l'uso di scanner asincroni per la ricognizione su larga scala.

- Attività: Confronto pratico tra Nmap e Masscan.
- Key Finding: Analisi critica dei "Falsi Negativi" generati da scanner stateless (Masscan) in ambienti virtualizzati (NAT), dimostrando l'importanza della validazione incrociata.

2. Deep Enumeration (Nmap Scripts)

In questa sezione l'attività si sposta sull'enumerazione avanzata dei servizi utilizzando l'Nmap Scripting Engine (NSE).

- Attività: Scansione del servizio SMB (porta 445) con script di default e di sicurezza.
- Key Finding: Individuazione di Information Disclosure (Nome NetBIOS esposto) e di una Security Misconfiguration critica (SMB Signing not required), che espone il target ad attacchi di tipo SMB Relay.