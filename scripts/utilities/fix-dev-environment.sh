#!/bin/bash
################################################################################
# SynOS Environment Repair Script
# Purpose: Fix broken /dev filesystem and restore system functionality
# Created: 2025-10-25
# Issue: /dev only has 5 entries instead of 200+ (critically broken)
################################################################################

set -e

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║           🔧 SynOS Environment Repair Utility                        ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ ERROR: This script must be run as root"
    echo "   Usage: sudo $0"
    exit 1
fi

echo "📊 CURRENT STATE AUDIT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Count current /dev entries
DEV_COUNT=$(ls /dev/ | wc -l)
echo "   /dev entries: $DEV_COUNT (should be 200+)"

# Check critical device files
echo -n "   /dev/urandom: "
if [ -c /dev/urandom ]; then echo "✓ exists"; else echo "✗ MISSING"; fi

echo -n "   /dev/random: "
if [ -c /dev/random ]; then echo "✓ exists"; else echo "✗ MISSING"; fi

echo -n "   /dev/zero: "
if [ -c /dev/zero ]; then echo "✓ exists"; else echo "✗ MISSING"; fi

echo -n "   /dev/tty: "
if [ -c /dev/tty ]; then echo "✓ exists"; else echo "✗ MISSING"; fi

# Check udev status
echo -n "   systemd-udevd: "
if systemctl is-active --quiet systemd-udevd; then
    echo "✓ running"
else
    echo "✗ NOT RUNNING"
fi

# Check sysfs devices
SYSFS_DEVS=$(find /sys/devices -name "dev" 2>/dev/null | wc -l)
echo "   sysfs devices: $SYSFS_DEVS"

echo ""
echo "🔧 REPAIR OPERATIONS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Step 1: Manually create critical device nodes if missing
echo "[1/6] Creating critical device nodes..."
if [ ! -c /dev/urandom ]; then
    mknod -m 666 /dev/urandom c 1 9 && echo "   ✓ Created /dev/urandom"
fi
if [ ! -c /dev/random ]; then
    mknod -m 666 /dev/random c 1 8 && echo "   ✓ Created /dev/random"
fi
if [ ! -c /dev/zero ]; then
    mknod -m 666 /dev/zero c 1 5 && echo "   ✓ Created /dev/zero"
fi
if [ ! -c /dev/full ]; then
    mknod -m 666 /dev/full c 1 7 && echo "   ✓ Created /dev/full"
fi
if [ ! -c /dev/tty ]; then
    mknod -m 666 /dev/tty c 5 0 && echo "   ✓ Created /dev/tty"
fi

# Create /dev/fd, /dev/stdin, /dev/stdout, /dev/stderr symlinks
echo "[2/6] Creating standard I/O symlinks..."
[ ! -L /dev/stdin ] && ln -sf /proc/self/fd/0 /dev/stdin && echo "   ✓ Created /dev/stdin"
[ ! -L /dev/stdout ] && ln -sf /proc/self/fd/1 /dev/stdout && echo "   ✓ Created /dev/stdout"
[ ! -L /dev/stderr ] && ln -sf /proc/self/fd/2 /dev/stderr && echo "   ✓ Created /dev/stderr"
[ ! -L /dev/fd ] && ln -sf /proc/self/fd /dev/fd && echo "   ✓ Created /dev/fd"

# Step 2: Restart udev to trigger device creation
echo "[3/6] Restarting udev daemon..."
systemctl restart systemd-udevd
sleep 2
echo "   ✓ systemd-udevd restarted"

# Step 3: Trigger udev to recreate all devices
echo "[4/6] Triggering udev device creation..."
udevadm trigger --action=add
echo "   ✓ Triggered device add events"

# Step 4: Wait for udev to settle
echo "[5/6] Waiting for udev to process events..."
udevadm settle
echo "   ✓ udev settled"

# Step 5: Reload udev rules
echo "[6/6] Reloading udev rules..."
udevadm control --reload-rules
echo "   ✓ Rules reloaded"

echo ""
echo "✅ REPAIR RESULTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Count new /dev entries
NEW_DEV_COUNT=$(ls /dev/ | wc -l)
echo "   /dev entries: $DEV_COUNT → $NEW_DEV_COUNT"

# Check if significant improvement
if [ "$NEW_DEV_COUNT" -lt 50 ]; then
    echo ""
    echo "⚠️  WARNING: /dev still appears broken (only $NEW_DEV_COUNT entries)"
    echo ""
    echo "🔄 RECOMMENDED: Reboot your system"
    echo ""
    echo "   The reboot will:"
    echo "     • Completely reinitialize devtmpfs"
    echo "     • Force kernel to recreate all device nodes"
    echo "     • Reset udev to clean state"
    echo "     • Fix any persistent issues"
    echo ""
    echo "   After reboot, /dev should have 150-200+ entries"
    echo ""
    echo "   Command: sudo reboot"
    echo ""
    exit 1
fi

# Verify critical files
FIXED=0
STILL_BROKEN=0

for device in urandom random zero full tty stdin stdout stderr; do
    if [ -e /dev/$device ]; then
        echo "   ✓ /dev/$device"
        ((FIXED++))
    else
        echo "   ✗ /dev/$device STILL MISSING"
        ((STILL_BROKEN++))
    fi
done

echo ""
if [ $STILL_BROKEN -eq 0 ] && [ "$NEW_DEV_COUNT" -ge 100 ]; then
    echo "✅ SUCCESS: All critical device files restored!"
    echo ""
    echo "   Environment Status: HEALTHY"
    echo "   /dev entries: $NEW_DEV_COUNT"
    echo ""
    echo "You can now:"
    echo "   • Use git commands"
    echo "   • Run build scripts"
    echo "   • Use cryptographic tools"
    echo ""
    exit 0
elif [ $STILL_BROKEN -eq 0 ]; then
    echo "⚠️  PARTIAL SUCCESS: Critical files exist but /dev may be incomplete"
    echo ""
    echo "   /dev has $NEW_DEV_COUNT entries (should be 150-200+)"
    echo ""
    echo "Recommendation:"
    echo "   If you experience issues, reboot the system:"
    echo "   sudo reboot"
    echo ""
    exit 0
else
    echo "❌ FAILED: Some devices still missing"
    echo ""
    echo "🔄 STRONGLY RECOMMENDED: Reboot your system"
    echo ""
    echo "   A reboot is the most reliable way to fix persistent /dev issues."
    echo "   After reboot, /dev will be completely recreated by the kernel."
    echo ""
    echo "   Command: sudo reboot"
    echo ""
    echo "If problems persist after reboot:"
    echo "   1. Check for filesystem errors: sudo fsck /dev"
    echo "   2. Examine system logs: journalctl -xe | grep -E '(udev|devtmpfs)'"
    echo "   3. Consider reinstalling udev: sudo apt install --reinstall udev"
    echo ""
    exit 1
fi
