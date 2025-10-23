#!/usr/bin/env bash
################################################################################
# SynOS Kernel-Only Builder - Fast Testing ISO
# 
# Creates a minimal bootable ISO containing only the kernel for quick testing.
# Ideal for kernel development iterations and boot testing.
#
# Usage:
#   ./scripts/build-kernel-only.sh [OPTIONS]
#
# Options:
#   --output DIR      Specify output directory (default: build/)
#   --target TRIPLE   Kernel target (default: x86_64-unknown-none)
#   --debug           Build with debug symbols
#   --help            Show this help message
#
# Features:
#   - Fast builds (typically 2-5 minutes)
#   - Minimal ISO size (~50MB)
#   - Kernel + GRUB only
#   - Auto-testing with QEMU (optional)
#
# Exit Codes:
#   0 - Success
#   1 - Build failure
#   2 - Dependency missing
#
################################################################################

set -euo pipefail

# Source shared library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/build-common.sh"

################################################################################
# Configuration
################################################################################

OUTPUT_BASE=""
KERNEL_TARGET="${KERNEL_TARGET:-x86_64-unknown-none}"
BUILD_TYPE="${BUILD_TYPE:-release}"
RUN_QEMU=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --output)
            OUTPUT_BASE="$2"
            shift 2
            ;;
        --target)
            KERNEL_TARGET="$2"
            shift 2
            ;;
        --debug)
            BUILD_TYPE="debug"
            shift
            ;;
        --test-qemu)
            RUN_QEMU=true
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

# Initialize build environment (sets PROJECT_ROOT and other variables)
init_build_env

if [[ -n "$OUTPUT_BASE" ]]; then
    BUILD_DIR="$OUTPUT_BASE"
fi

################################################################################
# Main Build Process
################################################################################

main() {
    local start_time
    start_time=$(date +%s)
    
    print_banner "SynOS Kernel-Only Builder"
    
    # Initialize
    section "Initializing"
    init_build_env
    
    # Quick checks
    check_not_root
    check_required_tools cargo rustc grub-mkrescue
    check_disk_space 5  # 5GB minimum for kernel-only build
    
    info "Configuration:"
    info "  Target:     ${KERNEL_TARGET}"
    info "  Build Type: ${BUILD_TYPE}"
    info "  Output:     ${BUILD_DIR}"
    
    setup_cleanup
    
    # Build kernel only
    section "Building Kernel"
    build_kernel "${KERNEL_TARGET}"
    KERNEL_BINARY=$(find_kernel_binary)
    success "Kernel: ${KERNEL_BINARY}"
    
    # Setup minimal ISO structure
    section "Creating Minimal ISO Structure"
    mkdir -p "${ISOROOT_DIR}/boot/grub"
    
    # Copy kernel
    cp "${KERNEL_BINARY}" "${ISOROOT_DIR}/boot/kernel.bin"
    info "Kernel size: $(du -h "${KERNEL_BINARY}" | cut -f1)"
    
    # Create minimal GRUB config
    info "Creating GRUB config..."
    cat > "${ISOROOT_DIR}/boot/grub/grub.cfg" <<'EOF'
set timeout=3
set default=0

menuentry "SynOS Kernel Test" {
    multiboot2 /boot/kernel.bin
    boot
}

menuentry "SynOS Kernel Test (Debug)" {
    multiboot2 /boot/kernel.bin debug
    boot
}
EOF
    
    # Generate ISO
    section "Generating ISO"
    local timestamp
    timestamp=$(date +%Y%m%d-%H%M%S)
    local version="${SYNOS_VERSION:-v1.0.0}"
    OUTPUT_ISO="${BUILD_DIR}/SynOS-${version}-KernelTest-${timestamp}.iso"
    
    generate_iso "${ISOROOT_DIR}" "${OUTPUT_ISO}"
    
    # Summary
    section "Build Complete!"
    success "ISO: ${OUTPUT_ISO}"
    info "Size: $(du -h "${OUTPUT_ISO}" | cut -f1)"
    info "Time: $(elapsed_time "$start_time")"
    
    # Optional QEMU test
    if [[ "$RUN_QEMU" == true ]]; then
        section "Testing in QEMU"
        if command -v qemu-system-x86_64 &>/dev/null; then
            info "Starting QEMU (press Ctrl+C to exit)..."
            qemu-system-x86_64 \
                -cdrom "${OUTPUT_ISO}" \
                -m 2G \
                -enable-kvm \
                -serial stdio \
                -display none \
                || true
        else
            warning "QEMU not installed, skipping test"
        fi
    else
        echo ""
        info "Test with: qemu-system-x86_64 -cdrom ${OUTPUT_ISO} -m 2G"
    fi
    
    return 0
}

################################################################################
# Execute
################################################################################

main "$@"
