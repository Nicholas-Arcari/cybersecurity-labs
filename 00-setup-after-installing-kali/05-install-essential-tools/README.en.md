> **English** | [Italiano](README.md)

# 05 - Install essential tools

> - **Phase:** System Setup - Toolset Configuration
> - **Priority:** Medium - improves daily operational efficiency
> - **Prerequisites:** System updated (step 01); internet connectivity
> - **Estimated time:** 5 minutes

---

## Commands

```Bash
sudo apt install -y htop curl tmux net-tools wget git vim
```

---

## Why do it?

Kali's default tools are basic or absent for daily use. `htop` is vastly superior to `top` for visual process diagnostics. `tmux` solves one of the most frustrating remote work problems: session loss due to SSH disconnections. `curl` is indispensable for quick endpoint testing and script downloads.

## What happens next?

Operational efficiency will improve noticeably. `tmux` in particular allows having multiple terminal sessions in a single SSH connection and keeping processes alive even in case of disconnection.

## What's the risk if you don't?

You waste valuable time on cumbersome operations, have less visibility into what's consuming system resources, and risk losing long work sessions (e.g., Nmap scans or compilations) due to network disconnections.

---

## Reference tools

| tool | main use case |
| :--- | :--- |
| `htop` | interactive process monitor with colors, filters and direct kill |
| `tmux` | terminal multiplexer: persistent sessions, split panes, detach/attach |
| `curl` | cli http client: endpoint testing, script download, rest api interaction |
| `net-tools` | legacy network toolkit: `ifconfig`, `netstat`, `route` |
| `wget` | command-line file download with resume and recursion |
| `git` | version control: clone tools, scripts and exploit repositories |
| `vim` | advanced text editor for configuration file editing |

---

> **Note:** For intensive terminal work sessions, configure `tmux` with a custom `~/.tmux.conf` file (prefix key, colors, status bar). A recommended minimal configuration: `set -g mouse on` to enable mouse scrolling.
