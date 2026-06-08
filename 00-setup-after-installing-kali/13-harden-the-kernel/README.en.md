> **English** | [Italiano](README.md)

# 13 - Harden the Kernel (sysctl Hardening)

> - **Phase:** System Setup - Kernel & Network Hardening
> - **Priority:** High - protection against common network attack classes
> - **Prerequisites:** Root or sudo access; text editor
> - **Estimated time:** 10 minutes

---

## Commands

Edit `/etc/sysctl.conf`:

```Bash
sudo vim /etc/sysctl.conf
```

Hardening parameters to add or modify:

```Bash
# IP spoofing and source routing protection
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.accept_source_route = 0

# SYN flood protection (TCP syncookies)
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048

# Ignore ICMP ping (reduces network visibility)
net.ipv4.icmp_echo_ignore_all = 1

# ICMP redirect protection (routing manipulation)
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0

# Memory protection: disable SUID core dumps
fs.suid_dumpable = 0

# ASLR (Address Space Layout Randomization) - maximum
kernel.randomize_va_space = 2
```

Apply changes without reboot:

```Bash
sudo sysctl -p    # Load /etc/sysctl.conf
sudo sysctl -a    # Verify all current parameters
```

---

## Why do it?

Default Linux kernel settings favor compatibility and interoperability, not security. Many network parameters are configured for the general use case (server or workstation in a secure LAN), not for a system exposed to potentially hostile networks like those used during labs.

## What happens next?

The kernel will ignore malicious ping floods and ICMP redirects, prevent source routing (used for spoofing), limit the effectiveness of SYN floods and make exploitation of memory vulnerabilities harder through maximized ASLR.

## What's the risk if you don't?

The system is susceptible to DoS (Denial of Service) attacks, IP spoofing and routing manipulation. On a shared lab network, these techniques could be used by other participants to interfere with your sessions.

---

> **Note:** Some settings (e.g., `icmp_echo_ignore_all = 1`) can interfere with network diagnostic tools like `ping`. Adapt according to operational needs: on isolated lab systems you can be more aggressive; on production machines evaluate impact before applying. Verify compatibility with any VPNs or network tunnels before application.
