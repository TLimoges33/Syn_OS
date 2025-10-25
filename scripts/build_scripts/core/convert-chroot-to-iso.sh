#!/bin/bash

# Quick script to convert existing chroot to proper live ISO
# Uses the 2.3GB chroot we already built

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         Convert Existing Chroot to Live ISO                 ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}[ERROR]${NC} This script must be run as root"
    echo -e "${YELLOW}[INFO]${NC} Run with: sudo $0"
    exit 1
fi

# Find the most recent workspace
WORKSPACE=$(ls -td /home/diablorain/Syn_OS/build/workspace-* 2>/dev/null | head -1)

if [[ -z "$WORKSPACE" ]]; then
    echo -e "${RED}[ERROR]${NC} No workspace found in build directory"
    exit 1
fi

CHROOT_DIR="$WORKSPACE/chroot"
ISO_DIR="$WORKSPACE/iso-rebuild"
OUTPUT_ISO="/home/diablorain/Syn_OS/build/SynOS-v1.0-Live-$(date +%Y%m%d-%H%M%S).iso"

echo -e "${BLUE}[INFO]${NC} Using workspace: $WORKSPACE"
echo -e "${BLUE}[INFO]${NC} Chroot: $CHROOT_DIR"

# Verify chroot exists
if [[ ! -d "$CHROOT_DIR" ]]; then
    echo -e "${RED}[ERROR]${NC} Chroot directory not found: $CHROOT_DIR"
    exit 1
fi

# Check chroot size
CHROOT_SIZE=$(du -sh "$CHROOT_DIR" | cut -f1)
echo -e "${GREEN}[INFO]${NC} Chroot size: $CHROOT_SIZE"

# Create fresh ISO directory
echo -e "${BLUE}[INFO]${NC} Creating ISO structure..."
rm -rf "$ISO_DIR"
mkdir -p "$ISO_DIR/live"
mkdir -p "$ISO_DIR/boot/grub"

# Create squashfs filesystem
echo -e "${CYAN}[BUILD]${NC} Creating squashfs filesystem..."
echo -e "${YELLOW}[INFO]${NC} This may take 5-10 minutes depending on system speed"

if mksquashfs "$CHROOT_DIR" "$ISO_DIR/live/filesystem.squashfs" \
    -comp xz \
    -b 1M \
    -Xbcj x86 \
    -e boot \
    -noappend; then
    SQUASHFS_SIZE=$(du -h "$ISO_DIR/live/filesystem.squashfs" | cut -f1)
    echo -e "${GREEN}[SUCCESS]${NC} Squashfs created: $SQUASHFS_SIZE"
else
    echo -e "${RED}[ERROR]${NC} Failed to create squashfs"
    exit 1
fi

# Copy kernel and initrd
echo -e "${BLUE}[INFO]${NC} Copying kernel and initrd..."

if [[ -f "$CHROOT_DIR/vmlinuz" ]]; then
    cp "$CHROOT_DIR/vmlinuz" "$ISO_DIR/live/vmlinuz"
    cp "$CHROOT_DIR/initrd.img" "$ISO_DIR/live/initrd.img"
    echo -e "${GREEN}[SUCCESS]${NC} Copied from chroot root"
elif [[ -f "$CHROOT_DIR"/boot/vmlinuz-* ]]; then
    cp "$CHROOT_DIR"/boot/vmlinuz-* "$ISO_DIR/live/vmlinuz"
    cp "$CHROOT_DIR"/boot/initrd.img-* "$ISO_DIR/live/initrd.img"
    echo -e "${GREEN}[SUCCESS]${NC} Copied from /boot directory"
else
    echo -e "${RED}[ERROR]${NC} Cannot find kernel/initrd"
    exit 1
fi

# Create GRUB configuration for live boot
echo -e "${BLUE}[INFO]${NC} Creating GRUB configuration..."

cat > "$ISO_DIR/boot/grub/grub.cfg" << 'EOF'
set timeout=10
set default=0

menuentry "SynOS v1.0 - Live Boot" {
    linux /live/vmlinuz boot=live components quiet splash
    initrd /live/initrd.img
}

menuentry "SynOS v1.0 - Live Boot (Safe Mode)" {
    linux /live/vmlinuz boot=live components noapic noapm nodma nomce nolapic nosmp
    initrd /live/initrd.img
}

menuentry "SynOS v1.0 - Live Boot (Debug Mode)" {
    linux /live/vmlinuz boot=live components debug verbose systemd.log_level=debug
    initrd /live/initrd.img
}

menuentry "SynOS v1.0 - Live Boot (No Graphics)" {
    linux /live/vmlinuz boot=live components nofb nomodeset vga=normal
    initrd /live/initrd.img
}

menuentry "SynOS v1.0 - Live Boot (Persistence)" {
    linux /live/vmlinuz boot=live components persistent
    initrd /live/initrd.img
}
EOF

echo -e "${GREEN}[SUCCESS]${NC} GRUB configuration created"

# Create system info file
cat > "$ISO_DIR/SYNOS_INFO.txt" << EOF
╔════════════════════════════════════════════════════════════════════════════╗
║                  SynOS v1.0 - Ultimate Live Edition                        ║
╚════════════════════════════════════════════════════════════════════════════╝

Build Information:
  Build Date:    $(date '+%Y-%m-%d %H:%M:%S')
  Build Host:    $(hostname)
  Chroot Size:   $CHROOT_SIZE
  Squashfs Size: $SQUASHFS_SIZE

Features:
  ✓ Debian 12 Bookworm base
  ✓ Parrot Security tools integration
  ✓ Live boot with persistence support
  ✓ Hybrid BIOS/UEFI compatible
  ✓ Security tools: Hydra, Nikto, Nmap, and more

Boot Instructions:
  1. Boot from this ISO image (USB/CD/VM)
  2. Select boot option from GRUB menu
  3. System will boot into live environment

For more information:
  Project: https://github.com/TLimoges33/Syn_OS
EOF

# Generate ISO
echo -e "${CYAN}[BUILD]${NC} Generating bootable ISO..."
echo -e "${YELLOW}[INFO]${NC} Output: $OUTPUT_ISO"

if grub-mkrescue -o "$OUTPUT_ISO" "$ISO_DIR"; then
    echo -e "${GREEN}[SUCCESS]${NC} ISO created successfully!"
else
    echo -e "${RED}[ERROR]${NC} ISO creation failed"
    exit 1
fi

# Generate checksums
echo -e "${BLUE}[INFO]${NC} Generating checksums..."
sha256sum "$OUTPUT_ISO" > "${OUTPUT_ISO}.sha256"
md5sum "$OUTPUT_ISO" > "${OUTPUT_ISO}.md5"

# Final verification
ISO_SIZE=$(du -h "$OUTPUT_ISO" | cut -f1)
ISO_SIZE_MB=$(du -m "$OUTPUT_ISO" | cut -f1)

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    BUILD COMPLETE!                           ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}ISO Details:${NC}"
echo -e "  Location:  $OUTPUT_ISO"
echo -e "  Size:      $ISO_SIZE (${ISO_SIZE_MB}MB)"
echo -e "  SHA256:    $(cat "${OUTPUT_ISO}.sha256" | cut -d' ' -f1)"
echo -e "  MD5:       $(cat "${OUTPUT_ISO}.md5" | cut -d' ' -f1)"
echo ""

# Check if it's the right size
if [[ $ISO_SIZE_MB -lt 500 ]]; then
    echo -e "${RED}[WARNING]${NC} ISO seems small (${ISO_SIZE_MB}MB)"
    echo -e "${YELLOW}[INFO]${NC} Expected 1GB+ for full system"
else
    echo -e "${GREEN}[SUCCESS]${NC} ISO size looks correct!"
fi

echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo -e "  1. Test in VM: ${YELLOW}qemu-system-x86_64 -cdrom $OUTPUT_ISO -m 4096${NC}"
echo -e "  2. Write to USB: ${YELLOW}sudo dd if=$OUTPUT_ISO of=/dev/sdX bs=4M status=progress${NC}"
echo -e "  3. Verify contents: ${YELLOW}sudo mount -o loop $OUTPUT_ISO /mnt${NC}"
echo ""
