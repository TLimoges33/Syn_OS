#!/bin/bash
# Emergency Swap Configuration Script
# Critical: Prevents OOM crashes during Phase 3.4 implementation

set -e

echo "=== CRITICAL: Configuring 4GB Swap Space ==="
echo "This will prevent OOM crashes during dependency installation"
echo

# Check if already configured
if swapon -s | grep -q "/swapfile"; then
    echo "Swap already configured. Current status:"
    swapon -s
    free -h
    exit 0
fi

echo "Step 1: Creating 4GB swap file..."
fallocate -l 4G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=4096

echo "Step 2: Setting secure permissions..."
chmod 600 /swapfile

echo "Step 3: Setting up swap area..."
mkswap /swapfile

echo "Step 4: Activating swap..."
swapon /swapfile

echo "Step 5: Adding to /etc/fstab for persistence..."
if ! grep -q "/swapfile" /etc/fstab; then
    echo "/swapfile none swap sw 0 0" >> /etc/fstab
fi

echo
echo "=== SWAP CONFIGURATION COMPLETE ==="
echo "Memory status:"
free -h
echo
echo "Swap status:"
swapon -s
echo
echo "✅ System now protected from OOM crashes"
echo "✅ Phase 3.4 installation can proceed safely"