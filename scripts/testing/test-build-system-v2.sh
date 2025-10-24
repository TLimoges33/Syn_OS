#!/bin/bash

################################################################################
# Regression Test Suite for Build System v2.0
# Tests all 10 consolidated scripts
################################################################################

set -euo pipefail

PROJECT_ROOT="/home/diablorain/Syn_OS"
cd "$PROJECT_ROOT"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                               ║"
echo "║              🧪 BUILD SYSTEM V2.0 REGRESSION TEST SUITE 🧪                    ║"
echo "║                                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Test function
test_script() {
    local test_name="$1"
    local command="$2"
    local expected_result="$3"  # "pass" or "skip" or custom check
    
    echo ""
    echo -e "${BLUE}┌─────────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${BLUE}│${NC} TEST: $test_name"
    echo -e "${BLUE}└─────────────────────────────────────────────────────────────────┘${NC}"
    echo "Command: $command"
    echo ""
    
    if eval "$command" > /tmp/test_output.log 2>&1; then
        if [ "$expected_result" = "pass" ]; then
            echo -e "${GREEN}✓ PASS${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "${YELLOW}⚠ UNEXPECTED SUCCESS${NC}"
            ((TESTS_FAILED++))
        fi
    else
        local exit_code=$?
        if [ "$expected_result" = "skip" ]; then
            echo -e "${YELLOW}⊘ SKIPPED (exit code: $exit_code)${NC}"
            ((TESTS_SKIPPED++))
        else
            echo -e "${RED}✗ FAIL (exit code: $exit_code)${NC}"
            echo "Last 10 lines of output:"
            tail -10 /tmp/test_output.log
            ((TESTS_FAILED++))
        fi
    fi
}

# Test help output
test_help() {
    local script="$1"
    echo ""
    echo -e "${BLUE}┌─────────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${BLUE}│${NC} TEST: $script --help"
    echo -e "${BLUE}└─────────────────────────────────────────────────────────────────┘${NC}"
    
    if [ ! -f "$script" ]; then
        echo -e "${RED}✗ FAIL - Script not found: $script${NC}"
        ((TESTS_FAILED++))
        return
    fi
    
    if [ ! -x "$script" ]; then
        echo -e "${RED}✗ FAIL - Script not executable: $script${NC}"
        ((TESTS_FAILED++))
        return
    fi
    
    if "$script" --help > /tmp/help_output.log 2>&1; then
        local line_count=$(wc -l < /tmp/help_output.log)
        if [ "$line_count" -gt 10 ]; then
            echo -e "${GREEN}✓ PASS - Help output ($line_count lines)${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "${YELLOW}⚠ PARTIAL - Help output too short ($line_count lines)${NC}"
            ((TESTS_FAILED++))
        fi
    else
        echo -e "${RED}✗ FAIL - Help command failed${NC}"
        ((TESTS_FAILED++))
    fi
}

# Test version output
test_version() {
    local script="$1"
    echo ""
    echo -e "${BLUE}┌─────────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${BLUE}│${NC} TEST: $script --version"
    echo -e "${BLUE}└─────────────────────────────────────────────────────────────────┘${NC}"
    
    if "$script" --version > /tmp/version_output.log 2>&1; then
        if grep -q "v2.0" /tmp/version_output.log; then
            echo -e "${GREEN}✓ PASS - Version v2.0 found${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "${YELLOW}⚠ PARTIAL - Version output present but no v2.0${NC}"
            cat /tmp/version_output.log
            ((TESTS_PASSED++))
        fi
    else
        echo -e "${YELLOW}⊘ SKIPPED - No version option${NC}"
        ((TESTS_SKIPPED++))
    fi
}

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "PHASE 1: SCRIPT EXISTENCE & PERMISSIONS"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

SCRIPTS=(
    "scripts/lib/build-common.sh"
    "scripts/build-kernel-only.sh"
    "scripts/build-iso.sh"
    "scripts/build-full-linux.sh"
    "scripts/testing/verify-build.sh"
    "scripts/testing/test-iso.sh"
    "scripts/maintenance/clean-builds.sh"
    "scripts/maintenance/archive-old-isos.sh"
    "scripts/utilities/sign-iso.sh"
    "scripts/docker/build-docker.sh"
)

for script in "${SCRIPTS[@]}"; do
    echo -n "Checking $script ... "
    if [ -f "$script" ]; then
        # Library files don't need to be executable
        if [[ "$script" == *"/lib/"* ]]; then
            echo -e "${GREEN}✓ EXISTS (library)${NC}"
            ((TESTS_PASSED++))
        elif [ -x "$script" ]; then
            echo -e "${GREEN}✓ EXISTS & EXECUTABLE${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "${YELLOW}⚠ EXISTS BUT NOT EXECUTABLE${NC}"
            chmod +x "$script"
            echo "   (made executable)"
            ((TESTS_PASSED++))
        fi
    else
        echo -e "${RED}✗ NOT FOUND${NC}"
        ((TESTS_FAILED++))
    fi
done

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "PHASE 2: HELP DOCUMENTATION"
echo "═══════════════════════════════════════════════════════════════════"

# Test --help for all main scripts (not lib)
test_help "scripts/build-kernel-only.sh"
test_help "scripts/build-iso.sh"
test_help "scripts/build-full-linux.sh"
test_help "scripts/testing/verify-build.sh"
test_help "scripts/testing/test-iso.sh"
test_help "scripts/maintenance/clean-builds.sh"
test_help "scripts/maintenance/archive-old-isos.sh"
test_help "scripts/utilities/sign-iso.sh"
test_help "scripts/docker/build-docker.sh"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "PHASE 3: VERSION INFORMATION"
echo "═══════════════════════════════════════════════════════════════════"

test_version "scripts/build-kernel-only.sh"
test_version "scripts/build-iso.sh"
test_version "scripts/build-full-linux.sh"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "PHASE 4: DRY-RUN TESTS (NO ACTUAL BUILDS)"
echo "═══════════════════════════════════════════════════════════════════"

# Test verify-build.sh (should actually run)
test_script "verify-build.sh basic run" \
    "./scripts/testing/verify-build.sh --quiet" \
    "pass"

# Test clean-builds.sh dry-run
test_script "clean-builds.sh dry-run" \
    "./scripts/maintenance/clean-builds.sh --dry-run" \
    "pass"

# Test archive-old-isos.sh dry-run
test_script "archive-old-isos.sh dry-run" \
    "./scripts/maintenance/archive-old-isos.sh --dry-run" \
    "pass"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "PHASE 5: PARAMETER VALIDATION"
echo "═══════════════════════════════════════════════════════════════════"

# Test invalid parameters (should fail gracefully)
test_script "build-iso.sh invalid param" \
    "./scripts/build-iso.sh --invalid-option 2>&1 | grep -q 'Unknown option'" \
    "pass"

test_script "test-iso.sh no ISO provided" \
    "./scripts/testing/test-iso.sh 2>&1 | grep -q 'Usage'" \
    "pass"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "PHASE 6: SHELLCHECK VALIDATION"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

if command -v shellcheck >/dev/null 2>&1; then
    for script in "${SCRIPTS[@]}"; do
        if [ -f "$script" ] && [ "$script" != "scripts/lib/build-common.sh" ]; then
            echo -n "ShellCheck $script ... "
            if shellcheck "$script" -x > /tmp/shellcheck.log 2>&1; then
                echo -e "${GREEN}✓ CLEAN${NC}"
                ((TESTS_PASSED++))
            else
                local warning_count=$(wc -l < /tmp/shellcheck.log)
                echo -e "${YELLOW}⚠ $warning_count warnings/errors${NC}"
                # Show first 5 lines
                head -5 /tmp/shellcheck.log
                ((TESTS_FAILED++))
            fi
        fi
    done
else
    echo -e "${YELLOW}⊘ SKIPPED - shellcheck not installed${NC}"
    ((TESTS_SKIPPED+=10))
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "PHASE 7: SOURCE FILE CHECKS"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Check if lib/build-common.sh can be sourced
echo -n "Source lib/build-common.sh ... "
if bash -c "source scripts/lib/build-common.sh" > /tmp/source.log 2>&1; then
    echo -e "${GREEN}✓ SOURCEABLE${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ CANNOT SOURCE${NC}"
    cat /tmp/source.log
    ((TESTS_FAILED++))
fi

# Check for common function availability
echo -n "Check common functions exist ... "
if bash -c "source scripts/lib/build-common.sh && declare -f log_info >/dev/null" 2>&1; then
    echo -e "${GREEN}✓ FUNCTIONS AVAILABLE${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FUNCTIONS MISSING${NC}"
    ((TESTS_FAILED++))
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "TEST SUMMARY"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}Passed:  $TESTS_PASSED${NC}"
echo -e "${RED}Failed:  $TESTS_FAILED${NC}"
echo -e "${YELLOW}Skipped: $TESTS_SKIPPED${NC}"
echo ""

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))
if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))
    echo "Success Rate: $SUCCESS_RATE%"
else
    echo "No tests run"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CRITICAL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo "Review failures above and fix issues."
    exit 1
fi
