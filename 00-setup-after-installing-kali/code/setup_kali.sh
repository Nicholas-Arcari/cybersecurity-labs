#!/bin/bash
# setup_kali.sh - Automazione setup post-installazione Kali Linux
# Eseguire come utente non-root con sudo disponibile
# Uso: chmod +x setup_kali.sh && sudo ./setup_kali.sh

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()    { echo -e "${GREEN}[+]${NC} $1"; }
warn()   { echo -e "${YELLOW}[!]${NC} $1"; }
error()  { echo -e "${RED}[-]${NC} $1"; exit 1; }

[[ $EUID -ne 0 ]] && error "Eseguire come root (sudo ./setup_kali.sh)"

# --- Passo 1: Aggiornamento sistema ---
log "Aggiornamento sistema..."
apt-get update -qq && apt-get upgrade -y -qq
apt-get dist-upgrade -y -qq

# --- Passo 2: Tool essenziali ---
log "Installazione tool essenziali..."
TOOLS=(
    curl wget git vim tmux
    net-tools dnsutils whois
    nmap masscan enum4linux-ng
    gobuster ffuf nikto
    john hashcat
    python3-pip python3-venv
    fail2ban ufw logwatch
    auditd rkhunter
)
apt-get install -y -qq "${TOOLS[@]}"

# --- Passo 3: Firewall UFW ---
log "Configurazione UFW..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw --force enable
log "UFW attivo. Stato:"
ufw status verbose

# --- Passo 4: SSH hardening ---
log "Hardening SSH..."
SSHD_CONF="/etc/ssh/sshd_config"
cp "$SSHD_CONF" "${SSHD_CONF}.bak.$(date +%F)"

sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' "$SSHD_CONF"
sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' "$SSHD_CONF"
sed -i 's/^#*MaxAuthTries.*/MaxAuthTries 3/' "$SSHD_CONF"
sed -i 's/^#*X11Forwarding.*/X11Forwarding no/' "$SSHD_CONF"

systemctl restart ssh
log "SSH riconfigurato (backup in ${SSHD_CONF}.bak.*)"

# --- Passo 5: Kernel hardening (sysctl) ---
log "Hardening kernel via sysctl..."
cat >> /etc/sysctl.d/99-kali-lab.conf <<'EOF'
# Network hardening
net.ipv4.ip_forward = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.rp_filter = 1
net.ipv4.tcp_syncookies = 1
net.ipv6.conf.all.disable_ipv6 = 1

# Memory hardening
kernel.randomize_va_space = 2
kernel.dmesg_restrict = 1
fs.suid_dumpable = 0
EOF
sysctl -p /etc/sysctl.d/99-kali-lab.conf -q

# --- Passo 6: fail2ban ---
log "Attivazione fail2ban..."
systemctl enable fail2ban
systemctl start fail2ban

# --- Passo 7: Logwatch crontab ---
log "Configurazione logwatch..."
mkdir -p /etc/logwatch/conf
cat > /etc/logwatch/conf/logwatch.conf <<'EOF'
Output = stdout
Format = text
Detail = Med
Range = yesterday
Service = All
EOF

CRON_ENTRY="0 7 * * * /usr/sbin/logwatch --output stdout --format text --detail med >> /var/log/logwatch-report.log 2>&1"
(crontab -l 2>/dev/null | grep -v logwatch; echo "$CRON_ENTRY") | crontab -

# --- Passo 8: Crea cartella scripts utente ---
SCRIPT_DIR="/root/scripts"
mkdir -p "$SCRIPT_DIR"
log "Cartella script creata in $SCRIPT_DIR"

log "=============================="
log "Setup completato con successo!"
log "=============================="
warn "IMPORTANTE: Creare utente non-root manualmente: adduser pentest && usermod -aG sudo pentest"
warn "IMPORTANTE: Configurare chiave SSH pubblica prima di disabilitare PasswordAuthentication"
