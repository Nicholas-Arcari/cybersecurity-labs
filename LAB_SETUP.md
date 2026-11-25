> [English](LAB_SETUP.en.md) | **Italiano**

# LAB_SETUP.md - topologia e configurazione del laboratorio

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
- [Target Web Containerizzati (Docker Compose)](#target-web-containerizzati-docker-compose)
- [Registrazione Demo con Asciinema](#registrazione-demo-con-asciinema)

---

## Requisiti hardware

| risorsa | minimo | raccomandato |
| :--- | :--- | :--- |
| ram totale host | 8 gb | 16 gb |
| cpu | quad-core, vt-x abilitato | 8 core, vt-x/amd-v |
| disco host | 100 gb liberi | 200 gb ssd |
| scheda di rete | 1x (nat sufficiente) | 1x (bridge richiede accesso lan) |

---

## Software di virtualizzazione

| software | versione usata | note |
| :--- | :--- | :--- |
| virtualbox | 7.0.x | hypervisor principale, gratuito |
| virtualbox extension pack | stessa versione | necessario per usb 3.0 e schede di rete avanzate |
| host os | qualsiasi (linux/windows/macos) | lab eseguito su host linux |

---

## Macchine virtuali

### Kali Linux (attaccante)

| parametro | valore |
| :--- | :--- |
| os | kali linux 2024.x (rolling) |
| ram | 4096 mb |
| cpu | 2 vcpu |
| disco | 80 gb (thin provisioned) |
| schede di rete | 2x (adapter 1: nat o bridge secondo il modulo) |
| snapshot pre-operativi | raccomandati prima di ogni sessione di exploitation |

### Windows 10 (target principale)

| parametro | valore |
| :--- | :--- |
| os | windows 10 pro x64 (non aggiornato, vulnerabile by design) |
| ram | 2048 mb |
| cpu | 2 vcpu |
| disco | 60 gb |
| configurazione sicurezza | firewall disabilitato, uac ridotto, smbv1 abilitato |
| utenti configurati | `Administrator` (password debole), `user1`, `svc_backup` |
| servizi esposti | smb (445), rdp (3389), http (8080), snmp (161 udp) |

### Ubuntu Linux (target secondario - PrivEsc Linux)

| parametro | valore |
| :--- | :--- |
| os | ubuntu server 20.04 lts |
| ram | 1024 mb |
| cpu | 1 vcpu |
| disco | 20 gb |
| configurazione sicurezza | configurazione intenzionalmente misconfigured per privesc |
| utenti configurati | `ubuntu` (low-privilege), `www-data` (web service) |
| servizi esposti | ssh (22), http (80), servizi con suid misconfigured |

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

## Configurazione NAT (moduli 01-02)

Utilizzata per: ricognizione passiva/attiva, vulnerability assessment, fasi che
non richiedono visibilita diretta sulla LAN reale.

### Indirizzi IP (NAT)

| vm | hostname | ip | ruolo |
| :--- | :--- | :--- | :--- |
| kali linux | kali | `10.0.2.15` | attaccante |
| windows 10 | win10-target | `10.0.2.3` | target primario |
| gateway virtualbox | - | `10.0.2.1` | default gateway |
| dhcp virtualbox | - | `10.0.2.2` | dhcp server |

### Configurazione VirtualBox (NAT)

```
VM Settings > Network > Adapter 1:
  - Attached to: NAT
  - (Avanzate) Port Forwarding: non necessario per traffico interno
```

### Port forwarding opzionale (accesso da host a VM in NAT)

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

## Configurazione network bridge (moduli 03-04)

Utilizzata per: exploitation attivo, privilege escalation, post-exploitation,
fasi che simulano un attaccante gia sulla stessa rete del target.

> **Nota di sicurezza:** In modalita Bridge le VM sono visibili sulla LAN fisica.
> Eseguire SEMPRE in ambiente di rete controllato (rete domestica isolata o VLAN dedicata).
> Mai in rete aziendale o pubblica.

### Indirizzi IP (bridge)

| vm | hostname | ip | ruolo |
| :--- | :--- | :--- | :--- |
| kali linux | kali | `192.168.0.110` | attaccante |
| windows 10 | win10-target | `192.168.0.109` | target primario |
| gateway lan | router | `192.168.0.1` | default gateway |
| subnet | - | `192.168.0.0/24` | segmento di lab |

### Configurazione VirtualBox (bridge)

```
VM Settings > Network > Adapter 1:
  - Attached to: Bridged Adapter
  - Name: [selezionare la NIC fisica dell'host]
  - Promiscuous Mode: Deny (o Allow VMs per scenari avanzati)
```

> Gli IP 192.168.0.109 e 192.168.0.110 possono variare. Assegnare IP statici
> o verificare con `ip a` (Kali) e `ipconfig` (Windows) a inizio sessione.

### Assegnazione IP statico su Kali (bridge)

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

| modulo | topologia | ip kali | ip target |
| :--- | :--- | :--- | :--- |
| `01-recon` | nat | 10.0.2.15 | 10.0.2.3 |
| `02-vulnerability-assessment` | nat | 10.0.2.15 | 10.0.2.3 |
| `03-web-attacks` | nat | 10.0.2.15 | 10.0.2.3 |
| `04-system-exploitation` | bridge | 192.168.0.110 | 192.168.0.109 |
| `05-social-engineering` | bridge | 192.168.0.110 | 192.168.0.109 |
| `06-wireless-security` | bridge | 192.168.0.110 | n/a (ap fisico) |
| `07-post-exploitation` | bridge | 192.168.0.110 | 192.168.0.109 |
| `08-defense-hardenings` | nat | 10.0.2.15 | n/a (self) |
| `09-digital-forensics` | nat | n/a | immagini disco locali |
| `10-cloud-security` | internet | n/a | endpoint cloud |

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

### Verifica connettivita (bridge)

```Bash
# Da Kali
ping 192.168.0.109 -c 3
nmap -sn 192.168.0.109
```

### Configurazione target Windows (script PowerShell - eseguire come administrator)

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

## Target web containerizzati (Docker compose)

Per i lab del modulo 03 (Web Attacks) e in parte del modulo 02, e disponibile un `docker-compose.yml` nella root della repository che fornisce target web containerizzati. Questo e **complementare** alla topologia VirtualBox - non la sostituisce.

### Cosa copre Docker compose

| servizio | porta | modulo | target per |
| :--- | :--- | :--- | :--- |
| dvwa | `localhost:8080` | 03-web-attacks | sqli, xss, command injection, csrf |
| dvga | `localhost:5013` | 03-web-attacks | graphql introspection, idor, batching |
| juice shop | `localhost:3000` | 03-web-attacks | owasp top 10 completa (100+ challenge) |

### Cosa richiede ancora VirtualBox

I lab di System Exploitation (modulo 04), Post-Exploitation (modulo 07), Wireless (modulo 06) e tutti gli scenari Windows-based richiedono le VM documentate nelle sezioni precedenti.

### Avvio rapido

```Bash
# Avviare tutti i target web
cd cybersecurity-labs/
docker compose up -d

# Avviare solo DVWA
docker compose up dvwa dvwa-db -d

# Verificare lo stato
docker compose ps

# Fermare tutto
docker compose down

# Fermare e rimuovere volumi (reset completo)
docker compose down -v
```

---

## Registrazione demo con asciinema

Per registrare sessioni terminale dimostrative dei lab, si utilizza [asciinema](https://asciinema.org/). Le registrazioni sono complementari agli screenshot (PoC statici) e mostrano il flusso operativo completo.

### Installazione

```Bash
sudo apt install asciinema
```

### Registrazione

```Bash
# Registrare una sessione (salva in locale come .cast)
asciinema rec demo_nmap_scan.cast

# Registrare con titolo e idle-time limitato (consigliato)
asciinema rec -t "Nmap 3-Phase Scan Pipeline" --idle-time-limit 3 nmap_pipeline.cast

# Terminare la registrazione
exit   # oppure Ctrl+D
```

### Embedding nei README (MkDocs)

Per includere una registrazione in un README visibile su MkDocs/GitHub Pages, usare il player JavaScript:

```html
<div id="demo-player"></div>
<script src="https://asciinema.org/a/XXXXX.js" id="asciicast-XXXXX" async></script>
```

Oppure in formato Markdown (compatibile GitHub):

```markdown
[![asciicast](https://asciinema.org/a/XXXXX.svg)](https://asciinema.org/a/XXXXX)
```

### Lab consigliati da registrare

| lab | file | durata target |
| :--- | :--- | :--- |
| nmap 3-phase scan | `01-recon/.../nmap/` | 2-3 min |
| sqli manuale su dvwa | `03-web-attacks/.../sql-injection/` | 3-5 min |
| winpeas enumeration | `04-system-exploitation/.../winpeas/` | 2-3 min |
| hashcat mask attack | `04-system-exploitation/.../hashcat/` | 1-2 min |
| mimikatz credential dump | `07-post-exploitation/.../mimikatz/` | 2-3 min |

---

> **Disclaimer:** Questo laboratorio e configurato intenzionalmente in modo vulnerabile
> per scopi educativi. Non replicare questa configurazione su sistemi di produzione.
> Eseguire sempre in ambiente isolato. Gli IP e le configurazioni documentati si
> riferiscono esclusivamente all'ambiente virtualizzato di test.
