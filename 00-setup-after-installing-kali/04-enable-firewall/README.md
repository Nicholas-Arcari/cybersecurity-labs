# Abilita il firewall

Comando:

```Bash
sudo apt install ufw
sudo ufw enable
sudo ufw allow 22/tcp   # (opzionale: solo se usi SSH)
```

- Perché farlo?

Kali Purple avvia molti servizi di rete. Un firewall blocca le connessioni in entrata non richieste

- Cosa accade dopo?

Il sistema rifiuterà silenziosamente tentativi di connessione dall'esterno, eccetto quelli esplicitamente permessi

- Cosa rischi se non lo fai?

Esponi servizi potenzialmente vulnerabili a tutta la rete. Un attaccante potrebbe sfruttare una porta aperta dimenticata per entrare nel sistema