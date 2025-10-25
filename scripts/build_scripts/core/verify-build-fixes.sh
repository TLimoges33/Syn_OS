#!/bin/bash
# Verify that build fixes have been applied correctly

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================="
echo " Build Environment Verification"
echo "========================================="
echo ""

ISSUES=0

# Check 1: PROJECT_ROOT resolution
echo -n "Checking PROJECT_ROOT resolution... "
cd "$(dirname "$0")"
TEST_ROOT="$(cd ../../.. && pwd)"
if [[ "$TEST_ROOT" =~ Syn_OS$ ]]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC} (resolves to: $TEST_ROOT)"
    ((ISSUES++))
fi

# Check 2: ALFRED daemon exists
echo -n "Checking ALFRED daemon... "
if [ -f "$TEST_ROOT/src/ai/alfred/alfred-daemon.py" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC} (not found)"
    ((ISSUES++))
fi

# Check 3: Kernel source exists
echo -n "Checking kernel source... "
if [ -f "$TEST_ROOT/src/kernel/Cargo.toml" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC} (not found)"
    ((ISSUES++))
fi

# Check 4: Mount helper exists
echo -n "Checking chroot mount helper... "
if [ -x "$TEST_ROOT/scripts/02-build/core/ensure-chroot-mounts.sh" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC} (not found or not executable)"
    ((ISSUES++))
fi

# Check 5: No /scripts/src/ references
echo -n "Checking for incorrect path references... "
BAD_REFS=$(grep -r "/scripts/src/" "$TEST_ROOT/scripts/" --include="*.sh" 2>/dev/null | wc -l)
if [ "$BAD_REFS" -eq 0 ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC} (found $BAD_REFS)"
    ((ISSUES++))
fi

echo ""
echo "========================================="
if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Found $ISSUES issue(s)${NC}"
    exit 1
fi
