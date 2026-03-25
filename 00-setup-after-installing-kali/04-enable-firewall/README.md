# 04 - Abilita il firewall (UFW)

> - **Fase:** System Setup - Network Hardening
> - **Priorita:** Alta - eseguire prima di connettere il sistema a reti non fidate
> - **Prerequisiti:** Accesso sudo; pacchetto `ufw` (incluso in Kali di default)
> - **Tempo stimato:** 3 minuti

---

## Comandi

```Bash
sudo apt install ufw          # Installazione (se non presente)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp         # Solo se usi SSH - sostituire con la porta personalizzata (passo 06)
sudo ufw enable
sudo ufw status verbose       # Verifica regole attive
```

---

## Perche farlo?

Kali Linux avvia diversi servizi di rete durante il boot (SSH, servizi RPC, eventuali tool installati con listener). Senza un firewall, tutte le porte in ascolto sono accessibili da qualsiasi host della rete locale. In ambienti condivisi (reti aziendali, hotspot pubblici, VPN di laboratorio), questa superficie di attacco e inaccettabile.

## Cosa accade dopo?

Il sistema rifiutera silenziosamente i tentativi di connessione in entrata non esplicitamente autorizzati. Solo le porte definite nelle regole UFW saranno accessibili. Il traffico in uscita rimane libero per default, consentendo il normale uso operativo.

## Cosa rischi se non lo fai?

Esponi servizi potenzialmente vulnerabili a tutta la rete. Un attaccante potrebbe sfruttare una porta aperta dimenticata (es. un listener Metasploit rimasto attivo da una sessione precedente) per ottenere accesso al sistema.

---

## Tool di riferimento

| Comando | Descrizione |
| :--- | :--- |
| `sudo ufw status verbose` | Mostra regole attive e stato del firewall |
| `sudo ufw allow <porta>/tcp` | Apre una porta specifica in ingresso |
| `sudo ufw delete allow <porta>/tcp` | Rimuove una regola precedentemente aggiunta |
| `sudo ufw logging on` | Abilita il logging delle connessioni bloccate in `/var/log/ufw.log` |

---

> **Nota:** UFW e un frontend semplificato per `iptables`. Per ambienti piu complessi (VPN, Docker, connessioni tra VM) potrebbe essere necessario aggiungere regole piu granulari. Verificare sempre le regole con `ufw status verbose` dopo ogni modifica.
