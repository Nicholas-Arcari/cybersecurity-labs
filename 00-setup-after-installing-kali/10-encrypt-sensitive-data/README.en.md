> **English** | [Italiano](README.md)

# 10 - Encrypt Sensitive Data

> - **Phase:** System Setup - Data Protection & Encryption
> - **Priority:** High - mandatory if the system contains engagement data or client reports
> - **Prerequisites:** Available partition or disk for encryption; `cryptsetup` installed (included in Kali)
> - **Estimated time:** 10-30 minutes (depends on volume size)

---

## Commands

### Option 1: LUKS (full partition encryption)

```Bash
# WARNING: destroys all data on the specified partition
sudo cryptsetup luksFormat /dev/sdX           # Replace /dev/sdX with the correct partition
sudo cryptsetup open /dev/sdX encrypted_vol   # Open and map
sudo mkfs.ext4 /dev/mapper/encrypted_vol      # Format
sudo mount /dev/mapper/encrypted_vol /mnt/secure
```

### Option 2: VeraCrypt (encrypted volume as file)

```Bash
sudo apt install veracrypt
veracrypt    # Graphical interface for creating and mounting encrypted volumes
```

---

## Why do it?

During a penetration test or forensic analysis, the system contains extremely sensitive data: client credentials, captured NTLM hashes, screenshots of compromised systems, confidential reports. If the laptop is lost or stolen, this data is directly accessible by mounting the disk on another system.

## What happens next?

Data is unreadable without the decryption key (password or keyfile), even if the hard disk is physically removed and read on another PC with forensic tools. Protection is at the hardware/filesystem level, independent of operating system authentication.

## What's the risk if you don't?

If you lose the laptop or it gets stolen, anyone can mount the disk and read all files, reports, SSH keys and credentials. In professional activities, this exposes you to legal liability (GDPR, NDA agreements) for unauthorized disclosure of client confidential data.

---

## Reference Tools

| Tool | Type | Pros | Cons |
| :--- | :--- | :--- | :--- |
| `LUKS` + `cryptsetup` | Partition encryption | Integrated in the Linux kernel, maximum performance | Requires dedicated partition, Linux-only format |
| `VeraCrypt` | Encrypted volume (file or partition) | Cross-platform (Linux/Win/Mac), hidden volumes | Requires separate installation |
| `GPG` | Single file encryption | Ideal for reports and text files | Not suitable for large volumes |

---

> **Note:** Store the decryption password in a secure password manager (e.g., KeePassXC with database file on separate media). A lost password on a LUKS volume means permanent and irrecoverable data loss.
