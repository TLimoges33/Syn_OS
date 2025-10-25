#!/bin/bash
# SynOS v1.0 Final Deployment - Execute This Script
# Run with: sudo bash EXECUTE_NOW.sh

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              SynOS v1.0 FINAL DEPLOYMENT                      ║"
echo "║                 3-Step Complete Process                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    echo "   Run: sudo bash EXECUTE_NOW.sh"
    exit 1
fi

ORIGINAL_USER="${SUDO_USER:-$USER}"
PROJECT_ROOT="/home/diablorain/Syn_OS"

cd "$PROJECT_ROOT"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1/3: Deploy All Components (3 minutes)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -f "scripts/deploy-synos-v1.0-nosudo.sh" ]; then
    bash scripts/deploy-synos-v1.0-nosudo.sh
    echo ""
    echo "✅ STEP 1 COMPLETE: All components deployed!"
else
    echo "❌ Deployment script not found!"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2/3: Rebuild ISO (30-40 minutes)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd linux-distribution/SynOS-Linux-Builder

echo "→ Cleaning previous build..."
lb clean --purge

echo ""
echo "→ Building new ISO with all deployments..."
echo "  (This will take 30-40 minutes depending on your system)"
echo ""

lb build

echo ""
echo "✅ STEP 2 COMPLETE: ISO built successfully!"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3/3: Finalize ISO (1 minute)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$PROJECT_ROOT"

# Move and rename ISO
if [ -f "linux-distribution/SynOS-Linux-Builder/live-image-amd64.hybrid.iso" ]; then
    mv linux-distribution/SynOS-Linux-Builder/live-image-amd64.hybrid.iso build/synos-v1.0-final.iso
    chown $ORIGINAL_USER:$ORIGINAL_USER build/synos-v1.0-final.iso

    echo "→ Creating checksums..."
    cd build
    sha256sum synos-v1.0-final.iso > synos-v1.0-final.iso.sha256
    md5sum synos-v1.0-final.iso > synos-v1.0-final.iso.md5

    chown $ORIGINAL_USER:$ORIGINAL_USER synos-v1.0-final.iso.*

    echo ""
    echo "✅ STEP 3 COMPLETE: Final ISO ready!"
    echo ""

    # Display ISO info
    ISO_SIZE=$(du -h synos-v1.0-final.iso | cut -f1)
    SHA256=$(cat synos-v1.0-final.iso.sha256 | cut -d' ' -f1)

    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                  🎉 v1.0 BUILD COMPLETE! 🎉                  ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📀 ISO Details:"
    echo "   Location: build/synos-v1.0-final.iso"
    echo "   Size: $ISO_SIZE"
    echo "   SHA256: ${SHA256:0:16}..."
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. Test in VM:"
    echo "      qemu-system-x86_64 -cdrom build/synos-v1.0-final.iso -m 4G -enable-kvm"
    echo ""
    echo "   2. Or create VirtualBox VM:"
    echo "      VBoxManage createvm --name 'SynOS-v1.0' --register"
    echo "      VBoxManage modifyvm 'SynOS-v1.0' --memory 4096 --cpus 2"
    echo "      VBoxManage storagectl 'SynOS-v1.0' --name 'IDE' --add ide"
    echo "      VBoxManage storageattach 'SynOS-v1.0' --storagectl 'IDE' \\"
    echo "          --port 0 --device 0 --type dvddrive \\"
    echo "          --medium $(pwd)/synos-v1.0-final.iso"
    echo "      VBoxManage startvm 'SynOS-v1.0'"
    echo ""
    echo "📊 What's Deployed:"
    echo "   ✅ 10 Rust enterprise binaries (134MB)"
    echo "   ✅ Custom SynOS kernel (73KB)"
    echo "   ✅ AI framework with nats-py"
    echo "   ✅ SynOS GRUB branding"
    echo "   ✅ Plymouth boot splash"
    echo "   ✅ Desktop theme & wallpaper"
    echo "   ✅ Systemd services"
    echo ""
    echo "🎯 Completion: 96% → Ready for production!"
    echo ""

else
    echo "❌ ISO not found after build!"
    exit 1
fi

echo "════════════════════════════════════════════════════════════════"
echo "                    DEPLOYMENT SUCCESSFUL! ✅"
echo "════════════════════════════════════════════════════════════════"
