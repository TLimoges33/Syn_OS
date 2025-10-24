#!/bin/bash

###############################################################################
# Quick Validation Test for Build System v2.0
# Fast validation of all consolidated scripts
###############################################################################

set -euo pipefail

cd /home/diablorain/Syn_OS

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASS=0
FAIL=0

echo ""
echo "🧪 Build System v2.0 - Quick Validation"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Test each script
test_script() {
    local script="$1"
    local name=$(basename "$script")
    
    echo -n "Testing $name ... "
    
    if [ ! -f "$script" ]; then
        echo -e "${RED}NOT FOUND${NC}"
        ((FAIL++))
        return
    fi
    
    if [ ! -x "$script" ] && [[ "$script" != *"/lib/"* ]]; then
        echo -e "${YELLOW}NOT EXECUTABLE (fixing)${NC}"
        chmod +x "$script"
    fi
    
    if "$script" --help >/dev/null 2>&1 ||  [[ "$script" == *"/lib/"* ]]; then
        echo -e "${GREEN}✓ OK${NC}"
        ((PASS++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAIL++))
    fi
}

echo "Core Build Scripts:"
test_script "scripts/lib/build-common.sh"
test_script "scripts/build-kernel-only.sh"
test_script "scripts/build-iso.sh"
test_script "scripts/build-full-linux.sh"

echo ""
echo "Testing & Validation:"
test_script "scripts/testing/verify-build.sh"
test_script "scripts/testing/test-iso.sh"

echo ""
echo "Maintenance Tools:"
test_script "scripts/maintenance/clean-builds.sh"
test_script "scripts/maintenance/archive-old-isos.sh"

echo ""
echo "Specialized Tools:"
test_script "scripts/utilities/sign-iso.sh"
test_script "scripts/docker/build-docker.sh"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo -e "Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ All scripts validated successfully!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some scripts need attention${NC}"
    exit 1
fi
