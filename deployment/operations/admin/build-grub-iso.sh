#!/bin/bash

# SynOS V1.0 GRUB ISO Builder
# Creates a bootable ISO using GRUB2 instead of ISOLINUX for multiboot kernel

set -e

ISO_NAME="SynOS-v1.0-grub-$(date +%Y%m%d).iso"
BUILD_DIR="build"
ISO_DIR="${BUILD_DIR}/grub-iso"
KERNEL_BIN="core/kernel/kernel.bin"
INITRD_IMG="build/synos-initrd.img"

echo "🔧 Building SynOS V1.0 GRUB ISO with Custom initrd..."
echo "📅 $(date)"
echo "📦 Target: ${ISO_NAME}"

# Check if kernel exists
if [ ! -f "${KERNEL_BIN}" ]; then
    echo "❌ Kernel binary not found: ${KERNEL_BIN}"
    echo "   Run: cd core/kernel && make all"
    exit 1
fi

# Build custom initrd if it doesn't exist
if [ ! -f "${INITRD_IMG}" ]; then
    echo "🛠️ Building custom initrd..."
    ./scripts/build-custom-initrd.sh
fi

# Verify initrd exists
if [ ! -f "${INITRD_IMG}" ]; then
    echo "❌ initrd not found: ${INITRD_IMG}"
    echo "   Run: ./scripts/build-custom-initrd.sh"
    exit 1
fi

# Create clean build environment
echo "🧹 Preparing build environment..."
rm -rf "${ISO_DIR}"
mkdir -p "${ISO_DIR}"/{boot/grub,live}

# Copy kernel
echo "📋 Copying multiboot kernel..."
cp "${KERNEL_BIN}" "${ISO_DIR}/boot/"

# Copy initrd
echo "📋 Copying custom initrd..."
cp "${INITRD_IMG}" "${ISO_DIR}/boot/"
cp "${KERNEL_BIN}" "${ISO_DIR}/boot/kernel.bin"

# Create GRUB configuration
echo "⚙️ Configuring GRUB2 with initrd support..."
cat > "${ISO_DIR}/boot/grub/grub.cfg" << 'EOF'
set timeout=15
set default=0

menuentry "SynOS V1.0 with Custom initrd" {
    multiboot /boot/kernel.bin
    module /boot/synos-initrd.img
    boot
}

menuentry "SynOS V1.0 Debug Mode (no initrd)" {
    multiboot /boot/kernel.bin debug
    boot
}

menuentry "SynOS V1.0 Legacy Mode" {
    multiboot /boot/kernel.bin legacy
    boot
}
EOF

# Create the ISO with GRUB
echo "💿 Building GRUB ISO image..."
grub-mkrescue -o "${BUILD_DIR}/${ISO_NAME}" "${ISO_DIR}"

# Cleanup
echo "🧹 Cleaning up..."
rm -rf "${ISO_DIR}"

# Results
ISO_SIZE=$(du -h "${BUILD_DIR}/${ISO_NAME}" | cut -f1)
echo ""
echo "✅ SynOS V1.0 GRUB ISO Build Complete!"
echo "📁 Location: ${BUILD_DIR}/${ISO_NAME}"
echo "📊 Size: ${ISO_SIZE}"
echo "🔍 Components:"
echo "   - Multiboot kernel (direct GRUB loading)"
echo "   - GRUB2 bootloader"
echo "   - Native multiboot protocol"
echo ""
echo "🚀 Test with: qemu-system-x86_64 -cdrom ${BUILD_DIR}/${ISO_NAME} -m 512M"
echo "🔧 Serial test: qemu-system-x86_64 -cdrom ${BUILD_DIR}/${ISO_NAME} -m 512M -serial stdio -nographic"
