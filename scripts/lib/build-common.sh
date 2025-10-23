#!/bin/bash

################################################################################
# SynOS Build Common Library
# Shared functions and utilities for all build scripts
# Date: October 23, 2025
################################################################################

# Prevent multiple inclusion
if [ -n "${SYNOS_BUILD_COMMON_LOADED:-}" ]; then
    return 0
fi
SYNOS_BUILD_COMMON_LOADED=1

################################################################################
# Color Definitions
################################################################################

export RED='\033[0;31m'
export GREEN='\033[0;32m'
export YELLOW='\033[1;33m'
export BLUE='\033[0;34m'
export PURPLE='\033[0;35m'
export CYAN='\033[0;36m'
export WHITE='\033[0;37m'
export BOLD='\033[1m'
export NC='\033[0m'

################################################################################
# Logging Functions
################################################################################

# Log with timestamp
log() {
    local msg="$*"
    echo -e "${CYAN}[$(date '+%H:%M:%S')]${NC} ${msg}" | tee -a "${BUILD_LOG:-/dev/null}"
}

# Success message
success() {
    local msg="$*"
    echo -e "${GREEN}✓${NC} ${msg}" | tee -a "${BUILD_LOG:-/dev/null}"
}

# Error message
error() {
    local msg="$*"
    echo -e "${RED}✗${NC} ${msg}" | tee -a "${BUILD_LOG:-/dev/null}"
}

# Warning message
warning() {
    local msg="$*"
    echo -e "${YELLOW}⚠${NC} ${msg}" | tee -a "${BUILD_LOG:-/dev/null}"
}

# Info message
info() {
    local msg="$*"
    echo -e "${BLUE}ℹ${NC} ${msg}" | tee -a "${BUILD_LOG:-/dev/null}"
}

# Section header
section() {
    local title="$*"
    echo | tee -a "${BUILD_LOG:-/dev/null}"
    echo -e "${BOLD}${PURPLE}═══════════════════════════════════════════════════════${NC}" | tee -a "${BUILD_LOG:-/dev/null}"
    echo -e "${BOLD}${PURPLE}  ${title}${NC}" | tee -a "${BUILD_LOG:-/dev/null}"
    echo -e "${BOLD}${PURPLE}═══════════════════════════════════════════════════════${NC}" | tee -a "${BUILD_LOG:-/dev/null}"
    echo | tee -a "${BUILD_LOG:-/dev/null}"
}

################################################################################
# Environment Setup
################################################################################

# Initialize build environment
init_build_env() {
    # Determine project root
    if [ -z "${PROJECT_ROOT:-}" ]; then
        export PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    fi
    
    # Set default paths
    export BUILD_DIR="${BUILD_DIR:-${PROJECT_ROOT}/build}"
    export ISO_DIR="${ISO_DIR:-${BUILD_DIR}/iso}"
    export ISOROOT_DIR="${ISOROOT_DIR:-${BUILD_DIR}/isoroot}"
    export LOGS_DIR="${LOGS_DIR:-${BUILD_DIR}/logs}"
    export TIMESTAMP="${TIMESTAMP:-$(date '+%Y%m%d-%H%M%S')}"
    
    # Set version from Cargo.toml if not already set
    if [ -z "${SYNOS_VERSION:-}" ]; then
        if [ -f "${PROJECT_ROOT}/Cargo.toml" ]; then
            export SYNOS_VERSION=$(grep -m1 '^version = ' "${PROJECT_ROOT}/Cargo.toml" | cut -d'"' -f2 | sed 's/^/v/')
        else
            export SYNOS_VERSION="v1.0.0"
        fi
    fi
    
    # Set build configuration defaults
    export BUILD_TYPE="${BUILD_TYPE:-release}"
    export KERNEL_TARGET="${KERNEL_TARGET:-x86_64-unknown-none}"
    
    # Create log file if not set
    if [ -z "${BUILD_LOG:-}" ]; then
        export BUILD_LOG="${LOGS_DIR}/iso-build/build-${TIMESTAMP}.log"
        mkdir -p "$(dirname "${BUILD_LOG}")"
    fi
    
    log "Build environment initialized"
    log "Project root: ${PROJECT_ROOT}"
    log "Build directory: ${BUILD_DIR}"
    log "Log file: ${BUILD_LOG}"
}

################################################################################
# Dependency Checking
################################################################################

# Check if running as root
check_not_root() {
    if [ "$EUID" -eq 0 ]; then
        error "Do not run this script as root!"
        error "Run as regular user with sudo privileges"
        return 1
    fi
    return 0
}

# Check for required tools
check_required_tools() {
    local tools=("$@")
    local missing=()
    
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &>/dev/null; then
            missing+=("$tool")
        fi
    done
    
    if [ ${#missing[@]} -ne 0 ]; then
        error "Missing required tools: ${missing[*]}"
        return 1
    fi
    
    return 0
}

# Check disk space (GB)
check_disk_space() {
    local required_gb="${1:-10}"
    local available_gb=$(df -BG "${PROJECT_ROOT}" | awk 'NR==2 {print $4}' | sed 's/G//')
    
    if [ "$available_gb" -lt "$required_gb" ]; then
        error "Insufficient disk space: ${available_gb}GB (need at least ${required_gb}GB)"
        return 1
    fi
    
    success "Sufficient disk space: ${available_gb}GB available"
    return 0
}

################################################################################
# Rust Build Functions
################################################################################

# Build Rust kernel
build_kernel() {
    local target="${1:-x86_64-unknown-none}"
    local manifest="${2:-src/kernel/Cargo.toml}"
    
    section "Building Rust Kernel"
    
    log "Target: ${target}"
    log "Manifest: ${manifest}"
    
    # Add target if not installed
    if ! rustup target list | grep "${target} (installed)" &>/dev/null; then
        log "Adding Rust target: ${target}"
        rustup target add "${target}" | tee -a "${BUILD_LOG}"
    fi
    
    # Build kernel
    log "Building kernel (this may take a few minutes)..."
    if cargo build --manifest-path="${manifest}" \
        --target="${target}" \
        --release \
        2>&1 | tee -a "${BUILD_LOG}" | grep -E "(Compiling|Finished)"; then
        success "Kernel compilation completed"
        return 0
    else
        error "Kernel compilation failed"
        info "Check log: ${BUILD_LOG}"
        return 1
    fi
}

# Locate kernel binary
find_kernel_binary() {
    local target="${1:-x86_64-unknown-none}"
    local kernel_binary=""
    
    local possible_paths=(
        "target/${target}/release/kernel"
        "target/${target}/release/syn-os-kernel"
        "target/${target}/release/syn_os_kernel"
        "target/${target}/release/deps/kernel-"
        "src/kernel/target/${target}/release/kernel"
    )
    
    for path in "${possible_paths[@]}"; do
        # Handle deps directory with hash suffix
        if [[ "$path" == *"deps/kernel-"* ]]; then
            local found=$(find "${PROJECT_ROOT}/target/${target}/release/deps/" -name "kernel-*" -type f ! -name "*.d" 2>/dev/null | head -1)
            if [ -n "$found" ] && [ -f "$found" ]; then
                kernel_binary="$found"
                break
            fi
        elif [ -f "${PROJECT_ROOT}/${path}" ]; then
            kernel_binary="${PROJECT_ROOT}/${path}"
            break
        fi
    done
    
    if [ -z "$kernel_binary" ]; then
        error "Kernel binary not found after compilation"
        return 1
    fi
    
    local kernel_size=$(du -h "$kernel_binary" | cut -f1)
    success "Kernel binary located: $(basename "$kernel_binary") (${kernel_size})" >&2
    echo "$kernel_binary"
    return 0
}

# Build workspace packages
build_workspace() {
    local build_mode="${1:-release}"
    
    section "Building Workspace Packages"
    
    log "Building all workspace packages in ${build_mode} mode..."
    
    if cargo build --workspace --"${build_mode}" 2>&1 | tee -a "${BUILD_LOG}" | tail -20; then
        success "Workspace build completed"
        return 0
    else
        warning "Some workspace packages failed to build (non-critical)"
        return 1
    fi
}

# Collect compiled binaries
collect_binaries() {
    local dest_dir="$1"
    local build_mode="${2:-release}"
    local binary_count=0
    
    log "Collecting compiled binaries..."
    mkdir -p "$dest_dir"
    
    # Find all executables in the target directory
    while IFS= read -r binary; do
        if [ -n "$binary" ] && cp "$binary" "$dest_dir/" 2>/dev/null; then
            ((binary_count++))
        fi
    done < <(find "${PROJECT_ROOT}/target/${build_mode}" -maxdepth 1 -type f -executable ! -name "*.so" ! -name "*.d" 2>/dev/null || true)
    
    if [ "$binary_count" -gt 0 ]; then
        success "Copied ${binary_count} compiled binaries"
    else
        warning "No binaries found to copy"
    fi
    
    return 0  # Always return success; missing binaries is just a warning
}

################################################################################
# GRUB Configuration
################################################################################

# Create GRUB configuration
create_grub_config() {
    local grub_cfg="$1"
    local version="${2:-1.0.0}"
    
    log "Creating GRUB configuration..."
    
    mkdir -p "$(dirname "$grub_cfg")"
    
    cat > "$grub_cfg" << EOF
# SynOS GRUB Configuration
# Generated: $(date)

set timeout=10
set default=0

# Terminal configuration
terminal_output console
set menu_color_normal=cyan/black
set menu_color_highlight=white/blue

# Main boot menu
menuentry "SynOS v${version} - Neural Darwinism OS" {
    echo 'Loading SynOS kernel...'
    multiboot /boot/kernel.bin
    echo 'Booting SynOS...'
    boot
}

menuentry "SynOS v${version} - Safe Mode" {
    echo 'Loading SynOS kernel in safe mode...'
    multiboot /boot/kernel.bin safe_mode
    echo 'Booting SynOS (Safe Mode)...'
    boot
}

menuentry "SynOS v${version} - Debug Mode (Verbose)" {
    echo 'Loading SynOS kernel with debugging...'
    multiboot /boot/kernel.bin debug verbose
    echo 'Booting SynOS (Debug)...'
    boot
}

menuentry "SynOS v${version} - Recovery Mode" {
    echo 'Loading SynOS kernel in recovery mode...'
    multiboot /boot/kernel.bin recovery
    echo 'Booting SynOS (Recovery)...'
    boot
}

submenu 'Advanced Options' {
    menuentry "SynOS - Minimal Mode (No AI)" {
        multiboot /boot/kernel.bin minimal no_ai
        boot
    }

    menuentry "SynOS - Testing Mode" {
        multiboot /boot/kernel.bin test_mode
        boot
    }

    menuentry "SynOS - Single User Mode" {
        multiboot /boot/kernel.bin single_user
        boot
    }
}

menuentry "System Information" {
    echo "SynOS v${version}"
    echo "Built: $(date)"
    echo "Architecture: x86_64"
    echo "Press any key to continue..."
    read
}

menuentry "Reboot" {
    reboot
}

menuentry "Power Off" {
    halt
}
EOF
    
    success "GRUB configuration created"
    return 0
}

################################################################################
# ISO Generation
################################################################################

# Generate ISO image
generate_iso() {
    local iso_dir="$1"
    local output_iso="$2"
    local iso_label="${3:-SynOS}"
    
    section "Generating ISO Image"
    
    log "ISO directory: ${iso_dir}"
    log "Output file: ${output_iso}"
    log "Label: ${iso_label}"
    
    # Create output directory
    mkdir -p "$(dirname "$output_iso")"
    
    # Generate ISO with grub-mkrescue
    # Use i386-pc platform (BIOS) since it's more universally compatible
    if grub-mkrescue -o "$output_iso" \
        --compress=xz \
        "${iso_dir}" \
        2>&1 | tee -a "${BUILD_LOG}"; then
        
        local iso_size=$(du -h "$output_iso" | cut -f1)
        success "ISO created: $(basename "$output_iso") (${iso_size})"
        return 0
    else
        error "ISO generation failed"
        return 1
    fi
}

# Generate checksums
generate_checksums() {
    local iso_file="$1"
    local checksum_dir="${2:-$(dirname "$iso_file")}"
    
    log "Generating checksums..."
    
    mkdir -p "$checksum_dir"
    
    local basename=$(basename "$iso_file")
    
    # MD5
    if md5sum "$iso_file" > "${checksum_dir}/${basename}.md5"; then
        success "MD5 checksum generated"
    else
        warning "MD5 checksum generation failed"
    fi
    
    # SHA256
    if sha256sum "$iso_file" > "${checksum_dir}/${basename}.sha256"; then
        success "SHA256 checksum generated"
    else
        warning "SHA256 checksum generation failed"
    fi
    
    return 0
}

################################################################################
# File Operations
################################################################################

# Copy documentation files
copy_documentation() {
    local dest_dir="$1"
    shift
    local docs=("$@")
    local doc_count=0
    
    log "Copying documentation files..."
    mkdir -p "$dest_dir"
    
    for doc in "${docs[@]}"; do
        if [ -f "${PROJECT_ROOT}/${doc}" ]; then
            cp "${PROJECT_ROOT}/${doc}" "$dest_dir/"
            ((doc_count++))
        fi
    done
    
    success "Included ${doc_count} documentation files"
    return 0
}

# Create source archive
create_source_archive() {
    local output_file="$1"
    local version="${2:-1.0.0}"
    
    log "Creating source code archive..."
    mkdir -p "$(dirname "$output_file")"
    
    tar czf "$output_file" \
        --exclude='target' \
        --exclude='build' \
        --exclude='.git' \
        --exclude='*.iso' \
        -C "${PROJECT_ROOT}" \
        src/ core/ docs/ Cargo.toml Cargo.lock 2>&1 | tee -a "${BUILD_LOG}"
    
    if [ -f "$output_file" ]; then
        local archive_size=$(du -h "$output_file" | cut -f1)
        success "Source archive created: ${archive_size}"
        return 0
    else
        error "Source archive creation failed"
        return 1
    fi
}

################################################################################
# Cleanup Functions
################################################################################

# Setup cleanup trap
setup_cleanup() {
    trap 'cleanup_handler $?' EXIT INT TERM
}

# Cleanup handler
cleanup_handler() {
    local exit_code=$1
    
    if [ "${CLEANUP_ON_EXIT:-true}" = "true" ]; then
        log "Performing cleanup..."
        # Add any specific cleanup tasks here
    fi
    
    if [ "$exit_code" -eq 0 ]; then
        success "Build completed successfully"
    else
        error "Build failed with exit code: $exit_code"
    fi
}

################################################################################
# Validation Functions
################################################################################

# Verify ISO is bootable
verify_iso() {
    local iso_file="$1"
    
    log "Verifying ISO structure..."
    
    if [ ! -f "$iso_file" ]; then
        error "ISO file not found: $iso_file"
        return 1
    fi
    
    # Check if ISO has GRUB boot
    if xorriso -indev "$iso_file" -find / 2>/dev/null | grep -q "boot/grub"; then
        success "ISO has GRUB bootloader"
    else
        warning "GRUB bootloader not detected in ISO"
    fi
    
    # Check if kernel is present
    if xorriso -indev "$iso_file" -find / 2>/dev/null | grep -q "boot/kernel"; then
        success "Kernel binary found in ISO"
    else
        warning "Kernel binary not detected in ISO"
    fi
    
    return 0
}

################################################################################
# Banner Functions
################################################################################

# Print build banner
print_banner() {
    local title="${1:-SynOS Build System}"
    local version="${2:-1.0.0}"
    
    echo -e "${BOLD}${CYAN}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║      ███████╗██╗   ██╗███╗   ██╗ ██████╗ ███████╗                       ║
║      ██╔════╝╚██╗ ██╔╝████╗  ██║██╔═══██╗██╔════╝                       ║
║      ███████╗ ╚████╔╝ ██╔██╗ ██║██║   ██║███████╗                       ║
║      ╚════██║  ╚██╔╝  ██║╚██╗██║██║   ██║╚════██║                       ║
║      ███████║   ██║   ██║ ╚████║╚██████╔╝███████║                       ║
║      ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝                       ║
║                                                                          ║
EOF
    echo -e "║                    ${title}${NC}"
    echo -e "${BOLD}${CYAN}║                         Version ${version}                               ║"
    echo -e "╚══════════════════════════════════════════════════════════════════════════╝${NC}"
    echo
}

################################################################################
# Utility Functions
################################################################################

# Human-readable file size
human_size() {
    local bytes="$1"
    if [ "$bytes" -lt 1024 ]; then
        echo "${bytes}B"
    elif [ "$bytes" -lt $((1024 * 1024)) ]; then
        echo "$((bytes / 1024))KB"
    elif [ "$bytes" -lt $((1024 * 1024 * 1024)) ]; then
        echo "$((bytes / 1024 / 1024))MB"
    else
        echo "$((bytes / 1024 / 1024 / 1024))GB"
    fi
}

# Elapsed time
elapsed_time() {
    local start_time="$1"
    local end_time="${2:-$(date +%s)}"
    local elapsed=$((end_time - start_time))
    
    local hours=$((elapsed / 3600))
    local minutes=$(((elapsed % 3600) / 60))
    local seconds=$((elapsed % 60))
    
    if [ $hours -gt 0 ]; then
        echo "${hours}h ${minutes}m ${seconds}s"
    elif [ $minutes -gt 0 ]; then
        echo "${minutes}m ${seconds}s"
    else
        echo "${seconds}s"
    fi
}

################################################################################
# Export all functions
################################################################################

export -f log success error warning info section
export -f init_build_env check_not_root check_required_tools check_disk_space
export -f build_kernel find_kernel_binary build_workspace collect_binaries
export -f create_grub_config generate_iso generate_checksums
export -f copy_documentation create_source_archive
export -f setup_cleanup cleanup_handler verify_iso
export -f print_banner human_size elapsed_time

log "Build common library loaded"
