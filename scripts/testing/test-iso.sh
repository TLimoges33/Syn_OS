#!/bin/bash
################################################################################
# SynOS ISO Test Script
# Tests the built ISO in QEMU VM
################################################################################

set -euo pipefail

ISO_FILE="${1:-}"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║               SynOS ISO Testing (QEMU)                       ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Find ISO if not specified
if [ -z "$ISO_FILE" ]; then
    echo "Looking for latest ISO..."
    ISO_FILE=$(find build/full-distribution -name "*.iso" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
    
    if [ -z "$ISO_FILE" ]; then
        echo -e "${RED}✗${NC} No ISO file found!"
        echo "Usage: $0 <path-to-iso>"
        exit 1
    fi
    
    echo -e "${GREEN}✓${NC} Found: $ISO_FILE"
fi

if [ ! -f "$ISO_FILE" ]; then
    echo -e "${RED}✗${NC} ISO file not found: $ISO_FILE"
    exit 1
fi

# Check for QEMU
if ! command -v qemu-system-x86_64 &> /dev/null; then
    echo -e "${RED}✗${NC} QEMU not installed!"
    echo ""
    echo "Install with:"
    echo "  sudo apt-get install qemu-system-x86"
    echo ""
    echo "Or test manually:"
    echo "  1. Write to USB: sudo dd if=$ISO_FILE of=/dev/sdX bs=4M status=progress"
    echo "  2. Or use VirtualBox/VMware"
    exit 1
fi

# Check ISO size
ISO_SIZE=$(stat -c%s "$ISO_FILE")
ISO_SIZE_MB=$((ISO_SIZE / 1024 / 1024))

echo ""
echo "ISO Information:"
echo "  File: $ISO_FILE"
echo "  Size: ${ISO_SIZE_MB} MB"
echo ""

if [ $ISO_SIZE_MB -lt 100 ]; then
    echo -e "${YELLOW}⚠${NC} Warning: ISO seems small (< 100 MB)"
fi

# Verify checksums if available
if [ -f "${ISO_FILE}.md5" ]; then
    echo "Verifying MD5 checksum..."
    if md5sum -c "${ISO_FILE}.md5" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} MD5 checksum valid"
    else
        echo -e "${RED}✗${NC} MD5 checksum failed!"
    fi
fi

if [ -f "${ISO_FILE}.sha256" ]; then
    echo "Verifying SHA256 checksum..."
    if sha256sum -c "${ISO_FILE}.sha256" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} SHA256 checksum valid"
    else
        echo -e "${RED}✗${NC} SHA256 checksum failed!"
    fi
fi

echo ""
echo -e "${CYAN}Starting QEMU VM...${NC}"
echo ""
echo "VM Configuration:"
echo "  Memory: 4 GB"
echo "  CPUs: 2"
echo "  Display: GTK (if available)"
echo ""
echo "Press Ctrl+Alt+G to release mouse"
echo "Press Ctrl+Alt+F to toggle fullscreen"
echo ""
echo -e "${YELLOW}Starting in 3 seconds...${NC}"
sleep 3

# Start QEMU with reasonable defaults
qemu-system-x86_64 \
    -m 4096 \
    -smp 2 \
    -cdrom "$ISO_FILE" \
    -boot d \
    -vga std \
    -display gtk \
    -enable-kvm \
    -cpu host \
    2>/dev/null || \
qemu-system-x86_64 \
    -m 4096 \
    -smp 2 \
    -cdrom "$ISO_FILE" \
    -boot d \
    -vga std \
    -display sdl \
    2>/dev/null || \
qemu-system-x86_64 \
    -m 4096 \
    -smp 2 \
    -cdrom "$ISO_FILE" \
    -boot d \
    -vga std \
    -nographic

echo ""
echo -e "${GREEN}✓${NC} QEMU session ended"
echo ""
echo "Manual testing checklist:"
echo "  □ ISO boots successfully"
echo "  □ Kernel loads without errors"
echo "  □ System reaches login prompt"
echo "  □ Can login with synos/synos"
echo "  □ Network tools work (nmap, etc.)"
echo "  □ SynOS binaries are accessible"
echo "  □ /opt/synos directory structure exists"
echo ""
