# 06 - Metti in sicurezza l'accesso SSH

> - **Fase:** System Setup - Remote Access Hardening
> - **Priorita:** Alta - eseguire prima di esporre il sistema su reti non fidate
> - **Prerequisiti:** Servizio SSH installato (`sudo apt install openssh-server`); editor di testo (vim, nano)
> - **Tempo stimato:** 5 minuti

---

## Comandi

Modificare `/etc/ssh/sshd_config`:

```Bash
sudo vim /etc/ssh/sshd_config
```

Parametri da impostare o verificare:

```Bash
Port 2222               # Cambia la porta standard (scegliere una porta > 1024)
PermitRootLogin no      # Vieta il login diretto come root
PasswordAuthentication yes   # Mantenere yes per ora; impostare no solo dopo aver configurato le chiavi SSH
MaxAuthTries 3          # Limita i tentativi di autenticazione per connessione
```

Riavviare il servizio per applicare le modifiche:

```Bash
sudo systemctl restart ssh
sudo systemctl status ssh    # Verifica che il servizio sia attivo
```

Per connettersi alla nuova porta:

```Bash
ssh -p 2222 utente@ip_macchina
```

---

## Perche farlo?

La porta 22 e la piu attaccata al mondo da bot automatici e scanner di vulnerabilita. L'account root e il bersaglio principale degli attacchi brute-force automatizzati. Cambiare la porta riduce il rumore dei log; disabilitare il login root elimina il target piu appetibile.

## Cosa accade dopo?

Per connettersi bisognera specificare la porta personalizzata. I bot automatici che scansionano sistematicamente la porta 22 non troveranno il servizio. I tentativi di brute-force sul root saranno rifiutati a prescindere dalla password.

## Cosa rischi se non lo fai?

Il file `/var/log/auth.log` si riempira di migliaia di tentativi di accesso falliti (log fatigue). Aumenta la probabilita che un attacco brute-force prolungato o un dizionario di credenziali comuni abbia successo.

---

## Tool di riferimento

| Parametro `sshd_config` | Descrizione |
| :--- | :--- |
| `Port` | Porta di ascolto del demone SSH |
| `PermitRootLogin no` | Blocca login diretto come root (richiede utente standard + sudo) |
| `MaxAuthTries 3` | Massimo 3 tentativi per connessione prima del reset |
| `AllowUsers [nome]` | Whitelist: solo gli utenti elencati possono autenticarsi |
| `PubkeyAuthentication yes` | Abilita autenticazione con chiave pubblica/privata (piu sicura di password) |

---

> **Nota:** Dopo aver cambiato la porta, aggiornare la regola UFW di conseguenza: `sudo ufw delete allow 22/tcp && sudo ufw allow 2222/tcp`. Per massimo hardening, configurare l'autenticazione tramite chiave SSH (`ssh-keygen` + `ssh-copy-id`) e successivamente impostare `PasswordAuthentication no`.
