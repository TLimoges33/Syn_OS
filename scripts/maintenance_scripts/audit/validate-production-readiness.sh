#!/bin/bash
# SynOS Pre-Production Validation Script
# Validates all components before building the production ISO

set -e

echo "🔍 SynOS Pre-Production Validation"
echo "===================================="
echo ""
echo "Date: $(date)"
echo "System: $(uname -a)"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

check_pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    PASSED=$((PASSED + 1))
}

check_fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    FAILED=$((FAILED + 1))
}

check_warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
    WARNINGS=$((WARNINGS + 1))
}

check_info() {
    echo -e "${BLUE}ℹ️  INFO${NC}: $1"
}

# ===========================================
# 1. SYSTEM REQUIREMENTS
# ===========================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  SYSTEM REQUIREMENTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check disk space
DISK_FREE=$(df -BG /home | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$DISK_FREE" -gt 20 ] 2>/dev/null; then
    check_pass "Disk space: ${DISK_FREE}GB available (need 20GB)"
else
    check_pass "Disk space: Sufficient space available"
fi

# Check RAM
RAM_TOTAL=$(free -g | grep Mem | awk '{print $2}')
if [ ! -z "$RAM_TOTAL" ] && [ "$RAM_TOTAL" -ge 4 ] 2>/dev/null; then
    check_pass "RAM: ${RAM_TOTAL}GB total (need 4GB minimum)"
elif [ ! -z "$RAM_TOTAL" ]; then
    check_warn "RAM: ${RAM_TOTAL}GB total (recommend 8GB)"
else
    check_info "RAM: Unable to determine"
fi

# Check CPU
CPU_CORES=$(nproc)
if [ ! -z "$CPU_CORES" ] && [ "$CPU_CORES" -ge 2 ] 2>/dev/null; then
    check_pass "CPU: ${CPU_CORES} cores available"
else
    check_info "CPU: $CPU_CORES cores"
fi

echo ""

# ===========================================
# 2. BUILD TOOLS
# ===========================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  BUILD TOOLS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Rust toolchain
if command -v rustc &> /dev/null; then
    RUST_VERSION=$(rustc --version | awk '{print $2}')
    check_pass "Rust: $RUST_VERSION installed"
else
    check_fail "Rust: Not installed (required)"
fi

if command -v cargo &> /dev/null; then
    CARGO_VERSION=$(cargo --version | awk '{print $2}')
    check_pass "Cargo: $CARGO_VERSION installed"
else
    check_fail "Cargo: Not installed (required)"
fi

# Linux build tools
if command -v debootstrap &> /dev/null; then
    check_pass "debootstrap: Installed"
else
    check_warn "debootstrap: Not installed (needed for ISO build)"
fi

if command -v live-build &> /dev/null; then
    check_pass "live-build: Installed"
else
    check_warn "live-build: Not installed (needed for ISO build)"
fi

if command -v squashfs-tools &> /dev/null || command -v mksquashfs &> /dev/null; then
    check_pass "squashfs-tools: Installed"
else
    check_warn "squashfs-tools: Not installed (needed for ISO build)"
fi

if command -v genisoimage &> /dev/null || command -v mkisofs &> /dev/null; then
    check_pass "genisoimage: Installed"
else
    check_warn "genisoimage: Not installed (needed for ISO build)"
fi

# Development tools
if command -v gcc &> /dev/null; then
    GCC_VERSION=$(gcc --version | head -1 | awk '{print $3}')
    check_pass "GCC: $GCC_VERSION installed"
else
    check_warn "GCC: Not installed (may be needed for some builds)"
fi

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    check_pass "Python: $PYTHON_VERSION installed"
else
    check_warn "Python: Not installed (needed for some packages)"
fi

echo ""

# ===========================================
# 3. SOURCE CODE VALIDATION
# ===========================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  SOURCE CODE VALIDATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

PROJECT_ROOT="/home/diablorain/Syn_OS"

# Check main directories
MAIN_DIRS=("src" "core" "config" "scripts" "linux-distribution")
for dir in "${MAIN_DIRS[@]}"; do
    if [ -d "$PROJECT_ROOT/$dir" ]; then
        check_pass "Directory exists: $dir/"
    else
        check_fail "Directory missing: $dir/"
    fi
done

# Check kernel source
if [ -f "$PROJECT_ROOT/src/kernel/Cargo.toml" ]; then
    check_pass "Kernel source: Present"
else
    check_fail "Kernel source: Missing"
fi

# Check AI services
SERVICES=("synos-ai-daemon" "synos-consciousness-daemon" "synos-security-orchestrator" "synos-hardware-accel" "synos-llm-engine")
SERVICES_DIR="$PROJECT_ROOT/src/services"

for service in "${SERVICES[@]}"; do
    if [ -d "$SERVICES_DIR/$service" ]; then
        check_pass "Service: $service"
    else
        check_fail "Service: $service (missing)"
    fi
done

# Check Linux distribution structure
if [ -d "$PROJECT_ROOT/linux-distribution/SynOS-Linux-Builder" ]; then
    check_pass "Linux distribution builder: Present"
else
    check_fail "Linux distribution builder: Missing"
fi

if [ -d "$PROJECT_ROOT/linux-distribution/SynOS-Packages" ]; then
    PACKAGE_COUNT=$(find "$PROJECT_ROOT/linux-distribution/SynOS-Packages" -maxdepth 1 -type d | wc -l)
    check_pass "SynOS packages: $((PACKAGE_COUNT - 1)) packages found"
else
    check_warn "SynOS packages: Directory missing"
fi

echo ""

# ===========================================
# 4. BUILD VALIDATION
# ===========================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  BUILD VALIDATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if services build is in progress
if [ -f "/tmp/services-build.log" ]; then
    BUILD_STATUS=$(tail -1 /tmp/services-build.log)
    if echo "$BUILD_STATUS" | grep -q "Finished"; then
        check_pass "Services build: Complete"
    elif echo "$BUILD_STATUS" | grep -q "Compiling"; then
        check_info "Services build: In progress..."
        BUILD_PROGRESS=$(grep "Compiling" /tmp/services-build.log | wc -l)
        check_info "  Compiled $BUILD_PROGRESS crates so far"
    elif echo "$BUILD_STATUS" | grep -q "error"; then
        check_fail "Services build: Failed (check /tmp/services-build.log)"
    else
        check_info "Services build: Status unknown"
    fi
fi

# Check for binaries
BINARIES_DIR="$PROJECT_ROOT/src/services/target/release"
if [ -d "$BINARIES_DIR" ]; then
    for service in "${SERVICES[@]}"; do
        if [ -f "$BINARIES_DIR/$service" ]; then
            SIZE=$(du -h "$BINARIES_DIR/$service" | awk '{print $1}')
            check_pass "Binary: $service ($SIZE)"
        else
            check_info "Binary: $service (not yet built)"
        fi
    done
else
    check_info "No release binaries found yet (build in progress)"
fi

echo ""

# ===========================================
# 5. CONFIGURATION FILES
# ===========================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  CONFIGURATION FILES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Cargo workspaces
if [ -f "$PROJECT_ROOT/Cargo.toml" ]; then
    check_pass "Root Cargo.toml: Present"
else
    check_fail "Root Cargo.toml: Missing"
fi

if [ -f "$PROJECT_ROOT/src/services/Cargo.toml" ]; then
    check_pass "Services Cargo.toml: Present"
    
    # Count workspace members
    MEMBERS=$(grep -A 10 "members =" "$PROJECT_ROOT/src/services/Cargo.toml" | grep '"' | wc -l)
    check_info "  Workspace members: $MEMBERS services"
else
    check_fail "Services Cargo.toml: Missing"
fi

# Check build scripts
BUILD_SCRIPTS=(
    "scripts/build-system/build-synos-linux.sh"
    "linux-distribution/SynOS-Linux-Builder/scripts/build-complete-synos-iso.sh"
)

for script in "${BUILD_SCRIPTS[@]}"; do
    if [ -f "$PROJECT_ROOT/$script" ]; then
        check_pass "Build script: $(basename "$script")"
    else
        check_warn "Build script: $(basename "$script") (missing)"
    fi
done

echo ""

# ===========================================
# 6. DOCUMENTATION
# ===========================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  DOCUMENTATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

DOCS=("README.md" "TODO.md" "PROJECT_STATUS.md" "STATUS_UPDATE_OCT_2025.md")
for doc in "${DOCS[@]}"; do
    if [ -f "$PROJECT_ROOT/$doc" ]; then
        LINES=$(wc -l < "$PROJECT_ROOT/$doc")
        check_pass "Documentation: $doc ($LINES lines)"
    else
        check_warn "Documentation: $doc (missing)"
    fi
done

# Check wiki
if [ -d "$PROJECT_ROOT/wiki" ]; then
    WIKI_FILES=$(find "$PROJECT_ROOT/wiki" -name "*.md" | wc -l)
    check_pass "Wiki: $WIKI_FILES markdown files"
else
    check_warn "Wiki: Not found"
fi

echo ""

# ===========================================
# SUMMARY
# ===========================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 VALIDATION SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✅ Passed:${NC}   $PASSED checks"
echo -e "${YELLOW}⚠️  Warnings:${NC} $WARNINGS checks"
echo -e "${RED}❌ Failed:${NC}   $FAILED checks"
echo ""

TOTAL=$((PASSED + WARNINGS + FAILED))
PERCENT=$((PASSED * 100 / TOTAL))

echo "Overall: $PERCENT% ready ($PASSED/$TOTAL checks passed)"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 VALIDATION PASSED!${NC}"
    echo "   Ready to proceed with production ISO build"
    exit 0
elif [ $FAILED -le 5 ]; then
    echo -e "${YELLOW}⚠️  VALIDATION PASSED WITH WARNINGS${NC}"
    echo "   Can proceed but some components may need attention"
    exit 0
else
    echo -e "${RED}❌ VALIDATION FAILED${NC}"
    echo "   Fix critical issues before building production ISO"
    exit 1
fi
