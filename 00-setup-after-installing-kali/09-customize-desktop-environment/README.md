# 09 - Personalizza l'ambiente desktop

> - **Fase:** System Setup - Ergonomia & Produttivita
> - **Priorita:** Bassa - impatto indiretto sulla qualita del lavoro durante sessioni lunghe
> - **Prerequisiti:** Ambiente grafico installato (XFCE di default in Kali)
> - **Tempo stimato:** 15-30 minuti

---

## Comandi

Apertura pannello impostazioni XFCE:

```Bash
xfce4-settings-manager    # GUI impostazioni grafiche
```

Configurazione terminale (font, colori, opacita):

```Bash
xfce4-terminal --preferences
```

Per installare un tema scuro (raccomandato per sessioni notturne):

```Bash
sudo apt install kali-themes    # Temi ufficiali Kali
```

Per installare GNOME come alternativa a XFCE:

```Bash
sudo apt install kali-desktop-gnome
sudo update-alternatives --config x-session-manager
```

---

## Perche farlo?

L'ergonomia non e vanita: e produttivita. Lavorare ore su terminali con contrasto sbagliato, font piccoli o layout scomodi stanca la vista, aumenta l'affaticamento cognitivo e porta a errori di lettura nei log o di digitazione nei comandi.

## Cosa accade dopo?

Un ambiente di lavoro confortevole riduce l'affaticamento visivo durante sessioni di analisi prolungate. Font monospaziati ben leggibili, temi scuri e layout dei workspace ottimizzati aumentano la velocita di lettura degli output.

## Cosa rischi se non lo fai?

Minore produttivita e maggiore probabilita di commettere errori di lettura su output di tool (es. confondere caratteri simili in hash NTLM o indirizzi IP).

---

## Personalizzazioni consigliate

| Impostazione | Raccomandazione |
| :--- | :--- |
| Font terminale | `Hack Nerd Font` o `JetBrains Mono` - monospazio ottimizzato per codice |
| Tema | Tema scuro (es. `Kali-Dark`) - riduce affaticamento visivo in ambienti bui |
| Dimensione font | 12-14pt per schermi standard, 16pt per HiDPI |
| Workspace | 4 workspace: terminali, browser, tool GUI, note |
| Opacita terminale | 85-90% per leggibilita mantenendo il contesto dello schermo |

---

> **Nota:** Le preferenze del desktop sono soggettive. Il punto chiave e standardizzare la propria configurazione e documentarla (passo 18) per replicarla rapidamente su nuove installazioni. Considerare l'uso di dotfiles (repository git con `.bashrc`, `.vimrc`, `.tmux.conf`) per portare la propria configurazione su qualsiasi macchina in pochi minuti.
