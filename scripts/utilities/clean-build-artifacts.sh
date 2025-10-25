#!/bin/bash
# Clean up SynOS build artifacts that may be owned by root
# Usage: sudo ./scripts/clean-build-artifacts.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}✗ This script must be run as root${NC}"
    echo -e "${YELLOW}Usage: sudo $0${NC}"
    exit 1
fi

echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     SynOS Build Artifact Cleanup Script                 ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build/full-distribution"

# Check if build directory exists
if [ ! -d "$BUILD_DIR" ]; then
    echo -e "${YELLOW}ℹ${NC} No build directory found at: $BUILD_DIR"
    echo -e "${GREEN}✓${NC} Nothing to clean"
    exit 0
fi

echo -e "${YELLOW}📁 Build directory:${NC} $BUILD_DIR"
echo ""

# Show what will be removed
echo -e "${YELLOW}The following will be removed:${NC}"
if [ -d "$BUILD_DIR/chroot" ]; then
    SIZE=$(du -sh "$BUILD_DIR/chroot" 2>/dev/null | cut -f1)
    echo "  • chroot/ ($SIZE)"
fi
if [ -d "$BUILD_DIR/iso" ]; then
    SIZE=$(du -sh "$BUILD_DIR/iso" 2>/dev/null | cut -f1)
    echo "  • iso/ ($SIZE)"
fi
LOG_COUNT=$(find "$BUILD_DIR" -maxdepth 1 -name "*.log" -type f 2>/dev/null | wc -l)
if [ "$LOG_COUNT" -gt 0 ]; then
    echo "  • $LOG_COUNT log files"
fi
if [ -d "$BUILD_DIR/logs" ]; then
    COUNT=$(ls -1 "$BUILD_DIR/logs" 2>/dev/null | wc -l)
    echo "  • logs/ directory ($COUNT files)"
fi
if [ -d "$BUILD_DIR/binaries" ]; then
    echo "  • binaries/"
fi
if [ -d "$BUILD_DIR/tools" ]; then
    echo "  • tools/"
fi
echo ""

# Confirm
read -p "Continue with cleanup? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Cleanup cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}🧹 Cleaning up build artifacts...${NC}"

# Unmount any mounted filesystems in chroot
if [ -d "$BUILD_DIR/chroot" ]; then
    echo -e "${YELLOW}ℹ${NC} Unmounting chroot filesystems..."
    umount -l "$BUILD_DIR/chroot/sys" 2>/dev/null || true
    umount -l "$BUILD_DIR/chroot/proc" 2>/dev/null || true
    umount -l "$BUILD_DIR/chroot/dev/pts" 2>/dev/null || true
    umount -l "$BUILD_DIR/chroot/dev" 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Filesystems unmounted"
fi

# Remove build directory
echo -e "${YELLOW}ℹ${NC} Removing build directory..."
rm -rf "$BUILD_DIR"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Build directory removed successfully"
    echo ""
    echo -e "${GREEN}✨ Cleanup complete!${NC}"
    echo ""
    echo -e "You can now run a fresh build with:"
    echo -e "  ${YELLOW}sudo ./scripts/build-full-distribution.sh --clean --fresh${NC}"
else
    echo -e "${RED}✗${NC} Failed to remove some files"
    echo ""
    echo -e "${YELLOW}You may need to manually check:${NC}"
    echo -e "  ls -la $BUILD_DIR"
    exit 1
fi
