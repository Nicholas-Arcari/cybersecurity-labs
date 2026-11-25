#!/usr/bin/env bash
# Finding ID validation script
# Used by: pre-commit hook, CI pipeline
# Checks:
#   1. All Finding IDs follow the format PREFIX-NNN
#   2. No duplicate IDs exist across the repository
#   3. Valid prefixes only

set -euo pipefail

VALID_PREFIXES="OSINT|SCAN|DNS|INTEL|VULN|WEB|EXPLOIT|SE|WIFI|POST|DEF|FOR|CLOUD"
EXIT_CODE=0

# Extract all finding IDs from the Finding Registry in README.md
# Format: | [ID-NNN](...) | ... |
REGISTRY_IDS=$(grep -oP "\[($VALID_PREFIXES)-\d{3}\]" README.md 2>/dev/null | tr -d '[]' | sort)

if [ -z "$REGISTRY_IDS" ]; then
    echo "[WARN] No finding IDs found in README.md registry"
    exit 0
fi

# Check for duplicates
DUPLICATES=$(echo "$REGISTRY_IDS" | uniq -d)
if [ -n "$DUPLICATES" ]; then
    echo "[FAIL] Duplicate Finding IDs in registry:"
    echo "$DUPLICATES" | while read -r id; do
        echo "  - $id"
    done
    EXIT_CODE=1
fi

# Check format: must be PREFIX-NNN (3 digits, zero-padded)
INVALID_FORMAT=$(echo "$REGISTRY_IDS" | grep -vP "^($VALID_PREFIXES)-\d{3}$" || true)
if [ -n "$INVALID_FORMAT" ]; then
    echo "[FAIL] Invalid Finding ID format:"
    echo "$INVALID_FORMAT" | while read -r id; do
        echo "  - $id (expected: PREFIX-NNN with 3 digits)"
    done
    EXIT_CODE=1
fi

# Check sequentiality per prefix
echo "$REGISTRY_IDS" | while read -r id; do
    echo "${id%-*}"
done | sort -u | while read -r prefix; do
    NUMS=$(echo "$REGISTRY_IDS" | grep "^${prefix}-" | sed "s/${prefix}-//" | sort -n)
    EXPECTED=1
    for num in $NUMS; do
        num_int=$((10#$num))
        if [ "$num_int" -ne "$EXPECTED" ]; then
            echo "[WARN] Gap in ${prefix} sequence: expected ${prefix}-$(printf '%03d' $EXPECTED), found ${prefix}-$(printf '%03d' $num_int)"
        fi
        EXPECTED=$((num_int + 1))
    done
done

# Count summary
TOTAL=$(echo "$REGISTRY_IDS" | wc -l)
UNIQUE=$(echo "$REGISTRY_IDS" | sort -u | wc -l)

if [ "$EXIT_CODE" -eq 0 ]; then
    echo "[OK] Finding ID validation passed: $UNIQUE unique IDs, $TOTAL total references"
else
    echo "[FAIL] Finding ID validation failed"
fi

exit $EXIT_CODE
