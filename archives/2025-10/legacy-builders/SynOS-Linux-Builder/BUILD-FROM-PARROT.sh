#!/bin/bash
set -e

echo "=== Building SynOS from Parrot OS Base ==="

# Clean
sudo lb clean --purge
sudo rm -rf cache/ chroot/ binary/ .build/ *.iso

# Use Parrot as base distribution
lb config \
    --distribution parrot \
    --parent-mirror-bootstrap "http://deb.parrot.sh/parrot/" \
    --parent-mirror-chroot "http://deb.parrot.sh/parrot/" \
    --archive-areas "main contrib non-free" \
    --binary-images iso-hybrid \
    --memtest none \
    --apt-secure false

echo "Building from Parrot base (already has 500+ security tools)..."
sudo systemd-run --scope -p MemoryMax=4G -p CPUQuota=300% \
    lb build 2>&1 | tee build-parrot-$(date +%Y%m%d-%H%M%S).log

if ls *.iso 2>/dev/null; then
    ls -lh *.iso
    echo "✅ SUCCESS! Parrot-based SynOS built"
else
    echo "❌ Failed"
    tail -50 build-parrot-*.log | tail -30
fi
