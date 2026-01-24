# Crittografa i dati sensibili

Comando: 

(Richiede setup LUKS o VeraCrypt)

```Bash
sudo cryptsetup luksFormat /dev/sdX
sudo cryptsetup open /dev/sda1 encrypted_partition  # (inserire il nome corretto della tua partizione)
```


- Perché farlo?

Se stai facendo pentesting o analisi forense, hai dati sensibili dei clienti sul disco

- Cosa accade dopo?

I dati sono illeggibili senza la chiave di decrittazione, anche se l'hard disk viene smontato e letto su un altro PC

- Cosa rischi se non lo fai?

Se perdi il laptop o viene rubato, chiunque può montare il disco e leggere tutti i tuoi file, report e chiavi SSH. Responsabilità legale enorme