#!/usr/bin/env bash
################################################################################
# SynOS ULTIMATE ISO Enhancement Script
# Phase 6: ISO Rebuild & Finalization
################################################################################

set -euo pipefail

CHROOT_DIR="${1:-/home/diablorain/Syn_OS/build/synos-v1.0/chroot}"
PROJECT_ROOT="/home/diablorain/Syn_OS"
BUILD_DIR="${PROJECT_ROOT}/build"
ISO_DIR="${BUILD_DIR}/iso"
OUTPUT_DIR="${BUILD_DIR}"

source "$PROJECT_ROOT/scripts/build/enhancement-utils.sh" 2>/dev/null || true

section "Phase 6: ISO Rebuild & Finalization"

################################################################################
# CLEANUP CHROOT
################################################################################

cleanup_chroot() {
    log "Cleaning up chroot environment..."

    chroot "$CHROOT_DIR" bash -c '
        # Clean package cache
        apt-get clean
        apt-get autoclean
        apt-get autoremove -y

        # Remove temporary files
        rm -rf /tmp/*
        rm -rf /var/tmp/*
        rm -rf /var/cache/apt/archives/*.deb

        # Clean logs
        find /var/log -type f -name "*.log" -exec truncate -s 0 {} \;
        find /var/log -type f -name "*.gz" -delete
        find /var/log -type f -name "*.old" -delete

        # Remove bash history
        rm -f /root/.bash_history
        rm -f /home/*/.bash_history 2>/dev/null || true

        # Clear machine-id
        truncate -s 0 /etc/machine-id
    '

    # Unmount virtual filesystems
    unmount_chroot "$CHROOT_DIR"
}

################################################################################
# UPDATE GRUB CONFIGURATION
################################################################################

update_grub_config() {
    log "Updating GRUB configuration for ISO..."

    mkdir -p "$ISO_DIR/boot/grub"

    cat > "$ISO_DIR/boot/grub/grub.cfg" <<'EOF'
set timeout=30
set default=0

loadfont unicode

insmod all_video
insmod gfxterm
insmod png

set gfxmode=auto
set gfxpayload=keep

terminal_output gfxterm

if [ -f /boot/grub/themes/synos/theme.txt ]; then
    set theme=/boot/grub/themes/synos/theme.txt
fi

menuentry "SynOS 1.0.0 Ultimate (Live)" {
    linux /casper/vmlinuz boot=casper quiet splash noeject noprompt --
    initrd /casper/initrd
}

menuentry "SynOS 1.0.0 Ultimate (Safe Mode)" {
    linux /casper/vmlinuz boot=casper xforcevesa nomodeset noeject noprompt --
    initrd /casper/initrd
}

menuentry "SynOS 1.0.0 Ultimate (Install)" {
    linux /casper/vmlinuz boot=casper only-ubiquity quiet splash noeject noprompt --
    initrd /casper/initrd
}

menuentry "Check disc for defects" {
    linux /casper/vmlinuz boot=casper integrity-check quiet splash noeject noprompt --
    initrd /casper/initrd
}

menuentry "Memory test (memtest86+)" {
    linux16 /boot/memtest86+.bin
}

menuentry "Boot from first hard disk" {
    set root=(hd0)
    chainloader +1
}
EOF
}

################################################################################
# CREATE MANIFEST
################################################################################

create_manifest() {
    log "Creating package manifest..."

    mkdir -p "$ISO_DIR/casper"

    chroot "$CHROOT_DIR" dpkg-query -W --showformat='${Package} ${Version}\n' > \
        "$ISO_DIR/casper/filesystem.manifest"

    cp "$ISO_DIR/casper/filesystem.manifest" \
        "$ISO_DIR/casper/filesystem.manifest-desktop"
}

################################################################################
# BUILD SQUASHFS
################################################################################

build_squashfs() {
    log "Building compressed squashfs filesystem..."

    local chroot_size=$(du -sh "$CHROOT_DIR" | cut -f1)
    log "Chroot size: $chroot_size (this will take time to compress)"

    timer_start

    # Remove old squashfs if exists
    rm -f "$ISO_DIR/casper/filesystem.squashfs"

    # Create squashfs with VISIBLE progress (removed -no-progress)
    # Using gzip instead of xz for faster compression (still good compression ratio)
    log "Starting mksquashfs compression (you'll see progress bars)..."
    mksquashfs "$CHROOT_DIR" "$ISO_DIR/casper/filesystem.squashfs" \
        -comp gzip \
        -b 1M \
        -progress

    echo ""
    timer_end "Squashfs creation"

    # Write filesystem size
    printf $(du -sx --block-size=1 "$CHROOT_DIR" | cut -f1) > \
        "$ISO_DIR/casper/filesystem.size"
}

################################################################################
# COPY KERNEL AND INITRD
################################################################################

copy_kernel_initrd() {
    log "Copying kernel and initrd..."

    mkdir -p "$ISO_DIR/casper"

    # Find and copy kernel
    cp "$CHROOT_DIR"/boot/vmlinuz-* "$ISO_DIR/casper/vmlinuz" 2>/dev/null || \
        warn "Kernel not found in chroot"

    # Find and copy initrd
    cp "$CHROOT_DIR"/boot/initrd.img-* "$ISO_DIR/casper/initrd" 2>/dev/null || \
        warn "Initrd not found in chroot"

    # Copy memtest if available
    cp "$CHROOT_DIR"/boot/memtest86+*.bin "$ISO_DIR/boot/memtest86+.bin" 2>/dev/null || true
}

################################################################################
# CREATE ISO METADATA
################################################################################

create_iso_metadata() {
    log "Creating ISO metadata files..."

    mkdir -p "$ISO_DIR/.disk"

    # Disc info
    echo "SynOS 1.0.0 Ultimate - AI-Powered Security OS" > "$ISO_DIR/.disk/info"

    # Release notes
    cat > "$ISO_DIR/.disk/release_notes_url" <<'EOF'
https://github.com/diablorain/Syn_OS/releases
EOF

    # Base installable flag
    touch "$ISO_DIR/.disk/base_installable"

    # CD type
    echo "live" > "$ISO_DIR/.disk/cd_type"

    # Create README
    cat > "$ISO_DIR/README.txt" <<'EOF'
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              SynOS 1.0.0 Ultimate                            ║
║         AI-Powered Security Operating System                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

Welcome to SynOS!

This is a live/installation ISO that includes:
  • 500+ pre-installed security tools
  • AI-powered threat detection
  • Organized tools menu (11 categories)
  • Multiple desktop environments (MATE, KDE, XFCE, Cinnamon)
  • Comprehensive documentation
  • Pre-installed GitHub security resources

BOOT OPTIONS:
  1. Live Mode - Try SynOS without installing
  2. Safe Mode - Boot with basic graphics drivers
  3. Install - Install SynOS to your hard drive
  4. Memory Test - Check your RAM

SYSTEM REQUIREMENTS:
  • 4GB RAM minimum (8GB recommended)
  • 50GB disk space for installation
  • 64-bit processor
  • UEFI or BIOS boot support

GETTING STARTED:
  1. Boot from the ISO
  2. Select "SynOS 1.0.0 Ultimate (Live)"
  3. Wait for desktop to load
  4. Run 'synos-demo' from terminal for feature showcase
  5. Access tools from Applications → SynOS Tools

INSTALLATION:
  • In live mode, double-click "Install SynOS" on desktop
  • Or boot directly with "Install" option from GRUB menu

DOCUMENTATION:
  • GitHub: https://github.com/diablorain/Syn_OS
  • Wiki: https://github.com/diablorain/Syn_OS/wiki
  • Issues: https://github.com/diablorain/Syn_OS/issues

LEGAL NOTICE:
⚠️  These tools are for authorized security testing only.
    Unauthorized access to computer systems is illegal.

Enjoy SynOS!
EOF
}

################################################################################
# BUILD ISO IMAGE
################################################################################

build_iso() {
    log "Building ISO image..."

    timer_start

    local iso_name="SynOS-v1.0.0-Ultimate-$(date +%Y%m%d).iso"
    local iso_path="$OUTPUT_DIR/$iso_name"

    # Remove old ISO if exists
    rm -f "$iso_path"

    # Create GRUB standalone boot image for BIOS
    log "Creating GRUB boot images..."
    mkdir -p "$ISO_DIR/boot/grub/i386-pc"
    mkdir -p "$ISO_DIR/boot/grub/x86_64-efi"

    # Create BIOS boot image
    grub-mkstandalone \
        --format=i386-pc \
        --output="$ISO_DIR/boot/grub/i386-pc/eltorito.img" \
        --install-modules="linux normal iso9660 biosdisk memdisk search tar ls" \
        --modules="linux normal iso9660 biosdisk search" \
        --locales="" \
        --fonts="" \
        "boot/grub/grub.cfg=$ISO_DIR/boot/grub/grub.cfg" \
        2>/dev/null || warn "BIOS boot image creation failed (non-critical)"

    # Create EFI boot image
    grub-mkstandalone \
        --format=x86_64-efi \
        --output="$ISO_DIR/boot/grub/efi.img" \
        --install-modules="linux normal iso9660 efi_gop efi_uga search" \
        --modules="linux normal iso9660 efi_gop efi_uga search" \
        --locales="" \
        --fonts="" \
        "boot/grub/grub.cfg=$ISO_DIR/boot/grub/grub.cfg" \
        2>/dev/null || warn "EFI boot image creation failed (non-critical)"

    # Build ISO using xorriso
    log "Building final ISO with xorriso..."
    xorriso -as mkisofs \
        -r -V "SynOS 1.0.0 Ultimate" \
        -o "$iso_path" \
        -J -l \
        -b boot/grub/i386-pc/eltorito.img \
        -no-emul-boot -boot-load-size 4 -boot-info-table \
        -eltorito-alt-boot \
        -e boot/grub/efi.img \
        -no-emul-boot \
        -isohybrid-gpt-basdat \
        -isohybrid-apm-hfsplus \
        "$ISO_DIR" 2>&1 | while read -r line; do
            [[ "$line" =~ ^xorriso ]] && echo "  $line" || true
        done

    timer_end "ISO creation"

    # Check if ISO was created
    if [ -f "$iso_path" ]; then
        log "ISO created successfully: $iso_path"
        local iso_size
        iso_size=$(du -h "$iso_path" | cut -f1)
        log "ISO size: $iso_size"
    else
        error "ISO creation failed!"
        return 1
    fi

    echo "$iso_path"
}

################################################################################
# GENERATE CHECKSUMS
################################################################################

generate_checksums() {
    local iso_path=$1

    log "Generating checksums..."

    # MD5
    (cd "$(dirname "$iso_path")" && md5sum "$(basename "$iso_path")" > "$(basename "$iso_path").md5")

    # SHA256
    (cd "$(dirname "$iso_path")" && sha256sum "$(basename "$iso_path")" > "$(basename "$iso_path").sha256")

    log "Checksums generated"
}

################################################################################
# CREATE RELEASE NOTES
################################################################################

create_release_notes() {
    local iso_path=$1
    local iso_name=$(basename "$iso_path")
    local iso_size=$(du -h "$iso_path" | cut -f1)

    cat > "$OUTPUT_DIR/RELEASE_NOTES.md" <<EOF
# SynOS 1.0.0 Ultimate - Release Notes

**Release Date:** $(date +"%Y-%m-%d")

## 📦 Download

- **Filename:** $iso_name
- **Size:** $iso_size
- **MD5:** \`$(cat "$iso_path.md5" | cut -d' ' -f1)\`
- **SHA256:** \`$(cat "$iso_path.sha256" | cut -d' ' -f1)\`

## ✨ What's New

### Comprehensive Tool Suite
- ✅ **500+ security tools** pre-installed from multiple sources:
  - ParrotOS security tools repository
  - Kali Linux tool metapackages
  - Essential GitHub repositories
  - Python security packages
  - Custom SynOS tools

### Organized Tool Menu
- ✅ **11 categorized tool sections:**
  1. Information Gathering (nmap, masscan, subfinder, amass, etc.)
  2. Vulnerability Analysis (nuclei, nikto, wpscan, openvas)
  3. Web Application Analysis (burpsuite, zaproxy, sqlmap, gobuster)
  4. Database Assessment (sqlmap, specialized tools)
  5. Password Attacks (john, hashcat, hydra, medusa)
  6. Wireless Attacks (aircrack-ng, wifite, kismet)
  7. Exploitation Tools (metasploit, crackmapexec, bloodhound)
  8. Sniffing & Spoofing (wireshark, ettercap, responder)
  9. Post Exploitation (mimikatz, empire, powershell tools)
  10. Forensics (autopsy, volatility, memory analysis)
  11. Reporting Tools (dradis, faraday)

### AI-Powered Features
- ✅ AI consciousness engine for threat detection
- ✅ Automated security monitoring service
- ✅ Intelligent log analysis
- ✅ Machine learning model integration

### Custom Branding
- ✅ SynOS-themed GRUB boot menu
- ✅ Plymouth boot splash screen
- ✅ Custom desktop themes (Windows 10 Dark, ARK-Dark)
- ✅ Nuclear/space themed wallpapers
- ✅ Branded login screen

### Desktop Configuration
- ✅ MATE desktop with customized panel
- ✅ Pre-configured themes and icons
- ✅ Desktop shortcuts for quick access
- ✅ Multiple desktop environments available (KDE, XFCE, Cinnamon)

### Demo Application
- ✅ Interactive \`synos-demo\` application
- ✅ Feature showcase with 9 demo modules
- ✅ Tool verification and testing
- ✅ System performance metrics

### Pre-Installed Resources
- ✅ GitHub security repositories cloned
- ✅ SecLists wordlists
- ✅ PayloadsAllTheThings
- ✅ PEASS-ng privilege escalation tools
- ✅ Nuclei vulnerability templates

### Documentation
- ✅ Comprehensive README with quick start guide
- ✅ Tool reference documentation
- ✅ Quick reference cards
- ✅ GitHub wiki integration

## 🖥️ System Requirements

### Minimum
- 4GB RAM
- 50GB disk space
- 64-bit processor
- BIOS or UEFI boot support

### Recommended
- 8GB+ RAM
- 100GB+ disk space
- Multi-core processor
- 20GB+ for tools and wordlists

## 🚀 Quick Start

1. **Boot the ISO:**
   - Write to USB: \`dd if=$iso_name of=/dev/sdX bs=4M status=progress\`
   - Or use in VM: Allocate 4GB+ RAM

2. **Select Boot Option:**
   - Live Mode - Try without installing
   - Install - Install to hard drive
   - Safe Mode - Basic graphics drivers

3. **First Steps:**
   \`\`\`bash
   # Launch demo
   synos-demo

   # View tools
   cat /opt/synos-tools-inventory.txt

   # Access menu
   Applications → SynOS Tools
   \`\`\`

## 📚 Documentation

- **GitHub:** https://github.com/diablorain/Syn_OS
- **Wiki:** https://github.com/diablorain/Syn_OS/wiki
- **Issues:** https://github.com/diablorain/Syn_OS/issues

## ⚖️ Legal Notice

⚠️ **IMPORTANT:** These tools are for authorized security testing only.
Unauthorized access to computer systems is illegal. Always obtain proper
authorization before performing security assessments.

## 🙏 Acknowledgments

Built with tools from:
- ParrotOS Security Platform
- Kali Linux
- Offensive Security Community
- GitHub Security Community

## 📝 License

See LICENSE file in repository.

---

**Enjoy SynOS 1.0.0 Ultimate!** 🎉
EOF

    log "Release notes created: $OUTPUT_DIR/RELEASE_NOTES.md"
}

################################################################################
# MAIN EXECUTION
################################################################################

main() {
    echo "Phase 6: ISO Rebuild & Finalization"
    echo "==================================="

    check_root
    check_disk_space "$BUILD_DIR" 10

    cleanup_chroot
    update_grub_config
    create_manifest
    build_squashfs
    copy_kernel_initrd
    create_iso_metadata

    local iso_path
    iso_path=$(build_iso)

    generate_checksums "$iso_path"
    create_release_notes "$iso_path"

    print_summary "Phase 6 Complete - ISO Ready!" \
        "ISO Path: $iso_path" \
        "ISO Size: $(get_dir_size "$iso_path")" \
        "Checksums generated" \
        "Release notes created"

    log "✓ Phase 6 complete!"
    log "Enhanced ISO ready: $iso_path"
}

main "$@"
