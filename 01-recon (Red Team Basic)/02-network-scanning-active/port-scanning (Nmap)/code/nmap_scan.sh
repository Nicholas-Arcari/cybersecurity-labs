#!/bin/bash
# nmap_scan.sh - Pipeline di scansione Nmap in tre fasi
# Uso: ./nmap_scan.sh <target_ip_o_range> [output_dir]
# Esempio: ./nmap_scan.sh 10.0.2.3
# Esempio: ./nmap_scan.sh 10.0.2.0/24 /tmp/scan_results

set -euo pipefail

TARGET="${1:?Specificare il target: ./nmap_scan.sh <IP o range>}"
OUTPUT_DIR="${2:-./nmap_results_$(date +%F)}"
TIMESTAMP=$(date +%F_%H-%M)

mkdir -p "$OUTPUT_DIR"

log()  { echo "[*] $1"; }
ok()   { echo "[+] $1"; }
warn() { echo "[!] $1"; }

# --- Fase 1: Host discovery rapida ---
log "Fase 1/3: Host discovery (ping sweep)..."
nmap -sn -T4 "$TARGET" \
    -oG "$OUTPUT_DIR/01_discovery_${TIMESTAMP}.gnmap" \
    -oN "$OUTPUT_DIR/01_discovery_${TIMESTAMP}.txt"

LIVE_HOSTS=$(grep "Up" "$OUTPUT_DIR/01_discovery_${TIMESTAMP}.gnmap" | awk '{print $2}' | tr '\n' ' ')
ok "Host attivi: $LIVE_HOSTS"

if [[ -z "$LIVE_HOSTS" ]]; then
    warn "Nessun host attivo trovato. Verificare target e connettivita."
    exit 0
fi

# --- Fase 2: Port scan veloce (top 1000) ---
log "Fase 2/3: Port scan veloce sui host attivi..."
# shellcheck disable=SC2086
nmap -sS -T4 --open \
    -oA "$OUTPUT_DIR/02_portscan_${TIMESTAMP}" \
    $LIVE_HOSTS

ok "Port scan completato. Risultati in $OUTPUT_DIR/02_portscan_${TIMESTAMP}.*"

# Estrae le porte aperte per la fase successiva
OPEN_PORTS=$(grep "open" "$OUTPUT_DIR/02_portscan_${TIMESTAMP}.gnmap" \
    | grep -oP '\d+/open' | grep -oP '^\d+' | sort -u | paste -sd,)

if [[ -z "$OPEN_PORTS" ]]; then
    warn "Nessuna porta aperta trovata."
    exit 0
fi

ok "Porte aperte: $OPEN_PORTS"

# --- Fase 3: Scansione dettagliata con versioni e script ---
log "Fase 3/3: Enumerazione servizi e script NSE default..."
# shellcheck disable=SC2086
nmap -sV -sC -O --script=banner,http-title,smb-os-discovery \
    -p "$OPEN_PORTS" \
    -oA "$OUTPUT_DIR/03_services_${TIMESTAMP}" \
    $LIVE_HOSTS

ok "======================================"
ok "Scansione completata!"
ok "Output in: $OUTPUT_DIR/"
ok "File principali:"
ok "  - 01_discovery_${TIMESTAMP}.txt    (host attivi)"
ok "  - 02_portscan_${TIMESTAMP}.nmap    (porte aperte)"
ok "  - 03_services_${TIMESTAMP}.nmap    (servizi + banner)"
ok "======================================"

# Genera mini-report testuale
REPORT="$OUTPUT_DIR/SUMMARY_${TIMESTAMP}.txt"
{
    echo "=== NMAP SCAN SUMMARY ==="
    echo "Target:    $TARGET"
    echo "Data:      $TIMESTAMP"
    echo "Host live: $LIVE_HOSTS"
    echo "Porte:     $OPEN_PORTS"
    echo ""
    echo "=== SERVIZI RILEVATI ==="
    grep "open" "$OUTPUT_DIR/03_services_${TIMESTAMP}.nmap" 2>/dev/null || true
} > "$REPORT"

ok "Summary in: $REPORT"
