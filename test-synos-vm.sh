#!/bin/bash
# SynOS Linux VM Testing Script

set -e

ISO_FILE=""
VM_NAME="SynOS-Test-$(date +%Y%m%d-%H%M%S)"
VM_RAM="4096"
VM_DISK="20G"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $*"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

# Find the newest SynOS ISO
find_synos_iso() {
    log "🔍 Searching for SynOS ISO files..."

    # Look in common locations
    SEARCH_PATHS=(
        "/home/diablorain/Syn_OS/linux-distribution/SynOS-Linux-Builder/"
        "/home/diablorain/Syn_OS/"
        "$(pwd)"
    )

    for path in "${SEARCH_PATHS[@]}"; do
        if [ -d "$path" ]; then
            local found_iso=$(find "$path" -name "*synos*.iso" -o -name "*SynOS*.iso" | sort -t- -k3 -n | tail -1)
            if [ -n "$found_iso" ] && [ -f "$found_iso" ]; then
                ISO_FILE="$found_iso"
                success "Found SynOS ISO: $ISO_FILE"
                local size=$(du -h "$ISO_FILE" | cut -f1)
                log "📏 ISO Size: $size"
                return 0
            fi
        fi
    done

    error "No SynOS ISO file found!"
    log "Please ensure the ISO build completed successfully."
    exit 1
}

# Test with QEMU
test_qemu() {
    log "🖥️  Testing SynOS with QEMU..."

    if ! command -v qemu-system-x86_64 >/dev/null; then
        error "QEMU not found! Install with: sudo apt install qemu-system-x86"
        return 1
    fi

    log "🚀 Launching SynOS in QEMU..."
    log "   VM Name: $VM_NAME"
    log "   RAM: ${VM_RAM}MB"
    log "   Boot: $ISO_FILE"
    echo
    log "💡 QEMU Controls:"
    log "   - Ctrl+Alt+G: Release mouse"
    log "   - Ctrl+Alt+F: Fullscreen"
    log "   - Ctrl+Alt+2: QEMU Monitor"
    log "   - Close window to exit"
    echo

    qemu-system-x86_64 \
        -name "$VM_NAME" \
        -m "$VM_RAM" \
        -cdrom "$ISO_FILE" \
        -boot d \
        -enable-kvm \
        -cpu host \
        -smp 2 \
        -vga virtio \
        -display gtk \
        -netdev user,id=net0 \
        -device virtio-net-pci,netdev=net0 \
        -audiodev pulseaudio,id=audio0 \
        -device intel-hda \
        -device hda-duplex,audiodev=audio0
}

# Test with VirtualBox
test_vbox() {
    log "📦 Testing SynOS with VirtualBox..."

    if ! command -v VBoxManage >/dev/null; then
        warn "VirtualBox not found! Install VirtualBox to use this option."
        return 1
    fi

    log "🔧 Creating VirtualBox VM..."

    # Create VM
    VBoxManage createvm --name "$VM_NAME" --ostype "Debian_64" --register

    # Configure VM
    VBoxManage modifyvm "$VM_NAME" \
        --memory "$VM_RAM" \
        --vram 128 \
        --cpus 2 \
        --boot1 dvd \
        --boot2 disk \
        --boot3 none \
        --boot4 none \
        --audio pulse \
        --audiocontroller hda \
        --nic1 nat \
        --graphicscontroller vmsvga \
        --accelerate3d on

    # Create and attach optical drive with SynOS ISO
    VBoxManage storagectl "$VM_NAME" --name "IDE" --add ide
    VBoxManage storageattach "$VM_NAME" \
        --storagectl "IDE" \
        --port 0 \
        --device 0 \
        --type dvddrive \
        --medium "$ISO_FILE"

    log "🚀 Starting SynOS VM..."
    VBoxManage startvm "$VM_NAME" --type gui

    success "SynOS VM created and started!"
    log "💡 VM Management:"
    log "   - Use VirtualBox Manager to control the VM"
    log "   - VM Name: $VM_NAME"
}

# Main menu
main() {
    echo "🎯 SynOS Linux VM Testing Suite"
    echo "================================"
    echo

    find_synos_iso

    echo
    echo "Choose testing method:"
    echo "1) QEMU (Recommended - faster, no VM creation)"
    echo "2) VirtualBox (Creates persistent VM)"
    echo "3) Both (QEMU first, then VirtualBox)"
    echo "q) Quit"
    echo

    read -p "Enter choice [1-3,q]: " choice

    case $choice in
        1)
            test_qemu
            ;;
        2)
            test_vbox
            ;;
        3)
            test_qemu
            echo
            read -p "Press Enter to continue with VirtualBox test..."
            test_vbox
            ;;
        q|Q)
            log "👋 Exiting SynOS VM test suite."
            exit 0
            ;;
        *)
            error "Invalid choice: $choice"
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"