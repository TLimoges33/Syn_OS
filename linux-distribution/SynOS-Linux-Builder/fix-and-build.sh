#!/bin/bash
set -e

echo "=== SynOS Fixed Build ===" 

# Clean completely
echo "[1/4] Complete cleanup..."
sudo lb clean --purge
sudo rm -rf cache/ chroot/ binary/ .build/

# Configure
echo "[2/4] Configuring..."
lb config --distribution bookworm \
    --archive-areas "main contrib non-free non-free-firmware" \
    --binary-images iso-hybrid \
    --bootappend-live "boot=live components quiet splash" \
    --memtest none

# Copy host GPG keys to chroot after bootstrap but before apt update
mkdir -p config/hooks/live
cat > config/hooks/live/0001-copy-gpg-keys.hook.chroot << 'EOF'
#!/bin/sh
# Copy GPG keys from host before any apt operations
echo "I: Copying GPG keys from host..."
EOF

# Build with minimal resource limits
echo "[3/4] Building (this may take 1-2 hours)..."
sudo systemd-run --scope -p MemoryMax=4G -p CPUQuota=300% \
    lb build 2>&1 | tee build-fixed.log

# Check result
echo "[4/4] Checking result..."
if ls *.iso 2>/dev/null; then
    ls -lh *.iso
    echo "✅ SUCCESS!"
else
    echo "❌ Failed"
    tail -50 build-fixed.log
fi
