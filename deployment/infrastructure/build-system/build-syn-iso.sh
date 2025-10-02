#!/bin/bash

# Security: Load environment configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../config/environment-secure.sh"

# Security: Validate we're in correct project
if [[ ! -f "${PROJECT_ROOT}/Cargo.toml" ]]; then
    echo "❌ SECURITY ERROR: Not in valid Syn_OS project directory"
    exit 1
fi

# Syn_OS Production ISO Build Script - V2
# Uses actual Syn_OS kernel and properly organized structure

set -e

# Configuration
PROJECT_ROOT="${PROJECT_ROOT}"
BUILD_BASE="${PROJECT_ROOT}/build/iso"
ISO_OUTPUT="$BUILD_BASE/Syn_OS-v1.0.iso"

# Build directories with clear naming
SYN_FILESYSTEM="$BUILD_BASE/syn_filesystem"    # Our modified Linux filesystem
ISO_STRUCTURE="$BUILD_BASE/iso_structure"     # Final ISO layout
KERNEL_BUILD="$BUILD_BASE/kernel_build"       # Kernel compilation area

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

cleanup() {
    log_info "Cleaning up mount points..."
    sudo umount "$SYN_FILESYSTEM/proc" 2>/dev/null || true
    sudo umount "$SYN_FILESYSTEM/sys" 2>/dev/null || true
    sudo umount "$SYN_FILESYSTEM/dev" 2>/dev/null || true
    sudo umount "$SYN_FILESYSTEM/dev/pts" 2>/dev/null || true
}
trap cleanup EXIT

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    log_error "Do not run as root! Use sudo when needed."
    exit 1
fi

prepare_build_environment() {
    log_info "Preparing clean build environment..."
    
    # Clean previous builds
    [[ -d "$BUILD_BASE" ]] && sudo rm -rf "$BUILD_BASE"
    
    # Create clean directory structure
    mkdir -p "$BUILD_BASE"/{logs,cache}
    mkdir -p "$SYN_FILESYSTEM"
    mkdir -p "$ISO_STRUCTURE"/{boot,live,isolinux}
    mkdir -p "$KERNEL_BUILD"
    
    log_success "Build environment prepared"
}

build_syn_kernel() {
    log_info "Building Syn_OS consciousness-enhanced kernel..."
    
    cd "$PROJECT_ROOT"
    
    # Build the Rust kernel
    log_info "Compiling Rust kernel components..."
    if cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none --release; then
        log_success "Rust kernel compiled successfully"
        
        # Check if kernel binary was created
        local kernel_binary="$PROJECT_ROOT/target/x86_64-unknown-none/release/kernel"
        
        if [[ -f "$kernel_binary" ]]; then
            # Copy kernel to build area
            cp "$kernel_binary" "$KERNEL_BUILD/syn_kernel.bin"
            
            # Copy GRUB configuration
            cp "$PROJECT_ROOT/src/kernel/grub.cfg" "$KERNEL_BUILD/"
            
            log_success "Syn_OS kernel ready: $KERNEL_BUILD/syn_kernel.bin"
            return 0
        else
            log_warning "Kernel binary not found at expected location"
            return 1
        fi
    else
        log_warning "Kernel compilation failed"
        return 1
    fi
}

create_base_filesystem() {
    log_info "Creating Syn_OS base filesystem..."
    
    # Copy current system but exclude problematic directories
    sudo rsync -av \
        --exclude=/proc \
        --exclude=/sys \
        --exclude=/dev \
        --exclude=/tmp \
        --exclude=/var/tmp \
        --exclude=/var/log \
        --exclude=/var/cache \
        --exclude=/home/*/.*cache \
        --exclude=/home/*/.local/share/Trash \
        --exclude=/root \
        --exclude=/mnt \
        --exclude=/media \
        --exclude=/lost+found \
        --exclude="$PROJECT_ROOT/build" \
        --exclude="$PROJECT_ROOT/target" \
        / "$SYN_FILESYSTEM/" 2>/dev/null || true
    
    # Create necessary empty directories
    sudo mkdir -p "$SYN_FILESYSTEM"/{proc,sys,dev,tmp,var/tmp,var/log,root,mnt,media}
    sudo mkdir -p "$SYN_FILESYSTEM/dev/pts"
    
    # Set proper permissions
    sudo chmod 1777 "$SYN_FILESYSTEM/tmp" "$SYN_FILESYSTEM/var/tmp"
    sudo chmod 755 "$SYN_FILESYSTEM/root"
    
    log_success "Base filesystem created"
}

integrate_syn_components() {
    log_info "Integrating Syn_OS consciousness components..."
    
    # Create Syn_OS directory structure
    sudo mkdir -p "$SYN_FILESYSTEM/opt/syn_os"
    sudo mkdir -p "$SYN_FILESYSTEM/etc/syn_os"
    
    # Copy Syn_OS source code
    sudo cp -r "$PROJECT_ROOT/src" "$SYN_FILESYSTEM/opt/syn_os/"
    sudo cp -r "$PROJECT_ROOT/config" "$SYN_FILESYSTEM/opt/syn_os/"
    
    # Copy eBPF programs
    if [[ -d "$PROJECT_ROOT/src/kernel/ebpf/build" ]]; then
        sudo mkdir -p "$SYN_FILESYSTEM/opt/syn_os/ebpf"
        sudo cp -r "$PROJECT_ROOT/src/kernel/ebpf/build"/* "$SYN_FILESYSTEM/opt/syn_os/ebpf/"
        log_info "eBPF programs integrated"
    fi
    
    # Install systemd services
    if [[ -d "$PROJECT_ROOT/scripts/systemd" ]]; then
        sudo cp "$PROJECT_ROOT/scripts/systemd"/*.service "$SYN_FILESYSTEM/etc/systemd/system/"
        log_info "Systemd services installed"
    fi
    
    log_success "Syn_OS components integrated"
}

configure_syn_branding() {
    log_info "Applying Syn_OS branding and configuration..."
    
    # Update OS release information
    sudo tee "$SYN_FILESYSTEM/etc/os-release" > /dev/null <<EOF
NAME="Syn_OS"
VERSION="1.0 (Consciousness Edition)"
ID=syn_os
ID_LIKE=debian
PRETTY_NAME="Syn_OS 1.0 - Consciousness-Enhanced Cybersecurity"
VERSION_ID="1.0"
HOME_URL="https://syn-os.dev"
SUPPORT_URL="https://syn-os.dev/support"
BUG_REPORT_URL="https://syn-os.dev/bugs"
PRIVACY_POLICY_URL="https://syn-os.dev/privacy"
VERSION_CODENAME=consciousness
EOF

    # Update login messages
    sudo tee "$SYN_FILESYSTEM/etc/issue" > /dev/null <<EOF

    ███████╗██╗   ██╗███╗   ██╗     ██████╗ ███████╗
    ██╔════╝╚██╗ ██╔╝████╗  ██║    ██╔═══██╗██╔════╝
    ███████╗ ╚████╔╝ ██╔██╗ ██║    ██║   ██║███████╗
    ╚════██║  ╚██╔╝  ██║╚██╗██║    ██║   ██║╚════██║
    ███████║   ██║   ██║ ╚████║    ╚██████╔╝███████║
    ╚══════╝   ╚═╝   ╚═╝  ╚═══╝     ╚═════╝ ╚══════╝

    Consciousness-Enhanced Cybersecurity Platform v1.0
    
    🧠 Neural Darwinism Engine Active
    ⚡ Real-time eBPF Monitoring  
    🔒 Advanced Threat Detection
    🎓 Educational Framework Ready
    
    Login: \\l
    
EOF

    sudo cp "$SYN_FILESYSTEM/etc/issue" "$SYN_FILESYSTEM/etc/issue.net"
    
    # Set hostname
    echo "syn-os" | sudo tee "$SYN_FILESYSTEM/etc/hostname" > /dev/null
    
    # Configure hosts file
    sudo tee "$SYN_FILESYSTEM/etc/hosts" > /dev/null <<EOF
127.0.0.1	localhost
127.0.1.1	syn-os
::1		localhost ip6-localhost ip6-loopback
ff02::1		ip6-allnodes
ff02::2		ip6-allrouters
EOF

    log_success "Syn_OS branding applied"
}

setup_live_system() {
    log_info "Configuring live system environment..."
    
    # Mount necessary filesystems for chroot operations
    sudo mount --bind /proc "$SYN_FILESYSTEM/proc"
    sudo mount --bind /sys "$SYN_FILESYSTEM/sys"
    sudo mount --bind /dev "$SYN_FILESYSTEM/dev"
    sudo mount --bind /dev/pts "$SYN_FILESYSTEM/dev/pts"
    
    # Update package lists and install live system packages
    sudo chroot "$SYN_FILESYSTEM" apt-get update
    sudo chroot "$SYN_FILESYSTEM" apt-get install -y live-boot live-config live-config-systemd
    
    # Create live user
    sudo chroot "$SYN_FILESYSTEM" useradd -m -s /bin/bash -G sudo,adm syn_user 2>/dev/null || true
    echo "syn_user:syn_os" | sudo chroot "$SYN_FILESYSTEM" chpasswd
    
    # Configure automatic login
    sudo mkdir -p "$SYN_FILESYSTEM/etc/systemd/system/getty@tty1.service.d"
    sudo tee "$SYN_FILESYSTEM/etc/systemd/system/getty@tty1.service.d/override.conf" > /dev/null <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin syn_user --noclear %I \$TERM
EOF

    # Enable Syn_OS services
    sudo chroot "$SYN_FILESYSTEM" systemctl enable syn-consciousness 2>/dev/null || true
    sudo chroot "$SYN_FILESYSTEM" systemctl enable syn-ebpf-monitor 2>/dev/null || true
    sudo chroot "$SYN_FILESYSTEM" systemctl enable syn-enterprise-dashboard 2>/dev/null || true
    
    # Install required Python packages for consciousness system
    sudo chroot "$SYN_FILESYSTEM" pip3 install fastapi uvicorn psutil websockets 2>/dev/null || true
    
    # Cleanup
    sudo chroot "$SYN_FILESYSTEM" apt-get clean
    sudo rm -rf "$SYN_FILESYSTEM/var/lib/apt/lists/*"
    sudo rm -rf "$SYN_FILESYSTEM/tmp/*"
    sudo rm -rf "$SYN_FILESYSTEM/var/tmp/*"
    
    # Unmount filesystems
    sudo umount "$SYN_FILESYSTEM/dev/pts"
    sudo umount "$SYN_FILESYSTEM/dev"
    sudo umount "$SYN_FILESYSTEM/sys"
    sudo umount "$SYN_FILESYSTEM/proc"
    
    log_success "Live system configured"
}

prepare_kernel_and_initrd() {
    log_info "Preparing kernel and initrd..."
    
    # First try to use our custom kernel
    if [[ -f "$KERNEL_BUILD/syn_kernel.bin" ]]; then
        log_info "Using Syn_OS custom kernel"
        cp "$KERNEL_BUILD/syn_kernel.bin" "$ISO_STRUCTURE/live/vmlinuz"
        
        # For a custom kernel, we need a custom initrd - use system one for now
        sudo cp /boot/initrd.img-* "$ISO_STRUCTURE/live/initrd.img" 2>/dev/null || {
            log_warning "No system initrd found, creating minimal one"
            # Create a minimal initrd
            mkdir -p /tmp/initrd
            cd /tmp/initrd
            echo "#!/bin/sh" > init
            echo "exec /sbin/init" >> init
            chmod +x init
            find . | cpio -o -H newc | gzip > "$ISO_STRUCTURE/live/initrd.img"
            cd - > /dev/null
            rm -rf /tmp/initrd
        }
    else
        log_info "Using system kernel"
        # Use system kernel
        sudo cp /boot/vmlinuz-* "$ISO_STRUCTURE/live/vmlinuz"
        sudo cp /boot/initrd.img-* "$ISO_STRUCTURE/live/initrd.img"
    fi
    
    log_success "Kernel and initrd prepared"
}

create_squashfs() {
    log_info "Creating compressed filesystem (this may take several minutes)..."
    
    # Create squashfs with high compression
    sudo mksquashfs "$SYN_FILESYSTEM" "$ISO_STRUCTURE/live/filesystem.squashfs" \
        -comp xz \
        -Xbcj x86 \
        -b 1048576 \
        -noappend \
        -progress
    
    local size=$(du -h "$ISO_STRUCTURE/live/filesystem.squashfs" | cut -f1)
    log_success "Compressed filesystem created: $size"
}

setup_bootloader() {
    log_info "Setting up bootloader..."
    
    # Copy isolinux files
    cp /usr/lib/ISOLINUX/isolinux.bin "$ISO_STRUCTURE/isolinux/"
    cp /usr/lib/syslinux/modules/bios/*.c32 "$ISO_STRUCTURE/isolinux/"
    
    # Create isolinux configuration
    tee "$ISO_STRUCTURE/isolinux/isolinux.cfg" > /dev/null <<EOF
DEFAULT vesamenu.c32
TIMEOUT 300
MENU TITLE Syn_OS 1.0 - Consciousness-Enhanced Cybersecurity Platform

LABEL live
    MENU LABEL ^Syn_OS Live (Default)
    MENU DEFAULT
    KERNEL /live/vmlinuz
    APPEND initrd=/live/initrd.img boot=live config quiet splash

LABEL live-safe
    MENU LABEL Syn_OS Live (^Safe Mode)
    KERNEL /live/vmlinuz
    APPEND initrd=/live/initrd.img boot=live config quiet splash nomodeset

LABEL live-debug
    MENU LABEL Syn_OS Live (^Debug Mode)
    KERNEL /live/vmlinuz
    APPEND initrd=/live/initrd.img boot=live config debug

MENU SEPARATOR

LABEL reboot
    MENU LABEL ^Reboot
    COM32 reboot.c32

LABEL poweroff
    MENU LABEL ^Power Off
    COM32 poweroff.c32
EOF

    # Setup GRUB for UEFI (if our kernel supports it)
    if [[ -f "$KERNEL_BUILD/grub.cfg" ]]; then
        mkdir -p "$ISO_STRUCTURE/boot/grub"
        cp "$KERNEL_BUILD/grub.cfg" "$ISO_STRUCTURE/boot/grub/"
        log_info "GRUB configuration added"
    fi
    
    log_success "Bootloader configured"
}

build_final_iso() {
    log_info "Building final ISO image..."
    
    # Remove existing ISO
    [[ -f "$ISO_OUTPUT" ]] && rm -f "$ISO_OUTPUT"
    
    # Build hybrid ISO with xorriso
    xorriso -as mkisofs \
        -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin \
        -c isolinux/boot.cat \
        -b isolinux/isolinux.bin \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        -volid "SYN_OS_V1_0" \
        -o "$ISO_OUTPUT" \
        "$ISO_STRUCTURE"
    
    log_success "ISO built successfully: $ISO_OUTPUT"
}

verify_iso() {
    log_info "Verifying ISO..."
    
    # Check ISO format
    if file "$ISO_OUTPUT" | grep -q "ISO 9660"; then
        log_success "ISO format verified"
    else
        log_error "ISO format verification failed"
        return 1
    fi
    
    # Generate checksums
    md5sum "$ISO_OUTPUT" > "$ISO_OUTPUT.md5"
    sha256sum "$ISO_OUTPUT" > "$ISO_OUTPUT.sha256"
    
    # Display information
    local size=$(du -h "$ISO_OUTPUT" | cut -f1)
    log_info "Final ISO size: $size"
    log_info "MD5: $(cat "$ISO_OUTPUT.md5" | cut -d' ' -f1)"
    log_info "SHA256: $(head -c 64 "$ISO_OUTPUT.sha256")"
    
    log_success "ISO verification complete"
}

# Main execution
main() {
    echo
    log_info "🧠 Syn_OS Production ISO Builder v2.0"
    log_info "Building consciousness-enhanced cybersecurity platform"
    echo
    
    prepare_build_environment
    
    # Try to build our custom kernel
    if build_syn_kernel; then
        log_success "Using Syn_OS custom kernel"
    else
        log_warning "Falling back to system kernel"
    fi
    
    create_base_filesystem
    integrate_syn_components
    configure_syn_branding
    setup_live_system
    prepare_kernel_and_initrd
    create_squashfs
    setup_bootloader
    build_final_iso
    verify_iso
    
    echo
    log_success "🎉 Syn_OS v1.0 ISO build completed!"
    log_info "📦 Output: $ISO_OUTPUT"
    log_info "🚀 Ready for deployment and testing"
    echo
}

main "$@"
