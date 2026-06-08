> **English** | [Italiano](README.md)

# 00 - Setup After Installing Kali Linux

> - **Phase:** Pre-Operative - System Hardening & Configuration
> - **Context:** One-time configuration to perform immediately after a new Kali Linux installation, before any operational activity (recon, exploitation, forensic analysis)
> - **Prerequisites:** Kali Linux installation completed (bare metal or VM); access with default credentials (`kali/kali`); network connectivity for package downloads
> - **Output:** Hardened Kali environment, configured for Blue Team operations, Threat Hunting and Forensic Analysis; reduced operating system attack surface

---

## Introduction

A "fresh" Kali Linux installation is a powerful but unhardened system: publicly known default passwords (`kali/kali`), SSH exposed on port 22, no active firewall, kernel with permissive parameters. Using Kali in this state during an engagement is an operational risk: the attacker is as vulnerable as the target.

This folder documents the 20 essential steps to transform a clean installation into a secure, optimized environment ready for operations. The objective is twofold: reduce the operating system attack surface (defensive hardening) and configure monitoring and automation tools that transform Kali into a personal SOC-in-a-Box.

---

## Folder Structure

| Step | Folder | Objective |
| :---: | :--- | :--- |
| 01 | `01-update-your-system/` | Full package and kernel update |
| 02 | `02-create-non-root-user/` | Least privilege principle: standard user |
| 03 | `03-change-default-password/` | Change default credentials `kali/kali` |
| 04 | `04-enable-firewall/` | UFW configuration: close unnecessary ports |
| 05 | `05-install-essential-tools/` | Base toolset: htop, curl, tmux, net-tools |
| 06 | `06-secure-ssh-access/` | SSH hardening: non-standard port, no root login |
| 07 | `07-enable-automatic-updates/` | `unattended-upgrades` for automatic security patches |
| 08 | `08-install-monitoring-tools/` | System status dashboard (Nagios/Zabbix agent) |
| 09 | `09-customize-desktop-environment/` | Ergonomics: XFCE/Gnome for long work sessions |
| 10 | `10-encrypt-sensitive-data/` | LUKS/VeraCrypt for engagement data protection |
| 11 | `11-perform-vulnerability-scans/` | OpenVAS/GVM: vulnerability self-assessment |
| 12 | `12-schedule-regular-maintenance/` | Cronjobs for automatic updates and disk cleanup |
| 13 | `13-harden-the-kernel/` | `sysctl.conf`: protection against DoS, spoofing, flooding |
| 14 | `14-configure-intrusion-detection-systems/` | Suricata IDS: real-time attack detection |
| 15 | `15-test-defensive-tools/` | Empirical validation of configured defenses |
| 16 | `16-automate-tasks/` | Log backup scripts (tar) and system backup (rsync) |
| 17 | `17-join-kali-community/` | Official Kali Linux forums and Discord |
| 18 | `18-document-your-configuration/` | Configuration change documentation (Markdown/Obsidian) |
| 19 | `19-backup-your-system/` | Disaster recovery: rsync and Timeshift |
| 20 | `20-setup-logwatch-system-monitoring/` | Logwatch: aggregated daily report via email |

---

## Recommended Execution Flow

```
[HIGH PRIORITY - Execute within the first 10 minutes]
Step 01: apt update && upgrade       -> eliminate known vulnerabilities
Step 03: passwd                      -> change kali/kali (public credentials)
Step 02: adduser + usermod sudo      -> abandon root for daily use
Step 04: ufw enable                  -> close unnecessary ports
Step 06: sshd_config hardening       -> port 2222, no root login

[MEDIUM PRIORITY - Environment configuration]
Step 05: essential tools             -> htop, curl, tmux, net-tools
Step 07: unattended-upgrades         -> automatic patches
Step 09: desktop environment         -> ergonomics for long sessions
Step 12: crontab maintenance         -> automatic disk cleanup

[HIGH PRIORITY - Defensive tools]
Step 13: sysctl.conf hardening       -> kernel protection from DoS/spoofing
Step 14: Suricata IDS                -> network attack detection
Step 08: monitoring tools            -> CPU/RAM/services status
Step 20: logwatch                    -> aggregated log report

[HIGH PRIORITY - Data protection]
Step 10: LUKS/VeraCrypt              -> engagement data encryption
Step 16: log backup script           -> forensic evidence
Step 19: system backup               -> disaster recovery

[MAINTENANCE]
Step 11: OpenVAS self-assessment     -> periodic security posture check
Step 15: test defenses               -> firewall/IDS validation
Step 18: documentation               -> change tracking
Step 17: community                   -> professional development
```

---

## Reference Tools

| Tool | Type | Step | Main Use Case |
| :--- | :--- | :---: | :--- |
| `apt` / `unattended-upgrades` | Package manager | 01, 07 | System update and automatic patches |
| `ufw` | Firewall | 04 | Firewall rules management (Uncomplicated Firewall) |
| `htop` | Resource monitor | 05 | Interactive CPU, RAM, process visualization |
| `tmux` | Terminal multiplexer | 05 | Multiple sessions, persistence even on disconnect |
| `sshd_config` | SSH daemon | 06 | Remote SSH access hardening |
| `cryptsetup` (LUKS) | Disk encryption | 10 | Block-level encryption for partitions and volumes |
| `VeraCrypt` | Disk encryption | 10 | Single volume encryption (cross-platform alternative) |
| `GVM` / `OpenVAS` | Vulnerability scanner | 11 | Local environment CVE self-assessment |
| `sysctl` | Kernel parameters | 13 | Linux kernel network parameter hardening |
| `Suricata` | IDS/IPS | 14 | Network Intrusion Detection with Emerging Threats rules |
| `rsync` | Backup tool | 16, 19 | Incremental file and directory synchronization |
| `Logwatch` | Log aggregator | 20 | Aggregated daily report from `/var/log` |
| `Timeshift` | Snapshot tool | 19 | Point-in-time system backup (similar to Time Machine) |

---

> **Note:** The documented steps were executed on Kali Linux Purple (version 2024.x) in a virtualized lab environment (VirtualBox). Some commands may require adjustments for bare-metal installations or different versions. The described configuration represents the author's personal choices and does not constitute a universal standard.
