# 05 - Installa strumenti essenziali

> - **Fase:** System Setup - Toolset Configuration
> - **Priorita:** Media - migliora l'efficienza operativa quotidiana
> - **Prerequisiti:** Sistema aggiornato (passo 01); connettivita internet
> - **Tempo stimato:** 5 minuti

---

## Comandi

```Bash
sudo apt install -y htop curl tmux net-tools wget git vim
```

---

## Perche farlo?

Gli strumenti di default di Kali sono basilari o assenti per l'uso quotidiano. `htop` e nettamente superiore a `top` per la diagnostica visiva dei processi. `tmux` risolve uno dei problemi piu frustranti del lavoro remoto: la perdita della sessione a causa di disconnessioni SSH. `curl` e indispensabile per test rapidi di endpoint e download di script.

## Cosa accade dopo?

L'efficienza operativa migliorera sensibilmente. `tmux` in particolare consente di avere multiple sessioni terminale in una sola connessione SSH e di mantenere i processi attivi anche in caso di disconnessione.

## Cosa rischi se non lo fai?

Perdi tempo prezioso in operazioni macchinose, hai meno visibilita su cosa consuma le risorse del sistema, e rischi di perdere sessioni di lavoro lunghe (es. scansioni Nmap o compilazioni) a causa di disconnessioni di rete.

---

## Tool di riferimento

| Tool | Caso d'uso principale |
| :--- | :--- |
| `htop` | Monitor interattivo processi con colori, filtri e kill diretto |
| `tmux` | Multiplexer terminale: sessioni persistenti, split pane, detach/attach |
| `curl` | HTTP client CLI: test endpoint, download script, interazione API REST |
| `net-tools` | Toolkit rete legacy: `ifconfig`, `netstat`, `route` |
| `wget` | Download file da riga di comando con resume e ricorsivita |
| `git` | Version control: clonare tool, script e repository di exploit |
| `vim` | Editor testo avanzato per modifica file di configurazione |

---

> **Nota:** Per sessioni di lavoro intensivo su terminale, configurare `tmux` con un file `~/.tmux.conf` personalizzato (prefix key, colori, status bar). Una configurazione minimale consigliata: `set -g mouse on` per abilitare lo scroll con il mouse.
