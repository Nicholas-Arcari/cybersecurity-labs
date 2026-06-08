> **English** | [Italiano](README.md)

# 02 - Create a Non-Root User

> - **Phase:** System Setup - Local Identity & Access Management
> - **Priority:** High - abandoning root for daily use is a fundamental practice
> - **Prerequisites:** Installation completed; access as root or kali (default)
> - **Estimated time:** 2 minutes

---

## Commands

```Bash
sudo adduser [your_name]
sudo usermod -aG sudo [your_name]
```

---

## Why do it?

The "Least Privilege" principle. Always working as root is dangerous because every command has absolute power over the system without confirmation prompts. A single typo can have irreversible consequences.

## What happens next?

You will have a standard user for daily use. When you need to perform administrative tasks, the system will require the password (`sudo`), adding an awareness barrier against accidental commands.

## What's the risk if you don't?

An erroneous command (e.g., `rm -rf /` with wrong autocomplete) could destroy the entire operating system. Furthermore, if malware infects the system while you are root, it will immediately gain total control without needing to perform privilege escalation.

---

> **Note:** After creation, log in with the new user and verify sudo access with `sudo whoami` (should return `root`). From this point on, use the new account for all daily operations.
