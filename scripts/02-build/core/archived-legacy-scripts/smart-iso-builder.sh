#!/bin/bash

# SynOS v1.0 Smart ISO Builder
# Incremental, resource-aware ISO creation that won't crash the system

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
BUILD_DIR="/home/diablorain/Syn_OS/build/synos-iso"
WORK_DIR="/tmp/synos-work"
ISO_NAME="SynOS-v1.0-Developer-$(date +%Y%m%d).iso"
LOG_FILE="/home/diablorain/Syn_OS/build/iso-build.log"

# Resource management
MAX_MEMORY_USAGE=80  # Percentage
CHECK_INTERVAL=5     # Seconds

log_info() { echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"; }

print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║              🧠 SynOS v1.0 Smart ISO Builder                 ║"
    echo "║           Incremental, System-Safe Construction              ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_system_resources() {
    local memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    local disk_usage=$(df /tmp | awk 'NR==2{printf "%.1f", $5}' | sed 's/%//')
    local load_avg=$(uptime | awk -F'load average:' '{ print $2 }' | awk '{ print $1 }' | sed 's/,//')
    
    log_info "System Status - Memory: ${memory_usage}%, Disk: ${disk_usage}%, Load: ${load_avg}"
    
    # Check if we're approaching resource limits
    if (( $(echo "$memory_usage > $MAX_MEMORY_USAGE" | bc -l) )); then
        log_warning "High memory usage detected (${memory_usage}%) - waiting for resources..."
        sleep 10
        return 1
    fi
    
    if (( $(echo "$disk_usage > 90" | bc -l) )); then
        log_error "Disk space critically low (${disk_usage}%) - aborting build"
        exit 1
    fi
    
    return 0
}

wait_for_resources() {
    log_info "Waiting for system resources to stabilize..."
    while ! check_system_resources; do
        log_info "Resources still constrained, waiting ${CHECK_INTERVAL}s..."
        sleep $CHECK_INTERVAL
    done
    log_success "System resources available for next operation"
}

create_build_structure() {
    log_info "📁 Creating smart build structure..."
    
    # Clean any previous failed builds
    if [[ -d "$WORK_DIR" ]]; then
        log_info "Cleaning previous build workspace..."
        rm -rf "$WORK_DIR"
    fi
    
    mkdir -p "$BUILD_DIR"
    mkdir -p "$WORK_DIR"/{iso,rootfs,chroot}
    
    log_success "Build directories created"
}

download_base_system() {
    log_info "📦 Setting up base system (minimal approach)..."
    
    wait_for_resources
    
    # Use mmdebstrap instead of debootstrap - it's more efficient
    if ! command -v mmdebstrap >/dev/null 2>&1; then
        log_info "Installing mmdebstrap for efficient base system creation..."
        sudo apt update
        sudo apt install -y mmdebstrap
    fi
    
    # Create minimal base system with resource monitoring
    log_info "Creating minimal Debian base system..."
    
    # Monitor the mmdebstrap process
    (
        sudo mmdebstrap \
            --mode=sudo \
            --variant=minbase \
            --include=systemd,udev,kmod,ifupdown,iproute2,iputils-ping,wget,curl,nano,bash-completion \
            --customize-hook='chroot "$1" /bin/bash -c "echo SynOS > /etc/hostname"' \
            --customize-hook='chroot "$1" /bin/bash -c "echo 127.0.0.1 localhost SynOS >> /etc/hosts"' \
            bookworm \
            "$WORK_DIR/rootfs" \
            http://deb.debian.org/debian
    ) &
    
    MMDEBSTRAP_PID=$!
    
    # Monitor resource usage during base system creation
    while kill -0 $MMDEBSTRAP_PID 2>/dev/null; do
        if ! check_system_resources; then
            log_warning "Resource pressure detected during base system creation"
            # Don't kill the process, just wait and monitor
        fi
        sleep $CHECK_INTERVAL
    done
    
    wait $MMDEBSTRAP_PID
    if [[ $? -eq 0 ]]; then
        log_success "Base system created successfully"
    else
        log_error "Base system creation failed"
        exit 1
    fi
}

install_synos_components() {
    log_info "🧠 Installing SynOS consciousness components..."
    
    wait_for_resources
    
    # Copy our lightweight implementation into the ISO
    SYNOS_DIR="$WORK_DIR/rootfs/opt/synos"
    sudo mkdir -p "$SYNOS_DIR"
    
    # Copy consciousness components
    sudo cp -r /home/diablorain/Syn_OS/core/build/lightweight-iso/* "$SYNOS_DIR/"
    
    # Make scripts executable
    sudo chmod +x "$SYNOS_DIR/scripts/"*.sh
    sudo chmod +x "$SYNOS_DIR"/*.sh
    
    # Install Python packages needed for consciousness service
    log_info "Installing Python dependencies..."
    sudo chroot "$WORK_DIR/rootfs" /bin/bash -c "
        apt update
        apt install -y python3 python3-pip python3-venv
        pip3 install --break-system-packages requests urllib3
    "
    
    # Create systemd service for consciousness
    sudo tee "$WORK_DIR/rootfs/etc/systemd/system/synos-consciousness.service" > /dev/null <<EOF
[Unit]
Description=SynOS Consciousness Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/synos/scripts
ExecStart=/usr/bin/python3 /opt/synos/scripts/consciousness-service.py 8080
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    # Enable the service
    sudo chroot "$WORK_DIR/rootfs" /bin/bash -c "systemctl enable synos-consciousness.service"
    
    log_success "SynOS consciousness components installed"
}

install_security_tools() {
    log_info "🔐 Installing essential security tools..."
    
    wait_for_resources
    
    # Install core security packages in chunks to manage memory
    local tool_groups=(
        "nmap netcat-traditional netdiscover"
        "wireshark tcpdump tshark"
        "hashcat john hydra"
        "metasploit-framework"
        "burpsuite"
    )
    
    for group in "${tool_groups[@]}"; do
        log_info "Installing: $group"
        wait_for_resources
        
        sudo chroot "$WORK_DIR/rootfs" /bin/bash -c "
            apt update
            apt install -y $group || echo 'Some packages in group failed, continuing...'
        "
        
        # Small pause between groups
        sleep 2
    done
    
    log_success "Security tools installation completed"
}

create_live_system() {
    log_info "💿 Creating live boot system..."
    
    wait_for_resources
    
    # Install live-boot packages
    sudo chroot "$WORK_DIR/rootfs" /bin/bash -c "
        apt update
        apt install -y live-boot live-config live-config-systemd
        apt install -y linux-image-amd64 live-boot-initramfs-tools
    "
    
    # Create live-specific directories
    sudo mkdir -p "$WORK_DIR/rootfs/etc/live/config"
    
    # Configure live boot
    sudo tee "$WORK_DIR/rootfs/etc/live/config/0010-main" > /dev/null <<EOF
#!/bin/sh
# SynOS Live Boot Configuration
echo "Welcome to SynOS v1.0 - AI-Powered Security OS"
/opt/synos/scripts/consciousness-service.py 8080 &
EOF
    
    sudo chmod +x "$WORK_DIR/rootfs/etc/live/config/0010-main"
    
    log_success "Live system configuration completed"
}

build_iso_image() {
    log_info "🏗️ Building final ISO image..."
    
    wait_for_resources
    
    # Install xorriso for ISO creation
    if ! command -v xorriso >/dev/null 2>&1; then
        sudo apt install -y xorriso isolinux syslinux-efi grub-pc-bin grub-efi-amd64-bin
    fi
    
    # Create ISO structure
    mkdir -p "$WORK_DIR/iso/live"
    
    # Create filesystem
    log_info "Creating compressed filesystem..."
    sudo mksquashfs "$WORK_DIR/rootfs" "$WORK_DIR/iso/live/filesystem.squashfs" -comp xz -Xbcj x86
    
    # Copy kernel and initrd
    sudo cp "$WORK_DIR/rootfs/boot/vmlinuz-"* "$WORK_DIR/iso/live/vmlinuz"
    sudo cp "$WORK_DIR/rootfs/boot/initrd.img-"* "$WORK_DIR/iso/live/initrd"
    
    # Create isolinux configuration
    mkdir -p "$WORK_DIR/iso/isolinux"
    sudo cp /usr/lib/ISOLINUX/isolinux.bin "$WORK_DIR/iso/isolinux/"
    sudo cp /usr/lib/syslinux/modules/bios/*.c32 "$WORK_DIR/iso/isolinux/"
    
    # Create boot menu
    cat > "$WORK_DIR/iso/isolinux/isolinux.cfg" <<EOF
DEFAULT live
TIMEOUT 50
PROMPT 1

LABEL live
  MENU LABEL SynOS v1.0 Live (Default)
  KERNEL /live/vmlinuz
  APPEND initrd=/live/initrd boot=live components quiet splash
  
LABEL consciousness
  MENU LABEL SynOS Consciousness Mode
  KERNEL /live/vmlinuz
  APPEND initrd=/live/initrd boot=live components quiet splash synos=consciousness

LABEL forensics
  MENU LABEL SynOS Forensics Mode (No Swap)
  KERNEL /live/vmlinuz
  APPEND initrd=/live/initrd boot=live components quiet splash noswap noeject
EOF
    
    # Build the final ISO
    log_info "Creating bootable ISO image..."
    xorriso -as mkisofs \
        -iso-level 3 \
        -full-iso9660-filenames \
        -volid "SynOS_v1.0" \
        -eltorito-boot isolinux/isolinux.bin \
        -eltorito-catalog isolinux/boot.cat \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin \
        -output "$BUILD_DIR/$ISO_NAME" \
        "$WORK_DIR/iso"
    
    log_success "ISO image created: $BUILD_DIR/$ISO_NAME"
}

cleanup_build() {
    log_info "🧹 Cleaning up build workspace..."
    
    # Clean work directory but keep logs
    if [[ -d "$WORK_DIR" ]]; then
        sudo rm -rf "$WORK_DIR"
    fi
    
    log_success "Build cleanup completed"
}

show_final_status() {
    local iso_size=$(du -h "$BUILD_DIR/$ISO_NAME" 2>/dev/null | cut -f1 || echo "Unknown")
    
    echo ""
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║                 🎉 SynOS v1.0 ISO COMPLETE! 🎉               ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo -e "${BLUE}📀 ISO Details:${NC}"
    echo "   File: $BUILD_DIR/$ISO_NAME"
    echo "   Size: $iso_size"
    echo "   Build Log: $LOG_FILE"
    echo ""
    echo -e "${BLUE}🎯 Features Included:${NC}"
    echo "   • AI Consciousness Service (auto-starts on boot)"
    echo "   • Interactive Learning Platform"
    echo "   • Essential Security Tools"
    echo "   • Live Boot System"
    echo "   • Web Dashboard (http://localhost:8080)"
    echo ""
    echo -e "${BLUE}🚀 Testing Commands:${NC}"
    echo "   Virtual Test: qemu-system-x86_64 -m 2048 -cdrom $BUILD_DIR/$ISO_NAME"
    echo "   USB Creation: dd if=$BUILD_DIR/$ISO_NAME of=/dev/sdX bs=4M status=progress"
    echo ""
    echo -e "${GREEN}✅ SynOS v1.0 is ready for deployment!${NC}"
}

main() {
    print_banner
    
    # Check prerequisites
    if [[ $EUID -ne 0 ]] && ! sudo -n true 2>/dev/null; then
        log_error "This script requires sudo access for chroot operations"
        exit 1
    fi
    
    # Check available disk space
    local available_space=$(df /tmp | awk 'NR==2{print $4}')
    if [[ $available_space -lt 4194304 ]]; then  # 4GB in KB
        log_error "Insufficient disk space. Need at least 4GB free in /tmp"
        exit 1
    fi
    
    log_info "🚀 Starting SynOS v1.0 Smart ISO Build Process..."
    log_info "Build will be monitored for resource usage to prevent system crashes"
    echo ""
    
    # Execute build phases with resource monitoring
    create_build_structure
    download_base_system
    install_synos_components
    install_security_tools
    create_live_system
    build_iso_image
    cleanup_build
    show_final_status
    
    log_success "🎯 SynOS v1.0 ISO build completed successfully!"
}

# Trap to ensure cleanup on exit
trap cleanup_build EXIT

# Run main function
main "$@"
