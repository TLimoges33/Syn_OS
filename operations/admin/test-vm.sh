#!/bin/bash

# SynOS VM Testing Script
# Tests the built ISO in QEMU

set -e

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ISO_PATH="$PROJECT_ROOT/build/SynOS-v1.0-20250902.iso"
LOG_DIR="$PROJECT_ROOT/build/test-logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Create log directory
mkdir -p "$LOG_DIR"

# Check if ISO exists
if [[ ! -f "$ISO_PATH" ]]; then
    log_error "ISO not found: $ISO_PATH"
    log_info "Please build the ISO first with: ./ecosystem/build-system/build-simple-kernel-iso.sh"
    exit 1
fi

log_info "=== SynOS VM Testing ==="
log_info "ISO: $ISO_PATH"
log_info "Size: $(du -h "$ISO_PATH" | cut -f1)"

# Test 1: Basic QEMU boot test
test_qemu_basic() {
    log_info "Testing basic QEMU boot..."
    
    local log_file="$LOG_DIR/qemu-basic-$(date +%Y%m%d-%H%M%S).log"
    
    log_info "Starting QEMU (will timeout after 60 seconds)..."
    log_info "Boot log will be saved to: $log_file"
    
    # Run QEMU with serial console output
    timeout 60s qemu-system-x86_64 \
        -cdrom "$ISO_PATH" \
        -m 1024 \
        -boot d \
        -serial file:"$log_file" \
        -display none \
        -no-reboot \
        > /dev/null 2>&1 &
    
    local qemu_pid=$!
    
    # Monitor for a few seconds
    sleep 10
    
    if ps -p $qemu_pid > /dev/null; then
        log_success "QEMU started successfully and is running"
        kill $qemu_pid 2>/dev/null || true
        wait $qemu_pid 2>/dev/null || true
    else
        log_warning "QEMU process ended quickly - check logs"
    fi
    
    # Check log content
    if [[ -f "$log_file" ]]; then
        log_info "Boot log analysis:"
        if grep -q "Syn" "$log_file"; then
            log_success "Found SynOS references in boot log"
        else
            log_warning "No SynOS references found in boot log"
        fi
        
        if grep -i "panic\|error\|failed" "$log_file"; then
            log_warning "Found potential errors in boot log"
        else
            log_success "No obvious errors in boot log"
        fi
        
        log_info "Full boot log:"
        cat "$log_file"
    else
        log_error "No boot log generated"
    fi
}

# Test 2: Interactive QEMU session
test_qemu_interactive() {
    log_info "Starting interactive QEMU session..."
    log_info "Press Ctrl+Alt+G to release mouse, Ctrl+Alt+Q to quit"
    log_info "Starting in 3 seconds..."
    sleep 3
    
    qemu-system-x86_64 \
        -cdrom "$ISO_PATH" \
        -m 1024 \
        -boot d \
        -vga std \
        -usb \
        -device usb-tablet
}

# Test 3: Check ISO structure
test_iso_structure() {
    log_info "Analyzing ISO structure..."
    
    # Create temporary mount point
    local mount_point="/tmp/synos-iso-$$"
    mkdir -p "$mount_point"
    
    # Mount ISO (requires sudo)
    if sudo mount -o loop "$ISO_PATH" "$mount_point" 2>/dev/null; then
        log_success "ISO mounted successfully"
        
        log_info "ISO contents:"
        ls -la "$mount_point"
        
        if [[ -d "$mount_point/live" ]]; then
            log_success "Found live directory"
            ls -la "$mount_point/live"
            
            if [[ -f "$mount_point/live/vmlinuz" ]]; then
                log_success "Found kernel: $(du -h "$mount_point/live/vmlinuz" | cut -f1)"
            fi
            
            if [[ -f "$mount_point/live/initrd.img" ]]; then
                log_success "Found initrd: $(du -h "$mount_point/live/initrd.img" | cut -f1)"
            fi
            
            if [[ -f "$mount_point/live/filesystem.squashfs" ]]; then
                log_success "Found filesystem: $(du -h "$mount_point/live/filesystem.squashfs" | cut -f1)"
            fi
        fi
        
        # Unmount
        sudo umount "$mount_point"
        rmdir "$mount_point"
    else
        log_warning "Could not mount ISO (sudo required)"
    fi
}

# Main execution
main() {
    case "${1:-all}" in
        "basic")
            test_qemu_basic
            ;;
        "interactive")
            test_qemu_interactive
            ;;
        "structure")
            test_iso_structure
            ;;
        "all")
            test_iso_structure
            test_qemu_basic
            log_info ""
            log_info "To run interactive test: $0 interactive"
            ;;
        *)
            echo "Usage: $0 [basic|interactive|structure|all]"
            echo "  basic       - Automated boot test with log capture"
            echo "  interactive - Manual testing with GUI"
            echo "  structure   - Analyze ISO file structure"
            echo "  all         - Run all automated tests"
            exit 1
            ;;
    esac
}

main "$@"
