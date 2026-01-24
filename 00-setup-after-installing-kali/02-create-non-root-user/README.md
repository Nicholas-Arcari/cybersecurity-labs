# Crea un utente non-root

Comando:

```Bash
sudo adduser [tuo_nome]
sudo usermod -aG sudo [tuo_nome]
```

- Perché farlo?

Il principio del "minimo privilegio". Lavorare sempre come root è pericoloso perché ogni comando ha potere assoluto sul sistema senza conferme

- Cosa accade dopo?

Avrai un utente standard per l'uso quotidiano. Quando dovrai eseguire compiti amministrativi, il sistema ti chiederà la password (sudo)

- Cosa rischi se non lo fai?

Un comando errato (es. cancellazione file) potrebbe distruggere l'intero sistema operativo. Inoltre, se un malware infetta il pc mentre sei root, otterrà immediatamente il controllo totale