#!/bin/bash
set -e

echo "🔧 Building SynOS bootable disk image..."
echo

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build"
KERNEL_DIR="$PROJECT_ROOT/src/kernel"

# Ensure build directory exists
mkdir -p "$BUILD_DIR"

# Step 1: Build the kernel
echo "Step 1: Building kernel..."
cd "$KERNEL_DIR"
cargo build \
    --release \
    --target=x86_64-unknown-none \
    --features=kernel-binary

KERNEL_PATH="$PROJECT_ROOT/target/x86_64-unknown-none/release/kernel"

if [ ! -f "$KERNEL_PATH" ]; then
    echo "❌ Error: Kernel binary not found at: $KERNEL_PATH"
    exit 1
fi

KERNEL_SIZE=$(stat -c%s "$KERNEL_PATH")
echo "✅ Kernel built successfully"
echo "  Binary: $KERNEL_PATH"
echo "  Size: $KERNEL_SIZE bytes ($((KERNEL_SIZE / 1024)) KB)"
echo

# Step 2: Create bootable image using GRUB (fallback method)
echo "Step 2: Creating bootable ISO with GRUB..."

ISO_DIR="$BUILD_DIR/iso"
mkdir -p "$ISO_DIR/boot/grub"

# Copy kernel to ISO directory
cp "$KERNEL_PATH" "$ISO_DIR/boot/kernel.bin"

# Create GRUB configuration
cat > "$ISO_DIR/boot/grub/grub.cfg" << 'EOFGRUB'
set timeout=0
set default=0

menuentry "SynOS v1.0" {
    multiboot2 /boot/kernel.bin
    boot
}
EOFGRUB

# Check if grub-mkrescue is available
if command -v grub-mkrescue >/dev/null 2>&1; then
    # Create ISO
    ISO_PATH="$BUILD_DIR/synos-v1.0.iso"
    grub-mkrescue -o "$ISO_PATH" "$ISO_DIR" 2>&1 | grep -v "warning"

    if [ -f "$ISO_PATH" ]; then
        ISO_SIZE=$(stat -c%s "$ISO_PATH")
        echo "✅ ISO image created"
        echo "  Path: $ISO_PATH"
        echo "  Size: $ISO_SIZE bytes ($((ISO_SIZE / 1024 / 1024)) MB)"
        echo

        echo "🎉 Build complete!"
        echo
        echo "To test the ISO:"
        echo "  qemu-system-x86_64 -cdrom $ISO_PATH -m 4G"
    else
        echo "❌ Failed to create ISO image"
        exit 1
    fi
else
    echo "⚠️  grub-mkrescue not found. Kernel built but ISO not created."
    echo "   Install grub-pc-bin or xorriso to create bootable ISOs."
    echo
    echo "Kernel is available at: $KERNEL_PATH"
fi
