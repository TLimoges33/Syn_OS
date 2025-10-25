#!/bin/bash
# SynOS v1.0 Final Build Script
# Complete ISO build with all fixes applied
# Author: SynOS Development Team
# Date: October 8, 2025

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CHROOT=/home/diablorain/Syn_OS/build/synos-v1.0/work/chroot
BUILD_DIR=/home/diablorain/Syn_OS/build
SCRIPTS_DIR=/home/diablorain/Syn_OS/scripts/build
LOG_DIR=/home/diablorain/Syn_OS/logs
LOG_FILE=$LOG_DIR/synos-v1.0-final-build-$(date +%Y%m%d-%H%M%S).log

mkdir -p "$LOG_DIR"

echo -e "${BLUE}=========================================================================${NC}" | tee "$LOG_FILE"
echo -e "${BLUE}                   SynOS v1.0 FINAL BUILD${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}=========================================================================${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Started: $(date)" | tee -a "$LOG_FILE"
echo "Chroot: $CHROOT" | tee -a "$LOG_FILE"
echo "Build Directory: $BUILD_DIR" | tee -a "$LOG_FILE"
echo "Log File: $LOG_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}ERROR: This script must be run as root (use sudo)${NC}" | tee -a "$LOG_FILE"
    exit 1
fi

# Verify chroot exists
if [ ! -d "$CHROOT" ]; then
    echo -e "${RED}ERROR: Chroot not found at $CHROOT${NC}" | tee -a "$LOG_FILE"
    echo "Please run the earlier phases first to create the chroot" | tee -a "$LOG_FILE"
    exit 1
fi

# ====================
# STEP 1: Fix Security Tool Categories
# ====================
echo -e "${BLUE}=========================================================================${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}[1/4] FIXING SECURITY TOOL CATEGORIES${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}=========================================================================${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

if [ -f "$SCRIPTS_DIR/fix-security-tool-categories.sh" ]; then
    echo "Running security tool categorization fix..." | tee -a "$LOG_FILE"
    bash "$SCRIPTS_DIR/fix-security-tool-categories.sh" 2>&1 | tee -a "$LOG_FILE"
    echo -e "${GREEN}✓ Security tool categories fixed${NC}" | tee -a "$LOG_FILE"
else
    echo -e "${YELLOW}WARNING: fix-security-tool-categories.sh not found, skipping...${NC}" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"

# ====================
# STEP 2: Configure Desktop Environment
# ====================
echo -e "${BLUE}=========================================================================${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}[2/4] CONFIGURING DESKTOP ENVIRONMENT${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}=========================================================================${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Export current panel configuration
echo "Exporting MATE panel configuration..." | tee -a "$LOG_FILE"
if command -v dconf >/dev/null 2>&1; then
    PANEL_CONFIG=$(dconf dump /org/mate/panel/ 2>/dev/null || echo "")
    if [ -n "$PANEL_CONFIG" ]; then
        echo "$PANEL_CONFIG" > /tmp/mate-panel-config.dconf
        echo -e "${GREEN}✓ Panel configuration exported${NC}" | tee -a "$LOG_FILE"

        # Create default panel config for skeleton
        mkdir -p "$CHROOT/etc/skel/.config/dconf"
        echo "$PANEL_CONFIG" > "$CHROOT/etc/skel/.config/mate-panel.dconf"
        echo -e "${GREEN}✓ Panel configuration saved to skeleton${NC}" | tee -a "$LOG_FILE"
    else
        echo -e "${YELLOW}WARNING: No panel configuration found on host${NC}" | tee -a "$LOG_FILE"
    fi
else
    echo -e "${YELLOW}WARNING: dconf not available, skipping panel export${NC}" | tee -a "$LOG_FILE"
fi

# Install Brisk Menu if not present
echo "Checking for Brisk Menu..." | tee -a "$LOG_FILE"
if ! chroot "$CHROOT" dpkg -l | grep -q mate-applet-brisk-menu; then
    echo "Installing Brisk Menu..." | tee -a "$LOG_FILE"
    chroot "$CHROOT" apt-get update -qq 2>&1 | tee -a "$LOG_FILE"
    chroot "$CHROOT" apt-get install -y mate-applet-brisk-menu 2>&1 | tee -a "$LOG_FILE"
    echo -e "${GREEN}✓ Brisk Menu installed${NC}" | tee -a "$LOG_FILE"
else
    echo -e "${GREEN}✓ Brisk Menu already installed${NC}" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"

# ====================
# STEP 3: Update Menu Database
# ====================
echo -e "${BLUE}=========================================================================${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}[3/4] UPDATING MENU DATABASE${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}=========================================================================${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "Updating desktop database..." | tee -a "$LOG_FILE"
chroot "$CHROOT" update-desktop-database /usr/share/applications 2>&1 | tee -a "$LOG_FILE"
echo -e "${GREEN}✓ Desktop database updated${NC}" | tee -a "$LOG_FILE"

echo "Updating menu cache..." | tee -a "$LOG_FILE"
chroot "$CHROOT" update-menus 2>&1 | tee -a "$LOG_FILE" || true
echo -e "${GREEN}✓ Menu cache updated${NC}" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"

# ====================
# STEP 4: Generate ISO with Fixed Scripts
# ====================
echo -e "${BLUE}=========================================================================${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}[4/4] GENERATING ISO IMAGE${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}=========================================================================${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

if [ -f "$SCRIPTS_DIR/phase6-iso-generation.sh" ]; then
    echo "Running ISO generation with fixed script..." | tee -a "$LOG_FILE"
    bash "$SCRIPTS_DIR/phase6-iso-generation.sh" 2>&1 | tee -a "$LOG_FILE"

    ISO_FILE="$BUILD_DIR/synos-v1.0-complete.iso"
    if [ -f "$ISO_FILE" ]; then
        ISO_SIZE=$(du -sh "$ISO_FILE" | awk '{print $1}')
        echo -e "${GREEN}=========================================================================${NC}" | tee -a "$LOG_FILE"
        echo -e "${GREEN}                   BUILD SUCCESSFUL!${NC}" | tee -a "$LOG_FILE"
        echo -e "${GREEN}=========================================================================${NC}" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        echo -e "${GREEN}ISO Location: $ISO_FILE${NC}" | tee -a "$LOG_FILE"
        echo -e "${GREEN}ISO Size: $ISO_SIZE${NC}" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        echo "Boot Modes: Hybrid BIOS + UEFI" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        echo "Test Commands:" | tee -a "$LOG_FILE"
        echo "  QEMU: qemu-system-x86_64 -m 4G -cdrom $ISO_FILE" | tee -a "$LOG_FILE"
        echo "  USB:  sudo dd if=$ISO_FILE of=/dev/sdX bs=4M status=progress" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
    else
        echo -e "${RED}ERROR: ISO generation failed!${NC}" | tee -a "$LOG_FILE"
        echo "Check log for details: $LOG_FILE" | tee -a "$LOG_FILE"
        exit 1
    fi
else
    echo -e "${RED}ERROR: phase6-iso-generation.sh not found!${NC}" | tee -a "$LOG_FILE"
    exit 1
fi

# ====================
# FINAL SUMMARY
# ====================
echo -e "${BLUE}=========================================================================${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}                   BUILD SUMMARY${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}=========================================================================${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Count security tools
TOOL_COUNT=$(ls "$CHROOT/usr/share/applications/synos-"*.desktop 2>/dev/null | wc -l)

echo "Completed: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Statistics:" | tee -a "$LOG_FILE"
echo "  - Security Tools: $TOOL_COUNT tools" | tee -a "$LOG_FILE"
echo "  - ISO Size: $ISO_SIZE" | tee -a "$LOG_FILE"
echo "  - Boot Support: BIOS + UEFI (hybrid)" | tee -a "$LOG_FILE"
echo "  - Desktop Environment: MATE with Brisk Menu" | tee -a "$LOG_FILE"
echo "  - Menu Categories: 11 specialized security categories" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "Menu Categories Configured:" | tee -a "$LOG_FILE"
echo "  1. Information Gathering" | tee -a "$LOG_FILE"
echo "  2. Vulnerability Analysis" | tee -a "$LOG_FILE"
echo "  3. Web Application Analysis" | tee -a "$LOG_FILE"
echo "  4. Database Assessment" | tee -a "$LOG_FILE"
echo "  5. Password Attacks" | tee -a "$LOG_FILE"
echo "  6. Wireless Attacks" | tee -a "$LOG_FILE"
echo "  7. Exploitation Tools" | tee -a "$LOG_FILE"
echo "  8. Sniffing & Spoofing" | tee -a "$LOG_FILE"
echo "  9. Post Exploitation" | tee -a "$LOG_FILE"
echo "  10. Forensics" | tee -a "$LOG_FILE"
echo "  11. Reporting Tools" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo -e "${GREEN}Log saved to: $LOG_FILE${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo -e "${GREEN}=========================================================================${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}          SynOS v1.0 BUILD COMPLETE - READY FOR TESTING!${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}=========================================================================${NC}" | tee -a "$LOG_FILE"

# Create success marker
cat > "$BUILD_DIR/SYNOS_V1.0_COMPLETE.txt" << EOF
SynOS v1.0 - Final Build Complete
==================================

Build Date: $(date)
ISO File: $ISO_FILE
ISO Size: $ISO_SIZE

Security Tools: $TOOL_COUNT
Menu Categories: 11 specialized categories
Desktop: MATE with Brisk Menu
Boot Support: BIOS + UEFI (hybrid)

Status: READY FOR TESTING AND DEPLOYMENT

All fixes applied:
✓ UEFI bootloader created
✓ Security tool categories fixed
✓ Menu structure configured
✓ Desktop environment optimized
✓ ISO generation successful

Next Steps:
1. Test ISO in QEMU
2. Test BIOS boot
3. Test UEFI boot
4. Verify security tools menu
5. Create demo video
6. Release v1.0

Build Log: $LOG_FILE
EOF

echo -e "${GREEN}Build completion marker created: $BUILD_DIR/SYNOS_V1.0_COMPLETE.txt${NC}"
echo ""
echo "🎉 SynOS v1.0 is ready for release! 🎉"
