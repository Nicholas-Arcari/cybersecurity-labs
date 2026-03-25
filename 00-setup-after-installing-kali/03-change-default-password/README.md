# 03 - Cambia le password di default

> - **Fase:** System Setup - Credential Management
> - **Priorita:** Critica - eseguire entro i primi minuti dall'installazione
> - **Prerequisiti:** Accesso al sistema con le credenziali di default (`kali/kali`)
> - **Tempo stimato:** 1 minuto

---

## Comandi

```Bash
passwd
```

Per cambiare la password di root (se necessario):

```Bash
sudo passwd root
```

---

## Perche farlo?

La password predefinita di Kali Linux e `kali`. E un'informazione di pubblico dominio, documentata nella wiki ufficiale e nota a chiunque abbia mai installato Kali. Qualsiasi scanner di rete o tool di brute-force la tenta come prima opzione.

## Cosa accade dopo?

L'accesso al sistema sara protetto da una stringa segreta nota solo a te. Tutti i servizi che usano l'autenticazione di sistema (SSH, sudo, login grafico) erediteranno automaticamente la nuova password.

## Cosa rischi se non lo fai?

Chiunque si trovi sulla stessa rete (o se il PC e esposto su internet) puo accedere al sistema digitando `kali/kali`, rubando dati, installando backdoor o usando la macchina come pivot per attacchi verso altri target.

---

> **Nota:** Scegliere una password di almeno 16 caratteri con mix di maiuscole, minuscole, numeri e simboli. Considerare l'uso di un password manager (es. KeePassXC) per generare e conservare la password in modo sicuro.
