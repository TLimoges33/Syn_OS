#!/bin/bash

# SynOS Linux Distribution Builder - Quick Start
# Run with: sudo ./start-build.sh

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}🚀 SynOS Linux Distribution Builder - Quick Start${NC}"
echo "=================================================="
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run with sudo"
   echo "Usage: sudo ./start-build.sh"
   exit 1
fi

# Create necessary directories
echo -e "${BLUE}Creating build directories...${NC}"
mkdir -p "$BUILD_DIR/config/includes.chroot/etc"
mkdir -p "$BUILD_DIR/config/includes.chroot/opt/synos"
mkdir -p "$BUILD_DIR/logs"

# Run the Quick Test Build configuration
echo -e "${BLUE}Configuring Quick Test Build...${NC}"
cd "$SCRIPT_DIR"
./scripts/build-synos-base.sh

# Integrate SynOS AI components
echo -e "${BLUE}Integrating SynOS AI Consciousness Framework...${NC}"
./scripts/copy-synos-components.sh

# Add branding
echo -e "${BLUE}Creating SynOS branding and themes...${NC}"
./scripts/create-branding-assets.sh

cd "$BUILD_DIR"

# Fix the hostname file issue
echo "synos-linux" > config/includes.chroot/etc/hostname

# Configure minimal package list for quick test
cat > config/package-lists/synos-security.list.chroot << 'EOF'
# Minimal Security Tools for Quick Test Build
nmap
wireshark-qt
curl
wget
netcat-traditional
openssh-client
EOF

echo -e "${GREEN}✅ Configuration complete${NC}"
echo ""

# Start the actual build
echo -e "${CYAN}🚀 Starting SynOS Linux ISO build...${NC}"
echo "This will take approximately 30 minutes for Quick Test Build"
echo ""

# Run live-build
lb build 2>&1 | tee "logs/build-$(date +%Y%m%d-%H%M%S).log"

# Check if ISO was created
if [[ -f "live-image-amd64.hybrid.iso" ]]; then
    ISO_SIZE=$(du -h live-image-amd64.hybrid.iso | cut -f1)
    ISO_NAME="synos-linux-$(date +%Y%m%d)-amd64.iso"

    # Rename ISO
    mv live-image-amd64.hybrid.iso "$ISO_NAME"

    # Generate checksums
    sha256sum "$ISO_NAME" > "$ISO_NAME.sha256"
    md5sum "$ISO_NAME" > "$ISO_NAME.md5"

    echo ""
    echo -e "${GREEN}🎉 BUILD SUCCESSFUL!${NC}"
    echo -e "${GREEN}ISO created: $ISO_NAME (Size: $ISO_SIZE)${NC}"
    echo -e "${GREEN}Location: $BUILD_DIR/$ISO_NAME${NC}"
    echo ""
    echo "Test with QEMU:"
    echo "qemu-system-x86_64 -m 2048 -cdrom $BUILD_DIR/$ISO_NAME"
    echo ""
    echo "Write to USB:"
    echo "sudo dd if=$BUILD_DIR/$ISO_NAME of=/dev/sdX bs=4M status=progress"
else
    echo -e "${YELLOW}⚠️ ISO file not found after build${NC}"
    echo "Check logs in $BUILD_DIR/logs/"
    exit 1
fi