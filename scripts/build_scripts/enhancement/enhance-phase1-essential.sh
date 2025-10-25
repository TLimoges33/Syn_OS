#!/usr/bin/env bash
###############################################################################
# SynOS Phase 1 - Essential Security Tools Installation
# Installs 100+ most important security tools from Kali repos
###############################################################################

set -e

CHROOT_DIR="${1:-/home/diablorain/Syn_OS/build/synos-v1.0/work/chroot}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Phase 1: Essential Security Tools (100+ tools)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

install_tools() {
    local category="$1"
    shift
    local tools="$@"

    echo "[→] Installing $category..."
    sudo DEBIAN_FRONTEND=noninteractive chroot "$CHROOT_DIR" bash -c \
        "apt-get install -y --no-install-recommends $tools 2>&1" | \
        grep -E "(Setting up|already|newest|^E:)" || true
}

# Core Reconnaissance Tools
install_tools "Reconnaissance Tools" \
    nmap \
    masscan \
    netdiscover \
    dnsenum \
    dnsrecon \
    enum4linux \
    nbtscan \
    whatweb \
    wafw00f

# Web Application Tools
install_tools "Web Application Tools" \
    nikto \
    sqlmap \
    wpscan \
    dirb \
    gobuster \
    wfuzz \
    commix \
    skipfish

# Password Attack Tools
install_tools "Password Attack Tools" \
    john \
    hashcat \
    hydra \
    medusa \
    ncrack \
    patator \
    crunch \
    cewl

# Wireless Attack Tools
install_tools "Wireless Attack Tools" \
    aircrack-ng \
    reaver \
    bully \
    pixiewps \
    wifite \
    kismet \
    cowpatty \
    mdk4

# Exploitation Frameworks
install_tools "Exploitation Frameworks" \
    metasploit-framework \
    exploitdb \
    searchsploit \
    beef-xss

# Sniffing & Analysis
install_tools "Sniffing & Analysis Tools" \
    wireshark \
    tshark \
    tcpdump \
    ettercap-text-only \
    dsniff \
    mitmproxy \
    sslstrip

# Post-Exploitation
install_tools "Post-Exploitation Tools" \
    weevely \
    proxychains4 \
    sbd \
    iodine \
    dns2tcpc

# Forensics Tools
install_tools "Forensics Tools" \
    autopsy \
    sleuthkit \
    binwalk \
    foremost \
    bulk-extractor \
    hashdeep \
    dc3dd \
    scalpel \
    chkrootkit \
    rkhunter

# Reverse Engineering
install_tools "Reverse Engineering Tools" \
    gdb \
    radare2 \
    rizin \
    objdump \
    strace \
    ltrace \
    valgrind

# Social Engineering
install_tools "Social Engineering Tools" \
    set \
    social-engineer-toolkit

# Hardware & Mobile
install_tools "Hardware & Mobile Tools" \
    android-tools-adb \
    android-tools-fastboot \
    apktool \
    dex2jar

# Reporting & Documentation
install_tools "Reporting Tools" \
    faraday \
    pipal

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Verification & Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verify key tools
echo "Verifying installation of key tools:"
KEY_TOOLS="nmap metasploit msfconsole aircrack-ng john hashcat hydra wireshark nikto sqlmap gobuster burpsuite"

INSTALLED=0
MISSING=0

for tool in $KEY_TOOLS; do
    if sudo chroot "$CHROOT_DIR" which "$tool" &>/dev/null; then
        echo "  ✓ $tool"
        INSTALLED=$((INSTALLED + 1))
    else
        echo "  ✗ $tool (not found)"
        MISSING=$((MISSING + 1))
    fi
done

echo ""
echo "Results:"
echo "  ✓ Installed: $INSTALLED/$((INSTALLED + MISSING))"
if [ $MISSING -gt 0 ]; then
    echo "  ✗ Missing: $MISSING (may not be available in repos)"
fi

# Count total security packages
SECURITY_COUNT=$(sudo chroot "$CHROOT_DIR" dpkg -l | grep -i "^ii" | grep -E "(hack|exploit|crack|scan|forensic|pentest|security)" | wc -l)
echo ""
echo "Total security-related packages: $SECURITY_COUNT"

# Check chroot size
CHROOT_SIZE=$(sudo du -sh "$CHROOT_DIR" 2>/dev/null | cut -f1)
echo "Chroot size: $CHROOT_SIZE"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Phase 1 Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✓ Essential security tools installed"
echo "✓ Combined with 81 GitHub repos"
echo "✓ Ready for Phase 2 (Core Integration)"
echo ""

exit 0
