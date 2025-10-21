#!/bin/bash
#
# SynOS Master Rust Build Script
# Builds ALL Rust components in the codebase
#
# Author: SynOS Development Team
# Date: October 15, 2025
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

WORKSPACE_ROOT="/home/diablorain/Syn_OS"
BUILD_OUTPUT="$WORKSPACE_ROOT/build/rust-binaries"
BUILD_LOG="$WORKSPACE_ROOT/logs/rust-build-$(date +%Y%m%d-%H%M%S).log"

# Create output directories
mkdir -p "$BUILD_OUTPUT"/{binaries,libraries,modules}
mkdir -p "$(dirname "$BUILD_LOG")"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1" | tee -a "$BUILD_LOG"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$BUILD_LOG"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$BUILD_LOG"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$BUILD_LOG"
}

# Build counter
TOTAL_BUILDS=0
SUCCESSFUL_BUILDS=0
FAILED_BUILDS=0

# Build function with error handling
build_component() {
    local path=$1
    local name=$2
    local target=${3:-""}

    TOTAL_BUILDS=$((TOTAL_BUILDS + 1))

    log "Building $name..."

    if [ ! -d "$WORKSPACE_ROOT/$path" ]; then
        warn "Directory not found: $path - SKIPPING"
        return
    fi

    if [ ! -f "$WORKSPACE_ROOT/$path/Cargo.toml" ]; then
        warn "No Cargo.toml in $path - SKIPPING"
        return
    fi

    cd "$WORKSPACE_ROOT/$path"

    if [ -n "$target" ]; then
        if cargo build --release --target "$target" >> "$BUILD_LOG" 2>&1; then
            success "✓ $name built successfully"
            SUCCESSFUL_BUILDS=$((SUCCESSFUL_BUILDS + 1))
        else
            error "✗ Failed to build $name"
            FAILED_BUILDS=$((FAILED_BUILDS + 1))
        fi
    else
        if cargo build --release >> "$BUILD_LOG" 2>&1; then
            success "✓ $name built successfully"
            SUCCESSFUL_BUILDS=$((SUCCESSFUL_BUILDS + 1))
        else
            error "✗ Failed to build $name"
            FAILED_BUILDS=$((FAILED_BUILDS + 1))
        fi
    fi
}

# Display banner
clear
cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║        🦀 SynOS Master Rust Build System 🦀                          ║
║                                                                      ║
║        Building ALL Rust Components                                 ║
║        The Pinnacle of OS Development                               ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

EOF

log "Starting comprehensive Rust build process..."
log "Build log: $BUILD_LOG"
echo ""

# ============================================================================
# TIER 1: Core System Components (CRITICAL)
# ============================================================================
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  TIER 1: Core System Components                              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

build_component "src/kernel" "SynOS Kernel" "x86_64-unknown-none"
build_component "core/security" "Core Security Framework"
build_component "core/ai" "Core AI Framework"
build_component "core/common" "Core Common Libraries"
build_component "core/services" "Core Services Framework"
build_component "core/infrastructure/package" "Core Infrastructure Package"

echo ""

# ============================================================================
# TIER 2: System Services (HIGH PRIORITY)
# ============================================================================
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  TIER 2: System Services                                     ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

build_component "src/services/synos-ai-daemon" "AI Daemon"
build_component "src/services/synos-consciousness-daemon" "Consciousness Daemon"
build_component "src/services/synos-security-orchestrator" "Security Orchestrator"
build_component "src/services/synos-hardware-accel" "Hardware Accelerator"
build_component "src/services/synos-llm-engine" "LLM Engine"

echo ""

# ============================================================================
# TIER 3: Advanced Security Tools (EDUCATIONAL)
# ============================================================================
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  TIER 3: Advanced Security Tools                             ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

build_component "src/zero-trust-engine" "Zero Trust Engine"
build_component "src/threat-intel" "Threat Intelligence Platform"
build_component "src/threat-hunting" "Threat Hunting Framework"
build_component "src/deception-tech" "Deception Technology"
build_component "src/compliance-runner" "Compliance Runner"
build_component "src/analytics" "Analytics Engine"
build_component "src/hsm-integration" "HSM Integration"
build_component "src/vuln-research" "Vulnerability Research Framework"
build_component "src/vm-wargames" "VM War Games Platform"

echo ""

# ============================================================================
# TIER 4: Development & Tools
# ============================================================================
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  TIER 4: Development & Tools                                 ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

build_component "src/userspace/shell" "SynOS Shell (synsh)"
build_component "src/userspace/libc" "Userspace libc"
build_component "src/userspace/libtsynos" "Userspace libtsynos"
build_component "src/userspace/synpkg" "SynPkg Package Manager"
build_component "src/tools/ai-model-manager" "AI Model Manager"
build_component "src/tools/distro-builder" "Distribution Builder"
build_component "src/tools/dev-utils" "Development Utilities"

echo ""

# ============================================================================
# TIER 5: Specialized Components
# ============================================================================
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  TIER 5: Specialized Components                              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

build_component "src/ai-runtime" "AI Runtime Engine"
build_component "src/ai-engine" "AI Engine Core"
build_component "src/desktop" "Desktop Environment"
build_component "src/graphics" "Graphics Stack"
build_component "src/drivers/ai-accelerator" "AI Accelerator Driver"

echo ""

# ============================================================================
# TIER 6: Testing & Quality Assurance
# ============================================================================
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  TIER 6: Testing & Quality Assurance                         ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

build_component "tests/fuzzing" "Fuzzing Test Suite"
build_component "tests/ai_module" "AI Module Tests"
build_component "tests/integration" "Integration Tests"
build_component "src/userspace/tests" "Userspace Tests"

echo ""

# ============================================================================
# TIER 7: Build Tools & Infrastructure
# ============================================================================
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  TIER 7: Build Tools & Infrastructure                        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

build_component "scripts/boot-builder" "Boot Builder"

echo ""
echo ""

# ============================================================================
# Copy all binaries to output directory
# ============================================================================
log "Copying built artifacts to $BUILD_OUTPUT..."

# Find and copy all release binaries
find "$WORKSPACE_ROOT" -type f -path "*/target/release/*" ! -path "*/deps/*" ! -path "*/build/*" ! -path "*/incremental/*" -executable -exec cp {} "$BUILD_OUTPUT/binaries/" \; 2>/dev/null || true

# Find and copy all libraries
find "$WORKSPACE_ROOT" -type f -path "*/target/release/*.so" -exec cp {} "$BUILD_OUTPUT/libraries/" \; 2>/dev/null || true
find "$WORKSPACE_ROOT" -type f -path "*/target/release/*.a" -exec cp {} "$BUILD_OUTPUT/libraries/" \; 2>/dev/null || true

# Find and copy kernel modules
find "$WORKSPACE_ROOT" -type f -path "*/target/*/release/*.ko" -exec cp {} "$BUILD_OUTPUT/modules/" \; 2>/dev/null || true

success "Artifacts copied to $BUILD_OUTPUT"

# ============================================================================
# Generate Build Report
# ============================================================================
echo ""
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  BUILD SUMMARY                                               ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Total Components:      ${BLUE}$TOTAL_BUILDS${NC}"
echo -e "Successful Builds:     ${GREEN}$SUCCESSFUL_BUILDS${NC}"
echo -e "Failed Builds:         ${RED}$FAILED_BUILDS${NC}"
echo ""

if [ $FAILED_BUILDS -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ ALL COMPONENTS BUILT SUCCESSFULLY!                       ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
else
    echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  ⚠️  Some components failed to build                         ║${NC}"
    echo -e "${YELLOW}║  Check build log: $BUILD_LOG${NC}"
    echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════╝${NC}"
fi

echo ""
echo -e "Build artifacts location: ${BLUE}$BUILD_OUTPUT${NC}"
echo -e "  - Binaries:  $BUILD_OUTPUT/binaries/"
echo -e "  - Libraries: $BUILD_OUTPUT/libraries/"
echo -e "  - Modules:   $BUILD_OUTPUT/modules/"
echo ""
echo -e "Full build log: ${BLUE}$BUILD_LOG${NC}"
echo ""

# List what was built
echo -e "${BLUE}Built Binaries:${NC}"
ls -lh "$BUILD_OUTPUT/binaries/" 2>/dev/null || echo "  (none)"
echo ""
echo -e "${BLUE}Built Libraries:${NC}"
ls -lh "$BUILD_OUTPUT/libraries/" 2>/dev/null || echo "  (none)"
echo ""

# ============================================================================
# Next Steps
# ============================================================================
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  NEXT STEPS                                                  ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "1. Review build log for any warnings/errors"
echo "2. Run remaster script to integrate into ISO:"
echo "   sudo ./scripts/02-build/build-synos-from-parrot.sh"
echo "3. Test the complete ISO"
echo ""
echo -e "${GREEN}🦀 Rust build process complete! 🦀${NC}"
echo ""

# Exit with appropriate code
if [ $FAILED_BUILDS -gt 0 ]; then
    exit 1
else
    exit 0
fi
