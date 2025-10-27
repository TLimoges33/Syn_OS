#!/bin/bash
################################################################################
# SynOS - Complete Clean and Fix for Fresh Build
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  SynOS - Complete Clean & Fix for Fresh Build ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"
echo ""

CHROOT_DIR="../build/full-distribution/chroot"
BUILD_DIR="../build/full-distribution"

# Step 1: Unmount any chroot filesystems
echo -e "${YELLOW}→${NC} Step 1: Unmounting chroot filesystems..."
if mount | grep -q "$CHROOT_DIR"; then
    sudo umount -R "$CHROOT_DIR/dev" 2>/dev/null || true
    sudo umount -R "$CHROOT_DIR/proc" 2>/dev/null || true
    sudo umount -R "$CHROOT_DIR/sys" 2>/dev/null || true
    sudo umount -R "$CHROOT_DIR/dev/pts" 2>/dev/null || true
    echo -e "${GREEN}  ✓ Unmounted${NC}"
else
    echo -e "${GREEN}  ✓ No mounts found${NC}"
fi

# Step 2: Remove package locks
echo -e "${YELLOW}→${NC} Step 2: Removing package locks..."
if [ -d "$CHROOT_DIR" ]; then
    sudo rm -f "$CHROOT_DIR/var/lib/dpkg/lock" 2>/dev/null || true
    sudo rm -f "$CHROOT_DIR/var/lib/dpkg/lock-frontend" 2>/dev/null || true
    sudo rm -f "$CHROOT_DIR/var/cache/apt/archives/lock" 2>/dev/null || true
    sudo rm -f "$CHROOT_DIR/var/lib/apt/lists/lock" 2>/dev/null || true
    echo -e "${GREEN}  ✓ Locks removed${NC}"
else
    echo -e "${GREEN}  ✓ No chroot directory yet${NC}"
fi

# Step 3: Kill any zombie build processes
echo -e "${YELLOW}→${NC} Step 3: Killing zombie build processes..."
pkill -9 -f 'build-full-distribution.sh' 2>/dev/null || true
sleep 1
echo -e "${GREEN}  ✓ Processes killed${NC}"

# Step 4: Remove old build directory
echo -e "${YELLOW}→${NC} Step 4: Cleaning old build directory..."
if [ -d "$BUILD_DIR" ]; then
    echo -e "${YELLOW}  → Removing $BUILD_DIR ...${NC}"
    sudo rm -rf "$BUILD_DIR" 2>/dev/null || true
    echo -e "${GREEN}  ✓ Removed${NC}"
else
    echo -e "${GREEN}  ✓ No old build directory${NC}"
fi

# Step 5: Remove checkpoints and logs
echo -e "${YELLOW}→${NC} Step 5: Removing checkpoints and old logs..."
rm -f ../build/.build_checkpoint 2>/dev/null || true
rm -f ../build/.stage_* 2>/dev/null || true
rm -f ../build/*.log ../build/*.log.gz 2>/dev/null || true
echo -e "${GREEN}  ✓ Checkpoints and logs cleared${NC}"

# Step 6: Create fresh build directory
echo -e "${YELLOW}→${NC} Step 6: Creating fresh build directory..."
mkdir -p ../build
echo -e "${GREEN}  ✓ Fresh build directory created${NC}"

# Step 7: Verify system resources
echo -e "${YELLOW}→${NC} Step 7: Checking system resources..."
FREE_MEM=$(free -g | awk 'NR==2 {print $7}')
FREE_DISK=$(df -BG ../build | awk 'NR==2 {print $4}' | sed 's/G//')
echo -e "${BLUE}  ℹ Memory available: ${FREE_MEM}GB${NC}"
echo -e "${BLUE}  ℹ Disk available: ${FREE_DISK}GB${NC}"

if [ "$FREE_MEM" -lt 3 ]; then
    echo -e "${RED}  ✗ Warning: Low memory (${FREE_MEM}GB). Recommend 4GB+${NC}"
fi

if [ "$FREE_DISK" -lt 50 ]; then
    echo -e "${RED}  ✗ Warning: Low disk space (${FREE_DISK}GB). Need 50GB+${NC}"
else
    echo -e "${GREEN}  ✓ Resources sufficient${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Clean complete! Ready for fresh build.${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo -e "  ${GREEN}1.${NC} Verify script fix: ${BLUE}grep -A 5 'Initialize counter variables' build-full-distribution.sh${NC}"
echo -e "  ${GREEN}2.${NC} Start fresh build: ${BLUE}./build-full-distribution.sh --fresh --no-parallel${NC}"
echo -e "  ${GREEN}3.${NC} Monitor in another terminal: ${BLUE}tail -f ../build/full-distribution/build-*.log${NC}"
echo ""
echo "Build will take 2-4 hours. Be patient! ☕"
echo ""
