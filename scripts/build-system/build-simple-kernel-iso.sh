#!/bin/bash

# =========================================================
# Syn_OS Simple Kernel ISO Builder
# Creates a bootable ISO image for testing and deployment
# =========================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build"
ISO_DIR="$BUILD_DIR/iso"
KERNEL_TARGET="x86_64-unknown-none"
KERNEL_NAME="syn_os_kernel"
ISO_NAME="syn_os.iso"

# Print functions
print_status() {
    local status=$1
    local message=$2

    case $status in
        "success")
            echo -e "${GREEN}✓${NC} $message"
            ;;
        "error")
            echo -e "${RED}✗${NC} $message"
            ;;
        "info")
            echo -e "${BLUE}ℹ${NC} $message"
            ;;
        "warning")
            echo -e "${YELLOW}⚠${NC} $message"
            ;;
    esac
}

cleanup() {
    print_status "info" "Cleaning up temporary files..."
    # Remove any temporary files if needed
}

# Set trap for cleanup
trap cleanup EXIT

echo "========================================="
echo "    Syn_OS Kernel ISO Builder"
echo "========================================="
echo ""

# Check dependencies
print_status "info" "Checking dependencies..."
MISSING_DEPS=()

if ! command -v cargo &> /dev/null; then
    MISSING_DEPS+=("cargo")
fi

if ! command -v grub-mkrescue &> /dev/null; then
    MISSING_DEPS+=("grub-mkrescue")
fi

if ! command -v xorriso &> /dev/null; then
    MISSING_DEPS+=("xorriso")
fi

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    print_status "error" "Missing dependencies: ${MISSING_DEPS[*]}"
    print_status "info" "Install with: sudo apt-get install grub-pc-bin grub-common xorriso"
    exit 1
fi

print_status "success" "All dependencies available"

# Create build directories
print_status "info" "Creating build directories..."
mkdir -p "$ISO_DIR/boot/grub"
mkdir -p "$BUILD_DIR/logs"

# Build the kernel
print_status "info" "Building Syn_OS kernel..."
cd "$PROJECT_ROOT"

# Set Rust environment variables for kernel compilation
export RUST_TARGET_PATH="$PROJECT_ROOT/.cargo"

# Build kernel with release optimizations
if cargo build --manifest-path=src/kernel/Cargo.toml --target=$KERNEL_TARGET --release 2>&1 | tee "$BUILD_DIR/logs/kernel_build.log"; then
    print_status "success" "Kernel compilation completed"
else
    print_status "error" "Kernel compilation failed"
    print_status "info" "Check build log: $BUILD_DIR/logs/kernel_build.log"
    exit 1
fi

# Locate the kernel binary
KERNEL_BINARY=""
POSSIBLE_PATHS=(
    "target/$KERNEL_TARGET/release/kernel"
    "target/$KERNEL_TARGET/release/syn_os_kernel"
    "target/$KERNEL_TARGET/release/syn-os-kernel"
    "src/kernel/target/$KERNEL_TARGET/release/kernel"
)

for path in "${POSSIBLE_PATHS[@]}"; do
    if [ -f "$PROJECT_ROOT/$path" ]; then
        KERNEL_BINARY="$PROJECT_ROOT/$path"
        break
    fi
done

if [ -z "$KERNEL_BINARY" ]; then
    print_status "error" "Could not locate kernel binary"
    print_status "info" "Searched in:"
    for path in "${POSSIBLE_PATHS[@]}"; do
        echo "  - $path"
    done

    print_status "info" "Available files in target directory:"
    find "$PROJECT_ROOT/target" -name "*kernel*" -type f 2>/dev/null || echo "No files found"
    exit 1
fi

print_status "success" "Found kernel binary: $(basename "$KERNEL_BINARY")"

# Copy kernel to ISO directory
print_status "info" "Preparing ISO structure..."
cp "$KERNEL_BINARY" "$ISO_DIR/boot/kernel.bin"

# Create GRUB configuration
cat > "$ISO_DIR/boot/grub/grub.cfg" << 'EOF'
set timeout=5
set default=0

menuentry "Syn_OS - Neural Darwinism OS" {
    multiboot /boot/kernel.bin
    boot
}

menuentry "Syn_OS - Safe Mode" {
    multiboot /boot/kernel.bin safe_mode
    boot
}

menuentry "Syn_OS - Debug Mode" {
    multiboot /boot/kernel.bin debug
    boot
}
EOF

print_status "success" "GRUB configuration created"

# Create system information file
cat > "$ISO_DIR/SYN_OS_INFO.txt" << EOF
Syn_OS - Neural Darwinism Enhanced Operating System
===================================================

Build Information:
- Build Date: $(date)
- Kernel Target: $KERNEL_TARGET
- Build Host: $(hostname)
- Git Commit: $(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

Boot Instructions:
1. Boot from this ISO image
2. Select boot option from GRUB menu
3. Syn_OS will initialize with AI consciousness integration

Features:
- Rust-based kernel with memory safety
- Zero-trust security architecture
- Neural Darwinism AI integration
- Real-time threat detection
- Advanced cryptographic operations

For more information, visit the project repository.
EOF

# Create the ISO image
print_status "info" "Creating bootable ISO image..."
ISO_OUTPUT="$BUILD_DIR/$ISO_NAME"

if grub-mkrescue -o "$ISO_OUTPUT" "$ISO_DIR" 2>&1 | tee "$BUILD_DIR/logs/iso_creation.log"; then
    print_status "success" "ISO image created successfully"

    # Get file size
    ISO_SIZE=$(du -h "$ISO_OUTPUT" | cut -f1)
    print_status "info" "ISO size: $ISO_SIZE"
    print_status "info" "ISO location: $ISO_OUTPUT"
else
    print_status "error" "ISO creation failed"
    print_status "info" "Check log: $BUILD_DIR/logs/iso_creation.log"
    exit 1
fi

# Verify the ISO
print_status "info" "Verifying ISO image..."
if file "$ISO_OUTPUT" | grep -q "ISO 9660"; then
    print_status "success" "ISO image verification passed"
else
    print_status "warning" "ISO verification inconclusive"
fi

# Create checksum
print_status "info" "Generating checksums..."
cd "$BUILD_DIR"
sha256sum "$ISO_NAME" > "${ISO_NAME}.sha256"
md5sum "$ISO_NAME" > "${ISO_NAME}.md5"

print_status "success" "Checksums generated"

echo ""
echo "========================================="
echo "          Build Complete!"
echo "========================================="
echo ""
echo "ISO Image: $ISO_OUTPUT"
echo "Size: $ISO_SIZE"
echo "SHA256: $(cat "${ISO_OUTPUT}.sha256" | cut -d' ' -f1)"
echo ""
echo "Test with QEMU:"
echo "  qemu-system-x86_64 -cdrom \"$ISO_OUTPUT\" -m 512M"
echo ""
echo "Or use the make target:"
echo "  make qemu-test"
echo ""
print_status "success" "Syn_OS kernel ISO build completed successfully! 🚀"