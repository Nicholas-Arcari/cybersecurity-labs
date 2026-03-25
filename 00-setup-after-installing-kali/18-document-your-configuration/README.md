# 18 - Documenta la tua configurazione

> - **Fase:** System Setup - Configuration Management & Documentation
> - **Priorita:** Media - investimento a lungo termine per replicabilita e manutenibilita
> - **Prerequisiti:** Editor Markdown (Obsidian, VSCode, vim); repository git (opzionale, raccomandato)
> - **Tempo stimato:** 30-60 minuti per la documentazione iniziale; ongoing per gli aggiornamenti

---

## Approccio consigliato

### Opzione 1: Repository git con dotfiles

```Bash
mkdir ~/dotfiles && cd ~/dotfiles
git init

# Copia e traccia i file di configurazione principali
cp ~/.bashrc ~/dotfiles/
cp ~/.vimrc ~/dotfiles/
cp ~/.tmux.conf ~/dotfiles/
cp /etc/ssh/sshd_config ~/dotfiles/sshd_config.bak

git add . && git commit -m "initial dotfiles configuration"
# Push su GitHub privato per accesso da qualsiasi macchina
```

### Opzione 2: Note Markdown (Obsidian)

```Bash
sudo apt install obsidian   # o flatpak install md.obsidian.Obsidian
```

Struttura consigliata del vault:
```
kali-config/
+-- setup-checklist.md       # 20 passi: stato (fatto/da fare/note)
+-- tools-installed.md       # Lista tool con versione e scopo
+-- network-config.md        # IP, interfacce, regole UFW, VPN
+-- services-config.md       # SSH porta, Suricata, Logwatch
+-- troubleshooting.md       # Problemi incontrati e soluzioni
```

---

## Perche farlo?

Tra 6 mesi non ti ricorderai perche hai modificato quel parametro in `sysctl.conf`, quale versione di un tool era installata al momento di un test specifico, o come hai risolto quel problema di configurazione che ti ha impiegato 3 ore. La documentazione trasforma l'esperienza personale in conoscenza riutilizzabile.

## Cosa accade dopo?

Puoi replicare l'intera configurazione su una nuova macchina in pochi minuti invece di ore. Puoi identificare rapidamente cosa e cambiato quando qualcosa smette di funzionare. Il portfolio tecnico (questo stesso repository) diventa una dimostrazione concreta di competenze a un recruiter.

## Cosa rischi se non lo fai?

"Configurazione Voodoo": il sistema funziona ma hai paura di toccarlo perche non sai come e stato configurato. Impossibilita di replicare l'ambiente su un'altra macchina. Perdita della conoscenza accumulata in caso di reinstallazione.

---

> **Nota:** Questo stesso repository (`cybersecurity-labs`) e un esempio concreto di documentazione tecnica professionale. Il modulo `00-setup-after-installing-kali` che stai leggendo e la documentazione della propria configurazione applicata alla metodologia di questo progetto.
