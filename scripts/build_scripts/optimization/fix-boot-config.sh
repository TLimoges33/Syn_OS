#!/bin/bash

# Fix SynOS boot configuration - remove Plymouth, add proper boot params
# This script fixes the hanging boot issue

set -e

ISO_DIR="/home/diablorain/Syn_OS/build/iso"
GRUB_CFG="$ISO_DIR/boot/grub/grub.cfg"
ISOLINUX_CFG="$ISO_DIR/isolinux/isolinux.cfg"
ISO_OUTPUT="/home/diablorain/Syn_OS/build/synos-v1.0-complete.iso"

echo "========================================================================"
echo "         FIXING SYNOS BOOT CONFIGURATION"
echo "========================================================================"
echo ""

# Backup current configs
echo "[1/4] Backing up current configs..."
cp "$GRUB_CFG" "$GRUB_CFG.bak"
[ -f "$ISOLINUX_CFG" ] && cp "$ISOLINUX_CFG" "$ISOLINUX_CFG.bak"

# Create new GRUB config without Plymouth splash
echo "[2/4] Creating new GRUB config (no Plymouth)..."
cat > "$GRUB_CFG" << 'EOF'
set default="0"
set timeout=30

if loadfont /boot/grub/unicode.pf2 ; then
    set gfxmode=auto
    insmod all_video
    insmod gfxterm
    terminal_output gfxterm
fi

set menu_color_normal=white/black
set menu_color_highlight=black/light-gray

menuentry "SynOS v1.0 - Live" {
    linux /casper/vmlinuz boot=casper noplymouth systemd.show_status=true ---
    initrd /casper/initrd
}

menuentry "SynOS v1.0 - Live (Safe Graphics)" {
    linux /casper/vmlinuz boot=casper nomodeset noplymouth systemd.show_status=true ---
    initrd /casper/initrd
}

menuentry "SynOS v1.0 - Live (Verbose)" {
    linux /casper/vmlinuz boot=casper noplymouth systemd.show_status=true debug ---
    initrd /casper/initrd
}

menuentry "SynOS v1.0 - Live with Persistence" {
    linux /casper/vmlinuz boot=casper persistent noplymouth systemd.show_status=true ---
    initrd /casper/initrd
}

menuentry "SynOS v1.0 - Forensics Mode" {
    linux /casper/vmlinuz boot=casper nopersistent readonly toram noplymouth ---
    initrd /casper/initrd
}

menuentry "Install SynOS v1.0" {
    linux /casper/vmlinuz boot=casper only-ubiquity noplymouth ---
    initrd /casper/initrd
}
EOF

echo "GRUB config updated"

# Update ISOLINUX config if it exists
if [ -f "$ISOLINUX_CFG" ]; then
    echo "[3/4] Updating ISOLINUX config..."
    cat > "$ISOLINUX_CFG" << 'EOF'
DEFAULT live
LABEL live
  menu label ^SynOS v1.0 - Live
  kernel /casper/vmlinuz
  append initrd=/casper/initrd boot=casper noplymouth systemd.show_status=true ---

LABEL live-safe
  menu label SynOS v1.0 - Live (Safe Graphics)
  kernel /casper/vmlinuz
  append initrd=/casper/initrd boot=casper nomodeset noplymouth systemd.show_status=true ---

LABEL live-verbose
  menu label SynOS v1.0 - Live (Verbose)
  kernel /casper/vmlinuz
  append initrd=/casper/initrd boot=casper noplymouth systemd.show_status=true debug ---

LABEL persistent
  menu label SynOS v1.0 - Live with Persistence
  kernel /casper/vmlinuz
  append initrd=/casper/initrd boot=casper persistent noplymouth systemd.show_status=true ---

LABEL forensics
  menu label SynOS v1.0 - Forensics Mode
  kernel /casper/vmlinuz
  append initrd=/casper/initrd boot=casper nopersistent readonly toram noplymouth ---

PROMPT 0
TIMEOUT 300
EOF
    echo "ISOLINUX config updated"
else
    echo "ISOLINUX config not found, skipping"
fi

# Recreate UEFI bootloader with new config
echo "[4/4] Recreating UEFI bootloader..."
if command -v grub-mkstandalone >/dev/null 2>&1; then
    grub-mkstandalone \
        --format=x86_64-efi \
        --output=$ISO_DIR/EFI/BOOT/BOOTX64.EFI \
        --locales="" \
        --fonts="" \
        "boot/grub/grub.cfg=$GRUB_CFG"
    echo "UEFI bootloader recreated"
else
    echo "WARNING: grub-mkstandalone not found, UEFI boot may not work"
fi

echo ""
echo "========================================================================"
echo "Boot configuration fixed!"
echo "========================================================================"
echo ""
echo "Changes made:"
echo "  - Removed 'quiet splash' (Plymouth hanging)"
echo "  - Added 'noplymouth' (disable Plymouth completely)"
echo "  - Added 'systemd.show_status=true' (show boot messages)"
echo "  - Added 'Verbose' boot option for debugging"
echo ""
echo "Next: Rebuild ISO with:"
echo "  sudo /home/diablorain/Syn_OS/scripts/build/rebuild-iso-only.sh"
echo ""
