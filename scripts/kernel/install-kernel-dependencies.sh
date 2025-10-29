#!/bin/bash
# Install Kernel Build Dependencies for SynOS AI Kernel Development
# Phase 1: Linux Kernel Source Setup
# Date: October 28, 2025

set -e  # Exit on error

echo "================================================"
echo "SynOS AI Kernel - Dependency Installation"
echo "================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
   echo -e "${RED}ERROR: Please run as root (use sudo)${NC}"
   exit 1
fi

echo -e "${GREEN}Step 1: Updating package lists...${NC}"
apt update

echo ""
echo -e "${GREEN}Step 2: Installing kernel build dependencies...${NC}"
echo "This will install:"
echo "  - build-essential (GCC, make)"
echo "  - bc (calculator)"
echo "  - bison (parser generator)"
echo "  - flex (lexical analyzer)"
echo "  - libssl-dev (SSL for crypto)"
echo "  - libelf-dev (ELF for BPF)"
echo "  - libncurses-dev (menuconfig UI)"
echo "  - dwarves (BTF utilities)"
echo "  - rsync (file sync)"
echo "  - git (version control)"
echo "  - fakeroot (packaging)"
echo "  - debhelper (Debian packaging tools)"
echo "  - linux-source-6.12 (kernel source)"
echo ""

apt install -y \
    build-essential \
    bc \
    bison \
    flex \
    libssl-dev \
    libelf-dev \
    libncurses-dev \
    dwarves \
    rsync \
    git \
    fakeroot \
    debhelper \
    linux-source-6.12

echo ""
echo -e "${GREEN}Step 3: Verifying installation...${NC}"

# Check each package
PACKAGES=(
    "build-essential"
    "bc"
    "bison"
    "flex"
    "libssl-dev"
    "libelf-dev"
    "libncurses-dev"
    "dwarves"
    "rsync"
    "git"
    "fakeroot"
    "debhelper"
    "linux-source-6.12"
)

ALL_INSTALLED=true
for pkg in "${PACKAGES[@]}"; do
    if dpkg-query -W -f='${Status}' "$pkg" 2>/dev/null | grep -q "install ok installed"; then
        echo -e "  ${GREEN}✓${NC} $pkg"
    else
        echo -e "  ${RED}✗${NC} $pkg - NOT INSTALLED"
        ALL_INSTALLED=false
    fi
done

echo ""
if [ "$ALL_INSTALLED" = true ]; then
    echo -e "${GREEN}✅ All dependencies installed successfully!${NC}"
    echo ""
    echo "Kernel source location: /usr/src/linux-source-6.12.tar.xz"
    echo ""
    echo "Next steps:"
    echo "  1. Extract kernel source: cd /usr/src && sudo tar -xf linux-source-6.12.tar.xz"
    echo "  2. Configure kernel: cd linux-source-6.12 && sudo cp /boot/config-$(uname -r) .config"
    echo "  3. Build kernel: sudo make -j$(nproc) bzImage modules"
    echo ""
    echo "See: /home/diablorain/Syn_OS/docs/05-planning/roadmaps/PHASE1_KERNEL_SOURCE_SETUP.md"
else
    echo -e "${RED}❌ Some dependencies failed to install${NC}"
    echo "Please check errors above and try again"
    exit 1
fi

echo ""
echo "================================================"
echo "Dependency installation complete!"
echo "================================================"
