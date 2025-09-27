#!/bin/bash

# Simple QEMU Test for Rust Kernel
# Tests the existing Rust kernel with bootloader crate

set -e

echo "🧠 Syn_OS Rust Kernel QEMU Test"
echo "================================"

# Check if bootimage is installed
if ! command -v cargo-bootimage &> /dev/null; then
    echo "📦 Installing bootimage..."
    cargo install bootimage
fi

# Add rust-src component if missing
rustup component add rust-src --toolchain nightly

# Build bootable image using bootimage
echo "🔨 Building bootable kernel image with bootimage..."
cargo bootimage --target x86_64-unknown-none --release

if [ $? -ne 0 ]; then
    echo "❌ Bootimage build failed! Let's try a different approach..."
    
    # Alternative: use existing target specification
    echo "🔄 Trying alternative build approach..."
    RUSTFLAGS="-C link-arg=-nostartfiles" cargo build --release --target x86_64-unknown-none
    
    if [ $? -ne 0 ]; then
        echo "❌ Alternative build also failed. Kernel may need bootloader fixes."
        exit 1
    fi
fi

# Find the bootimage
BOOTIMAGE=$(find ../../target -name "*.img" | head -1)

if [ -z "$BOOTIMAGE" ]; then
    echo "⚠️  No bootimage found, looking for kernel binary..."
    KERNEL_BIN=$(find ../../target -path "*/x86_64-unknown-none/release/*kernel*" -type f | head -1)
    
    if [ -z "$KERNEL_BIN" ]; then
        echo "❌ No kernel binary found!"
        exit 1
    fi
    
    echo "🔍 Found kernel binary: $KERNEL_BIN"
    echo "🚀 Testing kernel with multiboot in QEMU..."
    
    # Test raw kernel with multiboot
    qemu-system-x86_64 \
        -kernel "$KERNEL_BIN" \
        -m 256M \
        -display curses \
        -serial stdio \
        -no-reboot \
        -no-shutdown \
        -cpu qemu64
        
else
    echo "🔍 Found bootimage: $BOOTIMAGE"
    echo "🚀 Testing bootimage in QEMU..."
    
    # Test with bootimage
    qemu-system-x86_64 \
        -drive format=raw,file="$BOOTIMAGE" \
        -m 256M \
        -display curses \
        -serial stdio \
        -no-reboot \
        -no-shutdown \
        -cpu qemu64
fi

echo ""
echo "🎓 QEMU Test Information:"
echo "========================"
echo "This test demonstrates:"
echo "- Kernel loading in virtual environment"
echo "- VGA text mode output"
echo "- Cybersecurity subsystem initialization"
echo "- Educational framework activation"
echo ""
echo "Expected output:"
echo "- Kernel initialization messages"
echo "- Security subsystem status"
echo "- Neural darwinian security activation"  
echo "- Educational API readiness"
echo "- Comprehensive kernel tests"