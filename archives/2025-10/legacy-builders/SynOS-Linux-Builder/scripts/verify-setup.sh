#!/bin/bash

# SynOS Linux Distribution Setup Verification
# Verifies that all components are properly configured

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_status() {
    local status=$1
    local message=$2

    case $status in
        "success") echo -e "${GREEN}✅${NC} $message" ;;
        "error") echo -e "${RED}❌${NC} $message" ;;
        "info") echo -e "${BLUE}ℹ️${NC} $message" ;;
        "warning") echo -e "${YELLOW}⚠️${NC} $message" ;;
        "header") echo -e "${CYAN}🚀 $message${NC}" ;;
    esac
}

echo ""
print_status "header" "SynOS Linux Distribution Setup Verification"
echo "========================================================"
echo ""

# Check directory structure
print_status "info" "Checking directory structure..."

dirs=(
    "scripts"
    "base/filesystem"
    "base/packages"
    "base/configs"
    "synos/consciousness"
    "synos/education"
    "synos/themes"
    "synos/tools"
    "build/stages"
    "build/logs"
    "build/releases"
)

for dir in "${dirs[@]}"; do
    if [[ -d "$PROJECT_ROOT/$dir" ]]; then
        print_status "success" "Directory exists: $dir"
    else
        print_status "warning" "Directory missing: $dir"
    fi
done

echo ""

# Check scripts
print_status "info" "Checking build scripts..."

scripts=(
    "scripts/setup-build-environment.sh"
    "scripts/build-synos-base.sh"
    "scripts/copy-synos-components.sh"
    "scripts/create-branding-assets.sh"
    "build-synos-linux.sh"
)

for script in "${scripts[@]}"; do
    if [[ -f "$PROJECT_ROOT/$script" && -x "$PROJECT_ROOT/$script" ]]; then
        print_status "success" "Script ready: $script"
    else
        print_status "error" "Script missing or not executable: $script"
    fi
done

echo ""

# Check required tools
print_status "info" "Checking required tools..."

tools=(
    "git:Git version control"
    "curl:HTTP client"
    "wget:Web downloader"
    "python3:Python interpreter"
    "rustc:Rust compiler"
)

for tool_info in "${tools[@]}"; do
    IFS=':' read -r tool desc <<< "$tool_info"
    if command -v "$tool" &>/dev/null; then
        print_status "success" "$desc available"
    else
        print_status "warning" "$desc not found"
    fi
done

echo ""

# Check live-build tools (for actual building)
print_status "info" "Checking live-build tools (for ISO creation)..."

build_tools=(
    "lb:Live-build"
    "debootstrap:Debian bootstrap"
    "mksquashfs:SquashFS tools"
    "xorriso:ISO creation"
)

all_build_tools_available=true

for tool_info in "${build_tools[@]}"; do
    IFS=':' read -r tool desc <<< "$tool_info"
    if command -v "$tool" &>/dev/null; then
        print_status "success" "$desc available"
    else
        print_status "warning" "$desc not installed"
        all_build_tools_available=false
    fi
done

echo ""

# Check SynOS source components
print_status "info" "Checking SynOS source components..."

synos_components=(
    "/home/diablorain/Syn_OS/src/consciousness:AI Consciousness"
    "/home/diablorain/Syn_OS/core/ai:AI Core"
    "/home/diablorain/Syn_OS/src/userspace/synpkg:SynPkg Manager"
    "/home/diablorain/Syn_OS/src/kernel:Custom Kernel"
)

for component_info in "${synos_components[@]}"; do
    IFS=':' read -r path desc <<< "$component_info"
    if [[ -d "$path" ]]; then
        print_status "success" "$desc source available"
    else
        print_status "warning" "$desc source not found"
    fi
done

echo ""

# Check ParrotOS ISO
print_status "info" "Checking ParrotOS base ISO..."

parrot_iso="/home/diablorain/Downloads/Parrot-security-6.4_amd64.iso"
if [[ -f "$parrot_iso" ]]; then
    iso_size=$(du -h "$parrot_iso" | cut -f1)
    print_status "success" "ParrotOS ISO available ($iso_size)"
else
    print_status "error" "ParrotOS ISO not found at $parrot_iso"
fi

echo ""

# Summary and recommendations
print_status "header" "Setup Summary"
echo "============="
echo ""

if [[ $all_build_tools_available == true ]]; then
    print_status "success" "All build tools available - Ready to build ISO!"
    echo ""
    print_status "info" "Next steps:"
    print_status "info" "  1. Run: cd $PROJECT_ROOT"
    print_status "info" "  2. Run: ./build-synos-linux.sh"
    print_status "info" "  3. Select build option (Quick Test recommended for first build)"
else
    print_status "warning" "Build tools missing - Setup required"
    echo ""
    print_status "info" "To install required tools:"
    print_status "info" "  1. Run: cd $PROJECT_ROOT"
    print_status "info" "  2. Run: ./scripts/setup-build-environment.sh"
    print_status "info" "  3. Then run: ./build-synos-linux.sh"
fi

echo ""

# Disk space check
available_space=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
available_gb=$((available_space / 1024 / 1024))

if [[ $available_gb -gt 10 ]]; then
    print_status "success" "Sufficient disk space available (${available_gb}GB)"
else
    print_status "warning" "Low disk space (${available_gb}GB) - Recommend 10GB+ for building"
fi

echo ""

# Configuration verification
if [[ -f "$PROJECT_ROOT/build-synos-linux.sh" ]]; then
    print_status "success" "Master build script ready"

    echo ""
    print_status "info" "Build options available:"
    print_status "info" "  • Quick Test: ~2GB ISO, 30 minutes"
    print_status "info" "  • Standard: ~4GB ISO, 60 minutes"
    print_status "info" "  • Full: ~6GB ISO, 90 minutes"
else
    print_status "error" "Master build script not found"
fi

echo ""
print_status "header" "Verification complete!"

# Show current status
echo ""
if [[ $all_build_tools_available == true ]]; then
    echo "🎯 Status: READY TO BUILD"
else
    echo "⚠️ Status: SETUP REQUIRED"
fi

echo ""