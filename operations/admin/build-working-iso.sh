#!/bin/bash

# SynOS V1.0 Working ISO Builder
# Creates a bootable ISO with our debugged multiboot kernel

set -e

ISO_NAME="SynOS-v1.0-working-$(date +%Y%m%d).iso"
BUILD_DIR="build"
ISO_DIR="${BUILD_DIR}/iso"
KERNEL_BIN="build/kernel.bin"

echo "🔧 Building SynOS V1.0 Working ISO..."
echo "📅 $(date)"
echo "📦 Target: ${ISO_NAME}"

# Check if kernel exists
if [ ! -f "${KERNEL_BIN}" ]; then
    echo "❌ Kernel binary not found: ${KERNEL_BIN}"
    echo "   Run: cd core/kernel && make all"
    exit 1
fi

# Create clean build environment
echo "🧹 Preparing build environment..."
rm -rf "${ISO_DIR}"
mkdir -p "${ISO_DIR}"/{live,isolinux}

# Copy kernel
echo "📋 Copying kernel binary..."
cp "${KERNEL_BIN}" "${ISO_DIR}/live/vmlinuz"

# Create a minimal initrd
echo "🔧 Creating minimal initrd..."
INITRD_TMP="/tmp/synos-initrd-$$"
CURRENT_DIR="$(pwd)"
mkdir -p "${INITRD_TMP}"
echo "#!/bin/sh" > "${INITRD_TMP}/init"
echo "echo 'SynOS V1.0 Initrd Loaded'" >> "${INITRD_TMP}/init"
echo "exec /sbin/init" >> "${INITRD_TMP}/init"
chmod +x "${INITRD_TMP}/init"
(cd "${INITRD_TMP}" && find . | cpio -o -H newc | gzip > "${CURRENT_DIR}/${ISO_DIR}/live/initrd.img")
rm -rf "${INITRD_TMP}"

# Copy isolinux files
echo "📋 Setting up bootloader..."
if [ -d /usr/lib/ISOLINUX ]; then
    cp /usr/lib/ISOLINUX/isolinux.bin "${ISO_DIR}/isolinux/"
    cp /usr/lib/syslinux/modules/bios/*.c32 "${ISO_DIR}/isolinux/" 2>/dev/null || true
elif [ -d /usr/lib/syslinux ]; then
    cp /usr/lib/syslinux/isolinux.bin "${ISO_DIR}/isolinux/"
    cp /usr/lib/syslinux/*.c32 "${ISO_DIR}/isolinux/" 2>/dev/null || true
else
    echo "❌ ISOLINUX not found. Install syslinux-utils"
    exit 1
fi

# Create bootloader configuration
echo "⚙️ Configuring bootloader..."
cat > "${ISO_DIR}/isolinux/isolinux.cfg" << EOF
DEFAULT working
TIMEOUT 30
PROMPT 1

LABEL working
    MENU LABEL SynOS V1.0 Working Kernel
    KERNEL /live/vmlinuz
    APPEND initrd=/live/initrd.img boot=live config quiet

LABEL debug
    MENU LABEL SynOS V1.0 Debug Mode
    KERNEL /live/vmlinuz
    APPEND initrd=/live/initrd.img boot=live config debug
EOF

# Create filesystem manifest
echo "📄 Creating filesystem manifest..."
cat > "${ISO_DIR}/live/filesystem.manifest" << EOF
# SynOS V1.0 Working Kernel Package Manifest
synos-kernel-working
synos-minimal-runtime
EOF

# Create a minimal squashfs
echo "🗜️ Creating minimal filesystem..."
mkdir -p /tmp/synos-fs/{bin,sbin,etc,dev,proc,sys,tmp,var,usr}
echo "SynOS V1.0 Working" > /tmp/synos-fs/etc/version
mksquashfs /tmp/synos-fs "${ISO_DIR}/live/filesystem.squashfs" -comp xz -quiet
rm -rf /tmp/synos-fs

# Create the ISO
echo "💿 Building ISO image..."
genisoimage \
    -o "${BUILD_DIR}/${ISO_NAME}" \
    -b isolinux/isolinux.bin \
    -c isolinux/boot.cat \
    -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    -J -R -V "SynOS_V1.0_Working" \
    "${ISO_DIR}"

# Make it hybrid
if command -v isohybrid >/dev/null 2>&1; then
    echo "🔧 Making hybrid ISO..."
    isohybrid "${BUILD_DIR}/${ISO_NAME}"
fi

# Cleanup
echo "🧹 Cleaning up..."
rm -rf "${ISO_DIR}"

# Results
ISO_SIZE=$(du -h "${BUILD_DIR}/${ISO_NAME}" | cut -f1)
echo ""
echo "✅ SynOS V1.0 Working ISO Build Complete!"
echo "📁 Location: ${BUILD_DIR}/${ISO_NAME}"
echo "📊 Size: ${ISO_SIZE}"
echo "🔍 Components:"
echo "   - Working multiboot kernel"
echo "   - Minimal initrd"
echo "   - ISOLINUX bootloader"
echo "   - Minimal SquashFS"
echo ""
echo "🚀 Test with: qemu-system-x86_64 -cdrom ${BUILD_DIR}/${ISO_NAME} -m 512M"
echo "🔧 Serial test: qemu-system-x86_64 -cdrom ${BUILD_DIR}/${ISO_NAME} -m 512M -serial stdio -nographic"
