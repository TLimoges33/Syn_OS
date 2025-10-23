#!/usr/bin/env bash
################################################################################
# SynOS ISO Builder - Production ISO Generation
# 
# This is the primary build script for creating SynOS bootable ISO images.
# It uses the shared build-common.sh library for all core functionality.
#
# Usage:
#   ./scripts/build-iso.sh [OPTIONS]
#
# Options:
#   --quick           Skip workspace binaries (kernel only)
#   --no-source       Exclude source code archive
#   --no-checksums    Skip checksum generation
#   --output DIR      Specify output directory (default: build/)
#   --kernel-only     Build minimal kernel-only ISO
#   --help            Show this help message
#
# Environment Variables:
#   SYNOS_VERSION     Override version (default: from Cargo.toml)
#   BUILD_TYPE        Build profile: release|debug (default: release)
#   KERNEL_TARGET     Kernel target triple (default: x86_64-unknown-none)
#
# Exit Codes:
#   0 - Success
#   1 - Build failure
#   2 - Dependency missing
#   3 - Insufficient disk space
#
################################################################################

set -euo pipefail

# Source shared library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/build-common.sh"

################################################################################
# Configuration
################################################################################

# Parse command line arguments
QUICK_BUILD=false
INCLUDE_SOURCE=true
GENERATE_CHECKSUMS=true
OUTPUT_BASE=""
KERNEL_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_BUILD=true
            shift
            ;;
        --no-source)
            INCLUDE_SOURCE=false
            shift
            ;;
        --no-checksums)
            GENERATE_CHECKSUMS=false
            shift
            ;;
        --output)
            OUTPUT_BASE="$2"
            shift 2
            ;;
        --kernel-only)
            KERNEL_ONLY=true
            QUICK_BUILD=true
            INCLUDE_SOURCE=false
            shift
            ;;
        --help)
            grep "^#" "$0" | grep -v "^#!/" | sed 's/^# \?//'
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Initialize build environment (sets PROJECT_ROOT and other variables)
init_build_env

# Set output directory
if [[ -n "$OUTPUT_BASE" ]]; then
    BUILD_DIR="$OUTPUT_BASE"
fi

################################################################################
# Main Build Process
################################################################################

main() {
    local start_time
    start_time=$(date +%s)
    
    print_banner "SynOS ISO Builder v1.0"
    
    # Initialize build environment
    section "Initializing Build Environment"
    init_build_env
    
    # Pre-flight checks
    section "Pre-flight Checks"
    check_not_root
    check_required_tools cargo rustc grub-mkrescue xorriso
    check_disk_space 5  # 5GB minimum for ISO build
    
    # Display configuration
    info "Build Configuration:"
    info "  Version:        ${SYNOS_VERSION}"
    info "  Build Type:     ${BUILD_TYPE}"
    info "  Kernel Target:  ${KERNEL_TARGET}"
    info "  Quick Build:    ${QUICK_BUILD}"
    info "  Include Source: ${INCLUDE_SOURCE}"
    info "  Kernel Only:    ${KERNEL_ONLY}"
    info "  Output Dir:     ${BUILD_DIR}"
    
    # Setup cleanup handler
    setup_cleanup
    
    # Phase 1: Build Kernel
    section "Phase 1: Building Kernel"
    build_kernel "${KERNEL_TARGET}"
    KERNEL_BINARY=$(find_kernel_binary)
    success "Kernel built: ${KERNEL_BINARY}"
    
    # Phase 2: Build Workspace (unless quick/kernel-only)
    if [[ "$QUICK_BUILD" == false ]]; then
        section "Phase 2: Building Workspace Binaries"
        build_workspace
        
        section "Phase 3: Collecting Binaries"
        mkdir -p "${ISOROOT_DIR}/boot/binaries"
        collect_binaries "${ISOROOT_DIR}/boot/binaries" "${BUILD_TYPE}"
        success "Collected binaries to ${ISOROOT_DIR}/boot/binaries/"
    else
        info "Skipping workspace build (quick/kernel-only mode)"
    fi
    
    # Phase 3/4: Setup ISO structure
    section "Phase 4: Setting Up ISO Structure"
    
    # Create ISO directories
    mkdir -p "${ISOROOT_DIR}"/{boot/{grub,binaries},docs,src}
    
    # Copy kernel
    info "Copying kernel..."
    cp "${KERNEL_BINARY}" "${ISOROOT_DIR}/boot/kernel.bin"
    
    # Create GRUB configuration
    info "Generating GRUB configuration..."
    create_grub_config "${ISOROOT_DIR}/boot/grub/grub.cfg"
    
    # Copy documentation
    section "Phase 5: Copying Documentation"
    copy_documentation
    
    # Create source archive (optional)
    if [[ "$INCLUDE_SOURCE" == true ]]; then
        section "Phase 6: Creating Source Archive"
        create_source_archive
    else
        info "Skipping source archive"
    fi
    
    # Phase 6/7: Generate ISO
    section "Phase 7: Generating ISO Image"
    
    # Determine ISO filename
    local timestamp
    timestamp=$(date +%Y%m%d-%H%M%S)
    
    if [[ "$KERNEL_ONLY" == true ]]; then
        OUTPUT_ISO="${BUILD_DIR}/SynOS-${SYNOS_VERSION}-Kernel-${timestamp}.iso"
    elif [[ "$QUICK_BUILD" == true ]]; then
        OUTPUT_ISO="${BUILD_DIR}/SynOS-${SYNOS_VERSION}-Quick-${timestamp}.iso"
    else
        OUTPUT_ISO="${BUILD_DIR}/SynOS-${SYNOS_VERSION}-Complete-${timestamp}.iso"
    fi
    
    generate_iso "${ISOROOT_DIR}" "${OUTPUT_ISO}"
    
    # Phase 7/8: Generate checksums
    if [[ "$GENERATE_CHECKSUMS" == true ]]; then
        section "Phase 8: Generating Checksums"
        generate_checksums "${OUTPUT_ISO}"
    else
        info "Skipping checksum generation"
    fi
    
    # Verify ISO
    section "Phase 9: Verifying ISO"
    verify_iso "${OUTPUT_ISO}"
    
    # Final summary
    local end_time elapsed
    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    
    section "Build Complete!"
    success "ISO created: ${OUTPUT_ISO}"
    info "ISO size: $(human_size "${OUTPUT_ISO}")"
    info "Build time: $(elapsed_time $elapsed)"
    
    if [[ "$GENERATE_CHECKSUMS" == true ]]; then
        info "Checksums:"
        info "  MD5:    ${OUTPUT_ISO}.md5"
        info "  SHA256: ${OUTPUT_ISO}.sha256"
    fi
    
    echo ""
    info "Next steps:"
    info "  1. Test ISO:  qemu-system-x86_64 -cdrom ${OUTPUT_ISO} -m 2G"
    info "  2. Burn ISO:  dd if=${OUTPUT_ISO} of=/dev/sdX bs=4M status=progress"
    info "  3. Verify:    md5sum -c ${OUTPUT_ISO}.md5"
    
    return 0
}

################################################################################
# Execute
################################################################################

# Run main function
main "$@"
