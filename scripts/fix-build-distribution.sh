#!/bin/bash
################################################################################
# SynOS Build Distribution - Diagnostic & Fix Tool
#
# This script diagnoses and fixes common issues with build-full-distribution.sh
#
# Usage:
#   ./fix-build-distribution.sh          # Run diagnostics
#   ./fix-build-distribution.sh --fix    # Apply all fixes
#   ./fix-build-distribution.sh --clean  # Clean and restart
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_SCRIPT="$SCRIPT_DIR/build-full-distribution.sh"
BUILD_DIR="$SCRIPT_DIR/../build"
CHROOT_DIR="$BUILD_DIR/full-distribution/chroot"

# Counters
ISSUES_FOUND=0
FIXES_APPLIED=0

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}  SynOS Build Diagnostic Tool  ${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Function: Check issue
check_issue() {
    local issue_name="$1"
    local check_command="$2"

    if eval "$check_command"; then
        echo -e "${GREEN}✓${NC} $issue_name"
        return 0
    else
        echo -e "${RED}✗${NC} $issue_name"
        ((ISSUES_FOUND++))
        return 1
    fi
}

# Function: Apply fix
apply_fix() {
    local fix_name="$1"
    local fix_command="$2"

    echo -e "${YELLOW}→${NC} Applying: $fix_name"
    if eval "$fix_command"; then
        echo -e "${GREEN}  ✓ Fixed${NC}"
        ((FIXES_APPLIED++))
        return 0
    else
        echo -e "${RED}  ✗ Failed${NC}"
        return 1
    fi
}

################################################################################
# DIAGNOSTIC CHECKS
################################################################################

echo "Running diagnostics..."
echo ""

# 1. Check if build script exists
check_issue "Build script exists" "[ -f '$BUILD_SCRIPT' ]" || {
    echo -e "${RED}ERROR: build-full-distribution.sh not found!${NC}"
    exit 1
}

# 2. Check if build script is executable
check_issue "Build script is executable" "[ -x '$BUILD_SCRIPT' ]" || {
    if [ "$1" = "--fix" ]; then
        apply_fix "Make build script executable" "chmod +x '$BUILD_SCRIPT'"
    fi
}

# 3. Check for required commands
REQUIRED_CMDS="debootstrap sudo chroot xorriso mksquashfs"
for cmd in $REQUIRED_CMDS; do
    check_issue "Command available: $cmd" "command -v $cmd >/dev/null 2>&1" || {
        echo -e "${YELLOW}  Install with: sudo apt install ${cmd}${NC}"
    }
done

# 4. Check disk space
FREE_SPACE_GB=$(df -BG "$BUILD_DIR" 2>/dev/null | awk 'NR==2 {print $4}' | sed 's/G//' || echo "0")
check_issue "Sufficient disk space (>50GB available)" "[ $FREE_SPACE_GB -gt 50 ]" || {
    echo -e "${YELLOW}  Warning: Only ${FREE_SPACE_GB}GB available. Need 50GB+ for full build.${NC}"
}

# 5. Check memory
FREE_MEM_GB=$(free -g | awk 'NR==2 {print $7}')
check_issue "Sufficient memory (>4GB free)" "[ $FREE_MEM_GB -gt 4 ]" || {
    echo -e "${YELLOW}  Warning: Only ${FREE_MEM_GB}GB memory available. Recommend 8GB+${NC}"
}

# 6. Check for stale chroot mounts
check_issue "No stale chroot mounts" "! mount | grep -q '$CHROOT_DIR'" || {
    if [ "$1" = "--fix" ]; then
        apply_fix "Unmount stale chroot filesystems" "
            sudo umount -R '$CHROOT_DIR/dev' 2>/dev/null || true
            sudo umount -R '$CHROOT_DIR/proc' 2>/dev/null || true
            sudo umount -R '$CHROOT_DIR/sys' 2>/dev/null || true
            sudo umount -R '$CHROOT_DIR' 2>/dev/null || true
        "
    else
        echo -e "${YELLOW}  Run with --fix to unmount${NC}"
    fi
}

# 7. Check for locked dpkg/apt in chroot
if [ -d "$CHROOT_DIR" ]; then
    check_issue "No locked package managers" "! [ -f '$CHROOT_DIR/var/lib/dpkg/lock' ]" || {
        if [ "$1" = "--fix" ]; then
            apply_fix "Remove dpkg/apt locks" "
                sudo rm -f '$CHROOT_DIR/var/lib/dpkg/lock'
                sudo rm -f '$CHROOT_DIR/var/lib/dpkg/lock-frontend'
                sudo rm -f '$CHROOT_DIR/var/cache/apt/archives/lock'
                sudo rm -f '$CHROOT_DIR/var/lib/apt/lists/lock'
            "
        fi
    }
fi

# 8. Check for zombie processes
check_issue "No zombie build processes" "! pgrep -f 'build-full-distribution.sh' >/dev/null 2>&1" || {
    if [ "$1" = "--fix" ]; then
        apply_fix "Kill zombie build processes" "
            pkill -9 -f 'build-full-distribution.sh' 2>/dev/null || true
            sleep 2
        "
    fi
}

# 9. Check build log for errors
if [ -f "$BUILD_DIR/build-full-distribution.log" ]; then
    LAST_ERROR=$(tail -100 "$BUILD_DIR/build-full-distribution.log" | grep -i "error\|fatal\|failed" | tail -1)
    if [ -n "$LAST_ERROR" ]; then
        ((ISSUES_FOUND++))
        echo -e "${RED}✗${NC} Previous build had errors"
        echo -e "${YELLOW}  Last error: ${LAST_ERROR:0:100}${NC}"
    else
        echo -e "${GREEN}✓${NC} No errors in build log"
    fi
fi

# 10. Check checkpoint file
if [ -f "$BUILD_DIR/.build_checkpoint" ]; then
    LAST_CHECKPOINT=$(cat "$BUILD_DIR/.build_checkpoint" 2>/dev/null || echo "unknown")
    echo -e "${BLUE}ℹ${NC}  Build checkpoint exists: $LAST_CHECKPOINT"
    echo -e "${YELLOW}  Resume from checkpoint or use --fresh to restart${NC}"
fi

################################################################################
# SUMMARY
################################################################################

echo ""
echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}  Diagnostic Summary  ${NC}"
echo -e "${BLUE}=================================${NC}"

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✓ No issues found! Ready to build.${NC}"
else
    echo -e "${YELLOW}⚠ Found $ISSUES_FOUND issue(s)${NC}"
    if [ "$1" != "--fix" ]; then
        echo ""
        echo "Run with --fix to automatically fix issues:"
        echo -e "  ${BLUE}$0 --fix${NC}"
    fi
fi

if [ "$1" = "--fix" ] && [ $FIXES_APPLIED -gt 0 ]; then
    echo -e "${GREEN}✓ Applied $FIXES_APPLIED fix(es)${NC}"
fi

################################################################################
# FIX OPTIONS
################################################################################

if [ "$1" = "--fix" ]; then
    echo ""
    echo "Additional fix options applied:"

    # Fix 1: Ensure proper permissions
    echo -e "${YELLOW}→${NC} Fixing permissions..."
    sudo chown -R $(whoami):$(whoami) "$BUILD_DIR" 2>/dev/null || true
    echo -e "${GREEN}  ✓ Permissions fixed${NC}"

    # Fix 2: Clean temporary files
    echo -e "${YELLOW}→${NC} Cleaning temporary files..."
    rm -f /tmp/synos-* 2>/dev/null || true
    echo -e "${GREEN}  ✓ Temporary files cleaned${NC}"

    # Fix 3: Reset apt cache in chroot
    if [ -d "$CHROOT_DIR/var/cache/apt" ]; then
        echo -e "${YELLOW}→${NC} Clearing apt cache in chroot..."
        sudo rm -rf "$CHROOT_DIR/var/cache/apt/archives/*.deb" 2>/dev/null || true
        echo -e "${GREEN}  ✓ Apt cache cleared${NC}"
    fi

    echo ""
    echo -e "${GREEN}✓ All fixes applied!${NC}"
    echo ""
    echo "You can now run:"
    echo -e "  ${BLUE}cd $(dirname $BUILD_SCRIPT)${NC}"
    echo -e "  ${BLUE}./$(basename $BUILD_SCRIPT)${NC}"

elif [ "$1" = "--clean" ]; then
    echo ""
    echo -e "${YELLOW}⚠ WARNING: This will delete all build artifacts!${NC}"
    echo -e "  - Build directory: $BUILD_DIR"
    echo -e "  - All checkpoints and logs"
    echo ""
    read -p "Are you sure? (yes/no): " -r
    if [[ $REPLY == "yes" ]]; then
        echo -e "${YELLOW}→${NC} Cleaning build directory..."

        # Unmount any chroot filesystems
        sudo umount -R "$CHROOT_DIR/dev" 2>/dev/null || true
        sudo umount -R "$CHROOT_DIR/proc" 2>/dev/null || true
        sudo umount -R "$CHROOT_DIR/sys" 2>/dev/null || true

        # Remove build directory
        sudo rm -rf "$BUILD_DIR/full-distribution" 2>/dev/null || true
        rm -f "$BUILD_DIR"/*.log "$BUILD_DIR"/*.log.gz 2>/dev/null || true
        rm -f "$BUILD_DIR/.build_checkpoint" 2>/dev/null || true
        rm -f "$BUILD_DIR"/.stage_* 2>/dev/null || true

        echo -e "${GREEN}✓ Build directory cleaned!${NC}"
        echo ""
        echo "Ready for a fresh build:"
        echo -e "  ${BLUE}./$(basename $BUILD_SCRIPT) --fresh${NC}"
    else
        echo "Clean cancelled."
    fi
fi

################################################################################
# COMMON ISSUES & SOLUTIONS
################################################################################

if [ $ISSUES_FOUND -gt 0 ] && [ "$1" != "--fix" ]; then
    echo ""
    echo -e "${BLUE}=================================${NC}"
    echo -e "${BLUE}  Common Issues & Solutions  ${NC}"
    echo -e "${BLUE}=================================${NC}"
    echo ""

    cat << 'TIPS'
1. Build fails during debootstrap:
   → Check internet connection
   → Try: --clean then rebuild
   → Use different Debian mirror

2. Build fails during apt update:
   → Repository might be temporarily down
   → Check: sudo chroot /path/to/chroot apt update
   → Try: --fresh to skip checkpoint

3. Build hangs during package installation:
   → Check for stale mounts: mount | grep chroot
   → Kill zombie processes: pkill -f build-full
   → Run: ./fix-build-distribution.sh --fix

4. Out of disk space:
   → Clean old builds: ./fix-build-distribution.sh --clean
   → Free up space: sudo apt clean
   → Check: df -h

5. Permission errors:
   → Fix ownership: sudo chown -R $USER build/
   → Fix script: chmod +x build-full-distribution.sh

6. Build fails at specific phase:
   → Check build log: tail -100 build/*.log
   → Resume from checkpoint (automatic)
   → Skip phase: edit checkpoint file

Run diagnostic with fixes:
  ./fix-build-distribution.sh --fix

Clean and restart:
  ./fix-build-distribution.sh --clean
TIPS
fi

echo ""
exit $([ $ISSUES_FOUND -eq 0 ] && echo 0 || echo 1)
