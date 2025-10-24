#!/bin/bash

################################################################################
#
# SynOS Comprehensive Pre-Build Testing Suite
# Validates all components before ISO creation
# Date: October 22, 2025
#
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/build/logs/prebuild-tests"
TIMESTAMP=$(date '+%Y%m%d-%H%M%S')
TEST_LOG="$LOG_DIR/prebuild-test-$TIMESTAMP.log"

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
WARNED_TESTS=0

# Create log directory
mkdir -p "$LOG_DIR"

# Logging functions
log() {
    echo -e "${CYAN}[$(date '+%H:%M:%S')]${NC} $*" | tee -a "$TEST_LOG"
}

success() {
    echo -e "${GREEN}✓${NC} $*" | tee -a "$TEST_LOG"
    ((PASSED_TESTS++))
}

error() {
    echo -e "${RED}✗${NC} $*" | tee -a "$TEST_LOG"
    ((FAILED_TESTS++))
}

warning() {
    echo -e "${YELLOW}⚠${NC} $*" | tee -a "$TEST_LOG"
    ((WARNED_TESTS++))
}

info() {
    echo -e "${BLUE}ℹ${NC} $*" | tee -a "$TEST_LOG"
}

section() {
    echo | tee -a "$TEST_LOG"
    echo -e "${BOLD}${PURPLE}═══════════════════════════════════════════════════════${NC}" | tee -a "$TEST_LOG"
    echo -e "${BOLD}${PURPLE}  $*${NC}" | tee -a "$TEST_LOG"
    echo -e "${BOLD}${PURPLE}═══════════════════════════════════════════════════════${NC}" | tee -a "$TEST_LOG"
    echo | tee -a "$TEST_LOG"
}

run_test() {
    local test_name="$1"
    local test_command="$2"
    ((TOTAL_TESTS++))

    info "Testing: $test_name"
    if eval "$test_command" >> "$TEST_LOG" 2>&1; then
        success "$test_name"
        return 0
    else
        error "$test_name"
        return 1
    fi
}

# Print header
clear
echo -e "${BOLD}${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║     ███████╗██╗   ██╗███╗   ██╗ ██████╗ ███████╗                     ║
║     ██╔════╝╚██╗ ██╔╝████╗  ██║██╔═══██╗██╔════╝                     ║
║     ███████╗ ╚████╔╝ ██╔██╗ ██║██║   ██║███████╗                     ║
║     ╚════██║  ╚██╔╝  ██║╚██╗██║██║   ██║╚════██║                     ║
║     ███████║   ██║   ██║ ╚████║╚██████╔╝███████║                     ║
║     ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝                     ║
║                                                                       ║
║           Comprehensive Pre-Build Testing Suite                      ║
║                    October 22, 2025                                  ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

log "Starting comprehensive pre-build tests..."
log "Project root: $PROJECT_ROOT"
log "Test log: $TEST_LOG"
echo

# ============================================================================
# SECTION 1: Environment & Dependencies
# ============================================================================
section "1. Environment & System Dependencies"

run_test "System is Linux" "uname -s | grep -q Linux"
run_test "User has sudo access" "sudo -n true 2>/dev/null || sudo -v"
run_test "Cargo (Rust) installed" "command -v cargo"
run_test "Git installed" "command -v git"
run_test "Python3 installed" "command -v python3"

# Build tools
info "Checking build tools..."
run_test "GCC compiler available" "command -v gcc"
run_test "Make available" "command -v make"
run_test "GRUB tools installed" "command -v grub-mkrescue"
run_test "xorriso installed" "command -v xorriso"
run_test "debootstrap installed" "command -v debootstrap"

# Optional but recommended tools
if command -v qemu-system-x86_64 &>/dev/null; then
    success "QEMU available for testing"
else
    warning "QEMU not found - ISO testing will be limited"
fi

# Check disk space
AVAILABLE_SPACE=$(df -BG "$PROJECT_ROOT" | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$AVAILABLE_SPACE" -gt 50 ]; then
    success "Sufficient disk space: ${AVAILABLE_SPACE}GB available"
else
    warning "Low disk space: ${AVAILABLE_SPACE}GB (50GB+ recommended)"
fi

# Check memory
TOTAL_MEM=$(free -g | awk 'NR==2 {print $2}')
if [ "$TOTAL_MEM" -ge 8 ]; then
    success "Sufficient RAM: ${TOTAL_MEM}GB"
else
    warning "Limited RAM: ${TOTAL_MEM}GB (8GB+ recommended)"
fi

# ============================================================================
# SECTION 2: Rust Workspace Compilation
# ============================================================================
section "2. Rust Workspace Compilation"

cd "$PROJECT_ROOT"

info "Checking Rust toolchain..."
run_test "Rust nightly toolchain" "rustup show | grep -q nightly"

info "Running cargo check on workspace..."
if cargo check --workspace --message-format=short 2>&1 | tee -a "$TEST_LOG" | tail -20; then
    success "Workspace cargo check passed"
    ((PASSED_TESTS++))
else
    error "Workspace cargo check failed"
    ((FAILED_TESTS++))
fi
((TOTAL_TESTS++))

info "Testing critical crates compilation..."
CRITICAL_CRATES=(
    "syn-security"
    "synos-services"
    "synos-gamification"
    "syn-desktop"
    "synos-graphics"
)

for crate in "${CRITICAL_CRATES[@]}"; do
    run_test "Compile $crate" "cargo build -p $crate --release"
done

# ============================================================================
# SECTION 3: Kernel Build Test
# ============================================================================
section "3. Custom Kernel Build"

info "Testing kernel compilation..."
if [ -f "src/kernel/Cargo.toml" ]; then
    KERNEL_TARGET="x86_64-unknown-none"

    run_test "Kernel target available" "rustup target list | grep -q $KERNEL_TARGET"

    info "Building kernel (this may take a few minutes)..."
    if cargo build --manifest-path=src/kernel/Cargo.toml --target=$KERNEL_TARGET --release 2>&1 | tail -20 | tee -a "$TEST_LOG"; then
        success "Kernel build successful"
        ((PASSED_TESTS++))

        # Check for kernel binary
        KERNEL_PATHS=(
            "target/$KERNEL_TARGET/release/kernel"
            "target/$KERNEL_TARGET/release/syn_os_kernel"
            "target/$KERNEL_TARGET/release/syn-os-kernel"
        )

        KERNEL_FOUND=false
        for path in "${KERNEL_PATHS[@]}"; do
            if [ -f "$path" ]; then
                KERNEL_SIZE=$(du -h "$path" | cut -f1)
                success "Kernel binary found: $path (${KERNEL_SIZE})"
                KERNEL_FOUND=true
                ((PASSED_TESTS++))
                break
            fi
        done

        if [ "$KERNEL_FOUND" = false ]; then
            error "Kernel binary not found after build"
            ((FAILED_TESTS++))
        fi
        ((TOTAL_TESTS++))
    else
        error "Kernel build failed"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
else
    warning "Kernel source not found at src/kernel/"
    ((WARNED_TESTS++))
    ((TOTAL_TESTS++))
fi

# ============================================================================
# SECTION 4: Module Verification
# ============================================================================
section "4. Module Integrity Checks"

info "Verifying V1.5-V1.8 modules..."
MODULES=(
    "src/gamification"
    "src/cloud-security"
    "src/ai-tutor"
    "src/mobile-bridge"
)

for module in "${MODULES[@]}"; do
    if [ -d "$module" ]; then
        FILE_COUNT=$(find "$module" -name "*.rs" | wc -l)
        if [ "$FILE_COUNT" -gt 0 ]; then
            success "Module $module: $FILE_COUNT Rust files"
            ((PASSED_TESTS++))
        else
            error "Module $module: No Rust files found"
            ((FAILED_TESTS++))
        fi
    else
        error "Module $module: Directory not found"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
done

# ============================================================================
# SECTION 5: Documentation Validation
# ============================================================================
section "5. Documentation Completeness"

REQUIRED_DOCS=(
    "README.md"
    "docs/V1.5-V1.8_COMPILATION_FIXES_OCT22_2025.md"
    "docs/06-project-status/PROJECT_STATUS.md"
    "CHANGELOG.md"
)

for doc in "${REQUIRED_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        WORD_COUNT=$(wc -w < "$doc")
        if [ "$WORD_COUNT" -gt 100 ]; then
            success "Documentation $doc exists ($WORD_COUNT words)"
            ((PASSED_TESTS++))
        else
            warning "Documentation $doc is very short ($WORD_COUNT words)"
            ((WARNED_TESTS++))
        fi
    else
        error "Missing documentation: $doc"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
done

# ============================================================================
# SECTION 6: Build Scripts Validation
# ============================================================================
section "6. Build Scripts Availability"

BUILD_SCRIPTS=(
    "scripts/02-build/core/build-simple-kernel-iso.sh"
    "Makefile"
)

for script in "${BUILD_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ] || [[ "$script" == *.sh ]]; then
            success "Build script available: $script"
            ((PASSED_TESTS++))
        else
            warning "Build script not executable: $script"
            ((WARNED_TESTS++))
        fi
    else
        error "Build script missing: $script"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
done

# ============================================================================
# SECTION 7: Git Repository Status
# ============================================================================
section "7. Git Repository Health"

if git rev-parse --git-dir > /dev/null 2>&1; then
    success "Valid git repository"
    ((PASSED_TESTS++))

    COMMIT_HASH=$(git rev-parse --short HEAD)
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    info "Current branch: $BRANCH"
    info "Latest commit: $COMMIT_HASH"

    # Check for uncommitted changes
    if git diff-index --quiet HEAD --; then
        success "No uncommitted changes"
        ((PASSED_TESTS++))
    else
        warning "Uncommitted changes detected"
        git status --short | head -10 | tee -a "$TEST_LOG"
        ((WARNED_TESTS++))
    fi
    ((TOTAL_TESTS++))

    # Check if we can push
    if git remote get-url origin &>/dev/null; then
        success "Remote repository configured"
        ((PASSED_TESTS++))
    else
        warning "No remote repository configured"
        ((WARNED_TESTS++))
    fi
    ((TOTAL_TESTS++))
else
    error "Not a git repository"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
fi

# ============================================================================
# SECTION 8: Security & Configuration
# ============================================================================
section "8. Security Configuration"

# Check for sensitive files that shouldn't be in the repo
SENSITIVE_PATTERNS=(
    "*.key"
    "*.pem"
    "*.p12"
    "*.pfx"
    "*password*"
    "*secret*"
)

SENSITIVE_FOUND=false
for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if find . -name "$pattern" -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/target/*" | grep -q .; then
        warning "Sensitive files found matching: $pattern"
        SENSITIVE_FOUND=true
        ((WARNED_TESTS++))
    fi
done

if [ "$SENSITIVE_FOUND" = false ]; then
    success "No sensitive files detected in repository"
    ((PASSED_TESTS++))
fi
((TOTAL_TESTS++))

# Check .gitignore
if [ -f ".gitignore" ]; then
    if grep -q "target/" .gitignore && grep -q "*.log" .gitignore; then
        success ".gitignore configured properly"
        ((PASSED_TESTS++))
    else
        warning ".gitignore may need updates"
        ((WARNED_TESTS++))
    fi
else
    error ".gitignore missing"
    ((FAILED_TESTS++))
fi
((TOTAL_TESTS++))

# ============================================================================
# SECTION 9: Build Directory Structure
# ============================================================================
section "9. Build Environment Structure"

BUILD_DIRS=(
    "build"
    "build/iso"
    "build/logs"
    "target"
)

for dir in "${BUILD_DIRS[@]}"; do
    if mkdir -p "$dir" 2>/dev/null; then
        success "Build directory writable: $dir"
        ((PASSED_TESTS++))
    else
        error "Cannot create build directory: $dir"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
done

# ============================================================================
# SECTION 10: Quick Functionality Tests
# ============================================================================
section "10. Quick Functionality Tests"

info "Testing basic Rust code compilation..."
cat > /tmp/synos_test.rs << 'EOF'
fn main() {
    println!("SynOS test successful!");
}
EOF

if rustc /tmp/synos_test.rs -o /tmp/synos_test && /tmp/synos_test | grep -q "successful"; then
    success "Rust toolchain functional"
    ((PASSED_TESTS++))
    rm -f /tmp/synos_test.rs /tmp/synos_test
else
    error "Rust toolchain test failed"
    ((FAILED_TESTS++))
fi
((TOTAL_TESTS++))

# Test Python
info "Testing Python availability..."
if python3 -c "print('SynOS')" 2>/dev/null | grep -q "SynOS"; then
    success "Python3 functional"
    ((PASSED_TESTS++))
else
    error "Python3 test failed"
    ((FAILED_TESTS++))
fi
((TOTAL_TESTS++))

# ============================================================================
# FINAL REPORT
# ============================================================================
echo | tee -a "$TEST_LOG"
section "Test Results Summary"

PASS_RATE=0
if [ "$TOTAL_TESTS" -gt 0 ]; then
    PASS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
fi

echo -e "${BOLD}Total Tests:${NC}    $TOTAL_TESTS" | tee -a "$TEST_LOG"
echo -e "${GREEN}${BOLD}Passed:${NC}         $PASSED_TESTS" | tee -a "$TEST_LOG"
echo -e "${RED}${BOLD}Failed:${NC}         $FAILED_TESTS" | tee -a "$TEST_LOG"
echo -e "${YELLOW}${BOLD}Warnings:${NC}       $WARNED_TESTS" | tee -a "$TEST_LOG"
echo -e "${BOLD}Success Rate:${NC}   ${PASS_RATE}%" | tee -a "$TEST_LOG"
echo | tee -a "$TEST_LOG"

# Determine build readiness
if [ "$FAILED_TESTS" -eq 0 ]; then
    if [ "$WARNED_TESTS" -eq 0 ]; then
        echo -e "${GREEN}${BOLD}╔═══════════════════════════════════════════════════════════╗${NC}" | tee -a "$TEST_LOG"
        echo -e "${GREEN}${BOLD}║  ✓ ALL TESTS PASSED - BUILD READY FOR ISO CREATION! ✓   ║${NC}" | tee -a "$TEST_LOG"
        echo -e "${GREEN}${BOLD}╚═══════════════════════════════════════════════════════════╝${NC}" | tee -a "$TEST_LOG"
        echo | tee -a "$TEST_LOG"
        log "You can proceed with:"
        log "  ./scripts/unified-iso-builder.sh"
        EXIT_CODE=0
    else
        echo -e "${YELLOW}${BOLD}╔═══════════════════════════════════════════════════════════╗${NC}" | tee -a "$TEST_LOG"
        echo -e "${YELLOW}${BOLD}║  ⚠ BUILD READY WITH WARNINGS - REVIEW RECOMMENDED  ⚠    ║${NC}" | tee -a "$TEST_LOG"
        echo -e "${YELLOW}${BOLD}╚═══════════════════════════════════════════════════════════╝${NC}" | tee -a "$TEST_LOG"
        echo | tee -a "$TEST_LOG"
        log "Review warnings above, then proceed with:"
        log "  ./scripts/unified-iso-builder.sh"
        EXIT_CODE=0
    fi
else
    echo -e "${RED}${BOLD}╔═══════════════════════════════════════════════════════════╗${NC}" | tee -a "$TEST_LOG"
    echo -e "${RED}${BOLD}║  ✗ TESTS FAILED - FIX ERRORS BEFORE BUILDING ISO  ✗     ║${NC}" | tee -a "$TEST_LOG"
    echo -e "${RED}${BOLD}╚═══════════════════════════════════════════════════════════╝${NC}" | tee -a "$TEST_LOG"
    echo | tee -a "$TEST_LOG"
    error "Fix the $FAILED_TESTS failed tests before proceeding"
    log "Review detailed log: $TEST_LOG"
    EXIT_CODE=1
fi

log "Test completed at $(date)"
log "Full log saved to: $TEST_LOG"

exit $EXIT_CODE
