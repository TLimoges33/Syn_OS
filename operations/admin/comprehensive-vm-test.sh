#!/bin/bash

# Comprehensive VM Testing Framework for SynOS
# This script provides extensive testing and debugging capabilities

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ISO_PATH="${1:-$PROJECT_ROOT/build/SynOS-v1.0-20250902.iso}"
TEST_MODE="${2:-comprehensive}"

# Create logs directory
LOG_DIR="$PROJECT_ROOT/build/test-logs"
mkdir -p "$LOG_DIR"

log_info() {
    echo "[INFO] $1" | tee -a "$LOG_DIR/test-session.log"
}

log_success() {
    echo "✅ $1" | tee -a "$LOG_DIR/test-session.log"
}

log_warning() {
    echo "⚠️ $1" | tee -a "$LOG_DIR/test-session.log"
}

log_error() {
    echo "❌ $1" | tee -a "$LOG_DIR/test-session.log"
}

# Check if ISO exists
if [[ ! -f "$ISO_PATH" ]]; then
    log_error "ISO not found: $ISO_PATH"
    exit 1
fi

log_info "=== SynOS Comprehensive VM Testing Framework ==="
log_info "ISO: $ISO_PATH"
log_info "Size: $(du -h "$ISO_PATH" | cut -f1)"
log_info "Test Mode: $TEST_MODE"
log_info "Session started: $(date)"

# Test 1: ISO Structure Analysis
test_iso_structure() {
    log_info "=== Testing ISO Structure ==="
    
    local temp_mount=$(mktemp -d)
    local iso_extract=$(mktemp -d)
    
    # Try to extract ISO contents
    if command -v 7z >/dev/null 2>&1; then
        log_info "Extracting ISO with 7z..."
        7z x "$ISO_PATH" -o"$iso_extract" > /dev/null 2>&1 || {
            log_warning "7z extraction failed, trying isoinfo"
        }
    fi
    
    # Check basic structure
    if [[ -d "$iso_extract" ]]; then
        log_info "ISO Contents:"
        find "$iso_extract" -type f -exec ls -lh {} \; | head -20 | tee -a "$LOG_DIR/iso-structure.log"
        
        # Check critical files
        if [[ -f "$iso_extract/live/vmlinuz" ]]; then
            log_success "Found kernel: vmlinuz"
            file "$iso_extract/live/vmlinuz" | tee -a "$LOG_DIR/iso-structure.log"
            stat "$iso_extract/live/vmlinuz" | tee -a "$LOG_DIR/iso-structure.log"
        else
            log_error "Kernel vmlinuz not found!"
        fi
        
        if [[ -f "$iso_extract/live/initrd.img" ]]; then
            log_success "Found initrd: initrd.img"
            stat "$iso_extract/live/initrd.img" | tee -a "$LOG_DIR/iso-structure.log"
        else
            log_error "initrd.img not found!"
        fi
        
        if [[ -f "$iso_extract/isolinux/isolinux.cfg" ]]; then
            log_success "Found bootloader config"
            log_info "Bootloader configuration:"
            cat "$iso_extract/isolinux/isolinux.cfg" | tee -a "$LOG_DIR/bootloader-config.log"
        else
            log_error "Bootloader configuration not found!"
        fi
    fi
    
    # Cleanup
    rm -rf "$temp_mount" "$iso_extract" 2>/dev/null || true
}

# Test 2: QEMU Testing with Serial Output
test_qemu_serial() {
    log_info "=== Testing QEMU with Serial Output ==="
    
    local log_file="$LOG_DIR/qemu-serial-$(date +%Y%m%d-%H%M%S).log"
    local qemu_log="$LOG_DIR/qemu-debug-$(date +%Y%m%d-%H%M%S).log"
    
    log_info "Starting QEMU with comprehensive logging..."
    log_info "Serial output: $log_file"
    log_info "QEMU debug: $qemu_log"
    
    # Run QEMU with extensive debugging
    timeout 45s qemu-system-x86_64 \
        -cdrom "$ISO_PATH" \
        -m 1024 \
        -boot d \
        -serial file:"$log_file" \
        -monitor stdio \
        -d guest_errors,unimp \
        -D "$qemu_log" \
        -no-reboot \
        -enable-kvm 2>/dev/null || \
    timeout 45s qemu-system-x86_64 \
        -cdrom "$ISO_PATH" \
        -m 1024 \
        -boot d \
        -serial file:"$log_file" \
        -monitor stdio \
        -d guest_errors,unimp \
        -D "$qemu_log" \
        -no-reboot \
        > /dev/null 2>&1 &
    
    local qemu_pid=$!
    
    # Wait and monitor
    sleep 30
    
    if ps -p $qemu_pid > /dev/null 2>/dev/null; then
        log_success "QEMU is running"
        kill $qemu_pid 2>/dev/null || true
        wait $qemu_pid 2>/dev/null || true
    else
        log_warning "QEMU process finished"
    fi
    
    # Analyze logs
    log_info "Analyzing boot logs..."
    
    if [[ -f "$log_file" ]]; then
        local log_size=$(stat -c%s "$log_file" 2>/dev/null || echo "0")
        if [[ $log_size -gt 0 ]]; then
            log_success "Serial output captured ($log_size bytes)"
            log_info "Serial output content:"
            head -20 "$log_file" | tee -a "$LOG_DIR/boot-analysis.log"
            
            # Look for SynOS specific output
            if grep -q "SynOS\|Syn_OS\|SynapticOS" "$log_file" 2>/dev/null; then
                log_success "Found SynOS references in serial output!"
            else
                log_warning "No SynOS references found in serial output"
            fi
        else
            log_warning "Serial output file is empty"
        fi
    else
        log_error "Serial output file not created"
    fi
    
    if [[ -f "$qemu_log" ]]; then
        local debug_size=$(stat -c%s "$qemu_log" 2>/dev/null || echo "0")
        if [[ $debug_size -gt 0 ]]; then
            log_info "QEMU debug log captured ($debug_size bytes)"
            # Check for critical errors
            if grep -i "error\|fail\|panic" "$qemu_log" >/dev/null 2>&1; then
                log_warning "Found errors in QEMU debug log:"
                grep -i "error\|fail\|panic" "$qemu_log" | head -5 | tee -a "$LOG_DIR/boot-analysis.log"
            fi
        fi
    fi
}

# Test 3: Boot Process Analysis
test_boot_process() {
    log_info "=== Analyzing Boot Process ==="
    
    local boot_log="$LOG_DIR/boot-trace-$(date +%Y%m%d-%H%M%S).log"
    
    # Run QEMU with detailed tracing
    log_info "Tracing boot process..."
    
    timeout 30s qemu-system-x86_64 \
        -cdrom "$ISO_PATH" \
        -m 512 \
        -boot d \
        -serial file:"$boot_log" \
        -display none \
        -d exec,cpu_reset,int \
        -no-reboot \
        > /dev/null 2>&1 &
    
    local trace_pid=$!
    sleep 25
    kill $trace_pid 2>/dev/null || true
    wait $trace_pid 2>/dev/null || true
    
    # Analyze boot sequence
    if [[ -f "$boot_log" ]]; then
        if [[ $(stat -c%s "$boot_log") -gt 0 ]]; then
            log_success "Boot trace captured"
            log_info "Boot sequence analysis:"
            
            # Look for bootloader messages
            if grep -i "isolinux\|syslinux\|grub" "$boot_log" >/dev/null 2>&1; then
                log_success "Bootloader activity detected"
            else
                log_warning "No bootloader activity detected"
            fi
            
            # Look for kernel loading
            if grep -i "kernel\|loading\|vmlinuz" "$boot_log" >/dev/null 2>&1; then
                log_success "Kernel loading activity detected"
            else
                log_warning "No kernel loading activity detected"
            fi
            
        else
            log_warning "Boot trace is empty"
        fi
    fi
}

# Test 4: Alternative Bootloader Testing
test_alternative_boot() {
    log_info "=== Testing Alternative Boot Methods ==="
    
    # Test with different QEMU machine types
    local machines=("pc" "q35")
    
    for machine in "${machines[@]}"; do
        log_info "Testing with machine type: $machine"
        
        local machine_log="$LOG_DIR/boot-$machine-$(date +%Y%m%d-%H%M%S).log"
        
        timeout 20s qemu-system-x86_64 \
            -cdrom "$ISO_PATH" \
            -m 512 \
            -boot d \
            -machine "$machine" \
            -serial file:"$machine_log" \
            -display none \
            -no-reboot \
            > /dev/null 2>&1 &
        
        local machine_pid=$!
        sleep 15
        kill $machine_pid 2>/dev/null || true
        wait $machine_pid 2>/dev/null || true
        
        if [[ -f "$machine_log" && $(stat -c%s "$machine_log") -gt 0 ]]; then
            log_success "Machine $machine produced output"
        else
            log_warning "Machine $machine produced no output"
        fi
    done
}

# Test 5: Kernel Analysis
test_kernel_analysis() {
    log_info "=== Analyzing Kernel Binary ==="
    
    local kernel_path="$PROJECT_ROOT/target/x86_64-unknown-none/debug/kernel"
    
    if [[ -f "$kernel_path" ]]; then
        log_info "Original kernel analysis:"
        file "$kernel_path" | tee -a "$LOG_DIR/kernel-analysis.log"
        ls -lh "$kernel_path" | tee -a "$LOG_DIR/kernel-analysis.log"
        
        # Check if kernel has multiboot header
        if command -v objdump >/dev/null 2>&1; then
            log_info "Checking for multiboot headers..."
            if objdump -h "$kernel_path" 2>/dev/null | grep -i "multiboot\|boot" >/dev/null; then
                log_success "Found boot-related sections"
            else
                log_warning "No obvious boot sections found"
            fi
        fi
        
        # Check entry point
        if command -v readelf >/dev/null 2>&1; then
            log_info "Entry point information:"
            readelf -h "$kernel_path" 2>/dev/null | grep "Entry point" | tee -a "$LOG_DIR/kernel-analysis.log"
        fi
    else
        log_error "Kernel binary not found at $kernel_path"
    fi
}

# Main test execution
case "$TEST_MODE" in
    "structure")
        test_iso_structure
        ;;
    "serial")
        test_qemu_serial
        ;;
    "boot")
        test_boot_process
        ;;
    "kernel")
        test_kernel_analysis
        ;;
    "comprehensive")
        test_iso_structure
        test_kernel_analysis
        test_qemu_serial
        test_boot_process
        test_alternative_boot
        ;;
    *)
        log_error "Unknown test mode: $TEST_MODE"
        log_info "Available modes: structure, serial, boot, kernel, comprehensive"
        exit 1
        ;;
esac

# Generate summary report
log_info "=== Test Session Summary ==="
log_info "Session completed: $(date)"
log_info "Logs available in: $LOG_DIR"

# List all generated logs
log_info "Generated files:"
find "$LOG_DIR" -name "*$(date +%Y%m%d)*" -type f -exec ls -lh {} \;

log_success "VM testing framework execution complete!"
log_info "Review logs for detailed analysis and debugging information"
