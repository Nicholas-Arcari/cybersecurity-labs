> **English** | [Italiano](README.md)

# 18 - Document Your Configuration

> - **Phase:** System Setup - Configuration Management & Documentation
> - **Priority:** Medium - long-term investment for replicability and maintainability
> - **Prerequisites:** Markdown editor (Obsidian, VSCode, vim); git repository (optional, recommended)
> - **Estimated time:** 30-60 minutes for initial documentation; ongoing for updates

---

## Recommended Approach

### Option 1: Git repository with dotfiles

```Bash
mkdir ~/dotfiles && cd ~/dotfiles
git init

# Copy and track main configuration files
cp ~/.bashrc ~/dotfiles/
cp ~/.vimrc ~/dotfiles/
cp ~/.tmux.conf ~/dotfiles/
cp /etc/ssh/sshd_config ~/dotfiles/sshd_config.bak

git add . && git commit -m "initial dotfiles configuration"
# Push to private GitHub for access from any machine
```

### Option 2: Markdown notes (Obsidian)

```Bash
sudo apt install obsidian   # or flatpak install md.obsidian.Obsidian
```

Recommended vault structure:
```
kali-config/
+-- setup-checklist.md       # 20 steps: status (done/to do/notes)
+-- tools-installed.md       # Tool list with version and purpose
+-- network-config.md        # IPs, interfaces, UFW rules, VPN
+-- services-config.md       # SSH port, Suricata, Logwatch
+-- troubleshooting.md       # Problems encountered and solutions
```

---

## Why do it?

In 6 months you will not remember why you modified that parameter in `sysctl.conf`, which version of a tool was installed at the time of a specific test, or how you solved that configuration problem that took you 3 hours. Documentation transforms personal experience into reusable knowledge.

## What happens next?

You can replicate the entire configuration on a new machine in minutes instead of hours. You can quickly identify what changed when something stops working. Your technical portfolio (this very repository) becomes a concrete demonstration of skills to a recruiter.

## What's the risk if you don't?

"Voodoo Configuration": the system works but you are afraid to touch it because you do not know how it was configured. Impossibility of replicating the environment on another machine. Loss of accumulated knowledge in case of reinstallation.

---

> **Note:** This very repository (`cybersecurity-labs`) is a concrete example of professional technical documentation. The `00-setup-after-installing-kali` module you are reading is the documentation of one's own configuration applied to this project's methodology.
