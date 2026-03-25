# LAB_SETUP.md - Topologia e Configurazione del Laboratorio

> Documento tecnico di riferimento per la riproduzione dell'ambiente di laboratorio
> utilizzato in questo repository. Tutte le sessioni di testing sono state eseguite
> in ambiente virtualizzato isolato dalla rete di produzione.

---

## Indice

- [Requisiti hardware](#requisiti-hardware)
- [Software di virtualizzazione](#software-di-virtualizzazione)
- [Macchine virtuali](#macchine-virtuali)
- [Topologie di rete](#topologie-di-rete)
- [Configurazione NAT (Moduli 01-02)](#configurazione-nat-moduli-01-02)
- [Configurazione Network Bridge (Moduli 03-04)](#configurazione-network-bridge-moduli-03-04)
- [Moduli per topologia](#moduli-per-topologia)
- [Snapshot e gestione VM](#snapshot-e-gestione-vm)
- [Riprodurre il lab](#riprodurre-il-lab)

---

## Requisiti hardware

| Risorsa | Minimo | Raccomandato |
| :--- | :--- | :--- |
| RAM totale host | 8 GB | 16 GB |
| CPU | Quad-core, VT-x abilitato | 8 core, VT-x/AMD-V |
| Disco host | 100 GB liberi | 200 GB SSD |
| Scheda di rete | 1x (NAT sufficiente) | 1x (Bridge richiede accesso LAN) |

---

## Software di virtualizzazione

| Software | Versione usata | Note |
| :--- | :--- | :--- |
| VirtualBox | 7.0.x | Hypervisor principale, gratuito |
| VirtualBox Extension Pack | stessa versione | Necessario per USB 3.0 e schede di rete avanzate |
| Host OS | Qualsiasi (Linux/Windows/macOS) | Lab eseguito su host Linux |

---

## Macchine virtuali

### Kali Linux (Attaccante)

| Parametro | Valore |
| :--- | :--- |
| OS | Kali Linux 2024.x (rolling) |
| RAM | 4096 MB |
| CPU | 2 vCPU |
| Disco | 80 GB (thin provisioned) |
| Schede di rete | 2x (Adapter 1: NAT o Bridge secondo il modulo) |
| Snapshot pre-operativi | Raccomandati prima di ogni sessione di exploitation |

### Windows 10 (Target principale)

| Parametro | Valore |
| :--- | :--- |
| OS | Windows 10 Pro x64 (non aggiornato, vulnerabile by design) |
| RAM | 2048 MB |
| CPU | 2 vCPU |
| Disco | 60 GB |
| Configurazione sicurezza | Firewall disabilitato, UAC ridotto, SMBv1 abilitato |
| Utenti configurati | `Administrator` (password debole), `user1`, `svc_backup` |
| Servizi esposti | SMB (445), RDP (3389), HTTP (8080), SNMP (161 UDP) |

### Ubuntu Linux (Target secondario - PrivEsc Linux)

| Parametro | Valore |
| :--- | :--- |
| OS | Ubuntu Server 20.04 LTS |
| RAM | 1024 MB |
| CPU | 1 vCPU |
| Disco | 20 GB |
| Configurazione sicurezza | Configurazione intenzionalmente misconfigured per PrivEsc |
| Utenti configurati | `ubuntu` (low-privilege), `www-data` (web service) |
| Servizi esposti | SSH (22), HTTP (80), servizi con SUID misconfigured |

---

## Topologie di rete

Il laboratorio ha utilizzato due modalita di rete distinte a seconda della fase del test.
La scelta dipende dall'obiettivo: NAT per isolamento massimo, Bridge per simulare
scenari realistici su segmento LAN.

```
+-----------------------------------------------------------+
|                    TOPOLOGIA NAT                          |
|                  (Moduli 01-02)                           |
|                                                           |
|  [Host OS] <---NAT---> [VirtualBox NAT Gateway]           |
|                               |                           |
|                    +----------+----------+                |
|                    |                     |                |
|             [Kali Linux]        [Windows 10]              |
|            10.0.2.15             10.0.2.3                 |
|         (attaccante)            (target)                  |
|                                                           |
|  Gateway NAT: 10.0.2.1   DHCP: 10.0.2.2                   |
+-----------------------------------------------------------+

+-----------------------------------------------------------+
|               TOPOLOGIA NETWORK BRIDGE                    |
|                  (Moduli 03-04)                           |
|                                                           |
|  [Router LAN] <---> [Host OS NIC] <---> [VirtualBox]      |
|       |                                     |             |
|  [Altri host LAN]              +------------+----------+  |
|                                |                       |  |
|                         [Kali Linux]        [Windows]  |  |
|                        192.168.0.110      192.168.0.109|  |
|                         (attaccante)         (target)  |  |
|                                                        |  |
|  Gateway: 192.168.0.1   Subnet: 192.168.0.0/24         |  |
+-----------------------------------------------------------+
```

---

## Configurazione NAT (Moduli 01-02)

Utilizzata per: ricognizione passiva/attiva, vulnerability assessment, fasi che
non richiedono visibilita diretta sulla LAN reale.

### Indirizzi IP (NAT)

| VM | Hostname | IP | Ruolo |
| :--- | :--- | :--- | :--- |
| Kali Linux | kali | `10.0.2.15` | Attaccante |
| Windows 10 | WIN10-TARGET | `10.0.2.3` | Target primario |
| Gateway VirtualBox | - | `10.0.2.1` | Default gateway |
| DHCP VirtualBox | - | `10.0.2.2` | DHCP server |

### Configurazione VirtualBox (NAT)

```
VM Settings > Network > Adapter 1:
  - Attached to: NAT
  - (Avanzate) Port Forwarding: non necessario per traffico interno
```

### Port Forwarding opzionale (accesso da host a VM in NAT)

```
Host: 127.0.0.1:2222  -->  Guest: 10.0.2.15:22   (SSH Kali)
Host: 127.0.0.1:8080  -->  Guest: 10.0.2.3:8080  (HTTP Windows)
Host: 127.0.0.1:3389  -->  Guest: 10.0.2.3:3389  (RDP Windows)
```

Configurazione in VirtualBox:
```
VM Settings > Network > Adapter 1 > Avanzate > Port Forwarding > [+]
```

---

## Configurazione Network Bridge (Moduli 03-04)

Utilizzata per: exploitation attivo, privilege escalation, post-exploitation,
fasi che simulano un attaccante gia sulla stessa rete del target.

> **Nota di sicurezza:** In modalita Bridge le VM sono visibili sulla LAN fisica.
> Eseguire SEMPRE in ambiente di rete controllato (rete domestica isolata o VLAN dedicata).
> Mai in rete aziendale o pubblica.

### Indirizzi IP (Bridge)

| VM | Hostname | IP | Ruolo |
| :--- | :--- | :--- | :--- |
| Kali Linux | kali | `192.168.0.110` | Attaccante |
| Windows 10 | WIN10-TARGET | `192.168.0.109` | Target primario |
| Gateway LAN | router | `192.168.0.1` | Default gateway |
| Subnet | - | `192.168.0.0/24` | Segmento di lab |

### Configurazione VirtualBox (Bridge)

```
VM Settings > Network > Adapter 1:
  - Attached to: Bridged Adapter
  - Name: [selezionare la NIC fisica dell'host]
  - Promiscuous Mode: Deny (o Allow VMs per scenari avanzati)
```

> Gli IP 192.168.0.109 e 192.168.0.110 possono variare. Assegnare IP statici
> o verificare con `ip a` (Kali) e `ipconfig` (Windows) a inizio sessione.

### Assegnazione IP statico su Kali (Bridge)

```Bash
sudo ip addr add 192.168.0.110/24 dev eth0
sudo ip route add default via 192.168.0.1
```

Configurazione persistente in `/etc/network/interfaces`:

```
auto eth0
iface eth0 inet static
  address 192.168.0.110
  netmask 255.255.255.0
  gateway 192.168.0.1
```

---

## Moduli per topologia

| Modulo | Topologia | IP Kali | IP Target |
| :--- | :--- | :--- | :--- |
| `01-recon` | NAT | 10.0.2.15 | 10.0.2.3 |
| `02-vulnerability-assessment` | NAT | 10.0.2.15 | 10.0.2.3 |
| `03-web-attacks` | NAT | 10.0.2.15 | 10.0.2.3 |
| `04-system-exploitation` | Bridge | 192.168.0.110 | 192.168.0.109 |
| `05-social-engineering` | Bridge | 192.168.0.110 | 192.168.0.109 |
| `06-wireless-security` | Bridge | 192.168.0.110 | N/A (AP fisico) |
| `07-post-exploitation` | Bridge | 192.168.0.110 | 192.168.0.109 |
| `08-defense-hardenings` | NAT | 10.0.2.15 | N/A (self) |
| `09-digital-forensics` | NAT | N/A | immagini disco locali |
| `10-cloud-security` | Internet | N/A | endpoint cloud |

---

## Snapshot e gestione VM

### Strategia snapshot raccomandata

```
[SNAPSHOT BASE]                          <- stato pulito post-installazione
      |
      +-- [SNAPSHOT PRE-RECON]           <- dopo configurazione rete
      |         |
      |         +-- [SNAPSHOT PRE-EXPLOIT] <- dopo vuln assessment
      |                   |
      |                   +-- [SNAPSHOT POST-SHELL] <- dopo initial access
      |                             |
      |                             +-- [SNAPSHOT PRE-PRIVESC]
```

### Comandi VirtualBox CLI (vboxmanage)

```Bash
# Creare snapshot
vboxmanage snapshot "Kali Linux" take "pre-exploitation" --description "Prima di MS17-010"

# Listare snapshot
vboxmanage snapshot "Kali Linux" list

# Ripristinare snapshot
vboxmanage snapshot "Kali Linux" restore "pre-exploitation"

# Eliminare snapshot
vboxmanage snapshot "Kali Linux" delete "pre-exploitation"
```

---

## Riprodurre il lab

### Prerequisiti

```Bash
# Verificare virtualizzazione hardware abilitata
grep -E '(vmx|svm)' /proc/cpuinfo | head -1

# Installare VirtualBox (Debian/Ubuntu/Kali)
sudo apt install virtualbox virtualbox-ext-pack

# Scaricare immagini
# Kali Linux:   https://www.kali.org/get-kali/#kali-virtual-machines (OVA preconfigurata)
# Windows 10:   https://www.microsoft.com/evalcenter/download-windows-10-enterprise (ISO eval 90gg)
```

### Sequenza di setup

1. Importare OVA Kali Linux in VirtualBox (`File > Import Appliance`)
2. Installare Windows 10 da ISO in nuova VM con parametri da tabella sopra
3. Configurare Windows 10 come target (disabilitare firewall, abilitare SMBv1, creare utenti)
4. Scegliere la topologia di rete in base al modulo da eseguire
5. Fare uno snapshot base di entrambe le VM prima di iniziare
6. Verificare connettivita con `ping` prima di ogni sessione

### Verifica connettivita (NAT)

```Bash
# Da Kali
ping 10.0.2.3 -c 3
nmap -sn 10.0.2.3
```

### Verifica connettivita (Bridge)

```Bash
# Da Kali
ping 192.168.0.109 -c 3
nmap -sn 192.168.0.109
```

### Configurazione target Windows (script PowerShell - eseguire come Administrator)

```Bash
# Disabilitare firewall
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

# Abilitare SMBv1 (per test MS17-010)
Set-SmbServerConfiguration -EnableSMB1Protocol $true -Force

# Abilitare RDP
Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name fDenyTSConnections -Value 0
Enable-NetFirewallRule -DisplayGroup "Remote Desktop"

# Creare utente low-privilege per test
net user user1 Password123! /add
net user svc_backup ServicePass1! /add
net localgroup "Remote Desktop Users" user1 /add
```

---

> **Disclaimer:** Questo laboratorio e configurato intenzionalmente in modo vulnerabile
> per scopi educativi. Non replicare questa configurazione su sistemi di produzione.
> Eseguire sempre in ambiente isolato. Gli IP e le configurazioni documentati si
> riferiscono esclusivamente all'ambiente virtualizzato di test.
