> **English** | [Italiano](README.md)

# 01 - Update Your System

> - **Phase:** System Setup - Package and kernel update
> - **Priority:** High - execute as the absolute first step after installation
> - **Prerequisites:** Internet connectivity; sudo or root access
> - **Estimated time:** 5-20 minutes (depends on connection and packages to update)

---

## Commands

```Bash
sudo apt update && sudo apt upgrade -y
```

---

## Why do it?

Installation ISO images are static and often months old. Repositories contain the most recent software versions, including security patches released after ISO publication.

## What happens next?

The system downloads the latest package definitions, fixes known bugs and updates the Linux kernel to the latest stable version available in the Kali repositories.

## What's the risk if you don't?

You will be working with outdated software that may contain security vulnerabilities already known to attackers, making the system unstable or easily penetrable. During an engagement, an unpatched attacker system is an operational risk.

---

> **Note:** Run periodically (at least once a week) or before every important operational session. Combine with step 07 (automatic updates) for routine maintenance.
