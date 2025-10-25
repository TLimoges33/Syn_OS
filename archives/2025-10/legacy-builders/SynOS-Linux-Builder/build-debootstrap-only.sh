#!/bin/bash
set -e

echo "=== Minimal Debootstrap Build ==="

# Clean
sudo lb clean --purge
sudo rm -rf cache/ chroot/ binary/ .build/ *.iso

# Configure - minimal, no updates
lb config \
    --distribution bookworm \
    --archive-areas "main" \
    --binary-images iso-hybrid \
    --memtest none \
    --apt-indices false \
    --apt-recommends false \
    --debootstrap-options "--variant=minbase --no-check-gpg"

# Build
echo "Building (debootstrap only, no GPG checks)..."
sudo lb build 2>&1 | tee build-debootstrap-$(date +%Y%m%d-%H%M%S).log

ls -lh *.iso 2>/dev/null || echo "Failed - check log"
