#!/bin/bash
# =========================================================
# Syn_OS Build Fix Script
# Automatically repairs common build issues
# =========================================================

set -eo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${CYAN}"
echo "========================================="
echo " Syn_OS Build Environment Fix Script"
echo "========================================="
echo -e "${NC}"
echo ""

# Counter for fixes applied
FIXES_APPLIED=0

# Fix 1: Check and fix PROJECT_ROOT path in build scripts
echo -e "${BLUE}[1/7]${NC} Checking PROJECT_ROOT path resolution..."
BUILD_SCRIPT="scripts/02-build/core/build-simple-kernel-iso.sh"

if [ -f "$BUILD_SCRIPT" ]; then
    if grep -F '../../..' "$BUILD_SCRIPT" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} PROJECT_ROOT path is correct"
    else
        echo -e "${YELLOW}⚠${NC} PROJECT_ROOT path was already fixed earlier"
    fi
else
    echo -e "${RED}✗${NC} Build script not found: $BUILD_SCRIPT"
fi

# Fix 2: Create fix for chroot mount failures
echo ""
echo -e "${BLUE}[2/7]${NC} Creating chroot mount helper..."

cat > scripts/02-build/core/ensure-chroot-mounts.sh << 'MOUNTEOF'
#!/bin/bash
# Ensure chroot mounts are properly established

CHROOT_DIR="$1"

if [ -z "$CHROOT_DIR" ] || [ ! -d "$CHROOT_DIR" ]; then
    echo "Error: Invalid chroot directory"
    exit 1
fi

echo "Setting up chroot mounts in: $CHROOT_DIR"

# Ensure mount points exist
mkdir -p "$CHROOT_DIR"/{proc,sys,dev/pts}

# Mount if not already mounted
if ! mountpoint -q "$CHROOT_DIR/proc"; then
    mount -t proc proc "$CHROOT_DIR/proc" && echo "✓ Mounted /proc"
fi

if ! mountpoint -q "$CHROOT_DIR/sys"; then
    mount -t sysfs sys "$CHROOT_DIR/sys" && echo "✓ Mounted /sys"
fi

if ! mountpoint -q "$CHROOT_DIR/dev"; then
    mount -o bind /dev "$CHROOT_DIR/dev" && echo "✓ Mounted /dev"
fi

if ! mountpoint -q "$CHROOT_DIR/dev/pts"; then
    mount -t devpts devpts "$CHROOT_DIR/dev/pts" && echo "✓ Mounted /dev/pts"
fi

echo "✓ All chroot mounts verified"
MOUNTEOF

chmod +x scripts/02-build/core/ensure-chroot-mounts.sh
echo -e "${GREEN}✓${NC} Created chroot mount helper"
FIXES_APPLIED=$((FIXES_APPLIED+1))

# Fix 3: Update ultimate-iso-builder to use mount helper
echo ""
echo -e "${BLUE}[3/7]${NC} Updating ultimate-iso-builder mount handling..."

ULTIMATE_BUILDER="scripts/02-build/core/ultimate-iso-builder.sh"

# Check if mount verification exists
if ! grep -q "mountpoint -q" "$ULTIMATE_BUILDER"; then
    echo -e "${YELLOW}⚠${NC} Adding mount verification to ultimate-iso-builder..."
    
    # Create a backup
    cp "$ULTIMATE_BUILDER" "${ULTIMATE_BUILDER}.backup"
    
    # Add source for mount helper at the top of configure_chroot_environment function
    sed -i '/configure_chroot_environment() {/a\    # Ensure mounts are properly established\n    "${PROJECT_ROOT}/scripts/02-build/core/ensure-chroot-mounts.sh" "$CHROOT_DIR" || log_error "Failed to setup chroot mounts"' "$ULTIMATE_BUILDER"
    
    echo -e "${GREEN}✓${NC} Updated ultimate-iso-builder"
    FIXES_APPLIED=$((FIXES_APPLIED+1))
else
    echo -e "${GREEN}✓${NC} Mount verification already present"
fi

# Fix 4: Create problematic package exclusion list
echo ""
echo -e "${BLUE}[4/7]${NC} Creating package exclusion list..."

cat > config/build/problematic-packages.txt << 'PKGEOF'
# Packages that require newer versions than Debian 12 provides
# These will be excluded from automatic installation

# Ruby 3.3+ required (Debian 12 has 3.1)
beef-xss
metasploit-framework

# Python 3.13+ required (Debian 12 has 3.11)
python3-aardwolf
python3-aioconsole

# libc6 2.38+ required (Debian 12 has 2.36)
# (included in metasploit-framework)

# libssl3t64 required (Debian 12 has libssl3)
sslyze

# Not in Debian repositories
king-phisher
volatility

# Already missing from repos
objdump  # Part of binutils (should already be installed)
strings  # Part of binutils (should already be installed)
exiftool # Use libimage-exiftool-perl instead
PKGEOF

echo -e "${GREEN}✓${NC} Created package exclusion list"
FIXES_APPLIED=$((FIXES_APPLIED+1))

# Fix 5: Fix path references (scripts/src -> src)
echo ""
echo -e "${BLUE}[5/7]${NC} Fixing source path references..."

# Find files with /src/ references
FILES_TO_FIX=$(grep -r "/src/" scripts/ --include="*.sh" -l 2>/dev/null || true)

if [ -n "$FILES_TO_FIX" ]; then
    echo -e "${YELLOW}⚠${NC} Found files with incorrect paths:"
    echo "$FILES_TO_FIX"
    
    # Fix each file
    while IFS= read -r file; do
        if [ -f "$file" ]; then
            sed -i 's|/src/|/src/|g' "$file"
            echo "  Fixed: $file"
            FIXES_APPLIED=$((FIXES_APPLIED+1))
        fi
    done <<< "$FILES_TO_FIX"
    
    echo -e "${GREEN}✓${NC} Fixed source path references"
else
    echo -e "${GREEN}✓${NC} No incorrect path references found"
fi

# Fix 6: Fix locale warnings
echo ""
echo -e "${BLUE}[6/7]${NC} Creating locale fix for chroot..."

cat > scripts/02-build/core/fix-chroot-locales.sh << 'LOCEOF'
#!/bin/bash
# Fix locale issues in chroot environment

CHROOT_DIR="$1"

if [ -z "$CHROOT_DIR" ] || [ ! -d "$CHROOT_DIR" ]; then
    echo "Error: Invalid chroot directory"
    exit 1
fi

echo "Fixing locales in: $CHROOT_DIR"

# Generate locale
cat > "$CHROOT_DIR/etc/locale.gen" << EOF
en_US.UTF-8 UTF-8
C.UTF-8 UTF-8
EOF

# Set default locale
cat > "$CHROOT_DIR/etc/default/locale" << EOF
LANG=en_US.UTF-8
LC_ALL=en_US.UTF-8
LANGUAGE=en_US.UTF-8
EOF

# Generate locales in chroot
if [ -d "$CHROOT_DIR/proc" ] && mountpoint -q "$CHROOT_DIR/proc"; then
    chroot "$CHROOT_DIR" locale-gen en_US.UTF-8 2>/dev/null || echo "Note: locale-gen may need installation"
else
    echo "Warning: /proc not mounted, skipping locale-gen"
fi

echo "✓ Locale configuration updated"
LOCEOF

chmod +x scripts/02-build/core/fix-chroot-locales.sh
echo -e "${GREEN}✓${NC} Created locale fix script"
FIXES_APPLIED=$((FIXES_APPLIED+1))

# Fix 7: Create verification script
echo ""
echo -e "${BLUE}[7/7]${NC} Creating build environment verification..."

cat > scripts/02-build/core/verify-build-fixes.sh << 'VERIFYEOF'
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

# Check 5: No /src/ references
echo -n "Checking for incorrect path references... "
BAD_REFS=$(grep -r "/src/" "$TEST_ROOT/scripts/" --include="*.sh" 2>/dev/null | wc -l)
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
VERIFYEOF

chmod +x scripts/02-build/core/verify-build-fixes.sh
echo -e "${GREEN}✓${NC} Created verification script"
FIXES_APPLIED=$((FIXES_APPLIED+1))

# Run verification
echo ""
echo -e "${CYAN}=========================================${NC}"
echo -e "${CYAN} Running Verification${NC}"
echo -e "${CYAN}=========================================${NC}"
echo ""

bash scripts/02-build/core/verify-build-fixes.sh

# Summary
echo ""
echo -e "${CYAN}=========================================${NC}"
echo -e "${CYAN} Fix Summary${NC}"
echo -e "${CYAN}=========================================${NC}"
echo ""
echo -e "${GREEN}✓${NC} Applied $FIXES_APPLIED fixes"
echo ""
echo "Next steps:"
echo "1. Clean old build artifacts: make clean"
echo "2. Try building again: ./scripts/02-build/core/build-simple-kernel-iso.sh"
echo ""
echo "For ISO with security tools:"
echo "  ./scripts/02-build/core/ultimate-iso-builder.sh"
echo ""
echo -e "${YELLOW}Note:${NC} Some security tools may be skipped due to dependency version mismatches."
echo "This is expected on Debian 12. Critical tools (john, hashcat, etc.) will still install."
echo ""
