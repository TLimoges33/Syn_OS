#!/bin/bash
# Quick Terminal Fix - Run with sudo password piped
# Usage: echo "password" | bash quick-terminal-fix.sh

set -e

echo "=== Quick Terminal Environment Fix ==="
echo "Timestamp: $(date)"
echo ""

# Read password from stdin
read -r SUDO_PASSWORD

# Fix /dev/null
echo ">>> Fixing /dev/null"
if [ ! -c /dev/null ] || ! echo test >/dev/null 2>&1; then
    echo "$SUDO_PASSWORD" | sudo -S rm -f /dev/null 2>&1
    echo "$SUDO_PASSWORD" | sudo -S mknod -m 666 /dev/null c 1 3 2>&1
    echo "✓ /dev/null recreated"
else
    echo "✓ /dev/null OK"
fi

# Fix /dev/ptmx
echo ">>> Fixing /dev/ptmx"
if [ ! -c /dev/ptmx ]; then
    echo "$SUDO_PASSWORD" | sudo -S rm -f /dev/ptmx 2>&1
    echo "$SUDO_PASSWORD" | sudo -S mknod -m 666 /dev/ptmx c 5 2 2>&1
    echo "✓ /dev/ptmx recreated"
else
    echo "✓ /dev/ptmx OK"
fi

# Ensure /dev/pts is mounted
echo ">>> Checking /dev/pts mount"
if ! mount | grep -q '/dev/pts type devpts'; then
    echo "$SUDO_PASSWORD" | sudo -S mount -t devpts devpts /dev/pts -o rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=000 2>&1
    echo "✓ /dev/pts mounted"
else
    echo "✓ /dev/pts already mounted"
fi

# Fix permissions
echo ">>> Fixing device permissions"
echo "$SUDO_PASSWORD" | sudo -S chmod 666 /dev/null /dev/zero /dev/ptmx 2>&1 || true

# Clear caches
echo ">>> Clearing system caches"
sync
echo "$SUDO_PASSWORD" | sudo -S sh -c 'echo 3 > /proc/sys/vm/drop_caches' 2>&1 || true

# Show status
echo ""
echo "=== Status ==="
ls -la /dev/null /dev/ptmx 2>&1
mount | grep pts
echo ""
echo "✓ Fix complete"
echo ""
echo "RESTART VS CODE NOW to apply changes"
