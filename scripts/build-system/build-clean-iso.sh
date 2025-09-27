#!/bin/bash

# =========================================================
# Syn_OS Clean ISO Builder
# Builds a clean, optimized ISO for production deployment
# =========================================================

set -euo pipefail

# Import common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    local status=$1
    local message=$2

    case $status in
        "success") echo -e "${GREEN}${NC} $message" ;;
        "error") echo -e "${RED}${NC} $message" ;;
        "info") echo -e "${BLUE}9${NC} $message" ;;
        "warning") echo -e "${YELLOW} ${NC} $message" ;;
    esac
}

echo "========================================="
echo "    Syn_OS Clean ISO Builder"
echo "========================================="

# Clean previous builds
print_status "info" "Cleaning previous build artifacts..."
cd "$PROJECT_ROOT"

# Clean Rust targets
cargo clean
rm -rf build/

print_status "success" "Build artifacts cleaned"

# Build with clean environment
print_status "info" "Building clean kernel with optimizations..."

# Use release-small profile for minimal size
export CARGO_PROFILE_RELEASE_SMALL_OPT_LEVEL="z"
export CARGO_PROFILE_RELEASE_SMALL_LTO="fat"
export CARGO_PROFILE_RELEASE_SMALL_CODEGEN_UNITS="1"
export CARGO_PROFILE_RELEASE_SMALL_PANIC="abort"
export CARGO_PROFILE_RELEASE_SMALL_STRIP="symbols"

if cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none --profile=release-small; then
    print_status "success" "Clean kernel build completed"
else
    print_status "error" "Clean kernel build failed"
    exit 1
fi

# Create optimized ISO
print_status "info" "Creating optimized clean ISO..."
"$SCRIPT_DIR/build-simple-kernel-iso.sh"

# Rename for clarity
BUILD_DIR="$PROJECT_ROOT/build"
if [ -f "$BUILD_DIR/syn_os.iso" ]; then
    mv "$BUILD_DIR/syn_os.iso" "$BUILD_DIR/syn_os_clean.iso"
    mv "$BUILD_DIR/syn_os.iso.sha256" "$BUILD_DIR/syn_os_clean.iso.sha256" 2>/dev/null || true
    mv "$BUILD_DIR/syn_os.iso.md5" "$BUILD_DIR/syn_os_clean.iso.md5" 2>/dev/null || true

    print_status "success" "Clean ISO created: $BUILD_DIR/syn_os_clean.iso"
else
    print_status "error" "Clean ISO creation failed"
    exit 1
fi

echo ""
print_status "success" "Clean ISO build completed! >ù("