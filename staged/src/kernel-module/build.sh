#!/bin/bash

# SynOS Phase 4.2: Consciousness Monitoring Module Build Script
# Advanced Logging and Debugging Infrastructure

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULE_NAME="synos_consciousness"
VERSION="4.2.0"

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

# Banner
print_banner() {
    echo "=================================================================="
    echo "  SynOS Phase 4.2: Consciousness Monitoring Kernel Module"
    echo "  Advanced Logging and Debugging Infrastructure"
    echo "  Version: $VERSION"
    echo "=================================================================="
    echo ""
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if running as root for installation
    if [[ $EUID -eq 0 ]] && [[ "$1" != "build" ]]; then
        log_warning "Running as root. This is required for module installation."
    fi
    
    # Check kernel headers
    KERNEL_VERSION=$(uname -r)
    KERNEL_HEADERS="/lib/modules/$KERNEL_VERSION/build"
    
    if [ ! -d "$KERNEL_HEADERS" ]; then
        log_error "Kernel headers not found for kernel $KERNEL_VERSION"
        log_error "Please install kernel headers:"
        log_error "  Ubuntu/Debian: sudo apt install linux-headers-\$(uname -r)"
        log_error "  CentOS/RHEL: sudo yum install kernel-devel"
        log_error "  Fedora: sudo dnf install kernel-devel"
        exit 1
    fi
    
    # Check build tools
    if ! command -v make &> /dev/null; then
        log_error "make command not found. Please install build-essential."
        exit 1
    fi
    
    if ! command -v gcc &> /dev/null; then
        log_error "gcc compiler not found. Please install build tools."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
    echo "  Kernel: $KERNEL_VERSION"
    echo "  Headers: $KERNEL_HEADERS"
    echo ""
}

# Build the module
build_module() {
    log_info "Building SynOS consciousness monitoring kernel module..."
    
    cd "$SCRIPT_DIR"
    
    # Clean previous build
    make clean > /dev/null 2>&1 || true
    
    # Build module
    if make all; then
        log_success "Module built successfully: ${MODULE_NAME}.ko"
        
        # Show module info
        if [ -f "${MODULE_NAME}.ko" ]; then
            echo ""
            log_info "Module information:"
            modinfo "${MODULE_NAME}.ko" | grep -E "(filename|version|description|author|license)"
        fi
    else
        log_error "Module build failed"
        exit 1
    fi
}

# Install the module
install_module() {
    log_info "Installing SynOS consciousness monitoring module..."
    
    if [ ! -f "${MODULE_NAME}.ko" ]; then
        log_error "Module file not found. Build first with: $0 build"
        exit 1
    fi
    
    # Remove existing module if loaded
    if lsmod | grep -q "$MODULE_NAME"; then
        log_info "Removing existing module..."
        if ! rmmod "$MODULE_NAME"; then
            log_error "Failed to remove existing module"
            exit 1
        fi
    fi
    
    # Install new module
    if insmod "${MODULE_NAME}.ko"; then
        log_success "Module installed successfully"
        
        # Verify installation
        if lsmod | grep -q "$MODULE_NAME"; then
            log_success "Module is loaded and running"
            echo "  Device: /dev/synos"
            echo "  Proc: /proc/synos_consciousness"
        else
            log_error "Module installation verification failed"
            exit 1
        fi
        
        # Show recent kernel messages
        echo ""
        log_info "Recent kernel messages:"
        dmesg | tail -10 | grep -i synos || echo "  (No SynOS messages in recent dmesg)"
        
    else
        log_error "Module installation failed"
        exit 1
    fi
}

# Remove the module
remove_module() {
    log_info "Removing SynOS consciousness monitoring module..."
    
    if lsmod | grep -q "$MODULE_NAME"; then
        if rmmod "$MODULE_NAME"; then
            log_success "Module removed successfully"
        else
            log_error "Failed to remove module"
            exit 1
        fi
    else
        log_warning "Module is not currently loaded"
    fi
}

# Test module functionality
test_module() {
    log_info "Testing SynOS consciousness monitoring module..."
    
    if ! lsmod | grep -q "$MODULE_NAME"; then
        log_error "Module is not loaded. Install first with: $0 install"
        exit 1
    fi
    
    echo ""
    log_info "Test 1: Reading device status..."
    if [ -c "/dev/synos" ]; then
        cat /dev/synos
    else
        log_error "Device /dev/synos not found"
        exit 1
    fi
    
    echo ""
    log_info "Test 2: Reading proc interface..."
    if [ -f "/proc/synos_consciousness" ]; then
        cat /proc/synos_consciousness
    else
        log_error "Proc interface /proc/synos_consciousness not found"
        exit 1
    fi
    
    echo ""
    log_info "Test 3: Testing component registration..."
    echo "REGISTER:test_component_$(date +%s)" > /dev/synos
    
    echo ""
    log_info "Test 4: Testing logging..."
    echo "LOG:Test message from build script at $(date)" > /dev/synos
    
    echo ""
    log_info "Test 5: Testing events..."
    echo "EVENT:Test event from build script at $(date)" > /dev/synos
    
    echo ""
    log_info "Test 6: Final status check..."
    cat /proc/synos_consciousness
    
    echo ""
    log_success "All tests completed successfully!"
}

# Monitor kernel messages
monitor_module() {
    log_info "Monitoring SynOS kernel messages (Ctrl+C to exit)..."
    echo ""
    
    if ! lsmod | grep -q "$MODULE_NAME"; then
        log_warning "Module is not loaded"
    fi
    
    # Clear dmesg and start monitoring
    dmesg -C 2>/dev/null || true
    dmesg -w | grep --line-buffered -i synos
}

# Show module status
show_status() {
    echo ""
    log_info "SynOS Phase 4.2 Module Status:"
    echo ""
    
    # Check if module is loaded
    if lsmod | grep -q "$MODULE_NAME"; then
        log_success "Module Status: LOADED"
        echo "  Module: $MODULE_NAME"
        lsmod | grep "$MODULE_NAME"
        
        # Check interfaces
        if [ -c "/dev/synos" ]; then
            log_success "Device Interface: AVAILABLE (/dev/synos)"
        else
            log_error "Device Interface: NOT AVAILABLE"
        fi
        
        if [ -f "/proc/synos_consciousness" ]; then
            log_success "Proc Interface: AVAILABLE (/proc/synos_consciousness)"
        else
            log_error "Proc Interface: NOT AVAILABLE"
        fi
        
    else
        log_warning "Module Status: NOT LOADED"
    fi
    
    # Check if module file exists
    if [ -f "${SCRIPT_DIR}/${MODULE_NAME}.ko" ]; then
        log_info "Module File: EXISTS (${MODULE_NAME}.ko)"
        echo "  Size: $(ls -lh "${MODULE_NAME}.ko" | awk '{print $5}')"
        echo "  Modified: $(stat -c %y "${MODULE_NAME}.ko" | cut -d'.' -f1)"
    else
        log_warning "Module File: NOT BUILT"
    fi
    
    echo ""
}

# Show help
show_help() {
    echo "Usage: $0 {build|install|remove|test|monitor|status|reload|help}"
    echo ""
    echo "Commands:"
    echo "  build    - Build the kernel module"
    echo "  install  - Install the module (requires root)"
    echo "  remove   - Remove the installed module (requires root)"
    echo "  test     - Test module functionality (requires root)"
    echo "  monitor  - Monitor kernel messages from SynOS"
    echo "  status   - Show module status and information"
    echo "  reload   - Remove and reinstall the module (requires root)"
    echo "  help     - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build                    # Build module"
    echo "  sudo $0 install             # Install module"
    echo "  sudo $0 test               # Test functionality"
    echo "  $0 monitor                 # Monitor kernel messages"
    echo "  sudo $0 reload             # Reload module"
    echo ""
    echo "Phase 4.2 Features:"
    echo "  ✓ Consciousness component monitoring"
    echo "  ✓ Advanced logging (9 levels, 11 categories)"
    echo "  ✓ Debug infrastructure and system analysis"
    echo "  ✓ Continuous monitoring thread"
    echo "  ✓ Device interface (/dev/synos)"
    echo "  ✓ Proc interface (/proc/synos_consciousness)"
    echo "  ✓ IOCTL commands for control"
    echo ""
}

# Main script logic
main() {
    cd "$SCRIPT_DIR"
    
    case "${1:-help}" in
        build)
            print_banner
            check_prerequisites build
            build_module
            show_status
            ;;
        install)
            print_banner
            check_prerequisites install
            build_module
            install_module
            show_status
            ;;
        remove)
            print_banner
            remove_module
            show_status
            ;;
        test)
            print_banner
            test_module
            ;;
        monitor)
            monitor_module
            ;;
        status)
            show_status
            ;;
        reload)
            print_banner
            check_prerequisites install
            remove_module
            build_module
            install_module
            show_status
            ;;
        help|--help|-h)
            print_banner
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
