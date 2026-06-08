> **English** | [Italiano](README.md)

# 07 - Enable Automatic Updates

> - **Phase:** System Setup - Automatic Patch Management
> - **Priority:** Medium - complementary to step 01 for long-term maintenance
> - **Prerequisites:** System updated (step 01); sudo access
> - **Estimated time:** 3 minutes

---

## Commands

```Bash
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

To verify the configuration:

```Bash
cat /etc/apt/apt.conf.d/50unattended-upgrades
sudo unattended-upgrades --dry-run --debug   # Test without installing
```

---

## Why do it?

Security is a continuous process, but humans forget to update. Critical security patches are released in response to actively exploited vulnerabilities: every day of delay in application is an exposure window.

## What happens next?

The system will autonomously install critical security patches in the background, without requiring manual intervention. Updates are applied according to a configurable schedule (nightly, by default).

## What's the risk if you don't?

You could remain exposed to a critical vulnerability (a CVE that became public and is already weaponized) for weeks or months, simply because you forgot to run `apt upgrade`. Many documented corporate breaches were caused by systems unpatched against vulnerabilities with patches available for weeks.

---

> **Note:** On Kali Linux, `unattended-upgrades` updates only security repositories by default. Tool version updates (e.g., new Metasploit version) still require a manual `apt upgrade`. Periodically check logs in `/var/log/unattended-upgrades/`.
