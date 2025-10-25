#!/bin/bash
################################################################################
# SynOS v1.0 Pre-Build Verification Script
# Checks for broken references, missing files, and build readiness
################################################################################

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "${PROJECT_ROOT}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         SynOS v1.0 Pre-Build Verification                    ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

################################################################################
# 1. Check Build Script Paths
################################################################################

echo -e "${CYAN}[1/8] Checking build script path references...${NC}"

# Check for old path references
OLD_PATH_REFS=$(grep -r "scripts/build/synos-ultimate" scripts/ 2>/dev/null | grep -v "Binary file" | grep -v ".git" || true)
OLD_PATH_COUNT=$(echo "$OLD_PATH_REFS" | grep -c . || true)

if [ -n "$OLD_PATH_REFS" ] && [ "$OLD_PATH_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Found $OLD_PATH_COUNT old path reference(s):${NC}"
    while IFS= read -r line; do
        echo "   $line"
    done <<< "$OLD_PATH_REFS"
    WARNINGS=$((WARNINGS + OLD_PATH_COUNT))
else
    echo -e "${GREEN}✅ No old path references found${NC}"
fi

################################################################################
# 2. Verify Critical Directories Exist
################################################################################

echo -e "${CYAN}[2/8] Verifying directory structure...${NC}"

CRITICAL_DIRS=(
    "build"
    "scripts/02-build/core"
    "src/kernel"
    "src/ai-engine"
    "core/security"
    "docs"
    "assets/branding"
)

for dir in "${CRITICAL_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✅ $dir${NC}"
    else
        echo -e "${RED}❌ Missing: $dir${NC}"
        ((ERRORS++))
    fi
done

################################################################################
# 3. Verify Main Build Script
################################################################################

echo -e "${CYAN}[3/8] Verifying main build script...${NC}"

BUILD_SCRIPT="scripts/02-build/core/ultimate-final-master-developer-v1.0-build.sh"

if [ ! -f "$BUILD_SCRIPT" ]; then
    echo -e "${RED}❌ Build script not found: $BUILD_SCRIPT${NC}"
    ((ERRORS++))
else
    echo -e "${GREEN}✅ Build script exists${NC}"

    # Check for stage functions
    if grep -q "stage_initialize()" "$BUILD_SCRIPT"; then
        echo -e "${GREEN}✅ Build stage functions defined${NC}"
    else
        echo -e "${RED}❌ Build stage functions missing${NC}"
        ((ERRORS++))
    fi

    # Check if audio function is called
    if grep -q "install_audio_enhancements$" "$BUILD_SCRIPT"; then
        echo -e "${GREEN}✅ Audio enhancement function called in main()${NC}"
    else
        echo -e "${RED}❌ Audio enhancement function not called${NC}"
        ((ERRORS++))
    fi

    # Check for correct build path
    if grep -q 'BUILD_BASE="build/synos-ultimate"' "$BUILD_SCRIPT"; then
        echo -e "${GREEN}✅ Correct build path configured${NC}"
    else
        echo -e "${RED}❌ Incorrect build path in script${NC}"
        ((ERRORS++))
    fi
fi

################################################################################
# 4. Check for Required Tools
################################################################################

echo -e "${CYAN}[4/8] Checking required build tools...${NC}"

REQUIRED_TOOLS=(
    "debootstrap"
    "mksquashfs"
    "xorriso"
    "grub-mkrescue"
    "sox"
    "cargo"
)

for tool in "${REQUIRED_TOOLS[@]}"; do
    if command -v "$tool" &> /dev/null; then
        echo -e "${GREEN}✅ $tool${NC}"
    else
        echo -e "${YELLOW}⚠️  Missing (optional): $tool${NC}"
        ((WARNINGS++))
    fi
done

################################################################################
# 5. Verify Source Code Directories
################################################################################

echo -e "${CYAN}[5/8] Verifying source code structure...${NC}"

SOURCE_DIRS=(
    "src/kernel"
    "src/ai-engine"
    "src/ai-runtime"
    "src/security"
    "core/security"
    "core/ai"
)

for dir in "${SOURCE_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        FILE_COUNT=$(find "$dir" -name "*.rs" -o -name "*.toml" | wc -l)
        echo -e "${GREEN}✅ $dir ($FILE_COUNT files)${NC}"
    else
        echo -e "${RED}❌ Missing: $dir${NC}"
        ((ERRORS++))
    fi
done

################################################################################
# 6. Check Documentation
################################################################################

echo -e "${CYAN}[6/8] Verifying documentation...${NC}"

CRITICAL_DOCS=(
    "README.md"
    "CLAUDE.md"
    "BUILD_V1.0_NOW.md"
    "docs/README.md"
    "docs/03-build/ultimate-build-guide.md"
)

for doc in "${CRITICAL_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo -e "${GREEN}✅ $doc${NC}"
    else
        echo -e "${YELLOW}⚠️  Missing: $doc${NC}"
        ((WARNINGS++))
    fi
done

################################################################################
# 7. Check Disk Space & Memory
################################################################################

echo -e "${CYAN}[7/10] Checking system resources...${NC}"

AVAILABLE_GB=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')

if [ "$AVAILABLE_GB" -ge 50 ]; then
    echo -e "${GREEN}✅ Excellent disk space: ${AVAILABLE_GB}GB available${NC}"
elif [ "$AVAILABLE_GB" -ge 30 ]; then
    echo -e "${GREEN}✅ Sufficient disk space: ${AVAILABLE_GB}GB available${NC}"
elif [ "$AVAILABLE_GB" -ge 20 ]; then
    echo -e "${YELLOW}⚠️  Low disk space: ${AVAILABLE_GB}GB available (50GB+ recommended)${NC}"
    ((WARNINGS++))
else
    echo -e "${RED}❌ Insufficient disk space: ${AVAILABLE_GB}GB available (30GB minimum)${NC}"
    ((ERRORS++))
fi

# Check available memory
AVAILABLE_RAM_GB=$(free -g | awk '/^Mem:/{print $7}')
if [ "$AVAILABLE_RAM_GB" -ge 8 ]; then
    echo -e "${GREEN}✅ Sufficient memory: ${AVAILABLE_RAM_GB}GB free${NC}"
elif [ "$AVAILABLE_RAM_GB" -ge 4 ]; then
    echo -e "${YELLOW}⚠️  Limited memory: ${AVAILABLE_RAM_GB}GB free (8GB+ recommended)${NC}"
    ((WARNINGS++))
else
    echo -e "${YELLOW}⚠️  Low memory: ${AVAILABLE_RAM_GB}GB free (may cause issues)${NC}"
    ((WARNINGS++))
fi

################################################################################
# 8. Check Network Connectivity
################################################################################

echo -e "${CYAN}[8/10] Checking network connectivity to repositories...${NC}"

# Check Debian repo
if ping -c 1 -W 2 deb.debian.org &> /dev/null; then
    echo -e "${GREEN}✅ Debian repository reachable${NC}"
else
    echo -e "${YELLOW}⚠️  Cannot reach deb.debian.org${NC}"
    ((WARNINGS++))
fi

# Check ParrotOS repo
if ping -c 1 -W 2 deb.parrot.sh &> /dev/null; then
    echo -e "${GREEN}✅ ParrotOS repository reachable${NC}"
else
    echo -e "${YELLOW}⚠️  Cannot reach deb.parrot.sh${NC}"
    ((WARNINGS++))
fi

# Check Kali repo
if ping -c 1 -W 2 http.kali.org &> /dev/null; then
    echo -e "${GREEN}✅ Kali repository reachable${NC}"
else
    echo -e "${YELLOW}⚠️  Cannot reach http.kali.org${NC}"
    ((WARNINGS++))
fi

################################################################################
# 9. Check for Old Build Artifacts
################################################################################

echo -e "${CYAN}[9/10] Checking for conflicting build artifacts...${NC}"

OLD_CHROOT="build/synos-ultimate/chroot"
OLD_ISO="build/synos-ultimate.iso"

if [ -d "$OLD_CHROOT" ]; then
    CHROOT_SIZE=$(du -sh "$OLD_CHROOT" 2>/dev/null | awk '{print $1}')
    echo -e "${YELLOW}⚠️  Old chroot exists: $OLD_CHROOT ($CHROOT_SIZE)${NC}"
    echo -e "${YELLOW}   Consider: sudo rm -rf $OLD_CHROOT${NC}"
    ((WARNINGS++))
else
    echo -e "${GREEN}✅ No old chroot directory${NC}"
fi

if [ -f "$OLD_ISO" ]; then
    ISO_SIZE=$(du -sh "$OLD_ISO" 2>/dev/null | awk '{print $1}')
    echo -e "${YELLOW}⚠️  Old ISO exists: $OLD_ISO ($ISO_SIZE)${NC}"
    echo -e "${YELLOW}   Will be overwritten by new build${NC}"
    ((WARNINGS++))
else
    echo -e "${GREEN}✅ No old ISO file${NC}"
fi

################################################################################
# 10. Check for Broken Symlinks
################################################################################

echo -e "${CYAN}[10/10] Checking for broken symlinks...${NC}"

BROKEN_LINKS=$(find . -type l ! -exec test -e {} \; -print 2>/dev/null || true)
BROKEN_COUNT=$(echo "$BROKEN_LINKS" | grep -c . || true)

if [ -n "$BROKEN_LINKS" ] && [ "$BROKEN_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Found $BROKEN_COUNT broken symlink(s):${NC}"
    while IFS= read -r link; do
        echo "   $link"
    done <<< "$BROKEN_LINKS"
    WARNINGS=$((WARNINGS + BROKEN_COUNT))
else
    echo -e "${GREEN}✅ No broken symlinks found${NC}"
fi

################################################################################
# Summary
################################################################################

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                    Verification Summary                      ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED - READY FOR v1.0 BUILD!${NC}"
    echo ""
    echo -e "${CYAN}To start the build:${NC}"
    echo "  cd /home/diablorain/Syn_OS"
    echo "  sudo ./scripts/02-build/core/build-synos-ultimate-iso.sh 2>&1 | tee build-log-\$(date +%Y%m%d-%H%M%S).log"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  ${WARNINGS} WARNINGS - Build may proceed with caution${NC}"
    echo ""
    echo -e "${CYAN}To start the build anyway:${NC}"
    echo "  cd /home/diablorain/Syn_OS"
    echo "  sudo ./scripts/02-build/core/build-synos-ultimate-iso.sh 2>&1 | tee build-log-\$(date +%Y%m%d-%H%M%S).log"
    echo ""
    exit 0
else
    echo -e "${RED}❌ ${ERRORS} ERRORS, ${WARNINGS} WARNINGS - Build NOT recommended${NC}"
    echo ""
    echo -e "${YELLOW}Please fix errors before attempting build.${NC}"
    echo ""
    exit 1
fi
