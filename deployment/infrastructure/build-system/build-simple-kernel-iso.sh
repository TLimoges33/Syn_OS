#!/bin/bash

# Security: Load environment configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../../config/environment-secure.sh"

# Security: Validate we're in correct project
if [[ ! -f "${PROJECT_ROOT}/Cargo.toml" ]]; then
    echo "❌ SECURITY ERROR: Not in valid Syn_OS project directory"
    exit 1
fi

# Syn_OS Clean ISO Build Script
# Phase 4: Production Deployment with proper permissions

set -e  # Exit on any error

# Configuration
PROJECT_ROOT="${PROJECT_ROOT}"
BUILD_BASE="$PROJECT_ROOT/build"
ISO_WORKSPACE="$BUILD_BASE/synos-iso"
FINAL_ISO="$BUILD_BASE/SynOS-v1.0-$(date +%Y%m%d).iso"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check user permissions
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        log_error "Do not run as root! Run as regular user with sudo access."
        exit 1
    fi
    
    if ! sudo -n true 2>/dev/null; then
        log_info "Testing sudo access..."
        sudo echo "Sudo access confirmed"
    fi
}

# Clean previous builds
clean_build() {
    log_info "Cleaning previous build artifacts..."
    sudo rm -rf "$ISO_WORKSPACE" 2>/dev/null || true
    rm -f "$BUILD_BASE"/SynOS-*.iso 2>/dev/null || true
    log_success "Build environment cleaned"
}

# Create clean directory structure
setup_workspace() {
    log_info "Setting up clean workspace..."
    
    mkdir -p "$BUILD_BASE"
    mkdir -p "$ISO_WORKSPACE"/{iso,rootfs,temp}
    
    # Set proper ownership
    sudo chown -R "$USER:$USER" "$BUILD_BASE"
    
    log_success "Workspace created: $ISO_WORKSPACE"
}

# Create minimal bootable system
create_minimal_system() {
    log_info "Creating minimal bootable system..."
    
    local ROOTFS="$ISO_WORKSPACE/rootfs"
    
    # Create essential directory structure
    sudo mkdir -p "$ROOTFS"/{bin,sbin,etc,proc,sys,dev,tmp,var,usr,home,root,mnt,media,opt}
    sudo mkdir -p "$ROOTFS"/usr/{bin,sbin,lib,share}
    sudo mkdir -p "$ROOTFS"/var/{log,tmp}
    sudo mkdir -p "$ROOTFS"/etc/{systemd/system,network}
    
    # Copy essential binaries
    sudo cp -a /bin/bash "$ROOTFS/bin/" 2>/dev/null || true
    sudo cp -a /bin/sh "$ROOTFS/bin/" 2>/dev/null || true
    sudo cp -a /sbin/init "$ROOTFS/sbin/" 2>/dev/null || true
    
    # Copy essential libraries
    sudo mkdir -p "$ROOTFS/lib/x86_64-linux-gnu"
    sudo cp -a /lib/x86_64-linux-gnu/ld-*.so* "$ROOTFS/lib/x86_64-linux-gnu/" 2>/dev/null || true
    sudo cp -a /lib/x86_64-linux-gnu/libc.so* "$ROOTFS/lib/x86_64-linux-gnu/" 2>/dev/null || true
    sudo cp -a /lib/x86_64-linux-gnu/libdl.so* "$ROOTFS/lib/x86_64-linux-gnu/" 2>/dev/null || true
    
    # Set permissions
    sudo chmod 755 "$ROOTFS"
    sudo chmod 1777 "$ROOTFS/tmp" "$ROOTFS/var/tmp"
    
    log_success "Minimal system created"
}

# Install Syn_OS components
install_synos_components() {
    log_info "Installing Syn_OS consciousness components..."
    
    local ROOTFS="$ISO_WORKSPACE/rootfs"
    
    # Create Syn_OS directory
    sudo mkdir -p "$ROOTFS/opt/synos"
    
    # Copy consciousness system (with better error handling)
    if [[ -d "$PROJECT_ROOT/src" ]]; then
        sudo cp -r "$PROJECT_ROOT/src" "$ROOTFS/opt/synos/" 2>/dev/null || true
    fi
    
    if [[ -d "$PROJECT_ROOT/config" ]]; then
        sudo cp -r "$PROJECT_ROOT/config" "$ROOTFS/opt/synos/" 2>/dev/null || true
    fi
    
    # Copy eBPF programs
    if [[ -d "$PROJECT_ROOT/src/kernel/ebpf/build" ]]; then
        sudo mkdir -p "$ROOTFS/opt/synos/ebpf"
        sudo cp -r "$PROJECT_ROOT/src/kernel/ebpf/build/"* "$ROOTFS/opt/synos/ebpf/" 2>/dev/null || true
    fi
    
    # Install systemd services
    if [[ -d "$PROJECT_ROOT/scripts/systemd" ]]; then
        sudo cp "$PROJECT_ROOT/scripts/systemd/"*.service "$ROOTFS/etc/systemd/system/" 2>/dev/null || true
    fi
    
    log_success "Syn_OS components installed"
}

# Configure system
configure_system() {
    log_info "Configuring Syn_OS system..."
    
    local ROOTFS="$ISO_WORKSPACE/rootfs"
    
    # Create OS release info
    sudo tee "$ROOTFS/etc/os-release" > /dev/null <<EOF
NAME="Syn_OS"
VERSION="1.0"
ID=synos
ID_LIKE=debian
PRETTY_NAME="Syn_OS 1.0 - Consciousness Enhanced"
VERSION_ID="1.0"
HOME_URL="https://syn-os.dev"
SUPPORT_URL="https://syn-os.dev/support"
BUG_REPORT_URL="https://syn-os.dev/issues"
EOF

    # Create hostname
    echo "synos-live" | sudo tee "$ROOTFS/etc/hostname" > /dev/null
    
    # Create simple init script
    sudo tee "$ROOTFS/sbin/synos-init" > /dev/null <<'EOF'
#!/bin/bash
echo "Starting Syn_OS..."
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev
echo "Syn_OS Live System Ready"
exec /bin/bash
EOF
    
    sudo chmod +x "$ROOTFS/sbin/synos-init"
    
    log_success "System configured"
}

# Create kernel and initrd
prepare_boot_files() {
    log_info "Preparing boot files..."
    
    local ISO_DIR="$ISO_WORKSPACE/iso"
    mkdir -p "$ISO_DIR/live"
    
    # Copy our built Syn_OS kernel
    if [[ -f "$PROJECT_ROOT/target/x86_64-unknown-none/debug/kernel" ]]; then
        sudo cp "$PROJECT_ROOT/target/x86_64-unknown-none/debug/kernel" "$ISO_DIR/live/vmlinuz" || {
            log_error "Could not copy Syn_OS kernel"
            return 1
        }
        log_info "Using Syn_OS debug kernel"
    elif [[ -f "$PROJECT_ROOT/target/x86_64-unknown-none/release/kernel" ]]; then
        sudo cp "$PROJECT_ROOT/target/x86_64-unknown-none/release/kernel" "$ISO_DIR/live/vmlinuz" || {
            log_error "Could not copy Syn_OS kernel"
            return 1
        }
        log_info "Using Syn_OS release kernel"
    else
        # Fallback to system kernel
        sudo cp /boot/vmlinuz-* "$ISO_DIR/live/vmlinuz" 2>/dev/null || {
            log_error "Could not copy kernel"
            return 1
        }
        log_info "Using system kernel as fallback"
    fi
    
    # Copy system initrd
    if ls /boot/initrd.img-* >/dev/null 2>&1; then
        INITRD_FILE=$(ls /boot/initrd.img-* | head -1)
        sudo cp "$INITRD_FILE" "$ISO_DIR/live/initrd.img" || {
            log_error "Could not copy initrd"
            return 1
        }
        log_info "Using initrd: $(basename "$INITRD_FILE")"
    else
        log_error "No initrd files found"
        return 1
    fi
    
    # Fix permissions
    sudo chown "$USER:$USER" "$ISO_DIR/live/vmlinuz" "$ISO_DIR/live/initrd.img"
    
    log_success "Boot files prepared"
}

# Create compressed filesystem
create_filesystem() {
    log_info "Creating compressed filesystem..."
    
    local ROOTFS="$ISO_WORKSPACE/rootfs"
    local ISO_DIR="$ISO_WORKSPACE/iso"
    local SQUASHFS="$ISO_DIR/live/filesystem.squashfs"
    
    # Create squashfs
    sudo mksquashfs "$ROOTFS" "$SQUASHFS" \
        -comp xz \
        -b 1048576 \
        -noappend \
        -progress
    
    log_success "Filesystem created: $(du -h "$SQUASHFS" | cut -f1)"
}

# Setup bootloader
setup_bootloader() {
    log_info "Setting up bootloader..."
    
    local ISO_DIR="$ISO_WORKSPACE/iso"
    
    # Create isolinux directory
    mkdir -p "$ISO_DIR/isolinux"
    
    # Copy bootloader files
    cp /usr/lib/ISOLINUX/isolinux.bin "$ISO_DIR/isolinux/"
    cp /usr/lib/syslinux/modules/bios/*.c32 "$ISO_DIR/isolinux/"
    
    # Create boot configuration
    tee "$ISO_DIR/isolinux/isolinux.cfg" > /dev/null <<EOF
DEFAULT live
TIMEOUT 30
PROMPT 1

LABEL live
    KERNEL /live/vmlinuz
    APPEND initrd=/live/initrd.img boot=live config quiet

LABEL shell
    KERNEL /live/vmlinuz
    APPEND initrd=/live/initrd.img init=/sbin/synos-init
EOF

    log_success "Bootloader configured"
}

# Build final ISO
build_iso() {
    log_info "Building final ISO..."
    
    local ISO_DIR="$ISO_WORKSPACE/iso"
    
    # Build ISO with genisoimage
    genisoimage \
        -o "$FINAL_ISO" \
        -b isolinux/isolinux.bin \
        -c isolinux/boot.cat \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        -J -R -V "SYNOS_LIVE" \
        "$ISO_DIR"
    
    # Make ISO hybrid (bootable from USB)
    isohybrid "$FINAL_ISO" 2>/dev/null || true
    
    log_success "ISO created: $FINAL_ISO"
    log_info "ISO size: $(du -h "$FINAL_ISO" | cut -f1)"
}

# Generate checksums
generate_checksums() {
    log_info "Generating checksums..."
    
    cd "$(dirname "$FINAL_ISO")"
    md5sum "$(basename "$FINAL_ISO")" > "$(basename "$FINAL_ISO").md5"
    sha256sum "$(basename "$FINAL_ISO")" > "$(basename "$FINAL_ISO").sha256"
    
    log_success "Checksums generated"
}

# Main execution
main() {
    log_info "=== Syn_OS Clean ISO Build ==="
    log_info "Building production ISO with proper permissions"
    echo
    
    check_permissions
    clean_build
    setup_workspace
    create_minimal_system
    install_synos_components
    configure_system
    prepare_boot_files
    create_filesystem
    setup_bootloader
    build_iso
    generate_checksums
    
    echo
    log_success "=== Build Complete ==="
    log_info "ISO: $FINAL_ISO"
    log_info "Size: $(du -h "$FINAL_ISO" | cut -f1)"
    log_info "Ready for testing!"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
