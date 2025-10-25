#!/bin/bash
# Quick v1.0 Fix - Get to working ISO in 1 hour
# Disables broken AI, fixes menu, builds ISO

set -e

CHROOT=/home/diablorain/Syn_OS/build/synos-v1.0/work/chroot

echo "========================================================================="
echo "           SynOS v1.0 QUICK FIX - Security-Focused Release"
echo "========================================================================="
echo ""
echo "This script will:"
echo "  1. Disable broken AI services (temporary)"
echo "  2. Fix security tool categories"
echo "  3. Build working ISO"
echo ""
echo "Estimated time: 45 minutes"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Must run as root (use sudo)"
    exit 1
fi

# Step 1: Disable broken AI services
echo "[1/3] Disabling broken AI services..."
if [ -f "$CHROOT/etc/systemd/system/synos-ai.service" ]; then
    # Comment out the broken ExecStart line
    sed -i 's|^ExecStart=.*|# ExecStart disabled - daemon.py missing (enable in v1.1)|' \
        "$CHROOT/etc/systemd/system/synos-ai.service"
    echo "  ✓ AI service disabled (will be fixed in v1.1)"
else
    echo "  - AI service not found, skipping"
fi

# Step 2: Fix security tool categories
echo ""
echo "[2/3] Fixing security tool categories..."
if [ -f "/home/diablorain/Syn_OS/scripts/build/fix-security-tool-categories.sh" ]; then
    bash /home/diablorain/Syn_OS/scripts/build/fix-security-tool-categories.sh
    echo "  ✓ Security tool categories fixed"
else
    echo "  ERROR: Category fix script not found!"
    exit 1
fi

# Step 3: Build ISO
echo ""
echo "[3/3] Building ISO..."
if [ -f "/home/diablorain/Syn_OS/scripts/build/phase6-iso-generation.sh" ]; then
    bash /home/diablorain/Syn_OS/scripts/build/phase6-iso-generation.sh

    if [ -f "/home/diablorain/Syn_OS/build/synos-v1.0-complete.iso" ]; then
        echo ""
        echo "========================================================================="
        echo "                         SUCCESS!"
        echo "========================================================================="
        echo ""
        echo "ISO created: /home/diablorain/Syn_OS/build/synos-v1.0-complete.iso"
        echo ""
        echo "SynOS v1.0 Security Edition"
        echo "  ✓ 107+ security tools"
        echo "  ✓ Organized in 11 categories"
        echo "  ✓ BIOS + UEFI bootable"
        echo "  ✓ MATE desktop"
        echo "  - AI features disabled (coming in v1.1)"
        echo ""
        echo "Test: qemu-system-x86_64 -m 4G -cdrom /home/diablorain/Syn_OS/build/synos-v1.0-complete.iso"
        echo ""
    else
        echo "ERROR: ISO not created!"
        exit 1
    fi
else
    echo "  ERROR: ISO generation script not found!"
    exit 1
fi
