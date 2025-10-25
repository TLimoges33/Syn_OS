#!/bin/bash
set -e

echo "=== SynOS Working Build ===" 

# Complete clean
sudo lb clean --purge
sudo rm -rf cache/ chroot/ binary/ .build/ *.iso *.log

# Configure WITHOUT apt updates in chroot (this is where GPG fails)
lb config \
    --distribution bookworm \
    --archive-areas "main contrib non-free non-free-firmware" \
    --binary-images iso-hybrid \
    --bootappend-live "boot=live components quiet splash" \
    --memtest none \
    --chroot-squashfs-compression-type gzip

# Disable chroot apt updates (skip the failing step)
echo 'LB_CHROOT_FILESYSTEM="squashfs"' >> config/chroot
echo 'LB_APT="apt"' >> config/chroot  
echo 'LB_APT_INDICES="false"' >> config/chroot

echo "Building with 4GB RAM limit..."
sudo systemd-run --scope -p MemoryMax=4G -p CPUQuota=300% \
    lb build 2>&1 | tee build-$(date +%Y%m%d-%H%M%S).log

if ls *.iso; then
    ls -lh *.iso
    echo "✅ SUCCESS!"
else
    echo "❌ Failed - check log"
fi
