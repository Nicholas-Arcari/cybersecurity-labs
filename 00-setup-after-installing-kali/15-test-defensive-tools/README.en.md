> **English** | [Italiano](README.md)

# 15 - Test Defensive Tools

> - **Phase:** System Setup - Defense Validation (Defense Testing)
> - **Priority:** High - unvalidated configuration is a false sense of security
> - **Prerequisites:** Firewall (step 04), SSH hardening (step 06), IDS (step 14) configured; a target VM or the local machine as target
> - **Estimated time:** 30-60 minutes for a complete test

---

## Approach

Unlike other steps, this one does not have a single command: it is an empirical validation phase. The objective is to generate controlled test traffic towards your own system and verify that defenses respond as expected.

```Bash
# Test 1: verify firewall blocks closed ports
nmap -sV 127.0.0.1                          # From local: visible open ports
nmap -sV [machine_IP] -p 1-65535            # From another VM: only UFW-allowed ports

# Test 2: verify SSH responds on the new port
ssh -p 2222 user@[IP]          # Should work
ssh -p 22 user@[IP]            # Should be rejected (port closed)

# Test 3: verify IDS detects the port scan
sudo tail -f /var/log/suricata/fast.log &    # Open log in background
nmap -sS [machine_IP]                        # Launch scan from another VM
# -> Suricata should generate alerts for "ET SCAN"

# Test 4: verify SSH root login blocked
ssh root@[IP] -p 2222    # Should be rejected with "Permission denied"
```

---

## Why do it?

Configuring a firewall or IDS is not enough: you need empirical confirmation that they work. A UFW rule with a typo, an unreloaded sshd_config parameter, an outdated Suricata rule: these are all scenarios where you believe you are protected but you are not.

## What happens next?

You have objective, evidence-based confirmation that the configured defenses detect and block simulated attacks. Each passed test is a validated requirement; each failed test is a problem to fix before exposing the system to real environments.

## What's the risk if you don't?

"False sense of security": the system appears correctly configured but a hidden misconfiguration leaves it exposed. Discovering this during a real engagement, when the attacker machine has been compromised, is an operational disaster.

---

## Validation Checklist

| Test | Command | Expected Result |
| :--- | :--- | :--- |
| Firewall active | `sudo ufw status` | `Status: active` |
| Closed ports | `nmap [IP]` from another VM | Only authorized ports visible |
| SSH custom port | `ssh -p 2222 user@[IP]` | Login successful |
| SSH root blocked | `ssh root@[IP] -p 2222` | `Permission denied` |
| IDS port scan alert | `nmap -sS [IP]` + `fast.log` | ET SCAN alert in Suricata |
| Kernel hardening | `sysctl net.ipv4.tcp_syncookies` | `= 1` |

---

> **Note:** Tests should preferably be executed from a separate VM on the same network (not from localhost) to simulate an external attacker's perspective. For a more realistic test, use the Windows VM used in the rest of the lab as the source of simulated attacks.
