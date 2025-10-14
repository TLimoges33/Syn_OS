#!/bin/bash

###############################################################################
# SynOS - Optimize Chroot for ISO Build
# Removes bloat while preserving all functionality
###############################################################################

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if chroot directory is provided
if [ -z "$1" ]; then
    echo -e "${RED}Usage: $0 <chroot_directory>${NC}"
    echo "Example: $0 /home/diablorain/Syn_OS/build/synos-v1.0/work/chroot"
    exit 1
fi

CHROOT_DIR="$1"

# Verify chroot directory exists
if [ ! -d "$CHROOT_DIR" ]; then
    echo -e "${RED}[✗] Chroot directory not found: $CHROOT_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     SynOS - Chroot Optimization for ISO Build               ║"
echo "║     Removing bloat while preserving functionality           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Record starting size
echo -e "${YELLOW}[→] Calculating starting size...${NC}"
START_SIZE=$(sudo du -sb "$CHROOT_DIR" 2>/dev/null | cut -f1)
START_SIZE_H=$(sudo du -sh "$CHROOT_DIR" 2>/dev/null | cut -f1)
echo -e "${BLUE}Starting size: $START_SIZE_H${NC}"
echo ""

###############################################################################
# Optimization Step 1: Remove Git History
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}[1/5] Removing Git history from GitHub repos...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

GIT_DIRS=$(sudo find "$CHROOT_DIR/opt/github-repos" -type d -name '.git' 2>/dev/null | wc -l)
echo -e "${BLUE}Found $GIT_DIRS .git directories${NC}"

if [ "$GIT_DIRS" -gt 0 ]; then
    echo -e "${YELLOW}Removing Git history...${NC}"
    sudo find "$CHROOT_DIR/opt/github-repos" -type d -name '.git' -prune -exec rm -rf {} + 2>/dev/null || true
    echo -e "${GREEN}[✓] Git history removed${NC}"

    # Calculate savings
    AFTER_GIT=$(sudo du -sb "$CHROOT_DIR" 2>/dev/null | cut -f1)
    GIT_SAVED=$((START_SIZE - AFTER_GIT))
    GIT_SAVED_H=$(numfmt --to=iec --suffix=B $GIT_SAVED 2>/dev/null || echo "$GIT_SAVED bytes")
    echo -e "${GREEN}   Saved: $GIT_SAVED_H${NC}"
else
    echo -e "${GREEN}[✓] No Git history found${NC}"
fi
echo ""

###############################################################################
# Optimization Step 2: Remove Non-English Locales
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}[2/5] Removing non-English locales...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

if [ -d "$CHROOT_DIR/usr/share/locale" ]; then
    LOCALE_COUNT=$(sudo find "$CHROOT_DIR/usr/share/locale" -mindepth 1 -maxdepth 1 ! -name 'en*' 2>/dev/null | wc -l)
    echo -e "${BLUE}Found $LOCALE_COUNT non-English locale directories${NC}"

    if [ "$LOCALE_COUNT" -gt 0 ]; then
        BEFORE_LOCALE=$(sudo du -sb "$CHROOT_DIR" 2>/dev/null | cut -f1)
        sudo find "$CHROOT_DIR/usr/share/locale" -mindepth 1 -maxdepth 1 ! -name 'en*' -exec rm -rf {} + 2>/dev/null || true
        AFTER_LOCALE=$(sudo du -sb "$CHROOT_DIR" 2>/dev/null | cut -f1)
        LOCALE_SAVED=$((BEFORE_LOCALE - AFTER_LOCALE))
        LOCALE_SAVED_H=$(numfmt --to=iec --suffix=B $LOCALE_SAVED 2>/dev/null || echo "$LOCALE_SAVED bytes")
        echo -e "${GREEN}[✓] Non-English locales removed${NC}"
        echo -e "${GREEN}   Saved: $LOCALE_SAVED_H${NC}"
    fi
else
    echo -e "${GREEN}[✓] No locale directory found${NC}"
fi
echo ""

###############################################################################
# Optimization Step 3: Clean Package Caches
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}[3/5] Cleaning package caches...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

BEFORE_CACHE=$(sudo du -sb "$CHROOT_DIR" 2>/dev/null | cut -f1)

# APT cache
if [ -d "$CHROOT_DIR/var/cache/apt/archives" ]; then
    APT_FILES=$(sudo find "$CHROOT_DIR/var/cache/apt/archives" -name "*.deb" 2>/dev/null | wc -l)
    if [ "$APT_FILES" -gt 0 ]; then
        echo -e "${YELLOW}Removing $APT_FILES .deb files...${NC}"
        sudo rm -rf "$CHROOT_DIR/var/cache/apt/archives"/*.deb 2>/dev/null || true
        echo -e "${GREEN}[✓] APT cache cleaned${NC}"
    fi
fi

# Root cache
if [ -d "$CHROOT_DIR/root/.cache" ]; then
    sudo rm -rf "$CHROOT_DIR/root/.cache"/* 2>/dev/null || true
    echo -e "${GREEN}[✓] Root cache cleaned${NC}"
fi

# Python cache
if [ -d "$CHROOT_DIR/root/.local/share/pip" ]; then
    sudo rm -rf "$CHROOT_DIR/root/.local/share/pip"/* 2>/dev/null || true
    echo -e "${GREEN}[✓] Python cache cleaned${NC}"
fi

AFTER_CACHE=$(sudo du -sb "$CHROOT_DIR" 2>/dev/null | cut -f1)
CACHE_SAVED=$((BEFORE_CACHE - AFTER_CACHE))
CACHE_SAVED_H=$(numfmt --to=iec --suffix=B $CACHE_SAVED 2>/dev/null || echo "$CACHE_SAVED bytes")
echo -e "${GREEN}   Saved: $CACHE_SAVED_H${NC}"
echo ""

###############################################################################
# Optimization Step 4: Truncate Logs
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}[4/5] Truncating log files...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

BEFORE_LOGS=$(sudo du -sb "$CHROOT_DIR" 2>/dev/null | cut -f1)

if [ -d "$CHROOT_DIR/var/log" ]; then
    LOG_COUNT=$(sudo find "$CHROOT_DIR/var/log" -type f -name "*.log" 2>/dev/null | wc -l)
    echo -e "${BLUE}Found $LOG_COUNT log files${NC}"

    if [ "$LOG_COUNT" -gt 0 ]; then
        sudo find "$CHROOT_DIR/var/log" -type f -name "*.log" -exec truncate -s 0 {} \; 2>/dev/null || true
        echo -e "${GREEN}[✓] Log files truncated${NC}"
    fi
fi

AFTER_LOGS=$(sudo du -sb "$CHROOT_DIR" 2>/dev/null | cut -f1)
LOGS_SAVED=$((BEFORE_LOGS - AFTER_LOGS))
LOGS_SAVED_H=$(numfmt --to=iec --suffix=B $LOGS_SAVED 2>/dev/null || echo "$LOGS_SAVED bytes")
echo -e "${GREEN}   Saved: $LOGS_SAVED_H${NC}"
echo ""

###############################################################################
# Optimization Step 5: Remove Temporary Files
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}[5/5] Removing temporary files...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

BEFORE_TMP=$(sudo du -sb "$CHROOT_DIR" 2>/dev/null | cut -f1)

# /tmp
if [ -d "$CHROOT_DIR/tmp" ]; then
    sudo rm -rf "$CHROOT_DIR/tmp"/* 2>/dev/null || true
    echo -e "${GREEN}[✓] /tmp cleaned${NC}"
fi

# /var/tmp
if [ -d "$CHROOT_DIR/var/tmp" ]; then
    sudo rm -rf "$CHROOT_DIR/var/tmp"/* 2>/dev/null || true
    echo -e "${GREEN}[✓] /var/tmp cleaned${NC}"
fi

AFTER_TMP=$(sudo du -sb "$CHROOT_DIR" 2>/dev/null | cut -f1)
TMP_SAVED=$((BEFORE_TMP - AFTER_TMP))
TMP_SAVED_H=$(numfmt --to=iec --suffix=B $TMP_SAVED 2>/dev/null || echo "$TMP_SAVED bytes")
echo -e "${GREEN}   Saved: $TMP_SAVED_H${NC}"
echo ""

###############################################################################
# Final Statistics
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║            OPTIMIZATION COMPLETE                             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Calculate final size and total savings
END_SIZE=$(sudo du -sb "$CHROOT_DIR" 2>/dev/null | cut -f1)
END_SIZE_H=$(sudo du -sh "$CHROOT_DIR" 2>/dev/null | cut -f1)
TOTAL_SAVED=$((START_SIZE - END_SIZE))
TOTAL_SAVED_H=$(numfmt --to=iec --suffix=B $TOTAL_SAVED 2>/dev/null || echo "$TOTAL_SAVED bytes")
PERCENT_SAVED=$(awk "BEGIN {printf \"%.1f\", ($TOTAL_SAVED / $START_SIZE) * 100}")

echo -e "${BLUE}Size Statistics:${NC}"
echo -e "  • Starting size: ${YELLOW}$START_SIZE_H${NC}"
echo -e "  • Final size: ${GREEN}$END_SIZE_H${NC}"
echo -e "  • Total saved: ${GREEN}$TOTAL_SAVED_H${NC} (${GREEN}$PERCENT_SAVED%${NC})"

echo ""
echo -e "${BLUE}Breakdown:${NC}"
echo -e "  • Git history removed: ${GREEN}$GIT_SAVED_H${NC}"
echo -e "  • Locales cleaned: ${GREEN}$LOCALE_SAVED_H${NC}"
echo -e "  • Caches cleaned: ${GREEN}$CACHE_SAVED_H${NC}"
echo -e "  • Logs truncated: ${GREEN}$LOGS_SAVED_H${NC}"
echo -e "  • Temp files removed: ${GREEN}$TMP_SAVED_H${NC}"

echo ""
echo -e "${BLUE}Expected ISO Size:${NC}"
EXPECTED_ISO_SIZE=$(awk "BEGIN {printf \"%.1f\", $END_SIZE / 1073741824 * 0.45}")
echo -e "  • Estimated (gzip compression): ${GREEN}~${EXPECTED_ISO_SIZE}GB${NC}"

echo ""
echo -e "${GREEN}✓ Chroot is now optimized and ready for Phase 6 ISO rebuild!${NC}"
echo ""

exit 0
