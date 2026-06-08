> **English** | [Italiano](README.md)

# 04 - Enable the Firewall (UFW)

> - **Phase:** System Setup - Network Hardening
> - **Priority:** High - execute before connecting the system to untrusted networks
> - **Prerequisites:** Sudo access; `ufw` package (included in Kali by default)
> - **Estimated time:** 3 minutes

---

## Commands

```Bash
sudo apt install ufw          # Install (if not present)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp         # Only if using SSH - replace with custom port (step 06)
sudo ufw enable
sudo ufw status verbose       # Verify active rules
```

---

## Why do it?

Kali Linux starts several network services during boot (SSH, RPC services, any installed tools with listeners). Without a firewall, all listening ports are accessible from any host on the local network. In shared environments (corporate networks, public hotspots, lab VPNs), this attack surface is unacceptable.

## What happens next?

The system will silently reject incoming connection attempts not explicitly authorized. Only ports defined in UFW rules will be accessible. Outbound traffic remains unrestricted by default, allowing normal operational use.

## What's the risk if you don't?

You expose potentially vulnerable services to the entire network. An attacker could exploit a forgotten open port (e.g., a Metasploit listener left active from a previous session) to gain system access.

---

## Reference Tools

| Command | Description |
| :--- | :--- |
| `sudo ufw status verbose` | Show active rules and firewall status |
| `sudo ufw allow <port>/tcp` | Open a specific inbound port |
| `sudo ufw delete allow <port>/tcp` | Remove a previously added rule |
| `sudo ufw logging on` | Enable logging of blocked connections in `/var/log/ufw.log` |

---

> **Note:** UFW is a simplified frontend for `iptables`. For more complex environments (VPN, Docker, inter-VM connections), more granular rules may be necessary. Always verify rules with `ufw status verbose` after every change.
