#!/bin/bash
################################################################################
# SynOS v1.0 Clean Build Environment Script
# Removes old build artifacts to ensure clean v1.0 build
################################################################################

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "${PROJECT_ROOT}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     SynOS v1.0 Build Environment Cleanup                    ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

ITEMS_REMOVED=0

remove_dir() {
    local DIR="$1"
    local DESC="$2"
    
    if [ -d "$DIR" ]; then
        SIZE=$(du -sh "$DIR" 2>/dev/null | awk '{print $1}')
        echo -e "${YELLOW}🗑️  Removing $DESC: $DIR ($SIZE)${NC}"
        
        if rm -rf "$DIR" 2>/dev/null; then
            echo -e "${GREEN}✅ Removed successfully${NC}"
        else
            echo -e "${YELLOW}⚠️  Need sudo permissions...${NC}"
            sudo rm -rf "$DIR" && echo -e "${GREEN}✅ Removed with sudo${NC}"
        fi
        ((ITEMS_REMOVED++))
    else
        echo -e "${GREEN}✅ $DESC already clean${NC}"
    fi
}

remove_file() {
    local FILE="$1"
    local DESC="$2"
    
    if [ -f "$FILE" ]; then
        SIZE=$(du -sh "$FILE" 2>/dev/null | awk '{print $1}')
        echo -e "${YELLOW}🗑️  Removing $DESC: $FILE ($SIZE)${NC}"
        
        if rm -f "$FILE" 2>/dev/null; then
            echo -e "${GREEN}✅ Removed${NC}"
        else
            sudo rm -f "$FILE" && echo -e "${GREEN}✅ Removed with sudo${NC}"
        fi
        ((ITEMS_REMOVED++))
    fi
}

echo -e "${CYAN}[1/5] Cleaning old chroot directories...${NC}"
remove_dir "build/synos-ultimate/chroot" "Ultimate chroot"
echo ""

echo -e "${CYAN}[2/5] Cleaning old ISO files...${NC}"
remove_file "build/synos-ultimate.iso" "Ultimate ISO"
echo ""

echo -e "${CYAN}[3/5] Cleaning package caches...${NC}"
remove_dir "linux-distribution/SynOS-Linux-Builder/live-build-workspace/cache" "Live-build cache"
echo ""

echo -e "${CYAN}[4/5] Cleaning build logs...${NC}"
if ls build-log-*.log 1> /dev/null 2>&1; then
    mkdir -p build/archives/logs
    mv build-log-*.log build/archives/logs/ 2>/dev/null || true
    echo -e "${GREEN}✅ Archived to build/archives/logs/${NC}"
fi
echo ""

echo -e "${CYAN}[5/5] Verifying clean state...${NC}"
if [ ! -d "build/synos-ultimate/chroot" ] && [ ! -f "build/synos-ultimate.iso" ]; then
    echo -e "${GREEN}✅ All critical paths clean${NC}"
fi
echo ""

echo -e "${GREEN}🚀 Build environment ready for v1.0!${NC}"
echo -e "${CYAN}Items removed: ${ITEMS_REMOVED}${NC}"
echo ""
