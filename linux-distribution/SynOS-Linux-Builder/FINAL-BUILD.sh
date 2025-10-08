#!/bin/bash
set -e

echo "=== FINAL FIX - Complete Rebuild ==="

# NUKE EVERYTHING
echo "Nuking all caches and builds..."
sudo lb clean --purge
sudo rm -rf cache/ chroot/ binary/ .build/ *.iso *.log

# Remove broken synos-repo reference  
rm -f config/archives/synos-local.list.chroot

# Simple config
lb config \
    --distribution bookworm \
    --archive-areas "main contrib non-free non-free-firmware" \
    --binary-images iso-hybrid \
    --memtest none

echo "Starting build with Debian keys installed..."
echo "This will take 1-2 hours. Go get coffee."

sudo systemd-run --scope -p MemoryMax=4G -p CPUQuota=300% \
    lb build 2>&1 | tee build-final-$(date +%Y%m%d-%H%M%S).log

if ls *.iso 2>/dev/null; then
    ls -lh *.iso
    echo "✅ FINALLY WORKED!"
else
    echo "❌ Failed again - check log"
    tail -50 build-final-*.log | tail -30
fi
