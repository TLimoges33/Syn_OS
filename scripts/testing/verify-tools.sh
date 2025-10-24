#!/bin/bash
################################################################################
# SynOS Tool Verification Script
# Verifies that all security tools are present in the ISO
################################################################################

set -euo pipefail

MOUNT_POINT="${1:-/mnt/synos-iso}"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║          SynOS Security Tools Verification                   ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ ! -d "$MOUNT_POINT" ]; then
    echo -e "${RED}✗${NC} Mount point not found: $MOUNT_POINT"
    echo "Usage: $0 <iso-mount-point>"
    exit 1
fi

# Tool categories to verify
declare -A TOOL_CATEGORIES

TOOL_CATEGORIES[network]="nmap masscan tcpdump wireshark tshark netcat socat"
TOOL_CATEGORIES[passwords]="john hashcat hydra medusa"
TOOL_CATEGORIES[wireless]="aircrack-ng wifite"
TOOL_CATEGORIES[web]="sqlmap nikto gobuster dirb wfuzz"
TOOL_CATEGORIES[exploitation]="metasploit"
TOOL_CATEGORIES[forensics]="binwalk foremost sleuthkit autopsy"
TOOL_CATEGORIES[reverse]="gdb radare2 ghidra ltrace strace"
TOOL_CATEGORIES[crypto]="openssl gnupg"

TOTAL_FOUND=0
TOTAL_MISSING=0

for category in "${!TOOL_CATEGORIES[@]}"; do
    echo -e "\n${CYAN}Checking $category tools:${NC}"
    
    FOUND=0
    MISSING=0
    
    for tool in ${TOOL_CATEGORIES[$category]}; do
        if chroot "$MOUNT_POINT" which "$tool" &>/dev/null; then
            echo -e "  ${GREEN}✓${NC} $tool"
            ((FOUND++))
            ((TOTAL_FOUND++))
        else
            echo -e "  ${RED}✗${NC} $tool"
            ((MISSING++))
            ((TOTAL_MISSING++))
        fi
    done
    
    echo -e "  ${CYAN}Category summary:${NC} $FOUND found, $MISSING missing"
done

# Check for Python packages
echo -e "\n${CYAN}Checking Python security packages:${NC}"
PYTHON_PKGS=(impacket scapy requests)
for pkg in "${PYTHON_PKGS[@]}"; do
    if chroot "$MOUNT_POINT" python3 -c "import $pkg" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $pkg"
        ((TOTAL_FOUND++))
    else
        echo -e "  ${YELLOW}⚠${NC} $pkg (optional)"
    fi
done

# Check for GitHub repos
echo -e "\n${CYAN}Checking GitHub repositories:${NC}"
if [ -d "$MOUNT_POINT/opt/security-tools/github" ]; then
    REPO_COUNT=$(find "$MOUNT_POINT/opt/security-tools/github" -mindepth 1 -maxdepth 1 -type d | wc -l)
    echo -e "  ${GREEN}✓${NC} $REPO_COUNT repositories found"
    ((TOTAL_FOUND += REPO_COUNT))
else
    echo -e "  ${YELLOW}⚠${NC} GitHub tools directory not found"
fi

# Check SynOS binaries
echo -e "\n${CYAN}Checking SynOS binaries:${NC}"
if [ -d "$MOUNT_POINT/opt/synos/bin" ]; then
    SYNOS_COUNT=$(find "$MOUNT_POINT/opt/synos/bin" -type f -executable | wc -l)
    echo -e "  ${GREEN}✓${NC} $SYNOS_COUNT SynOS binaries found"
else
    echo -e "  ${RED}✗${NC} SynOS binaries not found"
fi

# Summary
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                    Verification Summary                      ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Tools Found:   ${GREEN}$TOTAL_FOUND${NC}"
echo -e "  Tools Missing: ${RED}$TOTAL_MISSING${NC}"
echo ""

if [ $TOTAL_MISSING -eq 0 ]; then
    echo -e "${GREEN}✓ All critical tools are present!${NC}"
    exit 0
elif [ $TOTAL_MISSING -lt 10 ]; then
    echo -e "${YELLOW}⚠ Some tools missing, but build is usable${NC}"
    exit 0
else
    echo -e "${RED}✗ Too many tools missing, build may have issues${NC}"
    exit 1
fi
