> **English** | [Italiano](README.md)

# 06 - Secure SSH Access

> - **Phase:** System Setup - Remote Access Hardening
> - **Priority:** High - execute before exposing the system on untrusted networks
> - **Prerequisites:** SSH service installed (`sudo apt install openssh-server`); text editor (vim, nano)
> - **Estimated time:** 5 minutes

---

## Commands

Edit `/etc/ssh/sshd_config`:

```Bash
sudo vim /etc/ssh/sshd_config
```

Parameters to set or verify:

```Bash
Port 2222               # Change the standard port (choose a port > 1024)
PermitRootLogin no      # Deny direct root login
PasswordAuthentication yes   # Keep yes for now; set to no only after configuring SSH keys
MaxAuthTries 3          # Limit authentication attempts per connection
```

Restart the service to apply changes:

```Bash
sudo systemctl restart ssh
sudo systemctl status ssh    # Verify the service is active
```

To connect to the new port:

```Bash
ssh -p 2222 user@machine_ip
```

---

## Why do it?

Port 22 is the most attacked port in the world by automated bots and vulnerability scanners. The root account is the primary target of automated brute-force attacks. Changing the port reduces log noise; disabling root login eliminates the most attractive target.

## What happens next?

Connecting will require specifying the custom port. Automated bots that systematically scan port 22 will not find the service. Root brute-force attempts will be rejected regardless of the password.

## What's the risk if you don't?

The `/var/log/auth.log` file will fill with thousands of failed access attempts (log fatigue). The probability increases that a prolonged brute-force attack or common credential dictionary succeeds.

---

## Reference Tools

| `sshd_config` Parameter | Description |
| :--- | :--- |
| `Port` | SSH daemon listening port |
| `PermitRootLogin no` | Block direct root login (requires standard user + sudo) |
| `MaxAuthTries 3` | Maximum 3 attempts per connection before reset |
| `AllowUsers [name]` | Whitelist: only listed users can authenticate |
| `PubkeyAuthentication yes` | Enable public/private key authentication (more secure than password) |

---

> **Note:** After changing the port, update the UFW rule accordingly: `sudo ufw delete allow 22/tcp && sudo ufw allow 2222/tcp`. For maximum hardening, configure SSH key authentication (`ssh-keygen` + `ssh-copy-id`) and subsequently set `PasswordAuthentication no`.
