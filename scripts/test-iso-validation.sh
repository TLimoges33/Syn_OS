#!/bin/bash

# Syn_OS ISO Validation and Testing Framework
# Comprehensive testing suite for bootable ISO validation
# Advanced AI-Powered Cybersecurity Education Operating System

set -e

# Script metadata
SCRIPT_VERSION="1.0.0"
TEST_DATE=$(date +%Y%m%d-%H%M%S)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
BUILD_DIR="${PROJECT_ROOT}/build/iso-complete"
TEST_RESULTS_DIR="${BUILD_DIR}/test-results"
QEMU_TIMEOUT=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_test() { echo -e "${PURPLE}[TEST]${NC} $1"; }
log_result() { echo -e "${CYAN}[RESULT]${NC} $1"; }

# Test tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test result tracking
start_test() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    log_test "$1"
}

pass_test() {
    PASSED_TESTS=$((PASSED_TESTS + 1))
    log_success "✅ PASS: $1"
}

fail_test() {
    FAILED_TESTS=$((FAILED_TESTS + 1))
    log_error "❌ FAIL: $1"
}

# Setup test environment
setup_test_environment() {
    log_info "Setting up ISO validation test environment..."
    
    mkdir -p "$TEST_RESULTS_DIR"
    
    # Find the most recent ISO
    ISO_FILE=$(find "$BUILD_DIR" -name "*.iso" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
    
    if [[ -z "$ISO_FILE" ]]; then
        log_error "No ISO file found in $BUILD_DIR"
        log_info "Please run ./scripts/build-iso.sh first"
        exit 1
    fi
    
    log_info "Testing ISO: $(basename "$ISO_FILE")"
    log_info "ISO Size: $(du -h "$ISO_FILE" | cut -f1)"
    
    # Create test report header
    cat > "$TEST_RESULTS_DIR/validation-report-${TEST_DATE}.txt" << EOF
Syn_OS ISO Validation Report
============================

Test Date: $(date -R)
ISO File: $(basename "$ISO_FILE")
ISO Size: $(du -h "$ISO_FILE" | cut -f1)
Test Framework Version: $SCRIPT_VERSION

EOF
}

# Test 1: ISO file integrity
test_iso_integrity() {
    start_test "ISO file integrity and checksums"
    
    local iso_name=$(basename "$ISO_FILE")
    local checksum_file="${ISO_FILE}.sha256"
    
    if [[ -f "$checksum_file" ]]; then
        cd "$(dirname "$ISO_FILE")"
        if sha256sum -c "$(basename "$checksum_file")" >/dev/null 2>&1; then
            pass_test "SHA256 checksum verification"
        else
            fail_test "SHA256 checksum verification"
        fi
    else
        log_warning "No SHA256 checksum file found"
    fi
    
    # Test ISO file structure
    if file "$ISO_FILE" | grep -q "ISO 9660"; then
        pass_test "ISO 9660 format validation"
    else
        fail_test "ISO 9660 format validation"
    fi
}

# Test 2: ISO bootability
test_iso_bootability() {
    start_test "ISO bootability and GRUB configuration"
    
    # Mount ISO to check contents
    local mount_point="/tmp/synos-iso-test-$$"
    mkdir -p "$mount_point"
    
    if sudo mount -o loop "$ISO_FILE" "$mount_point" 2>/dev/null; then
        # Check for essential boot files
        if [[ -f "$mount_point/boot/syn_kernel.bin" ]]; then
            pass_test "Kernel binary present"
        else
            fail_test "Kernel binary missing"
        fi
        
        if [[ -f "$mount_point/boot/grub/grub.cfg" ]]; then
            pass_test "GRUB configuration present"
            
            # Validate GRUB config syntax
            if grep -q "menuentry" "$mount_point/boot/grub/grub.cfg"; then
                pass_test "GRUB menu entries found"
            else
                fail_test "No GRUB menu entries found"
            fi
        else
            fail_test "GRUB configuration missing"
        fi
        
        # Check for consciousness integration
        if [[ -d "$mount_point/opt/synos" ]]; then
            pass_test "Consciousness engine integration present"
        else
            fail_test "Consciousness engine integration missing"
        fi
        
        sudo umount "$mount_point"
        rmdir "$mount_point"
    else
        fail_test "Unable to mount ISO for inspection"
    fi
}

# Test 3: QEMU boot test
test_qemu_boot() {
    start_test "QEMU virtual machine boot test"
    
    if ! command -v qemu-system-x86_64 &> /dev/null; then
        log_warning "QEMU not available, skipping boot test"
        return
    fi
    
    log_info "Starting QEMU boot test (timeout: ${QEMU_TIMEOUT}s)..."
    
    # Create QEMU test script
    local qemu_test_script="/tmp/qemu-test-$$.sh"
    cat > "$qemu_test_script" << EOF
#!/bin/bash
timeout $QEMU_TIMEOUT qemu-system-x86_64 \\
    -cdrom "$ISO_FILE" \\
    -m 512M \\
    -display none \\
    -serial file:$TEST_RESULTS_DIR/qemu-boot-log.txt \\
    -no-reboot \\
    -no-shutdown \\
    -boot d \\
    -cpu qemu64 \\
    -enable-kvm 2>/dev/null || \\
timeout $QEMU_TIMEOUT qemu-system-x86_64 \\
    -cdrom "$ISO_FILE" \\
    -m 512M \\
    -display none \\
    -serial file:$TEST_RESULTS_DIR/qemu-boot-log.txt \\
    -no-reboot \\
    -no-shutdown \\
    -boot d \\
    -cpu qemu64
EOF
    
    chmod +x "$qemu_test_script"
    
    # Run QEMU test
    if "$qemu_test_script" >/dev/null 2>&1; then
        pass_test "QEMU boot initiated successfully"
        
        # Check boot log for expected messages
        if [[ -f "$TEST_RESULTS_DIR/qemu-boot-log.txt" ]]; then
            if grep -q "Syn_OS" "$TEST_RESULTS_DIR/qemu-boot-log.txt"; then
                pass_test "Syn_OS kernel messages detected"
            else
                fail_test "No Syn_OS kernel messages in boot log"
            fi
            
            if grep -q "Consciousness" "$TEST_RESULTS_DIR/qemu-boot-log.txt"; then
                pass_test "Consciousness engine messages detected"
            else
                log_warning "No consciousness engine messages detected"
            fi
        fi
    else
        fail_test "QEMU boot test failed"
    fi
    
    rm -f "$qemu_test_script"
}

# Test 4: Kernel compliance
test_kernel_compliance() {
    start_test "Kernel multiboot compliance"
    
    # Extract kernel from ISO
    local mount_point="/tmp/synos-kernel-test-$$"
    mkdir -p "$mount_point"
    
    if sudo mount -o loop "$ISO_FILE" "$mount_point" 2>/dev/null; then
        local kernel_file="$mount_point/boot/syn_kernel.bin"
        
        if [[ -f "$kernel_file" ]]; then
            # Test multiboot compliance
            if command -v grub-file &> /dev/null; then
                if grub-file --is-x86-multiboot "$kernel_file"; then
                    pass_test "Kernel is multiboot compliant"
                else
                    fail_test "Kernel is not multiboot compliant"
                fi
            else
                log_warning "grub-file not available, skipping multiboot test"
            fi
            
            # Check kernel size
            local kernel_size=$(stat -c%s "$kernel_file")
            if [[ $kernel_size -gt 1024 && $kernel_size -lt 67108864 ]]; then  # 1KB to
# Check kernel size
            local kernel_size=$(stat -c%s "$kernel_file")
            if [[ $kernel_size -gt 1024 && $kernel_size -lt 67108864 ]]; then  # 1KB to 64MB
                pass_test "Kernel size is reasonable ($(du -h "$kernel_file" | cut -f1))"
            else
                fail_test "Kernel size is unreasonable ($(du -h "$kernel_file" | cut -f1))"
            fi
        else
            fail_test "Kernel file not found in ISO"
        fi
        
        sudo umount "$mount_point"
        rmdir "$mount_point"
    else
        fail_test "Unable to mount ISO for kernel inspection"
    fi
}

# Test 5: Consciousness integration
test_consciousness_integration() {
    start_test "Consciousness engine integration validation"
    
    local mount_point="/tmp/synos-consciousness-test-$$"
    mkdir -p "$mount_point"
    
    if sudo mount -o loop "$ISO_FILE" "$mount_point" 2>/dev/null; then
        # Check consciousness engine files
        if [[ -d "$mount_point/opt/synos/consciousness_v2" ]]; then
            pass_test "Consciousness engine v2 directory present"
            
            # Check for key consciousness files
            local key_files=(
                "components/consciousness_core.py"
                "components/event_bus.py"
                "bridges/nats_bridge.py"
                "main_nats_integration.py"
            )
            
            for file in "${key_files[@]}"; do
                if [[ -f "$mount_point/opt/synos/consciousness_v2/$file" ]]; then
                    pass_test "Consciousness file present: $file"
                else
                    fail_test "Consciousness file missing: $file"
                fi
            done
        else
            fail_test "Consciousness engine directory missing"
        fi
        
        # Check startup script
        if [[ -f "$mount_point/opt/synos/start-consciousness.sh" ]]; then
            pass_test "Consciousness startup script present"
            
            if [[ -x "$mount_point/opt/synos/start-consciousness.sh" ]]; then
                pass_test "Consciousness startup script is executable"
            else
                fail_test "Consciousness startup script is not executable"
            fi
        else
            fail_test "Consciousness startup script missing"
        fi
        
        sudo umount "$mount_point"
        rmdir "$mount_point"
    else
        fail_test "Unable to mount ISO for consciousness inspection"
    fi
}

# Test 6: Security framework validation
test_security_framework() {
    start_test "Security framework validation"
    
    # This would test security components if they were included in the ISO
    # For now, we'll check for basic security indicators
    
    local mount_point="/tmp/synos-security-test-$$"
    mkdir -p "$mount_point"
    
    if sudo mount -o loop "$ISO_FILE" "$mount_point" 2>/dev/null; then
        # Check for security-related files
        if find "$mount_point" -name "*security*" -type f | grep -q .; then
            pass_test "Security-related files found in ISO"
        else
            log_warning "No security-related files found in ISO"
        fi
        
        # Check GRUB configuration for security options
        if [[ -f "$mount_point/boot/grub/grub.cfg" ]]; then
            if grep -q -i "security\|neural\|consciousness" "$mount_point/boot/grub/grub.cfg"; then
                pass_test "Security/AI options found in GRUB menu"
            else
                log_warning "No security/AI options found in GRUB menu"
            fi
        fi
        
        sudo umount "$mount_point"
        rmdir "$mount_point"
    else
        fail_test "Unable to mount ISO for security inspection"
    fi
}

# Test 7: Educational framework validation
test_educational_framework() {
    start_test "Educational framework validation"
    
    # Check for educational content and documentation
    local mount_point="/tmp/synos-edu-test-$$"
    mkdir -p "$mount_point"
    
    if sudo mount -o loop "$ISO_FILE" "$mount_point" 2>/dev/null; then
        # Look for educational content
        if find "$mount_point" -name "*README*" -o -name "*doc*" -o -name "*edu*" | grep -q .; then
            pass_test "Educational documentation found"
        else
            log_warning "No educational documentation found"
        fi
        
        # Check GRUB menu for educational options
        if [[ -f "$mount_point/boot/grub/grub.cfg" ]]; then
            if grep -q -i "educational\|demo\|learning" "$mount_point/boot/grub/grub.cfg"; then
                pass_test "Educational options found in GRUB menu"
            else
                log_warning "No educational options found in GRUB menu"
            fi
        fi
        
        sudo umount "$mount_point"
        rmdir "$mount_point"
    else
        fail_test "Unable to mount ISO for educational inspection"
    fi
}

# Generate comprehensive test report
generate_test_report() {
    log_info "Generating comprehensive test report..."
    
    local report_file="$TEST_RESULTS_DIR/validation-report-${TEST_DATE}.txt"
    
    cat >> "$report_file" << EOF

Test Results Summary
====================

Total Tests: $TOTAL_TESTS
Passed: $PASSED_TESTS
Failed: $FAILED_TESTS
Success Rate: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%

Test Status: $(if [[ $FAILED_TESTS -eq 0 ]]; then echo "✅ ALL TESTS PASSED"; else echo "❌ SOME TESTS FAILED"; fi)

Detailed Results
================

EOF
    
    # Add QEMU boot log if available
    if [[ -f "$TEST_RESULTS_DIR/qemu-boot-log.txt" ]]; then
        cat >> "$report_file" << EOF

QEMU Boot Log
=============

$(cat "$TEST_RESULTS_DIR/qemu-boot-log.txt")

EOF
    fi
    
    cat >> "$report_file" << EOF

Recommendations
===============

EOF
    
    if [[ $FAILED_TESTS -eq 0 ]]; then
        cat >> "$report_file" << EOF
🎉 Excellent! All tests passed. The ISO is ready for deployment.

Next Steps:
1. Deploy ISO to physical hardware for final testing
2. Conduct user acceptance testing
3. Prepare for educational deployment
4. Document any hardware-specific requirements

EOF
    else
        cat >> "$report_file" << EOF
⚠️  Some tests failed. Please review and address the following:

1. Fix any missing files or components
2. Verify kernel compilation and linking
3. Test consciousness engine integration
4. Validate GRUB configuration
5. Re-run validation after fixes

EOF
    fi
    
    cat >> "$report_file" << EOF

Test Environment
================

Test Date: $(date -R)
Test Framework Version: $SCRIPT_VERSION
Operating System: $(uname -sr)
Available Memory: $(free -h | grep '^Mem:' | awk '{print $2}')
Available Disk Space: $(df -h . | tail -1 | awk '{print $4}')

ISO Information
===============

File: $(basename "$ISO_FILE")
Size: $(du -h "$ISO_FILE" | cut -f1)
SHA256: $(sha256sum "$ISO_FILE" | cut -d' ' -f1)
Creation Date: $(stat -c %y "$ISO_FILE")

EOF
    
    log_success "Test report generated: $report_file"
}

# Main test execution
main() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                 SYN_OS ISO VALIDATION SUITE                  ║${NC}"
    echo -e "${PURPLE}║          Comprehensive Testing Framework v${SCRIPT_VERSION}              ║${NC}"
    echo -e "${PURPLE}║                                                              ║${NC}"
    echo -e "${PURPLE}║  🧪 Integrity Tests    🚀 Boot Validation                   ║${NC}"
    echo -e "${PURPLE}║  🧠 AI Integration     🔒 Security Framework                ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    log_info "Starting Syn_OS ISO validation suite..."
    
    # Setup and run tests
    setup_test_environment
    test_iso_integrity
    test_iso_bootability
    test_qemu_boot
    test_kernel_compliance
    test_consciousness_integration
    test_security_framework
    test_educational_framework
    generate_test_report
    
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    VALIDATION COMPLETE                      ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    log_info "Validation Results:"
    log_info "Total Tests: $TOTAL_TESTS"
    log_success "Passed: $PASSED_TESTS"
    if [[ $FAILED_TESTS -gt 0 ]]; then
        log_error "Failed: $FAILED_TESTS"
    fi
    log_info "Success Rate: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"
    
    echo ""
    if [[ $FAILED_TESTS -eq 0 ]]; then
        echo -e "${GREEN}🎉 ALL TESTS PASSED! ISO is ready for deployment.${NC}"
    else
        echo -e "${YELLOW}⚠️  Some tests failed. Please review the test report.${NC}"
    fi
    
    log_info "Test report: $TEST_RESULTS_DIR/validation-report-${TEST_DATE}.txt"
    
    # Return appropriate exit code
    if [[ $FAILED_TESTS -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Syn_OS ISO Validation Suite v${SCRIPT_VERSION}"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help      Show this help message"
        echo ""
        echo "This script validates a built Syn_OS ISO image by running"
        echo "comprehensive tests including:"
        echo "  - File integrity and checksums"
        echo "  - ISO bootability and GRUB configuration"
        echo "  - QEMU virtual machine boot test"
        echo "  - Kernel multiboot compliance"
        echo "  - Consciousness engine integration"
        echo "  - Security framework validation"
        echo "  - Educational framework validation"
        echo ""
        echo "The script automatically finds the most recent ISO in the"
        echo "build directory and generates a detailed test report."
        echo ""
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac