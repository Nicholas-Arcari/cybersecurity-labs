#!/usr/bin/env bash
# Lab Setup Automation Script - Cybersecurity Labs
# Automates VirtualBox VM creation, network configuration and snapshot management.
#
# Prerequisites:
#   - VirtualBox 7.0+ installed (vboxmanage in PATH)
#   - Kali Linux OVA downloaded
#   - Windows 10 ISO downloaded
#
# Usage:
#   ./lab-setup.sh --help
#   ./lab-setup.sh create-all
#   ./lab-setup.sh snapshot-all "pre-exploitation"
#   ./lab-setup.sh network nat
#   ./lab-setup.sh network bridge --interface eth0
#   ./lab-setup.sh verify
#   ./lab-setup.sh destroy-all   (WARNING: irreversible)

set -euo pipefail

# ============================================================
# Configuration - edit these paths before first run
# ============================================================
KALI_OVA="${KALI_OVA:-$HOME/Downloads/kali-linux-2024.4-virtualbox-amd64.ova}"
WIN10_ISO="${WIN10_ISO:-$HOME/Downloads/Win10_22H2_English_x64.iso}"

KALI_VM="Kali-Linux-Lab"
WIN10_VM="Win10-Target"
UBUNTU_VM="Ubuntu-PrivEsc"

KALI_RAM=4096
KALI_CPU=2
KALI_DISK=81920   # MB (80 GB)

WIN10_RAM=2048
WIN10_CPU=2
WIN10_DISK=61440  # MB (60 GB)

UBUNTU_RAM=1024
UBUNTU_CPU=1
UBUNTU_DISK=20480 # MB (20 GB)

# Network configuration
NAT_NETWORK="10.0.2.0/24"
BRIDGE_INTERFACE="${BRIDGE_INTERFACE:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# ============================================================
# Helper functions
# ============================================================
log_info()  { echo -e "${CYAN}[INFO]${NC} $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

check_vbox() {
    if ! command -v vboxmanage &>/dev/null; then
        log_error "VirtualBox not found. Install with: sudo apt install virtualbox virtualbox-ext-pack"
        exit 1
    fi
    local version
    version=$(vboxmanage --version)
    log_info "VirtualBox version: $version"
}

vm_exists() {
    vboxmanage showvminfo "$1" &>/dev/null 2>&1
}

# ============================================================
# VM Creation
# ============================================================
create_kali() {
    if vm_exists "$KALI_VM"; then
        log_warn "$KALI_VM already exists, skipping"
        return
    fi

    if [ ! -f "$KALI_OVA" ]; then
        log_error "Kali OVA not found: $KALI_OVA"
        log_info "Download from: https://www.kali.org/get-kali/#kali-virtual-machines"
        log_info "Set path: export KALI_OVA=/path/to/kali.ova"
        return 1
    fi

    log_info "Importing Kali Linux from OVA..."
    vboxmanage import "$KALI_OVA" --vsys 0 --vmname "$KALI_VM" \
        --memory "$KALI_RAM" --cpus "$KALI_CPU"

    # Add second network adapter (host-only for inter-VM comms)
    vboxmanage modifyvm "$KALI_VM" --nic2 hostonly

    log_ok "$KALI_VM created successfully"
}

create_win10() {
    if vm_exists "$WIN10_VM"; then
        log_warn "$WIN10_VM already exists, skipping"
        return
    fi

    if [ ! -f "$WIN10_ISO" ]; then
        log_error "Windows 10 ISO not found: $WIN10_ISO"
        log_info "Download from: https://www.microsoft.com/evalcenter/download-windows-10-enterprise"
        log_info "Set path: export WIN10_ISO=/path/to/Win10.iso"
        return 1
    fi

    log_info "Creating Windows 10 Target VM..."
    vboxmanage createvm --name "$WIN10_VM" --ostype "Windows10_64" --register

    # Hardware
    vboxmanage modifyvm "$WIN10_VM" \
        --memory "$WIN10_RAM" --cpus "$WIN10_CPU" \
        --vram 128 --graphicscontroller vboxsvga \
        --audio-driver pulse --audio-out on

    # Storage
    local vm_dir
    vm_dir=$(vboxmanage showvminfo "$WIN10_VM" --machinereadable | grep "CfgFile" | cut -d'"' -f2 | xargs dirname)
    vboxmanage createhd --filename "$vm_dir/$WIN10_VM.vdi" \
        --size "$WIN10_DISK" --variant Standard

    vboxmanage storagectl "$WIN10_VM" --name "SATA" --add sata --controller IntelAhci
    vboxmanage storageattach "$WIN10_VM" --storagectl "SATA" --port 0 \
        --device 0 --type hdd --medium "$vm_dir/$WIN10_VM.vdi"

    # CD-ROM with ISO
    vboxmanage storagectl "$WIN10_VM" --name "IDE" --add ide
    vboxmanage storageattach "$WIN10_VM" --storagectl "IDE" --port 0 \
        --device 0 --type dvddrive --medium "$WIN10_ISO"

    # Boot order
    vboxmanage modifyvm "$WIN10_VM" --boot1 dvd --boot2 disk --boot3 none --boot4 none

    log_ok "$WIN10_VM created successfully"
    log_warn "After installing Windows, run the PowerShell target setup script from LAB_SETUP.md"
}

create_ubuntu() {
    if vm_exists "$UBUNTU_VM"; then
        log_warn "$UBUNTU_VM already exists, skipping"
        return
    fi

    log_info "Creating Ubuntu PrivEsc VM..."
    vboxmanage createvm --name "$UBUNTU_VM" --ostype "Ubuntu_64" --register

    vboxmanage modifyvm "$UBUNTU_VM" \
        --memory "$UBUNTU_RAM" --cpus "$UBUNTU_CPU" \
        --vram 16 --graphicscontroller vmsvga

    local vm_dir
    vm_dir=$(vboxmanage showvminfo "$UBUNTU_VM" --machinereadable | grep "CfgFile" | cut -d'"' -f2 | xargs dirname)
    vboxmanage createhd --filename "$vm_dir/$UBUNTU_VM.vdi" \
        --size "$UBUNTU_DISK" --variant Standard

    vboxmanage storagectl "$UBUNTU_VM" --name "SATA" --add sata --controller IntelAhci
    vboxmanage storageattach "$UBUNTU_VM" --storagectl "SATA" --port 0 \
        --device 0 --type hdd --medium "$vm_dir/$UBUNTU_VM.vdi"

    log_ok "$UBUNTU_VM created successfully"
}

# ============================================================
# Network Configuration
# ============================================================
set_network_nat() {
    log_info "Configuring NAT topology (Modules 01-03)..."

    for vm in "$KALI_VM" "$WIN10_VM"; do
        if vm_exists "$vm"; then
            vboxmanage modifyvm "$vm" --nic1 nat
            log_ok "$vm -> NAT"
        fi
    done

    # Port forwarding for Kali SSH
    vboxmanage modifyvm "$KALI_VM" --natpf1 "ssh,tcp,,2222,,22" 2>/dev/null || true
    # Port forwarding for Windows HTTP/RDP
    vboxmanage modifyvm "$WIN10_VM" --natpf1 "http,tcp,,8080,,8080" 2>/dev/null || true
    vboxmanage modifyvm "$WIN10_VM" --natpf1 "rdp,tcp,,3389,,3389" 2>/dev/null || true

    log_ok "NAT topology configured. Port forwarding: SSH=2222, HTTP=8080, RDP=3389"
}

set_network_bridge() {
    local interface="${1:-$BRIDGE_INTERFACE}"

    if [ -z "$interface" ]; then
        log_info "Available network interfaces:"
        vboxmanage list bridgedifs | grep "^Name:" | sed 's/Name: */  /'
        log_error "Specify interface: $0 network bridge --interface <name>"
        return 1
    fi

    log_info "Configuring Bridge topology (Modules 04-07) on $interface..."

    for vm in "$KALI_VM" "$WIN10_VM"; do
        if vm_exists "$vm"; then
            vboxmanage modifyvm "$vm" --nic1 bridged --bridgeadapter1 "$interface"
            log_ok "$vm -> Bridge ($interface)"
        fi
    done

    log_ok "Bridge topology configured on $interface"
    log_warn "Assign static IPs or check with: ip a (Kali) / ipconfig (Windows)"
}

# ============================================================
# Snapshot Management
# ============================================================
snapshot_all() {
    local name="${1:-base}"
    local desc="${2:-Automated snapshot by lab-setup.sh}"

    for vm in "$KALI_VM" "$WIN10_VM" "$UBUNTU_VM"; do
        if vm_exists "$vm"; then
            log_info "Creating snapshot '$name' for $vm..."
            vboxmanage snapshot "$vm" take "$name" --description "$desc"
            log_ok "$vm snapshot '$name' created"
        fi
    done
}

restore_all() {
    local name="${1:-base}"

    for vm in "$KALI_VM" "$WIN10_VM" "$UBUNTU_VM"; do
        if vm_exists "$vm"; then
            log_info "Restoring snapshot '$name' for $vm..."
            vboxmanage snapshot "$vm" restore "$name"
            log_ok "$vm restored to '$name'"
        fi
    done
}

list_snapshots() {
    for vm in "$KALI_VM" "$WIN10_VM" "$UBUNTU_VM"; do
        if vm_exists "$vm"; then
            echo -e "\n${CYAN}=== $vm ===${NC}"
            vboxmanage snapshot "$vm" list 2>/dev/null || echo "  (no snapshots)"
        fi
    done
}

# ============================================================
# Verification
# ============================================================
verify() {
    log_info "Lab environment verification"
    echo ""

    for vm in "$KALI_VM" "$WIN10_VM" "$UBUNTU_VM"; do
        if vm_exists "$vm"; then
            local state
            state=$(vboxmanage showvminfo "$vm" --machinereadable | grep "VMState=" | cut -d'"' -f2)
            local ram
            ram=$(vboxmanage showvminfo "$vm" --machinereadable | grep "memory=" | cut -d'=' -f2)
            local nic
            nic=$(vboxmanage showvminfo "$vm" --machinereadable | grep "nic1=" | cut -d'"' -f2)

            echo -e "  ${GREEN}[OK]${NC} $vm"
            echo "       State: $state | RAM: ${ram}MB | NIC1: $nic"
        else
            echo -e "  ${RED}[--]${NC} $vm (not found)"
        fi
    done

    # Check Docker targets
    echo ""
    if command -v docker &>/dev/null; then
        local running
        running=$(docker ps --format '{{.Names}}' 2>/dev/null | grep -cE "(dvwa|dvga|juice)" || echo "0")
        log_info "Docker web targets running: $running"
    else
        log_warn "Docker not installed (optional - web targets only)"
    fi
}

# ============================================================
# Cleanup
# ============================================================
destroy_all() {
    log_warn "This will PERMANENTLY DELETE all lab VMs and their disks!"
    read -rp "Type 'DELETE' to confirm: " confirm
    if [ "$confirm" != "DELETE" ]; then
        log_info "Aborted"
        return
    fi

    for vm in "$KALI_VM" "$WIN10_VM" "$UBUNTU_VM"; do
        if vm_exists "$vm"; then
            # Power off if running
            vboxmanage controlvm "$vm" poweroff 2>/dev/null || true
            sleep 1
            vboxmanage unregistervm "$vm" --delete
            log_ok "$vm deleted"
        fi
    done
}

# ============================================================
# Usage
# ============================================================
usage() {
    cat <<EOF
${CYAN}Lab Setup Automation - Cybersecurity Labs${NC}

Usage: $0 <command> [options]

Commands:
  create-all                    Create all lab VMs (Kali, Win10, Ubuntu)
  create-kali                   Create Kali Linux VM from OVA
  create-win10                  Create Windows 10 Target VM from ISO
  create-ubuntu                 Create Ubuntu PrivEsc VM

  network nat                   Switch all VMs to NAT topology (Modules 01-03)
  network bridge [--interface]  Switch all VMs to Bridge topology (Modules 04-07)

  snapshot-all <name> [desc]    Create snapshot for all VMs
  restore-all <name>            Restore all VMs to named snapshot
  list-snapshots                List all snapshots

  verify                        Verify lab environment status
  destroy-all                   Delete all lab VMs (IRREVERSIBLE)

Environment variables:
  KALI_OVA          Path to Kali Linux OVA (default: ~/Downloads/kali-*.ova)
  WIN10_ISO         Path to Windows 10 ISO (default: ~/Downloads/Win10_*.iso)
  BRIDGE_INTERFACE  Network interface for bridge mode

Examples:
  $0 create-all
  $0 network nat
  $0 snapshot-all "pre-exploitation" "Before MS17-010 test"
  $0 network bridge --interface eth0
  $0 verify
EOF
}

# ============================================================
# Main
# ============================================================
main() {
    check_vbox

    case "${1:-}" in
        create-all)
            create_kali
            create_win10
            create_ubuntu
            ;;
        create-kali)    create_kali ;;
        create-win10)   create_win10 ;;
        create-ubuntu)  create_ubuntu ;;
        network)
            case "${2:-}" in
                nat)    set_network_nat ;;
                bridge) set_network_bridge "${4:-}" ;;  # --interface <name>
                *)      log_error "Usage: $0 network <nat|bridge> [--interface <name>]" ;;
            esac
            ;;
        snapshot-all)   snapshot_all "${2:-base}" "${3:-}" ;;
        restore-all)    restore_all "${2:-base}" ;;
        list-snapshots) list_snapshots ;;
        verify)         verify ;;
        destroy-all)    destroy_all ;;
        -h|--help|"")   usage ;;
        *)              log_error "Unknown command: $1"; usage; exit 1 ;;
    esac
}

main "$@"
