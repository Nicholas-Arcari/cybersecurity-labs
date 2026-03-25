# 10 - Crittografa i dati sensibili

> - **Fase:** System Setup - Data Protection & Encryption
> - **Priorita:** Alta - obbligatorio se il sistema contiene dati di engagement o report clienti
> - **Prerequisiti:** Partizione o disco disponibile per cifratura; `cryptsetup` installato (incluso in Kali)
> - **Tempo stimato:** 10-30 minuti (dipende dalla dimensione del volume)

---

## Comandi

### Opzione 1: LUKS (cifratura partizione intera)

```Bash
# ATTENZIONE: distrugge tutti i dati sulla partizione specificata
sudo cryptsetup luksFormat /dev/sdX           # Sostituire /dev/sdX con la partizione corretta
sudo cryptsetup open /dev/sdX encrypted_vol   # Apertura e mapping
sudo mkfs.ext4 /dev/mapper/encrypted_vol      # Formattazione
sudo mount /dev/mapper/encrypted_vol /mnt/secure
```

### Opzione 2: VeraCrypt (volume cifrato come file)

```Bash
sudo apt install veracrypt
veracrypt    # Interfaccia grafica per creare e montare volumi cifrati
```

---

## Perche farlo?

Durante un penetration test o un'analisi forense, il sistema contiene dati estremamente sensibili: credenziali del cliente, hash NTLM catturati, screenshot di sistemi compromessi, report riservati. Se il laptop viene perso o rubato, questi dati sono direttamente accessibili montando il disco su un altro sistema.

## Cosa accade dopo?

I dati sono illeggibili senza la chiave di decrittazione (password o keyfile), anche se l'hard disk viene smontato fisicamente e letto su un altro PC con strumenti forensi. La protezione e a livello hardware/filesystem, indipendente dall'autenticazione del sistema operativo.

## Cosa rischi se non lo fai?

Se perdi il laptop o viene rubato, chiunque puo montare il disco e leggere tutti i file, report, chiavi SSH e credenziali. Nelle attivita professionali, questo espone a responsabilita legali (GDPR, accordi NDA) per la divulgazione non autorizzata di dati riservati del cliente.

---

## Tool di riferimento

| Tool | Tipo | Pro | Contro |
| :--- | :--- | :--- | :--- |
| `LUKS` + `cryptsetup` | Cifratura partizione | Integrato nel kernel Linux, massima performance | Richiede partizione dedicata, formato Linux-only |
| `VeraCrypt` | Volume cifrato (file o partizione) | Cross-platform (Linux/Win/Mac), hidden volumes | Richiede installazione separata |
| `GPG` | Cifratura file singoli | Ideale per report e file di testo | Non adatto per volumi grandi |

---

> **Nota:** Conservare la password di decrittazione in un password manager sicuro (es. KeePassXC con file database su supporto separato). Una password persa su un volume LUKS significa perdita permanente e irrecuperabile dei dati.
