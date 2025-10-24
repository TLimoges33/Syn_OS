#!/bin/bash
################################################################################
# Fix /dev/null permissions - Comprehensive Solution
################################################################################

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           /dev/null Permission Fix Utility                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    echo "Run: sudo ./scripts/fix-dev-null.sh"
    exit 1
fi

echo "Step 1: Current /dev/null status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
stat /dev/null || echo "⚠ stat failed"
ls -la /dev/null || echo "⚠ ls failed"
file /dev/null || echo "⚠ file failed"
echo ""

echo "Step 2: Check /dev mount"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
mount | grep '/dev '
echo ""

echo "Step 3: Test write to /dev/null"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if echo "test" > /dev/null 2>&1; then
    echo "✓ /dev/null is writable (issue may be with specific user)"
else
    echo "✗ /dev/null is NOT writable (even as root!)"
fi
echo ""

echo "Step 4: Attempting to fix /dev/null"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Method 1: Remove and recreate
echo "  Method 1: Remove and recreate..."
rm -f /dev/null
mknod -m 666 /dev/null c 1 3
chown root:root /dev/null
chmod 666 /dev/null

# Verify
ls -la /dev/null
echo ""

echo "Step 5: Verify fix"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if echo "test" > /dev/null 2>&1; then
    echo "✓ /dev/null is now working!"
else
    echo "✗ Still not working - deeper system issue"
    echo ""
    echo "Possible causes:"
    echo "  1. SELinux is blocking access"
    echo "  2. AppArmor is blocking access"
    echo "  3. /dev is mounted read-only"
    echo "  4. Kernel issue"
    echo ""
    echo "Checking SELinux..."
    sestatus 2>/dev/null || echo "  SELinux not installed"
    echo ""
    echo "Checking AppArmor..."
    aa-status 2>/dev/null || echo "  AppArmor not installed"
    echo ""
    echo "Checking /dev mount options..."
    mount | grep '/dev '
fi

echo ""
echo "Step 6: Test as regular user"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo -u diablorain bash -c 'echo "test" > /dev/null 2>&1 && echo "✓ Works for diablorain user" || echo "✗ Fails for diablorain user"'

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "Fix attempt complete!"
echo "═══════════════════════════════════════════════════════════════"
