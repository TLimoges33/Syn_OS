#!/usr/bin/env bash
################################################################################
# SynOS Full Linux Distribution Builder
# 
# Creates a complete bootable Linux distribution ISO with:
#   - SynOS kernel
#   - Debian/Ubuntu base system
#   - All workspace binaries
#   - Documentation and source code
#   - Custom desktop environment
#   - Pre-configured services
#
# Usage:
#   ./scripts/build-full-linux.sh [OPTIONS]
#
# Options:
#   --base-distro NAME   Base distribution (debian|ubuntu) [default: debian]
#   --variant TYPE       Variant (minimal|standard|full) [default: standard]
#   --output DIR         Output directory [default: build/]
#   --skip-packages      Skip package installation (use existing base)
#   --no-customize       Skip customization phase
#   --help               Show this help message
#
# Environment Variables:
#   DEBIAN_MIRROR        Debian mirror URL
#   UBUNTU_MIRROR        Ubuntu mirror URL
#   SYNOS_HOSTNAME       System hostname [default: synos]
#
# Requirements:
#   - debootstrap
#   - squashfs-tools
#   - genisoimage or xorriso
#   - At least 10GB free disk space
#
# Exit Codes:
#   0 - Success
#   1 - Build failure
#   2 - Dependency missing
#   3 - Insufficient disk space
#
################################################################################

set -euo pipefail

# Source shared library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/build-common.sh"

################################################################################
# Configuration
################################################################################

BASE_DISTRO="debian"
VARIANT="standard"
OUTPUT_BASE=""
SKIP_PACKAGES=false
SKIP_CUSTOMIZE=false
SYNOS_HOSTNAME="${SYNOS_HOSTNAME:-synos}"

while [[ $# -gt 0 ]]; do
    case $1 in
        --base-distro)
            BASE_DISTRO="$2"
            shift 2
            ;;
        --variant)
            VARIANT="$2"
            shift 2
            ;;
        --output)
            OUTPUT_BASE="$2"
            shift 2
            ;;
        --skip-packages)
            SKIP_PACKAGES=true
            shift
            ;;
        --no-customize)
            SKIP_CUSTOMIZE=true
            shift
            ;;
        --help)
            grep "^#" "$0" | grep -v "^#!/" | sed 's/^# \?//'
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [[ -n "$OUTPUT_BASE" ]]; then
    BUILD_DIR="$OUTPUT_BASE"
else
    BUILD_DIR="${PROJECT_ROOT}/build"
fi

# Distribution-specific settings
case "$BASE_DISTRO" in
    debian)
        DISTRO_CODENAME="bookworm"
        MIRROR="${DEBIAN_MIRROR:-http://deb.debian.org/debian}"
        ;;
    ubuntu)
        DISTRO_CODENAME="jammy"
        MIRROR="${UBUNTU_MIRROR:-http://archive.ubuntu.com/ubuntu}"
        ;;
    *)
        error "Unsupported base distribution: $BASE_DISTRO"
        exit 1
        ;;
esac

# Variant-specific package lists
case "$VARIANT" in
    minimal)
        EXTRA_PACKAGES="systemd,udev,sudo"
        ;;
    standard)
        EXTRA_PACKAGES="systemd,udev,sudo,network-manager,vim,curl,wget"
        ;;
    full)
        EXTRA_PACKAGES="systemd,udev,sudo,network-manager,vim,curl,wget,git,build-essential,python3,nodejs"
        ;;
    *)
        error "Unsupported variant: $VARIANT"
        exit 1
        ;;
esac

################################################################################
# Helper Functions
################################################################################

check_distro_tools() {
    section "Checking Distribution Tools"
    check_required_tools debootstrap squashfs-tools genisoimage
    
    if ! command -v debootstrap &>/dev/null; then
        error "debootstrap not found"
        info "Install with: sudo apt install debootstrap"
        exit 2
    fi
    
    success "All distribution tools available"
}

build_base_system() {
    local chroot_dir="$1"
    
    section "Building Base System"
    info "Distribution: ${BASE_DISTRO} ${DISTRO_CODENAME}"
    info "Mirror: ${MIRROR}"
    info "Variant: ${VARIANT}"
    info "Chroot: ${chroot_dir}"
    
    if [[ -d "$chroot_dir" ]] && [[ "$SKIP_PACKAGES" == true ]]; then
        info "Using existing base system (--skip-packages)"
        return 0
    fi
    
    # Clean previous attempt
    if [[ -d "$chroot_dir" ]]; then
        warning "Removing existing chroot..."
        sudo rm -rf "$chroot_dir"
    fi
    
    mkdir -p "$chroot_dir"
    
    info "Running debootstrap (this may take 10-20 minutes)..."
    sudo debootstrap \
        --variant=minbase \
        --include="${EXTRA_PACKAGES}" \
        "${DISTRO_CODENAME}" \
        "$chroot_dir" \
        "${MIRROR}" \
        2>&1 | tee "${LOG_DIR}/debootstrap.log" | grep -E "(I:|E:)" || true
    
    success "Base system created"
}

customize_system() {
    local chroot_dir="$1"
    
    if [[ "$SKIP_CUSTOMIZE" == true ]]; then
        info "Skipping customization (--no-customize)"
        return 0
    fi
    
    section "Customizing System"
    
    # Set hostname
    info "Setting hostname: ${SYNOS_HOSTNAME}"
    echo "${SYNOS_HOSTNAME}" | sudo tee "${chroot_dir}/etc/hostname" >/dev/null
    
    # Configure network
    info "Configuring network..."
    sudo tee "${chroot_dir}/etc/network/interfaces" >/dev/null <<EOF
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet dhcp
EOF
    
    # Set up fstab
    info "Creating fstab..."
    sudo tee "${chroot_dir}/etc/fstab" >/dev/null <<EOF
# SynOS fstab
proc /proc proc defaults 0 0
sysfs /sys sysfs defaults 0 0
tmpfs /tmp tmpfs defaults 0 0
EOF
    
    # Install SynOS kernel
    info "Installing SynOS kernel..."
    sudo mkdir -p "${chroot_dir}/boot"
    sudo cp "${KERNEL_BINARY}" "${chroot_dir}/boot/synos-kernel"
    
    # Install SynOS binaries
    if [[ -d "${ISOROOT_DIR}/boot/binaries" ]]; then
        info "Installing SynOS binaries..."
        sudo mkdir -p "${chroot_dir}/opt/synos/bin"
        sudo cp -r "${ISOROOT_DIR}/boot/binaries/"* "${chroot_dir}/opt/synos/bin/" || true
    fi
    
    # Install documentation
    if [[ -d "${ISOROOT_DIR}/docs" ]]; then
        info "Installing documentation..."
        sudo mkdir -p "${chroot_dir}/usr/share/doc/synos"
        sudo cp -r "${ISOROOT_DIR}/docs/"* "${chroot_dir}/usr/share/doc/synos/" || true
    fi
    
    # Create synos user
    info "Creating synos user..."
    sudo chroot "$chroot_dir" /bin/bash -c "
        useradd -m -s /bin/bash -G sudo synos || true
        echo 'synos:synos' | chpasswd
        echo 'root:root' | chpasswd
    " 2>/dev/null || warning "User creation may have issues"
    
    success "System customized"
}

install_grub_for_linux() {
    local chroot_dir="$1"
    local iso_dir="$2"
    
    section "Installing GRUB"
    
    # Install GRUB in chroot
    info "Installing GRUB packages..."
    sudo chroot "$chroot_dir" /bin/bash -c "
        apt-get update -qq
        apt-get install -y grub-pc grub-efi-amd64 linux-image-generic
    " 2>&1 | grep -v "^[WE]:" || true
    
    # Create GRUB config for live ISO
    info "Creating GRUB configuration..."
    mkdir -p "${iso_dir}/boot/grub"
    
    cat > "${iso_dir}/boot/grub/grub.cfg" <<EOF
set timeout=10
set default=0

menuentry "SynOS Live" {
    linux /boot/synos-kernel boot=live
    initrd /boot/initrd.img
}

menuentry "SynOS Live (Safe Mode)" {
    linux /boot/synos-kernel boot=live nomodeset
    initrd /boot/initrd.img
}

menuentry "SynOS Live (Debug)" {
    linux /boot/synos-kernel boot=live debug
    initrd /boot/initrd.img
}
EOF
    
    success "GRUB configured"
}

create_squashfs() {
    local chroot_dir="$1"
    local output_squashfs="$2"
    
    section "Creating SquashFS"
    info "Compressing filesystem (this may take 5-10 minutes)..."
    
    sudo mksquashfs \
        "$chroot_dir" \
        "$output_squashfs" \
        -comp xz \
        -b 1M \
        -noappend \
        2>&1 | grep -E "(Creating|Writing)" || true
    
    info "SquashFS size: $(human_size "$output_squashfs")"
    success "Filesystem compressed"
}

################################################################################
# Main Build Process
################################################################################

main() {
    local start_time
    start_time=$(date +%s)
    
    print_banner "SynOS Full Linux Distribution Builder"
    
    # Initialize
    section "Initializing Build Environment"
    init_build_env
    
    # Pre-flight checks
    section "Pre-flight Checks"
    check_not_root
    check_distro_tools
    check_disk_space 10000000  # 10GB minimum
    
    # Display configuration
    info "Build Configuration:"
    info "  Base Distribution: ${BASE_DISTRO} ${DISTRO_CODENAME}"
    info "  Variant:           ${VARIANT}"
    info "  Hostname:          ${SYNOS_HOSTNAME}"
    info "  Mirror:            ${MIRROR}"
    info "  Output:            ${BUILD_DIR}"
    
    setup_cleanup
    
    # Phase 1: Build SynOS components
    section "Phase 1: Building SynOS Kernel"
    build_kernel "${KERNEL_TARGET}"
    KERNEL_BINARY=$(find_kernel_binary)
    success "Kernel built"
    
    section "Phase 2: Building Workspace"
    build_workspace
    
    section "Phase 3: Collecting Binaries"
    collect_binaries
    
    # Phase 2: Build base system
    local chroot_dir="${BUILD_DIR}/chroot-${BASE_DISTRO}"
    build_base_system "$chroot_dir"
    
    # Phase 3: Customize system
    customize_system "$chroot_dir"
    
    # Phase 4: Create ISO structure
    section "Phase 4: Creating ISO Structure"
    local linux_iso_dir="${BUILD_DIR}/iso-linux"
    mkdir -p "${linux_iso_dir}"/{boot,live}
    
    # Copy kernel
    sudo cp "${chroot_dir}/boot/synos-kernel" "${linux_iso_dir}/boot/"
    
    # Install GRUB
    install_grub_for_linux "$chroot_dir" "$linux_iso_dir"
    
    # Create SquashFS
    create_squashfs "$chroot_dir" "${linux_iso_dir}/live/filesystem.squashfs"
    
    # Phase 5: Generate ISO
    section "Phase 5: Generating ISO Image"
    local timestamp
    timestamp=$(date +%Y%m%d-%H%M%S)
    OUTPUT_ISO="${BUILD_DIR}/SynOS-${SYNOS_VERSION}-${BASE_DISTRO^}-${VARIANT^}-${timestamp}.iso"
    
    info "Creating hybrid ISO..."
    genisoimage \
        -rational-rock \
        -volid "SynOS_${SYNOS_VERSION}" \
        -cache-inodes \
        -joliet \
        -full-iso9660-filenames \
        -b boot/grub/i386-pc/eltorito.img \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        -output "$OUTPUT_ISO" \
        -graft-points \
        "${linux_iso_dir}" \
        2>&1 | grep -E "(done|Writing)" || true
    
    success "ISO generated"
    
    # Generate checksums
    section "Phase 6: Generating Checksums"
    generate_checksums "$OUTPUT_ISO"
    
    # Final summary
    local end_time elapsed
    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    
    section "Build Complete!"
    success "ISO: ${OUTPUT_ISO}"
    info "Size: $(human_size "$OUTPUT_ISO")"
    info "Time: $(elapsed_time $elapsed)"
    info "Base: ${BASE_DISTRO} ${DISTRO_CODENAME}"
    info "Variant: ${VARIANT}"
    
    echo ""
    info "Next steps:"
    info "  1. Test: qemu-system-x86_64 -cdrom ${OUTPUT_ISO} -m 4G -enable-kvm"
    info "  2. Login: user=synos, pass=synos (or root/root)"
    info "  3. Burn: dd if=${OUTPUT_ISO} of=/dev/sdX bs=4M status=progress"
    
    return 0
}

################################################################################
# Execute
################################################################################

main "$@"
