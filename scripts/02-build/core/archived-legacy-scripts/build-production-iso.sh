#!/bin/bash

# =========================================================
# Syn_OS Production ISO Builder
# Creates a production-ready ISO with full optimizations
# =========================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_status() {
    local status=$1
    local message=$2

    case $status in
        "success") echo -e "${GREEN}${NC} $message" ;;
        "error") echo -e "${RED}${NC} $message" ;;
        "info") echo -e "${BLUE}9${NC} $message" ;;
        "warning") echo -e "${YELLOW} ${NC} $message" ;;
        "header") echo -e "${CYAN}${message}${NC}" ;;
    esac
}

echo ""
print_status "header" "========================================="
print_status "header" "    Syn_OS Production ISO Builder"
print_status "header" "    Neural Darwinism Enhanced OS"
print_status "header" "========================================="
echo ""

# Pre-build validation
print_status "info" "Running pre-build validation..."

# Check security status
if [ -f "$SCRIPT_DIR/a_plus_security_audit.py" ]; then
    print_status "info" "Running security audit..."
    if python3 "$SCRIPT_DIR/a_plus_security_audit.py"; then
        print_status "success" "Security audit passed"
    else
        print_status "error" "Security audit failed - cannot create production ISO"
        exit 1
    fi
else
    print_status "warning" "Security audit script not found"
fi

# Check environment
if [ -f "$SCRIPT_DIR/validate-environment.sh" ]; then
    print_status "info" "Validating build environment..."
    if "$SCRIPT_DIR/validate-environment.sh"; then
        print_status "success" "Environment validation passed"
    else
        print_status "error" "Environment validation failed"
        exit 1
    fi
fi

# Clean build
print_status "info" "Performing clean build..."
cd "$PROJECT_ROOT"

# Full clean
cargo clean
rm -rf build/ target/
print_status "success" "Build environment cleaned"

# Run comprehensive tests
print_status "info" "Running comprehensive test suite..."
if make test; then
    print_status "success" "All tests passed"
else
    print_status "error" "Tests failed - cannot create production ISO"
    exit 1
fi

# Build with maximum optimizations
print_status "info" "Building production kernel with maximum optimizations..."

# Set production environment variables
export CARGO_PROFILE_RELEASE_OPT_LEVEL="3"
export CARGO_PROFILE_RELEASE_LTO="fat"
export CARGO_PROFILE_RELEASE_CODEGEN_UNITS="1"
export CARGO_PROFILE_RELEASE_PANIC="abort"
export CARGO_PROFILE_RELEASE_STRIP="true"
export RUSTFLAGS="-C target-cpu=native -C target-feature=+crt-static"

if cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none --release; then
    print_status "success" "Production kernel build completed"
else
    print_status "error" "Production kernel build failed"
    exit 1
fi

# Create production ISO
print_status "info" "Creating production ISO..."
"$SCRIPT_DIR/build-simple-kernel-iso.sh"

# Rename and finalize
BUILD_DIR="$PROJECT_ROOT/build"
if [ -f "$BUILD_DIR/syn_os.iso" ]; then
    mv "$BUILD_DIR/syn_os.iso" "$BUILD_DIR/syn_os_production.iso"

    # Generate security checksums
    cd "$BUILD_DIR"
    sha256sum "syn_os_production.iso" > "syn_os_production.iso.sha256"
    sha512sum "syn_os_production.iso" > "syn_os_production.iso.sha512"

    print_status "success" "Production ISO created: $BUILD_DIR/syn_os_production.iso"
else
    print_status "error" "Production ISO creation failed"
    exit 1
fi

echo ""
print_status "success" "Production ISO build completed! =€="