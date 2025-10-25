#!/bin/bash

# Quick rebuild ISO without recompressing SquashFS
# This takes ~5 minutes instead of 90 minutes

set -e

ISO_DIR="/home/diablorain/Syn_OS/build/iso"
ISO_OUTPUT="/home/diablorain/Syn_OS/build/synos-v1.0-complete.iso"
ISO_OLD="$ISO_OUTPUT.old"

echo "========================================================================"
echo "         QUICK ISO REBUILD - SynOS v1.0"
echo "========================================================================"
echo ""
echo "This rebuilds only the ISO image, reusing existing SquashFS"
echo "Time: ~5 minutes (vs 90 minutes for full rebuild)"
echo ""

# Backup old ISO
if [ -f "$ISO_OUTPUT" ]; then
    echo "[1/3] Backing up old ISO..."
    mv "$ISO_OUTPUT" "$ISO_OLD"
    echo "Old ISO backed up to: $ISO_OLD"
fi

# Rebuild ISO image
echo ""
echo "[2/3] Generating new ISO image..."
echo ""

xorriso -as mkisofs \
    -r -V "SynOS v1.0" \
    -o "$ISO_OUTPUT" \
    -J -J -joliet-long \
    -iso-level 3 \
    -cache-inodes \
    -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin \
    -b isolinux/isolinux.bin \
    -c isolinux/boot.cat \
    -boot-load-size 4 \
    -boot-info-table \
    -no-emul-boot \
    -eltorito-alt-boot \
    -e EFI/BOOT/BOOTX64.EFI \
    -no-emul-boot \
    -isohybrid-gpt-basdat \
    -isohybrid-apm-hfsplus \
    "$ISO_DIR"

echo ""
echo "[3/3] Generating checksums..."

# Generate new checksums
cd "$(dirname "$ISO_OUTPUT")"
md5sum "$(basename "$ISO_OUTPUT")" > "${ISO_OUTPUT}.md5"
sha256sum "$(basename "$ISO_OUTPUT")" > "${ISO_OUTPUT}.sha256"

echo ""
echo "========================================================================"
echo "                    ISO REBUILD COMPLETE!"
echo "========================================================================"
echo ""
echo "ISO File: $ISO_OUTPUT"
echo "Size: $(du -h "$ISO_OUTPUT" | cut -f1)"
echo ""
echo "Checksums:"
cat "${ISO_OUTPUT}.md5"
cat "${ISO_OUTPUT}.sha256"
echo ""
echo "Next: Test with QEMU"
echo "  qemu-system-x86_64 -m 4G -cdrom $ISO_OUTPUT -enable-kvm"
echo ""
