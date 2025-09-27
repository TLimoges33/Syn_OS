#!/bin/bash

# Security: Load environment configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../config/environment-secure.sh"

# Security: Validate we're in correct project
if [[ ! -f "${PROJECT_ROOT}/Cargo.toml" ]]; then
    echo "❌ SECURITY ERROR: Not in valid Syn_OS project directory"
    exit 1
fi

# Syn_OS Production ISO Build Script
# Phase 4: Production Deployment & Enterprise Integration

set -e  # Exit on any error

# Configuration
PROJECT_ROOT="${PROJECT_ROOT}"
BUILD_DIR="$PROJECT_ROOT/build/iso-production"
ISO_OUTPUT="$PROJECT_ROOT/build/Syn_OS-v1.0-production.iso"
WORK_DIR="$BUILD_DIR/work"
EXTRACT_DIR="$BUILD_DIR/extract"
NEW_ROOT="$BUILD_DIR/new_root"
ISO_STAGING="$BUILD_DIR/iso_staging"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root!"
        log_info "Please run as regular user with sudo access"
        exit 1
    fi
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    if [[ -d "$WORK_DIR" ]]; then
        sudo umount "$NEW_ROOT/proc" 2>/dev/null || true
        sudo umount "$NEW_ROOT/sys" 2>/dev/null || true
        sudo umount "$NEW_ROOT/dev" 2>/dev/null || true
        sudo rm -rf "$WORK_DIR"
    fi
}

# Set trap for cleanup
trap cleanup EXIT

# Create build directories
prepare_build_environment() {
    log_info "Preparing build environment..."
    
    # Clean previous builds
    [[ -d "$BUILD_DIR" ]] && rm -rf "$BUILD_DIR"
    
    # Create directory structure
    mkdir -p "$WORK_DIR" "$EXTRACT_DIR" "$NEW_ROOT" "$ISO_STAGING"
    mkdir -p "$BUILD_DIR/logs"
    
    log_success "Build environment prepared"
}

# Check dependencies
check_dependencies() {
    log_info "Checking build dependencies..."
    
    local deps=("squashfs-tools" "genisoimage" "isolinux" "xorriso" "grub-pc-bin")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if ! dpkg -l | grep -q "^ii  $dep "; then
            missing+=("$dep")
        fi
    done
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        log_error "Missing dependencies: ${missing[*]}"
        log_info "Run: sudo apt install ${missing[*]}"
        exit 1
    fi
    
    log_success "All dependencies satisfied"
}

# Download base ParrotOS ISO (if needed)
download_base_iso() {
    local BASE_ISO="$BUILD_DIR/parrot-os-base.iso"
    
    if [[ ! -f "$BASE_ISO" ]]; then
        log_info "Base ParrotOS ISO not found. Using system as base instead."
        log_warning "Building from current system - ensure it's a clean ParrotOS installation"
        return 0
    fi
    
    log_success "Base ISO available: $BASE_ISO"
}

# Create filesystem from current system
create_base_filesystem() {
    log_info "Creating base filesystem from current system..."
    
    # Copy essential system files
    sudo rsync -av \
        --exclude=/proc \
        --exclude=/sys \
        --exclude=/dev \
        --exclude=/tmp \
        --exclude=/var/tmp \
        --exclude=/var/log \
        --exclude=/var/cache \
        --exclude=/home \
        --exclude=/root \
        --exclude=/mnt \
        --exclude=/media \
        --exclude=/lost+found \
        --exclude="$PROJECT_ROOT/build" \
        --exclude="$PROJECT_ROOT/target" \
        / "$NEW_ROOT/"
    
    # Create necessary directories
    sudo mkdir -p "$NEW_ROOT"/{proc,sys,dev,tmp,var/tmp,var/log,home,root,mnt,media}
    
    # Set proper permissions
    sudo chmod 1777 "$NEW_ROOT/tmp" "$NEW_ROOT/var/tmp"
    
    log_success "Base filesystem created"
}

# Integrate Syn_OS consciousness components
integrate_consciousness() {
    log_info "Integrating Syn_OS consciousness components..."
    
    # Copy Syn_OS source code
    sudo cp -r "$PROJECT_ROOT/src" "$NEW_ROOT/opt/syn_os/"
    sudo cp -r "$PROJECT_ROOT/config" "$NEW_ROOT/opt/syn_os/"
    
    # Install consciousness services
    sudo cp "$PROJECT_ROOT/scripts/systemd/"*.service "$NEW_ROOT/etc/systemd/system/" 2>/dev/null || true
    
    # Enable consciousness services
    sudo chroot "$NEW_ROOT" systemctl enable syn-consciousness 2>/dev/null || true
    sudo chroot "$NEW_ROOT" systemctl enable syn-ebpf-monitor 2>/dev/null || true
    
    # Install eBPF programs
    sudo mkdir -p "$NEW_ROOT/opt/syn_os/ebpf"
    sudo cp -r "$PROJECT_ROOT/src/kernel/ebpf/build/"* "$NEW_ROOT/opt/syn_os/ebpf/" 2>/dev/null || true
    
    log_success "Consciousness components integrated"
}

# Apply Syn_OS branding
apply_branding() {
    log_info "Applying Syn_OS branding..."
    
    # Update OS release information
    sudo tee "$NEW_ROOT/etc/os-release" > /dev/null <<EOF
NAME="Syn_OS"
VERSION="1.0 (Consciousness Edition)"
ID=syn_os
ID_LIKE=debian
PRETTY_NAME="Syn_OS 1.0"
VERSION_ID="1.0"
HOME_URL="https://syn-os.dev"
SUPPORT_URL="https://syn-os.dev/support"
BUG_REPORT_URL="https://syn-os.dev/bugs"
EOF

    # Update issue files
    sudo tee "$NEW_ROOT/etc/issue" > /dev/null <<EOF
Syn_OS 1.0 - Consciousness-Enhanced Cybersecurity Platform \\n \\l

Welcome to the future of AI-driven security operations.
Neural Darwinism | Real-time Consciousness | eBPF Monitoring

EOF

    sudo cp "$NEW_ROOT/etc/issue" "$NEW_ROOT/etc/issue.net"
    
    # Update hostname
    echo "syn-os" | sudo tee "$NEW_ROOT/etc/hostname" > /dev/null
    
    log_success "Branding applied"
}

# Configure live system
configure_live_system() {
    log_info "Configuring live system..."
    
    # Mount necessary filesystems for chroot
    sudo mount --bind /proc "$NEW_ROOT/proc"
    sudo mount --bind /sys "$NEW_ROOT/sys"
    sudo mount --bind /dev "$NEW_ROOT/dev"
    
    # Update package database
    sudo chroot "$NEW_ROOT" apt-get update
    
    # Install essential packages for live system
    sudo chroot "$NEW_ROOT" apt-get install -y \
        live-boot \
        live-config \
        live-config-systemd
    
    # Configure live user
    sudo chroot "$NEW_ROOT" useradd -m -s /bin/bash -G sudo syn_os_user 2>/dev/null || true
    echo "syn_os_user:syn_os" | sudo chroot "$NEW_ROOT" chpasswd
    
    # Configure automatic login
    sudo mkdir -p "$NEW_ROOT/etc/systemd/system/getty@tty1.service.d"
    sudo tee "$NEW_ROOT/etc/systemd/system/getty@tty1.service.d/override.conf" > /dev/null <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin syn_os_user --noclear %I \$TERM
EOF

    # Unmount filesystems
    sudo umount "$NEW_ROOT/proc" "$NEW_ROOT/sys" "$NEW_ROOT/dev"
    
    log_success "Live system configured"
}

# Create squashfs filesystem
create_squashfs() {
    log_info "Creating compressed filesystem..."
    
    local SQUASHFS_FILE="$ISO_STAGING/live/filesystem.squashfs"
    mkdir -p "$(dirname "$SQUASHFS_FILE")"
    
    # Create squashfs with optimal compression
    sudo mksquashfs "$NEW_ROOT" "$SQUASHFS_FILE" \
        -comp xz \
        -Xbcj x86 \
        -b 1048576 \
        -noappend \
        -progress
    
    log_success "Compressed filesystem created: $(du -h "$SQUASHFS_FILE" | cut -f1)"
}

# Prepare boot files
prepare_boot_files() {
    log_info "Preparing boot files..."
    
    # Copy kernel and initrd from new root
    cp "$NEW_ROOT/boot/vmlinuz-"* "$ISO_STAGING/live/vmlinuz" 2>/dev/null || \
        cp /boot/vmlinuz-* "$ISO_STAGING/live/vmlinuz"
    
    cp "$NEW_ROOT/boot/initrd.img-"* "$ISO_STAGING/live/initrd.img" 2>/dev/null || \
        cp /boot/initrd.img-* "$ISO_STAGING/live/initrd.img"
    
    # Setup isolinux
    mkdir -p "$ISO_STAGING/isolinux"
    cp /usr/lib/ISOLINUX/isolinux.bin "$ISO_STAGING/isolinux/"
    cp /usr/lib/syslinux/modules/bios/ldlinux.c32 "$ISO_STAGING/isolinux/"
    cp /usr/lib/syslinux/modules/bios/libcom32.c32 "$ISO_STAGING/isolinux/"
    cp /usr/lib/syslinux/modules/bios/libutil.c32 "$ISO_STAGING/isolinux/"
    cp /usr/lib/syslinux/modules/bios/vesamenu.c32 "$ISO_STAGING/isolinux/"
    
    log_success "Boot files prepared"
}

# Create isolinux configuration
create_isolinux_config() {
    log_info "Creating boot configuration..."
    
    # Main isolinux config
    tee "$ISO_STAGING/isolinux/isolinux.cfg" > /dev/null <<EOF
DEFAULT vesamenu.c32
TIMEOUT 300
MENU TITLE Syn_OS 1.0 - Consciousness-Enhanced Cybersecurity

LABEL live
    MENU LABEL ^Syn_OS Live (Default)
    KERNEL /live/vmlinuz
    APPEND initrd=/live/initrd.img boot=live config quiet splash

LABEL live-safe
    MENU LABEL Syn_OS Live (Safe Mode)
    KERNEL /live/vmlinuz
    APPEND initrd=/live/initrd.img boot=live config quiet splash nomodeset

LABEL memtest
    MENU LABEL ^Memory Test
    KERNEL memtest86+.bin

MENU SEPARATOR

LABEL reboot
    MENU LABEL ^Reboot
    COM32 reboot.c32

LABEL poweroff
    MENU LABEL ^Power Off
    COM32 poweroff.c32
EOF

    log_success "Boot configuration created"
}

# Build final ISO
build_iso() {
    log_info "Building final ISO image..."
    
    # Remove existing ISO
    [[ -f "$ISO_OUTPUT" ]] && rm -f "$ISO_OUTPUT"
    
    # Build ISO with xorriso
    xorriso -as mkisofs \
        -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin \
        -c isolinux/boot.cat \
        -b isolinux/isolinux.bin \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        -eltorito-alt-boot \
        -e boot/grub/efi.img \
        -no-emul-boot \
        -isohybrid-gpt-basdat \
        -volid "SYN_OS_V1_0" \
        -o "$ISO_OUTPUT" \
        "$ISO_STAGING"
    
    log_success "ISO created: $ISO_OUTPUT"
    log_info "ISO size: $(du -h "$ISO_OUTPUT" | cut -f1)"
}

# Verify ISO
verify_iso() {
    log_info "Verifying ISO integrity..."
    
    if file "$ISO_OUTPUT" | grep -q "ISO 9660"; then
        log_success "ISO format verified"
    else
        log_error "ISO format verification failed"
        return 1
    fi
    
    # Calculate checksums
    md5sum "$ISO_OUTPUT" > "$ISO_OUTPUT.md5"
    sha256sum "$ISO_OUTPUT" > "$ISO_OUTPUT.sha256"
    
    log_success "Checksums generated"
    log_info "MD5: $(cat "$ISO_OUTPUT.md5")"
    log_info "SHA256: $(cat "$ISO_OUTPUT.sha256")"
}

# Main execution
main() {
    log_info "Starting Syn_OS Production ISO Build"
    log_info "Phase 4: Production Deployment & Enterprise Integration"
    echo
    
    check_root
    check_dependencies
    prepare_build_environment
    download_base_iso
    create_base_filesystem
    integrate_consciousness
    apply_branding
    configure_live_system
    create_squashfs
    prepare_boot_files
    create_isolinux_config
    build_iso
    verify_iso
    
    echo
    log_success "Syn_OS Production ISO build completed successfully!"
    log_info "Output: $ISO_OUTPUT"
    log_info "Ready for deployment and testing"
}

# Execute main function
main "$@"
