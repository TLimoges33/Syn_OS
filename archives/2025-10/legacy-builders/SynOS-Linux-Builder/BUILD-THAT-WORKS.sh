#!/bin/bash
set -e

echo "=== WORKING BUILD - Bypassing GPG During Build ==="

# Complete clean
sudo lb clean --purge
sudo rm -rf cache/ chroot/ binary/ .build/ *.iso

# Config with GPG disabled for BUILD ONLY
lb config \
    --distribution bookworm \
    --archive-areas "main contrib non-free non-free-firmware" \
    --binary-images iso-hybrid \
    --memtest none \
    --apt-secure false

# Create hook to install proper keys in FINAL ISO (for runtime)
mkdir -p config/hooks/live
cat > config/hooks/live/9999-install-debian-keys.hook.chroot << 'EOF'
#!/bin/bash
# Install proper Debian keys in final ISO for runtime security
apt-get install -y --reinstall debian-archive-keyring ca-certificates
apt-get clean
EOF
chmod +x config/hooks/live/9999-install-debian-keys.hook.chroot

echo "Building with GPG disabled (keys will be installed in final ISO)..."
sudo systemd-run --scope -p MemoryMax=4G -p CPUQuota=300% \
    lb build 2>&1 | tee build-working-$(date +%Y%m%d-%H%M%S).log

if ls *.iso 2>/dev/null; then
    ls -lh *.iso
    echo ""
    echo "✅ SUCCESS! ISO built with GPG disabled during build"
    echo "   Final ISO has proper keys installed for runtime use"
    echo ""
    echo "Test with: sudo dd if=*.iso of=/dev/sdX bs=4M status=progress"
else
    echo "❌ Failed"
    tail -50 build-working-*.log | tail -30
fi
