#!/bin/bash

# =========================================================
# Syn_OS Environment Validation Script
# =========================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REQUIRED_RUST_VERSION="1.70.0"
REQUIRED_PYTHON_VERSION="3.8"
REQUIRED_GO_VERSION="1.19"
REQUIRED_NODE_VERSION="18"

# Tracking variables
ERRORS=0
WARNINGS=0

# Function to print colored output
print_status() {
    local status=$1
    local message=$2

    case $status in
        "success")
            echo -e "${GREEN}✓${NC} $message"
            ;;
        "error")
            echo -e "${RED}✗${NC} $message"
            ((ERRORS++))
            ;;
        "warning")
            echo -e "${YELLOW}⚠${NC} $message"
            ((WARNINGS++))
            ;;
        "info")
            echo -e "${BLUE}ℹ${NC} $message"
            ;;
    esac
}

# Function to check command existence
check_command() {
    local cmd=$1
    local name=$2

    if command -v $cmd &> /dev/null; then
        print_status "success" "$name is installed"
        return 0
    else
        print_status "error" "$name is not installed"
        return 1
    fi
}

# Function to compare versions
version_compare() {
    local version1=$1
    local version2=$2

    if [[ "$(printf '%s\n' "$version2" "$version1" | sort -V | head -n1)" == "$version2" ]]; then
        return 0
    else
        return 1
    fi
}

echo "========================================="
echo "   Syn_OS Environment Validation"
echo "========================================="
echo ""

# Check Rust installation
print_status "info" "Checking Rust environment..."
if command -v rustc &> /dev/null; then
    RUST_VERSION=$(rustc --version | cut -d' ' -f2)
    if version_compare "$RUST_VERSION" "$REQUIRED_RUST_VERSION"; then
        print_status "success" "Rust $RUST_VERSION installed (minimum: $REQUIRED_RUST_VERSION)"
    else
        print_status "warning" "Rust $RUST_VERSION installed but minimum version is $REQUIRED_RUST_VERSION"
    fi

    # Check required Rust targets
    if rustup target list | grep -q "x86_64-unknown-none (installed)"; then
        print_status "success" "Rust target x86_64-unknown-none is installed"
    else
        print_status "error" "Rust target x86_64-unknown-none is not installed"
        print_status "info" "Install with: rustup target add x86_64-unknown-none"
    fi

    # Check Cargo
    check_command "cargo" "Cargo"

    # Check important Cargo tools
    if cargo install --list | grep -q "cargo-audit"; then
        print_status "success" "cargo-audit is installed"
    else
        print_status "warning" "cargo-audit is not installed (recommended for security)"
        print_status "info" "Install with: cargo install cargo-audit"
    fi
else
    print_status "error" "Rust is not installed"
    print_status "info" "Install from: https://rustup.rs/"
fi

echo ""

# Check Python installation
print_status "info" "Checking Python environment..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if version_compare "$PYTHON_VERSION" "$REQUIRED_PYTHON_VERSION"; then
        print_status "success" "Python $PYTHON_VERSION installed (minimum: $REQUIRED_PYTHON_VERSION)"
    else
        print_status "warning" "Python $PYTHON_VERSION installed but minimum version is $REQUIRED_PYTHON_VERSION"
    fi

    # Check pip
    check_command "pip3" "pip3"

    # Check critical Python packages
    for package in pytest pyyaml requests; do
        if python3 -c "import $package" 2>/dev/null; then
            print_status "success" "Python package '$package' is installed"
        else
            print_status "warning" "Python package '$package' is not installed"
        fi
    done
else
    print_status "error" "Python 3 is not installed"
fi

echo ""

# Check Go installation
print_status "info" "Checking Go environment..."
if command -v go &> /dev/null; then
    GO_VERSION=$(go version | cut -d' ' -f3 | sed 's/go//')
    if version_compare "$GO_VERSION" "$REQUIRED_GO_VERSION"; then
        print_status "success" "Go $GO_VERSION installed (minimum: $REQUIRED_GO_VERSION)"
    else
        print_status "warning" "Go $GO_VERSION installed but minimum version is $REQUIRED_GO_VERSION"
    fi
else
    print_status "warning" "Go is not installed (optional for service orchestration)"
fi

echo ""

# Check Node.js installation
print_status "info" "Checking Node.js environment..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | sed 's/v//' | cut -d'.' -f1)
    if [[ "$NODE_VERSION" -ge "${REQUIRED_NODE_VERSION}" ]]; then
        print_status "success" "Node.js $(node --version) installed (minimum: v$REQUIRED_NODE_VERSION)"
    else
        print_status "warning" "Node.js $(node --version) installed but minimum version is v$REQUIRED_NODE_VERSION"
    fi

    check_command "npm" "npm"
else
    print_status "warning" "Node.js is not installed (optional for frontend development)"
fi

echo ""

# Check build tools
print_status "info" "Checking build tools..."
check_command "make" "Make"
check_command "git" "Git"
check_command "docker" "Docker"
check_command "docker-compose" "Docker Compose"

echo ""

# Check QEMU for kernel testing
print_status "info" "Checking virtualization tools..."
if command -v qemu-system-x86_64 &> /dev/null; then
    QEMU_VERSION=$(qemu-system-x86_64 --version | head -n1 | cut -d' ' -f4)
    print_status "success" "QEMU $QEMU_VERSION is installed"
else
    print_status "warning" "QEMU is not installed (required for kernel testing)"
    print_status "info" "Install with: sudo apt-get install qemu-system-x86"
fi

# Check for GRUB tools (for ISO creation)
check_command "grub-mkrescue" "GRUB mkrescue (for ISO creation)"
check_command "xorriso" "xorriso (for ISO creation)"

echo ""

# Check project structure
print_status "info" "Checking project structure..."
PROJECT_DIRS=("src/kernel" "core/security" "core/consciousness" "tests" "scripts" "config")
for dir in "${PROJECT_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        print_status "success" "Directory $dir exists"
    else
        print_status "error" "Directory $dir is missing"
    fi
done

# Check for Cargo.toml
if [[ -f "Cargo.toml" ]]; then
    print_status "success" "Cargo.toml found"
else
    print_status "error" "Cargo.toml not found"
fi

# Check for Makefile
if [[ -f "Makefile" ]]; then
    print_status "success" "Makefile found"
else
    print_status "error" "Makefile not found"
fi

echo ""
echo "========================================="
echo "           Validation Summary"
echo "========================================="

if [[ $ERRORS -eq 0 ]]; then
    if [[ $WARNINGS -eq 0 ]]; then
        print_status "success" "Environment is fully configured! ✨"
    else
        print_status "warning" "Environment is functional with $WARNINGS warnings"
        echo ""
        echo "Your environment will work but some optional features may be unavailable."
    fi
else
    print_status "error" "Found $ERRORS errors and $WARNINGS warnings"
    echo ""
    echo "Please fix the errors above before proceeding with development."
    exit 1
fi

echo ""
echo "Ready to build Syn_OS! 🚀"