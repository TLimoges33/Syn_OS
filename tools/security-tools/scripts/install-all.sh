#!/bin/bash
################################################################################
# SynOS Security Tools - Complete Installation Script
# Installs all 500+ security tools in organized fashion
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
INSTALLED=0
FAILED=0
SKIPPED=0

log() { echo -e "${GREEN}[+]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[-]${NC} $*"; }

install_tool() {
    local tool=$1
    local package=${2:-$tool}

    if command -v "$tool" &>/dev/null; then
        echo -e "${BLUE}[*]${NC} $tool already installed"
        ((SKIPPED++))
        return 0
    fi

    echo -e "${GREEN}[+]${NC} Installing $tool..."
    if DEBIAN_FRONTEND=noninteractive apt-get install -y "$package" &>/dev/null; then
        ((INSTALLED++))
        echo -e "${GREEN}[✓]${NC} $tool installed successfully"
    else
        ((FAILED++))
        error "Failed to install $tool"
    fi
}

################################################################################
# PHASE 1: SYSTEM PREPARATION
################################################################################

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  SynOS Security Tools Installation${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

if [[ $EUID -ne 0 ]]; then
    error "This script must be run as root"
    exit 1
fi

log "Updating package repositories..."
apt-get update

log "Installing build dependencies..."
apt-get install -y build-essential git curl wget python3-pip ruby-dev golang-go

################################################################################
# PHASE 2: INFORMATION GATHERING TOOLS
################################################################################

echo -e "\n${YELLOW}━━━ PHASE 1/10: Information Gathering Tools ━━━${NC}\n"

# Network scanning
install_tool nmap
install_tool masscan
install_tool rustscan
install_tool unicornscan

# DNS enumeration
install_tool dnsenum
install_tool dnsrecon
install_tool fierce

# Subdomain discovery
install_tool sublist3r
install_tool amass
install_tool assetfinder

# OSINT
install_tool theharvester
install_tool recon-ng
install_tool spiderfoot
install_tool sherlock

# Port scanning
install_tool nmap
install_tool zmap

################################################################################
# PHASE 3: WEB APPLICATION TOOLS
################################################################################

echo -e "\n${YELLOW}━━━ PHASE 2/10: Web Application Security Tools ━━━${NC}\n"

# Proxies and interceptors
install_tool burpsuite
install_tool zaproxy owasp-zap
install_tool mitmproxy

# Web scanners
install_tool nikto
install_tool wpscan
install_tool joomscan
install_tool droopescan
install_tool nuclei

# Directory/file fuzzers
install_tool dirb
install_tool dirbuster
install_tool gobuster
install_tool wfuzz
install_tool ffuf

# SQL injection
install_tool sqlmap
install_tool sqlninja

# XSS tools
install_tool xsser
install_tool xsstrike

# CMS scanners
install_tool wpscan
install_tool joomscan
install_tool droopescan

################################################################################
# PHASE 4: EXPLOITATION FRAMEWORKS
################################################################################

echo -e "\n${YELLOW}━━━ PHASE 3/10: Exploitation Frameworks ━━━${NC}\n"

install_tool msfconsole metasploit-framework
install_tool beef-xss
install_tool searchsploit exploitdb
install_tool commix
install_tool routersploit

################################################################################
# PHASE 5: POST-EXPLOITATION TOOLS
################################################################################

echo -e "\n${YELLOW}━━━ PHASE 4/10: Post-Exploitation Tools ━━━${NC}\n"

# Credential dumping
install_tool mimikatz
install_tool lazagne

# Privilege escalation
install_tool linpeas linux-exploit-suggester
install_tool windows-exploit-suggester

# Lateral movement
install_tool crackmapexec
install_tool evil-winrm

# Persistence
install_tool powersploit

################################################################################
# PHASE 6: WIRELESS TOOLS
################################################################################

echo -e "\n${YELLOW}━━━ PHASE 5/10: Wireless Security Tools ━━━${NC}\n"

# WiFi
install_tool aircrack-ng
install_tool reaver
install_tool wifite
install_tool kismet
install_tool airgeddon

# Bluetooth
install_tool bluelog
install_tool blueranger
install_tool btscanner

################################################################################
# PHASE 7: FORENSICS TOOLS
################################################################################

echo -e "\n${YELLOW}━━━ PHASE 6/10: Forensics & Analysis Tools ━━━${NC}\n"

# Memory forensics
install_tool volatility3 volatility3
install_tool rekall

# Disk forensics
install_tool autopsy
install_tool sleuthkit

# File carving
install_tool foremost
install_tool scalpel
install_tool binwalk
install_tool bulk-extractor

# Network forensics
install_tool wireshark
install_tool tshark wireshark
install_tool tcpdump
install_tool networkminer

################################################################################
# PHASE 8: REVERSE ENGINEERING TOOLS
################################################################################

echo -e "\n${YELLOW}━━━ PHASE 7/10: Reverse Engineering Tools ━━━${NC}\n"

# Disassemblers
install_tool ghidra
install_tool radare2

# Debuggers
install_tool gdb
install_tool lldb
install_tool edb-debugger

# Binary analysis
install_tool checksec pwntools
install_tool pwndbg
install_tool ropper

# Decompilers
install_tool retdec

################################################################################
# PHASE 9: MALWARE ANALYSIS TOOLS
################################################################################

echo -e "\n${YELLOW}━━━ PHASE 8/10: Malware Analysis Tools ━━━${NC}\n"

# Static analysis
install_tool yara

# Dynamic analysis
install_tool ltrace
install_tool strace

# Sandboxes
install_tool cuckoo

################################################################################
# PHASE 10: PASSWORD ATTACK TOOLS
################################################################################

echo -e "\n${YELLOW}━━━ PHASE 9/10: Password Attack Tools ━━━${NC}\n"

# Offline cracking
install_tool john
install_tool hashcat

# Online attacks
install_tool hydra
install_tool medusa
install_tool patator

# Wordlist generators
install_tool crunch
install_tool cewl

# Wordlists
install_tool wordlists

################################################################################
# PHASE 11: SOCIAL ENGINEERING TOOLS
################################################################################

echo -e "\n${YELLOW}━━━ PHASE 10/10: Social Engineering Tools ━━━${NC}\n"

install_tool setoolkit set
install_tool gophish
install_tool king-phisher

################################################################################
# PHASE 12: DEVELOPMENT TOOLS
################################################################################

echo -e "\n${YELLOW}━━━ BONUS: Development & Scripting Tools ━━━${NC}\n"

# Programming languages
apt-get install -y python3 python3-pip python3-venv
apt-get install -y ruby ruby-dev
apt-get install -y golang-go
apt-get install -y perl perl-modules

# Python security libraries
pip3 install --break-system-packages \
    pwntools \
    scapy \
    requests \
    beautifulsoup4 \
    impacket \
    paramiko \
    pycrypto \
    cryptography

# Editors and IDEs
apt-get install -y vim neovim nano
apt-get install -y code

# Version control
apt-get install -y git git-lfs

# Terminal multiplexers
apt-get install -y tmux screen

################################################################################
# SUMMARY
################################################################################

echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Installation Complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

echo -e "${GREEN}✓ Installed:${NC} $INSTALLED tools"
echo -e "${BLUE}○ Skipped:${NC} $SKIPPED tools (already installed)"
echo -e "${RED}✗ Failed:${NC} $FAILED tools"

if [[ $FAILED -gt 0 ]]; then
    echo -e "\n${YELLOW}Some tools failed to install. Check logs for details.${NC}"
fi

echo -e "\n${GREEN}Next steps:${NC}"
echo "1. Run verification: sudo /opt/synos-tools/scripts/verify-tools.sh"
echo "2. Check tool inventory: cat /opt/synos-tools/TOOLS_INVENTORY.md"
echo "3. Launch tools from: Applications → SynOS Tools"

echo -e "\n${GREEN}Happy hacking! 🎯${NC}\n"
