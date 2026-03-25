# 02 - Crea un utente non-root

> - **Fase:** System Setup - Identity & Access Management locale
> - **Priorita:** Alta - abbandonare root per l'uso quotidiano e una pratica fondamentale
> - **Prerequisiti:** Installazione completata; accesso come root o kali (default)
> - **Tempo stimato:** 2 minuti

---

## Comandi

```Bash
sudo adduser [tuo_nome]
sudo usermod -aG sudo [tuo_nome]
```

---

## Perche farlo?

Il principio del "minimo privilegio" (Least Privilege). Lavorare sempre come root e pericoloso perche ogni comando ha potere assoluto sul sistema senza richieste di conferma. Un singolo errore di digitazione puo avere conseguenze irreversibili.

## Cosa accade dopo?

Avrai un utente standard per l'uso quotidiano. Quando dovrai eseguire compiti amministrativi, il sistema richiedera la password (`sudo`), aggiungendo una barriera di consapevolezza contro i comandi accidentali.

## Cosa rischi se non lo fai?

Un comando errato (es. `rm -rf /` con autocomplete sbagliato) potrebbe distruggere l'intero sistema operativo. Inoltre, se un malware infetta il sistema mentre sei root, otterra immediatamente il controllo totale senza dover eseguire privilege escalation.

---

> **Nota:** Dopo la creazione, effettuare il login con il nuovo utente e verificare l'accesso sudo con `sudo whoami` (deve restituire `root`). Da questo momento, usare il nuovo account per tutte le operazioni quotidiane.
