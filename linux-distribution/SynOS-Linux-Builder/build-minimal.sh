#!/bin/bash
set -e

echo "=== Minimal SynOS ISO Builder ==="

# Clean everything
sudo lb clean --purge
sudo rm -rf cache/ .build/ chroot/ binary/ 2>/dev/null || true

# Simple config - no apt updates in chroot
lb config \
    --distribution bookworm \
    --archive-areas "main contrib non-free non-free-firmware" \
    --binary-images iso-hybrid \
    --apt-update false \
    --apt-recommends false \
    --memtest none

# Minimal package list
echo "live-boot live-config" > config/package-lists/minimal.list.chroot

# Build
echo "Building..."
sudo lb build 2>&1 | tee build.log

# Check result
if ls *.iso 2>/dev/null; then
    ls -lh *.iso
    echo "✅ SUCCESS!"
else
    echo "❌ Failed - check build.log"
    tail -30 build.log
fi
