#!/bin/bash

# SynapticOS Pre-Build Validation Script
# Ensures environment is ready for complete distribution build

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                SYNAPTICOS BUILD VALIDATOR                    ║${NC}"
echo -e "${CYAN}║              Environment & Dependencies Check               ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VALIDATION_PASSED=true
ISSUES_FOUND=0
RECOMMENDATIONS=()

echo -e "${BLUE}[INFO]${NC} Validating SynapticOS build environment..."
echo -e "${BLUE}[INFO]${NC} Project Root: ${PROJECT_ROOT}"
echo

# Helper functions
log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
    RECOMMENDATIONS+=("$1")
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
    VALIDATION_PASSED=false
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
}

log_info() {
    echo -e "${BLUE}[ℹ]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    log_error "Script should not be run as root. Please run as regular user."
    exit 1
fi

# System Requirements Check
echo -e "${PURPLE}═══ System Requirements ═══${NC}"

# Check available disk space
AVAILABLE_SPACE=$(df -BG "${PROJECT_ROOT}" | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$AVAILABLE_SPACE" -ge 20 ]; then
    log_success "Disk space: ${AVAILABLE_SPACE}GB available (minimum 20GB required)"
else
    log_error "Insufficient disk space: ${AVAILABLE_SPACE}GB available (minimum 20GB required)"
fi

# Check available memory
TOTAL_MEMORY=$(free -g | awk 'NR==2{printf "%.0f", $2}')
AVAILABLE_MEMORY=$(free -g | awk 'NR==2{printf "%.0f", $7}')
if [ "$TOTAL_MEMORY" -ge 4 ]; then
    log_success "Total memory: ${TOTAL_MEMORY}GB, Available: ${AVAILABLE_MEMORY}GB (minimum 4GB recommended)"
elif [ "$TOTAL_MEMORY" -ge 2 ]; then
    log_warning "Total memory: ${TOTAL_MEMORY}GB, Available: ${AVAILABLE_MEMORY}GB (minimum 4GB recommended for optimal performance)"
else
    log_error "Insufficient memory: ${TOTAL_MEMORY}GB total (minimum 2GB required)"
fi

# Check CPU cores
CPU_CORES=$(nproc)
if [ "$CPU_CORES" -ge 4 ]; then
    log_success "CPU cores: ${CPU_CORES} (optimal for parallel building)"
elif [ "$CPU_CORES" -ge 2 ]; then
    log_warning "CPU cores: ${CPU_CORES} (build will be slower but functional)"
else
    log_warning "CPU cores: ${CPU_CORES} (single core may cause very slow builds)"
fi

echo

# Essential Tools Check
echo -e "${PURPLE}═══ Essential Build Tools ═══${NC}"

REQUIRED_TOOLS=(
    "curl:Download ParrotOS ISO"
    "wget:Alternative download tool"
    "7z:ISO extraction (p7zip-full package)"
    "unsquashfs:SquashFS extraction (squashfs-tools)"
    "mksquashfs:SquashFS creation (squashfs-tools)"
    "xorriso:ISO creation"
    "grub-mkrescue:GRUB bootloader (grub-common)"
    "python3:Consciousness services"
    "cargo:Rust kernel compilation"
    "rustc:Rust compiler"
    "gcc:C compiler for kernel"
    "make:Build automation"
    "git:Version control"
    "sudo:Privilege elevation"
)

for tool_entry in "${REQUIRED_TOOLS[@]}"; do
    tool=$(echo "$tool_entry" | cut -d: -f1)
    description=$(echo "$tool_entry" | cut -d: -f2)
    
    if command -v "$tool" >/dev/null 2>&1; then
        version=$(${tool} --version 2>/dev/null | head -1 || echo "version unknown")
        log_success "${tool}: Available (${description})"
    else
        log_error "${tool}: Missing (${description})"
    fi
done

echo

# Rust Toolchain Validation
echo -e "${PURPLE}═══ Rust Development Environment ═══${NC}"

if command -v rustup >/dev/null 2>&1; then
    log_success "Rustup: Available"
    
    # Check for custom target
    if rustup target list --installed | grep -q "x86_64-syn_os"; then
        log_success "Custom target x86_64-syn_os: Installed"
    else
        log_warning "Custom target x86_64-syn_os: Not installed (will be created during build)"
    fi
    
    # Check Rust version
    RUST_VERSION=$(rustc --version | cut -d' ' -f2)
    log_info "Rust version: ${RUST_VERSION}"
    
    # Check for nightly toolchain
    if rustup toolchain list | grep -q nightly; then
        log_success "Rust nightly toolchain: Available"
    else
        log_warning "Rust nightly toolchain: Not installed (required for kernel development)"
    fi
else
    log_error "Rustup: Not found (install from https://rustup.rs/)"
fi

echo

# Python Environment Check
echo -e "${PURPLE}═══ Python Environment ═══${NC}"

if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_success "Python 3: ${PYTHON_VERSION}"
    
    # Check for pip
    if python3 -m pip --version >/dev/null 2>&1; then
        log_success "pip: Available"
    else
        log_error "pip: Not available (install python3-pip)"
    fi
    
    # Check for virtualenv
    if python3 -m venv --help >/dev/null 2>&1; then
        log_success "venv: Available"
    else
        log_warning "venv: Not available (install python3-venv)"
    fi
else
    log_error "Python 3: Not found"
fi

echo

# Project Structure Validation
echo -e "${PURPLE}═══ Project Structure ═══${NC}"

REQUIRED_DIRS=(
    "src/kernel:Custom consciousness kernel"
    "parrotos-integration:ParrotOS integration framework"
    "parrotos-integration/build-scripts:Build automation scripts"
    "services:Consciousness microservices"
    "scripts:Utility scripts"
)

for dir_entry in "${REQUIRED_DIRS[@]}"; do
    dir=$(echo "$dir_entry" | cut -d: -f1)
    description=$(echo "$dir_entry" | cut -d: -f2)
    
    if [ -d "${PROJECT_ROOT}/${dir}" ]; then
        log_success "${dir}/: Present (${description})"
    else
        log_error "${dir}/: Missing (${description})"
    fi
done

# Check for essential files
REQUIRED_FILES=(
    "src/kernel/Cargo.toml:Kernel build configuration"
    "parrotos-integration/build-scripts/setup-parrotos-integration.sh:ParrotOS setup script"
    "parrotos-integration/build-scripts/build-synapticos-iso.sh:ISO builder script"
    "parrotos-integration/build-scripts/integrate-consciousness-kernel.sh:Kernel integration script"
    "parrotos-integration/build-synapticos-complete.sh:Master build script"
)

for file_entry in "${REQUIRED_FILES[@]}"; do
    file=$(echo "$file_entry" | cut -d: -f1)
    description=$(echo "$file_entry" | cut -d: -f2)
    
    if [ -f "${PROJECT_ROOT}/${file}" ]; then
        if [ -x "${PROJECT_ROOT}/${file}" ] && [[ "$file" == *.sh ]]; then
            log_success "${file}: Present and executable (${description})"
        elif [[ "$file" == *.sh ]]; then
            log_warning "${file}: Present but not executable (${description})"
        else
            log_success "${file}: Present (${description})"
        fi
    else
        log_error "${file}: Missing (${description})"
    fi
done

echo

# Network Connectivity Check
echo -e "${PURPLE}═══ Network Connectivity ═══${NC}"

if ping -c 1 google.com >/dev/null 2>&1; then
    log_success "Internet connectivity: Available"
else
    log_error "Internet connectivity: Failed (required for ParrotOS download)"
fi

# Check ParrotOS download availability
if curl -I "https://deb.parrot.sh/parrot/iso/" >/dev/null 2>&1; then
    log_success "ParrotOS repository: Accessible"
else
    log_warning "ParrotOS repository: May not be accessible (check firewall/proxy)"
fi

echo

# Storage Requirements Analysis
echo -e "${PURPLE}═══ Storage Requirements Analysis ═══${NC}"

log_info "Estimated space requirements:"
log_info "  • ParrotOS ISO download: ~3GB"
log_info "  • ISO extraction and working space: ~8GB"
log_info "  • Rust kernel compilation: ~2GB"
log_info "  • Final SynapticOS ISO: ~4GB"
log_info "  • Build artifacts and logs: ~1GB"
log_info "  • Total recommended: ~20GB free space"

echo

# Performance Optimization Suggestions
echo -e "${PURPLE}═══ Performance Optimization ═══${NC}"

# Check if on SSD
if [ -f /sys/block/sda/queue/rotational ]; then
    IS_SSD=$(cat /sys/block/sda/queue/rotational)
    if [ "$IS_SSD" = "0" ]; then
        log_success "Storage type: SSD detected (optimal for builds)"
    else
        log_warning "Storage type: HDD detected (SSD recommended for faster builds)"
    fi
fi

# Check swap space
SWAP_TOTAL=$(free -g | awk 'NR==3{print $2}')
if [ "$SWAP_TOTAL" -ge 4 ]; then
    log_success "Swap space: ${SWAP_TOTAL}GB (adequate for large builds)"
elif [ "$SWAP_TOTAL" -ge 2 ]; then
    log_warning "Swap space: ${SWAP_TOTAL}GB (consider increasing for very large builds)"
else
    log_warning "Swap space: ${SWAP_TOTAL}GB (may cause issues with memory-intensive operations)"
fi

echo

# Docker Environment Check (Optional)
echo -e "${PURPLE}═══ Optional: Docker Environment ═══${NC}"

if command -v docker >/dev/null 2>&1; then
    if docker info >/dev/null 2>&1; then
        log_success "Docker: Available and running (optional for containerized builds)"
    else
        log_warning "Docker: Installed but not running (optional for containerized builds)"
    fi
else
    log_info "Docker: Not installed (optional - can be used for isolated builds)"
fi

echo

# Validation Summary
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                    VALIDATION SUMMARY                        ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"

if [ "$VALIDATION_PASSED" = true ]; then
    echo -e "${GREEN}✅ Environment validation PASSED${NC}"
    echo -e "${GREEN}🚀 Your system is ready for SynapticOS distribution building!${NC}"
    echo
    
    if [ ${#RECOMMENDATIONS[@]} -gt 0 ]; then
        echo -e "${YELLOW}📋 Recommendations for optimal performance:${NC}"
        for rec in "${RECOMMENDATIONS[@]}"; do
            echo -e "   • ${rec}"
        done
        echo
    fi
    
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "   1. Run: ./parrotos-integration/build-synapticos-complete.sh"
    echo -e "   2. Monitor build progress in generated log file"
    echo -e "   3. Test resulting ISO in virtual machine"
    echo
else
    echo -e "${RED}❌ Environment validation FAILED${NC}"
    echo -e "${RED}${ISSUES_FOUND} critical issues found that must be resolved${NC}"
    echo
    echo -e "${YELLOW}Required actions:${NC}"
    echo -e "   1. Install missing packages: sudo apt update && sudo apt install -y curl wget p7zip-full squashfs-tools xorriso grub-common python3-pip python3-venv build-essential"
    echo -e "   2. Install Rust toolchain: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    echo -e "   3. Ensure adequate disk space (minimum 20GB free)"
    echo -e "   4. Re-run this validation script"
    echo
    exit 1
fi

# Quick setup commands for common issues
echo -e "${CYAN}🛠️  Quick Setup Commands:${NC}"
echo -e "   • Install packages: sudo apt update && apt install -y curl wget p7zip-full squashfs-tools xorriso grub-common python3-pip python3-venv build-essential"
echo -e "   • Install Rust: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh && source ~/.cargo/env"
echo -e "   • Install nightly Rust: rustup toolchain install nightly"
echo -e "   • Make scripts executable: chmod +x parrotos-integration/build-scripts/*.sh parrotos-integration/*.sh"

echo
echo -e "${GREEN}🎯 SynapticOS Build Environment Validation Complete!${NC}"
