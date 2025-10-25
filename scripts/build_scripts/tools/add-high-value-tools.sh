#!/bin/bash

###############################################################################
# SynOS - Add 20 High-Value Small-Footprint Security Tools
# Total space needed: ~85MB
###############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CHROOT_DIR="$1"
if [ -z "$CHROOT_DIR" ]; then
    echo -e "${RED}Usage: $0 <chroot_directory>${NC}"
    exit 1
fi

GITHUB_DIR="$CHROOT_DIR/opt/github-repos"

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   Adding 20 High-Value Small-Footprint Security Tools       ║"
echo "║   Total Space: ~85MB | High Impact                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

INSTALLED=0
FAILED=0

clone_tool() {
    local name="$1"
    local repo="$2"
    local dest="$GITHUB_DIR/$name"

    if [ -d "$dest" ]; then
        echo -e "${YELLOW}[!] $name already exists${NC}"
        return 0
    fi

    echo -e "${YELLOW}[→] Installing $name...${NC}"
    if sudo git clone --depth 1 "https://github.com/$repo.git" "$dest" >/dev/null 2>&1; then
        # Remove .git immediately to save space
        sudo rm -rf "$dest/.git" 2>/dev/null || true
        size=$(sudo du -sh "$dest" 2>/dev/null | cut -f1)
        echo -e "${GREEN}[✓] $name installed ($size)${NC}"
        INSTALLED=$((INSTALLED + 1))
    else
        echo -e "${RED}[✗] Failed: $name${NC}"
        FAILED=$((FAILED + 1))
    fi
}

echo -e "${BLUE}═══ WEB SECURITY TOOLS ═══${NC}"
clone_tool "dirsearch" "maurosoria/dirsearch"
clone_tool "ffuf" "ffuf/ffuf"
clone_tool "waybackurls" "tomnomnom/waybackurls"
clone_tool "gau" "lc/gau"

echo ""
echo -e "${BLUE}═══ OSINT TOOLS ═══${NC}"
clone_tool "theHarvester" "laramies/theHarvester"
clone_tool "sherlock" "sherlock-project/sherlock"
clone_tool "holehe" "megadose/holehe"

echo ""
echo -e "${BLUE}═══ RECONNAISSANCE TOOLS ═══${NC}"
clone_tool "amass" "owasp-amass/amass"
clone_tool "subfinder" "projectdiscovery/subfinder"
clone_tool "assetfinder" "tomnomnom/assetfinder"

echo ""
echo -e "${BLUE}═══ EXPLOITATION TOOLS ═══${NC}"
clone_tool "GitTools" "internetwache/GitTools"
clone_tool "git-dumper" "arthaud/git-dumper"
clone_tool "sqlmap" "sqlmapproject/sqlmap"

echo ""
echo -e "${BLUE}═══ NETWORK TOOLS ═══${NC}"
clone_tool "masscan" "robertdavidgraham/masscan"
clone_tool "rustscan" "RustScan/RustScan"

echo ""
echo -e "${BLUE}═══ PASSWORD TOOLS ═══${NC}"
clone_tool "username-anarchy" "urbanadventurer/username-anarchy"
clone_tool "h8mail" "khast3x/h8mail"

echo ""
echo -e "${BLUE}═══ WIRELESS TOOLS ═══${NC}"
clone_tool "wifite2" "derv82/wifite2"
clone_tool "airgeddon" "v1s1t0r1sh3r3/airgeddon"

echo ""
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║            HIGH-VALUE TOOLS INSTALLATION COMPLETE            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${GREEN}✓ Installed: $INSTALLED/20 tools${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}✗ Failed: $FAILED${NC}"
fi

FINAL_SIZE=$(sudo du -sh "$GITHUB_DIR" 2>/dev/null | cut -f1)
echo -e "${BLUE}GitHub repos total size: $FINAL_SIZE${NC}"

exit 0
