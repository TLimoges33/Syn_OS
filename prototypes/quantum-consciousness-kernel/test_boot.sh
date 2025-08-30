#!/bin/bash

# Syn_OS Kernel QEMU Boot Test Script
# Tests the cybersecurity education kernel in a virtual environment

echo "🧠 Syn_OS - AI-Powered Cybersecurity Education Kernel"
echo "======================================================="
echo "🎓 Starting QEMU boot test..."

# Build the kernel first
echo "📦 Building kernel..."
cargo build --release --target x86_64-unknown-none

if [ $? -ne 0 ]; then
    echo "❌ Kernel build failed!"
    exit 1
fi

echo "✅ Kernel build successful!"

# Check if QEMU is available
if ! command -v qemu-system-x86_64 &> /dev/null; then
    echo "❌ QEMU not found! Please install qemu-system-x86_64"
    exit 1
fi

# Find the kernel binary
KERNEL_BINARY=$(find ../../target -name "*syn-kernel*" -executable -type f | head -1)

if [ -z "$KERNEL_BINARY" ]; then
    echo "❌ Could not find kernel binary"
    echo "🔍 Searching in target directories..."
    find ../../target -name "*kernel*" | head -10
    exit 1
fi

echo "🔍 Found kernel binary: $KERNEL_BINARY"

# Create a simple bootloader test
echo "🚀 Starting QEMU with basic multiboot configuration..."

# Test basic kernel loading
qemu-system-x86_64 \
    -kernel "$KERNEL_BINARY" \
    -m 256M \
    -display curses \
    -serial stdio \
    -no-reboot \
    -no-shutdown \
    2>&1

echo "🎓 QEMU test completed!"
echo "📚 This test demonstrates kernel loading in a virtual environment"
echo "🛡️ Next: Implement full boot sequence with security features"