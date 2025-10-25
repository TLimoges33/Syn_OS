#!/bin/bash
# Phase 6: ISO Generation for SynOS v1.0
# Complete ISO build from verified chroot

set -e

CHROOT=/home/diablorain/Syn_OS/build/synos-v1.0/work/chroot
ISO_DIR=/home/diablorain/Syn_OS/build/iso
ISO_OUTPUT=/home/diablorain/Syn_OS/build/synos-v1.0-complete.iso
LOG_DIR=/home/diablorain/Syn_OS/logs
LOG_FILE=$LOG_DIR/phase6-iso-generation-$(date +%Y%m%d-%H%M%S).log

mkdir -p $LOG_DIR

echo "========================================================================" | tee "$LOG_FILE"
echo "         PHASE 6: ISO GENERATION - SynOS v1.0" | tee -a "$LOG_FILE"
echo "========================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Started: $(date)" | tee -a "$LOG_FILE"
echo "Chroot: $CHROOT" | tee -a "$LOG_FILE"
echo "ISO Output: $ISO_OUTPUT" | tee -a "$LOG_FILE"
echo "Log: $LOG_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Check dependencies
echo "========================================================================" | tee -a "$LOG_FILE"
echo "CHECKING DEPENDENCIES" | tee -a "$LOG_FILE"
echo "========================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

MISSING_DEPS=()
for dep in mksquashfs xorriso grub-mkrescue grub-mkstandalone syslinux md5sum sha256sum; do
    if ! command -v $dep >/dev/null 2>&1; then
        echo "  X $dep - NOT FOUND" | tee -a "$LOG_FILE"
        MISSING_DEPS+=("$dep")
    else
        echo "  OK $dep" | tee -a "$LOG_FILE"
    fi
done

# Check for isolinux binary file
if [ -f /usr/lib/ISOLINUX/isolinux.bin ] || [ -f /usr/lib/syslinux/modules/bios/isolinux.bin ]; then
    echo "  OK isolinux (binary found)" | tee -a "$LOG_FILE"
else
    echo "  X isolinux - NOT FOUND" | tee -a "$LOG_FILE"
    MISSING_DEPS+=("isolinux")
fi

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "ERROR: Missing dependencies: ${MISSING_DEPS[*]}" | tee -a "$LOG_FILE"
    exit 1
fi
echo "" | tee -a "$LOG_FILE"

# [1/8] Clean chroot
echo "========================================================================" | tee -a "$LOG_FILE"
echo "[1/8] CLEANING CHROOT" | tee -a "$LOG_FILE"
echo "========================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "Removing apt cache..." | tee -a "$LOG_FILE"
chroot $CHROOT apt-get clean 2>&1 | tee -a "$LOG_FILE"

echo "Removing temporary files..." | tee -a "$LOG_FILE"
rm -rf $CHROOT/tmp/* 2>&1 | tee -a "$LOG_FILE" || true
rm -rf $CHROOT/var/tmp/* 2>&1 | tee -a "$LOG_FILE" || true

echo "Truncating log files..." | tee -a "$LOG_FILE"
find $CHROOT/var/log -type f -exec truncate -s 0 {} \; 2>&1 | tee -a "$LOG_FILE"

echo "Removing bash history..." | tee -a "$LOG_FILE"
rm -f $CHROOT/root/.bash_history 2>&1 | tee -a "$LOG_FILE" || true
rm -f $CHROOT/home/*/.bash_history 2>&1 | tee -a "$LOG_FILE" || true

CLEANED_SIZE=$(du -sh $CHROOT 2>/dev/null | awk '{print $1}')
echo "Chroot cleaned (size: $CLEANED_SIZE)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# [2/8] Create ISO directory structure
echo "========================================================================" | tee -a "$LOG_FILE"
echo "[2/8] CREATING ISO DIRECTORY STRUCTURE" | tee -a "$LOG_FILE"
echo "========================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

rm -rf $ISO_DIR 2>&1 | tee -a "$LOG_FILE" || true
mkdir -p $ISO_DIR/{casper,isolinux,boot/grub,EFI/BOOT,.disk} 2>&1 | tee -a "$LOG_FILE"

echo "ISO directory structure created" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# [3/8] Generate SquashFS filesystem
echo "========================================================================" | tee -a "$LOG_FILE"
echo "[3/8] GENERATING SQUASHFS FILESYSTEM" | tee -a "$LOG_FILE"
echo "========================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "This will take 15-30 minutes for 37GB chroot..." | tee -a "$LOG_FILE"
echo "Starting mksquashfs with high compression..." | tee -a "$LOG_FILE"

mksquashfs $CHROOT $ISO_DIR/casper/filesystem.squashfs \
    -comp zstd \
    -Xcompression-level 15 \
    -b 1M \
    -processors 4 \
    -no-duplicates \
    -no-exports \
    -e boot 2>&1 | tee -a "$LOG_FILE" || { echo "mksquashfs failed!"; exit 1; }

SQUASHFS_SIZE=$(du -sh $ISO_DIR/casper/filesystem.squashfs 2>/dev/null | awk '{print $1}')
echo "SquashFS created (size: $SQUASHFS_SIZE)" | tee -a "$LOG_FILE"

# Create filesystem size file
printf $(du -sx --block-size=1 $CHROOT | cut -f1) > $ISO_DIR/casper/filesystem.size
echo "Filesystem size file created" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# [4/8] Copy kernel and initrd
echo "========================================================================" | tee -a "$LOG_FILE"
echo "[4/8] COPYING KERNEL AND INITRD" | tee -a "$LOG_FILE"
echo "========================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

KERNEL=$(ls $CHROOT/boot/vmlinuz-* 2>/dev/null | sort -V | tail -n 1)
INITRD=$(ls $CHROOT/boot/initrd.img-* 2>/dev/null | sort -V | tail -n 1)

if [ -z "$KERNEL" ] || [ -z "$INITRD" ]; then
    echo "ERROR: Kernel or initrd not found in chroot" | tee -a "$LOG_FILE"
    exit 1
fi

cp "$KERNEL" $ISO_DIR/casper/vmlinuz 2>&1 | tee -a "$LOG_FILE"
cp "$INITRD" $ISO_DIR/casper/initrd 2>&1 | tee -a "$LOG_FILE"

echo "Kernel: $(basename "$KERNEL")" | tee -a "$LOG_FILE"
echo "Initrd: $(basename "$INITRD")" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# [5/8] Configure bootloaders
echo "========================================================================" | tee -a "$LOG_FILE"
echo "[5/8] CONFIGURING BOOTLOADERS" | tee -a "$LOG_FILE"
echo "========================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# GRUB configuration
echo "Creating GRUB configuration..." | tee -a "$LOG_FILE"
cat > $ISO_DIR/boot/grub/grub.cfg << 'GRUBEOF'
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
    linux /casper/vmlinuz boot=casper quiet splash ---
    initrd /casper/initrd
}

menuentry "SynOS v1.0 - Live (Safe Graphics)" {
    linux /casper/vmlinuz boot=casper nomodeset quiet splash ---
    initrd /casper/initrd
}

menuentry "SynOS v1.0 - Live with Persistence" {
    linux /casper/vmlinuz boot=casper persistent quiet splash ---
    initrd /casper/initrd
}

menuentry "SynOS v1.0 - Forensics Mode" {
    linux /casper/vmlinuz boot=casper nopersistent readonly toram ---
    initrd /casper/initrd
}

menuentry "Install SynOS v1.0" {
    linux /casper/vmlinuz boot=casper only-ubiquity quiet splash ---
    initrd /casper/initrd
}
GRUBEOF

echo "GRUB configuration created" | tee -a "$LOG_FILE"

# ISOLINUX configuration
echo "Creating ISOLINUX configuration..." | tee -a "$LOG_FILE"
cat > $ISO_DIR/isolinux/isolinux.cfg << 'ISOLINUXEOF'
DEFAULT live
LABEL live
  menu label Start SynOS v1.0
  kernel /casper/vmlinuz
  append initrd=/casper/initrd boot=casper quiet splash ---

LABEL live-safe
  menu label Start SynOS v1.0 (Safe Graphics)
  kernel /casper/vmlinuz
  append initrd=/casper/initrd boot=casper nomodeset quiet splash ---

LABEL live-persistent
  menu label Start SynOS v1.0 with Persistence
  kernel /casper/vmlinuz
  append initrd=/casper/initrd boot=casper persistent quiet splash ---

LABEL forensic
  menu label Start SynOS v1.0 (Forensics Mode)
  kernel /casper/vmlinuz
  append initrd=/casper/initrd boot=casper readonly toram ---

LABEL install
  menu label Install SynOS v1.0
  kernel /casper/vmlinuz
  append initrd=/casper/initrd boot=casper only-ubiquity quiet splash ---

DISPLAY isolinux.txt
TIMEOUT 300
PROMPT 1
ISOLINUXEOF

cat > $ISO_DIR/isolinux/isolinux.txt << 'TXTEOF'
***********************************
*      SynOS v1.0                 *
*      Security & AI OS           *
***********************************
Press ENTER to boot
TXTEOF

echo "ISOLINUX configuration created" | tee -a "$LOG_FILE"

# Copy ISOLINUX binaries
echo "Copying ISOLINUX binaries..." | tee -a "$LOG_FILE"
if [ -f /usr/lib/ISOLINUX/isolinux.bin ]; then
    cp /usr/lib/ISOLINUX/isolinux.bin $ISO_DIR/isolinux/ 2>&1 | tee -a "$LOG_FILE"
elif [ -f /usr/lib/syslinux/modules/bios/isolinux.bin ]; then
    cp /usr/lib/syslinux/modules/bios/isolinux.bin $ISO_DIR/isolinux/ 2>&1 | tee -a "$LOG_FILE"
fi

if [ -f /usr/lib/syslinux/modules/bios/ldlinux.c32 ]; then
    cp /usr/lib/syslinux/modules/bios/*.c32 $ISO_DIR/isolinux/ 2>&1 | tee -a "$LOG_FILE"
fi

echo "ISOLINUX binaries copied" | tee -a "$LOG_FILE"

# Create UEFI bootloader
echo "Creating UEFI bootloader..." | tee -a "$LOG_FILE"

# Check if grub-mkstandalone is available
if ! command -v grub-mkstandalone >/dev/null 2>&1; then
    echo "WARNING: grub-mkstandalone not found, UEFI boot may not work" | tee -a "$LOG_FILE"
else
    # Create UEFI boot image using existing grub.cfg
    grub-mkstandalone \
        --format=x86_64-efi \
        --output=$ISO_DIR/EFI/BOOT/BOOTX64.EFI \
        --locales="" \
        --fonts="" \
        "boot/grub/grub.cfg=$ISO_DIR/boot/grub/grub.cfg" 2>&1 | tee -a "$LOG_FILE"

    if [ -f "$ISO_DIR/EFI/BOOT/BOOTX64.EFI" ]; then
        echo "UEFI bootloader created successfully" | tee -a "$LOG_FILE"
    else
        echo "WARNING: UEFI bootloader creation failed" | tee -a "$LOG_FILE"
    fi
fi

echo "" | tee -a "$LOG_FILE"

# [6/8] Create disk info
echo "========================================================================" | tee -a "$LOG_FILE"
echo "[6/8] CREATING DISK INFO" | tee -a "$LOG_FILE"
echo "========================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "SynOS v1.0 - Security & AI Operating System" > $ISO_DIR/.disk/info
echo "SynOS v1.0" > $ISO_DIR/.disk/release_notes_url
echo "https://github.com/TLimoges33/Syn_OS" > $ISO_DIR/.disk/base_installable
touch $ISO_DIR/.disk/casper-uuid-generic

echo "Disk info created" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# [7/8] Generate ISO
echo "========================================================================" | tee -a "$LOG_FILE"
echo "[7/8] GENERATING ISO IMAGE" | tee -a "$LOG_FILE"
echo "========================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "Building hybrid BIOS/UEFI bootable ISO (this may take 5-10 minutes)..." | tee -a "$LOG_FILE"

xorriso -as mkisofs \
    -iso-level 3 \
    -full-iso9660-filenames \
    -volid "SynOS_v1.0" \
    -appid "SynOS v1.0" \
    -publisher "SynOS Project" \
    -preparer "SynOS Build System" \
    -eltorito-boot isolinux/isolinux.bin \
    -eltorito-catalog isolinux/boot.cat \
    -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin \
    -eltorito-alt-boot \
    -e EFI/BOOT/BOOTX64.EFI \
    -no-emul-boot \
    -isohybrid-gpt-basdat \
    -output $ISO_OUTPUT \
    $ISO_DIR 2>&1 | tee -a "$LOG_FILE"

if [ -f "$ISO_OUTPUT" ]; then
    ISO_SIZE=$(du -sh $ISO_OUTPUT | awk '{print $1}')
    echo "ISO generated successfully!" | tee -a "$LOG_FILE"
    echo "Location: $ISO_OUTPUT" | tee -a "$LOG_FILE"
    echo "Size: $ISO_SIZE" | tee -a "$LOG_FILE"
else
    echo "ERROR: ISO generation failed!" | tee -a "$LOG_FILE"
    exit 1
fi
echo "" | tee -a "$LOG_FILE"

# [8/8] Generate checksums
echo "========================================================================" | tee -a "$LOG_FILE"
echo "[8/8] GENERATING CHECKSUMS" | tee -a "$LOG_FILE"
echo "========================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "Generating MD5 checksum..." | tee -a "$LOG_FILE"
md5sum $ISO_OUTPUT > ${ISO_OUTPUT}.md5 2>&1 | tee -a "$LOG_FILE"
echo "MD5: ${ISO_OUTPUT}.md5" | tee -a "$LOG_FILE"

echo "Generating SHA256 checksum..." | tee -a "$LOG_FILE"
sha256sum $ISO_OUTPUT > ${ISO_OUTPUT}.sha256 2>&1 | tee -a "$LOG_FILE"
echo "SHA256: ${ISO_OUTPUT}.sha256" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "Checksums:" | tee -a "$LOG_FILE"
cat ${ISO_OUTPUT}.md5 | tee -a "$LOG_FILE"
cat ${ISO_OUTPUT}.sha256 | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Final summary
echo "========================================================================" | tee -a "$LOG_FILE"
echo "                    PHASE 6 COMPLETE!" | tee -a "$LOG_FILE"
echo "========================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "ISO Generation Summary:" | tee -a "$LOG_FILE"
echo "ISO File: $ISO_OUTPUT" | tee -a "$LOG_FILE"
echo "ISO Size: $ISO_SIZE" | tee -a "$LOG_FILE"
echo "SquashFS: $SQUASHFS_SIZE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Boot Modes: UEFI + BIOS (Hybrid)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Boot Menu Options:" | tee -a "$LOG_FILE"
echo "  1. SynOS v1.0 - Live" | tee -a "$LOG_FILE"
echo "  2. SynOS v1.0 - Live (Safe Graphics)" | tee -a "$LOG_FILE"
echo "  3. SynOS v1.0 - Live with Persistence" | tee -a "$LOG_FILE"
echo "  4. SynOS v1.0 - Forensics Mode" | tee -a "$LOG_FILE"
echo "  5. Install SynOS v1.0" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Next Steps:" | tee -a "$LOG_FILE"
echo "  Test in QEMU: qemu-system-x86_64 -m 4G -cdrom $ISO_OUTPUT" | tee -a "$LOG_FILE"
echo "  Write to USB: sudo dd if=$ISO_OUTPUT of=/dev/sdX bs=4M status=progress" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Completed: $(date)" | tee -a "$LOG_FILE"
echo "Log: $LOG_FILE" | tee -a "$LOG_FILE"
echo "========================================================================" | tee -a "$LOG_FILE"

# Create completion marker
touch /home/diablorain/Syn_OS/build/PHASE6_COMPLETE.txt
cat > /home/diablorain/Syn_OS/build/PHASE6_COMPLETE.txt << MARKEREOF
SynOS v1.0 - Phase 6: ISO Generation
Status: COMPLETE
Completed: $(date)

ISO Details:
- File: $ISO_OUTPUT
- Size: $ISO_SIZE
- SquashFS: $SQUASHFS_SIZE
- Boot: UEFI + BIOS (Hybrid)

All 6 phases complete - 100% DONE!
MARKEREOF

echo "Phase 6 completion marker created" | tee -a "$LOG_FILE"
echo "BUILD COMPLETE! SynOS v1.0 is ready!" | tee -a "$LOG_FILE"
