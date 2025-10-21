#!/bin/bash
set -euo pipefail

cd /home/diablorain/Syn_OS/linux-distribution/SynOS-Linux-Builder

echo "Testing package counting..."
TOTAL_PACKAGES=0

for list in config/package-lists/*.list.chroot; do
    if [ -f "$list" ]; then
        echo "Processing: $list"
        COUNT=$(grep -v '^#' "$list" | grep -v '^$' | wc -l)
        TOTAL_PACKAGES=$((TOTAL_PACKAGES + COUNT))
        echo "  Count: $COUNT"
        echo "  Running total: $TOTAL_PACKAGES"
    fi
done

echo ""
echo "Total packages: $TOTAL_PACKAGES"
