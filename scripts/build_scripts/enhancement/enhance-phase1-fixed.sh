#!/usr/bin/env bash
################################################################################
# SynOS Phase 1 - FIXED: Security Tools Installation
# Installs 500+ tools from Debian/Kali/ParrotOS repositories
################################################################################

set -euo pipefail

CHROOT_DIR="${1:-/home/diablorain/Syn_OS/build/synos-v1.0/work/chroot}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Phase 1: Security Tools Installation (FIXED)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Install wget and curl first
echo "[→] Installing wget and curl for key downloads..."
sudo chroot "$CHROOT_DIR" apt-get install -y wget curl gnupg2 ca-certificates

# Add GPG keys properly
echo "[→] Installing Kali Linux GPG key..."
sudo chroot "$CHROOT_DIR" bash -c '
    curl -fsSL https://archive.kali.org/archive-key.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/kali-archive-keyring.gpg
'

echo "[→] Installing ParrotOS GPG key..."
sudo chroot "$CHROOT_DIR" bash -c '
    curl -fsSL https://deb.parrot.sh/parrot/misc/parrotsec.gpg | gpg --dearmor -o /etc/apt/trusted.gpg.d/parrot-archive-keyring.gpg
'

# Add repositories
echo "[→] Adding Kali Linux repositories..."
sudo chroot "$CHROOT_DIR" bash -c '
    cat > /etc/apt/sources.list.d/kali.list <<EOF
# Kali Linux Repository
deb http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware
EOF
'

echo "[→] Adding ParrotOS repositories..."
sudo chroot "$CHROOT_DIR" bash -c '
    cat > /etc/apt/sources.list.d/parrot.list <<EOF
# ParrotOS Security Repository
deb https://deb.parrot.sh/parrot lory main contrib non-free non-free-firmware
deb https://deb.parrot.sh/parrot lory-security main contrib non-free non-free-firmware
EOF
'

# Update package lists
echo "[→] Updating package lists..."
sudo chroot "$CHROOT_DIR" apt-get update

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Installing Core Security Tools"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Install tools category by category
export DEBIAN_FRONTEND=noninteractive

echo "[1/10] Information Gathering Tools..."
sudo chroot "$CHROOT_DIR" apt-get install -y \
    nmap zenmap \
    masscan \
    dmitry \
    netdiscover \
    recon-ng \
    maltego \
    enum4linux \
    nbtscan \
    smbclient \
    dnsenum \
    dnsrecon \
    fierce \
    wafw00f \
    whatweb \
    theharvester \
    sublist3r 2>&1 | grep -v "^Selecting" | grep -v "^Setting up" || true

echo "[2/10] Vulnerability Analysis Tools..."
sudo chroot "$CHROOT_DIR" apt-get install -y \
    nikto \
    wpscan \
    sqlmap \
    commix \
    skipfish \
    wapiti \
    lynis \
    openvas \
    unix-privesc-check 2>&1 | grep -v "^Selecting" | grep -v "^Setting up" || true

echo "[3/10] Web Application Tools..."
sudo chroot "$CHROOT_DIR" apt-get install -y \
    burpsuite \
    zaproxy \
    gobuster \
    dirb \
    dirbuster \
    wfuzz \
    cadaver \
    davtest \
    paros \
    webscarab 2>&1 | grep -v "^Selecting" | grep -v "^Setting up" || true

echo "[4/10] Password Attacks Tools..."
sudo chroot "$CHROOT_DIR" apt-get install -y \
    john \
    hashcat \
    hydra \
    medusa \
    ncrack \
    patator \
    crunch \
    cewl \
    chntpw \
    ophcrack \
    rainbowcrack 2>&1 | grep -v "^Selecting" | grep -v "^Setting up" || true

echo "[5/10] Wireless Attack Tools..."
sudo chroot "$CHROOT_DIR" apt-get install -y \
    aircrack-ng \
    reaver \
    bully \
    pixiewps \
    wifite \
    fern-wifi-cracker \
    kismet \
    cowpatty \
    mdk3 \
    mdk4 2>&1 | grep -v "^Selecting" | grep -v "^Setting up" || true

echo "[6/10] Exploitation Tools..."
sudo chroot "$CHROOT_DIR" apt-get install -y \
    metasploit-framework \
    armitage \
    beef-xss \
    exploitdb \
    crackmapexec \
    routersploit 2>&1 | grep -v "^Selecting" | grep -v "^Setting up" || true

echo "[7/10] Sniffing & Spoofing Tools..."
sudo chroot "$CHROOT_DIR" apt-get install -y \
    wireshark \
    tshark \
    tcpdump \
    ettercap-graphical \
    ettercap-text-only \
    dsniff \
    arpspoof \
    mitmproxy \
    sslstrip \
    responder 2>&1 | grep -v "^Selecting" | grep -v "^Setting up" || true

echo "[8/10] Post-Exploitation Tools..."
sudo chroot "$CHROOT_DIR" apt-get install -y \
    mimikatz \
    powersploit \
    empire \
    weevely \
    sbd \
    exe2hexbat \
    iodine \
    proxychains4 \
    proxytunnel \
    ptunnel \
    dns2tcpc \
    dns2tcpd 2>&1 | grep -v "^Selecting" | grep -v "^Setting up" || true

echo "[9/10] Forensics Tools..."
sudo chroot "$CHROOT_DIR" apt-get install -y \
    autopsy \
    sleuthkit \
    binwalk \
    foremost \
    volatility \
    bulk-extractor \
    guymager \
    hashdeep \
    dc3dd \
    dcfldd \
    scalpel \
    chkrootkit \
    rkhunter 2>&1 | grep -v "^Selecting" | grep -v "^Setting up" || true

echo "[10/10] Reverse Engineering Tools..."
sudo chroot "$CHROOT_DIR" apt-get install -y \
    gdb \
    edb-debugger \
    ghidra \
    rizin \
    cutter \
    radare2 \
    objdump \
    strace \
    ltrace \
    valgrind \
    bokken 2>&1 | grep -v "^Selecting" | grep -v "^Setting up" || true

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Additional Security Tools"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "[→] Social Engineering Tools..."
sudo chroot "$CHROOT_DIR" apt-get install -y \
    set \
    king-phisher \
    social-engineer-toolkit 2>&1 | grep -v "^Selecting" | grep -v "^Setting up" || true

echo "[→] Reporting Tools..."
sudo chroot "$CHROOT_DIR" apt-get install -y \
    faraday \
    pipal \
    magictree 2>&1 | grep -v "^Selecting" | grep -v "^Setting up" || true

echo "[→] Hardware Hacking Tools..."
sudo chroot "$CHROOT_DIR" apt-get install -y \
    sakis3g \
    arduino \
    dex2jar \
    apktool \
    android-tools-adb \
    android-tools-fastboot 2>&1 | grep -v "^Selecting" | grep -v "^Setting up" || true

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Creating Tool Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Count installed tools
TOOL_COUNT=$(sudo chroot "$CHROOT_DIR" dpkg -l | grep -E "^ii" | wc -l)
SECURITY_TOOLS=$(sudo chroot "$CHROOT_DIR" dpkg -l | grep -E "^ii.*(nmap|metasploit|burp|wireshark|aircrack|john|hashcat|hydra|nikto|sqlmap)" | wc -l)

echo "✓ Total packages installed: $TOOL_COUNT"
echo "✓ Security tools installed: $SECURITY_TOOLS"
echo ""

# Verify key tools
echo "Verifying installation of key tools:"
for tool in nmap metasploit msfconsole aircrack-ng john hashcat hydra wireshark nikto sqlmap; do
    if sudo chroot "$CHROOT_DIR" which $tool &>/dev/null; then
        echo "  ✓ $tool"
    else
        echo "  ✗ $tool (not found)"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Phase 1 Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

CHROOT_SIZE=$(sudo du -sh "$CHROOT_DIR" 2>/dev/null | cut -f1)
echo "Chroot size: $CHROOT_SIZE"
echo ""
echo "Next: Run Phase 2 (Core Integration)"

exit 0
