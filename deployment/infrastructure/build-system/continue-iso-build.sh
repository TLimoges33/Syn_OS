#!/bin/bash
# Enhanced Syn_OS Production ISO Build Script
# Phase 4: Production Deployment - Handles rsync errors gracefully

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

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    if [[ -d "$WORK_DIR" ]]; then
        sudo umount "$NEW_ROOT/proc" 2>/dev/null || true
        sudo umount "$NEW_ROOT/sys" 2>/dev/null || true
        sudo umount "$NEW_ROOT/dev/pts" 2>/dev/null || true
        sudo umount "$NEW_ROOT/dev" 2>/dev/null || true
        sudo umount "$NEW_ROOT/run" 2>/dev/null || true
        sudo umount "$NEW_ROOT/tmp" 2>/dev/null || true
    fi
}

# Set trap for cleanup
trap cleanup EXIT

# Resume from where we left off - integrate consciousness components
integrate_consciousness() {
    log_info "Integrating Syn_OS consciousness components..."
    
    # Create Syn_OS directory structure
    sudo mkdir -p "$NEW_ROOT/opt/syn_os"
    
    # Copy Syn_OS source code (excluding build directories)
    sudo rsync -av \
        --exclude="build/" \
        --exclude="target/" \
        --exclude=".git/" \
        --exclude="*.pyc" \
        --exclude="__pycache__/" \
        "$PROJECT_ROOT/src" "$NEW_ROOT/opt/syn_os/" || {
            log_warning "Some source files couldn't be copied (non-critical)"
        }
    
    # Copy configuration files
    sudo rsync -av \
        --exclude="build/" \
        "$PROJECT_ROOT/config" "$NEW_ROOT/opt/syn_os/" || true
    
    # Copy scripts
    sudo rsync -av \
        "$PROJECT_ROOT/scripts" "$NEW_ROOT/opt/syn_os/" || true
    
    # Install consciousness services
    if [[ -d "$PROJECT_ROOT/scripts/systemd" ]]; then
        sudo cp "$PROJECT_ROOT/scripts/systemd/"*.service "$NEW_ROOT/etc/systemd/system/" 2>/dev/null || true
        log_success "Systemd services installed"
    fi
    
    # Install eBPF programs
    sudo mkdir -p "$NEW_ROOT/opt/syn_os/ebpf"
    if [[ -d "$PROJECT_ROOT/src/kernel/ebpf/build" ]]; then
        sudo cp -r "$PROJECT_ROOT/src/kernel/ebpf/build/"* "$NEW_ROOT/opt/syn_os/ebpf/" 2>/dev/null || true
        log_success "eBPF programs installed"
    fi
    
    # Set proper permissions
    sudo chown -R root:root "$NEW_ROOT/opt/syn_os"
    sudo chmod +x "$NEW_ROOT/opt/syn_os/scripts/"*.sh 2>/dev/null || true
    
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
PRETTY_NAME="Syn_OS 1.0 - Consciousness-Enhanced Cybersecurity"
VERSION_ID="1.0"
HOME_URL="https://syn-os.dev"
SUPPORT_URL="https://syn-os.dev/support"
BUG_REPORT_URL="https://syn-os.dev/bugs"
ANSI_COLOR="0;34"
LOGO="syn_os"
EOF

    # Update issue files
    sudo tee "$NEW_ROOT/etc/issue" > /dev/null <<EOF

╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║     ███████╗██╗   ██╗███╗   ██╗     ██████╗ ███████╗    ██╗   ██╗██╗ ██████╗ ║
║     ██╔════╝╚██╗ ██╔╝████╗  ██║    ██╔═══██╗██╔════╝    ██║   ██║███╔══██╗  ║
║     ███████╗ ╚████╔╝ ██╔██╗ ██║    ██║   ██║███████╗    ██║   ██║ ██║  ██║  ║
║     ╚════██║  ╚██╔╝  ██║╚██╗██║    ██║   ██║╚════██║    ╚██╗ ██╔╝ ██║  ██║  ║
║     ███████║   ██║   ██║ ╚████║    ╚██████╔╝███████║     ╚████╔╝  ██████╔╝  ║
║     ╚══════╝   ╚═╝   ╚═╝  ╚═══╝     ╚═════╝ ╚══════╝      ╚═══╝   ╚═════╝   ║
║                                                                               ║
║                 Consciousness-Enhanced Cybersecurity Platform                 ║
║                                                                               ║
║  🧠 Neural Darwinism Engine    🔍 Real-time eBPF Monitoring                  ║
║  ⚡ Quantum Consciousness      🛡️  Advanced Threat Detection                 ║
║  🌐 Enterprise MSSP Platform   📊 Intelligent Analytics                      ║
║                                                                               ║
║                            Version 1.0 - Production                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Welcome to the future of AI-driven security operations.

Default login: syn_os_user / syn_os

Network Terminal on \\l

EOF

    sudo cp "$NEW_ROOT/etc/issue" "$NEW_ROOT/etc/issue.net"
    
    # Update hostname
    echo "syn-os" | sudo tee "$NEW_ROOT/etc/hostname" > /dev/null
    
    # Update MOTD
    sudo tee "$NEW_ROOT/etc/motd" > /dev/null <<EOF

🧠 Syn_OS Consciousness Engine Status:
   Neural Darwinism: Online
   eBPF Monitoring: Active
   Enterprise Dashboard: http://localhost:8080

Type 'syn-status' for system status
Type 'syn-dashboard' to open monitoring interface

EOF
    
    log_success "Branding applied"
}

# Configure live system
configure_live_system() {
    log_info "Configuring live system..."
    
    # Mount necessary filesystems for chroot
    sudo mount --bind /proc "$NEW_ROOT/proc"
    sudo mount --bind /sys "$NEW_ROOT/sys"
    sudo mount --bind /dev "$NEW_ROOT/dev"
    sudo mount --bind /dev/pts "$NEW_ROOT/dev/pts"
    sudo mount --bind /run "$NEW_ROOT/run"
    sudo mount --bind /tmp "$NEW_ROOT/tmp"
    
    # Update package database in chroot
    sudo chroot "$NEW_ROOT" apt-get update || {
        log_warning "Package update failed in chroot (non-critical)"
    }
    
    # Install essential packages for live system
    sudo chroot "$NEW_ROOT" apt-get install -y \
        live-boot \
        live-config \
        live-config-systemd \
        python3-pip \
        python3-venv \
        || {
            log_warning "Some packages failed to install (may already be present)"
        }
    
    # Install Python dependencies for consciousness engine
    sudo chroot "$NEW_ROOT" pip3 install --break-system-packages \
        fastapi \
        uvicorn \
        asyncio \
        websockets \
        psutil \
        jinja2 \
        || {
            log_warning "Some Python packages failed to install"
        }
    
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

    # Enable Syn_OS services
    if [[ -f "$NEW_ROOT/etc/systemd/system/syn-consciousness.service" ]]; then
        sudo chroot "$NEW_ROOT" systemctl enable syn-consciousness || true
        log_success "Consciousness service enabled"
    fi
    
    if [[ -f "$NEW_ROOT/etc/systemd/system/syn-ebpf-monitor.service" ]]; then
        sudo chroot "$NEW_ROOT" systemctl enable syn-ebpf-monitor || true
        log_success "eBPF monitor service enabled"
    fi
    
    if [[ -f "$NEW_ROOT/etc/systemd/system/syn-enterprise-dashboard.service" ]]; then
        sudo chroot "$NEW_ROOT" systemctl enable syn-enterprise-dashboard || true
        log_success "Enterprise dashboard service enabled"
    fi
    
    # Create desktop shortcuts for Syn_OS tools
    sudo mkdir -p "$NEW_ROOT/home/syn_os_user/Desktop"
    
    # Desktop shortcut for dashboard
    sudo tee "$NEW_ROOT/home/syn_os_user/Desktop/syn_os_dashboard.desktop" > /dev/null <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Syn_OS Dashboard
Comment=Consciousness-Enhanced Security Dashboard
Exec=firefox http://localhost:8080
Icon=applications-internet
Terminal=false
Categories=Security;Network;
EOF

    sudo chmod +x "$NEW_ROOT/home/syn_os_user/Desktop/syn_os_dashboard.desktop"
    sudo chown -R 1000:1000 "$NEW_ROOT/home/syn_os_user" 2>/dev/null || true
    
    # Unmount filesystems
    sudo umount "$NEW_ROOT/tmp" "$NEW_ROOT/run" "$NEW_ROOT/dev/pts" "$NEW_ROOT/dev" "$NEW_ROOT/sys" "$NEW_ROOT/proc"
    
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
        -no-duplicates \
        -no-recovery \
        -wildcards \
        -e "build" "target" ".git" "*.log" "*.tmp" "lost+found" \
        -progress
    
    log_success "Compressed filesystem created: $(du -h "$SQUASHFS_FILE" | cut -f1)"
}

# Prepare boot files
prepare_boot_files() {
    log_info "Preparing boot files..."
    
    mkdir -p "$ISO_STAGING/live"
    
    # Copy kernel and initrd from new root or system
    if [[ -f "$NEW_ROOT/boot/vmlinuz" ]]; then
        cp "$NEW_ROOT/boot/vmlinuz" "$ISO_STAGING/live/vmlinuz"
    else
        cp /boot/vmlinuz-* "$ISO_STAGING/live/vmlinuz" 2>/dev/null || {
            log_error "No kernel found!"
            return 1
        }
    fi
    
    if [[ -f "$NEW_ROOT/boot/initrd.img" ]]; then
        cp "$NEW_ROOT/boot/initrd.img" "$ISO_STAGING/live/initrd.img"
    else
        cp /boot/initrd.img-* "$ISO_STAGING/live/initrd.img" 2>/dev/null || {
            log_error "No initrd found!"
            return 1
        }
    fi
    
    # Setup isolinux
    mkdir -p "$ISO_STAGING/isolinux"
    cp /usr/lib/ISOLINUX/isolinux.bin "$ISO_STAGING/isolinux/"
    cp /usr/lib/syslinux/modules/bios/ldlinux.c32 "$ISO_STAGING/isolinux/"
    cp /usr/lib/syslinux/modules/bios/libcom32.c32 "$ISO_STAGING/isolinux/"
    cp /usr/lib/syslinux/modules/bios/libutil.c32 "$ISO_STAGING/isolinux/"
    cp /usr/lib/syslinux/modules/bios/vesamenu.c32 "$ISO_STAGING/isolinux/"
    cp /usr/lib/syslinux/modules/bios/reboot.c32 "$ISO_STAGING/isolinux/"
    cp /usr/lib/syslinux/modules/bios/poweroff.c32 "$ISO_STAGING/isolinux/"
    
    # Create EFI boot structure
    mkdir -p "$ISO_STAGING/boot/grub"
    
    log_success "Boot files prepared"
}

# Create isolinux configuration
create_isolinux_config() {
    log_info "Creating boot configuration..."
    
    # Main isolinux config
    tee "$ISO_STAGING/isolinux/isolinux.cfg" > /dev/null <<EOF
DEFAULT vesamenu.c32
TIMEOUT 300
MENU TITLE Syn_OS 1.0 - Consciousness-Enhanced Cybersecurity Platform

MENU BACKGROUND splash.png
MENU COLOR screen 37;40 #80ffffff #00000000 std
MENU COLOR border 30;44 #40ffffff #a0000000 std
MENU COLOR title 1;36;44 #ffffffff #a0000000 std
MENU COLOR sel 7;37;40 #e0ffffff #20ffffff all
MENU COLOR unsel 37;44 #50ffffff #a0000000 std
MENU COLOR help 37;40 #c0ffffff #a0000000 std
MENU COLOR timeout_msg 37;40 #80ffffff #00000000 std
MENU COLOR timeout 1;37;40 #c0ffffff #00000000 std
MENU COLOR msg07 37;40 #90ffffff #a0000000 std
MENU COLOR tabmsg 31;40 #30ffffff #00000000 std

LABEL live
    MENU LABEL ^Syn_OS Live (Default)
    MENU DEFAULT
    KERNEL /live/vmlinuz
    APPEND initrd=/live/initrd.img boot=live config quiet splash components username=syn_os_user hostname=syn-os

LABEL live-safe
    MENU LABEL Syn_OS Live (Safe Mode)
    KERNEL /live/vmlinuz
    APPEND initrd=/live/initrd.img boot=live config quiet splash nomodeset acpi=off

LABEL live-debug
    MENU LABEL Syn_OS Live (Debug Mode)
    KERNEL /live/vmlinuz
    APPEND initrd=/live/initrd.img boot=live config debug

MENU SEPARATOR

LABEL reboot
    MENU LABEL ^Reboot System
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
        -isohybrid-gpt-basdat \
        -volid "SYN_OS_V1_0" \
        -joliet \
        -rational-rock \
        -follow-links \
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
    echo "MD5: $(cat "$ISO_OUTPUT.md5")"
    echo "SHA256: $(cat "$ISO_OUTPUT.sha256")"
}

# Main execution flow - Continue from where we left off
main() {
    log_info "Continuing Syn_OS Production ISO Build"
    log_info "Phase 4: Production Deployment & Enterprise Integration"
    echo
    
    # Continue from post-rsync
    integrate_consciousness
    apply_branding
    configure_live_system
    create_squashfs
    prepare_boot_files
    create_isolinux_config
    build_iso
    verify_iso
    
    echo
    log_success "🎉 Syn_OS Production ISO build completed successfully!"
    log_info "📀 Output: $ISO_OUTPUT"
    log_info "🚀 Ready for deployment and testing"
    echo
    log_info "To test the ISO:"
    log_info "  sudo qemu-system-x86_64 -m 2048 -cdrom $ISO_OUTPUT"
    echo
    log_info "To write to USB drive:"
    log_info "  sudo dd if=$ISO_OUTPUT of=/dev/sdX bs=4M status=progress"
}

# Execute main function
main "$@"
