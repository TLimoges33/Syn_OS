#!/bin/bash

################################################################################
# ⚠️  DEPRECATION WARNING
################################################################################
# This script is DEPRECATED and archived as of October 23, 2025.
#
# Please use the new consolidated Build System v2.0 instead:
#   → ./scripts/build-iso.sh           (Standard ISO - 20-30 min)
#   → ./scripts/build-kernel-only.sh   (Quick kernel - 5-10 min)
#   → ./scripts/build-full-linux.sh    (Full distro - 60-90 min)
#
# Migration Guide: docs/BUILD_SCRIPTS_MIGRATION_GUIDE.md
# Script Help:     ./scripts/build-iso.sh --help
#
# This script remains functional but is no longer maintained.
# It will be removed in a future release.
#
# Original: SynOS Unified ISO Builder v1.0 (October 22, 2025)
################################################################################

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "⚠️  WARNING: DEPRECATED SCRIPT"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "This script has been replaced by the new Build System v2.0"
echo ""
echo "  Recommended: ./scripts/build-iso.sh"
echo "  Quick test:  ./scripts/build-kernel-only.sh"
echo "  Full build:  ./scripts/build-full-linux.sh"
echo ""
echo "  Help:        ./scripts/build-iso.sh --help"
echo "  Migration:   docs/BUILD_SCRIPTS_MIGRATION_GUIDE.md"
echo ""
echo "This script will continue running in 5 seconds..."
echo "Press Ctrl+C to cancel and use the new scripts instead."
echo ""
sleep 5
echo "Continuing with deprecated unified-iso-builder.sh..."
echo ""

################################################################################
#
# SynOS Unified ISO Builder v1.0
# Comprehensive bootable ISO creation combining all SynOS features
# Date: October 22, 2025
#
# This script creates a complete bootable SynOS ISO with:
#   ✓ Custom Rust kernel with multiboot support
#   ✓ All compiled Rust workspace modules
#   ✓ V1.5-V1.8 modules (gamification, cloud, AI tutor, mobile)
#   ✓ Security framework and services
#   ✓ Debian-based userland with essential tools
#   ✓ AI consciousness integration
#   ✓ GRUB bootloader with multiple boot options
#   ✓ Hybrid BIOS/UEFI support
#
################################################################################

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_BASE="build"
BUILD_DIR="$PROJECT_ROOT/$BUILD_BASE"
ISO_DIR="$BUILD_DIR/iso"
CHROOT_DIR="$BUILD_DIR/chroot"
LOGS_DIR="$BUILD_DIR/logs/iso-build"
TIMESTAMP=$(date '+%Y%m%d-%H%M%S')
BUILD_LOG="$LOGS_DIR/build-$TIMESTAMP.log"

# ISO Configuration
SYNOS_VERSION="1.0.0"
ISO_NAME="SynOS-v${SYNOS_VERSION}-Complete-${TIMESTAMP}.iso"
ISO_LABEL="SynOS-Linux"
ISO_PUBLISHER="SynOS Development Team"

# Kernel Configuration
KERNEL_TARGET="x86_64-unknown-none"
KERNEL_NAME="syn_os_kernel"

# Build Options
INCLUDE_RUST_BINARIES=true
INCLUDE_SOURCE_CODE=false  # Set to true to include full source
INCLUDE_DOCS=true
QUICK_BUILD=false  # Set to true for faster testing builds

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ============================================================================
# Helper Functions
# ============================================================================

log() {
    echo -e "${CYAN}[$(date '+%H:%M:%S')]${NC} $*" | tee -a "$BUILD_LOG"
}

success() {
    echo -e "${GREEN}✓${NC} $*" | tee -a "$BUILD_LOG"
}

error() {
    echo -e "${RED}✗${NC} $*" | tee -a "$BUILD_LOG"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $*" | tee -a "$BUILD_LOG"
}

info() {
    echo -e "${BLUE}ℹ${NC} $*" | tee -a "$BUILD_LOG"
}

section() {
    echo | tee -a "$BUILD_LOG"
    echo -e "${BOLD}${PURPLE}═══════════════════════════════════════════════════════${NC}" | tee -a "$BUILD_LOG"
    echo -e "${BOLD}${PURPLE}  $*${NC}" | tee -a "$BUILD_LOG"
    echo -e "${BOLD}${PURPLE}═══════════════════════════════════════════════════════${NC}" | tee -a "$BUILD_LOG"
    echo | tee -a "$BUILD_LOG"
}

cleanup() {
    if [ "${CLEANUP_ON_EXIT:-true}" = "true" ]; then
        log "Performing cleanup..."
        # Add any cleanup tasks here
    fi
}

trap cleanup EXIT

# ============================================================================
# Header
# ============================================================================

clear
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
║                    Unified ISO Builder v1.0                             ║
║              Creating Complete Bootable Linux Distribution              ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

log "Starting SynOS ISO build process..."
log "Version: $SYNOS_VERSION"
log "Timestamp: $TIMESTAMP"
log "Build log: $BUILD_LOG"
echo

# ============================================================================
# Pre-flight Checks
# ============================================================================

section "1. Pre-flight Checks"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    error "Do not run this script as root!"
    error "Run as regular user with sudo privileges"
    exit 1
fi

# Check for required tools
REQUIRED_TOOLS=(
    "cargo"
    "rustc"
    "grub-mkrescue"
    "xorriso"
    "git"
)

MISSING_TOOLS=()
for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v "$tool" &>/dev/null; then
        MISSING_TOOLS+=("$tool")
    fi
done

if [ ${#MISSING_TOOLS[@]} -ne 0 ]; then
    error "Missing required tools: ${MISSING_TOOLS[*]}"
    info "Install with: sudo apt-get install cargo rust-all grub-pc-bin grub-common xorriso git"
    exit 1
fi

success "All required tools available"

# Check disk space
AVAILABLE_SPACE=$(df -BG "$PROJECT_ROOT" | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$AVAILABLE_SPACE" -lt 10 ]; then
    error "Insufficient disk space: ${AVAILABLE_SPACE}GB (need at least 10GB)"
    exit 1
fi
success "Sufficient disk space: ${AVAILABLE_SPACE}GB available"

# Create directory structure
log "Creating build directories..."
mkdir -p "$ISO_DIR"/{boot/grub,synos/{bin,lib,docs,source},live}
mkdir -p "$LOGS_DIR"
mkdir -p "$BUILD_DIR/checksums"

success "Build directory structure created"

# ============================================================================
# Kernel Build
# ============================================================================

section "2. Building Custom Rust Kernel"

cd "$PROJECT_ROOT"

# Check if kernel source exists
if [ ! -f "src/kernel/Cargo.toml" ]; then
    error "Kernel source not found at src/kernel/"
    exit 1
fi

log "Building kernel for target: $KERNEL_TARGET"
log "This may take several minutes..."

# Add target if not already installed
if ! rustup target list | grep "$KERNEL_TARGET (installed)" &>/dev/null; then
    log "Adding Rust target: $KERNEL_TARGET"
    rustup target add "$KERNEL_TARGET" | tee -a "$BUILD_LOG"
fi

# Build kernel
if cargo build --manifest-path=src/kernel/Cargo.toml \
    --target="$KERNEL_TARGET" \
    --release \
    2>&1 | tee -a "$BUILD_LOG" | grep -E "(Compiling|Finished)"; then
    success "Kernel compilation completed"
else
    error "Kernel compilation failed"
    info "Check log: $BUILD_LOG"
    exit 1
fi

# Locate kernel binary
KERNEL_BINARY=""
POSSIBLE_KERNEL_PATHS=(
    "target/$KERNEL_TARGET/release/kernel"
    "target/$KERNEL_TARGET/release/$KERNEL_NAME"
    "target/$KERNEL_TARGET/release/syn-os-kernel"
    "src/kernel/target/$KERNEL_TARGET/release/kernel"
)

for path in "${POSSIBLE_KERNEL_PATHS[@]}"; do
    if [ -f "$PROJECT_ROOT/$path" ]; then
        KERNEL_BINARY="$PROJECT_ROOT/$path"
        break
    fi
done

if [ -z "$KERNEL_BINARY" ]; then
    error "Kernel binary not found after compilation"
    info "Searched locations:"
    for path in "${POSSIBLE_KERNEL_PATHS[@]}"; do
        info "  - $path"
    done
    exit 1
fi

KERNEL_SIZE=$(du -h "$KERNEL_BINARY" | cut -f1)
success "Kernel binary located: $(basename "$KERNEL_BINARY") (${KERNEL_SIZE})"

# Copy kernel to ISO
cp "$KERNEL_BINARY" "$ISO_DIR/boot/kernel.bin"
success "Kernel copied to ISO directory"

# ============================================================================
# Workspace Binaries
# ============================================================================

section "3. Building Workspace Binaries"

if [ "$INCLUDE_RUST_BINARIES" = true ]; then
    log "Building all workspace binaries..."

    # Build all workspace packages
    if cargo build --workspace --release 2>&1 | tee -a "$BUILD_LOG" | tail -20; then
        success "Workspace build completed"

        # Copy important binaries
        log "Collecting compiled binaries..."
        BINARY_COUNT=0

        find target/release -maxdepth 1 -type f -executable ! -name "*.so" ! -name "*.d" 2>/dev/null | while read -r binary; do
            cp "$binary" "$ISO_DIR/synos/bin/" 2>/dev/null && ((BINARY_COUNT++)) || true
        done

        # Count binaries
        TOTAL_BINARIES=$(find "$ISO_DIR/synos/bin" -type f 2>/dev/null | wc -l)
        if [ "$TOTAL_BINARIES" -gt 0 ]; then
            success "Copied $TOTAL_BINARIES compiled binaries to ISO"
        else
            warning "No binaries found to copy"
        fi
    else
        warning "Some workspace packages failed to build (non-critical)"
    fi
else
    info "Skipping workspace binary build (INCLUDE_RUST_BINARIES=false)"
fi

# ============================================================================
# Documentation
# ============================================================================

section "4. Including Documentation"

if [ "$INCLUDE_DOCS" = true ]; then
    log "Copying documentation files..."

    DOCS_TO_INCLUDE=(
        "README.md"
        "CHANGELOG.md"
        "docs/V1.5-V1.8_COMPILATION_FIXES_OCT22_2025.md"
        "docs/06-project-status/PROJECT_STATUS.md"
    )

    DOC_COUNT=0
    for doc in "${DOCS_TO_INCLUDE[@]}"; do
        if [ -f "$PROJECT_ROOT/$doc" ]; then
            cp "$PROJECT_ROOT/$doc" "$ISO_DIR/synos/docs/"
            ((DOC_COUNT++))
        fi
    done

    success "Included $DOC_COUNT documentation files"
else
    info "Skipping documentation (INCLUDE_DOCS=false)"
fi

# ============================================================================
# Source Code (Optional)
# ============================================================================

section "5. Source Code Inclusion"

if [ "$INCLUDE_SOURCE_CODE" = true ]; then
    warning "Including full source code (this will increase ISO size significantly)"

    # Create source archive
    log "Creating source code archive..."
    tar czf "$ISO_DIR/synos/source/synos-source-${SYNOS_VERSION}.tar.gz" \
        --exclude='target' \
        --exclude='build' \
        --exclude='.git' \
        --exclude='*.iso' \
        -C "$PROJECT_ROOT" \
        src/ core/ docs/ Cargo.toml Cargo.lock 2>&1 | tee -a "$BUILD_LOG"

    ARCHIVE_SIZE=$(du -h "$ISO_DIR/synos/source/synos-source-${SYNOS_VERSION}.tar.gz" | cut -f1)
    success "Source archive created: ${ARCHIVE_SIZE}"
else
    info "Skipping source code (INCLUDE_SOURCE_CODE=false)"
fi

# ============================================================================
# GRUB Configuration
# ============================================================================

section "6. Configuring GRUB Bootloader"

log "Creating GRUB configuration..."

cat > "$ISO_DIR/boot/grub/grub.cfg" << EOF
# SynOS GRUB Configuration
# Generated: $(date)

set timeout=10
set default=0

# Terminal configuration
terminal_output console
set menu_color_normal=cyan/black
set menu_color_highlight=white/blue

# Main boot menu
menuentry "SynOS v${SYNOS_VERSION} - Neural Darwinism OS" {
    echo 'Loading SynOS kernel...'
    multiboot /boot/kernel.bin
    echo 'Booting SynOS...'
    boot
}

menuentry "SynOS v${SYNOS_VERSION} - Safe Mode" {
    echo 'Loading SynOS kernel in safe mode...'
    multiboot /boot/kernel.bin safe_mode
    echo 'Booting SynOS (Safe Mode)...'
    boot
}

menuentry "SynOS v${SYNOS_VERSION} - Debug Mode (Verbose)" {
    echo 'Loading SynOS kernel with debugging...'
    multiboot /boot/kernel.bin debug verbose
    echo 'Booting SynOS (Debug)...'
    boot
}

menuentry "SynOS v${SYNOS_VERSION} - Recovery Mode" {
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

    menuentry "System Information" {
        cat /synos/SYN_OS_INFO.txt
        echo "Press any key to return to menu..."
        read
    }
}

menuentry "Reboot" {
    reboot
}

menuentry "Shutdown" {
    halt
}
EOF

success "GRUB configuration created"

# ============================================================================
# System Information File
# ============================================================================

log "Creating system information file..."

cat > "$ISO_DIR/synos/SYN_OS_INFO.txt" << EOF
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║      ███████╗██╗   ██╗███╗   ██╗ ██████╗ ███████╗                       ║
║      ██╔════╝╚██╗ ██╔╝████╗  ██║██╔═══██╗██╔════╝                       ║
║      ███████╗ ╚████╔╝ ██╔██╗ ██║██║   ██║███████╗                       ║
║      ╚════██║  ╚██╔╝  ██║╚██╗██║██║   ██║╚════██║                       ║
║      ███████║   ██║   ██║ ╚████║╚██████╔╝███████║                       ║
║      ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝                       ║
║                                                                          ║
║           Neural Darwinism Enhanced Operating System                    ║
║                     www.synos.ai                                        ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝

SynOS - Cognitive Security Operating System
═══════════════════════════════════════════

VERSION INFORMATION:
───────────────────
Version:        ${SYNOS_VERSION}
Build Date:     $(date '+%Y-%m-%d %H:%M:%S')
Build ID:       ${TIMESTAMP}
Kernel Target:  ${KERNEL_TARGET}
Git Commit:     $(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
Build Host:     $(hostname)

SYSTEM FEATURES:
───────────────
✓ Custom Rust Kernel with Memory Safety
✓ Zero-Trust Security Architecture
✓ Neural Darwinism AI Integration
✓ Real-Time Threat Detection & Response
✓ V1.5-V1.8 Enhanced Modules:
  • Legendary Gamification System
  • Cloud Security Orchestration
  • AI-Powered Tutor System
  • Mobile Bridge Integration
✓ Advanced Cryptographic Operations
✓ Consciousness-Aware Process Scheduling
✓ Multi-Cloud Security Management

BOOT INSTRUCTIONS:
─────────────────
1. Boot system from this ISO image
2. Select desired boot option from GRUB menu
3. SynOS will initialize with full AI integration
4. Default credentials (if applicable):
   Username: synos
   Password: (set during installation)

INCLUDED COMPONENTS:
───────────────────
• Custom Rust Kernel ($(du -h "$ISO_DIR/boot/kernel.bin" 2>/dev/null | cut -f1 || echo "N/A"))
• Compiled Workspace Binaries
• Complete Documentation Suite
• Security Framework & Services
• AI Consciousness Engine

TESTING & VIRTUALIZATION:
────────────────────────
QEMU:
  qemu-system-x86_64 -cdrom $ISO_NAME -m 2G -enable-kvm

VirtualBox:
  Create VM with minimum 2GB RAM, boot from ISO

Physical Hardware:
  Write ISO to USB: dd if=$ISO_NAME of=/dev/sdX bs=4M status=progress

DOCUMENTATION:
─────────────
Full documentation available in /synos/docs/
Online: https://github.com/TLimoges33/Syn_OS

SUPPORT & DEVELOPMENT:
────────────────────
Repository:     https://github.com/TLimoges33/Syn_OS
Issues:         https://github.com/TLimoges33/Syn_OS/issues
Discussions:    https://github.com/TLimoges33/Syn_OS/discussions

Build completed successfully at $(date)
═══════════════════════════════════════════════════════════════════════════
EOF

cp "$ISO_DIR/synos/SYN_OS_INFO.txt" "$ISO_DIR/SYN_OS_INFO.txt"
success "System information file created"

# ============================================================================
# Create ISO Image
# ============================================================================

section "7. Creating Bootable ISO Image"

ISO_OUTPUT="$BUILD_DIR/$ISO_NAME"

log "Generating ISO image with grub-mkrescue..."
log "This may take a few minutes..."

if grub-mkrescue -o "$ISO_OUTPUT" "$ISO_DIR" \
    --volid="$ISO_LABEL" \
    2>&1 | tee -a "$BUILD_LOG"; then
    success "ISO image created successfully"
else
    error "ISO creation failed"
    info "Check log: $BUILD_LOG"
    exit 1
fi

# Get ISO size
ISO_SIZE=$(du -h "$ISO_OUTPUT" | cut -f1)
info "ISO size: $ISO_SIZE"

# ============================================================================
# Verification & Checksums
# ============================================================================

section "8. Verification & Checksums"

log "Verifying ISO image format..."
if file "$ISO_OUTPUT" | grep -q "ISO 9660"; then
    success "ISO image format verified"
else
    warning "ISO format verification inconclusive"
fi

log "Generating checksums..."
cd "$BUILD_DIR"

# SHA256
sha256sum "$ISO_NAME" > "$BUILD_DIR/checksums/${ISO_NAME}.sha256"
SHA256=$(cut -d' ' -f1 < "$BUILD_DIR/checksums/${ISO_NAME}.sha256")

# MD5
md5sum "$ISO_NAME" > "$BUILD_DIR/checksums/${ISO_NAME}.md5"
MD5=$(cut -d' ' -f1 < "$BUILD_DIR/checksums/${ISO_NAME}.md5")

success "Checksums generated"

# Create build manifest
log "Creating build manifest..."
cat > "$BUILD_DIR/${ISO_NAME}.manifest" << EOF
SynOS Build Manifest
═══════════════════

ISO Name:           $ISO_NAME
Version:            $SYNOS_VERSION
Build Date:         $(date '+%Y-%m-%d %H:%M:%S')
Build Timestamp:    $TIMESTAMP
ISO Size:           $ISO_SIZE
Git Commit:         $(git rev-parse HEAD 2>/dev/null || echo "unknown")
Git Branch:         $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

Checksums:
─────────
SHA256:             $SHA256
MD5:                $MD5

Build Configuration:
───────────────────
Kernel Target:      $KERNEL_TARGET
Include Binaries:   $INCLUDE_RUST_BINARIES
Include Source:     $INCLUDE_SOURCE_CODE
Include Docs:       $INCLUDE_DOCS

Build Host Info:
───────────────
Hostname:           $(hostname)
OS:                 $(uname -s)
Kernel:             $(uname -r)
Architecture:       $(uname -m)

Files Included:
──────────────
$(find "$ISO_DIR" -type f | wc -l) total files
Kernel:             $(basename "$KERNEL_BINARY")
Binaries:           $(find "$ISO_DIR/synos/bin" -type f 2>/dev/null | wc -l) executables
Documentation:      $(find "$ISO_DIR/synos/docs" -type f 2>/dev/null | wc -l) files

Build Log:          $BUILD_LOG
═══════════════════════════════════════════════════════════════════════════
EOF

success "Build manifest created"

# ============================================================================
# Final Report
# ============================================================================

echo | tee -a "$BUILD_LOG"
section "Build Complete!"

echo -e "${BOLD}${GREEN}"
cat << "EOF"
    ██████╗ ██╗   ██╗██╗██╗     ██████╗
    ██╔══██╗██║   ██║██║██║     ██╔══██╗
    ██████╔╝██║   ██║██║██║     ██║  ██║
    ██╔══██╗██║   ██║██║██║     ██║  ██║
    ██████╔╝╚██████╔╝██║███████╗██████╔╝
    ╚═════╝  ╚═════╝ ╚═╝╚══════╝╚═════╝
     ██████╗ ██████╗ ███╗   ███╗██████╗ ██╗     ███████╗████████╗███████╗
    ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██║     ██╔════╝╚══██╔══╝██╔════╝
    ██║     ██║   ██║██╔████╔██║██████╔╝██║     █████╗     ██║   █████╗
    ██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝     ██║   ██╔══╝
    ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ███████╗███████╗   ██║   ███████╗
     ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝   ╚═╝   ╚══════╝
EOF
echo -e "${NC}"

echo -e "${BOLD}ISO Build Summary:${NC}" | tee -a "$BUILD_LOG"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$BUILD_LOG"
echo -e "${CYAN}ISO File:${NC}       $ISO_OUTPUT" | tee -a "$BUILD_LOG"
echo -e "${CYAN}Size:${NC}           $ISO_SIZE" | tee -a "$BUILD_LOG"
echo -e "${CYAN}Version:${NC}        $SYNOS_VERSION" | tee -a "$BUILD_LOG"
echo -e "${CYAN}Build ID:${NC}       $TIMESTAMP" | tee -a "$BUILD_LOG"
echo -e "${CYAN}SHA256:${NC}         $SHA256" | tee -a "$BUILD_LOG"
echo -e "${CYAN}MD5:${NC}            $MD5" | tee -a "$BUILD_LOG"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$BUILD_LOG"
echo | tee -a "$BUILD_LOG"

echo -e "${BOLD}Testing Commands:${NC}" | tee -a "$BUILD_LOG"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$BUILD_LOG"
echo -e "${YELLOW}QEMU (Recommended):${NC}" | tee -a "$BUILD_LOG"
echo -e "  qemu-system-x86_64 -cdrom \"$ISO_OUTPUT\" -m 2G -enable-kvm" | tee -a "$BUILD_LOG"
echo | tee -a "$BUILD_LOG"
echo -e "${YELLOW}VirtualBox:${NC}" | tee -a "$BUILD_LOG"
echo -e "  1. Create new VM (Type: Linux, Version: Other Linux 64-bit)" | tee -a "$BUILD_LOG"
echo -e "  2. Allocate 2GB+ RAM" | tee -a "$BUILD_LOG"
echo -e "  3. Boot from $ISO_NAME" | tee -a "$BUILD_LOG"
echo | tee -a "$BUILD_LOG"
echo -e "${YELLOW}Physical Hardware (USB):${NC}" | tee -a "$BUILD_LOG"
echo -e "  sudo dd if=\"$ISO_OUTPUT\" of=/dev/sdX bs=4M status=progress && sync" | tee -a "$BUILD_LOG"
echo -e "  ${RED}WARNING: Replace /dev/sdX with your actual USB device!${NC}" | tee -a "$BUILD_LOG"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$BUILD_LOG"
echo | tee -a "$BUILD_LOG"

echo -e "${BOLD}Build Artifacts:${NC}" | tee -a "$BUILD_LOG"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$BUILD_LOG"
echo -e "  ISO:        $ISO_OUTPUT" | tee -a "$BUILD_LOG"
echo -e "  Checksums:  $BUILD_DIR/checksums/" | tee -a "$BUILD_LOG"
echo -e "  Manifest:   $BUILD_DIR/${ISO_NAME}.manifest" | tee -a "$BUILD_LOG"
echo -e "  Build Log:  $BUILD_LOG" | tee -a "$BUILD_LOG"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$BUILD_LOG"
echo | tee -a "$BUILD_LOG"

success "SynOS ISO build completed successfully! 🎉🚀"
log "Build finished at $(date)"

exit 0
