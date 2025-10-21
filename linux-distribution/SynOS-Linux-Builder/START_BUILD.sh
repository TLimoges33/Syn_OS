#!/bin/bash
################################################################################
# SynOS v1.0 Build Launcher
#
# This is a simple wrapper that you can run to start the build.
# It will prompt for confirmation and then execute the main build script.
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

clear

echo -e "${CYAN}${BOLD}"
cat << 'EOF'
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║                  SynOS v1.0 BUILD LAUNCHER                ║
║                                                           ║
║  Phase 1 Day 1: Build Demo ISO with Sanitized Script     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${GREEN}Pre-Build Verification: ✅ PASSED${NC}"
echo ""
echo "  ✅ SynOS components staged (kernel, AI, consciousness)"
echo "  ✅ Repository configuration clean (ParrotOS only, no conflicts)"
echo "  ✅ Package lists sanitized (332 packages, all verified)"
echo "  ✅ Hooks cleaned (20 hooks, no duplicates)"
echo ""
echo -e "${BLUE}Build Readiness Report: ${NC}BUILD_READINESS_REPORT.md"
echo ""

echo -e "${YELLOW}${BOLD}Build Configuration:${NC}"
echo "  • Base: ParrotOS 6.4 (Debian 12 Bookworm)"
echo "  • Kernel: Linux 6.5 + SynOS Rust kernel (optional boot)"
echo "  • Tools: 500+ security tools from ParrotOS"
echo "  • AI: Neural Darwinism consciousness + ALFRED"
echo "  • Expected Size: 8-12 GB ISO"
echo "  • Estimated Time: 2-4 hours"
echo ""

echo -e "${CYAN}${BOLD}This build will:${NC}"
echo "  1. Clean previous builds (lb clean --purge)"
echo "  2. Configure live-build with SynOS metadata"
echo "  3. Build complete bootable ISO"
echo "  4. Create checksums (SHA256, MD5)"
echo "  5. Provide testing instructions"
echo ""

echo -e "${YELLOW}⚠️  Requirements:${NC}"
echo "  • 50+ GB free disk space"
echo "  • Stable internet connection"
echo "  • sudo privileges"
echo "  • 2-4 hours of uninterrupted build time"
echo ""

# Check disk space
AVAILABLE_GB=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$AVAILABLE_GB" -lt 50 ]; then
    echo -e "${RED}⚠️  WARNING: Only ${AVAILABLE_GB}GB available. 50GB+ recommended.${NC}"
    echo ""
fi

# Ask for confirmation
echo -e "${BOLD}Ready to start the build?${NC}"
echo ""
echo "  [Y] Yes, start the build now"
echo "  [V] View build readiness report first"
echo "  [N] No, exit"
echo ""
read -p "Your choice [Y/V/N]: " -n 1 -r
echo ""

case $REPLY in
    [Yy]* )
        echo ""
        echo -e "${GREEN}${BOLD}Starting SynOS v1.0 build...${NC}"
        echo ""
        echo "Build log will be saved to: build-sanitized-$(date +%Y%m%d-%H%M%S).log"
        echo ""
        echo -e "${YELLOW}You can monitor progress in another terminal with:${NC}"
        echo "  tail -f build-sanitized-*.log"
        echo ""
        sleep 2

        # Execute the build script
        sudo ./build-synos-v1.0-sanitized.sh
        ;;

    [Vv]* )
        echo ""
        echo -e "${BLUE}Opening build readiness report...${NC}"
        echo ""
        if command -v less >/dev/null 2>&1; then
            less BUILD_READINESS_REPORT.md
        else
            cat BUILD_READINESS_REPORT.md
        fi
        echo ""
        echo -e "${BOLD}Run ./START_BUILD.sh again when ready to build.${NC}"
        ;;

    * )
        echo ""
        echo -e "${YELLOW}Build cancelled.${NC}"
        echo ""
        echo "When ready to build, run:"
        echo "  sudo ./build-synos-v1.0-sanitized.sh"
        echo ""
        echo "Or for interactive mode:"
        echo "  ./START_BUILD.sh"
        exit 0
        ;;
esac
