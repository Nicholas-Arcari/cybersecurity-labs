> **English** | [Italiano](README.md)

# 03 - Change Default Passwords

> - **Phase:** System Setup - Credential Management
> - **Priority:** Critical - execute within the first minutes after installation
> - **Prerequisites:** System access with default credentials (`kali/kali`)
> - **Estimated time:** 1 minute

---

## Commands

```Bash
passwd
```

To change the root password (if needed):

```Bash
sudo passwd root
```

---

## Why do it?

Kali Linux's default password is `kali`. It is publicly known information, documented in the official wiki and known to anyone who has ever installed Kali. Any network scanner or brute-force tool tries it as the first option.

## What happens next?

System access will be protected by a secret string known only to you. All services using system authentication (SSH, sudo, graphical login) will automatically inherit the new password.

## What's the risk if you don't?

Anyone on the same network (or if the PC is exposed to the internet) can access the system by typing `kali/kali`, stealing data, installing backdoors or using the machine as a pivot for attacks against other targets.

---

> **Note:** Choose a password of at least 16 characters with a mix of uppercase, lowercase, numbers and symbols. Consider using a password manager (e.g., KeePassXC) to generate and securely store the password.
