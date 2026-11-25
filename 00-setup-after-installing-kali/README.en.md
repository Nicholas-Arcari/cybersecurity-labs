> **English** | [Italiano](README.md)

# 00 - Setup after installing Kali Linux

> - **Phase:** Pre-Operative - System Hardening & Configuration
> - **Context:** One-time configuration to perform immediately after a new Kali Linux installation, before any operational activity (recon, exploitation, forensic analysis)
> - **Prerequisites:** Kali Linux installation completed (bare metal or VM); access with default credentials (`kali/kali`); network connectivity for package downloads
> - **Output:** Hardened Kali environment, configured for Blue Team operations, Threat Hunting and Forensic Analysis; reduced operating system attack surface

---

## Introduction

A "fresh" Kali Linux installation is a powerful but unhardened system: publicly known default passwords (`kali/kali`), SSH exposed on port 22, no active firewall, kernel with permissive parameters. Using Kali in this state during an engagement is an operational risk: the attacker is as vulnerable as the target.

This folder documents the 20 essential steps to transform a clean installation into a secure, optimized environment ready for operations. The objective is twofold: reduce the operating system attack surface (defensive hardening) and configure monitoring and automation tools that transform Kali into a personal SOC-in-a-Box.

---

## Folder structure

| step | folder | objective |
| :---: | :--- | :--- |
| 01 | `01-update-your-system/` | full package and kernel update |
| 02 | `02-create-non-root-user/` | least privilege principle: standard user |
| 03 | `03-change-default-password/` | change default credentials `kali/kali` |
| 04 | `04-enable-firewall/` | ufw configuration: close unnecessary ports |
| 05 | `05-install-essential-tools/` | base toolset: htop, curl, tmux, net-tools |
| 06 | `06-secure-ssh-access/` | ssh hardening: non-standard port, no root login |
| 07 | `07-enable-automatic-updates/` | `unattended-upgrades` for automatic security patches |
| 08 | `08-install-monitoring-tools/` | system status dashboard (nagios/zabbix agent) |
| 09 | `09-customize-desktop-environment/` | ergonomics: xfce/gnome for long work sessions |
| 10 | `10-encrypt-sensitive-data/` | luks/veracrypt for engagement data protection |
| 11 | `11-perform-vulnerability-scans/` | openvas/gvm: vulnerability self-assessment |
| 12 | `12-schedule-regular-maintenance/` | cronjobs for automatic updates and disk cleanup |
| 13 | `13-harden-the-kernel/` | `sysctl.conf`: protection against dos, spoofing, flooding |
| 14 | `14-configure-intrusion-detection-systems/` | suricata ids: real-time attack detection |
| 15 | `15-test-defensive-tools/` | empirical validation of configured defenses |
| 16 | `16-automate-tasks/` | log backup scripts (tar) and system backup (rsync) |
| 17 | `17-join-kali-community/` | official kali linux forums and discord |
| 18 | `18-document-your-configuration/` | configuration change documentation (markdown/obsidian) |
| 19 | `19-backup-your-system/` | disaster recovery: rsync and timeshift |
| 20 | `20-setup-logwatch-system-monitoring/` | logwatch: aggregated daily report via email |

---

## Recommended execution flow

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

## Reference tools

| tool | type | step | main use case |
| :--- | :--- | :---: | :--- |
| `apt` / `unattended-upgrades` | package manager | 01, 07 | system update and automatic patches |
| `ufw` | firewall | 04 | firewall rules management (uncomplicated firewall) |
| `htop` | resource monitor | 05 | interactive cpu, ram, process visualization |
| `tmux` | terminal multiplexer | 05 | multiple sessions, persistence even on disconnect |
| `sshd_config` | ssh daemon | 06 | remote ssh access hardening |
| `cryptsetup` (luks) | disk encryption | 10 | block-level encryption for partitions and volumes |
| `VeraCrypt` | disk encryption | 10 | single volume encryption (cross-platform alternative) |
| `GVM` / `OpenVAS` | vulnerability scanner | 11 | local environment cve self-assessment |
| `sysctl` | kernel parameters | 13 | linux kernel network parameter hardening |
| `Suricata` | ids/ips | 14 | network intrusion detection with emerging threats rules |
| `rsync` | backup tool | 16, 19 | incremental file and directory synchronization |
| `Logwatch` | log aggregator | 20 | aggregated daily report from `/var/log` |
| `Timeshift` | snapshot tool | 19 | point-in-time system backup (similar to time machine) |

---

> **Note:** The documented steps were executed on Kali Linux Purple (version 2024.x) in a virtualized lab environment (VirtualBox). Some commands may require adjustments for bare-metal installations or different versions. The described configuration represents the author's personal choices and does not constitute a universal standard.
