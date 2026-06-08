> **English** | [Italiano](README.md)

# 09 - Customize Desktop Environment

> - **Phase:** System Setup - Ergonomics & Productivity
> - **Priority:** Low - indirect impact on work quality during long sessions
> - **Prerequisites:** Graphical environment installed (XFCE by default in Kali)
> - **Estimated time:** 15-30 minutes

---

## Commands

Open XFCE settings panel:

```Bash
xfce4-settings-manager    # GUI graphical settings
```

Terminal configuration (font, colors, opacity):

```Bash
xfce4-terminal --preferences
```

To install a dark theme (recommended for night sessions):

```Bash
sudo apt install kali-themes    # Official Kali themes
```

To install GNOME as an alternative to XFCE:

```Bash
sudo apt install kali-desktop-gnome
sudo update-alternatives --config x-session-manager
```

---

## Why do it?

Ergonomics is not vanity: it is productivity. Working hours on terminals with wrong contrast, small fonts or uncomfortable layouts strains eyesight, increases cognitive fatigue and leads to reading errors in logs or typing errors in commands.

## What happens next?

A comfortable working environment reduces visual fatigue during extended analysis sessions. Well-readable monospaced fonts, dark themes and optimized workspace layouts increase output reading speed.

## What's the risk if you don't?

Lower productivity and higher probability of making reading errors on tool outputs (e.g., confusing similar characters in NTLM hashes or IP addresses).

---

## Recommended Customizations

| Setting | Recommendation |
| :--- | :--- |
| Terminal font | `Hack Nerd Font` or `JetBrains Mono` - monospace optimized for code |
| Theme | Dark theme (e.g., `Kali-Dark`) - reduces visual fatigue in dark environments |
| Font size | 12-14pt for standard screens, 16pt for HiDPI |
| Workspaces | 4 workspaces: terminals, browser, GUI tools, notes |
| Terminal opacity | 85-90% for readability while maintaining screen context |

---

> **Note:** Desktop preferences are subjective. The key point is to standardize your configuration and document it (step 18) to quickly replicate it on new installations. Consider using dotfiles (git repository with `.bashrc`, `.vimrc`, `.tmux.conf`) to bring your configuration to any machine in minutes.
