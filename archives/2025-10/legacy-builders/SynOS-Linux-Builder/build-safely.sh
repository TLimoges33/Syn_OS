#!/bin/bash
# Safe ISO build script with resource limits
# Prevents system crashes by constraining memory and CPU usage

set -e

echo "=== SynOS Safe ISO Builder ==="
echo "This will build a minimal ISO without overwhelming your system"
echo ""

# Check we're in the right directory
if [[ ! -f config/binary ]]; then
    echo "Error: Must be run from SynOS-Linux-Builder directory"
    exit 1
fi

# 1. Clean previous builds and cache
echo "[1/5] Cleaning previous builds and cache..."
sudo lb clean --purge
sudo rm -rf cache/bootstrap cache/packages_* 2>/dev/null || true

# Update keyring first
echo "[1.5/5] Updating Debian keyring..."
sudo apt-get update -qq 2>/dev/null || true
sudo apt-get install -y debian-archive-keyring 2>/dev/null || true

# Recreate config after purge
echo "[1.6/5] Recreating configuration..."
lb config --distribution bookworm \
    --archive-areas "main contrib non-free non-free-firmware" \
    --binary-images iso-hybrid \
    --bootappend-live "boot=live components quiet splash" \
    --debian-installer live \
    --memtest none \
    --apt-indices false \
    --apt-secure false

# 2. Build with resource limits (FULL ISO - all packages included)
echo "[2/3] Building FULL ISO with resource limits (this may take 1-2 hours)..."
echo "  - Memory limited to 3GB to prevent crashes"
echo "  - CPU limited to 200% (2 cores) to keep system responsive"
echo ""

LOG_FILE="build-safe-$(date +%Y%m%d-%H%M%S).log"

# Run build with systemd resource controls
sudo systemd-run \
    --scope \
    --unit=synos-safe-build \
    -p MemoryMax=3G \
    -p MemoryHigh=2.5G \
    -p CPUQuota=200% \
    -p IOWeight=500 \
    lb build 2>&1 | tee "$LOG_FILE"

# 3. Check result
echo "[3/3] Build complete!"
if [[ -f *.iso ]]; then
    ISO_FILE=$(ls -t *.iso | head -1)
    ISO_SIZE=$(du -h "$ISO_FILE" | cut -f1)
    echo ""
    echo "✅ SUCCESS! ISO built: $ISO_FILE ($ISO_SIZE)"
    echo ""
    echo "To test: sudo dd if=$ISO_FILE of=/dev/sdX bs=4M status=progress"
    echo "Or use in VirtualBox/VMware"
else
    echo ""
    echo "❌ Build failed. Check log: $LOG_FILE"
    echo "Last 20 lines:"
    tail -20 "$LOG_FILE"
fi
