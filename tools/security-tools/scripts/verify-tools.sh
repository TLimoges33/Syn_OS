#!/bin/bash
################################################################################
# SynOS Security Tools - Verification Script
# Verifies all critical tools are installed and functional
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
PRESENT=0
MISSING=0
TOTAL=0

check_tool() {
    local tool=$1
    local display_name=${2:-$tool}

    ((TOTAL++))

    if command -v "$tool" &>/dev/null; then
        echo -e "${GREEN}[✓]${NC} $display_name"
        ((PRESENT++))
        return 0
    else
        echo -e "${RED}[✗]${NC} $display_name ${YELLOW}(missing)${NC}"
        ((MISSING++))
        return 1
    fi
}

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  SynOS Security Tools Verification${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}━━━ Information Gathering ━━━${NC}"
check_tool nmap "Nmap"
check_tool masscan "Masscan"
check_tool dnsenum "DNSenum"
check_tool amass "Amass"
check_tool sublist3r "Sublist3r"
check_tool theharvester "theHarvester"

echo -e "\n${YELLOW}━━━ Web Application Testing ━━━${NC}"
check_tool burpsuite "Burp Suite"
check_tool zaproxy "OWASP ZAP"
check_tool sqlmap "SQLMap"
check_tool nikto "Nikto"
check_tool wpscan "WPScan"
check_tool gobuster "Gobuster"
check_tool ffuf "FFUF"

echo -e "\n${YELLOW}━━━ Exploitation ━━━${NC}"
check_tool msfconsole "Metasploit Framework"
check_tool searchsploit "SearchSploit"
check_tool beef-xss "BeEF"

echo -e "\n${YELLOW}━━━ Wireless ━━━${NC}"
check_tool aircrack-ng "Aircrack-ng"
check_tool reaver "Reaver"
check_tool wifite "Wifite"

echo -e "\n${YELLOW}━━━ Forensics ━━━${NC}"
check_tool autopsy "Autopsy"
check_tool volatility3 "Volatility 3"
check_tool binwalk "Binwalk"
check_tool foremost "Foremost"

echo -e "\n${YELLOW}━━━ Reverse Engineering ━━━${NC}"
check_tool ghidra "Ghidra"
check_tool radare2 "Radare2"
check_tool gdb "GDB"

echo -e "\n${YELLOW}━━━ Password Attacks ━━━${NC}"
check_tool john "John the Ripper"
check_tool hashcat "Hashcat"
check_tool hydra "Hydra"
check_tool medusa "Medusa"

echo -e "\n${YELLOW}━━━ Development Tools ━━━${NC}"
check_tool python3 "Python 3"
check_tool ruby "Ruby"
check_tool go "Go"
check_tool git "Git"

echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Verification Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

echo -e "Total tools checked: ${BLUE}$TOTAL${NC}"
echo -e "${GREEN}Present:${NC} $PRESENT ($(( PRESENT * 100 / TOTAL ))%)"
echo -e "${RED}Missing:${NC} $MISSING ($(( MISSING * 100 / TOTAL ))%)"

if [[ $MISSING -eq 0 ]]; then
    echo -e "\n${GREEN}✓ All critical tools are installed!${NC}\n"
    exit 0
else
    echo -e "\n${YELLOW}⚠ Some tools are missing. Run install script:${NC}"
    echo -e "  sudo /opt/synos-tools/scripts/install-all.sh\n"
    exit 1
fi
